"""Expand Go content to match other languages (add courses + sections)."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def _seed(db, title, desc, lang, sections):
    if (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none():
        return None
    c = Course(title=title, description=desc, language=lang)
    db.add(c); await db.flush(); await db.refresh(c)
    total = 0
    for sec in sections:
        s = Section(course_id=c.id, title=sec["title"], order=sec["order"])
        db.add(s); await db.flush(); await db.refresh(s)
        for st in sec["steps"]:
            db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st.get("cd"))); total += 1
    await db.flush()
    logger.info("  Created: %s (%d steps)", title, total)
    return c

async def run():
    async with async_session_maker() as db:
        # ── 1. Add sections to Go Basics ──
        go_basics = (await db.execute(select(Course).where(Course.title == "Go Basics"))).scalar_one_or_none()
        if go_basics:
            last = (await db.execute(select(Section).where(Section.course_id == go_basics.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 4
            extra = [
                {"title":"Pointers","order":o,"steps":[
                    {"title":"Pointers","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Pointers\n\n```go\nfunc main() {\n    x := 42\n    p := &x  // pointer to x\n\n    fmt.Println(x)   // 42\n    fmt.Println(*p)  // 42 (dereference)\n\n    *p = 21          // change via pointer\n    fmt.Println(x)   // 21\n}\n\n// Pointer parameter (no pass-by-reference, but can mutate)\nfunc increment(n *int) {\n    *n++\n}\n\nfunc main() {\n    a := 5\n    increment(&a)\n    fmt.Println(a)  // 6\n}\n```"}},
                    {"title":"Pointers Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What does `&x` give you in Go?","options":[{"id":"a","label":"Value of x"},{"id":"b","label":"Memory address of x"},{"id":"c","label":"Copy of x"},{"id":"d","label":"Type of x"}],"correct_option":"b","hints":["& is the address-of operator","It returns a pointer"],"explanation":"&x returns the memory address of x (a pointer to x)."}},
                ]},
                {"title":"Arrays & Slices","order":o+1,"steps":[
                    {"title":"Slices","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Arrays & Slices\n\n## Arrays (fixed size)\n```go\nvar nums [5]int\nnums[0] = 10\nprimes := [5]int{2, 3, 5, 7, 11}\n```\n\n## Slices (dynamic, preferred)\n```go\nnums := []int{1, 2, 3}\nnums = append(nums, 4)  // [1,2,3,4]\n\n// Make with capacity\nslice := make([]int, 5, 10)  // len=5, cap=10\n\n// Slicing\nnumbers := []int{0,1,2,3,4,5}\nsub := numbers[1:4]  // [1,2,3]\n\n// Range\nfor i, v := range numbers {\n    fmt.Printf(\"index=%d value=%d\\n\", i, v)\n}\n```"}},
                    {"title":"Slice Practice","st":StepType.CODE,"order":1,"xp":30,"cd":{"instruction":"Write a Go function that takes a slice of ints and returns the sum.","starter_code":"package main\nimport \"fmt\"\n\nfunc sum(nums []int) int {\n    total := 0\n    for _, n := range nums {\n        total += n\n    }\n    return total\n}\n\nfunc main() {\n    nums := []int{10, 20, 30, 40, 50}\n    fmt.Println(sum(nums))\n}","solution":"package main\nimport \"fmt\"\nfunc sum(nums []int) int {\n    total := 0\n    for _, n := range nums {\n        total += n\n    }\n    return total\n}\nfunc main() {\n    nums := []int{10, 20, 30, 40, 50}\n    fmt.Println(sum(nums))\n}","compare_mode":"trim","expected_output":"150","hints":["Use `for _, n := range nums` to iterate","Use `_` to ignore the index"]}},
                ]},
            ]
            for sec_data in extra:
                s = Section(course_id=go_basics.id, title=sec_data["title"], order=sec_data["order"])
                db.add(s); await db.flush(); await db.refresh(s)
                count = 0
                for st in sec_data["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st.get("cd"))); count += 1
                logger.info("  Go Basics + %s (%d steps)", sec_data["title"], count)

        # ── 2. Add sections to Go Web ──
        go_web = (await db.execute(select(Course).where(Course.title == "Go Web Development"))).scalar_one_or_none()
        if go_web:
            last = (await db.execute(select(Section).where(Section.course_id == go_web.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 2
            extra = [
                {"title":"Middleware & Routing","order":o,"steps":[
                    {"title":"Middleware","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Middleware\n\n```go\nfunc loggingMiddleware(next http.Handler) http.Handler {\n    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {\n        log.Printf(\"%s %s\", r.Method, r.URL.Path)\n        next.ServeHTTP(w, r)\n    })\n}\n\nfunc main() {\n    mux := http.NewServeMux()\n    mux.HandleFunc(\"/api\", apiHandler)\n    \n    handler := loggingMiddleware(mux)\n    http.ListenAndServe(\":8080\", handler)\n}\n```"}},
                    {"title":"Middleware Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What does middleware typically do in Go HTTP servers?","options":[{"id":"a","label":"Serve static files"},{"id":"b","label":"Process requests before/after handlers"},{"id":"c","label":"Compile Go code"},{"id":"d","label":"Create databases"}],"correct_option":"b","hints":["Middleware wraps handlers","Common uses: logging, auth, compression"],"explanation":"Middleware processes HTTP requests before they reach the handler, or responses after."}},
                ]},
                {"title":"Database Access","order":o+1,"steps":[
                    {"title":"SQL with database/sql","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Database Access\n\n```go\nimport (\n    \"database/sql\"\n    _ \"github.com/lib/pq\"  // PostgreSQL driver\n)\n\ntype User struct {\n    ID    int\n    Name  string\n    Email string\n}\n\nfunc getUser(db *sql.DB, id int) (*User, error) {\n    user := &User{}\n    err := db.QueryRow(\n        \"SELECT id, name, email FROM users WHERE id = $1\", id,\n    ).Scan(&user.ID, &user.Name, &user.Email)\n    if err != nil {\n        return nil, err\n    }\n    return user, nil\n}\n\nfunc listUsers(db *sql.DB) ([]User, error) {\n    rows, err := db.Query(\"SELECT id, name, email FROM users\")\n    if err != nil {\n        return nil, err\n    }\n    defer rows.Close()\n\n    var users []User\n    for rows.Next() {\n        var u User\n        rows.Scan(&u.ID, &u.Name, &u.Email)\n        users = append(users, u)\n    }\n    return users, nil\n}\n```"}},
                    {"title":"DB Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What does db.QueryRow() return?","options":[{"id":"a","label":"Multiple rows"},{"id":"b","label":"A single row"},{"id":"c","label":"The database connection"},{"id":"d","label":"An error only"}],"correct_option":"b","hints":["Row vs Rows","QueryRow expects exactly one result"],"explanation":"QueryRow executes a query that returns at most one row. Use Query for multiple rows."}},
                ]},
            ]
            for sec_data in extra:
                s = Section(course_id=go_web.id, title=sec_data["title"], order=sec_data["order"])
                db.add(s); await db.flush(); await db.refresh(s)
                count = 0
                for st in sec_data["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st.get("cd"))); count += 1
                logger.info("  Go Web + %s (%d steps)", sec_data["title"], count)

        # ── 3. Go Errors & Testing course ──
        go_testing = await _seed(db, "Go Errors & Testing",
            "Error handling, panic/recover, unit testing, benchmarking, and debugging in Go.",
            "Go", [
                {"title":"Error Handling","order":0,"steps":[
                    {"title":"Errors & Panic","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Error Handling\n\n```go\n// Custom error\ntype ValidationError struct {\n    Field string\n    Value interface{}\n}\n\nfunc (e ValidationError) Error() string {\n    return fmt.Sprintf(\"invalid %s: %v\", e.Field, e.Value)\n}\n\n// Error wrapping\nfunc readFile(path string) error {\n    f, err := os.Open(path)\n    if err != nil {\n        return fmt.Errorf(\"opening %s: %w\", path, err)\n    }\n    defer f.Close()\n    return nil\n}\n\n// Panic & Recover\nfunc safeCall() {\n    defer func() {\n        if r := recover(); r != nil {\n            fmt.Println(\"Recovered:\", r)\n        }\n    }()\n    panic(\"something went wrong\")\n}\n```"}},
                    {"title":"Error Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What does `recover()` do in Go?","options":[{"id":"a","label":"Restarts the program"},{"id":"b","label":"Catches a panic"},{"id":"c","label":"Returns an error"},{"id":"d","label":"Logs a message"}],"correct_option":"b","hints":["Only works inside deferred functions","Stops the panic from crashing the program"],"explanation":"recover() catches a panic and returns the panic value, allowing the program to continue."}},
                ]},
                {"title":"Testing","order":1,"steps":[
                    {"title":"Unit Testing","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Testing in Go\n\n```go\n// math.go\nfunc Add(a, b int) int { return a + b }\nfunc Divide(a, b float64) (float64, error) {\n    if b == 0 { return 0, fmt.Errorf(\"division by zero\") }\n    return a / b, nil\n}\n\n// math_test.go\npackage main\n\nimport \"testing\"\n\nfunc TestAdd(t *testing.T) {\n    result := Add(2, 3)\n    expected := 5\n    if result != expected {\n        t.Errorf(\"Add(2,3) = %d; want %d\", result, expected)\n    }\n}\n\n// Table-driven test\nfunc TestDivide(t *testing.T) {\n    tests := []struct {\n        name string\n        a, b float64\n        want float64\n        err  bool\n    }{\n        {\"positive\", 10, 2, 5, false},\n        {\"by zero\", 10, 0, 0, true},\n    }\n    for _, tc := range tests {\n        t.Run(tc.name, func(t *testing.T) {\n            got, err := Divide(tc.a, tc.b)\n            if tc.err && err == nil {\n                t.Error(\"expected error\")\n            }\n            if !tc.err && got != tc.want {\n                t.Errorf(\"got %f want %f\", got, tc.want)\n            }\n        })\n    }\n}\n\n// Run: go test -v ./...\n```"}},
                    {"title":"Testing Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"How do you run all tests in a Go project?","options":[{"id":"a","label":"go test"},{"id":"b","label":"go test ./..."},{"id":"c","label":"go run test"},{"id":"d","label":"go check"}],"correct_option":"b","hints":["... means all packages","./ means current directory"],"explanation":"`go test ./...` runs all tests in all packages (including subdirectories)."}},
                ]},
        ])

        # ── 4. Go Advanced course ──
        go_adv = await _seed(db, "Go Advanced",
            "Interfaces, generics, reflection, file I/O, JSON, and CLI tools in Go.",
            "Go", [
                {"title":"Interfaces & Generics","order":0,"steps":[
                    {"title":"Interfaces","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Interfaces & Generics\n\n## Type Assertion\n```go\nvar i interface{} = \"hello\"\ns := i.(string)       // panics if wrong type\ns, ok := i.(string)  // safe: ok=false if wrong type\n```\n\n## Empty Interface\n```go\nfunc printAny(v interface{}) {\n    fmt.Printf(\"Value: %v, Type: %T\\n\", v, v)\n}\n\n// any is an alias for interface{} (Go 1.18+)\nfunc printAny2(v any) {\n    fmt.Println(v)\n}\n```\n\n## Generics (Go 1.18+)\n```go\nfunc Min[T constraints.Ordered](a, b T) T {\n    if a < b { return a }\n    return b\n}\n\nfunc main() {\n    fmt.Println(Min(3, 7))       // 3\n    fmt.Println(Min(3.14, 2.5))  // 2.5\n    fmt.Println(Min(\"a\", \"z\"))   // \"a\"\n}\n```"}},
                    {"title":"Generics Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What Go version introduced generics?","options":[{"id":"a","label":"Go 1.14"},{"id":"b","label":"Go 1.18"},{"id":"c","label":"Go 1.21"},{"id":"d","label":"Go 2.0"}],"correct_option":"b","hints":["Relatively recent addition","Type parameters in square brackets"],"explanation":"Generics were added in Go 1.18, allowing functions and types to be parameterized with type parameters."}},
                ]},
                {"title":"File I/O & JSON","order":1,"steps":[
                    {"title":"File I/O","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# File I/O & JSON\n\n## Reading Files\n```go\n// Entire file\ndata, err := os.ReadFile(\"data.txt\")\nif err != nil { log.Fatal(err) }\nfmt.Println(string(data))\n\n// Line by line\nfile, err := os.Open(\"data.txt\")\nif err != nil { log.Fatal(err) }\ndefer file.Close()\n\nscanner := bufio.NewScanner(file)\nfor scanner.Scan() {\n    fmt.Println(scanner.Text())\n}\n```\n\n## Writing Files\n```go\ndata := []byte(\"Hello, Go!\\n\")\nerr := os.WriteFile(\"output.txt\", data, 0644)\n```\n\n## JSON\n```go\ntype Person struct {\n    Name string `json:\"name\"`\n    Age  int    `json:\"age\"`\n}\n\n// Marshal (encode)\np := Person{Name: \"Alice\", Age: 30}\njsonData, _ := json.Marshal(p)\nfmt.Println(string(jsonData))\n\n// Unmarshal (decode)\nvar p2 Person\njson.Unmarshal([]byte(`{\"name\":\"Bob\",\"age\":25}`), &p2)\nfmt.Printf(\"%+v\\n\", p2)\n```"}},
                    {"title":"JSON Practice","st":StepType.CODE,"order":1,"xp":35,"cd":{"instruction":"Write a program that defines a Product struct (id, name, price), creates a product, marshals it to JSON, and prints the JSON string.","starter_code":"package main\nimport (\n    \"encoding/json\"\n    \"fmt\"\n)\n\ntype Product struct {\n    ID    int     `json:\"id\"`\n    Name  string  `json:\"name\"`\n    Price float64 `json:\"price\"`\n}\n\nfunc main() {\n    p := Product{ID: 1, Name: \"Laptop\", Price: 999.99}\n    data, _ := json.Marshal(p)\n    fmt.Println(string(data))\n}","solution":"package main\nimport (\n    \"encoding/json\"\n    \"fmt\"\n)\ntype Product struct {\n    ID    int     `json:\"id\"`\n    Name  string  `json:\"name\"`\n    Price float64 `json:\"price\"`\n}\nfunc main() {\n    p := Product{ID: 1, Name: \"Laptop\", Price: 999.99}\n    data, _ := json.Marshal(p)\n    fmt.Println(string(data))\n}","compare_mode":"contains","expected_output":"\"price\":999.99","hints":["Use json.Marshal to encode","Define struct with json tags"]}},
                ]},
        ])

        # ── Add to path ──
        go_path = (await db.execute(select(LearningPath).where(LearningPath.language == "Go"))).scalar_one_or_none()
        if go_path:
            for course, lvl_name, order, req in [
                (go_testing, "Intermediate: Errors & Testing", 2, 75),
                (go_adv, "Advanced: Generics & I/O", 3, 75),
            ]:
                if course and not (await db.execute(select(PathLevel).where(PathLevel.path_id == go_path.id, PathLevel.course_id == course.id))).scalar_one_or_none():
                    db.add(PathLevel(path_id=go_path.id, course_id=course.id, level_name=lvl_name, order=order, required_progress_pct=req))
                    logger.info("  Go path + %s", lvl_name)

        await db.commit()
        logger.info("=" * 50)
        logger.info("GO EXPANSION COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
