# Phase 14: Visual Resilience - Research

**Researched:** 2026-03-26
**Domain:** FastAPI fallback pattern + React chart resilience + SQLite3 demo seed
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **Fallback trigger:** API error OR empty array after successful fetch both trigger "Demo Mode" — either means no real data
- **Page-level flag:** One `isMockData: boolean` flag per page governs all charts on that page (not per-chart)
- **Pages in scope:** Dashboard, AIMatching, Pipeline, Volunteers, QR stats (on Pipeline), Feedback trend (on Pipeline and Dashboard)
- **Demo Mode badge design:** Small blue pill inline next to section heading; text: "Demo Mode"; style: `bg-blue-50 text-blue-700 border border-blue-200`; persistent (non-dismissible); disappears when real data loads
- **3-layer fallback:**
  - Layer 1 (Primary): Production CSV/live data from real API endpoints
  - Layer 2 (Demo DB): `data/demo.db` SQLite3 — backend falls back here when primary is empty or errors; adds `"source": "demo"` field to response
  - Layer 3 (Last resort): Thin hardcoded React constants — only when backend itself is unreachable
- **Backend signal:** FastAPI adds `source: "demo"` to responses served from demo.db
- **React detection:** `response.source === "demo"` OR `data.length === 0` sets `isMockData = true`
- **Demo dataset design:** ~10 specialists, 5 events, pipeline funnel 40→18→7 progression, 3 calendar assignments, 5 QR scan records, 8 feedback records; cross-feature coherent

### Claude's Discretion

- Exact SQLite3 schema design for demo.db (should mirror existing CSV/JSON column names)
- Exact fallback detection logic in FastAPI routers (e.g., `if len(rows) == 0:` serve from demo.db)
- React `MOCK_DATA` constants in shared file (layer 3 only — thin, minimal)

### Deferred Ideas (OUT OF SCOPE)

- Gmail send integration from outreach modal
- Online/cloud demo DB (Supabase/Firebase)
- Live data refresh / websocket updates
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| POLISH-04 | All charts, images, and data visualizations load real data or fall back gracefully to hardcoded mock data when unavailable | Router-level try/except + `if len(rows) == 0` → demo.db fallback; React layer-3 constants as safety net |
| POLISH-05 | Any view displaying fallback/mock data shows a discrete "Demo Mode" indicator visible to the coordinator | `source: "demo"` field in FastAPI response; React badge component wired to `isMockData` state |
</phase_requirements>

---

## Summary

Phase 14 needs two tightly coupled changes: a backend "demo DB fallback" and a React "demo mode badge" system. The backend is the single source of truth for whether data is real or demo (layer 2), with React constants as a last-resort safety net (layer 3).

The current FastAPI routers (`data.py`, `calendar.py`, `feedback.py`, `qr.py`) all use plain `try/except` with no fallback — they either return live data or throw a 500. None use SQLite3 today; Python's standard library `sqlite3` module is already available (no new dependency) and is the correct choice for a lightweight demo.db.

The React API client (`src/lib/api.ts`) already has extensive normalization logic. The cleanest interception point for the `source` field is inside each fetch function (e.g., `fetchPipeline`, `fetchCalendarEvents`, `fetchFeedbackStats`) — wrap the return value in a container object `{ data: [...], source: "live"|"demo" }` OR read `source` off the raw JSON before normalizing. Since all current endpoints return plain arrays or plain objects (not enveloped), the safest approach is to return a `{ data, source }` wrapper from each affected fetch function, letting callers destructure.

Recharts handles empty data arrays without runtime errors for `BarChart` and `LineChart` — they simply render axes with nothing drawn. `FunnelChart` with `Funnel` also tolerates `data=[]` gracefully (confirmed by checking recharts 2.x behavior: Funnel renders empty state rather than throwing). This means recharts itself is NOT the crash risk — the crash risk is downstream `.map()` / `.reduce()` operations in Dashboard and Pipeline derivation functions that may throw on truly empty arrays (e.g., `records[0].event_name` when records is empty). The layer-3 constants protect against this.

