"""Notification API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.notifications import services
from app.modules.notifications.schemas import (
    NotificationCountResponse,
    NotificationResponse,
)
from app.modules.users.router import get_current_user
from app.modules.users.schemas import UserResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get(
    "/",
    response_model=list[NotificationResponse],
    summary="List notifications for current user",
)
async def list_notifications(
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[NotificationResponse]:
    """Return recent notifications for the authenticated user."""
    notifs = await services.list_notifications(
        db, current_user.id, limit=limit, unread_only=unread_only
    )
    return [NotificationResponse.model_validate(n) for n in notifs]


@router.get(
    "/unread-count",
    response_model=NotificationCountResponse,
    summary="Get unread notification count",
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> NotificationCountResponse:
    """Return the number of unread notifications."""
    count = await services.count_unread(db, current_user.id)
    return NotificationCountResponse(count=count)


@router.post(
    "/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark a notification as read",
)
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Mark a single notification as read."""
    try:
        nid = UUID(notification_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid notification_id.")
    ok = await services.mark_as_read(db, current_user.id, nid)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found.")


@router.post(
    "/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark all notifications as read",
)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Mark all notifications as read for the current user."""
    await services.mark_all_as_read(db, current_user.id)
