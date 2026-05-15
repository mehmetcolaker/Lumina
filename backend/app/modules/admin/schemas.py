"""Pydantic schemas for the Admin API."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.courses.schemas import StepTypeEnum


# ---------- User management ----------


class AdminUserUpdate(BaseModel):
    """Request body for updating a user (admin-only)."""

    email: str | None = Field(None, max_length=255)
    is_active: bool | None = None
    is_premium: bool | None = None
    is_superuser: bool | None = None


class AdminUserResponse(BaseModel):
    """Full user profile visible to admins."""

    id: UUID
    email: str
    is_active: bool
    is_premium: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Course management ----------


class AdminCourseCreate(BaseModel):
    """Request body for creating a new course."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    language: str = Field(..., max_length=100)
    level: str | None = Field(None, max_length=50)
    runtime_language: str | None = Field(None, max_length=50)
    runtime_version: str | None = Field(None, max_length=50)
    outcomes: list[str] | None = None
    prerequisites: list[str] | None = None


class AdminSectionCreate(BaseModel):
    """Request body for creating a new section within a course."""

    title: str = Field(..., max_length=255)
    order: int = 0


class AdminStepCreate(BaseModel):
    """Request body for creating a new step within a section."""

    title: str = Field(..., max_length=255)
    step_type: StepTypeEnum
    order: int = 0
    xp_reward: int = Field(default=10, ge=0)
    content_data: dict | None = None
    runtime_language: str | None = Field(None, max_length=50)
    runtime_version: str | None = Field(None, max_length=50)
    previewable: bool = False


class AdminStepUpdate(BaseModel):
    """Request body for updating an existing step."""

    title: str | None = None
    step_type: StepTypeEnum | None = None
    order: int | None = None
    xp_reward: int | None = Field(None, ge=0)
    content_data: dict | None = None
    runtime_language: str | None = Field(None, max_length=50)
    runtime_version: str | None = Field(None, max_length=50)
    previewable: bool | None = None
