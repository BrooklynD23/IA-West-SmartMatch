---
plan: 14-02
phase: 14-visual-resilience
status: complete
completed: 2026-03-27
subsystem: frontend
tags: [visual-resilience, demo-mode, mock-data, layer-3-fallback, react]
dependency_graph:
  requires: ["14-01"]
  provides: ["POLISH-04", "POLISH-05"]
  affects: ["frontend/src/lib/api.ts", "frontend/src/lib/mockData.ts", "frontend/src/app/pages/Dashboard.tsx", "frontend/src/app/pages/AIMatching.tsx", "frontend/src/app/pages/Pipeline.tsx", "frontend/src/app/pages/Volunteers.tsx"]
tech_stack:
  added: []
  patterns: ["WithSource<T> wrapper for API responses", "isMockData page-level flag", "Layer-3 React constants safety net"]
key_files:
  created:
    - "Category 3 - IA West Smart Match CRM/frontend/src/lib/mockData.ts"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/components/ui/DemoModeBadge.tsx"
  modified:
    - "Category 3 - IA West Smart Match CRM/frontend/src/lib/api.ts"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Dashboard.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Opportunities.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Outreach.tsx"
    - "Category 3 - IA West Smart Match CRM/frontend/src/components/FeedbackForm.tsx"
decisions:
  - "WithSource<T> wrapper exposes source field from all fetch functions; callers destructure {data, source} to detect demo mode"
  - "isMockData is page-level (one boolean per page); true if ANY data source on that page is demo or backend-unreachable"
  - "Layer-3 constants activate in catch blocks only (backend completely unreachable); Layer-2 demo.db data flows normally when backend is up"
  - "DemoModeBadge renders inline next to h1 heading using conditional rendering: {isMockData && <DemoModeBadge />}"
metrics:
  duration: "21 minutes"
  completed_date: "2026-03-27"
  tasks: 2
  files_created: 2
  files_modified: 9
---

# Phase 14 Plan 02: React Layer-3 Mock Data, DemoModeBadge, and WithSource API Wrappers

## What Was Built

React Layer-3 visual resilience: typed mock data constants, a "Demo Mode" badge component, updated API fetch functions exposing data source, and four chart-bearing pages wired to display fallback data with a discrete badge indicator.

### 1. `frontend/src/lib/mockData.ts` — Layer-3 constants

8 typed exports covering all chart-bearing pages:
- `MOCK_SPECIALISTS` (10 records) — same specialist names as demo.db for cross-page coherence
- `MOCK_PIPELINE` (20 records) — funnel-distributed across all 5 stages (Matched/Contacted/Confirmed/Attended/Member Inquiry)
- `MOCK_EVENTS` (5 events) — matching demo.db CPP event catalog
- `MOCK_CALENDAR_EVENTS` (5 events) — with all coverage_status, region, assignment fields
- `MOCK_CALENDAR_ASSIGNMENTS` (3 assignments) — with fatigue/recovery metadata
- `MOCK_QR_STATS` — 5 entries, 42 scans, 12 conversions, conversion_rate
- `MOCK_FEEDBACK_STATS` — 8 feedback records, 62.5% accept rate, trend/weights/history
- `MOCK_RANKED_MATCHES` (5 matches) — factor_scores and weighted_factor_scores for AI Matching

### 2. `frontend/src/app/components/ui/DemoModeBadge.tsx`

Single-responsibility component rendering blue pill badge:
```tsx
<span className="ml-2 inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
  Demo Mode
</span>
```
Non-dismissible, inline next to section heading, disappears when all sources are live.

### 3. `frontend/src/lib/api.ts` — WithSource<T> wrapper

Added `WithSource<T>` type and updated all chart-feeding fetch functions:
- `fetchSpecialists()` → `Promise<WithSource<Specialist[]>>`
- `fetchEvents()` → `Promise<WithSource<CppEvent[]>>`
- `fetchPipeline()` → `Promise<WithSource<PipelineRecord[]>>`
- `fetchCalendarEvents()` → `Promise<WithSource<CalendarEventSummary[]>>`
- `fetchCalendarAssignments()` → `Promise<WithSource<CalendarAssignmentSummary[]>>`
- `fetchQrStats()` → `Promise<WithSource<QrStatsSummary>>`
- `fetchFeedbackStats()` → `Promise<WithSource<FeedbackStatsSummary>>`

Source detection: list endpoints read `payload[0]?.source === "demo"`; dict endpoints read `payload?.source === "demo"`.

### 4. Dashboard, AIMatching, Pipeline, Volunteers — isMockData wiring

Each page now:
1. Has `const [isMockData, setIsMockData] = useState(false)` state
2. Destructures `{ data, source }` from all fetch results
3. Sets `anyMock = true` if any source equals `"demo"` (Layer-2 demo.db)
4. Falls back to `MOCK_*` constants in catch blocks (Layer-3, backend unreachable)
5. Renders `{isMockData && <DemoModeBadge />}` inline in the `<h1>` heading

