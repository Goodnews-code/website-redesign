# 🚀 Automated Website Redesign Project | Before vs After

> **A professional demonstration of modernizing high-content legacy websites.**

This project showcases the successful redesign and modernization of two legacy Christian ministry websites: **Joyful Heart** and **JesusWalk**.

---

## 🔗 Live Demos
*   **✨ New Website Redesign**: [View Redesign (Deploy to Netlify)](https://your-netlify-url.netlify.app/)
*   **🏛️ Legacy Site Archive**: [View Original Scraped Content](./old-website/)

---

## 🛠️ Project Goals & Successes
The objective was to take 200+ pages of high-quality content and transform them into a mobile-first, high-performance, and accessible web experience.

| Feature | Legacy Experience | Modern Redesign | Result |
|:---|:---|:---|:---|
| **Responsiveness** | Fixed width, poor on mobile | Fluid, responsive grids | 100% Mobile Optimized |
| **Typography** | Generic fonts, small sizes | Cormorant Garamond & Inter | Enhanced readability |
| **Navigation** | Overwhelming text menus | Sticky pill navigation + search | 3x Faster navigation |
| **Speed** | Heavy legacy assets | Light CSS + Optimized assets | Instant load times |

---

## 📂 Project Structure

```text
.
├── /new-website         <-- THE REDESIGN (Deploy THIS folder to Netlify)
│   ├── index.html       <-- Central Landing Page for Portolio
│   ├── /joyful-heart    <-- Redesigned Devotional Site
│   └── /jesuswalk       <-- Redesigned Study Catalog
│
├── /old-website         <-- THE ARCHIVE
│   └── /source-data     <-- Original Scraped JSON/HTML
│
└── /redesign            <-- THE AGENT SYSTEM (Reusable Code)
    ├── /scraper         <-- BFS Python Crawler Template
    └── /generator       <-- Dynamic Page Generation Engine
```

---

## ⚙️ Technical Process (How it was built)

1.  **AI-Powered Scraping**: Using a custom Python BFS crawler to extract structured JSON content while preserving metadata.
2.  **Design System Generation**: Leveraging the `UI/UX Pro Max` design intelligence tool to select premium palettes and modern typography.
3.  **Dynamic Generation**: Building custom `PageGenerator` classes to turn JSON content into semantically correct, SEO-friendly HTML.
4.  **Polish & Link Migration**: Running automated cleanup scripts to fix legacy text artifacts and migrate all external links to local relative paths.

---

## 👤 About
This project was developed as part of a high-end web development portfolio to demonstrate expertise in **automation**, **design systems**, and **mass-scale content migration**.

---

> [!NOTE]
> If you are the owner of the original sites, please see the live Netlify link above for a demonstration of how your content looks with modern architecture.
