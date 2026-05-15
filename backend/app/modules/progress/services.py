from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.courses.models import Course, Section, Step
from app.modules.execution.models import Submission, SubmissionVerdict
from app.modules.notifications.triggers import notify_course_completed
from app.modules.progress.models import UserProgress


async def check_course_completion(
    db: AsyncSession,
    user_id: UUID,
    course_id: UUID,
) -> tuple[bool, int, int]:
    """Check if a user has completed 100% of a course."""
    from sqlalchemy import func, select

    total_result = await db.execute(
        select(func.count())
        .select_from(Step)
        .join(Section, Step.section_id == Section.id)
        .where(Section.course_id == course_id)
    )
    total_steps = total_result.scalar() or 0
    if total_steps == 0:
        return False, 0, 0

    subq = (
        select(Step.id)
        .join(Section, Step.section_id == Section.id)
        .where(Section.course_id == course_id)
    ).subquery()

    completed_result = await db.execute(
        select(func.count())
        .select_from(UserProgress)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.step_id.in_(select(subq.c.id)),
            UserProgress.is_completed.is_(True),
        )
    )
    completed = completed_result.scalar() or 0
    return completed >= total_steps, completed, total_steps


async def _get_previous_step(
    db: AsyncSession,
    step_id: UUID,
) -> Step | None:
    """Return the step that comes immediately before the given step
    in the course, or None if this is the first step."""
    step = await db.get(Step, step_id)
    if step is None:
        return None

    # Load section.course relationship
    stmt = (
        select(Step)
        .options(selectinload(Step.section))
        .where(Step.id == step_id)
    )
    result = await db.execute(stmt)
    step = result.scalar_one_or_none()
    if step is None or step.section is None:
        return None

    course_id = step.section.course_id

    # Get all steps in the course ordered by section.order, step.order
    course_stmt = (
        select(Course)
        .options(selectinload(Course.sections).selectinload(Section.steps))
        .where(Course.id == course_id)
    )
    course_result = await db.execute(course_stmt)
    course = course_result.scalar_one_or_none()
    if course is None:
        return None

    all_steps: list[Step] = []
    for sec in course.sections:
        for s in sec.steps:
            all_steps.append(s)

    for i, s in enumerate(all_steps):
        if s.id == step_id and i > 0:
            return all_steps[i - 1]

    return None


async def mark_step_complete(
    db: AsyncSession,
    user_id: UUID,
    step_id: UUID,
) -> tuple[UserProgress, int]:
    """Mark a step as completed for the given user.

    Enforces **sequential locking**: the previous step must be completed
    before this one can be marked complete (first step is exempt).

    If a UserProgress record already exists for this (user, step) pair
    and is_completed is True, a ValueError is raised.

    Args:
        db: An async database session.
        user_id: The UUID of the user completing the step.
        step_id: The UUID of the step to mark complete.

    Returns:
        A tuple of (UserProgress record, xp_reward earned).

    Raises:
        ValueError: If the step is already completed, or the previous
                    step has not been completed yet.
    """
    # Sequential lock check
    prev_step = await _get_previous_step(db, step_id)
    if prev_step is not None:
        prev_progress = await _get_progress(db, user_id, prev_step.id)
        if prev_progress is None or not prev_progress.is_completed:
            raise ValueError(
                f"Step '{step_id}' is locked. Complete the previous step first."
            )
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

    # Check if this completed the entire course -> send notification
    from app.modules.courses.models import Section as _Section

    course_id = None
    if step and step.section:
        s = await db.get(_Section, step.section_id)
        if s:
            course_id = s.course_id

    if course_id:
        is_done, _, _ = await check_course_completion(db, user_id, course_id)
        if is_done:
            course = await db.get(Course, course_id)
            if course:
                await notify_course_completed(db, user_id, course.title, course_id)

    return progress, xp_earned


async def has_successful_submission(
    db: AsyncSession,
    user_id: UUID,
    step_id: UUID,
) -> bool:
    """Return whether the user has a passing submission for a code step."""
    stmt = (
        select(Submission)
        .where(
            Submission.user_id == user_id,
            Submission.step_id == step_id,
            Submission.verdict == SubmissionVerdict.PASS,
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


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
