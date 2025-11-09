"""Enum definitions for database models."""
import enum


class EquipmentStatus(str, enum.Enum):
    """Equipment status enum."""
    WORKING = "WORKING"
    UNDER_REPAIR = "UNDER_REPAIR"
    EXPIRED = "EXPIRED"
    DECOMMISSIONED = "DECOMMISSIONED"


class IssueType(str, enum.Enum):
    """Issue type enum."""
    TECHNICAL = "TECHNICAL"
    MECHANICAL = "MECHANICAL"
    ELECTRICAL = "ELECTRICAL"
    USER_OPERATION = "USER_OPERATION"


class IssueStatus(str, enum.Enum):
    """Issue status enum."""
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class UserRole(str, enum.Enum):
    """User role enum."""
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    VIEWER = "VIEWER"
