from copy import deepcopy
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, Section, Step


def _strip_correct_option(step: Step) -> Step:
    """Remove ``correct_option`` from a step's content_data in-place.

    This prevents quiz answer keys from being leaked to the client.
    """
    if step.content_data and "correct_option" in step.content_data:
        step.content_data = deepcopy(step.content_data)
        step.content_data.pop("correct_option", None)
    return step


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

    Returns:
        The Course with sections and steps populated, or None if not found.

    Note:
        ``correct_option`` is stripped from quiz step content_data to
        prevent answer keys being leaked to the client.
    """
    stmt = (
        select(Course)
        .options(
            selectinload(Course.sections).selectinload(Section.steps)
        )
        .where(Course.id == UUID(course_id))
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if course:
        for sec in course.sections:
            sec.steps = [_strip_correct_option(s) for s in sec.steps]
    return course