## Commits

| Task | Commit | Description |
|------|--------|-------------|
| Task 1 | 4b21451 | mockData constants, DemoModeBadge, WithSource api wrappers + Calendar.tsx fix |
| Task 2 | 1d626e8 | wire isMockData and DemoModeBadge into all 4 chart pages |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Calendar.tsx: fetchCalendarEvents/fetchCalendarAssignments call sites**
- **Found during:** Task 1 verification
- **Issue:** Calendar.tsx uses both `fetchCalendarEvents()` and `fetchCalendarAssignments()` which were updated to return `WithSource<T>`, breaking compilation
- **Fix:** Updated Calendar.tsx to destructure `.data` from the `WithSource` wrapper on both fetch results
- **Files modified:** `frontend/src/app/pages/Calendar.tsx`
- **Commit:** 4b21451

**2. [Rule 3 - Blocking] Opportunities.tsx, Outreach.tsx, FeedbackForm.tsx: additional WithSource callers**
- **Found during:** Task 2 TSC verification
- **Issue:** Three more files used `fetchEvents()`, `fetchSpecialists()`, `fetchFeedbackStats()` which returned raw types; now return `WithSource<T>` requiring destructuring
- **Fix:** Updated all three to destructure `.data` from the WithSource wrapper
- **Files modified:** `frontend/src/app/pages/Opportunities.tsx`, `frontend/src/app/pages/Outreach.tsx`, `frontend/src/components/FeedbackForm.tsx`
- **Commit:** 1d626e8

**3. [Rule 1 - Bug] api.ts shorthand property bugs (pre-existing)**
- **Found during:** Task 2 TSC verification (errors existed before Task 1 changes)
- **Issue:** `normalizeCalendarEvent` return object used bare property names (`coverage_ratio`, `assigned_volunteers`, `assignment_count`, `open_slots`) as shorthand but local variables used camelCase names (`coverageRatio`, `assignedVolunteers`, etc.). Similarly `volunteer_fatigue` shorthand in `normalizeVolunteerRecovery`.
- **Fix:** Replaced shorthand with explicit key-value form for all 5 fields
- **Files modified:** `frontend/src/lib/api.ts`
- **Commit:** 1d626e8

**4. [Rule 1 - Bug] TypeScript `.reason` narrowing issues (introduced by WithSource)**
- **Found during:** Task 2 TSC verification
- **Issue:** Pattern `throw calendarResult.reason` fails when TypeScript can't narrow `calendarResult` to `PromiseRejectedResult` in cascading condition chains; same in Pipeline.tsx and Volunteers.tsx
- **Fix:** Added `as PromiseRejectedResult` cast on the final ternary branch in all 3 pages
- **Files modified:** Dashboard.tsx, Pipeline.tsx, Volunteers.tsx
- **Commit:** 1d626e8

**5. [Rule 2 - Missing functionality] AIMatching: MOCK_RANKED_MATCHES safety net**
- **Found during:** Task 2 implementation (per plan specification)
- **Issue:** When `rankSpeakers()` fails and the page is already in mock mode (events were from demo.db), returning empty matches `[]` still shows broken state
- **Fix:** In the rank failure catch block, use `MOCK_RANKED_MATCHES` when `isMockData` is already true
- **Files modified:** `frontend/src/app/pages/AIMatching.tsx`
- **Commit:** 1d626e8

### Out of Scope (Deferred)

- LandingPage.tsx and LoginPage.tsx framer-motion type errors (pre-existing, unrelated files)
- Chunk-size build warning (pre-existing, Phase 15 scope)

These were logged but not fixed per scope boundary rules.

## Known Stubs

None — all 8 MOCK_* constants are fully populated with realistic data matching demo.db specialist names, event names, and cross-table coherence. DemoModeBadge renders complete UI. All 4 pages are wired end-to-end.

## Self-Check: PASSED

- ✓ `frontend/src/lib/mockData.ts` exists and exports all 8 MOCK_* constants
- ✓ `frontend/src/app/components/ui/DemoModeBadge.tsx` exists with "Demo Mode" text and blue pill classes
- ✓ `frontend/src/lib/api.ts` contains `WithSource` type and 7 updated fetch functions
- ✓ All 4 pages have `isMockData` state (9 isMockData references across pages)
- ✓ All 4 pages import and render `DemoModeBadge` conditionally
- ✓ `npx tsc --noEmit` produces only pre-existing framer-motion errors in LandingPage/LoginPage (unrelated to this plan)
- ✓ `npm run build` succeeds (built in 3m 38s, 1042.85 kB bundle)
- ✓ Commits exist: 4b21451, 1d626e8
