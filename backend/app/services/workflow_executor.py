import time
from typing import Dict, List, Any, Optional, Protocol
from collections import defaultdict, deque
from datetime import datetime
from app.schemas.workflow import WorkflowPayload, ExecutionResult, ExecutionLog


class NodeRunner(Protocol):
    """Protocol for node execution"""
    def run(self, input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
        ...


def run_http_trigger(input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
    """Stub HTTP trigger for test mode"""
    return {"triggered": True, "timestamp": datetime.now().isoformat()}, {}


def run_action_email(input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
    """Stub email action"""
    return {"email_sent": True, "to": config.get("to", "test@example.com")}, {}


def run_condition(input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
    """Evaluate condition and return boolean result"""
    condition_expr = config.get("condition", "True")
    try:
        # Simple condition evaluation (in production, use a proper expression evaluator)
        result = eval(condition_expr, {"input": input_data, "ctx": ctx})
        return bool(result), {}
    except Exception as e:
        return False, {}


def run_transformer(input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
    """Transform input data"""
    transform_type = config.get("type", "pass_through")
    
    if transform_type == "pass_through":
        return input_data, {}
    elif transform_type == "to_uppercase" and isinstance(input_data, str):
        return input_data.upper(), {}
    elif transform_type == "to_lowercase" and isinstance(input_data, str):
        return input_data.lower(), {}
    elif transform_type == "add_prefix":
        prefix = config.get("prefix", "")
        return f"{prefix}{input_data}", {}
    else:
        return input_data, {}


def run_webhook(input_data: Any, ctx: Dict[str, Any], config: Dict[str, Any]) -> tuple[Any, Dict[str, Any]]:
    """Stub webhook action"""
    return {"webhook_called": True, "url": config.get("url", "https://example.com")}, {}


# Node runner registry
RUNNERS: Dict[str, NodeRunner] = {
    "trigger": run_http_trigger,
    "action": run_action_email,
    "condition": run_condition,
    "transformer": run_transformer,
    "webhook": run_webhook,
}


class WorkflowExecutor:
    """Workflow execution engine"""
    
    def __init__(self):
        self.runners = RUNNERS
    
    def build_graph(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Build adjacency list from nodes and edges"""
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        # Initialize graph with all nodes
        for node in nodes:
            # Handle both dict and Pydantic models
            if hasattr(node, 'id'):
                node_id = node.id
            else:
                node_id = node.get('id') or node.get('node_id')
            graph[node_id] = []
            in_degree[node_id] = 0
        
        # Add edges
        for edge in edges:
            # Handle both dict and Pydantic models
            if hasattr(edge, 'source'):
                source = edge.source
                target = edge.target
            else:
                source = edge.get('source') or edge.get('source_node_id')
                target = edge.get('target') or edge.get('target_node_id')
            
            if source and target and source in graph and target in graph:
                graph[source].append(target)
                in_degree[target] += 1
        
        return dict(graph), dict(in_degree)
    
    def topological_sort(self, graph: Dict[str, List[str]], in_degree: Dict[str, int]) -> List[str]:
        """Perform topological sort using Kahn's algorithm"""
        result = []
        queue = deque()
        
        # Add nodes with no incoming edges
        for node, degree in in_degree.items():
            if degree == 0:
                queue.append(node)
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            # Remove edges from current node
            for neighbor in graph.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(graph):
            raise ValueError("Workflow contains cycles")
        
        return result
    
    def execute_workflow(self, workflow_data: WorkflowPayload, trigger_data: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Execute a workflow"""
        start_time = time.time()
        logs: List[ExecutionLog] = []
        outputs: Dict[str, Any] = {}
        context: Dict[str, Any] = {}
        
        try:
            # Build graph and get execution order
            graph, in_degree = self.build_graph(workflow_data.nodes, workflow_data.edges)
            execution_order = self.topological_sort(graph, in_degree)
            
            # Create node lookup
            node_lookup = {}
            for node in workflow_data.nodes:
                node_lookup[node.id] = node
            
            # Execute nodes in topological order
            for node_id in execution_order:
                node = node_lookup.get(node_id)
                if not node:
                    continue
                
                node_start_time = time.time()
                node_type = node.type
                node_name = node.data.get('name', 'Unnamed Node')
                node_config = node.data.get('config', {})
                
                # Get input from incoming edges
                incoming_edges = [
                    edge for edge in workflow_data.edges 
                    if edge.target == node_id
                ]
                
                input_data = None
                if incoming_edges:
                    # For now, take the first input (could be enhanced for multiple inputs)
                    source_node_id = incoming_edges[0].source
                    input_data = outputs.get(source_node_id)
                
                # Special handling for trigger nodes
                if node_type == 'trigger':
                    input_data = trigger_data or {}
                
                # Execute node
                try:
                    runner = self.runners.get(node_type)
                    if not runner:
                        raise ValueError(f"No runner found for node type: {node_type}")
                    
                    output, ctx_patch = runner(input_data, context, node_config)
                    outputs[node_id] = output
                    
                    # Update context
                    if ctx_patch:
                        context.update(ctx_patch)
                    
                    # Log success
                    execution_time = time.time() - node_start_time
                    logs.append(ExecutionLog(
                        node_id=node_id,
                        node_type=node_type,
                        node_name=node_name,
                        status="success",
                        start_time=datetime.fromtimestamp(node_start_time).isoformat(),
                        execution_time=execution_time,
                        input=input_data,
                        output=output,
                        context_patch=ctx_patch
                    ))
                    
                except Exception as e:
                    # Log error
                    execution_time = time.time() - node_start_time
                    logs.append(ExecutionLog(
                        node_id=node_id,
                        node_type=node_type,
                        node_name=node_name,
                        status="error",
                        start_time=datetime.fromtimestamp(node_start_time).isoformat(),
                        execution_time=execution_time,
                        input=input_data,
                        error=str(e)
                    ))
                    
                    # For now, stop execution on error (could be configurable)
                    break
            
            total_time = time.time() - start_time
            
            return ExecutionResult(
                success=len([log for log in logs if log.status == "error"]) == 0,
                logs=logs,
                outputs=outputs,
                context=context
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            logs.append(ExecutionLog(
                node_id="system",
                node_type="system",
                node_name="Workflow Engine",
                status="error",
                start_time=datetime.fromtimestamp(start_time).isoformat(),
                execution_time=total_time,
                error=str(e)
            ))
            
            return ExecutionResult(
                success=False,
                error=str(e),
                logs=logs
            )
    
    def validate_workflow(self, workflow_data: WorkflowPayload) -> Dict[str, Any]:
        """Validate workflow structure"""
        errors = []
        
        try:
            # Check for cycles
            graph, in_degree = self.build_graph(workflow_data.nodes, workflow_data.edges)
            execution_order = self.topological_sort(graph, in_degree)
            
            # Check for orphaned nodes
            connected_nodes = set()
            for edge in workflow_data.edges:
                connected_nodes.add(edge.source)
                connected_nodes.add(edge.target)
            
            all_nodes = {node.id for node in workflow_data.nodes}
            orphaned_nodes = all_nodes - connected_nodes
            
            if orphaned_nodes:
                errors.append(f"Orphaned nodes found: {orphaned_nodes}")
            
            # Check for valid node types
            valid_types = set(self.runners.keys())
            for node in workflow_data.nodes:
                if node.type not in valid_types:
                    errors.append(f"Invalid node type: {node.type}")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)]
            }
