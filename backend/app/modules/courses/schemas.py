from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StepTypeEnum(str, Enum):
    THEORY = "theory"
    QUIZ = "quiz"
    CODE = "code"


class StepBase(BaseModel):
    title: str = Field(..., max_length=255)
    step_type: StepTypeEnum
    content_data: Optional[Dict[str, Any]] = None
    order: int = 0
    xp_reward: int = 10


class StepResponse(StepBase):
    id: UUID
    section_id: UUID
    model_config = ConfigDict(from_attributes=True)


class SectionBase(BaseModel):
    title: str = Field(..., max_length=255)
    order: int = 0


class SectionWithSteps(SectionBase):
    id: UUID
    course_id: UUID
    steps: List[StepResponse] = []
    model_config = ConfigDict(from_attributes=True)


class CourseBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    language: str = Field(..., max_length=100)


class CourseResponse(CourseBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class CoursePathResponse(CourseBase):
    id: UUID
    sections: List[SectionWithSteps] = []
    model_config = ConfigDict(from_attributes=True)


# ── Learning Path (Roadmap) ────────────────────────────

class PathLevelResponse(BaseModel):
    """A single level in a learning path.

    Attributes:
        id: PathLevel UUID.
        level_name: e.g. "Beginner 1", "Intermediate 2".
        order: Ordinal position (1-based).
        required_progress_pct: % of previous level needed to unlock.
        course: The Course associated with this level.
        unlocked: Whether the current user has access.
        progress_pct: % of steps completed in this level (for the user).
    """

    id: UUID
    level_name: str
    order: int
    required_progress_pct: int
    course: CourseResponse
    unlocked: bool = False
    progress_pct: int = 0

    model_config = ConfigDict(from_attributes=True)


class LearningPathResponse(BaseModel):
    """Full learning path with levels."""

    id: UUID
    title: str
    description: Optional[str] = None
    language: str
    icon: Optional[str] = None
    order: int
    levels: List[PathLevelResponse] = []

    model_config = ConfigDict(from_attributes=True)
