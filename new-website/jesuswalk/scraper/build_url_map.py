#!/usr/bin/env python3
"""
Build and print a clean URL→local_page mapping as a Python dict
that we can embed into page_generator.py.
"""
import os, json, re

base = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop"
pages_dir = os.path.join(base, "jesuswalk-redesign", "pages")
scraped_dir = os.path.join(base, "joyful-heart-redesign", "scraped_data", "pages")

url_map = {}

# Map main category root URLs to our special pages
hardcoded = {
    "https://www.jesuswalk.com/":                      "../../jesuswalk-redesign/index.html",
    "https://www.jesuswalk.com/bible-study/":          "bible-study-tips.html",
    "https://www.jesuswalk.com/books/":                "books.html",
    "https://www.jesuswalk.com/podcast/":              "podcast.html",
    "https://www.jesuswalk.com/beginning/":            "beginning.html",
    "https://www.jesuswalk.com/discipleship/":         "discipleship.html",
    "https://www.jesuswalk.com/lords-supper/":         "jw_lords-supper.html",
    "https://www.jesuswalk.com/christian-symbols/":    "jw_christian-symbols.html",
}
url_map.update(hardcoded)

# Scrape individual article urls
for fname in sorted(os.listdir(scraped_dir)):
    if not fname.startswith("jw_") or not fname.endswith(".json"):
        continue
    fpath = os.path.join(scraped_dir, fname)
    with open(fpath, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    url = data.get("url", "")
    html_name = fname.replace(".json", ".html")
    html_path = os.path.join(pages_dir, html_name)
    if url and os.path.exists(html_path):
        # Use relative path from Joyful Heart pages/ dir → JesusWalk pages/
        url_map[url] = f"../../jesuswalk-redesign/pages/{html_name}"

# Also build a prefix map: jesuswalk.com/abraham/ → all-studies.html#old-testament
category_prefix_map = {
    "https://www.jesuswalk.com/abraham/":       "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/jacob/":         "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/moses/":         "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/samuel/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/david/":         "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/solomon/":       "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/elijah/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/psalms/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/isaiah/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/daniel/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/lamb/":          "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/john/":          "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/luke/":          "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/mark/":          "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/sermon/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/parables/":      "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/7lastwords/":    "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/resurrection/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/acts/":          "../../jesuswalk-redesign/pages/all-studies.html#acts",
    "https://www.jesuswalk.com/early-church/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/romans/":        "../../jesuswalk-redesign/pages/all-studies.html#pauls-letters",
    "https://www.jesuswalk.com/1corinthians/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/2corinthians/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/galatians/":     "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/ephesians/":     "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/philippians/":   "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/colossians/":    "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/1thessalonians/":"../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/timothy/":       "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/hebrews/":       "../../jesuswalk-redesign/pages/all-studies.html#general-letters",
    "https://www.jesuswalk.com/james/":         "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/1peter/":        "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/123john/":       "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/revelation/":    "../../jesuswalk-redesign/pages/all-studies.html#revelation",
    "https://www.jesuswalk.com/grace/":         "../../jesuswalk-redesign/pages/all-studies.html#topical",
    "https://www.jesuswalk.com/holy-spirit/":   "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/greatprayers/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/humility/":      "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/names-of-god/":  "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/manifesto/":     "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/proverbs/":      "../../jesuswalk-redesign/pages/all-studies.html",
    "https://www.jesuswalk.com/voice/":         "../../jesuswalk-redesign/pages/all-studies.html",
}

# Print the final combined dict
all_map = {}
all_map.update(url_map)
all_map.update(category_prefix_map)

print("JW_URL_MAP = {")
for k, v in sorted(all_map.items()):
    print(f"    {repr(k)}: {repr(v)},")
print("}")
print(f"\n# Total entries: {len(all_map)}")
