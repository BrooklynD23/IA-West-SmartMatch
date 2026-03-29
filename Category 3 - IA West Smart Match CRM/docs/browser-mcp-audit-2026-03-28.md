# Browser MCP audit — IA West Smart Match CRM

**Date:** 2026-03-28  
**Scope:** End-to-end smoke and interaction pass using the Cursor IDE Browser MCP (`cursor-ide-browser`) against the Category 3 full stack.  
**Audience:** Follow-up audit or QA agents (replay steps, expand coverage, or file defects).

## Environment under test

| Component | URL / command | Notes |
|-----------|---------------|--------|
| Vite dev server | `http://localhost:5173/` | `npm run dev` from `frontend/` (port 5173, proxy `/api` → 8000) |
| FastAPI backend | `http://127.0.0.1:8000` | `python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000` from CRM repo root |
| Health | `GET /api/health` | Returned `{"status":"ok"}` (HTTP 200) |

**Windows note:** `python scripts/start_fullstack.py` exited with a `charmap` codec error when printing Unicode status icons. For this session, backend and frontend were started manually (commands above). An audit agent should either fix console encoding for that script or document the same manual startup.

## Authentication and routing

- **Public routes:** `/`, `/login`
- **Coordinator shell (sidebar layout):** `/dashboard`, `/opportunities`, `/volunteers`, `/ai-matching`, `/pipeline`, `/calendar`, `/outreach`
- **Auth model:** There is **no server-side session gate** on coordinator routes. Navigating directly to `/dashboard` loads the app without visiting `/login` (expected for the current demo).
- **Login:** `/login` accepts any email/password; submit navigates to `/dashboard`. **Sign In with LinkedIn** is **disabled** in the accessibility tree (placeholder integration).

## API sanity (non-browser)

Verified outside the browser (same machine as dev servers):

- `GET http://127.0.0.1:8000/api/health` → 200
- `GET http://127.0.0.1:5173/api/data/events` (via Vite proxy) → 200, JSON array of CPP events with `source: "live"` (15 rows in this environment)

**Note:** `GET /api/data/opportunities` is **not** a registered route (404). The Opportunities UI uses **`/api/data/events`**.

## MCP test matrix (results)

| Area | Check | Result |
|------|--------|--------|
| Landing | `/` loads marketing content; multiple **Sign In** links present | Pass |
| Login | Fill email/password → **Sign In as Coordinator** → `/dashboard` | Pass |
| Dashboard | KPI copy (e.g. **Active Opportunities** count **15**), charts/sections, **discovery feed** | Pass |
| Dashboard | **Start Crawl** → button becomes **Crawling...** (disabled) while work runs | Pass |
| Opportunities | After async load: **Showing 15 of 15 opportunities**; filter controls populated; **Match Volunteers** per card | Pass |
| Opportunities → AI Matching | **Match Volunteers** → `/ai-matching`; **AI Matching Engine** heading present | Pass |
| Volunteers | **Volunteer Profiles**; roster text (e.g. **Rob Kaiser**) after load | Pass |
| AI Matching | Event combobox, feedback metrics, **Top Recommended Volunteers** section | Pass |
| Pipeline | **Pipeline Tracking** heading; host filter combobox | Pass |
| Calendar | **Coordinator scheduling view**; coverage metrics; month grid day buttons **1–31**; **Month/Week/Day**, **Today**, filter toggles | Pass |
| Outreach | Templates, **Save Draft** enables recipient/event comboboxes and contextual copy (**Event host**, **Audience**); **AI Generate Email**, QR, ICS actions move out of disabled state as appropriate | Pass |
| Outreach | **Start Crawl** present (crawler feed section) | Pass |
| Deep link | `/dashboard` without prior login | Pass (no redirect to `/login`) |

## Console and network (MCP observations)

- **Console:** No application errors observed; expected dev noise only (Vite HMR, React DevTools suggestion, Cursor browser dialog override warning).
- **Network:** `GET /api/data/events` from the Opportunities page returned **HTTP 200** (seen in MCP network log).

## Automation lessons (critical for audit agents)

1. **Async UI:** Right after `browser_navigate`, accessibility snapshots can still show **pre-fetch** state (e.g. **Showing 0 of 0 opportunities**). Prefer `browser_wait_for` on stable copy (e.g. event title or section heading) or a short delay before asserting counts.
2. **SPA transitions:** Clicks that change the route may briefly leave the previous view in the snapshot until the next paint; wait for route-specific headings before scoring pass/fail.
3. **Viewport / sidebar:** In a short viewport, sidebar nav links sometimes required scroll-into-view for `browser_click`; **direct URL navigation** was reliable for route coverage.
4. **LinkedIn CTA:** Intentionally disabled; do not file as a regression without a spec change.

## Suggested follow-ups for a deeper audit

- Exercise **Feedback** flows on AI Matching (accept/decline) and confirm `/api/feedback` persistence.
- Generate QR / ICS on Outreach after **Save Draft** and verify downloads or preview.
- Run crawler to completion and assert **Web Crawler Feed** rows match `/api/crawler` responses.
- **Auth:** Decide whether unauthenticated access to `/dashboard` should be blocked before production.
- **Windows:** Fix `start_fullstack.py` status output encoding (`PYTHONUTF8` / console code page) so one-command startup works.

## Evidence summary

All checks above were executed with the Browser MCP against `http://localhost:5173` while the FastAPI backend on port **8000** was running. No blocking defects were found for the exercised paths; the main caveat is **timing-sensitive assertions** immediately after navigation.
