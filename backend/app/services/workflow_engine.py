import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from sqlalchemy.orm import Session
from app.models.workflow import Workflow, WorkflowNode, WorkflowConnection
from app.models.execution import WorkflowExecution, ExecutionLog, NodeExecutionStatus
from app.services.node_executor import NodeExecutor
from app.services.oauth_manager import OAuthManager


class WorkflowEngine:
    """Core workflow execution engine for DAG-based workflow processing"""
    
    def __init__(self, db: Session, execution_id: str):
        self.db = db
        self.execution_id = execution_id
        self.node_executor = NodeExecutor(db)
        self.oauth_manager = OAuthManager(db)
        self.execution_data: Dict[str, Any] = {}
        self.executed_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
    
    def execute(self, workflow: Workflow, trigger_data: Dict[str, Any] = None, test_mode: bool = False) -> Dict[str, Any]:
        """Execute a complete workflow"""
        try:
            # Initialize execution data with trigger data
            self.execution_data = trigger_data or {}
            
            # Build execution graph
            nodes = {node.node_id: node for node in workflow.nodes if node.is_enabled}
            connections = [conn for conn in workflow.connections if conn.is_enabled]
            
            # Find trigger nodes (nodes with no incoming connections)
            trigger_nodes = self._find_trigger_nodes(nodes, connections)
            
            if not trigger_nodes:
                return {
                    "success": False,
                    "error_message": "No trigger nodes found in workflow"
                }
            
            # Execute workflow starting from trigger nodes
            result_data = {}
            for trigger_node_id in trigger_nodes:
                node_result = self._execute_node_recursive(
                    trigger_node_id, nodes, connections, test_mode
                )
                if node_result:
                    result_data.update(node_result)
            
            return {
                "success": len(self.failed_nodes) == 0,
                "result_data": result_data,
                "error_message": None if len(self.failed_nodes) == 0 else f"Failed nodes: {list(self.failed_nodes)}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error_message": str(e)
            }
    
    def _find_trigger_nodes(self, nodes: Dict[str, WorkflowNode], connections: List[WorkflowConnection]) -> List[str]:
        """Find nodes that have no incoming connections (trigger nodes)"""
        all_nodes = set(nodes.keys())
        target_nodes = set()
        
        for conn in connections:
            target_nodes.add(conn.target_node_id)
        
        return list(all_nodes - target_nodes)
    
    def _execute_node_recursive(
        self, 
        node_id: str, 
        nodes: Dict[str, WorkflowNode], 
        connections: List[WorkflowConnection],
        test_mode: bool
    ) -> Optional[Dict[str, Any]]:
        """Execute a node and its downstream nodes recursively"""
        
        # Skip if already executed or failed
        if node_id in self.executed_nodes:
            return self.execution_data.get(node_id)
        
        if node_id in self.failed_nodes:
            return None
        
        node = nodes.get(node_id)
        if not node:
            return None
        
        # Check if all dependencies are satisfied
        dependencies = self._get_node_dependencies(node_id, connections)
        for dep_node_id in dependencies:
            if dep_node_id not in self.executed_nodes:
                # Execute dependency first
                self._execute_node_recursive(dep_node_id, nodes, connections, test_mode)
                if dep_node_id in self.failed_nodes:
                    self.failed_nodes.add(node_id)
                    return None
        
        # Execute the node
        try:
            node_result = self._execute_single_node(node, test_mode)
            self.executed_nodes.add(node_id)
            self.execution_data[node_id] = node_result
            
            # Execute downstream nodes
            downstream_nodes = self._get_downstream_nodes(node_id, connections)
            for downstream_node_id in downstream_nodes:
                if downstream_node_id in nodes:
                    self._execute_node_recursive(downstream_node_id, nodes, connections, test_mode)
            
            return node_result
            
        except Exception as e:
            self.failed_nodes.add(node_id)
            self._log_node_execution(node, NodeExecutionStatus.FAILED, error_message=str(e))
            return None
    
    def _execute_single_node(self, node: WorkflowNode, test_mode: bool) -> Dict[str, Any]:
        """Execute a single workflow node"""
        start_time = time.time()
        
        # Log node start
        self._log_node_execution(node, NodeExecutionStatus.RUNNING)
        
        try:
            # Get input data for the node
            input_data = self._prepare_node_input(node)
            
            # Execute the node
            if test_mode:
                result = self.node_executor.test_node(node, input_data)
            else:
                result = self.node_executor.execute_node(node, input_data)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log successful execution
            self._log_node_execution(
                node, 
                NodeExecutionStatus.COMPLETED,
                input_data=input_data,
                output_data=result,
                execution_time_ms=execution_time
            )
            
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self._log_node_execution(
                node,
                NodeExecutionStatus.FAILED,
                error_message=str(e),
                execution_time_ms=execution_time
            )
            raise
    
    def _prepare_node_input(self, node: WorkflowNode) -> Dict[str, Any]:
        """Prepare input data for a node based on upstream nodes"""
        input_data = {}
        
        # Get data from upstream nodes
        for upstream_node_id, data in self.execution_data.items():
            if upstream_node_id != node.node_id:
                input_data[upstream_node_id] = data
        
        # Add node-specific configuration
        if node.config:
            input_data["config"] = node.config
        
        return input_data
    
    def _get_node_dependencies(self, node_id: str, connections: List[WorkflowConnection]) -> List[str]:
        """Get list of nodes that must be executed before this node"""
        dependencies = []
        for conn in connections:
            if conn.target_node_id == node_id:
                dependencies.append(conn.source_node_id)
        return dependencies
    
    def _get_downstream_nodes(self, node_id: str, connections: List[WorkflowConnection]) -> List[str]:
        """Get list of nodes that depend on this node"""
        downstream = []
        for conn in connections:
            if conn.source_node_id == node_id:
                downstream.append(conn.target_node_id)
        return downstream
    
    def _log_node_execution(
        self, 
        node: WorkflowNode, 
        status: NodeExecutionStatus,
        input_data: Dict[str, Any] = None,
        output_data: Dict[str, Any] = None,
        error_message: str = None,
        execution_time_ms: int = None
    ):
        """Log node execution details"""
        execution = self.db.query(WorkflowExecution).filter(
            WorkflowExecution.execution_id == self.execution_id
        ).first()
        
        if not execution:
            return
        
        log = ExecutionLog(
            execution_id=execution.id,
            node_id=node.node_id,
            node_name=node.name,
            node_type=node.node_type,
            status=status,
            input_data=input_data,
            output_data=output_data,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            started_at=datetime.utcnow() if status == NodeExecutionStatus.RUNNING else None,
            completed_at=datetime.utcnow() if status in [NodeExecutionStatus.COMPLETED, NodeExecutionStatus.FAILED] else None
        )
        
        self.db.add(log)
        self.db.commit() 