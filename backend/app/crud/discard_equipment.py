"""CRUD operations for DiscardEquipment model."""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.discard_equipment import DiscardEquipment
from app.models.equipment import Equipment
from app.models.enums import EquipmentStatus


async def get_discard(db: AsyncSession, discard_id: int) -> Optional[DiscardEquipment]:
    """Get discard record by ID with equipment loaded."""
    result = await db.execute(
        select(DiscardEquipment)
        .where(DiscardEquipment.discard_id == discard_id)
        .options(selectinload(DiscardEquipment.equipment))
    )
    return result.scalar_one_or_none()


async def get_discards(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    equipment_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: str = "date",
    sort_order: str = "desc"
) -> tuple[List[DiscardEquipment], int]:
    """
    Get paginated list of discard records with filters.

    Returns tuple of (discards, total_count)
    """
    # Base query
    query = select(DiscardEquipment).options(
        selectinload(DiscardEquipment.equipment)
    )

    # Search filter (searches reason)
    if search:
        query = query.where(DiscardEquipment.reason.ilike(f"%{search}%"))

    # Equipment filter
    if equipment_id:
        query = query.where(DiscardEquipment.equipment_id == equipment_id)

    # Date range filter
    if date_from:
        query = query.where(DiscardEquipment.date >= date_from)
    if date_to:
        query = query.where(DiscardEquipment.date <= date_to)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_column = getattr(DiscardEquipment, sort_by, DiscardEquipment.date)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    discards = result.scalars().all()

    return discards, total


async def create_discard(
    db: AsyncSession,
    equipment_id: int,
    reason: str,
    discard_date: date,
    media_url: Optional[str] = None
) -> DiscardEquipment:
    """
    Create new discard record.

    Also updates the equipment status to DECOMMISSIONED.
    """
    # Create discard record
    discard = DiscardEquipment(
        equipment_id=equipment_id,
        reason=reason,
        date=discard_date,
        media_url=media_url
    )
    db.add(discard)

    # Update equipment status to DECOMMISSIONED
    result = await db.execute(
        select(Equipment).where(Equipment.equipment_id == equipment_id)
    )
    equipment = result.scalar_one()
    equipment.status = EquipmentStatus.DECOMMISSIONED
    equipment.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(discard)
    return discard


async def update_discard(
    db: AsyncSession,
    discard: DiscardEquipment,
    reason: Optional[str] = None,
    discard_date: Optional[date] = None,
    media_url: Optional[str] = None
) -> DiscardEquipment:
    """Update discard record fields (cannot change equipment_id)."""
    if reason is not None:
        discard.reason = reason
    if discard_date is not None:
        discard.date = discard_date
    if media_url is not None:
        discard.media_url = media_url

    discard.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(discard)
    return discard


async def delete_discard(db: AsyncSession, discard: DiscardEquipment) -> None:
    """
    Delete discard record.

    Also reverts equipment status to WORKING (or can be customized).
    """
    # Get equipment
    result = await db.execute(
        select(Equipment).where(Equipment.equipment_id == discard.equipment_id)
    )
    equipment = result.scalar_one()

    # Revert equipment status (set to WORKING as default, could be smarter)
    equipment.status = EquipmentStatus.WORKING
    equipment.updated_at = datetime.utcnow()

    # Delete discard record
    await db.delete(discard)
    await db.commit()


async def get_discard_by_equipment(
    db: AsyncSession,
    equipment_id: int
) -> Optional[DiscardEquipment]:
    """Check if equipment already has a discard record."""
    result = await db.execute(
        select(DiscardEquipment).where(DiscardEquipment.equipment_id == equipment_id)
    )
    return result.scalar_one_or_none()
