# Architecture Research

**Domain:** Voice + Agent Orchestration layer on existing Streamlit CRM (brownfield integration)
**Researched:** 2026-03-23
**Confidence:** MEDIUM — KittenTTS is well-documented; NemoClaw is alpha (released March 2026) with limited API documentation; Streamlit audio/threading patterns are MEDIUM confidence from official docs

---

## Standard Architecture

### System Overview

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                          STREAMLIT UI LAYER                                    │
│                                                                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  Existing Tabs   │  │  Command Center  │  │   Voice I/O Panel            │ │
│  │  (Matches,       │  │  (new tab)       │  │   (new panel/sidebar)        │ │
│  │   Discovery,     │  │  Agent dispatch  │  │   Mic input + TTS output     │ │
│  │   Pipeline, etc) │  │  status board    │  │   Text fallback              │ │
│  └──────────────────┘  └────────┬─────────┘  └──────────────┬───────────────┘ │
└───────────────────────────────── │ ──────────────────────────│────────────────┘
                                   │ st.session_state          │ audio bytes
                                   ▼                           ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                          COORDINATOR CORE (new)                                │
│                                                                                │
│  ┌──────────────────────────┐    ┌──────────────────────────────────────────┐  │
│  │   Voice Bridge           │    │   Jarvis Coordinator                     │  │
│  │   - st.audio_input /     │    │   - Intent parsing (Gemini/NemoClaw)     │  │
│  │     streamlit-mic-       │    │   - Action proposal generation           │  │
│  │     recorder             │    │   - Human-in-the-loop gate               │  │
│  │   - faster-whisper STT   │    │   - Approval state machine               │  │
│  │   - KittenTTS TTS        │    │   - Agent result aggregation             │  │
│  └──────────┬───────────────┘    └────────────────┬─────────────────────────┘  │
│             │ text transcript                     │ approved actions            │
└─────────────│─────────────────────────────────────│────────────────────────────┘
              │                                     │
              ▼                                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     AGENT ORCHESTRATION LAYER (new)                            │
│                                                                                │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │                    NemoClaw Orchestrator (Lead Agent)                     │  │
│  │     - Decomposes tasks into parallel sub-agent dispatches                 │  │
│  │     - MCP tool bus for sub-agent communication                            │  │
│  │     - Policy-gated: no action executes without approval token             │  │
│  └─────────┬──────────────┬──────────────┬─────────────────┬────────────────┘  │
│            │              │              │                 │                   │
│  ┌─────────▼──┐  ┌────────▼───┐  ┌──────▼──────┐  ┌──────▼────────────────┐   │
│  │ Scraper    │  │ Matcher    │  │ Outreach    │  │ POC Contact Manager   │   │
│  │ Sub-Agent  │  │ Sub-Agent  │  │ Sub-Agent   │  │ Sub-Agent             │   │
│  └─────────┬──┘  └────────┬───┘  └──────┬──────┘  └──────┬────────────────┘   │
└────────────│──────────────│──────────────│────────────────│────────────────────┘
             │              │              │                │
             ▼              ▼              ▼                ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                     EXISTING SMARTMATCH SERVICES (unchanged API)               │
