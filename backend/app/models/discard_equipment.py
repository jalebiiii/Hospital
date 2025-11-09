"""Discard equipment model."""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DiscardEquipment(Base):
    """Discard equipment model for tracking disposed equipment."""

    __tablename__ = "discard_equipment"

    discard_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(
        Integer,
        ForeignKey("equipment.equipment_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    reason = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="discard_record")

    def __repr__(self) -> str:
        return f"<DiscardEquipment(id={self.discard_id}, equipment_id={self.equipment_id}, date={self.date})>"
