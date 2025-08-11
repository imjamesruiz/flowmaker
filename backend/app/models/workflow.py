from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


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
    node_type = Column(String(100), nullable=False)  # trigger, action, condition, etc.
    name = Column(String(255), nullable=False)
    position_x = Column(Float, nullable=False)
    position_y = Column(Float, nullable=False)
    config = Column(JSON, nullable=True)  # Node configuration
    integration_id = Column(Integer, ForeignKey("integrations.id"), nullable=True)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="nodes")
    integration = relationship("Integration")
    
    def __repr__(self):
        return f"<WorkflowNode(id={self.id}, node_id='{self.node_id}', type='{self.node_type}')>"


class WorkflowConnection(Base):
    __tablename__ = "workflow_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    connection_id = Column(String(255), nullable=False)  # Joint.js connection ID
    source_node_id = Column(String(255), nullable=False)
    target_node_id = Column(String(255), nullable=False)
    source_port = Column(String(100), nullable=True)
    target_port = Column(String(100), nullable=True)
    condition = Column(JSON, nullable=True)  # Conditional logic
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    workflow = relationship("Workflow", back_populates="connections")
    
    def __repr__(self):
        return f"<WorkflowConnection(id={self.id}, source='{self.source_node_id}', target='{self.target_node_id}')>" 