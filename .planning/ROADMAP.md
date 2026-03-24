# Roadmap: IA West SmartMatch CRM

## Overview

This roadmap covers two milestones for the Category 3 SmartMatch CRM on `sprint5-cat3` and `sprint6-cat3`.

**v1.0 (Sprint 5 Closeout):** Closes Sprint 5 — restores the live demo path, reconciles docs and governance from one verification baseline, runs adversarial audit, remediates findings, and records explicit closure evidence.

**v2.0 (Jarvis Agent Coordinator):** Adds a "Jarvis"-style AI coordination layer — full-duplex voice + text interface, human-in-the-loop approval for all agent actions, NemoClaw-orchestrated sub-agents wrapping existing SmartMatch services, and a visual Command Center dashboard. Phases are strictly ordered by dependency so a demoable product exists at the end of every phase even if the next phase encounters alpha-library instability.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, ...): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

### v1.0 — Sprint 5 Closeout

- [x] **Phase 1: Runtime Fixes and Clean Outputs** - Restore the closeout-critical demo path and isolate generated runtime artifacts.
- [x] **Phase 2: Documentation and Governance Reconciliation** - Refresh Category 3 closeout docs and mirrors from one live verification baseline.
- [x] **Phase 3: Adversarial Audit and Sprint Closure** - Run `$ecc-code-review`, remediate accepted findings, verify the final state, and close Sprint 5.

### v2.0 — Jarvis Agent Coordinator

- [x] **Phase 4: Voice I/O Foundation** - Validate KittenTTS (TTS) and faster-whisper (STT) on demo hardware; deliver a working voice panel with text fallback before any agent complexity is added.
- [x] **Phase 5: Coordinator Core and HITL Approval Gate** - Implement the Gemini-powered intent parser and the approval state machine; prove the full voice → intent → propose → approve/reject cycle with stubbed agent execution. (completed 2026-03-24)
- [x] **Phase 6: Agent Tool Wrappers and Result Bus** - Wrap existing SmartMatch services as OpenClaw-callable tools; establish background-threading safety; add POC contact data layer; deliver direct-dispatch fallback path. (completed 2026-03-24)
- [ ] **Phase 7: NemoClaw Lead Agent and Live Dashboard** - Integrate NemoClaw orchestrator; complete the Command Center with real-time per-agent status; add proactive Jarvis suggestions; deliver end-to-end demo.

## Phase Details

### Phase 1: Runtime Fixes and Clean Outputs
**Goal**: The operator can run the intended discovery-to-match demo flow from stable project-root configuration without generated rehearsal outputs polluting source-controlled diffs.
**Depends on**: Nothing (first phase)
**Requirements**: FLOW-01, FLOW-02, DEMO-01, PATH-01, OPS-01
**Parallelization**: After the runtime handoff contract is fixed, regression coverage work and artifact-isolation work can run in parallel subagents.
**Success Criteria** (what must be TRUE):
  1. Operator can add a discovered event to the active match pool and see it in the Matches tab during the same Streamlit session.
  2. Automated regression coverage fails when the discovery-to-matching session-state handoff breaks.
  3. Operator can exercise the core matching flow in Demo Mode or cache-only mode on a clean checkout without requiring live Gemini calls.
  4. Running the app from the repo root or the Category 3 directory writes feedback and generated artifacts to configured project-root locations.
  5. Rehearsal and runtime-generated files are ignored or isolated so they do not appear as product-source changes during Sprint 5 work.
**Plans**: 3 plans

Plans:
- [x] 01-01: Repair the discovery-to-matching handoff and project-root path resolution in the existing runtime.
- [x] 01-02: Add targeted regression coverage for the handoff and clean-checkout demo-mode or cache-only flow.
- [x] 01-03: Isolate or ignore generated runtime outputs and verify that closeout rehearsal does not dirty source-controlled paths.

