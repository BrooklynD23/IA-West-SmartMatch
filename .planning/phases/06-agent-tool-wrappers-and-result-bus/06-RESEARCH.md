# Phase 6: Agent Tool Wrappers and Result Bus - Research

**Researched:** 2026-03-24
**Domain:** Python threading, queue-based result bus, Streamlit fragment polling, thin adapter pattern, JSON contact data
**Confidence:** HIGH

## Summary

Phase 6 replaces Phase 5's `stub_execute()` with real background-threaded service calls. The codebase already has all the required service functions (`scrape_university`, `rank_speakers_for_event`, `generate_outreach_email`), a clean `ActionProposal` state machine, and a well-understood Streamlit mock pattern in `conftest.py`. The core work is three things: (1) creating thin adapter modules under `src/coordinator/tools/` that call existing functions without modifying their signatures, (2) a `result_bus.py` module that dispatches daemon threads and manages per-proposal `queue.Queue` instances in session state, and (3) a POC contact data layer (`data/poc_contacts.json` + `src/coordinator/tools/contacts_tool.py`) with overdue-follow-up detection.

The critical constraint is that `st.fragment(run_every=2)` is used for polling — this is available in Streamlit 1.31+ and avoids blocking the script thread. The `ActionProposal` dataclass currently has no `result_queue` field; that field must not be added. Storing queues on the dataclass is unsafe because `queue.Queue` is not JSON-serializable, which can cause Streamlit state errors. The safest approach is to store queues in a separate `result_queues` session state key rather than on the dataclass, so the dataclass contract stays unchanged and the 501-test baseline stays intact.

**Primary recommendation:** Store per-proposal `Queue` instances in `st.session_state["result_queues"][proposal_id]` — separate from the `ActionProposal` dataclass — so zero dataclass fields change and the 501-test baseline stays intact.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### Tool Wrapper Architecture
- Tool wrappers live in `src/coordinator/tools/` package with one module per service — consistent with Phase 5's `src/coordinator/` pattern
- Thin adapter functions that import and call existing functions unchanged (e.g., `scrape_university()`, `rank_speakers_for_event()`) — per STATE.md "zero signature changes" constraint
- Dict mapping intent names to tool callables, registered at module level — mirrors Phase 5's intent to agent mapping
- Tools call existing functions directly (no NemoClaw) — this IS the fallback path; Phase 7 adds NemoClaw as an optional orchestration layer on top

#### Background Threading and Result Bus
- `threading.Thread(daemon=True)` + `queue.Queue` per task — per STATE.md decision; each approved action spawns a daemon thread, result posted to queue
- `st.fragment(run_every=2)` polling loop checks queue, updates `action_proposals[id].status` — per STATE.md decision
- Each `ActionProposal` gets its own `Queue` instance stored in session state — independent status, no cross-task corruption
- Thread catches exceptions, posts `{status: "failed", error: str}` to its queue — action card shows error with retry option

#### POC Contact Data Layer and Display
- JSON file (`data/poc_contacts.json`) loaded into session state — hackathon-appropriate, no DB needed; seed with sample contacts from CPP event data
- Contact schema: `{name, email, org, role, comm_history: [{date, type, summary}], last_contact, follow_up_due}` — covers POC-01 (history) and POC-02 (follow-up tracking)
- New section within Command Center — expandable contact cards, overdue contacts highlighted, triggered by `check_contacts` intent
- Proactive suggestion (same as Phase 5 staleness check) — on Command Center load, check `follow_up_due < today`, inject suggestion card for overdue contacts

### Claude's Discretion
- Exact thread naming and daemon configuration
- Queue timeout values for polling
- POC seed data content (derived from CPP event contacts)
- Result formatting for Command Center display
- Retry logic details for failed actions

