"""CRUD operations for IssueReport model."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.issue_report import IssueReport
from app.models.enums import IssueType, IssueStatus


async def get_issue(db: AsyncSession, issue_id: int) -> Optional[IssueReport]:
    """Get issue by ID with equipment loaded."""
    result = await db.execute(
        select(IssueReport)
        .where(IssueReport.issue_id == issue_id)
        .options(selectinload(IssueReport.equipment))
    )
    return result.scalar_one_or_none()


async def get_issues(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    equipment_id: Optional[int] = None,
    issue_type: Optional[List[IssueType]] = None,
    status: Optional[List[IssueStatus]] = None,
    date_raised_from: Optional[datetime] = None,
    date_raised_to: Optional[datetime] = None,
    technician: Optional[str] = None,
    sort_by: str = "date_raised",
    sort_order: str = "desc"
) -> tuple[List[IssueReport], int]:
    """
    Get paginated list of issues with filters.

    Returns tuple of (issues, total_count)
    """
    # Base query
    query = select(IssueReport).options(
        selectinload(IssueReport.equipment)
    )

    # Search filter (searches problem description)
    if search:
        query = query.where(IssueReport.problem_description.ilike(f"%{search}%"))

    # Equipment filter
    if equipment_id:
        query = query.where(IssueReport.equipment_id == equipment_id)

    # Issue type filter
    if issue_type:
        query = query.where(IssueReport.issue_type.in_(issue_type))

    # Status filter
    if status:
        query = query.where(IssueReport.status.in_(status))

    # Date raised range filter
    if date_raised_from:
        query = query.where(IssueReport.date_raised >= date_raised_from)
    if date_raised_to:
        query = query.where(IssueReport.date_raised <= date_raised_to)

    # Technician filter (partial match)
    if technician:
        query = query.where(IssueReport.technician.ilike(f"%{technician}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_column = getattr(IssueReport, sort_by, IssueReport.date_raised)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    issues = result.scalars().all()

    return issues, total


async def create_issue(
    db: AsyncSession,
    equipment_id: int,
    issue_type: IssueType,
    problem_description: str,
    media_url: Optional[str] = None,
    date_raised: Optional[datetime] = None,
    status: IssueStatus = IssueStatus.OPEN,
    technician: Optional[str] = None
) -> IssueReport:
    """Create new issue report."""
    issue = IssueReport(
        equipment_id=equipment_id,
        issue_type=issue_type,
        problem_description=problem_description,
        media_url=media_url,
        date_raised=date_raised or datetime.utcnow(),
        status=status,
        technician=technician
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    return issue


async def update_issue(
    db: AsyncSession,
    issue: IssueReport,
    issue_type: Optional[IssueType] = None,
    problem_description: Optional[str] = None,
    media_url: Optional[str] = None,
    status: Optional[IssueStatus] = None,
    technician: Optional[str] = None
) -> IssueReport:
    """Update issue fields. Auto-set resolved_at when status changes to RESOLVED or CLOSED."""
    if issue_type is not None:
        issue.issue_type = issue_type
    if problem_description is not None:
        issue.problem_description = problem_description
    if media_url is not None:
        issue.media_url = media_url
    if status is not None:
        old_status = issue.status
        issue.status = status
        # Auto-set resolved_at if status changes to RESOLVED or CLOSED
        if status in [IssueStatus.RESOLVED, IssueStatus.CLOSED] and old_status not in [IssueStatus.RESOLVED, IssueStatus.CLOSED]:
            issue.resolved_at = datetime.utcnow()
    if technician is not None:
        issue.technician = technician

    issue.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(issue)
    return issue


async def delete_issue(db: AsyncSession, issue: IssueReport) -> None:
    """Delete issue report."""
    await db.delete(issue)
    await db.commit()
