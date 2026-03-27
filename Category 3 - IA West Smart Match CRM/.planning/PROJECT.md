# IA West Smart Match CRM

## What This Is

An AI-powered coordinator tool for IA West (Industry Advisors West) that matches board member volunteers to university speaking and event opportunities across SoCal. Built as a Streamlit + FastAPI + React app with a 9-factor scoring engine, web scraping pipeline, and a voice-enabled Jarvis command center. Demoed at a hackathon for Better Future 2026.

## Core Value

Judges can see the full pipeline live: scraper agent discovers real university events → SQLite catalogs them → AI scores volunteer-event ROI → coordinator triggers outreach — all in one demo session.

## Requirements

### Validated

- ✓ AI matching engine (9 scoring factors) — Phase 0 (existing)
- ✓ Volunteer profiles (5 IA West board members) — Phase 0 (existing)
- ✓ Event profiles (Cal Poly catalog) — Phase 0 (existing)
- ✓ Email generation for outreach — Phase 0 (existing)
- ✓ Pipeline tab visualization — Phase 0 (existing)
- ✓ KittenTTS + faster-whisper voice stack — Phase 0 (existing)
- ✓ NemoClaw parallel orchestration adapter — Phase 0 (existing, not activated)

### Active

- [ ] SQLite database seeded from CSVs (smartmatch.db)
- [ ] 12 additional SoCal UC/CSU schools in scraper targets
- [ ] Live Scraper Agent Tab with real-time agent feed UI
- [ ] ROI scoring factor (roi_potential composite score)
- [ ] Floating Jarvis FAB accessible on all authenticated pages
- [ ] Calendar fix (Vite proxy → VITE_API_BASE_URL env var)

### Out of Scope

- Multi-user auth / login system — hackathon demo, single-coordinator use
- Production deployment / cloud hosting — local demo only
- Real email delivery — outreach templates generated, not sent
- Mobile responsive design — demo on laptop only

## Context

**Iceberg problem:** Rich backend infrastructure (scraper, voice stack, NemoClaw, ROI factors in config) built but never wired into demo-visible UI. Judges see static CSVs while scraper + DB + ROI exist only as dead code.

**Tech stack:** Python 3.11+, Streamlit (primary UI), FastAPI (REST API for React calendar), React + Vite (calendar frontend), sqlite3 (built-in, zero new deps), BeautifulSoup4 + Playwright (scraping), Gemini API (LLM extraction), KittenTTS + faster-whisper (voice).

**Existing data:** All data in `data/` as CSVs. No DB exists. CSVs become seed source; DB becomes runtime truth.

**Scraper current state:** 5 universities (UCLA, SDSU, UC Davis, USC, Portland State). Only 3 are SoCal. 12 SoCal UC/CSU schools are missing.

**Two dead config factors:** `event_urgency` and `coverage_diversity` defined in config.py but never implemented in factors.py. Will be stubbed at 0.5.

**Calendar broken:** React calendar calls `/api/calendar/events` through Vite dev proxy. Proxy only works when Vite dev server is running. Backend endpoints work — purely a runtime config issue.

## Constraints

- **Timeline**: Hackathon deadline — phases must be completable in <1 day total
- **Dependencies**: Zero new Python packages — use sqlite3 (stdlib), existing requirements.txt only
- **Compatibility**: Python 3.11+ (KittenTTS has 3.13 incompatibility — text fallback already exists)
- **Git branch**: All work on `feature/cat3-demo-polish`, merge to main before demo

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| sqlite3 over SQLAlchemy | Zero new deps, single .db file, sufficient for demo scale | — Pending |
| CSV-first seeding | CSVs remain authoritative seed; DB is runtime truth — no data migration risk | — Pending |
| CSS injection for Jarvis FAB | Streamlit has no native FAB — position:fixed via st.markdown is the standard workaround | — Pending |
| Stub event_urgency/coverage_diversity at 0.5 | Clear dead config entries without breaking existing weights | — Pending |
| USE_NEMOCLAW=1 env var activation | Activates parallel tool dispatch for faster demo without code changes | — Pending |

---
*Last updated: 2026-03-26 after project initialization on feature/cat3-demo-polish*
