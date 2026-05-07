"""Admin business logic — CRUD for users, courses, sections, and steps."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import Course, Section, Step, StepType
from app.modules.users.models import User


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------


async def list_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Return a paginated list of all users."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_user_by_id_admin(db: AsyncSession, user_id: UUID) -> User | None:
    """Return a single user by ID (admin scope)."""
    return await db.get(User, user_id)


async def update_user(
    db: AsyncSession, user_id: UUID, updates: dict
) -> User | None:
    """Partially update a user record.  Returns the updated user or None."""
    user = await db.get(User, user_id)
    if user is None:
        return None
    for key, value in updates.items():
        if value is not None:
            setattr(user, key, value)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Soft-delete a user by setting is_active=False.  Returns True if found."""
    user = await db.get(User, user_id)
    if user is None:
        return False
    user.is_active = False
    db.add(user)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# Course management
# ---------------------------------------------------------------------------


async def create_course(db: AsyncSession, data: dict) -> Course:
    """Create a new course."""
    course = Course(**data)
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return course


async def update_course(db: AsyncSession, course_id: UUID, data: dict) -> Course | None:
    """Update a course.  Returns None if not found."""
    course = await db.get(Course, course_id)
    if course is None:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(course, key, value)
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return course


async def delete_course(db: AsyncSession, course_id: UUID) -> bool:
    """Delete a course and all its sections/steps (CASCADE)."""
    course = await db.get(Course, course_id)
    if course is None:
        return False
    await db.delete(course)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# Section management
# ---------------------------------------------------------------------------


async def create_section(db: AsyncSession, course_id: UUID, data: dict) -> Section:
    """Create a new section within a course."""
    section = Section(course_id=course_id, **data)
    db.add(section)
    await db.flush()
    await db.refresh(section)
    return section


async def delete_section(db: AsyncSession, section_id: UUID) -> bool:
    """Delete a section and its steps (CASCADE)."""
    section = await db.get(Section, section_id)
    if section is None:
        return False
    await db.delete(section)
    await db.flush()
    return True


# ---------------------------------------------------------------------------
# Step management
# ---------------------------------------------------------------------------


async def create_step(db: AsyncSession, section_id: UUID, data: dict) -> Step:
    """Create a new step within a section."""
    step = Step(section_id=section_id, **data)
    db.add(step)
    await db.flush()
    await db.refresh(step)
    return step


async def update_step(db: AsyncSession, step_id: UUID, data: dict) -> Step | None:
    """Update an existing step."""
    step = await db.get(Step, step_id)
    if step is None:
        return None
    for key, value in data.items():
        if value is not None:
            setattr(step, key, value)
    db.add(step)
    await db.flush()
    await db.refresh(step)
    return step


async def delete_step(db: AsyncSession, step_id: UUID) -> bool:
    """Delete a single step."""
    step = await db.get(Step, step_id)
    if step is None:
        return False
    await db.delete(step)
    await db.flush()
    return True
