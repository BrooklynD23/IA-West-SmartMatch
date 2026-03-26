# Phase 9: Outreach Button + NemoClaw Workflow - Context

**Gathered:** 2026-03-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a single "Initiate Outreach" workflow that orchestrates email generation, ICS calendar invite creation, and pipeline status update from the AI Matching page. The workflow runs through a new `/api/outreach/workflow` endpoint and is presented via a step-by-step progress modal in React.

</domain>

<decisions>
## Implementation Decisions

### Workflow Architecture
- Pipeline status persists via in-memory update + CSV append (hackathon scope, no DB)
- NemoClaw uses serial fallback only — openclaw-sdk not installed, demo-safe
- Single `/api/outreach/workflow` endpoint orchestrates email + ICS + pipeline update in one call
- Partial failure returns results with per-step statuses (show what succeeded/failed)

### Modal UX
- Progress display uses step checklist with checkmarks (email ✓, ICS ✓, pipeline updating...)
- ICS delivered via download button in modal after generation
- Pipeline transition: "Matched" → "Contacted" per ROADMAP spec

### Claude's Discretion
- Internal step ordering and error message formatting
- Exact modal animation/transition styling
- Whether to show estimated time per step

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/api/routers/outreach.py` — already has `/email` and `/ics` endpoints (reuse logic)
- `src/coordinator/nemoclaw_adapter.py` — `dispatch_parallel()` with serial fallback
- `src/ui/outreach_bridge.py` — `build_outreach_params()` data transformer
- `src/outreach/email_gen.py` — `generate_outreach_email()` core function
- `src/outreach/ics_generator.py` — `generate_ics()` core function
- `frontend/src/lib/api.ts` — `generateEmail()`, `generateIcs()` already typed
- `frontend/src/app/pages/AIMatching.tsx` — has email modal, needs workflow upgrade

### Established Patterns
- FastAPI routers with Pydantic BaseModel request/response
- React pages use useEffect+useState with active flag cleanup
- API client uses `requestJson<T>()` helper for typed fetch calls
- Modal pattern: fixed overlay with stopPropagation on inner div

### Integration Points
- AIMatching.tsx "Generate Outreach Email" button → upgrade to "Initiate Outreach"
- `/api/outreach/workflow` → calls existing email_gen + ics_generator + pipeline update
- Pipeline CSV at `data/pipeline_sample_data.csv` — append/update for status changes
- `api.ts` needs new `initiateWorkflow()` function

</code_context>

<specifics>
## Specific Ideas

- Reuse existing `/email` and `/ics` endpoint logic internally — don't duplicate
- The workflow endpoint should return all 3 results (email, ICS content, pipeline update status) in a single response
- Frontend modal should show a 3-step checklist that updates as each step completes

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
