# Sprint 5 Code Review

**Date:** 2026-03-21  
**Branch:** `sprint5-cat3`  
**Scope:** Sprint 5 closeout delta after Phase 2 documentation/governance reconciliation

## Baseline

- Preserve the local Discovery rerender fix already present in `src/ui/discovery_tab.py` and `tests/test_discovery_tab.py`.
- Keep Sprint 5 limited to contract fixes, regression coverage, truthful closeout docs, and a scoped final commit.

## Accepted Findings

| Severity | Area | Finding | Status |
|----------|------|---------|--------|
| High | Discovery -> Matches | Discovered events never got an event embedding or equivalent topic-relevance fallback, so topic relevance silently dropped to `0.0` | Accepted |
| High | Discovery identity | Discovered events had no stable `event_id` or dedupe contract, so duplicate clicks and same-named events could collapse onto the wrong row or feedback entry | Accepted |
| Medium | Matching geography | Discovered events used the university name in `Host / Unit`, but matching treated that field as geographic region for proximity scoring | Accepted |
| Medium | Volunteer Dashboard | Dashboard totals still used `datasets.events` instead of the merged events frame, undercounting discovered-event availability and utilization | Accepted |

## Remediation Scope

Phase 3 fixes the accepted findings by:

1. normalizing discovered events into a stable contract with `event_id`, dedupe behavior, event-region metadata, and fallback topic scoring text;
2. selecting and persisting event identity by `event_id` instead of display name where duplicates can exist;
3. routing the merged events frame into Matches and Volunteer Dashboard views; and
4. rerunning targeted tests, the full suite, and `scripts/sprint4_preflight.py` before doc closure.

## Out of Scope

- broad module refactors
- new product capabilities
- demo-machine-only cache warming steps that still require `GEMINI_API_KEY`

## Verification Reference

- Targeted regressions after the fix pass: `87 passed in 6.56s`
- Full regression baseline after the fix pass: `392 passed in 11.93s`
- `scripts/sprint4_preflight.py`: passes with the same expected cache warnings for un-warmed live artifacts
