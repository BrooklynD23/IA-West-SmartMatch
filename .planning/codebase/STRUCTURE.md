# Codebase Structure

**Analysis Date:** 2026-03-26

## Directory Layout

```text
[project-root]/
├── Category 3 - IA West Smart Match CRM/        # Product slice: Python app, React app, data, scripts, tests
│   ├── src/                                     # Shared Python application package
│   │   ├── api/                                 # FastAPI app and routers
│   │   ├── coordinator/                         # Jarvis/HITL command center logic
│   │   ├── matching/                            # Ranking engine, factors, explanations
│   │   ├── outreach/                            # Email, ICS, pipeline update services
│   │   ├── feedback/                            # File-backed feedback and optimizer services
│   │   ├── qr/                                  # QR generation and ROI tracking
│   │   ├── scraping/                            # University discovery and cache logic
│   │   ├── extraction/                          # LLM event extraction
│   │   ├── ui/                                  # Streamlit pages, routing, visual helpers
│   │   └── voice/                               # STT/TTS wrappers for Jarvis
│   ├── frontend/                                # Vite/React SPA
│   │   ├── src/app/                             # Route shell, pages, app-local components
│   │   ├── src/components/                      # Reusable feature widgets
│   │   ├── src/lib/                             # API client and contract normalization
│   │   └── dist/                                # Built frontend assets
│   ├── data/                                    # Canonical CSV inputs and persisted JSON/JSONL outputs
│   ├── cache/                                   # Embedding, scrape, explanation, and demo caches
│   ├── docs/                                    # Category-specific docs, mockups, testing, reviews
│   ├── scripts/                                 # Startup, verification, Playwright, and preflight scripts
│   ├── tests/                                   # Python pytest suite
│   ├── output/                                  # Generated Playwright screenshot artifacts
│   └── .streamlit/                              # Streamlit config
├── docs/governance/                             # Repo-level document ownership map and reports
├── tasks/                                       # Active execution board and lessons
├── .planning/codebase/                          # Generated codebase map documents
├── Agents.md                                    # Repo workflow rules
├── PRD_SECTION_CAT3.md                          # Category 3 feature authority
└── Makefile                                     # Shared category run/test helpers
```

## Directory Purposes

**`Category 3 - IA West Smart Match CRM/src/`:**
- Purpose: Hold the shared Python code that powers Streamlit, FastAPI, and background verification scripts.
- Contains: `Category 3 - IA West Smart Match CRM/src/app.py`, configuration, file readers, domain services, UI modules, and runtime-state helpers.
- Key files: `Category 3 - IA West Smart Match CRM/src/app.py`, `Category 3 - IA West Smart Match CRM/src/config.py`, `Category 3 - IA West Smart Match CRM/src/data_loader.py`, `Category 3 - IA West Smart Match CRM/src/runtime_state.py`

**`Category 3 - IA West Smart Match CRM/src/api/`:**
- Purpose: Keep the REST backend separate from Streamlit page rendering while still reusing the same Python services.
- Contains: `Category 3 - IA West Smart Match CRM/src/api/main.py` plus router modules under `Category 3 - IA West Smart Match CRM/src/api/routers/`.
- Key files: `Category 3 - IA West Smart Match CRM/src/api/main.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/matching.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/feedback.py`, `Category 3 - IA West Smart Match CRM/src/api/routers/qr.py`

**`Category 3 - IA West Smart Match CRM/src/coordinator/`:**
- Purpose: Isolate Jarvis intent parsing, approval state, tool wrappers, and result-bus orchestration.
- Contains: proposal state, intent parsing, proactive suggestions, NemoClaw adapter notes, and tool registry code.
- Key files: `Category 3 - IA West Smart Match CRM/src/coordinator/approval.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/intent_parser.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/result_bus.py`, `Category 3 - IA West Smart Match CRM/src/coordinator/tools/discovery_tool.py`

