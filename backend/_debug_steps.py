import re

with open("seed_rust.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find all '''))}, instances and their surrounding context
parts = content.split("'''))},")
print(f"Found {len(parts)} instances of '''))},")

# For each part (except the last), look at what follows
for idx, part in enumerate(parts):
    if idx == len(parts) - 1:
        continue
    # Get the first 200 chars after this position to see context
    rest = parts[idx+1][:200] if idx+1 < len(parts) else ""
    # Normalize whitespace
    rest = rest.strip()
    print(f"\n--- Instance {idx}: after '''))},")
    print(f"  Next content: {rest[:100]}")
