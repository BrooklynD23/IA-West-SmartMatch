---
phase: 05-coordinator-core-and-hitl-approval-gate
plan: "01"
subsystem: coordinator
tags: [hitl, state-machine, intent-parser, gemini, tdd, pure-python]
dependency_graph:
  requires: []
  provides:
    - src/coordinator/approval.py (ActionProposal, ProposalStatus)
    - src/coordinator/intent_parser.py (ParsedIntent, parse_intent, SUPPORTED_INTENTS, ACTION_REGISTRY)
    - src/coordinator/suggestions.py (check_staleness_conditions, STALENESS_HOURS)
  affects:
    - Phase 05 Plan 02 (UI integration of HITL approval gate)
tech_stack:
  added: []
  patterns:
    - dataclass state machine with guard-clause methods
    - frozen dataclass as immutable DTO
    - pure-function staleness checker returning domain objects
    - mock.patch for unit-testing LLM-backed functions
key_files:
  created:
    - Category 3 - IA West Smart Match CRM/src/coordinator/__init__.py
    - Category 3 - IA West Smart Match CRM/src/coordinator/approval.py
    - Category 3 - IA West Smart Match CRM/src/coordinator/intent_parser.py
    - Category 3 - IA West Smart Match CRM/src/coordinator/suggestions.py
    - Category 3 - IA West Smart Match CRM/tests/test_approval.py
    - Category 3 - IA West Smart Match CRM/tests/test_intent_parser.py
    - Category 3 - IA West Smart Match CRM/tests/test_suggestions.py
  modified: []
decisions:
  - "Used project .venv (Category 3 - IA West Smart Match CRM/.venv) for test runs — system python3 lacks dotenv and other project deps"
  - "ParsedIntent is frozen dataclass (immutable DTO); ActionProposal is mutable dataclass (owns mutable lifecycle state)"
  - "All coordinator modules are pure Python with zero Streamlit imports — testable without mock-streamlit conftest plumbing"
metrics:
  duration: "~4 minutes"
  completed: "2026-03-24"
  tasks_completed: 3
  files_created: 7
  tests_added: 33
---

# Phase 05 Plan 01: Coordinator Core and HITL Approval Gate — Core Modules Summary

**One-liner:** Three pure-Python coordinator modules — ActionProposal state machine, Gemini intent parser with unknown fallback, and proactive staleness suggestion engine — fully TDD'd with 33 tests green.

## What Was Built

Three new modules under `src/coordinator/` forming the pure-Python logic layer for the HITL approval gate:

1. **approval.py** — `ActionProposal` mutable dataclass with a 6-state lifecycle (`proposed → approved → executing → completed/failed/rejected`). Methods `approve()`, `reject()`, and `stub_execute()` enforce valid transitions via guard clauses and raise `ValueError` on invalid ones.

2. **intent_parser.py** — `ParsedIntent` frozen dataclass and `parse_intent()` function that calls `gemini_client.generate_text()` with a structured JSON prompt, strips markdown fences from responses, validates intent against `SUPPORTED_INTENTS`, and falls back gracefully to `intent="unknown"` on any error (GeminiAPIError, JSONDecodeError, KeyError, TypeError).

3. **suggestions.py** — `check_staleness_conditions()` pure function that returns a proactive `ActionProposal` when `scraped_events` is empty or `scraped_at` is older than 24 hours (or None/invalid), and returns an empty list when data is fresh.

## Test Results

```
33 passed in 0.64s
- tests/test_approval.py: 13 tests
- tests/test_intent_parser.py: 10 tests (Gemini mocked via @patch)
- tests/test_suggestions.py: 10 tests
```

No Streamlit imports in any coordinator module.

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1: approval.py | 3e284f3 | ActionProposal state machine with approve/reject/stub_execute |
| Task 2: intent_parser.py | 1370fa9 | Gemini intent parser with ParsedIntent and fallback handling |
| Task 3: suggestions.py | 4fc49dd | Proactive staleness suggestion engine |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Used project .venv instead of system python3**
- **Found during:** Task 2 (test_intent_parser.py)
- **Issue:** System `python3` lacks `dotenv` and other project dependencies; `approval.py` tests passed because they have no `src.config` import, but `intent_parser.py` imports `src.config` which imports `dotenv`.
- **Fix:** Used `.venv/bin/python` (the project's virtual environment) for all test runs from Task 2 onward.
- **Files modified:** None — runtime fix only.

None of the source modules were altered; the deviation was purely in the test invocation command.

## Known Stubs

None. All three modules are complete implementations. `stub_execute()` in `approval.py` is intentionally named "stub" — it is the Phase 5 implementation that transitions to `completed` immediately without real agent dispatch. Phase 6 will replace it with real queue-based dispatch. This is by design per the plan, not a data stub.

## Self-Check

See below.
