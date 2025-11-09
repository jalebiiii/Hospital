"""CRUD operations for RefreshToken model."""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from app.core.config import settings


def generate_refresh_token() -> str:
    """Generate a secure random refresh token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256."""
    return hashlib.sha256(token.encode()).hexdigest()


async def create_refresh_token(db: AsyncSession, user_id: int) -> tuple[str, RefreshToken]:
    """
    Create a new refresh token for a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        tuple: (plain_token, RefreshToken record)
    """
    plain_token = generate_refresh_token()
    token_hash = hash_token(plain_token)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False
    )
    db.add(refresh_token)
    await db.commit()
    await db.refresh(refresh_token)

    return plain_token, refresh_token


async def get_refresh_token_by_hash(db: AsyncSession, token_hash: str) -> Optional[RefreshToken]:
    """Get refresh token by hash."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    return result.scalar_one_or_none()


async def validate_refresh_token(
    db: AsyncSession,
    plain_token: str
) -> Optional[RefreshToken]:
    """
    Validate a refresh token.

    Args:
        db: Database session
        plain_token: Plain text token

    Returns:
        Optional[RefreshToken]: Token if valid, None otherwise
    """
    token_hash = hash_token(plain_token)
    token = await get_refresh_token_by_hash(db, token_hash)

    if token is None:
        return None
    if token.revoked:
        return None
    if token.expires_at < datetime.utcnow():
        return None

    return token


async def revoke_refresh_token(db: AsyncSession, refresh_token: RefreshToken) -> None:
    """Revoke a refresh token."""
    refresh_token.revoked = True
    await db.commit()


async def revoke_user_tokens(db: AsyncSession, user_id: int) -> None:
    """Revoke all refresh tokens for a user."""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        )
    )
    tokens = result.scalars().all()

    for token in tokens:
        token.revoked = True

    await db.commit()


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Delete expired and revoked tokens.

    Returns:
        int: Number of deleted tokens
    """
    result = await db.execute(
        select(RefreshToken).where(
            (RefreshToken.expires_at < datetime.utcnow()) |
            (RefreshToken.revoked == True)
        )
    )
    tokens = result.scalars().all()

    count = len(tokens)
    for token in tokens:
        await db.delete(token)

    await db.commit()
    return count
