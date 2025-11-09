"""CRUD operations for Vendor model."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vendor import Vendor


async def get_vendor(db: AsyncSession, vendor_id: int) -> Optional[Vendor]:
    """Get vendor by ID."""
    result = await db.execute(
        select(Vendor).where(Vendor.vendor_id == vendor_id)
    )
    return result.scalar_one_or_none()


async def get_vendors(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "vendor_name",
    sort_order: str = "asc"
) -> tuple[List[Vendor], int]:
    """
    Get paginated list of vendors.

    Returns tuple of (vendors, total_count)
    """
    # Base query
    query = select(Vendor)

    # Search filter (searches name and email)
    if search:
        search_filter = or_(
            Vendor.vendor_name.ilike(f"%{search}%"),
            Vendor.email.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Category filter
    if category:
        query = query.where(Vendor.category.ilike(category))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_column = getattr(Vendor, sort_by, Vendor.vendor_name)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await db.execute(query)
    vendors = result.scalars().all()

    return vendors, total


async def create_vendor(
    db: AsyncSession,
    vendor_name: str,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    category: Optional[str] = None
) -> Vendor:
    """Create a new vendor."""
    vendor = Vendor(
        vendor_name=vendor_name,
        phone=phone,
        email=email,
        address=address,
        category=category
    )
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


async def update_vendor(
    db: AsyncSession,
    vendor: Vendor,
    vendor_name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    address: Optional[str] = None,
    category: Optional[str] = None
) -> Vendor:
    """Update vendor fields."""
    if vendor_name is not None:
        vendor.vendor_name = vendor_name
    if phone is not None:
        vendor.phone = phone
    if email is not None:
        vendor.email = email
    if address is not None:
        vendor.address = address
    if category is not None:
        vendor.category = category

    vendor.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(vendor)
    return vendor


async def delete_vendor(db: AsyncSession, vendor: Vendor) -> None:
    """Delete a vendor."""
    await db.delete(vendor)
    await db.commit()