### Deferred Ideas (OUT OF SCOPE)
- NemoClaw orchestrator integration replacing direct dispatch (Phase 7)
- Live per-agent swimlane dashboard with real-time status (Phase 7 — DASH-01, DASH-02)
- Jarvis speaking result summaries via TTS (Phase 7)
- POC follow-up as proactive Jarvis suggestion in HITL flow (Phase 7 — POC-03)
- Agent self-modification or dynamic tool creation (out of scope — ORCH-05)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| ORCH-01 | Existing SmartMatch discovery, matching, and outreach functions are wrapped as agent-callable tool services | Tool wrappers in `src/coordinator/tools/` call existing functions unchanged — verified signatures below |
| ORCH-02 | NemoClaw/OpenClaw dispatches sub-agents for webscraping, matching, and outreach tasks | Phase 6 uses direct dispatch (fallback path); NemoClaw deferred to Phase 7 — locked decision |
| ORCH-03 | Sub-agents can run in parallel with independent status tracking | `threading.Thread(daemon=True)` + per-proposal `queue.Queue` + `st.fragment(run_every=2)` polling — each proposal's queue is independent |
| POC-01 | Coordinator can view and manage POC contacts with communication history | `data/poc_contacts.json` + `contacts_tool.py` + expandable cards in Command Center |
| POC-02 | Coordinator can track follow-up reminders and see overdue contacts | `follow_up_due` field compared to today's date, highlighted in contact cards + proactive suggestion |
</phase_requirements>

## Standard Stack

### Core (all already installed in project .venv)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `threading` | stdlib | Daemon thread dispatch for agent tasks | No extra install; daemon=True ensures no hang on exit |
| `queue.Queue` | stdlib | Thread-safe result delivery to main thread | No extra install; thread-safe by design; `get_nowait()` for non-blocking poll |
| `streamlit` | >=1.31 | `st.fragment(run_every=2)` polling | Already used for entire UI; fragment API is the approved non-blocking poll pattern |
| `json` | stdlib | Load/save `poc_contacts.json` | No extra install; simple, readable, hackathon-appropriate |
| `datetime` | stdlib | `follow_up_due` comparison for overdue detection | Already used in `suggestions.py` and `approval.py` |
| `dataclasses` | stdlib | Contact schema frozen dataclass | Pattern already used for `ParsedIntent` |
| `pytest` | project .venv | Test framework | 501-test baseline already runs with `.venv/bin/python -m pytest` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `unittest.mock.patch` | stdlib | Mock `scrape_university`, `rank_speakers_for_event`, `generate_outreach_email` in tool tests | Isolate tool wrapper tests from live network/Gemini calls |
| `unittest.mock.MagicMock` | stdlib | Mock `threading.Thread` in result_bus tests | Prevent actual thread spawn during unit tests |

### Existing Service Function Signatures (verified from source)

```python
# src/scraping/scraper.py line 377
def scrape_university(
    url: str,
    method: Literal["bs4", "playwright"] = "bs4",
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> dict[str, Any]: ...

# src/matching/engine.py line 179
def rank_speakers_for_event(
    event_row: pd.Series,
    speakers_df: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embedding: np.ndarray,
    ia_event_calendar: pd.DataFrame,
    top_n: int = 10,
    weights: Optional[dict[str, float]] = None,
    conversion_overrides: Optional[dict[str, float]] = None,
    student_interest_override: Optional[float] = None,
) -> list[dict[str, Any]]: ...

# src/outreach/email_gen.py line 229
def generate_outreach_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
    model: str = EMAIL_MODEL,
    temperature: float = EMAIL_TEMPERATURE,
) -> dict[str, str]: ...
```

**Installation:** No new packages required. All dependencies already present.

## Architecture Patterns

### Recommended Project Structure (additions to existing src/)

```
src/coordinator/tools/
├── __init__.py              # exports TOOL_REGISTRY dict
├── discovery_tool.py        # wraps scrape_university()
├── matching_tool.py         # wraps rank_speakers_for_event()
├── outreach_tool.py         # wraps generate_outreach_email()
└── contacts_tool.py         # reads/queries poc_contacts.json

src/coordinator/
└── result_bus.py            # dispatch(), poll_result(), TOOL_REGISTRY reference

data/
└── poc_contacts.json        # seed contact records

tests/
├── test_discovery_tool.py
├── test_matching_tool.py
├── test_outreach_tool.py
├── test_contacts_tool.py
└── test_result_bus.py
```

