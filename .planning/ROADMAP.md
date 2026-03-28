# Roadmap: IA West SmartMatch CRM

## Milestones

- ✅ **v1.0 Sprint 5 Closeout** — Phases 1-3 (shipped 2026-03-21) | [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v2.0 Jarvis Agent Coordinator** — Phases 4-7 (shipped 2026-03-24) | [Archive](milestones/v2.0-ROADMAP.md)
- ✅ **v3.0 Production UI & Demo Polish** — Phases 8-12 (shipped 2026-03-26) | [Archive](milestones/v3.0-ROADMAP.md)
- ✅ **v3.1 Demo Readiness** — Phases 13-17 (shipped 2026-03-28)
- 🚧 **v3.2 Tech Debt Cleanup** — Phases 18-19 (in progress)

<details>
<summary>✅ v3.0 Production UI & Demo Polish (Phases 8-12) - SHIPPED 2026-03-26</summary>

## v3.0 Phases

### Phase 8: Frontend UI Redesign — Landing, Login & Coordinator Dashboard ✅
**Goal:** Replace Streamlit-default UI with pixel-faithful reproductions of the V1.0 mockups. Deliver a public landing page, login/role-selection screen, and coordinator dashboard that use real specialist + POC data from `data/`.

**Scope:**
- Landing page (product showcase, hero, features, CTA) — matches `ia_smartmatch_landing_page_updated/`
- Login page with role selector: Coordinator (full demo), Volunteer (LinkedIn placeholder)
- Coordinator Home Dashboard — matches `coordinator_home_dashboard/`
- Match Engine Dashboard — matches `match_engine_dashboard_updated/`
- Shared design system: Academic Curator (Tailwind tokens, Inter/Inter Tight, tonal layering)
- Data integration: specialist profiles from `data_speaker_profiles.csv`, POCs from `poc_contacts.json`, pipeline from `pipeline_sample_data.csv`

**Requirements:** REQ-UI-01, REQ-UI-02, REQ-UI-03, REQ-UI-04, REQ-UI-05

**Plans:** 5/5 plans executed

Plans:
- [x] 08-01-PLAN.md — Design system, HTML base wrapper, and page router foundation
- [x] 08-02-PLAN.md — Data loading helpers for UI templates
- [x] 08-03-PLAN.md — Landing page (pixel-faithful HTML via st.components.v1.html)
- [x] 08-04-PLAN.md — Login/role-selection page
- [x] 08-05-PLAN.md — Coordinator dashboard, match engine, and app.py wiring

### Phase 8.5: FastAPI Backend + React Promotion ✅
**Goal:** Stand up a FastAPI backend that exposes all existing Python business logic as REST endpoints, and promote the V1.1 React mockup to a production frontend that calls these APIs.

**Scope:**
- FastAPI application at `src/api/` with CORS config
- REST routers: matching, outreach, data
- Promote `docs/mockup/V1.1/IA-West_UI/` to `frontend/` production app
- Wire React pages to fetch from FastAPI instead of hardcoded data
- Keep Streamlit running in parallel (don't delete)
- FastAPI on `:8000`, React dev on `:5173` with proxy

**Success Criteria:**
- `uvicorn src.api.main:app` starts without errors
- `GET /api/data/specialists` returns specialist records
- `POST /api/matching/rank` returns ranked matches with scores
- React frontend loads all pages from V1.1 mockup
- Volunteer Profiles grid renders with real data
- Pipeline funnel renders with real data

**Plans:** 3/3 plans executed

Plans:
- [x] 08.5-01-PLAN.md — FastAPI app with data, matching, and outreach routers
- [x] 08.5-02-PLAN.md — React promotion from V1.1 mockup to frontend/ with API client
- [x] 08.5-03-PLAN.md — Wire all React pages to fetch real data from FastAPI

### Phase 9: Outreach Button + NemoClaw Workflow ✅
**Goal:** Wire the "Initiate Outreach" button in the React Match Engine page to trigger a complete NemoClaw-orchestrated workflow: email generation + meeting scheduling + pipeline status update.

**Scope:**
- `/api/outreach/workflow` endpoint orchestrating full outreach flow
- Meeting coordination tool with timezone-aware suggestions
- OutreachWorkflowModal in React with progress overlay
- Pipeline status transitions ("Matched" → "Contacted")
- NemoClaw parallel dispatch with serial fallback

**Requirements:** WF-01, WF-02, WF-03, WF-04, WF-05, WF-06, WF-07, WF-08

**Success Criteria:**
- "Initiate Outreach" button triggers API call
- Email generated and displayed in modal
- Calendar invite downloadable as .ics
- NemoClaw parallel dispatch works (or falls back to serial)
- Pipeline status updates from "Matched" to "Contacted"

**Plans:** 2/2 plans complete

Plans:
- [x] 09-01-PLAN.md — Backend workflow endpoint + pipeline updater with tests
- [x] 09-02-PLAN.md — Frontend OutreachWorkflowModal + AIMatching upgrade

### Phase 09.1: V1.2 UI Rebrand - Blue/White Professional Theme ✅
**Goal:** Apply the V1.2 senior-frontend audit across the React app so the public entry path, coordinator shell, volunteer management, and AI matching surfaces all ship with the professional blue/white IA West design language.

**Scope:**
- Tokenize the public V1.2 brand in `theme.css` and `fonts.css`
- Rebuild the landing page as a real React page with motion and anchored storytelling sections
- Keep coordinator login functional while preserving the volunteer LinkedIn placeholder
- Rebrand the authenticated shell, KPI cards, dashboard, and opportunities page to the V1.2 institutional look
- Add fatigue-aware volunteer presentation and richer AI matching factor visuals without introducing new backend dependencies

**Success Criteria:**
- Public landing/login share one brand system and route cleanly into coordinator login
- Dashboard exposes the V1.2 density-map and discovery-feed enhancements
- Volunteer cards/detail view expose fatigue-aware coordinator cues
- AI Matching keeps the top-five contract with blue-theme factor/radar presentation
- Merged frontend build passes after the phase integration review

**Plans:** 3/3 plans executed

Plans:
- [x] 09.1-01-PLAN.md - Public brand foundation, routing, landing page, and login flow
- [x] 09.1-02-PLAN.md - Authenticated shell, KPI cards, dashboard, and opportunities polish
- [x] 09.1-03-PLAN.md - Volunteers and AI Matching fatigue-aware V1.2 refresh

### Phase 10: Master Calendar + Volunteer Recovery Period ✅
**Goal:** Add a master calendar showing all events and volunteer assignments, plus a "recovery period" algorithm factor that prevents over-scheduling volunteers.

**Scope:**
- `volunteer_fatigue` scoring factor (days since last event, travel distance, event duration, 30-day event count)
- Factor weight: configurable, default 0.10
- Master calendar with month/week/day views, color-coded events
- Volunteer assignment overlay and recovery period visualization
- Recovery status badge (Available / Needs Rest / On Cooldown)
- Calendar API router: `/api/calendar/events`, `/api/calendar/assignments`

**Success Criteria:**
- Master calendar shows all events with color coding
- Volunteer assignments visible on calendar
- `volunteer_fatigue` factor appears in match score breakdown
- Recovery badge shows on volunteer cards
- Re-matching after recent event shows reduced fatigue score

**Plans:** 2/2 plans executed

Plans:
- [x] 10-01-PLAN.md - Backend recovery factor and calendar API contract
- [x] 10-02-PLAN.md - React master calendar and recovery-aware coordinator surfaces

### Phase 11: QR Code Generation + ROI Tracking ✅
**Goal:** Generate unique QR codes for each speaker-event pair that encode referral metadata, allowing students to scan at events for membership sign-up tracking and ROI measurement.

**Scope:**
- QR code generation with `qrcode` + `Pillow` (IA West branding overlay)
- Deterministic referral code generation per speaker-event pair
- Scan tracking + analytics (CSV/JSON local storage)
- QR API router: `/api/qr/generate`, `/api/qr/scan/{code}`, `/api/qr/stats`
- QRCodeCard React component with display + download
- Pipeline dashboard QR scan analytics section

**Success Criteria:**
- QR code generates with IA West branding for any speaker-event pair
- QR encodes unique referral code
- Scan endpoint redirects to sign-up URL with referral code
- Pipeline dashboard shows QR scan → sign-up conversion

**Plans:** 2/2 plans executed

Plans:
- [x] 11-01-PLAN.md - Backend QR generation, scan logging, and stats contract
- [x] 11-02-PLAN.md - React QR generation workflow plus ROI analytics integration

### Phase 12: Continuous Algorithm Improvement ✅
**Goal:** Implement a feedback loop where match outcomes feed back into scoring weights, continuously improving match quality.

**Scope:**
- Feedback collection: match acceptance, event outcome, student engagement, coordinator/volunteer ratings
- Match success score computation from feedback data
- Weight optimizer: simple gradient adjustment of factor weights
- Weight history audit trail
- Feedback API: `/api/feedback/submit`, `/api/feedback/stats`
- FeedbackForm React component (post-event modal)
- Dashboard algorithm performance section + Pain Score tracking

**Success Criteria:**
- Feedback form collectable after events
- Weight optimizer produces adjusted weights from feedback
- Dashboard shows algorithm improvement over time
- Pain score metrics tracked and visualized

**Plans:** 2/2 plans executed

Plans:
- [x] 12-01-PLAN.md - Backend feedback service, persisted optimizer snapshots, and FastAPI feedback contract
- [x] 12-02-PLAN.md - React feedback form plus dashboard/pipeline optimizer analytics

---

</details>

## v3.1 Demo Readiness

### Phases

- [x] **Phase 13: Demo Polish** — Remove internal labels, finalize all copy, and enable smooth scrolling (completed 2026-03-27)
- [x] **Phase 14: Visual Resilience** — Graceful fallback graphics with Demo Mode indicator (completed 2026-03-27)
- [x] **Phase 15: Build Quality + Playwright Evidence** — Fix chunk-size warning and capture browser test evidence for QR and feedback flows (completed 2026-03-28)
- [x] **Phase 16: Voice/Mic UAT Guide** — Structured human walkthrough document for live voice path (completed 2026-03-28)
- [x] **Phase 17: Persistent Database Layer + Web Crawler Live Feed** — Introduce Layer 0 (persistent SQLite), remap Layer 1 (demo.db) and Layer 2 (CSV), seed all layers with IA West data, and add real-time Gemini/Tavily web crawler activity feed for coordinators (completed 2026-03-28)

### Phase Details

### Phase 13: Demo Polish
**Goal:** Every user-facing text string is submission-ready — no internal phase labels, no placeholder copy, and all page transitions scroll smoothly.
**Depends on:** Nothing (first phase of v3.1)
**Requirements:** POLISH-01, POLISH-02, POLISH-03
**Success Criteria** (what must be TRUE):
  1. No "Phase #N" or similar internal label appears anywhere in the rendered app across all pages
  2. Every page heading, button label, and body copy reads as concrete, professional product text with no dev-flavored placeholders
  3. Navigating between pages and scrolling within any page produces smooth animated transitions with no abrupt jumps
**Plans:** 1/1 plans complete

Plans:
- [x] 13-01-PLAN.md — Remove Phase labels, replace dev copy, add scroll-to-top

### Phase 14: Visual Resilience
**Goal:** Charts, images, and data visualizations never show broken states — they render real data or silently fall back to hardcoded mock data, and the coordinator always knows when mock data is active.
**Depends on:** Phase 13
**Requirements:** POLISH-04, POLISH-05
**Success Criteria** (what must be TRUE):
  1. Every chart and visualization in the app renders without error regardless of whether the backend returns data or not
  2. When a visualization uses fallback mock data, a discrete "Demo Mode" badge or indicator is visible on that view without disrupting the layout
  3. The "Demo Mode" indicator is absent on any view that has successfully loaded real data
**Plans:** 2/2 plans complete

Plans:
- [x] 14-01-PLAN.md — Backend demo.db seed, helper module, and router fallback wiring
- [x] 14-02-PLAN.md — Frontend mockData constants, DemoModeBadge, and page-level isMockData wiring

### Phase 15: Build Quality + Playwright Evidence
**Goal:** The React production build is clean and browser-captured evidence proves the QR and feedback flows work end-to-end.
**Depends on:** Phase 14
**Requirements:** BUILD-01, VERIFY-01, VERIFY-02
**Success Criteria** (what must be TRUE):
  1. `npm run build` completes with zero chunk-size warnings
  2. A Playwright test script runs headlessly and captures a passing assertion that QR code generation and scan attribution complete in the browser
  3. A Playwright test script runs headlessly and captures a passing assertion that coordinator feedback submission triggers weight-shift analytics rendering in the browser
  4. Both test artifacts (screenshots or trace files) are committed as evidence alongside the test scripts
**Plans:** 2/2 plans complete

Plans:
- [x] 15-01-PLAN.md — Fix React build chunk-size warning via manualChunks vendor splitting
- [x] 15-02-PLAN.md — Python Playwright E2E tests for QR and feedback flows with screenshot evidence

### Phase 16: Voice/Mic UAT Guide
**Goal:** A human reviewer can pick up the UAT guide and independently walk through the live voice/mic coordinator path with no prior knowledge of the implementation.
**Depends on:** Phase 15
**Requirements:** VERIFY-03
**Success Criteria** (what must be TRUE):
  1. The UAT guide lists every step in the voice/mic workflow in sequence, with the exact expected outcome for each step
  2. A reviewer following only the guide can trigger voice input, observe intent parsing, see an approval card, and confirm agent action gating without requiring any developer assistance
  3. The guide documents known edge cases (microphone permission prompt, fallback to text input) with explicit handling steps
**Plans:** 1/1 plans complete

Plans:
- [x] 16-01-PLAN.md — Write and validate UAT voice/mic walkthrough guide

### Phase 17: Persistent Database Layer + Web Crawler Live Feed
**Goal:** Replace the current 2-layer fallback (CSV → demo.db) with a 3-layer architecture where a persistent SQLite database is Layer 0 (always-on primary), demo.db becomes Layer 1, and CSVs are Layer 2 (last resort). Add a real-time web crawler feed so coordinators can watch Gemini/Tavily discover directed school pages live.
**Depends on:** Phase 16
**Requirements:** DB-01, DB-02, DB-03, DB-04, CRAWLER-01, CRAWLER-02, CRAWLER-03
**Success Criteria** (what must be TRUE):
  1. A persistent `data/smartmatch.db` SQLite database exists and is the primary data source for all API endpoints
  2. All IA West CSV datasets are imported into `smartmatch.db` on first run (specialists, events, pipeline, calendar, QR, feedback)
  3. Layer fallback order is: `smartmatch.db` → `demo.db` → CSV, with source tag (`live`, `demo`, `csv`) in every API response
  4. Web crawler events discovered by Gemini/Tavily are stored in `smartmatch.db`'s `web_crawler_events` table
  5. A `/api/crawler/feed` SSE endpoint streams real-time crawler activity (URL visited, title extracted, timestamp) to the frontend
  6. The coordinator dashboard shows a live scrolling feed of crawler activity (site names, crawl status) similar to ChatGPT deep research UI
  7. Coordinator can trigger a new crawl targeting IA West directed school pages from the UI
**Plans:** 2/3 plans executed

Plans:
- [x] 17-01-PLAN.md — Create `smartmatch.db` schema, seed script with IA West data, and migrate Layer 0 into all API endpoints
- [x] 17-02-PLAN.md — Web crawler backend: Gemini/Tavily integration, SSE feed endpoint, `web_crawler_events` table
- [x] 17-03-PLAN.md — Frontend crawler live feed UI: real-time scrolling activity panel and trigger button


### Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 13. Demo Polish | 1/1 | Complete    | 2026-03-27 |
| 14. Visual Resilience | 2/2 | Complete    | 2026-03-27 |
| 15. Build Quality + Playwright Evidence | 2/2 | Complete    | 2026-03-28 |
| 16. Voice/Mic UAT Guide | 1/1 | Complete    | 2026-03-28 |
| 17. Persistent Database Layer + Web Crawler Live Feed | 3/3 | Complete    | 2026-03-28 |

---

---

## v3.2 Tech Debt Cleanup

### Phases

- [ ] **Phase 18: Tech Debt Cleanup — Code Fixes** — Fix 4 code-level items from v3.1 audit
- [ ] **Phase 19: Human UAT Sign-off** — Complete all deferred human validation items from phases 14-16

### Phase Details

### Phase 18: Tech Debt Cleanup — Code Fixes
**Goal:** Resolve all code-level tech debt identified in the v3.1 audit — type safety gap, frozen crawler timestamps, stale Playwright docstrings, and TypeScript build errors.
**Depends on:** Phase 17
**Requirements:** DEBT-01, DEBT-02, DEBT-03, DEBT-04
**Gap Closure:** Closes code-fixable tech debt from v3.1 audit
**Success Criteria** (what must be TRUE):
  1. `WithSource<T>` in `frontend/src/lib/api.ts` includes `"csv"` as a valid source type and `isMockData` is true when source is `"csv"`
  2. Crawler timestamp in `src/api/routers/crawler.py` calls `.isoformat()` (with parentheses) so each event gets a distinct timestamp
  3. DB-01–CRAWLER-03 requirements are added to REQUIREMENTS.md traceability table with Phase 17 mapped
  4. framer-motion TypeScript errors in LandingPage.tsx and LoginPage.tsx are resolved and `npm run build` reports zero TS errors from those files
**Plans:** 0/1 plans

Plans:
- [ ] 18-01-PLAN.md — Fix WithSource csv type, crawler timestamp, REQUIREMENTS.md doc gap, framer-motion TS errors

### Phase 19: Human UAT Sign-off
**Goal:** A human reviewer completes all deferred UAT walkthroughs from v3.1 and any remaining code cleanup (stale docstrings) is resolved, so the codebase has zero outstanding audit items.
**Depends on:** Phase 18
**Requirements:** UAT-01, UAT-02, UAT-03, UAT-04, UAT-05
**Gap Closure:** Closes all human validation items from v3.1 audit
**Success Criteria** (what must be TRUE):
  1. Human confirms Demo Mode badge is visible when backend is offline (Phase 14 UAT)
  2. Human confirms badge is absent when live data is returned (Phase 14 UAT)
  3. Human inspects `react-qr-flow.png` and `react-feedback-flow.png` and confirms meaningful content is visible (Phase 15 UAT)
  4. Playwright test docstrings updated to reference `smartmatch.db` as Layer 0 (Phase 15 doc fix)
  5. Human completes live voice/audio WebRTC end-to-end walkthrough via the UAT guide (Phase 16 UAT)
  6. Human confirms multi-card simultaneous rendering for `prepare_campaign` intent (Phase 16 UAT)
**Plans:** 0/1 plans

Plans:
- [ ] 19-01-PLAN.md — UAT checklist execution + Playwright docstring update

### Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 18. Tech Debt Cleanup — Code Fixes | 0/1 | Pending | — |
| 19. Human UAT Sign-off | 0/1 | Pending | — |

---

## Backlog / Parking Lot

- **Gmail Send Integration** — Wire generated outreach email to Gmail API (OAuth2) so coordinators can send directly from the modal instead of copy-pasting. Potential post-hackathon.

## Current Status

v3.1 complete. All phases 13-17 complete. Pre-demo 1.0 audit passed (2026-03-28). v3.2 tech debt phases 18-19 added (2026-03-28).
