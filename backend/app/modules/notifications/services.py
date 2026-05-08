"""Notification business logic."""

import logging
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification

logger = logging.getLogger(__name__)


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    type: str,
    title: str,
    body: str | None = None,
    link: str | None = None,
) -> Notification:
    """Create a notification for a user.

    Args:
        db: Async database session.
        user_id: Recipient user UUID.
        type: Notification type (streak, badge, reply, xp, system).
        title: Short title.
        body: Optional body text.
        link: Optional deep-link.

    Returns:
        The created Notification instance.
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        link=link,
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    logger.info("Notification created for user %s: %s", user_id, title)
    return notification


async def list_notifications(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 20,
    unread_only: bool = False,
) -> list[Notification]:
    """Return recent notifications for a user.

    Args:
        db: Async database session.
        user_id: User UUID.
        limit: Max notifications to return.
        unread_only: Only return unread notifications.

    Returns:
        A list of Notification instances, newest first.
    """
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def mark_as_read(
    db: AsyncSession,
    user_id: UUID,
    notification_id: UUID,
) -> bool:
    """Mark a single notification as read. Returns True if found."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    notif = result.scalar_one_or_none()
    if notif is None:
        return False
    notif.is_read = True
    db.add(notif)
    await db.flush()
    return True


async def mark_all_as_read(
    db: AsyncSession,
    user_id: UUID,
) -> int:
    """Mark all notifications as read for a user. Returns count."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    )
    notifs = result.scalars().all()
    for n in notifs:
        n.is_read = True
    await db.flush()
    return len(notifs)


async def count_unread(
    db: AsyncSession,
    user_id: UUID,
) -> int:
    """Return the number of unread notifications for a user."""
    result = await db.execute(
        select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    )
    return result.scalar() or 0
