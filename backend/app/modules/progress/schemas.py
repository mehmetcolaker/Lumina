from datetime import datetime
from typing import Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
