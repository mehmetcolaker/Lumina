"""Redis-backed rate limiter for sensitive endpoints (auth, etc.).

Provides a FastAPI dependency that restricts the caller (by IP) to a
maximum number of requests within a sliding window.

Usage in a router::

    from app.core.rate_limiter import rate_limit

    @router.post("/auth/login")
    async def login(_, _limit: None = Depends(rate_limit(5, 60))):
        ...
"""

import time
from collections.abc import Callable
from typing import Optional

from fastapi import Depends, HTTPException, Request, status

from app.core.redis_client import get_redis


def rate_limit(max_requests: int = 5, window_seconds: int = 60) -> Callable:
    """Return a FastAPI dependency that enforces a sliding-window rate limit.

    Uses a Redis sorted set per IP to track request timestamps.

    Args:
        max_requests: Maximum number of requests allowed in the window.
        window_seconds: Width of the sliding window in seconds.

    Returns:
        A FastAPI dependency callable.

    Raises:
        HTTPException 429: When the limit is exceeded.
    """

    async def _dependency(request: Request) -> None:
        client_ip: str = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}"
        now = time.time()
        window_start = now - window_seconds

        try:
            redis = get_redis()

            # Remove entries outside the window
            await redis.zremrangebyscore(key, 0, window_start)

            # Count current window entries
            count = await redis.zcard(key)

            if count is not None and count >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {window_seconds} seconds.",
                )

            # Record this request
            await redis.zadd(key, {str(now): now})
            await redis.expire(key, window_seconds)

        except HTTPException:
            # Re-raise 429 — don't swallow it
            raise
        except Exception:
            # Redis unavailable (RuntimeError, TimeoutError, ConnectionError, etc.)
            # — allow the request through silently
            pass

    return _dependency
