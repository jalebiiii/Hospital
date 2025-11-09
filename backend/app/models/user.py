"""User model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.user_id}, username='{self.username}', role={self.role.value})>"
