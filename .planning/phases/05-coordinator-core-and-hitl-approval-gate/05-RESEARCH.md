# Phase 5: Coordinator Core and HITL Approval Gate - Research

**Researched:** 2026-03-23
**Domain:** Python state machines, Gemini intent parsing, Streamlit session-state UI patterns
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Intent Parsing Design**
- Use structured JSON prompt via existing `gemini_client.py` REST pattern — send user text + available actions list, expect `{intent, agent, params, reasoning}` JSON response
- Support 4 core intents: `discover_events`, `rank_speakers`, `generate_outreach`, `check_contacts`, plus `unknown` fallback — maps 1:1 to existing SmartMatch services
- Handle parsing failures with a graceful fallback card showing "Could not understand" with raw text and a rephrase suggestion — no crash, no silent failure
- Run intent parsing inline in Streamlit script thread (~1-2s Gemini call) — result needed immediately to render action card

**Action Card UI**
- Each action card shows: agent name, action description, Jarvis reasoning, and editable parameters — matches HITL-01 requirement exactly
- Action cards appear inline in conversation history as Jarvis message bubbles with embedded approve/reject buttons — maintains chronological flow from Phase 4
- Approve/reject via `st.button` with `session_state` tracking per card — each card gets a unique key, button click updates `action_proposals[id].status`, triggers `st.rerun()`
- Edit params flow uses `st.expander` within the card, collapsed by default — expand to edit, then approve

**Approval State Machine**
- 5 states: `proposed` → `approved` → `executing` → `completed`/`failed`, plus `rejected` — clean lifecycle matching Phase 6 dispatch contract
- Store approval state in `st.session_state["action_proposals"]` as a dict keyed by UUID — follows established session_state pattern from runtime_state.py
- Multiple proposals queue and coexist with independent state — coordinator can issue several commands before approving
- Phase 5 stub execution: immediate transition to "completed" with mock result after ~1s delay — proves state machine end-to-end without real agents

**Proactive Suggestions (ORCH-04)**
- Trigger: data staleness check — if `scraped_events` timestamp > 24h old or empty, Jarvis suggests "Discovery data is stale — re-run scraper?"
- Surface on Command Center tab load — check staleness conditions during render, inject suggestion if not already present
- Use same action card format as parsed intents with `source: "proactive"` flag — consistent approve/reject UX
- Max 1 active proactive suggestion at a time — avoid overwhelming the coordinator

### Claude's Discretion
- Exact Gemini prompt template wording and JSON schema for intent parsing
- CSS styling of action cards (borders, colors, status indicators)
- UUID generation strategy for action proposals
- Mock result text content for stub execution
- Staleness threshold tuning (24h is the starting point)

### Deferred Ideas (OUT OF SCOPE)
- Real agent dispatch and background execution (Phase 6 — ORCH-01, ORCH-02, ORCH-03)
- POC contact management integration (Phase 6 — POC-01, POC-02)
- NemoClaw orchestrator integration (Phase 7)
- Live per-agent dashboard swimlanes (Phase 7 — DASH-01, DASH-02)
- Multiple proactive trigger types beyond data staleness (future enhancement)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HITL-01 | Every agent action displays a proposed action card with agent name, action description, and reasoning | `ActionProposal` dataclass + `_render_action_card()` renders agent/description/reasoning before any execution |
| HITL-02 | Coordinator can approve, reject, or edit parameters on any proposed action before execution | 3-button pattern (Approve/Reject/Edit) on each card keyed by UUID; `st.expander` for param editing |
| HITL-03 | No agent action executes without explicit coordinator approval | State machine enforces `proposed → approved → executing` — stub execute only fires on explicit Approve click |
| ORCH-04 | Jarvis proactively suggests actions when data is stale or follow-ups are overdue | `check_staleness_conditions()` in `suggestions.py` injects proactive proposal at Command Center tab render |
</phase_requirements>

---

## Summary

Phase 5 replaces the hardcoded echo handler in `_handle_text_command()` with a real Gemini-powered intent parser and a complete HITL approval state machine. The phase is entirely self-contained: it introduces three new pure-Python modules (`intent_parser.py`, `approval.py`, `suggestions.py`) under `src/coordinator/`, extends the Command Center UI with action card rendering and approve/reject buttons, and extends `runtime_state.py` with the `action_proposals` session-state key. No existing function signatures change; the 392-test baseline must remain green after every plan.