│                                                                                │
│  src/scraping/scraper.py   src/matching/engine.py   src/outreach/email_gen.py  │
│  src/data_loader.py        src/embeddings.py        src/runtime_state.py       │
│  src/gemini_client.py      src/similarity.py        src/feedback/acceptance.py │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | New or Existing |
|-----------|----------------|-----------------|
| Voice Bridge | Audio capture via browser mic, STT via faster-whisper, TTS via KittenTTS, audio playback via st.audio | NEW |
| Jarvis Coordinator | Intent parsing, action proposal, approval gate state machine, response synthesis | NEW |
| NemoClaw Orchestrator | Lead agent that decomposes intent into parallel sub-agent tasks, enforces policy gate | NEW |
| Scraper Sub-Agent | Wraps `src/scraping/scraper.py` as a NemoClaw MCP tool | NEW (thin wrapper) |
| Matcher Sub-Agent | Wraps `src/matching/engine.py` and `src/embeddings.py` as a NemoClaw MCP tool | NEW (thin wrapper) |
| Outreach Sub-Agent | Wraps `src/outreach/email_gen.py` and `src/outreach/ics_generator.py` as a NemoClaw MCP tool | NEW (thin wrapper) |
| POC Contact Manager Sub-Agent | New: maintains POC history, follow-ups, communication log | NEW (net-new logic) |
| Command Center Tab | Streamlit tab showing live agent status board, proposal queue, approval UI | NEW |
| Voice I/O Panel | Sidebar/panel rendering mic recorder widget and TTS audio player | NEW |
| Existing SmartMatch Services | All current business logic — not modified, consumed via function call | EXISTING (unchanged) |

---

## Recommended Project Structure

```
Category 3 - IA West Smart Match CRM/src/
├── app.py                        # existing — add Command Center + Voice Panel imports
├── config.py                     # existing — add NemoClaw/KittenTTS config keys
├── runtime_state.py              # existing — extend with agent queue + approval state
│
├── voice/                        # NEW — Voice I/O subsystem
│   ├── __init__.py
│   ├── bridge.py                 # Mic capture → STT transcript → TTS bytes pipeline
│   ├── stt.py                    # faster-whisper wrapper (audio bytes → text)
│   └── tts.py                   # KittenTTS wrapper (text → WAV bytes)
│
├── coordinator/                  # NEW — Jarvis coordinator core
│   ├── __init__.py
│   ├── intent.py                 # Parse transcript → intent + entities (via Gemini)
│   ├── proposal.py               # Build action proposal from intent
│   ├── approval.py               # Approval state machine (PENDING → APPROVED/REJECTED)
│   └── response.py               # Synthesize coordinator reply from agent results
│
├── agents/                       # NEW — NemoClaw sub-agent wrappers
│   ├── __init__.py
│   ├── orchestrator.py           # NemoClaw lead agent setup + dispatch
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── scraper_tool.py       # MCP tool wrapping src/scraping/scraper.py
│   │   ├── matcher_tool.py       # MCP tool wrapping src/matching/engine.py
│   │   ├── outreach_tool.py      # MCP tool wrapping src/outreach/*.py
│   │   └── poc_tool.py           # POC contact management (new logic + CSV persistence)
│   └── result_bus.py             # Thread-safe queue for agent results → session state
│
├── ui/                           # existing folder — add new tabs
│   ├── ...existing files...
│   ├── command_center.py         # NEW — Agent dispatch dashboard tab
│   └── voice_panel.py            # NEW — Voice I/O sidebar panel
│
├── poc/                          # NEW — POC contact data layer
│   ├── __init__.py
│   ├── store.py                  # CSV-backed POC contact store (immutable update pattern)
│   └── history.py                # Communication history log
│
└── ...existing modules...
```

### Structure Rationale

