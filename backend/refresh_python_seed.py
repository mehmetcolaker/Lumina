"""Delete python course and re-seed it."""
import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course

async def run():
    async with async_session_maker() as db:
        result = await db.execute(select(Course).where(Course.title == 'Python Fundamentals'))
        course = result.scalar_one_or_none()
        if course:
            await db.delete(course)
            await db.commit()
            print("Old Python course deleted. Re-run seed_data.py now.")

asyncio.run(run())
