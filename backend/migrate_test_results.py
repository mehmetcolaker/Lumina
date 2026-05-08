"""Add/alter test_results column to submissions table."""
import asyncio
from app.core.database import engine
from sqlalchemy import text


async def run():
    async with engine.begin() as conn:
        # Try to add as JSON (portable across PG/SQLite)
        json_type = "JSON"  
        # Check PostgreSQL then add
        await conn.execute(
            text(f"ALTER TABLE submissions ADD COLUMN IF NOT EXISTS test_results {json_type} DEFAULT NULL")
        )
        # If exists as JSONB, convert to JSON for test compat
        await conn.execute(
            text("ALTER TABLE submissions ALTER COLUMN test_results TYPE JSON USING test_results::text::json")
        )
        print("OK: test_results column added/updated")


asyncio.run(run())