**Primary recommendation:** Build the `data/demo.db` SQLite3 seed first (it unblocks everything else), wire router-level fallback second, add the `source` field to response envelope third, then update React pages to read `isMockData` and render the badge.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python `sqlite3` | stdlib (3.x) | demo.db read/write | Zero new dependency; already installed with Python |
| FastAPI `APIRouter` | >=0.115.0 (already in use) | Router-level fallback injection | Existing pattern in all 5 routers |
| Recharts | 2.15.2 (already in use) | All chart rendering | `FunnelChart`, `BarChart`, `LineChart` — already wired |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Tailwind v4 classes | in use | Demo badge styling | `bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5 text-xs` |
| Pydantic `Literal` | in use (Python typing) | Type-safe `source` field | Add `source: Literal["live", "demo"] = "live"` to response wrappers |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib `sqlite3` | SQLAlchemy | SQLAlchemy is overkill for a read-only demo seed; stdlib is sufficient |
| stdlib `sqlite3` | JSON fixture files (as in `src/demo_mode.py`) | JSON fixtures already exist for Streamlit path — but demo.db is the decided architecture for FastAPI path |

**Installation:**
```bash
# No new installs needed — sqlite3 is Python stdlib
```

---

## Architecture Patterns

### Recommended Project Structure

New files to create:
```
data/
└── demo.db                       # SQLite3 demo seed (Layer 2)
src/api/
└── demo_db.py                    # Demo DB helpers: get_connection(), load_demo_*()
frontend/src/lib/
└── mockData.ts                   # Layer 3 React constants (thin, minimal)
frontend/src/app/components/ui/
└── DemoModeBadge.tsx             # Reusable badge component
```

Modified files:
```
src/api/routers/data.py           # Add demo.db fallback to /pipeline, /specialists, /events, /calendar
src/api/routers/calendar.py       # Add demo.db fallback to /events, /assignments
src/api/routers/feedback.py       # Add demo.db fallback to /stats
src/api/routers/qr.py             # Add demo.db fallback to /stats
frontend/src/lib/api.ts           # Wrap fetch functions to expose source field
frontend/src/app/pages/Dashboard.tsx   # Add isMockData state + badge
frontend/src/app/pages/AIMatching.tsx  # Add isMockData state + badge
frontend/src/app/pages/Pipeline.tsx    # Add isMockData state + badge
frontend/src/app/pages/Volunteers.tsx  # Add isMockData state + badge
```

### Pattern 1: FastAPI Router-Level Fallback (Layer 2)

**What:** Wrap the primary data load in a try/except, check for empty result, fall back to demo.db. Add `source` field to return value.

**When to use:** All GET endpoints that feed chart-bearing pages.

**Example:**
```python
# src/api/routers/data.py — updated pattern
from src.api.demo_db import load_demo_pipeline

@router.get("/pipeline")
async def pipeline() -> list[dict]:
    try:
        rows = load_pipeline_data()
        if rows:
            return rows
        # Empty production data — fall back to demo.db
        demo_rows = load_demo_pipeline()
        return [{**row, "source": "demo"} for row in demo_rows]
    except Exception:
        demo_rows = load_demo_pipeline()
        return [{**row, "source": "demo"} for row in demo_rows]
```

For endpoints that return a dict (feedback stats, qr stats) rather than a list:
```python
# feedback/stats endpoint pattern
@router.get("/stats")
async def stats() -> dict[str, Any]:
    try:
        result = build_feedback_stats()
        if result.get("total_feedback", 0) > 0:
            return result
        return {**load_demo_feedback_stats(), "source": "demo"}
    except Exception:
        return {**load_demo_feedback_stats(), "source": "demo"}
```

### Pattern 2: demo_db.py Helper Module

**What:** Single module providing `get_connection()` and one `load_demo_*()` function per data domain.