### Phase 2: Documentation and Governance Reconciliation
**Goal**: Category 3 closeout docs, status surfaces, and governance mirrors report one current verification baseline and one truthful set of remaining manual steps.
**Depends on**: Phase 1
**Requirements**: GOV-01, DOC-01
**Parallelization**: Once the live verification baseline is established, Category 3 doc refreshes and governance-mirror reconciliation can run in parallel subagents.
**Success Criteria** (what must be TRUE):
  1. Category 3 status docs, sprint docs, and the task board all report the same current verification baseline for Sprint 5 closeout.
  2. Operators can read the closeout docs and see the real remaining manual steps, demo readiness, and preflight expectations without stale or contradictory claims.
  3. Governance-facing mirrors point back to one live source of truth for closeout evidence instead of maintaining conflicting copies.
**Plans**: 2 plans

Plans:
- [x] 02-01: Reconcile the canonical verification baseline across Category 3 status, sprint, and task-board documents.
- [x] 02-02: Refresh closeout guidance and governance mirrors so manual steps, readiness notes, and ownership are current.

### Phase 3: Adversarial Audit and Sprint Closure
**Goal**: Sprint 5 changes survive adversarial review, accepted findings are resolved or explicitly documented, and closure evidence is preserved on `sprint5-cat3`.
**Depends on**: Phase 2
**Requirements**: REV-01, REV-02
**Parallelization**: After review triage, independent accepted findings can be remediated in parallel subagents before one final verification and closure pass.
**Success Criteria** (what must be TRUE):
  1. Sprint 5 changes have an `$ecc-code-review` report that records severity, locations, and suggested fixes for the branch delta.
  2. Every accepted review finding is fixed or explicitly documented before the sprint is closed.
  3. Direct verification evidence for touched behavior is recorded in planning or task docs and matches the final closeout state.
  4. Sprint 5 closure on `sprint5-cat3` is supported by scoped remediation work and explicit final verification evidence.
**Plans**: 3 plans

Plans:
- [x] 03-01: Run `$ecc-code-review` on the Sprint 5 change set and triage findings by acceptance and severity.
- [x] 03-02: Remediate accepted findings, rerun targeted or full verification, and keep fixes inside the closeout scope.
- [x] 03-03: Record final closure evidence in planning or task docs and prepare the sprint-closeout handoff.

### Phase 4: Voice I/O Foundation
**Goal**: Coordinator can speak to and hear Jarvis via a working push-to-talk + TTS voice panel in Streamlit, with text command input as a reliable fallback, before any agent or coordinator logic depends on the voice layer.
**Depends on**: Phase 3
**Requirements**: VOICE-01, VOICE-02, VOICE-03, VOICE-04
**Success Criteria** (what must be TRUE):
  1. Coordinator can type a text command in the Command Center tab and receive a parsed intent response rendered in the UI.
  2. Coordinator can hear a hardcoded Jarvis reply spoken aloud via KittenTTS voice synthesis after submitting any command.
  3. Coordinator can press a push-to-talk button, speak a sentence, and see the transcribed text appear in the input field via faster-whisper STT.
  4. Coordinator can scroll the Command Center and see a full chronological history of every voice and text exchange in the current session.
  5. All 392 existing tests continue to pass after the voice layer is added (no existing signature changes).
**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — Voice service modules (TTS + STT) with tests and dependencies
- [x] 04-02-PLAN.md — Command Center UI tab with text input, echo replies, and conversation history
- [x] 04-03-PLAN.md — Integration wiring: TTS + STT + push-to-talk into Command Center tab in app.py

### Phase 5: Coordinator Core and HITL Approval Gate
**Goal**: Coordinator can submit any command (voice or text), have Jarvis parse the intent and propose a concrete agent action with reasoning, and explicitly approve or reject that action before any execution occurs — the approval state machine is proven correct with stubbed agent calls.
**Depends on**: Phase 4
**Requirements**: HITL-01, HITL-02, HITL-03, ORCH-04
**Success Criteria** (what must be TRUE):
  1. Every proposed agent action displays a card showing the agent name, action description, and Jarvis reasoning before any execution begins.
  2. Coordinator can click Approve on a proposed action card and see its status advance to "Executing" (or a stub success result).
  3. Coordinator can click Reject on a proposed action card and confirm that no agent execution is triggered.
  4. Coordinator can edit the parameters of a proposed action before approving it, and the edited values are what gets executed.
  5. Jarvis proactively surfaces a suggested action (e.g. "discovery data is stale — re-run scraper?") when a data staleness condition is detected, and that suggestion follows the same approve/reject flow.
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md — Coordinator core modules: approval state machine, intent parser, proactive suggestions (pure Python + tests)
- [x] 05-02-PLAN.md — UI integration: action cards, approve/reject buttons, proactive injection into Command Center

