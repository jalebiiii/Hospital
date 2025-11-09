"""CRUD operations for Department model."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.department import Department


async def get_department(db: AsyncSession, department_id: int) -> Optional[Department]:
    """Get department by ID."""
    result = await db.execute(
        select(Department).where(Department.department_id == department_id)
    )
    return result.scalar_one_or_none()


async def get_departments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    sort_by: str = "department_name",
    sort_order: str = "asc"
) -> tuple[List[Department], int]:
    """
    Get paginated list of departments.

    Returns tuple of (departments, total_count)
    """
    # Base query
    query = select(Department)

    # Search filter
    if search:
        query = query.where(Department.department_name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_column = getattr(Department, sort_by, Department.department_name)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    departments = result.scalars().all()

    return departments, total


async def create_department(
    db: AsyncSession,
    department_name: str
) -> Department:
    """Create a new department."""
    department = Department(department_name=department_name)
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return department


async def update_department(
    db: AsyncSession,
    department: Department,
    department_name: str
) -> Department:
    """Update department name."""
    department.department_name = department_name
    department.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(department)
    return department


async def delete_department(db: AsyncSession, department: Department) -> None:
    """Delete a department."""
    await db.delete(department)
    await db.commit()


async def get_department_by_name(
    db: AsyncSession,
    department_name: str
) -> Optional[Department]:
    """Get department by name (case-insensitive)."""
    result = await db.execute(
        select(Department).where(Department.department_name.ilike(department_name))
    )
    return result.scalar_one_or_none()
