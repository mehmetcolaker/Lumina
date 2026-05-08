from datetime import datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StepCompleteResponse(BaseModel):
    """Response returned after marking a step as complete.

    Attributes:
        step_id: The UUID of the just-completed step.
        completed_at: The timestamp of completion.
        xp_earned: The XP rewarded for this step.
    """

    step_id: UUID
    completed_at: datetime
    xp_earned: int


class QuizAnswerRequest(BaseModel):
    """Request body for submitting a quiz answer.

    Attributes:
        step_id: The UUID of the quiz step.
        option_id: The ID of the selected option (e.g. "a", "b", "c", "d").
    """

    step_id: UUID
    option_id: str = Field(..., min_length=1, max_length=10)


class QuizAnswerResponse(BaseModel):
    """Response after validating a quiz answer.

    Attributes:
        is_correct: Whether the answer was correct.
        correct_option: The correct option ID (only if wrong).
        explanation: The answer explanation.
        xp_earned: XP earned if correct, 0 if wrong.
    """

    is_correct: bool
    correct_option: str | None = None
    explanation: str | None = None
    xp_earned: int = 0


class MyPathStep(BaseModel):
    """Lightweight step representation for the my-path endpoint.

    Attributes:
        step_id: The step UUID.
        is_completed: Whether the current user has finished this step.
    """

    step_id: UUID
    is_completed: bool


class MyPathSection(BaseModel):
    """A section with per-step completion flags for the current user.

    Attributes:
        section_id: The section UUID.
        title: Section title.
        order: Ordinal position.
        steps: List of steps with their completion status.
    """

    section_id: UUID
    title: str
    order: int
    steps: list[MyPathStep] = []


class MyPathResponse(BaseModel):
    """User's progress snapshot for a given course.

    Attributes:
        course_id: The course UUID.
        sections: Sections enriched with per-user completion flags.
    """

    course_id: UUID
    sections: list[MyPathSection] = []

    model_config = ConfigDict(from_attributes=True)
