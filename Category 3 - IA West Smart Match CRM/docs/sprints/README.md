# Category 3 Sprint Specs

## Canonical Sprint Specs

- `sprint-0-foundation.md`
- `sprint-1-matching-core.md`
- `sprint-2-discovery-email.md`
- `sprint-3-polish-freeze.md`
- `sprint-4-ship.md`

These five files are the current implementation specs for the Category 3 build. They are derived from:

- `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`
- `PRD_SECTION_CAT3.md`
- `archived/general_project_docs/MASTER_SPRINT_PLAN.md`
- `archived/general_project_docs/STRATEGIC_REVIEW.md`

## Review History

- `REVIEW_HANDOFF.md`
  Reviewer prompt. Use for audit/re-review only.
- `SPRINT_SPEC_ADVERSARIAL_REVIEW_2026-03-17.md`
  Historical review report against the pre-reconciliation sprint draft.

## Fast Checks Before Implementing

- Read `../README.md` first.
- Do not treat `PLAN.md` as execution authority.
- Expect flat embedding files in `cache/`, hashed scrape files in `cache/scrapes/`, and hashed email files in `cache/emails/`.
- Expect live cross-tab runtime state in `st.session_state`, not on `LoadedDatasets`.

## Sprint 5 Closeout Baseline

- Sprint 3 integration audit and Sprint 4 hardening are already reflected in the checked-in runtime; Sprint 5 closeout engineering work is now complete on `sprint5-cat3`.
- Current verification baseline: `./.venv/bin/python -m pytest -q` -> `392 passed in 11.93s`.
- Current targeted Phase 3 regression baseline: `87 passed in 6.56s`.
- Current preflight baseline: `./.venv/bin/python scripts/sprint4_preflight.py` passes with warnings only for un-warmed live caches (embedding artifacts plus scrape, extraction, explanation, and email caches).
- Current review artifact: `Category 3 - IA West Smart Match CRM/docs/reviews/2026-03-21-sprint5-code-review.md`.
- Current manual/demo-day follow-ups remain: warm live caches on the demo machine, verify the real rehearsal path, and complete the human-run testing logs under `docs/testing/`.
