from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.execution import tasks
from app.modules.execution.models import Submission, SubmissionStatus
from app.modules.execution.schemas import (
    CodeSubmitRequest,
    CodeSubmitResponse,
    SubmissionStatusResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/execution", tags=["Execution (Sandbox)"])


@router.post(
    "/submit",
    response_model=CodeSubmitResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit user code for sandboxed execution",
)
async def submit_code(
    payload: CodeSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> CodeSubmitResponse:
    """Accept user code, create a pending ``Submission`` record, and
    enqueue a Celery task to run it in an isolated Docker sandbox.

    Args:
        payload: Contains ``step_id`` and the source ``code`` string.

    Returns:
        A ``submission_id`` that the front-end can poll via the
        status endpoint.
    """
    submission = Submission(
        user_id=current_user.id,
        step_id=payload.step_id,
        code=payload.code,
        status=SubmissionStatus.PENDING,
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)

    # Dispatch the Celery task asynchronously
    tasks.execute_user_code.delay(str(submission.id))

    return CodeSubmitResponse(
        submission_id=submission.id,
        status=submission.status.value,
    )


@router.get(
    "/status/{submission_id}",
    response_model=SubmissionStatusResponse,
    summary="Poll the execution status of a submission",
)
async def get_submission_status(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> SubmissionStatusResponse:
    """Return the current status and output (if finished) of a code
    submission. The front-end should poll this endpoint at regular
    intervals until the status is ``completed`` or ``failed``.

    Args:
        submission_id: UUID of the submission to query.

    Raises:
        404: If the submission does not exist.
        403: If the submission belongs to another user.
    """
    try:
        sub_id = UUID(submission_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid submission_id format.",
        )

    from sqlalchemy import select

    result = await db.execute(select(Submission).where(Submission.id == sub_id))
    submission = result.scalar_one_or_none()

    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found.",
        )

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own submissions.",
        )

    return SubmissionStatusResponse(
        submission_id=submission.id,
        status=submission.status.value,
        output=submission.output,
    )
