# Roadmap: IA West Smart Match CRM — Demo Polish Milestone

**Milestone:** Demo Polish
**Goal:** Surface the hidden backend infrastructure (scraper, DB, ROI scoring, Jarvis) as demo-visible features before hackathon judging.
**Branch:** `feature/cat3-demo-polish`

---

## Phase 1 — SQLite Foundation

**Goal:** Create `smartmatch.db` seeded from existing CSVs; give the app a "real database" story.

**Requirements:** DB-01, DB-02, DB-03, DB-04

**Files:**
- `src/db.py` (new) — sqlite3 connection, table creation, seed from CSVs, CRUD helpers
- `src/data_loader.py` — add `load_from_db()` path alongside existing CSV path

**Success criteria:**
- `smartmatch.db` is created on first `streamlit run app.py`
- All 5 CSV files are seeded into corresponding tables
- `scraped_opportunities` table accepts inserts from scraper
- Existing app functionality unchanged (CSV fallback intact)

---

## Phase 2 — SoCal University Expansion

**Goal:** Add 12 missing UC/CSU SoCal schools to scraper targets.

**Requirements:** SCRP-01, SCRP-02, SCRP-03

**Files:**
- `src/config.py` — add 12 schools to `UNIVERSITY_TARGETS`, coordinates to `UNIVERSITY_COORDINATES`
- `src/scraping/scraper.py` — verify new targets work with existing scraper loop

**New schools:** UC San Diego, UC Irvine, UC Riverside, UC Santa Barbara, Cal Poly Pomona, Cal State LA, Cal State Fullerton, Cal State Long Beach, Cal State Northridge, Cal State Dominguez Hills, Cal State San Bernardino, Cal State San Marcos

**Success criteria:**
- `UNIVERSITY_TARGETS` has 17 total entries (5 existing + 12 new)
- All new entries have method, region, and coordinates
- Existing schools still present and unmodified

---

## Phase 3 — Live Scraper Agent Tab

**Goal:** Demo-visible UI that shows scraping in real time and catalogs events to SQLite.

**Requirements:** UI-01 through UI-07

**Files:**
- `src/ui/live_scraper_tab.py` (new) — full tab UI with agent feed, opportunities table, DB status
- `src/api/routers/scraper.py` (new) — FastAPI router: POST /api/scraper/run, GET /api/scraper/opportunities
- `src/api/main.py` — register scraper router
- `src/app.py` — add "Live Discovery Agent" to `WORKSPACE_NAV_ITEMS`
- `src/ui/page_router.py` — add `"live_scraper"` to `PAGES` dict

**UI sections:**
1. Control bar: [▶ Run Full Scrape] [▶ SoCal Only] Status indicator
2. Agent feed log (scrolling, st.empty() container, append-style)
3. Discovered opportunities table (live-updating dataframe)
4. Database status footer (total cataloged + new this session)

**Success criteria:**
- Tab appears in coordinator nav
- Clicking "Run SoCal Scrape" starts scrape loop, feed updates per school
- Events appear in discovered table and in `smartmatch.db`
- "Add to Pool" populates `session_state["matching_discovered_events"]`

---

## Phase 4 — ROI Scoring Factor

**Goal:** Add `roi_potential` composite score to matching engine; surface it in UI.

**Requirements:** ROI-01 through ROI-06

**Files:**
- `src/matching/factors.py` — implement `roi_potential()`, stub `event_urgency()` and `coverage_diversity()`
- `src/config.py` — add `CATEGORY_REACH_WEIGHTS` dict
- `src/matching/engine.py` — wire `roi_potential` into score calculation
- `src/ui/matches_tab.py` — add ROI badge to match cards
- (pipeline tab file) — add sortable ROI column

**ROI formula:**
```
roi_potential = (
    0.35 × student_interest_score
  + 0.30 × event_reach_score          # from CATEGORY_REACH_WEIGHTS
  + 0.20 × historical_conversion_score
  + 0.15 × role_fit_score
)
```

**CATEGORY_REACH_WEIGHTS:**
- Career Fair: 0.95, Hackathon: 0.90, Case Competition: 0.80
- Networking: 0.70, Symposium: 0.75, Guest Lecture: 0.60, Workshop: 0.55

**Success criteria:**
- ROI score appears on match cards (0.0–1.0 scale, labeled "Est. ROI")
- Pipeline tab has ROI column, sortable
- `event_urgency` and `coverage_diversity` no longer return unimplemented errors

---

## Phase 5 — Floating Jarvis Button

**Goal:** Move Jarvis from buried sidebar checkbox to persistent FAB on all pages.

**Requirements:** JAR-01 through JAR-06

**Files:**
- `src/ui/styles.py` — add CSS for position:fixed FAB (bottom-right)
- `src/app.py` — render FAB + Jarvis panel on all authenticated pages; remove old checkbox
- `src/ui/command_center.py` — adapt render to work as overlay panel
- `src/coordinator/nemoclaw_adapter.py` — activate when `USE_NEMOCLAW=1`

**CSS approach:**
```css
.jarvis-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}
```

**Success criteria:**
- 🤖 button visible on coordinator dashboard, matches page, pipeline tab, live scraper tab
- Clicking opens/closes Jarvis panel without page navigation
- Panel has text input + push-to-talk + chat history
- Old "Show Jarvis Command Center" checkbox is gone
- `USE_NEMOCLAW=1 streamlit run app.py` activates parallel dispatch

---

## Phase 6 — Calendar Fix

**Goal:** Fix Vite proxy dependency so React calendar works in demo environment.

**Requirements:** CAL-01, CAL-02, CAL-03

**Files:**
- `frontend/src/lib/api.ts` — add `VITE_API_BASE_URL` env var with `http://localhost:8000` fallback
- `frontend/.env` — set `VITE_API_BASE_URL=http://localhost:8000`
- `frontend/.gitignore` — ensure `.env` is not committed (or commit intentionally for demo)

**Change in api.ts:**
```typescript
const API_BASE = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000';
// use API_BASE + path in requestJson()
```

**Success criteria:**
- React frontend at `:5173` shows calendar events without CORS error
- Works when Vite dev server started independently from FastAPI
- No hardcoded localhost references remain in api.ts

---

## Milestone Success Criteria

1. Boot app → Live Scraper tab shows agent feed for 12+ SoCal schools, events appear in smartmatch.db
2. Matches page → ROI badge visible on all match cards, pipeline tab has sortable ROI column
3. Any authenticated page → 🤖 FAB visible, clicking opens Jarvis voice+chat panel
4. React calendar at :5173 → events load without error

---
*Roadmap created: 2026-03-26*
*Branch: feature/cat3-demo-polish*
