# Pitfalls Research

**Domain:** Voice AI + Agent Orchestration added to existing Streamlit CRM
**Researched:** 2026-03-23
**Confidence:** MEDIUM — NemoClaw is alpha (March 16, 2026 launch), KittenTTS is TTS-only (not duplex), Streamlit threading issues are HIGH confidence from documented issues.

---

## Critical Pitfalls

### Pitfall 1: KittenTTS Is TTS-Only — "Full Duplex" Requires a Separate STT Layer

**What goes wrong:**
The PROJECT.md describes "full-duplex voice + text interaction via KittenTTS." KittenTTS is a 15M-parameter, 25MB text-to-speech synthesis model. It does NOT provide speech-to-text or full-duplex coordination. Building voice input using KittenTTS as the complete voice stack produces an app that can speak but cannot hear. The demo breaks the moment a coordinator tries to use voice input.

**Why it happens:**
The project spec conflates "voice interface" with a single library. KittenTTS handles the output (agent speech) side only. The input (coordinator speech) side requires a separate STT library — Whisper, faster-whisper, Deepgram, or browser Web Speech API. This distinction is easy to miss during planning.

**How to avoid:**
Split the voice pipeline into two discrete components from the start:
- STT component: browser Web Speech API (zero-install for demo) or faster-whisper (local, offline)
- TTS component: KittenTTS for agent voice output
Wire them through a common `VoiceIO` abstraction so they can be swapped independently. Do not assume KittenTTS covers both sides.

**Warning signs:**
- Any plan that only mentions KittenTTS for voice I/O without naming an STT provider
- Sprint tasks that say "integrate KittenTTS for voice" without separate STT tasks
- The word "duplex" applied only to KittenTTS in design docs

**Phase to address:**
Voice integration phase (first phase that touches voice I/O) — before any UI is built around voice. Architectural decision must be made at phase entry.

---

### Pitfall 2: NemoClaw Is Alpha Software With NVIDIA-Only Model Support

**What goes wrong:**
NemoClaw was announced at GTC 2026 and entered early preview on March 16, 2026 — one week before this milestone started. APIs, configuration schemas, and runtime behavior are explicitly documented as subject to breaking changes between releases. The platform does not support OpenAI, Anthropic, or any non-NVIDIA model in its initial release — only NVIDIA Nemotron and locally hosted NIM containers. The existing SmartMatch app uses Gemini (Google) as its LLM backend. Connecting NemoClaw sub-agents to Gemini is not a supported configuration at launch.

**Why it happens:**
Project specs reference "Nvidia NemoClaw for sub-agent orchestration" without accounting for its first-week alpha status or its current model lock-in. The build.nvidia.com landing page markets capabilities planned for future releases, not what is available today.

**How to avoid:**
Two paths:
1. **Accept the constraint**: Use NemoClaw with Nemotron models for sub-agents, keeping Gemini only for existing SmartMatch matching logic. Treat them as parallel LLM backends with different roles.
2. **Use NemoClaw as architecture reference only**: Implement the sub-agent orchestration pattern that NemoClaw defines (blueprint-based, sandboxed, policy-controlled) using a framework that supports Gemini today (LangGraph, CrewAI, or a simple asyncio task manager).

For a hackathon demo, option 2 is lower risk. If NemoClaw integration is a judging criterion, use option 1 with explicit scoping to Nemotron models only.

**Warning signs:**
- Any code that tries to pass a Gemini API key to NemoClaw's inference configuration
- Sub-agent tasks designed around OpenAI-compatible endpoints without verifying NemoClaw support
- Installing NemoClaw and immediately writing agent logic without reading the release notes

**Phase to address:**
Architecture / technology selection phase. Decide before writing a single line of agent code whether NemoClaw is used directly or as a pattern reference.

---

### Pitfall 3: Streamlit's Rerun Model Kills Long-Running Agent Tasks

**What goes wrong:**
Streamlit reruns the entire Python script from top to bottom on every user interaction — button click, slider move, text input. When a sub-agent task is running (scraping a university site, generating an outreach email, doing speaker matching), any user interaction immediately terminates the running script and starts a new rerun. Agent execution assumes it will not be interrupted mid-task. This causes silent task abandonment, orphaned state, and a demo that appears frozen or randomly resets.

