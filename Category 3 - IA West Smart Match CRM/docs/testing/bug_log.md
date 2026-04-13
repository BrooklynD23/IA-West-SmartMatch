# SmartMatch Bug Tracker

## Active Bugs

| ID | Severity | Title | Status | Assigned | Fix Commit | Verified |
|----|----------|-------|--------|----------|------------|----------|
| *(none)* | - | - | - | - | - | - |

## Resolved Bugs

| ID | Severity | Title | Fix Commit | Verified By | Regression Passed |
|----|----------|-------|------------|-------------|-------------------|
| B-006 | P0 | Vercel read-only FS: QR manifest.json write fails (`[Errno 30]`) | pre-investor-fixes | Danny | `test_api_calendar.py` |
| B-007 | P0 | Vercel read-only FS: pipeline_sample_data.csv write fails (`[Errno 30]`) | pre-investor-fixes | Danny | manual Vercel deploy |
| B-008 | P1 | Opportunities "Find Best Matches" top button navigates without event pre-selection | pre-investor-fixes | Danny | `docs/audit-pre-demo-1.0.md` |
| B-009 | P1 | University contacts missing from Outreach recipient dropdown | pre-investor-fixes | Danny | `GET /api/data/university-contacts` |
| B-010 | P2 | Fatigue label reads "On Cooldown" — should be "Rest Recommended" | pre-investor-fixes | Danny | grep confirms zero remaining occurrences in code |

## Fix Session Log

| Session | Date | Duration | Bugs Fixed | Bugs Remaining (P0/P1/P2/P3) |
|---------|------|----------|------------|-------------------------------|
| Session 1 | 2026-03-20 | Sprint 4 hardening pass | 0 (new) | 0/0/0/0 |
| Session 2 | 2026-04-13 | Pre-investor 5-fix pass | 5 (B-006–B-010) | 0/0/0/0 |
