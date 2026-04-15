# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-26)

**Core value:** Judges can see the full pipeline live: scraper discovers real events → SQLite catalogs them → AI scores ROI → coordinator triggers outreach — all in one demo session.
**Current focus:** React + FastAPI judge demo (portals + `demo.db` narrative) is packaged; `.planning/ROADMAP.md` “Demo Polish” phases remain the longer-term Streamlit/SQLite expansion backlog unless reprioritized.

## Current Status

**Milestone:** Demo Polish (roadmap) + **v3 portals / demo narrative shipped** (2026-04-14)
**Branch:** feature/cat3-demo-polish (typical); confirm active branch locally before commits
**Active phase (roadmap):** Phase 1 — SQLite Foundation (still pending as *Streamlit* `smartmatch.db` scope in ROADMAP)
**Parallel shipped path:** `data/demo.db` + FastAPI portal routers + Vite portals — see `docs/demo-narrative-2026-04-14.md`
**Roadmap phases complete:** 0 / 6 (unchanged — refers to ROADMAP.md phase list, not the April portal drop)

## Phase Status

| Phase | Name | Status |
|-------|------|--------|
| 1 | SQLite Foundation | ○ Pending (per ROADMAP; separate from April `demo.db` seed) |
| 2 | SoCal University Expansion | ○ Pending |
| 3 | Live Scraper Agent Tab | ○ Pending |
| 4 | ROI Scoring Factor | ○ Pending |
| 5 | Floating Jarvis Button | ○ Pending |
| 6 | Calendar Fix | ○ Pending |

## Session Log

- **2026-04-14**: Student + event coordinator portals, extended `scripts/seed_demo_db.py`, `src/api/routers/portals.py`, QR attendance API, agentic outreach SSE UI, landing/login CTAs and URL-param login pre-selection, UI token + accessibility pass. Verification and 6-scene narrative: `docs/demo-narrative-2026-04-14.md`. Memory: `.memory/context/2026-04-14-cat3-portals-demo-narrative.md`.
- **2026-03-26**: Project initialized from pre-designed 6-phase plan. GSD planning infrastructure created on branch `feature/cat3-demo-polish`.

## Notes

- All work happens inside `Category 3 - IA West Smart Match CRM/` subdirectory
- Phase 1 is prerequisite for Phase 3 (scraper tab writes to DB)
- Phase 2 is prerequisite for Phase 3 (scraper targets must exist before UI triggers them)
- Phases 4, 5, 6 are independent of each other
- The **April 2026** portal work uses **`data/demo.db`** and the **fullstack** app (`:5173` + `:8000`); it does not by itself satisfy ROADMAP “Phase 1” until the Streamlit/CSV `smartmatch.db` path is implemented as specified there
