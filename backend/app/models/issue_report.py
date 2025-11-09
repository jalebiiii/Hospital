"""Issue report model."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import IssueType, IssueStatus


class IssueReport(Base):
    """Issue report model for equipment maintenance issues."""

    __tablename__ = "issue_report"

    issue_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    equipment_id = Column(
        Integer,
        ForeignKey("equipment.equipment_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    issue_type = Column(SQLEnum(IssueType), nullable=False)
    problem_description = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    date_raised = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(IssueStatus), nullable=False, default=IssueStatus.OPEN, index=True)
    technician = Column(String(100), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    equipment = relationship("Equipment", back_populates="issue_reports")

    def __repr__(self) -> str:
        return f"<IssueReport(id={self.issue_id}, equipment_id={self.equipment_id}, type={self.issue_type.value}, status={self.status.value})>"