The critical architectural constraint is that **the state machine lives in `st.session_state`**, never in a blocking loop or background thread. Phase 5 does not dispatch real agents — stub execution proves the lifecycle end-to-end. The Phase 6 dispatch contract (`proposed → approved → executing → completed/failed`) is the direct continuation.

The second architectural constraint is **test isolation**: new modules must have no Streamlit imports (pure Python), allowing them to be tested without the mock-streamlit conftest plumbing. Only the UI layer (`command_center.py`) imports Streamlit, and tests for it use the existing mock-streamlit pattern from `conftest.py`.

**Primary recommendation:** Build bottom-up — `approval.py` dataclass and state machine first (pure Python, fully testable), then `intent_parser.py` (calls `gemini_client.generate_text`, returns `ParsedIntent`), then `suggestions.py` (staleness check, no external calls), then UI integration in `command_center.py` last.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `uuid` (stdlib) | 3.12 stdlib | Generate unique proposal IDs | No install required; `uuid.uuid4()` produces collision-resistant keys |
| `dataclasses` (stdlib) | 3.12 stdlib | `ActionProposal`, `ParsedIntent` as typed DTOs | Project already uses `@dataclass(frozen=True)` in `config.py`; consistent pattern |
| `datetime` (stdlib) | 3.12 stdlib | Staleness timestamp comparison | Already used in `command_center.py` for `HH:MM:SS` formatting |
| `json` (stdlib) | 3.12 stdlib | Parse Gemini JSON response in intent parser | Already used in `gemini_client.py` |
| `streamlit` | existing (pinned) | `st.button`, `st.expander`, `st.session_state` for card UI | All Streamlit UI patterns established in Phases 1-4 |
| `gemini_client.generate_text` | existing | LLM call for intent parsing | REST-based, no SDK dependency; project's established Gemini wrapper |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `time.sleep` (stdlib) | 3.12 stdlib | 1-second stub execution delay | Stub only — simulates execution latency without real agent |
| `logging` (stdlib) | 3.12 stdlib | Error logging in intent_parser and approval | Project uses `logger = logging.getLogger(__name__)` pattern everywhere |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `uuid.uuid4()` | `secrets.token_hex(8)` | uuid4 is idiomatic and produces full UUID strings; token_hex is shorter but less standard for dict keys |
| Inline state machine dict | `transitions` library | `transitions` adds install complexity; 5-state machine is simple enough that a plain `if/elif` guard in `approve()` / `reject()` / `execute()` methods is cleaner |
| `st.expander` for param edit | `st.form` | `st.form` requires a submit button; `st.expander` with direct text_input widgets fits the single-card approve flow better |

**Installation:** No new packages required. All functionality uses stdlib + existing project dependencies.

---

## Architecture Patterns

### Recommended Project Structure

```
src/
├── coordinator/             # NEW — Phase 5 modules
│   ├── __init__.py
│   ├── intent_parser.py     # pure Python — ParsedIntent, parse_intent()
│   ├── approval.py          # pure Python — ActionProposal, state transitions
│   └── suggestions.py       # pure Python — check_staleness_conditions()
├── ui/
│   └── command_center.py    # EXTENDED — action card rendering + approve/reject
└── runtime_state.py         # EXTENDED — add action_proposals key
tests/
├── test_intent_parser.py    # NEW — parse_intent unit tests + Gemini mock
├── test_approval.py         # NEW — state machine transition tests
├── test_suggestions.py      # NEW — staleness condition tests
└── test_command_center.py   # EXTENDED — card rendering + button tests
```

### Pattern 1: ParsedIntent Dataclass

**What:** A frozen dataclass returned by `parse_intent()` — carries all fields needed to construct an `ActionProposal`. Immutable; callers cannot accidentally mutate the parsed result.

**When to use:** Single return type for intent parsing; makes tests clean (compare whole struct, not loose dicts).

```python
# src/coordinator/intent_parser.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

SUPPORTED_INTENTS = frozenset({
    "discover_events",
    "rank_speakers",
    "generate_outreach",
    "check_contacts",
    "unknown",
})

@dataclass(frozen=True)
class ParsedIntent:
    intent: str           # one of SUPPORTED_INTENTS
    agent: str            # display name, e.g. "Discovery Agent"
    params: dict[str, Any]
    reasoning: str
    raw_text: str         # original user text, preserved for fallback card
```

