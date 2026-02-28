"""
Joyful Heart Content Scraper
=============================
Purpose-built scraper to extract ALL content from joyfulheart.com and jesuswalk.com
for full website redesign. Based on the website-analyzer-poc stack.

Features:
- Crawls from homepage, discovers all internal links
- Extracts: title, headings, paragraphs, images, links, navigation
- Saves structured JSON per page + full sitemap
- Downloads key images (Dr. Wilson's photo, logos, etc.)
- Zero cloud cost — runs 100% locally

Usage:
    python content_scraper.py
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


class JoyfulHeartScraper:
    def __init__(self, output_dir="scraped_data"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

        self.output_dir = output_dir
        self.images_dir = os.path.join(output_dir, "images")
        self.pages_dir = os.path.join(output_dir, "pages")
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.pages_dir, exist_ok=True)

        # Tracking
        self.visited = set()
        self.failed = []
        self.all_pages = []
        self.sitemap = {}
        self.downloaded_images = {}

        # Domains we're allowed to crawl
        self.allowed_domains = ["www.joyfulheart.com", "joyfulheart.com",
                                 "www.jesuswalk.com", "jesuswalk.com"]

        # Skip patterns (binary files, external links, anchors-only)
        self.skip_extensions = {'.pdf', '.doc', '.docx', '.mp3', '.mp4', '.wav',
                                '.zip', '.rar', '.exe', '.png', '.jpg', '.jpeg',
                                '.gif', '.svg', '.ico', '.css', '.js', '.xml',
                                '.rss', '.atom'}

        self.skip_patterns = [
            '/wp-login', '/wp-admin', '/feed/', '/xmlrpc',
            'javascript:', 'mailto:', 'tel:', '#',
        ]

    def normalize_url(self, url):
        """Normalize URL for deduplication"""
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme or 'https',
            parsed.netloc.lower(),
            parsed.path.rstrip('/') or '/',
            parsed.params,
            parsed.query,
            ''  # no fragment
        ))
        return normalized

    def is_valid_url(self, url):
        """Check if URL should be crawled"""
        parsed = urlparse(url)

        # Must be in allowed domains
        if parsed.netloc.lower() not in self.allowed_domains:
            return False

        # Skip binary files
        path_lower = parsed.path.lower()
        for ext in self.skip_extensions:
            if path_lower.endswith(ext):
                return False

        # Skip known patterns
        for pattern in self.skip_patterns:
            if pattern in url.lower():
                return False

        return True

    def fetch_page(self, url, retries=2):
        """Fetch a page with retries"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=20, allow_redirects=True)
                if response.status_code == 200:
                    return response.text, response.url
                elif response.status_code == 404:
                    return None, None
                else:
                    time.sleep(1)
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    return None, None
        return None, None

    def download_image(self, img_url, page_url):
        """Download an image and save locally"""
        if img_url in self.downloaded_images:
            return self.downloaded_images[img_url]

        try:
            full_url = urljoin(page_url, img_url)
            response = self.session.get(full_url, timeout=15, stream=True)
            if response.status_code == 200:
                # Generate filename from URL
                parsed = urlparse(full_url)
                ext = os.path.splitext(parsed.path)[1] or '.jpg'
                name = os.path.basename(parsed.path) or 'image'
                if not name.endswith(ext):
                    name = name + ext

                # Make unique
                hash_prefix = hashlib.md5(full_url.encode()).hexdigest()[:8]
                safe_name = f"{hash_prefix}_{name}"
                safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)

                filepath = os.path.join(self.images_dir, safe_name)
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)

                self.downloaded_images[img_url] = safe_name
                return safe_name
        except Exception:
            pass
        return None

    def extract_content(self, html, url):
        """Extract structured content from a page"""
        soup = BeautifulSoup(html, 'html.parser')

        # --- Title ---
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)

        # --- Meta Description ---
        meta_desc = ""
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag:
            meta_desc = meta_tag.get('content', '')

        # --- Headings ---
        headings = []
        for level in range(1, 7):
            for h in soup.find_all(f'h{level}'):
                text = h.get_text(strip=True)
                if text:
                    headings.append({
                        'level': level,
                        'text': text
                    })

        # --- Main Content ---
        # Try to find the main content area (skip nav/footer)
        # JoyfulHeart uses tables, so we look for the widest content area
        content_blocks = []

        # Remove script, style, nav elements
        for tag in soup.find_all(['script', 'style', 'noscript']):
            tag.decompose()

        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 20:  # Skip tiny fragments
                paragraphs.append(text)

        # Extract lists
        lists = []
        for ul in soup.find_all(['ul', 'ol']):
            items = []
            for li in ul.find_all('li', recursive=False):
                li_text = li.get_text(strip=True)
                li_link = None
                a_tag = li.find('a')
                if a_tag and a_tag.get('href'):
                    li_link = urljoin(url, a_tag['href'])
                if li_text:
                    items.append({
                        'text': li_text,
                        'link': li_link
                    })
            if items:
                lists.append(items)

        # Extract blockquotes
        quotes = []
        for bq in soup.find_all('blockquote'):
            text = bq.get_text(strip=True)
            if text:
                quotes.append(text)

        # --- Images ---
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                full_src = urljoin(url, src)
                # Download image
                local_name = self.download_image(src, url)
                images.append({
                    'src': full_src,
                    'alt': alt,
                    'local_file': local_name,
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                })

        # --- Internal Links ---
        internal_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_href = urljoin(url, href)
            text = a.get_text(strip=True)
            parsed = urlparse(full_href)
            if parsed.netloc.lower() in self.allowed_domains:
                internal_links.append({
                    'text': text,
                    'url': full_href,
                })

        # --- Navigation Links ---
        nav_links = []
        nav = soup.find('nav') or soup.find('ul', class_=re.compile('nav|menu', re.I))
        if nav:
            for a in nav.find_all('a', href=True):
                nav_links.append({
                    'text': a.get_text(strip=True),
                    'url': urljoin(url, a['href'])
                })

        # --- Tables (often used for content in old sites) ---
        tables = []
        for table in soup.find_all('table'):
            rows = []
            for tr in table.find_all('tr'):
                cells = []
                for td in tr.find_all(['td', 'th']):
                    cell_text = td.get_text(strip=True)
                    cell_html = str(td)
                    cells.append({
                        'text': cell_text,
                        'has_image': bool(td.find('img')),
                        'has_link': bool(td.find('a')),
                    })
                if cells:
                    rows.append(cells)
            if rows:
                tables.append(rows)

        # --- Raw body text (fallback) ---
        body = soup.find('body')
        body_text = body.get_text(separator='\n', strip=True) if body else ""

        # --- Determine page category ---
        parsed_url = urlparse(url)
        path_parts = [p for p in parsed_url.path.split('/') if p]
        category = path_parts[0] if path_parts else "home"

        return {
            'url': url,
            'title': title,
            'meta_description': meta_desc,
            'category': category,
            'headings': headings,
            'paragraphs': paragraphs,
            'lists': lists,
            'quotes': quotes,
            'images': images,
            'internal_links': internal_links,
            'nav_links': nav_links,
            'tables': tables,
            'body_text': body_text[:5000],  # First 5000 chars of body
            'scraped_at': datetime.now().isoformat(),
        }

    def discover_links(self, html, base_url):
        """Find all internal links on a page"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()

        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            normalized = self.normalize_url(full_url)

            if self.is_valid_url(normalized) and normalized not in self.visited:
                links.add(normalized)

        return links

    def crawl(self, start_urls, max_pages=300):
        """BFS crawl starting from given URLs"""
        queue = deque()
        for url in start_urls:
            normalized = self.normalize_url(url)
            queue.append(normalized)

        total_scraped = 0
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"  JOYFUL HEART CONTENT SCRAPER")
        print(f"  Starting crawl of {len(start_urls)} seed URL(s)")
        print(f"  Max pages: {max_pages}")
        print(f"  Output: {os.path.abspath(self.output_dir)}")
        print(f"{'='*70}\n")

        while queue and total_scraped < max_pages:
            url = queue.popleft()

            if url in self.visited:
                continue

            self.visited.add(url)
            total_scraped += 1

            elapsed = time.time() - start_time
            print(f"  [{total_scraped:3d}/{max_pages}] ({elapsed:.0f}s) Scraping: {url[:80]}...", end=" ")

            html, final_url = self.fetch_page(url)
            if html is None:
                print("[FAIL]")
                self.failed.append(url)
                continue

            # Extract content
            page_data = self.extract_content(html, final_url or url)
            self.all_pages.append(page_data)

            # Save individual page JSON
            safe_filename = self._url_to_filename(url)
            page_path = os.path.join(self.pages_dir, f"{safe_filename}.json")
            with open(page_path, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)

            # Add to sitemap
            self.sitemap[url] = {
                'title': page_data['title'],
                'category': page_data['category'],
                'heading_count': len(page_data['headings']),
                'paragraph_count': len(page_data['paragraphs']),
                'image_count': len(page_data['images']),
                'internal_link_count': len(page_data['internal_links']),
            }

            print(f"[OK] h:{len(page_data['headings'])} p:{len(page_data['paragraphs'])} img:{len(page_data['images'])}")

            # Discover new links
            new_links = self.discover_links(html, final_url or url)
            for link in new_links:
                if link not in self.visited:
                    queue.append(link)

            # Polite delay
            time.sleep(0.3)

        total_time = time.time() - start_time

        # Save master files
        self._save_master_files(total_time)

        print(f"\n{'='*70}")
        print(f"  CRAWL COMPLETE")
        print(f"  Pages scraped: {total_scraped}")
        print(f"  Pages failed:  {len(self.failed)}")
        print(f"  Images saved:  {len(self.downloaded_images)}")
        print(f"  Total time:    {total_time:.1f}s")
        print(f"  Output dir:    {os.path.abspath(self.output_dir)}")
        print(f"{'='*70}\n")

        return self.all_pages

    def _url_to_filename(self, url):
        """Convert URL to a safe filename"""
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        if not path:
            path = "index"
        # Replace slashes and special chars
        safe = re.sub(r'[^a-zA-Z0-9-]', '_', path)
        # Add domain prefix for jesuswalk pages
        if 'jesuswalk' in parsed.netloc:
            safe = 'jw_' + safe
        return safe[:100]  # Limit filename length

    def _save_master_files(self, total_time):
        """Save sitemap and summary files"""
        # Sitemap JSON
        sitemap_path = os.path.join(self.output_dir, "sitemap.json")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            json.dump(self.sitemap, f, indent=2, ensure_ascii=False)

        # All pages combined JSON
        all_pages_path = os.path.join(self.output_dir, "all_pages.json")
        with open(all_pages_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_pages, f, indent=2, ensure_ascii=False)

        # Failed URLs
        if self.failed:
            failed_path = os.path.join(self.output_dir, "failed_urls.json")
            with open(failed_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed, f, indent=2)

        # Summary report
        summary = {
            'scrape_date': datetime.now().isoformat(),
            'total_pages': len(self.all_pages),
            'total_failed': len(self.failed),
            'total_images': len(self.downloaded_images),
            'total_time_seconds': round(total_time, 1),
            'domains_crawled': list(set(
                urlparse(p['url']).netloc for p in self.all_pages
            )),
            'categories': {},
        }

        # Count by category
        for page in self.all_pages:
            cat = page['category']
            summary['categories'][cat] = summary['categories'].get(cat, 0) + 1

        summary_path = os.path.join(self.output_dir, "scrape_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n  Saved: sitemap.json, all_pages.json, scrape_summary.json")


if __name__ == "__main__":
    scraper = JoyfulHeartScraper(
        output_dir=os.path.join(os.path.dirname(__file__), "..", "scraped_data")
    )

    # Seed URLs — start from both homepages
    seed_urls = [
        "https://www.joyfulheart.com/",
        "https://www.joyfulheart.com/menu/",
        "https://www.joyfulheart.com/about/",
        "https://www.joyfulheart.com/contact/",
        "https://www.joyfulheart.com/giving/",
        "https://www.joyfulheart.com/newsletter/",
        "https://www.joyfulheart.com/faq/",
        "https://www.joyfulheart.com/jesus/",
        "https://www.joyfulheart.com/maturity/",
        "https://www.joyfulheart.com/encourag/",
        "https://www.joyfulheart.com/evang/",
        "https://www.joyfulheart.com/church/",
        "https://www.joyfulheart.com/communion/",
        "https://www.joyfulheart.com/prayer/",
        "https://www.joyfulheart.com/scholar/",
        "https://www.joyfulheart.com/christmas/",
        "https://www.joyfulheart.com/easter/",
        "https://www.joyfulheart.com/thanksgiving/",
        "https://www.joyfulheart.com/pentecost/",
        "https://www.joyfulheart.com/stpatrick/",
        "https://www.joyfulheart.com/art/",
        "https://www.joyfulheart.com/misc/",
        "https://www.jesuswalk.com/",
        "https://www.jesuswalk.com/books/",
        "https://www.jesuswalk.com/podcast/",
    ]

    # Crawl with a reasonable limit
    scraper.crawl(seed_urls, max_pages=250)
