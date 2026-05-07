from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.courses import services
from app.modules.courses.schemas import CoursePathResponse, CourseResponse

router = APIRouter(prefix="/api/v1/courses", tags=["Courses"])


@router.get(
    "/",
    response_model=List[CourseResponse],
    summary="List all courses",
)
async def list_courses(
    db: AsyncSession = Depends(get_db),
) -> List[CourseResponse]:
    """Return every course available on the platform.

    Useful for populating a course-catalogue page.
    """
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
    """Return a single course with its sections and steps in a hierarchical
    structure — the data the front-end needs to render a Duolingo-style
    learning-path map.

    Args:
        course_id: The UUID of the course to fetch.

    Raises:
        422: If ``course_id`` is not a valid UUID.
        404: If no course with the given ID exists.
    """
    try:
        UUID(course_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid course_id format.",
        )

    course = await services.get_course_with_path(db, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course '{course_id}' not found.",
        )
    return CoursePathResponse.model_validate(course)
