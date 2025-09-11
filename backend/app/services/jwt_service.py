from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.models.user import User
from app.models.jwt_token import JWTToken
from app.config import settings


class JWTService:
    """Service for managing JWT tokens. We persist refresh tokens for rotation/revocation.

    Access tokens are short-lived and are not stored server-side.
    """

    @staticmethod
    def _encode_token(payload: dict) -> str:
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_access_token(user: User, expires_minutes: Optional[int] = None) -> Tuple[str, datetime]:
        """Create a short-lived access token."""
        if expires_minutes is None:
            expires_minutes = 15
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload = {
            "sub": user.email,
            "user_id": user.id,
            "type": "access",
            "exp": expire,
        }
        return JWTService._encode_token(payload), expire

    @staticmethod
    def create_refresh_token(user: User, expires_days: Optional[int] = None) -> Tuple[str, datetime]:
        """Create a long-lived refresh token and return token + expiry."""
        if expires_days is None:
            expires_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        expire = datetime.utcnow() + timedelta(days=expires_days)
        payload = {
            "sub": user.email,
            "user_id": user.id,
            "type": "refresh",
            "exp": expire,
        }
        return JWTService._encode_token(payload), expire

    @staticmethod
    def store_refresh_token(db: Session, user: User, token: str, expires_at: datetime) -> JWTToken:
        """Persist a refresh token for rotation/revocation."""
        db_token = JWTToken(token=token, user_id=user.id, expires_at=expires_at)
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token

    @staticmethod
    def revoke_refresh_token(db: Session, token: str) -> bool:
        record = db.query(JWTToken).filter(JWTToken.token == token).first()
        if record:
            record.is_revoked = True
            db.commit()
            return True
        return False

    @staticmethod
    def revoke_all_user_refresh_tokens(db: Session, user_id: int) -> bool:
        db.query(JWTToken).filter(JWTToken.user_id == user_id, JWTToken.is_revoked == False).update({"is_revoked": True})
        db.commit()
        return True

    @staticmethod
    def validate_token(db: Session, token: str) -> Optional[User]:
        """Validate an access token and return the associated user if valid."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "access":
                return None
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if not email or not user_id:
                return None
            user = db.query(User).filter(User.id == user_id, User.email == email).first()
            if not user or not user.is_active:
                return None
            return user
        except JWTError:
            return None

    @staticmethod
    def validate_refresh_token(db: Session, token: str) -> Optional[User]:
        """Validate a refresh token against DB and return the associated user if valid."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "refresh":
                return None
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            if not email or not user_id:
                return None
            db_token = db.query(JWTToken).filter(JWTToken.token == token, JWTToken.is_revoked == False).first()
            if not db_token or db_token.is_expired:
                return None
            user = db.query(User).filter(User.id == user_id, User.email == email).first()
            if not user or not user.is_active:
                return None
            return user
        except JWTError:
            return None

    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """Remove expired refresh tokens from database."""
        removed = db.query(JWTToken).filter(JWTToken.expires_at < datetime.utcnow()).delete()
        db.commit()
        return removed
