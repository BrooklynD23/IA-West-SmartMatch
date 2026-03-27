---
phase: 10-master-calendar-volunteer-recovery
plan: "01"
subsystem: backend
tags: [fastapi, matching, calendar, recovery, fatigue, pytest]
dependency_graph:
  requires: []
  provides: [canonical_volunteer_fatigue_factor, calendar_api_contract, recovery_metadata]
  affects:
    - "Category 3 - IA West Smart Match CRM/src/config.py"
    - "Category 3 - IA West Smart Match CRM/src/matching/factors.py"
    - "Category 3 - IA West Smart Match CRM/src/matching/engine.py"
    - "Category 3 - IA West Smart Match CRM/src/api/main.py"
    - "Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py"
    - "Category 3 - IA West Smart Match CRM/src/api/routers/matching.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_matching.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_calendar.py"
tech_stack:
  added: []
  patterns: [shared recovery-details helper, csv-backed calendar overlay contract, direct route pytest coverage]
key_files:
  created:
    - "Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_calendar.py"
  modified:
    - "Category 3 - IA West Smart Match CRM/src/config.py"
    - "Category 3 - IA West Smart Match CRM/src/matching/factors.py"
    - "Category 3 - IA West Smart Match CRM/src/matching/engine.py"
    - "Category 3 - IA West Smart Match CRM/src/api/main.py"
    - "Category 3 - IA West Smart Match CRM/src/api/routers/matching.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_matching.py"
decisions:
  - "Keep `factor_scores.volunteer_fatigue` as recovery-readiness for positive-weight ranking, and emit the inverse fatigue burden as top-level API metadata for coordinator UI"
  - "Use one shared `volunteer_recovery_details()` helper so matching and calendar overlays expose the same recovery semantics"
  - "Switch focused API tests away from `TestClient` to direct route/helper calls because this environment can hang on the TestClient path"
metrics:
  completed_date: "2026-03-26"
  tasks_completed: 2
  files_changed: 8
---

# Phase 10 Plan 01: Backend Calendar and Recovery Summary

One-liner: promoted volunteer recovery into the canonical matching model and exposed a dedicated `/api/calendar` contract with normalized event coverage and assignment overlay metadata.

## Tasks Completed

| Task | Name | Result |
|------|------|--------|
| 1 | Add canonical volunteer_fatigue scoring support to the matching engine | Completed in worktree |
| 2 | Expose normalized calendar events and assignment overlays through FastAPI | Completed in worktree |

## What Was Built

### Matching and recovery model

- `config.py` now includes `volunteer_fatigue` at default weight `0.10`, with the surrounding defaults rebalanced to keep the registry coherent.
- `factors.py` now exposes `volunteer_recovery_details()` plus the canonical `volunteer_fatigue()` factor.
- `engine.py` now includes `volunteer_fatigue` in both `factor_scores` and `weighted_factor_scores`.
- `matching.py` now emits top-level `volunteer_fatigue`, `recovery_status`, and `recovery_label` so the frontend can show coordinator-facing fatigue and recovery state without inventing its own rules.

### Calendar API

- Added `src/api/routers/calendar.py` and mounted it from `src/api/main.py` at `/api/calendar`.
- `GET /api/calendar/events` now returns normalized scheduling windows with coverage status, coverage ratio, assigned volunteers, and color metadata.
- `GET /api/calendar/assignments` now returns assignment overlays derived from the pipeline rows, including recovery/fatigue metrics, event-region mapping, and coverage metadata.

### Focused test coverage

- `tests/test_api_matching.py` now asserts the presence and effect of `volunteer_fatigue`.
- `tests/test_api_calendar.py` verifies router mounting plus the event and assignment response shapes.
- The focused route tests call the FastAPI functions directly to avoid the environment-specific `TestClient` hang.

## Verification Results

```bash
cd "Category 3 - IA West Smart Match CRM" && timeout 60s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py -q
```

Result:

```text
9 passed, 22 warnings in 9.48s
```

Warnings were non-blocking pandas deprecation warnings from `data_loader.py`.

## Success Criteria Verification

- [x] Matching engine exposes a canonical `volunteer_fatigue` factor and honors its weight
- [x] FastAPI exposes dedicated calendar endpoints for normalized event and assignment data
- [x] Recovery status can be derived from backend responses without React inventing private rules
- [x] Automated tests cover both the new factor and the calendar routes

## Deviations from Plan

- `src/api/routers/matching.py` was also updated so the frontend receives explicit recovery metadata alongside the factor breakdown. This was required to keep the backend and frontend semantics aligned.

## Known Stubs

- The calendar overlay still maps pipeline events onto IA planning-window slots heuristically because the source CSVs do not include a first-class event-to-calendar join key.

## Self-Check

PASSED
