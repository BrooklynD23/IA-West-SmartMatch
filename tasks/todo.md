# Todo

## Current Work

### Sprint 4 Review Fix Pass

- [x] Fix the Sprint 4 review findings without expanding product scope.
- [x] Make `scripts/sprint4_preflight.py --prewarm-discovery` actually warm the caches it claims to warm.
- [x] Reconcile the deployment/runtime contract with Sprint 4 docs and make preflight validate content, not just file presence.
- [x] Harden discovery and extraction cache reads so corrupt or malformed cache files degrade safely instead of crashing.
- [x] Add regression tests for each fixed review finding and rerun targeted verification.

### Sprint 4 Autonomous Orchestration

#### Requirements Restatement

- Execute Sprint 4 for Category 3 from the reviewed sprint docs, using `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` and `Category 3 - IA West Smart Match CRM/docs/sprints/sprint-4-ship.md` as the implementation authority.
- Work on the new git branch `sprint4-cat3`.
- Orchestrate with subagents and keep progress visible in this file.
- Treat Sprint 4 as ship-hardening only: testing, bug fixing, performance, deployment readiness, demo readiness, cache/demo-mode readiness, and final cleanup.
- Verify every code change with direct evidence before marking it complete.

#### Risks

- High: Sprint 4 explicitly forbids new feature work, so fixes must stay inside existing product contracts.
- High: Demo-mode, cache, and fallback paths can pass unit tests while still failing in the real demo flow.
- High: Deployment and performance work may expose environment-specific bugs not covered by the current local suite.
- Medium: The repo already has unrelated dirty files; avoid reverting or entangling them.
- Medium: Some Sprint 4 items are human-only operational tasks and must be separated from code-completable work.

#### Execution Board

- [x] Phase 1: Establish Sprint 4 execution context.
  - Create and switch to branch `sprint4-cat3`.
  - Reconcile current repo state, Sprint 4 authority docs, and Category 3 status.
  - Rewrite this task board for Sprint 4 orchestration.

- [ ] Phase 2: Audit Sprint 4 gaps with subagents.
- [x] Phase 2: Audit Sprint 4 gaps with subagents.
  - Compare current code/test/docs state against A4.1-A4.10 requirements.
  - Identify missing automation, weak fallback paths, deployment gaps, and verification gaps.
  - Turn findings into a prioritized implementation backlog.

- [x] Phase 3: Close code and test gaps.
  - Implement only Sprint 4 bug-fix, hardening, performance, deployment, and cleanup work.
  - Add or tighten tests where the current suite misses Sprint 4 acceptance criteria.
  - Keep fixes minimal and aligned with the existing runtime contracts.

- [x] Phase 4: Produce Sprint 4 operational artifacts.
  - Create testing/rehearsal/day-of prep artifacts that can be committed now.
  - Separate automated evidence from human-only rehearsal/video tasks.
  - Record any items that still require manual execution by the team.

- [x] Phase 5: Verify and close out.
  - Run targeted verification for all touched areas.
  - Run the full relevant regression suite if feasible in the project environment.
  - Update this review section with evidence, residual risks, and next manual steps.

#### Execution Guidance For Worker

- Start with the delta between Sprint 4 acceptance criteria and the current checked-in behavior.
- Prefer fixes that improve the real demo path and Demo Mode together instead of maintaining separate logic branches.
- Do not invent new UX or product scope under the banner of polish.
- If a Sprint 4 requirement is human-only, document it cleanly rather than faking completion in code.

## Review

- Status: Sprint 4 CLOSED for engineering scope (code + committed artifacts)
- Notes: Created `sprint4-cat3`, hardened discovery for stale-cache fallback and cache-first status visibility, made cache paths repo-stable for root/subdir execution, blocked all-zero match-weight runs, added file-specific empty-dataset errors, aligned the demo funnel fixture to the 6-stage runtime contract, added `runtime.txt`, and committed Sprint 4 testing/rehearsal templates plus `scripts/sprint4_preflight.py`.
- Review fix pass: `scripts/sprint4_preflight.py --prewarm-discovery` now persists extraction caches, `runtime.txt` and preflight now match the Sprint 4 Streamlit Cloud contract, scrape/extraction cache loaders degrade safely on corrupt payloads, and regression coverage was added for those cases.
- Verification:
  - `git checkout -b sprint4-cat3` -> branch created from `sprint3-cat3`
  - `./.venv/bin/python -m pytest tests/test_scraper.py tests/test_llm_extractor.py tests/test_matches_tab.py tests/test_app.py -q` -> 47 passed
  - `./.venv/bin/python -m pytest tests/test_demo_mode.py tests/test_pipeline_tab.py -q` -> 47 passed
  - `./.venv/bin/python -m pytest -q` -> 373 passed
  - `./.venv/bin/python scripts/sprint4_preflight.py` -> passes with warnings only for missing live-warmed caches (`cache/scrapes`, embedding cache, `cache/explanations`, `cache/emails`)
  - `Category 3 - IA West Smart Match CRM/.venv/bin/python -m pytest 'Category 3 - IA West Smart Match CRM/tests/test_demo_mode.py' -q` from repo root -> 27 passed
  - `./.venv/bin/python -m pytest tests/test_scraper.py tests/test_llm_extractor.py tests/test_sprint4_preflight.py -q` -> 45 passed
  - `./.venv/bin/python -m pytest tests/test_app.py tests/test_scraper.py tests/test_llm_extractor.py tests/test_matches_tab.py tests/test_pipeline_tab.py tests/test_discovery_tab.py tests/test_sprint4_preflight.py -q` -> 81 passed
- Follow-ups:
  - Run `./.venv/bin/python scripts/sprint4_preflight.py --prewarm-discovery` on the actual demo machine with `GEMINI_API_KEY` configured to warm live scrape and extraction caches.
  - Generate real embedding, explanation, and email caches on the demo machine before rehearsal and day-of use.
  - Complete the human-only Sprint 4 items in `docs/testing/rehearsal_log.md`, `docs/testing/test_log.md`, and `docs/testing/bug_log.md`.
  - Manual gaps still remaining: true copy-to-clipboard confirmation in the email UI, full browser-level E2E rehearsal automation, Streamlit Cloud deployment verification, and backup video recording.

## Sprint 4 Closure

- Closed on branch `sprint4-cat3` after Sprint 4 hardening implementation plus review-fix pass.
- Closure scope: repository code, tests, deployment/runtime wiring, and Sprint 4 operational scaffolding templates.
- Remaining items are explicitly manual/demo-operations tasks and are tracked in `Category 3 - IA West Smart Match CRM/docs/testing/`.
