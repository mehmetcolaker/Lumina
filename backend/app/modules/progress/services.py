from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import Course, Section, Step
from app.modules.progress.models import UserProgress


async def mark_step_complete(
    db: AsyncSession,
    user_id: UUID,
    step_id: UUID,
) -> tuple[UserProgress, int]:
    """Mark a step as completed for the given user.

    If a UserProgress record already exists for this (user, step) pair
    and is_completed is True, a ValueError is raised.

    Args:
        db: An async database session.
        user_id: The UUID of the user completing the step.
        step_id: The UUID of the step to mark complete.

    Returns:
        A tuple of (UserProgress record, xp_reward earned).

    Raises:
        ValueError: If the step is already completed by this user.
    """
    # Check for existing completion
    existing = await _get_progress(db, user_id, step_id)
    if existing and existing.is_completed:
        raise ValueError(f"Step '{step_id}' is already completed by this user.")

    if existing and not existing.is_completed:
        # Re-activate a soft-cancelled record
        existing.is_completed = True
        existing.completed_at = datetime.now(timezone.utc)
        db.add(existing)
        await db.flush()
        progress = existing
    else:
        progress = UserProgress(
            user_id=user_id,
            step_id=step_id,
            is_completed=True,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(progress)
        await db.flush()
        await db.refresh(progress)

    # Fetch the step to retrieve xp_reward
    step = await db.get(Step, step_id)
    xp_earned = step.xp_reward if step else 10

    return progress, xp_earned


async def get_user_progress_for_course(
    db: AsyncSession,
    user_id: UUID,
    course_id: UUID,
) -> dict[str, bool]:
    """Retrieve all completed step IDs for a user within a given course.

    Args:
        db: An async database session.
        user_id: The UUID of the user.
        course_id: The UUID of the course.

    Returns:
        A dict mapping step UUID strings to their completion status
        (True if completed, key absent means not completed).
    """
    # Fetch all steps belonging to this course via sections
    subquery = (
        select(Step.id)
        .join(Section, Step.section_id == Section.id)
        .where(Section.course_id == course_id)
    ).subquery()

    stmt = select(UserProgress).where(
        UserProgress.user_id == user_id,
        UserProgress.step_id.in_(select(subquery.c.id)),
        UserProgress.is_completed.is_(True),
    )
    result = await db.execute(stmt)
    progresses = result.scalars().all()

    return {str(p.step_id): True for p in progresses}


async def _get_progress(
    db: AsyncSession,
    user_id: UUID,
    step_id: UUID,
) -> UserProgress | None:
    """Return the UserProgress record for a given (user, step) pair, if any.

    Args:
        db: An async database session.
        user_id: The UUID of the user.
        step_id: The UUID of the step.

    Returns:
        The existing UserProgress record, or None.
    """
    stmt = select(UserProgress).where(
        UserProgress.user_id == user_id,
        UserProgress.step_id == step_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
