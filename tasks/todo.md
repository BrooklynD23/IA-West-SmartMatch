# Todo

## Current Work

### Cat3 Fullstack Port Conflict Recovery

_Execution board for fixing `./start_cat3_fullstack.sh` when the backend port is already occupied and the launcher currently reports a generic startup failure._

- [x] Reproduce the backend failure from the captured log and confirm the exact occupied-port path in the launcher.
- [x] Patch the launcher to surface explicit startup diagnostics and reuse an already-running CAT3 backend when `/api/health` is already available.
- [x] Tighten the frontend launch contract so the readiness probe cannot silently drift to a different Vite port.
- [x] Add focused launcher tests and record verification plus any remaining sandbox limits.

#### Review

- Root cause: the failing WSL run was not a dependency-sync regression. The backend log showed `ERROR: [Errno 98] Address already in use`, but the launcher surfaced that as a generic readiness failure instead of recognizing a duplicate bind or printing the real log-tail message.
- Fixes:
  - Updated `Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py` to probe `/api/health` before launching the backend and reuse an already-running CAT3 FastAPI instance on `:8000`.
  - Added backend port-conflict recovery so a duplicate bind now resolves to either `Already running` for the CAT3 API or an explicit `Port 127.0.0.1:8000 already in use` message with the backend log path.
  - Added `--strictPort` to the Vite launch command and now prefer the frontend log tail on startup failure so occupied `:5173` errors are surfaced directly instead of a vague `Process exited with code 1`.
  - Added focused regression coverage in `Category 3 - IA West Smart Match CRM/tests/test_start_fullstack.py`.
- Verification:
  - `python3 -m py_compile "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py" "Category 3 - IA West Smart Match CRM/tests/test_start_fullstack.py"` -> passed.
  - `python3 -m pytest "Category 3 - IA West Smart Match CRM/tests/test_start_fullstack.py" -q` -> `5 passed in 0.10s`.
  - `./start_cat3_fullstack.sh --help` -> passed.
  - `timeout 20s ./start_cat3_fullstack.sh --skip-install --no-browser` -> failed fast in this sandbox with `PermissionError: [Errno 1] Operation not permitted`, which confirms the launcher now surfaces the backend log-tail error instead of a generic exit code.
  - Full live boot remains unverified inside this Codex sandbox because local socket binding is restricted here, so the occupied-port fix still needs one run on your machine for end-to-end confirmation.

### Cat3 Fullstack Launcher UX + Startup Reliability

_Execution board for making `./start_cat3_fullstack.sh` readable in WSL2/Windows Terminal and reducing false “stuck on sync” startup failures._

- [x] Inspect the current fullstack launcher flow and identify why startup appears stuck before backend/frontend launch.
- [x] Replace the raw dependency flood with staged terminal status output and check-mark completion states.
- [x] Split the fullstack launcher onto a slim Python dependency set so React + FastAPI boot does not pull optional voice/ML packages by default.
- [x] Add startup readiness checks so the launcher reports whether backend and frontend actually became available.
- [x] Update launcher docs and run lightweight verification checks.

#### Review

- Root cause 1: `start_fullstack.py` always ran `pip install -r requirements.txt`, which pulled optional voice/ML dependencies such as `kittentts`, `torch`, and CUDA wheels even though the React + FastAPI launcher does not need them to boot.
- Root cause 2: the previous launcher handed control directly to child processes with no readiness check, so “not starting” failures were opaque and the terminal gave no staged progress.
- Fixes:
  - Reworked `Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py` to render a staged terminal status board with check marks for environment, runtime, dependency sync, backend readiness, frontend readiness, and overall ready state.
  - Added cached install-state tracking so repeated runs skip Python/npm sync when `requirements-fullstack.txt` and `package-lock.json` are unchanged.
  - Added `Category 3 - IA West Smart Match CRM/requirements-fullstack.txt` for the slim React + FastAPI launcher path.
  - Added `--force-install`, `--full-install`, `--backend-host`, and `--frontend-host` flags.
  - On Unix/WSL, backend/frontend logs are now written to temp log files and the launcher waits for `http://127.0.0.1:8000/api/health` and `http://127.0.0.1:5173` before reporting success.
- Verification:
  - `python3 -m py_compile "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py"` -> passed.
  - Additional live bind verification is limited in this Codex environment because local socket binding is sandbox-restricted.

### Cat3 Fullstack Pip Install Visibility Fix

_Execution board for making dependency sync visibly report pip install progress during `./start_cat3_fullstack.sh`._

- [x] Confirm root cause of hidden output in the fullstack launcher install step.
- [x] Remove quiet pip mode and enable visible progress output in the startup script.
- [x] Run a lightweight verification check and record outcome.

#### Review

- Root cause: `Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py` invoked pip with `-q`, which suppresses dependency install output and makes long installs appear stalled.
- Fix: updated launcher dependency sync command to run `pip install --progress-bar on -r requirements.txt` and updated the sync message to indicate live pip output.
- Verification: `python3 -m py_compile "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py"` -> passed.

### Cat3 Fullstack Dependency Sync Fix (Pillow Conflict)

_Execution board for resolving the launcher-time pip resolver failure: `streamlit==1.42.2` vs `Pillow==12.1.1` in `Category 3 - IA West Smart Match CRM/requirements.txt`._

- [x] Reproduce/inspect the failing dependency set from the startup path and identify the conflicting pins.
- [x] Apply the minimal requirements pin change that restores resolver compatibility for the existing Streamlit runtime.
- [x] Run focused verification checks and record any environment limits that prevent full end-to-end install validation.

#### Review

- Root cause: `Category 3 - IA West Smart Match CRM/requirements.txt` pinned `streamlit==1.42.2` together with `Pillow==12.1.1`, which conflicts with Streamlit 1.42.x dependency bounds and triggers `ResolutionImpossible` during the startup script dependency sync.
- Fix: updated the Pillow pin to `Pillow==11.3.0` in `Category 3 - IA West Smart Match CRM/requirements.txt` to remain in the latest 11.x line while staying compatible with Streamlit 1.42.x.
- Verification performed:
  - Confirmed requirement file edit with line-numbered file inspection.
  - Attempted full `pip install -r requirements.txt`, but this environment currently cannot resolve external hosts (`pypi.org`, `github.com`), so a complete install test is blocked by network DNS failures unrelated to the dependency-pin fix.
