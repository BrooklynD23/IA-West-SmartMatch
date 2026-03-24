# Hackathon For Better Future 2026 - Category 3 SmartMatch CRM

## What This Is

This repository contains the IA West SmartMatch CRM hackathon build, with the active product implementation living in `Category 3 - IA West Smart Match CRM/`. The application is a Streamlit-based demo that loads curated IA West data, discovers public university events, ranks speakers against event and course opportunities, and generates outreach artifacts. In v2.0 the app evolves into a "Jarvis"-style AI coordinator: a full-duplex voice + text agent (powered by KittenTTS) that proposes actions to the human coordinator, and dispatches parallel sub-agents via Nvidia NemoClaw for webscraping, speaker matching, outreach drafting, and POC contact management — all within the existing Streamlit interface.

## Core Value

A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach — with human approval gating every action.

## Current Milestone: v2.0 Jarvis Agent Coordinator

**Goal:** Add an agentic AI coordination layer to SmartMatch CRM — voice/text interface via KittenTTS, sub-agent orchestration via NemoClaw, human-in-the-loop approval for all actions, with a demo-ready "command center" showing multi-agent dispatching in real-time.

**Target features:**
- Full-duplex voice + text interaction with the coordinator via KittenTTS integration
- NemoClaw-orchestrated sub-agents for webscraping, matching, outreach, and POC management
- Human-in-the-loop approval workflow — Jarvis proposes, coordinator approves before execution
- Visual multi-agent orchestration dashboard ("command center") in Streamlit
- Extend existing SmartMatch capabilities (discovery, ranking, outreach) as agent-callable services

## Requirements

### Validated

- ✓ Operators can load the four canonical Category 3 CSV datasets and inspect data quality in the Streamlit app - existing
- ✓ Operators can compute six-factor speaker rankings for events and courses, with explainable score breakdowns - existing
- ✓ Operators can scrape approved university pages, cache results, and extract structured event candidates - existing
- ✓ Operators can generate outreach emails, calendar invites, and pipeline or volunteer views from runtime state - existing
- ✓ Operators can use preflight and demo-support tooling to validate local/demo readiness - existing
- ✓ Sprint 5 closeout resolved the broken discovery-event contract across Discovery, Matches, acceptance, and Volunteer Dashboard - completed 2026-03-21
- ✓ Sprint 5 closeout reconciled tests, status docs, and governance-facing mirrors to the final `392 passed` plus preflight baseline - completed 2026-03-21
- ✓ Sprint 5 closeout kept generated runtime artifacts isolated from source-controlled product files - completed 2026-03-21
- ✓ Sprint 5 ended with a checked-in review artifact, accepted-finding remediation, documentation refresh, and explicit closure evidence on `sprint5-cat3` - completed 2026-03-21

### Active

- [x] Full-duplex voice + text coordinator interface via KittenTTS — Validated in Phase 4: Voice I/O Foundation (human UAT deferred)
- [ ] NemoClaw sub-agent orchestration for webscraping, matching, outreach, and POC management
- [ ] Human-in-the-loop approval workflow — all agent actions require coordinator sign-off
- [x] Visual multi-agent orchestration dashboard ("command center") in Streamlit — Validated in Phase 4: Voice I/O Foundation (Command Center tab)
- [ ] Existing SmartMatch capabilities wrapped as agent-callable services
- [ ] POC contact management with communication history and follow-up tracking

### Out of Scope

- Fully autonomous agent actions without human approval — all actions gate on coordinator confirmation
- Mobile or native app interfaces — Streamlit web interface only for v2.0
- Custom TTS model training — use KittenTTS as provided
- Production deployment infrastructure (auth, scaling, multi-tenant) — demo-focused for hackathon

## Context

- Category 3 authority lives in `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`, `PRD_SECTION_CAT3.md`, `archived/general_project_docs/MASTER_SPRINT_PLAN.md`, and `archived/general_project_docs/STRATEGIC_REVIEW.md`.
- Before this initialization, the repo had no `.planning/` state even though `tasks/todo.md` was already tracking Sprint 5 as a GSD-driven closeout.
- The brownfield codebase map in `.planning/codebase/` confirms that the app runtime already exists and the remaining work is closeout-oriented, not greenfield delivery.
- Closeout evidence is now reconciled to the post-remediation baseline: targeted regressions `87 passed in 6.56s`, full suite `392 passed in 11.93s`, and `scripts/sprint4_preflight.py` passes with expected cache warnings only.
- The current worktree contains unrelated local changes and untracked files, so all Sprint 5 commits must use explicit pathspecs.

## Constraints

- **Tech stack**: Python + Streamlit + pandas + Plotly + Gemini runtime in `Category 3 - IA West Smart Match CRM/src/`, extended with KittenTTS (https://github.com/KittenML/KittenTTS) and Nvidia NemoClaw (https://build.nvidia.com/nemoclaw).
- **Verification**: No phase is done without direct evidence from tests, scripts, or demo verification.
- **Working tree**: The repo is already dirty outside this milestone — use explicit pathspecs for commits.
- **Demo-first**: Every feature must be demonstrable in the Streamlit app for hackathon presentation.
- **Human-in-the-loop**: No agent action executes without coordinator approval — this is a hard architectural constraint, not a nice-to-have.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat Sprint 5 as a closeout milestone derived from local wrap-up signals | No canonical Sprint 5 spec exists, but the repo explicitly says remaining work is documentation/governance refresh plus closeout | Implemented across Phases 1-3 |
| Initialize GSD at the repo root with Category 3 as the active implementation focus | The user asked for repo-level GSD initialization, while the actual runtime work is concentrated in the Category 3 subtree | Implemented during Sprint 5 bootstrap |
| Use parallel mapper and review agents, but keep implementation fixes targeted | Parallel subagents reduce context pressure, while closeout changes should still minimize surface area | Implemented; final remediation stayed narrow |
| Prefer live command output over stale historical pass-count mirrors | Multiple docs disagree on verification totals, so closeout needs one authoritative baseline | Implemented with final `392 passed` baseline |
| Run `$ecc-code-review` before declaring Sprint 5 closed | The request explicitly requires adversarial audit plus remediation before closure | Implemented via `docs/reviews/2026-03-21-sprint5-code-review.md` |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-24 after Phase 4 Voice I/O Foundation completion*
