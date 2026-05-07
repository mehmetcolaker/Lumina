"""pytest fixtures — uses a single file-based SQLite database per test.

Patching strategy:
  - ``app.core.database.async_session_maker`` → async SQLite session
  - ``app.core.database.sync_session_maker``  → sync SQLite session (same file)
  - FastAPI ``get_db``   dependency → returns the **same** session for the
    entire test so that seed data is visible to every request.
  - FastAPI ``get_sync_db`` dependency → sync session (monetization webhook)
"""

import tempfile
from pathlib import Path
from typing import AsyncGenerator
from uuid import UUID

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from unittest.mock import MagicMock

import pytest

from app.core import database as db_module
from app.core.security import create_access_token
from app.modules.courses.models import Course, Section, Step, StepType
from app.modules.users.models import User
from main import app


@pytest.fixture(autouse=True)
def _mock_celery(monkeypatch: pytest.MonkeyPatch):
    """Patch Celery ``.delay()`` so it's a no-op — prevents hanging
    when Redis is unreachable during tests."""
    mock = MagicMock()
    mock.delay.return_value = None
    monkeypatch.setattr(
        "app.modules.execution.tasks.execute_user_code", mock
    )


@pytest_asyncio.fixture(scope="function")
async def lumina_db():
    """Create a temporary SQLite database, patch every session maker,
    and yield a dict with both a reusable async session maker and a
    sync session maker.

    The yielded ``maker`` can be used by ``seeded_course_data`` and
    ``_override_get_db`` wraps around it so that every HTTP request
    during the test also sees the same data.
    """
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db_path = Path(tmp.name)
    db_url = f"sqlite+aiosqlite:///{db_path}"
    sync_url = f"sqlite:///{db_path}"

    # --- Async engine ---
    async_engine = create_async_engine(db_url, echo=False, poolclass=NullPool)

    @event.listens_for(async_engine.sync_engine, "connect")
    def _set_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with async_engine.begin() as conn:
        await conn.run_sync(db_module.Base.metadata.create_all)

    async_maker = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    sync_engine = create_engine(sync_url, echo=False)
    sync_maker = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)

    # --- Patch module-level globals ---
    _orig_async_maker = db_module.async_session_maker
    _orig_sync_maker = db_module.sync_session_maker
    db_module.async_session_maker = async_maker
    db_module.sync_session_maker = sync_maker

    # --- Override FastAPI dependencies ---
    async def _test_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def _test_get_sync_db():
        session = sync_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    app.dependency_overrides[db_module.get_db] = _test_get_db
    app.dependency_overrides[db_module.get_sync_db] = _test_get_sync_db

    yield {"async_maker": async_maker, "sync_maker": sync_maker}

    app.dependency_overrides.clear()
    db_module.async_session_maker = _orig_async_maker
    db_module.sync_session_maker = _orig_sync_maker
    await async_engine.dispose()
    sync_engine.dispose()
    try:
        db_path.unlink(missing_ok=True)
    except PermissionError:
        pass


@pytest_asyncio.fixture
async def async_client(
    lumina_db,
) -> AsyncGenerator[AsyncClient, None]:
    """An httpx AsyncClient wired to the FastAPI app via ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def demo_user(async_client: AsyncClient) -> User:
    """Create a demo user via the API."""
    resp = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "demo@test.dev", "password": "demopass123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    return User(
        id=UUID(data["id"]),
        email=data["email"],
        is_active=data["is_active"],
        is_premium=data["is_premium"],
        is_superuser=data.get("is_superuser", False),
        hashed_password="",
    )


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
async def seeded_course_data(lumina_db) -> dict:
    """Create a course with one section and two steps."""
    maker = lumina_db["async_maker"]
    async with maker() as session:
        course = Course(
            title="Test Course",
            description="A course for testing",
            language="Python",
        )
        session.add(course)
        await session.flush()
        await session.refresh(course)

        section = Section(course_id=course.id, title="Section 1", order=0)
        session.add(section)
        await session.flush()
        await session.refresh(section)

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
        session.add_all([step1, step2])
        await session.flush()
        await session.refresh(step1)
        await session.refresh(step2)
        await session.commit()

        return {
            "course_id": str(course.id),
            "section_id": str(section.id),
            "step_id_1": str(step1.id),
            "step_id_2": str(step2.id),
        }