**Why it happens:**
Developers port synchronous agent logic directly into Streamlit callbacks without accounting for Streamlit's execution model. The existing SmartMatch app avoids this because its heaviest operations (scraping, matching) are triggered by explicit buttons and complete within a single script run. Adding agents that run for 10-30 seconds breaks this assumption.

**How to avoid:**
Run agent tasks in background threads using `threading.Thread` or `concurrent.futures.ThreadPoolExecutor`. Write results back to `st.session_state` using a thread-safe write pattern (acquire lock, write, release). Use `st.rerun()` only after confirming the background task is complete or at timed intervals via `st.fragment` with `run_every`. Never block the main script thread waiting for agent output.

```python
# Pattern: background agent task
import threading
import streamlit as st

_lock = threading.Lock()

def _run_agent_task(task_id: str, payload: dict) -> None:
    result = run_nemoclaw_agent(payload)  # long-running
    with _lock:
        st.session_state[f"agent_result_{task_id}"] = result
        st.session_state["agent_pending"] = False
```

**Warning signs:**
- Agent calls made directly inside `st.button` callback bodies without threading
- `time.sleep()` calls inside main Streamlit script flow
- "Awaiting agent..." spinners that freeze the entire UI
- Tests that pass individually but fail when UI interactions are interleaved

**Phase to address:**
Agent orchestration phase — establish the threading pattern as the first task before implementing any individual agent.

---

### Pitfall 4: Session State Corruption from Concurrent Agent Writes

**What goes wrong:**
When multiple NemoClaw sub-agents (webscraping, matching, outreach) run in parallel and all write to `st.session_state`, they race on shared keys. Streamlit's session state is not thread-safe by default. The existing `init_runtime_state()` function initializes keys like `match_results_df`, `scraped_events`, and `generated_email_keys` — all of which parallel agents will need to update. Without locking, two agents can read-modify-write the same key simultaneously, producing corrupted DataFrames, duplicate emails, or lost results.

**Why it happens:**
`st.session_state` looks like a plain dict and developers treat it as one. The existing codebase uses it safely because all mutations happen on the main script thread. Parallel background threads break that assumption silently — no exception is raised, data just becomes wrong.

**How to avoid:**
- Use a module-level `threading.Lock()` for all session state writes from background threads.
- Alternatively, use Python `queue.Queue` to funnel all agent results back to the main thread, which then writes to session state during a rerun.
- The `streamlit-server-state` library provides thread-safe server-side state, but adds a dependency.
- Isolate each agent's output namespace: agent writes to `session_state["agent_scrape_result"]` not directly into `session_state["scraped_events"]`. The main thread merges on rerun.

**Warning signs:**
- `match_results_df` has duplicate rows after parallel agent runs
- `generated_email_keys` grows incorrectly (missing or repeated entries)
- Results differ between runs for identical inputs
- Tests pass in isolation but fail when run concurrently

**Phase to address:**
Agent orchestration phase — enforce the write isolation pattern before wiring agents to existing session state keys.

---

### Pitfall 5: Human-in-the-Loop Approval Blocks the Script Thread

**What goes wrong:**
The hard architectural constraint is "no agent action executes without coordinator approval." A naive implementation waits for user approval by polling: `while not st.session_state["approved"]: time.sleep(0.5)`. This blocks the Streamlit script thread entirely, freezing the UI and preventing any rerender. Users see a hung app. On a demo day, this reads as a crash.

**Why it happens:**
Approval workflows from non-Streamlit frameworks (LangGraph, OpenAI Agents SDK) use synchronous `await` or callback patterns that assume an async event loop. In Streamlit, there is no such loop available to the script — Streamlit controls the execution model.

**How to avoid:**
Model approval as a state machine in session state, not as a blocking wait:
1. Agent completes planning, writes proposal to `session_state["pending_action"]` and sets `session_state["awaiting_approval"] = True`.
2. Script rerun renders the approval UI (proposal text, Approve/Reject buttons) only when `awaiting_approval` is True.
3. On Approve click, set `session_state["approved_action"] = pending_action`, clear `awaiting_approval`, and trigger agent execution in a background thread.
4. Use `st.stop()` after rendering the approval UI to prevent the rest of the script from proceeding until approval is given.