### Pattern 2: ActionProposal Dataclass + State Machine

**What:** Mutable dataclass (not frozen) that owns its lifecycle state. `approve()`, `reject()`, and `stub_execute()` are methods that guard transitions with `if self.status != expected` checks.

**When to use:** Stores proposal state in `st.session_state["action_proposals"][id]`. Methods enforce valid transitions; invalid calls raise `ValueError` so tests catch bad flows immediately.

```python
# src/coordinator/approval.py
from __future__ import annotations
import uuid
import datetime
from dataclasses import dataclass, field
from typing import Any, Literal

ProposalStatus = Literal["proposed", "approved", "executing", "completed", "failed", "rejected"]

@dataclass
class ActionProposal:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent: str = ""
    agent: str = ""
    description: str = ""
    reasoning: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    status: ProposalStatus = "proposed"
    source: Literal["parsed", "proactive"] = "parsed"
    created_at: str = field(default_factory=lambda: datetime.datetime.now().strftime("%H:%M:%S"))
    result: str | None = None

    def approve(self) -> None:
        if self.status != "proposed":
            raise ValueError(f"Cannot approve proposal in state '{self.status}'")
        self.status = "approved"

    def reject(self) -> None:
        if self.status != "proposed":
            raise ValueError(f"Cannot reject proposal in state '{self.status}'")
        self.status = "rejected"

    def stub_execute(self) -> None:
        """Transition proposed → executing → completed with mock result."""
        if self.status != "approved":
            raise ValueError(f"Cannot execute proposal in state '{self.status}'")
        self.status = "executing"
        # Phase 5: stub — real dispatch wires in Phase 6
        self.result = f"[Stub] {self.agent} completed successfully."
        self.status = "completed"
```

### Pattern 3: Gemini Intent Parsing via generate_text

**What:** Send a structured prompt to `gemini_client.generate_text()` requesting JSON output. Parse the response with `json.loads()`. On any failure (malformed JSON, missing keys, network error), return a `ParsedIntent` with `intent="unknown"` — never propagate the exception to the UI.

**When to use:** Called from `_handle_text_command()` in `command_center.py`. Runs synchronously (inline), ~1-2s; result is available before `st.rerun()`.

```python
# src/coordinator/intent_parser.py (core logic)
import json
from src.gemini_client import generate_text, GeminiAPIError
from src.config import GEMINI_API_KEY, GEMINI_TEXT_MODEL

ACTION_REGISTRY = [
    {"intent": "discover_events",   "agent": "Discovery Agent",  "description": "Scrape universities for new events"},
    {"intent": "rank_speakers",     "agent": "Matching Agent",   "description": "Rank speakers for a target event"},
    {"intent": "generate_outreach", "agent": "Outreach Agent",   "description": "Draft outreach emails for a match"},
    {"intent": "check_contacts",    "agent": "Contacts Agent",   "description": "Review POC contact status"},
]

_SYSTEM_PROMPT = """\
You are Jarvis, an AI coordinator assistant. Given a coordinator command and a list
of available agent actions, identify the best matching intent and return ONLY valid JSON.

Available actions:
{actions}

Response format (JSON only, no markdown):
{{
  "intent": "<one of the intent keys above, or 'unknown'>",
  "agent": "<agent display name>",
  "params": {{}},
  "reasoning": "<one sentence explaining why>"
}}
"""

def parse_intent(text: str) -> ParsedIntent:
    """Parse coordinator text into a structured intent. Never raises."""
    actions_str = json.dumps(ACTION_REGISTRY, indent=2)
    system = _SYSTEM_PROMPT.format(actions=actions_str)
    try:
        raw = generate_text(
            messages=[{"role": "user", "content": text}],
            api_key=GEMINI_API_KEY,
            model=GEMINI_TEXT_MODEL,
            system_instruction=system,
            temperature=0.1,
            max_output_tokens=300,
            timeout=10.0,
        )
        data = json.loads(raw)
        intent = data.get("intent", "unknown")
        if intent not in SUPPORTED_INTENTS:
            intent = "unknown"
        return ParsedIntent(
            intent=intent,
            agent=data.get("agent", "Jarvis"),
            params=data.get("params", {}),
            reasoning=data.get("reasoning", ""),
            raw_text=text,
        )
    except (GeminiAPIError, json.JSONDecodeError, KeyError, TypeError):
        return ParsedIntent(
            intent="unknown",
            agent="Jarvis",
            params={},
            reasoning="",
            raw_text=text,
        )
```

