from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.services.oauth_manager import OAuthManager
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class GmailService:
    """Gmail integration service for reading and sending emails"""
    
    def __init__(self, db: Session):
        self.db = db
        self.oauth_manager = OAuthManager(db)
    
    def get_new_emails(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get new emails from Gmail"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        # Build Gmail service
        credentials = Credentials(
            token.access_token,
            refresh_token=token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token.integration.config.get("client_id"),
            client_secret=token.integration.config.get("client_secret")
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get emails
        query = config.get("query", "is:unread")
        max_results = config.get("max_results", 10)
        
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_data = self._parse_email_message(msg)
                emails.append(email_data)
            
            return {
                "emails": emails,
                "count": len(emails)
            }
            
        except Exception as e:
            raise Exception(f"Failed to get emails: {str(e)}")
    
    def send_email(self, config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via Gmail"""
        integration_id = config.get("integration_id")
        if not integration_id:
            raise ValueError("Integration ID not configured")
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            raise ValueError("No valid OAuth token found")
        
        # Build Gmail service
        credentials = Credentials(
            token.access_token,
            refresh_token=token.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=token.integration.config.get("client_id"),
            client_secret=token.integration.config.get("client_secret")
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Prepare email
        to_email = config.get("to_email") or input_data.get("to_email")
        subject = config.get("subject") or input_data.get("subject")
        body = config.get("body") or input_data.get("body")
        
        if not all([to_email, subject, body]):
            raise ValueError("Email configuration incomplete")
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            
            msg = MIMEText(body)
            message.attach(msg)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            sent_message = service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return {
                "message_id": sent_message['id'],
                "thread_id": sent_message['threadId'],
                "to_email": to_email,
                "subject": subject
            }
            
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")
    
    def test_connection(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test Gmail connection"""
        integration_id = config.get("integration_id")
        if not integration_id:
            return {"status": "error", "message": "Integration ID not configured"}
        
        token = self.oauth_manager.get_valid_token(integration_id)
        if not token:
            return {"status": "error", "message": "No valid OAuth token found"}
        
        try:
            credentials = Credentials(
                token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=token.integration.config.get("client_id"),
                client_secret=token.integration.config.get("client_secret")
            )
            
            service = build('gmail', 'v1', credentials=credentials)
            
            # Test by getting profile
            profile = service.users().getProfile(userId='me').execute()
            
            return {
                "status": "success",
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal')
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _parse_email_message(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into readable format"""
        headers = msg['payload'].get('headers', [])
        header_dict = {h['name']: h['value'] for h in headers}
        
        # Extract body
        body = self._extract_email_body(msg['payload'])
        
        return {
            "id": msg['id'],
            "thread_id": msg['threadId'],
            "from": header_dict.get('From', ''),
            "to": header_dict.get('To', ''),
            "subject": header_dict.get('Subject', ''),
            "date": header_dict.get('Date', ''),
            "body": body,
            "snippet": msg.get('snippet', ''),
            "labels": msg.get('labelIds', [])
        }
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload"""
        if 'body' in payload and payload['body'].get('data'):
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if part['body'].get('data'):
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    if part['body'].get('data'):
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        
        return "" 