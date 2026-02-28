---
description: Fully automated website redesign from any URL — parallel agent system
---

# Website Redesign Workflow

> Give this workflow a URL, and it redesigns the entire website automatically.
> Uses 6 sub-agents running in parallel where possible.

## Input
User provides: A website URL to redesign

---

## Phase 1: SCOUT (solo)
// turbo

1. Use `read_url_content` to fetch the homepage HTML
2. Use `browser_subagent` to browse the site — take screenshots of: homepage, navigation menu, about page, a sample inner page
3. Extract from page DOM: navigation links, footer links, estimated page count
4. Identify companion/sister sites linked in footer or nav
5. Determine the site's purpose and industry
6. Generate `analysis.json` with this schema:
   ```json
   {
     "url": "<target URL>",
     "purpose": "<1-sentence description>",
     "organization": "<name>",
     "industry": "<education|ministry|ecommerce|portfolio|saas|etc>",
     "page_types": ["homepage", "article", "about", ...],
     "total_estimated_pages": 0,
     "navigation_structure": ["Home", "About", ...],
     "linked_sites": [],
     "key_people": [],
     "design_keywords": "<3-5 adjectives>",
     "has_blog": false,
     "has_ecommerce": false,
     "color_mood": "<warm|cool|neutral|vibrant>"
   }
   ```
7. **MCP optional**: Use Google AI Studio `generate_content` to analyze the homepage HTML for deeper purpose/audience/tone insight
8. **GATE 1**: Validate `analysis.json` has all fields populated, purpose is a real sentence, page_types has 3+ entries. If fail → re-run with deeper browsing.

---

## Phase 2: SCRAPER + DESIGNER (parallel)
// turbo
// turbo-all

> Run 2A and 2B **at the SAME TIME** — they have NO dependency on each other

### 2A: SCRAPER (runs in parallel with 2B)

9. Create project directory: `<project-name>-redesign/` inside the workspace
10. Copy the scraper engine template:
    ```
    cp "c:\Users\ADMIN\Desktop\J_project\Automated website develop\joyful-heart-redesign\scraper\content_scraper.py" <project>/scraper/
    ```
11. Update the scraper config:
    - `start_urls` = [target URL + any companion sites from SCOUT]
    - `max_pages` = SCOUT's `total_estimated_pages` (cap at 300)
    - `allowed_domains` = [target domain]
// turbo
12. Run the scraper:
    ```
    python <project>/scraper/content_scraper.py
    ```
13. Count output: JSON files in `scraped_data/pages/`, images in `scraped_data/images/`
14. **Fallback** if scraper fails (403/blocked):
    - Try Apify MCP with `maxCrawlPages: 3` for sitemap only
    - Then use `read_url_content` on individual pages
    - Parse manually with BeautifulSoup

### 2B: DESIGNER (runs in parallel with 2A)

15. Read the UI/UX Pro Max Skill:
    ```
    view_file c:\Users\ADMIN\.agents\skills\ui-ux-pro-max-skill\SKILL.md
    ```
// turbo
16. Run design system search:
    ```
    python c:\Users\ADMIN\.agents\skills\ui-ux-pro-max-skill\src\ui-ux-pro-max\scripts\search.py "<industry> <design_keywords>" --design-system -p "<Project Name>"
    ```
17. **MCP optional**: Use Stitch MCP `get_screen_code` to extract Design DNA from similar projects
18. Generate `index.css` with complete design system:
    - CSS custom properties (colors, fonts, spacing)
    - Typography system (Google Fonts)
    - Layout system (.container, grids, .section)
    - Component styles (.btn, .card, .hero, .navbar, .footer)
    - Animation system (@keyframes, .animate-in)
    - Responsive breakpoints (375px, 768px, 1024px, 1440px)
    - Smooth scroll, hover states, transitions

### GATE 2: Wait for BOTH to finish

19. Validate SCRAPER: JSON count >= 80% of SCOUT estimate, each JSON has title + paragraphs
20. Validate DESIGNER: CSS defines `--color-primary`, `--color-secondary`, `--bg-surface`, `--font-heading`, `--font-body`
21. If SCRAPER fails → re-run with added URLs (DESIGNER result preserved)
22. If DESIGNER fails → re-run search with adjusted keywords (scraper result preserved)
23. Only proceed when BOTH pass

---

## Phase 3: BUILDER (solo — needs both scraper data + CSS)
// turbo

24. Adapt `page_generator.py` for this site's structure:
    - Copy template from: `c:\Users\ADMIN\Desktop\J_project\Automated website develop\joyful-heart-redesign\scraper\page_generator.py`
    - Update nav links from SCOUT's `navigation_structure`
    - Update footer with SCOUT's `organization` name
    - Update brand name and tagline
    - Configure page types from SCOUT's `page_types`
25. **Image handling** (follow priority chain):
    - PRIORITY 1: Use scraped images from `scraped_data/images/`
    - PRIORITY 2: Use `generate_image` tool to create missing hero backgrounds, illustrations, placeholders
    - PRIORITY 3: Use CSS gradients/patterns as fallback
26. **MCP optional**: Use Stitch MCP `build_site` for production HTML on complex pages
27. **MCP optional**: Use Google AI Studio `generate_content` to rewrite poorly-written copy
// turbo
28. Run the generator: `python <project>/scraper/page_generator.py`
29. Start local server: `python -m http.server 8080 --directory <project>`
30. **GATE 3**: Use `browser_subagent` to verify: homepage renders, nav works, images load. If fail → fix generator and re-run.

---

## Phase 4: POLISHER + LINKER (parallel)
// turbo
// turbo-all

> Run 4A and 4B **at the SAME TIME** — they operate on different concerns

### 4A: POLISHER (runs in parallel with 4B)

31. Create and run a text quality Python script that:
    - Finds `<h3>` tags with double spaces → fix
    - Finds `<p>` tags with broken parentheses → fix
    - Removes ".Spanish version." and similar artifacts
    - Fixes HTML entities: `&#x27;` → `'`
    - Collapses double spaces everywhere
    - Truncates titles longer than 60 characters
// turbo
32. Take responsive screenshots at 1920px, 768px, 375px using `browser_subagent`
33. **MCP optional**: Use Google AI Studio `generate_content` to improve meta descriptions and alt text

### 4B: LINKER (runs in parallel with 4A)

34. Build URL map: scan all scraped JSONs for original URLs, map to generated HTML filenames
35. Patch all internal links in all HTML files:
    - External `href` → local relative path
    - Remove `target="_blank"` for local links
    - Update CTA labels ("Visit External" → "Explore →")
36. If site has 10+ items in any category, add:
    - Sticky section jump bar with pills
    - Live search/filter input
    - Section anchor IDs with scroll-offset

### GATE 4: Wait for BOTH to finish

37. Validate: zero double-spaces, zero broken parens, zero missed external links
38. If POLISHER fails → run fix script, re-verify (LINKER result preserved)
39. If LINKER fails → add missing URL entries, re-patch (POLISHER result preserved)
40. Only deliver to user when BOTH pass

---

## Delivery

41. Create a walkthrough document summarizing what was built
42. Notify the user with screenshots and the local server URL
