#!/usr/bin/env python3
"""
Completely rewrites all-studies.html with:
1. All 58 card links updated to local jesuswalk-redesign pages
2. A sticky section jump navigation bar
3. A live search/filter input
4. Section anchor scroll-offset fix (for fixed navbar)
5. Smooth scroll behavior
"""
import re, os, json

base     = r"c:\Users\ADMIN\Desktop\J_project\Automated website develop"
src      = os.path.join(base, "jesuswalk-redesign", "pages", "all-studies.html")
jw_scrp  = os.path.join(base, "joyful-heart-redesign", "scraped_data", "pages")
jw_pages = os.path.join(base, "jesuswalk-redesign", "pages")

# URL → local page map
CATALOG = "all-studies.html"
URL_MAP = {
    # OT
    "https://www.jesuswalk.com/abraham/":        f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/gideon/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/jacob/":          f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/joshua/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/moses/":          f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/rebuild/":        f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/samuel/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/ascent/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/david/":          f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/solomon/":        f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/elijah/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/psalms/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/isaiah/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/advent/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/daniel/":         f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/names-god/":      f"{CATALOG}#old-testament",
    "https://www.jesuswalk.com/names-of-god/":   f"{CATALOG}#old-testament",
    # Gospels
    "https://www.jesuswalk.com/christmas-incarnation/": f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/manifesto/":      f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/mark/":           f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/luke/":           f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/john/":           f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/7-last-words/":   f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/parables/":       f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/kingdom/":        f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/resurrection/":   f"{CATALOG}#gospels",
    "https://www.jesuswalk.com/peter/":          f"{CATALOG}#gospels",
    # Acts
    "https://www.jesuswalk.com/early-church/":   f"{CATALOG}#acts",
    "https://www.jesuswalk.com/paul/":           f"{CATALOG}#acts",
    "https://www.jesuswalk.com/church/":         f"{CATALOG}#acts",
    # Paul's Letters
    "https://www.jesuswalk.com/christ-power/":   f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/1corinthians/":   f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/2corinthians/":   f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/galatians/":      f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/ephesians/":      f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/philippians/":    f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/colossians/":     f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/thessalonians/":  f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/1thessalonians/": f"{CATALOG}#pauls-letters",
    "https://www.jesuswalk.com/timothy/":        f"{CATALOG}#pauls-letters",
    # General Letters
    "https://www.jesuswalk.com/hebrews/":        f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/james/":          f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/1peter/":         f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/2peter/":         f"{CATALOG}#general-letters",
    "https://www.jesuswalk.com/123john/":        f"{CATALOG}#general-letters",
    # Revelation
    "https://www.jesuswalk.com/revelation/":     f"{CATALOG}#revelation",
    "https://www.jesuswalk.com/lamb-revelation/": f"{CATALOG}#revelation",
    # Topical
    "https://www.jesuswalk.com/discipleship/":   "discipleship.html",
    "https://www.jesuswalk.com/glory/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/grace/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/greatprayers/":   f"{CATALOG}#topical",
    "https://www.jesuswalk.com/spirit/":         f"{CATALOG}#topical",
    "https://www.jesuswalk.com/holy-spirit/":    f"{CATALOG}#topical",
    "https://www.jesuswalk.com/humility/":       f"{CATALOG}#topical",
    "https://www.jesuswalk.com/beginning/":      "beginning.html",
    "https://www.jesuswalk.com/lamb/":           f"{CATALOG}#topical",
    "https://www.jesuswalk.com/voice/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/lords-supper":    f"{CATALOG}#topical",
    "https://www.jesuswalk.com/lords-supper/":   f"{CATALOG}#topical",
    "https://www.jesuswalk.com/names-jesus/":    f"{CATALOG}#topical",
    "https://www.jesuswalk.com/christ-power/":   f"{CATALOG}#topical",
    "https://www.jesuswalk.com/kingdom/":        f"{CATALOG}#topical",
    "https://www.jesuswalk.com/glory/":          f"{CATALOG}#topical",
    "https://www.jesuswalk.com/christmas-incarnation/": f"{CATALOG}#topical",
}

