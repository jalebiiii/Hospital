"""DiscardEquipment Pydantic schemas."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.schemas.equipment import EquipmentResponse


class DiscardEquipmentCreate(BaseModel):
    """Schema for creating a discard record."""
    equipment_id: int = Field(..., gt=0)
    reason: str = Field(..., min_length=1)
    media_url: Optional[str] = Field(None, max_length=500)
    date: date

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        """Validate that date is not in the future."""
        if v > date.today():
            raise ValueError("Discard date cannot be in the future")
        return v


class DiscardEquipmentUpdate(BaseModel):
    """Schema for updating a discard record."""
    reason: Optional[str] = Field(None, min_length=1)
    media_url: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None


class DiscardEquipmentResponse(BaseModel):
    """Schema for discard equipment response."""
    discard_id: int
    equipment_id: int
    equipment: Optional[EquipmentResponse] = None
    reason: str
    media_url: Optional[str]
    date: date
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