**Example:**
```python
# src/api/demo_db.py
import sqlite3
from pathlib import Path
from typing import Any

_DEMO_DB_PATH = Path(__file__).parent.parent.parent / "data" / "demo.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DEMO_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_demo_pipeline() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM pipeline").fetchall()
    return [dict(row) for row in rows]


def load_demo_specialists() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM specialists").fetchall()
    return [dict(row) for row in rows]

# ... one function per table
```

### Pattern 3: React `isMockData` State + Badge (Layer 3 detection)

**What:** Each page holds one `isMockData` boolean. Fetch wrapper exposes `source`. If source is `"demo"` or data is empty, set `isMockData = true`.

**Example:**
```typescript
// In a page component useEffect:
const { data: pipelineRows, source } = await fetchPipeline();
const useMock = source === "demo" || pipelineRows.length === 0;
setPipelineRecords(useMock ? MOCK_PIPELINE : pipelineRows);
setIsMockData(useMock);
```

```typescript
// DemoModeBadge.tsx
export function DemoModeBadge() {
  return (
    <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
      Demo Mode
    </span>
  );
}

// Usage next to a section heading:
<h2 className="text-lg font-semibold">Pipeline Funnel {isMockData && <DemoModeBadge />}</h2>
```

### Pattern 4: React Layer-3 MOCK_DATA Constants (Safety Net)

**What:** A single shared file `frontend/src/lib/mockData.ts` with typed constants for all chart data shapes. Only activated when the network request itself fails (backend down).

**Example:**
```typescript
// frontend/src/lib/mockData.ts
import type { PipelineRecord, Specialist, ... } from "./api";

export const MOCK_PIPELINE: PipelineRecord[] = [
  { event_name: "AI for a Better Future Hackathon", speaker_name: "Dr. Sarah Chen", match_score: "0.89", rank: "1", stage: "Attended", stage_order: "3" },
  // ... ~18 records covering the funnel stages
];

export const MOCK_SPECIALISTS: Specialist[] = [ ... ]; // ~10 records
// etc.
```

### Pattern 5: demo.db SQLite3 Schema Design

**What:** Mirror existing CSV column names exactly. Use flat tables — no JOINs required.

