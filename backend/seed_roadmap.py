"""Seed the Python Developer Roadmap with 5 new English courses.

Run AFTER seed_data.py to add:
  - 5 new courses (Beginner 2-3, Intermediate 1-3)
  - LearningPath "Python Developer Roadmap"
  - PathLevel records linking each level to its course

Usage:
    python seed_roadmap.py
"""

import asyncio
import logging

from sqlalchemy import select

from app.core.database import async_session_maker
from app.modules.courses.models import (
    Course, LearningPath, PathLevel, Section, Step, StepType,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# COURSE: Beginner 2 — Logic & Loops Deep Dive
# ─────────────────────────────────────────────
B2_COURSE = {
    "title": "Logic & Loops Deep Dive",
    "description": "Master Python's control flow: advanced loops, nested patterns, comprehensions, and while-loop applications.",
    "language": "Python",
}

B2_SECTIONS = [
    {
        "title": "Advanced Loops",
        "order": 0,
        "steps": [
            {
                "title": "Break, Continue, Pass",
                "step_type": StepType.THEORY,
                "order": 0, "xp_reward": 10,
                "content_data": {"body_markdown": "# Break, Continue, Pass\n\nThree loop control statements:\n\n## break\nExit the loop immediately.\n```python\nfor i in range(10):\n    if i == 5:\n        break\n    print(i)\n# Prints 0 1 2 3 4\n```\n\n## continue\nSkip the rest of the current iteration.\n```python\nfor i in range(5):\n    if i == 2:\n        continue\n    print(i)\n# Prints 0 1 3 4\n```\n\n## pass\nDoes nothing - placeholder for future code.\n```python\nfor i in range(5):\n    pass  # TODO later\n```"},
            },
            {
                "title": "Loop Control Quiz",
                "step_type": StepType.QUIZ,
                "order": 1, "xp_reward": 20,
                "content_data": {
                    "question": "What does the following code print?\n```python\nfor i in range(5):\n    if i % 2 == 0:\n        continue\n    print(i)\n```",
                    "options": [
                        {"id": "a", "label": "0 2 4"},
                        {"id": "b", "label": "1 3"},
                        {"id": "c", "label": "0 1 2 3 4"},
                        {"id": "d", "label": "Nothing"},
                    ],
                    "correct_option": "b",
                    "hints": [
                        "The modulo operator `%` checks if a number is even.",
                        "`continue` skips the rest of the loop body for even numbers.",
                        "Only odd numbers (1 and 3) get printed.",
                    ],
                    "explanation": "i=0 is even -> continue. i=1 odd -> print. i=2 even -> continue. i=3 odd -> print. i=4 even -> continue. Output: 1 3",
                },
            },
            {
                "title": "Find Primes with Break",
                "step_type": StepType.CODE,
                "order": 2, "xp_reward": 30,
                "content_data": {
                    "instruction": "Write a program that prints all prime numbers between 1 and 50. Use a nested loop with `break` to detect non-primes.\n\nTip: A prime is only divisible by 1 and itself.",
                    "starter_code": "for num in range(2, 51):\n    is_prime = True\n    for divisor in range(2, num):\n        if num % divisor == 0:\n            is_prime = False\n            break\n    if is_prime:\n        print(num)",
                    "solution": "for num in range(2, 51):\n    is_prime = True\n    for divisor in range(2, num):\n        if num % divisor == 0:\n            is_prime = False\n            break\n    if is_prime:\n        print(num)",
                    "expected_output": "2\n3\n5\n7\n11\n13\n17\n19\n23\n29\n31\n37\n41\n43\n47",
                    "compare_mode": "trim",
                    "test_cases": [
                        {"input": "", "expected": "2\n3\n5\n7\n11\n13\n17\n19\n23\n29\n31\n37\n41\n43\n47"},
                    ],
                    "hints": [
                        "Use a nested loop: outer loop for numbers, inner loop to check divisibility.",
                        "If `num % divisor == 0`, the number is not prime - use `break`.",
                        "Only print when `is_prime` is still True after the inner loop.",
                    ],
                },
            },
        ],
    },
    {
        "title": "Nested Loops & Patterns",
        "order": 1,
        "steps": [
            {
                "title": "Nested Loops",
                "step_type": StepType.THEORY,
                "order": 0, "xp_reward": 10,
                "content_data": {"body_markdown": "# Nested Loops\n\nA loop inside another loop is called a **nested loop**.\n\n```python\nfor i in range(3):     # outer loop\n    for j in range(3): # inner loop\n        print(f\"({i},{j})\", end=\" \")\n    print()  # newline\n\n# Output:\n# (0,0) (0,1) (0,2)\n# (1,0) (1,1) (1,2)\n# (2,0) (2,1) (2,2)\n```\n\nUse nested loops for:\n- Multiplication tables\n- Drawing patterns (pyramids, grids)\n- Working with 2D data (matrices)"},
            },
            {
                "title": "Pattern Drawing",
                "step_type": StepType.CODE,
                "order": 1, "xp_reward": 35,
                "content_data": {
                    "instruction": "Write code that prints a right-angled triangle of stars with height 5:\n```\n*\n**\n***\n****\n*****\n```",
                    "starter_code": "height = 5\n# Use nested loops here\n",
                    "solution": "height = 5\nfor i in range(1, height + 1):\n    print('*' * i)",
                    "expected_output": "*\n**\n***\n****\n*****",
                    "compare_mode": "trim",
                    "test_cases": [{"input": "", "expected": "*\n**\n***\n****\n*****"}],
                    "hints": ["The inner loop runs `i` times.", "Outer loop: `for i in range(1, height+1)`"],
                },
            },
        ],
    },
    {
        "title": "While Loop Applications",
        "order": 2,
        "steps": [
            {
                "title": "While Loops",
                "step_type": StepType.THEORY,
                "order": 0, "xp_reward": 10,
                "content_data": {"body_markdown": "# While Loops\n\nA `while` loop repeats as long as a condition is True.\n\n```python\ncount = 0\nwhile count < 5:\n    print(count)\n    count += 1\n# Prints 0 1 2 3 4\n```\n\n## Infinite loop warning!\nAlways ensure the condition will eventually become False.\n\n```python\n# DANGER: never runs\ni = 0\nwhile True:\n    print(\"forever...\")\n    # Missing: i += 1\n```\n\n## Common use cases:\n- User input validation\n- Game loops\n- Guessing games"},
            },
            {
                "title": "Number Guessing Game",
                "step_type": StepType.CODE,
                "order": 1, "xp_reward": 40,
                "content_data": {
                    "instruction": "Create a number guessing game:\n1. Generate a random number between 1-20\n2. Let the user guess (use `int(input())`)\n3. Give hints \"Too high\" or \"Too low\"\n4. Stop when guessed correctly",
                    "starter_code": "import random\n\nsecret = random.randint(1, 20)\nguess = None\n\nwhile guess != secret:\n    guess = int(input(\"Guess: \"))\n    if guess < secret:\n        print(\"Too low\")\n    elif guess > secret:\n        print(\"Too high\")\n\nprint(\"Correct!\")",
                    "solution": "import random\nsecret = random.randint(1, 20)\nguess = None\nwhile guess != secret:\n    guess = int(input(\"Guess: \"))\n    if guess < secret:\n        print(\"Too low\")\n    elif guess > secret:\n        print(\"Too high\")\nprint(\"Correct!\")",
                    "compare_mode": "contains",
                    "expected_output": "Correct!",
                    "hints": ["Use `random.randint(1, 20)` for the secret number.", "Keep looping `while guess != secret`."],
                },
            },
        ],
    },
    {
        "title": "List Comprehensions",
        "order": 3,
        "steps": [
            {
                "title": "List Comprehensions",
                "step_type": StepType.THEORY,
                "order": 0, "xp_reward": 10,
                "content_data": {"body_markdown": "# List Comprehensions\n\nA concise way to create lists.\n\n```python\n# Traditional\nsquares = []\nfor x in range(10):\n    squares.append(x**2)\n\n# Comprehension (one line!)\nsquares = [x**2 for x in range(10)]\n```\n\n## With condition\n```python\nevens = [x for x in range(20) if x % 2 == 0]\n```\n\n## Nested comprehension\n```python\nmatrix = [[i*j for j in range(3)] for i in range(3)]\n```\n\nComprehensions are faster and more readable than traditional loops!"},
            },
            {
                "title": "Comprehension Quiz",
                "step_type": StepType.QUIZ,
                "order": 1, "xp_reward": 20,
                "content_data": {
                    "question": "What does this comprehension produce?\n```python\n[x*2 for x in range(1, 6) if x > 3]\n```",
                    "options": [
                        {"id": "a", "label": "[8, 10]"},
                        {"id": "b", "label": "[2, 4, 6, 8, 10]"},
                        {"id": "c", "label": "[6, 8, 10]"},
                        {"id": "d", "label": "[4, 5]"},
                    ],
                    "correct_option": "a",
                    "hints": ["range(1,6) = [1,2,3,4,5]", "Filter `x > 3` leaves [4,5]", "Then `x*2` gives [8,10]"],
                    "explanation": "range(1,6) = [1,2,3,4,5]. Filter x>3: [4,5]. Multiply by 2: [8,10].",
                },
            },
            {
                "title": "Comprehension Practice",
                "step_type": StepType.CODE,
                "order": 2, "xp_reward": 35,
                "content_data": {
                    "instruction": "Use a list comprehension to create a list of squares for numbers 1 through 15, but only include squares that are divisible by 5.",
                    "starter_code": "result = [x**2 for x in range(1, 16) if x**2 % 5 == 0]\nprint(result)",
                    "solution": "result = [x**2 for x in range(1, 16) if x**2 % 5 == 0]\nprint(result)",
                    "expected_output": "[25, 100, 225]",
                    "compare_mode": "trim",
                    "test_cases": [{"input": "", "expected": "[25, 100, 225]"}],
                    "hints": ["`range(1, 16)` gives numbers 1-15.", "Use `x**2` for the square.", "Filter with `if x**2 % 5 == 0`."],
                },
            },
        ],
    },
]

# ─────────────────────────────────────────────
# COURSES: Beginner 3 — Data Structures Mastery
# ─────────────────────────────────────────────
B3_COURSE = {
    "title": "Data Structures Mastery",
    "description": "Deep dive into Python data structures: strings, lists, tuples, sets, and dictionaries.",
    "language": "Python",
}

B3_SECTIONS = [
    {
        "title": "String Manipulation",
        "order": 0,
        "steps": [
            {"title": "String Methods", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# String Methods\n\nStrings have many built-in methods.\n\n```python\ntext = \"Hello, Python!\"\nprint(text.lower())        # \"hello, python!\"\nprint(text.upper())        # \"HELLO, PYTHON!\"\nprint(text.split(\",\"))    # ['Hello', ' Python!']\nprint(text.startswith(\"H\")) # True\nprint(text.replace(\"Python\", \"World\"))  # \"Hello, World!\"\n```\n\n## String Formatting\n```python\nname = \"Alice\"\nscore = 95\nprint(f\"{name} scored {score}%\")   # f-string (modern)\nprint(\"{} scored {}%\".format(name, score))  # format()\n```"}},
            {"title": "String Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "What is the result of `\"Python is fun\".split()[1]`?",
                 "options": [
                     {"id": "a", "label": "\"Python\""},
                     {"id": "b", "label": "\"is\""},
                     {"id": "c", "label": "\"fun\""},
                     {"id": "d", "label": "\"Python is\""},
                 ], "correct_option": "b",
                 "hints": ["split() without arguments splits by whitespace.", "The result is ['Python', 'is', 'fun']", "Index [1] gives the second element."],
                 "explanation": "split() returns ['Python', 'is', 'fun']. Index [1] is 'is'.",
             }},
            {"title": "String Formatting", "step_type": StepType.CODE, "order": 2, "xp_reward": 30,
             "content_data": {
                 "instruction": "Write a program that asks for a name and age, then prints a formatted message using an f-string.\n\nExpected format: \"Hello NAME! You are AGE years old.\"",
                 "starter_code": "name = input(\"Enter name: \")\nage = input(\"Enter age: \")\n# Use f-string to format\nprint(f\"Hello {name}! You are {age} years old.\")",
                 "solution": "name = input(\"Enter name: \")\nage = input(\"Enter age: \")\nprint(f\"Hello {name}! You are {age} years old.\")",
                 "expected_output": "Hello ",
                 "compare_mode": "contains",
                 "hints": ["f-strings start with `f` before quotes.", "Variables go inside curly braces: `{variable}`."],
             }},
        ],
    },
    {
        "title": "List Methods & Slicing",
        "order": 1,
        "steps": [
            {"title": "List Operations", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# List Operations\n\n```python\nnumbers = [3, 1, 4, 1, 5, 9]\n\n# Methods\nnumbers.append(2)   # add to end\nnumbers.sort()      # sort in-place\nnumbers.reverse()   # reverse\nnumbers.pop()       # remove last\nnumbers.remove(3)   # remove first 3\n\n# Slicing\nprint(numbers[1:4])    # elements 1-3\nprint(numbers[:3])     # first 3\nprint(numbers[::2])    # every second\nprint(numbers[::-1])   # reversed copy\n```"}},
            {"title": "Slicing Practice", "step_type": StepType.CODE, "order": 1, "xp_reward": 35,
             "content_data": {
                 "instruction": "Given the list `data = [10, 20, 30, 40, 50, 60, 70, 80]`, print:\n1. The first 3 elements\n2. The last 3 elements\n3. Every second element\n4. The list in reverse order",
                 "starter_code": "data = [10, 20, 30, 40, 50, 60, 70, 80]\nprint(data[:3])\nprint(data[-3:])\nprint(data[::2])\nprint(data[::-1])",
                 "solution": "data = [10, 20, 30, 40, 50, 60, 70, 80]\nprint(data[:3])\nprint(data[-3:])\nprint(data[::2])\nprint(data[::-1])",
                 "compare_mode": "contains",
                 "expected_output": "[10, 20, 30]",
                 "hints": ["First 3: `list[:3]`", "Last 3: `list[-3:]`", "Reverse: `list[::-1]`"],
             }},
        ],
    },
    {
        "title": "Tuple & Set Operations",
        "order": 2,
        "steps": [
            {"title": "Tuples and Sets", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Tuples & Sets\n\n## Tuples (immutable lists)\n```python\npoint = (3, 5)\nx, y = point  # unpacking\nprint(x)  # 3\n```\nTuples cannot be changed after creation.\n\n## Sets (unique items)\n```python\nnumbers = {1, 2, 2, 3, 3, 3}\nprint(numbers)  # {1, 2, 3}\n\n# Set operations\na = {1, 2, 3}\nb = {3, 4, 5}\nprint(a | b)  # union: {1,2,3,4,5}\nprint(a & b)  # intersection: {3}\nprint(a - b)  # difference: {1,2}\n```"}},
            {"title": "Set Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 25,
             "content_data": {
                 "question": "What does `{1, 2, 3} & {2, 3, 4}` return?",
                 "options": [
                     {"id": "a", "label": "{1, 2, 3, 4}"},
                     {"id": "b", "label": "{2, 3}"},
                     {"id": "c", "label": "{1, 4}"},
                     {"id": "d", "label": "{1, 2, 3}"},
                 ], "correct_option": "b",
                 "hints": ["The `&` operator finds common elements.", "Both sets share 2 and 3."],
                 "explanation": "& is intersection - returns elements that appear in BOTH sets: {2, 3}.",
             }},
        ],
    },
    {
        "title": "Dictionary Advanced",
        "order": 3,
        "steps": [
            {"title": "Dictionary Methods", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Dictionary Advanced\n\n```python\nuser = {\n    \"name\": \"Alice\",\n    \"age\": 30,\n    \"skills\": [\"Python\", \"SQL\"]\n}\n\n# Methods\nprint(user.keys())    # dict_keys(['name', 'age', 'skills'])\nprint(user.values())  # dict_values(['Alice', 30, ['Python', 'SQL']])\nprint(user.items())   # dict_items([('name', 'Alice'), ...])\n\n# Safe access\nage = user.get(\"age\", 0)  # returns 0 if missing\n\n# Update\nuser.update({\"city\": \"Istanbul\", \"age\": 31})\n```\n\n## Dictionary Comprehension\n```python\nsquares = {x: x**2 for x in range(5)}\n# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}\n```"}},
            {"title": "Word Counter", "step_type": StepType.CODE, "order": 1, "xp_reward": 45,
             "content_data": {
                 "instruction": "Write a program that counts the frequency of each word in a sentence. Use a dictionary.\n\nExample:\nsentence = \"the cat and the dog and the bird\"\nOutput: {'the': 3, 'cat': 1, 'and': 2, 'dog': 1, 'bird': 1}",
                 "starter_code": "sentence = \"the cat and the dog and the bird\"\nwords = sentence.split()\nword_count = {}\nfor word in words:\n    if word in word_count:\n        word_count[word] += 1\n    else:\n        word_count[word] = 1\nprint(word_count)",
                 "solution": "sentence = \"the cat and the dog and the bird\"\nwords = sentence.split()\nword_count = {}\nfor word in words:\n    if word in word_count:\n        word_count[word] += 1\n    else:\n        word_count[word] = 1\nprint(word_count)",
                 "expected_output": "{'the': 3, 'cat': 1, 'and': 2, 'dog': 1, 'bird': 1}",
                 "compare_mode": "contains",
                 "hints": ["Split the sentence into words with `split()`.", "Use dictionary to count: `count[word] = count.get(word, 0) + 1`"],
             }},
        ],
    },
]

# ─────────────────────────────────────────────
# COURSE: Intermediate 1 — Functions & Modules
# ─────────────────────────────────────────────
I1_COURSE = {
    "title": "Functions & Modules",
    "description": "Advanced function concepts: args/kwargs, scope, lambda, standard library, and package management.",
    "language": "Python",
}

I1_SECTIONS = [
    {
        "title": "Advanced Functions",
        "order": 0,
        "steps": [
            {"title": "*args and **kwargs", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# *args and **kwargs\n\n## *args (variable positional arguments)\n```python\ndef sum_all(*args):\n    return sum(args)\n\nprint(sum_all(1, 2, 3))     # 6\nprint(sum_all(10, 20))      # 30\n```\n\n## **kwargs (variable keyword arguments)\n```python\ndef print_info(**kwargs):\n    for key, value in kwargs.items():\n        print(f\"{key}: {value}\")\n\nprint_info(name=\"Alice\", age=30, city=\"NYC\")\n```\n\n## Scope (LEGB rule)\n- **L**ocal: inside the function\n- **E**nclosing: outer functions\n- **G**lobal: module level\n- **B**uilt-in: Python builtins"}},
            {"title": "Scope & Args Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "What does this print?\n```python\ndef test(*args):\n    return sum(args)\n\nprint(test(1, 2, 3, 4))\n```",
                 "options": [
                     {"id": "a", "label": "10"},
                     {"id": "b", "label": "1234"},
                     {"id": "c", "label": "(1, 2, 3, 4)"},
                     {"id": "d", "label": "Error"},
                 ], "correct_option": "a",
                 "hints": ["*args collects all arguments into a tuple.", "sum() adds all elements."],
                 "explanation": "*args collects (1,2,3,4) into a tuple. sum() = 10.",
             }},
        ],
    },
    {
        "title": "Lambda & Map/Filter",
        "order": 1,
        "steps": [
            {"title": "Lambda Functions", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Lambda Functions\n\nOne-line anonymous functions.\n\n```python\n# Regular function\ndef double(x):\n    return x * 2\n\n# Lambda equivalent\ndouble = lambda x: x * 2\n```\n\n## map() - apply to each element\n```python\nnumbers = [1, 2, 3]\ndoubled = list(map(lambda x: x * 2, numbers))\nprint(doubled)  # [2, 4, 6]\n```\n\n## filter() - keep matching elements\n```python\nnumbers = [1, 2, 3, 4, 5]\nevens = list(filter(lambda x: x % 2 == 0, numbers))\nprint(evens)  # [2, 4]\n```"}},
            {"title": "Lambda Practice", "step_type": StepType.CODE, "order": 1, "xp_reward": 35,
             "content_data": {
                 "instruction": "Use `map()` with a lambda to convert a list of temperatures from Celsius to Fahrenheit. Formula: F = C * 9/5 + 32\n\nPrint the resulting list.",
                 "starter_code": "celsius = [0, 10, 20, 30, 40]\nfahrenheit = list(map(lambda c: c * 9/5 + 32, celsius))\nprint(fahrenheit)",
                 "solution": "celsius = [0, 10, 20, 30, 40]\nfahrenheit = list(map(lambda c: c * 9/5 + 32, celsius))\nprint(fahrenheit)",
                 "compare_mode": "contains",
                 "expected_output": "[32.0, 50.0, 68.0, 86.0, 104.0]",
                 "hints": ["Formula: `c * 9/5 + 32`", "Wrap map() with list() to get a list."],
             }},
        ],
    },
    {
        "title": "Standard Library",
        "order": 2,
        "steps": [
            {"title": "Useful Standard Modules", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Standard Library\n\n## math\n```python\nimport math\nprint(math.pi)          # 3.14159...\nprint(math.sqrt(16))    # 4.0\nprint(math.floor(3.7))  # 3\n```\n\n## random\n```python\nimport random\nprint(random.randint(1, 10))   # random int\nprint(random.choice([\"a\",\"b\",\"c\"]))  # random pick\n```\n\n## datetime\n```python\nfrom datetime import datetime\nnow = datetime.now()\nprint(now.strftime(\"%Y-%m-%d %H:%M\"))\n```"}},
            {"title": "Date Formatting", "step_type": StepType.CODE, "order": 1, "xp_reward": 30,
             "content_data": {
                 "instruction": "Print the current date and time in the format: \"Today is YYYY-MM-DD and the time is HH:MM\".",
                 "starter_code": "from datetime import datetime\nnow = datetime.now()\nprint(f\"Today is {now.strftime('%Y-%m-%d')} and the time is {now.strftime('%H:%M')}\")",
                 "solution": "from datetime import datetime\nnow = datetime.now()\nprint(f\"Today is {now.strftime('%Y-%m-%d')} and the time is {now.strftime('%H:%M')}\")",
                 "compare_mode": "contains", "expected_output": "Today is",
                 "hints": ["strftime('%Y-%m-%d') for date", "strftime('%H:%M') for time"],
             }},
        ],
    },
]

# ─────────────────────────────────────────────
# COURSE: Intermediate 2 — OOP
# ─────────────────────────────────────────────
I2_COURSE = {
    "title": "Object-Oriented Programming",
    "description": "Master OOP in Python: classes, inheritance, polymorphism, encapsulation, and magic methods.",
    "language": "Python",
}

I2_SECTIONS = [
    {
        "title": "Classes & Objects",
        "order": 0,
        "steps": [
            {"title": "Classes & __init__", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Classes & Objects\n\n```python\nclass Dog:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n\n    def bark(self):\n        print(f\"{self.name} says Woof!\")\n\n# Create object\nmy_dog = Dog(\"Rex\", 3)\nprint(my_dog.name)  # Rex\nmy_dog.bark()       # Rex says Woof!\n```\n\n- `__init__` is the constructor\n- `self` refers to the current instance\n- Methods need `self` as first parameter"}},
            {"title": "Class Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "What does `self` represent in a Python class method?",
                 "options": [
                     {"id": "a", "label": "The class itself"},
                     {"id": "b", "label": "The current instance/object"},
                     {"id": "c", "label": "The parent class"},
                     {"id": "d", "label": "Nothing special"},
                 ], "correct_option": "b",
                 "hints": ["__init__ receives `self` as the first parameter.", "Through `self` you access instance attributes."],
                 "explanation": "`self` is the current instance of the class. It gives access to instance variables and methods.",
             }},
        ],
    },
    {
        "title": "Inheritance & Polymorphism",
        "order": 1,
        "steps": [
            {"title": "Inheritance", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Inheritance\n\nA class can **inherit** attributes and methods from another class.\n\n```python\nclass Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        pass  # override in subclass\n\nclass Cat(Animal):  # Cat inherits from Animal\n    def speak(self):\n        print(f\"{self.name} says Meow!\")\n\nclass Dog(Animal):\n    def speak(self):\n        print(f\"{self.name} says Woof!\")\n\n# Polymorphism\nanimals = [Cat(\"Whiskers\"), Dog(\"Rex\")]\nfor a in animals:\n    a.speak()  # Each calls its own version\n```"}},
            {"title": "Inheritance Practice", "step_type": StepType.CODE, "order": 1, "xp_reward": 40,
             "content_data": {
                 "instruction": "Create a base class `Vehicle` with `__init__(self, brand, year)` and a method `info()` that returns brand and year.\n\nThen create a subclass `Car` that adds an attribute `doors` and overrides `info()` to include doors.\n\nPrint the info of a Car object.",
                 "starter_code": "class Vehicle:\n    def __init__(self, brand, year):\n        self.brand = brand\n        self.year = year\n\n    def info(self):\n        return f\"{self.brand} ({self.year})\"\n\nclass Car(Vehicle):\n    def __init__(self, brand, year, doors):\n        super().__init__(brand, year)\n        self.doors = doors\n\n    def info(self):\n        return f\"{self.brand} ({self.year}) - {self.doors} doors\"\n\nmy_car = Car(\"Toyota\", 2022, 4)\nprint(my_car.info())",
                 "solution": "class Vehicle:\n    def __init__(self, brand, year):\n        self.brand = brand\n        self.year = year\n    def info(self):\n        return f\"{self.brand} ({self.year})\"\n\nclass Car(Vehicle):\n    def __init__(self, brand, year, doors):\n        super().__init__(brand, year)\n        self.doors = doors\n    def info(self):\n        return f\"{self.brand} ({self.year}) - {self.doors} doors\"\n\nmy_car = Car(\"Toyota\", 2022, 4)\nprint(my_car.info())",
                 "expected_output": "Toyota (2022) - 4 doors",
                 "compare_mode": "contains",
                 "hints": ["Use `super().__init__()` to call parent constructor.", "Override `info()` in Car to include doors."],
             }},
        ],
    },
]

# ─────────────────────────────────────────────
# COURSE: Intermediate 3 — Error Handling & File I/O
# ─────────────────────────────────────────────
I3_COURSE = {
    "title": "Error Handling & File I/O",
    "description": "Robust error handling with try/except, custom exceptions, and file operations (TXT, JSON, CSV).",
    "language": "Python",
}

I3_SECTIONS = [
    {
        "title": "Try/Except Blocks",
        "order": 0,
        "steps": [
            {"title": "Exception Handling", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# Exception Handling\n\n```python\ntry:\n    number = int(input(\"Enter a number: \"))\n    result = 10 / number\n    print(f\"Result: {result}\")\nexcept ValueError:\n    print(\"That's not a valid number!\")\nexcept ZeroDivisionError:\n    print(\"Cannot divide by zero!\")\nexcept Exception as e:\n    print(f\"Unexpected error: {e}\")\nelse:\n    print(\"No errors occurred!\")\nfinally:\n    print(\"This always runs.\")\n```\n\n- `try`: code that might fail\n- `except`: handle specific errors\n- `else`: runs if no error\n- `finally`: always runs"}},
            {"title": "Error Quiz", "step_type": StepType.QUIZ, "order": 1, "xp_reward": 20,
             "content_data": {
                 "question": "Which block runs ONLY if no exception occurs?",
                 "options": [
                     {"id": "a", "label": "try"},
                     {"id": "b", "label": "except"},
                     {"id": "c", "label": "else"},
                     {"id": "d", "label": "finally"},
                 ], "correct_option": "c",
                 "hints": ["finally always runs.", "except runs only on error.", "else runs only on success."],
                 "explanation": "The `else` block runs when no exception is raised in the try block.",
             }},
            {"title": "Safe Division", "step_type": StepType.CODE, "order": 2, "xp_reward": 35,
             "content_data": {
                 "instruction": "Write a program that safely divides two numbers. Handle ValueError (non-numeric input) and ZeroDivisionError. Print the result or an appropriate error message.",
                 "starter_code": "try:\n    a = float(input(\"Enter first number: \"))\n    b = float(input(\"Enter second number: \"))\n    result = a / b\n    print(f\"Result: {result}\")\nexcept ValueError:\n    print(\"Please enter valid numbers.\")\nexcept ZeroDivisionError:\n    print(\"Cannot divide by zero!\")",
                 "solution": "try:\n    a = float(input(\"Enter first number: \"))\n    b = float(input(\"Enter second number: \"))\n    result = a / b\n    print(f\"Result: {result}\")\nexcept ValueError:\n    print(\"Please enter valid numbers.\")\nexcept ZeroDivisionError:\n    print(\"Cannot divide by zero!\")",
                 "compare_mode": "contains",
                 "expected_output": "Result:",
                 "hints": ["Use `float()` for decimal support.", "ZeroDivisionError when dividing by zero."],
             }},
        ],
    },
    {
        "title": "File Operations",
        "order": 1,
        "steps": [
            {"title": "Reading & Writing Files", "step_type": StepType.THEORY, "order": 0, "xp_reward": 10,
             "content_data": {"body_markdown": "# File Operations\n\n## Text Files\n```python\n# Write\nwith open(\"hello.txt\", \"w\") as f:\n    f.write(\"Hello, World!\\n\")\n    f.writelines([\"Line 2\\n\", \"Line 3\\n\"])\n\n# Read\nwith open(\"hello.txt\", \"r\") as f:\n    content = f.read()        # whole file\n    lines = f.readlines()     # list of lines\n    for line in f:            # iterate\n        print(line)\n```\n\n## Modes\n- `\"r\"` - read (default)\n- `\"w\"` - write (overwrites)\n- `\"a\"` - append\n- `\"r+\"` - read and write\n\n## Context Manager (`with`)\nAutomatically closes the file, even if an error occurs."}},
            {"title": "JSON & CSV", "step_type": StepType.THEORY, "order": 1, "xp_reward": 10,
             "content_data": {"body_markdown": "# JSON & CSV Files\n\n## JSON (JavaScript Object Notation)\n```python\nimport json\n\ndata = {\"name\": \"Alice\", \"age\": 30, \"skills\": [\"Python\"]}\n\n# Write\nwith open(\"data.json\", \"w\") as f:\n    json.dump(data, f, indent=2)\n\n# Read\nwith open(\"data.json\", \"r\") as f:\n    loaded = json.load(f)\n    print(loaded[\"name\"])  # Alice\n```\n\n## CSV (Comma-Separated Values)\n```python\nimport csv\n\n# Write\nwith open(\"users.csv\", \"w\", newline=\"\") as f:\n    writer = csv.writer(f)\n    writer.writerow([\"name\", \"age\"])\n    writer.writerow([\"Alice\", 30])\n\n# Read\nwith open(\"users.csv\", \"r\") as f:\n    reader = csv.reader(f)\n    for row in reader:\n        print(row)  # ['name', 'age'], ['Alice', '30']\n```"}},
            {"title": "JSON Read/Write", "step_type": StepType.CODE, "order": 2, "xp_reward": 45,
             "content_data": {
                 "instruction": "Create a dictionary with keys 'name', 'age', and 'city'. Write it to a JSON file named 'profile.json', then read it back and print the name.",
                 "starter_code": "import json\n\nprofile = {\"name\": \"Alice\", \"age\": 30, \"city\": \"Istanbul\"}\n\nwith open(\"profile.json\", \"w\") as f:\n    json.dump(profile, f)\n\nwith open(\"profile.json\", \"r\") as f:\n    data = json.load(f)\n    print(data[\"name\"])",
                 "solution": "import json\nprofile = {\"name\": \"Alice\", \"age\": 30, \"city\": \"Istanbul\"}\nwith open(\"profile.json\", \"w\") as f:\n    json.dump(profile, f)\nwith open(\"profile.json\", \"r\") as f:\n    data = json.load(f)\n    print(data[\"name\"])",
                 "expected_output": "Alice",
                 "compare_mode": "trim",
                 "hints": ["Use `json.dump(data, file)` to write.", "Use `json.load(file)` to read.", "Access fields like `data['name']`."],
             }},
        ],
    },
]


# ─────────────────────────────────────────────
# Seed logic
# ─────────────────────────────────────────────
async def _seed_course(db, title, description, language, sections_data):
    result = await db.execute(select(Course).where(Course.title == title))
    if result.scalar_one_or_none():
        logger.info("  Skipping (exists): %s", title)
        return None

    course = Course(title=title, description=description, language=language)
    db.add(course)
    await db.flush()
    await db.refresh(course)

    total = 0
    for sec_data in sections_data:
        section = Section(course_id=course.id, title=sec_data["title"], order=sec_data["order"])
        db.add(section)
        await db.flush()
        await db.refresh(section)

        for step_data in sec_data["steps"]:
            step = Step(
                section_id=section.id,
                title=step_data["title"],
                step_type=step_data["step_type"],
                order=step_data["order"],
                xp_reward=step_data["xp_reward"],
                content_data=step_data.get("content_data"),
            )
            db.add(step)
            total += 1

    await db.flush()
    logger.info("  Created: %s (%d sections, %d steps)", title, len(sections_data), total)
    return course


async def seed_roadmap():
    async with async_session_maker() as db:
        # 1. Create 5 new courses
        b2 = await _seed_course(db, B2_COURSE["title"], B2_COURSE["description"], B2_COURSE["language"], B2_SECTIONS)
        b3 = await _seed_course(db, B3_COURSE["title"], B3_COURSE["description"], B3_COURSE["language"], B3_SECTIONS)
        i1 = await _seed_course(db, I1_COURSE["title"], I1_COURSE["description"], I1_COURSE["language"], I1_SECTIONS)
        i2 = await _seed_course(db, I2_COURSE["title"], I2_COURSE["description"], I2_COURSE["language"], I2_SECTIONS)
        i3 = await _seed_course(db, I3_COURSE["title"], I3_COURSE["description"], I3_COURSE["language"], I3_SECTIONS)

        # 2. Find existing courses for the path
        existing_python = await db.execute(select(Course).where(Course.title == "Python Fundamentals"))
        py_course = existing_python.scalar_one_or_none()
        if not py_course:
            logger.error("Python Fundamentals not found! Run seed_data.py first.")
            return

        # 3. Create or get LearningPath
        existing_path = await db.execute(select(LearningPath).where(LearningPath.title == "Python Developer Roadmap"))
        path = existing_path.scalar_one_or_none()

        if path is None:
            path = LearningPath(
                title="Python Developer Roadmap",
                description="A complete journey from programming beginner to job-ready Python developer. 6 levels of hands-on learning.",
                language="Python",
                icon="\U0001F4CD",
                order=0,
            )
            db.add(path)
            await db.flush()

            # Create PathLevels
            levels = [
                (py_course, "Beginner 1: Python Fundamentals", 0, 0),     # First level, always unlocked
                (b2, "Beginner 2: Logic & Loops Deep Dive", 1, 75),
                (b3, "Beginner 3: Data Structures Mastery", 2, 75),
                (i1, "Intermediate 1: Functions & Modules", 3, 75),
                (i2, "Intermediate 2: Object-Oriented Programming", 4, 75),
                (i3, "Intermediate 3: Error Handling & File I/O", 5, 75),
            ]

            for course, level_name, order, required_pct in levels:
                if course is None:
                    continue
                pl = PathLevel(
                    path_id=path.id,
                    course_id=course.id,
                    level_name=level_name,
                    order=order,
                    required_progress_pct=required_pct,
                )
                db.add(pl)

            await db.flush()
            logger.info("LearningPath created: Python Developer Roadmap (6 levels)")
            logger.info("  Level 0: %s (always unlocked)", py_course.title)
            for c, ln, o, _ in levels[1:]:
                if c:
                    logger.info("  Level %d: %s -> requires %d%% of previous", o, c.title, 75)
        else:
            logger.info("LearningPath already exists, skipping.")

        await db.commit()
        logger.info("=" * 50)
        logger.info("ROADMAP SEED COMPLETE!")
        logger.info("  6 levels, 5 new courses, 1 Learning Path")
        logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_roadmap())
