"""Seed Rust content with a complete learning path."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

S = StepType

def mk(title, md):
    return {"title": title, "st": S.THEORY, "order": 0, "xp": 10, "cd": {"body_markdown": md}}

def q(title, qst, opts, correct, hints=None, expl="", **kw):
    return {"title": title, "st": S.QUIZ, "order": kw.get("o", 1), "xp": kw.get("x", 20),
            "cd": {"question": qst, "options": opts, "correct_option": correct,
                   "hints": hints or [], "explanation": expl}}

def cd(title, inst, starter, solution, expected, **kw):
    return {"title": title, "st": S.CODE, "order": kw.get("o", 2), "xp": kw.get("x", 30),
            "cd": {"instruction": inst, "starter_code": starter, "solution": solution,
                   "compare_mode": "contains", "expected_output": expected,
                   "hints": kw.get("hints", [])}}

async def _seed(db, title, desc, lang, sections):
    if (await db.execute(select(Course).where(Course.title == title))).scalar_one_or_none():
        logger.info("  Exists: %s", title)
        return None
    c = Course(title=title, description=desc, language=lang)
    db.add(c); await db.flush(); await db.refresh(c)
    total = 0
    for sec in sections:
        s = Section(course_id=c.id, title=sec[0], order=sec[1])
        db.add(s); await db.flush(); await db.refresh(s)
        for st in sec[2]:
            db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"],
                        xp_reward=st["xp"], content_data=st["cd"])); total += 1
    await db.flush()
    logger.info("  Created: %s (%d steps)", title, total)
    return c

async def run():
    async with async_session_maker() as db:

        # ── Course 1: Rust Fundamentals ──
        fund = await _seed(db, "Rust Fundamentals",
            "Learn Rust from scratch: variables, types, ownership, borrowing, functions, and control flow.",
            "Rust", [
            ("Getting Started", 0, [
                mk("Hello, Rust!", """# Hello, Rust!

```rust
fn main() { println!("Hello, Rust!"); }

let x = 5;           // immutable
let mut y = 10;      // mutable
const MAX: u32 = 100; // constant
```
Rust is a systems language focused on safety, speed, and concurrency.
Every value has exactly one owner."""),
            ]),
            ("Variables & Types", 1, [
                mk("Data Types", """# Data Types in Rust

## Scalar Types
```rust
let a: i32 = -42;     // signed 32-bit
let b: u8 = 255;      // unsigned 8-bit
let pi: f64 = 3.14159; // 64-bit float
let ok: bool = true;   // boolean
let c: char = 'R';     // unicode character
```

## Compound Types
```rust
let pair: (i32, f64) = (42, 3.14); // tuple
let (x, y) = pair;                 // destructuring
println!("{} {}", pair.0, pair.1);

let nums: [i32; 3] = [1, 2, 3];   // array
let first = nums[0];
```"""),
                q("Types Quiz", "What type does `let x = 3.14;` infer?",
                  [{"id":"a","label":"f32"},{"id":"b","label":"f64"},{"id":"c","label":"float"},{"id":"d","label":"double"}],
                  "b", ["f64 is the default for float literals", "Use f32 suffix for 32-bit"]),
            ]),
            ("Ownership & Borrowing", 2, [
                mk("Ownership", """# Ownership Rules

1. Each value has **one** owner
2. Only **one** owner at a time
3. When owner goes out of scope, value is **dropped**

```rust
let s1 = String::from("hello");
let s2 = s1;           // s1 is MOVED to s2
// println!("{}", s1); // ERROR! s1 invalidated

let s3 = s2.clone();   // deep copy (OK)

// Borrowing
fn len(s: &String) -> usize { s.len() }
let s = String::from("hi");
let l = len(&s);        // borrow, not move
println!("{}", s);      // s still usable

// Mutable reference
let mut msg = String::from("hello");
let r = &mut msg;
r.push_str(" world");
```"""),
            ]),
            ("Functions & Control Flow", 3, [
                mk("Functions & Loops", """# Functions and Control Flow

