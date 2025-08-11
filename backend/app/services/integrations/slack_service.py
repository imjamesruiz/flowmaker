from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.oauth_manager import OAuthManager
import httpx


class SlackService:
    """Slack integration service for reading and sending messages"""
    
    def __init__(self, db: Session):
        self.db = db
        self.oauth_manager = OAuthManager(db)
        self.base_url = "https://slack.com/api"
    
    def get_messages(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get messages from Slack channel"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        channel_id = config.get("channel_id")
        if not channel_id:
            raise ValueError("Channel ID not configured")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {token.access_token}"}
                
                # Get channel history
                params = {
                    "channel": channel_id,
                    "limit": config.get("limit", 10)
                }
                
                response = client.get(
                    f"{self.base_url}/conversations.history",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                
                result = response.json()
                
                if not result.get("ok"):
                    raise Exception(f"Slack API error: {result.get('error')}")
                
                messages = result.get("messages", [])
                
                return {
                    "messages": messages,
                    "count": len(messages),
                    "channel_id": channel_id
                }
                
        except Exception as e:
            raise Exception(f"Failed to get Slack messages: {str(e)}")
    
    def send_message(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to Slack channel"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        channel_id = config.get("channel_id") or input_data.get("channel_id")
        message_text = config.get("message") or input_data.get("message")
        
        if not all([channel_id, message_text]):
            raise ValueError("Channel ID and message are required")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token.access_token}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "channel": channel_id,
                    "text": message_text
                }
                
                # Add optional parameters
                if config.get("username"):
                    data["username"] = config["username"]
                
                if config.get("icon_emoji"):
                    data["icon_emoji"] = config["icon_emoji"]
                
                response = client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                
                if not result.get("ok"):
                    raise Exception(f"Slack API error: {result.get('error')}")
                
                return {
                    "message_id": result["ts"],
                    "channel_id": channel_id,
                    "text": message_text,
                    "ok": result["ok"]
                }
                
        except Exception as e:
            raise Exception(f"Failed to send Slack message: {str(e)}")
    
    def send_rich_message(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send rich message with attachments to Slack"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        channel_id = config.get("channel_id") or input_data.get("channel_id")
        attachments = config.get("attachments") or input_data.get("attachments", [])
        
        if not channel_id:
            raise ValueError("Channel ID is required")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {token.access_token}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "channel": channel_id,
                    "attachments": attachments
                }
                
                response = client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                
                if not result.get("ok"):
                    raise Exception(f"Slack API error: {result.get('error')}")
                
                return {
                    "message_id": result["ts"],
                    "channel_id": channel_id,
                    "attachments_count": len(attachments),
                    "ok": result["ok"]
                }
                
        except Exception as e:
            raise Exception(f"Failed to send rich Slack message: {str(e)}")
    
    def get_channels(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of accessible Slack channels"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        try:
            with httpx.Client(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {token.access_token}"}
                
                response = client.get(
                    f"{self.base_url}/conversations.list",
                    headers=headers,
                    params={"types": "public_channel,private_channel"}
                )
                response.raise_for_status()
                
                result = response.json()
                
                if not result.get("ok"):
                    raise Exception(f"Slack API error: {result.get('error')}")
                
                channels = result.get("channels", [])
                
                return {
                    "channels": channels,
                    "count": len(channels)
                }
                
        except Exception as e:
            raise Exception(f"Failed to get Slack channels: {str(e)}")
    
    def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Slack connection"""
        integration_id = config.get("integration_id")
        if not integration_id:
            return {"status": "error", "message": "Integration ID not configured"}
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            return {"status": "error", "message": "No valid OAuth token found"}
        
        try:
            with httpx.Client(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {token.access_token}"}
                
                response = client.post(
                    f"{self.base_url}/auth.test",
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                if result.get("ok"):
                    return {
                        "status": "success",
                        "team": result.get("team"),
                        "user": result.get("user"),
                        "team_id": result.get("team_id"),
                        "user_id": result.get("user_id")
                    }
                else:
                    return {"status": "error", "message": result.get("error")}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)} 