"""Refresh token model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.core.database import Base


class RefreshToken(Base):
    """Refresh token model for managing JWT refresh tokens."""

    __tablename__ = "refresh_token"

    token_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    token_hash = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, nullable=False, default=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.token_id}, user_id={self.user_id}, revoked={self.revoked})>"
