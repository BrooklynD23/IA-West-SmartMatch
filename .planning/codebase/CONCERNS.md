# Codebase Concerns

**Analysis Date:** 2026-03-26

## Tech Debt

**Planning state says shipped while core v3.0 work is still only in the worktree:**
- Issue: `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/MILESTONES.md` mark `v3.0` shipped, but the current implementation still lives in modified and untracked files such as `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`, and `.planning/phases/10-master-calendar-volunteer-recovery/`.
- Files: `.planning/STATE.md`, `.planning/ROADMAP.md`, `.planning/MILESTONES.md`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`
- Impact: milestone closeout documents can be treated as canonical even though the underlying code has not been reduced to a reviewed commit boundary yet.
- Fix approach: either commit and review the Phase 09.1-12 implementation delta, or roll the planning state back from shipped until the code and planning state match.

**Data-path resolution is split between config-aware loaders and hard-coded UI helpers:**
- Issue: `Category 3 - IA West Smart Match CRM/src/config.py` and `Category 3 - IA West Smart Match CRM/src/data_loader.py` honor `DATA_DIR`, but `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py` hard-codes `project_root/data`, and `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, and `Category 3 - IA West Smart Match CRM/src/qr/service.py` depend on that helper.
- Files: `Category 3 - IA West Smart Match CRM/src/config.py`, `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`, `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`
- Impact: non-default data layouts and some tests can read from one directory while QR, feedback, and pipeline mutations write to another.
- Fix approach: make `Category 3 - IA West Smart Match CRM/src/config.py` the only source of truth for mutable data paths and pass those paths into helpers/services explicitly.

**The repo carries two feedback systems with different storage models:**
- Issue: the Streamlit path still uses `Category 3 - IA West Smart Match CRM/src/feedback/acceptance.py` and `data/feedback_log.csv`, while the React/FastAPI path uses `Category 3 - IA West Smart Match CRM/src/feedback/service.py` plus `data/feedback/feedback-log.jsonl` and `data/feedback/weight-history.json`; `Category 3 - IA West Smart Match CRM/src/app.py` still renders the legacy feedback sidebar.
- Files: `Category 3 - IA West Smart Match CRM/src/feedback/acceptance.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/app.py`, `Category 3 - IA West Smart Match CRM/frontend/src/components/FeedbackForm.tsx`
- Impact: match decisions, optimizer snapshots, and dashboard analytics can diverge depending on whether a coordinator uses the Streamlit or React surface.
- Fix approach: pick one canonical feedback service and either migrate the Streamlit sidebar to it or retire the legacy path.

**The calendar API is still a scenario-planning model, not authoritative scheduling data:**
- Issue: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py` fabricates `calendar-xx` IDs from `data_event_calendar.csv`, assigns events to slots with `_stable_slot_index()`, and hard-codes `open_slots` against a target of three volunteers per event.
- Files: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`
- Impact: the React calendar and recovery views look authoritative but are still derived from a deterministic sample model instead of persisted event assignments.
- Fix approach: persist real event-to-slot assignments, or explicitly label the current API as planning data and keep it separate from operational scheduling.

**Frontend contract handling is concentrated in one large normalization file:**
- Issue: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts` has grown to roughly 1,100 lines and mixes request helpers, type definitions, normalization, fallback behavior, and empty-state defaults for every backend domain.
- Files: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`
- Impact: backend contract changes are expensive to reason about, easy to mask, and difficult to test in isolation.
- Fix approach: split API clients by domain (`matching`, `calendar`, `qr`, `feedback`, `outreach`) and keep normalization close to each route contract.

## Known Bugs

**The outreach workflow never uses the NemoClaw parallel-dispatch path:**
- Symptoms: `POST /api/outreach/workflow` in `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py` always returns `"dispatch_mode": "serial"` and never calls `dispatch_parallel()` from `Category 3 - IA West Smart Match CRM/src/coordinator/nemoclaw_adapter.py`, even though the adapter exists and is tested.
- Files: `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/nemoclaw_adapter.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_outreach_workflow.py`, `Category 3 - IA West Smart Match CRM/tests/test_nemoclaw_adapter.py`
- Trigger: any React or API call to `/api/outreach/workflow`.
- Workaround: none. The current coordinator workflow path is always serial.

