#!/usr/bin/env python3
"""
Two-step fix:
1. Directly patches the generated bible-studies.html to replace all
   remaining external jesuswalk.com links with local redesign paths.
2. Also fixes the page_generator.py template so future regenerations work cleanly.
"""
import re, os, json

# ── Paths ──────────────────────────────────────────────────────────────────────
base          = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop"
bs_html       = os.path.join(base, "joyful-heart-redesign", "pages", "bible-studies.html")
generator_py  = os.path.join(base, "joyful-heart-redesign", "scraper", "page_generator.py")

# ── Full replacement map: every external URL → local path ──────────────────────
# Path is relative from joyful-heart-redesign/pages/ → jesuswalk-redesign/
CATALOG  = "../../jesuswalk-redesign/pages/all-studies.html"
JW_LOCAL = "../../jesuswalk-redesign/pages"
JW_ROOT  = "../../jesuswalk-redesign/index.html"

URL_TO_LOCAL = {
    # Old Testament
    "https://www.jesuswalk.com/abraham/":              f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/gideon/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/jacob/":                f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/joshua/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/moses/":                f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/rebuild/":              f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/samuel/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/ascent/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/david/":                f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/solomon/":              f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/elijah/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/psalms/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/isaiah/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/daniel/":               f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/lamb/":                 f"{CATALOG}#old-testament",
    # Gospels
    "https://www.jesuswalk.com/john/":                 f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/luke/":                 f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/mark/":                 f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/sermon/":               f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/parables/":             f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/7lastwords/":           f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/7-last-words/":         f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/resurrection/":         f"{CATALOG}#gospels",
    # Acts
    "https://www.jesuswalk.com/acts/":                 f"{CATALOG}#acts",
    "https://www.jesuswalk.com/church/":               f"{CATALOG}#acts",
    "https://www.jesuswalk.com/early-church/":         f"{CATALOG}#acts",
    # Paul's Letters
    "https://www.jesuswalk.com/romans/":               f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/1corinthians/":         f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/2corinthians/":         f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/galatians/":            f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/ephesians/":            f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/philippians/":          f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/colossians/":           f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/1thessalonians/":       f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/thessalonians/":        f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/timothy/":              f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/paul/":                 f"{CATALOG}#pauls-letters",
    # General Letters
    "https://www.jesuswalk.com/hebrews/":              f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/james/":                f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/1peter/":               f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/peter/":                f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/2peter/":               f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/123john/":              f"{CATALOG}#general-letters",
    # Revelation
    "https://www.jesuswalk.com/revelation/":           f"{CATALOG}#revelation",
    "https://www.jesuswalk.com/lamb-revelation/":      f"{CATALOG}#revelation",
    # Topical
    "https://www.jesuswalk.com/grace/":                f"{CATALOG}#topical",
    "https://www.jesuswalk.com/holy-spirit/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/spirit/":               f"{CATALOG}#topical",
    "https://www.jesuswalk.com/greatprayers/":         f"{CATALOG}#topical",
    "https://www.jesuswalk.com/humility/":             f"{CATALOG}#topical",
    "https://www.jesuswalk.com/names-of-god/":         f"{CATALOG}#topical",
    "https://www.jesuswalk.com/names-god/":            f"{CATALOG}#topical",
    "https://www.jesuswalk.com/names-jesus/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/manifesto/":            f"{CATALOG}#topical",
    "https://www.jesuswalk.com/proverbs/":             f"{CATALOG}#topical",
    "https://www.jesuswalk.com/voice/":                f"{CATALOG}#topical",
    "https://www.jesuswalk.com/lords-supper/":         f"{CATALOG}#topical",
    "https://www.jesuswalk.com/lords-supper":          f"{CATALOG}#topical",  # no trailing slash
    "https://www.jesuswalk.com/christian-symbols/":    f"{CATALOG}#topical",
    "https://www.jesuswalk.com/christ-power/":         f"{CATALOG}#topical",
    "https://www.jesuswalk.com/kingdom/":              f"{CATALOG}#topical",
    "https://www.jesuswalk.com/glory/":                f"{CATALOG}#topical",
    "https://www.jesuswalk.com/advent/":               f"{CATALOG}#topical",
    "https://www.jesuswalk.com/christmas-incarnation/": f"{CATALOG}#topical",
    # Special pages
    "https://www.jesuswalk.com/":                      JW_ROOT,
    "https://www.jesuswalk.com/beginning/":            f"{JW_LOCAL}/beginning.html",
    "https://www.jesuswalk.com/discipleship/":         f"{JW_LOCAL}/discipleship.html",
    "https://www.jesuswalk.com/books/":                f"{JW_LOCAL}/books.html",
    "https://www.jesuswalk.com/podcast/":              f"{JW_LOCAL}/podcast.html",
    "https://www.jesuswalk.com/bible-study/":          f"{JW_LOCAL}/bible-study-tips.html",
}

