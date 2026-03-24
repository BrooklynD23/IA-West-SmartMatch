---
phase: 07-nemoclaw-lead-agent-and-live-dashboard
plan: "01"
subsystem: ui, api

tags: [nemoclaw, openclaw-sdk, swimlane, streamlit, session-state, proactive-suggestions, intent-parser, dispatch]

requires:
  - phase: 06-agent-tool-wrappers-and-result-bus
    provides: "result_bus.dispatch() callable, TOOL_REGISTRY, poc_contacts session state"

provides:
  - "NemoClaw adapter with graceful degradation (NEMOCLAW_AVAILABLE flag + USE_NEMOCLAW env var check)"
  - "dispatch_parallel() that routes to NemoClaw or falls back to result_bus.dispatch() serially"
  - "check_overdue_contacts() proactive suggestion returning ActionProposal with formatted message"
  - "prepare_campaign multi-step intent with MULTI_STEP_INTENTS mapping to 3 sub-intents"
  - "render_swimlane_dashboard() rendering horizontal status cards from agent_swimlanes session state"
  - "_update_swimlane() for creating/updating swimlane entries with started_at preservation"
  - "agent_swimlanes initialized in init_runtime_state()"
  - "Swimlane CSS rules in styles.py (.swimlane-card, .swimlane-compact, status variants)"

affects:
  - 07-02-command-center-ui-wiring
  - future-phases

tech-stack:
  added: []
  patterns:
    - "Graceful degradation via module-level try/except for optional SDK imports"
    - "Lazy import of streamlit inside async functions to preserve testability"
    - "Swimlane state keyed by proposal_id in st.session_state['agent_swimlanes']"
    - "started_at preserved across updates (set-once pattern)"
    - "Cap at 8 most-recently-inserted swimlane entries via list slicing"

key-files:
  created:
    - "Category 3 - IA West Smart Match CRM/src/coordinator/nemoclaw_adapter.py"
    - "Category 3 - IA West Smart Match CRM/src/ui/swimlane_dashboard.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_nemoclaw_adapter.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_swimlane_dashboard.py"
  modified:
    - "Category 3 - IA West Smart Match CRM/src/coordinator/suggestions.py"
    - "Category 3 - IA West Smart Match CRM/src/coordinator/intent_parser.py"
    - "Category 3 - IA West Smart Match CRM/src/runtime_state.py"
    - "Category 3 - IA West Smart Match CRM/src/ui/styles.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_suggestions.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_intent_parser.py"

key-decisions:
  - "NemoClaw adapter uses module-level try/except so NEMOCLAW_AVAILABLE is set at import time, making tests able to control it via sys.modules manipulation"
  - "Lazy import of streamlit inside _nemo_batch() preserves the pure-Python test contract for the adapter module"
  - "swimlane-compact class triggers after 30s for completed entries, reducing visual noise in long-running sessions"
  - "dispatch_parallel() fallback path is serial (not parallel) to guarantee result_bus queue semantics are preserved"

patterns-established:
  - "Graceful SDK degradation: NEMOCLAW_AVAILABLE = False on ImportError, checked at runtime alongside env var"
  - "Session state set-once pattern: if 'key' not in entry: entry['key'] = value"
  - "Proactive suggestions return list[ActionProposal] with source='proactive'"

requirements-completed: [DASH-01, DASH-02, POC-03]

duration: 5min
completed: 2026-03-24
---

# Phase 7 Plan 01: NemoClaw Backend Modules Summary

**NemoClaw adapter with USE_NEMOCLAW graceful degradation, swimlane dashboard rendering from session state, overdue-contact proactive proposals, and prepare_campaign multi-step intent — all backed by 48 passing tests**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-24T19:45:55Z
- **Completed:** 2026-03-24T19:51:00Z
- **Tasks:** 2
- **Files modified:** 10 (4 created, 6 modified)

## Accomplishments