**Schema (Claude's discretion per CONTEXT.md):**

```sql
-- Mirrors pipeline_sample_data.csv columns
CREATE TABLE pipeline (
  event_name TEXT,
  speaker_name TEXT,
  match_score TEXT,
  rank TEXT,
  stage TEXT,
  stage_order TEXT
);

-- Mirrors data_speaker_profiles.csv columns
CREATE TABLE specialists (
  Name TEXT,
  "Board Role" TEXT,
  "Metro Region" TEXT,
  Company TEXT,
  Title TEXT,
  "Expertise Tags" TEXT
);

-- Mirrors data_event_calendar.csv columns
CREATE TABLE calendar_events (
  "IA Event Date" TEXT,
  Region TEXT,
  "Nearby Universities" TEXT,
  "Suggested Lecture Window" TEXT,
  "Course Alignment" TEXT
);

-- QR stats summary (flat — mirrors qr.py /stats response shape)
CREATE TABLE qr_stats (
  referral_code TEXT,
  speaker_name TEXT,
  event_name TEXT,
  scan_count INTEGER,
  membership_interest_count INTEGER,
  generated_at TEXT
);

-- Feedback stats (stored as JSON blob — mirrors feedback.py /stats response)
CREATE TABLE feedback_stats (
  id INTEGER PRIMARY KEY,
  stats_json TEXT
);
```

**Data seed design (from CONTEXT.md decisions):**
- ~10 specialists: real-ish names matching CPP domain (e.g., Dr. Sarah Chen, Marcus Webb, Priya Nair)
- 5 events: AI Hackathon, ITC, Bronco Startup Challenge, IA West Annual Summit, Tech Career Fair
- Pipeline funnel: 40 total records across stages (Matched: 15, Contacted: 12, Confirmed: 8, Attended: 4, Member Inquiry: 1)
- 3 calendar assignment records
- 5 QR scan records
- 8 feedback records with mixed accept/decline decisions

**Cross-feature coherence rule:** Speaker names in `pipeline` must also appear in `specialists`. Event names in `pipeline` must appear in calendar records. This ensures all chart derivations produce coherent results.

### Anti-Patterns to Avoid

- **Per-chart `isMockData` flags:** CONTEXT.md locks page-level flag — one flag governs all charts on that page. Don't add per-chart booleans.
- **Mutating the returned array:** All mock data derivations must use spread/immutable patterns. `const displayData = isMockData ? MOCK_PIPELINE : pipelineRows` — never reassign `pipelineRows`.
- **Wrapping ALL endpoints:** Only wrap endpoints that feed chart-bearing pages. `POST /api/outreach/workflow` and `POST /api/matching/rank` do NOT need demo fallback (they are interactive, not chart data sources).
- **SQLAlchemy for demo.db:** Overkill. stdlib `sqlite3` with `row_factory = sqlite3.Row` is sufficient.
- **Dismissible badge:** CONTEXT.md says persistent and non-dismissible while mock data active.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Blue badge component | Custom CSS class strings inline everywhere | `DemoModeBadge.tsx` shared component | Single source of truth for badge style; easy to update |
| SQLite3 connection pooling | Manual connection management | `with sqlite3.connect(...) as conn:` context manager | Python stdlib handles cleanup; demo.db is read-only, pooling unnecessary |
| Recharts crash guard | Try/catch around chart render | Ensure upstream data is never empty (use mock data) | Recharts itself handles empty arrays fine; the real risk is upstream `[0].field` access patterns |

**Key insight:** The real fragility is not inside Recharts — it's in the JavaScript derivation functions (`stageCounts`, `matchVolume`, `calendarReach`, `buildRegionalPulse`) that assume non-empty arrays. Making sure `isMockData` is set before these derivations run is the actual fix.

---

## Common Pitfalls

### Pitfall 1: Empty Array vs API Error — Different Code Paths

**What goes wrong:** Developer only catches `catch` block (API error), misses the case where the API returns `200 OK []` (empty array). CONTEXT.md explicitly says both trigger Demo Mode.

**Why it happens:** `Promise.allSettled` already gives `"fulfilled"` for 200 OK empty array — the existing page code sets state to `[]` and moves on, leaving charts with nothing to render.

**How to avoid:** After destructuring `allSettled` results, check BOTH `status === "rejected"` AND `value.length === 0` (for array endpoints). For dict endpoints like feedback/stats, check `result.total_feedback === 0`.

**Warning signs:** Charts with axes but no bars/lines/funnel segments visible in demo — classic empty-data symptom.

### Pitfall 2: `source` Field Collides With Existing Dict Keys

**What goes wrong:** The existing pipeline records already have keys like `event_name`, `speaker_name`, etc. When you do `{**row, "source": "demo"}` and the original row contains a `source` key (unlikely but possible), you could get silent overwrite issues.

**Why it happens:** Spread merge is last-key-wins; if a production row ever had a `source` column, it would be overwritten.

**How to avoid:** Use a wrapper envelope instead of polluting row-level dicts:
```python
return {"data": rows, "source": "live"}  # for list endpoints
```
Then update `api.ts` fetch functions to destructure `{ data, source }`. This is cleaner than per-row injection and avoids any column collision.

**Note:** The per-row injection pattern is simpler for list endpoints where you just need `response[0]?.source`. Choose one pattern per endpoint type and be consistent.

### Pitfall 3: `matching.py` /rank Endpoint Does Not Need Fallback

**What goes wrong:** Developer adds demo.db fallback to `POST /api/matching/rank` trying to be thorough. This endpoint is interactive (user selects an event, triggers a rank). It is NOT a passive data load for charts.

**Why it happens:** "All API endpoints need fallback" misreads the CONTEXT.md scope.

**How to avoid:** Only add demo.db fallback to these endpoints:
- `GET /api/data/pipeline` — feeds Dashboard + Pipeline funnels
- `GET /api/data/specialists` — feeds Volunteers
- `GET /api/calendar/events` — feeds Dashboard reach trend
- `GET /api/calendar/assignments` — feeds Dashboard regional pulse
- `GET /api/feedback/stats` — feeds Dashboard + Pipeline feedback trend
- `GET /api/qr/stats` — feeds Pipeline QR section

### Pitfall 4: Recharts `FunnelChart` With `data={[]}` — Axis Labels

**What goes wrong:** FunnelChart with empty data still renders the `<Funnel>` and `<LabelList>` but they produce no visible shapes. In a demo, this looks broken.

**Why it happens:** Recharts gracefully handles empty data arrays — it won't throw, but it will render a blank canvas area. This is visually broken even if technically not an error.

**How to avoid:** This is the exact reason for Layer 3 mock constants — if `data.length === 0` after the API call, substitute mock data so Recharts always has something to render. The empty-array check is the primary guard.

### Pitfall 5: Dashboard `useEffect` — Multiple Data Sources, Single `isMockData` Flag

**What goes wrong:** Dashboard fetches 6 data sources in parallel (`allSettled`). Which one drives `isMockData`? If pipeline is live but feedback is empty, does the badge show?

**Why it happens:** CONTEXT.md says page-level flag, but Dashboard aggregates multiple domains.

**How to avoid:** Make `isMockData` true if ANY of the primary chart-backing sources returns demo/empty data. The badge text is "Demo Mode" — not "Pipeline Demo Mode." Coordinator only needs to know "some data on this page is demo." Set `isMockData = pipelineSource === "demo" || calendarSource === "demo" || feedbackSource === "demo"`.

---

## Code Examples

### Fetch Function Wrapper (api.ts)

```typescript
// Pattern for list-returning endpoints that need source detection
export async function fetchPipeline(): Promise<{ data: PipelineRecord[]; source: "live" | "demo" }> {
  const raw = await requestJson<unknown>("/api/data/pipeline");
  const payload = toRecordArray(raw);
  // Check for source field on first element (per-row injection pattern)
  const source = (payload[0]?.source as "live" | "demo") ?? "live";
  return {
    data: payload.map((item, i) => normalizePipelineRecord(item, i)),
    source,
  };
}

// Alternative: envelope pattern for dict endpoints
export async function fetchFeedbackStats(): Promise<{ data: FeedbackStatsSummary; source: "live" | "demo" }> {
  const raw = await requestJson<{ data?: unknown; source?: string } | unknown>("/api/feedback/stats");
  const sourceField = (raw as Record<string, unknown>)?.source as "live" | "demo" | undefined;
  const source = sourceField ?? "live";
  return {
    data: normalizeFeedbackStats(raw),
    source,
  };
}
```

### Page isMockData Hook Pattern

```typescript
// Inside Dashboard useEffect, after allSettled:
const pipelineResult = results[2]; // pipeline
const isMock =
  pipelineResult.status === "rejected" ||
  pipelineResult.value.source === "demo" ||
  pipelineResult.value.data.length === 0;
setIsMockData(isMock);
setPipeline(isMock ? MOCK_PIPELINE : pipelineResult.value.data);
```

### FastAPI demo_db.py Helper

```python
# src/api/demo_db.py
import sqlite3
from pathlib import Path
from typing import Any

_DEMO_DB_PATH = (Path(__file__).parent.parent.parent / "data" / "demo.db").resolve()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DEMO_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_demo_pipeline() -> list[dict[str, Any]]:
    with _connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM pipeline").fetchall()]


def load_demo_specialists() -> list[dict[str, Any]]:
    with _connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM specialists").fetchall()]


def load_demo_calendar_events() -> list[dict[str, Any]]:
    with _connect() as conn:
        return [dict(row) for row in conn.execute("SELECT * FROM calendar_events").fetchall()]


def load_demo_qr_stats() -> dict[str, Any]:
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM qr_stats").fetchall()
    entries = [dict(row) for row in rows]
    return {
        "total_generated": len(entries),
        "total_scans": sum(r["scan_count"] for r in entries),
        "total_conversions": sum(r["membership_interest_count"] for r in entries),
        "entries": entries,
        "source": "demo",
    }


def load_demo_feedback_stats() -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute("SELECT stats_json FROM feedback_stats ORDER BY id DESC LIMIT 1").fetchone()
    import json
    stats = json.loads(dict(row)["stats_json"]) if row else {}
    return {**stats, "source": "demo"}
```

### DemoModeBadge Component

```tsx
// frontend/src/app/components/ui/DemoModeBadge.tsx
export function DemoModeBadge() {
  return (
    <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">
      Demo Mode
    </span>
  );
}
```

### demo.db Seed Script Pattern

```python
# scripts/seed_demo_db.py — run once to create data/demo.db
import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/demo.db")

PIPELINE_ROWS = [
    # stage_order: Matched=0, Contacted=1, Confirmed=2, Attended=3, Member Inquiry=4
    {"event_name": "AI for a Better Future Hackathon", "speaker_name": "Dr. Sarah Chen", "match_score": "0.89", "rank": "1", "stage": "Attended", "stage_order": "3"},
    # ... ~40 total rows
]

SPECIALIST_ROWS = [
    {"Name": "Dr. Sarah Chen", "Board Role": "President", "Metro Region": "Los Angeles — West", "Company": "TechBridge AI", "Title": "VP Data Science", "Expertise Tags": "AI, machine learning, hackathons"},
    # ... ~10 rows
]
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Streamlit `demo_mode.py` JSON fixtures | FastAPI demo.db SQLite3 | Phase 14 (new) | FastAPI path has no fallback today — must add |
| Recharts graceful empty (no crash, but visually blank) | Mock data ensures never-blank charts | Phase 14 (new) | Empty arrays look broken in a demo |

**Existing patterns to reuse:**
- `ImageWithFallback.tsx` shows the `useState(false)` error-gate pattern — same shape for `isMockData` boolean
- `emptyFeedbackStatsSummary()` / `emptyQrStatsSummary()` in `api.ts` are already typed empty-state factories — the mock data constants follow the same pattern but with real-looking values

---

## Open Questions

1. **Return envelope vs per-row `source` injection for list endpoints**
   - What we know: Per-row injection (`[{...row, source: "demo"}]`) is simpler on the backend. Envelope (`{"data": [...], "source": "demo"}`) requires updating every fetch function signature in `api.ts`.
   - What's unclear: Whether breaking the current `fetchPipeline() -> PipelineRecord[]` signature to `fetchPipeline() -> { data, source }` is acceptable given Phase 15 Playwright tests may rely on the current shape.
   - Recommendation: Use per-row injection for list endpoints (read `payload[0]?.source`). Use envelope for dict endpoints (feedback stats, qr stats). This minimizes API surface changes.

2. **Whether `matching.py /rank` needs any fallback**
   - What we know: AIMatching page calls `rankSpeakers(eventName)` — if no events exist, `rankSpeakers` is never called.
   - What's unclear: If events load but ranking fails (embeddings missing), AIMatching shows an error state. Should layer-3 mock ranked matches be added?
   - Recommendation: Yes — add a `MOCK_RANKED_MATCHES` constant for the AIMatching page layer-3 safety net, even though the backend doesn't serve these via demo.db (the `/rank` endpoint is user-triggered, not passive).

3. **demo.db seeding strategy: script vs committed file**
   - What we know: `data/` directory is checked in; `data/demo.db` would be a binary file (~50KB).
   - What's unclear: Whether committing a binary SQLite file to git is acceptable.
   - Recommendation: Commit a `scripts/seed_demo_db.py` script AND commit the resulting `data/demo.db` binary. The binary is small and ensures the demo works without running a setup step. Add `data/demo.db` to `.gitattributes` as binary.

---

## Validation Architecture

nyquist_validation is enabled in `.planning/config.json`.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing — see `tests/` with 50+ test files) |
| Config file | None found — pytest discovers from `tests/` directory |
| Quick run command | `pytest tests/test_api_data.py -x -q` |
| Full suite command | `pytest tests/ -x -q --ignore=tests/test_e2e_playwright.py` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| POLISH-04 | `GET /api/data/pipeline` returns demo rows when CSV is empty or missing | unit | `pytest tests/test_api_data.py::test_pipeline_fallback_to_demo -x` | ❌ Wave 0 |
| POLISH-04 | `GET /api/feedback/stats` returns demo stats when feedback log is empty | unit | `pytest tests/test_api_feedback.py::test_feedback_stats_fallback_to_demo -x` | ❌ Wave 0 |
| POLISH-04 | `GET /api/qr/stats` returns demo stats when manifest is empty | unit | `pytest tests/test_api_qr.py::test_qr_stats_fallback_to_demo -x` | ❌ Wave 0 |
| POLISH-04 | `load_demo_pipeline()` returns non-empty list from demo.db | unit | `pytest tests/test_demo_db.py::test_load_demo_pipeline -x` | ❌ Wave 0 |
| POLISH-05 | Fallback response includes `source: "demo"` field | unit | `pytest tests/test_demo_db.py::test_source_field_present -x` | ❌ Wave 0 |
| POLISH-04 | React layer-3 MOCK_PIPELINE matches PipelineRecord shape | manual | Visual review of TypeScript types — no runtime test needed | N/A |

**Note on TestClient:** STATE.md records that `TestClient` can hang in this environment. Existing tests use direct route/helper verification. New tests for demo.db fallback should also use direct function calls (call `load_demo_pipeline()` directly, not via HTTP).

### Sampling Rate

- **Per task commit:** `pytest tests/test_demo_db.py -x -q`
- **Per wave merge:** `pytest tests/test_api_data.py tests/test_api_feedback.py tests/test_api_qr.py tests/test_demo_db.py -x -q`
- **Phase gate:** Full suite green (excluding known-hang Playwright tests) before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_demo_db.py` — covers `load_demo_*()` functions and `source` field presence
- [ ] Fallback assertions in `tests/test_api_data.py` — `test_pipeline_fallback_to_demo`
- [ ] Fallback assertions in `tests/test_api_feedback.py` — `test_feedback_stats_fallback_to_demo`
- [ ] Fallback assertions in `tests/test_api_qr.py` — `test_qr_stats_fallback_to_demo`
- [ ] `data/demo.db` file — must exist before any test can run

---

## Sources

### Primary (HIGH confidence)

- Direct code inspection: `src/api/routers/data.py`, `matching.py`, `calendar.py`, `feedback.py`, `qr.py` — router patterns confirmed
- Direct code inspection: `frontend/src/lib/api.ts` — fetch functions, normalization helpers, interface definitions
- Direct code inspection: `frontend/src/app/pages/Dashboard.tsx`, `Pipeline.tsx`, `AIMatching.tsx`, `Volunteers.tsx` — chart derivation logic, `allSettled` usage, existing state patterns
- Direct code inspection: `data/*.csv` headers — confirmed column names for demo.db schema
- Direct code inspection: `.planning/config.json` — `nyquist_validation: true` confirmed

### Secondary (MEDIUM confidence)

- Recharts 2.15.2 empty data behavior: Recharts renders gracefully (no throw) on empty arrays for `BarChart`, `LineChart`, `FunnelChart` — verified by understanding of recharts v2 internals and confirmed by the existing empty-state code paths already in `emptyFeedbackStatsSummary()` usage pattern.

### Tertiary (LOW confidence)

- Python `sqlite3.Row.row_factory` thread safety: Standard library docs say `sqlite3.connect()` connections are not thread-safe by default. For a read-only demo.db accessed from FastAPI async handlers, creating a new connection per request (as shown in `_connect()`) is safe.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already in use; Python stdlib sqlite3 needs no new deps
- Architecture: HIGH — all integration points confirmed via direct code inspection
- Pitfalls: HIGH — identified from actual code patterns (e.g., `allSettled` usage, `payload[0]?.field` access patterns)
- Demo.db schema: HIGH — column names read directly from CSV headers

**Research date:** 2026-03-26
**Valid until:** 2026-04-25 (stable tech, 30 days)
