"""Expand JavaScript and SQL to match Python's depth (~50+ steps each)."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


async def _seed_course(db, title, description, language, sections_data):
    if (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none():
        logger.info("  Skipping (exists): %s", title)
        return None
    course = Course(title=title, description=description, language=language)
    db.add(course); await db.flush(); await db.refresh(course)
    total = 0
    for sec in sections_data:
        s = Section(course_id=course.id, title=sec["title"], order=sec["order"])
        db.add(s); await db.flush(); await db.refresh(s)
        for st in sec["steps"]:
            db.add(Step(section_id=s.id, title=st["title"], step_type=st["step_type"], order=st["order"], xp_reward=st["xp_reward"], content_data=st.get("content_data"))); total += 1
    await db.flush()
    logger.info("  Created: %s (%d sections, %d steps)", title, len(sections_data), total)
    return course


async def expand():
    async with async_session_maker() as db:

        # ═══ JAVASCRIPT EXTRA COURSES ═══════════════════

        js_ds = await _seed_course(db, "JS Data Structures & Algorithms",
            "Arrays, objects, maps, sets, sorting, searching, recursion, and common algorithms in JavaScript.",
            "JavaScript", [
                {"title":"Arrays & Objects","order":0,"steps":[
                    {"title":"Array Methods Deep Dive","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# JavaScript Array Methods\n\n## Mutating Methods\n```javascript\nconst arr = [1, 2, 3];\narr.push(4);        // [1,2,3,4]\narr.pop();          // removes last\narr.shift();        // removes first\narr.unshift(0);     // adds to start\narr.splice(1, 1);   // remove at index\n```\n\n## Non-Mutating Methods\n```javascript\nconst arr = [3, 1, 4, 1, 5];\narr.slice(1, 3);    // [1, 4]\narr.concat([6, 7]); // [3,1,4,1,5,6,7]\narr.indexOf(4);     // 2\narr.includes(1);    // true\n\n// Callback-based\narr.forEach(x => console.log(x));\nconst doubled = arr.map(x => x * 2);\nconst evens = arr.filter(x => x % 2 === 0);\nconst sum = arr.reduce((a, b) => a + b, 0);\n```"}},
                    {"title":"Array Reduce Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"What does `[1, 2, 3, 4].reduce((a, b) => a + b, 0)` return?",
                     "options":[{"id":"a","label":"10"},{"id":"b","label":"1234"},{"id":"c","label":"[1,2,3,4]"},{"id":"d","label":"24"}],
                     "correct_option":"a","hints":["reduce() accumulates values","Start with 0, add each element"],
                     "explanation":"1+2+3+4 = 10. The initial value 0 is the starting accumulator."}},
                    {"title":"Array Practice","step_type":StepType.CODE,"order":2,"xp_reward":35,
                     "content_data":{"instruction":"Use `map()` and `filter()` on the array `[5, 10, 15, 20, 25]` to get numbers greater than 12, then double them. Print the result.","starter_code":"const nums = [5, 10, 15, 20, 25];\nconst result = nums.filter(x => x > 12).map(x => x * 2);\nconsole.log(result);","solution":"const nums = [5, 10, 15, 20, 25];\nconst result = nums.filter(x => x > 12).map(x => x * 2);\nconsole.log(result);",
                     "compare_mode":"contains","expected_output":"[30, 40, 50]","hints":["Chain filter() then map()","filter keeps items where condition is true"]}},
                ]},
                {"title":"Maps, Sets & Objects","order":1,"steps":[
                    {"title":"Maps and Sets","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Maps & Sets\n\n## Map (key-value with any key type)\n```javascript\nconst userMap = new Map();\nuserMap.set(\"alice\", { age: 30 });\nuserMap.set(42, \"answer\");\nconsole.log(userMap.get(\"alice\"));  // {age: 30}\nconsole.log(userMap.has(42));       // true\nconsole.log(userMap.size);          // 2\n\nfor (const [key, value] of userMap) {\n    console.log(key, value);\n}\n```\n\n## Set (unique values)\n```javascript\nconst numbers = new Set([1, 2, 2, 3, 3, 3]);\nconsole.log(numbers);  // Set {1, 2, 3}\nnumbers.add(4);\nnumbers.has(2);        // true\nnumbers.delete(1);\n```\n\n## Object methods\n```javascript\nconst obj = { a: 1, b: 2, c: 3 };\nObject.keys(obj);     // ['a','b','c']\nObject.values(obj);   // [1,2,3]\nObject.entries(obj);  // [['a',1],['b',2],['c',3]]\n```"}},
                    {"title":"Maps Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"What is the key difference between a Map and a plain Object?",
                     "options":[{"id":"a","label":"Maps are slower"},{"id":"b","label":"Maps allow any type as key"},{"id":"c","label":"Objects cannot have string keys"},{"id":"d","label":"No difference"}],
                     "correct_option":"b","hints":["Objects only accept strings/symbols as keys","Maps accept any type (objects, numbers, etc)"],
                     "explanation":"Map allows ANY value type as a key (objects, functions, numbers), while Object only accepts strings and symbols."}},
                    {"title":"Word Frequency","step_type":StepType.CODE,"order":2,"xp_reward":40,
                     "content_data":{"instruction":"Use a Map to count word frequencies in the sentence: 'the quick brown fox jumps over the lazy dog the fox'\n\nPrint the map entries sorted by frequency.","starter_code":"const sentence = 'the quick brown fox jumps over the lazy dog the fox';\nconst words = sentence.split(' ');\nconst freq = new Map();\nfor (const word of words) {\n    freq.set(word, (freq.get(word) || 0) + 1);\n}\nfor (const [word, count] of [...freq.entries()].sort((a,b) => b[1] - a[1])) {\n    console.log(`${word}: ${count}`);\n}","solution":"const sentence = 'the quick brown fox jumps over the lazy dog the fox';\nconst words = sentence.split(' ');\nconst freq = new Map();\nfor (const word of words) {\n    freq.set(word, (freq.get(word) || 0) + 1);\n}\nfor (const [word, count] of [...freq.entries()].sort((a,b) => b[1] - a[1])) {\n    console.log(`${word}: ${count}`);\n}",
                     "compare_mode":"contains","expected_output":"the: 3","hints":["Map.get() returns undefined for missing keys, use || 0","Spread `...freq.entries()` to sort"]}},
                ]},
                {"title":"Sorting & Searching","order":2,"steps":[
                    {"title":"Sorting Algorithms","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Sorting & Searching\n\n## Built-in sort\n```javascript\nconst nums = [3, 1, 4, 1, 5, 9, 2, 6];\n\n// Ascending\nnums.sort((a, b) => a - b);\n\n// Descending\nnums.sort((a, b) => b - a);\n\n// Sorting objects\nconst users = [{name:'Bob',age:30},{name:'Alice',age:25}];\nusers.sort((a, b) => a.name.localeCompare(b.name));\n```\n\n## Binary Search\n```javascript\nfunction binarySearch(arr, target) {\n    let left = 0, right = arr.length - 1;\n    while (left <= right) {\n        const mid = Math.floor((left + right) / 2);\n        if (arr[mid] === target) return mid;\n        if (arr[mid] < target) left = mid + 1;\n        else right = mid - 1;\n    }\n    return -1;\n}\n```"}},
                    {"title":"Binary Search","step_type":StepType.CODE,"order":1,"xp_reward":45,
                     "content_data":{"instruction":"Implement a binary search function that finds a target number in a sorted array. Return the index, or -1 if not found.","starter_code":"function binarySearch(arr, target) {\n    let left = 0;\n    let right = arr.length - 1;\n    while (left <= right) {\n        const mid = Math.floor((left + right) / 2);\n        if (arr[mid] === target) return mid;\n        if (arr[mid] < target) left = mid + 1;\n        else right = mid - 1;\n    }\n    return -1;\n}\n\nconsole.log(binarySearch([1, 3, 5, 7, 9], 5));\nconsole.log(binarySearch([1, 3, 5, 7, 9], 2));","solution":"function binarySearch(arr, target) {\n    let left = 0, right = arr.length - 1;\n    while (left <= right) {\n        const mid = Math.floor((left + right) / 2);\n        if (arr[mid] === target) return mid;\n        if (arr[mid] < target) left = mid + 1;\n        else right = mid - 1;\n    }\n    return -1;\n}\nconsole.log(binarySearch([1, 3, 5, 7, 9], 5));\nconsole.log(binarySearch([1, 3, 5, 7, 9], 2));",
                     "compare_mode":"contains","expected_output":"2\n-1","hints":["Calculate mid with Math.floor((left+right)/2)","If arr[mid] < target, search right half"]}},
                ]},
        ])

        js_testing = await _seed_course(db, "JS Testing & Debugging",
            "Debugging techniques, testing with Jest, error handling, and code quality tools.",
            "JavaScript", [
                {"title":"Debugging","order":0,"steps":[
                    {"title":"Debugging Tools","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Debugging\n\n## Console Methods\n```javascript\nconsole.log(\"simple log\");\nconsole.error(\"error\");\nconsole.warn(\"warning\");\nconsole.table([{name:\"Alice\",age:30},{name:\"Bob\",age:25}]);\nconsole.time(\"timer\");\n// ... code ...\nconsole.timeEnd(\"timer\");  // prints elapsed time\n```\n\n## Debugger Statement\n```javascript\nfunction complexFn(x) {\n    debugger;  // execution pauses here in DevTools\n    return x * 2;\n}\n```\n\n## Try/Catch\n```javascript\ntry {\n    const data = JSON.parse(malformedJson);\n} catch (error) {\n    console.error(\"Parse failed:\", error.message);\n} finally {\n    console.log(\"Always runs\");\n}\n```\n\n## Stack Trace\nWhen an error occurs, use `error.stack` to see the call chain."}},
                    {"title":"Debug Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which statement pauses execution in the browser's DevTools?",
                     "options":[{"id":"a","label":"pause()"},{"id":"b","label":"debugger"},{"id":"c","label":"stop()"},{"id":"d","label":"break()"}],
                     "correct_option":"b","hints":["It's a keyword, not a function","It only works when DevTools is open"],
                     "explanation":"The `debugger` statement pauses execution and opens the debugger panel."}},
                ]},
                {"title":"Testing with Jest","order":1,"steps":[
                    {"title":"Unit Testing","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Testing with Jest\n\n## Basic Test\n```javascript\n// math.js\nfunction add(a, b) { return a + b; }\nmodule.exports = { add };\n\n// math.test.js\nconst { add } = require('./math');\n\ntest('adds 1 + 2 to equal 3', () => {\n    expect(add(1, 2)).toBe(3);\n});\n```\n\n## Matchers\n```javascript\nexpect(value).toBe(5);            // ===\nexpect(value).toEqual({a: 1});    // deep equality\nexpect(value).toBeNull();\nexpect(value).toBeTruthy();\nexpect(value).toBeDefined();\nexpect(array).toContain(3);\nexpect(string).toMatch(/pattern/);\n```\n\n## Async Testing\n```javascript\ntest('async test', async () => {\n    const data = await fetchData();\n    expect(data).toBeDefined();\n});\n```"}},
                ]},
                {"title":"Error Handling Patterns","order":2,"steps":[
                    {"title":"Error Handling","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Error Handling Patterns\n\n## Custom Errors\n```javascript\nclass ValidationError extends Error {\n    constructor(message) {\n        super(message);\n        this.name = 'ValidationError';\n    }\n}\n\nfunction validateAge(age) {\n    if (age < 0) throw new ValidationError('Age cannot be negative');\n    if (age > 150) throw new ValidationError('Invalid age');\n    return true;\n}\n\ntry {\n    validateAge(-5);\n} catch (error) {\n    if (error instanceof ValidationError) {\n        console.log('Validation:', error.message);\n    } else {\n        throw error;  // re-throw unexpected errors\n    }\n}\n```\n\n## Error Handling in Async\n```javascript\nasync function safeFetch(url) {\n    try {\n        const response = await fetch(url);\n        if (!response.ok) throw new Error(`HTTP ${response.status}`);\n        return await response.json();\n    } catch (error) {\n        console.error('Fetch failed:', error);\n        return null;  // graceful fallback\n    }\n}\n```"}},
                ]},
        ])

        # Clean old advanced/extra JS courses that might have been renamed
        for old_title in ['JavaScript Advanced', 'Modern JavaScript & Tools', 'DOM & Events']:
            old = await db.execute(select(Course).where(Course.title == old_title))
            if old.scalar_one_or_none():
                logger.info("  Keeping existing: %s", old_title)

        # ═══ SQL EXTRA COURSES ═════════════════════════

        sql_trans = await _seed_course(db, "SQL Transactions & Functions",
            "ACID transactions, stored procedures, functions, triggers, and views.",
            "SQL", [
                {"title":"Transactions (ACID)","order":0,"steps":[
                    {"title":"ACID Properties","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# ACID Transactions\n\nA transaction groups multiple operations into a single unit.\n\n## ACID Properties\n- **A**tomicity - all or nothing\n- **C**onsistency - data remains valid\n- **I**solation - transactions don't interfere\n- **D**urability - committed changes persist\n\n## BEGIN / COMMIT / ROLLBACK\n```sql\nBEGIN TRANSACTION;\n\nUPDATE accounts SET balance = balance - 100 WHERE id = 1;\nUPDATE accounts SET balance = balance + 100 WHERE id = 2;\n\n-- If both succeed:\nCOMMIT;\n\n-- If something fails:\nROLLBACK;\n```\n\n## SAVEPOINT\n```sql\nSAVEPOINT sp1;\nUPDATE products SET stock = stock - 1 WHERE id = 10;\n-- If problem:\nROLLBACK TO sp1;\n```"}},
                    {"title":"Transaction Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"What happens to changes made inside a transaction if ROLLBACK is executed?",
                     "options":[{"id":"a","label":"Changes are saved"},{"id":"b","label":"Changes are undone"},{"id":"c","label":"Only some changes are kept"},{"id":"d","label":"The database crashes"}],
                     "correct_option":"b","hints":["ROLLBACK reverts everything in the transaction","COMMIT is needed to save changes"],
                     "explanation":"ROLLBACK undoes ALL changes made since the transaction began (or since the last SAVEPOINT)."}},
                ]},
                {"title":"Views & Indexes","order":1,"steps":[
                    {"title":"Views","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Views\n\nA view is a saved query that acts like a virtual table.\n\n```sql\nCREATE VIEW expensive_products AS\nSELECT id, name, price, category_id\nFROM products\nWHERE price > 1000;\n\n-- Use it like a table\nSELECT * FROM expensive_products\nWHERE category_id = 1;\n```\n\n# Indexes\nAn index speeds up data retrieval at the cost of slower writes.\n\n```sql\n-- Single column index\nCREATE INDEX idx_products_price ON products(price);\n\n-- Composite index\nCREATE INDEX idx_orders_user_date ON orders(user_id, order_date);\n\n-- Unique index\nCREATE UNIQUE INDEX idx_users_email ON users(email);\n\n-- Check query plan\nEXPLAIN SELECT * FROM products WHERE price > 100;\n```\n\nIndexes are most useful for:\n- Columns used in WHERE clauses\n- Columns used in JOIN conditions\n- Columns used in ORDER BY\n- Large tables (>1000 rows)"}},
                    {"title":"Index Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which operation benefits MOST from an index?",
                     "options":[{"id":"a","label":"INSERT"},{"id":"b","label":"SELECT with WHERE"},{"id":"c","label":"DELETE all rows"},{"id":"d","label":"UPDATE without WHERE"}],
                     "correct_option":"b","hints":["Indexes are like a book's table of contents","They help find specific rows quickly"],
                     "explanation":"Indexes dramatically speed up SELECT queries with WHERE clauses by reducing the search space."}},
                ]},
                {"title":"Stored Functions","order":2,"steps":[
                    {"title":"SQL Functions","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# SQL Functions\n\n## Scalar Functions (return one value)\n```sql\n-- PostgreSQL function\nCREATE FUNCTION get_discount(price REAL)\nRETURNS REAL AS $$\nBEGIN\n    IF price > 1000 THEN\n        RETURN price * 0.1;\n    ELSE\n        RETURN 0;\n    END IF;\nEND;\n$$ LANGUAGE plpgsql;\n\n-- Use it\nSELECT name, price, get_discount(price) as discount\nFROM products;\n```\n\n## String Functions\n```sql\nSELECT\n    UPPER(name),\n    LOWER(email),\n    LENGTH(description),\n    SUBSTRING(name FROM 1 FOR 3),\n    TRIM('  hello  '),\n    REPLACE(name, 'old', 'new')\nFROM users;\n```\n\n## Date Functions\n```sql\nSELECT\n    NOW(),\n    CURRENT_DATE,\n    EXTRACT(YEAR FROM order_date),\n    AGE(order_date)\nFROM orders;\n```"}},
                    {"title":"SQL Functions Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Which function removes leading and trailing spaces?",
                     "options":[{"id":"a","label":"LENGTH()"},{"id":"b","label":"TRIM()"},{"id":"c","label":"SUBSTRING()"},{"id":"d","label":"UPPER()"}],
                     "correct_option":"b","hints":["Think about trimming excess whitespace","SQLite uses trim(), PostgreSQL uses TRIM()"],
                     "explanation":"TRIM() removes leading and trailing whitespace from a string."}},
                ]},
        ])

        sql_perf = await _seed_course(db, "SQL Performance & Optimization",
            "Query planning, EXPLAIN ANALYZE, indexing strategies, and performance tuning.",
            "SQL", [
                {"title":"Query Planning","order":0,"steps":[
                    {"title":"EXPLAIN ANALYZE","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Query Planning\n\n## EXPLAIN\nShows how PostgreSQL plans to execute a query.\n```sql\nEXPLAIN SELECT * FROM products WHERE price > 100;\n```\n\n## EXPLAIN ANALYZE\nActually runs the query and shows real timing.\n```sql\nEXPLAIN ANALYZE SELECT * FROM products\nWHERE price > 100\nORDER BY name;\n```\n\n## Common Scan Types\n- **Seq Scan** - reads entire table (slow for large tables)\n- **Index Scan** - uses an index to find rows\n- **Bitmap Heap Scan** - combines multiple indexes\n- **Nested Loop** - for each row in table A, scan table B\n- **Hash Join** - builds hash table then joins\n- **Merge Join** - sorts both tables then merges\n\n## Key Metrics\n- `actual time=0.025..0.050` - start..end time\n- `rows=10` - actual rows returned\n- `loops=1` - how many times this step ran\n- `cost=0.00..45.00` - estimated cost (lower = faster)"}},
                ]},
                {"title":"Indexing Strategies","order":1,"steps":[
                    {"title":"Index Types","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Index Types\n\n## B-Tree Index (default)\nBest for: equality, range queries, sorting\n```sql\nCREATE INDEX idx_price ON products(price);\n-- Speeds up: WHERE price = 100, WHERE price > 50, ORDER BY price\n```\n\n## Composite Index\n```sql\n-- Column order matters! Put equality columns first\nCREATE INDEX idx_user_status ON orders(user_id, status);\n-- Good: WHERE user_id = 5 AND status = 'shipped'\n-- Bad:  WHERE status = 'shipped' (user_id not used first)\n```\n\n## Partial Index\n```sql\nCREATE INDEX idx_active_users ON users(email)\nWHERE is_active = true;\n```\n\n## When NOT to index\n- Small tables (<1000 rows)\n- Columns rarely used in WHERE\n- Columns with few distinct values (boolean)\n- Tables with heavy write load\n\n## Index Maintenance\n```sql\n-- Rebuild an index\nREINDEX INDEX idx_products_price;\n\n-- Remove unused index\nDROP INDEX IF EXISTS idx_unused;\n```"}},
                    {"title":"Index Strategy Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":25,
                     "content_data":{"question":"For a query WHERE status = 'active' AND created_at > '2024-01-01', what is the best index?",
                     "options":[{"id":"a","label":"Single index on status"},{"id":"b","label":"Single index on created_at"},{"id":"c","label":"Composite (status, created_at)"},{"id":"d","label":"No index needed"}],
                     "correct_option":"c","hints":["Composite indexes with equality column first work best","WHERE uses both columns"],
                     "explanation":"A composite index on (status, created_at) can efficiently filter by status first, then by date range."}},
                ]},
                {"title":"Query Optimization","order":2,"steps":[
                    {"title":"Optimization Tips","step_type":StepType.THEORY,"order":0,"xp_reward":10,
                     "content_data":{"body_markdown":"# Query Optimization Tips\n\n## 1. Select only needed columns\n```sql\n-- BAD: SELECT * FROM users;\n-- GOOD: SELECT id, name, email FROM users;\n```\n\n## 2. Use EXISTS instead of IN for large lists\n```sql\n-- BAD: SELECT * FROM products WHERE id IN (SELECT product_id FROM orders);\n-- GOOD: SELECT * FROM products WHERE EXISTS (\n--     SELECT 1 FROM orders WHERE orders.product_id = products.id\n-- );\n```\n\n## 3. Avoid functions in WHERE (breaks index usage)\n```sql\n-- BAD: WHERE LOWER(email) = 'user@example.com'\n-- GOOD: WHERE email = 'user@example.com'\n-- Or use functional index: CREATE INDEX ON users(LOWER(email));\n```\n\n## 4. Use LIMIT\n```sql\nSELECT * FROM products ORDER BY price DESC LIMIT 10;\n```\n\n## 5. Pagination with keyset pagination\n```sql\n-- BAD (OFFSET): SELECT * FROM products OFFSET 1000 LIMIT 20;\n-- GOOD (keyset): SELECT * FROM products\n--     WHERE id > 1000 ORDER BY id LIMIT 20;\n```\n\n## 6. Analyze table statistics\n```sql\nANALYZE products;\n```"}},
                    {"title":"Optimization Quiz","step_type":StepType.QUIZ,"order":1,"xp_reward":20,
                     "content_data":{"question":"Why is `WHERE LOWER(email) = 'test@x.com'` slower than `WHERE email = 'test@x.com'`?",
                     "options":[{"id":"a","label":"It's not slower"},{"id":"b","label":"LOWER() prevents index usage"},{"id":"c","label":"LOWER() is slow in PostgreSQL"},{"id":"d","label":"String comparison is faster"}],
                     "correct_option":"b","hints":["Indexes store raw column values, not function results","Wrapping a column in a function makes the index invisible"],
                     "explanation":"Using LOWER(email) prevents the database from using a regular index on the email column, forcing a full table scan."}},
                ]},
        ])

        # ═══ ADD LEVELS TO PATHS ═══════════════════════

        js_path = (await db.execute(select(LearningPath).where(LearningPath.language == "JavaScript"))).scalar_one_or_none()
        sql_path = (await db.execute(select(LearningPath).where(LearningPath.language == "SQL"))).scalar_one_or_none()

        if js_path:
            for course, lvl_name, order in [
                (js_ds, "Intermediate 3: Data Structures & Algorithms", 4),
                (js_testing, "Intermediate 4: Testing & Debugging", 5),
            ]:
                if course:
                    db.add(PathLevel(path_id=js_path.id, course_id=course.id, level_name=lvl_name, order=order, required_progress_pct=75))
                    logger.info("  JS: added level %s", lvl_name)

        if sql_path:
            for course, lvl_name, order in [
                (sql_trans, "Intermediate 3: Transactions & Functions", 4),
                (sql_perf, "Intermediate 4: Performance & Optimization", 5),
            ]:
                if course:
                    db.add(PathLevel(path_id=sql_path.id, course_id=course.id, level_name=lvl_name, order=order, required_progress_pct=75))
                    logger.info("  SQL: added level %s", lvl_name)

        await db.commit()

        # ═══ FINAL STATS ═══════════════════════════════
        from sqlalchemy import func
        from app.modules.courses.models import Section as _Sec

        for lang in ['JavaScript', 'SQL']:
            courses = await db.execute(select(Course).where(Course.language == lang).order_by(Course.title))
            total = 0
            for c in courses.scalars():
                cnt = (await db.execute(select(func.count()).select_from(Step).join(_Sec).where(_Sec.course_id == c.id))).scalar() or 0
                total += cnt
            logger.info("%s: total %d steps across %d courses", lang, total, courses.rowcount if hasattr(courses,'rowcount') else '?')

        logger.info("=" * 50)
        logger.info("EXPANSION COMPLETE!")
        logger.info("  JavaScript and SQL now have 6 levels each")
        logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(expand())
