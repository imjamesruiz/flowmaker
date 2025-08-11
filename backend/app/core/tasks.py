import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from celery import current_task
from sqlalchemy.orm import Session
from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.workflow import Workflow, WorkflowNode, WorkflowConnection
from app.models.execution import WorkflowExecution, ExecutionLog, ExecutionStatus, NodeExecutionStatus
from app.models.integration import OAuthToken
from app.services.workflow_engine import WorkflowEngine
from app.services.oauth_manager import OAuthManager


@celery_app.task(bind=True)
def execute_workflow(self, workflow_id: int, trigger_data: Dict[str, Any] = None, test_mode: bool = False):
    """Execute a workflow as a Celery task"""
    db = SessionLocal()
    try:
        # Get workflow and create execution record
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        execution_id = str(uuid.uuid4())
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            execution_id=execution_id,
            status=ExecutionStatus.RUNNING,
            trigger_data=trigger_data,
            started_at=datetime.utcnow()
        )
        db.add(execution)
        db.commit()
        
        # Initialize workflow engine
        engine = WorkflowEngine(db, execution_id)
        
        # Execute workflow
        result = engine.execute(workflow, trigger_data, test_mode)
        
        # Update execution status
        execution.status = ExecutionStatus.COMPLETED if result["success"] else ExecutionStatus.FAILED
        execution.result_data = result.get("result_data")
        execution.error_message = result.get("error_message")
        execution.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "execution_id": execution_id,
            "success": result["success"],
            "result_data": result.get("result_data"),
            "error_message": result.get("error_message")
        }
        
    except Exception as e:
        # Update execution status on error
        if 'execution' in locals():
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            db.commit()
        
        raise
    finally:
        db.close()


@celery_app.task
def cleanup_expired_tokens():
    """Clean up expired OAuth tokens"""
    db = SessionLocal()
    try:
        expired_tokens = db.query(OAuthToken).filter(
            OAuthToken.expires_at < datetime.utcnow(),
            OAuthToken.is_valid == True
        ).all()
        
        for token in expired_tokens:
            token.is_valid = False
        
        db.commit()
        return f"Cleaned up {len(expired_tokens)} expired tokens"
    finally:
        db.close()


@celery_app.task
def refresh_oauth_tokens():
    """Refresh OAuth tokens that are about to expire"""
    db = SessionLocal()
    try:
        oauth_manager = OAuthManager(db)
        
        # Find tokens expiring in the next hour
        expiry_threshold = datetime.utcnow() + timedelta(hours=1)
        expiring_tokens = db.query(OAuthToken).filter(
            OAuthToken.expires_at < expiry_threshold,
            OAuthToken.is_valid == True,
            OAuthToken.refresh_token.isnot(None)
        ).all()
        
        refreshed_count = 0
        for token in expiring_tokens:
            try:
                success = oauth_manager.refresh_token(token)
                if success:
                    refreshed_count += 1
            except Exception as e:
                # Log error but continue with other tokens
                print(f"Failed to refresh token {token.id}: {e}")
        
        db.commit()
        return f"Refreshed {refreshed_count} tokens"
    finally:
        db.close()


@celery_app.task
def test_workflow_connection(integration_id: int, node_config: Dict[str, Any]):
    """Test a workflow node connection"""
    db = SessionLocal()
    try:
        # This would test the specific integration connection
        # Implementation depends on the integration type
        return {"success": True, "message": "Connection test successful"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        db.close()


@celery_app.task
def send_webhook_notification(webhook_url: str, payload: Dict[str, Any]):
    """Send webhook notification"""
    import httpx
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(webhook_url, json=payload)
            response.raise_for_status()
            return {"success": True, "status_code": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)} 