from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, Section


async def list_courses(db: AsyncSession) -> list[Course]:
    """Return all courses ordered by title.

    Args:
        db: An async database session.

    Returns:
        A list of all Course instances.
    """
    result = await db.execute(select(Course).order_by(Course.title))
    return list(result.scalars().all())


async def get_course_with_path(
    db: AsyncSession,
    course_id: str,
) -> Course | None:
    """Retrieve a single course with its sections and steps eagerly loaded.

    Args:
        db: An async database session.
        course_id: The UUID string identifying the course.

    Returns:
        The Course with sections and steps populated, or None if not found.
    """
    stmt = (
        select(Course)
        .options(
            selectinload(Course.sections).selectinload(Section.steps)
        )
        .where(Course.id == UUID(course_id))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
