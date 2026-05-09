"""Add final Rust steps to reach 50+."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)
S = StepType

def md(s):
    return {"body_markdown": s}

async def run():
    async with async_session_maker() as db:

        # ── Add to Rust Standard Library ──
        std = (await db.execute(select(Course).where(Course.title == "Rust Standard Library"))).scalar_one_or_none()
        if std:
            last = (await db.execute(select(Section).where(Section.course_id == std.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 10
            for sec in [
                {"title":"Error Handling & Logging","order":o,"steps":[
                    {"title":"Error Types & Logging","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Error Types & Logging

## Custom Error Types
```rust
use std::fmt;

#[derive(Debug)]
enum AppError {
    NotFound(String),
    PermissionDenied,
    IoError(std::io::Error),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            AppError::NotFound(s) => write!(f, "Not found: {}", s),
            AppError::PermissionDenied => write!(f, "Permission denied"),
            AppError::IoError(e) => write!(f, "IO error: {}", e),
        }
    }
}

impl std::error::Error for AppError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            AppError::IoError(e) => Some(e),
            _ => None,
        }
    }
}

// Convert io::Error into our custom error
impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self { AppError::IoError(e) }
}
```

## Logging
```rust
// Cargo.toml: log = "0.4", env_logger = "0.10"
use log::{info, warn, error};

fn main() {
    env_logger::init();
    info!("Application started");
    warn!("Low disk space");
    error!("Failed to connect");
}
// Run: RUST_LOG=info cargo run
```''')},
                    {"title":"Custom Error Quiz","st":S.QUIZ,"order":1,"xp":20,"cd":{"question":"Which trait must custom errors implement for the ? operator?","options":[{"id":"a","label":"Debug"},{"id":"b","label":"Display + Error"},{"id":"c","label":"Clone"},{"id":"d","label":"Default"}],"correct_option":"b","hints":["Display for user-facing messages", "Error trait for interoperability with ? and source()"]}},
                    {"title":"Custom Error","st":S.CODE,"order":2,"xp":35,"cd":{"instruction":"Create a function parse_int that returns Result<i32, String>. Parse a &str to i32, return Err if invalid.",
                        "starter_code":"fn parse_int(s: &str) -> Result<i32, String> {\n    s.trim().parse::<i32>().map_err(|e| format!(\"Invalid int: {}\", e))\n}\n\nfn main() {\n    match parse_int(\"42\") {\n        Ok(n) => println!(\"{}\", n + 1),\n        Err(e) => println!(\"Error: {}\", e),\n    }\n}",
                        "solution":"fn parse_int(s: &str) -> Result<i32, String> {\n    s.trim().parse::<i32>().map_err(|e| format!(\"Invalid int: {}\", e))\n}\nfn main() {\n    match parse_int(\"42\") {\n        Ok(n) => println!(\"{}\", n + 1),\n        Err(e) => println!(\"Error: {}\", e),\n    }\n}",
                        "compare_mode":"contains","expected_output":"43",
                        "hints":["parse::<i32>() returns Result", "map_err converts error types"]}},
                ]},
                {"title":"Collections & Iterators","order":o+1,"steps":[
                    {"title":"Advanced Collections","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Advanced Collections

## BTreeMap (ordered)
```rust
use std::collections::BTreeMap;
let mut map = BTreeMap::new();
map.insert("c", 3);
map.insert("a", 1);
map.insert("b", 2);
for (k, v) in &map { println!("{}: {}", k, v); }
// a: 1, b: 2, c: 3 (sorted by key)
```

## HashSet / BTreeSet
```rust
use std::collections::HashSet;
let mut set = HashSet::new();
set.insert(1); set.insert(2); set.insert(1);
println!("{:?}", set);  // {1, 2} (no duplicates)
```

## VecDeque (double-ended queue)
```rust
use std::collections::VecDeque;
let mut deque: VecDeque<i32> = VecDeque::new();
deque.push_front(1);
deque.push_back(2);
deque.push_front(0);
println!("{:?}", deque);  // [0, 1, 2]
```

## BinaryHeap (max-heap)
```rust
use std::collections::BinaryHeap;
let mut heap = BinaryHeap::new();
heap.push(3); heap.push(1); heap.push(5);
println!("{}", heap.pop().unwrap());  // 5 (largest)
```''')},
                ]},
            ]:
                s = Section(course_id=std.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
                logger.info("  StdLib + %s (%d steps)", sec["title"], len(sec["steps"]))

        # ── Add to Rust Concurrency ──
        conc = (await db.execute(select(Course).where(Course.title == "Rust Concurrency & Memory"))).scalar_one_or_none()
        if conc:
            last = (await db.execute(select(Section).where(Section.course_id == conc.id).order_by(Section.order.desc()).limit(1))).scalar_one_or_none()
            o = (last.order + 1) if last else 10
            for sec in [
                {"title":"Concurrency Patterns","order":o,"steps":[
                    {"title":"Producer-Consumer","st":S.THEORY,"order":0,"xp":10,"cd":md('''# Concurrency Patterns

## Producer-Consumer with channels
```rust
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = mpsc::channel();
    let tx2 = tx.clone();

    // Producer 1
    thread::spawn(move || {
        for i in 1..=5 {
            tx.send(format!("Producer A: {}", i)).unwrap();
            thread::sleep(Duration::from_millis(100));
        }
    });

    // Producer 2
    thread::spawn(move || {
        for i in 1..=5 {
            tx2.send(format!("Producer B: {}", i)).unwrap();
            thread::sleep(Duration::from_millis(150));
        }
    });

    // Consumer
    for received in rx {
        println!("{}", received);
    }
}
```

## Fan-out / Fan-in
- Multiple workers read from one channel (fan-out)
- Multiple producers write to one channel (fan-in)
- Use Arc for shared state between workers
''')},
                ]},
            ]:
                s = Section(course_id=conc.id, title=sec["title"], order=sec["order"]); db.add(s); await db.flush(); await db.refresh(s)
                for st in sec["steps"]:
                    db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"]))
                logger.info("  Concurrency + %s (%d steps)", sec["title"], len(sec["steps"]))

        await db.commit()
        logger.info("=" * 50)
        logger.info("RUST FINAL EXPANSION COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