### Pattern 4: Action Card Rendering in _render_conversation_history

**What:** Conversation history entries with `role: "proposal"` render as action cards instead of plain chat bubbles. Cards embed `st.button` calls with unique keys derived from the proposal UUID.

**When to use:** `_render_conversation_history()` is the single place where history is rendered. The pattern keeps rendering logic co-located and avoids separate render paths.

```python
# In command_center.py — extended _render_conversation_history
for entry in history:
    role = entry.get("role", "user")
    if role == "proposal":
        proposal_id = entry.get("action_id")
        proposal = st.session_state.get("action_proposals", {}).get(proposal_id)
        if proposal:
            _render_action_card(proposal)
    else:
        # existing chat bubble logic unchanged
        ...
```

### Pattern 5: Proactive Suggestion Injection

**What:** `check_staleness_conditions()` in `suggestions.py` inspects `st.session_state["scraped_events"]` and returns a list of `ActionProposal` objects. Called once at tab load; injects into `action_proposals` and `conversation_history` only if no active proactive suggestion exists (max 1).

**When to use:** Called at the top of `render_command_center_tab()` before rendering the voice panel, so suggestions appear in conversation history immediately on tab open.

```python
# src/coordinator/suggestions.py
from __future__ import annotations
import datetime
from src.coordinator.approval import ActionProposal

STALENESS_HOURS = 24

def check_staleness_conditions(
    scraped_events: list,
    scraped_at: str | None,
) -> list[ActionProposal]:
    """Return proactive suggestions based on data staleness. Pure function."""
    suggestions = []
    if not scraped_events or _is_stale(scraped_at, hours=STALENESS_HOURS):
        suggestions.append(ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="Re-run event discovery scraper",
            reasoning="Discovery data is stale or empty — re-running will surface new events.",
            source="proactive",
        ))
    return suggestions

def _is_stale(timestamp_str: str | None, hours: int) -> bool:
    if not timestamp_str:
        return True
    try:
        ts = datetime.datetime.fromisoformat(timestamp_str)
        return (datetime.datetime.now() - ts).total_seconds() > hours * 3600
    except ValueError:
        return True
```

### Anti-Patterns to Avoid

- **Calling `stub_execute()` in a button callback directly:** Streamlit reruns the entire script on each interaction. Calling `stub_execute()` inside the `if st.button(...)` block is fine for stubs (synchronous), but must NOT be the pattern for Phase 6 (real dispatch must use queue/thread). Write the stub call so Phase 6 can replace it with `queue.put(proposal.id)` without restructuring the if-block.
- **Putting Streamlit imports in `approval.py` or `intent_parser.py`:** These modules must be pure Python so tests run without the mock-streamlit conftest plumbing. Only `command_center.py` imports `streamlit`.
- **Using `st.session_state` inside `approval.py`:** The approval module does not know about Streamlit. The UI layer reads from `session_state`, mutates the proposal object, and triggers `st.rerun()`. The proposal is the pure state; session_state is the store.
- **Mutating `conversation_history` entries to track proposal status:** Status lives on the `ActionProposal` object, not in the history list entry. The history entry only holds an `action_id` reference. This avoids divergence between the two.
- **Generating a new proactive suggestion on every rerun:** The injection guard must check `action_proposals` for any existing proactive proposal in `proposed` or `approved` state before injecting a new one. Without this guard, every button click (which triggers `st.rerun()`) injects a duplicate.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| UUID generation | Custom incrementing counter | `uuid.uuid4()` | Counters reset on session restart and cause key collisions across reruns |
| JSON extraction from LLM response | Regex parsing of freeform text | Structured prompt + `json.loads()` with fallback | Regex-based extraction breaks on whitespace/formatting variations; structured prompt constrains the model reliably |
| State machine enforcement | ad-hoc status string checks scattered in UI | Methods on `ActionProposal` (`approve()`, `reject()`) with guard clauses | Scattered checks create untestable state transition paths; method-based state machine is testable in isolation |
| Streamlit widget key uniqueness | Manual integer counters | UUID-derived keys: `f"approve_{proposal.id}"` | Manual counters require careful management; UUID keys are globally unique and survive reruns |

