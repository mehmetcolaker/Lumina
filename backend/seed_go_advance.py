"""Add meaningful advanced Go content following a logical learning progression."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def _seed(db, title, desc, lang, sections):
    if (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none():
        logger.info("  Exists: %s", title)
        return None
    c = Course(title=title, description=desc, language=lang)
    db.add(c); await db.flush(); await db.refresh(c)
    total = 0
    for sec in sections:
        s = Section(course_id=c.id, title=sec["title"], order=sec["order"])
        db.add(s); await db.flush(); await db.refresh(s)
        for st in sec["steps"]:
            db.add(Step(section_id=s.id, title=st["t"], step_type=st["st"], order=st["o"], xp_reward=st["x"], content_data=st["d"])); total += 1
    await db.flush()
    logger.info("  Created: %s (%d steps)", title, total)
    return c

async def run():
    async with async_session_maker() as db:

        # ── 1. Add sections to Go Basics ──
        basics = (await db.execute(select(Course).where(Course.title == "Go Basics"))).scalar_one_or_none()
        if basics:
            last = (await db.execute(select(Section).where(Section.course_id == basics.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 100
            for sec_data in [
                {"title":"Constants & Iota","order":o,"steps":[
                    {"t":"Constants","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Constants & iota\n\n```go\nconst Pi = 3.14159\nconst AppName = \"Lumina\"\n\n// Typed vs untyped\nconst A int = 5        // typed\nconst B = 5              // untyped (inferred)\n\n// iota - sequential constants\nconst (\n    StatusOK = iota  // 0\n    StatusError      // 1\n    StatusPending    // 2\n)\n\n// iota with skip\nconst (\n    _ = iota      // 0 (discarded)\n    KB = 1 << (10 * iota)  // 1 << 10 = 1024\n    MB                     // 1 << 20\n    GB                     // 1 << 30\n)\nfmt.Println(KB, MB, GB)  // 1024 1048576 1073741824\n```"}},
                    {"t":"Constants Quiz","st":StepType.QUIZ,"o":1,"x":20,"d":{"question":"What value does the first use of iota get?","options":[{"id":"a","label":"1"},{"id":"b","label":"0"},{"id":"c","label":"Random"},{"id":"d","label":"-1"}],"correct_option":"b","hints":["iota starts at 0 within a const block","Each line increments by 1"],"explanation":"iota starts at 0 and increments by 1 for each new constant in the const block."}},
                ]},
            ]:
                s = Section(course_id=basics.id, title=sec_data["title"], order=sec_data["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec_data["steps"]:
                    db.add(Step(section_id=s.id, title=st["t"], step_type=st["st"], order=st["o"], xp_reward=st["x"], content_data=st["d"]))
                logger.info("  Basics + %s", sec_data["title"])

        # ── 2. Go Concurrency course ──
        await _seed(db, "Go Concurrency in Depth",
            "Master goroutines, channels, select, mutexes, wait groups, and concurrent patterns.",
            "Go", [
                {"title":"Goroutines","order":0,"steps":[
                    {"t":"Goroutine Lifecycle","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Goroutine Lifecycle\n\n```go\nfunc printNums() {\n    for i := 1; i <= 5; i++ {\n        time.Sleep(100 * time.Millisecond)\n        fmt.Println(i)\n    }\n}\n\nfunc main() {\n    go printNums()  // runs concurrently\n    go printNums()\n    \n    // Wait so main doesn't exit early\n    time.Sleep(2 * time.Second)\n}\n\n// sync.WaitGroup (proper way)\nfunc worker(id int, wg *sync.WaitGroup) {\n    defer wg.Done()\n    fmt.Printf(\"Worker %d starting\\n\", id)\n    time.Sleep(time.Second)\n    fmt.Printf(\"Worker %d done\\n\", id)\n}\n\nfunc main() {\n    var wg sync.WaitGroup\n    for i := 1; i <= 3; i++ {\n        wg.Add(1)\n        go worker(i, &wg)\n    }\n    wg.Wait()  // blocks until all done\n    fmt.Println(\"All workers finished\")\n}\n```"}},
                ]},
                {"title":"Channels","order":1,"steps":[
                    {"t":"Channels","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Channels\n\n## Unbuffered (synchronous)\n```go\nch := make(chan int)\n\n// Send and receive must happen simultaneously\ngo func() { ch <- 42 }()\nvalue := <-ch\nfmt.Println(value)  // 42\n```\n\n## Buffered (async up to capacity)\n```go\nch := make(chan string, 3)\nch <- \"a\"\nch <- \"b\"\nch <- \"c\"\n// ch <- \"d\"  // would block (full)\n\nfmt.Println(<-ch)  // \"a\"\n```\n\n## Closing channels\n```go\nch := make(chan int)\ngo func() {\n    for i := 0; i < 5; i++ {\n        ch <- i\n    }\n    close(ch)\n}()\n\nfor value := range ch {\n    fmt.Println(value)  // receives until closed\n}\n```\n\n## Select (wait on multiple channels)\n```go\nselect {\ncase msg1 := <-ch1:\n    fmt.Println(\"Received from ch1:\", msg1)\ncase msg2 := <-ch2:\n    fmt.Println(\"Received from ch2:\", msg2)\ncase <-time.After(1 * time.Second):\n    fmt.Println(\"Timeout!\")\ndefault:\n    fmt.Println(\"No channels ready\")\n}\n```"}},
                    {"t":"Channel Quiz","st":StepType.QUIZ,"o":1,"x":20,"d":{"question":"What happens when you send to a full buffered channel?","options":[{"id":"a","label":"Panics"},{"id":"b","label":"Blocks until space available"},{"id":"c","label":"Drops the value"},{"id":"d","label":"Overwrites the oldest value"}],"correct_option":"b","hints":["Buffered channels block when full","Unbuffered channels always block until received"],"explanation":"A buffered channel blocks the sender when the buffer is full until a receiver reads a value."}},
                    {"t":"Worker Pool","st":StepType.CODE,"o":2,"x":45,"d":{"instruction":"Create a worker pool: 3 workers process 5 jobs from a channel. Each worker prints 'Worker W processing job J'. Use sync.WaitGroup.\n\nHint: range over jobs channel, close it after sending all jobs.","starter_code":"package main\nimport (\n    \"fmt\"\n    \"sync\"\n    \"time\"\n)\n\nfunc worker(id int, jobs <-chan int, wg *sync.WaitGroup) {\n    defer wg.Done()\n    for job := range jobs {\n        fmt.Printf(\"Worker %d processing job %d\\n\", id, job)\n        time.Sleep(200 * time.Millisecond)\n    }\n}\n\nfunc main() {\n    jobs := make(chan int, 5)\n    var wg sync.WaitGroup\n\n    for w := 1; w <= 3; w++ {\n        wg.Add(1)\n        go worker(w, jobs, &wg)\n    }\n\n    for j := 1; j <= 5; j++ {\n        jobs <- j\n    }\n    close(jobs)\n\n    wg.Wait()\n    fmt.Println(\"All done!\")\n}","solution":"package main\nimport (\n    \"fmt\"\n    \"sync\"\n    \"time\"\n)\nfunc worker(id int, jobs <-chan int, wg *sync.WaitGroup) {\n    defer wg.Done()\n    for job := range jobs {\n        fmt.Printf(\"Worker %d processing job %d\\n\", id, job)\n        time.Sleep(200 * time.Millisecond)\n    }\n}\nfunc main() {\n    jobs := make(chan int, 5)\n    var wg sync.WaitGroup\n    for w := 1; w <= 3; w++ {\n        wg.Add(1)\n        go worker(w, jobs, &wg)\n    }\n    for j := 1; j <= 5; j++ { jobs <- j }\n    close(jobs)\n    wg.Wait()\n    fmt.Println(\"All done!\")\n}","compare_mode":"contains","expected_output":"All done!","hints":["defer wg.Done() in the worker","close(jobs) after sending all jobs","wg.Wait() in main"]}},
                ]},
                {"title":"Mutex & Atomic","order":2,"steps":[
                    {"t":"Mutex & Atomic","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Mutex & Atomic\n\n## sync.Mutex\n```go\ntype Counter struct {\n    mu    sync.Mutex\n    value int\n}\n\nfunc (c *Counter) Increment() {\n    c.mu.Lock()\n    defer c.mu.Unlock()\n    c.value++\n}\n\nfunc (c *Counter) Value() int {\n    c.mu.Lock()\n    defer c.mu.Unlock()\n    return c.value\n}\n\n// RWMutex - multiple readers allowed\nvar rw sync.RWMutex\nfunc read() {\n    rw.RLock()\n    defer rw.RUnlock()\n    // multiple goroutines can read simultaneously\n}\n```\n\n## sync/atomic\n```go\nimport \"sync/atomic\"\n\nvar counter int64\natomic.AddInt64(&counter, 1)\nvalue := atomic.LoadInt64(&counter)\n```\n\n## Once\n```go\nvar once sync.Once\nonce.Do(func() {\n    // runs only once, even from multiple goroutines\n    fmt.Println(\"Initialized!\")\n})\n```"}},
                    {"t":"Mutex Quiz","st":StepType.QUIZ,"o":1,"x":20,"d":{"question":"What is the main purpose of sync.Mutex?","options":[{"id":"a","label":"Speed up execution"},{"id":"b","label":"Prevent concurrent data races"},{"id":"c","label":"Create new goroutines"},{"id":"d","label":"Manage memory"}],"correct_option":"b","hints":["Race conditions happen with concurrent writes","Mutex serializes access to shared data"],"explanation":"Mutex prevents multiple goroutines from accessing shared data simultaneously, preventing race conditions."}},
                ]},
        ])

        # ── 3. Go Standard Library course ──
        await _seed(db, "Go Standard Library",
            "Explore Go's powerful standard library: fmt, strings, time, sort, crypto, and more.",
            "Go", [
                {"title":"Strings & Formatting","order":0,"steps":[
                    {"t":"String Manipulation","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Strings & Formatting\n\n## strings package\n```go\nimport \"strings\"\n\ns := \"Hello, Go World!\"\n\nstrings.Contains(s, \"Go\")        // true\nstrings.HasPrefix(s, \"Hello\")    // true\nstrings.HasSuffix(s, \"!\")       // true\nstrings.Index(s, \"Go\")          // 7\nstrings.Replace(s, \"Go\", \"Golang\", 1)  // \"Hello, Golang World!\"\nstrings.ToUpper(s)               // \"HELLO, GO WORLD!\"\nstrings.Split(s, \", \")          // [\"Hello\", \"Go World!\"]\nstrings.Join([]string{\"a\",\"b\"}, \"-\") // \"a-b\"\nstrings.Trim(\"  hello  \", \" \")    // \"hello\"\n```\n\n## fmt formatting\n```go\nname := \"Alice\"\nage := 30\n\nfmt.Printf(\"%%s: %%s\\n\", \"name\", name)     // name: Alice\nfmt.Printf(\"%%d\\n\", age)                   // 30\nfmt.Printf(\"%%5d\\n\", age)                  // \"   30\" (width 5)\nfmt.Printf(\"%%-5d\\n\", age)                 // \"30   \" (left align)\nfmt.Printf(\"%%.2f\\n\", 3.14159)            // 3.14\nfmt.Printf(\"%%t\\n\", true)                  // true\nfmt.Printf(\"%%T\\n\", name)                  // string (type)\nfmt.Printf(\"%%v - %%+v\\n\", name, name)     // Alice - Alice\nfmt.Printf(\"%%#v\\n\", name)                 // \"Alice\" (Go syntax)\n```"}},
                    {"t":"String Quiz","st":StepType.QUIZ,"o":1,"x":20,"d":{"question":"What does strings.Trim(\"  hi  \", \" \") return?","options":[{"id":"a","label":"\"hi\""},{"id":"b","label":"\"  hi\""},{"id":"c","label":"\"hi  \""},{"id":"d","label":"\"hi\" extra space"}],"correct_option":"a","hints":["Trim removes leading AND trailing characters","The second argument is the cutset"],"explanation":"strings.Trim removes all leading and trailing characters contained in the cutset."}},
                ]},
                {"title":"Time & Date","order":1,"steps":[
                    {"t":"Time Package","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Time Package\n\n```go\nimport \"time\"\n\n// Current time\nnow := time.Now()\nfmt.Println(now)  // 2026-05-09 12:00:00 +0300 +03\n\n// Creating time\nt := time.Date(2026, time.May, 9, 12, 0, 0, 0, time.UTC)\n\n// Formatting (Go uses reference time: Mon Jan 2 15:04:05 MST 2006)\nfmt.Println(now.Format(\"2006-01-02\"))              // 2026-05-09\nfmt.Println(now.Format(\"Monday, Jan 2, 2006\"))      // Saturday, May 9, 2026\nfmt.Println(now.Format(\"15:04:05\"))                 // 12:00:00\n\n// Parsing\nparsed, _ := time.Parse(\"2006-01-02\", \"2026-05-09\")\n\n// Duration\nlater := now.Add(2 * time.Hour)\ndiff := later.Sub(now)\nfmt.Println(diff)  // 2h0m0s\n\n// Sleep\ntime.Sleep(100 * time.Millisecond)\n\n// Ticker (periodic)\nticker := time.NewTicker(1 * time.Second)\nfor range ticker.C {\n    fmt.Println(\"tick\")\n}\n\n// Timer (one-shot)\ntimer := time.NewTimer(2 * time.Second)\n<-timer.C  // blocks for 2 seconds\n```"}},
                    {"t":"Time Quiz","st":StepType.QUIZ,"o":1,"x":20,"d":{"question":"What reference time does Go use for formatting?","options":[{"id":"a","label":"01/01/1970"},{"id":"b","label":"Mon Jan 2 15:04:05 MST 2006"},{"id":"c","label":"12/25/2025"},{"id":"d","label":"Unix epoch"}],"correct_option":"b","hints":["Go uses a specific memorable time","It's a mnemonic: 01/02 03:04:05PM '06 -0700"],"explanation":"Go's reference time is Mon Jan 2 15:04:05 MST 2006 (1 2 3 4 5 6 -7). Each number corresponds to a format component."}},
                ]},
                {"title":"Sort & Containers","order":2,"steps":[
                    {"t":"Sorting","st":StepType.THEORY,"o":0,"x":10,"d":{"body_markdown":"# Sort & Containers\n\n## sort package\n```go\nimport \"sort\"\n\n// Basic sorts\nnums := []int{5, 2, 6, 3, 1, 4}\nsort.Ints(nums)  // [1 2 3 4 5 6]\n\nstrs := []string{\"banana\", \"apple\", \"cherry\"}\nsort.Strings(strs)  // [apple banana cherry]\n\n// Sort custom type\npeople := []Person{\n    {Name: \"Alice\", Age: 30},\n    {Name: \"Bob\", Age: 25},\n    {Name: \"Charlie\", Age: 35},\n}\n\nsort.Slice(people, func(i, j int) bool {\n    return people[i].Age < people[j].Age\n})\n// [{Bob 25} {Alice 30} {Charlie 35}]\n\n// Sort by multiple fields\nsort.Slice(people, func(i, j int) bool {\n    if people[i].Age != people[j].Age {\n        return people[i].Age < people[j].Age\n    }\n    return people[i].Name < people[j].Name\n})\n\n// Check if sorted\nsort.IntsAreSorted(nums)  // true\n\n// Search (binary search)\nindex := sort.SearchInts(nums, 3)  // finds 3 in sorted nums\n```"}},
                    {"t":"Sort Practice","st":StepType.CODE,"o":1,"x":35,"d":{"instruction":"Sort a slice of Product structs by price descending (highest first).\n\nUse sort.Slice() with a custom less function.","starter_code":"package main\nimport (\n    \"fmt\"\n    \"sort\"\n)\n\ntype Product struct {\n    Name  string\n    Price float64\n}\n\nfunc main() {\n    products := []Product{\n        {\"Laptop\", 2499.99},\n        {\"Mouse\", 29.99},\n        {\"Monitor\", 599.99},\n        {\"Keyboard\", 149.99},\n    }\n\n    sort.Slice(products, func(i, j int) bool {\n        return products[i].Price > products[j].Price\n    })\n\n    for _, p := range products {\n        fmt.Printf(\"%s: $%.2f\\n\", p.Name, p.Price)\n    }\n}","solution":"package main\nimport (\n    \"fmt\"\n    \"sort\"\n)\ntype Product struct { Name string; Price float64 }\nfunc main() {\n    products := []Product{\n        {\"Laptop\", 2499.99}, {\"Mouse\", 29.99},\n        {\"Monitor\", 599.99}, {\"Keyboard\", 149.99},\n    }\n    sort.Slice(products, func(i, j int) bool {\n        return products[i].Price > products[j].Price\n    })\n    for _, p := range products {\n        fmt.Printf(\"%s: $%.2f\\n\", p.Name, p.Price)\n    }\n}","compare_mode":"contains","expected_output":"Laptop: $2499.99","hints":["sort.Slice takes a less function","> for descending, < for ascending"]}},
                ]},
        ])

        # ── 4. Add to path ──
        go_path = (await db.execute(select(LearningPath).where(LearningPath.language == "Go"))).scalar_one_or_none()
        if go_path:
            # find max current order
            levels = await db.execute(select(PathLevel).where(PathLevel.path_id == go_path.id).order_by(PathLevel.order.desc()).limit(1))
            level_row = levels.first()
            max_order = level_row[0].order if level_row else 0

            for course, lvl_name, req in [
                ("Go Concurrency in Depth", "Advanced: Concurrency in Depth", 75),
                ("Go Standard Library", "Advanced: Standard Library", 75),
            ]:
                c = (await db.execute(select(Course).where(Course.title == course))).scalar_one_or_none()
                if c and not (await db.execute(select(PathLevel).where(PathLevel.path_id == go_path.id, PathLevel.course_id == c.id))).scalar_one_or_none():
                    max_order += 1
                    db.add(PathLevel(path_id=go_path.id, course_id=c.id, level_name=lvl_name, order=max_order, required_progress_pct=req))
                    logger.info("  Go path + %s", lvl_name)

        await db.commit()
        logger.info("=" * 50)
        logger.info("GO ADVANCED EXPANSION COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
