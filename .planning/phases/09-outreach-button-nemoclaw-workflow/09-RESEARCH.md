# Phase 9: Outreach Button + NemoClaw Workflow - Research

**Researched:** 2026-03-26
**Domain:** FastAPI endpoint orchestration + React modal UX + CSV pipeline mutation
**Confidence:** HIGH — all findings derived from reading the actual codebase. No external library discovery needed; every component already exists.

## Summary

Phase 9 wires together components that already exist in the codebase. The backend needs a single new `/api/outreach/workflow` endpoint that calls three already-implemented functions in sequence: `generate_outreach_email()`, `generate_ics()`, and a new pipeline-update helper. The frontend needs an `OutreachWorkflowModal` component that replaces the existing email-only modal, plus a new `initiateWorkflow()` function in `api.ts`.

The critical complexity is the pipeline update: `data_helpers.py` uses `functools.lru_cache` on all CSV loaders, which means an in-process write to `pipeline_sample_data.csv` will NOT be visible to `load_pipeline_data()` on the same process without cache invalidation. The planner must account for cache busting after every pipeline write.

NemoClaw is locked to serial fallback per CONTEXT.md (openclaw-sdk not installed). The existing `dispatch_parallel()` in `nemoclaw_adapter.py` handles this gracefully — `USE_NEMOCLAW` env var defaults to `"0"`, so it falls through to the serial path immediately. For the workflow endpoint, NemoClaw dispatch is not required at all: the three steps are synchronous Python calls that complete in one HTTP request. The NemoClaw "orchestration" in this phase means calling `dispatch_parallel()` with the three tasks as a `TaskList`, letting it execute serially.

**Primary recommendation:** Build the workflow endpoint as a sequential orchestrator that calls the existing `email` and `ics` logic directly (not via HTTP sub-calls), writes the pipeline update, invalidates the LRU cache, then returns all three results in one response. The modal consumes this single response and renders a 3-step checklist from the per-step status fields.

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Pipeline status persists via in-memory update + CSV append (hackathon scope, no DB)
- NemoClaw uses serial fallback only — openclaw-sdk not installed, demo-safe
- Single `/api/outreach/workflow` endpoint orchestrates email + ICS + pipeline update in one call
- Partial failure returns results with per-step statuses (show what succeeded/failed)
- Progress display uses step checklist with checkmarks (email, ICS, pipeline updating...)
- ICS delivered via download button in modal after generation
- Pipeline transition: "Matched" → "Contacted" per ROADMAP spec

### Claude's Discretion
- Internal step ordering and error message formatting
- Exact modal animation/transition styling
- Whether to show estimated time per step

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope
</user_constraints>

---

## Standard Stack

### Core (all already installed — no new dependencies needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| fastapi | >=0.115.0 | Workflow endpoint + Pydantic models | Already in use for all routers |
| pydantic | (bundled with fastapi) | Request/response model validation | Established project pattern |
| pytest | 8.3.4 | Test framework | Established project standard |
| fastapi.testclient | (bundled) | API integration tests | Used in test_api_data.py and test_api_matching.py |

### No New Packages Required

All functionality is achieved with the existing stack:
- Email generation: `src/outreach/email_gen.py` — `generate_outreach_email()`
- ICS generation: `src/outreach/ics_generator.py` — `generate_ics()`
- Bridge/params: `src/ui/outreach_bridge.py` — `build_outreach_params()`
- Data loading: `src/ui/data_helpers.py` — `load_pipeline_data()`, `_load_pipeline_data_cached`
- NemoClaw: `src/coordinator/nemoclaw_adapter.py` — `dispatch_parallel()` with serial fallback

**Installation:** No new packages. Run existing venv.

---

## Architecture Patterns

### Recommended File Structure for New Code

