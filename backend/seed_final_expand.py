"""Final expansion: bring JS and SQL to ~50 steps each like Python."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def _seed(db, title, desc, lang, sections):
    if (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none():
        logger.info("  Exists: %s", title); return None
    c = Course(title=title, description=desc, language=lang)
    db.add(c); await db.flush(); await db.refresh(c)
    total = 0
    for sec in sections:
        s = Section(course_id=c.id, title=sec["title"], order=sec["order"])
        db.add(s); await db.flush(); await db.refresh(s)
        for st in sec["steps"]:
            db.add(Step(section_id=s.id, title=st["title"], step_type=st["step_type"], order=st["order"], xp_reward=st["xp_reward"], content_data=st.get("content_data")))
            total += 1
    await db.flush()
    logger.info("  Created: %s (%d steps)", title, total)
    return c

async def run():
    async with async_session_maker() as db:

        # ═══ JS EXTRA 1: Async JavaScript ═══════════════
        js_async = await _seed(db, "Async JavaScript & APIs",
            "Promises, async/await, fetch API, error handling, and building REST clients.",
            "JavaScript", [
                {"title":"Promises in Depth","order":0,"steps":[
                    {"title":"Promise Chaining","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Promise Chaining\n\n```javascript\nfetch('/api/user')\n    .then(res => res.json())\n    .then(user => fetch(`/api/orders/${user.id}`))\n    .then(res => res.json())\n    .then(orders => console.log(orders))\n    .catch(err => console.error('Failed:', err));\n\n// Promise.all - run in parallel\nconst [user, posts] = await Promise.all([\n    fetch('/api/user').then(r => r.json()),\n    fetch('/api/posts').then(r => r.json()),\n]);\n\n// Promise.race - first to resolve wins\nconst timeout = new Promise((_, reject) =>\n    setTimeout(() => reject(new Error('Timeout')), 5000)\n);\nconst data = await Promise.race([fetch(url), timeout]);\n```"}},
                    {"title":"Promise Methods Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"What does `Promise.race([p1, p2])` return?",
                     "options":[{"id":"a","label":"All promises' results"},{"id":"b","label":"The first settled promise"},{"id":"c","label":"The last settled promise"},{"id":"d","label":"Only rejected promises"}],
                     "correct_option":"b","hints":["Race = competition","The fastest 'runner' wins"],
                     "explanation":"Promise.race returns a promise that resolves/rejects as soon as the FIRST promise in the array settles."}},
                    {"title":"Fetch Users","step_type":StepType.CODE,"order":2,"xp_reward":40,
                     "content_data":{"instruction":"Write an async function `getUser(id)` that fetches user data from JSONPlaceholder API and returns the user name.\n\n```javascript\nasync function getUser(id) {\n    const res = await fetch(`https://jsonplaceholder.typicode.com/users/${id}`);\n    const user = await res.json();\n    return user.name;\n}\n```","starter_code":"async function getUser(id) {\n    const res = await fetch(`https://jsonplaceholder.typicode.com/users/${id}`);\n    const user = await res.json();\n    return user.name;\n}\n\ngetUser(1).then(console.log);","solution":"async function getUser(id) {\n    const res = await fetch(`https://jsonplaceholder.typicode.com/users/${id}`);\n    const user = await res.json();\n    return user.name;\n}\ngetUser(1).then(console.log);","compare_mode":"contains","expected_output":"Leanne Graham","hints":["Use `fetch(url)` then `res.json()`", "URL: `https://jsonplaceholder.typicode.com/users/${id}`"]}},
                ]},
                {"title":"Error Handling in Async","order":1,"steps":[
                    {"title":"Async Error Patterns","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Async Error Patterns\n\n## Try/Catch in Async\n```javascript\nasync function safeFetch(url) {\n    try {\n        const response = await fetch(url);\n        if (!response.ok) {\n            throw new Error(`HTTP ${response.status}: ${response.statusText}`);\n        }\n        return await response.json();\n    } catch (error) {\n        if (error instanceof TypeError) {\n            console.error('Network error:', error.message);\n        } else {\n            console.error('API error:', error.message);\n        }\n        return null;  // graceful fallback\n    }\n}\n```\n\n## Retry Pattern\n```javascript\nasync function fetchWithRetry(url, retries = 3) {\n    for (let i = 0; i < retries; i++) {\n        try {\n            const res = await fetch(url);\n            if (!res.ok) throw new Error(`HTTP ${res.status}`);\n            return await res.json();\n        } catch (err) {\n            if (i === retries - 1) throw err;\n            await new Promise(r => setTimeout(r, 1000 * (i + 1)));\n        }\n    }\n}\n```"}},
                    {"title":"Retry Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"After 3 retries all fail, what does fetchWithRetry do?",
                     "options":[{"id":"a","label":"Returns null"},{"id":"b","label":"Throws the last error"},{"id":"c","label":"Returns undefined"},{"id":"d","label":"Retries forever"}],
                     "correct_option":"b","hints":["On the last retry (i === retries-1), the error is thrown","Earlier retries catch and wait"],
                     "explanation":"On the final attempt, if it still fails, the error is re-thrown so the caller can handle it."}},
                ]},
                {"title":"Event Loop","order":2,"steps":[
                    {"title":"The Event Loop","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# The JavaScript Event Loop\n\nJavaScript is single-threaded but non-blocking thanks to the event loop.\n\n## Call Stack\nFunctions are added to the call stack and executed LIFO (Last In, First Out).\n\n## Task Queue (macrotasks)\n- setTimeout, setInterval\n- DOM events (click, load)\n- fetch (network)\n\n## Microtask Queue (higher priority)\n- Promise.then/catch/finally\n- queueMicrotask()\n- MutationObserver\n\n## Order of Execution\n```javascript\nconsole.log('1');  // sync\n\nsetTimeout(() => console.log('2'), 0);  // macrotask\n\nPromise.resolve().then(() => console.log('3'));  // microtask\n\nconsole.log('4');  // sync\n\n// Output: 1, 4, 3, 2\n// Why? Microtasks run BEFORE macrotasks\n```"}},
                    {"title":"Event Loop Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":25,
                     "content_data":{"question":"What is the output of:\n```javascript\nconsole.log('A');\nsetTimeout(() => console.log('B'), 0);\nPromise.resolve().then(() => console.log('C'));\nconsole.log('D');\n```",
                     "options":[{"id":"a","label":"A, B, C, D"},{"id":"b","label":"A, D, C, B"},{"id":"c","label":"A, D, B, C"},{"id":"d","label":"D, A, C, B"}],
                     "correct_option":"b","hints":["Sync code runs first (A, D)","Microtasks (Promise) run before macrotasks (setTimeout)"],
                     "explanation":"1. Sync: A, D. 2. Microtask: C. 3. Macrotask: B."}},
                ]},
        ])

        # ═══ JS EXTRA 2: Browser APIs ═══════════════════
        js_browser = await _seed(db, "Browser APIs & Storage",
            "LocalStorage, sessionStorage, cookies, geolocation, canvas, and web APIs.",
            "JavaScript", [
                {"title":"Web Storage","order":0,"steps":[
                    {"title":"LocalStorage & SessionStorage","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Web Storage\n\n## localStorage (persists until deleted)\n```javascript\n// Set\nlocalStorage.setItem('theme', 'dark');\nlocalStorage.setItem('user', JSON.stringify({name:'Alice', age:30}));\n\n// Get\nconst theme = localStorage.getItem('theme');\nconst user = JSON.parse(localStorage.getItem('user'));\n\n// Remove\nlocalStorage.removeItem('theme');\nlocalStorage.clear();\n```\n\n## sessionStorage (cleared when tab closes)\n```javascript\nsessionStorage.setItem('temp', 'value');\n```\n\n## Cookies\n```javascript\ndocument.cookie = 'sessionId=abc123; max-age=3600; path=/; secure';\ndocument.cookie = 'theme=dark';\n```\n\n## sessionStorage vs localStorage\n| Feature | localStorage | sessionStorage |\n|---------|-------------|----------------|\n| Lifetime | Until deleted | Until tab closes |\n| Scope | All tabs/windows | Same tab |\n| Capacity | ~5MB | ~5MB |"}},
                    {"title":"Storage Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"When does sessionStorage data get cleared?",
                     "options":[{"id":"a","label":"Never"},{"id":"b","label":"When the browser closes"},{"id":"c","label":"When the tab closes"},{"id":"d","label":"After 24 hours"}],
                     "correct_option":"c","hints":["Think about the word 'session'","Session = single browsing session"],
                     "explanation":"sessionStorage data is cleared when the browser tab (session) is closed."}},
                ]},
                {"title":"Geolocation & Canvas","order":1,"steps":[
                    {"title":"Browser APIs","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Browser APIs\n\n## Geolocation\n```javascript\nnavigator.geolocation.getCurrentPosition(\n    (position) => {\n        console.log('Lat:', position.coords.latitude);\n        console.log('Lng:', position.coords.longitude);\n    },\n    (error) => {\n        console.error('Geolocation error:', error.message);\n    },\n    { enableHighAccuracy: true }\n);\n\n// Watch position (updates as user moves)\nconst watchId = navigator.geolocation.watchPosition(handler);\nnavigator.geolocation.clearWatch(watchId);\n```\n\n## Canvas\n```javascript\nconst canvas = document.getElementById('myCanvas');\nconst ctx = canvas.getContext('2d');\n\n// Draw a rectangle\nctx.fillStyle = 'blue';\nctx.fillRect(10, 10, 100, 50);\n\n// Draw a circle\nctx.beginPath();\nctx.arc(200, 100, 50, 0, Math.PI * 2);\nctx.fillStyle = 'red';\nctx.fill();\n\n// Draw text\nctx.font = '20px Arial';\nctx.fillStyle = 'black';\nctx.fillText('Hello Canvas!', 50, 200);\n```"}},
                    {"title":"Canvas Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which method draws a filled rectangle on a canvas?",
                     "options":[{"id":"a","label":"ctx.drawRect()"},{"id":"b","label":"ctx.fillRect()"},{"id":"c","label":"ctx.rect()"},{"id":"d","label":"ctx.rectangle()"}],
                     "correct_option":"b","hints":["'fill' indicates a solid shape","'rect' is short for rectangle"],
                     "explanation":"fillRect(x, y, width, height) draws a filled rectangle. strokeRect() draws only the outline."}},
                ]},
        ])

        # ═══ SQL EXTRA 1: Data Types & Design ═══════════
        sql_types = await _seed(db, "SQL Data Types & Constraints",
            "Data types, constraints, CHECK, UNIQUE, DEFAULT, SERIAL, ENUM, and data integrity.",
            "SQL", [
                {"title":"Data Types","order":0,"steps":[
                    {"title":"PostgreSQL Data Types","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# PostgreSQL Data Types\n\n## Numeric\n```sql\nINTEGER      -- whole numbers (-2B to 2B)\nBIGINT       -- large whole numbers\nSMALLINT     -- small whole numbers\nDECIMAL(10,2)-- exact decimal (for money)\nREAL         -- floating point (~6 digits)\nDOUBLE PRECISION -- floating point (~15 digits)\n```\n\n## Character\n```sql\nCHAR(10)     -- fixed-length, padded with spaces\nVARCHAR(255) -- variable length with limit\nTEXT         -- unlimited length\n```\n\n## Date/Time\n```sql\nDATE         -- date only (no time)\nTIME         -- time only (no date)\nTIMESTAMP    -- date and time\nTIMESTAMPTZ  -- with timezone\nINTERVAL     -- time span\n```\n\n## Boolean\n```sql\nBOOLEAN      -- TRUE, FALSE, NULL\n```\n\n## JSON\n```sql\nJSON         -- stores exact copy of input text\nJSONB        -- stores decomposed binary (faster for queries)\n```\n\n## Arrays\n```sql\nINTEGER[]    -- array of integers\nVARCHAR(50)[] -- array of strings\n```\n\n## Network\n```sql\nINET         -- IPv4/IPv6 address\nCIDR         -- network range\nMACADDR      -- MAC address\n```"}},
                    {"title":"Data Type Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which data type should you use to store a product price?",
                     "options":[{"id":"a","label":"REAL"},{"id":"b","label":"DECIMAL(10,2)"},{"id":"c","label":"INTEGER"},{"id":"d","label":"VARCHAR"}],
                     "correct_option":"b","hints":["Money needs exact decimal precision","REAL can have rounding errors"],
                     "explanation":"DECIMAL(10,2) stores exact values with 2 decimal places, perfect for monetary values where precision matters."}},
                ]},
                {"title":"Constraints","order":1,"steps":[
                    {"title":"Constraints","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# SQL Constraints\n\n## NOT NULL\n```sql\nCREATE TABLE users (\n    id SERIAL PRIMARY KEY,\n    name VARCHAR(100) NOT NULL,\n    email VARCHAR(255) NOT NULL\n);\n```\n\n## UNIQUE\n```sql\nALTER TABLE users ADD CONSTRAINT uq_email UNIQUE (email);\nCREATE TABLE products (\n    sku VARCHAR(50) UNIQUE NOT NULL\n);\n```\n\n## CHECK\n```sql\nCREATE TABLE employees (\n    id SERIAL PRIMARY KEY,\n    name VARCHAR(100),\n    salary DECIMAL(10,2) CHECK (salary > 0),\n    age INTEGER CHECK (age >= 18 AND age <= 70)\n);\n```\n\n## DEFAULT\n```sql\nCREATE TABLE orders (\n    id SERIAL PRIMARY KEY,\n    status VARCHAR(20) DEFAULT 'pending',\n    created_at TIMESTAMP DEFAULT NOW()\n);\n```\n\n## SERIAL (auto-increment)\n```sql\nCREATE TABLE users (\n    id SERIAL PRIMARY KEY,  -- auto-generates 1, 2, 3...\n    name TEXT\n);\n```"}},
                    {"title":"Constraints Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"What does CHECK do in a CREATE TABLE statement?",
                     "options":[{"id":"a","label":"Verifies table exists"},{"id":"b","label":"Validates column values"},{"id":"c","label":"Creates an index"},{"id":"d","label":"Checks permissions"}],
                     "correct_option":"b","hints":["CHECK is a constraint","It ensures data quality"],
                     "explanation":"CHECK validates that column values meet a specified condition before allowing INSERT or UPDATE."}},
                ]},
                {"title":"Table Relationships","order":2,"steps":[
                    {"title":"Self-Join & Cross-Join","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Advanced JOINs\n\n## Self-Join (table joined to itself)\n```sql\n-- Find employees and their managers\nSELECT e.name as employee, m.name as manager\nFROM employees e\nLEFT JOIN employees m ON e.manager_id = m.id;\n```\n\n## Cross Join (Cartesian product)\n```sql\n-- All possible color-size combinations\nSELECT colors.name, sizes.name\nFROM colors\nCROSS JOIN sizes;\n```\n\n## Natural Join (auto-match by column name)\n```sql\nSELECT * FROM products NATURAL JOIN categories;\n-- Automatically joins on matching column names\n```\n\n## Lateral Join\n```sql\nSELECT p.name, recent_orders.total\nFROM products p,\nLATERAL (\n    SELECT total FROM orders\n    WHERE product_id = p.id\n    ORDER BY created_at DESC\n    LIMIT 1\n) recent_orders;\n```"}},
                ]},
        ])

        # ═══ SQL EXTRA 2: Backup & Security ═════════════
        sql_security = await _seed(db, "SQL Security & Administration",
            "User permissions, roles, backups, pg_dump, and database administration basics.",
            "SQL", [
                {"title":"User Management","order":0,"steps":[
                    {"title":"Users & Roles","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Users & Permissions\n\n## Creating Users\n```sql\nCREATE USER app_user WITH PASSWORD 'secure_pass';\nCREATE USER readonly WITH PASSWORD 'read_only';\n```\n\n## Granting Permissions\n```sql\n-- Database level\nGRANT CONNECT ON DATABASE mydb TO app_user;\n\n-- Schema level\nGRANT USAGE ON SCHEMA public TO app_user;\n\n-- Table level\nGRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;\nGRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;\n\n-- Future tables\nALTER DEFAULT PRIVILEGES IN SCHEMA public\nGRANT SELECT ON TABLES TO readonly;\n```\n\n## Revoking\n```sql\nREVOKE DELETE ON orders FROM app_user;\n```\n\n## Roles (groups)\n```sql\nCREATE ROLE developer;\nGRANT developer TO alice, bob;\nGRANT SELECT, INSERT ON ALL TABLES TO developer;\n```"}},
                    {"title":"Permissions Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which command gives a user access to a database?",
                     "options":[{"id":"a","label":"GIVE ACCESS"},{"id":"b","label":"GRANT CONNECT"},{"id":"c","label":"ALLOW DATABASE"},{"id":"d","label":"PERMIT LOGIN"}],
                     "correct_option":"b","hints":["Think about establishing a connection","The keyword is GRANT"],
                     "explanation":"GRANT CONNECT ON DATABASE db_name TO user_name gives the user permission to connect to the database."}},
                ]},
                {"title":"Backup & Restore","order":1,"steps":[
                    {"title":"pg_dump and pg_restore","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Backup & Restore\n\n## pg_dump (single database)\n```bash\n# Custom format (compressed, parallel restore)\npg_dump -Fc mydb > mydb.dump\n\n# Plain SQL\npg_dump mydb > mydb.sql\n\n# Specific table\npg_dump -t users mydb > users.sql\n\n# Exclude table\npg_dump -T logs mydb > mydb.sql\n```\n\n## pg_restore\n```bash\n# Restore custom format\npg_restore -d mydb mydb.dump\n\n# Parallel restore (4 jobs)\npg_restore -j 4 -d mydb mydb.dump\n```\n\n## pg_dumpall (all databases)\n```bash\npg_dumpall > all_databases.sql\n```\n\n## Continuous Archiving (WAL)\n```bash\n# archive_mode = on in postgresql.conf\narchive_command = 'cp %p /backups/%f'\n```\n\n## Point-in-Time Recovery\n```bash\n# Restore to specific time\npg_restore --target-time \"2024-01-15 10:30:00\" -d mydb mydb.dump\n```"}},
                    {"title":"Backup Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which pg_dump format allows parallel restore with multiple jobs?",
                     "options":[{"id":"a","label":"Plain SQL (-Fp)"},{"id":"b","label":"Custom (-Fc)"},{"id":"c","label":"Directory (-Fd)"},{"id":"d","label":"Tar (-Ft)"}],
                     "correct_option":"b","hints":["Parallel restore needs multiple files or custom format","Both -Fc and -Fd support parallel restore"],
                     "explanation":"Custom format (-Fc) and Directory format (-Fd) support parallel restore. Plain SQL (-Fp) does not."}},
                ]},
        ])

        # ═══ ADD TO PATHS ═══════════════════════════════
        js_path = (await db.execute(select(LearningPath).where(LearningPath.language == "JavaScript"))).scalar_one_or_none()
        sql_path = (await db.execute(select(LearningPath).where(LearningPath.language == "SQL"))).scalar_one_or_none()

        if js_path:
            for course, name, order in [
                (js_async, "Advanced 1: Async JavaScript & APIs", 6),
                (js_browser, "Advanced 2: Browser APIs & Storage", 7),
            ]:
                if course and not (await db.execute(
                    select(PathLevel).where(PathLevel.path_id == js_path.id, PathLevel.course_id == course.id)
                )).scalar_one_or_none():
                    db.add(PathLevel(path_id=js_path.id, course_id=course.id, level_name=name, order=order, required_progress_pct=75))
                    logger.info("  JS: added %s", name)

        if sql_path:
            for course, name, order in [
                (sql_types, "Advanced 1: Data Types & Constraints", 6),
                (sql_security, "Advanced 2: Security & Administration", 7),
            ]:
                if course and not (await db.execute(
                    select(PathLevel).where(PathLevel.path_id == sql_path.id, PathLevel.course_id == course.id)
                )).scalar_one_or_none():
                    db.add(PathLevel(path_id=sql_path.id, course_id=course.id, level_name=name, order=order, required_progress_pct=75))
                    logger.info("  SQL: added %s", name)

        await db.commit()
        logger.info("=" * 50)
        logger.info("FINAL EXPANSION COMPLETE!")
        logger.info("=" * 50)

if __name__ == "__main__":
    asyncio.run(run())