This pattern is documented in LangGraph + Streamlit integration guides and avoids any blocking.

**Warning signs:**
- Any `while True` or `time.sleep()` waiting for a session state flag
- Async `await` calls in Streamlit callbacks without `asyncio.run()` wrapper
- Approval UI that disappears on page interaction before the user has responded

**Phase to address:**
Human-in-the-loop phase — the approval state machine is the first thing to build and test in isolation before attaching agent logic to it.

---

### Pitfall 6: Browser Microphone Requires HTTPS — Demo Breaks on HTTP Localhost

**What goes wrong:**
Browser microphone access (required for voice input) is blocked on non-HTTPS origins except `localhost`. A demo served over HTTP on a local network (e.g., `http://192.168.1.x:8501` projected on a screen) will silently deny microphone permission. The voice input UI renders but produces no audio. The coordinator clicks the mic button and nothing happens.

**Why it happens:**
Developers test on `http://localhost:8501` where microphone access works. They miss that sharing the demo via IP address or a non-localhost URL requires HTTPS. Hackathon demos are often run from a laptop projected directly, but sometimes shared via a local network URL.

**How to avoid:**
- For demo day: always run the demo on the presenter's own machine using `localhost`, not a shared network URL.
- If network sharing is required: use `ngrok` or a self-signed TLS certificate with Streamlit's `--server.sslCertFile` and `--server.sslKeyFile` options.
- Add a preflight check to `scripts/sprint4_preflight.py` (the existing preflight script) that verifies the audio component can initialize.

**Warning signs:**
- Demo rehearsed exclusively on `localhost` without testing the actual presentation setup
- No HTTPS configuration in demo runbook
- `streamlit-audio-recorder` component rendering but `st.session_state["audio"]` always None

**Phase to address:**
Demo integration / hardening phase — add to the demo runbook and preflight checklist.

---

### Pitfall 7: Wrapping Existing SmartMatch Functions as Agent-Callable Services Breaks the 392-Test Baseline

**What goes wrong:**
The existing app has 392 passing tests across matching, discovery, outreach, and pipeline. When existing functions (e.g., `render_matches_tab`, scraping pipeline, outreach generators) are refactored to be callable by agents, their signatures change. Tests that mock the old signatures at import time break without being changed themselves. The test count drops and the demo readiness preflight fails, signaling a regression that took working features backward.

**Why it happens:**
Agent-callable wrappers are added as thin adapters, but developers also change the underlying function signatures "while they're in there." Tests that patch `src.matching.engine.rank_speakers` by exact signature no longer work if the function gains an `agent_context: AgentContext | None = None` parameter. Mock objects stop matching.

**How to avoid:**
- Add agent-callable adapters as new functions that call the existing functions, not by modifying existing function signatures. Keep the originals intact.
- Run `pytest tests/ -x` after every adapter addition before continuing.
- Use the adapter pattern: `def agent_rank_speakers(payload: dict) -> dict: return {"results": rank_speakers(...)}`. The inner `rank_speakers` is unchanged.
- Mark new adapter tests with `@pytest.mark.agent` so they can be run separately during development.

**Warning signs:**
- Test count drops below 392 during agent integration work
- `ImportError` or `TypeError` in existing tests after adding agent adapters
- `conftest.py` fixtures being changed to accommodate new function signatures

