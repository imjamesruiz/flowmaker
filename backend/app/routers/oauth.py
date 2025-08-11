from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.integration import Integration, OAuthToken
from app.schemas.integration import OAuthCallback, OAuthUrlResponse
from app.auth.dependencies import get_current_active_user
from app.services.oauth_manager import OAuthManager
from app.config import settings
import secrets
import httpx

router = APIRouter()


@router.get("/google/auth-url", response_model=OAuthUrlResponse)
def get_google_auth_url(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get Google OAuth authorization URL"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id,
        Integration.provider == "gmail"
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    state = secrets.token_urlsafe(32)
    
    # Store state in integration config for verification
    config = integration.config or {}
    config["oauth_state"] = state
    integration.config = config
    db.commit()
    
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        "response_type=code&"
        "scope=https://www.googleapis.com/auth/gmail.readonly "
        "https://www.googleapis.com/auth/gmail.send "
        "https://www.googleapis.com/auth/spreadsheets "
        "https://www.googleapis.com/auth/drive&"
        "redirect_uri=http://localhost:8000/api/v1/oauth/google/callback&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}


@router.get("/slack/auth-url", response_model=OAuthUrlResponse)
def get_slack_auth_url(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get Slack OAuth authorization URL"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id,
        Integration.provider == "slack"
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    state = secrets.token_urlsafe(32)
    
    # Store state in integration config for verification
    config = integration.config or {}
    config["oauth_state"] = state
    integration.config = config
    db.commit()
    
    auth_url = (
        "https://slack.com/oauth/v2/authorize?"
        f"client_id={settings.SLACK_CLIENT_ID}&"
        "scope=channels:read,chat:write,channels:history&"
        "redirect_uri=http://localhost:8000/api/v1/oauth/slack/callback&"
        f"state={state}"
    )
    
    return {"auth_url": auth_url, "state": state}


@router.get("/google/callback")
async def google_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    # Find integration by state
    integration = db.query(Integration).filter(
        Integration.config.contains({"oauth_state": state})
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:8000/api/v1/oauth/google/callback"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
        
        # Store tokens
        oauth_manager = OAuthManager(db)
        oauth_token = oauth_manager.create_token(
            user_id=integration.user_id,
            integration_id=integration.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
            scope=token_data.get("scope")
        )
        
        # Clear state from config
        config = integration.config
        config.pop("oauth_state", None)
        integration.config = config
        db.commit()
        
        return {
            "message": "Google OAuth successful",
            "integration_id": integration.id,
            "provider": "gmail"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth token exchange failed: {str(e)}"
        )


@router.get("/slack/callback")
async def slack_oauth_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Slack OAuth callback"""
    # Find integration by state
    integration = db.query(Integration).filter(
        Integration.config.contains({"oauth_state": state})
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )
    
    # Exchange code for tokens
    token_url = "https://slack.com/api/oauth.v2.access"
    data = {
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
        "code": code,
        "redirect_uri": "http://localhost:8000/api/v1/oauth/slack/callback"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
        
        if not token_data.get("ok"):
            raise Exception(token_data.get("error", "Unknown error"))
        
        # Store tokens
        oauth_manager = OAuthManager(db)
        oauth_token = oauth_manager.create_token(
            user_id=integration.user_id,
            integration_id=integration.id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_in=token_data.get("expires_in"),
            scope=token_data.get("scope")
        )
        
        # Clear state from config
        config = integration.config
        config.pop("oauth_state", None)
        integration.config = config
        db.commit()
        
        return {
            "message": "Slack OAuth successful",
            "integration_id": integration.id,
            "provider": "slack"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth token exchange failed: {str(e)}"
        )


@router.delete("/tokens/{token_id}")
def revoke_token(
    token_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Revoke an OAuth token"""
    token = db.query(OAuthToken).join(Integration).filter(
        OAuthToken.id == token_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    oauth_manager = OAuthManager(db)
    success = oauth_manager.invalidate_token(token_id)
    
    if success:
        return {"message": "Token revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke token"
        ) 