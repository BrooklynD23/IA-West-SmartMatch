# Hackathon For Better Future 2026 - Category 3 SmartMatch CRM

## What This Is

This repository contains the IA West SmartMatch CRM hackathon build, with the active implementation in `Category 3 - IA West Smart Match CRM/`. The app is a Streamlit demo for event discovery, speaker matching, outreach generation, and coordinator-driven agent orchestration.

## Core Value

A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach, with human approval gating every action.

## Shipped Milestones

- **v1.0 Sprint 5 Closeout (2026-03-21):** Runtime reliability fixes, documentation/governance reconciliation, and adversarial closeout audit remediation. Archive: [milestones/v1.0-ROADMAP.md](milestones/v1.0-ROADMAP.md)
- **v2.0 Jarvis Agent Coordinator (2026-03-24):** Voice I/O foundation, coordinator HITL state machine, agent tool wrappers with result bus, and NemoClaw-enabled live dashboard. Archive: [milestones/v2.0-ROADMAP.md](milestones/v2.0-ROADMAP.md)
- **v3.0 Production UI & Demo Polish (2026-03-26):** FastAPI + React promotion completion, V1.2 rebrand, recovery-aware scheduling, QR ROI tracking, and continuous algorithm-improvement feedback loop. Archive: [milestones/v3.0-ROADMAP.md](milestones/v3.0-ROADMAP.md)

## Current State

- Command Center supports text and voice interaction paths.
- Approval cards gate every proposed agent action.
- Tool wrappers dispatch discovery, ranking, outreach, and contact workflows.
- Swimlane dashboard renders real-time per-agent statuses.
- React + FastAPI coordinator surfaces now cover recovery-aware scheduling, QR attribution, and feedback-driven optimizer analytics.
- Demo-first constraints remain in effect (single-tenant, no production auth/scaling).
- All v3.0 phases through continuous-improvement feedback are complete and verified at the focused contract/build level.

## v3.0 Completion (Shipped: 2026-03-26)

- ~~Phase 8.5: FastAPI backend + React promotion from V1.1 mockup~~ ✅
- ~~Phase 9: Outreach button + NemoClaw workflow integration~~ ✅
- ~~Phase 09.1: V1.2 UI Rebrand — blue/white professional theme (INSERTED)~~ ✅
- ~~Phase 10: Master calendar + volunteer recovery period factor~~ ✅
- ~~Phase 11: QR code generation + ROI tracking~~ ✅
- ~~Phase 12: Continuous algorithm improvement via feedback loops~~ ✅

## Constraints

- **Tech stack:** Python + FastAPI (backend) + React 18/Vite/Tailwind v4/shadcn-ui (frontend) + Gemini runtime + NemoClaw
- **Migration strategy:** Parallel — keep Streamlit on `:8501` during migration, React on `:5173`, FastAPI on `:8000`
- **Storage:** CSV/JSON local storage for QR tracking and feedback/optimizer history (hackathon scope, no cloud DB)
- **Verification standard:** No phase is complete without direct test/demo evidence.
- **Human-in-the-loop:** No autonomous execution without coordinator approval.

---
*Last updated: 2026-03-26 after v3.0 shipped*
