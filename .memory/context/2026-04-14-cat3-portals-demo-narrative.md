# Category 3 — Portals, demo DB, and demo narrative (handoff)

**Date:** 2026-04-14  
**Category:** Cat 3  
**Author:** session closeout  
**Status:** Active

## Context

Final verification and demo narrative packaging completed for the React + FastAPI path: student and event coordinator portals, seeded `data/demo.db`, QR attendance extensions, agentic outreach SSE, landing/login UX, and UI hardening (design tokens + ARIA).

## Decision / Context

- **Demo source of truth:** `Category 3 - IA West Smart Match CRM/docs/demo-narrative-2026-04-14.md` (6-scene walkthrough, verification snapshot, competitor comparison, remaining design-pass notes).
- **Seed:** `scripts/seed_demo_db.py` populates synchronized demo entities (students, coordinators, registrations, outreach threads, meetings, retention nudges, mock login roles, calendar/pipeline/QR-related tables as defined in the script).
- **API surface:** `src/api/routers/portals.py` (student/coordinator profiles and related reads + `POST /auth/mock-login`), `src/api/routers/qr.py` + `src/qr/service.py` (attendance check-in/history), `src/api/routers/outreach.py` (agentic workflow SSE).
- **Frontend:** `frontend/src/app/pages/LoginPage.tsx`, `StudentLayout.tsx`, `CoordinatorPortalLayout.tsx`, student/coordinator pages under `app/pages/`, `AgenticOutreachPanel.tsx` / `OutreachWorkflowModal.tsx`, landing portal CTAs.

## Consequences

- Judges and teammates should run the fullstack launcher, seed `demo.db` as needed, and follow the dated demo narrative for rehearsal.
- Next visual pass (Gemini/Sonnet) can target spacing, header hierarchy, optional student top-nav, and transitions; portal surfaces already use semantic design tokens rather than raw Tailwind palette classes.
