"""Add more sections to existing JS/SQL courses to match Python's 52 steps."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXTRA_SECTIONS = {
    "JavaScript Fundamentals": [
        {"title":"Numbers & Math","order":3,"steps":[
            {"title":"Numbers & Math Object","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Numbers & Math\n\n```javascript\n// Number methods\nconsole.log(Number.parseInt('42'));     // 42\nconsole.log(Number.parseFloat('3.14')); // 3.14\nconsole.log((123.456).toFixed(2));      // '123.46'\nconsole.log((0.1 + 0.2).toPrecision(2)); // '0.30'\n\n// Math object\nconsole.log(Math.round(4.7));    // 5\nconsole.log(Math.floor(4.7));    // 4\nconsole.log(Math.ceil(4.3));     // 5\nconsole.log(Math.random());      // 0..1\nconsole.log(Math.max(1,5,3));    // 5\nconsole.log(Math.min(1,5,3));    // 1\n```"}},
            {"title":"Random Number Practice","step_type":StepType.CODE,"order":1,"xp_reward":30,"content_data":{"instruction":"Generate 10 random integers between 1 and 100, print each on a new line.","starter_code":"for (let i = 0; i < 10; i++) {\n    console.log(Math.floor(Math.random() * 100) + 1);\n}","solution":"for (let i = 0; i < 10; i++) {\n    console.log(Math.floor(Math.random() * 100) + 1);\n}","compare_mode":"contains","expected_output":"1","hints":["Math.random() returns 0..0.999", "Multiply by 100, floor, add 1"]}},
        ]},
        {"title":"Type Coercion","order":4,"steps":[
            {"title":"Type Coercion & Equality","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Type Coercion\n\nJavaScript automatically converts types:\n\n```javascript\n// String + Number = String\nconsole.log('5' + 3);    // '53'\n\n// String - Number = Number\nconsole.log('10' - 5);   // 5\n\n// Boolean to Number\nconsole.log(true + 1);   // 2\nconsole.log(false + 1);  // 1\n\n// == vs === (ALWAYS use ===)\nconsole.log(5 == '5');   // true  (coercion)\nconsole.log(5 === '5');  // false (no coercion)\nconsole.log(null == undefined);  // true\nconsole.log(null === undefined); // false\n```"}},
            {"title":"Coercion Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,"content_data":{"question":"What does `console.log('10' - 5)` print?","options":[{"id":"a","label":"'105'"},{"id":"b","label":"5"},{"id":"c","label":"'10-5'"},{"id":"d","label":"NaN"}],"correct_option":"b","hints":["Minus operator triggers numeric conversion","Plus (+) concatenates, minus (-) subtracts"],"explanation":"The - operator converts '10' to number 10, then subtracts 5 = 5."}},
        ]},
    ],
    "DOM & Events": [
        {"title":"Animations","order":3,"steps":[
            {"title":"CSS Animations with JS","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Animations\n\n## requestAnimationFrame\n```javascript\nfunction animate() {\n    element.style.transform = `translateX(${pos}px)`;\n    pos += 2;\n    if (pos < 500) {\n        requestAnimationFrame(animate);\n    }\n}\nrequestAnimationFrame(animate);\n```\n\n## CSS Transitions\n```javascript\nbox.style.transition = 'transform 0.5s ease';\nbox.style.transform = 'translateX(200px)';\n```\n\n## setInterval Animation\n```javascript\nlet opacity = 1;\nconst interval = setInterval(() => {\n    opacity -= 0.1;\n    element.style.opacity = opacity;\n    if (opacity <= 0) clearInterval(interval);\n}, 100);\n```"}},
        ]},
    ],
    "SQL Essentials": [
        {"title":"Sorting & Limiting","order":2,"steps":[
            {"title":"ORDER BY & LIMIT","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# ORDER BY & LIMIT\n\n```sql\n-- Ascending (default)\nSELECT name, price FROM products ORDER BY price;\n\n-- Descending\nSELECT name, price FROM products ORDER BY price DESC;\n\n-- Multiple columns\nSELECT name, price, stock\nFROM products\nORDER BY category_id, price DESC;\n\n-- Limit results\nSELECT * FROM products ORDER BY price DESC LIMIT 5;\n\n-- Offset (pagination)\nSELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;\n```"}},
            {"title":"ORDER BY Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,"content_data":{"question":"What does `ORDER BY price DESC, name ASC` do?","options":[{"id":"a","label":"price ascending, name descending"},{"id":"b","label":"price descending, name ascending"},{"id":"c","label":"only price descending"},{"id":"d","label":"only name ascending"}],"correct_option":"b","hints":["DESC = descending, ASC = ascending","First criterion is primary, second is tiebreaker"],"explanation":"Sorts by price descending first, then by name ascending for ties."}},
        ]},
    ],
    "JS Data Structures & Algorithms": [
        {"title":"Recursion","order":3,"steps":[
            {"title":"Recursion","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Recursion\n\nA function that calls itself.\n\n```javascript\n// Factorial with recursion\nfunction factorial(n) {\n    if (n <= 1) return 1;  // base case\n    return n * factorial(n - 1);  // recursive case\n}\n\nconsole.log(factorial(5));  // 120\n\n// Fibonacci\nfunction fib(n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}\n\nconsole.log(fib(6));  // 8\n```\n\n## Common Recursion Patterns\n- Tree traversal\n- Directory walking\n- Divide and conquer\n- Backtracking"}},
            {"title":"Recursion Practice","step_type":StepType.CODE,"order":1,"xp_reward":45,"content_data":{"instruction":"Write a recursive function `sumTo(n)` that returns the sum of numbers from 1 to n.\n\nExample: sumTo(5) = 1+2+3+4+5 = 15","starter_code":"function sumTo(n) {\n    if (n <= 1) return n;\n    return n + sumTo(n - 1);\n}\nconsole.log(sumTo(5)); // 15\nconsole.log(sumTo(10)); // 55","solution":"function sumTo(n) {\n    if (n <= 1) return n;\n    return n + sumTo(n - 1);\n}\nconsole.log(sumTo(5));\nconsole.log(sumTo(10));","compare_mode":"contains","expected_output":"15\n55","hints":["Base case: if n <= 1 return n", "Recursive: return n + sumTo(n-1)"]}},
        ]},
    ],
    "SQL Transactions & Functions": [
        {"title":"Triggers","order":3,"steps":[
            {"title":"Triggers","step_type":StepType.THEORY,"order":0,"xp_reward":10,"content_data":{"body_markdown":"# Triggers\n\nA trigger runs automatically before/after an event.\n\n```sql\nCREATE OR REPLACE FUNCTION update_updated_at()\nRETURNS TRIGGER AS $$\nBEGIN\n    NEW.updated_at = NOW();\n    RETURN NEW;\nEND;\n$$ LANGUAGE plpgsql;\n\nCREATE TRIGGER set_timestamp\nBEFORE UPDATE ON users\nFOR EACH ROW\nEXECUTE FUNCTION update_updated_at();\n```\n\n## Trigger Events\n- BEFORE/AFTER INSERT\n- BEFORE/AFTER UPDATE\n- BEFORE/AFTER DELETE\n- INSTEAD OF (for views)\n\n## Audit Log Trigger\n```sql\nCREATE TABLE audit_log (\n    id SERIAL PRIMARY KEY,\n    table_name TEXT,\n    action TEXT,\n    old_data JSONB,\n    new_data JSONB,\n    changed_at TIMESTAMP DEFAULT NOW()\n);\n```"}},
        ]},
    ],
}

async def add_extra():
    async with async_session_maker() as db:
        for course_title, sections in EXTRA_SECTIONS.items():
            course = (await db.execute(select(Course).where(Course.title == course_title))).scalar_one_or_none()
            if not course:
                logger.warning("  Course not found: %s", course_title)
                continue
            # Check max order
            existing = (await db.execute(select(Section).where(Section.course_id == course.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            next_order = (existing.order + 1) if existing else 0
            for sec_data in sections:
                sec = Section(course_id=course.id, title=sec_data["title"], order=next_order)
                db.add(sec); await db.flush(); await db.refresh(sec)
                st_count = 0
                for st in sec_data["steps"]:
                    db.add(Step(section_id=sec.id, title=st["title"], step_type=st["step_type"], order=st["order"], xp_reward=st["xp_reward"], content_data=st.get("content_data"))); st_count += 1
                next_order += 1
                logger.info("  %s + '%s' (%d steps)", course_title, sec_data["title"], st_count)
        await db.commit()
        logger.info("EXTRA SECTIONS ADDED")

if __name__ == "__main__":
    asyncio.run(add_extra())
