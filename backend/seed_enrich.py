"""Add more sections and steps to all courses."""
import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def add():
    async with async_session_maker() as db:
        total = 0

        def make_step(title, st, order, xp, cd):
            return Step(section_id=sec_id, title=title, step_type=st, order=order, xp_reward=xp, content_data=cd)

        # Python Fundamentals
        c = (await db.execute(select(Course).where(Course.title == "Python Fundamentals"))).scalar_one_or_none()
        if c:
            last = (await db.execute(select(Section).where(Section.course_id == c.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 0
            s = Section(course_id=c.id, title="Clean Code & Style", order=o)
            db.add(s); await db.flush(); await db.refresh(s); sec_id = s.id
            for step in [
                ("Comments & Docstrings", StepType.THEORY, 0, 10, {"body_markdown": "# Clean Code\n\n```python\n# Single line\n'''Docstring'''\ndef f(x):\n    '''Return x*2'''\n    return x*2\n\n# snake_case for vars\n# PascalCase for classes\n# UPPER_CASE for constants\n```"}),
                ("Write a Greeting Function", StepType.CODE, 1, 30, {"instruction":"Write a function greet(name) that returns 'Hello, name!'", "starter_code":"def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))\nprint(greet('Bob'))","solution":"def greet(name):\n    return f'Hello, {name}!'\nprint(greet('Alice'))\nprint(greet('Bob'))","compare_mode":"contains","expected_output":"Hello"}),
            ]: db.add(make_step(*step)); total += 1

        # JavaScript Fundamentals
        c = (await db.execute(select(Course).where(Course.title == "JavaScript Fundamentals"))).scalar_one_or_none()
        if c:
            last = (await db.execute(select(Section).where(Section.course_id == c.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 0
            s = Section(course_id=c.id, title="Objects & JSON", order=o)
            db.add(s); await db.flush(); await db.refresh(s); sec_id = s.id
            for step in [
                ("Object Basics", StepType.THEORY, 0, 10, {"body_markdown":"# Objects\n\n```javascript\nconst user = { name:'Alice', age:30 };\nuser.city = 'NYC';\nconsole.log(user.name);\n'name' in user;  // true\ndelete user.age;\n\nconst calc = {\n    add(a,b) { return a+b; }\n};\n```"}),
                ("Object Quiz", StepType.QUIZ, 1, 20, {"question":"How to check if property 'email' exists in object?","options":[{"id":"a","label":"'email' in obj"},{"id":"b","label":"obj.exists('email')"},{"id":"c","label":"obj.has('email')"},{"id":"d","label":"obj.contains('email')"}],"correct_option":"a","hints":["Use the in operator"],"explanation":"'email' in obj returns true if property exists."}),
                ("Build Car Object", StepType.CODE, 2, 35, {"instruction":"Create a car object with brand, model, year and method getInfo().","starter_code":"const car = {\n    brand: 'Toyota', model: 'Corolla', year: 2022,\n    getInfo() { return `${this.brand} ${this.model} (${this.year})`; }\n};\nconsole.log(car.getInfo());","solution":"const car = {\n    brand: 'Toyota', model: 'Corolla', year: 2022,\n    getInfo() { return `${this.brand} ${this.model} (${this.year})`; }\n};\nconsole.log(car.getInfo());","compare_mode":"contains","expected_output":"Toyota","hints":["Use this.property inside methods"]}),
            ]: db.add(make_step(*step)); total += 1

        # SQL Essentials
        c = (await db.execute(select(Course).where(Course.title == "SQL Essentials"))).scalar_one_or_none()
        if c:
            last = (await db.execute(select(Section).where(Section.course_id == c.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 0
            s = Section(course_id=c.id, title="DISTINCT & LIMIT", order=o)
            db.add(s); await db.flush(); await db.refresh(s); sec_id = s.id
            for step in [
                ("DISTINCT & LIMIT", StepType.THEORY, 0, 10, {"body_markdown":"# DISTINCT & LIMIT\n\n```sql\nSELECT DISTINCT city FROM users;\nSELECT * FROM products ORDER BY price DESC LIMIT 5;\nSELECT * FROM products LIMIT 10 OFFSET 20;\n```"}),
                ("DISTINCT Quiz", StepType.QUIZ, 1, 20, {"question":"What does DISTINCT do?","options":[{"id":"a","label":"Removes duplicates"},{"id":"b","label":"Sorts data"},{"id":"c","label":"Limits rows"},{"id":"d","label":"Groups rows"}],"correct_option":"a","hints":["Returns unique values"],"explanation":"DISTINCT removes duplicate rows."}),
                ("Top 3 Products", StepType.CODE, 2, 35, {"instruction":"Return the 3 most expensive products.","starter_code":"SELECT name, price FROM products ORDER BY price DESC LIMIT 3;","solution":"SELECT name, price FROM products ORDER BY price DESC LIMIT 3;","compare_mode":"contains","expected_output":"price","hints":["ORDER BY price DESC", "LIMIT 3"]}),
            ]: db.add(make_step(*step)); total += 1

        await db.commit()
        logger.info("Added %d extra steps!", total)

asyncio.run(add())