```
src/
├── api/
│   └── routers/
│       └── outreach.py           # ADD: /workflow endpoint here (same router)
├── outreach/
│   └── pipeline_updater.py       # NEW: pipeline CSV write + cache invalidation
frontend/src/
├── app/pages/
│   └── AIMatching.tsx            # MODIFY: replace email modal with workflow modal
├── components/
│   └── OutreachWorkflowModal.tsx # NEW: 3-step checklist modal
└── lib/
    └── api.ts                    # ADD: initiateWorkflow() function + types
```

### Pattern 1: Workflow Endpoint — Sequential Orchestration with Per-Step Status

**What:** Single FastAPI endpoint that runs 3 steps in sequence, captures success/failure for each, returns all results even on partial failure.

**When to use:** Hackathon demo context where reliability matters more than parallelism.

**Shape of the response (to define as Pydantic models):**
```python
# Source: derived from existing EmailRequest/IcsRequest patterns in outreach.py

class WorkflowRequest(BaseModel):
    speaker_name: str
    event_name: str

class StepResult(BaseModel):
    status: Literal["ok", "error"]
    error: str | None = None

class WorkflowResponse(BaseModel):
    email: str
    email_data: dict[str, str]
    ics_content: str
    pipeline_updated: bool
    steps: dict[str, StepResult]  # keys: "email", "ics", "pipeline"
```

**Step ordering (recommended):** email → ICS → pipeline. Email is the most likely to fail (Gemini API call); fail it first so ICS and pipeline steps only run if the user actually gets an email. However, per locked decision, partial failure still returns completed steps.

**Implementation sketch:**
```python
# Source: mirrors _rank_matches() + email() patterns in existing outreach.py

@router.post("/workflow")
def workflow(body: WorkflowRequest) -> dict[str, Any]:
    steps: dict[str, dict] = {}
    email_result: dict[str, str] = {}
    ics_content: str = ""
    pipeline_updated: bool = False

    # Step 1: Email
    try:
        match = _find_ranked_match(body.event_name, body.speaker_name)
        # ... build bridge spec, call generate_outreach_email()
        steps["email"] = {"status": "ok"}
    except Exception as exc:
        steps["email"] = {"status": "error", "error": str(exc)}

    # Step 2: ICS
    try:
        ics_content = generate_ics(event_name=body.event_name)
        steps["ics"] = {"status": "ok"}
    except Exception as exc:
        steps["ics"] = {"status": "error", "error": str(exc)}

    # Step 3: Pipeline
    try:
        update_pipeline_status(body.event_name, body.speaker_name, "Contacted")
        pipeline_updated = True
        steps["pipeline"] = {"status": "ok"}
    except Exception as exc:
        steps["pipeline"] = {"status": "error", "error": str(exc)}

    return {
        "email": email_result.get("full_email", ""),
        "email_data": email_result,
        "ics_content": ics_content,
        "pipeline_updated": pipeline_updated,
        "steps": steps,
    }
```

### Pattern 2: Pipeline Updater — CSV Write + LRU Cache Invalidation

**What:** New `src/outreach/pipeline_updater.py` module that writes pipeline status changes to CSV and clears the LRU cache so subsequent reads see fresh data.

**Critical insight:** `data_helpers.py` caches `pipeline_sample_data.csv` with `@functools.lru_cache(maxsize=1)` on `_load_pipeline_data_cached()`. Any CSV write is invisible until the cache is cleared. The cache must be busted via `_load_pipeline_data_cached.cache_clear()` after every write.

