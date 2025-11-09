"""Application configuration settings."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./hospital.db"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    UPLOAD_DIR: str = "backend/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50

    # S3 (optional, for production)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET_NAME: str = ""
    AWS_S3_REGION: str = "us-east-1"
    S3_PRESIGNED_URL_EXPIRY: int = 3600

    # Bootstrap admin
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_EMAIL: str = "admin@hospital.local"
    FIRST_ADMIN_PASSWORD: str = "ChangeMe123!"
    FIRST_ADMIN_FULL_NAME: str = "System Administrator"

    # Background tasks
    ENABLE_MEDIA_CLEANUP: bool = True
    MEDIA_CLEANUP_SCHEDULE: str = "0 2 * * *"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def allowed_origins(self) -> List[str]:
        """Get list of allowed CORS origins."""
        return [self.FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"]

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


# Global settings instance
settings = Settings()
