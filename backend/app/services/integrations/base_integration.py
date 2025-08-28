from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.integration import Integration, OAuthToken
from app.models.workflow import WorkflowNode


class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.provider_name = self.get_provider_name()
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'gmail', 'slack')"""
        pass
    
    @abstractmethod
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Return list of available actions for this integration"""
        pass
    
    @abstractmethod
    def get_available_triggers(self) -> List[Dict[str, Any]]:
        """Return list of available triggers for this integration"""
        pass
    
    @abstractmethod
    def execute_action(self, action_type: str, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action"""
        pass
    
    @abstractmethod
    def test_connection(self, integration: Integration) -> Dict[str, Any]:
        """Test the integration connection"""
        pass
    
    def get_oauth_token(self, user_id: int, integration_id: int) -> Optional[OAuthToken]:
        """Get valid OAuth token for user and integration"""
        return self.db.query(OAuthToken).filter(
            OAuthToken.user_id == user_id,
            OAuthToken.integration_id == integration_id,
            OAuthToken.is_valid == True
        ).first()
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate integration configuration"""
        return {"valid": True, "errors": []}
    
    def get_action_schema(self, action_type: str) -> Dict[str, Any]:
        """Get JSON schema for action configuration"""
        actions = self.get_available_actions()
        for action in actions:
            if action["type"] == action_type:
                return action.get("schema", {})
        return {}
    
    def get_trigger_schema(self, trigger_type: str) -> Dict[str, Any]:
        """Get JSON schema for trigger configuration"""
        triggers = self.get_available_triggers()
        for trigger in triggers:
            if trigger["type"] == trigger_type:
                return trigger.get("schema", {})
        return {}
    
    def format_input_data(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format input data for the integration"""
        # Default implementation - can be overridden by specific integrations
        return input_data
    
    def format_output_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format output data from the integration"""
        # Default implementation - can be overridden by specific integrations
        return result
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Handle integration-specific errors"""
        return {
            "success": False,
            "error": str(error),
            "error_type": type(error).__name__
        }


class IntegrationRegistry:
    """Registry for managing all available integrations"""
    
    def __init__(self):
        self._integrations = {}
    
    def register(self, integration_class: type):
        """Register an integration class"""
        instance = integration_class(None)  # Create temporary instance to get provider name
        self._integrations[instance.get_provider_name()] = integration_class
    
    def get_integration(self, provider_name: str, db: Session) -> Optional[BaseIntegration]:
        """Get integration instance by provider name"""
        if provider_name in self._integrations:
            return self._integrations[provider_name](db)
        return None
    
    def get_all_providers(self) -> List[str]:
        """Get list of all available providers"""
        return list(self._integrations.keys())
    
    def get_integration_info(self, provider_name: str) -> Dict[str, Any]:
        """Get integration information"""
        if provider_name in self._integrations:
            integration_class = self._integrations[provider_name]
            # Create temporary instance to get info
            temp_db = None
            instance = integration_class(temp_db)
            return {
                "provider": provider_name,
                "actions": instance.get_available_actions(),
                "triggers": instance.get_available_triggers(),
                "oauth_required": hasattr(instance, 'oauth_required') and instance.oauth_required
            }
        return {}


# Global registry instance
integration_registry = IntegrationRegistry()
