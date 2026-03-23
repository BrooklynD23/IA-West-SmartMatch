# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-23)

**Core value:** A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach — with human approval gating every action.
**Current focus:** v2.0 Jarvis Agent Coordinator — Phase 4: Voice I/O Foundation

## Current Position

Phase: 4 — Voice I/O Foundation
Plan: Not started — CONTEXT.md + RESEARCH.md + VALIDATION.md complete, ready for gsd-planner
Status: Ready to plan (run `/gsd:plan-phase 4` to continue)
Last activity: 2026-03-23 — Smart discuss + research + validation strategy complete

```
Progress: [===-------] 3/7 phases complete (v1 done, v2 not started)
```

## Performance Metrics

**Velocity:**
- Total plans completed: 8 (all from v1.0)
- Average duration: not tracked
- Total execution time: not tracked

**By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| 1. Runtime Fixes and Clean Outputs | 3/3 | Complete |
| 2. Documentation and Governance Reconciliation | 2/2 | Complete |
| 3. Adversarial Audit and Sprint Closure | 3/3 | Complete |
| 4. Voice I/O Foundation | 0/TBD | Not started |
| 5. Coordinator Core and HITL Approval Gate | 0/TBD | Not started |
| 6. Agent Tool Wrappers and Result Bus | 0/TBD | Not started |
| 7. NemoClaw Lead Agent and Live Dashboard | 0/TBD | Not started |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- v2.0: Full-duplex voice requires two separate libraries — KittenTTS for TTS output only, faster-whisper for STT input; plans that treat KittenTTS as duplex will produce a deaf Jarvis
- v2.0: Human-in-the-loop approval gates ALL agent actions — approval state machine in `st.session_state`, never a blocking loop
- v2.0: All agent execution runs in background daemon threads via `queue.Queue`; `@st.fragment(run_every=2)` polls for results — never call agent logic in a button callback
- v2.0: Existing `src/` function signatures are NEVER modified — tool wrappers are thin adapters that call existing functions unchanged; 392-test baseline must stay green after every wrapper addition
- v2.0: NemoClaw is 7-day-old alpha (launched 2026-03-16) and supports only Nemotron models, not Gemini; build Phases 4-6 against a direct-dispatch fallback contract so Phase 7 has a working fallback if NemoClaw is unusable on demo day
- v2.0: KittenTTS model must be loaded once at startup into `st.session_state["tts_model"]` — cold start is 3-5s per call if not cached
- v2.0: Coordinator uses Gemini for intent parsing; sub-agents use Nemotron via NemoClaw — these are parallel LLM backends with distinct roles

### Pending Todos

- Validate KittenTTS wheel install (`misaki>=0.9.4` dependency) on demo hardware before Phase 4 begins
- Validate streamlit-webrtc push-to-talk browser mic capture at localhost in development environment
- Confirm NVIDIA NGC API key availability before Phase 7 begins — NemoClaw requires keys from `build.nvidia.com/settings/api-keys`
- Verify openclaw-sdk tool registration API and parallel dispatch syntax against installed version before Phase 6 begins
- Confirm demo presentation environment (localhost vs. projected via network URL) — streamlit-webrtc requires HTTPS for non-localhost mic access; add explicit preflight check
- Warm live discovery and embedding caches on the real demo machine with `GEMINI_API_KEY`
- Run the real-environment rehearsal and complete the human-run logs under `Category 3 - IA West Smart Match CRM/docs/testing/`

### Blockers/Concerns

- The worktree is already dirty outside this milestone — use explicit pathspecs for all commits
- KittenTTS install has reported `misaki>=0.9.4` PyPI dependency failures — must validate wheel install on demo hardware before Phase 4 code begins
- NemoClaw alpha API changes between releases — pin `openclaw-sdk` version in requirements.txt; have asyncio direct-dispatch fallback ready to swap in if NemoClaw fails

## Session Continuity

Last session: 2026-03-23
Stopped at: v2.0 roadmap created — Phase 4 ready to plan
Resume file: None
