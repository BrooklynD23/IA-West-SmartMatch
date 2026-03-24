# Roadmap: IA West SmartMatch CRM

## Milestones

- ✅ **v1.0 Sprint 5 Closeout** — Phases 1-3 (shipped 2026-03-21) | [Archive](milestones/v1.0-ROADMAP.md)
- ✅ **v2.0 Jarvis Agent Coordinator** — Phases 4-7 (shipped 2026-03-24) | [Archive](milestones/v2.0-ROADMAP.md)

- **v3.0 Production UI & Demo Polish** — Phases 8-10 (in progress)

## v3.0 Phases

### Phase 8: Frontend UI Redesign — Landing, Login & Coordinator Dashboard
**Goal:** Replace Streamlit-default UI with pixel-faithful reproductions of the V1.0 mockups. Deliver a public landing page, login/role-selection screen, and coordinator dashboard that use real specialist + POC data from `data/`.

**Scope:**
- Landing page (product showcase, hero, features, CTA) — matches `ia_smartmatch_landing_page_updated/`
- Login page with role selector: Coordinator (full demo), Volunteer (LinkedIn placeholder)
- Coordinator Home Dashboard — matches `coordinator_home_dashboard/`
- Match Engine Dashboard — matches `match_engine_dashboard_updated/`
- Shared design system: Academic Curator (Tailwind tokens, Inter/Inter Tight, tonal layering)
- Data integration: specialist profiles from `data_speaker_profiles.csv`, POCs from `poc_contacts.json`, pipeline from `pipeline_sample_data.csv`

**Requirements:** REQ-UI-01, REQ-UI-02, REQ-UI-03, REQ-UI-04, REQ-UI-05

**Plans:** 5 plans

Plans:
- [ ] 08-01-PLAN.md — Design system, HTML base wrapper, and page router foundation
- [x] 08-02-PLAN.md — Data loading helpers for UI templates
- [ ] 08-03-PLAN.md — Landing page (pixel-faithful HTML via st.components.v1.html)
- [ ] 08-04-PLAN.md — Login/role-selection page
- [ ] 08-05-PLAN.md — Coordinator dashboard, match engine, and app.py wiring

### Phase 9: Voice & Command Center Integration (TBD)
### Phase 10: Demo Rehearsal & Final Polish (TBD)

## Current Status

v3.0 milestone active. Phase 8 planned — 5 plans in 3 waves.
