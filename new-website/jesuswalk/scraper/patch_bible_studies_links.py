#!/usr/bin/env python3
"""
Patches page_generator.py to update Bible Studies links
to point to local JesusWalk redesign pages.
"""
import os
import json
import re

generator_path = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop\joyful-heart-redesign\scraper\page_generator.py"
jw_pages_dir   = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop\jesuswalk-redesign\pages"
jw_scraped_dir = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop\joyful-heart-redesign\scraped_data\pages"

# ── 1. Build URL → local path map ────────────────────────────────────────────

# Base anchor map: series root URLs → all-studies with section anchor
ANCHOR_MAP = {
    "https://www.jesuswalk.com/abraham/":        "#old-testament",
    "https://www.jesuswalk.com/jacob/":          "#old-testament",
    "https://www.jesuswalk.com/moses/":          "#old-testament",
    "https://www.jesuswalk.com/samuel/":         "#old-testament",
    "https://www.jesuswalk.com/david/":          "#old-testament",
    "https://www.jesuswalk.com/solomon/":        "#old-testament",
    "https://www.jesuswalk.com/elijah/":         "#old-testament",
    "https://www.jesuswalk.com/psalms/":         "#old-testament",
    "https://www.jesuswalk.com/isaiah/":         "#old-testament",
    "https://www.jesuswalk.com/daniel/":         "#old-testament",
    "https://www.jesuswalk.com/lamb/":           "#old-testament",
    "https://www.jesuswalk.com/john/":           "#gospels",
    "https://www.jesuswalk.com/luke/":           "#gospels",
    "https://www.jesuswalk.com/mark/":           "#gospels",
    "https://www.jesuswalk.com/sermon/":         "#gospels",
    "https://www.jesuswalk.com/parables/":       "#gospels",
    "https://www.jesuswalk.com/7lastwords/":     "#gospels",
    "https://www.jesuswalk.com/resurrection/":   "#gospels",
    "https://www.jesuswalk.com/acts/":           "#acts",
    "https://www.jesuswalk.com/early-church/":   "#acts",
    "https://www.jesuswalk.com/romans/":         "#pauls-letters",
    "https://www.jesuswalk.com/1corinthians/":   "#pauls-letters",
    "https://www.jesuswalk.com/2corinthians/":   "#pauls-letters",
    "https://www.jesuswalk.com/galatians/":      "#pauls-letters",
    "https://www.jesuswalk.com/ephesians/":      "#pauls-letters",
    "https://www.jesuswalk.com/philippians/":    "#pauls-letters",
    "https://www.jesuswalk.com/colossians/":     "#pauls-letters",
    "https://www.jesuswalk.com/1thessalonians/": "#pauls-letters",
    "https://www.jesuswalk.com/timothy/":        "#pauls-letters",
    "https://www.jesuswalk.com/hebrews/":        "#general-letters",
    "https://www.jesuswalk.com/james/":          "#general-letters",
    "https://www.jesuswalk.com/1peter/":         "#general-letters",
    "https://www.jesuswalk.com/123john/":        "#general-letters",
    "https://www.jesuswalk.com/revelation/":     "#revelation",
    "https://www.jesuswalk.com/grace/":          "#topical",
    "https://www.jesuswalk.com/holy-spirit/":    "#topical",
    "https://www.jesuswalk.com/greatprayers/":   "#topical",
    "https://www.jesuswalk.com/humility/":       "#topical",
    "https://www.jesuswalk.com/names-of-god/":   "#topical",
    "https://www.jesuswalk.com/manifesto/":      "#topical",
    "https://www.jesuswalk.com/proverbs/":       "#topical",
    "https://www.jesuswalk.com/voice/":          "#topical",
    "https://www.jesuswalk.com/lords-supper/":   "#topical",
    "https://www.jesuswalk.com/christian-symbols/": "#topical",
}

JW_URL_MAP = {}
# Add series root → all-studies catalog
for url, anchor in ANCHOR_MAP.items():
    JW_URL_MAP[url] = f"../../jesuswalk-redesign/pages/all-studies.html{anchor}"

# Add special pages
JW_URL_MAP.update({
    "https://www.jesuswalk.com/":              "../../jesuswalk-redesign/index.html",
    "https://www.jesuswalk.com/beginning/":    "../../jesuswalk-redesign/pages/beginning.html",
    "https://www.jesuswalk.com/discipleship/": "../../jesuswalk-redesign/pages/discipleship.html",
    "https://www.jesuswalk.com/books/":        "../../jesuswalk-redesign/pages/books.html",
    "https://www.jesuswalk.com/podcast/":      "../../jesuswalk-redesign/pages/podcast.html",
    "https://www.jesuswalk.com/bible-study/":  "../../jesuswalk-redesign/pages/bible-study-tips.html",
})

# Add individual article pages from scraped JSON
for fname in sorted(os.listdir(jw_scraped_dir)):
    if not fname.startswith("jw_") or not fname.endswith(".json"):
        continue
    try:
        with open(os.path.join(jw_scraped_dir, fname), "r", encoding="utf-8") as fh:
            data = json.load(fh)
        url = data.get("url", "")
        html_name = fname.replace(".json", ".html")
        full_path = os.path.join(jw_pages_dir, html_name)
        if url and os.path.exists(full_path):
            JW_URL_MAP[url] = f"../../jesuswalk-redesign/pages/{html_name}"
    except Exception as e:
        print(f"  WARN: {fname}: {e}")

print(f"Built URL map with {len(JW_URL_MAP)} entries")
matched = sum(1 for v in JW_URL_MAP.values() if "all-studies" not in v and "index" not in v)
print(f"  {matched} direct article page links")
print(f"  {len(JW_URL_MAP)-matched} catalog/home links")

