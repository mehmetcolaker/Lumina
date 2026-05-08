from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CodeSubmitRequest(BaseModel):
    """Request body for submitting user code for execution."""

    step_id: UUID
    code: str = Field(..., min_length=1, description="Source code to execute")


class CodeSubmitResponse(BaseModel):
    """Immediate response returned after a successful submission."""

    submission_id: UUID
    status: str = "pending"


class TestResult(BaseModel):
    """Result of a single test case.

    Attributes:
        name: Test case name/description.
        input: The input used for this test.
        expected: Expected output.
        actual: Actual stdout produced.
        passed: Whether the test passed.
        stderr: Any error output from this test.
        runtime_ms: Execution time of this test.
    """

    name: str = ""
    input: str = ""
    expected: str = ""
    actual: str = ""
    passed: bool = False
    stderr: str = ""
    runtime_ms: int = 0


class SubmissionStatusResponse(BaseModel):
    """Polling response for a code submission's status."""

    submission_id: UUID
    status: str
    code: str | None = None
    output: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    runtime_ms: int | None = None
    verdict: str | None = None
    test_results: list[TestResult] | None = None
    created_at: str | None = None


class ExecutionResult(BaseModel):
    """Result from the Docker sandbox or SQLite executor."""

    stdout: str
    stderr: str
    exit_code: int | None = 0
    runtime_ms: int
    timed_out: bool = False
