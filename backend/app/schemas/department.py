"""Department Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    """Schema for creating a department."""
    department_name: str = Field(..., min_length=1, max_length=100)


class DepartmentUpdate(BaseModel):
    """Schema for updating a department."""
    department_name: Optional[str] = Field(None, min_length=1, max_length=100)


class DepartmentResponse(BaseModel):
    """Schema for department response."""
    department_id: int
    department_name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
