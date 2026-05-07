from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.core.redis_client import close_redis, init_redis
from app.modules.courses.router import router as courses_router
from app.modules.execution.router import router as execution_router
from app.modules.gamification.router import router as gamification_router
from app.modules.progress.router import router as progress_router
from app.modules.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler.

    On startup:
        - Create all database tables that do not yet exist
          (development convenience — replace with Alembic migrations in production).
        - Initialise the async Redis client (leaderboard, caching etc.).

    On shutdown:
        - Dispose of the database connection pool.
        - Close the async Redis client.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        await init_redis()
    except Exception as exc:
        import logging
        logging.getLogger("uvicorn.error").warning(
            "Redis unavailable — leaderboard will fall back to Postgres. %s", exc
        )

    yield

    await engine.dispose()
    await close_redis()


app = FastAPI(
    title="Lumina API",
    description="Interactive coding education SaaS platform — backend API.",
    version="0.4.0",
    lifespan=lifespan,
)

app.include_router(users_router)
app.include_router(courses_router)
app.include_router(progress_router)
app.include_router(execution_router)
app.include_router(gamification_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint."""
    return {"status": "ok"}