**Key insight:** Gemini JSON parsing is inherently fragile unless the prompt strongly constrains the output format. Setting `temperature=0.1` and making the system prompt say "Response format (JSON only, no markdown)" dramatically reduces the probability of receiving markdown-fenced JSON or prose explanations.

---

## Common Pitfalls

### Pitfall 1: Duplicate Buttons from Streamlit Reruns
**What goes wrong:** After approving a proposal, `st.rerun()` fires. If the `action_proposals` dict still contains the proposal and its status is not checked before rendering buttons, the Approve button re-renders and produces a duplicate-key Streamlit error, or worse, allows double-approval.
**Why it happens:** Streamlit re-executes the entire script on every interaction. Button rendering is unconditional unless guarded by status.
**How to avoid:** Render Approve/Reject buttons only when `proposal.status == "proposed"`. For any other status, render a status indicator (e.g., "Approved", "Rejected", "Completed") as plain text instead.
**Warning signs:** `DuplicateWidgetID` exception in Streamlit, or proposals transitioning to `approved` more than once.

### Pitfall 2: LLM Returns Markdown-Fenced JSON
**What goes wrong:** Gemini wraps the JSON in triple-backtick markdown fences: ` ```json\n{...}\n``` `. `json.loads()` raises `JSONDecodeError`, causing the fallback card to appear for a valid command.
**Why it happens:** Even with explicit instructions, Gemini occasionally adds markdown formatting, especially with higher temperatures.
**How to avoid:** Set `temperature=0.1` for intent parsing. Add a pre-processing step: strip leading/trailing whitespace, then if the string starts with ` ``` `, extract the content between the first and last ``` blocks before parsing.
**Warning signs:** Fallback "Could not understand" cards appearing for clearly valid commands in testing.

### Pitfall 3: Proactive Suggestion Flooding
**What goes wrong:** Every Streamlit rerun (triggered by any button click or text input) calls `check_staleness_conditions()`, which injects a new proactive suggestion each time. The conversation history grows unbounded with duplicate suggestions.
**Why it happens:** `render_command_center_tab()` is called on every rerun. Without a guard, `check_staleness_conditions()` injects unconditionally.
**How to avoid:** Before injecting a suggestion, check if any `action_proposals` entry has `source == "proactive"` and `status in ("proposed", "approved")`. Only inject if none exist.
**Warning signs:** Multiple identical "Discovery data is stale" cards appearing in conversation history.

### Pitfall 4: Breaking Existing Tests on `_handle_text_command`
**What goes wrong:** Phase 5 replaces the echo body of `_handle_text_command()`. The existing tests in `test_command_center.py` assert `assistant_entry["text"] == "Received: hello"` and `assistant_entry["intent"] == "echo"`. These assertions will fail after replacement.
**Why it happens:** Tests were written against the Phase 4 echo behavior, which is intentionally temporary.
**How to avoid:** The existing echo tests MUST be updated as part of Phase 5. The replacement tests verify intent parsing behavior: that an assistant entry with `role="proposal"` or `intent` set to the parsed intent appears. The Phase 4 echo tests become the Phase 5 proposal tests. **This is expected and correct — not a regression.**
**Warning signs:** 7 tests in `TestHandleTextCommand` failing after the `_handle_text_command` replacement is a planned update, not a bug.

### Pitfall 5: `st.expander` Context Manager Scope in History Rendering
**What goes wrong:** When rendering action cards inside a loop with `st.expander`, using it as a context manager inside an `st.markdown(unsafe_allow_html=True)` block produces unexpected rendering. Expanders cannot be nested inside HTML-injected markdown.
**Why it happens:** `st.markdown` with `unsafe_allow_html=True` renders raw HTML; Streamlit components like `st.expander` live in the component tree, not the HTML tree. Mixing the two creates layout gaps.
**How to avoid:** Keep action cards fully in Streamlit's component model — use `st.container()`, `st.columns()`, `st.expander()`, and `st.button()`. Do not wrap the entire card in a `st.markdown` HTML div. Apply CSS classes only for cosmetic borders/backgrounds via a preceding `st.markdown` with just the wrapper div, or via global CSS injected in `styles.py`.

---

## Code Examples

### Verified Pattern: Gemini generate_text call for structured JSON

```python
# Source: src/gemini_client.py — generate_text signature already established
raw = generate_text(
    messages=[{"role": "user", "content": user_text}],
    api_key=GEMINI_API_KEY,
    model=GEMINI_TEXT_MODEL,
    system_instruction=_SYSTEM_PROMPT.format(actions=actions_str),
    temperature=0.1,          # low temp for deterministic JSON
    max_output_tokens=300,
    timeout=10.0,
)
```

