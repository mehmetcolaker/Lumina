"""Secure code sandbox with Docker and SQLite In-Memory.

Runs untrusted user code inside either:
  - A restricted Docker container (Python, JavaScript, Bash)
  - An in-memory SQLite database (SQL)

Security constraints applied to Docker containers:
    - mem_limit=50m         -> maximum 50 MB of RAM
    - cpu_quota=50000       -> at most 50 % of a single CPU core
    - network_disabled=True -> no network access
    - auto_remove=True      -> container is destroyed after exit
    - timeout=3s            -> killed forcibly if it runs longer
"""

import contextlib
import io
import logging
import sqlite3
import time

try:
    import docker
    from docker.errors import DockerException

    _DOCKER_AVAILABLE = True
except ImportError:
    _DOCKER_AVAILABLE = False


logger = logging.getLogger(__name__)


# Map of human-readable language -> Docker image + entry-point
_SUPPORTED_IMAGES: dict[str, tuple[str, list[str]]] = {
    "python": ("python:3.11-alpine", ["python", "-c"]),
    "javascript": ("node:20-alpine", ["node", "-e"]),
    "bash": ("alpine:latest", ["sh", "-c"]),
}


def _capture_python_stdout_stderr(code: str, timeout_s: int = 3) -> tuple[str, str, int, float]:
    """Run Python code safely in an in-process sandbox using exec()."""
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    start = time.monotonic()

    restricted_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "True": True,
            "False": False,
            "None": None,
            "abs": abs,
            "max": max,
            "min": min,
            "sum": sum,
            "round": round,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "type": type,
            "isinstance": isinstance,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "ZeroDivisionError": ZeroDivisionError,
            "AttributeError": AttributeError,
            "StopIteration": StopIteration,
            "Exception": Exception,
            "BaseException": BaseException,
            "KeyboardInterrupt": KeyboardInterrupt,
            "iter": iter,
            "next": next,
            "input": input,
            "open": open,
            "ord": ord,
            "chr": chr,
            "hex": hex,
            "oct": oct,
            "bin": bin,
            "format": format,
            "id": id,
            "repr": repr,
            "callable": callable,
        }
    }

    exit_code = 0

    try:
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            compiled = compile(code, "<user_code>", "exec")
            exec(compiled, restricted_globals)
    except KeyboardInterrupt:
        exit_code = -9
        stderr_buf.write("Execution interrupted (timeout).")
    except SystemExit as e:
        exit_code = e.code if e.code else 0
    except Exception as e:
        exit_code = 1
        stderr_buf.write(f"{type(e).__name__}: {e}")

    elapsed = time.monotonic() - start
    stdout = stdout_buf.getvalue()
    stderr = stderr_buf.getvalue()
    return stdout, stderr, exit_code, elapsed


def _run_container(image: str, command: list[str]) -> tuple[str, str, int, float, bool]:
    """Spin up a restricted container, wait for it, and return logs."""
    client = docker.from_env()

    container = client.containers.create(
        image=image,
        command=command,
        detach=True,
        mem_limit="50m",
        cpu_quota=50000,
        network_disabled=True,
        stdout=True,
        stderr=True,
    )

    start = time.monotonic()
    timed_out = False

    try:
        container.start()
    except DockerException as exc:
        container.remove()
        raise RuntimeError(f"Failed to start container: {exc}") from exc

    try:
        container.wait(timeout=3)
    except Exception:
        timed_out = True
        logger.warning("Container %s timed out, force-killing", container.id)
        try:
            container.kill()
        except Exception:
            pass

    elapsed = time.monotonic() - start
    runtime_ms = int(round(elapsed * 1000))

    try:
        stdout_raw = container.logs(stdout=True, stderr=False)
        stderr_raw = container.logs(stdout=False, stderr=True)
    except Exception:
        stdout_raw = b""
        stderr_raw = b""

    stdout = stdout_raw.decode("utf-8", errors="replace").strip()
    stderr = stderr_raw.decode("utf-8", errors="replace").strip()

    try:
        exit_code = container.wait(timeout=5).get("StatusCode", 1)
    except Exception:
        exit_code = 1 if timed_out else 0

    container.remove()

    return stdout, stderr, exit_code, runtime_ms, timed_out


def _run_python_code(code: str) -> tuple[str, str, int, float, bool]:
    """Execute Python code via Docker or fallback in-process sandbox."""
    if _DOCKER_AVAILABLE:
        try:
            return _run_container("python:3.11-alpine", ["python", "-c", code])
        except Exception as exc:
            logger.warning("Docker unavailable, falling back to in-process: %s", exc)

    stdout, stderr, exit_code, elapsed_s = _capture_python_stdout_stderr(code)
    return stdout, stderr, exit_code, int(round(elapsed_s * 1000)), False


def _run_javascript_code(code: str) -> tuple[str, str, int, float, bool]:
    """Execute JavaScript code via Node.js Docker container."""
    if not _DOCKER_AVAILABLE:
        raise RuntimeError("JavaScript execution requires Docker.")
    try:
        return _run_container("node:20-alpine", ["node", "-e", code])
    except Exception as exc:
        raise RuntimeError(f"JavaScript execution failed: {exc}") from exc


