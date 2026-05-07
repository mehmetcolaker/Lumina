"""Gamification business logic.

Handles XP awards (Postgres + Redis leaderboard sync), leaderboard
queries against Redis sorted sets, line-comment CRUD, and streak
management.
"""

import logging
from datetime import date, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import LEADERBOARD_KEY, get_redis
from app.modules.gamification.models import LineComment, UserStats
from app.modules.users.models import User

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# XP & Leaderboard
# ------------------------------------------------------------------


async def award_xp(db: AsyncSession, user_id: UUID, xp_amount: int) -> int:
    """Add experience points to a user and sync the Redis leaderboard.

    Creates a ``UserStats`` row on first call for the user.  Afterwards
    it performs an atomic increment on both Postgres and Redis.

    Also updates the user's streak based on ``last_active_date``:

        - If the last active date is **yesterday** → streak is incremented.
        - If the last active date is **today** → streak is left unchanged.
        - If the last active date is older (or never set) → streak is reset to 1.

    Args:
        db: An async database session.
        user_id: The UUID of the user receiving XP.
        xp_amount: The number of XP to grant (> 0).

    Returns:
        The user's new total_xp after the award.

    Raises:
        ValueError: If xp_amount is not positive.
    """
    if xp_amount <= 0:
        raise ValueError("XP amount must be positive.")

    stats = await _get_or_create_stats(db, user_id)

    # --- Streak logic ---
    today = date.today()
    yesterday = today - timedelta(days=1)

    if stats.last_active_date == yesterday:
        stats.current_streak += 1
    elif stats.last_active_date == today:
        pass  # same day, no change
    else:
        stats.current_streak = 1  # gap → reset

    stats.total_xp += xp_amount
    stats.last_active_date = today

    db.add(stats)
    await db.flush()

    # Sync to Redis leaderboard (sorted set)
    try:
        redis = get_redis()
        await redis.zadd(LEADERBOARD_KEY, {str(user_id): stats.total_xp})
    except Exception:
        logger.warning("Failed to sync XP to Redis for user %s", user_id)

    logger.info(
        "Awarded %d XP to user %s (total now %d, streak %d)",
        xp_amount,
        user_id,
        stats.total_xp,
        stats.current_streak,
    )

    return stats.total_xp


async def get_leaderboard(
    db: AsyncSession,
    limit: int = 10,
) -> list[dict]:
    """Return the top-N users sorted by total XP.

    Reads from Redis (``ZREVRANGE``) for near-instant response.
    Falls back to Postgres if Redis is unavailable.

    Args:
        db: An async database session (used for fallback / email lookup).
        limit: Maximum number of entries to return (default 10).

    Returns:
        A list of dicts with keys ``rank``, ``user_id``, ``email``,
        ``total_xp``.
    """
    try:
        redis = get_redis()
        results = await redis.zrevrange(
            LEADERBOARD_KEY, 0, limit - 1, withscores=True
        )
        entries = []
        for rank, (member, score) in enumerate(results, start=1):
            user_id_str: str = member  # type: ignore[assignment]
            xp: int = int(score)  # type: ignore[arg-type]

            email = await _get_user_email(db, UUID(user_id_str)) or "unknown"

            entries.append(
                {
                    "rank": rank,
                    "user_id": UUID(user_id_str),
                    "email": email,
                    "total_xp": xp,
                }
            )
        return entries
    except Exception:
        logger.warning("Redis unavailable, falling back to Postgres leaderboard.")
        return await _leaderboard_from_pg(db, limit)


# ------------------------------------------------------------------
# Line comments
# ------------------------------------------------------------------


async def add_comment(
    db: AsyncSession,
    user_id: UUID,
    step_id: UUID,
    line_number: int,
    content: str,
) -> LineComment:
    """Create a new line comment.

    Args:
        db: An async database session.
        user_id: UUID of the comment author.
        step_id: UUID of the step.
        line_number: 1-based line number.
        content: The comment text.

    Returns:
        The newly created ``LineComment`` instance.
    """
    comment = LineComment(
        step_id=step_id,
        user_id=user_id,
        line_number=line_number,
        content=content,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return comment


async def get_comments_for_step(
    db: AsyncSession,
    step_id: UUID,
) -> list[dict]:
    """Return all comments for a step, ordered by line number then time.

    Each entry is augmented with the author's email.

    Args:
        db: An async database session.
        step_id: UUID of the step.

    Returns:
        A list of comment dicts ready for serialisation.
    """
    stmt = (
        select(LineComment, User.email)
        .join(User, LineComment.user_id == User.id)
        .where(LineComment.step_id == step_id)
        .order_by(LineComment.line_number, LineComment.created_at)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "id": comment.id,
            "step_id": comment.step_id,
            "user_id": comment.user_id,
            "email": email,
            "line_number": comment.line_number,
            "content": comment.content,
            "created_at": comment.created_at,
        }
        for comment, email in rows
    ]


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


async def _get_or_create_stats(db: AsyncSession, user_id: UUID) -> UserStats:
    """Return the UserStats row for *user_id*, creating one if absent."""
    stmt = select(UserStats).where(UserStats.user_id == user_id)
    result = await db.execute(stmt)
    stats = result.scalar_one_or_none()
    if stats is None:
        stats = UserStats(user_id=user_id)
        db.add(stats)
        await db.flush()
        await db.refresh(stats)
    return stats


async def _get_user_email(db: AsyncSession, user_id: UUID) -> str | None:
    """Look up a user's email by their UUID."""
    result = await db.execute(select(User.email).where(User.id == user_id))
    row = result.scalar_one_or_none()
    return row


async def _leaderboard_from_pg(
    db: AsyncSession,
    limit: int,
) -> list[dict]:
    """Fallback leaderboard queried directly from Postgres."""
    stmt = (
        select(UserStats, User.email)
        .join(User, UserStats.user_id == User.id)
        .order_by(UserStats.total_xp.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {
            "rank": idx + 1,
            "user_id": stats.user_id,
            "email": email,
            "total_xp": stats.total_xp,
        }
        for idx, (stats, email) in enumerate(rows)
    ]
