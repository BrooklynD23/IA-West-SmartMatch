# Phase 15: Build Quality + Playwright Evidence - Context

**Gathered:** 2026-03-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 15 delivers a clean React production build and committed browser evidence proving the QR and feedback flows work end-to-end. The production build must complete with zero chunk-size warnings, and two Playwright test scripts (plus their screenshot artifacts) must be committed alongside the implementation.

</domain>

<decisions>
## Implementation Decisions

### Build Fix Strategy
- Use `manualChunks` vendor splitting in `vite.config.ts` — proper fix, no source code changes needed
- Split into 4 logical chunks: `react`+`react-dom`+`react-router` (core), `recharts` (charts), `@mui/*`+`@radix-ui/*` (component libs), `@emotion/*` (styling engine)
- All existing vite.config.ts settings (proxy, alias, server, assetsInclude) remain unchanged — only add `build.rollupOptions.output.manualChunks`
- Goal: each chunk under 500 kB, eliminating the current 1,042 kB warning

### Playwright Test Setup
- Python `playwright.sync_api` — consistent with existing `scripts/run_playwright_demo_qa.py` and `tests/test_e2e_playwright.py` patterns
- Test file: `tests/test_react_e2e.py` — pytest-compatible, lives alongside existing Python E2E tests
- Runner script: `scripts/run_react_e2e.py` — standalone entry with auto-retry on connection errors (same pattern as `run_playwright_demo_qa.py`)
- Evidence artifacts: PNG screenshots in `output/playwright/` directory — human-readable for judges

### Backend Strategy for Tests
- Tests target React at `:5173` + FastAPI at `:8000`
- Phase 14 demo.db provides fallback data — tests pass even without real CSVs
- No API mocking needed — demo.db ensures all API endpoints return coherent data
- Tests document required startup sequence in docstring: `start_fullstack.py` or `start_fullstack.sh`

### QR Flow Test Scope
- Navigate to `/outreach` page
- Select a speaker and event from dropdowns (use first available options)
- Click "Generate QR" button
- Assert QR code image renders (check `<img>` with referral QR src OR `data-testid` attribute)
- Capture screenshot as evidence: `output/playwright/react-qr-flow.png`

### Feedback Flow Test Scope
- Navigate to `/ai-matching` page
- Trigger feedback submission (FeedbackForm component — select outcome, submit)
- Assert weight-shift analytics section updates (check for feedback stats counts or weight display)
- Capture screenshot as evidence: `output/playwright/react-feedback-flow.png`

### Claude's Discretion
- Exact CSS selectors or data-testid attributes to target QR image and feedback stats (Claude reads the actual rendered DOM / component source)
- Retry logic and timeout values (follow existing script patterns)
- Whether to use `page.wait_for_selector` or `page.wait_for_load_state` after actions

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/run_playwright_demo_qa.py` — established standalone Playwright runner pattern (snap(), wait_for_body_contains(), auto-retry)
- `tests/test_e2e_playwright.py` — existing pytest-playwright pattern with fixtures
- `Category 3 - IA West Smart Match CRM/frontend/vite.config.ts` — current build config to extend with manualChunks
- `output/playwright/` — existing evidence output directory (used by run_playwright_demo_qa.py)

### Established Patterns
- `QRCodeCard` component in `Outreach.tsx` — renders when `qrAsset` state is populated after API call
- `FeedbackForm` component in `AIMatching.tsx` — submits to feedback API; stats refresh via `fetchFeedbackStats()`
- `isMockData` flag per page (Phase 14) — ensures charts/stats always render with demo.db data
- API at `:8000/api/qr/*` (QR endpoints) and `:8000/api/feedback/*` (feedback endpoints)

### Integration Points
- Vite dev server at `:5173` with proxy to FastAPI at `:8000`
- `start_fullstack.py` / `start_fullstack.sh` — the canonical startup scripts for both servers
- `data/demo.db` — Phase 14 demo database providing fallback data for all endpoints
- React Router routes: `/outreach` → Outreach page, `/ai-matching` → AIMatching page

</code_context>

<specifics>
## Specific Ideas

- Evidence screenshots must be committed to the repo alongside the test scripts — not just generated locally
- The manualChunks split must be verified by running `npm run build` again and confirming no chunk-size warnings in output
- Both test scripts should be runnable with a single command after the stack is started

</specifics>

<deferred>
## Deferred Ideas

- Playwright tests for additional coordinator workflows (beyond QR and feedback) — captured as future requirement
- Playwright trace files / video recording — screenshots sufficient for demo evidence
- CI integration for Playwright tests — beyond hackathon scope

</deferred>
