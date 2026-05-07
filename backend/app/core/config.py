from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (.env file).

    Attributes:
        DATABASE_URL: PostgreSQL connection string for async SQLAlchemy.
        SECRET_KEY: Secret key used for JWT signing.
        ALGORITHM: JWT signing algorithm (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes (default: 30).
        REDIS_URL: Redis connection string for Celery broker/backend.
    """

    DATABASE_URL: str
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Sync database URL for Celery workers (psycopg2 driver) ---
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Derive a synchronous Postgres connection string from DATABASE_URL.

        Celery tasks use synchronous SQLAlchemy, so the driver must be
        psycopg2 instead of asyncpg.
        """
        return self.DATABASE_URL.replace(
            "postgresql://", "postgresql+psycopg2://", 1
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
