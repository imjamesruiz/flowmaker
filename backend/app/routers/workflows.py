from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.workflow import Workflow, WorkflowNode, WorkflowConnection
from app.schemas.workflow import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowWithNodes,
    WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeResponse,
    WorkflowConnectionCreate, WorkflowConnectionUpdate, WorkflowConnectionResponse,
    WorkflowExecutionRequest, WorkflowBulkUpdate, WorkflowPayload, ExecutionResult,
    WorkflowValidationResult
)
from app.auth.dependencies import get_current_active_user
from app.core.tasks import execute_workflow
from app.services.workflow_executor import WorkflowExecutor

router = APIRouter()


@router.get("/workflows", response_model=List[WorkflowResponse])
def get_workflows(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all workflows for current user"""
    workflows = db.query(Workflow).filter(
        Workflow.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return workflows


@router.post("/workflows", response_model=WorkflowResponse)
def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    workflow = Workflow(
        **workflow_data.dict(),
        owner_id=current_user.id
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


@router.get("/workflows/{workflow_id}", response_model=WorkflowWithNodes)
def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific workflow with nodes and connections"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    for field, value in workflow_data.dict(exclude_unset=True).items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    return workflow


@router.put("/workflows/{workflow_id}/bulk", response_model=WorkflowWithNodes)
def update_workflow_bulk(
    workflow_id: int,
    workflow_data: WorkflowBulkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workflow with nodes and connections in a single transaction"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    try:
        # Update workflow basic info
        if workflow_data.name is not None:
            workflow.name = workflow_data.name
        if workflow_data.description is not None:
            workflow.description = workflow_data.description
        
        # Handle nodes if provided
        if workflow_data.nodes is not None:
            # Clear existing nodes and connections
            db.query(WorkflowConnection).filter(WorkflowConnection.workflow_id == workflow_id).delete()
            db.query(WorkflowNode).filter(WorkflowNode.workflow_id == workflow_id).delete()
            
            # Create new nodes
            for node_data in workflow_data.nodes:
                node = WorkflowNode(
                    node_id=node_data.id,
                    node_type=node_data.type,
                    name=node_data.data.get('name', 'Unnamed Node'),
                    position_x=node_data.position.get('x', 0),
                    position_y=node_data.position.get('y', 0),
                    config=node_data.data.get('config', {}),
                    workflow_id=workflow_id
                )
                db.add(node)
        
        # Handle edges if provided
        if workflow_data.edges is not None:
            for edge_data in workflow_data.edges:
                connection = WorkflowConnection(
                    connection_id=edge_data.id,
                    source_node_id=edge_data.source,
                    target_node_id=edge_data.target,
                    source_port=edge_data.sourceHandle,
                    target_port=edge_data.targetHandle,
                    condition={"label": edge_data.label} if edge_data.label else None,
                    workflow_id=workflow_id
                )
                db.add(connection)
        
        db.commit()
        db.refresh(workflow)
        return workflow
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update workflow: {str(e)}"
        )


@router.post("/workflows/{workflow_id}/validate", response_model=WorkflowValidationResult)
def validate_workflow(
    workflow_id: int,
    workflow_data: WorkflowBulkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate a workflow structure"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    if not workflow_data.nodes or not workflow_data.edges:
        return WorkflowValidationResult(
            valid=False,
            errors=["Workflow must contain nodes and edges"]
        )
    
    # Convert to WorkflowPayload format
    payload = WorkflowPayload(
        id=str(workflow_id),
        name=workflow.name,
        nodes=workflow_data.nodes,
        edges=workflow_data.edges,
        viewport=workflow_data.viewport
    )
    
    # Validate using executor
    executor = WorkflowExecutor()
    validation_result = executor.validate_workflow(payload)
    
    return WorkflowValidationResult(
        valid=validation_result["valid"],
        errors=validation_result["errors"]
    )


@router.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted successfully"}


@router.post("/workflows/{workflow_id}/execute")
def execute_workflow_endpoint(
    workflow_id: int,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Start async execution
    task = execute_workflow.delay(
        workflow_id=workflow_id,
        trigger_data=execution_request.trigger_data,
        test_mode=execution_request.test_mode
    )
    
    return {
        "task_id": task.id,
        "status": "executing",
        "message": "Workflow execution started"
    }


@router.post("/workflows/{workflow_id}/test", response_model=ExecutionResult)
def test_workflow_endpoint(
    workflow_id: int,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test execute a workflow synchronously"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Prepare workflow data for execution
    workflow_data = WorkflowPayload(
        id=str(workflow_id),
        name=workflow.name,
        nodes=[
            {
                "id": node.node_id,
                "type": node.node_type,
                "position": {"x": node.position_x, "y": node.position_y},
                "data": {
                    "name": node.name,
                    "config": node.config or {}
                }
            }
            for node in workflow.nodes
        ],
        edges=[
            {
                "id": conn.connection_id,
                "source": conn.source_node_id,
                "target": conn.target_node_id,
                "sourceHandle": conn.source_port,
                "targetHandle": conn.target_port,
                "label": conn.condition.get("label") if conn.condition else None
            }
            for conn in workflow.connections
        ]
    )
    
    # Execute workflow
    executor = WorkflowExecutor()
    result = executor.execute_workflow(
        workflow_data, 
        trigger_data=execution_request.trigger_data
    )
    
    return result


# Node endpoints
@router.get("/workflows/{workflow_id}/nodes", response_model=List[WorkflowNodeResponse])
def get_workflow_nodes(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all nodes for a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow.nodes


@router.post("/workflows/{workflow_id}/nodes", response_model=WorkflowNodeResponse)
def create_workflow_node(
    workflow_id: int,
    node_data: WorkflowNodeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new node in a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    node = WorkflowNode(
        **node_data.dict(),
        workflow_id=workflow_id
    )
    db.add(node)
    db.commit()
    db.refresh(node)
    return node


@router.put("/workflows/{workflow_id}/nodes/{node_id}", response_model=WorkflowNodeResponse)
def update_workflow_node(
    workflow_id: int,
    node_id: int,
    node_data: WorkflowNodeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workflow node"""
    node = db.query(WorkflowNode).join(Workflow).filter(
        WorkflowNode.id == node_id,
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    for field, value in node_data.dict(exclude_unset=True).items():
        setattr(node, field, value)
    
    db.commit()
    db.refresh(node)
    return node


@router.delete("/workflows/{workflow_id}/nodes/{node_id}")
def delete_workflow_node(
    workflow_id: int,
    node_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow node"""
    node = db.query(WorkflowNode).join(Workflow).filter(
        WorkflowNode.id == node_id,
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found"
        )
    
    db.delete(node)
    db.commit()
    return {"message": "Node deleted successfully"}


# Connection endpoints
@router.get("/workflows/{workflow_id}/connections", response_model=List[WorkflowConnectionResponse])
def get_workflow_connections(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all connections for a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    return workflow.connections


@router.post("/workflows/{workflow_id}/connections", response_model=WorkflowConnectionResponse)
def create_workflow_connection(
    workflow_id: int,
    connection_data: WorkflowConnectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new connection in a workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    connection = WorkflowConnection(
        **connection_data.dict(),
        workflow_id=workflow_id
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.put("/workflows/{workflow_id}/connections/{connection_id}", response_model=WorkflowConnectionResponse)
def update_workflow_connection(
    workflow_id: int,
    connection_id: int,
    connection_data: WorkflowConnectionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workflow connection"""
    connection = db.query(WorkflowConnection).join(Workflow).filter(
        WorkflowConnection.id == connection_id,
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    for field, value in connection_data.dict(exclude_unset=True).items():
        setattr(connection, field, value)
    
    db.commit()
    db.refresh(connection)
    return connection


@router.delete("/workflows/{workflow_id}/connections/{connection_id}")
def delete_workflow_connection(
    workflow_id: int,
    connection_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a workflow connection"""
    connection = db.query(WorkflowConnection).join(Workflow).filter(
        WorkflowConnection.id == connection_id,
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    db.delete(connection)
    db.commit()
    return {"message": "Connection deleted successfully"} 