### Pattern 1: Thin Adapter Tool Wrapper

**What:** A single public function `run(params: dict) -> dict` that calls the existing service function with extracted params and returns a normalized result dict. No business logic — just extraction, call, and normalization.

**When to use:** For every service wrapper. Keeps tool modules shallow and trivially testable.

**Example:**
```python
# src/coordinator/tools/discovery_tool.py
from __future__ import annotations
from typing import Any
from src.scraping.scraper import UNIVERSITY_TARGETS, scrape_university

TOOL_NAME = "discover_events"

def run(params: dict[str, Any]) -> dict[str, Any]:
    """Thin adapter: call scrape_university for a target university.

    Returns:
        {"status": "ok", "events": [...], "source": "cache"|"live"}
    """
    target_key = params.get("university", next(iter(UNIVERSITY_TARGETS)))
    target = UNIVERSITY_TARGETS.get(target_key, UNIVERSITY_TARGETS[next(iter(UNIVERSITY_TARGETS))])
    result = scrape_university(
        url=target["url"],
        method=target["method"],
    )
    events = result.get("events", [])
    return {"status": "ok", "events": events, "source": result.get("source", "live")}
```

### Pattern 2: Result Bus — Dispatch and Poll

**What:** `dispatch(proposal_id, tool_fn, params)` spawns a daemon thread. Thread writes `{"status": "completed", "result": ...}` or `{"status": "failed", "error": ...}` to a `queue.Queue` stored in `st.session_state["result_queues"][proposal_id]`. The `@st.fragment(run_every=2)` polling loop drains queues and updates proposal status.

**When to use:** Every `Approve` button click for a real action.

**Example (result_bus.py):**
```python
# src/coordinator/result_bus.py
from __future__ import annotations
import queue
import threading
import logging
from typing import Any, Callable
import streamlit as st

logger = logging.getLogger(__name__)


def dispatch(
    proposal_id: str,
    tool_fn: Callable[[dict[str, Any]], dict[str, Any]],
    params: dict[str, Any],
) -> None:
    """Spawn a daemon thread for tool_fn(params); post result to per-proposal queue.

    Stores queue in st.session_state["result_queues"][proposal_id].
    Caller must transition proposal to "executing" before calling this.
    """
    result_queues: dict[str, queue.Queue] = st.session_state.setdefault(
        "result_queues", {}
    )
    q: queue.Queue = queue.Queue(maxsize=1)
    result_queues[proposal_id] = q

    def _worker() -> None:
        try:
            result = tool_fn(params)
            q.put({"status": "completed", "result": result})
        except Exception as exc:
            logger.error("Tool %s failed: %s", proposal_id, exc)
            q.put({"status": "failed", "error": str(exc)})

    t = threading.Thread(target=_worker, name=f"tool-{proposal_id[:8]}", daemon=True)
    t.start()


def poll_results() -> list[tuple[str, dict[str, Any]]]:
    """Drain all queues with available results. Returns list of (proposal_id, payload).

    Non-blocking: uses get_nowait(), skips empty queues.
    """
    result_queues: dict[str, queue.Queue] = st.session_state.get("result_queues", {})
    ready = []
    for pid, q in list(result_queues.items()):
        try:
            payload = q.get_nowait()
            ready.append((pid, payload))
        except queue.Empty:
            pass
    return ready
```

