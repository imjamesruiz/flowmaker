from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowNode, NodeType
from app.services.integrations.base_integration import integration_registry
from app.models.integration import Integration


class NodeExecutor:
    """Executes different types of workflow nodes"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow node based on its type"""
        node_type = node.node_type
        
        if node_type == NodeType.TRIGGER:
            return self._execute_trigger_node(node, input_data)
        elif node_type == NodeType.ACTION:
            return self._execute_action_node(node, input_data)
        elif node_type == NodeType.CONDITION:
            return self._execute_condition_node(node, input_data)
        elif node_type == NodeType.TRANSFORMER:
            return self._execute_transformer_node(node, input_data)
        elif node_type == NodeType.WEBHOOK:
            return self._execute_webhook_node(node, input_data)
        elif node_type == NodeType.DELAY:
            return self._execute_delay_node(node, input_data)
        elif node_type == NodeType.LOOP:
            return self._execute_loop_node(node, input_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def test_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a workflow node without actually executing it"""
        try:
            # For testing, we'll simulate the execution
            if node.node_type == NodeType.ACTION:
                return self._test_action_node(node, input_data)
            else:
                # For non-action nodes, just return the input data
                return {
                    "success": True,
                    "result": input_data,
                    "test_mode": True
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_mode": True
            }
    
    def _execute_trigger_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trigger node"""
        config = node.config or {}
        trigger_type = config.get("trigger_type", "")
        
        if trigger_type == "webhook":
            return self._execute_webhook_trigger(config, input_data)
        elif trigger_type == "schedule":
            return self._execute_schedule_trigger(config, input_data)
        elif trigger_type == "manual":
            return self._execute_manual_trigger(config, input_data)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
    
    def _execute_action_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action node"""
        config = node.config or {}
        action_type = config.get("action_type", "")
        integration_provider = config.get("integration_provider", "")
        
        # Get integration instance
        if integration_provider:
            integration = integration_registry.get_integration(integration_provider, self.db)
            if not integration:
                raise ValueError(f"Integration provider '{integration_provider}' not found")
            
            # Add integration and user context to config
            config["integration_id"] = node.integration_id
            config["user_id"] = node.workflow.owner_id
            
            # Format input data for the integration
            formatted_input = integration.format_input_data(node, input_data)
            
            # Execute the action
            result = integration.execute_action(action_type, config, formatted_input)
            
            # Format output data
            return integration.format_output_data(result)
        else:
            # Handle built-in actions
            if action_type == "http_request":
                return self._execute_http_request(config, input_data)
            elif action_type == "data_transform":
                return self._execute_data_transform(config, input_data)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
    
    def _execute_condition_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a condition node"""
        config = node.config or {}
        condition_type = config.get("condition_type", "simple")
        
        if condition_type == "simple":
            return self._evaluate_simple_condition(config, input_data)
        elif condition_type == "advanced":
            return self._evaluate_advanced_condition(config, input_data)
        else:
            raise ValueError(f"Unknown condition type: {condition_type}")
    
    def _execute_transformer_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a transformer node"""
        config = node.config or {}
        transform_type = config.get("transform_type", "map")
        
        if transform_type == "map":
            return self._execute_data_mapping(config, input_data)
        elif transform_type == "filter":
            return self._execute_data_filtering(config, input_data)
        elif transform_type == "aggregate":
            return self._execute_data_aggregation(config, input_data)
        else:
            raise ValueError(f"Unknown transform type: {transform_type}")
    
    def _execute_webhook_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a webhook node"""
        config = node.config or {}
        webhook_type = config.get("webhook_type", "outgoing")
        
        if webhook_type == "outgoing":
            return self._execute_outgoing_webhook(config, input_data)
        elif webhook_type == "incoming":
            return self._execute_incoming_webhook(config, input_data)
        else:
            raise ValueError(f"Unknown webhook type: {webhook_type}")
    
    def _execute_delay_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a delay node"""
        config = node.config or {}
        delay_seconds = config.get("delay_seconds", 0)
        
        import time
        time.sleep(delay_seconds)
        
        return {
            "success": True,
            "result": input_data,
            "delay_seconds": delay_seconds
        }
    
    def _execute_loop_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a loop node"""
        config = node.config or {}
        loop_type = config.get("loop_type", "for_each")
        
        if loop_type == "for_each":
            return self._execute_for_each_loop(config, input_data)
        elif loop_type == "while":
            return self._execute_while_loop(config, input_data)
        else:
            raise ValueError(f"Unknown loop type: {loop_type}")
    
    def _test_action_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test an action node"""
        config = node.config or {}
        integration_provider = config.get("integration_provider", "")
        
        if integration_provider:
            integration = integration_registry.get_integration(integration_provider, self.db)
            if integration:
                # Test the integration connection
                if node.integration_id:
                    integration_obj = self.db.query(Integration).filter(Integration.id == node.integration_id).first()
                    if integration_obj:
                        test_result = integration.test_connection(integration_obj)
                        return {
                            "success": test_result.get("success", False),
                            "result": test_result,
                            "test_mode": True
                        }
        
        # Default test response
        return {
            "success": True,
            "result": input_data,
            "test_mode": True
        }
    
    # Helper methods for different node types
    def _execute_webhook_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute webhook trigger"""
        return {
            "success": True,
            "result": input_data,
            "trigger_type": "webhook"
        }
    
    def _execute_schedule_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute schedule trigger"""
        return {
            "success": True,
            "result": input_data,
            "trigger_type": "schedule"
        }
    
    def _execute_manual_trigger(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute manual trigger"""
        return {
            "success": True,
            "result": input_data,
            "trigger_type": "manual"
        }
    
    def _execute_http_request(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request"""
        import httpx
        
        url = config.get("url")
        method = config.get("method", "GET")
        headers = config.get("headers", {})
        body = config.get("body")
        
        if not url:
            raise ValueError("URL is required for HTTP request")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = client.post(url, headers=headers, json=body)
                elif method.upper() == "PUT":
                    response = client.put(url, headers=headers, json=body)
                elif method.upper() == "DELETE":
                    response = client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _execute_data_transform(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data transformation"""
        transform_type = config.get("transform_type", "map")
        
        if transform_type == "map":
            mapping = config.get("mapping", {})
            result = {}
            for key, value in input_data.items():
                if key in mapping:
                    result[mapping[key]] = value
                else:
                    result[key] = value
            return {"success": True, "result": result}
        else:
            raise ValueError(f"Unknown transform type: {transform_type}")
    
    def _evaluate_simple_condition(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate simple condition"""
        field = config.get("field")
        operator = config.get("operator", "equals")
        value = config.get("value")
        
        if field not in input_data:
            return {"success": True, "result": False}
        
        actual_value = input_data[field]
        
        if operator == "equals":
            result = actual_value == value
        elif operator == "not_equals":
            result = actual_value != value
        elif operator == "contains":
            result = value in str(actual_value)
        elif operator == "greater_than":
            result = actual_value > value
        elif operator == "less_than":
            result = actual_value < value
        else:
            raise ValueError(f"Unknown operator: {operator}")
        
        return {"success": True, "result": result}
    
    def _evaluate_advanced_condition(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate advanced condition"""
        # This would implement more complex conditional logic
        # For now, return the input data
        return {"success": True, "result": input_data}
    
    def _execute_data_mapping(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data mapping transformation"""
        mapping = config.get("mapping", {})
        result = {}
        
        for target_key, source_config in mapping.items():
            if isinstance(source_config, str):
                # Direct mapping
                if source_config in input_data:
                    result[target_key] = input_data[source_config]
            elif isinstance(source_config, dict):
                # Complex mapping with transformation
                source_key = source_config.get("source")
                transform = source_config.get("transform")
                
                if source_key in input_data:
                    value = input_data[source_key]
                    
                    if transform == "uppercase":
                        value = str(value).upper()
                    elif transform == "lowercase":
                        value = str(value).lower()
                    elif transform == "trim":
                        value = str(value).strip()
                    
                    result[target_key] = value
        
        return {"success": True, "result": result}
    
    def _execute_data_filtering(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data filtering transformation"""
        # Implementation for data filtering
        return {"success": True, "result": input_data}
    
    def _execute_data_aggregation(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data aggregation transformation"""
        # Implementation for data aggregation
        return {"success": True, "result": input_data}
    
    def _execute_outgoing_webhook(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute outgoing webhook"""
        # This would be similar to HTTP request
        return self._execute_http_request(config, input_data)
    
    def _execute_incoming_webhook(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute incoming webhook"""
        # This would handle incoming webhook data
        return {"success": True, "result": input_data}
    
    def _execute_for_each_loop(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute for-each loop"""
        # Implementation for for-each loop
        return {"success": True, "result": input_data}
    
    def _execute_while_loop(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute while loop"""
        # Implementation for while loop
        return {"success": True, "result": input_data} 