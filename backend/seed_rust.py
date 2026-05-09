"""Seed Rust content with a complete learning path."""

import asyncio, logging
from sqlalchemy import select
from app.core.database import async_session_maker
from app.modules.courses.models import Course, LearningPath, PathLevel, Section, Step, StepType

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

STEP = StepType

def t(title, **kw):
    return {"title": title, "st": kw.get("st", STEP.THEORY), "order": kw.get("order", 0),
            "xp": kw.get("xp", 10), "cd": kw.get("cd", {})}

def quiz(title, question, options, correct, hints=None, explanation="", **kw):
    return t(title, st=STEP.QUIZ, order=kw.get("order", 1), xp=kw.get("xp", 20),
        cd={"question": question, "options": options, "correct_option": correct,
            "hints": hints or [], "explanation": explanation})

def code(title, instruction, starter, solution, expected, **kw):
    return t(title, st=STEP.CODE, order=kw.get("order", 2), xp=kw.get("xp", 30),
        cd={"instruction": instruction, "starter_code": starter, "solution": solution,
            "compare_mode": kw.get("mode", "contains"), "expected_output": expected,
            "hints": kw.get("hints", [])})

M = "body_markdown"

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
            db.add(Step(section_id=s.id, title=st["title"], step_type=st["st"], order=st["order"], xp_reward=st["xp"], content_data=st["cd"])); total += 1
    await db.flush()
    logger.info("  Created: %s (%d steps)", title, total)
    return c

