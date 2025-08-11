from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeExecutionStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    execution_id = Column(String(255), unique=True, nullable=False)  # UUID for tracking
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.PENDING)
    trigger_data = Column(JSON, nullable=True)  # Data that triggered the execution
    result_data = Column(JSON, nullable=True)  # Final result data
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    logs = relationship("ExecutionLog", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WorkflowExecution(id={self.id}, execution_id='{self.execution_id}', status='{self.status}')>"


class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=False)
    node_id = Column(String(255), nullable=False)  # Joint.js node ID
    node_name = Column(String(255), nullable=False)
    node_type = Column(String(100), nullable=False)
    status = Column(Enum(NodeExecutionStatus), default=NodeExecutionStatus.PENDING)
    input_data = Column(JSON, nullable=True)  # Input data for the node
    output_data = Column(JSON, nullable=True)  # Output data from the node
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # Execution time in milliseconds
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    execution = relationship("WorkflowExecution", back_populates="logs")
    
    def __repr__(self):
        return f"<ExecutionLog(id={self.id}, node_id='{self.node_id}', status='{self.status}')>" 