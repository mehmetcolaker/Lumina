from copy import deepcopy
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step
from app.modules.progress.models import UserProgress


def _strip_correct_option(step: Step) -> Step:
    if step.content_data and "correct_option" in step.content_data:
        step.content_data = deepcopy(step.content_data)
        step.content_data.pop("correct_option", None)
    return step


async def list_courses(db: AsyncSession) -> list[Course]:
    result = await db.execute(select(Course).order_by(Course.title))
    return list(result.scalars().all())


async def get_course_with_path(
    db: AsyncSession,
    course_id: str,
) -> Course | None:
    stmt = (
        select(Course)
        .options(selectinload(Course.sections).selectinload(Section.steps))
        .where(Course.id == UUID(course_id))
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    if course:
        for sec in course.sections:
            sec.steps = [_strip_correct_option(s) for s in sec.steps]
    return course


# ── Learning Path (Roadmap) ────────────────────────────


async def list_paths(db: AsyncSession) -> list[LearningPath]:
    """Return all learning paths ordered by their sort order."""
    result = await db.execute(
        select(LearningPath)
        .options(selectinload(LearningPath.levels).selectinload(PathLevel.course))
        .order_by(LearningPath.order)
    )
    return list(result.scalars().all())


async def get_path_progress(
    db: AsyncSession,
    path_id: UUID,
    user_id: UUID,
) -> LearningPath | None:
    """Return a learning path with each level's progress and unlock status
    for the given user.

    A level is unlocked if:
        - It is the first level (order=0), OR
        - The previous level has >= required_progress_pct steps completed.
    """
    result = await db.execute(
        select(LearningPath)
        .options(selectinload(LearningPath.levels).selectinload(PathLevel.course))
        .where(LearningPath.id == path_id)
    )
    path = result.scalar_one_or_none()
    if path is None:
        return None

    # Calculate per-level progress (levels must be sorted by order)
    sorted_levels = sorted(path.levels, key=lambda l: l.order)
    for i, level in enumerate(sorted_levels):
        course = level.course
        if not course:
            continue

        # Count total steps in this course
        total_steps_query = await db.execute(
            select(func.count())
            .select_from(Step)
            .join(Section, Step.section_id == Section.id)
            .where(Section.course_id == course.id)
        )
        total_steps = total_steps_query.scalar() or 0

        # Count completed steps for this user
        subq = (
            select(Step.id)
            .join(Section, Step.section_id == Section.id)
            .where(Section.course_id == course.id)
        ).subquery()

        completed_query = await db.execute(
            select(func.count())
            .select_from(UserProgress)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.step_id.in_(select(subq.c.id)),
                UserProgress.is_completed.is_(True),
            )
        )
        completed = completed_query.scalar() or 0

        progress_pct = round((completed / total_steps) * 100) if total_steps > 0 else 0

        # Unlock logic using a separate dict
        level._cache = {"progress_pct": progress_pct}  # type: ignore[attr-defined]

        if i == 0:
            level._cache["unlocked"] = True  # type: ignore[attr-defined]
        else:
            prev_level = sorted_levels[i - 1]
            prev_pct = getattr(prev_level, "_cache", {}).get("progress_pct", 0)
            level._cache["unlocked"] = (  # type: ignore[attr-defined]
                prev_pct >= prev_level.required_progress_pct
            )

    return path