# ── 2. Read and patch page_generator.py ──────────────────────────────────────

with open(generator_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find the section with the old card generation code and replace it
# The old code generates cards with: href="{escape(link)}" ... target="_blank" rel="noopener"
# We replace just the card generation block inside the for study in studies loop

OLD_BLOCK = '''                    total_studies += 1

                    cards_html += f\'\'\'
        <a href="{escape(link)}" class="study-card" style="text-decoration: none; color: inherit;" target="_blank" rel="noopener">
          <div class="study-card-category">{section["label"]}</div>
          <h3>{escape(name)}</h3>
          {f\'<p>{escape(desc)}</p>\' if desc else \'\'}
          <div class="study-card-meta"><span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            Start Study \u2192
          </span></div>
        </a>\'\'\''''

NEW_BLOCK = '''                    total_studies += 1

                    # Resolve to local redesign page or fall back to external
                    local_link = JW_URL_MAP.get(orig_link)
                    if local_link:
                        link_attrs = f\'href="{local_link}"\\'
                        link_label = "Start Study \\u2192"
                    else:
                        link_attrs = f\'href="{escape(orig_link)}" target="_blank" rel="noopener"\\'
                        link_label = "Open on JesusWalk.com \\u2192"

                    cards_html += f\'\'\'
        <a {link_attrs} class="study-card" style="text-decoration: none; color: inherit;">
          <div class="study-card-category">{section["label"]}</div>
          <h3>{escape(name)}</h3>
          {f\'<p>{escape(desc)}</p>\' if desc else \'\'}
          <div class="study-card-meta"><span>{link_label}</span></div>
        </a>\'\'\''''

# Since we can't reliably do string substitution with all the nested quotes,
# let's use a regex approach on the key differentiating line
# Replace just the "link" variable name with "orig_link" and inject the map lookup

# Step A: Rename `link = study.get("link", "")` to `orig_link = ...`
content_new = content.replace(
    '                    link = study.get("link", "")',
    '                    orig_link = study.get("link", "")'
)
if content_new == content:
    print("WARN: Could not rename 'link' variable — checking alternate form")
    content_new = content.replace(
        "                    link = study.get('link', '')",
        "                    orig_link = study.get('link', '')"
    )

# Step B: Update the `if not text or not link:` guard
content_new = content_new.replace(
    '                    if not text or not link:',
    '                    if not text or not orig_link:'
)

# Step C: Inject the URL map constant and lookup at the top of the function,
# right after the docstring ─ find the function def and inject after it
MAP_INJECTION = '''
        # URL map: original jesuswalk.com URL -> local redesign page
        # Built dynamically from scraped JSON + hardcoded anchors
        JW_URL_MAP = ''' + repr(JW_URL_MAP) + '''

'''

# Find the position just after the docstring of generate_bible_studies_page
DOCSTRING_MARKER = '    def generate_bible_studies_page(self):\r\n        """Generate Bible Studies page dynamically from scraped JesusWalk data."""\r\n'
ALT_MARKER       = '    def generate_bible_studies_page(self):\n        """Generate Bible Studies page dynamically from scraped JesusWalk data."""\n'

inject_done = False
for marker in (DOCSTRING_MARKER, ALT_MARKER):
    if marker in content_new:
        content_new = content_new.replace(
            marker,
            marker + MAP_INJECTION
        )
        inject_done = True
        print("Injected JW_URL_MAP constant into generate_bible_studies_page")
        break

if not inject_done:
    print("WARN: Could not find docstring marker for map injection")

# Step D: Replace the card href line that uses {escape(link)} with map lookup
old_href = '        <a href="{escape(link)}" class="study-card" style="text-decoration: none; color: inherit;" target="_blank" rel="noopener">'
new_href = '''        <a {\'href="\' + (JW_URL_MAP.get(orig_link) or escape(orig_link)) + \'"\' + (\'\' if JW_URL_MAP.get(orig_link) else \' target="_blank" rel="noopener"\')}\
} class="study-card" style="text-decoration: none; color: inherit;">'''

# Simpler: replace the whole card template expression
old_card_a = '        <a href="{escape(link)}" class="study-card" style="text-decoration: none; color: inherit;" target="_blank" rel="noopener">'
new_card_a = '        <a href="{JW_URL_MAP.get(orig_link) or escape(orig_link)}" class="study-card" style="text-decoration: none; color: inherit;">'
content_new = content_new.replace(old_card_a, new_card_a)

# Step E: Update the external icon / label line in old content
old_icon_line = '''            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            Start Study \u2192'''
new_icon_line = '            {"Start Study \u2192" if JW_URL_MAP.get(orig_link) else "Open on JesusWalk.com \u2192"}'
content_new = content_new.replace(old_icon_line, new_icon_line)

# Step F: Update the hero CTA button
old_cta = '  <div class="hero-actions"><a href="https://www.jesuswalk.com/" class="btn btn-primary" target="_blank" rel="noopener">Visit JesusWalk.com</a></div>'
new_cta = '''  <div class="hero-actions">
    <a href="../../jesuswalk-redesign/index.html" class="btn btn-primary">Browse JesusWalk Site</a>
    <a href="../../jesuswalk-redesign/pages/all-studies.html" class="btn btn-secondary">Full Study Catalog</a>
  </div>'''
content_new = content_new.replace(old_cta, new_cta)

# ── 3. Write back ──────────────────────────────────────────────────────────────
with open(generator_path, "w", encoding="utf-8") as f:
    f.write(content_new)

print("\npage_generator.py patched successfully!")
print(f"  Changes: link variable renamed, JW_URL_MAP injected, card href updated, CTA updated")