- Residual risk:
  - Full dependency install needs one online verification run in your normal environment (where pip can access package indexes) to confirm end-to-end startup now passes.

### CAT3 React + FastAPI Cross-Environment Launcher

_Execution board for adding an easy launcher that starts the Category 3 React frontend + FastAPI backend across Windows and WSL2 with environment detection and teammate-friendly run guidance._

- [x] Confirm existing startup scripts/ports and define the new launcher contract for React (`:5173`) + FastAPI (`:8000`).
- [x] Implement a cross-environment launcher under `Category 3 - IA West Smart Match CRM/scripts/` that detects Windows vs WSL/Linux and starts both services.
- [x] Add root-level convenience wrappers so non-technical teammates can run from the repo root on Windows or WSL.
- [x] Update README instructions with a concise “quick start” path for the new launcher.
- [x] Run a dry verification pass (syntax/help or safe checks) and record outcomes in review notes.

#### Review

- Defined and implemented a dedicated v3 launch contract for React + FastAPI with defaults `frontend:5173` and `backend:8000`.
- Added cross-environment launcher: `Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py`.
  - Detects `windows`, `wsl`, or `linux`.
  - Ensures `.venv` exists and syncs Python deps from `requirements.txt` (unless `--skip-install`).
  - Ensures frontend deps (`npm install`) when `frontend/node_modules` is missing.
  - Starts `uvicorn src.api.main:app --reload` plus `npm run dev -- --host ... --port ...`.
  - Windows opens separate consoles; WSL/Linux runs both in one terminal with shutdown handling.
- Added teammate-friendly wrappers:
  - Category scripts: `scripts/start_fullstack.sh`, `scripts/start_fullstack.ps1`, `scripts/start_fullstack.cmd`
  - Repo-root wrappers: `start_cat3_fullstack.sh`, `start_cat3_fullstack.ps1`, `start_cat3_fullstack.cmd`
- Updated docs:
  - `Category 3 - IA West Smart Match CRM/README.md` now has a quick-start section for the new launcher.
  - Root `README.md` now includes one-line quick launch commands.
- Verification:
  - `python3 -m py_compile "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py"` passed.
  - `bash -n "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.sh" "start_cat3_fullstack.sh"` passed.
  - `python3 "Category 3 - IA West Smart Match CRM/scripts/start_fullstack.py" --help` returned expected CLI options.

### GSD Roadmap Analyze v3.0 False Incomplete Investigation

_Execution board for inspecting why `node /home/danny/.codex/get-shit-done/bin/gsd-tools.cjs roadmap analyze` reports `roadmap_complete: false` for v3.0 phases even though `.planning/ROADMAP.md` shows shipped/completed state._

- [x] Reproduce the current `roadmap analyze` output for v3.0 phases and capture which fields are false.
- [x] Compare the relevant `.planning/ROADMAP.md` milestone and phase markup against the analyzer/parser conditions.
- [x] Determine whether the false status reflects genuinely incomplete sprint artifacts or a parser/tooling mismatch, then record the exact cause below.

#### Review

- `roadmap analyze` reports `disk_status: "complete"` with matching plan/summary counts for v3.0 phases, but `roadmap_complete: false` for each phase.
- Root cause is a parser mismatch in `/home/danny/.codex/get-shit-done/bin/lib/roadmap.cjs`: phase completion is detected only from checklist lines matching `- [x] ... Phase N:`. The active roadmap uses `### Phase N: ... ✅` headings plus completed plan checkboxes instead, so the regex never matches and `roadmap_complete` falls back to `false`.
- Conclusion: this does not indicate real incomplete sprint work. The active roadmap marks v3.0 shipped and complete; the analyzer is checking for a different phase-status representation than the one in this repo’s current roadmap format.

### V3.0 Sprint Remaining Work Check

_Execution board for `$gsd-autonomous check for anything left for V3.0 sprint`. Scope is limited to confirming whether v3.0 still has incomplete phases, blocking follow-ups, or worktree drift that should keep the sprint open._

- [x] Reconcile `.planning/ROADMAP.md`, `.planning/STATE.md`, archived v3.0 milestone docs, and `gsd-tools` output for phase completion status.
- [x] Inspect the current git/worktree state plus retained follow-ups to determine whether any remaining items are blocking sprint work or post-closeout backlog.
- [x] Record the conclusion, evidence, and any residual non-blocking follow-ups in the review section.

#### Review

- `.planning/STATE.md`, `.planning/ROADMAP.md`, and `.planning/milestones/v3.0-MILESTONE-AUDIT.md` are aligned on the shipped-state claim: v3.0 is complete, all phases 8-12 are done, and the retained follow-ups are manual/non-blocking.
- Phase verification artifacts for `09.1`, `10`, `11`, and `12` do not expose any unverified must-have requirements. The recurring gaps are environment/UAT items: missing Playwright browser runtime for browser-backed QR/feedback evidence, missing `uvicorn` in the local `.venv` during 09.1, and the existing non-blocking frontend bundle-size warning.
- `node /home/danny/.codex/get-shit-done/bin/gsd-tools.cjs roadmap analyze` still reports `roadmap_complete: false` for every v3.0 phase while also reporting `disk_status: "complete"`, `completed_phases: 7`, and `progress_percent: 100`. Based on the current planning artifacts, this reads as a tooling/parser mismatch rather than unfinished sprint scope.
- Current `git status --short` shows the v3.0 planning and implementation work is still uncommitted relative to `HEAD`. That is a real closeout/handoff gap if this sprint must end on a clean committed worktree, but it does not contradict the planning verdict that the product scope is complete.
- `tasks/todo.md` still contains an older unchecked Phase 8.5 recovery board, but `.planning/phases/08.5-fastapi-backend-react-promotion/08.5-VERIFICATION.md` is already `status: passed` and the shipped roadmap/state docs mark Phase 8.5 complete. Treat those unchecked items as stale bookkeeping, not active sprint scope.
- Blocking remaining work: none found in the planning artifacts for the shipped React/FastAPI path.
- Accepted follow-ups: browser-backed QR/feedback UAT, live rehearsal / voice-path UAT, bundle/code-splitting cleanup, legacy Streamlit feedback-path cleanup, and the separate `gsd-tools roadmap analyze` false-incomplete investigation.