**Example (fragment in command_center.py):**
```python
@st.fragment(run_every=2)
def _poll_result_bus() -> None:
    """Poll result queues every 2s; update proposal status in session state."""
    from src.coordinator.result_bus import poll_results
    proposals = st.session_state.get("action_proposals", {})
    for proposal_id, payload in poll_results():
        proposal = proposals.get(proposal_id)
        if proposal is None:
            continue
        if payload["status"] == "completed":
            proposal.status = "completed"
            proposal.result = _format_result(payload["result"])
        else:
            proposal.status = "failed"
            proposal.result = f"Error: {payload.get('error', 'unknown')}"
```

### Pattern 3: Approve Button Wires Real Dispatch

**What:** Replace `proposal.stub_execute()` in `_render_action_card` with `proposal.approve()` + `proposal.status = "executing"` + `dispatch(proposal.id, TOOL_REGISTRY[proposal.intent], proposal.params)`.

**When to use:** Only for proposals whose intent is in `TOOL_REGISTRY`. Fall back to `stub_execute()` for `"unknown"` intent.

**Example (TOOL_REGISTRY in `src/coordinator/tools/__init__.py`):**
```python
from src.coordinator.tools.discovery_tool import run as _discovery_run
from src.coordinator.tools.matching_tool import run as _matching_run
from src.coordinator.tools.outreach_tool import run as _outreach_run
from src.coordinator.tools.contacts_tool import run as _contacts_run

TOOL_REGISTRY: dict[str, callable] = {
    "discover_events":    _discovery_run,
    "rank_speakers":      _matching_run,
    "generate_outreach":  _outreach_run,
    "check_contacts":     _contacts_run,
}
```

### Pattern 4: POC Contact Schema

**What:** Plain JSON file seeded from CPP contacts. Load once into session state. `contacts_tool.run()` queries in-memory list.

**Schema:**
```json
[
  {
    "name": "Jane Smith",
    "email": "jsmith@cpp.edu",
    "org": "Cal Poly Pomona",
    "role": "Career Center Director",
    "comm_history": [
      {"date": "2026-02-10", "type": "email", "summary": "Introduced SmartMatch program"},
      {"date": "2026-03-01", "type": "call",  "summary": "Discussed spring fair schedule"}
    ],
    "last_contact": "2026-03-01",
    "follow_up_due": "2026-03-15"
  }
]
```

### Anti-Patterns to Avoid

- **Blocking in button callback:** Never call `scrape_university()` or any slow function directly inside `if st.button("Approve"):`. That blocks the script thread. Always dispatch to a daemon thread.
- **Storing Queue on ActionProposal dataclass:** `ActionProposal` is a mutable dataclass already tested by 501 tests. Adding a `Queue` field risks serialization errors (Streamlit may attempt to serialize session state), breaks the existing contract, and triggers test failures. Store queues in a separate `result_queues` session state key.
- **get() with block=True in polling fragment:** Using `q.get(timeout=2)` inside the fragment blocks the polling fragment for up to 2 seconds per queue. Use `get_nowait()` with `queue.Empty` catch.
- **Modifying existing function signatures:** `scrape_university`, `rank_speakers_for_event`, `generate_outreach_email` must not gain new parameters. Tool wrappers extract what they need from `params` dict and call with positional/keyword args only.
- **Importing streamlit in tool modules:** Tool modules (`discovery_tool.py`, etc.) must stay pure Python — no `import streamlit`. This is the established pattern for all `src/coordinator/` modules.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Thread-safe result delivery | Custom shared-dict with lock | `queue.Queue` | Queue is thread-safe by design; dict requires explicit `threading.Lock` and `acquire/release` |
| Background task execution | `asyncio.create_task` in Streamlit | `threading.Thread(daemon=True)` | Streamlit runs a sync script; asyncio event loop is not running in script context |
| Non-blocking UI updates | Manual `st.rerun()` in a loop | `@st.fragment(run_every=2)` | Fragment reruns only itself, not the whole page; prevents full-page flickering |
| POC data persistence | SQLite or SQLAlchemy | JSON file in `data/` | Hackathon scope; JSON is readable, version-controlled, zero-dependency |
| Overdue date comparison | Custom date math | `datetime.date.fromisoformat()` + `< datetime.date.today()` | Standard library; already used in `suggestions.py` staleness check |

