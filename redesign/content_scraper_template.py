#!/usr/bin/env python3
"""
Website Content Scraper — Reusable Template
=============================================
BFS crawler that extracts structured content from any website.
Configure the settings below, then run: python content_scraper_template.py

Output:
  scraped_data/
    pages/       <- JSON files, one per page
    images/      <- Downloaded images
    sitemap.json <- URL → filename map
    summary.txt  <- Scrape statistics
"""

import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import hashlib
from urllib.parse import urljoin, urlparse, urlunparse
from datetime import datetime
from collections import deque

# ═══════════════════════════════════════════════════════════════════
# CONFIGURATION — Update these for each project
# ═══════════════════════════════════════════════════════════════════

START_URLS = [
    # Add target website URL(s) here
    # "https://www.example.com",
]

ALLOWED_DOMAINS = [
    # Only crawl pages on these domains
    # "www.example.com",
    # "example.com",
]

MAX_PAGES = 300         # Maximum pages to crawl
OUTPUT_DIR = "scraped_data"  # Where to save output
DELAY = 1.0             # Seconds between requests (be polite)
DOWNLOAD_IMAGES = True  # Download images locally

# File extensions to skip
SKIP_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
    '.zip', '.rar', '.tar', '.gz', '.mp3', '.mp4', '.wav',
    '.avi', '.mov', '.wmv', '.exe', '.dmg', '.iso',
}

# URL patterns to skip
SKIP_PATTERNS = [
    '/wp-admin/', '/wp-login', '/feed/', '/xmlrpc',
    'javascript:', 'mailto:', 'tel:', '#',
    '/cart', '/checkout', '/login', '/register',
]


# ═══════════════════════════════════════════════════════════════════
# SCRAPER ENGINE — Don't modify below unless customizing
# ═══════════════════════════════════════════════════════════════════

class WebsiteScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.visited = set()
        self.pages_data = {}
        self.image_map = {}
        self.errors = []

        # Create output dirs
        self.pages_dir = os.path.join(OUTPUT_DIR, "pages")
        self.images_dir = os.path.join(OUTPUT_DIR, "images")
        os.makedirs(self.pages_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)

    def normalize_url(self, url):
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        path = parsed.path.rstrip('/')
        if not path:
            path = '/'
        normalized = urlunparse((
            parsed.scheme, parsed.netloc.lower(),
            path, '', '', ''
        ))
        return normalized

    def is_valid_url(self, url):
        """Check if URL should be crawled."""
        parsed = urlparse(url)
        if not parsed.scheme.startswith('http'):
            return False
        if parsed.netloc.lower() not in [d.lower() for d in ALLOWED_DOMAINS]:
            return False
        path_lower = parsed.path.lower()
        ext = os.path.splitext(path_lower)[1]
        if ext in SKIP_EXTENSIONS:
            return False
        for pattern in SKIP_PATTERNS:
            if pattern in url.lower():
                return False
        return True

    def fetch_page(self, url, retries=2):
        """Fetch a page with retries."""
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(url, timeout=15, allow_redirects=True)
                if resp.status_code == 200:
                    return resp
                elif resp.status_code == 429:
                    time.sleep(5)
                else:
                    return None
            except Exception as e:
                if attempt < retries:
                    time.sleep(2)
                else:
                    self.errors.append(f"FETCH ERROR: {url} - {e}")
        return None

    def download_image(self, img_url, page_url):
        """Download an image and save locally."""
        if not DOWNLOAD_IMAGES:
            return None
        if img_url in self.image_map:
            return self.image_map[img_url]

        try:
            full_url = urljoin(page_url, img_url)
            resp = self.session.get(full_url, timeout=10, stream=True)
            if resp.status_code != 200:
                return None

            ext = os.path.splitext(urlparse(full_url).path)[1][:5] or '.jpg'
            name_hash = hashlib.md5(full_url.encode()).hexdigest()[:12]
            filename = f"img_{name_hash}{ext}"
            filepath = os.path.join(self.images_dir, filename)

            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    for chunk in resp.iter_content(8192):
                        f.write(chunk)

            self.image_map[img_url] = filename
            return filename
        except Exception:
            return None

    def extract_content(self, html, url):
        """Extract structured content from a page."""
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script/style/nav tags for cleaner content
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()

        # Title
        title = ''
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        h1 = soup.find('h1')
        if h1:
            title = h1.get_text(strip=True)

        # Meta description
        meta_desc = ''
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            meta_desc = meta.get('content', '')

        # Headings (h1-h6)
        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f'h{level}'):
                text = h.get_text(strip=True)
                if text and len(text) > 2:
                    headings.append({'level': level, 'text': text})

        # Paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 10:
                paragraphs.append(text)

        # Images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src and not src.startswith('data:'):
                local_file = self.download_image(src, url)
                images.append({
                    'src': src,
                    'alt': alt,
                    'local': local_file
                })

        # Links (internal)
        links = []
        for a in soup.find_all('a', href=True):
            href = urljoin(url, a['href'])
            text = a.get_text(strip=True)
            if text:
                links.append({'href': href, 'text': text[:100]})

        # Lists
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = [li.get_text(strip=True) for li in ul.find_all('li') if li.get_text(strip=True)]
            if items:
                lists.append(items)

        return {
            'url': url,
            'title': title,
            'meta_description': meta_desc,
            'headings': headings,
            'paragraphs': paragraphs,
            'images': images,
            'links': links,
            'lists': lists,
            'scraped_at': datetime.now().isoformat(),
        }

    def discover_links(self, html, base_url):
        """Find all internal links on a page."""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = urljoin(base_url, a['href'])
            normalized = self.normalize_url(href)
            if self.is_valid_url(normalized) and normalized not in self.visited:
                links.add(normalized)
        return links

    def url_to_filename(self, url):
        """Convert URL to a safe filename."""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = 'index'
        safe = re.sub(r'[^\w\-]', '_', path)
        safe = re.sub(r'_+', '_', safe).strip('_')
        return safe[:80] + '.json'

    def crawl(self):
        """BFS crawl starting from START_URLS."""
        if not START_URLS:
            print("ERROR: No START_URLS configured. Edit the CONFIGURATION section.")
            return

        if not ALLOWED_DOMAINS:
            # Auto-detect domains from start URLs
            for url in START_URLS:
                domain = urlparse(url).netloc
                if domain not in ALLOWED_DOMAINS:
                    ALLOWED_DOMAINS.append(domain)

        print(f"Starting crawl of {len(START_URLS)} URL(s)")
        print(f"Allowed domains: {ALLOWED_DOMAINS}")
        print(f"Max pages: {MAX_PAGES}")
        print(f"Output: {OUTPUT_DIR}/")
        print("=" * 60)

        queue = deque()
        for url in START_URLS:
            norm = self.normalize_url(url)
            queue.append(norm)

        start_time = time.time()
        count = 0

        while queue and count < MAX_PAGES:
            url = queue.popleft()
            if url in self.visited:
                continue
            self.visited.add(url)

            resp = self.fetch_page(url)
            if not resp:
                continue

            count += 1
            content_type = resp.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                continue

            html = resp.text
            page_data = self.extract_content(html, url)

            # Save JSON
            filename = self.url_to_filename(url)
            filepath = os.path.join(self.pages_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)

            self.pages_data[url] = filename
            print(f"  [{count}/{MAX_PAGES}] {url} -> {filename}")

            # Discover new links
            new_links = self.discover_links(html, url)
            for link in new_links:
                if link not in self.visited:
                    queue.append(link)

            time.sleep(DELAY)

        elapsed = time.time() - start_time
        self._save_summary(count, elapsed)

    def _save_summary(self, count, elapsed):
        """Save sitemap and summary."""
        # Sitemap
        sitemap_path = os.path.join(OUTPUT_DIR, "sitemap.json")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            json.dump(self.pages_data, f, indent=2)

        # Image map
        imgmap_path = os.path.join(OUTPUT_DIR, "image_map.json")
        with open(imgmap_path, 'w', encoding='utf-8') as f:
            json.dump(self.image_map, f, indent=2)

        # Summary
        summary_path = os.path.join(OUTPUT_DIR, "summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Scrape Summary\n{'='*40}\n")
            f.write(f"Start URLs: {START_URLS}\n")
            f.write(f"Domains: {ALLOWED_DOMAINS}\n")
            f.write(f"Pages scraped: {count}\n")
            f.write(f"Images downloaded: {len(self.image_map)}\n")
            f.write(f"Errors: {len(self.errors)}\n")
            f.write(f"Time: {elapsed:.1f}s\n")
            if self.errors:
                f.write(f"\nErrors:\n")
                for err in self.errors:
                    f.write(f"  {err}\n")

        print(f"\n{'='*60}")
        print(f"DONE: {count} pages scraped in {elapsed:.1f}s")
        print(f"  Pages: {self.pages_dir}/ ({count} files)")
        print(f"  Images: {self.images_dir}/ ({len(self.image_map)} files)")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Sitemap: {sitemap_path}")


if __name__ == '__main__':
    scraper = WebsiteScraper()
    scraper.crawl()
