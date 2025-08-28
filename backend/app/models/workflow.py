from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class NodeType(enum.Enum):
    TRIGGER = "trigger"
    ACTION = "action"
    CONDITION = "condition"
    TRANSFORMER = "transformer"
    WEBHOOK = "webhook"
    DELAY = "delay"
    LOOP = "loop"


class ConnectionType(enum.Enum):
    DATA_FLOW = "data_flow"
    CONDITIONAL = "conditional"
    ERROR_HANDLER = "error_handler"


class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    canvas_data = Column(JSON, nullable=True)  # Joint.js canvas data
    settings = Column(JSON, nullable=True)  # Workflow settings
    trigger_config = Column(JSON, nullable=True)  # Trigger configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="workflows")
    nodes = relationship("WorkflowNode", back_populates="workflow", cascade="all, delete-orphan")
    connections = relationship("WorkflowConnection", back_populates="workflow", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"


class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    node_id = Column(String(255), nullable=False)  # Joint.js node ID
    node_type = Column(Enum(NodeType), nullable=False)
    name = Column(String(255), nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    config = Column(JSON, nullable=True)  # Node configuration
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=True)
    is_enabled = Column(Boolean, default=True)
    retry_config = Column(JSON, nullable=True)  # Retry configuration
    timeout_seconds = Column(Integer, default=300)  # Node timeout
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="nodes")
    integration = relationship("Integration")
    # Temporarily disable problematic relationships for password reset functionality
    # input_connections = relationship("WorkflowConnection", foreign_keys="WorkflowConnection.target_node_id", back_populates="target_node")
    # output_connections = relationship("WorkflowConnection", foreign_keys="WorkflowConnection.source_node_id", back_populates="source_node")
    
    def __repr__(self):
        return f"<WorkflowNode(id={self.id}, node_id='{self.node_id}', type='{self.node_type}')>"


class WorkflowConnection(Base):
    __tablename__ = "workflow_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    connection_id = Column(String(255), nullable=False)  # Joint.js connection ID
    source_node_id = Column(String(255), nullable=False)
    target_node_id = Column(String(255), nullable=False)
    connection_type = Column(Enum(ConnectionType), default=ConnectionType.DATA_FLOW)
    source_port = Column(String(100), nullable=True)
    target_port = Column(String(100), nullable=True)
    condition = Column(JSON, nullable=True)  # Conditional logic
    data_mapping = Column(JSON, nullable=True)  # Data transformation mapping
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="connections")
    # Temporarily disable problematic relationships for password reset functionality
    # source_node = relationship("WorkflowNode", foreign_keys=[source_node_id], back_populates="output_connections")
    # target_node = relationship("WorkflowNode", foreign_keys=[target_node_id], back_populates="input_connections")
    
    def __repr__(self):
        return f"<WorkflowConnection(id={self.id}, source='{self.source_node_id}', target='{self.target_node_id}')>"


class WorkflowTrigger(Base):
    __tablename__ = "workflow_triggers"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    trigger_type = Column(String(100), nullable=False)  # webhook, schedule, manual
    config = Column(JSON, nullable=True)  # Trigger-specific configuration
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow")
    
    def __repr__(self):
        return f"<WorkflowTrigger(id={self.id}, workflow_id={self.workflow_id}, type='{self.trigger_type}')>" 