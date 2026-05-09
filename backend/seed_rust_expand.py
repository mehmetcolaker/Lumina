"""Add more Rust content to match 50+ step count."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
S = StepType

def md(s):
    return {"body_markdown": s}

async def run():
    async with async_session_maker() as db:

        # ── 1. Add sections to Rust Fundamentals ──
        fund = (await db.execute(select(Course).where(Course.title == "Rust Fundamentals"))).scalar_one_or_none()
        if fund:
            last = (await db.execute(select(Section).where(Section.course_id == fund.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 10
            for sec in [
                {"title":"Pattern Matching Deep Dive","order":o,"steps":[
                    {"title":"Advanced Match","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Advanced Pattern Matching

```rust
struct Point { x: i32, y: i32 }
let p = Point { x: 0, y: 7 };

match p {
    Point { x: 0, y } => println!("On y-axis at y={}", y),
    Point { x, y: 0 } => println!("On x-axis at x={}", x),
    Point { x, y } => println!("At ({}, {})", x, y),
}

// Guards
match number {
    1 => println!("One!"),
    n if n < 10 => println!("Less than 10"),
    _ => println!("Other"),
}

// @ bindings
if let Message::Write(s) = msg {
    println!("Length: {}", s.len());
}
```''')},
                    {"title":"Pattern Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"What does `if` do inside a match arm?","options":[{"id":"a","label":"Creates if-else"},{"id":"b","label":"Guard condition"},{"id":"c","label":"Pattern separator"},{"id":"d","label":"Loop"}],"correct_option":"b","hints":["Guard adds extra condition","n if n > 5 => ..."]}},
                ]},
            ]:
                s = Section(course_id=fund.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
                logger.info("  Fund + %s (%d steps)", sec["title"], len(sec["steps"]))

        # ── 2. Add sections to Rust Structs & Enums ──
        structs = (await db.execute(select(Course).where(Course.title == "Rust Structs & Enums"))).scalar_one_or_none()
        if structs:
            last = (await db.execute(select(Section).where(Section.course_id == structs.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 10
            for sec in [
                {"title":"Derive Macros","order":o,"steps":[
                    {"title":"Derive & Custom","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Derive Macros

```rust
#[derive(Debug, Clone, PartialEq)]
struct User { id: u32, name: String, }

let u1 = User { id: 1, name: "Alice".into() };
let u2 = u1.clone();
println!("{:?}", u2);
println!("{}", u1 == u2);
```
Common derivable traits: Debug, Clone, Copy, PartialEq, Eq, Hash, Default, PartialOrd, Ord.
''')},
                    {"title":"Derive Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"Which trait enables {:?} printing?","options":[{"id":"a","label":"Display"},{"id":"b","label":"Debug"},{"id":"c","label":"Show"},{"id":"d","label":"Format"}],"correct_option":"b","hints":["{:?} uses Debug trait","{} uses Display"]}},
                    {"title":"Derive Practice","st":S.CODE,"order":2,"xp":35,"cd":{"instruction":"Add derives to Point so it can be cloned, printed with {:?}, and compared with ==.","starter_code":"#[derive(Debug, Clone, PartialEq)]\nstruct Point { x: i32, y: i32 }\nfn main() {\n    let p1 = Point { x: 1, y: 2 };\n    let p2 = p1.clone();\n    let p3 = Point { x: 1, y: 2 };\n    println!(\"{:?}\", p2);\n    println!(\"{}\", p1 == p3);\n}","solution":"#[derive(Debug, Clone, PartialEq)]\nstruct Point { x: i32, y: i32 }\nfn main() {\n    let p1 = Point { x: 1, y: 2 };\n    let p2 = p1.clone();\n    let p3 = Point { x: 1, y: 2 };\n    println!(\"{:?}\", p2);\n    println!(\"{}\", p1 == p3);\n}","compare_mode":"contains","expected_output":"true","hints":["Add #[derive(Debug, Clone, PartialEq)]"]}},
                ]},
            ]:
                s = Section(course_id=structs.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
                logger.info("  Structs + %s (%d steps)", sec["title"], len(sec["steps"]))

        # ── 3. Add to Rust Testing ──
        testing = (await db.execute(select(Course).where(Course.title == "Rust Testing & Modules"))).scalar_one_or_none()
        if testing:
            last = (await db.execute(select(Section).where(Section.course_id == testing.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 10
            for sec in [
                {"title":"Integration & Doc Tests","order":o,"steps":[
                    {"title":"Advanced Testing","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Integration & Doc Tests

## Integration tests (tests/ directory)
```rust
use my_crate;
#[test]
fn test_full_flow() {
    let result = my_crate::process_data(vec![1, 2, 3]);
    assert!(result.is_ok());
}
```

## Doc tests (in doc comments)
```rust
/// ```rust
/// assert_eq!(my_crate::add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

## Attributes
- #[ignore] - skip
- #[should_panic(expected = "...")]
- cargo test -- --ignored
''')},
                ]},
            ]:
                s = Section(course_id=testing.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
                logger.info("  Testing + %s (%d steps)", sec["title"], len(sec["steps"]))

        # ── 4. New course: Rust Common Patterns ──
        patterns = (await db.execute(select(Course).where(Course.title == "Rust Common Patterns"))).scalar_one_or_none()
        if not patterns:
            patterns = Course(title="Rust Common Patterns",
                description="Builder pattern, newtype, RAII, type state, and other idiomatic Rust patterns.",
                language="Rust")
            db.add(patterns); await db.flush(); await db.refresh(patterns)
            for sec in [
                {"title":"Builder Pattern","order":0,"steps":[
                    {"title":"Builder & Newtype","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Idiomatic Rust Patterns

## Builder Pattern
```rust
#[derive(Debug)]
struct Request { url: String, method: String, headers: Vec<(String,String)> }

struct RequestBuilder { url: String, method: String, headers: Vec<(String,String)> }

impl RequestBuilder {
    fn new(url: &str) -> Self {
        Self { url: url.into(), method: "GET".into(), headers: vec![] }
    }
    fn method(mut self, m: &str) -> Self { self.method = m.into(); self }
    fn header(mut self, k: &str, v: &str) -> Self { self.headers.push((k.into(), v.into())); self }
    fn build(self) -> Request { Request { url: self.url, method: self.method, headers: self.headers } }
}

let req = RequestBuilder::new("https://api.example.com")
    .method("POST")
    .header("Authorization", "Bearer token")
    .build();
```

## Newtype Pattern
```rust
struct Email(String);
impl Email {
    fn new(s: &str) -> Result<Self, &str> {
        if s.contains('@') { Ok(Self(s.into())) } else { Err("invalid email") }
    }
}
```''')},
                    {"title":"Newtype Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"What is the newtype pattern?","options":[{"id":"a","label":"A struct with same fields"},{"id":"b","label":"Wrapping a single type for type safety"},{"id":"c","label":"Using generics"},{"id":"d","label":"Inheritance"}],"correct_option":"b","hints":["Wraps one type in a struct","Adds compile-time type safety"]}},
                ]},
                {"title":"RAII & Drop","order":1,"steps":[
                    {"title":"RAII","st":S.THEORY,"order":0,"xp":10,"cd":md('''# RAII (Resource Acquisition Is Initialization)

```rust
struct Database { connected: bool }

impl Database {
    fn connect(url: &str) -> Self { println!("Connecting..."); Self { connected: true } }
}

impl Drop for Database {
    fn drop(&mut self) { println!("Disconnecting"); self.connected = false; }
}

fn main() {
    let db = Database::connect("postgres://...");
    // use db
} // drop() called automatically
```

Key: resources freed when owner goes out of scope.
No garbage collector needed.
''')},
                    {"title":"RAII Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"When is Drop::drop() called?","options":[{"id":"a","label":"Manually by programmer"},{"id":"b","label":"When variable goes out of scope"},{"id":"c","label":"After main()"},{"id":"d","label":"Never"}],"correct_option":"b","hints":["RAII ties lifetime to scope","No manual memory management"]}},
                ]},
                {"title":"Type State","order":2,"steps":[
                    {"title":"Type State Pattern","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Type State Pattern

Enforce state transitions at compile time.

```rust
struct Locked; struct Unlocked;

struct Door<State = Locked> { _state: std::marker::PhantomData<State> }

impl Door<Locked> {
    fn new() -> Self { Self { _state: PhantomData } }
    fn unlock(self) -> Door<Unlocked> { Door { _state: PhantomData } }
}

impl Door<Unlocked> {
    fn open(self) { println!("Door opened!"); }
}

fn main() {
    let door = Door::new();
    // door.open(); // COMPILE ERROR
    let door = door.unlock();
    door.open(); // OK
}
```

Illegal states made unrepresentable at compile time.
''')},
                    {"title":"Type State Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"What does type state enforce?","options":[{"id":"a","label":"Runtime checks"},{"id":"b","label":"State at compile time"},{"id":"c","label":"Memory safety"},{"id":"d","label":"Thread safety"}],"correct_option":"b","hints":["Uses generics to track state","Illegal states caught at compile time"]}},
                ]},
            ]:
                s = Section(course_id=patterns.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
            logger.info("  Created Rust Common Patterns (3 sections)")

            # ── Add to Rust path ──
            rust_path = (await db.execute(select(LearningPath).where(LearningPath.language == "Rust"))).scalar_one_or_none()
            if rust_path and not (await db.execute(select(PathLevel).where(PathLevel.path_id == rust_path.id, PathLevel.course_id == patterns.id))).scalar_one_or_none():
                max_order_row = (await db.execute(select(PathLevel).where(PathLevel.path_id == rust_path.id).order_by(PathLevel.order.desc()).limit(1))).scalar_one_or_none()
                new_order = (max_order_row.order + 1) if max_order_row else 7
                db.add(PathLevel(path_id=rust_path.id, course_id=patterns.id, level_name="Common Patterns", order=new_order, required_progress_pct=75))
                logger.info("  Rust path + Common Patterns")

        await db.commit()
        logger.info("=" * 50)
        logger.info("RUST EXPANSION COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
