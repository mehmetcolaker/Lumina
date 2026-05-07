"""Admin API — superuser-only endpoints for platform management.

Every endpoint in this router requires the caller to be both
authenticated and a superuser (``User.is_superuser == True``).
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.admin import services as admin_services
from app.modules.admin.schemas import (
    AdminCourseCreate,
    AdminSectionCreate,
    AdminStepCreate,
    AdminStepUpdate,
    AdminUserResponse,
    AdminUserUpdate,
)
from app.modules.courses.schemas import CourseResponse, SectionWithSteps, StepResponse
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


# ---------------------------------------------------------------------------
# Superuser guard dependency
# ---------------------------------------------------------------------------


async def require_superuser(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    """Verify that the authenticated user is a superuser.

    Raises:
        HTTPException 403: If the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
    summary="List all users (admin)",
)
async def admin_list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> list[AdminUserResponse]:
    """Return a paginated list of all registered users."""
    users = await admin_services.list_all_users(db, skip=skip, limit=limit)
    return [AdminUserResponse.model_validate(u) for u in users]


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Get a single user (admin)",
)
async def admin_get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> AdminUserResponse:
    """Return full details for a specific user."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user_id format.")
    user = await admin_services.get_user_by_id_admin(db, uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return AdminUserResponse.model_validate(user)


@router.patch(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="Update a user (admin)",
)
async def admin_update_user(
    user_id: str,
    payload: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> AdminUserResponse:
    """Partially update a user's profile (active, premium, superuser, etc.)."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user_id format.")
    updates = payload.model_dump(exclude_none=True)
    user = await admin_services.update_user(db, uid, updates)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return AdminUserResponse.model_validate(user)


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user (admin)",
)
async def admin_delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> None:
    """Soft-delete a user by setting is_active=False."""
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid user_id format.")
    deleted = await admin_services.delete_user(db, uid)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")


# ---------------------------------------------------------------------------
# Course management
# ---------------------------------------------------------------------------


@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course (admin)",
)
async def admin_create_course(
    payload: AdminCourseCreate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> CourseResponse:
    """Create a new top-level course."""
    course = await admin_services.create_course(db, payload.model_dump())
    return CourseResponse.model_validate(course)


@router.put(
    "/courses/{course_id}",
    response_model=CourseResponse,
    summary="Update a course (admin)",
)
async def admin_update_course(
    course_id: str,
    payload: AdminCourseCreate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> CourseResponse:
    """Replace the fields of an existing course."""
    try:
        cid = UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid course_id format.")
    course = await admin_services.update_course(db, cid, payload.model_dump())
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    return CourseResponse.model_validate(course)


@router.delete(
    "/courses/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course and its contents (admin)",
)
async def admin_delete_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> None:
    """Permanently delete a course, its sections, and steps."""
    try:
        cid = UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid course_id format.")
    deleted = await admin_services.delete_course(db, cid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found.")


# ---------------------------------------------------------------------------
# Section management
# ---------------------------------------------------------------------------


@router.post(
    "/courses/{course_id}/sections",
    response_model=SectionWithSteps,
    status_code=status.HTTP_201_CREATED,
    summary="Add a section to a course (admin)",
)
async def admin_create_section(
    course_id: str,
    payload: AdminSectionCreate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> SectionWithSteps:
    """Create a new section within an existing course."""
    try:
        cid = UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid course_id format.")
    section = await admin_services.create_section(db, cid, payload.model_dump())
    return SectionWithSteps.model_validate(section)


@router.delete(
    "/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a section (admin)",
)
async def admin_delete_section(
    section_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> None:
    """Permanently delete a section and its steps."""
    try:
        sid = UUID(section_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid section_id format.")
    deleted = await admin_services.delete_section(db, sid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Section not found.")


# ---------------------------------------------------------------------------
# Step management
# ---------------------------------------------------------------------------


@router.post(
    "/sections/{section_id}/steps",
    response_model=StepResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a step to a section (admin)",
)
async def admin_create_step(
    section_id: str,
    payload: AdminStepCreate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> StepResponse:
    """Create a new step within a section."""
    try:
        sid = UUID(section_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid section_id format.")
    step = await admin_services.create_step(db, sid, payload.model_dump())
    return StepResponse.model_validate(step)


@router.put(
    "/steps/{step_id}",
    response_model=StepResponse,
    summary="Update a step (admin)",
)
async def admin_update_step(
    step_id: str,
    payload: AdminStepUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> StepResponse:
    """Update the fields of an existing step."""
    try:
        sid = UUID(step_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid step_id format.")
    updates = payload.model_dump(exclude_none=True)
    step = await admin_services.update_step(db, sid, updates)
    if step is None:
        raise HTTPException(status_code=404, detail="Step not found.")
    return StepResponse.model_validate(step)


@router.delete(
    "/steps/{step_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a step (admin)",
)
async def admin_delete_step(
    step_id: str,
    db: AsyncSession = Depends(get_db),
    _: UserResponse = Depends(require_superuser),
) -> None:
    """Permanently delete a single step."""
    try:
        sid = UUID(step_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid step_id format.")
    deleted = await admin_services.delete_step(db, sid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Step not found.")
