# Roadmap: IA West SmartMatch CRM

## Milestones

- ✅ **v1.0 Sprint 5 Closeout** — Phases 1-3 (shipped 2026-03-21) | [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v2.0 Jarvis Agent Coordinator** — Phases 4-7 (shipped 2026-03-24) | [Archive](milestones/v2.0-ROADMAP.md)

- **v3.0 Production UI & Demo Polish** — Phases 8-12 (in progress)

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

### Phase 9: Outreach Button + NemoClaw Workflow
**Goal:** Wire the "Initiate Outreach" button in the React Match Engine page to trigger a complete NemoClaw-orchestrated workflow: email generation + meeting scheduling + pipeline status update.

**Scope:**
- `/api/outreach/workflow` endpoint orchestrating full outreach flow
- Meeting coordination tool with timezone-aware suggestions
- OutreachWorkflowModal in React with progress overlay
- Pipeline status transitions ("Matched" → "Contacted")
- NemoClaw parallel dispatch with serial fallback

**Success Criteria:**
- "Initiate Outreach" button triggers API call
- Email generated and displayed in modal
- Calendar invite downloadable as .ics
- NemoClaw parallel dispatch works (or falls back to serial)
- Pipeline status updates from "Matched" to "Contacted"

### Phase 10: Master Calendar + Volunteer Recovery Period
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

### Phase 11: QR Code Generation + ROI Tracking
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

### Phase 12: Continuous Algorithm Improvement
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

## Current Status

v3.0 milestone active. Phases 8 and 8.5 complete. Next: Phase 9 (Outreach Button + NemoClaw Workflow).
