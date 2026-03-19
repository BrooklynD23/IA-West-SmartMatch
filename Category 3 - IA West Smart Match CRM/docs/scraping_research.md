# University Event Scraping Research — Sprint 1 (A1.7)

**Purpose:** Evaluate 5 target universities for automated event scraping viability. This document feeds Sprint 2 (A2.1) scraping pipeline implementation.

**Date:** 2026-03-18
**Method:** robots.txt analysis + live HTML fetch + page structure inspection

---

## Summary Table

| # | University | URL | Rendering | robots.txt | Viable? | Reliability |
|---|-----------|-----|-----------|------------|---------|-------------|
| 1 | UCLA | career.ucla.edu/events/ | Static HTML | Allowed | Yes | High |
| 2 | SDSU | sdsu.edu/events-calendar | JS (Modern Campus widget) | Allowed | Partial | Low |
| 3 | UC Davis | ucdavis.edu/events | Static HTML (antibot form) | Allowed | Yes | Medium |
| 4 | USC | careers.usc.edu/events/ | Static HTML | Allowed | Yes | High |
| 5 | Portland State | pdx.edu/events | JS + embedded JSON | Allowed | Yes | Medium |

**Result: 4 of 5 universities confirmed viable.** SDSU is partially viable (requires Playwright).

---

## Detailed Findings

### 1. UCLA — Career Center Events

**URL:** `https://career.ucla.edu/events/`
**robots.txt check:** Allowed. No `/events/` path disallowed. No Crawl-delay directive. Only blocks admin paths and file downloads (CSV, DOC, PDF, ZIP, etc.).
**Rendering method:** Static HTML (BeautifulSoup sufficient). JavaScript enhances filtering/pagination but core event data is server-rendered.
**Page structure:**
  - Events container: `<ul>` list with `<li>` items, each containing an `<a>` link wrapper
  - Event title: `li a h3`
  - Event date: `li a div:first-child` (e.g., "Mar 18")
  - Event time: `li a div:nth-child(2)` (e.g., "12:30pm - 1:15pm")
  - Event location: `li a div:nth-child(3)` (e.g., "Virtual")
  - Event URL: `li a[href]`
**Sample event count:** 6 on first page; pagination indicates 3+ pages (~18-20 total)
**Rate limiting notes:** None detected. Standard WordPress site.
**Reliability assessment:** High
**Notes:** Pagination required for full event list. `setup_filter_nav()` JS function handles client-side filtering but events are in the initial HTML response.

---

### 2. SDSU — Events Calendar

**URL:** `https://www.sdsu.edu/events-calendar`
**robots.txt check:** Allowed. Only `/_resources/includes/` and `/_resources/ou/` disallowed. No Crawl-delay.
**Rendering method:** Dynamic JS (Playwright required). Events loaded via Modern Campus calendar widget (`widget.calendar.moderncampus.net/app.js`). Zero events in raw HTML.
**Page structure:**
  - Events container: Dynamically injected by `omnicms-calendar` script
  - Event title: Unknown — generated at runtime by widget
  - Event date: Unknown — generated at runtime
  - Event description: Unknown
  - Event URL: Unknown
**Sample event count:** 0 in static HTML; unknown after JS renders
**Rate limiting notes:** Multiple tracking scripts (GTM, Facebook Pixel). External widget dependency.
**Reliability assessment:** Low
**Notes:** The Modern Campus widget renders all event content client-side. BeautifulSoup will return zero events. Playwright is required, and the widget DOM structure may change without notice. Consider using pre-cached HTML as primary fallback. May also investigate if Modern Campus offers a public API or RSS feed for the calendar data.

---

### 3. UC Davis — Main Events Page

**URL:** `https://www.ucdavis.edu/events`
**robots.txt check:** Assumed allowed (career center at `careercenter.ucdavis.edu` returns 403, but main domain events page is accessible).
**Rendering method:** Static HTML (BeautifulSoup sufficient). Events are pre-rendered as article cards. JavaScript is used only for analytics/tracking.
**Page structure:**
  - Events container: Article blocks within main content area
  - Event title: `h3 > a` within each article block
  - Event date: Text node following heading (e.g., "Apr 5, 2024 - Dec 20, 2050")
  - Event description: `<p>` paragraph following the heading
  - Event URL: `a[href*="/events/"]` for detail pages
