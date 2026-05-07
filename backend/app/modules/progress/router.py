from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.courses.services import get_course_with_path
from app.modules.gamification.services import award_xp
from app.modules.progress import services as progress_services
from app.modules.progress.schemas import (
    MyPathResponse,
    MyPathSection,
    MyPathStep,
    StepCompleteResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/progress", tags=["Progress"])


@router.post(
    "/steps/{step_id}/complete",
    response_model=StepCompleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark a step as completed",
)
async def complete_step(
    step_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> StepCompleteResponse:
    """Mark a specific learning step as completed by the authenticated user.

    Args:
        step_id: The UUID of the step to mark complete.

    Raises:
        400: If the step is already completed by this user.
        404: If the step does not exist.
    """
    from uuid import UUID

    user_uuid = current_user.id
    step_uuid = UUID(step_id)

    try:
        progress, xp = await progress_services.mark_step_complete(
            db, user_uuid, step_uuid
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Award XP via the gamification module (Postgres + Redis leaderboard sync)
    await award_xp(db, user_uuid, xp)

    return StepCompleteResponse(
        step_id=step_uuid,
        completed_at=progress.completed_at,
        xp_earned=xp,
    )


@router.get(
    "/my-path/{course_id}",
    response_model=MyPathResponse,
    summary="Get the user's progress in a course",
)
async def get_my_path(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> MyPathResponse:
    """Return the authenticated user's progress for every step in a course.

    This endpoint mirrors the ``/courses/{course_id}/path`` structure but
    enriches each step with the current user's completion flag.

    Args:
        course_id: The UUID of the course.

    Raises:
        404: If the course does not exist.
    """
    from uuid import UUID

    user_uuid = current_user.id
    course_uuid = UUID(course_id)

    course = await get_course_with_path(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )

    completed_map = await progress_services.get_user_progress_for_course(
        db, user_uuid, course_uuid
    )

    sections = []
    for sec in course.sections:
        steps = [
            MyPathStep(
                step_id=step.id,
                is_completed=str(step.id) in completed_map,
            )
            for step in sec.steps
        ]
        sections.append(
            MyPathSection(
                section_id=sec.id,
                title=sec.title,
                order=sec.order,
                steps=steps,
            )
        )

    return MyPathResponse(
        course_id=course_uuid,
        sections=sections,
    )
