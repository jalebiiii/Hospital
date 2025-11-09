"""CRUD operations package."""
from app.crud import (
    user,
    refresh_token,
    department,
    vendor,
    equipment,
    issue_report,
    discard_equipment
)

__all__ = [
    "user",
    "refresh_token",
    "department",
    "vendor",
    "equipment",
    "issue_report",
    "discard_equipment"
]
