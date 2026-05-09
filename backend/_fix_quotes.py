import re

with open("seed_rust.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix pattern: after '''))},\n\n            {"title" 
# the ] is missing at the end of steps array
# We need to find where '''))}, appears and add ] before the closing }

# Strategy: replace '''))}, with '''))]},  -- this closes steps array
# but careful: body_md('''...''') is a function call that returns a dict
# so the structure is: t("title", cd=body_md('''...''')),
# After each step, there should be a ] to close steps:[

content = content.replace("'''))},\n\n            {", "'''))]},\n\n            {")
content = content.replace("'''))},\n\n        ])", "'''))]},\n\n        ])")
content = content.replace("'''))},\n        ]", "'''))]},\n        ]")

# Also fix where single step sections end before the parent dict closes
# Need to be more careful here

with open("seed_rust.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed!")
