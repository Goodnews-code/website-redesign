#!/usr/bin/env python3
"""
Polish all study card titles and descriptions in:
  - jesuswalk-redesign/pages/all-studies.html
  - joyful-heart-redesign/pages/bible-studies.html

Fixes:
  1. Removes "JesusWalk: " prefix from titles
  2. Cleans up extra spaces from double spaces
  3. Fixes broken parentheses in descriptions
  4. Cleans up ".Spanish version." appended to titles
  5. Shortens overly long titles with clean truncation
  6. Fixes "(for new Christians...)" junk in h3 tags
"""
import re, os

base = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop"

FILES = [
    os.path.join(base, "jesuswalk-redesign", "pages", "all-studies.html"),
    os.path.join(base, "joyful-heart-redesign", "pages", "bible-studies.html"),
]

# ── Title rewrites: exact h3 text → clean version ─────────────────────────────
TITLE_FIXES = {
    # Clean up "JesusWalk: Beginning..." mess
    "JesusWalk:  Beginning the Journey(for new Christians, 12 lessons,  not e-mail).Spanish version.":
        "Beginning the Journey",
    "JesusWalk: Beginning the Journey(for new Christians, 12 lessons, not e-mail).Spanish version.":
        "Beginning the Journey",

    # Listening for God's Voice mess
    "Listening for  God&#x27;s Voice(5 lessons).Spanish version.":
        "Listening for God's Voice",
    "Listening for God&#x27;s Voice(5 lessons).Spanish version.":
        "Listening for God's Voice",

    # Songs of Ascent
    "Songs of  Ascent":
        "Songs of Ascent",

    # Acts titles
    "Acts I:  The Early Church: Acts 1-12":
        "Acts I: The Early Church",
    "Acts II: Apostle  Paul: Passionate Discipleship":
        "Acts II: Apostle Paul",

    # Paul's Letters
    "1  Corinthians":         "1 Corinthians",
    "1 \u0026amp; 2 Timothy,  Titus": "1 &amp; 2 Timothy &amp; Titus",
    "1 \u0026amp; 2  Thessalonians":  "1 &amp; 2 Thessalonians",
    "Colossians and Philemon":        "Colossians &amp; Philemon",

    # Old Testament
    "Rebuild and Renew: The Post-Exilic Books of Ezra, Nehemiah,  Haggai, Zechariah, and Malachi":
        "Rebuild &amp; Renew: Ezra, Nehemiah, Haggai, Zechariah &amp; Malachi",
    "Names and Titles of God":        "Names &amp; Titles of God",
    "Messianic  Scriptures":          "Messianic Scriptures",

    # Gospels / NT
    "7 Last Words of Christ from the Cross": "7 Last Words from the Cross",
    "John&#x27;s Gospel":   "John's Gospel",
    "Luke&#x27;s Gospel":   "Luke's Gospel",
    "Mark&#x27;s Gospel":   "Mark's Gospel",
    "Jesus and the Kingdom":          "Jesus and the Kingdom",
    "Christmas Incarnation":          "The Christmas Incarnation",

    # General Letters
    "John&#x27;s Letters":   "John's Letters",
    "Conquering Lamb of Revelation":  "The Conquering Lamb of Revelation",

    # Topical
    "The  Discipleship Process":      "The Discipleship Process",
    "Glorious  Kingdom":              "The Glorious Kingdom",
    "Great Prayers of the Bible":     "Great Prayers of the Bible",
    "Names and  Titles of Jesus":     "Names &amp; Titles of Jesus",
    "Apostle Peter":                  "The Apostle Peter",
    "Vision for the Church":          "Vision for the Church",

    # Gospels section apostrophes
    "Apostle Peter":         "The Apostle Peter",
}

