# Phase 17: Persistent Database Layer + Web Crawler Live Feed - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning
**Source:** PRD Express Path (user-provided specification in /gsd:plan-phase arguments)

<domain>
## Phase Boundary

This phase delivers two tightly coupled capabilities:

1. **3-Layer Database Architecture** — A persistent `data/smartmatch.db` SQLite database becomes the primary data source (Layer 0), replacing the current 2-layer CSV-first fallback. The existing demo.db moves to Layer 1, and CSVs become Layer 2 (emergency last resort). All IA West CSV datasets are seeded into both Layer 0 and Layer 1 at startup. Every API endpoint returns a `source` tag (`live`, `demo`, `csv`) so the coordinator always knows which layer served the data.

2. **Web Crawler Live Feed** — A Gemini/Tavily-powered web crawler discovers directed school pages from IA West's network. A `/api/crawler/feed` SSE endpoint streams activity in real time. The coordinator dashboard shows a live scrolling panel (site name, crawl status, timestamp) matching the ChatGPT deep-research UX pattern. The coordinator can trigger a new crawl from the UI.

</domain>

<decisions>
## Implementation Decisions

### Layer 0: Persistent SQLite (`data/smartmatch.db`)
- File path: `data/smartmatch.db` (same directory as demo.db)
- Created on first run by a seed script `scripts/seed_smartmatch_db.py`
- Imports ALL IA West CSV datasets on first run:
  - `data/data_speaker_profiles.csv` → `specialists` table
  - `data/data_cpp_events_contacts.csv` → `cpp_events` table
  - `data/data_cpp_course_schedule.csv` → `cpp_courses` table
  - `data/data_event_calendar.csv` → `calendar_events` table
  - `data/pipeline_sample_data.csv` → `pipeline` table
  - `data/poc_contacts.json` → `poc_contacts` table
- Also has a `web_crawler_events` table for real-time web crawl results
- If `smartmatch.db` exists and has rows → return with `"source": "live"`
- If `smartmatch.db` missing/empty → fall through to Layer 1

### Layer 1: Demo SQLite (`data/demo.db`)
- Same as current demo.db, but renamed to Layer 1 (was previously called Layer 2)
- Should also have IA West datasets pre-seeded (same as Layer 0)
- Update `scripts/seed_demo_db.py` to import CSV data alongside Python constants
- If `demo.db` has rows → return with `"source": "demo"`
- If `demo.db` missing/empty → fall through to Layer 2

### Layer 2: CSV Files (Last Resort)
- The current CSV-first approach becomes last-resort fallback
- Same loader functions in `src/ui/data_helpers.py`
- Returns with `"source": "csv"`

### API Integration
- All existing routers in `src/api/routers/` must be updated to try Layer 0 first
- New helper module: `src/api/smartmatch_db.py` (mirrors `demo_db.py` pattern)
- `_load_rows_with_fallback()` pattern extends to 3 layers: `load_from_smartmatch` → `load_from_demo` → `load_from_csv`
- Every API response that returns list data must include a `source` field

### Web Crawler: Gemini + Tavily
- Primary crawler: Google Gemini API (using `google-generativeai` SDK)
- Secondary/parallel crawler: Tavily search API (`tavily-python` SDK)
- Crawler target: IA West directed school pages (CPP, Cal Poly, UC campuses, directed schools in data)
- Crawl stores results in `smartmatch.db` → `web_crawler_events` table:
  - `id`, `url`, `title`, `description`, `school_name`, `crawled_at`, `source` (gemini|tavily), `status`
- New router: `src/api/routers/crawler.py`
- Endpoints:
  - `POST /api/crawler/start` — Trigger a new crawl (background task)
  - `GET /api/crawler/feed` — SSE stream of real-time crawler activity
  - `GET /api/crawler/results` — Return stored crawl results from smartmatch.db

