# Requirements: IA West SmartMatch CRM

**Defined:** 2026-03-26
**Core Value:** A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach, with human approval gating every action.

## v3.1 Requirements

Requirements for the Demo Readiness milestone. Each maps to roadmap phases.

### Verification

- [x] **VERIFY-01**: Playwright automated test demonstrates QR code generation and scan attribution flowing end-to-end in the browser
- [x] **VERIFY-02**: Playwright automated test demonstrates coordinator feedback submission and weight-shift analytics rendering in the browser
- [x] **VERIFY-03**: UAT guide documents live voice/mic workflow steps with expected outcomes so a human reviewer can run a structured walkthrough

### Build Quality

- [x] **BUILD-01**: React production build completes without chunk-size warnings

### Demo Polish

- [x] **POLISH-01**: All internal "Phase #N" labels removed from user-facing UI text across all pages
- [x] **POLISH-02**: All page headings, button labels, and body copy are concrete and demo-ready (no placeholder or dev-flavored text)
- [x] **POLISH-03**: Smooth scrolling applied across all pages and view transitions
- [x] **POLISH-04**: All charts, images, and data visualizations load real data or fall back gracefully to hardcoded mock data when unavailable
- [x] **POLISH-05**: Any view displaying fallback/mock data shows a discrete "Demo Mode" indicator visible to the coordinator

## v3.1 Phase 17 Requirements (Previously Unregistered)

Requirements tracked in ROADMAP.md only — all verified by Phase 17 VERIFICATION.md. Registered here to close documentation gap (DEBT-03).

### Persistent Database Layer

- [x] **DB-01**: Persistent `data/smartmatch.db` SQLite database exists and is the primary data source (Layer 0) for all API endpoints
- [x] **DB-02**: All IA West CSV datasets are imported into `smartmatch.db` on first run (specialists, events, pipeline, calendar, QR, feedback)
- [x] **DB-03**: Layer fallback order is `smartmatch.db` → `demo.db` → CSV, with source tag (`live`, `demo`, `csv`) in every API response
- [x] **DB-04**: Web crawler events discovered by Gemini/Tavily are stored in `smartmatch.db`'s `web_crawler_events` table

### Web Crawler Live Feed

- [x] **CRAWLER-01**: `/api/crawler/feed` SSE endpoint streams real-time crawler activity (URL visited, title extracted, timestamp) to the frontend
- [x] **CRAWLER-02**: Coordinator dashboard shows a live scrolling feed of crawler activity (site names, crawl status)
- [x] **CRAWLER-03**: Coordinator can trigger a new crawl targeting IA West directed school pages from the UI

## v3.2 Requirements

Requirements for the Tech Debt Cleanup milestone (phases 18-19).

### Code Debt Fixes

- [ ] **DEBT-01**: `WithSource<T>` in `frontend/src/lib/api.ts` includes `"csv"` source type and `isMockData` is true when source is `"csv"`
- [ ] **DEBT-02**: Crawler timestamp in `src/api/routers/crawler.py` calls `.isoformat()` so each crawl event gets a distinct timestamp
- [ ] **DEBT-03**: DB-01–CRAWLER-03 added to REQUIREMENTS.md traceability table with Phase 17 mapped
- [ ] **DEBT-04**: framer-motion TypeScript errors in LandingPage.tsx and LoginPage.tsx resolved

### Human UAT Sign-off

- [ ] **UAT-01**: Human confirms Demo Mode badge visible when backend is offline
- [ ] **UAT-02**: Human confirms Demo Mode badge absent when live data is returned
- [ ] **UAT-03**: Human inspects `react-qr-flow.png` and `react-feedback-flow.png` for meaningful content
- [ ] **UAT-04**: Human completes live voice/audio WebRTC end-to-end walkthrough via UAT guide
- [ ] **UAT-05**: Human confirms multi-card simultaneous rendering for `prepare_campaign` intent

## Future Requirements

Tracked but deferred beyond v3.2.

### Testing

- Gmail integration for generated outreach emails — captured as future phase

### Infrastructure

- Browser-backed smoke pass for additional coordinator workflows (expanded beyond QR/feedback)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Production auth/scaling | Hackathon scope — demo-first constraints remain |
| Cloud database | Local CSV/JSON storage sufficient for demo |
| Mobile app | Web-first, not required for hackathon submission |
| Multi-tenant support | Single-tenant demo scope |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| POLISH-01 | Phase 13 | Complete |
| POLISH-02 | Phase 13 | Complete |
| POLISH-03 | Phase 13 | Complete |
| POLISH-04 | Phase 14 | Complete |
| POLISH-05 | Phase 14 | Complete |
| BUILD-01 | Phase 15 | Complete |
| VERIFY-01 | Phase 15 | Complete |
| VERIFY-02 | Phase 15 | Complete |
| VERIFY-03 | Phase 16 | Complete |
| DB-01 | Phase 17 | Complete |
| DB-02 | Phase 17 | Complete |
| DB-03 | Phase 17 | Complete |
| DB-04 | Phase 17 | Complete |
| CRAWLER-01 | Phase 17 | Complete |
| CRAWLER-02 | Phase 17 | Complete |
| CRAWLER-03 | Phase 17 | Complete |
| DEBT-01 | Phase 18 | Pending |
| DEBT-02 | Phase 18 | Pending |
| DEBT-03 | Phase 18 | Pending |
| DEBT-04 | Phase 18 | Pending |
| UAT-01 | Phase 19 | Pending |
| UAT-02 | Phase 19 | Pending |
| UAT-03 | Phase 19 | Pending |
| UAT-04 | Phase 19 | Pending |
| UAT-05 | Phase 19 | Pending |

**Coverage:**
- v3.1 requirements: 16 total (9 original + 7 Phase 17)
- v3.2 requirements: 9 total (4 code debt + 5 human UAT)
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 after v3.1 roadmap creation*
