"""Department model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Department(Base):
    """Department model for organizing equipment by hospital departments."""

    __tablename__ = "department"

    department_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    department_name = Column(String(100), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="department", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Department(id={self.department_id}, name='{self.department_name}')>"