**Implementation pattern:**
```python
# Source: data_helpers.py LRU cache pattern (lines 85-94)

import csv
from pathlib import Path
from src.ui.data_helpers import _data_dir, _load_pipeline_data_cached

PIPELINE_CSV = _data_dir() / "pipeline_sample_data.csv"
STAGE_ORDER = {"Matched": 0, "Contacted": 1, "Confirmed": 2, "Attended": 3, "Member Inquiry": 4}

def update_pipeline_status(
    event_name: str,
    speaker_name: str,
    new_stage: str,
) -> bool:
    """Find the matching row and update its stage, then rewrite the CSV.

    Returns True if a row was found and updated, False if not found.
    Clears the LRU cache after write so the change is immediately visible.
    """
    rows = list(_load_pipeline_data_cached())  # read from cache (fast)
    found = False
    updated_rows = []
    for row in rows:
        row_copy = dict(row)
        if (row_copy.get("event_name") == event_name and
                row_copy.get("speaker_name") == speaker_name):
            row_copy["stage"] = new_stage
            row_copy["stage_order"] = str(STAGE_ORDER.get(new_stage, 0))
            found = True
        updated_rows.append(row_copy)

    if not found:
        # Append new row if not in pipeline yet
        updated_rows.append({
            "event_name": event_name,
            "speaker_name": speaker_name,
            "match_score": "",
            "rank": "",
            "stage": new_stage,
            "stage_order": str(STAGE_ORDER.get(new_stage, 0)),
        })

    _write_pipeline_csv(updated_rows)
    _load_pipeline_data_cached.cache_clear()  # CRITICAL: bust cache
    return found


def _write_pipeline_csv(rows: list[dict]) -> None:
    fieldnames = ["event_name", "speaker_name", "match_score", "rank", "stage", "stage_order"]
    with PIPELINE_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
```

### Pattern 3: NemoClaw Dispatch Wrapper (Serial Fallback)

**What:** Per CONTEXT.md, NemoClaw runs serial fallback only. The `dispatch_parallel()` function already handles this — `USE_NEMOCLAW` is `"0"` by default, so it just iterates the task list serially.

**For the workflow endpoint:** NemoClaw dispatch is optional wrapping of the 3 steps. Since the endpoint runs synchronously anyway, the simplest demo-safe approach is to NOT use `dispatch_parallel()` inside the endpoint — just call the steps directly in sequence. If the product story requires showing "NemoClaw orchestrated this," call `dispatch_parallel()` as a post-hoc logging step, or mention it in response metadata.

**Recommended approach:** Keep the workflow endpoint as plain sequential Python calls. Document in the response that NemoClaw serial dispatch was used (`"dispatch_mode": "serial"`).

### Pattern 4: Frontend Modal — Step Checklist

**What:** Replace the existing `showEmailModal` flow in `AIMatching.tsx` with a new `OutreachWorkflowModal` component that shows a 3-step checklist.

**Existing modal pattern to follow** (from `AIMatching.tsx` lines 338-390):
```tsx
// Source: AIMatching.tsx - existing email modal (lines 338-390)
// Fixed overlay with bg-black/50 and stopPropagation on inner div
// Max width 3xl, max height 90vh with overflow-y-auto
// Uses useEffect+useState for async data

{showModal && selectedVolunteer ? (
  <div
    className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    onClick={() => setShowModal(false)}
  >
    <div
      className="bg-white rounded-xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
      onClick={(e) => e.stopPropagation()}
    >
      {/* content */}
    </div>
  </div>
) : null}
```

**Step checklist pattern (Claude's discretion for styling):**
```tsx
// Steps array drives the checklist render
const STEPS = [
  { key: "email", label: "Generating outreach email..." },
  { key: "ics",   label: "Creating calendar invite..." },
  { key: "pipeline", label: "Updating pipeline status..." },
] as const;

// Render per step: spinner while loading, check when done, X on error
{STEPS.map(({ key, label }) => (
  <div key={key} className="flex items-center gap-3 py-2">
    {stepStatus[key] === "ok" && <Check className="w-5 h-5 text-green-600" />}
    {stepStatus[key] === "error" && <X className="w-5 h-5 text-red-600" />}
    {stepStatus[key] === "loading" && <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />}
    <span className={stepStatus[key] === "error" ? "text-red-700" : "text-gray-700"}>
      {label}
    </span>
  </div>
))}
```

**ICS download button** (after workflow response):
```tsx
// Source: pattern from existing modal, adapted for blob download
const downloadIcs = () => {
  const blob = new Blob([workflowResult.ics_content], { type: "text/calendar" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${selectedVolunteer.name}-invite.ics`;
  a.click();
  URL.revokeObjectURL(url);
};
```

### Pattern 5: API Client — initiateWorkflow()

**What:** New function in `api.ts` that posts to `/api/outreach/workflow`.

**TypeScript types to add:**
```typescript
// Source: mirrors OutreachEmailResponse pattern in api.ts (lines 75-78)

