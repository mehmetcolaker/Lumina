"""Seed additional roadmaps for JavaScript and SQL.

Creates new courses and LearningPath objects for each supported language.
Run AFTER seed_data.py and seed_roadmap.py.
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session_maker
from app.modules.courses.models import (
    Course, LearningPath, PathLevel, Section, Step, StepType,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ── JAVASCRIPT ADVANCED ────────────────────────────────
JS_ADV_COURSE = {"title": "JavaScript Advanced", "description": "Advanced JavaScript: closures, promises, async/await, ES6+ features, and the event loop.", "language": "JavaScript"}
JS_ADV_SECTIONS = [
    {
        "title": "Functions & Scope",
        "order": 0,
        "steps": [
            {"title": "Closures and Scope", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Closures\n\nA **closure** is a function that remembers its outer variables even after the outer function has returned.\n\n```javascript\nfunction createCounter() {\n    let count = 0;\n    return function() {\n        count++;\n        return count;\n    };\n}\n\nconst counter = createCounter();\nconsole.log(counter()); // 1\nconsole.log(counter()); // 2\n```\n\n## Lexical Scope\nJavaScript uses **lexical scoping**: functions execute using the variable scope that was in effect when they were **defined**, not when they are **called**."}},
            {"title": "Closures Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "What will this code log?\n```javascript\nlet x = 10;\nfunction outer() {\n    let x = 20;\n    function inner() {\n        console.log(x);\n    }\n    return inner;\n}\nconst fn = outer();\nfn();\n```",
                 "options": [
                     {"id": "a", "label": "10"}, {"id": "b", "label": "20"},
                     {"id": "c", "label": "undefined"}, {"id": "d", "label": "ReferenceError"},
                 ], "correct_option": "b",
                 "hints": ["`inner()` remembers the `x` from `outer()`'s scope.", "The inner function was defined inside `outer()`, so it uses `outer()`'s `x=20`."],
                 "explanation": "Closures capture variables from the enclosing scope at definition time. `inner()` captures `x=20` from `outer()`.",
             }},
        ],
    },
    {
        "title": "Promises & Async",
        "order": 1,
        "steps": [
            {"title": "Promises and Async/Await", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Promises & Async/Await\n\n## Promises\n```javascript\nconst promise = new Promise((resolve, reject) => {\n    setTimeout(() => resolve(\"Done!\"), 1000);\n});\npromise.then(result => console.log(result));\n```\n\n## Async/Await (syntactic sugar)\n```javascript\nasync function fetchData() {\n    try {\n        const response = await fetch(\"https://api.example.com/data\");\n        const data = await response.json();\n        return data;\n    } catch (error) {\n        console.error(\"Failed:\", error);\n    }\n}\n```\n\n## Promise.all\n```javascript\nconst [users, posts] = await Promise.all([\n    fetch(\"/users\").then(r => r.json()),\n    fetch(\"/posts\").then(r => r.json()),\n]);\n```"}},
            {"title": "Async Practice", "step_type": StepType.CODE, "order": 1, "xp_reward": 40,
             "content_data": {
                 "instruction": "Write an async function `delayedHello(name)` that returns a Promise which resolves after 500ms with the string `\"Hello, NAME!\"`.",
                 "starter_code": "function delayedHello(name) {\n    return new Promise((resolve) => {\n        setTimeout(() => resolve(`Hello, ${name}!`), 500);\n    });\n}\n\ndelayedHello(\"World\").then(console.log);",
                 "solution": "function delayedHello(name) {\n    return new Promise((resolve) => {\n        setTimeout(() => resolve(`Hello, ${name}!`), 500);\n    });\n}\ndelayedHello(\"World\").then(console.log);",
                 "expected_output": "Hello, World!",
                 "compare_mode": "contains",
                 "hints": ["`new Promise((resolve) => { ... })`", "Use `setTimeout(() => resolve(value), 500)`"],
             }},
        ],
    },
]


# ── SQL ADVANCED ───────────────────────────────────────
SQL_ADV_COURSE = {"title": "SQL Advanced", "description": "Advanced SQL: JOINs, subqueries, aggregate functions, and database design.", "language": "SQL"}
SQL_ADV_SECTIONS = [
    {
        "title": "JOIN Operations",
        "order": 0,
        "steps": [
            {"title": "INNER JOIN, LEFT JOIN, RIGHT JOIN", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# JOIN Operations\n\n## INNER JOIN\nReturns only matching rows from both tables.\n```sql\nSELECT users.name, orders.total\nFROM users\nINNER JOIN orders ON users.id = orders.user_id;\n```\n\n## LEFT JOIN\nReturns all rows from the left table, matching rows from the right.\n```sql\nSELECT users.name, orders.total\nFROM users\nLEFT JOIN orders ON users.id = orders.user_id;\n-- Users with no orders will have NULL for total\n```\n\n## RIGHT JOIN\nReturns all rows from the right table.\n\n## FULL OUTER JOIN\nReturns all rows from both tables."}},
            {"title": "JOIN Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "Which JOIN returns ALL rows from the left table, even when there's no match in the right table?",
                 "options": [
                     {"id": "a", "label": "INNER JOIN"},
                     {"id": "b", "label": "LEFT JOIN"},
                     {"id": "c", "label": "RIGHT JOIN"},
                     {"id": "d", "label": "CROSS JOIN"},
                 ], "correct_option": "b",
                 "hints": ["LEFT JOIN keeps everything from the 'left' (first) table.", "INNER JOIN only keeps matches."],
                 "explanation": "LEFT JOIN returns ALL rows from the left table, with NULLs where there is no match in the right table.",
             }},
        ],
    },
    {
        "title": "Aggregates & Grouping",
        "order": 1,
        "steps": [
            {"title": "GROUP BY and HAVING", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# GROUP BY & HAVING\n\n## Aggregate Functions\n```sql\nSELECT COUNT(*), AVG(price), MAX(price), MIN(price), SUM(stock)\nFROM products;\n```\n\n## GROUP BY\n```sql\nSELECT category_id, COUNT(*) as product_count, AVG(price) as avg_price\nFROM products\nGROUP BY category_id;\n```\n\n## HAVING (WHERE for groups)\n```sql\nSELECT category_id, COUNT(*) as cnt\nFROM products\nGROUP BY category_id\nHAVING cnt > 2;\n```\n\n## Order of Execution\nFROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY -> LIMIT"}},
            {"title": "GROUP BY Practice", "step_type": StepType.CODE, "order": 1, "xp_reward": 35,
             "content_data": {
                 "instruction": "Write a SQL query that finds the total number of products in each category. Show the category_id and the count. Only include categories with at least 3 products.",
                 "starter_code": "SELECT category_id, COUNT(*) as product_count\nFROM products\nGROUP BY category_id\nHAVING product_count >= 3;",
                 "solution": "SELECT category_id, COUNT(*) as product_count\nFROM products\nGROUP BY category_id\nHAVING COUNT(*) >= 3;",
                 "expected_output": "category_id | product_count\n---\n1 | 4",
                 "compare_mode": "contains",
                 "hints": ["Use `GROUP BY category_id` to group products.", "Use `HAVING COUNT(*) >= 3` to filter groups."],
             }},
        ],
    },
]


async def _seed_course(db, title, description, language, sections_data):
    result = await db.execute(select(Course).where(Course.title == title))
    if result.scalar_one_or_none():
        logger.info("  Course exists, skipping: %s", title)
        return None

    course = Course(title=title, description=description, language=language)
    db.add(course)
    await db.flush()
    await db.refresh(course)

    total = 0
    for sec_data in sections_data:
        section = Section(course_id=course.id, title=sec_data["title"], order=sec_data["order"])
        db.add(section)
        await db.flush()
        await db.refresh(section)
        for step_data in sec_data["steps"]:
            db.add(Step(
                section_id=section.id, title=step_data["title"],
                step_type=step_data["step_type"], order=step_data["order"],
                xp_reward=step_data["xp_reward"], content_data=step_data.get("content_data"),
            ))
            total += 1
    await db.flush()
    logger.info("  Created: %s (%d sections, %d steps)", title, len(sections_data), total)
    return course


async def seed_roadmaps():
    async with async_session_maker() as db:
        # ── Create advanced courses ──
        js_adv = await _seed_course(db, JS_ADV_COURSE["title"], JS_ADV_COURSE["description"], JS_ADV_COURSE["language"], JS_ADV_SECTIONS)
        sql_adv = await _seed_course(db, SQL_ADV_COURSE["title"], SQL_ADV_COURSE["description"], SQL_ADV_COURSE["language"], SQL_ADV_SECTIONS)

        # ── Find existing courses for JavaScript ──
        js_fund = (await db.execute(select(Course).where(Course.title == "JavaScript Fundamentals"))).scalar_one_or_none()
        sql_ess = (await db.execute(select(Course).where(Course.title == "SQL Essentials"))).scalar_one_or_none()

        # ── Create JavaScript Roadmap ──
        existing_js_path = await db.execute(select(LearningPath).where(LearningPath.title == "JavaScript Developer Roadmap"))
        if not existing_js_path.scalar_one_or_none() and js_fund:
            path = LearningPath(title="JavaScript Developer Roadmap",
                                description="Master JavaScript from basics to advanced. Covers ES6+, closures, promises, async/await.",
                                language="JavaScript", icon="JS", order=1)
            db.add(path)
            await db.flush()
            levels_js = [
                (js_fund, "Beginner: JavaScript Fundamentals", 0, 0),
            ]
            if js_adv:
                levels_js.append((js_adv, "Advanced: Closures & Async", 1, 75))
            for course, level_name, order, req in levels_js:
                db.add(PathLevel(path_id=path.id, course_id=course.id, level_name=level_name, order=order, required_progress_pct=req))
            logger.info("JavaScript Developer Roadmap created (%d levels)", len(levels_js))

        # ── Create SQL Roadmap ──
        existing_sql_path = await db.execute(select(LearningPath).where(LearningPath.title == "SQL Developer Roadmap"))
        if not existing_sql_path.scalar_one_or_none() and sql_ess:
            path = LearningPath(title="SQL Developer Roadmap",
                                description="Learn SQL from zero to hero. SELECT queries, JOINs, aggregations, and database design.",
                                language="SQL", icon="SQL", order=2)
            db.add(path)
            await db.flush()
            levels_sql = [
                (sql_ess, "Beginner: SQL Essentials", 0, 0),
            ]
            if sql_adv:
                levels_sql.append((sql_adv, "Advanced: JOINs & Aggregates", 1, 75))
            for course, level_name, order, req in levels_sql:
                db.add(PathLevel(path_id=path.id, course_id=course.id, level_name=level_name, order=order, required_progress_pct=req))
            logger.info("SQL Developer Roadmap created (%d levels)", len(levels_sql))

        await db.commit()
        logger.info("=" * 50)
        logger.info("ALL ROADMAPS SEED COMPLETE!")
        logger.info("  3 languages, 2 new courses, 3 Learning Paths")
        logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_roadmaps())