**Key insight:** Python's stdlib threading + queue is purpose-built for this pattern — a producer thread writes one result, a consumer thread (via fragment poll) reads it. No third-party library is needed.

## Common Pitfalls

### Pitfall 1: Queue stored on ActionProposal causes session state serialization errors

**What goes wrong:** Streamlit may attempt to serialize session state objects in certain deployment modes. `queue.Queue` is not JSON-serializable and is not safe to store directly on the `ActionProposal` dataclass instance in `st.session_state["action_proposals"]`. This causes a runtime error.

**Why it happens:** Streamlit's session state is designed to hold JSON-compatible values. Non-serializable objects on the dataclass break the contract.

**How to avoid:** Store queues in `st.session_state["result_queues"]` keyed by `proposal_id` — a separate dict. The `ActionProposal` dataclass stores only safe primitives (`str`, `dict`, `None`).

**Warning signs:** Serialization errors or `TypeError` in Streamlit logs when session state is accessed.

### Pitfall 2: st.fragment(run_every=2) not available in older Streamlit

**What goes wrong:** `@st.fragment(run_every=2)` was introduced in Streamlit 1.31.0 (December 2023). If the installed version is older, `AttributeError: module 'streamlit' has no attribute 'fragment'` occurs.

**Why it happens:** The project may have pinned an older Streamlit version.

**How to avoid:** Verify with `pip show streamlit` in the project .venv. If below 1.31, upgrade. The conftest.py Streamlit mock must also add a `fragment` mock for tests.

**Warning signs:** `AttributeError` on `st.fragment` during app startup or test import.

### Pitfall 3: Thread dispatched but queue never drained — proposal stuck in "executing"

**What goes wrong:** If the `@st.fragment(run_every=2)` polling call is not placed in the render path of the Command Center tab, the queue fills (maxsize=1 blocks the worker) and the thread hangs.

**Why it happens:** Fragment must be called (rendered) during each Streamlit script run for the auto-rerun trigger to activate.

**How to avoid:** Call `_poll_result_bus()` unconditionally at the top of `render_command_center_tab()`, before conversation history rendering.

**Warning signs:** Proposal status stays `"executing"` indefinitely; worker thread alive but blocked on `q.put()`.

### Pitfall 4: conftest.py missing mock for st.fragment

**What goes wrong:** Any test that imports `command_center.py` after the `@st.fragment(run_every=2)` decorator is added will fail with `AttributeError` because the conftest Streamlit mock does not define `fragment`.

**Why it happens:** The Phase 5 conftest.py does not include `_mock_st.fragment`.

**How to avoid:** Add `_mock_st.fragment = lambda **kw: (lambda f: f)` to conftest.py in the Streamlit mock block. This passes the decorator through without any polling side effects.

**Warning signs:** `AttributeError: module 'streamlit' has no attribute 'fragment'` when running `pytest`.

### Pitfall 5: rank_speakers_for_event requires multiple DataFrames — tool wrapper needs pre-loaded data

**What goes wrong:** `rank_speakers_for_event` requires `speakers_df`, `speaker_embeddings`, `event_embedding`, and `ia_event_calendar` — not just an event name string. If the tool wrapper tries to pull these from params and they are absent, it crashes.

**Why it happens:** The matching engine was designed for in-session DataFrame context, not fire-and-forget dispatch.

**How to avoid:** The matching tool wrapper must capture required DataFrames from session state in the button callback (on the main thread) and pass them as serializable inputs via `params` at dispatch time. Never read `st.session_state` from inside a daemon thread — session state is not thread-safe in Streamlit.

**Warning signs:** `KeyError` or `AttributeError` when the matching tool runs without prior data load.

### Pitfall 6: Parallel tasks corrupting each other's status

**What goes wrong:** If two proposals share the same `Queue` object, one task's result overwrites the other's.