```rust
fn add(a: i32, b: i32) -> i32 { a + b }  // expression return

let status = if age >= 18 { "adult" } else { "minor" };

match value {
    1 => println!("one"),
    2 | 3 => println!("two or three"),
    _ => println!("other"),
}

let result = loop {
    count += 1;
    if count == 10 { break count * 2; }
};

for i in 0..5 { println!("{}", i); }
```"""),
                q("Match Quiz", "What does `|` mean in a match arm?",
                  [{"id":"a","label":"Bitwise OR"},{"id":"b","label":"Multiple patterns"},{"id":"c","label":"Logical OR"},{"id":"d","label":"Type cast"}],
                  "b", ["| lets you match multiple values like 2 | 3"]),
                cd("FizzBuzz", "Write FizzBuzz using match on a tuple.",
                  "fn fizzbuzz(n: u32) -> String {\n    match (n % 3, n % 5) {\n        (0, 0) => String::from(\"FizzBuzz\"),\n        (0, _) => String::from(\"Fizz\"),\n        (_, 0) => String::from(\"Buzz\"),\n        _ => n.to_string(),\n    }\n}\nfn main() {\n    println!(\"{}\", fizzbuzz(15));\n    println!(\"{}\", fizzbuzz(7));\n}",
                  "fn fizzbuzz(n: u32) -> String {\n    match (n % 3, n % 5) {\n        (0, 0) => \"FizzBuzz\".to_string(),\n        (0, _) => \"Fizz\".to_string(),\n        (_, 0) => \"Buzz\".to_string(),\n        _ => n.to_string(),\n    }\n}\nfn main() {\n    println!(\"{}\", fizzbuzz(15));\n    println!(\"{}\", fizzbuzz(7));\n}",
                  "FizzBuzz", hints=["match (n % 3, n % 5)", "String::from() or to_string()"]),
            ]),
        ])

        # ── Course 2: Rust Structs & Enums ──
        structs = await _seed(db, "Rust Structs & Enums",
            "Master structs, enums, pattern matching, methods, and Option/Result types.",
            "Rust", [
            ("Structs", 0, [
                mk("Defining Structs", """# Structs

```rust
struct User { username: String, email: String, active: bool, age: u8 }
struct Color(u8, u8, u8);   // tuple struct
struct AlwaysEqual;          // unit struct

let user = User {
    username: String::from("alice"),
    email: String::from("alice@example.com"),
    active: true, age: 30,
};
let user2 = User { email: String::from("b@b.com"), ..user };

impl Rectangle {
    fn area(&self) -> u32 { self.width * self.height }
    fn square(size: u32) -> Self { Self { width: size, height: size } }
}
```"""),
                cd("Struct Area", "Define Circle with radius and area() method.",
                  "struct Circle { radius: f64 }\nimpl Circle {\n    fn area(&self) -> f64 { 3.14159 * self.radius * self.radius }\n}\nfn main() {\n    let c = Circle { radius: 5.0 };\n    println!(\"{:.2}\", c.area());\n}",
                  "struct Circle { radius: f64 }\nimpl Circle {\n    fn area(&self) -> f64 { 3.14159 * self.radius * self.radius }\n}\nfn main() { let c = Circle { radius: 5.0 }; println!(\"{:.2}\", c.area()); }",
                  "78.54", hints=["fn area(&self) -> f64", "pi * r^2"]),
            ]),
            ("Enums & Pattern Matching", 1, [
                mk("Enums", """# Enums & Pattern Matching

```rust
enum Message { Quit, Move { x: i32, y: i32 }, Write(String), ChangeColor(i32,i32,i32) }

impl Message {
    fn call(&self) {
        match self {
            Message::Quit => println!("Quit"),
            Message::Move { x, y } => println!("({}, {})", x, y),
            Message::Write(text) => println!("{}", text),
            _ => println!("Other"),
        }
    }
}

// Option (replaces null)
enum Option<T> { None, Some(T) }

fn divide(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 { None } else { Some(a / b) }
}

// Result
enum Result<T, E> { Ok(T), Err(E) }
```"""),
                q("Option Quiz", "What does Option::None represent?",
                  [{"id":"a","label":"A null pointer"},{"id":"b","label":"No value"},{"id":"c","label":"Zero"},{"id":"d","label":"Error"}],
                  "b", ["Option replaces null", "Forces handling both Some and None"]),
            ]),
            ("if let & while let", 2, [
                mk("Concise Patterns", """# if let & while let

```rust
if let Some(value) = config_value {
    println!("{}", value);
} else {
    println!("No value");
}

let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() {
    println!("{}", top);  // 3, 2, 1
}
```"""),
                q("if let Quiz", "What does if let do?",
                  [{"id":"a","label":"One pattern concisely"},{"id":"b","label":"Create variable"},{"id":"c","label":"Loop forever"},{"id":"d","label":"Return early"}],
                  "a", ["Syntactic sugar for single-arm match"]),
            ]),
        ])

        # ── Course 3: Rust Collections & Error Handling ──
        collections = await _seed(db, "Rust Collections & Error Handling",
            "Vectors, Strings, HashMaps, error handling with ?, and Result combinators.",
            "Rust", [
            ("Collections", 0, [
                mk("Vectors, Strings, HashMaps", """# Collections

