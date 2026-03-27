# Phase 11: QR Code Generation + ROI Tracking - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Add deterministic QR-code generation and scan tracking for speaker-event pairs, then expose ROI analytics in the FastAPI + React experience. This phase must create the backend generation / redirect / stats flow, a React surface to view and download QR assets, and analytics that connect scans to downstream membership-interest outcomes.

</domain>

<decisions>
## Implementation Decisions

### QR Identity & Redirect Model
- Generate one deterministic referral code per speaker-event pair so repeated requests produce the same asset and analytics key.
- Encode a lightweight redirect URL / scan target, not raw business metadata directly in the QR image payload.
- Route scans through a FastAPI endpoint that records the scan event before redirecting to the sign-up destination.
- Keep IA West branding as an overlay / card treatment around the QR asset, while keeping the machine-readable QR matrix standards-compliant.

### Storage & Analytics
- Store QR definitions and scan events in local CSV/JSON artifacts under the project data area, consistent with the hackathon storage constraint.
- Track at least: referral code, speaker, event, generated timestamp, scan timestamp, destination URL, and any later conversion marker available to the app.
- Treat membership-interest / inquiry outcomes as the first ROI target, using the existing pipeline and feedback surfaces as analytics consumers.
- Prefer append-only logging for scan events so the audit trail stays reconstructable.

### React Surface Placement
- Put QR generation and download on the coordinator-facing surfaces that already deal with outreach or pipeline progression.
- Add summarized QR ROI metrics to the pipeline/dashboard views instead of creating an isolated analytics dead-end.
- Keep volunteer/speaker detail views eligible to show historical QR performance when that context is already available.
- Use the existing blue/white rebrand and card patterns; do not introduce a separate visual language for QR tooling.

### Integration Strategy
- Reuse the existing outreach workflow, pipeline updater, and volunteer metrics as the scaffolding for QR-triggered attribution.
- Expose QR APIs through FastAPI rather than bolting logic into React.
- Treat the existing Streamlit volunteer dashboard analytics as a domain reference only; React remains the production-facing surface.
- Keep the schema simple enough that Phase 12 can reuse the same tracked outcomes for the feedback/optimizer loop.

### the agent's Discretion
- Exact file layout for QR artifacts and scan logs under local storage.
- Whether QR generation uses PNG bytes, SVG, or both for frontend display/download.
- The specific placement of QR analytics cards across pipeline vs volunteer-detail screens.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Category 3 - IA West Smart Match CRM/src/outreach/pipeline_updater.py` already persists stage transitions to CSV and clears caches.
- `Category 3 - IA West Smart Match CRM/src/api/routers/outreach.py` and `frontend/src/components/OutreachWorkflowModal.tsx` already own the outreach handoff surface.
- `Category 3 - IA West Smart Match CRM/frontend/src/app/pages/Pipeline.tsx` and `Dashboard.tsx` already render coordinator analytics cards and funnels.
- `Category 3 - IA West Smart Match CRM/src/feedback/acceptance.py` and `src/ui/volunteer_dashboard.py` already model outcome-oriented analytics that can later consume QR attribution.

### Established Patterns
- New backend capabilities are exposed via typed FastAPI routes and mirrored in `frontend/src/lib/api.ts`.
- Persistence is intentionally local-file based and cache-aware.
- React analytics use cards, funnels, and bar/line charts rather than dense tables by default.
- Coordinator actions already flow through modal-driven UI and explicit success/error states.

### Integration Points
- `src/api/main.py` will need a new QR router or equivalent route registration.
- `frontend/src/lib/api.ts`, `frontend/src/app/pages/Pipeline.tsx`, and likely `frontend/src/app/pages/Outreach.tsx` are the first React consumers.
- `src/ui/data_helpers.py` is the natural place for cached read helpers over QR artifacts once created.
- Existing pipeline / feedback analytics should consume the new referral-code events rather than duplicating reporting logic.

</code_context>

<specifics>
## Specific Ideas

- ROI should not stop at “QR generated”; it should show scans and the downstream membership-interest signal that matters to IA West.
- Speaker-event QR assets need to feel like coordinator tools, not marketing collateral disconnected from the workflow.
- This phase starts from zero QR implementation, so schema simplicity and deterministic behavior matter more than breadth.

</specifics>

<deferred>
## Deferred Ideas

- OAuth/Gmail-assisted send flows that automatically embed the QR asset in outbound outreach.
- Multi-tenant analytics or cloud-backed scan ingestion.

</deferred>
