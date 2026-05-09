"""Extra SQL sections to reach ~52 steps."""
import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

SQL_EXTRA = {
    "SQL Essentials": [
        {"title":"NULLs & COALESCE","order":3,"steps":[
            {"title":"Handling NULLs","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# NULL Handling\n\nNULL means unknown / missing value.\n\n```sql\n-- IS NULL / IS NOT NULL\nSELECT * FROM users WHERE email IS NULL;\nSELECT * FROM users WHERE email IS NOT NULL;\n\n-- COALESCE (first non-null value)\nSELECT name, COALESCE(phone, email, 'No contact') as contact\nFROM users;\n\n-- NULLIF (returns NULL if equal)\nSELECT NULLIF(a, b);  -- if a=b returns NULL, else returns a\n\n-- Default value\nSELECT COALESCE(discount, 0) FROM products;\n```"}},
            {"title":"NULL Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,"content_data":{"question":"What does COALESCE(NULL, 'hello', NULL) return?", "options":[{"id":"a","label":"NULL"},{"id":"b","label":"'hello'"},{"id":"c","label":"Error"},{"id":"d","label":"''"}],"correct_option":"b","hints":["COALESCE returns the first non-null value","'hello' is the first non-null argument"],"explanation":"COALESCE returns the first argument that is NOT NULL. NULL is skipped, 'hello' is returned."}},
        ]},
        {"title":"String Functions","order":4,"steps":[
            {"title":"SQL String Functions","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# SQL String Functions\n\n```sql\n-- Concatenation\nSELECT first_name || ' ' || last_name AS full_name FROM users;\n\n-- Upper/Lower\nSELECT UPPER(name), LOWER(email) FROM users;\n\n-- Length\nSELECT name, LENGTH(name) FROM products;\n\n-- Substring\nSELECT SUBSTRING(email FROM 1 FOR 5) FROM users;\n\n-- Replace\nSELECT REPLACE(description, 'old', 'new') FROM products;\n\n-- Trim\nSELECT TRIM('  hello  ');  -- 'hello'\n\n-- Position\nSELECT POSITION('@' IN email) FROM users;\n```"}},
        ]},
    ],
    "SQL Advanced": [
        {"title":"Set Operations","order":2,"steps":[
            {"title":"UNION, INTERSECT, EXCEPT","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Set Operations\n\n## UNION (combine results)\n```sql\nSELECT city FROM customers\nUNION\nSELECT city FROM suppliers\nORDER BY city;\n-- UNION removes duplicates, UNION ALL keeps them\n```\n\n## INTERSECT (common rows)\n```sql\nSELECT product_id FROM orders\nINTERSECT\nSELECT id FROM products WHERE stock > 0;\n```\n\n## EXCEPT (in first, not in second)\n```sql\nSELECT id FROM products\nEXCEPT\nSELECT product_id FROM orders;\n-- Products that have never been ordered\n```"}},
            {"title":"Set Ops Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,"content_data":{"question":"What's the difference between UNION and UNION ALL?", "options":[{"id":"a","label":"No difference"},{"id":"b","label":"UNION removes duplicates"},{"id":"c","label":"UNION ALL removes duplicates"},{"id":"d","label":"UNION is faster"}],"correct_option":"b","hints":["Duplicate elimination is expensive","Think 'ALL' keeps everything"],"explanation":"UNION removes duplicate rows; UNION ALL keeps all rows including duplicates and is faster."}},
        ]},
        {"title":"Date/Time Queries","order":3,"steps":[
            {"title":"Working with Dates","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Date/Time Queries\n\n```sql\n-- Current date/time\nSELECT NOW();\nSELECT CURRENT_DATE;\nSELECT CURRENT_TIME;\n\n-- Extract parts\nSELECT EXTRACT(YEAR FROM order_date) as year,\n       EXTRACT(MONTH FROM order_date) as month,\n       EXTRACT(DAY FROM order_date) as day\nFROM orders;\n\n-- Date arithmetic\nSELECT order_date + INTERVAL '7 days' as due_date\nFROM orders;\n\n-- Age calculation\nSELECT name, AGE(birth_date) as age FROM users;\n\n-- Date truncation\nSELECT DATE_TRUNC('month', order_date) as month,\n       SUM(total) as revenue\nFROM orders\nGROUP BY DATE_TRUNC('month', order_date);\n```"}},
        ]},
    ],
    "Advanced SQL Queries": [
        {"title":"JSON Queries","order":2,"steps":[
            {"title":"JSON in PostgreSQL","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# JSON Queries in PostgreSQL\n\n```sql\n-- Create table with JSONB\nCREATE TABLE events (\n    id SERIAL PRIMARY KEY,\n    data JSONB\n);\n\n-- Insert JSON data\nINSERT INTO events (data) VALUES\n('{\"user\": \"alice\", \"action\": \"login\", \"ip\": \"192.168.1.1\"}'),\n('{\"user\": \"bob\", \"action\": \"purchase\", \"amount\": 99.99}');\n\n-- Query JSON fields\nSELECT data->>'user' as username,\n       data->>'action' as action\nFROM events;\n\n-- JSON path queries\nSELECT * FROM events WHERE data @> '{\"action\": \"login\"}';\n\n-- Nested JSON\nSELECT data #>> '{user, name}' as name FROM events;\n```"}},
        ]},
    ],
}

async def add():
    async with async_session_maker() as db:
        for course_title, sections in SQL_EXTRA.items():
            course = (await db.execute(select(Course).where(Course.title == course_title))).scalar_one_or_none()
            if not course: continue
            existing = (await db.execute(select(Section).where(Section.course_id == course.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            next_order = (existing.order + 1) if existing else 0
            for sec in sections:
                s = Section(course_id=course.id, title=sec["title"], order=next_order)
                db.add(s); await db.flush(); await db.refresh(s)
                cnt = 0
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["step_type"], order=st["order"], xp_reward=st["xp_reward"], content_data=st.get("content_data"))); cnt += 1
                next_order += 1; logger.info("  %s + %s (%d)", course_title, sec["title"], cnt)
        await db.commit()

asyncio.run(add())