**React analytics can silently degrade into empty states when backend routes fail:**
- Symptoms: `fetchQrStats()` and `fetchFeedbackStats()` in `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts` swallow all errors and return empty summaries; `fetchCalendarAssignments()` and `fetchCalendarEvents()` either fall back to different datasets or to `[]`, and several pages render those results as normal data rather than as degraded mode.
- Files: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx`
- Trigger: FastAPI route errors, schema mismatches, or local proxy/back-end outages.
- Workaround: inspect browser network traffic or backend logs; the UI often presents a zero-data dashboard instead of surfacing the failure clearly.

**Pipeline, QR, and feedback writes can target the wrong directory outside the default project layout:**
- Symptoms: `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py` binds `PIPELINE_CSV` from `_data_dir()` at import time, while QR and feedback persistence also depend on `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py` instead of `DATA_DIR`.
- Files: `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`, `Category 3 - IA West Smart Match CRM/src/config.py`
- Trigger: running with a non-default `DATA_DIR`, importing modules before monkeypatches, or trying to reuse the app in a different deployment layout.
- Workaround: run with the default `Category 3 - IA West Smart Match CRM/data/` layout only, or patch module-level path constants explicitly in tests.

## Security Considerations

**The FastAPI surface has no authentication or authorization boundary:**
- Risk: every coordinator route is currently open to any caller that can reach the server, including `Category 3 - IA West Smart Match CRM/src/api/routers/data.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`, and `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`.
- Files: `Category 3 - IA West Smart Match CRM/src/api/main.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/data.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`, `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`
- Current mitigation: CORS in `Category 3 - IA West Smart Match CRM/src/api/main.py` only allows localhost dev origins.
- Recommendations: keep the API private behind a trusted same-origin proxy for demo use, or add real authn/authz and rate limiting before any wider deployment.

**The QR flow is an open redirect sink:**
- Risk: `QRGenerateRequest.destination_url` in `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py` is accepted and persisted as-is, and `record_qr_scan()` in `Category 3 - IA West Smart Match CRM/src/qr/service.py` issues a 307 redirect to that stored destination with appended referral metadata.
- Files: `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`
- Current mitigation: `Category 3 - IA West Smart Match CRM/src/qr/service.py` falls back to `DEFAULT_DESTINATION_URL` only when no custom URL is supplied.
- Recommendations: validate schemes, allowlist approved hosts, and sign or derive the redirect target server-side instead of trusting request input.

**Operational feedback and QR logs live under repo-tracked data folders:**
- Risk: `Category 3 - IA West Smart Match CRM/src/feedback/service.py` and `Category 3 - IA West Smart Match CRM/src/qr/service.py` write volunteer names, coordinator outcomes, and scan history under `data/feedback/` and `data/qr/`, but the current ignore rules do not exclude those directories.
- Files: `.gitignore`, `Category 3 - IA West Smart Match CRM/.gitignore`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`, `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`
- Current mitigation: none beyond manual `git status` review.
- Recommendations: move mutable operational logs outside the repo, or explicitly ignore `Category 3 - IA West Smart Match CRM/data/feedback/` and `Category 3 - IA West Smart Match CRM/data/qr/`.

**Scraping still fails open when `robots.txt` cannot be read:**
- Risk: `check_robots_txt()` in `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py` logs a warning and returns `True` when the robots fetch fails.
- Files: `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`
- Current mitigation: `validate_public_demo_url()` constrains scheme, host type, and public-IP resolution before the scrape.
- Recommendations: treat robots-read failures as deny-by-default or require explicit operator override before scraping proceeds.

## Performance Bottlenecks

**Matching requests rebuild disk-backed context on every call:**
- Problem: `_load_matching_context()` in `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py` reloads speakers, events, calendar data, and embedding lookup dictionaries on every `/rank` and `/score` request.
- Files: `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/embeddings.py`
- Cause: immutable CSV and embedding artifacts are re-read from disk instead of being cached at process scope with explicit invalidation.
- Improvement path: memoize loaded DataFrames and embedding dictionaries for the running API process and invalidate them when source files change.