async def run():
    async with async_session_maker() as db:

        # ── Course 1: Rust Fundamentals ──
        fund = await _seed(db, "Rust Fundamentals",
            "Learn Rust from scratch: variables, types, ownership, borrowing, functions, and control flow.",
            "Rust", [
            {"title":"Getting Started","order":0,"steps":[
                t("Hello, Rust!",
                  cd={M:r"""# Hello, Rust!

```rust
fn main() {
    println!("Hello, Rust!");
}

// Variables (immutable by default)
let x = 5;
let y: i32 = 10;

// Mutable variables
let mut z = 15;
z += 5;  // works because z is mut

// Constants
const MAX_USERS: u32 = 1000;
```
Rust is a systems language focused on safety, speed, and concurrency.
Every value in Rust has an *owner*, and there can only be one owner at a time.
"""})]},

            {"title":"Variables & Types","order":1,"steps":[
                t("Data Types",
                  cd={M:r"""# Data Types in Rust

## Scalar Types
```rust
// Integers: i8, i16, i32, i64, u8, u16, u32, u64
let a: i32 = -42;
let b: u8 = 255;

// Floats: f32, f64
let pi: f64 = 3.14159;

// Boolean
let is_ready: bool = true;

// Character (4 bytes, Unicode)
let letter: char = 'R';
let emoji: char = '\u{1F980}';  // Rust's crab
```

## Compound Types
```rust
// Tuple (fixed length, mixed types)
let pair: (i32, f64) = (42, 3.14);
let (x, y) = pair;  // destructuring
println!("{} {}", pair.0, pair.1);  // index access

// Array (fixed length, same type)
let nums: [i32; 5] = [1, 2, 3, 4, 5];
let first = nums[0];
```"}),
                quiz("Types Quiz", "What is the type of `let x = 3.14;` in Rust?",
                     [{"id":"a","label":"f32"},{"id":"b","label":"f64"},{"id":"c","label":"float"},{"id":"d","label":"double"}],
                     "b", ["Rust infers f64 by default for floats", "f32 must be explicit"]),
            ]},

            {"title":"Ownership & Borrowing","order":2,"steps":[
                t("Ownership",
                  cd={M:r"""# Ownership

Three rules:
1. Each value has an **owner**
2. Only **one** owner at a time
3. When owner goes out of scope, value is **dropped**

```rust
let s1 = String::from("hello");
let s2 = s1;  // s1 is MOVED to s2
// println!("{}", s1);  // ERROR! s1 no longer valid

let s3 = s2.clone();  // deep copy (expensive)
println!("{}", s2);   // OK, s2 still valid

// Scope
{
    let inner = String::from("inside");
} // inner is dropped here
```

## Borrowing (& references)
```rust
fn calculate_length(s: &String) -> usize {  // borrow
    s.len()
}

let s1 = String::from("hello");
let len = calculate_length(&s1);  // pass reference
println!("'{}' has length {}", s1, len);  // s1 still usable
```

## Mutable References
```rust
let mut s = String::from("hello");
change(&mut s);
println!("{}", s);  // "hello world"

fn change(s: &mut String) {
    s.push_str(" world");
}
```
One big restriction: you can have **either** one mutable reference **or** any number of immutable references at a time.
"""})]},

            {"title":"Functions & Control Flow","order":3,"steps":[
                t("Functions & Loops",
                  cd={M:r"""# Functions & Control Flow

## Functions
```rust
fn add(a: i32, b: i32) -> i32 {
    a + b  // no semicolon = return value (expression)
}

fn greet(name: &str) -> String {
    return format!("Hello, {}!", name);  // explicit return
}

// Function pointer
let math_op: fn(i32, i32) -> i32 = add;
println!("{}", math_op(5, 3));  // 8
```

## Control Flow
```rust
// if / else if / else
let age = 18;
let status = if age >= 18 { "adult" } else { "minor" };

// match (powerful!)
let value = 3;
match value {
    1 => println!("one"),
    2 | 3 => println!("two or three"),
    4..=10 => println!("four to ten"),
    _ => println!("something else"),
}

// loops
let mut count = 0;
let result = loop {
    count += 1;
    if count == 10 { break count * 2; }
};
println!("result = {}", result);  // 20

// for range
for i in 0..5 { println!("{}", i); }  // 0,1,2,3,4
```"}),
                quiz("Match Quiz", "What does `|` mean in a match arm?",
                     [{"id":"a","label":"Bitwise OR"},{"id":"b","label":"Multiple patterns"},{"id":"c","label":"Logical OR"},{"id":"d","label":"Type cast"}],
                     "b", ["`|` lets you match multiple values", "e.g. `1 | 2 => ...`"]),
                code("FizzBuzz", "Write a FizzBuzz function using match. Return the string representation for numbers, 'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both.",
r"""fn fizzbuzz(n: u32) -> String {
    match (n % 3, n % 5) {
        (0, 0) => String::from("FizzBuzz"),
        (0, _) => String::from("Fizz"),
        (_, 0) => String::from("Buzz"),
        _ => n.to_string(),
    }
}

fn main() {
    println!("{}", fizzbuzz(15));
    println!("{}", fizzbuzz(3));
    println!("{}", fizzbuzz(5));
    println!("{}", fizzbuzz(7));
}""",
r"""fn fizzbuzz(n: u32) -> String {
    match (n % 3, n % 5) {
        (0, 0) => String::from("FizzBuzz"),
        (0, _) => String::from("Fizz"),
        (_, 0) => String::from("Buzz"),
        _ => n.to_string(),
    }
}
fn main() {
    println!("{}", fizzbuzz(15));
    println!("{}", fizzbuzz(3));
    println!("{}", fizzbuzz(5));
    println!("{}", fizzbuzz(7));
}""",
"FizzBuzz",
                    hints=["Use match on a tuple (n % 3, n % 5)", "Return String::from() or n.to_string()"]),
            ]},
        ])

        # ── Course 2: Rust Structs & Enums ──
        structs = await _seed(db, "Rust Structs & Enums",
            "Master structs, enums, pattern matching, methods, and Option/Result types.",
            "Rust", [
            {"title":"Structs","order":0,"steps":[
                t("Defining Structs",
                  cd={M:r"""# Structs

```rust
// Named struct
struct User {
    username: String,
    email: String,
    active: bool,
    age: u8,
}

// Tuple struct
struct Color(u8, u8, u8);

// Unit struct (no fields)
struct AlwaysEqual;

fn main() {
    let user = User {
        username: String::from("alice"),
        email: String::from("alice@example.com"),
        active: true,
        age: 30,
    };
    println!("{}", user.username);

    let black = Color(0, 0, 0);
    println!("R: {}", black.0);

    let _unit = AlwaysEqual;

    // Struct update syntax
    let user2 = User {
        email: String::from("new@example.com"),
        ..user  // remaining fields from user
    };
}
```"}),
                t("Methods & impl",
                  cd={M:r"""# Methods with impl

```rust
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    // Method (takes &self)
    fn area(&self) -> u32 {
        self.width * self.height
    }

    // Method with parameters
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    // Associated function (no self) - like static
    fn square(size: u32) -> Rectangle {
        Rectangle { width: size, height: size }
    }
}

fn main() {
    let rect = Rectangle { width: 30, height: 50 };
    println!("Area: {}", rect.area());  // 1500

    let sq = Rectangle::square(10);  // associated function
}
```"}),
                code("Struct Area", "Define a struct Circle with radius, implement a method area() that returns f64 using 3.14159 as PI.",
r"""struct Circle {
    radius: f64,
}

impl Circle {
    fn area(&self) -> f64 {
        3.14159 * self.radius * self.radius
    }
}

fn main() {
    let c = Circle { radius: 5.0 };
    println!("{:.2}", c.area());
}""",
r"""struct Circle {
    radius: f64,
}
impl Circle {
    fn area(&self) -> f64 {
        3.14159 * self.radius * self.radius
    }
}
fn main() {
    let c = Circle { radius: 5.0 };
    println!("{:.2}", c.area());
}""",
"78.54",
                    hints=["impl Circle { fn area(&self) -> f64 { ... } }", "Area = pi * r^2"]),
            ]},

            {"title":"Enums & Pattern Matching","order":1,"steps":[
                t("Enums",
                  cd={M:r"""# Enums & Pattern Matching

```rust
enum Message {
    Quit,
    Move { x: i32, y: i32 },  // struct variant
    Write(String),            // tuple variant
    ChangeColor(i32, i32, i32),
}

impl Message {
    fn call(&self) {
        match self {
            Message::Quit => println!("Quit"),
            Message::Move { x, y } => println!("Move to ({}, {})", x, y),
            Message::Write(text) => println!("{}", text),
            Message::ChangeColor(r, g, b) => println!("RGB({},{},{})", r, g, b),
        }
    }
}

let msg = Message::Write(String::from("hello"));
msg.call();
```

## Option\<T\> (no more null!)
```rust
enum Option<T> {
    None,
    Some(T),
}

fn divide(a: f64, b: f64) -> Option<f64> {
    if b == 0.0 { None } else { Some(a / b) }
}

match divide(10.0, 2.0) {
    Some(result) => println!("Result: {}", result),
    None => println!("Cannot divide by zero"),
}
```

## Result\<T, E\>
```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}

fn read_file(path: &str) -> Result<String, std::io::Error> {
    std::fs::read_to_string(path)
}
```"}),
                quiz("Option Quiz", "What does `Option::None` represent?",
                     [{"id":"a","label":"A null pointer"},{"id":"b","label":"The absence of a value"},{"id":"c","label":"A zero value"},{"id":"d","label":"An error"}],
                     "b", ["Option replaces null in Rust", "It forces you to handle both cases"]),
            ]},

            {"title":"if let & while let","order":2,"steps":[
                t("Concise Patterns",
                  cd={M:r"""# if let & while let

```rust
// Instead of:
match config_value {
    Some(value) => println!("{}", value),
    None => (),
}

// You can write:
if let Some(value) = config_value {
    println!("{}", value);
}
// The `else` block runs when the pattern doesn't match
if let Some(value) = risky_value {
    println!("Got: {}", value);
} else {
    println!("Got nothing");
}

// while let (useful for iterators)
let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() {
    println!("{}", top);  // 3, 2, 1
}
```"}),
                quiz("if let Quiz", "What does `if let` allow you to do?",
                     [{"id":"a","label":"Only match one pattern concisely"},{"id":"b","label":"Create a new variable"},{"id":"c","label":"Loop indefinitely"},{"id":"d","label":"Return early from a function"}],
                     "a", ["if let is syntactic sugar for a single-arm match", "Use when you only care about one variant"]),
            ]},
        ])

        # ── Course 3: Rust Collections & Error Handling ──
        collections = await _seed(db, "Rust Collections & Error Handling",
            "Vectors, Strings, HashMaps, error handling with ? operator, and Result combinators.",
            "Rust", [
            {"title":"Collections","order":0,"steps":[
                t("Vectors & Strings",
                  cd={M:r"""# Collections

## Vec\<T\>
```rust
let mut v: Vec<i32> = Vec::new();
v.push(1);
v.push(2);
v.push(3);

// Macro
let v2 = vec![1, 2, 3];

// Access
let third = &v[2];       // panics if out of bounds
let third = v.get(2);    // returns Option<&T>

// Iterate
for i in &v { println!("{}", i); }

// Pop
let last = v.pop();  // Some(3)
```

## String (not &str)
```rust
let mut s = String::from("hello");
s.push(' ');
s.push_str("world");
s += "!";

// Format
let name = "Rust";
let greeting = format!("Hello, {}!", name);  // "Hello, Rust!"

// Indexing (String does NOT support [i])
// Use chars() or bytes()
for c in "hello".chars() { println!("{}", c); }
```

## HashMap\<K, V\>
```rust
use std::collections::HashMap;

let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
scores.insert(String::from("Red"), 50);

let team = String::from("Blue");
if let Some(score) = scores.get(&team) {
    println!("{}: {}", score, team);
}

// Entry API
scores.entry(String::from("Blue")).or_insert(0);
```"}),
                code("HashMap Counter", "Count word frequencies in a sentence using a HashMap.",
r"""use std::collections::HashMap;

fn main() {
    let text = "the cat and the dog and the bird";
    let mut counts: HashMap<&str, u32> = HashMap::new();

    for word in text.split_whitespace() {
        *counts.entry(word).or_insert(0) += 1;
    }

    let result = counts.get("the").unwrap();
    println!("{}", result);
}""",
r"""use std::collections::HashMap;
fn main() {
    let text = "the cat and the dog and the bird";
    let mut counts: HashMap<&str, u32> = HashMap::new();
    for word in text.split_whitespace() {
        *counts.entry(word).or_insert(0) += 1;
    }
    let result = counts.get("the").unwrap();
    println!("{}", result);
}""",
"3",
                    hints=["Use entry().or_insert()", "Dereference the returned &mut V with *"]),
            ]},

            {"title":"Error Handling","order":1,"steps":[
                t("Result & ?",
                  cd={M:r"""# Error Handling with Result

```rust
use std::fs::File;
use std::io::{self, Read};

// Verbose match
fn read_username_verbose(path: &str) -> Result<String, io::Error> {
    let file_result = File::open(path);
    let mut file = match file_result {
        Ok(f) => f,
        Err(e) => return Err(e),
    };
    let mut username = String::new();
    match file.read_to_string(&mut username) {
        Ok(_) => Ok(username.trim().to_string()),
        Err(e) => Err(e),
    }
}

// The ? operator (magic!)
fn read_username(path: &str) -> Result<String, io::Error> {
    let mut file = File::open(path)?;  // returns Err early if failed
    let mut username = String::new();
    file.read_to_string(&mut username)?;
    Ok(username.trim().to_string())
}

// Chaining ?
fn read_username_short(path: &str) -> Result<String, io::Error> {
    let mut username = String::new();
    File::open(path)?.read_to_string(&mut username)?;
    Ok(username.trim().to_string())
}
```

## Combinators
```rust
let result: Result<i32, &str> = Ok(10);

// map: transforms Ok value
let doubled = result.map(|x| x * 2);  // Ok(20)

// and_then: chains another Result-returning fn
let chained = result.and_then(|x| {
    if x > 5 { Ok(x * 2) } else { Err("too small") }
});

// unwrap_or: default on Err
let value = result.unwrap_or(0);  // 10 (or 0 if Err)

// combinators on Option
let opt = Some(5);
let doubled = opt.map(|x| x * 2);  // Some(10)
```"}),
                quiz("? Operator Quiz", "When does the ? operator return early?",
                     [{"id":"a","label":"When the value is Ok"},{"id":"b","label":"When the value is Err"},{"id":"c","label":"Both cases"},{"id":"d","label":"Never"}],
                     "b", ["? propagates errors", "It unwraps Ok or returns Err from the function"]),
                code("Safe Division", "Write a function safe_divide(a, b) -> Result<f64, String> that returns Err if b is 0. Use the ? operator in main to call it.",
r"""fn safe_divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("division by zero"))
    } else {
        Ok(a / b)
    }
}

fn main() -> Result<(), String> {
    let result = safe_divide(10.0, 2.0)?;
    println!("{:.1}", result);
    Ok(())
}""",
r"""fn safe_divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err(String::from("division by zero"))
    } else {
        Ok(a / b)
    }
}
fn main() -> Result<(), String> {
    let result = safe_divide(10.0, 2.0)?;
    println!("{:.1}", result);
    Ok(())
}""",
"5.0",
                    hints=["Return Err if b is 0", "Use ? to propagate the Result"]),
            ]},
        ])

        # ── Course 4: Rust Traits & Generics ──
        traits = await _seed(db, "Rust Traits & Generics",
            "Traits, generics, lifetimes, closures, and iterators.",
            "Rust", [
            {"title":"Generics & Traits","order":0,"steps":[
                t("Generics",
                  cd={M:r"""# Generics & Traits

```rust
// Generic function
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

fn main() {
    let nums = vec![34, 50, 25, 100, 65];
    println!("{}", largest(&nums));  // 100

    let chars = vec!['y', 'm', 'a', 'q'];
    println!("{}", largest(&chars));  // 'y'
}
```

## Traits (like interfaces)
```rust
pub trait Summary {
    fn summarize(&self) -> String;
    fn summarize_author(&self) -> String;

    // Default implementation
    fn read_more(&self) -> String {
        format!("Read more from {}...", self.summarize_author())
    }
}

pub struct Article {
    pub headline: String,
    pub author: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{} by {}", self.headline, self.author)
    }
    fn summarize_author(&self) -> String {
        self.author.clone()
    }
}

// Trait bounds
fn notify<T: Summary>(item: &T) {
    println!("Breaking: {}", item.summarize());
}

// impl Trait syntax
fn notify2(item: &impl Summary) {
    println!("Breaking: {}", item.summarize());
}

// Multiple bounds
fn compare<T: Summary + Clone>(a: &T, b: &T) {}
```"}),
                quiz("Trait Quiz", "What keyword introduces a trait in Rust?",
                     [{"id":"a","label":"interface"},{"id":"b","label":"trait"},{"id":"c","label":"abstract"},{"id":"d","label":"protocol"}],
                     "b", ["Rust uses `trait` (not interface)", "Traits define shared behavior"]),
            ]},

            {"title":"Lifetimes","order":1,"steps":[
                t("Lifetimes",
                  cd={M:r"""# Lifetimes

Lifetimes ensure references are valid as long as they're used.

```rust
// Lifetime annotation: 'a
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let s1 = String::from("long string is long");
    {
        let s2 = String::from("xyz");
        let result = longest(&s1, &s2);
        println!("{}", result);
    }  // s2 dropped here, but result is not used after
}
```

## Lifetime Elision Rules
The compiler infers lifetimes in most cases:
1. Each input reference gets its own lifetime
2. If there's one input lifetime, output gets it
3. If `&self`, output gets `self`'s lifetime

```rust
// No annotation needed:
fn first_word(s: &str) -> &str { ... }

// Struct with reference (needs annotation)
struct Excerpt<'a> {
    part: &'a str,
}
```"}),
                quiz("Lifetime Quiz", "What do lifetime annotations prevent?",
                     [{"id":"a","label":"Memory leaks"},{"id":"b","label":"Dangling references"},{"id":"c","label":"Stack overflow"},{"id":"d","label":"Deadlocks"}],
                     "b", ["Lifetimes ensure references outlive their usage", "The borrow checker is the Rust compiler's enforcer"]),
            ]},

            {"title":"Closures & Iterators","order":2,"steps":[
                t("Closures & Iterators",
                  cd={M:r"""# Closures & Iterators

## Closures (anonymous functions)
```rust
let add_one = |x: i32| -> i32 { x + 1 };
println!("{}", add_one(5));  // 6

// Type inference
let add = |a, b| a + b;

// Capture environment
let factor = 2;
let multiplier = |x| x * factor;  // captures factor by reference
println!("{}", multiplier(5));    // 10

// Move closures
let data = vec![1, 2, 3];
let show = move || println!("{:?}", data);  // data moved in
```

## Iterators (lazy)
```rust
let numbers = vec![1, 2, 3, 4, 5];

// map, filter, collect
let evens_squared: Vec<i32> = numbers
    .iter()
    .filter(|&&x| x % 2 == 0)
    .map(|&x| x * x)
    .collect();
println!("{:?}", evens_squared);  // [4, 16]

// fold (reduce)
let sum: i32 = numbers.iter().fold(0, |acc, x| acc + x);
println!("{}", sum);  // 15

// any, all, find
let has_even = numbers.iter().any(|&x| x % 2 == 0);
println!("{}", has_even);  // true

// Chaining
let result: Vec<i32> = (1..=10)
    .filter(|x| x % 2 == 0)
    .map(|x| x * 10)
    .collect();
println!("{:?}", result);  // [20, 40, 60, 80, 100]
```"}),
                code("Iterator Chain", "Use iterators to: filter numbers > 5, double them, collect into a Vec.",
r"""fn main() {
    let nums = vec![1, 3, 7, 2, 9, 4, 11];
    let result: Vec<i32> = nums
        .iter()
        .filter(|&&x| x > 5)
        .map(|&x| x * 2)
        .collect();
    println!("{:?}", result);
}""",
r"""fn main() {
    let nums = vec![1, 3, 7, 2, 9, 4, 11];
    let result: Vec<i32> = nums
        .iter()
        .filter(|&&x| x > 5)
        .map(|&x| x * 2)
        .collect();
    println!("{:?}", result);
}""",
"[14, 18, 22]",
                    hints=["filter() keeps matching elements", "map() transforms each element"]),
            ]},
        ])

        # ── Course 5: Rust Concurrency & Memory ──
        concurrency = await _seed(db, "Rust Concurrency & Memory",
            "Threads, channels, Arc/Mutex, Send/Sync traits, and async/await fundamentals.",
            "Rust", [
            {"title":"Threads","order":0,"steps":[
                t("Threads & Channels",
                  cd={M:r"""# Threads & Channels

```rust
use std::thread;
use std::time::Duration;

// Spawn a thread
let handle = thread::spawn(|| {
    for i in 1..10 {
        println!("hi number {} from spawned thread!", i);
        thread::sleep(Duration::from_millis(1));
    }
});

for i in 1..5 {
    println!("hi number {} from main thread!", i);
    thread::sleep(Duration::from_millis(1));
}

handle.join().unwrap();  // wait for thread
```

## Message Passing (channels)
```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();  // Multiple Producer, Single Consumer

thread::spawn(move || {
    let vals = vec![1, 2, 3, 4, 5];
    for val in vals {
        tx.send(val).unwrap();
        thread::sleep(std::time::Duration::from_secs(1));
    }
});

for received in rx {
    println!("Got: {}", received);
}
```"}),
                t("Arc & Mutex",
                  cd={M:r"""# Arc & Mutex (Shared State)

## Mutex
```rust
use std::sync::Mutex;

let m = Mutex::new(5);
{
    let mut num = m.lock().unwrap();
    *num = 6;  // modify through MutexGuard (deref)
} // lock automatically released here
```

## Arc (Atomic Reference Counting)
```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter_clone = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter_clone.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}

println!("Result: {}", *counter.lock().unwrap());  // 10
```

## Send & Sync Traits
- **Send**: Types that can be transferred across threads
- **Sync**: Types that can be shared via reference across threads
- Most types are Send + Sync automatically
- Raw pointers are neither
- Rc\<T\> is not Send (single-threaded ref count)
- Arc\<T\> is Send + Sync (atomic ref count)
```"}),
                quiz("Arc vs Rc", "What's the difference between Rc and Arc?",
                     [{"id":"a","label":"Arc is for async, Rc for sync"},{"id":"b","label":"Arc uses atomic counting, Rc doesn't"},{"id":"c","label":"Rc is faster but not thread-safe"},{"id":"d","label":"Both B and C"}],
                     "d", ["Rc is for single-threaded use only", "Arc uses atomic operations for thread safety"]),
            ]},

            {"title":"Async/Await","order":1,"steps":[
                t("Async Basics",
                  cd={M:r"""# Async/Await in Rust

```rust
use tokio;  // or async-std

#[tokio::main]
async fn main() {
    let result = fetch_data().await;
    println!("{}", result);
}

async fn fetch_data() -> String {
    // Simulate network call
    thread::sleep(std::time::Duration::from_secs(1));
    String::from("Data fetched!")
}

// Multiple async tasks
use tokio::join;

async fn task1() -> String { "Task 1".to_string() }
async fn task2() -> String { "Task 2".to_string() }

#[tokio::main]
async fn main() {
    let (r1, r2) = join!(task1(), task2());
    println!("{}, {}", r1, r2);
}
```

## Key async concepts:
- **Future**: A value that may not be ready yet
- **await**: Pauses current function until Future completes
- **Runtime**: Executor that polls Futures (e.g., tokio, async-std)
- Unlike goroutines, Rust's async is zero-cost (no pre-allocated stack)
"""})]},

            {"title":"Smart Pointers","order":2,"steps":[
                t("Box, Rc, RefCell",
                  cd={M:r"""# Smart Pointers

## Box\<T\> - Heap allocation
```rust
// Recursive types need Box
enum List {
    Cons(i32, Box<List>),
    Nil,
}

let list = Cons(1, Box::new(Cons(2, Box::new(Nil))));
```

```rust
// Trait objects
trait Animal { fn speak(&self); }
struct Dog;
impl Animal for Dog { fn speak(&self) { println!("Woof!"); } }

let animal: Box<dyn Animal> = Box::new(Dog);
animal.speak();
```

## Rc\<T\> - Reference Counted (single-threaded)
```rust
use std::rc::Rc;

let a = Rc::new(String::from("hello"));
let b = Rc::clone(&a);  // increments reference count
println!("count: {}", Rc::strong_count(&a));  // 2
```

## RefCell\<T\> - Interior Mutability
```rust
use std::cell::RefCell;

let data = RefCell::new(5);
*data.borrow_mut() = 10;  // borrow_mut() panics if already borrowed
println!("{}", data.borrow());  // 10
```

## Reference Cycles
```rust
use std::rc::{Rc, Weak};
use std::cell::RefCell;

// Use Weak<T> to break cycles (doesn't own the value)
struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,
    children: RefCell<Vec<Rc<Node>>>,
}
```"}),
                quiz("Box Quiz", "When should you use Box<T>?",
                     [{"id":"a","label":"All heap allocations"},{"id":"b","label":"Recursive types and trait objects"},{"id":"c","label":"Multithreaded code"},{"id":"d","label":"String manipulation"}],
                     "b", ["Box is for heap allocation of recursive types or trait objects", "Use Vec, String, etc. for general heap allocation"]),
            ]},
        ])

        # ── Course 6: Rust Testing & Modules ──
        testing = await _seed(db, "Rust Testing & Modules",
            "Unit tests, integration tests, documentation tests, modules, packages, and Cargo.",
            "Rust", [
            {"title":"Testing","order":0,"steps":[
                t("Unit & Integration Tests",
                  cd={M:r"""# Testing in Rust

## Unit Tests (in the same file)
```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, 1), 0);
    }

    #[test]
    #[should_panic(expected = "divide by zero")]
    fn test_divide_by_zero() {
        divide(10, 0);
    }
}
```

## Integration Tests (in tests/ folder)
```rust
// tests/integration_test.rs
use my_crate;

#[test]
fn test_integration() {
    assert!(my_crate::do_something());
}
```

## Doc Tests
```rust
/// Adds two numbers
///
/// # Examples
/// ```
/// use my_lib::add;
/// assert_eq!(add(2, 3), 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

Run: `cargo test`
Doc tests: `cargo test --doc`
```"}),
                code("Write a Test", "Write a function is_even and a test for it.",
r"""pub fn is_even(n: i32) -> bool {
    n % 2 == 0
}

fn main() {
    println!("{}", is_even(4));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_even() {
        assert!(is_even(4));
    }

    #[test]
    fn test_odd() {
        assert!(!is_even(7));
    }
}""",
r"""pub fn is_even(n: i32) -> bool { n % 2 == 0 }
fn main() { println!("{}", is_even(4)); }
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_even() { assert!(is_even(4)); }
    #[test] fn test_odd() { assert!(!is_even(7)); }
}""",
"true",
                    hints=["#[cfg(test)] gates test code", "#[test] marks a function as a test"]),
            ]},

            {"title":"Modules & Crates","order":1,"steps":[
                t("Module System",
                  cd={M:r"""# Modules & Crates

```rust
// src/lib.rs
pub mod networking {
    pub mod http {
        pub fn get(url: &str) -> Result<String, &str> {
            Ok(format!("GET {}", url))
        }
    }
}

// src/main.rs
use my_lib::networking::http;

fn main() {
    let result = http::get("https://example.com").unwrap();
    println!("{}", result);
}

// Alternative: separate files
// src/networking/mod.rs  (or src/networking.rs)
// src/networking/http.rs
```

## Cargo.toml
```toml
[package]
name = "my_app"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
```

## Visibility
- `pub`: accessible everywhere
- `pub(crate)`: accessible within the crate
- `pub(super)`: accessible in parent module
- Default: private
```"}),
                quiz("Module Quiz", "What does `pub(crate)` mean?",
                     [{"id":"a","label":"Public to everyone"},{"id":"b","label":"Public only within the current crate"},{"id":"c","label":"Private"},{"id":"d","label":"Public to submodules only"}],
                     "b", ["pub(crate) restricts visibility to the crate", "Use for internal API that external consumers shouldn't access"]),
            ]},
        ])

        # ── Course 7: Rust Standard Library ──
        std_lib = await _seed(db, "Rust Standard Library Deep Dive",
            "File I/O, environment, command-line args, process management, serialization, and more.",
            "Rust", [
            {"title":"File & Environment","order":0,"steps":[
                t("File I/O & Environment",
                  cd={M:r"""# File I/O & Environment

## Reading & Writing Files
```rust
use std::fs;
use std::io::Write;

// Read entire file
let content = fs::read_to_string("hello.txt")
    .expect("Could not read file");
println!("{}", content);

// Write entire file
fs::write("output.txt", "Hello, Rust!").expect("Could not write");

// Read binary
let bytes = fs::read("image.png").unwrap();

// Create and write
let mut file = fs::File::create("log.txt")?;
file.write_all(b"Log entry 1\n")?;
```

## Environment & Args
```rust
use std::env;

// Command-line arguments
let args: Vec<String> = env::args().collect();
if args.len() < 2 {
    eprintln!("Usage: {} <name>", args[0]);
    std::process::exit(1);
}

// Environment variables
println!("PATH: {}", env::var("PATH").unwrap_or_default());
env::set_var("MY_VAR", "value");

// Current directory
let cwd = env::current_dir().unwrap();
println!("Working dir: {}", cwd.display());
```"}),
                code("File Line Count", "Read filename from args, print line count. If no filename, print '0'.",
r"""use std::env;
use std::fs;

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("0");
        return;
    }
    let content = fs::read_to_string(&args[1]).unwrap_or_default();
    let lines = content.lines().count();
    println!("{}", lines);
}""",
r"""use std::env;
use std::fs;
fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 { println!("0"); return; }
    let content = fs::read_to_string(&args[1]).unwrap_or_default();
    let lines = content.lines().count();
    println!("{}", lines);
}""",
"0",
                    hints=["env::args() gives command line args", "unwrap_or_default() handles missing files gracefully"]),
            ]},

            {"title":"Serialization","order":1,"steps":[
                t("Serde",
                  cd={M:r"""# Serialization with Serde

```rust
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
    email: String,
    #[serde(default)]
    active: bool,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let user = User {
        id: 1,
        name: "Alice".to_string(),
        email: "alice@example.com".to_string(),
        active: true,
    };

    // Serialize to JSON
    let json = serde_json::to_string_pretty(&user)?;
    println!("{}", json);

    // Deserialize from JSON
    let json_str = r#"{"id":2,"name":"Bob","email":"bob@example.com"}"#;
    let user2: User = serde_json::from_str(json_str)?;
    println!("{:?}", user2);

    // YAML, TOML, etc.
    // let yaml = serde_yaml::to_string(&user)?;
    Ok(())
}
```

## Custom Serialization
```rust
#[derive(Serialize)]
struct Response {
    status: u16,
    #[serde(rename = "message")]
    msg: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    data: Option<String>,
}
```"}),
            ]},
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
            (std_lib, "Standard Library", 75),
        ]

        existing = {(r.course_id) for r in (await db.execute(select(PathLevel).where(PathLevel.path_id == rust_path.id))).scalars().all()}
        order = 0
        for c, name, req in levels_config:
            if c and c.id not in existing:
                order += 1
                db.add(PathLevel(path_id=rust_path.id, course_id=c.id, level_name=name, order=order, required_progress_pct=req))
                logger.info("  Rust path + Level %d: %s", order, name)

        await db.commit()
        logger.info("=" * 50)
        logger.info("RUST SEEDING COMPLETE!")
        logger.info("=" * 50)

asyncio.run(run())