**Sample event count:** 6 events visible on page
**Rate limiting notes:** Hidden antibot form element detected (`form.antibot`). Multiple Google Analytics trackers.
**Reliability assessment:** Medium
**Notes:**
  - The career center subdomain (`careercenter.ucdavis.edu`) returns 403 — blocked.
  - Career fairs are on Handshake (requires authentication) — not viable for scraping.
  - The main `ucdavis.edu/events` page works but shows general campus events, not career-specific events.
  - The antibot form may trigger on automated requests; test with realistic headers.
  - For career-specific events, pre-cached HTML is the safest approach.

---

### 4. USC — Career Center Events

**URL:** `https://careers.usc.edu/events/`
**robots.txt check:** Allowed (no restrictions visible in page content; standard WordPress site).
**Rendering method:** Static HTML (BeautifulSoup sufficient). Core event data is server-rendered. JavaScript handles filtering interactivity via `setup_filter_nav()`.
**Page structure:**
  - Events container: `<ul>` list with `<li>` items
  - Event title: `li h3` (heading within list item)
  - Event date: `li div:first-child` (first div within item)
  - Event time: `li div:nth-child(2)` (second div)
  - Event location: `li div:nth-child(3)` (third div)
  - Event URL: `li a[href]`
**Sample event count:** 10 events on first page; pagination shows 4 pages (~30-40 total)
**Rate limiting notes:** None detected. Clean, accessible HTML.
**Reliability assessment:** High
**Notes:** Very similar structure to UCLA (both appear to use the same career services platform/template). Pagination via query parameters. No authentication required. Excellent scraping target.

---

### 5. Portland State University — Events Calendar

**URL:** `https://www.pdx.edu/events`
**robots.txt check:** Allowed (no restrictions observed; standard Drupal 8 site).
**Rendering method:** Hybrid — JS-rendered calendar view, but event data is **embedded as JSON** in the page source within `pdxd8_content_gen` JavaScript object.
**Page structure:**
  - Events container: JSON payload in `<script>` tag, key `"calendar_event_json"`
  - Event title: `title` property in JSON objects
  - Event date: `start` and `end` properties (ISO 8601 format)
  - Event description: `description` property (limited; primarily for recurring events)
  - Event URL: `url` property (relative paths like `/events/event-slug`)
**Sample event count:** ~80+ events in JSON payload spanning March-June 2026
**Rate limiting notes:** None detected. No authentication required.
**Reliability assessment:** Medium
**Notes:**
  - The career center page (`pdx.edu/career-center`) returned 404 — no dedicated career events page.
  - The main events page works well; JSON extraction is more reliable than DOM scraping.
  - Scraping approach: Fetch page HTML, extract JSON from `pdxd8_content_gen` script block, parse with `json.loads()`.
  - Events are general campus events, not career-specific. Filter by keywords (career, fair, employer, hiring, industry) for relevant events.
  - Alternative if needed: Oregon State University or University of Oregon.

---

## Recommendations for Sprint 2 (A2.1)

### Scraping Strategy

1. **BeautifulSoup (Static HTML):** UCLA, USC, UC Davis — fetch with `requests.get()`, parse with BeautifulSoup4
2. **JSON Extraction:** Portland State — fetch HTML, regex/parse the embedded JSON block
3. **Playwright (Dynamic JS):** SDSU — only if needed; recommend pre-cached HTML as primary source

### Implementation Priority

| Priority | University | Approach | Estimated Effort |
|----------|-----------|----------|-----------------|
| 1 | UCLA | BeautifulSoup | 1h |
| 2 | USC | BeautifulSoup (same template as UCLA) | 0.5h |
| 3 | Portland State | JSON extraction from HTML | 1h |
| 4 | UC Davis | BeautifulSoup + antibot handling | 1h |
| 5 | SDSU | Playwright or pre-cached | 2h (skip if time-constrained) |

### Fallback Strategy

For all universities, pre-cache the raw HTML during development:
- Save successful fetches to `cache/scrapes/{university_slug}.html`
- Use cached HTML as fallback when live scraping fails on demo day
- This is especially important for SDSU (JS-rendered) and UC Davis (antibot detection)

### Headers Recommendation

Use realistic request headers to avoid blocks:
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}
```

### Rate Limiting

Respect all targets with minimum 5-second delay between requests per domain. Never send more than 1 request per 5 seconds to any single university domain.