## Vec
```rust
let mut v: Vec<i32> = Vec::new();
v.push(1); v.push(2);
let v2 = vec![1, 2, 3];
let third = &v[2];        // may panic
let third = v.get(2);     // Option<&T>
for i in &v { println!("{}", i); }
```

## String
```rust
let mut s = String::from("hello");
s.push(' '); s.push_str("world");
let g = format!("Hello, {}!", name);
```

## HashMap
```rust
use std::collections::HashMap;
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
scores.entry(String::from("Blue")).or_insert(0);
```"""),
                cd("Word Counter", "Count word frequencies using HashMap.",
                  "use std::collections::HashMap;\nfn main() {\n    let text = \"the cat and the dog and the bird\";\n    let mut counts: HashMap<&str, u32> = HashMap::new();\n    for word in text.split_whitespace() {\n        *counts.entry(word).or_insert(0) += 1;\n    }\n    println!(\"{}\", counts.get(\"the\").unwrap());\n}",
                  "use std::collections::HashMap;\nfn main() {\n    let text = \"the cat and the dog and the bird\";\n    let mut counts: HashMap<&str, u32> = HashMap::new();\n    for word in text.split_whitespace() {\n        *counts.entry(word).or_insert(0) += 1;\n    }\n    println!(\"{}\", counts.get(\"the\").unwrap());\n}",
                  "3", hints=["entry().or_insert(0)", "Dereference with *"]),
            ]),
            ("Error Handling", 1, [
                mk("Result & ? Operator", """# Error Handling

```rust
fn read_username(path: &str) -> Result<String, io::Error> {
    let mut f = File::open(path)?;     // early return on Err
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s.trim().to_string())
}

// Combinators
let r: Result<i32, &str> = Ok(10);
let d = r.map(|x| x * 2);              // Ok(20)
let v = r.unwrap_or(0);                // 10 or 0 on Err
let opt = Some(5).map(|x| x * 2);      // Some(10)
```"""),
                q("? Operator Quiz", "When does ? return early?",
                  [{"id":"a","label":"On Ok"},{"id":"b","label":"On Err"},{"id":"c","label":"Both"},{"id":"d","label":"Never"}],
                  "b", ["? propagates errors", "Unwraps Ok or returns Err"]),
                cd("Safe Division", "safe_divide(a,b) -> Result<f64, String>",
                  "fn safe_divide(a: f64, b: f64) -> Result<f64, String> {\n    if b == 0.0 { Err(\"division by zero\".into()) }\n    else { Ok(a / b) }\n}\nfn main() -> Result<(), String> {\n    println!(\"{:.1}\", safe_divide(10.0, 2.0)?);\n    Ok(())\n}",
                  "fn safe_divide(a: f64, b: f64) -> Result<f64, String> {\n    if b == 0.0 { Err(\"division by zero\".into()) }\n    else { Ok(a / b) }\n}\nfn main() -> Result<(), String> {\n    println!(\"{:.1}\", safe_divide(10.0, 2.0)?);\n    Ok(())\n}",
                  "5.0", hints=["Err on zero", "Propagate with ?"]),
            ]),
        ])

        # ── Course 4: Rust Traits & Generics ──
        traits = await _seed(db, "Rust Traits & Generics",
            "Traits, generics, lifetimes, closures, and iterators.",
            "Rust", [
            ("Generics & Traits", 0, [
                mk("Generics and Traits", """# Generics & Traits

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut l = &list[0];
    for item in list { if item > l { l = item; } }
    l
}

trait Summary { fn summarize(&self) -> String; }

