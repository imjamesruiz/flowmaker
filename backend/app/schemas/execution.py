from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.execution import ExecutionStatus, NodeExecutionStatus


class ExecutionResponse(BaseModel):
    id: int
    workflow_id: int
    execution_id: str
    status: ExecutionStatus
    trigger_data: Optional[Dict[str, Any]] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionLogResponse(BaseModel):
    id: int
    execution_id: int
    node_id: str
    node_name: str
    node_type: str
    status: NodeExecutionStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExecutionWithLogs(ExecutionResponse):
    logs: List[ExecutionLogResponse] = []


class ExecutionStatusUpdate(BaseModel):
    status: ExecutionStatus
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class NodeExecutionUpdate(BaseModel):
    status: NodeExecutionStatus
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None 