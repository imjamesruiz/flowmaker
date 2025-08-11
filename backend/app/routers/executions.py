from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.execution import WorkflowExecution, ExecutionLog
from app.schemas.execution import ExecutionResponse, ExecutionLogResponse, ExecutionWithLogs
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[ExecutionResponse])
def get_executions(
    workflow_id: int = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get workflow executions for current user"""
    query = db.query(WorkflowExecution).join(Workflow).filter(
        Workflow.owner_id == current_user.id
    )
    
    if workflow_id:
        query = query.filter(WorkflowExecution.workflow_id == workflow_id)
    
    executions = query.order_by(WorkflowExecution.created_at.desc()).offset(skip).limit(limit).all()
    return executions


@router.get("/{execution_id}", response_model=ExecutionWithLogs)
def get_execution(
    execution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific execution with logs"""
    execution = db.query(WorkflowExecution).join(Workflow).filter(
        WorkflowExecution.id == execution_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    return execution


@router.get("/{execution_id}/logs", response_model=List[ExecutionLogResponse])
def get_execution_logs(
    execution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get logs for a specific execution"""
    # Verify execution belongs to user
    execution = db.query(WorkflowExecution).join(Workflow).filter(
        WorkflowExecution.id == execution_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    logs = db.query(ExecutionLog).filter(
        ExecutionLog.execution_id == execution_id
    ).order_by(ExecutionLog.created_at.asc()).all()
    
    return logs


@router.delete("/{execution_id}")
def delete_execution(
    execution_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an execution and its logs"""
    execution = db.query(WorkflowExecution).join(Workflow).filter(
        WorkflowExecution.id == execution_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found"
        )
    
    db.delete(execution)
    db.commit()
    return {"message": "Execution deleted successfully"} 