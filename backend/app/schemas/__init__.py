"""Schemas package."""
from app.schemas.common import (
    PaginationMeta,
    PaginatedResponse,
    ApiResponse,
    ErrorResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    TokenData,
)
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.schemas.vendor import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
)
from app.schemas.equipment import (
    EquipmentCreate,
    EquipmentUpdate,
    EquipmentResponse,
)
from app.schemas.issue_report import (
    IssueReportCreate,
    IssueReportUpdate,
    IssueReportResponse,
)
from app.schemas.discard_equipment import (
    DiscardEquipmentCreate,
    DiscardEquipmentUpdate,
    DiscardEquipmentResponse,
)

__all__ = [
    "PaginationMeta",
    "PaginatedResponse",
    "ApiResponse",
    "ErrorResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "TokenResponse",
    "TokenData",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentResponse",
    "VendorCreate",
    "VendorUpdate",
    "VendorResponse",
    "EquipmentCreate",
    "EquipmentUpdate",
    "EquipmentResponse",
    "IssueReportCreate",
    "IssueReportUpdate",
    "IssueReportResponse",
    "DiscardEquipmentCreate",
    "DiscardEquipmentUpdate",
    "DiscardEquipmentResponse",
]