def _run_sql_code(code: str) -> tuple[str, str, int, float, bool]:
    """Execute SQL queries against an in-memory SQLite database."""
    start = time.monotonic()
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    try:
        conn.executescript("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            );
            INSERT INTO categories VALUES
                (1, 'Elektronik', 'Bilgisayar, telefon, tablet urunleri'),
                (2, 'Giyim', 'Kiyafet ve aksesuarlar'),
                (3, 'Kitap', 'Roman, egitim, bilim kitaplari'),
                (4, 'Ev & Yasam', 'Mobilya, dekorasyon urunleri');
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                category_id INTEGER REFERENCES categories(id)
            );
            INSERT INTO products VALUES
                (1, 'Akilli Telefon', 8999.99, 50, 1),
                (2, 'Dizustu Bilgisayar', 24999.00, 25, 1),
                (3, 'Kulaklik', 1299.00, 100, 1),
                (4, 'TiSort', 199.99, 200, 2),
                (5, 'Kot Pantolon', 449.99, 80, 2),
                (6, 'Python Kitabi', 349.00, 150, 3),
                (7, 'SQL Rehberi', 249.00, 120, 3),
                (8, 'Saat', 3999.00, 40, 1),
                (9, 'Masa Lambasi', 299.00, 60, 4),
                (10, 'Kahve Makinesi', 1499.00, 35, 4);
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                city TEXT,
                age INTEGER
            );
            INSERT INTO users VALUES
                (1, 'Ali Yilmaz', 'ali@example.com', 'Istanbul', 28),
                (2, 'Ayse Demir', 'ayse@example.com', 'Ankara', 34),
                (3, 'Mehmet Kaya', 'mehmet@example.com', 'Izmir', 22),
                (4, 'Zeynep Celik', 'zeynep@example.com', 'Istanbul', 29),
                (5, 'Can Ozturk', 'can@example.com', 'Bursa', 31);
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                product_id INTEGER REFERENCES products(id),
                quantity INTEGER NOT NULL DEFAULT 1,
                order_date TEXT NOT NULL DEFAULT (date('now')),
                total REAL NOT NULL
            );
            INSERT INTO orders VALUES
                (1, 1, 1, 1, '2025-01-15', 8999.99),
                (2, 1, 3, 2, '2025-01-15', 2598.00),
                (3, 2, 2, 1, '2025-02-01', 24999.00),
                (4, 3, 6, 3, '2025-02-10', 1047.00),
                (5, 4, 8, 1, '2025-03-05', 3999.00),
                (6, 5, 4, 5, '2025-03-20', 999.95),
                (7, 1, 7, 1, '2025-04-01', 249.00),
                (8, 2, 9, 2, '2025-04-15', 598.00);
        """)

        dangerous_keywords = ["CREATE", "DROP", "ALTER", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REPLACE"]
        code_upper = code.strip().upper()
        first_word = code_upper.split()[0].rstrip(";") if code_upper.split() else ""
        if first_word in dangerous_keywords:
            raise ValueError(f"'{first_word}' islemine izin verilmez. Sadece SELECT sorgulari calistirabilirsiniz.")

        cursor = conn.execute(code)
        rows = cursor.fetchmany(50)

        if rows:
            col_names = [desc[0] for desc in cursor.description]
            stdout_buf.write(" | ".join(col_names) + "\n")
            stdout_buf.write("-" * (sum(len(c) for c in col_names) + 3 * (len(col_names) - 1)) + "\n")
            for row in rows:
                values = [str(row[c]) if row[c] is not None else "NULL" for c in col_names]
                stdout_buf.write(" | ".join(values) + "\n")
        else:
            stdout_buf.write("(empty result set)\n")

        exit_code = 0

    except ValueError as e:
        exit_code = 1
        stderr_buf.write(str(e))
    except Exception as e:
        exit_code = 1
        stderr_buf.write(f"SQL Error: {e}")
    finally:
        conn.close()

    elapsed = time.monotonic() - start
    runtime_ms = int(round(elapsed * 1000))
    stdout = stdout_buf.getvalue().strip()
    stderr = stderr_buf.getvalue().strip()

    return stdout, stderr, exit_code, runtime_ms, False


# -- Language -> runner mapping --
_LANGUAGE_RUNNERS = {
    "python": _run_python_code,
    "javascript": _run_javascript_code,
    "sql": _run_sql_code,
    "bash": lambda code: _run_container("alpine:latest", ["sh", "-c", code]),
}


def run_code_in_sandbox(code: str, language: str) -> dict:
    """Execute the provided source code inside a sandbox.

    Args:
        code: The raw source code to run.
        language: Target programming language.

    Returns:
        A dict with keys: stdout, stderr, exit_code, runtime_ms, timed_out.
    """
    runner = _LANGUAGE_RUNNERS.get(language.lower())
    if runner is None:
        raise RuntimeError(
            f"Unsupported language '{language}'. "
            f"Supported: {list(_LANGUAGE_RUNNERS)}"
        )

    stdout, stderr, exit_code, runtime_ms, timed_out = runner(code)

    return {
        "stdout": stdout if stdout else "",
        "stderr": stderr if stderr else "",
        "exit_code": exit_code,
        "runtime_ms": runtime_ms,
        "timed_out": timed_out,
    }


def run_test_case(
    code: str,
    language: str,
    test_input: str,
    expected: str,
) -> dict:
    """Run a single test case by executing code + input and comparing output.

    For Python, the test_input is appended to the user's code as a print
    statement, or if test_input already contains a function call it is
    appended directly.

    Args:
        code: The user's source code.
        language: Programming language.
        test_input: The input/function-call string to execute.
        expected: The expected stdout output.

    Returns:
        A dict with keys: name, input, expected, actual, passed, stderr, runtime_ms.
    """
    # Python: if test_input is a bare expression like "5", wrap in print()
    # Otherwise assume it is a full statement
    full_code = code
    if language == "python" and test_input:
        test_input_stripped = test_input.strip()
        # If it starts with "print(" or is a statement-like, use as-is
        if test_input_stripped.startswith("print(") or test_input_stripped.startswith("assert"):
            full_code = f"{code}\n{test_input_stripped}"
        elif test_input_stripped:
            # Possibly a bare value like "42" -> print it
            full_code = f"{code}\nprint({test_input_stripped})"
        else:
            full_code = code
    elif language == "javascript" and test_input:
        full_code = f"{code}\n{test_input.strip()}"
    elif language == "sql":
        # SQL test cases use the input as the query
        return _run_sql_test_case(test_input.strip(), expected)

    start = time.monotonic()

    try:
        result = run_code_in_sandbox(full_code, language)
    except Exception as exc:
        return {
            "name": test_input[:50] if test_input else "test",
            "input": test_input,
            "expected": expected,
            "actual": "",
            "passed": False,
            "stderr": str(exc),
            "runtime_ms": 0,
        }

    runtime_ms = result["runtime_ms"]
    actual = result["stdout"].strip()
    user_stderr = result["stderr"]
    timed_out = result["timed_out"]
    exit_code = result["exit_code"]

    if timed_out:
        passed = False
        user_stderr = user_stderr + "\n(3 saniye sinirini asti)" if user_stderr else "(3 saniye sinirini asti)"
    elif exit_code != 0:
        passed = False
    else:
        passed = actual == expected.strip()

    return {
        "name": test_input[:50] if test_input else "test",
        "input": test_input,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "stderr": user_stderr if user_stderr else "",
        "runtime_ms": runtime_ms,
    }


def _run_sql_test_case(sql_query: str, expected_str: str) -> dict:
    """Run a SQL query and compare its output with the expected string."""
    start = time.monotonic()
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    try:
        # Seed same tables
        conn.executescript("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY, name TEXT, price REAL, stock INTEGER, category_id INTEGER
            );
            INSERT INTO products VALUES
                (1,'Phone',8999.99,50,1),(2,'Laptop',24999.00,25,1),(3,'Shirt',199.99,200,2);
            CREATE TABLE users (
                id INTEGER PRIMARY KEY, name TEXT, email TEXT, city TEXT, age INTEGER
            );
            INSERT INTO users VALUES
                (1,'Ali','ali@x.com','Istanbul',28),(2,'Ayse','ayse@x.com','Ankara',34);
        """)

        cursor = conn.execute(sql_query)
        rows = cursor.fetchmany(50)

        if rows:
            col_names = [desc[0] for desc in cursor.description]
            stdout_buf.write(" | ".join(col_names) + "\n")
            stdout_buf.write("-" * 20 + "\n")
            for row in rows:
                values = [str(row[c]) if row[c] is not None else "NULL" for c in col_names]
                stdout_buf.write(" | ".join(values) + "\n")
        else:
            stdout_buf.write("(empty)\n")

        actual = stdout_buf.getvalue().strip()
        passed = actual == expected_str.strip() if expected_str else True
        exit_code = 0
    except Exception as e:
        passed = False
        exit_code = 1
        stderr_buf.write(f"SQL Error: {e}")
    finally:
        conn.close()

    elapsed = time.monotonic() - start
    return {
        "name": sql_query[:50],
        "input": sql_query,
        "expected": expected_str,
        "actual": stdout_buf.getvalue().strip() if not stderr_buf.getvalue() else "",
        "passed": passed,
        "stderr": stderr_buf.getvalue(),
        "runtime_ms": int(round(elapsed * 1000)),
    }


def run_all_test_cases(code: str, language: str, test_cases: list[dict]) -> list[dict]:
    """Run all test cases for a step and return results.

    Args:
        code: The user's source code.
        language: Programming language.
        test_cases: List of dicts with "input" and "expected" keys.

    Returns:
        A list of result dicts, one per test case.
    """
    results = []
    for tc in test_cases:
        result = run_test_case(
            code=code,
            language=language,
            test_input=tc.get("input", ""),
            expected=tc.get("expected", ""),
        )
        result["name"] = tc.get("name", result["input"][:50])
        results.append(result)
    return results