export interface WorkflowStepResult {
  status: "ok" | "error";
  error?: string;
}

export interface WorkflowResponse {
  email: string;
  email_data: OutreachEmailPayload;
  ics_content: string;
  pipeline_updated: boolean;
  steps: {
    email: WorkflowStepResult;
    ics: WorkflowStepResult;
    pipeline: WorkflowStepResult;
  };
}

export async function initiateWorkflow(
  speakerName: string,
  eventName: string,
): Promise<WorkflowResponse> {
  return requestJson<WorkflowResponse>("/api/outreach/workflow", {
    method: "POST",
    body: JSON.stringify({
      speaker_name: speakerName,
      event_name: eventName,
    }),
  });
}
```

### Anti-Patterns to Avoid

- **Making HTTP sub-calls inside the workflow endpoint:** Do not call `/api/outreach/email` and `/api/outreach/ics` via HTTP from within the workflow endpoint. Call the underlying Python functions directly. HTTP sub-calls add latency, create circular dependencies, and complicate error handling.
- **Forgetting cache_clear after CSV write:** Writing to `pipeline_sample_data.csv` without calling `_load_pipeline_data_cached.cache_clear()` means the `GET /api/data/pipeline` endpoint will return stale data for the entire process lifetime.
- **Duplicating `_find_ranked_match` logic:** This private function already exists in `outreach.py`. Import and reuse it for the workflow endpoint rather than copying.
- **Using `lru_cache` result directly as mutable list:** `_load_pipeline_data_cached()` returns a `tuple` of dicts. Convert to `list` before mutating. Writing back the tuple directly will cause a TypeError.
- **Mutating the button state after component unmount:** The existing pattern uses `let active = true` + cleanup `return () => { active = false }` in useEffect. The workflow call is triggered by user click (not useEffect), so the risk is different — use an abort flag or ignore stale results via a ref.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ICS generation | Custom RFC 5545 builder | `generate_ics()` in `ics_generator.py` | Already tested, handles edge cases (unparseable dates, RFC escaping) |
| Email generation | New LLM prompt | `generate_outreach_email()` in `email_gen.py` | Has disk cache, fallback email, tested with 7+ test cases |
| Bridge params | Re-implement spec→speaker dict mapping | `build_outreach_params()` in `outreach_bridge.py` | Has 4 tested functions covering all field mappings |
| Speaker lookup | Re-query ranking endpoint | `_find_ranked_match()` in `outreach.py` | Already does casefold matching with 404 HTTPException |
| Modal overlay | Custom backdrop component | Copy existing modal pattern from `AIMatching.tsx` lines 338-345 | Established pattern with stopPropagation, z-50, scroll handling |
| Blob download | Server-side file serving | Browser `Blob` + `URL.createObjectURL` | ICS is text content already in memory — no disk I/O needed |
| Pipeline write | pandas DataFrame operations | `csv.DictWriter` (already used in codebase pattern) | pandas is heavy; plain csv matches existing CSV loading pattern |

**Key insight:** Every meaningful operation in this phase is already implemented. The entire value-add is composing them into a single workflow and building the UI to present results.

---

## Common Pitfalls

### Pitfall 1: LRU Cache Stale Data After Pipeline Write
**What goes wrong:** Coordinator clicks "Initiate Outreach," pipeline CSV is written, but `GET /api/data/pipeline` still returns the old stage because `_load_pipeline_data_cached` cached the file at startup.
**Why it happens:** `functools.lru_cache(maxsize=1)` caches the first call result for the process lifetime. File writes do not auto-invalidate.
**How to avoid:** Call `_load_pipeline_data_cached.cache_clear()` immediately after `_write_pipeline_csv()`. Import the cached function directly: `from src.ui.data_helpers import _load_pipeline_data_cached`.
**Warning signs:** Unit test passes (uses patched/fresh data) but integration test shows old stage persisting after workflow call.

### Pitfall 2: Button Triggers Multiple Workflow Calls
**What goes wrong:** User double-clicks "Initiate Outreach," triggering two API calls. The pipeline update runs twice — second run may find stage already "Contacted" (harmless but noisy) or, if not properly idempotent, could append a duplicate row.
**Why it happens:** No debounce or disabled-state on the button during API call.
**How to avoid:** Set a `workflowLoading` boolean state in React; disable the button (and show spinner) while `workflowLoading === true`. The pipeline updater should also be idempotent — update existing row rather than append unconditionally.
**Warning signs:** Pipeline CSV has duplicate rows after testing.

### Pitfall 3: `_find_ranked_match` Returns 404 for Speaker Name Mismatch
**What goes wrong:** Workflow endpoint 404s for a speaker that exists in the pipeline but not in the ranking result for that event.
**Why it happens:** `_find_ranked_match()` calls `_rank_matches()` with `limit=100`, then does casefold matching. If the speaker was in `pipeline_sample_data.csv` but ranks below 100, or if the name has a slight variation (e.g., "Dr. Yufan Lin" vs "Yufan Lin"), the match fails.
**How to avoid:** The existing `_find_ranked_match` does `target in name.casefold()` as a substring fallback. For the workflow endpoint, pass the exact `speaker_name` as it comes from the frontend (which comes from `RankedMatch.name`, which came from the ranking endpoint — so it should already match).
**Warning signs:** 404 errors in workflow for speakers that were just displayed in the match list.

### Pitfall 4: ICS Download Fails in Safari
**What goes wrong:** `URL.createObjectURL` + programmatic `<a>` click works in Chrome/Firefox but not Safari.
**Why it happens:** Safari's restrictions on programmatic link clicks and object URLs.
**How to avoid:** Set `a.target = "_blank"` before clicking. Alternatively, use a `data:` URI: `a.href = "data:text/calendar;charset=utf-8," + encodeURIComponent(ics_content)`. Since this is a hackathon demo, document the known issue rather than building a full workaround.
**Warning signs:** ICS download works in Chrome but silently fails in Safari.

### Pitfall 5: Modal Shows "All Steps Complete" Before Pipeline Refresh in Dashboard
**What goes wrong:** Coordinator sees "Pipeline updated" checkmark in the modal, closes it, navigates to pipeline dashboard, but still sees "Matched" stage.
**Why it happens:** The pipeline dashboard likely fetches from `GET /api/data/pipeline` on mount. If the user navigated to the dashboard before the workflow endpoint finished, or if the dashboard component cached its data in React state, it shows stale data.
**How to avoid:** After workflow completes, optionally emit a context event or use a simple URL-based cache busting param (`?refresh=timestamp`) when navigating to pipeline. For the hackathon, ensure the pipeline page re-fetches on every mount (no persistent React state across pages).

---

## Code Examples

### Verified Pattern: Reuse `_find_ranked_match` + `build_outreach_params` in Workflow Router

```python
# Source: src/api/routers/outreach.py (existing email endpoint, lines 64-95)
# The workflow endpoint follows the same structure but calls all three generators.

