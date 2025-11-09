"""Bootstrap functionality for creating first admin user."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)


async def create_first_admin(db: AsyncSession) -> None:
    """
    Create first admin user from environment variables if no users exist.

    This function should be called on application startup.

    Args:
        db: Database session
    """
    try:
        # Check if any users exist
        result = await db.execute(select(User).limit(1))
        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            logger.info("Users already exist. Skipping bootstrap admin creation.")
            return

        # Verify required environment variables
        if not all([
            settings.FIRST_ADMIN_USERNAME,
            settings.FIRST_ADMIN_EMAIL,
            settings.FIRST_ADMIN_PASSWORD
        ]):
            logger.warning(
                "Bootstrap admin environment variables not fully configured. "
                "Skipping admin creation. You will need to create an admin user manually."
            )
            return

        # Create admin user
        admin_user = User(
            username=settings.FIRST_ADMIN_USERNAME,
            email=settings.FIRST_ADMIN_EMAIL,
            password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
            full_name=settings.FIRST_ADMIN_FULL_NAME,
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

        logger.info(
            f"Bootstrap admin user created successfully: "
            f"username='{admin_user.username}', "
            f"email='{admin_user.email}'"
        )

    except Exception as e:
        logger.error(f"Error creating bootstrap admin: {e}")
        await db.rollback()
        raise