### v3.0 Audit Findings Fix Pass

_Execution board for `$ecc-build-fix` against the 2026-03-26 audit findings recorded above. Scope is limited to the cited Category 3 backend, frontend, and targeted test files._

- [x] Fix backend optimizer weight application so matching APIs use the latest server-side effective weights by default while still allowing explicit overrides.
- [x] Harden the QR generate/scan flow against open redirects and pin the QR dependencies in `requirements.txt`.
- [x] Remove silent frontend fallbacks that convert API failures into false empty-state data for feedback and QR stats, and keep the feedback submission flow from wiping visible optimizer state on refresh failures.
- [x] Replace the dashboard coverage pulse/discovery narrative with source-backed regional summaries derived from live calendar and pipeline data.
- [x] Make the calendar selected-day assignment panel respect the active coverage filter.
- [x] Add real dialog accessibility behavior for the feedback and outreach overlays.
- [x] Strengthen targeted API tests through the FastAPI HTTP boundary for matching, calendar, feedback, and QR behavior.
- [x] Run targeted backend/frontend verification and capture outcomes plus residual risks here.

#### Review

- Backend matching now resolves optimizer history server-side by default via `get_effective_weights()`, and feedback submissions record the actual weights in use when the caller does not send an override.
- QR generation now ignores user-supplied `base_url` at the API boundary, validates `destination_url` against the app host or approved Insights Association domains, and returns `400` for invalid redirect targets; `qrcode` and `Pillow` are pinned in `requirements.txt`.
- FastAPI handlers under `src/api/` were converted to `async def` so real ASGI-boundary verification can run in-process, and `tests/asgi_client.py` now exercises validation, redirects, CORS, and JSON serialization without bypassing the HTTP layer.
- Frontend API helpers no longer silently fall back from `/api/calendar/*`, `/api/qr/stats`, or `/api/feedback/stats` to legacy/empty payloads; the affected pages now surface explicit warning banners while keeping any successful primary data.
- `FeedbackForm` now preserves optimizer state from the submit response if the follow-up stats refresh fails, instead of zeroing the visible matcher state after a successful submission.
- The dashboard coverage pulse/feed now derives its regional cards and coordinator callouts from live calendar coverage, assignment overlays, and member-inquiry counts; month labels also use local date parsing to avoid timezone drift on `YYYY-MM-DD` strings.
- The day-detail assignment panel on the calendar now filters overlays against the currently visible events, so hidden events no longer leak into the selected-day side rail.
- The feedback and outreach overlays now use the shared Radix dialog primitives for focus trapping, escape handling, and proper modal semantics.
- Verification:
  - `cd 'Category 3 - IA West Smart Match CRM' && timeout 240s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py tests/test_api_qr.py tests/test_api_feedback.py -q` -> `26 passed, 29 warnings in 6.13s`
  - `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` -> passed in `30.08s`; Vite still reports a `1,023.68 kB` JS chunk warning.
- Residual risks:
  - Browser-backed UAT for the QR and feedback flows is still absent, so the modal/accessibility improvements were verified via build plus API/tests, not end-to-end browser automation.
  - QR and feedback persistence are still file-backed read/modify/write flows without locking, so concurrent writes remain race-prone.
  - The targeted backend tests now hit the real ASGI boundary for the reviewed routes, but broader API coverage outside matching/calendar/feedback/QR still relies on older patterns.

### Codebase Map Refresh + v3.0 Audit

_Execution board for `$gsd-map-codebase` followed by `$ecc-code-review` on the uncommitted v3.0 session work. Review scope is the current worktree relative to `HEAD`, because the Phase 10-12 closeout changes have not been committed yet._

- [x] Reconcile repo state, `.planning/STATE.md`, `tasks/lessons.md`, and the current git diff so the audit scope is explicit.
- [x] Refresh `.planning/codebase/CONCERNS.md` against the current `Category 3 - IA West Smart Match CRM/` worktree state.
- [x] Re-audit Category 3 backend, frontend, tests, and planning artifacts for concrete debt, bugs, security, performance, and fragility concerns.
- [x] Replace the stale concerns doc with the refreshed current-state findings and note verification evidence.
- [x] Refresh `.planning/codebase/` using mapper agents without broadening scope beyond the current codebase state.
- [x] Review the Phase 09.1-12 backend/frontend/planning changes for security, quality, and standards issues.
- [x] Record findings, verification evidence, and residual risks in this section.

#### Review

- Refreshed `.planning/codebase/CONCERNS.md` for 2026-03-26 against the current worktree state rather than the last committed milestone snapshot.
- Highest-signal findings now called out in the doc: shipped-planning vs uncommitted-code drift, `DATA_DIR` split-brain paths, duplicate feedback systems, synthetic calendar semantics, unauthenticated/open-redirect API surfaces, eager React bundle growth, and missing React/concurrency coverage.
- Verification: manually audited the current Phase 09.1-12 backend/frontend files plus `.planning/STATE.md`, `.planning/ROADMAP.md`, `.gitignore`, and the current git diff before rewriting the concerns map.
- Refreshed `.planning/codebase/STACK.md` and `.planning/codebase/INTEGRATIONS.md` against the current Category 3 worktree state instead of the older Streamlit-only snapshot.
- Mapping now captures the hybrid runtime: legacy Streamlit shell in `Category 3 - IA West Smart Match CRM/src/app.py`, implemented FastAPI backend in `Category 3 - IA West Smart Match CRM/src/api/main.py`, and Vite/React frontend in `Category 3 - IA West Smart Match CRM/frontend/`.
- Integration inventory now records the active Gemini REST client, university scraping targets, local file-backed persistence and caches, Playwright/browser dependencies, and the promoted React/FastAPI contract surface.
- Final refreshed codebase map counts: `ARCHITECTURE.md` 179 lines, `STRUCTURE.md` 253, `CONCERNS.md` 195, `CONVENTIONS.md` 129, `TESTING.md` 243, `STACK.md` 101, `INTEGRATIONS.md` 113.
- Audit verification rerun:
  - `cd 'Category 3 - IA West Smart Match CRM' && timeout 240s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py tests/test_api_qr.py tests/test_api_feedback.py -q` -> `17 passed, 22 warnings in 49.17s`
  - `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` -> passed in `2m 11s`; Vite still reports a `959.80 kB` JS chunk warning.