- **voice/**: Isolated subsystem. STT and TTS are pure functions (bytes in → text out, text in → bytes out). No Streamlit imports inside voice/. This makes them testable and reusable.
- **coordinator/**: Separates intent understanding from agent dispatch and approval gating. The approval state machine is the hard architectural constraint from PROJECT.md.
- **agents/**: NemoClaw orchestrator plus MCP tool wrappers. Tools are thin adapters — all business logic stays in existing `src/` modules. This avoids duplicating logic.
- **poc/**: Isolated data layer for the net-new POC contact management feature. CSV-backed for demo simplicity; easy to swap later.

---

## Architectural Patterns

### Pattern 1: Thin MCP Tool Wrappers Over Existing Services

**What:** Each sub-agent tool is a decorator-wrapped function that calls existing SmartMatch service functions directly, with no business logic duplication.

**When to use:** Whenever existing services already implement the correct logic. Sub-agent wrappers should be 10-30 lines, not 300.

**Trade-offs:** Existing services remain independently testable; wrapper changes don't affect core logic. Risk: tool schemas must stay in sync with underlying function signatures.

**Example:**
```python
# agents/tools/matcher_tool.py
from mcp.server.fastmcp import FastMCP
from src.matching.engine import rank_speakers_for_event

mcp = FastMCP("matcher")

@mcp.tool()
def rank_speakers(event_id: str, top_n: int = 5) -> dict:
    """Rank IA West speakers for the given event ID."""
    results = rank_speakers_for_event(event_id, top_n=top_n)
    return {"ranked_speakers": results}
```

### Pattern 2: Approval State Machine in Session State

**What:** Every agent action proposal is stored in `st.session_state["pending_actions"]` as a queue. The coordinator UI renders each pending action with Approve/Reject buttons. Only APPROVED actions are dispatched to NemoClaw.

**When to use:** Always — this is a hard architectural constraint per PROJECT.md ("all agent actions require coordinator sign-off").

**Trade-offs:** Adds latency between proposal and execution (intentional). Prevents runaway agent behavior. Coordinator maintains full control.

**State schema:**
```python
# In runtime_state.py (extended)
from dataclasses import dataclass, field
from enum import Enum

class ActionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    DONE = "done"
    FAILED = "failed"

@dataclass
class AgentAction:
    action_id: str
    agent_type: str          # "scraper" | "matcher" | "outreach" | "poc"
    description: str         # Human-readable: "Scrape 3 university pages for spring events"
    params: dict             # Tool call parameters
    status: ActionStatus = ActionStatus.PENDING
    result: dict | None = None
    error: str | None = None
```

### Pattern 3: Background Thread + Session Queue for Agent Execution

**What:** Approved actions are dispatched to a background daemon thread via a `queue.Queue`. The NemoClaw orchestrator runs in the daemon thread. Results are placed back on a result queue. A `@st.fragment` with `run_every=2` polls the result queue and updates session state.

**When to use:** Any time an agent action takes more than ~500ms (scraping, LLM calls). Streamlit's script thread must not block.

**Trade-offs:** Streamlit has no first-class async background support (as of v1.42). The `add_script_run_ctx` pattern attaches Streamlit context to the background thread so `st.*` calls work. Risk: if WebSocket reconnects, session state resets and in-flight actions are lost — mitigated by persisting action queue to a session file.

**Example:**
```python
# agents/result_bus.py
import queue
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

_dispatch_queue: queue.Queue = queue.Queue()
_result_queue: queue.Queue = queue.Queue()

def start_agent_worker(ctx) -> None:
    """Start daemon thread with Streamlit context attached."""
    thread = threading.Thread(target=_worker_loop, daemon=True)
    add_script_run_ctx(thread, ctx)
    thread.start()

def _worker_loop() -> None:
    while True:
        action = _dispatch_queue.get()
        try:
            result = _run_nemoclaw_action(action)
            _result_queue.put({"action_id": action.action_id, "result": result})
        except Exception as e:
            _result_queue.put({"action_id": action.action_id, "error": str(e)})
```

### Pattern 4: KittenTTS as a Pure TTS Service (Text-to-WAV-Bytes)

**What:** KittenTTS generates audio synchronously (no streaming API). Generate WAV bytes in memory via `soundfile` → encode to base64 or write to temp file → pass to `st.audio()` for browser playback.

**When to use:** All coordinator voice responses. Sentence-chunk the response text (split on `.` or `?`) and generate per-sentence to reduce latency if the response is long.

**Trade-offs:** No native streaming forces manual chunking. WAV at 24kHz is ~48KB/second — acceptable for short coordinator phrases. Not suitable for multi-paragraph audio generation.

**Example:**
```python
# voice/tts.py
import io
import soundfile as sf
import numpy as np
from kittentts import KittenTTS

_model: KittenTTS | None = None

def get_model() -> KittenTTS:
    global _model
    if _model is None:
        _model = KittenTTS("KittenML/kitten-tts-mini-0.8")
    return _model

def synthesize_to_bytes(text: str, voice: str = "Jasper") -> bytes:
    """Return WAV bytes for the given text. Raises on empty text."""
    if not text.strip():
        raise ValueError("Cannot synthesize empty text")
    audio: np.ndarray = get_model().generate(text, voice=voice)
    buffer = io.BytesIO()
    sf.write(buffer, audio, samplerate=24000, format="WAV")
    return buffer.getvalue()
```

---

## Data Flow

### Primary Flow: Voice Input to Agent Execution to Voice Response

```
[Coordinator speaks or types]
         │
         ▼
[Voice Panel: st.audio_input or streamlit-mic-recorder]
         │ raw audio bytes (WAV, 16kHz)
         ▼
[voice/stt.py: faster-whisper transcribe()]
         │ text transcript
         ▼
[coordinator/intent.py: parse intent via Gemini]
         │ intent + entities (e.g. {action: "discover_events", university: "Cal Poly"})
         ▼
[coordinator/proposal.py: build AgentAction list]
         │ list of AgentAction (status=PENDING)
         ▼
[runtime_state: append to st.session_state["pending_actions"]]
         │
         ▼
[Command Center Tab: renders pending actions with Approve/Reject buttons]
         │ coordinator clicks Approve
         ▼
[coordinator/approval.py: set status=APPROVED, push to _dispatch_queue]
         │
         ▼
[agents/result_bus.py background thread: NemoClaw orchestrator executes]
         │ dispatches to sub-agent tools in parallel
         ▼
[agents/tools/*.py: call existing src/ services]
         │ results placed on _result_queue
         ▼
[@st.fragment poll: drain result queue, update action status=DONE, store results]
         │
         ▼
[coordinator/response.py: synthesize natural language summary of results]
         │ response text
         ▼
[voice/tts.py: KittenTTS synthesize_to_bytes()]
         │ WAV bytes
         ▼
[Voice Panel: st.audio(wav_bytes, autoplay=True)]
         │
         ▼
[Coordinator hears the result summary]
```

### State Management

```
st.session_state (per browser session)
    │
    ├── "pending_actions"      list[AgentAction]  — proposal queue
    ├── "action_history"       list[AgentAction]  — completed/rejected actions
    ├── "voice_transcript"     str                — last STT transcript
    ├── "coordinator_reply"    str                — last TTS text
    ├── "agent_worker_started" bool               — daemon thread lifecycle guard
    │
    └── [existing keys unchanged]
        ├── "match_results_df"
        ├── "matching_discovered_events"
        ├── "scraped_events"
        └── "emails_generated"
```

### Key Data Flows

1. **Voice → Action Proposal:** Audio bytes enter `voice/stt.py` (faster-whisper), transcript enters `coordinator/intent.py` (Gemini), intent becomes `AgentAction` objects in session state. All synchronous in the Streamlit script thread.

2. **Approval → Execution:** Coordinator clicks Approve in Command Center. `coordinator/approval.py` validates and pushes to `_dispatch_queue`. Background worker picks up, calls NemoClaw lead agent, which dispatches to MCP tool sub-agents in parallel. Results flow back via `_result_queue`.

3. **Results → Voice Response:** `@st.fragment` poll drains result queue every 2 seconds. On completion, `coordinator/response.py` builds a natural language summary, `voice/tts.py` generates WAV, `st.audio` plays it in the browser.

4. **Agent Results → Existing State:** Matcher sub-agent results are written to `st.session_state["match_results_df"]` via existing `runtime_state.set_match_results()`. Scraper results go to `st.session_state["scraped_events"]`. Existing tabs consume these unchanged — zero modifications to existing tab rendering logic.

---

## Integration Points

### External Services

| Service | Integration Pattern | Confidence | Notes |
|---------|---------------------|------------|-------|
| KittenTTS | `pip install kittentts` → Python function call → numpy array → soundfile WAV | HIGH | Pure Python, ONNX runtime, CPU-only, 25MB model. Model loads once at startup via module-level singleton. |
| faster-whisper | `pip install faster-whisper` → `WhisperModel("base").transcribe(audio_file)` | HIGH | Tiny/base models work on CPU. 16kHz input from `st.audio_input`. Write audio bytes to temp file first. |
| NemoClaw | `pip install nemoclaw` → `nemoclaw.Agent(tools=[...])` → MCP tool dispatch | LOW | Alpha as of March 2026. APIs subject to breaking change. Fallback: implement as a direct function router if NemoClaw proves too unstable for hackathon. |
| st.audio_input | Native Streamlit widget (v1.42+) → returns `UploadedFile` with `.getvalue()` bytes | HIGH | Returns WAV at 16kHz. Available in Streamlit 1.42.2 (current in requirements.txt). |
| streamlit-mic-recorder | Third-party component → returns dict with `"bytes"` key | MEDIUM | More control than st.audio_input (push-to-talk vs click-stop). Better for demo UX. |

### Internal Boundaries

| Boundary | Communication | Constraint |
|----------|---------------|------------|
| voice/ ↔ coordinator/ | Plain Python function call: `stt.transcribe(bytes) -> str` | voice/ must have zero Streamlit imports |
| coordinator/ ↔ agents/ | Session state queue + thread-safe `queue.Queue` | coordinator/ writes, agents/ reads; never reversed |
| agents/tools/ ↔ src/ | Direct Python imports: `from src.matching.engine import rank_speakers_for_event` | Tools are thin wrappers, no business logic duplication |
| agents/result_bus.py ↔ ui/ | `st.session_state` read by `@st.fragment` poll in `ui/command_center.py` | Only the poll fragment reads results; no other UI component reads the queue directly |
| ui/command_center.py ↔ runtime_state.py | Call `runtime_state.set_match_results()` to commit matched results from agent | Preserves existing cross-tab contract unchanged |
| poc/ ↔ agents/tools/poc_tool.py | MCP tool imports `poc/store.py` directly | POC store uses immutable update pattern (never mutate CSV in place) |

---

## New vs Existing Components

| Component | Status | Touches Existing Code? |
|-----------|--------|------------------------|
| `voice/bridge.py`, `voice/stt.py`, `voice/tts.py` | NET NEW | No |
| `coordinator/intent.py`, `proposal.py`, `approval.py`, `response.py` | NET NEW | No |
| `agents/orchestrator.py`, `agents/result_bus.py` | NET NEW | No |
| `agents/tools/scraper_tool.py` | NET NEW | Imports `src/scraping/scraper.py` (no modification) |
| `agents/tools/matcher_tool.py` | NET NEW | Imports `src/matching/engine.py` (no modification) |
| `agents/tools/outreach_tool.py` | NET NEW | Imports `src/outreach/email_gen.py` (no modification) |
| `agents/tools/poc_tool.py` | NET NEW | No |
| `poc/store.py`, `poc/history.py` | NET NEW | No |
| `ui/command_center.py` | NET NEW | No |
| `ui/voice_panel.py` | NET NEW | No |
| `src/app.py` | MODIFIED | Add two tab imports + init voice panel |
| `src/config.py` | MODIFIED | Add `KITTENTTS_VOICE`, `NEMO_CLAW_MODEL`, `WHISPER_MODEL_SIZE` constants |
| `src/runtime_state.py` | MODIFIED | Extend `init_runtime_state()` with `pending_actions`, `action_history`, `voice_transcript` keys |
| All other `src/` modules | UNCHANGED | None |

---

## Suggested Build Order

Build order is driven by three constraints: (1) existing service layer must not be modified until wrappers are ready, (2) the approval gate must exist before any agent execution, and (3) each phase must be independently demonstrable.

### Phase 1: Voice I/O Foundation (no agent, no NemoClaw)

Build `voice/` subsystem + `ui/voice_panel.py` in isolation. Verify: coordinator speaks → STT transcript appears → Jarvis replies with synthesized voice (hardcoded reply). KittenTTS and faster-whisper are validated here before any agent complexity is added.

**Deliverables:** `voice/stt.py`, `voice/tts.py`, `voice/bridge.py`, `ui/voice_panel.py`
**Risk:** KittenTTS model download (~25MB) must work in demo environment. Validate early.

### Phase 2: Coordinator + Approval Gate (no NemoClaw yet)

Build `coordinator/` and extend `runtime_state.py` + `ui/command_center.py`. Intent parsing uses Gemini (already integrated). Approval state machine is fully wired. Agent dispatch is stubbed — approved actions log to console but don't execute. Verify: full voice → intent → proposal → approve/reject cycle works without any real agent.

**Deliverables:** `coordinator/intent.py`, `coordinator/proposal.py`, `coordinator/approval.py`, `coordinator/response.py`, `ui/command_center.py`, extended `runtime_state.py`
**Dependency:** Phase 1 complete (voice bridge needed for voice input path).

### Phase 3: Agent Tool Wrappers (no NemoClaw orchestrator yet)

Build `agents/tools/*.py` as standalone MCP tools. Each tool is tested by calling it directly with known inputs and verifying it produces correct output via the underlying `src/` service. Build `agents/result_bus.py` background thread. Wire approved actions from Phase 2 to the result bus. NemoClaw orchestrator is still stubbed — approved actions call tools directly in sequence.

**Deliverables:** `agents/tools/scraper_tool.py`, `agents/tools/matcher_tool.py`, `agents/tools/outreach_tool.py`, `agents/result_bus.py`, `poc/store.py`, `poc/history.py`, `agents/tools/poc_tool.py`
**Dependency:** Phase 2 complete (approval gate needed to dispatch actions).

### Phase 4: NemoClaw Lead Agent + Command Center Dashboard

Wire `agents/orchestrator.py` to replace the direct tool calls from Phase 3. NemoClaw lead agent receives approved actions, decomposes and dispatches sub-agents in parallel. Command Center tab shows live status per sub-agent (PENDING → EXECUTING → DONE/FAILED). Voice response is synthesized from aggregated results.

**Deliverables:** `agents/orchestrator.py`, full `ui/command_center.py` with real-time status, end-to-end voice → approve → parallel agents → voice response demo.
**Dependency:** Phase 3 complete. NemoClaw alpha stability — if NemoClaw proves unusable before demo, the Phase 3 direct-dispatch fallback is demo-ready as a contingency.

---

## Streamlit Audio/Voice Constraints

These are specific constraints that affect implementation choices:

1. **`st.audio_input` vs `streamlit-mic-recorder`:** Both work in Streamlit 1.42.2. `st.audio_input` is native and simpler; `streamlit-mic-recorder` offers push-to-talk UX which is better for demo purposes. The choice does not affect downstream architecture.

2. **No audio streaming from KittenTTS:** KittenTTS has no streaming API. Generate the full phrase, encode to WAV, play via `st.audio()`. Keep TTS phrases short (<50 words) to avoid noticeable latency.

3. **Background thread session state access:** The background agent worker thread must have Streamlit's `ScriptRunContext` attached via `add_script_run_ctx` before calling any `st.*` API. Alternatively, write results only to `queue.Queue` and let the main thread's `@st.fragment` poll commit to session state — this is the safer pattern.

4. **`@st.fragment` polling:** Use `@st.fragment(run_every=2)` on the Command Center status section to poll `_result_queue` and refresh agent status. Fragment-scoped reruns avoid full page rerender on every poll cycle.

5. **WebSocket reconnect risk:** If the coordinator's browser tab reconnects (network interruption), `st.session_state` is reset. The `pending_actions` queue and `action_history` should be persisted to a session file in `cache/` keyed by a session UUID stored in a browser cookie. This is a demo mitigation, not a production solution.

---

## Anti-Patterns

### Anti-Pattern 1: Business Logic Inside Agent Tool Wrappers

**What people do:** Copy-paste matching or scraping logic into `agents/tools/matcher_tool.py` instead of calling the existing service.

**Why it's wrong:** Creates two codebases to maintain. Breaks the 392 existing tests (they cover the original modules, not the copies). Drift between tool behavior and tested behavior causes demo failures.

**Do this instead:** Tool wrappers are 10-30 lines. They call `src/matching/engine.rank_speakers_for_event()` directly. All logic stays in tested modules.

### Anti-Pattern 2: Executing Agent Actions Before Approval

**What people do:** Dispatch NemoClaw immediately on intent parse, then notify the coordinator after the fact.

**Why it's wrong:** Violates the hard constraint in PROJECT.md: "all agent actions require coordinator sign-off." Autonomous execution without approval is explicitly out of scope.

**Do this instead:** Intent → `AgentAction(status=PENDING)` in session state → coordinator sees it in Command Center → clicks Approve → then and only then dispatch to `_dispatch_queue`.

### Anti-Pattern 3: Blocking the Streamlit Script Thread on Agent Execution

**What people do:** Call `nemoclaw_orchestrator.run(action)` synchronously inside a Streamlit button click handler.

**Why it's wrong:** Streamlit's script thread blocks for the duration. Any UI interaction during execution triggers a rerun that cancels the in-progress call. Scraping + LLM calls can take 10-30 seconds.

**Do this instead:** Push to `_dispatch_queue` immediately (returns in microseconds), let the daemon thread run the agent, use `@st.fragment` poll to collect results.

### Anti-Pattern 4: Importing Streamlit Inside voice/ or coordinator/ Modules

**What people do:** Call `st.session_state` or `st.error()` inside `voice/stt.py` to report errors.

**Why it's wrong:** Makes voice/ and coordinator/ untestable without a running Streamlit context. Breaks the separation needed to unit-test STT/TTS without spinning up a full app.

**Do this instead:** voice/ and coordinator/ return results and raise exceptions. The UI layer (`ui/voice_panel.py`, `ui/command_center.py`) translates those into Streamlit calls.

---

## Scaling Considerations

This is a demo-focused hackathon app. Scaling is not a primary concern, but one practical constraint matters:

| Concern | Demo (1 coordinator) | Notes |
|---------|----------------------|-------|
| KittenTTS model load time | ~2-3 seconds on first call | Initialize at app startup, not on button click |
| faster-whisper cold start | ~1-2 seconds for base model | Same — initialize at startup |
| NemoClaw parallel agents | Demo: 2-4 parallel tools | Sequential fallback acceptable if NemoClaw alpha is unstable |
| `st.session_state` size | Low risk for single session | Action history should cap at 50 entries to avoid bloat |

---

## Sources

- [KittenTTS GitHub — KittenML/KittenTTS](https://github.com/KittenML/KittenTTS)
- [KittenTTS PyPI](https://pypi.org/project/kittentts/)
- [Kitten TTS Tutorial — byteiota.com](https://byteiota.com/kitten-tts-tutorial-cpu-text-to-speech-in-25mb/)
- [NVIDIA NemoClaw Developer Guide — Overview](https://docs.nvidia.com/nemoclaw/latest/about/overview.html)
- [NVIDIA NemoClaw — How It Works](https://docs.nvidia.com/nemoclaw/latest/about/how-it-works.html)
- [NemoClaw GitHub — NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw)
- [NemoClaw at build.nvidia.com](https://build.nvidia.com/nemoclaw)
- [Streamlit st.audio_input docs](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input)
- [Streamlit st.fragment docs](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
- [Streamlit threading docs](https://docs.streamlit.io/develop/concepts/design/multithreading)
- [faster-whisper GitHub — SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [MCP Python SDK — modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- [NemoClaw MCP integration analysis — techbytes.app](https://techbytes.app/posts/nvidia-nemoclaw-open-source-agentic-os-analysis-2026/)

---

*Architecture research for: Voice + Agent Orchestration layer on Streamlit SmartMatch CRM*
*Researched: 2026-03-23*