### Verified Pattern: session_state init guard

```python
# Source: src/runtime_state.py — init_runtime_state() pattern
def init_runtime_state() -> None:
    # ... existing keys ...
    if "action_proposals" not in st.session_state:
        st.session_state["action_proposals"] = {}
    if "scraped_events_timestamp" not in st.session_state:
        st.session_state["scraped_events_timestamp"] = None
```

### Verified Pattern: UUID-keyed button to avoid DuplicateWidgetID

```python
# All button keys derived from proposal UUID
if proposal.status == "proposed":
    col_approve, col_reject = st.columns(2)
    with col_approve:
        if st.button("Approve", key=f"approve_{proposal.id}", type="primary"):
            proposal.approve()
            proposal.stub_execute()
            st.rerun()
    with col_reject:
        if st.button("Reject", key=f"reject_{proposal.id}"):
            proposal.reject()
            st.rerun()
```

### Verified Pattern: markdown-fence strip for Gemini JSON safety

```python
def _strip_markdown_fence(text: str) -> str:
    """Remove triple-backtick fences that Gemini occasionally adds."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        # Remove first line (```json or ```) and last line (```)
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        return "\n".join(inner).strip()
    return stripped
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Hardcoded echo reply in `_handle_text_command` | Gemini intent parsing returning `ParsedIntent` | Phase 5 | Replaces placeholder; existing echo tests must be updated |
| Conversation history as flat list of `{role, text}` dicts | History entries with `role="proposal"` referencing `ActionProposal` objects by UUID | Phase 5 | Decouples rendering logic from state; proposal state lives on `ActionProposal`, not in history |

**Deprecated/outdated after Phase 5:**
- Echo reply logic (`jarvis_reply = f"Received: {text}"`) in `_handle_text_command`: replaced by intent parsing + proposal creation
- `intent == "echo"` in history entries: replaced by real parsed intents + proposal role

---

## Open Questions

1. **`scraped_events_timestamp` key in session state**
   - What we know: `runtime_state.py` initializes `scraped_events` as an empty list but has no `scraped_events_timestamp` key. The staleness check needs a timestamp to determine if data is stale.
   - What's unclear: Does the scraper currently write a timestamp when it populates `scraped_events`? If not, Phase 5 must also add `scraped_events_timestamp` tracking in `runtime_state.py` (and wherever the scraper writes to session_state).
   - Recommendation: Add `scraped_events_timestamp: None` to `init_runtime_state()` in Phase 5. For Phase 5 testing purposes, if the key is `None`, treat data as stale (triggers the suggestion). The scraper integration that writes the timestamp is Phase 6 scope.

2. **TTS for action card results**
   - What we know: CONTEXT.md mentions "action card results should also be spoken." The Phase 4 TTS playback pattern in `_handle_text_command` uses `split_into_sentences` + `synthesize_to_wav_bytes`.
   - What's unclear: Should TTS fire on the stub "completed" result, or only on real agent results in Phase 6?
   - Recommendation: Speak the stub result text when `proposal.status` transitions to `completed`. Keep the TTS call in the Approve button handler, consistent with Phase 4's TTS pattern. This proves the TTS plumbing works end-to-end even in stub mode.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.3.4 |
| Config file | `pytest.ini` or inline (verify: none detected — uses `pyproject.toml` or `setup.cfg` if present) |
| Quick run command | `python3 -m pytest tests/test_intent_parser.py tests/test_approval.py tests/test_suggestions.py tests/test_command_center.py -q --tb=short` |
| Full suite command | `python3 -m pytest tests/ -q --tb=short --ignore=tests/test_voice_tts.py --ignore=tests/test_voice_stt.py` |

