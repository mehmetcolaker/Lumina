"""Seed Go programming language roadmap with courses (English)."""

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
        go_basics = await _seed(db, "Go Basics",
            "Learn Go programming: variables, control flow, functions, structs, interfaces, and packages.",
            "Go", [
                {"title":"Getting Started","order":0,"steps":[
                    {"title":"Hello, Go!","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Go Basics\n\nGo is a compiled, concurrent, garbage-collected language developed at Google.\n\n```go\npackage main\n\nimport \"fmt\"\n\nfunc main() {\n    fmt.Println(\"Hello, Go!\")\n}\n```\n\n## Key Features\n- **Fast compilation** to a single binary\n- **Built-in concurrency** (goroutines, channels)\n- **Static typing** with type inference\n- **Garbage collected**\n- **Rich standard library**\n\nTo run: `go run main.go`\nTo build: `go build -o myapp main.go`"}},
                    {"title":"Variables & Types","st":StepType.THEORY,"order":1,"xp":10,"cd":{"body_markdown":"# Variables & Types\n\n```go\npackage main\nimport \"fmt\"\n\nfunc main() {\n    // Type inference\n    name := \"Alice\"        // string\n    age := 30               // int\n    height := 1.75          // float64\n    isActive := true        // bool\n\n    // Explicit declaration\n    var city string = \"NYC\"\n    var x int\n    x = 42\n\n    fmt.Printf(\"%s is %d years old\\n\", name, age)\n    fmt.Printf(\"Height: %.2f, Active: %t\\n\", height, isActive)\n}\n\n// Output:\n// Alice is 30 years old\n// Height: 1.75, Active: true\n```\n\n## Basic Types\n| Type | Description |\n|------|-------------|\n| `string` | Text |\n| `int`, `int32`, `int64` | Integers |\n| `float32`, `float64` | Floats |\n| `bool` | Boolean |\n| `byte` | alias for uint8 |\n| `rune` | alias for int32 (unicode)"}},
                    {"title":"Variables Quiz","st":StepType.QUIZ,"order":2,"xp":20,"cd":{"question":"What is the correct way to declare a variable with type inference in Go?","options":[{"id":"a","label":"var x = 5"},{"id":"b","label":"x := 5"},{"id":"c","label":"let x = 5"},{"id":"d","label":"auto x = 5"}],"correct_option":"b","hints":["Short declaration uses := operator","Type is inferred from the value"],"explanation":"x := 5 declares x with inferred type int and value 5."}},
                    {"title":"Hello Go","st":StepType.CODE,"order":3,"xp":30,"cd":{"instruction":"Write a Go program that prints your name and age using fmt.Printf.","starter_code":"package main\nimport \"fmt\"\n\nfunc main() {\n    name := \"YourName\"\n    age := 20\n    fmt.Printf(\"My name is %s and I am %d years old\\n\", name, age)\n}","solution":"package main\nimport \"fmt\"\nfunc main() {\n    name := \"YourName\"\n    age := 20\n    fmt.Printf(\"My name is %s and I am %d years old\\n\", name, age)\n}","compare_mode":"contains","expected_output":"My name is","hints":["Use := for variable declaration","fmt.Printf for formatted output"]}},
                ]},
                {"title":"Control Flow","order":1,"steps":[
                    {"title":"If, For, Switch","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Control Flow\n\n## If/Else\n```go\nif score >= 90 {\n    fmt.Println(\"A\")\n} else if score >= 70 {\n    fmt.Println(\"B\")\n} else {\n    fmt.Println(\"C\")\n}\n```\n\n## For (only loop in Go)\n```go\n// Traditional\nfor i := 0; i < 5; i++ {\n    fmt.Println(i)\n}\n\n// While-style\nsum := 0\nfor sum < 100 {\n    sum += 10\n}\n\n// Range loop\nnums := []int{10, 20, 30}\nfor index, value := range nums {\n    fmt.Println(index, value)\n}\n```\n\n## Switch\n```go\nswitch day {\ncase \"Monday\":\n    fmt.Println(\"Start of week\")\ncase \"Friday\":\n    fmt.Println(\"TGIF!\")\ndefault:\n    fmt.Println(\"Regular day\")\n}\n```\n\nNo parentheses needed, no fallthrough by default."}},
                    {"title":"Loop Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"Which keyword does Go use for ALL types of loops?","options":[{"id":"a","label":"while"},{"id":"b","label":"for"},{"id":"c","label":"loop"},{"id":"d","label":"foreach"}],"correct_option":"b","hints":["Go has only ONE loop keyword","It can be used in multiple styles"],"explanation":"Go only has `for`. It can be used as a traditional for, while, or range loop."}},
                ]},
                {"title":"Functions","order":2,"steps":[
                    {"title":"Functions & Multiple Returns","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Functions\n\n```go\n// Basic function\nfunc add(a int, b int) int {\n    return a + b\n}\n\n// Type shorthand\nfunc multiply(a, b int) int {\n    return a * b\n}\n\n// Multiple return values\nfunc divide(a, b float64) (float64, error) {\n    if b == 0 {\n        return 0, fmt.Errorf(\"division by zero\")\n    }\n    return a / b, nil\n}\n\n// Named returns\nfunc split(sum int) (x, y int) {\n    x = sum * 4 / 9\n    y = sum - x\n    return  // naked return\n}\n\n// Variadic\nfunc sum(nums ...int) int {\n    total := 0\n    for _, n := range nums {\n        total += n\n    }\n    return total\n}\n```"}},
                    {"title":"Functions Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"How do you return multiple values from a Go function?","options":[{"id":"a","label":"Return an array"},{"id":"b","label":"Multiple return types in parentheses"},{"id":"c","label":"Use pointers"},{"id":"d","label":"Use global variables"}],"correct_option":"b","hints":["Go supports multiple return values natively","Syntax: (type1, type2)"],"explanation":"Go functions can return multiple values by listing types in parentheses: func f() (int, error)"}},
                ]},
                {"title":"Structs & Methods","order":3,"steps":[
                    {"title":"Structs","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Structs & Methods\n\n```go\ntype Person struct {\n    Name string\n    Age  int\n    City string\n}\n\n// Method with value receiver\nfunc (p Person) Greet() string {\n    return fmt.Sprintf(\"Hi, I'm %s from %s\", p.Name, p.City)\n}\n\n// Method with pointer receiver (modifies)\nfunc (p *Person) Birthday() {\n    p.Age++\n}\n\nfunc main() {\n    alice := Person{Name: \"Alice\", Age: 30, City: \"NYC\"}\n    fmt.Println(alice.Greet())     // Hi, I'm Alice from NYC\n    \n    alice.Birthday()\n    fmt.Println(alice.Age)         // 31\n}\n```\n\n## Interfaces\n```go\ntype Shape interface {\n    Area() float64\n}\n\ntype Circle struct {\n    Radius float64\n}\n\nfunc (c Circle) Area() float64 {\n    return math.Pi * c.Radius * c.Radius\n}\n\n// Any type that has Area() float64 implements Shape\nfunc printArea(s Shape) {\n    fmt.Printf(\"Area: %.2f\\n\", s.Area())\n}\n```"}},
                    {"title":"Struct Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"What does a pointer receiver (p *Person) allow?","options":[{"id":"a","label":"Faster execution"},{"id":"b","label":"Modifying the original struct"},{"id":"c","label":"Method chaining"},{"id":"d","label":"Nil safety"}],"correct_option":"b","hints":["Pointer receivers can modify the struct","Value receivers work on a copy"],"explanation":"A pointer receiver allows the method to modify the original struct value, not a copy."}},
                ]},
        ])

        go_web = await _seed(db, "Go Web Development",
            "Build web servers with Go: HTTP handlers, JSON APIs, middleware, and database access.",
            "Go", [
                {"title":"HTTP Server","order":0,"steps":[
                    {"title":"Web Servers","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Go Web Server\n\n## Basic HTTP Server\n```go\npackage main\n\nimport (\n    \"fmt\"\n    \"net/http\"\n)\n\nfunc helloHandler(w http.ResponseWriter, r *http.Request) {\n    fmt.Fprintf(w, \"Hello, %s!\", r.URL.Path[1:])\n}\n\nfunc main() {\n    http.HandleFunc(\"/\", helloHandler)\n    http.ListenAndServe(\":8080\", nil)\n}\n```\n\n## JSON API\n```go\nfunc userHandler(w http.ResponseWriter, r *http.Request) {\n    w.Header().Set(\"Content-Type\", \"application/json\")\n    \n    user := User{Name: \"Alice\", Age: 30}\n    json.NewEncoder(w).Encode(user)\n}\n\n// Reading JSON\nfunc createUser(w http.ResponseWriter, r *http.Request) {\n    var user User\n    err := json.NewDecoder(r.Body).Decode(&user)\n    if err != nil {\n        http.Error(w, err.Error(), 400)\n        return\n    }\n    fmt.Fprintf(w, \"Created: %+v\", user)\n}\n```"}},
                    {"title":"Web Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"Which function starts an HTTP server in Go?","options":[{"id":"a","label":"http.StartServer()"},{"id":"b","label":"http.ListenAndServe()"},{"id":"c","label":"net.Listen()"},{"id":"d","label":"http.Run()"}],"correct_option":"b","hints":["It's in the net/http package","The standard way to serve HTTP"],"explanation":"http.ListenAndServe(port, handler) starts an HTTP server on the given port."}},
                ]},
                {"title":"Concurrency","order":1,"steps":[
                    {"title":"Goroutines & Channels","st":StepType.THEORY,"order":0,"xp":10,"cd":{"body_markdown":"# Concurrency\n\n## Goroutines (lightweight threads)\n```go\nfunc printNumbers() {\n    for i := 1; i <= 5; i++ {\n        time.Sleep(100 * time.Millisecond)\n        fmt.Println(i)\n    }\n}\n\nfunc main() {\n    go printNumbers()  // runs concurrently\n    go printNumbers()\n    time.Sleep(1 * time.Second)\n}\n```\n\n## Channels (communicate between goroutines)\n```go\nfunc worker(id int, jobs <-chan int, results chan<- int) {\n    for j := range jobs {\n        fmt.Printf(\"Worker %d processing job %d\\n\", id, j)\n        time.Sleep(time.Second)\n        results <- j * 2\n    }\n}\n\nfunc main() {\n    jobs := make(chan int, 5)\n    results := make(chan int, 5)\n\n    // Start 3 workers\n    for w := 1; w <= 3; w++ {\n        go worker(w, jobs, results)\n    }\n\n    // Send 5 jobs\n    for j := 1; j <= 5; j++ {\n        jobs <- j\n    }\n    close(jobs)\n\n    // Collect results\n    for r := 1; r <= 5; r++ {\n        <-results\n    }\n}\n```"}},
                    {"title":"Goroutine Quiz","st":StepType.QUIZ,"order":1,"xp":20,"cd":{"question":"Which keyword starts a concurrent goroutine?","options":[{"id":"a","label":"thread"},{"id":"b","label":"go"},{"id":"c","label":"async"},{"id":"d","label":"spawn"}],"correct_option":"b","hints":["It's a single keyword","Go makes concurrency easy"],"explanation":"The `go` keyword starts a goroutine: `go myFunction()` runs it concurrently."}},
                ]},
        ])

        # Create Go LearningPath
        existing_path = await db.execute(select(LearningPath).where(LearningPath.language == "Go"))
        if existing_path.scalar_one_or_none():
            logger.info("Go path exists, skipping")
        else:
            py_path = (await db.execute(select(LearningPath).where(LearningPath.language == "Python"))).scalar_one_or_none()
            max_order = py_path.order + 1 if py_path else 3

            path = LearningPath(
                title="Go Developer Roadmap",
                description="Learn Go programming from scratch: basics, web development, and concurrency.",
                language="Go", icon="GO", order=max_order,
            )
            db.add(path); await db.flush()

            courses_data = []
            if go_basics:
                courses_data.append((go_basics, "Beginner: Go Basics", 0, 0))
            if go_web:
                courses_data.append((go_web, "Intermediate: Web Development", 1, 75))

            for course, lvl_name, order, req in courses_data:
                if course:
                    db.add(PathLevel(path_id=path.id, course_id=course.id, level_name=lvl_name, order=order, required_progress_pct=req))
                    logger.info("  Added: %s", lvl_name)

            logger.info("Go Developer Roadmap created!")

        await db.commit()
        logger.info("=" * 50)
        logger.info("GO SEED COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
