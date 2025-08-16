from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.integration import Integration
from app.schemas.integration import IntegrationCreate, IntegrationUpdate, IntegrationResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.get("/integrations", response_model=List[IntegrationResponse])
def get_integrations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all integrations for current user"""
    integrations = db.query(Integration).filter(
        Integration.user_id == current_user.id
    ).all()
    return integrations


@router.post("/integrations", response_model=IntegrationResponse)
def create_integration(
    integration_data: IntegrationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new integration"""
    integration = Integration(
        **integration_data.dict(),
        user_id=current_user.id
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


@router.get("/integrations/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific integration"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    return integration


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an integration"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    for field, value in integration_data.dict(exclude_unset=True).items():
        setattr(integration, field, value)
    
    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/integrations/{integration_id}")
def delete_integration(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an integration"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    db.delete(integration)
    db.commit()
    return {"message": "Integration deleted successfully"}


@router.post("/integrations/{integration_id}/test")
def test_integration(
    integration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test an integration connection"""
    integration = db.query(Integration).filter(
        Integration.id == integration_id,
        Integration.user_id == current_user.id
    ).first()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    # Test connection based on provider
    try:
        if integration.provider == "gmail":
            from app.services.integrations.gmail_service import GmailService
            service = GmailService(db)
            result = service.test_connection({"integration_id": integration_id})
        elif integration.provider == "slack":
            from app.services.integrations.slack_service import SlackService
            service = SlackService(db)
            result = service.test_connection({"integration_id": integration_id})
        elif integration.provider == "sheets":
            from app.services.integrations.sheets_service import SheetsService
            service = SheetsService(db)
            result = service.test_connection({"integration_id": integration_id})
        else:
            result = {"status": "error", "message": "Unknown provider"}
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)} 