**Why it happens:** Bugs in queue initialization — e.g., checking `if proposal_id not in result_queues` and reusing a stale queue from a previous run.

**How to avoid:** Always create a fresh `queue.Queue()` in `dispatch()` — unconditionally overwrite `result_queues[proposal_id]`. A UUID is per-run unique anyway.

**Warning signs:** One "Approve" populates another proposal's result card.

## Code Examples

### Dispatch on Approve (command_center.py modification)

```python
# In _render_action_card(), replace proposal.stub_execute() block:
from src.coordinator.tools import TOOL_REGISTRY
from src.coordinator.result_bus import dispatch

if st.button("Approve", key=f"approve_{proposal.id}", type="primary"):
    proposal.approve()
    tool_fn = TOOL_REGISTRY.get(proposal.intent)
    if tool_fn:
        proposal.status = "executing"
        dispatch(proposal.id, tool_fn, proposal.params)
    else:
        proposal.stub_execute()   # fallback for unknown/unmapped intents
    st.rerun()
```

### Polling Fragment (command_center.py addition)

```python
@st.fragment(run_every=2)
def _poll_result_bus() -> None:
    from src.coordinator.result_bus import poll_results
    proposals = st.session_state.get("action_proposals", {})
    for proposal_id, payload in poll_results():
        proposal = proposals.get(proposal_id)
        if proposal is None:
            continue
        if payload["status"] == "completed":
            proposal.status = "completed"
            proposal.result = _format_result(payload["result"])
        else:
            proposal.status = "failed"
            proposal.result = f"Error: {payload.get('error', 'unknown')}"
    # Fragment auto-reruns every 2s; no explicit st.rerun() needed inside fragment
```

### POC Contacts Tool (contacts_tool.py)

```python
# src/coordinator/tools/contacts_tool.py
from __future__ import annotations
import datetime
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
_CONTACTS_PATH = Path(__file__).resolve().parents[3] / "data" / "poc_contacts.json"

def _load_contacts() -> list[dict[str, Any]]:
    try:
        return json.loads(_CONTACTS_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.warning("poc_contacts.json not found or invalid: %s", exc)
        return []

def run(params: dict[str, Any]) -> dict[str, Any]:
    contacts = _load_contacts()
    today = datetime.date.today()
    overdue = [
        c for c in contacts
        if c.get("follow_up_due")
        and datetime.date.fromisoformat(c["follow_up_due"]) < today
    ]
    return {
        "status": "ok",
        "contacts": contacts,
        "overdue": overdue,
        "total": len(contacts),
        "overdue_count": len(overdue),
    }
```

### Test Pattern for Tool Wrappers

```python
# tests/test_discovery_tool.py
from unittest.mock import patch
from src.coordinator.tools.discovery_tool import run

class TestDiscoveryTool:
    @patch("src.coordinator.tools.discovery_tool.scrape_university")
    def test_run_returns_events(self, mock_scrape):
        mock_scrape.return_value = {"events": [{"name": "Tech Fair"}], "source": "cache"}
        result = run({"university": "UCLA"})
        assert result["status"] == "ok"
        assert len(result["events"]) == 1
        mock_scrape.assert_called_once()

    @patch("src.coordinator.tools.discovery_tool.scrape_university")
    def test_run_propagates_exception(self, mock_scrape):
        mock_scrape.side_effect = RuntimeError("Network error")
        # Tool wrapper propagates — result_bus thread catches this
        import pytest
        with pytest.raises(RuntimeError):
            run({})
```

### Test Pattern for Result Bus