**`Category 3 - IA West Smart Match CRM/src/matching/`:**
- Purpose: Own ranking math and explanation generation.
- Contains: factor functions, match-score composition, course/event ranking, and explanation generation.
- Key files: `Category 3 - IA West Smart Match CRM/src/matching/factors.py`, `Category 3 - IA West Smart Match CRM/src/matching/engine.py`, `Category 3 - IA West Smart Match CRM/src/matching/explanations.py`

**`Category 3 - IA West Smart Match CRM/src/scraping/`, `Category 3 - IA West Smart Match CRM/src/extraction/`, `Category 3 - IA West Smart Match CRM/src/outreach/`, `Category 3 - IA West Smart Match CRM/src/feedback/`, `Category 3 - IA West Smart Match CRM/src/qr/`:**
- Purpose: Group cross-cutting service code by workflow stage rather than by UI surface.
- Contains: web scraping, Gemini extraction, outreach generation, pipeline mutation, feedback persistence, optimizer snapshots, QR creation, scan logs, and ROI summaries.
- Key files: `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`, `Category 3 - IA West Smart Match CRM/src/extraction/llm_extractor.py`, `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py`, `Category 3 - IA West Smart Match CRM/src/feedback/service.py`, `Category 3 - IA West Smart Match CRM/src/qr/service.py`

**`Category 3 - IA West Smart Match CRM/src/ui/`:**
- Purpose: Hold the Streamlit presentation layer and the routing helpers that glue HTML fragments, widgets, and session state together.
- Contains: page modules, navigation helpers, design-system wrappers, dashboard views, and email/outreach presentation bridges.
- Key files: `Category 3 - IA West Smart Match CRM/src/ui/page_router.py`, `Category 3 - IA West Smart Match CRM/src/ui/landing_page_v2.py`, `Category 3 - IA West Smart Match CRM/src/ui/coordinator_dashboard.py`, `Category 3 - IA West Smart Match CRM/src/ui/matches_tab.py`, `Category 3 - IA West Smart Match CRM/src/ui/command_center.py`

**`Category 3 - IA West Smart Match CRM/frontend/src/app/`:**
- Purpose: Hold the React app shell, route table, page components, and app-local UI pieces.
- Contains: `RouterProvider` wiring, coordinator/public pages, `Layout`, and the generated design-system primitives under `Category 3 - IA West Smart Match CRM/frontend/src/app/components/ui/`.
- Key files: `Category 3 - IA West Smart Match CRM/frontend/src/app/App.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/components/Layout.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx`

**`Category 3 - IA West Smart Match CRM/frontend/src/components/`:**
- Purpose: Keep reusable React feature widgets separate from the route shell.
- Contains: feedback capture, outreach workflow modal, and QR card widgets reused across coordinator pages.
- Key files: `Category 3 - IA West Smart Match CRM/frontend/src/components/FeedbackForm.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/components/OutreachWorkflowModal.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/components/QRCodeCard.tsx`

