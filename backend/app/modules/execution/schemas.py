from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CodeSubmitRequest(BaseModel):
    """Request body for submitting user code for execution.

    Attributes:
        step_id: The UUID of the step this code belongs to.
        code: The source code string to execute in the sandbox.
    """

    step_id: UUID
    code: str = Field(..., min_length=1, description="Source code to execute")


class CodeSubmitResponse(BaseModel):
    """Immediate response returned after a successful submission.

    The front-end should poll the status endpoint with the returned
    submission_id to obtain results.

    Attributes:
        submission_id: UUID identifying the newly created submission.
        status: Initial submission status (always "pending").
    """

    submission_id: UUID
    status: str = "pending"


class SubmissionStatusResponse(BaseModel):
    """Polling response for a code submission's status.

    Attributes:
        submission_id: UUID of the submission.
        status: Current status (pending/running/completed/failed).
        output: Combined stdout + stderr if execution finished, else None.
    """

    submission_id: UUID
    status: str
    output: str | None = None
