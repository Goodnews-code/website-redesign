"""
Joyful Heart Page Generator — Phase 3 (Refined)
=================================================
Reads scraped JSON data and generates styled HTML pages
with intelligent content cleaning:
  - Filters out navigation menu text from paragraphs
  - Removes copyright boilerplate & newsletter signup
  - Detects Bible quotes and renders as styled blockquotes
  - Includes relevant article images from scraped data
  - Interlaces headings and paragraphs properly
  - Adds related articles at the bottom
  - Dr. Wilson's photo on About page

Usage:
    python page_generator.py
"""

import json
import os
import re
from urllib.parse import urlparse
from html import escape


# =========================================================
# CONTENT CLEANING ENGINE
# =========================================================

# Patterns that indicate nav/boilerplate paragraphs
NAV_PATTERNS = [
    "HomeBible StudiesArticles",
    "Bible StudiesArticlesBooks",
    "SearchMenuDonate",
    "About UsFAQContact Us",
    "Site Map",
    "Free \r\n\tE-mail Bible Study",
    "Free \n\tE-mail Bible Study",
    "Free E-mail Bible Study",
    "Newsletter\nPodcast",
    "Joyful Heart Renewal Ministries, Inc.- Dr. Ralph F. Wilson",
    "Contributions\nto Joyful Heart",
    "Contributionsto Joyful Heart",
    "Country(2-letter abbreviation",
    "Preferred FormatHTML",
    "(recommended)Plain text",
    "FirstLastE-mail",
    "See legal, copyright, and reprint information",
    "don't subscribe your friends",
    "never sell, rent, or loan our lists",
    "[X] Close Window",
]

# End-of-article boilerplate markers
BOILERPLATE_MARKERS = [
    "Copyright ©",
    "copyright ©",
    "All rights reserved",
    "Do not put this on a website",
    "See legal, copyright",
    "To be notified about future articles",
    "why don't you subscribe",
    "placing your e-mail address",
]

# References/footnotes section markers
ENDNOTE_MARKERS = [
    "References and \nAbbreviations",
    "References and Abbreviations",
    "End Notes",
]


def is_nav_or_boilerplate(text):
    """Check if a paragraph is navigation or boilerplate text."""
    for pattern in NAV_PATTERNS:
        if pattern in text:
            return True
    for marker in BOILERPLATE_MARKERS:
        if marker in text:
            return True
    return False


def is_endnote(text):
    """Check if a paragraph is an endnote reference."""
    # Footnote-style text like "[1]"Urge"..." or "[12]Galatians 1:4..."
    if re.match(r'^\[\d+\]', text.strip()):
        return True
    for m in ENDNOTE_MARKERS:
        if text.strip().startswith(m):
            return True
    return False


def is_scripture_quote(text):
    """Detect if a paragraph is a scripture quotation."""
    # Starts with a quote mark and contains a Bible reference
    bible_books = r'(Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|Job|Psalms?|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|Corinthians|Galatians|Ephesians|Philippians|Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|Peter|Jude|Revelation)'
    t = text.strip()
    if t.startswith('"') or t.startswith('\\"') or t.startswith('"') or t.startswith('\"'):
        if re.search(bible_books, t):
            return True
        # Short quoted text is likely a quote
        if len(t) < 500 and (t.endswith('"') or t.endswith(')') or t.endswith('\\"')):
            return True
    return False


def is_discussion_question(text):
    """Detect discussion/reflection questions."""
    return text.strip().startswith("Question ") and "." in text[:15]


def clean_paragraph(text):
    """Clean a paragraph's text for display."""
    # Normalize whitespace
    t = re.sub(r'\r\n', '\n', text)
    t = re.sub(r'\n+', ' ', t)
    t = re.sub(r'\t+', ' ', t)
    t = re.sub(r'  +', ' ', t)
    return t.strip()


def filter_content_images(images):
    """Filter out nav/UI images, keep only content images."""
    content_imgs = []
    skip_names = [
        "search-icon", "menu-icon", "at_sign", "pencil",
        "caa-sm-cross", "the-joyful-heart-head",
        "articles-stories-meditations-head", "holidays-head",
        "books_head", "navigation_head", "books-available-from-amazon",
        "bible_icon", "search_", "menu_",
    ]
    for img in images:
        src = (img.get("src", "") or "").lower()
        alt = img.get("alt", "") or ""
        local = (img.get("local_file", "") or "").lower()
        w = int(img.get("width", 0) or 0)
        h = int(img.get("height", 0) or 0)

        # Skip tiny icons
        if w > 0 and w < 50:
            continue
        if h > 0 and h < 50:
            continue

        # Skip known nav/UI images
        skip = False
        for name in skip_names:
            if name in src or name in local:
                skip = True
                break
        if skip:
            continue

        # Skip blank alt text icons
        if alt in ["", "Search", "Menu", "@", "Sign up now!", "Celtic Cross"]:
            if w < 100 or h < 100:
                continue

        content_imgs.append(img)

    return content_imgs


