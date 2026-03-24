# Requirements: IA West SmartMatch CRM

**Defined:** 2026-03-20
**Updated:** 2026-03-23 (v2.0 Jarvis Agent Coordinator — traceability updated after roadmap)
**Core Value:** A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach — with human approval gating every action.

## v1 Requirements (Sprint 5 Closeout — Complete)

### Runtime Reliability

- [x] **FLOW-01**: Operator can add a discovered event into the active match pool and see it in the Matches tab during the same session.
- [x] **FLOW-02**: Discovery-to-matching handoff is protected by automated regression coverage that fails when session-state integration breaks.
- [x] **DEMO-01**: Operator can render the core matching flow in Demo Mode or cache-only mode on a clean checkout without requiring live Gemini calls.
- [x] **PATH-01**: Feedback and generated artifact persistence resolve from project-root configuration instead of the current working directory.

### Closeout Evidence

- [x] **GOV-01**: Category 3 status docs, sprint docs, and the task board report one live verification baseline for the current closeout state.
- [x] **OPS-01**: Generated rehearsal/runtime artifacts are ignored or isolated so they do not appear as product-source changes during Sprint 5.
- [x] **DOC-01**: Closeout documentation states the real remaining manual steps and current preflight or demo readiness without stale or contradictory claims.

### Final Audit

- [x] **REV-01**: Sprint 5 changes undergo an `$ecc-code-review` audit and every accepted finding is fixed or explicitly documented before closure.
- [x] **REV-02**: Sprint 5 closes with direct verification evidence recorded in planning or task docs and preserved in commit history.

## v2 Requirements (Jarvis Agent Coordinator)

### Voice I/O

- [x] **VOICE-01**: Coordinator can type text commands in a Command Center tab and receive parsed intent responses
- [x] **VOICE-02**: Coordinator can hear Jarvis speak responses via KittenTTS voice synthesis
- [x] **VOICE-03**: Coordinator can use push-to-talk to speak commands, transcribed via faster-whisper STT
- [x] **VOICE-04**: Coordinator can see full conversation history (voice + text) in the Command Center

### Agent Orchestration

- [x] **ORCH-01**: Existing SmartMatch discovery, matching, and outreach functions are wrapped as agent-callable tool services
- [x] **ORCH-02**: NemoClaw/OpenClaw dispatches sub-agents for webscraping, matching, and outreach tasks
- [x] **ORCH-03**: Sub-agents can run in parallel with independent status tracking
- [x] **ORCH-04**: Jarvis proactively suggests actions when data is stale or follow-ups are overdue

### Human-in-the-Loop

- [x] **HITL-01**: Every agent action displays a proposed action card with agent name, action description, and reasoning
- [x] **HITL-02**: Coordinator can approve, reject, or edit parameters on any proposed action before execution
- [x] **HITL-03**: No agent action executes without explicit coordinator approval

### Dashboard

- [x] **DASH-01**: Visual command center shows per-agent swimlane cards with idle/running/awaiting/complete status
- [x] **DASH-02**: Dashboard updates in real-time as agents dispatch, execute, and return results
- [ ] **DASH-03**: Command center integrates into existing Streamlit app as a new tab

### Contact Management

- [x] **POC-01**: Coordinator can view and manage POC contacts with communication history
- [x] **POC-02**: Coordinator can track follow-up reminders and see overdue contacts
- [x] **POC-03**: Jarvis surfaces POC follow-up status as part of proactive suggestions

## Future Requirements

### Deferred from v1

- **E2E-01**: Add a browser-driven end-to-end suite that exercises the full Streamlit demo path.
- **PAR-01**: Add automated Python 3.11 deployment-parity verification for the Streamlit Cloud runtime.
- **ARCH-01**: Break up late-stage hotspot modules into smaller units after closeout pressure is gone.

### Deferred from v2

- **VOICE-05**: Real-time streaming transcription during speech (requires VAD + streaming Whisper)
- **VOICE-06**: Wake word activation ("Hey Jarvis") for hands-free operation
- **ORCH-05**: Agent self-modification or dynamic tool creation
- **DASH-04**: Mobile-responsive command center layout

## Out of Scope

| Feature | Reason |
|---------|--------|
| Fully autonomous agent execution | Hard constraint — all actions gate on coordinator approval |
| Custom TTS voice training | KittenTTS built-in voices sufficient for demo |
| Always-on microphone listening | Unreliable in demo environments; push-to-talk instead |
| Production auth / multi-tenant | Demo-focused hackathon scope |
| Mobile / native app | Streamlit web is the demo surface |
| Agent self-modification | High risk, contradicts HITL constraint |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FLOW-01 | Phase 1 (v1) | Complete |
| FLOW-02 | Phase 1 (v1) | Complete |
| DEMO-01 | Phase 1 (v1) | Complete |
| PATH-01 | Phase 1 (v1) | Complete |
| GOV-01 | Phase 2 (v1) | Complete |
| OPS-01 | Phase 1 (v1) | Complete |
| DOC-01 | Phase 2 (v1) | Complete |
| REV-01 | Phase 3 (v1) | Complete |
| REV-02 | Phase 3 (v1) | Complete |
| VOICE-01 | Phase 4 | Complete |
| VOICE-02 | Phase 4 | Complete |
| VOICE-03 | Phase 4 | Complete |
| VOICE-04 | Phase 4 | Complete |
| HITL-01 | Phase 5 | Complete |
| HITL-02 | Phase 5 | Complete |
| HITL-03 | Phase 5 | Complete |
| ORCH-04 | Phase 5 | Complete |
| ORCH-01 | Phase 6 | Complete |
| ORCH-02 | Phase 6 | Complete |
| ORCH-03 | Phase 6 | Complete |
| POC-01 | Phase 6 | Complete |
| POC-02 | Phase 6 | Complete |
| DASH-01 | Phase 7 | Complete |
| DASH-02 | Phase 7 | Complete |
| DASH-03 | Phase 7 | Pending |
| POC-03 | Phase 7 | Complete |

**Coverage:**
- v1 requirements: 9 total (9 complete)
- v2 requirements: 16 total
- Mapped to phases: 16 (100% coverage)
- Unmapped: 0

---
*Requirements defined: 2026-03-20*
*Last updated: 2026-03-23 after v2.0 roadmap phase mapping*
