import os
import json
import httpx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.integrations.base_integration import BaseIntegration, integration_registry
from app.models.integration import Integration, OAuthToken


class SlackService(BaseIntegration):
    """Slack integration service"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.oauth_required = True
        self.base_url = "https://slack.com/api"
    
    def get_provider_name(self) -> str:
        return "slack"
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "send_message",
                "name": "Send Message",
                "description": "Send a message to a Slack channel",
                "schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "title": "Channel", "description": "Channel ID or name (e.g., #general)"},
                        "text": {"type": "string", "title": "Message Text", "description": "Message content"},
                        "blocks": {"type": "array", "title": "Blocks", "description": "Slack blocks for rich formatting"},
                        "attachments": {"type": "array", "title": "Attachments", "description": "Message attachments"},
                        "thread_ts": {"type": "string", "title": "Thread Timestamp", "description": "Reply in thread"}
                    },
                    "required": ["channel", "text"]
                }
            },
            {
                "type": "send_dm",
                "name": "Send Direct Message",
                "description": "Send a direct message to a user",
                "schema": {
                    "type": "object",
                    "properties": {
                        "user": {"type": "string", "title": "User ID", "description": "Slack user ID"},
                        "text": {"type": "string", "title": "Message Text", "description": "Message content"},
                        "blocks": {"type": "array", "title": "Blocks", "description": "Slack blocks for rich formatting"}
                    },
                    "required": ["user", "text"]
                }
            },
            {
                "type": "create_channel",
                "name": "Create Channel",
                "description": "Create a new Slack channel",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "title": "Channel Name", "description": "Channel name (without #)"},
                        "is_private": {"type": "boolean", "title": "Private Channel", "description": "Make channel private"}
                    },
                    "required": ["name"]
                }
            },
            {
                "type": "upload_file",
                "name": "Upload File",
                "description": "Upload a file to Slack",
                "schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "title": "Channel", "description": "Channel ID or name"},
                        "file_path": {"type": "string", "title": "File Path", "description": "Path to file to upload"},
                        "title": {"type": "string", "title": "Title", "description": "File title"},
                        "comment": {"type": "string", "title": "Comment", "description": "File comment"}
                    },
                    "required": ["channel", "file_path"]
                }
            }
        ]
    
    def get_available_triggers(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "new_message",
                "name": "New Message",
                "description": "Trigger when a new message is posted",
                "schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "title": "Channel", "description": "Channel to monitor"},
                        "keywords": {"type": "array", "title": "Keywords", "items": {"type": "string"}, "description": "Filter by keywords"},
                        "user": {"type": "string", "title": "User", "description": "Filter by specific user"}
                    }
                }
            },
            {
                "type": "reaction_added",
                "name": "Reaction Added",
                "description": "Trigger when a reaction is added to a message",
                "schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "title": "Channel", "description": "Channel to monitor"},
                        "reaction": {"type": "string", "title": "Reaction", "description": "Specific reaction to monitor"}
                    }
                }
            },
            {
                "type": "user_joined_channel",
                "name": "User Joined Channel",
                "description": "Trigger when a user joins a channel",
                "schema": {
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string", "title": "Channel", "description": "Channel to monitor"}
                    }
                }
            }
        ]
    
    def execute_action(self, action_type: str, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack action"""
        try:
            if action_type == "send_message":
                return self._send_message(config, input_data)
            elif action_type == "send_dm":
                return self._send_dm(config, input_data)
            elif action_type == "create_channel":
                return self._create_channel(config, input_data)
            elif action_type == "upload_file":
                return self._upload_file(config, input_data)
            else:
                raise ValueError(f"Unknown Slack action: {action_type}")
        except Exception as e:
            return self.handle_error(e)
    
    def test_connection(self, integration: Integration) -> Dict[str, Any]:
        """Test Slack connection"""
        try:
            # Get OAuth token
            token = self.get_oauth_token(integration.user_id, integration.id)
            if not token:
                return {"success": False, "error": "No valid OAuth token found"}
            
            # Test by getting team info
            headers = {"Authorization": f"Bearer {token.access_token}"}
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/team.info", headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if not data.get("ok"):
                    return {"success": False, "error": data.get("error", "Unknown error")}
                
                return {
                    "success": True,
                    "team_name": data["team"]["name"],
                    "team_id": data["team"]["id"]
                }
        except Exception as e:
            return self.handle_error(e)
    
    def _send_message(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Slack channel"""
        # Get OAuth token
        integration_id = config.get("integration_id")
        user_id = config.get("user_id")
        
        if not integration_id or not user_id:
            raise ValueError("integration_id and user_id are required")
        
        token = self.get_oauth_token(user_id, integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        # Prepare message data
        channel = config.get("channel") or input_data.get("channel")
        text = config.get("text") or input_data.get("text") or input_data.get("message")
        
        if not channel or not text:
            raise ValueError("channel and text are required")
        
        # Build payload
        payload = {
            "channel": channel,
            "text": text
        }
        
        if config.get("blocks"):
            payload["blocks"] = config["blocks"]
        if config.get("attachments"):
            payload["attachments"] = config["attachments"]
        if config.get("thread_ts"):
            payload["thread_ts"] = config["thread_ts"]
        
        # Send message
        headers = {"Authorization": f"Bearer {token.access_token}"}
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/chat.postMessage",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")
            
            return {
                "success": True,
                "ts": data["ts"],
                "channel": data["channel"],
                "message": text
            }
    
    def _send_dm(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send direct message to user"""
        # Similar to _send_message but uses chat.postMessage with user ID
        user = config.get("user") or input_data.get("user")
        text = config.get("text") or input_data.get("text") or input_data.get("message")
        
        if not user or not text:
            raise ValueError("user and text are required")
        
        # Use the same logic as _send_message but with user ID as channel
        config["channel"] = user
        return self._send_message(config, input_data)
    
    def _create_channel(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Slack channel"""
        # Get OAuth token
        integration_id = config.get("integration_id")
        user_id = config.get("user_id")
        
        if not integration_id or not user_id:
            raise ValueError("integration_id and user_id are required")
        
        token = self.get_oauth_token(user_id, integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        # Prepare channel data
        name = config.get("name") or input_data.get("name")
        is_private = config.get("is_private", False)
        
        if not name:
            raise ValueError("name is required")
        
        # Build payload
        payload = {
            "name": name,
            "is_private": is_private
        }
        
        # Create channel
        headers = {"Authorization": f"Bearer {token.access_token}"}
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/conversations.create",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                raise Exception(f"Slack API error: {data.get('error')}")
            
            return {
                "success": True,
                "channel_id": data["channel"]["id"],
                "channel_name": data["channel"]["name"],
                "is_private": data["channel"]["is_private"]
            }
    
    def _upload_file(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload file to Slack"""
        # Implementation for file upload
        # This would require handling file uploads and using files.upload API
        raise NotImplementedError("File upload not yet implemented")
    
    def format_input_data(self, node: WorkflowNode, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format input data for Slack actions"""
        formatted_data = {}
        
        for key, value in input_data.items():
            if isinstance(value, dict):
                # Look for Slack-related fields in nested data
                if "channel" in value:
                    formatted_data["channel"] = value["channel"]
                if "message" in value or "text" in value:
                    formatted_data["text"] = value.get("message") or value.get("text")
                if "user" in value:
                    formatted_data["user"] = value["user"]
            elif key in ["channel", "message", "text", "user"]:
                formatted_data[key] = value
        
        return formatted_data


# Register the integration
integration_registry.register(SlackService) 