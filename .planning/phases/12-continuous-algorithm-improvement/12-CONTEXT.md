# Phase 12: Continuous Algorithm Improvement - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn match outcomes into a lightweight feedback loop that records coordinator and event results, computes success metrics, and recommends or applies bounded weight adjustments over time. This phase must expose feedback submission/stat APIs, persist a weight-change audit trail, and show algorithm-performance analytics in the React coordinator surfaces.

</domain>

<decisions>
## Implementation Decisions

### Feedback Capture Model
- Capture structured outcomes across the coordinator lifecycle: match acceptance/decline, event attendance / completion, student-engagement or membership-interest follow-through, and optional rating signals.
- Promote the existing Streamlit feedback concepts into a shared backend service instead of inventing a second React-only feedback system.
- Keep feedback submission explicit and human-driven; do not infer success automatically from unrelated signals where the provenance is unclear.
- Normalize feedback entries around speaker-event pairs so they align with ranking, pipeline, and QR attribution records.

### Optimizer Policy
- Start with a simple bounded adjustment strategy over the existing factor weights rather than a complex ML optimizer.
- Treat weight changes as proposals / controlled updates with audit history, not opaque automatic rewrites to the scoring model.
- Keep every optimizer run reproducible from stored inputs, outputs, and timestamps.
- Prefer small deltas and clear explanations tied to the observed feedback statistics.

### Persistence & Audit Trail
- Store feedback records, optimizer snapshots, and weight-history artifacts in local CSV/JSON files for hackathon scope.
- Keep weight history append-only so regressions can be traced and prior configurations restored if needed.
- Ensure FastAPI endpoints surface both current effective weights and historical optimization summaries.
- Reuse cache/loader patterns already established in the project.

### React Analytics & Control Surface
- Add algorithm-performance visibility to the coordinator dashboard / pipeline experience rather than hiding it in a backend-only report.
- Show pain-score / quality signals in a way that explains trend direction, not just raw counts.
- Make post-event feedback collection available from the React app surfaces that already represent outcomes or next actions.
- Keep the UI understandable to coordinators: explain what changed, why it changed, and what effect it had on ranking quality.

### the agent's Discretion
- Exact file naming for feedback logs, optimizer snapshots, and weight-history artifacts.
- Whether weight updates require an explicit “apply” action or can be written at submission time once the optimizer threshold is met.
- Which charts best communicate trend, stability, and pain score without overloading the dashboard.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Category 3 - IA West Smart Match CRM/src/feedback/acceptance.py` already defines feedback entry fields, aggregation logic, and suggestion patterns.
- `Category 3 - IA West Smart Match CRM/src/config.py` contains the canonical factor registry and default weights.
- `Category 3 - IA West Smart Match CRM/src/matching/engine.py` and `src/matching/factors.py` are the scoring core the optimizer must influence.
- `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx` and `Dashboard.tsx` already render coordinator analytics and trend-friendly layouts.
- `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py` and QR/pipeline artifacts from earlier phases are the downstream signals this phase should learn from.

### Established Patterns
- Backend promotion happens by exposing existing domain logic through FastAPI and mirrored types in `frontend/src/lib/api.ts`.
- Local-file persistence and cached loader helpers are already accepted project constraints.
- Coordinator analytics surfaces favor summary cards plus focused charts over raw tables.
- The codebase already distinguishes between canonical factor keys, display labels, and weights through `config.py`.

### Integration Points
- `src/api/main.py` will need a feedback router and likely a supporting service module for shared feedback/optimizer logic.
- `frontend/src/lib/api.ts`, `frontend/src/app/pages/Dashboard.tsx`, `Pipeline.tsx`, and AI-matching-related pages are the main React consumers.
- Existing feedback logic in Streamlit should be refactored or wrapped so React and FastAPI share one source of truth.
- Any weight changes must flow back into `/api/matching/rank` and `/api/matching/score` without breaking the existing request contracts.

</code_context>

<specifics>
## Specific Ideas

- The optimizer should be explainable enough that a coordinator can understand why topic, geography, or recovery weights moved.
- Pain score and algorithm-improvement views should reuse whatever ROI and outcome data earlier phases make available.
- The current split-brain between Streamlit-only feedback and React/FastAPI ranking should end in this phase.

</specifics>

<deferred>
## Deferred Ideas

- Online learning / model retraining beyond bounded rule-based or gradient-lite weight adjustment.
- Database-backed experimentation frameworks or multi-user model governance.

</deferred>
