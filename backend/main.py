from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.core.middleware import register_middleware
from app.core.redis_client import close_redis, init_redis
from app.modules.courses.router import router as courses_router
from app.modules.execution.router import router as execution_router
from app.modules.gamification.router import router as gamification_router
from app.modules.monetization.router import router as monetization_router
from app.modules.progress.router import router as progress_router
from app.modules.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    On startup:
        - Initialise the async Redis client.
    On shutdown:
        - Dispose of the database connection pool.
        - Close the async Redis client.

    **Note:** Database tables are managed via Alembic migrations, not
    ``create_all``.  Run ``alembic upgrade head`` before starting the
    server.
    """
    try:
        await init_redis()
    except Exception as exc:
        import logging

        logging.getLogger("uvicorn.error").warning(
            "Redis unavailable — leaderboard & rate-limiter will "
            "use fallbacks. %s",
            exc,
        )

    yield

    await engine.dispose()
    await close_redis()


app = FastAPI(
    title="Lumina API",
    description="Interactive coding education SaaS platform — backend API.",
    version="0.5.0",
    lifespan=lifespan,
)

# --- Middleware (CORS, global exception handler) ---
register_middleware(app)

# --- Routers ---
app.include_router(users_router)
app.include_router(courses_router)
app.include_router(progress_router)
app.include_router(execution_router)
app.include_router(gamification_router)
app.include_router(monetization_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}