impl Summary for Article {
    fn summarize(&self) -> String { format!(\"{} by {}\", self.headline, self.author) }
}

fn notify(item: &impl Summary) { println!(\"{}\", item.summarize()); }
```"""),
                q("Trait Quiz", "Keyword to define shared behavior?",
                  [{"id":"a","label":"interface"},{"id":"b","label":"trait"},{"id":"c","label":"abstract"},{"id":"d","label":"protocol"}],
                  "b"),
            ]),
            ("Lifetimes", 1, [
                mk("Lifetimes", """# Lifetimes

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

struct Excerpt<'a> { part: &'a str }
```"""),
                q("Lifetime Quiz", "What do lifetimes prevent?",
                  [{"id":"a","label":"Memory leaks"},{"id":"b","label":"Dangling references"},{"id":"c","label":"Stack overflow"},{"id":"d","label":"Deadlocks"}],
                  "b"),
            ]),
            ("Closures & Iterators", 2, [
                mk("Closures and Iterators", """# Closures & Iterators

```rust
let add = |a, b| a + b;

let nums = vec![1, 2, 3, 4, 5];
let evens_squared: Vec<i32> = nums.iter()
    .filter(|&&x| x % 2 == 0)
    .map(|&x| x * x)
    .collect();

let sum: i32 = nums.iter().fold(0, |acc, x| acc + x);
let has_even = nums.iter().any(|&x| x % 2 == 0);
```"""),
                cd("Iterator Chain", "Filter > 5, double them, collect.",
                  "fn main() {\n    let nums = vec![1, 3, 7, 2, 9, 4, 11];\n    let result: Vec<i32> = nums.iter().filter(|&&x| x > 5).map(|&x| x * 2).collect();\n    println!(\"{:?}\", result);\n}",
                  "fn main() {\n    let nums = vec![1, 3, 7, 2, 9, 4, 11];\n    let result: Vec<i32> = nums.iter().filter(|&&x| x > 5).map(|&x| x * 2).collect();\n    println!(\"{:?}\", result);\n}",
                  "[14, 18, 22]", hints=["filter keeps elements", "map transforms"]),
            ]),
        ])

        # ── Course 5: Rust Concurrency & Memory ──
        concurrency = await _seed(db, "Rust Concurrency & Memory",
            "Threads, channels, Arc/Mutex, Send/Sync, async/await, smart pointers.",
            "Rust", [
            ("Threads & Channels", 0, [
                mk("Threads and Channels", """# Threads & Channels

```rust
use std::thread;
let handle = thread::spawn(|| { for i in 1..10 { println!(\"{}\", i); } });
handle.join().unwrap();

// mpsc channel
let (tx, rx) = std::sync::mpsc::channel();
thread::spawn(move || { tx.send(42).unwrap(); });
let received = rx.recv().unwrap();
```"""),
                mk("Arc & Mutex", """# Arc & Mutex

```rust
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];
for _ in 0..10 {
    let c = Arc::clone(&counter);
    handles.push(thread::spawn(move || {
        let mut num = c.lock().unwrap();
        *num += 1;
    }));
}
for h in handles { h.join().unwrap(); }
println!(\"{}\", *counter.lock().unwrap());  // 10
```

- **Send**: can transfer across threads
- **Sync**: can share via reference
- Rc: not Send. Arc: Send + Sync.
"""),
                q("Arc vs Rc", "Difference between Rc and Arc?",
                  [{"id":"a","label":"Arc is async, Rc sync"},{"id":"b","label":"Arc uses atomics"},{"id":"c","label":"Rc faster but not thread-safe"},{"id":"d","label":"Both B and C"}],
                  "d"),
            ]),
            ("Async & Smart Pointers", 1, [
                mk("Async/Await", """# Async/Await

```rust
#[tokio::main]
async fn main() {
    let data = fetch().await;
    println!(\"{}\", data);
}
async fn fetch() -> String { \"data\".into() }

// tokio::join runs concurrently
let (a, b) = tokio::join!(task1(), task2());
```"""),
                mk("Box, Rc, RefCell", """# Smart Pointers

```rust
// Box: heap allocation
enum List { Cons(i32, Box<List>), Nil }

// Rc: reference counted (single-threaded)
let a = Rc::new(5); let b = Rc::clone(&a);

// RefCell: interior mutability
let data = RefCell::new(5);
*data.borrow_mut() = 10;
```

- Use Box for recursive types and trait objects
- Use Rc for shared ownership (single thread)
- Use RefCell for runtime borrow checking
"""),
                q("Box Quiz", "When to use Box<T>?",
                  [{"id":"a","label":"All heap"},{"id":"b","label":"Recursive types & trait objects"},{"id":"c","label":"Threads"},{"id":"d","label":"Strings"}],
                  "b"),
            ]),
        ])

        # ── Course 6: Rust Testing & Modules ──
        testing = await _seed(db, "Rust Testing & Modules",
            "Unit tests, integration tests, modules, crates, packages, Cargo.",
            "Rust", [
            ("Testing", 0, [
                mk("Unit & Integration Tests", """# Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_add() { assert_eq!(add(2, 3), 5); }
    #[test] #[should_panic] fn test_div() { divide(10, 0); }
}
```

- Unit tests: in the same file with #[cfg(test)]
- Integration tests: in tests/ directory
- Run: cargo test
"""),
                cd("Write a Test", "Write is_even and a test.",
                  "pub fn is_even(n: i32) -> bool { n % 2 == 0 }\nfn main() { println!(\"{}\", is_even(4)); }\n#[cfg(test)]\nmod tests {\n    use super::*;\n    #[test] fn test_even() { assert!(is_even(4)); }\n    #[test] fn test_odd() { assert!(!is_even(7)); }\n}",
                  "pub fn is_even(n: i32) -> bool { n % 2 == 0 }\nfn main() { println!(\"{}\", is_even(4)); }\n#[cfg(test)]\nmod tests {\n    use super::*;\n    #[test] fn test_even() { assert!(is_even(4)); }\n    #[test] fn test_odd() { assert!(!is_even(7)); }\n}",
                  "true", hints=["#[test] marks test fn", "assert!() / assert_eq!()"]),
            ]),
            ("Modules & Crates", 1, [
                mk("Module System", """# Modules & Crates

```rust
// lib.rs
pub mod networking {
    pub mod http {
        pub fn get(url: &str) -> String { format!(\"GET {}\", url) }
    }
}

// main.rs
use my_crate::networking::http;
```

Visibility: pub, pub(crate), pub(super), private (default).
Cargo.toml controls package metadata and dependencies.
"""),
            ]),
        ])

        # ── Course 7: Rust Standard Library ──
        std_lib = await _seed(db, "Rust Standard Library",
            "File I/O, environment, args, serde serialization.",
            "Rust", [
            ("File I/O & Environment", 0, [
                mk("File I/O & Env", """# File I/O & Environment

```rust
use std::fs;
let content = fs::read_to_string(\"hello.txt\").expect(\"read failed\");
fs::write(\"out.txt\", \"data\").expect(\"write failed\");

let args: Vec<String> = std::env::args().collect();
let path = std::env::var(\"PATH\").unwrap_or_default();
```"""),
                cd("Line Count", "Read filename from args, print line count.",
                  "use std::env;\nuse std::fs;\nfn main() {\n    let args: Vec<String> = env::args().collect();\n    if args.len() < 2 { println!(\"0\"); return; }\n    let content = fs::read_to_string(&args[1]).unwrap_or_default();\n    println!(\"{}\", content.lines().count());\n}",
                  "use std::env;\nuse std::fs;\nfn main() {\n    let args: Vec<String> = env::args().collect();\n    if args.len() < 2 { println!(\"0\"); return; }\n    let content = fs::read_to_string(&args[1]).unwrap_or_default();\n    println!(\"{}\", content.lines().count());\n}",
                  "0", hints=["env::args()", "unwrap_or_default()"]),
            ]),
            ("Serialization", 1, [
                mk("Serde", """# Serialization

```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct User { id: u32, name: String, email: String }

let user = User { id: 1, name: \"Alice\".into(), email: \"a@b.com\".into() };
let json = serde_json::to_string_pretty(&user)?;
let u2: User = serde_json::from_str(&json)?;
```

- serde_json, serde_yaml, toml (behind feature flags)
- #[serde(rename = \"field\")], #[serde(skip_serializing_if = \"Option::is_none\")]
"""),
            ]),
        ])

        # ── Create Rust Learning Path ──
        rust_path = (await db.execute(select(LearningPath).where(LearningPath.language == "Rust"))).scalar_one_or_none()
        if not rust_path:
            rust_path = LearningPath(title="Rust Developer Roadmap", description="Master Rust: from fundamentals to systems programming.", language="Rust", icon="RS")
            db.add(rust_path)
            await db.flush()
            await db.refresh(rust_path)
            logger.info("Created Rust Learning Path")
        else:
            logger.info("Rust Learning Path already exists")

        levels_config = [
            (fund, "Rust Fundamentals", 75),
            (structs, "Structures & Enums", 75),
            (collections, "Collections & Error Handling", 75),
            (traits, "Traits & Generics", 75),
            (concurrency, "Concurrency & Memory", 75),
            (testing, "Testing & Modules", 75),
            (std_lib, "Rust Standard Library", 75),
        ]

        existing = {(r.course_id) for r in (await db.execute(select(PathLevel).where(PathLevel.path_id == rust_path.id))).scalars().all()}
        order = 0
        for course_obj, name, req in levels_config:
            if course_obj and course_obj.id not in existing:
                order += 1
                db.add(PathLevel(path_id=rust_path.id, course_id=course_obj.id, level_name=name, order=order, required_progress_pct=req))
                logger.info("  Rust path + Level %d: %s", order, name)

        await db.commit()
        logger.info("=" * 50)
        logger.info("RUST SEEDING COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
