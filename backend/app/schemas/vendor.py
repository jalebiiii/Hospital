"""Vendor Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class VendorCreate(BaseModel):
    """Schema for creating a vendor."""
    vendor_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=100)
    address: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class VendorUpdate(BaseModel):
    """Schema for updating a vendor."""
    vendor_name: Optional[str] = Field(None, min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=100)
    address: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)


class VendorResponse(BaseModel):
    """Schema for vendor response."""
    vendor_id: int
    vendor_name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    category: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