# Also add individual scraped article pages
for fname in os.listdir(jw_scrp):
    if not fname.startswith("jw_") or not fname.endswith(".json"):
        continue
    try:
        with open(os.path.join(jw_scrp, fname), encoding="utf-8") as fh:
            d = json.load(fh)
        url  = d.get("url", "")
        html = fname.replace(".json", ".html")
        if url and os.path.exists(os.path.join(jw_pages, html)):
            URL_MAP[url] = html
    except Exception:
        pass

# Read the current file
with open(src, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Replace all external URLs with local ones
replaced = 0
for ext_url, local in URL_MAP.items():
    old = f'href="{ext_url}"'
    new = f'href="{local}"'
    if old in content:
        content = content.replace(old, new)
        replaced += 1

# Step 2: Remove target=_blank from all study cards
content = re.sub(
    r'(<a href="[^"]+" class="study-card"[^>]*?) target="_blank" rel="noopener"',
    r'\1',
    content
)

# Step 3: Inject section jump bar + search after the hero section and before first section
JUMP_BAR = '''
  <!-- Section Jump Bar + Search -->
  <div id="section-jump-bar" style="
    position: sticky; top: 64px; z-index: 100;
    background: var(--bg-card, #fff);
    border-bottom: 1px solid var(--border-color, #e8e4f0);
    padding: 0;
    box-shadow: 0 2px 12px rgba(62,50,101,0.08);
  ">
    <div class="container" style="display:flex; align-items:center; gap:12px; padding-top:10px; padding-bottom:10px; flex-wrap:wrap;">
      <!-- Search -->
      <div style="position:relative; flex:1; min-width:180px; max-width:280px;">
        <svg style="position:absolute;left:10px;top:50%;transform:translateY(-50%);opacity:0.4;" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input id="study-search" type="search" placeholder="Search studies..." aria-label="Search Bible studies" style="width:100%;padding:8px 10px 8px 34px;border:1px solid var(--border-color,#e8e4f0);border-radius:8px;font-size:0.85rem;background:var(--bg-surface,#f8f6ff);outline:none;font-family:inherit;">
      </div>
      <!-- Section Pills -->
      <nav style="display:flex; gap:6px; flex-wrap:wrap;" aria-label="Jump to section">
        <a href="#old-testament"  class="jump-pill">Old Testament</a>
        <a href="#gospels"        class="jump-pill">Gospels</a>
        <a href="#acts"           class="jump-pill">Acts</a>
        <a href="#pauls-letters"  class="jump-pill">Paul's Letters</a>
        <a href="#general-letters"class="jump-pill">General Letters</a>
        <a href="#revelation"     class="jump-pill">Revelation</a>
        <a href="#topical"        class="jump-pill">Topical</a>
      </nav>
    </div>
  </div>
  <style>
    .jump-pill {
      display:inline-block; padding:5px 12px; border-radius:20px;
      font-size:0.78rem; font-weight:600; letter-spacing:.02em;
      background: var(--bg-surface, #f8f6ff);
      color: var(--color-primary, #3E3265);
      border: 1px solid var(--border-color, #e8e4f0);
      text-decoration:none; transition: all .2s ease;
      white-space: nowrap;
    }
    .jump-pill:hover, .jump-pill.active {
      background: var(--color-primary, #3E3265);
      color: #fff; border-color: var(--color-primary, #3E3265);
    }
    /* Offset anchor scroll for sticky nav + jump bar */
    [id^="old-testament"],[id^="gospels"],[id^="acts"],
    [id^="pauls-letters"],[id^="general-letters"],
    [id^="revelation"],[id^="topical"] {
      scroll-margin-top: 130px;
    }
    /* Search hidden state */
    .study-card.hidden { display: none !important; }
    .section-group.empty { display: none !important; }
    #no-results {
      display:none; text-align:center; padding:60px 20px;
      color: var(--text-muted, #888); font-size:1.1rem;
    }
    html { scroll-behavior: smooth; }
  </style>
  <script>
    // Live search filter
    const searchInput = document.getElementById('study-search');
    const noResults   = document.getElementById('no-results');
    if (searchInput) {
      searchInput.addEventListener('input', function() {
        const q = this.value.trim().toLowerCase();
        const cards = document.querySelectorAll('.study-card');
        let visibleCount = 0;
        cards.forEach(card => {
          const text = card.textContent.toLowerCase();
          const show = !q || text.includes(q);
          card.classList.toggle('hidden', !show);
          if (show) visibleCount++;
        });
        // Hide empty section groups
        document.querySelectorAll('.section-group').forEach(sg => {
          const visible = sg.querySelectorAll('.study-card:not(.hidden)').length;
          sg.classList.toggle('empty', visible === 0);
        });
        if (noResults) noResults.style.display = visibleCount === 0 ? 'block' : 'none';
      });
    }
    // Active pill on scroll
    const pills = document.querySelectorAll('.jump-pill');
    const sections = ['old-testament','gospels','acts','pauls-letters','general-letters','revelation','topical'];
    window.addEventListener('scroll', () => {
      let current = '';
      sections.forEach(id => {
        const el = document.getElementById(id);
        if (el && window.scrollY >= el.offsetTop - 160) current = id;
      });
      pills.forEach(p => {
        p.classList.toggle('active', p.getAttribute('href') === '#' + current);
      });
    });
  </script>
  <div id="no-results" class="container" style="display:none;">
    No studies found. Try a different search term.
  </div>
'''

# Inject jump bar right before the main section
content = content.replace(
    '  <section class="section"><div class="container">',
    JUMP_BAR + '\n  <section class="section"><div class="container">'
)

# Step 4: Wrap each section group (header + grid) in a .section-group div for search hiding
# Pattern: <div id="old-testament" ...>...</div><div class="studies-grid">...</div>
# We need to wrap each pair in <div class="section-group">...</div>
for section_id in ['old-testament', 'gospels', 'acts', 'pauls-letters', 'general-letters', 'revelation', 'topical']:
    # Find the section header start
    pattern = f'<div id="{section_id}"'
    if pattern in content:
        # Find the position and wrap until the next section-header or end of section
        idx = content.find(pattern)
        # Insert opening wrapper before the section header
        content = content[:idx] + f'<div class="section-group" id="sg-{section_id}">' + content[idx:]

# Close each section-group before the next one opens, or before </div></section>
# Insert closing tags before each new section-group (except the first)
for section_id in ['gospels', 'acts', 'pauls-letters', 'general-letters', 'revelation', 'topical']:
    content = content.replace(
        f'<div class="section-group" id="sg-{section_id}">',
        f'</div><div class="section-group" id="sg-{section_id}">'
    )

# Close the last section-group before </div></section>
content = content.replace(
    '</div></div></section>',
    '</div></div></div></section>',
    1  # only the first occurrence (the studies section)
)

# Write back
with open(src, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open(src, "r", encoding="utf-8") as f:
    verify = f.read()

ext_links = re.findall(r'href="https://www.jesuswalk.com[^"]*" class="study-card"', verify)
local_links = re.findall(r'href="[^h][^"]*" class="study-card"', verify)
has_search  = 'study-search' in verify
has_jump    = 'jump-pill' in verify
has_groups  = 'section-group' in verify

print(f"Replaced: {replaced} URLs")
print(f"External links remaining: {len(ext_links)}")
print(f"Local links: {len(local_links)}")
print(f"Has search input: {has_search}")
print(f"Has jump bar: {has_jump}")
print(f"Has section groups: {has_groups}")
if ext_links:
    print("Still external:", ext_links[:5])
else:
    print("ALL links are local!")
