from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.workflow import WorkflowNode
from app.services.integrations.gmail_service import GmailService
from app.services.integrations.slack_service import SlackService
from app.services.integrations.sheets_service import SheetsService


class NodeExecutor:
    """Executes different types of workflow nodes"""
    
    def __init__(self, db: Session):
        self.db = db
        self.gmail_service = GmailService(db)
        self.slack_service = SlackService(db)
        self.sheets_service = SheetsService(db)
    
    def execute_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow node based on its type"""
        node_type = node.node_type.lower()
        
        if node_type == "trigger":
            return self._execute_trigger_node(node, input_data)
        elif node_type == "action":
            return self._execute_action_node(node, input_data)
        elif node_type == "condition":
            return self._execute_condition_node(node, input_data)
        elif node_type == "transformer":
            return self._execute_transformer_node(node, input_data)
        elif node_type == "webhook":
            return self._execute_webhook_node(node, input_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def test_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a workflow node without performing actual operations"""
        node_type = node.node_type.lower()
        
        if node_type == "trigger":
            return self._test_trigger_node(node, input_data)
        elif node_type == "action":
            return self._test_action_node(node, input_data)
        elif node_type == "condition":
            return self._test_condition_node(node, input_data)
        elif node_type == "transformer":
            return self._test_transformer_node(node, input_data)
        elif node_type == "webhook":
            return self._test_webhook_node(node, input_data)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def _execute_trigger_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trigger node"""
        config = node.config or {}
        trigger_type = config.get("trigger_type", "")
        
        if trigger_type == "gmail_new_email":
            return self.gmail_service.get_new_emails(config)
        elif trigger_type == "slack_message":
            return self.slack_service.get_messages(config)
        elif trigger_type == "webhook":
            return {"webhook_data": input_data.get("webhook_data", {})}
        elif trigger_type == "schedule":
            return {"scheduled_time": input_data.get("scheduled_time")}
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
    
    def _execute_action_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action node"""
        config = node.config or {}
        action_type = config.get("action_type", "")
        
        if action_type == "gmail_send_email":
            return self.gmail_service.send_email(config, input_data)
        elif action_type == "slack_send_message":
            return self.slack_service.send_message(config, input_data)
        elif action_type == "sheets_update":
            return self.sheets_service.update_sheet(config, input_data)
        elif action_type == "http_request":
            return self._execute_http_request(config, input_data)
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
        """Execute a data transformer node"""
        config = node.config or {}
        transform_type = config.get("transform_type", "")
        
        if transform_type == "json_path":
            return self._transform_json_path(config, input_data)
        elif transform_type == "template":
            return self._transform_template(config, input_data)
        elif transform_type == "filter":
            return self._transform_filter(config, input_data)
        else:
            raise ValueError(f"Unknown transform type: {transform_type}")
    
    def _execute_webhook_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a webhook node"""
        config = node.config or {}
        webhook_url = config.get("webhook_url")
        
        if not webhook_url:
            raise ValueError("Webhook URL not configured")
        
        import httpx
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(webhook_url, json=input_data)
                response.raise_for_status()
                return {
                    "status_code": response.status_code,
                    "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
        except Exception as e:
            raise Exception(f"Webhook request failed: {str(e)}")
    
    def _test_trigger_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a trigger node"""
        config = node.config or {}
        trigger_type = config.get("trigger_type", "")
        
        if trigger_type == "gmail_new_email":
            return self.gmail_service.test_connection(config)
        elif trigger_type == "slack_message":
            return self.slack_service.test_connection(config)
        elif trigger_type == "webhook":
            return {"status": "webhook_ready"}
        elif trigger_type == "schedule":
            return {"status": "schedule_configured"}
        else:
            return {"status": "unknown_trigger"}
    
    def _test_action_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test an action node"""
        config = node.config or {}
        action_type = config.get("action_type", "")
        
        if action_type == "gmail_send_email":
            return self.gmail_service.test_connection(config)
        elif action_type == "slack_send_message":
            return self.slack_service.test_connection(config)
        elif action_type == "sheets_update":
            return self.sheets_service.test_connection(config)
        elif action_type == "http_request":
            return {"status": "http_request_configured"}
        else:
            return {"status": "unknown_action"}
    
    def _test_condition_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a condition node"""
        return {"status": "condition_configured"}
    
    def _test_transformer_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a transformer node"""
        return {"status": "transformer_configured"}
    
    def _test_webhook_node(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a webhook node"""
        config = node.config or {}
        webhook_url = config.get("webhook_url")
        
        if not webhook_url:
            return {"status": "webhook_url_missing"}
        
        return {"status": "webhook_configured", "url": webhook_url}
    
    def _execute_http_request(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an HTTP request"""
        import httpx
        
        method = config.get("method", "GET").upper()
        url = config.get("url")
        headers = config.get("headers", {})
        body = config.get("body")
        
        if not url:
            raise ValueError("HTTP request URL not configured")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                elif method == "POST":
                    response = client.post(url, headers=headers, json=body)
                elif method == "PUT":
                    response = client.put(url, headers=headers, json=body)
                elif method == "DELETE":
                    response = client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return {
                    "status_code": response.status_code,
                    "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
        except Exception as e:
            raise Exception(f"HTTP request failed: {str(e)}")
    
    def _evaluate_simple_condition(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a simple condition"""
        field = config.get("field")
        operator = config.get("operator")
        value = config.get("value")
        
        if not all([field, operator, value]):
            raise ValueError("Condition configuration incomplete")
        
        # Extract field value from input data
        field_value = self._extract_field_value(field, input_data)
        
        # Evaluate condition
        result = self._compare_values(field_value, operator, value)
        
        return {
            "condition_result": result,
            "field_value": field_value,
            "operator": operator,
            "expected_value": value
        }
    
    def _evaluate_advanced_condition(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate an advanced condition with multiple rules"""
        rules = config.get("rules", [])
        
        if not rules:
            raise ValueError("No rules configured for advanced condition")
        
        results = []
        for rule in rules:
            field = rule.get("field")
            operator = rule.get("operator")
            value = rule.get("value")
            
            if all([field, operator, value]):
                field_value = self._extract_field_value(field, input_data)
                rule_result = self._compare_values(field_value, operator, value)
                results.append({
                    "rule": rule,
                    "result": rule_result,
                    "field_value": field_value
                })
        
        # Apply logical operators (AND/OR)
        logical_operator = config.get("logical_operator", "AND")
        final_result = all(r["result"] for r in results) if logical_operator == "AND" else any(r["result"] for r in results)
        
        return {
            "condition_result": final_result,
            "rule_results": results,
            "logical_operator": logical_operator
        }
    
    def _transform_json_path(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data using JSON path expressions"""
        import jsonpath_ng as jsonpath
        
        json_path = config.get("json_path")
        if not json_path:
            raise ValueError("JSON path not configured")
        
        try:
            jsonpath_expr = jsonpath.parse(json_path)
            matches = [match.value for match in jsonpath_expr.find(input_data)]
            
            return {
                "transformed_data": matches[0] if len(matches) == 1 else matches
            }
        except Exception as e:
            raise Exception(f"JSON path transformation failed: {str(e)}")
    
    def _transform_template(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data using template strings"""
        template = config.get("template")
        if not template:
            raise ValueError("Template not configured")
        
        try:
            # Simple template replacement
            result = template
            for key, value in input_data.items():
                placeholder = f"{{{{{key}}}}}"
                if isinstance(value, (dict, list)):
                    value = str(value)
                result = result.replace(placeholder, str(value))
            
            return {
                "transformed_data": result
            }
        except Exception as e:
            raise Exception(f"Template transformation failed: {str(e)}")
    
    def _transform_filter(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on conditions"""
        filter_condition = config.get("filter_condition")
        if not filter_condition:
            raise ValueError("Filter condition not configured")
        
        try:
            # Simple filtering - this could be enhanced with more complex logic
            filtered_data = []
            for item in input_data.get("data", []):
                if self._evaluate_filter_condition(item, filter_condition):
                    filtered_data.append(item)
            
            return {
                "transformed_data": filtered_data
            }
        except Exception as e:
            raise Exception(f"Filter transformation failed: {str(e)}")
    
    def _extract_field_value(self, field: str, data: Dict[str, Any]) -> Any:
        """Extract field value from nested data structure"""
        keys = field.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    def _compare_values(self, field_value: Any, operator: str, expected_value: Any) -> bool:
        """Compare values using different operators"""
        if operator == "equals":
            return field_value == expected_value
        elif operator == "not_equals":
            return field_value != expected_value
        elif operator == "contains":
            return str(expected_value) in str(field_value)
        elif operator == "not_contains":
            return str(expected_value) not in str(field_value)
        elif operator == "greater_than":
            return field_value > expected_value
        elif operator == "less_than":
            return field_value < expected_value
        elif operator == "greater_than_or_equal":
            return field_value >= expected_value
        elif operator == "less_than_or_equal":
            return field_value <= expected_value
        else:
            return False
    
    def _evaluate_filter_condition(self, item: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate a filter condition on an item"""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if not all([field, operator, value]):
            return True
        
        field_value = self._extract_field_value(field, item)
        return self._compare_values(field_value, operator, value) 