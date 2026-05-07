from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---------- Internal enums (mirror of models.StepType) ----------


class StepTypeEnum(str, Enum):
    """Mirrors the database StepType enum for schema serialisation."""

    THEORY = "theory"
    QUIZ = "quiz"
    CODE = "code"


# ---------- Step ----------


class StepBase(BaseModel):
    """Shared Step fields."""

    title: str = Field(..., max_length=255)
    step_type: StepTypeEnum
    content_data: Optional[Dict[str, Any]] = None
    order: int = 0
    xp_reward: int = 10


class StepResponse(StepBase):
    """Step model returned for the course-path endpoint."""

    id: UUID
    section_id: UUID

    model_config = ConfigDict(from_attributes=True)


# ---------- Section ----------


class SectionBase(BaseModel):
    """Shared Section fields."""

    title: str = Field(..., max_length=255)
    order: int = 0


class SectionWithSteps(SectionBase):
    """Section with its nested steps, used in the path response."""

    id: UUID
    course_id: UUID
    steps: List[StepResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ---------- Course ----------


class CourseBase(BaseModel):
    """Shared Course fields."""

    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    language: str = Field(..., max_length=100)


class CourseResponse(CourseBase):
    """Public course summary returned by the list endpoint."""

    id: UUID

    model_config = ConfigDict(from_attributes=True)


class CoursePathResponse(CourseBase):
    """Full hierarchical response: course → sections → steps.

    This is the data the front-end needs to render a Duolingo-style
    learning-path map.
    """

    id: UUID
    sections: List[SectionWithSteps] = []

    model_config = ConfigDict(from_attributes=True)
