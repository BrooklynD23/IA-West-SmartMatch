# Architecture

**Analysis Date:** 2026-03-26

## Pattern Overview

**Overall:** Hybrid product slice with one shared Python domain core reused by a Streamlit operator app, a FastAPI REST adapter, and a separate Vite/React frontend, all surrounded by repo-level governance and planning artifacts.

**Key Characteristics:**
- `Category 3 - IA West Smart Match CRM/src/` is the shared application package. `Category 3 - IA West Smart Match CRM/src/app.py` and `Category 3 - IA West Smart Match CRM/src/api/main.py` both compose features from the same data, matching, outreach, feedback, and QR modules instead of maintaining separate service implementations.
- `Category 3 - IA West Smart Match CRM/frontend/src/` is a separate presentation surface. It never imports Python code directly; it consumes `/api/*` through `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`, where backend payloads are normalized into stable TypeScript contracts.
- Durable application state is file-backed. Canonical inputs live under `Category 3 - IA West Smart Match CRM/data/`; generated caches live under `Category 3 - IA West Smart Match CRM/cache/`; engagement telemetry is persisted under `Category 3 - IA West Smart Match CRM/data/feedback/` and `Category 3 - IA West Smart Match CRM/data/qr/`.
- Streamlit navigation is URL-synchronized through `Category 3 - IA West Smart Match CRM/src/ui/page_router.py` and `st.session_state`; React navigation is route-driven through `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx` and page-local component state.

## Layers

**Governance And Planning Layer:**
- Purpose: Own repo workflow rules, sprint authority, task tracking, generated codebase maps, and category-level documentation boundaries.
- Location: `Agents.md`, `tasks/todo.md`, `tasks/lessons.md`, `.planning/codebase/`, `docs/governance/canonical-map.yaml`, `docs/governance/REPO_REFERENCE.md`, `Category 3 - IA West Smart Match CRM/docs/README.md`, `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`, `Category 3 - IA West Smart Match CRM/.status.md`
- Contains: workflow rules, execution boards, lessons learned, canonical ownership maps, generated codebase docs, category read-order guidance, and status checkpoints.
- Depends on: checked-in repo state plus generated reports under `docs/governance/reports/`.
- Used by: GSD commands, repo governance tooling, and any engineering pass that needs the current source of truth before touching code.

**Configuration And Data Boundary Layer:**
- Purpose: Define runtime paths, environment-backed settings, factor defaults, and CSV schemas.
- Location: `Category 3 - IA West Smart Match CRM/src/config.py`, `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`
- Contains: filesystem roots, Gemini model settings, factor registry metadata, `LoadedDatasets`, `DataQualityResult`, schema validation, and cached file readers for CSV/JSON/JSONL data.
- Depends on: the product root `Category 3 - IA West Smart Match CRM/data/`, `Category 3 - IA West Smart Match CRM/cache/`, environment variables, and optional Streamlit secrets.
- Used by: every Python execution surface, including `Category 3 - IA West Smart Match CRM/src/app.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/*.py`, and several coordinator or UI helpers.

**Shared Domain Services Layer:**
- Purpose: Implement matching, discovery, extraction, outreach, feedback optimization, QR tracking, and utility logic independent of any one UI framework.
- Location: `Category 3 - IA West Smart Match CRM/src/matching/`, `Category 3 - IA West Smart Match CRM/src/scraping/`, `Category 3 - IA West Smart Match CRM/src/extraction/`, `Category 3 - IA West Smart Match CRM/src/outreach/`, `Category 3 - IA West Smart Match CRM/src/feedback/`, `Category 3 - IA West Smart Match CRM/src/qr/`, `Category 3 - IA West Smart Match CRM/src/utils.py`, `Category 3 - IA West Smart Match CRM/src/similarity.py`
- Contains: factor scoring, ranking, scrape orchestration, Gemini extraction, explanation generation, outreach email generation, ICS generation, pipeline mutation, feedback persistence, weight optimization, QR generation, scan logging, and formatting helpers.
- Depends on: the configuration/data boundary plus cache or data subdirectories such as `Category 3 - IA West Smart Match CRM/cache/explanations/`, `Category 3 - IA West Smart Match CRM/cache/scrapes/`, `Category 3 - IA West Smart Match CRM/data/feedback/`, and `Category 3 - IA West Smart Match CRM/data/qr/`.
- Used by: Streamlit UI modules, FastAPI routers, coordinator tool wrappers, verification scripts, and tests under `Category 3 - IA West Smart Match CRM/tests/`.

