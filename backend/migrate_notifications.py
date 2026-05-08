"""Create notifications table."""
import asyncio
from app.core.database import engine, Base
import app.modules.users.models  # noqa: F401 - register User table
import app.modules.notifications.models  # noqa: F401


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("OK: notifications table created")


asyncio.run(run())