**The React coordinator bundle is eagerly loaded and already at warning size:**
- Problem: `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx` statically imports every page, while `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, and `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx` are all large modules; `.planning/STATE.md` already records the build chunk-size warning as an accepted follow-up.
- Files: `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx`, `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts`, `.planning/STATE.md`
- Cause: route-level code splitting and domain-level client splitting have not been added.
- Improvement path: lazy-load coordinator routes, split chart-heavy domains into separate chunks, and break `api.ts` into smaller modules.

**Calendar and recovery payloads are recomputed repeatedly from sample pipeline data:**
- Problem: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py` rebuilds slot and overlay summaries for every request, and the React pages in `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx`, and `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx` each re-fetch and aggregate those rows on mount.
- Files: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`
- Cause: the model is purely derived at request time and there is no cache/materialized summary layer.
- Improvement path: cache derived calendar payloads server-side and recompute only when pipeline or calendar inputs change.

## Fragile Areas

**File-backed mutation paths have no locking or transactional safety:**
- Files: `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`, `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`
- Why fragile: these modules perform append or read-modify-write updates against JSON, JSONL, and CSV files without file locks or atomic replace semantics.
- Safe modification: move the mutation paths behind a transactional store or use temp-file replace plus explicit file locking.
- Test coverage: single-process happy paths are covered in `Category 3 - IA West Smart Match CRM/tests/test_api_feedback.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_qr.py`, and `Category 3 - IA West Smart Match CRM/tests/test_pipeline_updater.py`, but concurrent writes are not.

**Legacy Streamlit and React/FastAPI coordinator surfaces still overlap heavily:**
- Files: `Category 3 - IA West Smart Match CRM/src/app.py`, `Category 3 - IA West Smart Match CRM/src/ui/`, `Category 3 - IA West Smart Match CRM/frontend/src/app/`, `Category 3 - IA West Smart Match CRM/src/api/routers/`
- Why fragile: the repo carries two coordinator entry paths with overlapping business logic, different persistence contracts, and partially duplicated UX features.
- Safe modification: decide which surface is authoritative for each feature before changing shared matching, feedback, or pipeline logic.
- Test coverage: Streamlit unit coverage is broad, but cross-surface parity is not asserted anywhere.

**React error handling is inconsistent across domains:**
- Files: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx`
- Why fragile: some failures surface as top-level page errors while others are silently converted into empty arrays or zero summaries.
- Safe modification: preserve typed degraded-state objects and render explicit “backend unavailable / fallback data” messaging whenever a fallback path is taken.
- Test coverage: no frontend test suite exercises these degraded states.

**Verification hygiene is vulnerable to generated install artifacts and a dirty tree:**
- Files: `.planning/STATE.md`, `.planning/ROADMAP.md`, `Category 3 - IA West Smart Match CRM/frontend/node_modules/`, `Category 3 - IA West Smart Match CRM/package-lock.json`, `.gitignore`, `Category 3 - IA West Smart Match CRM/.gitignore`
- Why fragile: the repo records a shipped milestone while local install artifacts and large uncommitted implementation changes remain present, and `Category 3 - IA West Smart Match CRM/frontend/node_modules/` is not currently ignored.
- Safe modification: ignore generated install trees, clean local verification artifacts, and do not advance planning state until the scoped diff is committed.
- Test coverage: not applicable.

## Scaling Limits

**The current coordinator model is still tuned to a very small static dataset:**
- Current capacity: `18` speakers in `Category 3 - IA West Smart Match CRM/data/data_speaker_profiles.csv`, `15` events in `Category 3 - IA West Smart Match CRM/data/data_cpp_events_contacts.csv`, `35` course rows in `Category 3 - IA West Smart Match CRM/data/data_cpp_course_schedule.csv`, and `9` calendar rows in `Category 3 - IA West Smart Match CRM/data/data_event_calendar.csv`.
- Limit: the calendar API, top-five match UI, and recovery heuristics all assume small in-memory lists and sample-sized coordinator review flows.
- Scaling path: move filtering, ranking, and scheduling summaries behind paginated/queryable server contracts before the source datasets grow significantly.

**Mutable state is still single-instance local filesystem storage:**
- Current capacity: one process writing `Category 3 - IA West Smart Match CRM/data/pipeline_sample_data.csv`, `Category 3 - IA West Smart Match CRM/data/feedback/`, and `Category 3 - IA West Smart Match CRM/data/qr/`.
- Limit: there is no locking, deduplication, multi-user audit isolation, or conflict resolution.
- Scaling path: replace file-backed mutable state with a transactional store and keep CSVs as seed/reference data only.

