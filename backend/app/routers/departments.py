"""Departments router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import require_active_user, require_admin
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationMeta
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.crud import department as department_crud

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=PaginatedResponse[DepartmentResponse])
async def list_departments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: str = Query("department_name"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    current_user=Depends(require_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all departments with pagination.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **search**: Search in department name
    - **sort_by**: Field to sort by (default: department_name)
    - **sort_order**: Sort order (asc or desc)
    """
    skip = (page - 1) * page_size
    departments, total = await department_crud.get_departments(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=[DepartmentResponse.model_validate(d) for d in departments],
        pagination=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get("/{department_id}", response_model=ApiResponse[DepartmentResponse])
async def get_department(
    department_id: int,
    current_user=Depends(require_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get department by ID."""
    department = await department_crud.get_department(db, department_id)
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    return ApiResponse(data=DepartmentResponse.model_validate(department))


@router.post("", response_model=ApiResponse[DepartmentResponse], status_code=status.HTTP_201_CREATED)
async def create_department(
    department_data: DepartmentCreate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new department (admin only).

    - **department_name**: Unique department name
    """
    # Check if department with same name already exists
    existing = await department_crud.get_department_by_name(db, department_data.department_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Department with this name already exists"
        )

    department = await department_crud.create_department(
        db=db,
        department_name=department_data.department_name
    )

    return ApiResponse(
        data=DepartmentResponse.model_validate(department),
        message="Department created successfully"
    )


@router.patch("/{department_id}", response_model=ApiResponse[DepartmentResponse])
async def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update department (admin only)."""
    department = await department_crud.get_department(db, department_id)
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Check if new name conflicts with existing department
    if department_data.department_name:
        existing = await department_crud.get_department_by_name(db, department_data.department_name)
        if existing and existing.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department with this name already exists"
            )

        department = await department_crud.update_department(
            db=db,
            department=department,
            department_name=department_data.department_name
        )

    return ApiResponse(
        data=DepartmentResponse.model_validate(department),
        message="Department updated successfully"
    )


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete department (admin only).

    Cannot delete if equipment exists in this department.
    """
    department = await department_crud.get_department(db, department_id)
    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )

    # Check if department has equipment
    # Note: This will be caught by foreign key constraint, but we provide better error message
    from sqlalchemy import select, func
    from app.models.equipment import Equipment
    result = await db.execute(
        select(func.count()).select_from(Equipment).where(Equipment.department_id == department_id)
    )
    equipment_count = result.scalar_one()

    if equipment_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete department with {equipment_count} equipment items"
        )

    await department_crud.delete_department(db, department)
    return None