```python
# tests/test_result_bus.py
import queue
import time
import streamlit as st
from src.coordinator.result_bus import dispatch, poll_results

class TestResultBus:
    def setup_method(self):
        st.session_state["result_queues"] = {}

    def test_dispatch_posts_completed_result(self):
        def fast_tool(params):
            return {"events": ["A"]}
        dispatch("pid-1", fast_tool, {})
        time.sleep(0.1)   # let thread finish
        ready = poll_results()
        assert len(ready) == 1
        pid, payload = ready[0]
        assert pid == "pid-1"
        assert payload["status"] == "completed"

    def test_dispatch_posts_failed_on_exception(self):
        def failing_tool(params):
            raise ValueError("boom")
        dispatch("pid-2", failing_tool, {})
        time.sleep(0.1)
        ready = poll_results()
        assert ready[0][1]["status"] == "failed"
        assert "boom" in ready[0][1]["error"]

    def test_two_parallel_tasks_are_independent(self):
        results = {}
        def slow_tool(params):
            time.sleep(0.05)
            return {"val": params["val"]}
        dispatch("pid-a", slow_tool, {"val": "A"})
        dispatch("pid-b", slow_tool, {"val": "B"})
        time.sleep(0.2)
        for pid, payload in poll_results():
            results[pid] = payload
        assert results["pid-a"]["result"]["val"] == "A"
        assert results["pid-b"]["result"]["val"] == "B"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `stub_execute()` blocks and returns fake result | Real daemon thread + queue poll | Phase 6 | Actual service calls; coordinator sees real data |
| No contact management | `poc_contacts.json` + overdue detection | Phase 6 | POC-01, POC-02 satisfied |
| Intent dispatches to stub | Intent dispatches via `TOOL_REGISTRY` | Phase 6 | ORCH-01 satisfied |
| Single-threaded action execution | Parallel daemon threads with independent queues | Phase 6 | ORCH-03 satisfied |

**Deprecated/outdated after this phase:**
- `ActionProposal.stub_execute()`: Still present (for tests), but `_render_action_card` bypasses it when `TOOL_REGISTRY` has the intent. Do not remove — 501 tests depend on it.

## Open Questions

1. **Does the matching tool wrapper need session state access for DataFrames?**
   - What we know: `rank_speakers_for_event` requires `speakers_df`, `speaker_embeddings`, `event_embedding`, `ia_event_calendar` — heavyweight inputs not passable via simple `params` dict
   - What's unclear: Whether these are already in session state at approval time, or need to be loaded fresh in the thread
   - Recommendation: Capture DataFrames from session state in the Approve button callback (on the main thread) and include them in `params` before calling `dispatch()`. Never read `st.session_state` from inside a daemon thread — Streamlit session state is not thread-safe from background threads.

2. **Should `st.fragment` mock in conftest be a no-op decorator or raise?**
   - What we know: Tests don't test fragment polling (that requires actual Streamlit runtime); fragment mock should be transparent
   - What's unclear: Whether any test directly asserts on fragment behavior
   - Recommendation: `_mock_st.fragment = lambda **kw: (lambda f: f)` — identity decorator, no-op. Tests for `_poll_result_bus` should test the inner function directly, not through the decorator.

3. **What POC seed contacts should be used?**
   - What we know: `data/data_cpp_events_contacts.csv` exists and contains CPP event contact data
   - What's unclear: The exact column names in that CSV file
   - Recommendation: Read `data_cpp_events_contacts.csv` to extract ~5 sample contacts for the JSON seed. Use realistic `follow_up_due` dates — at least 2 overdue (before 2026-03-24) to demonstrate POC-02 immediately on demo day.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (project .venv) |
| Config file | none — run via `pytest tests/` |
| Quick run command | `.venv/bin/python -m pytest tests/test_result_bus.py tests/test_discovery_tool.py tests/test_matching_tool.py tests/test_outreach_tool.py tests/test_contacts_tool.py -x` |
| Full suite command | `.venv/bin/python -m pytest tests/ -x` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ORCH-01 | Discovery/matching/outreach wrapped as callable tools | unit | `.venv/bin/python -m pytest tests/test_discovery_tool.py tests/test_matching_tool.py tests/test_outreach_tool.py -x` | Wave 0 |
| ORCH-02 | Direct dispatch (fallback path) works end-to-end | unit | `.venv/bin/python -m pytest tests/test_result_bus.py -x` | Wave 0 |
| ORCH-03 | Two parallel tasks execute independently | unit | `.venv/bin/python -m pytest tests/test_result_bus.py::TestResultBus::test_two_parallel_tasks_are_independent -x` | Wave 0 |
| POC-01 | Contacts tool returns full comm_history | unit | `.venv/bin/python -m pytest tests/test_contacts_tool.py -x` | Wave 0 |
| POC-02 | Contacts tool identifies overdue contacts | unit | `.venv/bin/python -m pytest tests/test_contacts_tool.py -x` | Wave 0 |
| Regression | All 501 existing tests still pass | regression | `.venv/bin/python -m pytest tests/ -x` | exists |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_result_bus.py tests/test_discovery_tool.py tests/test_matching_tool.py tests/test_outreach_tool.py tests/test_contacts_tool.py -x`
- **Per wave merge:** `.venv/bin/python -m pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `tests/test_discovery_tool.py` — covers ORCH-01 (discovery wrapper)
- [ ] `tests/test_matching_tool.py` — covers ORCH-01 (matching wrapper)
- [ ] `tests/test_outreach_tool.py` — covers ORCH-01 (outreach wrapper)
- [ ] `tests/test_contacts_tool.py` — covers POC-01, POC-02
- [ ] `tests/test_result_bus.py` — covers ORCH-02, ORCH-03
- [ ] `src/coordinator/tools/__init__.py` — TOOL_REGISTRY module (new package)
- [ ] `src/coordinator/result_bus.py` — dispatch + poll_results
- [ ] `data/poc_contacts.json` — seed data file
- [ ] conftest.py addition: `_mock_st.fragment = lambda **kw: (lambda f: f)` — required for fragment decorator import in command_center.py tests

## Sources

### Primary (HIGH confidence)

- Python stdlib `threading` documentation — `Thread(daemon=True)` behavior; daemon threads do not block process exit
- Python stdlib `queue.Queue` documentation — `get_nowait()` raises `queue.Empty` (non-blocking), `Queue(maxsize=1)` blocks producer when full
- Source code direct read: `src/coordinator/approval.py` lines 19-71 — `ActionProposal` dataclass fields and state machine
- Source code direct read: `src/scraping/scraper.py` line 377 — `scrape_university` full signature
- Source code direct read: `src/matching/engine.py` line 179 — `rank_speakers_for_event` full signature
- Source code direct read: `src/outreach/email_gen.py` line 229 — `generate_outreach_email` full signature
- Source code direct read: `tests/conftest.py` — Streamlit mock structure and all mocked attributes
- Source code direct read: `src/ui/command_center.py` — existing `_render_action_card`, `_handle_text_command`, approval flow
- Source code direct read: `src/coordinator/suggestions.py` — proactive suggestion pattern for overdue extension
- Verified test count: 501 tests collected (run `.venv/bin/python -m pytest tests/ --co -q`)

### Secondary (MEDIUM confidence)

- Streamlit `@st.fragment` API: available since Streamlit 1.31.0 (Dec 2023); `run_every` parameter enables auto-polling interval in seconds — based on training data knowledge of Streamlit changelog; project already uses modern Streamlit patterns confirming version compatibility

### Tertiary (LOW confidence)

- Streamlit session state serialization behavior with non-JSON-serializable objects: documented as a known caution in Streamlit community resources. Exact failure mode varies by deployment configuration. The recommendation to keep queues separate from `ActionProposal` is a defensive pattern based on general Python serialization constraints.

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — all stdlib, all already installed, function signatures verified directly from source
- Architecture: HIGH — patterns derived directly from existing `src/coordinator/` structure and STATE.md locked decisions; no speculation
- Pitfalls: HIGH for threading/queue pitfalls (stdlib semantics); MEDIUM for Streamlit fragment edge cases (deployment-mode dependent)

**Research date:** 2026-03-24
**Valid until:** 2026-04-24 (stable stdlib patterns; Streamlit fragment API stable since 1.31)
