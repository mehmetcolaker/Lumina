from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables (.env file).

    Attributes:
        DATABASE_URL: PostgreSQL connection string for async SQLAlchemy.
        SECRET_KEY: Secret key used for JWT signing.
        ALGORITHM: JWT signing algorithm (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes.
        REDIS_URL: Redis connection string for Celery broker/backend.
        STRIPE_SECRET_KEY: Stripe API secret key.
        STRIPE_WEBHOOK_SECRET: Stripe webhook signing secret.
        STRIPE_PRICE_ID: Stripe Price ID for the premium plan.
        STRIPE_SUCCESS_URL: Redirect URL after successful checkout.
        STRIPE_CANCEL_URL: Redirect URL after cancelled checkout.
    """

    DATABASE_URL: str
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID: str = ""
    STRIPE_SUCCESS_URL: str = "https://lumina.app/dashboard"
    STRIPE_CANCEL_URL: str = "https://lumina.app/pricing"

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
