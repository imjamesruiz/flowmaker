import uuid
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from celery import current_task, chain, group
from sqlalchemy.orm import Session
from app.core.celery_app import celery_app
from app.database import SessionLocal
from app.models.workflow import Workflow, WorkflowNode, WorkflowConnection, NodeType, ConnectionType
from app.models.execution import WorkflowExecution, ExecutionLog, ExecutionStatus, NodeExecutionStatus
from app.models.integration import OAuthToken
from app.services.workflow_engine import WorkflowEngine
from app.services.oauth_manager import OAuthManager
from app.services.node_executor import NodeExecutor


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


@celery_app.task(bind=True)
def execute_single_node(self, node_id: str, input_data: Dict[str, Any], execution_id: str, test_mode: bool = False):
    """Execute a single workflow node"""
    db = SessionLocal()
    try:
        # Get node
        node = db.query(WorkflowNode).filter(WorkflowNode.node_id == node_id).first()
        if not node:
            raise ValueError(f"Node {node_id} not found")
        
        # Get execution
        execution = db.query(WorkflowExecution).filter(WorkflowExecution.execution_id == execution_id).first()
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        
        # Execute node
        executor = NodeExecutor(db)
        start_time = time.time()
        
        # Log node start
        log = ExecutionLog(
            execution_id=execution.id,
            node_id=node.node_id,
            node_name=node.name,
            node_type=node.node_type.value,
            status=NodeExecutionStatus.RUNNING,
            input_data=input_data,
            started_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        
        try:
            if test_mode:
                result = executor.test_node(node, input_data)
            else:
                result = executor.execute_node(node, input_data)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update log with success
            log.status = NodeExecutionStatus.COMPLETED
            log.output_data = result
            log.execution_time_ms = execution_time
            log.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "node_id": node_id,
                "success": True,
                "result": result,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update log with error
            log.status = NodeExecutionStatus.FAILED
            log.error_message = str(e)
            log.execution_time_ms = execution_time
            log.completed_at = datetime.utcnow()
            db.commit()
            
            raise
            
    except Exception as e:
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def execute_workflow_chain(self, workflow_id: int, node_sequence: List[str], execution_id: str, 
                          initial_data: Dict[str, Any] = None, test_mode: bool = False):
    """Execute a sequence of nodes in order"""
    db = SessionLocal()
    try:
        current_data = initial_data or {}
        
        for node_id in node_sequence:
            # Execute node with current data
            result = execute_single_node.delay(node_id, current_data, execution_id, test_mode)
            node_result = result.get()
            
            if not node_result["success"]:
                raise Exception(f"Node {node_id} failed: {node_result.get('error_message', 'Unknown error')}")
            
            # Update current data with node output
            current_data[node_id] = node_result["result"]
        
        return {
            "success": True,
            "final_data": current_data
        }
        
    except Exception as e:
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def execute_parallel_nodes(self, node_ids: List[str], input_data: Dict[str, Any], execution_id: str, 
                          test_mode: bool = False):
    """Execute multiple nodes in parallel"""
    try:
        # Create tasks for each node
        tasks = []
        for node_id in node_ids:
            task = execute_single_node.delay(node_id, input_data, execution_id, test_mode)
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = []
        for task in tasks:
            result = task.get()
            results.append(result)
        
        return {
            "success": all(r["success"] for r in results),
            "results": results
        }
        
    except Exception as e:
        raise


@celery_app.task(bind=True)
def trigger_workflow(self, workflow_id: int, trigger_type: str, trigger_data: Dict[str, Any] = None):
    """Trigger a workflow based on external events"""
    try:
        # Validate trigger
        db = SessionLocal()
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id, Workflow.is_active == True).first()
        if not workflow:
            raise ValueError(f"Active workflow {workflow_id} not found")
        
        # Check if workflow has the specified trigger type
        trigger_config = workflow.trigger_config or {}
        if trigger_type not in trigger_config.get("types", []):
            raise ValueError(f"Workflow {workflow_id} does not support trigger type: {trigger_type}")
        
        # Execute workflow
        result = execute_workflow.delay(workflow_id, trigger_data)
        return {
            "workflow_id": workflow_id,
            "trigger_type": trigger_type,
            "task_id": result.id,
            "status": "triggered"
        }
        
    except Exception as e:
        raise
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task
def cleanup_expired_tokens():
    """Clean up expired OAuth tokens"""
    db = SessionLocal()
    try:
        # Find expired tokens
        expired_tokens = db.query(OAuthToken).filter(
            OAuthToken.expires_at < datetime.utcnow(),
            OAuthToken.is_valid == True
        ).all()
        
        # Mark as invalid
        for token in expired_tokens:
            token.is_valid = False
        
        db.commit()
        
        return {
            "cleaned_tokens": len(expired_tokens)
        }
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task
def cleanup_old_executions():
    """Clean up old execution logs (older than 30 days)"""
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Delete old execution logs
        deleted_logs = db.query(ExecutionLog).filter(
            ExecutionLog.created_at < cutoff_date
        ).delete()
        
        # Delete old executions (keep metadata)
        deleted_executions = db.query(WorkflowExecution).filter(
            WorkflowExecution.created_at < cutoff_date,
            WorkflowExecution.status.in_([ExecutionStatus.COMPLETED, ExecutionStatus.FAILED])
        ).delete()
        
        db.commit()
        
        return {
            "deleted_logs": deleted_logs,
            "deleted_executions": deleted_executions
        }
        
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task
def health_check():
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "celery_worker": True
    } 