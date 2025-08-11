from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    canvas_data: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    canvas_data: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class WorkflowResponse(WorkflowBase):
    id: int
    owner_id: int
    is_active: bool
    is_template: bool
    version: int
    canvas_data: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowNodeBase(BaseModel):
    node_id: str = Field(..., description="Joint.js node ID")
    node_type: str = Field(..., description="trigger, action, condition, etc.")
    name: str = Field(..., min_length=1, max_length=255)
    position_x: float
    position_y: float
    config: Optional[Dict[str, Any]] = None
    integration_id: Optional[int] = None


class WorkflowNodeCreate(WorkflowNodeBase):
    pass


class WorkflowNodeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    config: Optional[Dict[str, Any]] = None
    integration_id: Optional[int] = None
    is_enabled: Optional[bool] = None


class WorkflowNodeResponse(WorkflowNodeBase):
    id: int
    workflow_id: int
    is_enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WorkflowConnectionBase(BaseModel):
    connection_id: str = Field(..., description="Joint.js connection ID")
    source_node_id: str
    target_node_id: str
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None


class WorkflowConnectionCreate(WorkflowConnectionBase):
    pass


class WorkflowConnectionUpdate(BaseModel):
    source_port: Optional[str] = None
    target_port: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class WorkflowConnectionResponse(WorkflowConnectionBase):
    id: int
    workflow_id: int
    is_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowWithNodes(WorkflowResponse):
    nodes: List[WorkflowNodeResponse] = []
    connections: List[WorkflowConnectionResponse] = []


class WorkflowExecutionRequest(BaseModel):
    trigger_data: Optional[Dict[str, Any]] = None
    test_mode: bool = False 