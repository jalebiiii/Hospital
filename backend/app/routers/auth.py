"""Authentication router."""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token
from app.dependencies.auth import require_admin, require_active_user
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.schemas.common import ApiResponse
from app.crud import user as user_crud, refresh_token as token_crud

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    current_user: UserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new user account (admin-only operation).

    - **username**: Unique username (3-50 chars, alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Min 8 chars, must contain: 1 uppercase, 1 lowercase, 1 number
    - **full_name**: Optional full name
    - **role**: User role (ADMIN, TECHNICIAN, or VIEWER)
    """
    # Check if username already exists
    existing_user = await user_crud.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # Check if email already exists
    existing_email = await user_crud.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Create user
    new_user = await user_crud.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role
    )

    return ApiResponse(
        data=UserResponse.model_validate(new_user),
        message="User created successfully"
    )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    response: Response,
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and receive access + refresh tokens.

    - **username**: Username
    - **password**: Password

    Returns access token in response body and refresh token in httpOnly cookie.
    """
    # Authenticate user
    user = await user_crud.authenticate_user(db, credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token = create_access_token({
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role.value
    })

    # Create refresh token
    refresh_token, _ = await token_crud.create_refresh_token(db, user.user_id)

    # Set refresh token as httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/api/v1/auth"
    )

    # Update last login
    await user_crud.update_last_login(db, user)

    return ApiResponse(
        data=TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        ),
        message="Login successful"
    )


@router.post("/refresh", response_model=ApiResponse[dict])
async def refresh_token(
    refresh_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new access token using refresh token from cookie.

    Refresh token must be provided in httpOnly cookie.
    """
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    # Validate refresh token
    token_record = await token_crud.validate_refresh_token(db, refresh_token)
    if token_record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user
    user = await user_crud.get_user_by_id(db, token_record.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or not found"
        )

    # Create new access token
    access_token = create_access_token({
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role.value
    })

    return ApiResponse(
        data={
            "access_token": access_token,
            "token_type": "bearer"
        },
        message="Token refreshed successfully"
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    current_user: UserResponse = Depends(require_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by invalidating refresh token.

    Requires valid access token.
    """
    # Revoke refresh token if present
    if refresh_token:
        token_record = await token_crud.validate_refresh_token(db, refresh_token)
        if token_record:
            await token_crud.revoke_refresh_token(db, token_record)

    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")

    return None


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(
    current_user: UserResponse = Depends(require_active_user)
):
    """
    Get current authenticated user information.

    Requires valid access token.
    """
    return ApiResponse(data=current_user)
