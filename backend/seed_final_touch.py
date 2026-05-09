"""Final touch: add a few more steps to JS and SQL to match Python."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FINAL = {
    "JavaScript Fundamentals": [
        {"title":"Template Literals & Strings","order":5,"steps":[
            {"title":"Template Literals","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Template Literals\n\n```javascript\nconst name = 'Alice';\nconst age = 30;\n\n// Old way\nconsole.log('Hello, ' + name + '! You are ' + age + '.');\n\n// Template literal (modern)\nconsole.log(`Hello, ${name}! You are ${age}.`);\n\n// Multi-line strings\nconst html = `\n<div>\n  <h1>${name}</h1>\n  <p>Age: ${age}</p>\n</div>\n`;\n```"}},
            {"title":"Template Literals Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,"content_data":{"question":"Which character(s) denote a template literal?", "options":[{"id":"a","label":"Single quotes ''"},{"id":"b","label":"Double quotes \"\""},{"id":"c","label":"Backticks ``"},{"id":"d","label":"Parentheses ()"}],"correct_option":"c","hints":["Template literals use a special quote character","Found on the key above Tab"],"explanation":"Template literals use backticks (`) instead of quotes."}},
            {"title":"String Practice","step_type":StepType.CODE,"order":2,"xp_reward":30,"content_data":{"instruction":"Use template literals to create a greeting message. Create variables `firstName` and `lastName`, then print: 'Hello, firstName lastName! Welcome to JavaScript.'","starter_code":"const firstName = 'Ada';\nconst lastName = 'Lovelace';\nconst message = `Hello, ${firstName} ${lastName}! Welcome to JavaScript.`;\nconsole.log(message);","solution":"const firstName = 'Ada';\nconst lastName = 'Lovelace';\nconst message = `Hello, ${firstName} ${lastName}! Welcome to JavaScript.`;\nconsole.log(message);","compare_mode":"contains","expected_output":"Hello, Ada Lovelace! Welcome to JavaScript."}},
        ]},
    ],
    "SQL Essentials": [
        {"title":"Subqueries","order":5,"steps":[
            {"title":"Subqueries","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Subqueries\n\nA subquery is a query inside another query.\n\n```sql\n-- In WHERE clause\nSELECT name, price\nFROM products\nWHERE price > (SELECT AVG(price) FROM products);\n\n-- In SELECT clause\nSELECT name,\n    (SELECT COUNT(*) FROM orders WHERE product_id = p.id) as times_ordered\nFROM products p;\n\n-- In FROM clause\nSELECT category, AVG(price) as avg_price\nFROM (\n    SELECT p.*, c.name as category\n    FROM products p\n    JOIN categories c ON c.id = p.category_id\n) sub\nGROUP BY category;\n```"}},
            {"title":"Subquery Practice","step_type":StepType.CODE,"order":1,"xp_reward":35,"content_data":{"instruction":"Write a query that finds all products whose price is above the average price. Show name and price.","starter_code":"SELECT name, price\nFROM products\nWHERE price > (SELECT AVG(price) FROM products);","solution":"SELECT name, price\nFROM products\nWHERE price > (SELECT AVG(price) FROM products);","compare_mode":"contains","expected_output":"price","hints":["AVG(price) calculates the average","Subquery in WHERE with > comparison"]}},
        ]},
        {"title":"CASE Statements","order":6,"steps":[
            {"title":"CASE WHEN","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# CASE Statements\n\nLike IF/ELSE in SQL.\n\n```sql\nSELECT name, price,\n    CASE\n        WHEN price > 1000 THEN 'Expensive'\n        WHEN price > 100 THEN 'Moderate'\n        ELSE 'Cheap'\n    END as price_category\nFROM products;\n\n-- Simple CASE (exact match)\nSELECT name,\n    CASE category_id\n        WHEN 1 THEN 'Electronics'\n        WHEN 2 THEN 'Clothing'\n        ELSE 'Other'\n    END as category_name\nFROM products;\n\n-- CASE in GROUP BY\nSELECT\n    CASE\n        WHEN price > 500 THEN 'Premium'\n        ELSE 'Standard'\n    END as tier,\n    COUNT(*) as count\nFROM products\nGROUP BY tier;\n```"}},
        ]},
    ],
}

async def add():
    async with async_session_maker() as db:
        for title, sections in FINAL.items():
            c = (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none()
            if not c: continue
            last = (await db.execute(select(Section).where(Section.course_id == c.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            order = (last.order + 1) if last else 0
            for sec in sections:
                s = Section(course_id=c.id, title=sec["title"], order=order); db.add(s); await db.flush(); await db.refresh(s); order += 1
                cnt = 0
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["step_type"], order=st["order"], xp_reward=st["xp_reward"], content_data=st.get("content_data"))); cnt += 1
                logger.info("  %s: %s (%d)", title, sec["title"], cnt)
        await db.commit()
        logger.info("DONE")

asyncio.run(add())
