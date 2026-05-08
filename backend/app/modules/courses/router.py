from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.courses import services
from app.modules.courses.schemas import (
    CoursePathResponse,
    CourseResponse,
    LearningPathResponse,
    PathLevelResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@router.get(
    "/",
    response_model=List[CourseResponse],
    summary="List all courses",
)
async def list_courses(
    db: AsyncSession = Depends(get_db),
) -> List[CourseResponse]:
    courses = await services.list_courses(db)
    return [CourseResponse.model_validate(c) for c in courses]


@router.get(
    "/{course_id}/path",
    response_model=CoursePathResponse,
    summary="Get the full learning path for a course",
)
async def get_course_path(
    course_id: str,
    db: AsyncSession = Depends(get_db),
) -> CoursePathResponse:
    try:
        UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid course_id format.")

    course = await services.get_course_with_path(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course '{course_id}' not found.")
    return CoursePathResponse.model_validate(course)


# ── Learning Path / Roadmap ────────────────────────────

router_path = APIRouter(prefix="/api/v1/paths", tags=["Roadmap"])


@router_path.get(
    "/",
    response_model=List[LearningPathResponse],
    summary="List all learning paths",
)
async def list_paths(
    db: AsyncSession = Depends(get_db),
) -> List[LearningPathResponse]:
    """Return all learning paths with their levels and courses."""
    paths = await services.list_paths(db)
    return [LearningPathResponse.model_validate(p) for p in paths]


@router_path.get(
    "/{path_id}",
    response_model=LearningPathResponse,
    summary="Get a learning path with user progress",
)
async def get_path_with_progress(
    path_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> LearningPathResponse:
    """Return a single learning path where each level is annotated with
    the current user's completion progress and unlock status.

    - ``unlocked``: True if the previous level's progress meets the required threshold.
    - ``progress_pct``: Percentage of steps completed within that level.
    """
    try:
        pid = UUID(path_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid path_id format.")

    path = await services.get_path_progress(db, pid, current_user.id)
    if path is None:
        raise HTTPException(status_code=404, detail="Learning path not found.")

    # Map internal attrs to schema
    level_responses = []
    for level in path.levels:
        unlocked = getattr(level, "_unlocked", False)
        progress = getattr(level, "_progress_pct", 0)
        level_responses.append(
            PathLevelResponse(
                id=level.id,
                level_name=level.level_name,
                order=level.order,
                required_progress_pct=level.required_progress_pct,
                course=CourseResponse.model_validate(level.course),
                unlocked=unlocked,
                progress_pct=progress,
            )
        )

    return LearningPathResponse(
        id=path.id,
        title=path.title,
        description=path.description,
        language=path.language,
        icon=path.icon,
        order=path.order,
        levels=level_responses,
    )
