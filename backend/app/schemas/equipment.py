"""Equipment Pydantic schemas."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.enums import EquipmentStatus
from app.schemas.department import DepartmentResponse
from app.schemas.vendor import VendorResponse


class EquipmentCreate(BaseModel):
    """Schema for creating equipment."""
    equipment_name: str = Field(..., min_length=1, max_length=200)
    serial_number: Optional[str] = Field(None, max_length=100)
    model_no: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=200)
    department_id: int = Field(..., gt=0)
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: EquipmentStatus = Field(default=EquipmentStatus.WORKING)
    vendor_id: Optional[int] = Field(None, gt=0)
    quantity: int = Field(default=1, ge=0)

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that expiry_date is after purchase_date if both provided."""
        if v is not None and info.data.get("purchase_date") is not None:
            if v < info.data["purchase_date"]:
                raise ValueError("expiry_date must be on or after purchase_date")
        return v


class EquipmentUpdate(BaseModel):
    """Schema for updating equipment."""
    equipment_name: Optional[str] = Field(None, min_length=1, max_length=200)
    serial_number: Optional[str] = Field(None, max_length=100)
    model_no: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=200)
    department_id: Optional[int] = Field(None, gt=0)
    purchase_date: Optional[date] = None
    expiry_date: Optional[date] = None
    status: Optional[EquipmentStatus] = None
    vendor_id: Optional[int] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)


class EquipmentResponse(BaseModel):
    """Schema for equipment response."""
    equipment_id: int
    equipment_name: str
    serial_number: Optional[str]
    model_no: Optional[str]
    manufacturer: Optional[str]
    department_id: int
    department: Optional[DepartmentResponse] = None
    purchase_date: Optional[date]
    expiry_date: Optional[date]
    status: EquipmentStatus
    vendor_id: Optional[int]
    vendor: Optional[VendorResponse] = None
    quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
