"""pytest fixtures and helpers for the Lumina test suite.

Uses an in-memory SQLite database (via aiosqlite) so tests run
without an external PostgreSQL instance.

Because SQLite does not support ``ENUM`` / ``JSON`` the same way as
PostgreSQL, SQLAlchemy handles graceful degradation automatically.
"""

from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.security import create_access_token, hash_password
from app.modules.courses.models import Course, Section, Step, StepType
from app.modules.users.models import User
from main import app

# ---------------------------------------------------------------------------
# Test database — in-memory SQLite
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh in-memory SQLite database per test function.

    Ensures complete isolation between test cases.
    """
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)

    # Enable WAL and foreign keys for SQLite compatibility
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    await engine.dispose()


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override FastAPI's ``get_db`` dependency with the test DB session.

    This is set up per-test by ``async_client``.
    """
    # Will be replaced dynamically by the test's db_session
    raise RuntimeError("_override_get_db must be overridden per test")


@pytest_asyncio.fixture
async def async_client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """An httpx AsyncClient wired to the FastAPI app via ASGI transport.

    Automatically uses the test database session for the duration of
    the test.
    """

    # Override the get_db dependency to return our test session
    async def _test_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _test_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def demo_user(db_session: AsyncSession) -> User:
    """Create and return a demo user in the test database."""
    user = User(
        email="demo@test.dev",
        hashed_password=hash_password("demopass123"),
        is_active=True,
        is_premium=False,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def demo_token(demo_user: User) -> str:
    """Return a valid JWT for the demo user."""
    return create_access_token(data={"sub": str(demo_user.id)})


@pytest_asyncio.fixture
async def auth_headers(demo_token: str) -> dict[str, str]:
    """Return Authorization headers for the demo user."""
    return {"Authorization": f"Bearer {demo_token}"}


# ---------------------------------------------------------------------------
# Seed data helpers
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def seeded_course(db_session: AsyncSession) -> Course:
    """Create a course with one section and two steps."""
    course = Course(
        title="Test Course",
        description="A course for testing",
        language="Python",
    )
    db_session.add(course)
    await db_session.flush()
    await db_session.refresh(course)

    section = Section(course_id=course.id, title="Section 1", order=0)
    db_session.add(section)
    await db_session.flush()
    await db_session.refresh(section)

    step1 = Step(
        section_id=section.id,
        title="Theory Step",
        step_type=StepType.THEORY,
        order=0,
        xp_reward=10,
        content_data={"body_markdown": "# Test"},
    )
    step2 = Step(
        section_id=section.id,
        title="Quiz Step",
        step_type=StepType.QUIZ,
        order=1,
        xp_reward=20,
        content_data={"question": "Test?", "correct_option": "a"},
    )
    db_session.add_all([step1, step2])
    await db_session.flush()
    await db_session.refresh(step1)
    await db_session.refresh(step2)

    # Eagerly load relationships
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    stmt = (
        select(Course)
        .options(selectinload(Course.sections).selectinload(Section.steps))
        .where(Course.id == course.id)
    )
    result = await db_session.execute(stmt)
    return result.scalar_one()
