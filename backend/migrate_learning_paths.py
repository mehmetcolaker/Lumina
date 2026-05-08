"""Create learning_paths and path_levels tables."""
import asyncio
from app.core.database import engine, Base
import app.modules.users.models  # noqa - register FK targets
import app.modules.courses.models  # noqa - includes LearningPath, PathLevel


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("OK: learning_paths and path_levels tables created")


asyncio.run(run())