### Phase 6: Agent Tool Wrappers and Result Bus
**Goal**: Approved actions dispatch to real SmartMatch services running in background threads, results return to the Command Center without blocking the Streamlit script thread, and all 392 existing tests still pass with zero signature changes to existing functions.
**Depends on**: Phase 5
**Requirements**: ORCH-01, ORCH-02, ORCH-03, POC-01, POC-02
**Success Criteria** (what must be TRUE):
  1. Coordinator can approve a "run discovery scraper" action and see real scraped events appear in the Command Center result panel after the background thread completes.
  2. Coordinator can approve a "rank speakers for event X" action and see real match scores returned from the existing SmartMatch ranking service.
  3. Two agent tasks dispatched at the same time execute in parallel and report independent status (idle/running/awaiting/complete) without corrupting each other's results.
  4. Coordinator can open a POC contacts view, see the full communication history for a contact, and read which contacts are overdue for follow-up.
  5. `pytest tests/ -x` passes with zero failures after every new tool wrapper is added.
**Plans**: 2 plans

Plans:
- [x] 06-01-PLAN.md — Tool wrappers (discovery, matching, outreach, contacts), TOOL_REGISTRY, result bus, POC seed data, and all tests
- [x] 06-02-PLAN.md — Wire real dispatch into Command Center UI: polling fragment, result formatting, POC contact display

### Phase 7: NemoClaw Lead Agent and Live Dashboard
**Goal**: Coordinator experiences the full end-to-end demo: voice command → Jarvis intent → approve → NemoClaw dispatches parallel sub-agents → live per-agent status updates appear in the Command Center → Jarvis speaks the summary result — with a direct-dispatch fallback that activates automatically if NemoClaw is unavailable.
**Depends on**: Phase 6
**Requirements**: DASH-01, DASH-02, DASH-03, POC-03
**Success Criteria** (what must be TRUE):
  1. Command Center shows a per-agent swimlane card for each dispatched sub-agent, with status cycling from idle through running to complete or failed in real-time as agents execute.
  2. Dashboard updates visibly (within 2 seconds) when any agent changes state — no manual page refresh required.
  3. Command Center is accessible as a distinct tab in the existing Streamlit app alongside the current Discovery, Matches, and Outreach tabs.
  4. Jarvis surfaces overdue POC follow-up contacts as proactive action suggestions in the Command Center, gated by the same approve/reject HITL flow.
**Plans**: 2 plans

Plans:
- [ ] 07-01-PLAN.md — NemoClaw adapter, swimlane dashboard module, overdue contacts suggestion, multi-step intent, session state extension, CSS rules, and all tests
- [ ] 07-02-PLAN.md — Wire all Phase 7 modules into Command Center: swimlane polling, TTS on completion, demo hints, overdue contacts injection, multi-step dispatch, and integration tests

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Runtime Fixes and Clean Outputs | 3/3 | Complete | 2026-03-20 |
| 2. Documentation and Governance Reconciliation | 2/2 | Complete | 2026-03-20 |
| 3. Adversarial Audit and Sprint Closure | 3/3 | Complete | 2026-03-21 |
| 4. Voice I/O Foundation | 2/3 | In Progress|  |
| 5. Coordinator Core and HITL Approval Gate | 2/2 | Complete   | 2026-03-24 |
| 6. Agent Tool Wrappers and Result Bus | 2/2 | Complete   | 2026-03-24 |
| 7. NemoClaw Lead Agent and Live Dashboard | 0/2 | Not started | - |
