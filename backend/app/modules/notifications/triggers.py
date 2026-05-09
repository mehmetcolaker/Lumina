"""Automatic notification triggers for key platform events.

Each function creates a ``Notification`` record when the corresponding
event occurs.  Call these from service-layer code (e.g. ``award_xp``,
comment creation).
"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.services import create_notification

logger = logging.getLogger(__name__)


async def notify_badge_awarded(
    db: AsyncSession,
    user_id: UUID,
    badge_title: str,
    badge_emoji: str,
) -> None:
    """Notify a user when they earn a new badge."""
    try:
        await create_notification(
            db,
            user_id=user_id,
            type="badge",
            title=f"New badge earned! {badge_emoji} {badge_title}",
            body=f"Congratulations! You have unlocked the '{badge_title}' badge.",
            link="/profile",
        )
    except Exception as exc:
        logger.warning("Failed to create badge notification: %s", exc)


async def notify_xp_milestone(
    db: AsyncSession,
    user_id: UUID,
    total_xp: int,
) -> None:
    """Notify a user on major XP milestones (100, 1000, 5000)."""
    if total_xp in (100, 1000, 5000):
        try:
            await create_notification(
                db,
                user_id=user_id,
                type="xp",
                title=f"{total_xp} XP reached!",
                body=f"You have accumulated {total_xp} total XP. Keep going!",
                link="/dashboard",
            )
        except Exception as exc:
            logger.warning("Failed to create XP milestone notification: %s", exc)


async def notify_streak_milestone(
    db: AsyncSession,
    user_id: UUID,
    streak: int,
) -> None:
    """Notify a user on streak milestones (3, 7, 30 days)."""
    if streak in (3, 7, 30):
        try:
            days_str = {3: "3-day", 7: "7-day", 30: "30-day"}
            await create_notification(
                db,
                user_id=user_id,
                type="streak",
                title=f"{days_str.get(streak, f'{streak}-day')} streak!",
                body=f"Amazing! You've maintained a {streak}-day learning streak.",
                link="/dashboard",
            )
        except Exception as exc:
            logger.warning("Failed to create streak notification: %s", exc)


async def notify_comment_reply(
    db: AsyncSession,
    recipient_user_id: UUID,
    replier_email: str,
    step_id: UUID,
    reply_content: str,
) -> None:
    """Notify a user when someone replies to their comment."""
    try:
        preview = reply_content[:100] + ("..." if len(reply_content) > 100 else "")
        await create_notification(
            db,
            user_id=recipient_user_id,
            type="reply",
            title=f"New reply from {replier_email.split('@')[0]}",
            body=preview,
            link=f"/courses/$slug",  # frontend will resolve
        )
    except Exception as exc:
        logger.warning("Failed to create reply notification: %s", exc)


async def notify_course_completed(
    db: AsyncSession,
    user_id: UUID,
    course_title: str,
    course_id: UUID,
) -> None:
    """Notify a user when they complete a course."""
    try:
        await create_notification(
            db,
            user_id=user_id,
            type="system",
            title=f"Course completed!",
            body=f"You have finished '{course_title}'. Download your certificate!",
            link=f"/courses/{course_id}",
        )
    except Exception as exc:
        logger.warning("Failed to create course completion notification: %s", exc)
