from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base declarative class for all SQLAlchemy ORM models."""

    pass


# ---------- Async engine (FastAPI endpoints) ----------

_async_connection_string = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://", 1
)

engine = create_async_engine(_async_connection_string, echo=False, future=True)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency that yields an async database session.

    Yields:
        An AsyncSession bound to the async engine. The session is
        automatically closed when the request finishes.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------- Sync engine (Celery workers) ----------

sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

sync_session_maker = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
)


def get_sync_db() -> Session:
    """Create a synchronous database session for Celery task usage.

    Returns:
        A plain SQLAlchemy Session.
    """
    session = sync_session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