**Streamlit Application Shell Layer:**
- Purpose: Assemble the operator-facing workspace, route between pages, and coordinate shared in-memory session state.
- Location: `Category 3 - IA West Smart Match CRM/src/app.py`, `Category 3 - IA West Smart Match CRM/src/runtime_state.py`, `Category 3 - IA West Smart Match CRM/src/demo_mode.py`, `Category 3 - IA West Smart Match CRM/src/ui/`
- Contains: page bootstrapping, sidebar composition, query-param routing, demo-mode toggles, normalized session keys, HTML-backed landing/login pages, native workspace pages, and tab/page-specific rendering.
- Depends on: configuration, loaded datasets, embedding caches, domain services, and `st.session_state`.
- Used by: `streamlit run src/app.py`, screenshot automation, Playwright demo runs, and human demo flows.

**Coordinator And HITL Layer:**
- Purpose: Add an operator command center with intent parsing, approval gates, tool dispatch, and lightweight background execution.
- Location: `Category 3 - IA West Smart Match CRM/src/coordinator/`, `Category 3 - IA West Smart Match CRM/src/ui/command_center.py`, `Category 3 - IA West Smart Match CRM/src/ui/swimlane_dashboard.py`
- Contains: `ActionProposal`, Gemini-or-keyword intent parsing, proactive suggestion rules, tool registry wiring, queue-based result dispatch, and command-center UI.
- Depends on: shared domain services, `Category 3 - IA West Smart Match CRM/src/gemini_client.py`, `st.session_state`, and tool wrappers under `Category 3 - IA West Smart Match CRM/src/coordinator/tools/`.
- Used by: the Streamlit dashboard path in `Category 3 - IA West Smart Match CRM/src/app.py` when Jarvis is enabled.

**FastAPI Adapter Layer:**
- Purpose: Expose the Python domain services as JSON endpoints for the promoted React frontend and API-oriented tests.
- Location: `Category 3 - IA West Smart Match CRM/src/api/main.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/`
- Contains: app construction, CORS policy, router registration, Pydantic request models, response normalization, and HTTP error translation.
- Depends on: shared domain services plus some file-reader helpers in `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`.
- Used by: `Category 3 - IA West Smart Match CRM/frontend/` through `/api/*`, router tests such as `Category 3 - IA West Smart Match CRM/tests/test_api_matching.py`, and any local `uvicorn src.api.main:app` run.