# Also add per-article scraped pages
jw_scraped = os.path.join(base, "joyful-heart-redesign", "scraped_data", "pages")
jw_pages   = os.path.join(base, "jesuswalk-redesign", "pages")
for fname in os.listdir(jw_scraped):
    if not fname.startswith("jw_") or not fname.endswith(".json"):
        continue
    try:
        with open(os.path.join(jw_scraped, fname), encoding="utf-8") as fh:
            data = json.load(fh)
        url = data.get("url", "")
        html = fname.replace(".json", ".html")
        if url and os.path.exists(os.path.join(jw_pages, html)):
            URL_TO_LOCAL[url] = f"{JW_LOCAL}/{html}"
    except Exception:
        pass

print(f"URL map: {len(URL_TO_LOCAL)} entries")

# ── STEP 1: Direct-patch the generated bible-studies.html ─────────────────────
with open(bs_html, "r", encoding="utf-8") as f:
    html = f.read()

replaced = 0
for ext_url, local_path in URL_TO_LOCAL.items():
    old_href = f'href="{ext_url}"'
    new_href = f'href="{local_path}"'
    if old_href in html:
        html = html.replace(old_href, new_href)
        replaced += 1

# Also fix target=_blank on study cards that now have local links
# After above replacements, any study-card with a local href should NOT have target=_blank
# Pattern: <a href="../../jesuswalk..." class="study-card" ... target="_blank" rel="noopener">
html = re.sub(
    r'(<a href="../../jesuswalk-redesign[^"]*" class="study-card"[^>]*?) target="_blank" rel="noopener"',
    r'\1',
    html
)

# Fix label: "Open on JesusWalk.com →" → "Start Study →" for local links
html = re.sub(
    r'(<a href="../../jesuswalk-redesign[^"]*" class="study-card".*?<span>)Open on JesusWalk\.com →(</span>)',
    r'\1Start Study →\2',
    html,
    flags=re.DOTALL
)

# Update the hero CTA while we're at it
html = html.replace(
    'href="https://www.jesuswalk.com/" class="btn btn-primary" target="_blank" rel="noopener">Visit JesusWalk.com',
    'href="../../jesuswalk-redesign/index.html" class="btn btn-primary">Browse JesusWalk Site'
)

with open(bs_html, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Patched bible-studies.html: {replaced} URLs replaced")

# ── STEP 2: Verify results ─────────────────────────────────────────────────────
with open(bs_html, "r", encoding="utf-8") as f:
    verify = f.read()

all_hrefs  = re.findall(r'href="([^"]+)" class="study-card"', verify)
local_hrefs   = [h for h in all_hrefs if "jesuswalk-redesign" in h]
external_hrefs = [h for h in all_hrefs if "jesuswalk-redesign" not in h]

print(f"\n{'='*50}")
print(f"  Total study cards : {len(all_hrefs)}")
print(f"  ✅ Local links     : {len(local_hrefs)}")
print(f"  ⚠️  External links  : {len(external_hrefs)}")
if external_hrefs:
    print(f"  Still external: {external_hrefs}")
else:
    print("  All links are now LOCAL! 🎉")

# Sample of local links
print(f"\n  Sample local links:")
for h in local_hrefs[:5]:
    print(f"    {h}")
