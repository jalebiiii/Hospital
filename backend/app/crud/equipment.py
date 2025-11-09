"""CRUD operations for Equipment model."""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.equipment import Equipment
from app.models.enums import EquipmentStatus


async def get_equipment(db: AsyncSession, equipment_id: int) -> Optional[Equipment]:
    """Get equipment by ID with relationships loaded."""
    result = await db.execute(
        select(Equipment)
        .where(Equipment.equipment_id == equipment_id)
        .options(
            selectinload(Equipment.department),
            selectinload(Equipment.vendor),
            selectinload(Equipment.issue_reports).limit(5),
            selectinload(Equipment.discard_record)
        )
    )
    return result.scalar_one_or_none()


async def get_equipment_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    status: Optional[List[EquipmentStatus]] = None,
    department_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    purchase_date_from: Optional[date] = None,
    purchase_date_to: Optional[date] = None,
    expiry_date_from: Optional[date] = None,
    expiry_date_to: Optional[date] = None,
    expired: Optional[bool] = None,
    sort_by: str = "equipment_name",
    sort_order: str = "asc"
) -> tuple[List[Equipment], int]:
    """
    Get paginated list of equipment with filters.

    Returns tuple of (equipment_list, total_count)
    """
    # Base query
    query = select(Equipment).options(
        selectinload(Equipment.department),
        selectinload(Equipment.vendor)
    )

    # Search filter (searches name, serial number, manufacturer)
    if search:
        search_filter = or_(
            Equipment.equipment_name.ilike(f"%{search}%"),
            Equipment.serial_number.ilike(f"%{search}%"),
            Equipment.manufacturer.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Status filter
    if status:
        query = query.where(Equipment.status.in_(status))

    # Department filter
    if department_id:
        query = query.where(Equipment.department_id == department_id)

    # Vendor filter
    if vendor_id:
        query = query.where(Equipment.vendor_id == vendor_id)

    # Purchase date range filter
    if purchase_date_from:
        query = query.where(Equipment.purchase_date >= purchase_date_from)
    if purchase_date_to:
        query = query.where(Equipment.purchase_date <= purchase_date_to)

    # Expiry date range filter
    if expiry_date_from:
        query = query.where(Equipment.expiry_date >= expiry_date_from)
    if expiry_date_to:
        query = query.where(Equipment.expiry_date <= expiry_date_to)

    # Expired filter (equipment with expiry_date <= today)
    if expired is True:
        today = date.today()
        query = query.where(
            Equipment.expiry_date <= today,
            Equipment.status != EquipmentStatus.DECOMMISSIONED
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_column = getattr(Equipment, sort_by, Equipment.equipment_name)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    equipment_list = result.scalars().all()

    return equipment_list, total


async def create_equipment(
    db: AsyncSession,
    equipment_name: str,
    department_id: int,
    serial_number: Optional[str] = None,
    model_no: Optional[str] = None,
    manufacturer: Optional[str] = None,
    purchase_date: Optional[date] = None,
    expiry_date: Optional[date] = None,
    status: EquipmentStatus = EquipmentStatus.WORKING,
    vendor_id: Optional[int] = None,
    quantity: int = 1
) -> Equipment:
    """Create new equipment."""
    equipment = Equipment(
        equipment_name=equipment_name,
        department_id=department_id,
        serial_number=serial_number,
        model_no=model_no,
        manufacturer=manufacturer,
        purchase_date=purchase_date,
        expiry_date=expiry_date,
        status=status,
        vendor_id=vendor_id,
        quantity=quantity
    )
    db.add(equipment)
    await db.commit()
    await db.refresh(equipment)
    return equipment


async def update_equipment(
    db: AsyncSession,
    equipment: Equipment,
    equipment_name: Optional[str] = None,
    serial_number: Optional[str] = None,
    model_no: Optional[str] = None,
    manufacturer: Optional[str] = None,
    department_id: Optional[int] = None,
    purchase_date: Optional[date] = None,
    expiry_date: Optional[date] = None,
    status: Optional[EquipmentStatus] = None,
    vendor_id: Optional[int] = None,
    quantity: Optional[int] = None
) -> Equipment:
    """Update equipment fields."""
    if equipment_name is not None:
        equipment.equipment_name = equipment_name
    if serial_number is not None:
        equipment.serial_number = serial_number
    if model_no is not None:
        equipment.model_no = model_no
    if manufacturer is not None:
        equipment.manufacturer = manufacturer
    if department_id is not None:
        equipment.department_id = department_id
    if purchase_date is not None:
        equipment.purchase_date = purchase_date
    if expiry_date is not None:
        equipment.expiry_date = expiry_date
    if status is not None:
        equipment.status = status
    if vendor_id is not None:
        equipment.vendor_id = vendor_id
    if quantity is not None:
        equipment.quantity = quantity

    equipment.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(equipment)
    return equipment


async def delete_equipment(db: AsyncSession, equipment: Equipment) -> None:
    """Delete equipment (cascades to issues and discard record)."""
    await db.delete(equipment)
    await db.commit()


async def get_equipment_by_serial(
    db: AsyncSession,
    serial_number: str
) -> Optional[Equipment]:
    """Get equipment by serial number."""
    result = await db.execute(
        select(Equipment).where(Equipment.serial_number == serial_number)
    )
    return result.scalar_one_or_none()