class PageGenerator:
    def __init__(self, scraped_dir, output_dir):
        self.scraped_dir = scraped_dir
        self.output_dir = output_dir
        self.pages_dir = os.path.join(output_dir, "pages")
        os.makedirs(self.pages_dir, exist_ok=True)

        # Load all scraped data
        with open(os.path.join(scraped_dir, "all_pages.json"), "r", encoding="utf-8") as f:
            self.all_pages = json.load(f)

        with open(os.path.join(scraped_dir, "sitemap.json"), "r", encoding="utf-8") as f:
            self.sitemap = json.load(f)

        print(f"Loaded {len(self.all_pages)} pages from scraped data")

        # Group pages by category
        self.by_category = {}
        for page in self.all_pages:
            cat = page.get("category", "misc")
            if cat not in self.by_category:
                self.by_category[cat] = []
            self.by_category[cat].append(page)

        # Category display names & styles
        self.category_meta = {
            "jesus": {"name": "Stories about Jesus", "gradient": "135deg, #5B4A8A, #7B6AAF"},
            "maturity": {"name": "Christian Maturity", "gradient": "135deg, #3E3265, #5B4A8A"},
            "encourag": {"name": "Encouragement", "gradient": "135deg, #C9956B, #E0BD97"},
            "evang": {"name": "Good News & Evangelism", "gradient": "135deg, #5B4A8A, #C9956B"},
            "church": {"name": "Building the Church", "gradient": "135deg, #3E3265, #7B6AAF"},
            "communion": {"name": "Communion & Lord's Supper", "gradient": "135deg, #5B4A8A, #3E3265"},
            "prayer": {"name": "Prayer", "gradient": "135deg, #7B6AAF, #5B4A8A"},
            "scholar": {"name": "Scholarly Articles", "gradient": "135deg, #3E3265, #5B4A8A"},
            "christmas": {"name": "Christmas", "gradient": "135deg, #8B0000, #C9956B"},
            "easter": {"name": "Easter & Holy Week", "gradient": "135deg, #5B4A8A, #D4AF37"},
            "thanksgiving": {"name": "Thanksgiving", "gradient": "135deg, #C9956B, #8B4513"},
            "pentecost": {"name": "Pentecost", "gradient": "135deg, #C0392B, #5B4A8A"},
            "stpatrick": {"name": "St. Patrick & Celtic Christianity", "gradient": "135deg, #2E7D32, #5B4A8A"},
            "art": {"name": "Christian Art", "gradient": "135deg, #5B4A8A, #C9956B"},
            "misc": {"name": "Miscellany", "gradient": "135deg, #5B4A8A, #7B6AAF"},
            "plant": {"name": "Church Planting", "gradient": "135deg, #3E3265, #5B4A8A"},
            "holiday": {"name": "Holiday Stories", "gradient": "135deg, #C9956B, #5B4A8A"},
            "psalms": {"name": "Psalms Studies", "gradient": "135deg, #5B4A8A, #D4AF37"},
            "luke": {"name": "Luke's Gospel", "gradient": "135deg, #3E3265, #7B6AAF"},
            "greatprayers": {"name": "Great Prayers of the Bible", "gradient": "135deg, #5B4A8A, #C9956B"},
        }

    def get_css_path(self, depth=1):
        return "../" * depth + "index.css"

    def get_nav_html(self, depth=1):
        root = "../" * depth
        return f'''<nav class="navbar" id="navbar">
    <div class="container">
      <a href="{root}index.html" class="nav-logo" aria-label="Joyful Heart Home">
        <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="20" cy="20" r="18" stroke="currentColor" stroke-width="2"/>
          <path d="M20 10C17 10 14 13 14 16C14 22 20 28 20 28C20 28 26 22 26 16C26 13 23 10 20 10Z" fill="currentColor" opacity="0.2"/>
          <path d="M20 10C17 10 14 13 14 16C14 22 20 28 20 28C20 28 26 22 26 16C26 13 23 10 20 10Z" stroke="currentColor" stroke-width="1.5"/>
          <line x1="20" y1="14" x2="20" y2="22" stroke="currentColor" stroke-width="1.5"/>
          <line x1="16" y1="18" x2="24" y2="18" stroke="currentColor" stroke-width="1.5"/>
        </svg>
        <div class="nav-logo-text">Joyful Heart<span>Renewal Ministries</span></div>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="{root}pages/bible-studies.html">Bible Studies</a></li>
        <li><a href="{root}pages/articles.html">Articles</a></li>
        <li><a href="{root}pages/podcast.html">Podcast</a></li>
        <li><a href="{root}pages/books.html">Books</a></li>
        <li><a href="{root}pages/about.html">About</a></li>
        <li><a href="{root}pages/newsletter.html" class="btn btn-primary nav-cta">Subscribe Free</a></li>
      </ul>
      <button class="mobile-toggle" id="mobileToggle" aria-label="Toggle menu" aria-expanded="false">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
    </div>
  </nav>'''

    def get_footer_html(self, depth=1):
        root = "../" * depth
        return f'''<footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <p style="font-family: var(--font-heading); font-size: 1.3rem; font-weight: 700; color: white; margin-bottom: 4px;">Joyful Heart</p>
          <p>Joyful Heart Renewal Ministries, Inc. A 501(c)3 non-profit serving believers worldwide since 1996.</p>
          <p style="margin-top: 8px;">3669 Taylor Rd., Unit 565<br>Loomis, CA 95650</p>
        </div>
        <div>
          <h4>Bible Studies</h4>
          <ul class="footer-links">
            <li><a href="{root}pages/bible-studies.html">All Studies</a></li>
            <li><a href="{root}pages/books.html">Books</a></li>
            <li><a href="{root}pages/podcast.html">Podcast</a></li>
          </ul>
        </div>
        <div>
          <h4>Articles</h4>
          <ul class="footer-links">
            <li><a href="{root}pages/articles.html">All Categories</a></li>
            <li><a href="{root}pages/cat-jesus.html">Stories about Jesus</a></li>
            <li><a href="{root}pages/cat-maturity.html">Christian Maturity</a></li>
            <li><a href="{root}pages/cat-encourag.html">Encouragement</a></li>
            <li><a href="{root}pages/cat-christmas.html">Christmas</a></li>
          </ul>
        </div>
        <div>
          <h4>Ministry</h4>
          <ul class="footer-links">
            <li><a href="{root}pages/about.html">About Us</a></li>
            <li><a href="{root}pages/contact.html">Contact</a></li>
            <li><a href="{root}pages/giving.html">Donate</a></li>
            <li><a href="{root}pages/faq.html">FAQ</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <span>&copy; 2026 Joyful Heart Renewal Ministries, Inc. All rights reserved.</span>
        <span>Dr. Ralph F. Wilson, Executive Director</span>
      </div>
    </div>
  </footer>'''

    def get_js(self):
        return '''<script>
    const navbar=document.getElementById('navbar');
    window.addEventListener('scroll',()=>{navbar.classList.toggle('scrolled',window.scrollY>40)});
    const mt=document.getElementById('mobileToggle'),nl=document.getElementById('navLinks');
    mt.addEventListener('click',()=>{const e=mt.getAttribute('aria-expanded')==='true';mt.setAttribute('aria-expanded',!e);nl.classList.toggle('active')});
    nl.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nl.classList.remove('active');mt.setAttribute('aria-expanded','false')}));
    const obs=new IntersectionObserver(e=>{e.forEach(en=>{if(en.isIntersecting){en.target.style.animationPlayState='running';obs.unobserve(en.target)}})},{threshold:0.1});
    document.querySelectorAll('.animate-in').forEach(el=>{el.style.animationPlayState='paused';obs.observe(el)});
  </script>'''

    def build_page(self, title, content_html, depth=1, description=""):
        desc = description or f"{title} — Joyful Heart Renewal Ministries"
        desc_escaped = escape(desc[:160])
        title_escaped = escape(title)
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_escaped} — Joyful Heart Renewal Ministries</title>
  <meta name="description" content="{desc_escaped}">
  <link rel="stylesheet" href="{self.get_css_path(depth)}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>💜</text></svg>">
</head>
<body>
  {self.get_nav_html(depth)}
  {content_html}
  {self.get_footer_html(depth)}
  {self.get_js()}