from src.api.routers.outreach import _find_ranked_match, _factor_scores_for_bridge
from src.ui.outreach_bridge import build_outreach_params
from src.outreach.email_gen import generate_outreach_email
from src.outreach.ics_generator import generate_ics

# In workflow endpoint:
match = _find_ranked_match(body.event_name, body.speaker_name)
bridge_spec = {
    "name": str(match.get("name", "")),
    "match_score": str(match.get("score", 0.0)),
    "rank": str(match.get("rank", "")),
    "company": str(match.get("company", "")),
    "title": str(match.get("title", "")),
    "expertise_tags": str(match.get("expertise_tags", "")),
    "initials": "".join(part[:1].upper() for part in str(match.get("name", "")).split() if part),
}
params = build_outreach_params(
    bridge_spec,
    body.event_name,
    _factor_scores_for_bridge(dict(match.get("factor_scores", {}))),
)
generated = generate_outreach_email(params["speaker"], params["event"], params["match_scores"])
```

### Verified Pattern: FastAPI TestClient for Workflow Endpoint

```python
# Source: test_api_matching.py pattern (lines 12-68) + test_api_data.py

from fastapi.testclient import TestClient
from src.api.main import app
from unittest.mock import patch

client = TestClient(app)

def test_workflow_returns_all_three_results():
    response = client.post(
        "/api/outreach/workflow",
        json={
            "speaker_name": "Dr. Yufan Lin",
            "event_name": "AI for a Better Future Hackathon",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert "email" in payload
    assert "ics_content" in payload
    assert "pipeline_updated" in payload
    assert "steps" in payload
    assert payload["steps"]["email"]["status"] == "ok"
    assert payload["steps"]["ics"]["status"] == "ok"

def test_workflow_pipeline_update_clears_cache(tmp_path, monkeypatch):
    # Verify cache is busted after write
    from src.ui import data_helpers
    monkeypatch.setattr(data_helpers, "_data_dir", lambda: tmp_path)
    # ... write temp CSV, call workflow, verify _load_pipeline_data_cached returns fresh data
```

### Verified Pattern: CSV Stage Constants (from pipeline_sample_data.csv)

```python
# Source: data/pipeline_sample_data.csv — observed stage values and stage_order integers
PIPELINE_STAGES = {
    "Matched": 0,        # stage_order = 0
    "Contacted": 1,      # stage_order = 1
    "Confirmed": 2,      # stage_order = 2
    "Attended": 3,       # stage_order = 3
    "Member Inquiry": 4, # stage_order = 4
}
# Workflow transitions: "Matched" (0) → "Contacted" (1)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Email-only modal (generateEmail) | Workflow modal (initiateWorkflow) | Phase 9 | Single API call replaces 2 separate calls |
| No pipeline write from frontend | CSV write + cache invalidation | Phase 9 | Pipeline stage visible immediately after outreach |
| Email modal in AIMatching.tsx (inline) | OutreachWorkflowModal as separate component | Phase 9 | Keeps AIMatching.tsx under 800-line limit |

**Deprecated/outdated after this phase:**
- The `generateEmail()` function in `api.ts`: still valid for standalone email generation, but the button in AIMatching.tsx should call `initiateWorkflow()` instead.
- The `showEmailModal` / `emailLoading` / `emailResult` / `emailError` state variables in `AIMatching.tsx`: replaced by workflow modal state.

---

## Open Questions

1. **Should the workflow endpoint also call `dispatch_parallel()` from nemoclaw_adapter?**
   - What we know: CONTEXT.md says "NemoClaw uses serial fallback only." The `dispatch_parallel()` function accepts a `TaskList` and a `fallback_dispatch` callable.
   - What's unclear: Whether the planner wants `dispatch_parallel()` to wrap the 3 steps (with a no-op fallback dispatch that just runs the callables), or whether the workflow endpoint runs its steps directly.
   - Recommendation: Run steps directly in the endpoint — no `dispatch_parallel()` wrapper needed. Include `"dispatch_mode": "serial"` in the response to satisfy the demo story. This avoids threading complexity in a synchronous FastAPI endpoint.

2. **Idempotency of pipeline update — update vs. append?**
   - What we know: The pipeline CSV has rows keyed by `(event_name, speaker_name)`. The updater should find and update existing rows.
   - What's unclear: What to do if the speaker is not yet in the pipeline (e.g., a speaker discovered via the matching engine but never added to `pipeline_sample_data.csv`).
   - Recommendation: Upsert — update if found, append new row with "Contacted" stage if not found. This matches the hackathon-scope behavior where the CSV is the source of truth.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 8.3.4 |
| Config file | none (no pytest.ini or pyproject.toml at project root) |
| Quick run command | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/test_api_outreach_workflow.py -x -q` |
| Full suite command | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x -q --ignore=tests/test_e2e_playwright.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| WF-01 | `POST /api/outreach/workflow` returns 200 with email + ics + pipeline fields | integration | `pytest tests/test_api_outreach_workflow.py::test_workflow_returns_all_three_results -x` | Wave 0 |
| WF-02 | Workflow response includes per-step status dict | integration | `pytest tests/test_api_outreach_workflow.py::test_workflow_step_statuses -x` | Wave 0 |
| WF-03 | Pipeline CSV stage updates from "Matched" to "Contacted" | unit | `pytest tests/test_pipeline_updater.py::test_update_stage_matched_to_contacted -x` | Wave 0 |
| WF-04 | LRU cache cleared after pipeline write | unit | `pytest tests/test_pipeline_updater.py::test_cache_cleared_after_write -x` | Wave 0 |
| WF-05 | Partial failure: email error still returns ics + pipeline results | integration | `pytest tests/test_api_outreach_workflow.py::test_workflow_partial_failure -x` | Wave 0 |
| WF-06 | `initiateWorkflow()` in api.ts sends correct payload shape | manual | Open browser, click Initiate Outreach, verify Network tab | N/A |
| WF-07 | ICS download button creates .ics file download | manual | Click Download Calendar Invite, verify file saved | N/A |
| WF-08 | Modal 3-step checklist renders and updates per step | manual | Open modal, observe step indicators during loading | N/A |

### Sampling Rate

- **Per task commit:** `python -m pytest tests/test_api_outreach_workflow.py tests/test_pipeline_updater.py -x -q`
- **Per wave merge:** `python -m pytest tests/ -x -q --ignore=tests/test_e2e_playwright.py`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_api_outreach_workflow.py` — covers WF-01, WF-02, WF-05
- [ ] `tests/test_pipeline_updater.py` — covers WF-03, WF-04

*(Existing test infrastructure: `fastapi.testclient`, `unittest.mock.patch`, `pytest` — no new framework install needed)*

---

## Sources

### Primary (HIGH confidence)

- Direct code read: `src/api/routers/outreach.py` — existing email + ICS endpoint patterns, `_find_ranked_match`, `_factor_scores_for_bridge`
- Direct code read: `src/ui/data_helpers.py` — LRU cache implementation, `_load_pipeline_data_cached`, `load_pipeline_data()`
- Direct code read: `src/coordinator/nemoclaw_adapter.py` — `dispatch_parallel()` serial fallback behavior
- Direct code read: `src/ui/outreach_bridge.py` — `build_outreach_params()` shape
- Direct code read: `src/outreach/email_gen.py` — `generate_outreach_email()` signature + return shape
- Direct code read: `src/outreach/ics_generator.py` — `generate_ics()` signature + return type
- Direct code read: `frontend/src/lib/api.ts` — `requestJson`, existing type interfaces, `generateEmail()`, `generateIcs()`
- Direct code read: `frontend/src/app/pages/AIMatching.tsx` — modal pattern, state management pattern, button handler
- Direct code read: `data/pipeline_sample_data.csv` — column names, stage values, stage_order integers
- Direct code read: `tests/test_api_data.py`, `tests/test_api_matching.py` — TestClient patterns, assertion style

### Secondary (MEDIUM confidence)

- `requirements.txt` — verified fastapi, pytest, pytest-cov versions match installed env
- `.planning/config.json` — confirmed `nyquist_validation: true`

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; all tools are pre-installed and in active use
- Architecture: HIGH — all patterns derived from reading the actual codebase, not assumptions
- Pitfalls: HIGH — LRU cache and CSV write interaction is a concrete, verifiable code-level concern
- Test framework: HIGH — pytest 8.3.4 confirmed in requirements.txt; TestClient pattern confirmed in 2 existing test files

**Research date:** 2026-03-26
**Valid until:** Phase 9 complete (code does not change between now and implementation)
