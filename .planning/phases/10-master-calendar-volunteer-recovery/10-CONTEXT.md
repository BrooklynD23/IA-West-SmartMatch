# Phase 10: Master Calendar + Volunteer Recovery Period - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Promote the existing React calendar and matching surfaces into a coordinator-facing scheduling view that shows all events, volunteer assignments, and a new volunteer fatigue / recovery factor inside the FastAPI-backed ranking flow. This phase must add backend support for calendar assignments and recovery scoring, then expose the result across the Calendar, Volunteers, and AI Matching pages.

</domain>

<decisions>
## Implementation Decisions

### Recovery Scoring Model
- Add a canonical `volunteer_fatigue` factor to the FastAPI matching flow rather than a frontend-only derived badge.
- Compute fatigue from four inputs: days since last assigned event, regional travel burden, event duration / recurrence intensity, and 30-day assignment count.
- Keep the default weight at `0.10`, with weights flowing through the existing `weights` override mechanism in `/api/matching/rank` and `/api/matching/score`.
- Clamp the score to a human-readable 0.0-1.0 range and derive status badges from that output: `Available`, `Needs Rest`, `On Cooldown`.

### Calendar Data & Assignment Contract
- Extend the backend with calendar-specific API endpoints instead of overloading the existing generic `/api/data/calendar` shape.
- Treat the current CSV-backed calendar and pipeline data as the source material; derive assignment overlays from ranked / contacted / confirmed rows rather than inventing a new persistence layer.
- Return one normalized event contract for the React calendar, with color/status metadata baked in for assigned vs unassigned events.
- Keep storage local-file based for hackathon scope; do not introduce a database in this phase.

### React Calendar Experience
- Upgrade the React calendar to support month, week, and day views from the same normalized API contract.
- Preserve the current white/blue visual language and use consistent badge colors to distinguish IA-covered events from events needing volunteers.
- Make assignment state and recovery summaries visible directly in the calendar cards / panels so coordinators do not need to cross-reference multiple pages.
- Prefer reusable chart/calendar primitives already present in the frontend stack before adding new libraries.

### Volunteer & Matching Surfaces
- Show the recovery badge and fatigue meter on volunteer cards and volunteer detail views, not only in the calendar.
- Surface `volunteer_fatigue` inside the AI Matching score breakdown alongside the existing canonical factors.
- Keep the volunteer detail dashboard concept from the existing Streamlit implementation as the behavioral reference for metrics and history.
- Use the React app as the primary user-facing surface; reuse Streamlit logic only as a backend/domain reference.

### the agent's Discretion
- Exact fatigue thresholds for the three recovery badges.
- Whether the calendar UI uses tabs, segmented controls, or route-state for month/week/day switching.
- Whether assignment overlays render as inline pills, side panels, or expandable detail cards.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Calendar.tsx` already renders month/list calendar views from `/api/data/calendar`.
- `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/AIMatching.tsx` already renders factor-score breakdowns from `/api/matching/rank`.
- `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Volunteers.tsx` and `src/ui/volunteer_dashboard.py` provide the volunteer-card and volunteer-metrics references.
- `Category 3 - IA West Smart Match CRM/src/api/routers/data.py` and `src/api/routers/matching.py` are the current FastAPI extension points.
- `Category 3 - IA West Smart Match CRM/src/matching/factors.py`, `src/matching/engine.py`, and `src/config.py` contain the canonical factor/weight system.

### Established Patterns
- React pages use typed fetch helpers from `frontend/src/lib/api.ts`, `useEffect` data loading, and Recharts for analytics.
- Backend data remains CSV/JSON-backed and is normalized through existing loader/helper functions.
- Factor-score payloads already flow through FastAPI with canonical keys and weighted score details.
- The codebase prefers incremental promotion of existing Streamlit/domain logic into FastAPI rather than re-implementing business rules in React.

### Integration Points
- `src/api/routers/matching.py` is where the new fatigue factor must become visible in rank/score responses.
- `src/api/routers/data.py` or a new calendar router is where assignment-aware calendar contracts should live.
- `frontend/src/lib/api.ts` must expand to consume new calendar/assignment and fatigue-bearing types.
- `frontend/src/app/pages/Calendar.tsx`, `Volunteers.tsx`, `AIMatching.tsx`, and `Dashboard.tsx` are the main React consumers.

</code_context>

<specifics>
## Specific Ideas

- The coordinator should be able to see which events already have IA West coverage and which still need a match without leaving the calendar.
- Recovery logic should prevent obvious over-scheduling and be explainable in the UI, not feel like a hidden penalty.
- The current config/engine drift around factor definitions should be reconciled in this phase rather than ignored.

</specifics>

<deferred>
## Deferred Ideas

- Real-time collaborative scheduling or database-backed assignment storage.
- Automated travel-time integrations using external mapping APIs.

</deferred>
