# Requirements: IA West Smart Match CRM — Demo Polish

**Defined:** 2026-03-26
**Core Value:** Judges can see the full pipeline live: scraper agent discovers real university events → SQLite catalogs them → AI scores volunteer-event ROI → coordinator triggers outreach — all in one demo session.

## v1 Requirements

### Database

- [ ] **DB-01**: App creates `smartmatch.db` on first boot by seeding from existing CSVs
- [ ] **DB-02**: `scraped_opportunities` table stores: university, event_name, category, date_or_recurrence, volunteer_roles, url, contact_email, scraped_at, added_to_pool
- [ ] **DB-03**: `data_loader.py` can load from DB (alongside existing CSV path)
- [ ] **DB-04**: DB tables cover: speakers, events, courses, scraped_opportunities, feedback_log

### Scraper Expansion

- [ ] **SCRP-01**: UNIVERSITY_TARGETS includes all 12 missing SoCal UC/CSU schools
- [ ] **SCRP-02**: UNIVERSITY_COORDINATES includes coordinates for all new schools in config.py
- [ ] **SCRP-03**: Existing 5-school scraper targets are unchanged and still functional

### Live Scraper UI

- [ ] **UI-01**: New "Live Discovery Agent" tab appears in coordinator sidebar nav
- [ ] **UI-02**: "Run SoCal Scrape" button triggers scraper loop over all SoCal schools
- [ ] **UI-03**: Agent feed log updates in real-time as each school is visited (st.empty())
- [ ] **UI-04**: Discovered opportunities table populates live during scrape
- [ ] **UI-05**: Database status counter shows total cataloged + new this session
- [ ] **UI-06**: "Add to Pool" button pushes event into matching session state
- [ ] **UI-07**: FastAPI endpoints: `POST /api/scraper/run` and `GET /api/scraper/opportunities`

### ROI Scoring

- [ ] **ROI-01**: `roi_potential` composite score implemented in `src/matching/factors.py`
- [ ] **ROI-02**: Formula: student_interest×0.35 + event_reach×0.30 + historical_conversion×0.20 + role_fit×0.15
- [ ] **ROI-03**: `CATEGORY_REACH_WEIGHTS` dict added to config.py with 7 event type mappings
- [ ] **ROI-04**: ROI badge displayed on match cards alongside match score
- [ ] **ROI-05**: Sortable ROI column added to pipeline tab
- [ ] **ROI-06**: `event_urgency` and `coverage_diversity` stubbed at 0.5 baseline (dead config cleared)

### Jarvis FAB

- [ ] **JAR-01**: Floating action button (🤖) appears bottom-right on all authenticated pages
- [ ] **JAR-02**: Clicking FAB toggles Jarvis panel open/closed via session_state
- [ ] **JAR-03**: Jarvis panel includes: text input, push-to-talk button, chat history
- [ ] **JAR-04**: Old "Show Jarvis Command Center" sidebar checkbox removed
- [ ] **JAR-05**: FAB renders on ALL authenticated pages (wired in app.py main loop)
- [ ] **JAR-06**: NemoClaw parallel dispatch activated when `USE_NEMOCLAW=1` env var set

### Calendar Fix

- [ ] **CAL-01**: `frontend/src/lib/api.ts` uses `VITE_API_BASE_URL` env var with fallback to `http://localhost:8000`
- [ ] **CAL-02**: `frontend/.env` file created with `VITE_API_BASE_URL=http://localhost:8000`
- [ ] **CAL-03**: React calendar loads events without CORS/proxy error in demo environment

## v2 Requirements

### Future Polish

- **V2-01**: Real-time WebSocket push for scraper feed (vs Streamlit polling)
- **V2-02**: Map view showing volunteer-to-school distance overlays
- **V2-03**: Bulk "Add All to Pool" for discovered opportunities

## Out of Scope

| Feature | Reason |
|---------|--------|
| Email delivery | Demo only — templates generated, not sent |
| Multi-user auth | Single coordinator demo session |
| Cloud deployment | Local demo only |
| SQLAlchemy ORM | sqlite3 stdlib sufficient; zero new deps constraint |
| Playwright JS scraping for new schools | bs4 sufficient for demo; Playwright already used for LA/USC |
| Voice wake word | Push-to-talk is sufficient for demo |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DB-01 | Phase 1 | Pending |
| DB-02 | Phase 1 | Pending |
| DB-03 | Phase 1 | Pending |
| DB-04 | Phase 1 | Pending |
| SCRP-01 | Phase 2 | Pending |
| SCRP-02 | Phase 2 | Pending |
| SCRP-03 | Phase 2 | Pending |
| UI-01 | Phase 3 | Pending |
| UI-02 | Phase 3 | Pending |
| UI-03 | Phase 3 | Pending |
| UI-04 | Phase 3 | Pending |
| UI-05 | Phase 3 | Pending |
| UI-06 | Phase 3 | Pending |
| UI-07 | Phase 3 | Pending |
| ROI-01 | Phase 4 | Pending |
| ROI-02 | Phase 4 | Pending |
| ROI-03 | Phase 4 | Pending |
| ROI-04 | Phase 4 | Pending |
| ROI-05 | Phase 4 | Pending |
| ROI-06 | Phase 4 | Pending |
| JAR-01 | Phase 5 | Pending |
| JAR-02 | Phase 5 | Pending |
| JAR-03 | Phase 5 | Pending |
| JAR-04 | Phase 5 | Pending |
| JAR-05 | Phase 5 | Pending |
| JAR-06 | Phase 5 | Pending |
| CAL-01 | Phase 6 | Pending |
| CAL-02 | Phase 6 | Pending |
| CAL-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 after initial definition*
