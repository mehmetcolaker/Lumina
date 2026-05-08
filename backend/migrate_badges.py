"""Create user_badges table."""
import asyncio
from app.core.database import engine, Base
import app.modules.users.models  # noqa
import app.modules.gamification.models  # noqa


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("OK: user_badges table created")


asyncio.run(run())