**`Category 3 - IA West Smart Match CRM/frontend/src/lib/`:**
- Purpose: Centralize frontend contract normalization and backend access.
- Contains: the single API client module and TypeScript interfaces for backend payloads.
- Key files: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`

**`Category 3 - IA West Smart Match CRM/data/`:**
- Purpose: Store canonical inputs plus file-backed outputs that act like a lightweight database.
- Contains: the four core CSV inputs, `pipeline_sample_data.csv`, point-of-contact JSON, and generated `feedback/` and `qr/` subtrees.
- Key files: `Category 3 - IA West Smart Match CRM/data/data_speaker_profiles.csv`, `Category 3 - IA West Smart Match CRM/data/data_cpp_events_contacts.csv`, `Category 3 - IA West Smart Match CRM/data/data_cpp_course_schedule.csv`, `Category 3 - IA West Smart Match CRM/data/data_event_calendar.csv`, `Category 3 - IA West Smart Match CRM/data/pipeline_sample_data.csv`

**`Category 3 - IA West Smart Match CRM/cache/`:**
- Purpose: Store reproducible generated artifacts and demo fixtures outside the canonical input tree.
- Contains: embedding arrays and manifests at the cache root, scrape responses, explanation caches, and demo fixtures.
- Key files: `Category 3 - IA West Smart Match CRM/cache/cache_manifest.json`, `Category 3 - IA West Smart Match CRM/cache/demo_fixtures/discovery_scan.json`, `Category 3 - IA West Smart Match CRM/cache/demo_fixtures/pipeline_funnel.json`

**`Category 3 - IA West Smart Match CRM/docs/`:**
- Purpose: Keep product-local execution guidance, mockups, reviews, and test artifacts close to the code they describe.
- Contains: the category README, sprint plan, sprint specs, mockup source material, review docs, and testing reports.
- Key files: `Category 3 - IA West Smart Match CRM/docs/README.md`, `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`, `Category 3 - IA West Smart Match CRM/docs/mockup/V1.1/IA-West_UI/`, `Category 3 - IA West Smart Match CRM/docs/testing/2026-03-25-playwright-demo-report.md`

**`Category 3 - IA West Smart Match CRM/scripts/`:**
- Purpose: Hold developer entry scripts, QA helpers, and verification automation.
- Contains: local startup wrappers, a minimal health backend, preflight checks, Playwright utilities, and E2E runners.
- Key files: `Category 3 - IA West Smart Match CRM/scripts/start_dev.sh`, `Category 3 - IA West Smart Match CRM/scripts/dev_backend.py`, `Category 3 - IA West Smart Match CRM/scripts/sprint4_preflight.py`, `Category 3 - IA West Smart Match CRM/scripts/run_playwright_demo_qa.py`

**`Category 3 - IA West Smart Match CRM/tests/`:**
- Purpose: Provide Python regression coverage for shared services, Streamlit routing/UI helpers, and the FastAPI layer.
- Contains: router tests, Streamlit page tests, service tests, command-center tests, and E2E-oriented Python checks.
- Key files: `Category 3 - IA West Smart Match CRM/tests/conftest.py`, `Category 3 - IA West Smart Match CRM/tests/test_app.py`, `Category 3 - IA West Smart Match CRM/tests/test_api_matching.py`, `Category 3 - IA West Smart Match CRM/tests/test_page_router.py`, `Category 3 - IA West Smart Match CRM/tests/test_command_center.py`

**`Category 3 - IA West Smart Match CRM/output/`:**
- Purpose: Hold generated QA artifacts that are separate from hand-written docs.
- Contains: Playwright screenshots and summary JSON outputs.
- Key files: `Category 3 - IA West Smart Match CRM/output/playwright/2026-03-25-summary.json`, `Category 3 - IA West Smart Match CRM/output/playwright/01-landing.png`

**`docs/governance/`:**
- Purpose: Hold repo-level canonical ownership metadata and generated governance reports that apply across planning commands.
- Contains: the canonical map, repo reference index, and dated governance reports.
- Key files: `docs/governance/canonical-map.yaml`, `docs/governance/REPO_REFERENCE.md`, `docs/governance/reports/2026-03-20-category-3-governance.md`, `docs/governance/reports/2026-03-20-category-3-sprint5-audit.md`

**`tasks/`:**
- Purpose: Hold the current execution board and self-correction notes for repo work.
- Contains: the active task checklist and lessons learned.
- Key files: `tasks/todo.md`, `tasks/lessons.md`

**`.planning/codebase/`:**
- Purpose: Hold generated reference docs that later GSD planning or execution phases read directly.
- Contains: `ARCHITECTURE.md`, `STRUCTURE.md`, `STACK.md`, `INTEGRATIONS.md`, `CONVENTIONS.md`, `TESTING.md`, and `CONCERNS.md`.
- Key files: `.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/STRUCTURE.md`

## Key File Locations

**Entry Points:**
- `Category 3 - IA West Smart Match CRM/src/app.py`: Streamlit composition root.
- `Category 3 - IA West Smart Match CRM/src/api/main.py`: FastAPI app construction and router registration.
- `Category 3 - IA West Smart Match CRM/frontend/src/main.tsx`: React SPA bootstrap.
- `Category 3 - IA West Smart Match CRM/scripts/start_dev.sh`: Linux or WSL startup wrapper for Streamlit plus the dev health stub.
- `Category 3 - IA West Smart Match CRM/scripts/dev_backend.py`: health-only backend used by the startup wrappers.
- `Makefile`: shared category run/test helpers from the repo root.

**Configuration:**
- `Category 3 - IA West Smart Match CRM/src/config.py`: Python runtime paths, model names, factor registry, and validation helpers.
- `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts`: React dev server, `/api` proxy, and alias configuration.
- `Category 3 - IA West Smart Match CRM/frontend/tsconfig.json`: TypeScript strictness and the `@/*` path alias.
- `Category 3 - IA West Smart Match CRM/.streamlit/config.toml`: Streamlit runtime/theme settings.
- `Category 3 - IA West Smart Match CRM/.env.example`: environment template for local setup.
- `Category 3 - IA West Smart Match CRM/requirements.txt`: Python dependency list for Streamlit, FastAPI, voice, and verification tooling.

**Core Logic:**
- `Category 3 - IA West Smart Match CRM/src/data_loader.py`: CSV loading and schema validation.
- `Category 3 - IA West Smart Match CRM/src/embeddings.py`: embedding lookup loading and bootstrap generation.
- `Category 3 - IA West Smart Match CRM/src/matching/engine.py`: event and course ranking.
- `Category 3 - IA West Smart Match CRM/src/scraping/scraper.py`: discovery fetch, cache, and URL safety logic.
- `Category 3 - IA West Smart Match CRM/src/extraction/llm_extractor.py`: HTML-to-event extraction.
- `Category 3 - IA West Smart Match CRM/src/feedback/service.py`: feedback persistence and weight optimization.
- `Category 3 - IA West Smart Match CRM/src/qr/service.py`: QR generation, scan logging, and ROI rollups.
- `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`: React-facing API contract normalization.

**Testing:**
- `Category 3 - IA West Smart Match CRM/tests/`: pytest suite root.
- `Category 3 - IA West Smart Match CRM/tests/test_api_data.py`: FastAPI data-router coverage.
- `Category 3 - IA West Smart Match CRM/tests/test_api_feedback.py`: feedback and optimizer API coverage.
- `Category 3 - IA West Smart Match CRM/tests/test_page_router.py`: Streamlit query-param routing coverage.
- `Category 3 - IA West Smart Match CRM/tests/test_command_center.py`: Jarvis command-center coverage.
- `Category 3 - IA West Smart Match CRM/docs/testing/README.md`: manual verification guidance.

## Naming Conventions

**Files:**
- Python application modules use `snake_case.py`: `Category 3 - IA West Smart Match CRM/src/runtime_state.py`
- Python router modules follow `src/api/routers/<domain>.py`: `Category 3 - IA West Smart Match CRM/src/api/routers/calendar.py`
- Python tests follow `tests/test_<area>.py`: `Category 3 - IA West Smart Match CRM/tests/test_api_qr.py`
- React pages and component files use `PascalCase.tsx`: `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/LoginPage.tsx`, `Category 3 - IA West Smart Match CRM/frontend/src/components/QRCodeCard.tsx`
- React support modules use lowercase names: `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`
- Governance and audit reports use date-prefixed kebab case: `docs/governance/reports/2026-03-20-category-3-governance.md`
- Generated codebase map docs use uppercase names: `.planning/codebase/ARCHITECTURE.md`

**Directories:**
- Python package directories are lowercase by domain: `Category 3 - IA West Smart Match CRM/src/matching/`, `Category 3 - IA West Smart Match CRM/src/coordinator/`
- React source directories separate route shell from reusable widgets: `Category 3 - IA West Smart Match CRM/frontend/src/app/`, `Category 3 - IA West Smart Match CRM/frontend/src/components/`, `Category 3 - IA West Smart Match CRM/frontend/src/lib/`
- Support and evidence directories are noun-based and stable: `Category 3 - IA West Smart Match CRM/docs/testing/`, `Category 3 - IA West Smart Match CRM/output/playwright/`, `docs/governance/reports/`

## Where to Add New Code

**New Feature:**
- Primary Python logic: put reusable business logic in the closest domain package under `Category 3 - IA West Smart Match CRM/src/` such as `src/matching/`, `src/outreach/`, `src/feedback/`, or `src/qr/`.
- Streamlit wiring: add or update the page module in `Category 3 - IA West Smart Match CRM/src/ui/`, then register navigation in `Category 3 - IA West Smart Match CRM/src/app.py` or `Category 3 - IA West Smart Match CRM/src/ui/page_router.py` if a new route is needed.
- Tests: add or extend pytest coverage in `Category 3 - IA West Smart Match CRM/tests/`, matching the affected area, for example `Category 3 - IA West Smart Match CRM/tests/test_api_feedback.py` or `Category 3 - IA West Smart Match CRM/tests/test_match_engine_page.py`.

**New API Endpoint:**
- Implementation: add a router module or extend an existing one under `Category 3 - IA West Smart Match CRM/src/api/routers/`.
- Registration: wire it into `Category 3 - IA West Smart Match CRM/src/api/main.py`.
- Frontend contract: add request and normalization helpers in `Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts`.
- Tests: create or update `Category 3 - IA West Smart Match CRM/tests/test_api_<domain>.py`.

**New React Page Or Module:**
- Route page: add the page to `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/` and register it in `Category 3 - IA West Smart Match CRM/frontend/src/app/routes.tsx`.
- Shared widget: place reusable feature widgets in `Category 3 - IA West Smart Match CRM/frontend/src/components/`.
- Design-system primitive: keep app-wide UI primitives under `Category 3 - IA West Smart Match CRM/frontend/src/app/components/ui/`.

**Utilities:**
- Python cross-domain helpers: extend `Category 3 - IA West Smart Match CRM/src/utils.py` only when the helper is truly cross-domain.
- File-backed read or formatting helpers for UI or API layers: prefer `Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py`.
- Operational scripts: place them in `Category 3 - IA West Smart Match CRM/scripts/`.

**Planning Or Governance Updates:**
- Task tracking and review notes: `tasks/todo.md`
- Workflow rules and lessons: `Agents.md`, `tasks/lessons.md`
- Category execution authority: `Category 3 - IA West Smart Match CRM/docs/README.md`, `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`, `Category 3 - IA West Smart Match CRM/.status.md`, `PRD_SECTION_CAT3.md`
- Planner-facing generated reference docs: `.planning/codebase/`

## Special Directories

**`Category 3 - IA West Smart Match CRM/cache/`:**
- Purpose: Generated runtime caches and demo fixtures.
- Generated: Yes
- Committed: Yes

**`Category 3 - IA West Smart Match CRM/frontend/dist/`:**
- Purpose: Built React assets generated from `Category 3 - IA West Smart Match CRM/frontend/src/`.
- Generated: Yes
- Committed: Yes

**`Category 3 - IA West Smart Match CRM/output/playwright/`:**
- Purpose: Stored browser QA screenshots and summary artifacts.
- Generated: Yes
- Committed: Yes

**`Category 3 - IA West Smart Match CRM/docs/mockup/`:**
- Purpose: Design-source and promoted mockup artifacts that inform the Streamlit and React UI implementations.
- Generated: No
- Committed: Yes

**`docs/governance/reports/`:**
- Purpose: Dated governance audit and reconcile outputs.
- Generated: Yes
- Committed: Yes

**`.planning/codebase/`:**
- Purpose: Generated codebase reference docs for future GSD planning and execution phases.
- Generated: Yes
- Committed: Yes

**`Category 3 - IA West Smart Match CRM/.streamlit/`:**
- Purpose: Streamlit runtime configuration.
- Generated: No
- Committed: Yes

---

*Structure analysis: 2026-03-26*
