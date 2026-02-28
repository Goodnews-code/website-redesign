#!/usr/bin/env python3
"""
Adds the 22 missing JesusWalk URLs to the JW_URL_MAP
already injected into page_generator.py, then regenerates all pages.
"""
import re
import os
import subprocess

generator_path = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop\joyful-heart-redesign\scraper\page_generator.py"

# These are the 22 URLs that were still falling back to external
# Map every one to the appropriate All Studies section anchor
MISSING = {
    "https://www.jesuswalk.com/2peter/":              "#general-letters",
    "https://www.jesuswalk.com/7-last-words/":        "#gospels",
    "https://www.jesuswalk.com/advent/":              "#topical",
    "https://www.jesuswalk.com/ascent/":              "#old-testament",
    "https://www.jesuswalk.com/christ-power/":        "#topical",
    "https://www.jesuswalk.com/christmas-incarnation/": "#topical",
    "https://www.jesuswalk.com/church/":              "#acts",
    "https://www.jesuswalk.com/gideon/":              "#old-testament",
    "https://www.jesuswalk.com/glory/":               "#topical",
    "https://www.jesuswalk.com/joshua/":              "#old-testament",
    "https://www.jesuswalk.com/kingdom/":             "#topical",
    "https://www.jesuswalk.com/lamb-revelation/":     "#revelation",
    "https://www.jesuswalk.com/lords-supper":         "#topical",   # no trailing slash variant
    "https://www.jesuswalk.com/names-god/":           "#topical",
    "https://www.jesuswalk.com/names-jesus/":         "#topical",
    "https://www.jesuswalk.com/paul/":                "#pauls-letters",
    "https://www.jesuswalk.com/peter/":               "#general-letters",
    "https://www.jesuswalk.com/rebuild/":             "#old-testament",
    "https://www.jesuswalk.com/spirit/":              "#topical",
    "https://www.jesuswalk.com/thessalonians/":       "#pauls-letters",
}

# Build the additional entries as Python dict literal lines
extra_entries = "\n".join(
    f"    {repr(url)}: '../../jesuswalk-redesign/pages/all-studies.html{anchor}',"
    for url, anchor in sorted(MISSING.items())
)

with open(generator_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the end of JW_URL_MAP dict (the last } before the first line that follows the map)
# The map was injected as JW_URL_MAP = { ... }
# We look for the closing brace of the map and insert our entries just before it

# Strategy: find the pattern "        JW_URL_MAP = {" and then find its closing "        }"
# Insert the new entries just before the closing brace

# Find map block
map_start = content.find("        JW_URL_MAP = {")
if map_start == -1:
    print("ERROR: Could not find JW_URL_MAP in file!")
    exit(1)

# Find the matching closing brace (at the same indent level = 8 spaces)
# After the opening {, we look for the next line that starts with "        }" 
map_region = content[map_start:]
# Find the closing brace line "        }" that ends the dict
closing_match = re.search(r'\n        \}', map_region)
if not closing_match:
    print("ERROR: Could not find closing brace of JW_URL_MAP!")
    exit(1)

close_pos = map_start + closing_match.start()

# Check if entries are already there
already_added = "lords-supper'" in content[map_start:close_pos]
if already_added:
    print("Missing entries already present in map — skipping injection")
else:
    # Insert extra entries just before the closing brace
    insert_point = close_pos + 1  # after the \n
    new_content = content[:insert_point] + extra_entries + "\n" + content[insert_point:]

    with open(generator_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Injected {len(MISSING)} missing URL entries into JW_URL_MAP")

# Now regenerate pages
print("\nRegenerating pages...")
result = subprocess.run(
    ["python", generator_path],
    cwd=os.path.dirname(generator_path),
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("ERRORS:", result.stderr[-500:])
else:
    print("Pages regenerated successfully!")