**React Frontend Layer:**
- Purpose: Provide a standalone coordinator-facing SPA that consumes the FastAPI layer instead of sharing Streamlit state.
- Location: `Category 3 - IA West Smart Match CRM/frontend/src/app/`, `Category 3 - IA West Smart Match CRM/frontend/src/components/`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`
- Contains: browser-router entry points, dashboard pages, AI matching flows, outreach and QR widgets, design-system primitives, and request/response normalization helpers.
- Depends on: Vite dev proxy in `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts`, route definitions in `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`, and the FastAPI `/api/*` endpoints.
- Used by: `vite` dev/build flows and any deployment or local preview of the React client.

**Operational And Verification Layer:**
- Purpose: Start local development surfaces, validate the runtime, and capture QA evidence.
- Location: `Category 3 - IA West Smart Match CRM/scripts/`, `Makefile`, `Category 3 - IA West Smart Match CRM/output/playwright/`, `Category 3 - IA West Smart Match CRM/docs/testing/`
- Contains: startup scripts, the legacy dev health stub, preflight checks, screenshot automation, E2E harnesses, and stored Playwright artifacts.
- Depends on: the product runtime modules plus local Python or Node environments.
- Used by: manual developer workflows, verification runs, and planning/closeout evidence gathering.

## Data Flow

**Streamlit Routed Workspace Flow:**

1. `streamlit run src/app.py` enters `Category 3 - IA West Smart Match CRM/src/app.py`, sets page config, injects shared CSS, and initializes `st.session_state` through `Category 3 - IA West Smart Match CRM/src/runtime_state.py`.
2. `Category 3 - IA West Smart Match CRM/src/ui/page_router.py` reads `route`, `role`, and `demo` query params, normalizes them, mirrors them back into the URL, and decides whether the landing page, login page, or an authenticated workspace page should render.
3. `Category 3 - IA West Smart Match CRM/src/config.py` validates local prerequisites, then `Category 3 - IA West Smart Match CRM/src/data_loader.py` loads the four canonical CSV datasets and emits data-quality warnings.
4. `Category 3 - IA West Smart Match CRM/src/embeddings.py` loads cached embedding maps from `Category 3 - IA West Smart Match CRM/cache/` and can bootstrap missing artifacts when Gemini is configured and demo mode is off.
5. Page modules under `Category 3 - IA West Smart Match CRM/src/ui/` call shared domain services, then persist cross-page state such as `match_results_df`, `matching_discovered_events`, `scraped_events`, `emails_generated`, and `action_proposals`.

**React Plus FastAPI Flow:**

1. `Category 3 - IA West Smart Match CRM/frontend/src/main.tsx` mounts `RouterProvider`, and `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx` selects a public or coordinator route.
2. Page components such as `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx` and `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx` call `fetch*`, `rankSpeakers`, `submitFeedback`, `fetchQrStats`, and related helpers in `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.
3. During local development, `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts` proxies `/api` traffic to `http://localhost:8000`.
4. `Category 3 - IA West Smart Match CRM/src/api/main.py` dispatches those requests to router modules under `Category 3 - IA West Smart Match CRM/src/api/routers/`.
5. Router modules load data or call shared domain services, return normalized JSON payloads, and `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts` performs a second normalization pass so React pages see stable TypeScript shapes even when backend field names vary.

**Discovery To Match To Outreach Flow:**

1. Discovery starts from `Category 3 - IA West Smart Match CRM/src/ui/discovery_tab.py` or the wrapper in `Category 3 - IA West Smart Match CRM/src/coordinator/tools/discovery_tool.py`.
2. `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py` validates the target, honors cache and safety checks, and returns HTML plus source metadata; `Category 3 - IA West Smart Match CRM/src/extraction/llm_extractor.py` converts that HTML into structured event rows.
3. `Category 3 - IA West Smart Match CRM/src/runtime_state.py` merges discovered rows into the matching event contract so downstream ranking can treat them like canonical event records.
4. `Category 3 - IA West Smart Match CRM/src/matching/engine.py` ranks speakers for events or courses, using factor functions from `Category 3 - IA West Smart Match CRM/src/matching/factors.py` and optional pipeline context from `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`.
5. Outreach side effects then fan out through `Category 3 - IA West Smart Match CRM/src/outreach/email_gen.py`, `Category 3 - IA West Smart Match CRM/src/outreach/ics_generator.py`, `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, and `Category 3 - IA West Smart Match CRM/src/qr/service.py`.

**State Management:**
- Streamlit uses `st.session_state` as the live shared store. The cross-page contract is declared in `Category 3 - IA West Smart Match CRM/src/runtime_state.py`, and routing/auth-like state is synchronized through `Category 3 - IA West Smart Match CRM/src/ui/page_router.py`.
- React pages use component-local `useState` and `useEffect` state only. No shared frontend store such as Redux or Zustand is present under `Category 3 - IA West Smart Match CRM/frontend/src/`.
- Durable state is filesystem-backed rather than database-backed. CSV inputs remain under `Category 3 - IA West Smart Match CRM/data/`; caches remain under `Category 3 - IA West Smart Match CRM/cache/`; feedback and QR activity append into JSON or JSONL files under `Category 3 - IA West Smart Match CRM/data/feedback/` and `Category 3 - IA West Smart Match CRM/data/qr/`.

## Key Abstractions

**Loaded Datasets Contract:**
- Purpose: Carry the four canonical CSV DataFrames plus quality-check results through Python execution surfaces.
- Examples: `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/app.py`
- Pattern: `load_all()` returns the immutable `LoadedDatasets` dataclass, and consumers pass that object downward instead of re-reading files.

**Normalized Match Contracts:**
- Purpose: Keep speaker-event ranking output stable across Streamlit, FastAPI, and React.
- Examples: `Category 3 - IA West Smart Match CRM/src/matching/engine.py`, `Category 3 - IA West Smart Match CRM/src/runtime_state.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`
- Pattern: raw ranking dicts are produced once, then normalized into a session-state DataFrame, normalized API payloads, and TypeScript interfaces such as `RankedMatch`.

**Action Proposal Contract:**
- Purpose: Represent coordinator commands as reviewable, stateful units before tool execution.
- Examples: `Category 3 - IA West Smart Match CRM/src/coordinator/approval.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/result_bus.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/tools/__init__.py`
- Pattern: `ActionProposal` instances move through `proposed` to `approved` or `rejected`, then `dispatch()` runs the mapped tool in a background thread and `poll_results()` feeds completion back into the UI.

**File-Backed Telemetry Contracts:**
- Purpose: Persist operational learning without introducing a database.
- Examples: `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`, `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`
- Pattern: append-only JSONL plus companion JSON summary files are written under `Category 3 - IA West Smart Match CRM/data/feedback/` and `Category 3 - IA West Smart Match CRM/data/qr/`, then cached loader helpers expose those files back to the app.

**HTML Navigation Bridge:**
- Purpose: Let full-page HTML fragments inside Streamlit drive the real router.
- Examples: `Category 3 - IA West Smart Match CRM/src/ui/html_base.py`, `Category 3 - IA West Smart Match CRM/src/ui/landing_page_v2.py`, `Category 3 - IA West Smart Match CRM/src/ui/login_page.py`
- Pattern: `render_html_page()` injects `window.iaSmartMatch.navigate(...)`, which rewrites the parent window query params so `Category 3 - IA West Smart Match CRM/src/ui/page_router.py` can re-enter the correct Streamlit page on rerun.

## Entry Points

**Streamlit Product App:**
- Location: `Category 3 - IA West Smart Match CRM/src/app.py`
- Triggers: `streamlit run src/app.py`, `python -m streamlit run src/app.py`, or `make run CAT=3`
- Responsibilities: validate config, initialize shared session state, load datasets, resolve route state, and render the operator-facing Streamlit shell.

**FastAPI Product Backend:**
- Location: `Category 3 - IA West Smart Match CRM/src/api/main.py`
- Triggers: `uvicorn src.api.main:app` or any test importing `app` from `Category 3 - IA West Smart Match CRM/src/api/main.py`
- Responsibilities: construct the API app, apply CORS, register routers, and expose JSON endpoints consumed by the React frontend.

**React Frontend:**
- Location: `Category 3 - IA West Smart Match CRM/frontend/src/main.tsx`
- Triggers: `npm run dev`, `npm run build`, or `vite preview` from `Category 3 - IA West Smart Match CRM/frontend/`
- Responsibilities: mount the browser router, render coordinator/public pages, call `/api/*`, and present the promoted V1.1/V1.2 UI.

**Legacy Dev Health Stub:**
- Location: `Category 3 - IA West Smart Match CRM/scripts/dev_backend.py`
- Triggers: `Category 3 - IA West Smart Match CRM/scripts/start_dev.sh`, `Category 3 - IA West Smart Match CRM/scripts/start_dev.ps1`, and `Category 3 - IA West Smart Match CRM/scripts/start_dev.cmd`
- Responsibilities: serve only `/` and `/health` for local startup flows; it is not the full FastAPI product backend.

**Verification And Artifact Capture:**
- Location: `Category 3 - IA West Smart Match CRM/scripts/sprint4_preflight.py`, `Category 3 - IA West Smart Match CRM/scripts/capture_screenshots.py`, `Category 3 - IA West Smart Match CRM/scripts/run_playwright_demo_qa.py`
- Triggers: manual QA, preflight verification, and documentation capture passes
- Responsibilities: validate runtime assumptions, warm selected caches, and write evidence into `Category 3 - IA West Smart Match CRM/output/playwright/` or the docs tree.

## Error Handling

**Strategy:** Validate early at the boundary, translate exceptions at UI and HTTP edges, and prefer cache-backed or empty-state fallbacks over process-level crashes for scrape and AI workflows.

**Patterns:**
- `Category 3 - IA West Smart Match CRM/src/app.py` calls `validate_config()`, renders explicit `st.error(...)` messages, and uses `st.stop()` when local prerequisites or datasets are invalid.
- `Category 3 - IA West Smart Match CRM/src/data_loader.py` records structural issues in `DataQualityResult` instead of silently tolerating schema drift.
- `Category 3 - IA West Smart Match CRM/src/api/routers/*.py` catch unexpected exceptions and convert them into `HTTPException` responses with `_server_error(...)`, while keeping router-local validation in Pydantic request models.
- `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`, `Category 3 - IA West Smart Match CRM/src/extraction/llm_extractor.py`, `Category 3 - IA West Smart Match CRM/src/matching/explanations.py`, and `Category 3 - IA West Smart Match CRM/src/outreach/email_gen.py` treat malformed cache entries or live-call failures as fallback conditions whenever possible.
- `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts` centralizes HTTP failure handling in `requestJson(...)` and raises a real `Error` with backend `detail` text so page components can render actionable messages.

## Cross-Cutting Concerns

**Logging:** Python modules under `Category 3 - IA West Smart Match CRM/src/` and `Category 3 - IA West Smart Match CRM/scripts/` use the standard `logging` module. Failures are logged near the integration boundary, then translated into Streamlit warnings/errors or HTTP responses.

**Validation:** Runtime validation is distributed but explicit. `Category 3 - IA West Smart Match CRM/src/config.py` validates environment and filesystem prerequisites; `Category 3 - IA West Smart Match CRM/src/data_loader.py` validates CSV schemas; `Category 3 - IA West Smart Match CRM/src/api/routers/*.py` validate inbound JSON with Pydantic; `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts` normalizes backend payload drift into stable frontend records.

**Authentication:** No persistent server-side auth layer is present. Streamlit uses `user_role` plus query params in `Category 3 - IA West Smart Match CRM/src/ui/page_router.py`; the React login page in `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/LoginPage.tsx` routes directly to `/dashboard`; FastAPI routers do not enforce auth headers or sessions.

---

*Architecture analysis: 2026-03-26*