**Phase to address:**
Agent service wrapping phase — establish the no-modification-of-existing-signatures rule before any wrapping begins.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Calling NemoClaw API directly in Streamlit callback (no abstraction layer) | Faster to wire up | Every NemoClaw breaking change requires touching UI code; alpha API will change | Never — always wrap in a service class |
| Storing full agent conversation history in `st.session_state` | Simple, no external state | Memory grows unbounded per session; large DataFrames in session state slow reruns significantly | Never for production; acceptable for hackathon demo if capped at N messages |
| Using browser Web Speech API for STT without fallback | Zero dependencies | Fails silently in Firefox, requires HTTPS, no offline mode | Only if demo is Chrome-only and HTTPS is confirmed |
| Polling `st.session_state["agent_done"]` in a tight loop | Simpler than thread-safe callbacks | Blocks main thread, hangs UI | Never |
| Skipping approval state machine, using `st.experimental_dialog` modal as approval gate | Visually cleaner, faster to build | Modal dismisses on page interaction, approval state lost; violates the HITL hard constraint | Never — approval state must survive reruns |
| Hard-coding NemoClaw blueprint version | Avoids version detection code | Alpha SDK changes blueprint schema between releases; app silently executes wrong blueprint | Never during alpha period |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| KittenTTS | Calling `synthesize()` on the main thread for every agent response — blocks UI for 1-3s per utterance | Run synthesis in a background thread; cache audio for repeated phrases (e.g., "Awaiting your approval") |
| KittenTTS | Expecting KittenTTS to handle STT — it is TTS-only | Use separate STT: browser Web Speech API for demo simplicity, or faster-whisper for offline reliability |
| NemoClaw | Passing Gemini API credentials to NemoClaw inference config — not supported in alpha | Use NemoClaw with Nemotron models only; keep Gemini for existing matching logic; wire through a model-router abstraction |
| NemoClaw | Treating NemoClaw blueprint schema as stable — it changes between alpha releases | Pin the exact NemoClaw version in `requirements.txt`; test after any update; keep a fallback asyncio-based orchestrator |
| NemoClaw | Running NemoClaw inside a Streamlit script thread — subprocess/sandbox model conflicts with Streamlit's execution model | Invoke NemoClaw as a subprocess or via its Python client from a background thread only |
| streamlit-webrtc | Using streamlit-webrtc without a TURN server in non-localhost environments | Configure Twilio Network Traversal Service or equivalent TURN server; test on the demo network before demo day |
| Existing Gemini client | Adding agent context to `gemini_client.py` calls and forgetting that Gemini has per-request rate limits | Implement exponential backoff in the agent layer; do not let sub-agents hammer Gemini in parallel without rate limiting |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Storing scraped HTML in `st.session_state["scraped_events"]` list — grows unbounded | Page rerenders slow from <100ms to >2s; browser tab memory climbs | Cap list at 50 items; store only structured extracted data, not raw HTML | After ~20 scrape operations in one session |
| Running speaker embedding generation inside agent task (re-generates on every agent call) | Each agent match call takes 30-60s; demo appears frozen | Cache embeddings at session init (already done in `init_runtime_state`); pass embedding dict as agent input, not raw speaker data | First agent match call in any session |
| KittenTTS loading the model on every synthesis call | First voice response takes 3-5s; subsequent calls also slow | Load KittenTTS model once at app startup into `st.session_state["tts_model"]`; call `synthesize()` on the cached model | Every single TTS call if not cached |
| Parallel NemoClaw sub-agents each making independent Gemini API calls | Rate limit 429 errors; some agents succeed, others fail silently | Route all LLM calls through a shared rate-limited client with a semaphore; log failures explicitly | 3+ parallel agents calling Gemini simultaneously |
| `st.rerun()` called in a polling loop to check agent status | Infinite rerun loop; app becomes unresponsive | Use `st.fragment(run_every=2)` for status polling; or use a websocket/SSE channel for push updates | Immediately — polling loops in Streamlit always create rerun storms |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Agent webscraping targets user-provided URLs without validation | Server-side request forgery (SSRF); agent scrapes internal network resources or credential endpoints | Allowlist university domains; validate URLs against `data_cpp_events_contacts.csv` approved domains before agent dispatch |
| Storing NemoClaw API credentials in `st.session_state` | Credentials visible in Streamlit's state serialization; leaked in browser dev tools | Store credentials only in environment variables loaded at startup via `os.environ`; never write API keys to session state |
| Agent-generated outreach emails sent without human review | Coordinator's name used for unauthorized communication; reputational damage | Enforce the HITL approval gate for ALL outreach actions; disable send capability entirely in demo mode (use existing `demo_mode.py` guard) |
| LLM prompt injection via scraped event content | Malicious content on a scraped page hijacks agent instructions | Sanitize scraped content before including in agent prompts; use a separate extraction step that strips HTML and limits field length |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing raw agent JSON output in the "command center" dashboard | Coordinator sees `{"status": "pending", "task_id": "abc"}` and has no idea what is happening | Translate all agent state to human language: "Searching university events... (3 of 5 agents active)" |
| Approval buttons disappear when the page rerenders mid-approval | Coordinator clicks Approve; button vanishes before click registers; action never executes | Render approval UI inside an `st.fragment` with a stable key; use `st.session_state` to persist approval state across reruns |
| Voice output (TTS) plays while coordinator is still speaking | Coordinator's mic picks up TTS audio; creates feedback loop or double-transcription | Mute STT while TTS is playing; use a `tts_speaking` flag in session state to gate microphone processing |
| No visual distinction between "agent thinking," "awaiting approval," and "agent complete" states | Coordinator cannot tell if app is working or frozen; may interrupt agent mid-task | Three distinct visual states with different spinners/colors: yellow for running, orange for needs approval, green for complete |
| Approval workflow requires coordinator to scroll to find the approval buttons | Coordinator misses pending approvals; agents time out or pile up | Render pending approvals at the top of the command center tab, above all other content, always |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Voice input:** KittenTTS integrated for TTS — verify a separate STT component exists and produces transcribed text in `session_state["voice_input"]`
- [ ] **NemoClaw orchestration:** Sub-agents dispatch successfully — verify they write results back to session state AND the main UI renders those results (not just logs to console)
- [ ] **Human-in-the-loop:** Approval buttons render — verify that clicking Approve actually triggers agent execution AND that Reject cancels the pending action cleanly
- [ ] **Command center dashboard:** Agent status widgets render — verify they update in real time without manual page refresh
- [ ] **Existing tests still pass:** New agent adapters added — verify `pytest tests/` still reports 392+ passed with no regressions
- [ ] **Demo mode guard:** Agent actions implemented — verify that `demo_mode.py` flags prevent any external writes (email sends, API calls with side effects) when `DEMO_MODE=true`
- [ ] **HTTPS / microphone:** Voice UI renders — verify microphone access works on the actual demo presentation setup (not just developer's localhost)
- [ ] **KittenTTS model loaded:** TTS synthesis called — verify model is cached in session state and is not reloaded on every synthesis call (check app startup log)
- [ ] **Thread safety:** Parallel agents dispatched — verify no `RuntimeError: Session state is not thread-safe` errors in Streamlit server logs during parallel agent runs

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| KittenTTS treated as duplex — no STT in place | MEDIUM | Add browser Web Speech API via `streamlit-js-eval` or a React custom component in one focused session; KittenTTS output side is unaffected |
| NemoClaw breaking change between alpha releases | MEDIUM | Pin NemoClaw version in requirements.txt; if already broken, swap NemoClaw invocation for a thin asyncio task manager that matches the same agent interface contract |
| Agent task killed by Streamlit rerun | LOW | Wrap agent call in background thread; existing session state keys already provide the write target; thread pattern is mechanical to add |
| Session state corruption from parallel writes | MEDIUM | Add module-level `threading.Lock` to all background-thread session state writes; replay the corrupted session by clearing state and rerunning |
| HTTPS/microphone blocked on demo day | LOW (if caught early) / HIGH (on demo day) | Serve via `localhost` on presenter machine; if IP sharing needed, run `ngrok http 8501` to get HTTPS tunnel in under 2 minutes |
| 392-test baseline broken by agent wrapping | MEDIUM | Revert signature changes to existing functions; add adapters as new functions only; re-run `pytest tests/ -x` to find first failure |
| Human-in-the-loop approval blocking main thread | LOW | Replace blocking loop with state-machine pattern; two-hour refactor if approval UI was built correctly as separate components |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| KittenTTS is TTS-only, not duplex | Phase 1: Voice architecture decision | Unit test that produces transcribed text from audio input via the STT component |
| NemoClaw alpha model lock-in | Phase 1: Technology selection and scoping | Integration test that dispatches one NemoClaw sub-agent and receives a structured result |
| Streamlit rerun kills agent tasks | Phase 2: Agent orchestration threading foundation | Load test: trigger a 10s agent task, click a UI button at 5s, verify agent result still appears |
| Session state corruption from parallel writes | Phase 2: Agent orchestration threading foundation | Concurrent test: dispatch 3 agents simultaneously, verify all 3 results appear without corruption |
| HITL approval blocks main thread | Phase 3: Human-in-the-loop approval workflow | Manual test: dispatch agent, wait for approval UI, reload page, verify approval UI persists |
| Browser microphone requires HTTPS | Phase 4: Demo hardening and preflight | Add to preflight script; test on demo presentation hardware before demo day |
| Agent wrapping breaks 392-test baseline | Phase 2: Agent service wrapping | `pytest tests/` must pass at 392+ after every adapter addition — gated in CI |
| KittenTTS model reload on every call | Phase 1: Voice architecture decision | Profile: measure synthesis latency; verify it is <500ms after first call |
| Agent output not surfaced in UI | Phase 3: Command center dashboard | Manual walkthrough: dispatch each agent type and verify result appears in UI without manual refresh |

---

## Sources

- [GitHub - KittenML/KittenTTS: State-of-the-art TTS model under 25MB](https://github.com/KittenML/KittenTTS) — TTS-only, no STT capability confirmed
- [KittenTTS on Hacker News](https://news.ycombinator.com/item?id=44807868) — Streaming API planned, not yet available; ~8.5s for 23-word prompt in early testing
- [NVIDIA NemoClaw Developer Guide - Overview](https://docs.nvidia.com/nemoclaw/latest/about/overview.html) — Alpha since March 16, 2026; breaking changes expected
- [NVIDIA NemoClaw Release Notes](https://docs.nvidia.com/nemoclaw/latest/about/release-notes.html) — "Do not use in production"
- [NemoClaw on build.nvidia.com](https://build.nvidia.com/nemoclaw) — Official landing page
- [NemoClaw on DEV Community](https://dev.to/arhtechpro/nemoclaw-nvidias-open-source-stack-for-running-ai-agents-you-can-actually-trust-50gl) — NVIDIA-only model support confirmed in current alpha
- [Streamlit threading documentation](https://docs.streamlit.io/develop/concepts/design/multithreading) — ScriptRunContext requirement; NoSessionContext exception from background threads
- [Streamlit issue #6818: async session state fails on Cloud](https://github.com/streamlit/streamlit/issues/6818) — fastReruns interaction with async code
- [Streamlit issue #11679: concurrent callback data loss](https://github.com/streamlit/streamlit/issues/11679) — on_change callbacks race condition
- [Streamlit issue #12076: event loop closed with st.stream_write and LangGraph](https://github.com/streamlit/streamlit/issues/12076) — async generator + LangGraph interaction
- [Streamlit discussion: microphone access when deployed](https://discuss.streamlit.io/t/enabling-microphone-access-when-deployed/16776) — HTTPS requirement for non-localhost mic access
- [Streamlit discussion: implementing HITL to decide whether to continue](https://discuss.streamlit.io/t/implementing-human-in-the-loop-to-decide-whether-to-continue/113911) — st.stop() pattern for approval gates
- [MarkTechPost: Human-in-the-Loop with LangGraph and Streamlit](https://www.marktechpost.com/2026/02/16/how-to-build-human-in-the-loop-plan-and-execute-ai-agents-with-explicit-user-approval-using-langgraph-and-streamlit/) — State-machine approval pattern
- [GitHub - whitphx/streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc) — TURN server required for non-localhost WebRTC
- [Real-Time vs Turn-Based Voice Agent Architecture (Softcery)](https://softcery.com/lab/ai-voice-agents-real-time-vs-turn-based-tts-stt-architecture) — 800ms turn-taking threshold; STT+NLP+TTS pipeline latency expectations
- [Scaling Autonomous AI Agents with NVIDIA DGX Spark](https://developer.nvidia.com/blog/scaling-autonomous-ai-agents-and-workloads-with-nvidia-dgx-spark/) — NemoClaw parallel sub-agent scaling via TensorRT LLM / vLLM

---
*Pitfalls research for: Voice AI + NemoClaw agent orchestration added to existing Streamlit CRM*
*Researched: 2026-03-23*
