#!/usr/bin/env python3
"""JesusWalk Page Generator — builds all inner pages from scraped data."""

import json
import os
import re
from html import escape

class JWPageGenerator:
    def __init__(self, scraped_dir, output_dir):
        self.scraped_dir = scraped_dir
        self.output_dir = output_dir
        self.all_pages = []
        self.jw_pages = []
        self.load_data()

    def load_data(self):
        pages_dir = os.path.join(self.scraped_dir, "pages")
        for f in sorted(os.listdir(pages_dir)):
            if f.endswith(".json") and f != "sitemap.json" and f != "failed_urls.json":
                with open(os.path.join(pages_dir, f), "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    data["_filename"] = f
                    self.all_pages.append(data)
                    if f.startswith("jw_"):
                        self.jw_pages.append(data)
        print(f"Loaded {len(self.all_pages)} total pages, {len(self.jw_pages)} JesusWalk pages")

    # ── Navigation boilerplate filter ──
    NAV_PATTERNS = [
        r"^HomeBible Studies",
        r"^Old TestamentNew",
        r"^Beginning the Journey.*?Sitemap$",
        r"^Bible StudiesArticles",
        r"^Home\|Bible Studies",
        r"^Copyright ©",
        r"^Joyful Heart Renewal Ministries",
        r"^Free\s+E-mail Bible Study",
        r"FirstLastE-mail",
        r"Preferred FormatHTML",
        r"\[X\] Close Window",
        r"^To be notified about future",
        r"subscribe to our free newsletter",
        r"We respect your\s*privacy",
        r"See legal, copyright",
        r"Contributions\s*to Joyful Heart",
        r"please\s*bookmark this page",
    ]

    def is_nav_text(self, text):
        t = text.strip()
        if len(t) < 3:
            return True
        for pat in self.NAV_PATTERNS:
            if re.search(pat, t, re.IGNORECASE | re.DOTALL):
                return True
        return False

    def extract_clean_paragraphs(self, page):
        raw = page.get("paragraphs", [])
        clean = []
        for p in raw:
            p = (p or "").strip()
            if not p or self.is_nav_text(p):
                continue
            # Clean whitespace
            p = re.sub(r'\r?\n\s*', ' ', p).strip()
            # Skip very short (likely UI element text)
            if len(p) < 15:
                continue
            clean.append(p)
        return clean

    def classify_paragraph(self, text):
        """Classify paragraph as scripture, question, or normal."""
        scripture_indicators = [
            r'\(\w+\s+\d+:\d+',       # (Romans 12:1)
            r'--\s*\w+\s+\d+:\d+',    # -- Romans 12:1
            r'\d+:\d+[a-d]?\)',        # 12:1a)
        ]
        question_indicators = [
            r'^Q\d+\.',
            r'^Question\s+\d+',
            r'^\d+\.\s+.*\?$',
        ]
        for pat in scripture_indicators:
            if re.search(pat, text):
                # Only if it's a quotation-like text (italicized, starts with quote)
                if text.startswith('"') or text.startswith("'") or text.startswith('\u201c'):
                    return "scripture"
        for pat in question_indicators:
            if re.search(pat, text, re.IGNORECASE):
                return "question"
        return "normal"

    def filter_content_images(self, images):
        """Filter to only meaningful content images."""
        skip_names = [
            "search-icon", "menu-icon", "bible_study_head", "books_head",
            "navigation_head", "books-available", "at_sign", "pencil",
            "caa-sm-cross", "bible_icon", "youtube-logo", "addthis",
            "podcast-60x60",
        ]
        keep = []
        for img in images:
            src = (img.get("src", "") or "").lower()
            alt = img.get("alt", "") or ""
            local = (img.get("local_file", "") or "").lower()
            w = int(img.get("width", 0) or 0)
            h = int(img.get("height", 0) or 0)
            if w > 0 and h > 0 and (w < 30 or h < 30):
                continue
            skip = False
            for name in skip_names:
                if name in src or name in local:
                    skip = True
                    break
            if skip:
                continue
            if local or alt:
                keep.append(img)
        return keep

    def render_article_body(self, page):
        paragraphs = self.extract_clean_paragraphs(page)
        images = self.filter_content_images(page.get("images", []))
        if not paragraphs:
            return '<div class="empty-notice"><p>Content for this study is available on the original site.</p></div>'

        html_parts = []
        img_idx = 0
        for i, p in enumerate(paragraphs):
            cls = self.classify_paragraph(p)
            escaped = escape(p)
            if cls == "scripture":
                html_parts.append(f'<blockquote class="scripture-quote">{escaped}</blockquote>')
            elif cls == "question":
                label_match = re.match(r'^(Q(?:uestion)?\s*\d+\.?)\s*(.*)', p, re.IGNORECASE)
                if label_match:
                    html_parts.append(f'<div class="discussion-question"><strong>{escape(label_match.group(1))}</strong> {escape(label_match.group(2))}</div>')
                else:
                    html_parts.append(f'<div class="discussion-question">{escaped}</div>')
            else:
                html_parts.append(f'<p>{escaped}</p>')

            # Insert image after first few paragraphs
            if i in (1, 4, 8) and img_idx < len(images):
                img = images[img_idx]
                local = img.get("local_file", "")
                alt = escape(img.get("alt", "") or "")
                if local:
                    img_src = f"../scraped_data/images/{local}"
                    html_parts.append(f'<figure class="article-figure"><img src="{img_src}" alt="{alt}" loading="lazy"><figcaption>{alt}</figcaption></figure>')
                    img_idx += 1

        return "\n".join(html_parts)

    def get_excerpt(self, page, max_len=160):
        paragraphs = self.extract_clean_paragraphs(page)
        for p in paragraphs:
            if len(p) > 40:
                return p[:max_len] + "..." if len(p) > max_len else p
        return page.get("title", "")

    # ── Page template ──
    def build_page(self, title, content, description=""):
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{escape(description or title)}">
<title>{escape(title)} — JesusWalk Bible Study Series</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../index.css">
</head>
<body>
<nav class="navbar scrolled"><div class="container nav-container">
<a href="../index.html" class="nav-brand">
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
  <div><span class="brand-name">JesusWalk</span><span class="brand-tagline">BIBLE STUDY SERIES</span></div>
</a>
<div class="nav-links">
  <a href="all-studies.html">All Studies</a>
  <a href="books.html">Books</a>
  <a href="podcast.html">Podcast</a>
  <a href="beginning.html">New Believers</a>
  <a href="all-studies.html" class="btn btn-primary nav-cta">Start Studying</a>
</div>
</div></nav>
{content}
<footer class="footer"><div class="container">
<div class="footer-bottom">
  <span>© 2026 Joyful Heart Renewal Ministries, Inc. — Dr. Ralph F. Wilson</span>
  <span><a href="../index.html" style="color: var(--color-secondary-light);">JesusWalk Home</a></span>
</div>
</div></footer>
</body>
</html>'''

    # ── Page generators ──
    def generate_all_studies_page(self):
        """Build the full studies catalog from jw_index.json."""
        jw_home = None
        for p in self.all_pages:
            if p.get("url") == "https://www.jesuswalk.com/":
                jw_home = p
                break

        sections = [
            {"label": "Old Testament", "title": "Old Testament Studies", "list_idx": 2, "anchor": "old-testament"},
            {"label": "Gospels", "title": "Gospels", "list_idx": 3, "anchor": "gospels"},
            {"label": "Acts", "title": "Acts of the Apostles", "list_idx": 4, "anchor": "acts"},
            {"label": "Paul's Letters", "title": "Paul's Letters", "list_idx": 5, "anchor": "pauls-letters"},
            {"label": "General Letters", "title": "General Letters", "list_idx": 6, "anchor": "general-letters"},
            {"label": "Revelation", "title": "Revelation", "list_idx": 7, "anchor": "revelation"},
            {"label": "Topical", "title": "Topical Studies", "list_idx": 8, "anchor": "topical"},
        ]

        shtml = ""
        total = 0
        if jw_home and "lists" in jw_home:
            lists = jw_home["lists"]
            for i, sec in enumerate(sections):
                idx = sec["list_idx"]
                if idx >= len(lists):
                    continue
                studies = lists[idx]
                if not studies:
                    continue
                cards = ""
                for study in studies:
                    text = (study.get("text", "") or "").strip()
                    link = study.get("link", "")
                    if not text or not link:
                        continue
                    text = re.sub(r'\r?\n\s*', ' ', text).strip()
                    match = re.match(r'^(.+?)\((.+?)\)$', text)
                    if match:
                        name, desc = match.group(1).strip(), match.group(2).strip()
                    else:
                        name, desc = text, ""
                    total += 1
                    cards += f'''
        <a href="{escape(link)}" class="study-card" style="text-decoration:none;color:inherit;" target="_blank" rel="noopener">
          <div class="study-card-category">{sec["label"]}</div>
          <h3>{escape(name)}</h3>
          {f'<p>{escape(desc)}</p>' if desc else ''}
          <div class="study-card-meta"><span>Start Study →</span></div>
        </a>'''
                margin = 'margin-top:80px;' if i > 0 else ''
                shtml += f'''
      <div id="{sec["anchor"]}" class="section-header" style="{margin}">
        <div class="section-label">{sec["label"]}</div>
        <h2 class="section-title">{sec["title"]}</h2>
      </div>
      <div class="studies-grid">{cards}</div>'''

        content = f'''
  <section class="hero" style="padding-bottom:40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Full Catalog</div>
      <h1>All {total} Bible <em>Studies</em></h1>
      <p class="hero-description">Browse the complete JesusWalk Bible Study Series — Old Testament, New Testament, and Topical.</p>
    </div></div>
  </section>
  <section class="section"><div class="container">{shtml}</div></section>'''
        return self.build_page("All Bible Studies", content, f"Browse all {total} free JesusWalk Bible studies.")

    def generate_study_article_page(self, page):
        """Generate individual study/article page."""
        title = page.get("title", "Study")
        # Clean title
        title = re.sub(r'\s*--.*$', '', title).strip()
        title = re.sub(r',\s*by Dr\..*$', '', title).strip()
        url = page.get("url", "")
        category = page.get("category", "study")
        body = self.render_article_body(page)

        # Find related pages in same category
        related = ""
        same_cat = [p for p in self.jw_pages if p.get("category") == category and p.get("url") != url][:4]
        if same_cat:
            rcards = ""
            for r in same_cat:
                rtitle = r.get("title", "").split("--")[0].split(",")[0].strip()[:60]
                fname = r["_filename"].replace(".json", ".html")
                excerpt = self.get_excerpt(r, 80)
                rcards += f'''<a href="{fname}" class="related-card"><div class="related-card-tag">{escape(category)}</div><h4>{escape(rtitle)}</h4><p>{escape(excerpt)}</p></a>'''
            related = f'<div class="related-articles"><h3>More Studies</h3><div class="related-grid">{rcards}</div></div>'

        content = f'''
  <section class="hero" style="padding-bottom:40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> {escape(category.upper())}</div>
      <h1>{escape(title)}</h1>
      <p class="hero-description">By Dr. Ralph F. Wilson</p>
    </div></div>
  </section>
  <section class="section"><div class="container" style="max-width:800px;">
    <div class="article-body">{body}</div>
    {related}
    <div class="article-nav-bar">
      <a href="all-studies.html" class="btn btn-secondary">← All Studies</a>
      {f'<a href="{escape(url)}" class="btn btn-primary" target="_blank" rel="noopener">View on JesusWalk.com</a>' if url else ''}
    </div>
  </div></section>'''
        return self.build_page(title, content, page.get("meta_description", ""))

    def generate_books_page(self):
        books_data = None
        for p in self.all_pages:
            if p.get("url") == "https://www.jesuswalk.com/books/":
                books_data = p
                break

        body = ""
        if books_data:
            body = self.render_article_body(books_data)

        content = f'''
  <section class="hero" style="padding-bottom:40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Books</div>
      <h1>JesusWalk <em>Books</em></h1>
      <p class="hero-description">Available in paperback, Kindle, and PDF formats from Amazon.</p>
      <div class="hero-actions"><a href="https://www.jesuswalk.com/books/" class="btn btn-primary" target="_blank">Browse on JesusWalk.com</a></div>
    </div></div>
  </section>
  <section class="section"><div class="container" style="max-width:800px;">
    <div class="article-body">{body if body else '<p>Over 50 books available — paperback, Kindle, and PDF formats. Visit <a href="https://www.jesuswalk.com/books/">JesusWalk Books</a> for the full catalog.</p>'}</div>
  </div></section>'''
        return self.build_page("Books", content, "JesusWalk books — paperback, Kindle, and PDF.")

    def generate_podcast_page(self):
        pod_data = None
        for p in self.all_pages:
            if p.get("url") == "https://www.jesuswalk.com/podcast/":
                pod_data = p
                break
        body = ""
        if pod_data:
            body = self.render_article_body(pod_data)

        content = f'''
  <section class="hero" style="padding-bottom:40px;">
    <div class="container"><div class="hero-content animate-in">
      <div class="hero-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="5"/></svg> Podcast</div>
      <h1>JesusWalk <em>Podcast</em></h1>
      <p class="hero-description">Listen to Bible study lessons on the go — available on major podcast platforms.</p>
      <div class="hero-actions"><a href="https://www.jesuswalk.com/podcast/" class="btn btn-primary" target="_blank">Listen Now</a></div>
    </div></div>
  </section>
  <section class="section"><div class="container" style="max-width:800px;">
    <div class="article-body">{body if body else '<p>JesusWalk Bible study lessons are available as free podcasts.</p>'}</div>
  </div></section>'''
        return self.build_page("Podcast", content, "JesusWalk podcast — Bible studies you can listen to.")

    def generate_all(self):
        os.makedirs(self.output_dir, exist_ok=True)
        count = 0

        # Core pages
        pages = {
            "all-studies.html": self.generate_all_studies_page(),
            "books.html": self.generate_books_page(),
            "podcast.html": self.generate_podcast_page(),
        }

        for fname, html in pages.items():
            path = os.path.join(self.output_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1

        # Individual study/article pages
        for page in self.jw_pages:
            fname = page["_filename"].replace(".json", ".html")
            # Skip the main index
            if fname == "jw_index.html":
                fname = "all-studies-home.html"
            html = self.generate_study_article_page(page)
            path = os.path.join(self.output_dir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            count += 1

        # Create aliases for key pages
        aliases = {
            "beginning.html": "jw_beginning.html",
            "discipleship.html": "jw_discipleship.html",
            "bible-study-tips.html": "jw_bible-study.html",
        }
        for alias, target in aliases.items():
            src_path = os.path.join(self.output_dir, target)
            dst_path = os.path.join(self.output_dir, alias)
            if os.path.exists(src_path):
                import shutil
                shutil.copy2(src_path, dst_path)
                count += 1

        print(f"\n{'='*53}")
        print(f"  Generated {count} JesusWalk pages")
        print(f"  Output: {self.output_dir}")
        print(f"{'='*53}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scraped = os.path.join(os.path.dirname(base), "joyful-heart-redesign", "scraped_data")
    output = os.path.join(base, "pages")
    gen = JWPageGenerator(scraped, output)
    gen.generate_all()