Note: The full suite currently has 18 collection errors due to missing native libraries (`dotenv`, `soundfile`, `faster_whisper`). Tests for Phase 5 pure-Python modules will be isolated and collectable without these dependencies.

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HITL-01 | Action card renders agent name, description, reasoning | unit | `pytest tests/test_command_center.py::TestRenderActionCard -x` | Wave 0 |
| HITL-02 | Approve transitions status to approved/executing/completed | unit | `pytest tests/test_approval.py::TestApprovalStateMachine -x` | Wave 0 |
| HITL-02 | Reject transitions status to rejected | unit | `pytest tests/test_approval.py::TestApprovalStateMachine::test_reject -x` | Wave 0 |
| HITL-02 | Edit params: edited values are used on approve | unit | `pytest tests/test_approval.py::TestApprovalStateMachine::test_approve_with_edited_params -x` | Wave 0 |
| HITL-03 | No execution without approve (stub_execute blocked on proposed) | unit | `pytest tests/test_approval.py::TestApprovalStateMachine::test_stub_execute_requires_approved -x` | Wave 0 |
| ORCH-04 | Staleness triggers proactive suggestion | unit | `pytest tests/test_suggestions.py::TestStalenessCheck -x` | Wave 0 |
| ORCH-04 | No suggestion injected when fresh data present | unit | `pytest tests/test_suggestions.py::TestStalenessCheck::test_no_suggestion_when_fresh -x` | Wave 0 |
| ORCH-04 | Max 1 active proactive suggestion | unit | `pytest tests/test_command_center.py::TestProactiveSuggestion::test_no_duplicate_injection -x` | Wave 0 |
| (baseline) | 392 existing tests continue to pass | regression | `python3 -m pytest tests/ -q --tb=short` | Existing |

### Sampling Rate
- **Per task commit:** `python3 -m pytest tests/test_approval.py tests/test_intent_parser.py tests/test_suggestions.py -q --tb=short`
- **Per wave merge:** `python3 -m pytest tests/ -q --tb=short` (full suite, ignoring native lib collection errors)
- **Phase gate:** Full suite green (new tests) + 392 existing tests unbroken before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/test_approval.py` — covers HITL-02, HITL-03 (state machine transitions)
- [ ] `tests/test_intent_parser.py` — covers HITL-01 upstream (ParsedIntent shape, unknown fallback, JSON parse failure)
- [ ] `tests/test_suggestions.py` — covers ORCH-04 (staleness detection, suggestion shape)
- [ ] `tests/test_command_center.py` (extended) — covers card rendering, button key uniqueness, duplicate injection guard

Note on existing `test_command_center.py`: The 7 tests in `TestHandleTextCommand` asserting `"Received: ..."` echo behavior **must be updated** in Wave 1 (the `_handle_text_command` replacement plan). These are not Wave 0 gaps — they are planned test updates.

---

## Sources

### Primary (HIGH confidence)
- Direct code inspection: `src/gemini_client.py` — `generate_text()` signature, `_post_json()` pattern, `GeminiAPIError`
- Direct code inspection: `src/runtime_state.py` — `init_runtime_state()` guard pattern, session_state keys
- Direct code inspection: `src/ui/command_center.py` — `_handle_text_command()`, `_render_conversation_history()`, TTS playback pattern
- Direct code inspection: `src/config.py` — `GEMINI_API_KEY`, `GEMINI_TEXT_MODEL`, `@dataclass(frozen=True)` pattern
- Direct code inspection: `tests/conftest.py` — mock-streamlit setup, pure-Python module isolation requirement
- Direct code inspection: `.planning/phases/05-coordinator-core-and-hitl-approval-gate/05-CONTEXT.md` — all locked decisions

### Secondary (MEDIUM confidence)
- Python 3.12 stdlib: `uuid`, `dataclasses`, `json`, `datetime` — all present in 3.12 stdlib; no verification needed beyond confirming project uses Python 3.12 (WSL2 environment confirmed `python3` maps to 3.12)
- Streamlit session_state + button pattern: established through direct observation of Phase 4 implementation in `command_center.py`

### Tertiary (LOW confidence)
- Gemini JSON consistency at `temperature=0.1`: based on general LLM behavior knowledge — LOW confidence on exact failure rate; the markdown-fence strip defense is recommended regardless

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries are stdlib or existing project deps; no new installs
- Architecture: HIGH — patterns derived directly from Phase 4 codebase, not from general knowledge
- Pitfalls: MEDIUM-HIGH — Pitfalls 1-3 are directly observable from the codebase; Pitfall 2 (LLM JSON) is MEDIUM (general LLM knowledge)
- Test infrastructure: HIGH — pytest 8.3.4 confirmed in requirements.txt; conftest.py mock pattern confirmed

**Research date:** 2026-03-23
**Valid until:** 2026-04-23 (stable stack — Streamlit and Gemini client are pinned; valid until Phase 6 planning)
