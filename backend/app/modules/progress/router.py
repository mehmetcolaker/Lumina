from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.courses.models import Step
from app.modules.courses.services import get_course_with_path
from app.modules.gamification.services import award_xp
from app.modules.progress import services as progress_services
from app.modules.progress.schemas import (
    MyPathResponse,
    MyPathSection,
    MyPathStep,
    QuizAnswerRequest,
    QuizAnswerResponse,
    StepCompleteResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/progress", tags=["Progress"])


@router.post(
    "/steps/{step_id}/answer",
    response_model=QuizAnswerResponse,
    summary="Submit a quiz answer for server-side validation",
)
async def answer_quiz(
    step_id: str,
    payload: QuizAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> QuizAnswerResponse:
    """Validate a quiz answer server-side.

    The front-end sends the selected option ID, the backend checks it
    against the stored ``correct_option`` (which is never sent to the
    client), and returns the result.

    If the answer is correct, the step is automatically marked complete
    and XP is awarded.
    """
    try:
        step_uuid = UUID(step_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid step_id format.")

    step = await db.get(Step, step_uuid)
    if step is None:
        raise HTTPException(status_code=404, detail="Step not found.")
    if step.step_type.value != "quiz":
        raise HTTPException(status_code=400, detail="Step is not a quiz.")

    content = step.content_data or {}
    correct_option: str = content.get("correct_option", "")
    explanation: str | None = content.get("explanation")

    is_correct = payload.option_id == correct_option

    if is_correct:
        xp_earned = step.xp_reward
        try:
            await progress_services.mark_step_complete(db, current_user.id, step_uuid)
            await award_xp(db, current_user.id, xp_earned)
        except ValueError:
            pass  # already completed
        return QuizAnswerResponse(
            is_correct=True,
            explanation=explanation,
            xp_earned=xp_earned,
        )
    else:
        return QuizAnswerResponse(
            is_correct=False,
            correct_option=correct_option,
            explanation=explanation,
            xp_earned=0,
        )


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
