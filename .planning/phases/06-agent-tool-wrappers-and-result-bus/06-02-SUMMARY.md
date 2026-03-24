---
phase: 06-agent-tool-wrappers-and-result-bus
plan: "02"
subsystem: ui/command_center + runtime_state
tags: [dispatch, result-bus, polling, tdd, poc-contacts, streamlit]
dependency_graph:
  requires:
    - "06-01: TOOL_REGISTRY and result_bus.dispatch/poll_results"
    - "05-02: ActionProposal state machine and _render_action_card shell"
    - "src/coordinator/tools/__init__.py: TOOL_REGISTRY"
    - "src/coordinator/result_bus.py: dispatch(), poll_results()"
  provides:
    - "Real tool dispatch wiring in Command Center Approve button"
    - "@st.fragment(run_every=2) polling for non-blocking result delivery"
    - "_format_result() human-readable result formatter"
    - "_render_contacts_result() POC contact cards with overdue highlighting"
    - "result_queues and poc_contacts session state keys in runtime_state.py"
  affects:
    - "Command Center UI: Approve now dispatches real SmartMatch services"
tech_stack:
  added: []
  patterns:
    - "Background dispatch via TOOL_REGISTRY + result_bus.dispatch()"
    - "@st.fragment(run_every=2) polling loop for non-blocking result delivery"
    - "Fallback stub_execute() for unknown intents"
key_files:
  created: []
  modified:
    - "Category 3 - IA West Smart Match CRM/src/ui/command_center.py"
    - "Category 3 - IA West Smart Match CRM/src/runtime_state.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_command_center.py"
decisions:
  - "st.button.side_effect used in dispatch tests to differentiate approve vs reject button clicks within same card render"
  - "proposal.status set to 'executing' before dispatch() call so UI shows spinner immediately without waiting for thread"
  - "_render_contacts_result calls contacts_tool.run() directly to get structured data for display (not from proposal.result string)"
metrics:
  duration: "~6 minutes"
  completed: "2026-03-24"
  tasks: 2
  files: 3
---

# Phase 06 Plan 02: Command Center UI Wiring Summary

**One-liner:** Real TOOL_REGISTRY dispatch wiring + @st.fragment polling loop replaces stub_execute() in Command Center, with POC contact cards and overdue highlighting for check_contacts actions.

## Tasks Completed

| # | Name | Commit | Files |
|---|------|--------|-------|
| 1 | Wire real dispatch into command_center.py and extend runtime_state.py | 7af77ef | 2 modified |
| 2 | Update command center tests and run full regression | 1ad5a75 | 1 modified |

## What Was Built

### command_center.py — Real Dispatch Wiring

**Import additions:** `TOOL_REGISTRY` from `src.coordinator.tools` and `dispatch, poll_results` from `src.coordinator.result_bus` added at module top.

**Approve button handler:** Replaced `proposal.stub_execute()` with TOOL_REGISTRY lookup. Known intents set `proposal.status = "executing"` then call `dispatch(proposal.id, tool_fn, proposal.params)`. Unknown intents fall back to `stub_execute()` unchanged.

**`_poll_result_bus()`:** `@st.fragment(run_every=2)` function called at the top of `render_command_center_tab()`. Drains `poll_results()` results, updates `proposal.status` and `proposal.result` for completed/failed payloads.

**`_format_result()`:** Converts tool result dicts to human-readable strings. Handles events, rankings, email, contacts, and error keys.

**`_render_contacts_result()`:** Called after `st.success()` when `proposal.intent == "check_contacts"` and status is completed. Calls `contacts_tool.run({})` for structured data, renders expandable contact cards with OVERDUE badge and expanded=True for overdue contacts.

**Failed status display:** Added `elif proposal.status == "failed": st.error(f"Failed: {proposal.result}")` after the executing branch.

### runtime_state.py — New Session State Keys

Added two guards in `init_runtime_state()`:
- `result_queues`: empty dict — used by `result_bus.dispatch()` to store per-proposal queues
- `poc_contacts`: empty list — available for future POC contact caching

### test_command_center.py — New Test Coverage

9 new tests across 3 new classes:
- **TestDispatchWiring** (2 tests): approve dispatches real tool, unknown intent uses stub
- **TestFormatResult** (5 tests): events, rankings, contacts, email, error formatting
- **TestPollResultBus** (2 tests): completed result updates proposal, failed result sets failed status

## Test Results

- **New tests added:** 9
- **All 9 new tests pass**
- **Full suite:** 528 passed, 2 pre-existing failures (e2e requires live server; embeddings requires real Gemini API key)
- **Total collected:** 539 tests

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] st.button mock returns same value for all buttons in card**
- **Found during:** Task 2
- **Issue:** Setting `st.button.return_value = True` caused both Approve and Reject buttons to fire, making `proposal.reject()` raise ValueError on a proposal already in "executing" state
- **Fix:** Used `st.button.side_effect` to return True only for the approve button key (`key == f"approve_{p.id}"`), False for reject
- **Files modified:** `tests/test_command_center.py`
- **Commit:** 1ad5a75

## Known Stubs

None. All wiring delegates to real TOOL_REGISTRY callables and result_bus threading. No placeholder return values.

## Self-Check: PASSED

- `src/ui/command_center.py` contains `from src.coordinator.tools import TOOL_REGISTRY` — FOUND
- `src/ui/command_center.py` contains `from src.coordinator.result_bus import dispatch, poll_results` — FOUND
- `src/ui/command_center.py` contains `dispatch(proposal.id, tool_fn, proposal.params)` — FOUND
- `src/ui/command_center.py` contains `@st.fragment(run_every=2)` — FOUND
- `src/ui/command_center.py` contains `def _format_result(` — FOUND
- `src/ui/command_center.py` contains `def _render_contacts_result(` — FOUND
- `src/ui/command_center.py` contains `proposal.status == "failed"` — FOUND
- `src/ui/command_center.py` contains `proposal.stub_execute()` in else branch — FOUND
- `src/runtime_state.py` contains `result_queues` and `poc_contacts` — FOUND
- Commit 7af77ef — FOUND
- Commit 1ad5a75 — FOUND
