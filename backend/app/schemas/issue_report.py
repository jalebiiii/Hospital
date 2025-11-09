"""IssueReport Pydantic schemas."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.enums import IssueType, IssueStatus
from app.schemas.equipment import EquipmentResponse


class IssueReportCreate(BaseModel):
    """Schema for creating an issue report."""
    equipment_id: int = Field(..., gt=0)
    issue_type: IssueType
    problem_description: str = Field(..., min_length=1)
    media_url: Optional[str] = Field(None, max_length=500)
    date_raised: Optional[datetime] = None
    status: IssueStatus = Field(default=IssueStatus.OPEN)
    technician: Optional[str] = Field(None, max_length=100)


class IssueReportUpdate(BaseModel):
    """Schema for updating an issue report."""
    issue_type: Optional[IssueType] = None
    problem_description: Optional[str] = Field(None, min_length=1)
    media_url: Optional[str] = Field(None, max_length=500)
    status: Optional[IssueStatus] = None
    technician: Optional[str] = Field(None, max_length=100)


class IssueReportResponse(BaseModel):
    """Schema for issue report response."""
    issue_id: int
    equipment_id: int
    equipment: Optional[EquipmentResponse] = None
    issue_type: IssueType
    problem_description: str
    media_url: Optional[str]
    date_raised: datetime
    status: IssueStatus
    technician: Optional[str]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