# ── Description fixes: fix broken parentheses, double spaces ──────────────────
DESC_FIXES = {
    "Ps 120-134)(15 daily meditations":  "Psalms 120-134, 15 daily meditations",
    "Rom 5-8)(8  lessons":               "Romans 5-8, 8 lessons",
    "Rom 5-8)(8 lessons":                "Romans 5-8, 8 lessons",
    "4 weeks,  Advent":                  "4 weeks, Advent season",
    "12  lessons, 1 &amp; 2 Samuel":     "12 lessons, 1 &amp; 2 Samuel",
    "7  lessons, Genesis 25-49":         "7 lessons, Genesis 25-49",
    "12  lessons":                       "12 lessons",
    "35  lessons, brief notes, not e-mail": "35 lessons (brief notes)",
    "140  lessons":                      "140 lessons",
    "4  lessons Judges 6-9":             "4 lessons, Judges 6-9",
    "5  lessons from Ephesians":         "5 lessons from Ephesians",
    "8  lessons":                        "8 lessons",
    "11  lessons":                       "11 lessons",
    "11  Lessons":                       "11 lessons",
    "6  lessons, 1 Kings 1-11":          "6 lessons, 1 Kings 1-11",
    "7  lessons, 1 Kings 17-2 Kings 2":  "7 lessons, 1 Kings 17–2 Kings 2",
    "1,  2, 3 John, 8 lessons":          "1, 2, 3 John — 8 lessons",
    "Acts 13-28; 11 lessons":            "Acts 13–28, 11 lessons",
    "Acts 1-12\n9 lessons":              "Acts 1–12, 9 lessons",
    "brief notes, not e-mail":           "(brief reference notes)",
    "not e-mail":                        "(self-paced)",
}

total_changes = 0

for fpath in FILES:
    if not os.path.exists(fpath):
        print(f"SKIP (not found): {fpath}")
        continue

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    original = html
    changes = 0

    # 1. Apply title fixes inside <h3>...</h3>
    for old, new in TITLE_FIXES.items():
        old_tag = f"<h3>{old}</h3>"
        new_tag = f"<h3>{new}</h3>"
        if old_tag in html:
            html = html.replace(old_tag, new_tag)
            changes += 1
            print(f"  Title: '{old[:50]}' -> '{new}'")

    # 2. Apply description fixes inside <p>...</p>
    for old, new in DESC_FIXES.items():
        old_tag = f"<p>{old}</p>"
        new_tag = f"<p>{new}</p>"
        if old_tag in html:
            html = html.replace(old_tag, new_tag)
            changes += 1
            print(f"  Desc : '{old[:50]}' -> '{new}'")

    # 3. Global cleanup: remove double spaces anywhere in h3/p tags
    def fix_tag_content(m):
        tag = m.group(1)
        content = m.group(2)
        # collapse multiple spaces/newlines
        content = re.sub(r'  +', ' ', content)
        content = re.sub(r'\s*\n\s*', ' ', content)
        content = content.strip()
        return f'<{tag}>{content}</{tag}>'

    new_html = re.sub(r'<(h3|p)>(.*?)</(h3|p)>', fix_tag_content, html, flags=re.DOTALL)
    if new_html != html:
        html = new_html
        changes += 5  # approximate

    # 4. Remove any raw trailing ".Spanish version." anywhere in card text
    html = re.sub(r'\.Spanish version\.', '', html)

    # 5. Fix "JesusWalk: " prefix that remains in any h3
    html = re.sub(r'<h3>JesusWalk:\s+', '<h3>', html)

    # 6. Fix "(for new Christians...)" junk still in title
    html = re.sub(r'\(for new Christians[^)]*\)', '', html)

    # 7. Clean up empty <p></p> or <p> </p>
    html = re.sub(r'<p>\s*</p>', '', html)

    # 8. Fix apostrophe entities &#x27; → proper '
    html = html.replace("&#x27;", "'")

    # Write back if changed
    if html != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(html)
        fname = os.path.basename(fpath)
        print(f"\n[SAVED] {fname} — {changes}+ changes applied")
        total_changes += changes
    else:
        print(f"\n[NO CHANGES] {os.path.basename(fpath)}")

print(f"\nTotal changes across all files: {total_changes}+")
print("Polishing complete!")