- NemoClaw adapter (`nemoclaw_adapter.py`) built with `NEMOCLAW_AVAILABLE` flag, env-var check, serial fallback path, and async NemoClaw batch path in daemon thread
- Swimlane dashboard (`swimlane_dashboard.py`) renders horizontal status cards from `agent_swimlanes` session state, caps at 8, compacts after 30s, and includes Retry button on failed cards
- `check_overdue_contacts()` added to suggestions.py: returns proactive `ActionProposal` with count, first-3-names truncation, and "review now?" message format
- `prepare_campaign` intent registered in `SUPPORTED_INTENTS`, `ACTION_REGISTRY`, and new `MULTI_STEP_INTENTS` constant mapping to 3 sub-intents
- `agent_swimlanes` state key initialized in `init_runtime_state()`
- Swimlane CSS rules appended to `styles.py` (`.swimlane-card`, status-variant borders, `.swimlane-compact`)
- All 48 tests pass across 4 test files; full suite shows 556 passed (no regressions)

## Task Commits

Each task was committed atomically:

1. **Task 1: NemoClaw adapter, overdue contacts suggestion, multi-step intent, and all tests** - `1243562` (feat)
2. **Task 2: Swimlane dashboard module, session state extension, CSS rules, and tests** - `6f26b09` (feat)

## Files Created/Modified

- `src/coordinator/nemoclaw_adapter.py` - NemoClaw parallel dispatch with graceful degradation to result_bus.dispatch()
- `src/ui/swimlane_dashboard.py` - Swimlane card rendering from agent_swimlanes session state
- `src/coordinator/suggestions.py` - Extended with check_overdue_contacts() proactive suggestion function
- `src/coordinator/intent_parser.py` - Extended with prepare_campaign intent, MULTI_STEP_INTENTS constant, and system prompt update
- `src/runtime_state.py` - Added agent_swimlanes initialization guard
- `src/ui/styles.py` - Added swimlane CSS rules (.swimlane-card, .swimlane-compact, status variants)
- `tests/test_nemoclaw_adapter.py` - 4 tests for NemoClaw availability and fallback dispatch paths
- `tests/test_swimlane_dashboard.py` - 12 tests for rendering, CSS mapping, compact logic, and _update_swimlane
- `tests/test_suggestions.py` - Extended with TestOverdueContacts (8 tests)
- `tests/test_intent_parser.py` - Extended with TestPrepareIntent (4 tests)

## Decisions Made

- NemoClaw adapter uses module-level try/except so `NEMOCLAW_AVAILABLE` is determined at import time; tests control it via `sys.modules` manipulation and direct attribute patching
- Lazy import of streamlit inside `_nemo_batch()` preserves the pure-Python test contract established in earlier phases
- `dispatch_parallel()` fallback path is serial rather than parallel to maintain result_bus queue semantics
- `swimlane-compact` renders after 30s for completed entries to reduce noise in long-running demo sessions

## Deviations from Plan

None - all source files and tests were already in place from prior work in this sprint. Plan execution verified existing implementations against acceptance criteria, ran all tests to confirm correctness, and committed uncommitted Task 2 files that were present but untracked.

## Issues Encountered

None - pre-existing E2E and embeddings API test failures (11 total) are known pre-existing conditions unrelated to this plan's changes.

## User Setup Required

None - no external service configuration required for these backend modules. NemoClaw path requires `USE_NEMOCLAW=1` and `openclaw-sdk` installed; fallback is automatic without configuration.

## Known Stubs

None - all functions are fully implemented and tested. NemoClaw path contains real async dispatch logic (not a stub); the fallback is an intentional design choice, not a stub.

## Next Phase Readiness

- All backend contracts for Phase 7 are established and tested
- `render_swimlane_dashboard()` and `_update_swimlane()` are ready for Plan 02 Command Center wiring
- `dispatch_parallel()` is ready to replace direct `result_bus.dispatch()` calls in the Command Center
- `check_overdue_contacts()` is ready to be called in the proactive suggestions polling loop
- `MULTI_STEP_INTENTS` is ready for use in the intent routing logic

---
*Phase: 07-nemoclaw-lead-agent-and-live-dashboard*
*Completed: 2026-03-24*
