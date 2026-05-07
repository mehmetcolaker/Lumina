"""Async Redis client singleton for the Lumina platform.

Provides a single ``redis.asyncio`` client instance initialised from
``Settings.REDIS_URL``.  The lifespan hook in ``main.py`` calls
``init_redis`` / ``close_redis``.
"""

import logging
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Optional[Redis] = None

# Name of the sorted set used for the global leaderboard.
LEADERBOARD_KEY = "leaderboard"


async def init_redis() -> None:
    """Create and store the global async Redis connection."""
    global redis_client
    redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
    # Ping to verify connectivity
    await redis_client.ping()
    logger.info("Async Redis client connected.")


async def close_redis() -> None:
    """Close the global async Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None
        logger.info("Async Redis client closed.")


def get_redis() -> Redis:
    """Return the global async Redis client.

    Raises:
        RuntimeError: If ``init_redis`` has not been called yet.
    """
    if redis_client is None:
        raise RuntimeError(
            "Redis client is not initialised.  Call init_redis() on startup."
        )
    return redis_client