## Dependencies at Risk

**Browser-backed verification still depends on optional Playwright and a live app process:**
- Risk: `Category 3 - IA West Smart Match CRM/requirements.txt` includes `playwright`, `Category 3 - IA West Smart Match CRM/tests/test_e2e_playwright.py` assumes a running Streamlit app on `127.0.0.1:8501` without an explicit skip guard, and `.planning/milestones/v3.0-MILESTONE-AUDIT.md` records that a browser runtime was unavailable in-session.
- Impact: browser-backed verification remains inconsistent across environments, and unattended `pytest` runs can be noisy or fail for setup reasons unrelated to the code under review.
- Migration plan: gate live-browser tests behind explicit markers/fixtures and make browser-backed verification a separate, documented profile.

**The combined Streamlit + FastAPI + Playwright + voice runtime is still brittle to reproduce:**
- Risk: `Category 3 - IA West Smart Match CRM/requirements.txt` now mixes Streamlit, FastAPI, Playwright, QR imaging, and optional voice dependencies, and the file already documents version drift for `pandas` and `scikit-learn`.
- Impact: clean-machine setup and CI parity remain fragile, especially when only one surface of the app is actually being verified.
- Migration plan: split runtime extras by surface or lock one known-good environment file per deployment/test profile.

## Missing Critical Features

**There is still no real authentication layer for the coordinator product:**
- Problem: the React coordinator routes in `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx` and the FastAPI routers under `Category 3 - IA West Smart Match CRM/src/api/routers/` assume trusted local access only.
- Blocks: safe exposure beyond local demo use.

**There is still no authoritative persisted scheduling model behind the calendar UI:**
- Problem: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py` derives event windows and recovery overlays from `pipeline_sample_data.csv` plus `data_event_calendar.csv`, rather than from stored assignments or calendar entities.
- Blocks: trustworthy scheduling, auditability, and multi-operator coordination.

**The shipped outreach path still lacks actual parallel-agent orchestration:**
- Problem: `Category 3 - IA West Smart Match CRM/src/coordinator/nemoclaw_adapter.py` is present but unused by `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py`.
- Blocks: truthful implementation of the “parallel agents” coordinator story in the API/React workflow.

## Test Coverage Gaps

**There is no React unit or integration suite for the shipped coordinator app:**
- What's not tested: the pages and components under `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/`, `Category 3 - IA West Smart Match CRM/frontend/src/components/`, and the normalization logic in `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.
- Files: `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/`, `Category 3 - IA West Smart Match CRM/frontend/src/components/`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, `Category 3 - IA West Smart Match CRM/frontend/package.json`
- Risk: backend contract drift and UI regressions are currently caught only by manual build checks or ad hoc browser testing.
- Priority: High

**Most newly added API routes are not exercised through the full HTTP stack:**
- What's not tested: real FastAPI request/response serialization, middleware behavior, and exception handling for matching, calendar, feedback, and QR routes.
- Files: `Category 3 - IA West Smart Match CRM/tests/test_api_matching.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_calendar.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_feedback.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_qr.py`, `Category 3 - IA West Smart Match CRM/src/api/main.py`
- Risk: framework-level regressions can slip through even when direct function-call tests stay green.
- Priority: High

**Browser-backed coverage is partial and environment dependent:**
- What's not tested: the React QR and feedback flows end-to-end, plus a reliable default browser-backed verification path for both coordinator surfaces.
- Files: `Category 3 - IA West Smart Match CRM/tests/test_e2e_playwright.py`, `Category 3 - IA West Smart Match CRM/tests/test_e2e_flows.py`, `.planning/milestones/v3.0-MILESTONE-AUDIT.md`, `.planning/STATE.md`
- Risk: the most visible coordinator workflows still depend on manual or environment-specific browser checks.
- Priority: High

**There are no concurrency tests for file-backed mutation paths:**
- What's not tested: simultaneous QR generation/scan logging, feedback submission, and pipeline status updates against the same files.
- Files: `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`, `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_feedback.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_qr.py`, `Category 3 - IA West Smart Match CRM/tests/test_pipeline_updater.py`
- Risk: lost updates and malformed operational files would only appear under live multi-action use.
- Priority: Medium

---

*Concerns audit: 2026-03-26*