### SSE Live Feed
- Use FastAPI's `StreamingResponse` with `text/event-stream` media type
- SSE events: `{ "url": "...", "title": "...", "status": "crawling|found|error", "timestamp": "..." }`
- Frontend connects with `EventSource` API
- Feed panel stays open until crawl finishes (server closes SSE stream)

### Frontend Crawler UI
- Location: Coordinator dashboard (existing page in `frontend/src/`)
- New component: `CrawlerFeed` panel — right-side panel or bottom drawer
- Displays live scrolling list: site URL, title snippet, status icon (⟳ crawling, ✓ found, ✗ error)
- "Start Crawl" button triggers `POST /api/crawler/start`
- Animation: entries slide in from bottom as they arrive (similar to ChatGPT deep research)
- When crawl finishes, panel shows "Found {N} directed school pages — results saved"

### Claude's Discretion
- Exact CSS/animation implementation for the live feed panel
- Whether to use polling as fallback if SSE not supported
- Rate limiting strategy for crawler (avoid hammering target sites)
- Whether to deduplicate crawl results by URL before storing

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/api/demo_db.py` — Pattern to replicate for `smartmatch_db.py` (exact same interface)
- `src/ui/data_helpers.py` — LRU-cached CSV loaders (become Layer 2 in new architecture)
- `scripts/seed_demo_db.py` — Seed script pattern to replicate for `seed_smartmatch_db.py`
- `src/api/routers/data.py` — All data endpoints (require Layer 0 integration)
- `frontend/src/lib/api.ts` — Frontend API client (needs crawler endpoints added)
- `frontend/src/components/ui/` — shadcn/ui components available for crawler panel

### Established Patterns
- 2-layer fallback: `load_X()` (CSV) → `load_demo_X()` (demo.db) — extend to 3 layers
- `source` tag in API responses already used (`"source": "live"` vs `"source": "demo"`)
- `DemoModeBadge` component in React already knows how to read `source` field
- FastAPI background tasks via `BackgroundTasks` (already used in outreach workflow)

### Integration Points
- `src/api/main.py` — Router registration (add crawler router)
- `src/api/routers/data.py` — All data endpoints update Layer 0 priority
- `frontend/src/pages/` — Coordinator dashboard page (add CrawlerFeed panel)
- `data/` directory — new `smartmatch.db` file created here

### Existing Data Files (IA West datasets to import)
- `data/data_speaker_profiles.csv` — 10+ specialist records
- `data/data_cpp_events_contacts.csv` — CPP event contacts
- `data/data_cpp_course_schedule.csv` — CPP course schedule
- `data/data_event_calendar.csv` — IA event calendar
- `data/pipeline_sample_data.csv` — funnel records
- `data/poc_contacts.json` — point-of-contact records

</code_context>

<specifics>
## Specific Ideas

- **UX reference:** ChatGPT deep research live crawl panel — entries appear in real time as each URL is visited, with animated status indicators
- **Layer naming in UI:** The DemoModeBadge should reflect the new naming: `live` = Layer 0 (smartmatch.db), `demo` = Layer 1 (demo.db), `csv` = Layer 2 (last resort)
- **Directed schools targeting:** Crawl should start from IA West's network — CPP-affiliated schools, UC system directed programs. Seed URLs can be derived from existing event data in CSV files.
- **Tavily as secondary:** If Gemini API key is unavailable, Tavily is the fallback for web search. Both can run in parallel for richer results.
- **Environment variables:** `GEMINI_API_KEY` and `TAVILY_API_KEY` — both optional (graceful degradation if missing)

</specifics>

<deferred>
## Deferred Ideas

- **Full OAuth Gmail integration** — already in backlog, not this phase
- **Cloud database** — hackathon scope stays with SQLite
- **Crawler scheduling** — cron/scheduled crawls are post-hackathon
- **Crawler deduplication UI** — show merged results, not this phase

</deferred>

---

*Phase: 17-persistent-database-layer-web-crawler-live-feed*
*Context gathered: 2026-03-27 via PRD Express Path (user arguments)*