</body>
</html>'''

    def clean_title(self, raw_title):
        """Clean up scraped title."""
        t = raw_title.strip()
        for suffix in [" - Christian Articles Archive", " - Joyful Heart Renewal Ministries",
                       ", by Dr. Ralph F. Wilson", ", by Ralph F. Wilson"]:
            t = t.replace(suffix, "")
        return t.strip()

    def extract_clean_paragraphs(self, page_data):
        """Extract paragraphs, filtering out navigation and boilerplate.
        Returns list of (type, text) tuples where type is 'p', 'quote', 'question', 'endnote'."""
        raw = page_data.get("paragraphs", [])
        cleaned = []
        hit_endnotes = False

        for text in raw:
            # Skip nav/boilerplate
            if is_nav_or_boilerplate(text):
                continue

            ct = clean_paragraph(text)

            # Skip very short text (likely UI fragments)
            if len(ct) < 15:
                continue

            # Check for endnotes section
            if is_endnote(ct):
                hit_endnotes = True
                cleaned.append(("endnote", ct))
                continue

            if hit_endnotes:
                # Everything after endnotes marker is footnotes or boilerplate
                if ct.startswith("[") or len(ct) < 100:
                    cleaned.append(("endnote", ct))
                continue

            # Classify content type
            if is_scripture_quote(ct):
                cleaned.append(("quote", ct))
            elif is_discussion_question(ct):
                cleaned.append(("question", ct))
            else:
                cleaned.append(("p", ct))

        return cleaned

    def get_article_excerpt(self, page_data, max_len=200):
        """Get a clean excerpt for article cards."""
        paras = self.extract_clean_paragraphs(page_data)
        for ptype, text in paras:
            if ptype == "p" and len(text) > 40:
                if len(text) > max_len:
                    # Cut at word boundary
                    cut = text[:max_len].rsplit(' ', 1)[0]
                    return cut + "..."
                return text
        return ""

    def render_article_body(self, page_data):
        """Render article body HTML with proper formatting."""
        paras = self.extract_clean_paragraphs(page_data)
        headings = page_data.get("headings", [])
        content_images = filter_content_images(page_data.get("images", []))

        html_parts = []

        # Render content paragraphs
        endnotes = []
        body_paras = []
        for ptype, text in paras:
            if ptype == "endnote":
                endnotes.append(text)
            else:
                body_paras.append((ptype, text))

        # Insert images at strategic points
        img_insert_points = []
        if content_images and len(body_paras) > 2:
            # Insert first image after the 2nd paragraph, second after the 6th, etc
            positions = [2, 6, 12]
            for i, pos in enumerate(positions):
                if i < len(content_images) and pos < len(body_paras):
                    img_insert_points.append((pos, content_images[i]))

        for idx, (ptype, text) in enumerate(body_paras):
            # Check if we need to insert an image before this paragraph
            for pos, img in img_insert_points:
                if idx == pos:
                    local_file = img.get("local_file", "")
                    alt = escape(img.get("alt", "Article illustration"))
                    if local_file:
                        html_parts.append(f'''
        <figure class="article-figure animate-in">
          <img src="../scraped_data/images/{local_file}" alt="{alt}" loading="lazy">
          {f'<figcaption>{alt}</figcaption>' if alt and alt != "Article illustration" else ""}
        </figure>''')

            escaped = escape(text)

            if ptype == "quote":
                html_parts.append(f'        <blockquote class="scripture-quote">{escaped}</blockquote>')
            elif ptype == "question":
                html_parts.append(f'        <div class="discussion-question"><strong>{escaped[:12]}</strong>{escaped[12:]}</div>')
            else:
                html_parts.append(f'        <p>{escaped}</p>')

        # Add endnotes if present
        if endnotes:
            html_parts.append('        <details class="endnotes-section"><summary>End Notes & References</summary>')
            for note in endnotes:
                html_parts.append(f'          <p class="endnote">{escape(note)}</p>')
            html_parts.append('        </details>')

        return '\n'.join(html_parts)

    def _url_to_filename(self, url):
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            path = "index"
        safe = re.sub(r"[^a-zA-Z0-9-]", "_", path)
        if "jesuswalk" in parsed.netloc:
            safe = "jw_" + safe
        return safe[:100]

    # ==========================================
    # ARTICLE PAGE GENERATOR
    # ==========================================

    def generate_article_page(self, page_data):
        """Generate an individual article page with cleaned content."""
        title = self.clean_title(page_data.get("title", "Untitled"))
        cat = page_data.get("category", "misc")
        meta = self.category_meta.get(cat, {"name": cat.title(), "gradient": "135deg, #5B4A8A, #7B6AAF"})

        body_html = self.render_article_body(page_data)

        # If no clean content found, show a notice
        if not body_html.strip():
            body_html = f'        <p class="empty-notice">This article\'s content is being migrated. Visit the <a href="{page_data["url"]}">original article</a> to read it now.</p>'

        # Related articles in same category
        related_html = ""
        same_cat = [p for p in self.by_category.get(cat, [])
                    if p["url"] != page_data["url"] and ".htm" in p.get("url", "")]
        related = same_cat[:3]
        if related:
            cards = ""
            for r in related:
                r_title = self.clean_title(r.get("title", "Untitled"))
                r_filename = self._url_to_filename(r["url"]) + ".html"
                r_excerpt = self.get_article_excerpt(r, 120)
                cards += f'''
            <a href="{r_filename}" class="related-card">
              <div class="related-card-tag">{meta["name"]}</div>
              <h4>{escape(r_title)}</h4>
              <p>{escape(r_excerpt)}</p>
            </a>'''

            related_html = f'''
      <div class="related-articles animate-in">
        <h3>More in {meta["name"]}</h3>
        <div class="related-grid">{cards}
        </div>
      </div>'''

        # Get first clean paragraph as description
        desc = self.get_article_excerpt(page_data, 160)

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in" style="max-width: 100%;">
      <a href="cat-{cat}.html" class="hero-badge" style="text-decoration:none;">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> {meta["name"]}
      </a>
      <h1 style="font-size: var(--fs-h1);">{escape(title)}</h1>
      <p class="hero-description">By Dr. Ralph F. Wilson</p>
    </div></div>
  </section>
  <section class="section" style="padding-top: 40px;">
    <div class="container" style="max-width: 800px;">
      <article class="article-body animate-in">
{body_html}
      </article>
      <div class="article-nav-bar">
        <a href="cat-{cat}.html" class="btn btn-secondary">← More {meta["name"]}</a>
        <a href="articles.html" class="btn btn-secondary">All Categories</a>
      </div>
      {related_html}
    </div>
  </section>'''
        return self.build_page(title, content, description=desc)

    # ==========================================
    # CATEGORY PAGE GENERATOR
    # ==========================================

    def generate_category_page(self, category):
        """Generate a category listing page with cleaned excerpts."""
        meta = self.category_meta.get(category, {"name": category.title(), "gradient": "135deg, #5B4A8A, #7B6AAF"})
        pages = self.by_category.get(category, [])
        articles = [p for p in pages if ".htm" in p.get("url", "")]

        cards_html = ""
        for i, article in enumerate(articles):
            title = self.clean_title(article.get("title", "Untitled"))
            desc = self.get_article_excerpt(article, 160)
            filename = self._url_to_filename(article["url"]) + ".html"
            delay = f"animate-delay-{(i % 4) + 1}"

            cards_html += f'''
        <a href="{filename}" class="article-card animate-in {delay}" style="text-decoration: none; color: inherit;">
          <div class="article-card-image" style="background: linear-gradient({meta["gradient"]}); display:flex;align-items:center;justify-content:center;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48" style="color: rgba(255,255,255,0.4);"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          </div>
          <div class="article-card-body">
            <div class="article-card-tag">{meta["name"]}</div>
            <h3>{escape(title)}</h3>
            <p>{escape(desc)}</p>
          </div>
        </a>'''

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Category</div>
      <h1>{meta["name"]}</h1>
      <p class="hero-description">{len(articles)} article{"s" if len(articles) != 1 else ""} by Dr. Ralph F. Wilson.</p>
      <div class="hero-actions"><a href="articles.html" class="btn btn-secondary">← All Categories</a></div>
    </div></div>
  </section>
  <section class="section">
    <div class="container">
      <div class="articles-grid">{cards_html}
      </div>
    </div>
  </section>'''
        return self.build_page(meta["name"], content, description=f"Browse {len(articles)} articles about {meta['name']} by Dr. Ralph F. Wilson.")

    # ==========================================
    # CORE PAGES (same as Phase 2, with minor improvements)
    # ==========================================

    def generate_about_page(self):
        photo = None
        images_dir = os.path.join(self.scraped_dir, "images")
        if os.path.isdir(images_dir):
            for fname in os.listdir(images_dir):
                if "ralph" in fname.lower() or "wilson" in fname.lower():
                    photo = fname
                    break

        photo_html = f'<img src="../scraped_data/images/{photo}" alt="Dr. Ralph F. Wilson" style="width:100%;height:400px;object-fit:cover;border-radius:16px;" loading="lazy">' if photo else '<div style="width:100%;height:400px;background:linear-gradient(135deg, #5B4A8A, #7B6AAF);border-radius:16px;display:flex;align-items:center;justify-content:center;"><svg viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" width="80" height="80"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div>'

        # Extract about content
        about_data = None
        for p in self.all_pages:
            if "about" in p.get("url", "").lower() and p.get("category") == "about":
                about_data = p
                break

        paras_html = ""
        if about_data:
            paras = self.extract_clean_paragraphs(about_data)
            for ptype, text in paras[:10]:
                if ptype == "p":
                    paras_html += f'<p>{escape(text)}</p>\n'

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Our Story</div>
      <h1>About Dr. Ralph F. <em>Wilson</em></h1>
      <p class="hero-description">Executive Director of Joyful Heart Renewal Ministries, pastor, author, and Bible teacher serving believers in 120+ countries since 1996.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container">
      <div class="about-grid">
        <div class="about-image animate-in">{photo_html}</div>
        <div class="about-content animate-in animate-delay-2">
          <div class="section-label">Executive Director</div>
          <h2>Dr. Ralph F. Wilson</h2>
          {paras_html if paras_html else "<p>Dr. Ralph F. Wilson is the Executive Director of Joyful Heart Renewal Ministries, Inc., a 501(c)3 non-profit organization serving believers worldwide since 1996. He has authored over 50 Bible studies and hundreds of articles, reaching believers in over 120 countries.</p><p>A pastor, scholar, and author with a Doctor of Ministry degree, Dr. Wilson brings decades of pastoral experience and deep scriptural insight to his writing. His Bible studies are available in paperback, PDF, and Kindle through Amazon.</p>"}
          <div class="about-facts" style="margin-top: 28px;">
            <div class="about-fact">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 12 3 12 0v-5"/></svg>
              <div class="about-fact-text"><strong>Scholar & Pastor</strong>Doctor of Ministry degree</div>
            </div>
            <div class="about-fact">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              <div class="about-fact-text"><strong>Global Reach</strong>120+ countries served</div>
            </div>
            <div class="about-fact">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
              <div class="about-fact-text"><strong>50+ Books</strong>Paperback, PDF, and Kindle</div>
            </div>
            <div class="about-fact">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
              <div class="about-fact-text"><strong>501(c)3 Nonprofit</strong>All donations tax-deductible</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>'''
        return self.build_page("About", content, description="About Dr. Ralph F. Wilson and Joyful Heart Renewal Ministries.")

    def generate_contact_page(self):
        content = '''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Get in Touch</div>
      <h1>Contact <em>Us</em></h1>
      <p class="hero-description">We\'d love to hear from you. Reach out with questions, prayer requests, or just to say hello.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container" style="max-width: 700px;">
      <div class="study-card animate-in" style="padding: 40px;">
        <h3 style="margin-bottom: 24px;">Dr. Ralph F. Wilson</h3>
        <p style="margin-bottom: 12px;"><strong>Email:</strong> pastor@joyfulheart.com</p>
        <p style="margin-bottom: 12px;"><strong>Phone:</strong> (916) 652-4659</p>
        <p style="margin-bottom: 12px;"><strong>Hours:</strong> Monday – Friday, 8 AM – 4 PM Pacific</p>
        <p style="margin-bottom: 24px;"><strong>Address:</strong> 3669 Taylor Rd., Unit 565, Loomis, CA 95650</p>
        <p style="color: var(--text-muted);">Joyful Heart Renewal Ministries, Inc. is a 501(c)3 non-profit organization. All contributions are tax-deductible.</p>
      </div>
    </div>
  </section>'''
        return self.build_page("Contact", content, description="Contact Dr. Ralph F. Wilson at Joyful Heart Renewal Ministries.")

    def generate_giving_page(self):
        content = '''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Support This Ministry</div>
      <h1>Your Gift Makes a <em>Difference</em></h1>
      <p class="hero-description">Joyful Heart Renewal Ministries is a 501(c)3 nonprofit. All contributions are tax-deductible and help keep Bible studies free for believers worldwide.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container" style="max-width: 700px; text-align: center;">
      <div class="study-card animate-in" style="padding: 40px;">
        <h3 style="margin-bottom: 16px;">Ways to Give</h3>
        <p style="margin-bottom: 24px;">Your generous gift supports free Bible studies, articles, and the Joyful Heart podcast reaching 120+ countries.</p>
        <a href="https://www.joyfulheart.com/giving/" class="btn btn-gold" style="font-size: 1.1rem; padding: 18px 48px;">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          Give a Tax-Deductible Gift
        </a>
        <p style="margin-top: 24px; color: var(--text-muted); font-size: var(--fs-sm);">You may also mail a check to:<br>Joyful Heart Renewal Ministries, Inc.<br>3669 Taylor Rd., Unit 565<br>Loomis, CA 95650</p>
      </div>
    </div>
  </section>'''
        return self.build_page("Donate", content, description="Support Joyful Heart Renewal Ministries with a tax-deductible gift.")

    def generate_newsletter_page(self):
        content = '''
  <section class="cta-section" style="padding-top: calc(var(--nav-height) + 80px);">
    <div class="container animate-in">
      <h2 style="font-size: var(--fs-h1);">The Joyful Heart Newsletter</h2>
      <p style="max-width: 600px; margin: 0 auto 16px;">Receive 6-8 encouraging articles per year from Dr. Ralph F. Wilson, plus notifications about new Bible studies. It\'s free, always.</p>
      <form class="cta-form" action="https://www.joyfulheart.com/newsletter/" method="get" style="max-width: 500px;">
        <input type="email" placeholder="Your email address" aria-label="Email address" required>
        <button type="submit" class="btn btn-gold">Subscribe Free</button>
      </form>
      <p style="font-size: 0.75rem; opacity: 0.5; margin-top: 16px;">We respect your privacy. We never sell, rent, or share your information.</p>
    </div>
  </section>'''
        return self.build_page("Newsletter", content, description="Subscribe to The Joyful Heart newsletter — free encouraging articles from Dr. Ralph F. Wilson.")

    def generate_articles_index(self):
        cards_html = ""
        article_categories = ["jesus", "maturity", "encourag", "evang", "church",
                              "communion", "prayer", "scholar", "christmas", "easter",
                              "thanksgiving", "pentecost", "stpatrick", "art", "misc",
                              "plant", "holiday"]
        for cat in article_categories:
            meta = self.category_meta.get(cat, {"name": cat.title(), "gradient": "135deg, #5B4A8A, #7B6AAF"})
            count = len([p for p in self.by_category.get(cat, []) if ".htm" in p.get("url", "")])
            if count == 0:
                continue
            cards_html += f'''
        <a href="cat-{cat}.html" class="study-card animate-in" style="text-decoration:none;">
          <div class="study-card-category">{count} Article{"s" if count != 1 else ""}</div>
          <h3>{meta["name"]}</h3>
          <p style="color:var(--text-secondary);font-size:var(--fs-sm);">Browse all articles in this category.</p>
        </a>'''

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Read & Reflect</div>
      <h1>Articles, Stories & <em>Meditations</em></h1>
      <p class="hero-description">Hundreds of inspiring pieces by Dr. Ralph F. Wilson. Browse by category below.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container">
      <div class="studies-grid">{cards_html}
      </div>
    </div>
  </section>'''
        return self.build_page("Articles", content, description="Browse hundreds of Christian articles, stories, and meditations by Dr. Ralph F. Wilson.")

    def generate_bible_studies_page(self):
        """Generate Bible Studies page dynamically from scraped JesusWalk data."""

        # URL map: original jesuswalk.com URL -> local redesign page
        # Built dynamically from scraped JSON + hardcoded anchors
        JW_URL_MAP = {'https://www.jesuswalk.com/abraham/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/jacob/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/moses/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/samuel/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/david/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/solomon/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/elijah/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/psalms/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/isaiah/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/daniel/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/lamb/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament', 'https://www.jesuswalk.com/john/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/luke/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/mark/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/sermon/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/parables/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/7lastwords/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/resurrection/': '../../jesuswalk-redesign/pages/all-studies.html#gospels', 'https://www.jesuswalk.com/acts/': '../../jesuswalk-redesign/pages/all-studies.html#acts', 'https://www.jesuswalk.com/early-church/': '../../jesuswalk-redesign/pages/all-studies.html#acts', 'https://www.jesuswalk.com/romans/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/1corinthians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/2corinthians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/galatians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/ephesians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/philippians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/colossians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/1thessalonians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/timothy/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters', 'https://www.jesuswalk.com/hebrews/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters', 'https://www.jesuswalk.com/james/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters', 'https://www.jesuswalk.com/1peter/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters', 'https://www.jesuswalk.com/123john/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters', 'https://www.jesuswalk.com/revelation/': '../../jesuswalk-redesign/pages/all-studies.html#revelation', 'https://www.jesuswalk.com/grace/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/holy-spirit/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/greatprayers/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/humility/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/names-of-god/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/manifesto/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/proverbs/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/voice/': '../../jesuswalk-redesign/pages/all-studies.html#topical', 'https://www.jesuswalk.com/lords-supper/': '../../jesuswalk-redesign/pages/jw_lords-supper.html', 'https://www.jesuswalk.com/christian-symbols/': '../../jesuswalk-redesign/pages/jw_christian-symbols.html', 'https://www.jesuswalk.com/': '../../jesuswalk-redesign/index.html', 'https://www.jesuswalk.com/beginning/': '../../jesuswalk-redesign/pages/jw_beginning.html', 'https://www.jesuswalk.com/discipleship/': '../../jesuswalk-redesign/pages/jw_discipleship.html', 'https://www.jesuswalk.com/books/': '../../jesuswalk-redesign/pages/jw_books.html', 'https://www.jesuswalk.com/podcast/': '../../jesuswalk-redesign/pages/jw_podcast.html', 'https://www.jesuswalk.com/bible-study/': '../../jesuswalk-redesign/pages/jw_bible-study.html', 'https://www.jesuswalk.com/123john/children-of-god-1jn3-1a.htm': '../../jesuswalk-redesign/pages/jw_123john_children-of-god-1jn3-1a_htm.html', 'https://www.jesuswalk.com/123john/spokesman-sacrifice.htm': '../../jesuswalk-redesign/pages/jw_123john_spokesman-sacrifice_htm.html', 'https://www.jesuswalk.com/1corinthians/steadfast-immoveable.htm': '../../jesuswalk-redesign/pages/jw_1corinthians_steadfast-immoveable_htm.html', 'https://www.jesuswalk.com/1peter/healed-by-his-wounds.htm': '../../jesuswalk-redesign/pages/jw_1peter_healed-by-his-wounds_htm.html', 'https://www.jesuswalk.com/2corinthians/comfort-for-downcast.htm': '../../jesuswalk-redesign/pages/jw_2corinthians_comfort-for-downcast_htm.html', 'https://www.jesuswalk.com/bible-study/bible-study-journal.htm': '../../jesuswalk-redesign/pages/jw_bible-study_bible-study-journal_htm.html', 'https://www.jesuswalk.com/books/beginning.htm': '../../jesuswalk-redesign/pages/jw_books_beginning_htm.html', 'https://www.jesuswalk.com/books/luke.htm': '../../jesuswalk-redesign/pages/jw_books_luke_htm.html', 'https://www.jesuswalk.com/colossians/archippus.htm': '../../jesuswalk-redesign/pages/jw_colossians_archippus_htm.html', 'https://www.jesuswalk.com/colossians/forbearance-forgiveness.htm': '../../jesuswalk-redesign/pages/jw_colossians_forbearance-forgiveness_htm.html', 'https://www.jesuswalk.com/david/david-and-goliath-its-not-your-fight.htm': '../../jesuswalk-redesign/pages/jw_david_david-and-goliath-its-not-your-fight_htm.html', 'https://www.jesuswalk.com/early-church/sweet-incense.htm': '../../jesuswalk-redesign/pages/jw_early-church_sweet-incense_htm.html', 'https://www.jesuswalk.com/books/lords-supper.htm': '../../jesuswalk-redesign/pages/jw_ebooks_lords-supper_htm.html', 'https://www.jesuswalk.com/greatprayers/10_thy_will.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_10_thy_will_htm.html', 'https://www.jesuswalk.com/greatprayers/2_moses_intercession.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_2_moses_intercession_htm.html', 'https://www.jesuswalk.com/greatprayers/3_abraham_sodom.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_3_abraham_sodom_htm.html', 'https://www.jesuswalk.com/greatprayers/4_david_confession.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_4_david_confession_htm.html', 'https://www.jesuswalk.com/greatprayers/5_david_end.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_5_david_end_htm.html', 'https://www.jesuswalk.com/greatprayers/6_hezekiah_petition.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_6_hezekiah_petition_htm.html', 'https://www.jesuswalk.com/greatprayers/8_daniel_confession.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_8_daniel_confession_htm.html', 'https://www.jesuswalk.com/greatprayers/artwork_prayer.htm': '../../jesuswalk-redesign/pages/jw_greatprayers_artwork_prayer_htm.html', 'https://www.jesuswalk.com/hebrews/dont-neglect-church.htm': '../../jesuswalk-redesign/pages/jw_hebrews_dont-neglect-church_htm.html', 'https://www.jesuswalk.com/hebrews/sacrifice-of-praise.htm': '../../jesuswalk-redesign/pages/jw_hebrews_sacrifice-of-praise_htm.html', 'https://www.jesuswalk.com/humility/humility-husbands-serving-wives.htm': '../../jesuswalk-redesign/pages/jw_humility_humility-husbands-serving-wives_htm.html', 'https://www.jesuswalk.com/isaiah/new-thing.htm': '../../jesuswalk-redesign/pages/jw_isaiah_new-thing_htm.html', 'https://www.jesuswalk.com/jacob/why-did-this-happen-to-me.htm': '../../jesuswalk-redesign/pages/jw_jacob_why-did-this-happen-to-me_htm.html', 'https://www.jesuswalk.com/john/half-healing-bethesda.htm': '../../jesuswalk-redesign/pages/jw_john_half-healing-bethesda_htm.html', 'https://www.jesuswalk.com/kutoa/': '../../jesuswalk-redesign/pages/jw_kutoa.html', 'https://www.jesuswalk.com/lamb/lamb_4passover.htm': '../../jesuswalk-redesign/pages/jw_lamb_lamb_4passover_htm.html', 'https://www.jesuswalk.com/luke/049-ask-seek-knock.htm': '../../jesuswalk-redesign/pages/jw_lessons_11_5-13_htm.html', 'https://www.jesuswalk.com/luke/077-unjust-judge.htm': '../../jesuswalk-redesign/pages/jw_lessons_18_1-8_htm.html', 'https://www.jesuswalk.com/luke/luke.htm': '../../jesuswalk-redesign/pages/jw_lessons_22_7-20_htm.html', 'https://www.jesuswalk.com/luke/7-essential-elements-for-growing-as-disciples.htm': '../../jesuswalk-redesign/pages/jw_luke_7-essential-elements-for-growing-as-disciples_htm.html', 'https://www.jesuswalk.com/luke/catch-and-release-luke-5.htm': '../../jesuswalk-redesign/pages/jw_luke_catch-and-release-luke-5_htm.html', 'https://www.jesuswalk.com/luke/gentle-jesus-matt-11-28-30.htm': '../../jesuswalk-redesign/pages/jw_luke_gentle-jesus-matt-11-28-30_htm.html', 'https://www.jesuswalk.com/manifesto/hating-enemies.htm': '../../jesuswalk-redesign/pages/jw_manifesto_hating-enemies_htm.html', 'https://www.jesuswalk.com/peter/worship-as-incense.htm': '../../jesuswalk-redesign/pages/jw_peter_worship-as-incense_htm.html', 'https://www.jesuswalk.com/proverbs/lean-not-on-own-understanding.htm': '../../jesuswalk-redesign/pages/jw_proverbs_lean-not-on-own-understanding_htm.html', 'https://www.jesuswalk.com/psalms/admiring-legs-ps147.htm': '../../jesuswalk-redesign/pages/jw_psalms_admiring-legs-ps147_htm.html', 'https://www.jesuswalk.com/psalms/confidant-ps25-14.htm': '../../jesuswalk-redesign/pages/jw_psalms_confidant-ps25-14_htm.html', 'https://www.jesuswalk.com/psalms/heart-pilgrimage-ps84-5.htm': '../../jesuswalk-redesign/pages/jw_psalms_heart-pilgrimage-ps84-5_htm.html', 'https://www.jesuswalk.com/psalms/higher-rock-psalm-61.htm': '../../jesuswalk-redesign/pages/jw_psalms_higher-rock-psalm-61_htm.html', 'https://www.jesuswalk.com/psalms/psalm-73-glory-portion.htm': '../../jesuswalk-redesign/pages/jw_psalms_psalm-73-glory-portion_htm.html', 'https://www.jesuswalk.com/psalms/psalm-84.htm': '../../jesuswalk-redesign/pages/jw_psalms_psalm-84_htm.html', 'https://www.jesuswalk.com/psalms/psalm-86.htm': '../../jesuswalk-redesign/pages/jw_psalms_psalm-86_htm.html', 'https://www.jesuswalk.com/psalms/psalm32-hiding-place.htm': '../../jesuswalk-redesign/pages/jw_psalms_psalm32-hiding-place_htm.html', 'https://www.jesuswalk.com/psalms/thanksgiving-ps-100.htm': '../../jesuswalk-redesign/pages/jw_psalms_thanksgiving-ps-100_htm.html', 'https://www.jesuswalk.com/timothy/inspiration.htm': '../../jesuswalk-redesign/pages/jw_timothy_inspiration_htm.html', 'https://www.jesuswalk.com/timothy/skilled-workmen.htm': '../../jesuswalk-redesign/pages/jw_timothy_skilled-workmen_htm.html', 'https://www.jesuswalk.com/voice/hearing-aids.htm': '../../jesuswalk-redesign/pages/jw_voice_hearing-aids_htm.html'}

        # Find the JesusWalk homepage data which contains the full study listings
        jw_home = None
        for p in self.all_pages:
            if p.get("url") == "https://www.jesuswalk.com/":
                jw_home = p
                break

        # Define sections with their list indices from the scraped data
        # The JesusWalk homepage has lists organized as:
        # [0,1] = nav links (skip)
        # [2] = Old Testament studies
        # [3] = Gospels
        # [4] = Acts
        # [5] = Paul's Letters
        # [6] = General Letters
        # [7] = Revelation
        # [8] = Topical Studies
        sections = [
            {"label": "Old Testament", "title": "Old Testament Studies", "list_idx": 2},
            {"label": "Gospels", "title": "Gospels", "list_idx": 3},
            {"label": "Acts", "title": "Acts of the Apostles", "list_idx": 4},
            {"label": "Paul's Letters", "title": "Paul's Letters", "list_idx": 5},
            {"label": "General Letters", "title": "General Letters", "list_idx": 6},
            {"label": "Revelation", "title": "Revelation", "list_idx": 7},
            {"label": "Topical", "title": "Topical Studies", "list_idx": 8},
        ]

        sections_html = ""
        total_studies = 0

        if jw_home and "lists" in jw_home:
            lists = jw_home["lists"]
            for i, section in enumerate(sections):
                idx = section["list_idx"]
                if idx >= len(lists):
                    continue

                studies = lists[idx]
                if not studies:
                    continue

                cards_html = ""
                for study in studies:
                    text = (study.get("text", "") or "").strip()
                    orig_link = study.get("link", "")
                    if not text or not orig_link:
                        continue

                    # Clean the text: split name from description
                    # Format is like "Abraham(10 studies from Genesis 12-25)"
                    text = re.sub(r'\r?\n\s*', ' ', text).strip()
                    match = re.match(r'^(.+?)\((.+?)\)$', text)
                    if match:
                        name = match.group(1).strip()
                        desc = match.group(2).strip()
                    else:
                        # Try to separate at first digit
                        parts = re.split(r'(\d+\s+lessons)', text, 1)
                        if len(parts) > 1:
                            name = parts[0].strip()
                            desc = parts[1].strip()
                            if len(parts) > 2:
                                desc += parts[2].strip()
                        else:
                            name = text
                            desc = ""

                    total_studies += 1

                    cards_html += f'''
        <a href="{JW_URL_MAP.get(orig_link) or escape(orig_link)}" class="study-card" style="text-decoration: none; color: inherit;">
          <div class="study-card-category">{section["label"]}</div>
          <h3>{escape(name)}</h3>
          {f'<p>{escape(desc)}</p>' if desc else ''}
          <div class="study-card-meta"><span>
            {"Start Study →" if JW_URL_MAP.get(orig_link) else "Open on JesusWalk.com →"}
          </span></div>
        </a>'''

                margin = 'margin-top: 80px;' if i > 0 else ''
                sections_html += f'''
      <div class="section-header" style="{margin}"><div class="section-label">{section["label"]}</div><h2 class="section-title">{section["title"]}</h2></div>
      <div class="studies-grid">{cards_html}
      </div>'''

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Explore Scripture</div>
      <h1>Free Bible Study <em>Series</em></h1>
      <p class="hero-description">Over {total_studies} free, e-mail delivered Bible studies designed to build disciples. Join tens of thousands studying in 120+ countries.</p>
      <div class="hero-actions">
    <a href="../../jesuswalk-redesign/index.html" class="btn btn-primary">Browse JesusWalk Site</a>
    <a href="../../jesuswalk-redesign/pages/all-studies.html" class="btn btn-secondary">Full Study Catalog</a>
  </div>
    </div></div>
  </section>
  <section class="section">
    <div class="container">{sections_html}
    </div>
  </section>'''
        return self.build_page("Bible Studies", content, description=f"Over {total_studies} free Bible studies from Dr. Ralph F. Wilson — Old Testament, New Testament, and Topical.")

    def generate_books_page(self):
        content = '''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Deeper Study</div>
      <h1>Books by Dr. Ralph F. <em>Wilson</em></h1>
      <p class="hero-description">Over 50 titles available in paperback, PDF, and Kindle from Amazon.</p>
      <div class="hero-actions"><a href="https://www.amazon.com/stores/Ralph-F.-Wilson/author/B001IU2RMU" class="btn btn-primary" target="_blank" rel="noopener">Browse on Amazon</a></div>
    </div></div>
  </section>
  <section class="section">
    <div class="container">
      <div class="studies-grid">
        <div class="study-card"><div class="study-card-category">Old Testament</div><h3>OT Study Books</h3><p>Abraham, Moses, David, Elijah, Psalms, Isaiah, Daniel, and post-exilic prophets.</p><div class="study-card-meta"><span>14+ books</span></div></div>
        <div class="study-card"><div class="study-card-category">Gospels</div><h3>Gospel Study Books</h3><p>Sermon on the Mount, Luke, John, Parables, 7 Last Words, and more.</p><div class="study-card-meta"><span>10+ books</span></div></div>
        <div class="study-card"><div class="study-card-category">Paul\'s Letters</div><h3>Epistles Study Books</h3><p>Romans, Corinthians, Galatians, Ephesians, Philippians, Colossians, and more.</p><div class="study-card-meta"><span>12+ books</span></div></div>
        <div class="study-card"><div class="study-card-category">Topical</div><h3>Topical Study Books</h3><p>Grace, Holy Spirit, Prayer, Discipleship, Humility, Names of God and Jesus.</p><div class="study-card-meta"><span>12+ books</span></div></div>
      </div>
    </div>
  </section>'''
        return self.build_page("Books", content, description="50+ Bible study books by Dr. Ralph F. Wilson.")

    def generate_podcast_page(self):
        content = '''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Listen Anywhere</div>
      <h1>The Joyful Heart <em>Podcast</em></h1>
      <p class="hero-description">Meditations from the Joyful Heart newsletter, read by Dr. Ralph F. Wilson. Available on all major platforms.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container">
      <div class="podcast-banner animate-in">
        <div class="podcast-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg></div>
        <div class="podcast-info">
          <h3>The Joyful Heart with Dr. Ralph F. Wilson</h3>
          <p>Published 6-8 times per year with encouraging meditations drawn from decades of pastoral ministry.</p>
          <div class="podcast-platforms">
            <a href="https://open.spotify.com/show/23YKefC8XYhqnROp0Kt72R" class="podcast-platform" target="_blank" rel="noopener">Spotify</a>
            <a href="https://podcasts.apple.com/podcast/the-joyful-heart/id1827342398" class="podcast-platform" target="_blank" rel="noopener">Apple Podcasts</a>
            <a href="https://pca.st/06fup8em" class="podcast-platform" target="_blank" rel="noopener">Pocket Casts</a>
            <a href="https://overcast.fm/itunes1827342398" class="podcast-platform" target="_blank" rel="noopener">Overcast</a>
          </div>
        </div>
      </div>
    </div>
  </section>'''
        return self.build_page("Podcast", content, description="The Joyful Heart Podcast — meditations by Dr. Ralph F. Wilson.")

    def generate_faq_page(self):
        faq_data = None
        for p in self.all_pages:
            if p.get("category") == "faq":
                faq_data = p
                break
        faq_items = ""
        if faq_data:
            paras = self.extract_clean_paragraphs(faq_data)
            for ptype, text in paras:
                if ptype == "p" and len(text) > 30:
                    faq_items += f'''
        <div class="study-card animate-in" style="margin-bottom: 0;">
          <p style="color: var(--text-secondary);">{escape(text)}</p>
        </div>'''

        content = f'''
  <section class="hero" style="padding-bottom: 40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Help</div>
      <h1>Frequently Asked <em>Questions</em></h1>
      <p class="hero-description">Common questions about our Bible studies, articles, and ministry.</p>
    </div></div>
  </section>
  <section class="section">
    <div class="container" style="max-width: 800px;">
      <div style="display: flex; flex-direction: column; gap: 16px;">
        {faq_items}
      </div>
    </div>
  </section>'''
        return self.build_page("FAQ", content, description="Frequently asked questions about Joyful Heart Renewal Ministries.")

    # ==========================================
    # MAIN GENERATION
    # ==========================================

    def generate_all(self):
        print(f"\n{'='*70}")
        print(f"  JOYFUL HEART PAGE GENERATOR — PHASE 3 (REFINED)")
        print(f"  Output: {os.path.abspath(self.output_dir)}")
        print(f"{'='*70}\n")

        generated = 0

        # 1. Core pages
        core = {
            "about.html": self.generate_about_page(),
            "contact.html": self.generate_contact_page(),
            "giving.html": self.generate_giving_page(),
            "newsletter.html": self.generate_newsletter_page(),
            "bible-studies.html": self.generate_bible_studies_page(),
            "books.html": self.generate_books_page(),
            "podcast.html": self.generate_podcast_page(),
            "faq.html": self.generate_faq_page(),
            "articles.html": self.generate_articles_index(),
    'https://www.jesuswalk.com/2peter/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters',
    'https://www.jesuswalk.com/7-last-words/': '../../jesuswalk-redesign/pages/all-studies.html#gospels',
    'https://www.jesuswalk.com/advent/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/ascent/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament',
    'https://www.jesuswalk.com/christ-power/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/christmas-incarnation/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/church/': '../../jesuswalk-redesign/pages/all-studies.html#acts',
    'https://www.jesuswalk.com/gideon/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament',
    'https://www.jesuswalk.com/glory/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/joshua/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament',
    'https://www.jesuswalk.com/kingdom/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/lamb-revelation/': '../../jesuswalk-redesign/pages/all-studies.html#revelation',
    'https://www.jesuswalk.com/lords-supper': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/names-god/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/names-jesus/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/paul/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters',
    'https://www.jesuswalk.com/peter/': '../../jesuswalk-redesign/pages/all-studies.html#general-letters',
    'https://www.jesuswalk.com/rebuild/': '../../jesuswalk-redesign/pages/all-studies.html#old-testament',
    'https://www.jesuswalk.com/spirit/': '../../jesuswalk-redesign/pages/all-studies.html#topical',
    'https://www.jesuswalk.com/thessalonians/': '../../jesuswalk-redesign/pages/all-studies.html#pauls-letters',
        }
        for filename, html in core.items():
            with open(os.path.join(self.pages_dir, filename), "w", encoding="utf-8") as f:
                f.write(html)
            generated += 1
            print(f"  [CORE] {filename}")

        # 2. Category pages
        cats = ["jesus", "maturity", "encourag", "evang", "church",
                "communion", "prayer", "scholar", "christmas", "easter",
                "thanksgiving", "pentecost", "stpatrick", "art", "misc",
                "plant", "holiday", "psalms", "luke", "greatprayers"]
        for cat in cats:
            if cat in self.by_category:
                html = self.generate_category_page(cat)
                with open(os.path.join(self.pages_dir, f"cat-{cat}.html"), "w", encoding="utf-8") as f:
                    f.write(html)
                generated += 1
                print(f"  [CAT]  cat-{cat}.html ({len(self.by_category[cat])} articles)")

        # 3. Individual article pages
        article_count = 0
        for page in self.all_pages:
            url = page.get("url", "")
            if ".htm" not in url:
                continue
            if page.get("category", "") in ["home", "menu", "search", "admin", "sitemap.html"]:
                continue
            html = self.generate_article_page(page)
            filename = self._url_to_filename(url) + ".html"
            with open(os.path.join(self.pages_dir, filename), "w", encoding="utf-8") as f:
                f.write(html)
            article_count += 1
            generated += 1

        print(f"\n  [ARTICLES] Generated {article_count} article pages")
        print(f"\n{'='*70}")
        print(f"  GENERATION COMPLETE — {generated} pages")
        print(f"  Output: {os.path.abspath(self.pages_dir)}")
        print(f"{'='*70}\n")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    gen = PageGenerator(os.path.join(base, "scraped_data"), base)
    gen.generate_all()
