"""Vendor model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vendor(Base):
    """Vendor model for equipment suppliers."""

    __tablename__ = "vendor"

    vendor_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vendor_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="vendor")

    def __repr__(self) -> str:
        return f"<Vendor(id={self.vendor_id}, name='{self.vendor_name}')>"