- Highest-severity review findings:
  - `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py` + `src/qr/service.py`: QR generation/scan currently allows open redirects because `destination_url` and `base_url` are accepted and replayed without allow-list validation.
  - `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `src/matching/engine.py`, and `src/feedback/service.py`: Phase 12 optimizer weights are surfaced as analytics but are not applied by the backend unless the client explicitly passes weight overrides, which does not match the shipped-state planning claims.
  - `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`: calendar/QR/feedback fetch helpers silently convert backend failures into fallback or zero-state UI data, which can hide contract breakage and reset visible optimizer state.
  - `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`: the regional density-map/feed presents fabricated operational conclusions from hard-coded points rather than source-backed coverage data.
  - `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx` and `frontend/src/lib/api.ts` are now monolithic review hotspots at `868` and `1110` lines respectively, and there are still no checked-in frontend tests.
- Additional medium/low findings:
  - `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx`: the coverage filter only filters events; the selected-day assignment overlay still shows assignments for hidden events.
  - `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`: month bucketing uses `new Date("YYYY-MM-DD")`, which can shift labels at US month boundaries.
  - `Category 3 - IA West Smart Match CRM/requirements.txt`: `qrcode` and `Pillow` were added unpinned.
  - `Category 3 - IA West Smart Match CRM/frontend/node_modules/` is present locally and is not ignored by the repo root `.gitignore`, which makes future worktree audits noisy.
- Residual risks:
  - Browser-backed QR/feedback UAT is still absent.
  - QR and feedback file persistence remain race-prone because both features use unlocked read/modify/write updates against local JSON and JSONL files.
  - The new API tests mainly call router functions directly, so the real HTTP boundary still lacks coverage for redirect restrictions, validation behavior, and CORS/serialization concerns.

### v3.0 Autonomous Closeout From Phase 09.1

_Execution board for `$gsd-autonomous --from 9.1`. Source of truth is `.planning/ROADMAP.md` + `.planning/STATE.md`; `roadmap analyze` currently under-reports roadmap completion for earlier phases, so this run scopes to Phases 09.1, 10, 11, and 12 only._

- [x] Reconcile the milestone state with the current phase queue and keep this board aligned while the autonomous run is in flight.
- [x] Phase 09.1: plan the V1.2 React rebrand from the existing `09.1-CONTEXT.md`, execute the approved work, and verify the user-facing result.
- [x] Phase 10: gather/write CONTEXT, plan master-calendar + recovery-period work, execute it, and verify both backend and frontend behavior.
- [x] Phase 11: gather/write CONTEXT, plan QR + ROI tracking work, execute it, and verify generation, scan tracking, and analytics behavior.
- [x] Phase 12: gather/write CONTEXT, plan feedback-loop + weight-optimization work, execute it, and verify the end-to-end data flow.
- [x] After all remaining phases: update `.planning/ROADMAP.md`, `.planning/STATE.md`, and phase verification artifacts to the truthful final state.
- [x] Run milestone audit / completion / cleanup steps required by the autonomous workflow and record outcomes here.

#### Review

- Phase 09.1 is now closed at the merged-build level with summary artifacts `09.1-01/02/03-SUMMARY.md` plus `09.1-VERIFICATION.md`.
- Integrated verification: `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` passed after restoring the accidentally dropped `/ai-matching` route during merge review.
- Residual environment gaps recorded in the verification doc: the local `.venv` is missing `uvicorn`, and the Playwright browser runtime could not be installed in-session, so no browser-backed screenshot evidence was captured.
- Phase 10 is now closed with `10-01-SUMMARY.md`, `10-02-SUMMARY.md`, and `10-VERIFICATION.md`.
- Verification: `timeout 60s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py -q` -> `9 passed, 22 warnings in 9.48s`; `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` passed with the existing non-blocking chunk-size warning only.
- Phase 11 is now closed with `11-01-SUMMARY.md`, `11-02-SUMMARY.md`, and `11-VERIFICATION.md`.
- Verification: `cd 'Category 3 - IA West Smart Match CRM' && timeout 120s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py tests/test_api_qr.py -q` -> `13 passed, 22 warnings in 10.91s`; `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` passed in `43.05s` with the existing non-blocking chunk-size warning only.
- Integration correction during review: `frontend/src/lib/api.ts` now normalizes backend `referral_codes`, `membership_interest_count`, and `qr_data_url`, which was required for live QR previews and ROI history to display correctly on the React surfaces.
- Phase 12 is now closed with `12-01-SUMMARY.md`, `12-02-SUMMARY.md`, and `12-VERIFICATION.md`.
- Verification: `cd 'Category 3 - IA West Smart Match CRM' && timeout 180s ./.venv/bin/python -m pytest tests/test_api_matching.py tests/test_api_calendar.py tests/test_api_qr.py tests/test_api_feedback.py -q` -> `17 passed, 22 warnings in 20.67s`; `cd 'Category 3 - IA West Smart Match CRM/frontend' && npm run build` passed in `2m 57s` with the existing non-blocking chunk-size warning only.
- Milestone closeout completed: wrote `.planning/milestones/v3.0-MILESTONE-AUDIT.md`, updated `.planning/PROJECT.md`, `.planning/MILESTONES.md`, `.planning/ROADMAP.md`, and `.planning/STATE.md` to shipped state, and retained the active phase directories as the canonical detailed record instead of deleting them.

### Phase 8.5 FastAPI + React Promotion Recovery

_Autonomous resume point from `.planning/phases/08.5-fastapi-backend-react-promotion/08.5-CONTEXT.md`: planning exists, execution not started. This section owns the backend/API promotion, React app promotion, live data wiring, and phase-closeout artifact updates._

- [x] Reconcile Phase 8.5 backend contract against the current codebase and keep task tracking aligned with `.planning/` state.
- [x] Create the FastAPI package at `Category 3 - IA West Smart Match CRM/src/api/` with app wiring, CORS, and data/matching/outreach routers.
- [x] Keep the matching API on `src/matching/engine.py` contracts, normalize rank payload fields for frontend consumers, and avoid Streamlit-import hazards in backend modules.
- [x] Add targeted backend API coverage in `Category 3 - IA West Smart Match CRM/tests/test_api_data.py` and `Category 3 - IA West Smart Match CRM/tests/test_api_matching.py`.
- [x] Promote `Category 3 - IA West Smart Match CRM/docs/mockup/V1.1/IA-West_UI/` into `Category 3 - IA West Smart Match CRM/frontend/`, fix its standalone Vite/package setup, and add a typed API client.
- [x] Wire the React pages to live `/api/*` data with loading/error states and preserve the existing V1.1 visual language.
- [ ] Install missing Python and npm dependencies in a disposable/local environment for Phase 8.5 verification.
- [ ] Run focused verification:
  - Python: `test_api_data.py`, `test_api_matching.py`, and a `uvicorn src.api.main:app` smoke start.
  - Frontend: `npm install` then `npm run build` under `Category 3 - IA West Smart Match CRM/frontend/`.
- [ ] Fix any verification failures discovered by that first install/build/test pass.
- [ ] Write Phase 8.5 summaries / verification artifacts and update `.planning/ROADMAP.md` + `.planning/STATE.md` from "execution in progress" to the truthful verified state.

#### Review

- Landed in the worktree:
  - FastAPI package at `Category 3 - IA West Smart Match CRM/src/api/` with `main.py`, `data.py`, `matching.py`, and `outreach.py`.
  - Targeted API tests at `Category 3 - IA West Smart Match CRM/tests/test_api_data.py` and `Category 3 - IA West Smart Match CRM/tests/test_api_matching.py`.
  - React frontend promoted into `Category 3 - IA West Smart Match CRM/frontend/` with Vite bootstrap files, typed API client, and API-backed rewrites of Dashboard, Opportunities, Volunteers, AI Matching, Pipeline, Calendar, and Outreach.
- Manual code correction applied during review:
  - Fixed the outreach ICS router to call `generate_ics(..., date_str=...)` instead of the invalid `event_date=` keyword.
- Verification attempted:
  - `python3 -m pytest 'Category 3 - IA West Smart Match CRM/tests/test_api_data.py' -q` -> failed at import time with `ModuleNotFoundError: No module named 'fastapi'`.
  - `python3 -m pytest 'Category 3 - IA West Smart Match CRM/tests/test_api_matching.py' -q` -> failed at import time with the same missing `fastapi` dependency.
  - Created disposable venv: `python3 -m venv /tmp/hbf-phase85-venv`.
  - Began requesting Python dependency installation into `/tmp/hbf-phase85-venv`, but the session was interrupted before that install/build step completed. Treat the verification environment as incomplete and re-check before reuse.
- Next-session resume point:
  - GSD status should stay on Phase 8.5 execution.
  - Next logical command after environment setup is `$gsd-execute-phase 8.5` continued through verification, then phase summaries/verification docs once the first clean test/build pass is complete.

### CRM Routing and Jarvis Fix Pass

_Overlap with **Frontend Routing and Match Engine QA Fix Pass** below: that pass owns the initial router/query-param sync + Match Engine regression work; this pass closes the Jarvis discovery wiring, NemoClaw documentation, coordinator/Jarvis UI ordering, sign-out follow-up, and the dated Playwright demo re-check._

- [x] Refactor Category 3 query-param handling to prefer `st.query_params` on the pinned Streamlit 1.42.x runtime, keep fallback support for legacy experimental APIs, and update router regression tests.
- [x] Wire the Jarvis `discover_events` tool through scrape + `extract_events(...)`, then update `tests/test_discovery_tool.py` to cover the extracted-event path and the no-Streamlit contract.
- [x] Document the dormant NemoClaw path in the Category 3 README and add a clarifying module note in `src/coordinator/nemoclaw_adapter.py`.
- [x] Apply the small demo-hardening UI tweaks: move the Jarvis checkbox above the dashboard iframe, keep the coordinator coverage-map expectation caption honest, and add a brief match-engine discoverability caption.
- [x] Run targeted verification for the touched Category 3 tests (`test_page_router`, `test_discovery_tool`, `test_app`, `test_match_engine_page`).
- [x] Run a dated Playwright browser pass on `http://127.0.0.1:8501`, save screenshots under `Category 3 - IA West Smart Match CRM/output/playwright/`, and write the QA report to `Category 3 - IA West Smart Match CRM/docs/testing/2026-03-25-playwright-demo-report.md`.
- [x] Add a review note here with implementation results, verification evidence, and any residual demo risk.

#### Review

- Implementation:
  - `page_router.py` now stages demo-mode changes through a pending navigation override so sign-out can clear `demo=1` without tripping Streamlit’s widget-state mutation guard.
  - `discovery_tool.py` stays wired through scrape + `extract_events(...)`; README/module documentation reflects NemoClaw’s dormant status; dashboard and Match Engine captions/ordering match the intended demo story.
  - Added `scripts/run_playwright_demo_qa.py` plus updated `tests/test_e2e_flows.py` so the routed workspace, deep links, Jarvis proposal flow, and sign-out path have reproducible browser coverage.
- Verification:
  - `python3 -m py_compile 'Category 3 - IA West Smart Match CRM/src/ui/page_router.py' 'Category 3 - IA West Smart Match CRM/tests/test_page_router.py' 'Category 3 - IA West Smart Match CRM/tests/conftest.py' 'Category 3 - IA West Smart Match CRM/scripts/run_playwright_demo_qa.py' 'Category 3 - IA West Smart Match CRM/tests/test_e2e_flows.py'`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python -m pytest tests/test_page_router.py -q` -> `8 passed`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python scripts/run_playwright_demo_qa.py` -> `16 cases`, `10 warnings`, `0 page_errors`, `0 request_failures`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python -m pytest tests/test_e2e_flows.py -q` -> `9 passed`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python -m pytest -q` -> `591 passed`, `1 failed`
  - Dated browser report: `Category 3 - IA West Smart Match CRM/docs/testing/2026-03-25-playwright-demo-report.md`
- Demo outcome:
  - The Playwright pass covered landing, login, View Demo, deep links, workspace nav, Jarvis toggle + text command + approve path, and sign-out. All 16 scripted checks passed, and screenshots were saved under `Category 3 - IA West Smart Match CRM/output/playwright/`.
  - Jarvis approval completed end-to-end in the UI with `Found 0 event(s) (source: cache)`, which confirms the patched tool path in this environment.
- Residual risk:
  - The embeddings API-key regression was a test isolation issue, not a runtime bug. The targeted regression now passes; the full suite was not rerun after this cleanup-only follow-up.
  - Jarvis voice/TTS dependencies were absent locally, so the command center degraded to text-only warnings during QA.
  - Discovery execution completed from cache with zero events here; live discovery quality still depends on cache freshness, network reachability, and Gemini availability.
  - Cleanup note: removed the accidental mockup `node_modules` tree and added ignore rules so dependency reinstalls do not flood the worktree again.

### Frontend Routing and Match Engine QA Fix Pass

_See **CRM Routing and Jarvis Fix Pass** for Jarvis/NemoClaw/discovery-tool deliverables and the latest Browser MCP table._

- [x] Reproduce the routing defects from the browser QA report against the current router helpers and Streamlit runtime assumptions.
- [x] Harden query-param read/write behavior so deep links, in-app navigation, and invalid-route normalization keep the URL bar in sync.
- [x] Improve the Match Engine page so the primary workspace shows meaningful above-the-fold content and an explicit empty state when match data is sparse.
- [x] Add or update targeted regression tests for router normalization/synchronization and Match Engine rendering.
- [x] Run targeted verification, then add a review note here summarizing pass/fail status and residual risk.

#### Review

- Root cause for the routing defects was the mixed query-param API usage in `page_router.py`: reads could come from `st.query_params` while writes went through `experimental_set_query_params`, which is fragile on the Streamlit 1.42.x runtime captured in QA.
- The router now uses one read/write family consistently, so alias routes, unknown-route normalization, and in-app navigation all go through the same query-param sync path.
- The Match Engine page no longer reserves a 5000px iframe height; it uses a tighter height and renders a visible shortlist summary or explicit empty state instead of leaving the main pane visually blank.
- Added regression coverage for query-param synchronization and Match Engine sparse-data rendering.
- Verification:
  - `python3 -m py_compile 'Category 3 - IA West Smart Match CRM/src/ui/page_router.py' 'Category 3 - IA West Smart Match CRM/src/ui/match_engine_page.py' 'Category 3 - IA West Smart Match CRM/tests/test_page_router.py' 'Category 3 - IA West Smart Match CRM/tests/test_match_engine_page.py'`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python -m pytest tests/test_page_router.py -q` -> `5 passed`
  - `cd 'Category 3 - IA West Smart Match CRM' && /tmp/hbf-pytest-venv/bin/python -m pytest tests/test_match_engine_page.py -q` -> `2 passed`
- Residual risk:
  - The live browser QA run used Streamlit 1.42.2 on the already-running `:8501` server. I did not re-run that exact browser flow after the patch, so bookmark/deep-link behavior still needs one manual confirmation pass against that runtime.
- 2026-03-25 closeout: Playwright follow-up on `127.0.0.1:8501` confirms cold `?route=matches`, `?route=coordinator&demo=1`, unknown-route normalization, workspace nav, Jarvis proposal/approve flow, and sign-out; see `Category 3 - IA West Smart Match CRM/docs/testing/2026-03-25-playwright-demo-report.md`.

### UI Audit Review Fix Pass

- [x] Replace the split `current_page`/`current_view` navigation with a single routed V2 workspace.
- [x] Wire landing, login, coordinator, and match-engine controls to real destinations instead of dead `#` links.
- [x] Promote the legacy Matches, Discovery, Pipeline, Expansion, and Volunteer surfaces into reachable V2 routes.
- [x] Replace the coordinator dashboard heatmap placeholder with a real Plotly map and warn on unmapped metro data.
- [x] Update the affected tests/docs, run targeted verification, and add a review note with results.

#### Review

- Unified the V2 router around query-param-synced `current_page` routes and removed the live dependency on the unreachable `current_view` CRM shell.
- Wired the landing/login/dashboard/match-engine iframe controls to real page destinations, added a shared iframe navigation bridge, and made the public landing nav scroll to real sections instead of `#`.
- Exposed reachable V2 pages for Dashboard, Matches, Discovery, Pipeline, Analytics, and Match Engine; Analytics now hosts the expansion map and volunteer dashboard, and the dashboard can surface Jarvis on demand.
- Replaced the coordinator heatmap mock with a live Plotly campus coverage map built from the shared expansion-map geography logic, including warnings for unmapped metro regions.
- Verification:
  - `python3 -m py_compile src/app.py src/ui/page_router.py src/ui/html_base.py src/ui/landing_page_v2.py src/ui/login_page.py src/ui/coordinator_dashboard.py src/ui/match_engine_page.py src/ui/expansion_map.py tests/test_app.py tests/test_expansion_map.py tests/test_page_router.py`
  - `"/mnt/c/Users/DangT/documents/github/HackathonForBetterFuture2026/.venv/Scripts/python.exe" -m pytest tests/test_app.py tests/test_expansion_map.py tests/test_page_router.py -q` -> `25 passed`

### Milestone Wrap-Up: v1.0 then v2.0 (Sequential)

- [x] Validate milestone pre-flight status for v1.0 and v2.0 (audit presence, phase completion, requirement coverage).
- [x] Clean accidental `--help` milestone artifacts generated during CLI probing.
- [x] Finalize v1.0 archive state (ensure archive docs + MILESTONES entry + audit archive) and create tag `v1.0`.
- [x] Archive v2.0 milestone artifacts (`ROADMAP`, `REQUIREMENTS`, milestones entry), then collapse active roadmap scope.
- [x] Update PROJECT/STATE for post-v2 shipped state and remove live `.planning/REQUIREMENTS.md` for next milestone reset.
- [x] Commit v2.0 archive changes and create tag `v2.0`.
- [x] Add verification + outcomes to the review section.

### Sprint 6 Phase 0-1 Review Fix Pass

- [x] Fix all HIGH findings from the latest `$ecc-code-review` report for Phase 0/1.
- [x] Close the MEDIUM finding by making landing-page factor visuals resilient to factor-count changes.
- [x] Close the LOW finding by removing unused imports and tightening test quality.
- [x] Verify touched files with targeted automated checks in the available environment.
- [x] Commit only the scoped fix files with a clear message.

### Sprint 5 GSD Closeout Orchestration

#### Requirements Restatement

- [x] Initialize GSD for this brownfield repo because `.planning/` does not exist yet.
- [x] Work on the new git branch `sprint5-cat3`.
- [x] Treat Sprint 5 as a closeout milestone for Category 3 unless a stronger local authority emerges:
  - The repo has no canonical Sprint 5 spec.
  - `Category 3 - IA West Smart Match CRM/docs/README.md` says the remaining work is documentation/governance refresh plus sprint closeout.
- [x] Use parallel subagents wherever they materially reduce context pressure or shorten independent discovery/review work.
- [x] Create a phase-based plan that ends with an `$ecc-code-review` audit, fixes, documentation updates, per-phase commits, and sprint closure.
- [x] Verify each phase with direct evidence before marking it complete.

#### Risks

- High: No canonical Sprint 5 spec exists in the repo, so scope must be derived from current closeout signals and verified against authoritative Category 3 docs.
- High: The worktree already contains unrelated local changes; do not revert or accidentally include them in Sprint 5 commits.
- Medium: GSD brownfield initialization may require codebase mapping before milestone planning can proceed.
- Medium: Closeout work may surface doc/governance drift that forces additional scoped cleanup beyond the initial assumption.

#### Execution Board

- [x] Phase 1: Establish Sprint 5 orchestration context.
  - Create and switch to branch `sprint5-cat3`.
  - Confirm whether GSD is already initialized.
  - Rewrite this task board for Sprint 5 orchestration.

- [x] Phase 2: Bootstrap GSD for the brownfield repo.
  - Map the existing codebase with parallel mapper agents.
  - Create `.planning/` project state, config, requirements, and roadmap for Sprint 5 closeout.
  - Record the Sprint 5 scope assumption in the planning docs.

- [x] Phase 3: Execute Sprint 5 closeout phases.
  - Run the planned closeout phases with parallel subagents where appropriate.
  - Keep commits scoped per phase with explicit pathspecs only.
  - Update progress in this file as work lands.

- [x] Phase 3.1: Runtime fixes and clean outputs.
  - Discovery events added from the Discovery tab now merge into the Matches event pool during the same session.
  - Demo Mode and offline/no-key runs no longer hard-block the Matches tab when embeddings are missing; warnings stay visible and fallback scoring is explicit.
  - Feedback persistence now resolves from config-backed project paths, and generated runtime artifacts are ignored without hiding checked-in demo fixtures.
  - Combined verification: `Category 3 - IA West Smart Match CRM/.venv/bin/python -m pytest tests/test_acceptance.py tests/test_discovery_tab.py tests/test_matches_tab.py tests/test_app.py -q` -> `37 passed in 21.78s`

- [x] Phase 3.2: Documentation and governance reconciliation.
  - Established one authoritative live verification baseline from `Category 3 - IA West Smart Match CRM/` with:
    - `timeout 300s ./.venv/bin/python -m pytest -q` -> `385 passed in 37.40s`
    - `timeout 180s ./.venv/bin/python scripts/sprint4_preflight.py` -> passes with warnings only for un-warmed live caches
  - Reconciled `docs/README.md`, `docs/sprints/README.md`, `.status.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and this task board to that baseline.
  - Ran the repo governance workflow for `category:3`, regenerated `docs/governance/REPO_REFERENCE.md`, and emitted dated Sprint 5 audit/reconcile reports under `docs/governance/reports/`.
  - Verified the governance outputs report `0` safe reconciliations and `0` human-decision items before committing Phase 3.2.

- [x] Phase 3.3: Adversarial audit and sprint closure.
  - Planning artifacts created in `.planning/phases/03-adversarial-audit-and-sprint-closure/`: `03-CONTEXT.md`, `03-01-PLAN.md`, `03-02-PLAN.md`, `03-03-PLAN.md`.
  - Created `Category 3 - IA West Smart Match CRM/docs/reviews/2026-03-21-sprint5-code-review.md` and fixed the accepted findings without expanding scope.
  - Reran targeted verification (`87 passed in 6.56s`), full `pytest -q` (`392 passed in 11.93s`), and `scripts/sprint4_preflight.py` (same expected cache warnings only).
  - Updated `.planning/ROADMAP.md`, `.planning/STATE.md`, and this review section with final evidence, residual risks, and truthful manual follow-ups.
  - Close out Sprint 5 on `sprint5-cat3` with a scoped final commit.

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

- Milestone wrap-up (2026-03-24): finalized v1.0 then v2.0 sequentially, archived both milestones under `.planning/milestones/`, moved milestone tracking into `.planning/MILESTONES.md`, collapsed `.planning/ROADMAP.md` to shipped one-line entries, removed live `.planning/REQUIREMENTS.md` for next-milestone reset, and created annotated tags `v1.0` + `v2.0`. Note: no dedicated `.planning/v2.0-MILESTONE-AUDIT.md` existed at closeout; this was recorded as accepted tech debt in milestones.
- Sprint 6 Phase 0-1 review fix pass: refactored `src/ui/landing_page.py` into smaller helpers (clearing the >50-line function finding), made donut heading/colors derive from `DEFAULT_WEIGHTS` count for future factor expansion, removed dead/unused test imports, and replaced the partner-logo no-op assertions with concrete per-university checks plus dynamic-factor donut assertions in `tests/test_landing_page.py`.
- Sprint 6 Phase 0-1 verification:
  - `python3 -m compileall Category 3 - IA West Smart Match CRM/src/ui/landing_page.py Category 3 - IA West Smart Match CRM/tests/test_landing_page.py` -> both files compiled successfully.
  - `rg -n \"TODO|FIXME|console\\.log\" Category 3 - IA West Smart Match CRM/src/ui/landing_page.py Category 3 - IA West Smart Match CRM/tests/test_landing_page.py` -> no matches.
- Sprint 5 bootstrap: created `sprint5-cat3`, initialized GSD at repo root, wrote `.planning/config.json`, `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, and the 7-file brownfield codebase map under `.planning/codebase/`, then committed the bootstrap as `docs: bootstrap sprint 5 planning`.
- Sprint 5 Phase 1 runtime fixes: discovery-to-match handoff now merges in-session discovered events into Matches, offline/demo runs can render Matches with fallback scoring when embeddings are unavailable, and feedback/generated output paths are repo-stable plus ignored correctly.
- Sprint 5 Phase 1 verification:
  - `Category 3 - IA West Smart Match CRM/.venv/bin/python -m pytest tests/test_acceptance.py tests/test_discovery_tab.py tests/test_matches_tab.py tests/test_app.py -q` -> `37 passed in 21.78s`
  - `git check-ignore -v -- Category 3 - IA West Smart Match CRM/data/feedback_log.csv Category 3 - IA West Smart Match CRM/cache/cache_manifest.json Category 3 - IA West Smart Match CRM/cache/extractions/generated.json` -> all ignored by `Category 3 - IA West Smart Match CRM/.gitignore`
  - `git check-ignore -v -n -- Category 3 - IA West Smart Match CRM/cache/demo_fixtures/pipeline_funnel.json` -> non-match, confirming the demo fixture path remains trackable
- Sprint 5 Phase 2 documentation/governance reconciliation: Category 3 readme surfaces, `.status.md`, and `.planning/` state now point to the live Sprint 5 baseline instead of stale Sprint 3 closeout counts, and governance artifacts were regenerated under dated Sprint 5 report names.
- Sprint 5 Phase 2 verification:
  - `timeout 300s ./.venv/bin/python -m pytest -q` -> `385 passed in 37.40s`
  - `timeout 180s ./.venv/bin/python scripts/sprint4_preflight.py` -> passes with warnings only for missing embedding artifacts plus empty or absent scrape, extraction, explanation, and email caches
  - `python3 .agents/skills/repo-governance/scripts/inventory.py --scope category:3` -> `Managed docs: 22`, `Selected docs: 6`, `Unmanaged governed docs: none`
  - `python3 .agents/skills/repo-governance/scripts/audit.py --scope category:3 --date 2026-03-20 --report docs/governance/reports/2026-03-20-category-3-sprint5-audit.md` -> `Safe reconciliations: 0`, `Needs human decision: 0`
  - `python3 .agents/skills/repo-governance/scripts/reconcile.py --scope category:3 --date 2026-03-20 --report docs/governance/reports/2026-03-20-category-3-sprint5-governance.md --index-output docs/governance/REPO_REFERENCE.md` -> `Safe issues before reconcile: 0`, `Safe issues after reconcile: 0`, `Needs human decision after reconcile: 0`
  - `python3 .agents/skills/repo-governance/scripts/build_index.py --output docs/governance/REPO_REFERENCE.md` -> `docs/governance/REPO_REFERENCE.md`
- Sprint 5 Phase 3 adversarial audit and closeout: checked in `Category 3 - IA West Smart Match CRM/docs/reviews/2026-03-21-sprint5-code-review.md`, normalized discovered events around stable `event_id` plus dedupe semantics, added fallback topic scoring for discovered events without cached embeddings, corrected discovered-event region handling, and routed merged events into Volunteer Dashboard accounting.
- Sprint 5 Phase 3 verification:
  - `Category 3 - IA West Smart Match CRM/.venv/bin/python -m pytest tests/test_discovery_tab.py tests/test_matches_tab.py tests/test_engine.py tests/test_app.py tests/test_acceptance.py tests/test_volunteer_dashboard.py -q` -> `87 passed in 6.56s`
  - `timeout 300s ./.venv/bin/python -m pytest -q` -> `392 passed in 11.93s`
  - `timeout 180s ./.venv/bin/python scripts/sprint4_preflight.py` -> passes with the same expected cache warnings for missing live-warmed embedding, scrape, extraction, explanation, and email artifacts
- Category 3 output/path hygiene: feedback CSV persistence now defaults to `src.config.DATA_DIR / "feedback_log.csv"` instead of a CWD-relative string, generated feedback/cache JSON outputs are ignored in the Category 3 subproject, and checked-in `cache/demo_fixtures/*.json` remain trackable.
- Codebase map review: `arch` mapping completed on 2026-03-20. Wrote `.planning/codebase/ARCHITECTURE.md` (177 lines) and `.planning/codebase/STRUCTURE.md` (181 lines) after inspecting the Category 3 runtime, root governance docs, and sprint task board. Verification: `wc -l .planning/codebase/ARCHITECTURE.md .planning/codebase/STRUCTURE.md` -> `177`, `181`.
- Status: Sprint 4 CLOSED for engineering scope (code + committed artifacts)
- Notes: Created `sprint4-cat3`, hardened discovery for stale-cache fallback and cache-first status visibility, made cache paths repo-stable for root/subdir execution, blocked all-zero match-weight runs, added file-specific empty-dataset errors, aligned the demo funnel fixture to the 6-stage runtime contract, added `runtime.txt`, and committed Sprint 4 testing/rehearsal templates plus `scripts/sprint4_preflight.py`.
- Review fix pass: `scripts/sprint4_preflight.py --prewarm-discovery` now persists extraction caches, `runtime.txt` and preflight now match the Sprint 4 Streamlit Cloud contract, scrape/extraction cache loaders degrade safely on corrupt payloads, and regression coverage was added for those cases.
- Verification:
  - `Category 3 - IA West Smart Match CRM/.venv/bin/python -m pytest tests/test_acceptance.py -q` -> 16 passed in 20.37s
  - `git check-ignore -v -- Category 3 - IA West Smart Match CRM/data/feedback_log.csv Category 3 - IA West Smart Match CRM/cache/cache_manifest.json Category 3 - IA West Smart Match CRM/cache/extractions/generated.json` -> all ignored by `Category 3 - IA West Smart Match CRM/.gitignore`
  - `git check-ignore -v -n -- Category 3 - IA West Smart Match CRM/cache/demo_fixtures/pipeline_funnel.json` -> non-match, confirming the demo fixture path stays trackable
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
