from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.models.user import User
from app.models.jwt_token import JWTToken
from app.config import settings
from app.auth.security import verify_token


class JWTService:
    """Service for managing JWT tokens in the database"""
    
    @staticmethod
    def create_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create a new JWT token and store it in the database"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        
        # Create token payload
        to_encode = {
            "sub": user.email,
            "user_id": user.id,
            "exp": expire
        }
        
        # Encode JWT token
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return token, expire
    
    @staticmethod
    def store_token(db: Session, user: User, token: str, expires_at: datetime) -> JWTToken:
        """Store JWT token in the database"""
        db_token = JWTToken(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    @staticmethod
    def validate_token(db: Session, token: str) -> Optional[User]:
        """Validate JWT token and return user if valid"""
        try:
            # Decode the JWT token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if not email or not user_id:
                return None
            
            # Check if token exists in database and is not revoked
            db_token = db.query(JWTToken).filter(
                JWTToken.token == token,
                JWTToken.is_revoked == False
            ).first()
            
            if not db_token:
                return None
            
            # Check if token is expired
            if db_token.is_expired:
                return None
            
            # Get user
            user = db.query(User).filter(User.id == user_id, User.email == email).first()
            if not user or not user.is_active:
                return None
            
            return user
            
        except JWTError:
            return None
    
    @staticmethod
    def revoke_token(db: Session, token: str) -> bool:
        """Revoke a JWT token"""
        db_token = db.query(JWTToken).filter(JWTToken.token == token).first()
        if db_token:
            db_token.is_revoked = True
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> bool:
        """Revoke all tokens for a specific user"""
        db.query(JWTToken).filter(
            JWTToken.user_id == user_id,
            JWTToken.is_revoked == False
        ).update({"is_revoked": True})
        db.commit()
        return True
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Remove expired tokens from database"""
        expired_tokens = db.query(JWTToken).filter(
            JWTToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return expired_tokens
