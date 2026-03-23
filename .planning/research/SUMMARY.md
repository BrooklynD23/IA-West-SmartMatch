# Project Research Summary

**Project:** IA West Smart Match CRM — v2.0 Jarvis Voice + Agent Orchestration Layer
**Domain:** Voice-driven AI coordinator with human-in-the-loop sub-agent orchestration on existing Streamlit CRM
**Researched:** 2026-03-23
**Confidence:** MEDIUM — KittenTTS well-documented; NemoClaw is seven-day-old alpha; Streamlit threading patterns are HIGH confidence from official sources

## Executive Summary

This project adds a "Jarvis-style" voice coordination layer and multi-agent orchestration to an existing Streamlit CRM (SmartMatch) without replacing or modifying its production business logic. The existing app already delivers event discovery, six-factor speaker ranking, and outreach generation backed by 392 passing tests. The v2.0 milestone wraps those services as NemoClaw/OpenClaw sub-agent tool callables and adds three new layers: a voice I/O pipeline (KittenTTS for TTS output, faster-whisper for STT input), a Jarvis coordinator that parses intent and manages approval state, and a Command Center tab with a live multi-agent status dashboard. The defining architectural constraint — every agent action requires explicit coordinator approval before execution — is non-negotiable and must be designed in from day one as a session-state state machine, not bolted on after the fact.

The recommended build order is strictly sequential by dependency: voice I/O first (validates KittenTTS and faster-whisper before agent complexity is added), then the coordinator core and HITL approval gate (proves the approval workflow without any real agent execution), then existing service wrappers as OpenClaw tool callables (builds on the stable approval foundation without modifying tested function signatures), and finally the NemoClaw lead agent and live dashboard (highest-risk component goes last so a direct-dispatch fallback is always demo-ready). This ordering means the demo is always in a demoable state at the end of each phase even if the next phase encounters NemoClaw alpha instability.

The central risk is NemoClaw: it launched March 16, 2026 — one week before this milestone — is alpha-only, supports only NVIDIA Nemotron models (not Gemini, which SmartMatch already uses), and is explicitly documented as "do not use in production." The mitigation is to treat NemoClaw as Phase 4's target while building Phases 1-3 against an asyncio/direct-dispatch fallback contract that NemoClaw can replace when stable. The second major risk is KittenTTS being assumed to provide full-duplex voice — it is TTS-only; faster-whisper must be added as a distinct STT component or the voice input side does not exist.

## Key Findings

### Recommended Stack

The existing stack (Streamlit, pandas, Plotly, Gemini, requests/BeautifulSoup, pytest) is unchanged. Four new runtime dependencies and two supporting libraries cover the entire new capability surface. KittenTTS is installed from a GitHub wheel release (not PyPI) and handles only TTS output; faster-whisper handles STT input and bundles FFmpeg via PyAV so no system-level FFmpeg install is needed. streamlit-webrtc provides browser mic capture via WebRTC (native `st.audio_input` returns clips only and cannot drive real-time STT). The openclaw-sdk Python package is the programmatic interface to NemoClaw/OpenClaw from Python (NemoClaw itself is a TypeScript CLI runtime). All asynchronous bridging between Streamlit's script thread and background agents uses stdlib `threading.Queue` — `asyncio.Queue` is explicitly unsafe with Streamlit's session state model.

**Core technologies (new additions):**
- **kittentts 0.8.1** (GitHub wheel): TTS output — CPU-only ONNX, 25MB, 8 voices, 24kHz numpy output; English-only; install via wheel not PyPI
- **faster-whisper** (pip): STT input — 4x faster than openai-whisper, bundled FFmpeg, CPU-optimized; closes the duplex loop KittenTTS cannot
- **streamlit-webrtc 0.6.0**: Browser mic capture — WebRTC audio frame streaming; required for push-to-talk UX; needs HTTPS on non-localhost
- **openclaw-sdk 2026.3.20**: NemoClaw Python interface — agent dispatch, workspace management, task scheduling from Python; independently maintained (LOW confidence)
- **soundfile** (pip): KittenTTS numpy array → in-memory WAV buffer for `st.audio()` playback
- **threading / queue** (stdlib): Background agent ↔ Streamlit UI bridge — the only safe pattern for Streamlit + background threads

**Critical version constraints:**
- Python >=3.10 required by streamlit-webrtc; avoid Python 3.13 until KittenTTS ONNX wheel is tested there
- Streamlit >=1.37 required for `@st.fragment(run_every=...)` (stable, non-experimental)
- Pin openclaw-sdk version — alpha APIs change between releases

### Expected Features

**Must have (table stakes — P1):**
- Text command interface (`st.chat_input`) — voice fallback for brittle demo environments; feeds same intent parser as voice
- Voice TTS output (KittenTTS Hugo/Bruno voice) — defines the "Jarvis" persona; silence breaks the demo illusion
- Voice STT input via push-to-talk — coordinator speaks to Jarvis; push-to-talk is more demo-reliable than wake word
- HITL approval flow — proposed action cards (agent name, action, reasoning) with Approve/Reject/Edit buttons; this is the hard architectural constraint
- Existing SmartMatch tools wrapped as OpenClaw callables (discovery, matching, outreach) — NemoClaw has nothing to dispatch without these
- NemoClaw/OpenClaw sub-agent dispatch — the named NVIDIA orchestration layer; core differentiator
- Visual multi-agent Command Center dashboard — per-agent status cards (idle/running/awaiting approval/complete); the "wow factor"

**Should have (differentiators — P2, add after P1 stable):**
- POC contact management with history — contact log per speaker/event, surfaces overdue follow-ups as proactive suggestions
- Proactive Jarvis suggestions — Jarvis notices stale discovery or overdue outreach and volunteers actions (all still HITL-gated)
- Parallel agent dispatch with live status — simultaneous sub-agent execution with real-time progress; visual proof of multi-agent coordination

**Defer to v3+:**
- Always-on wake word activation — too brittle for hackathon demo environments; revisit post-hackathon
- Real-time streaming transcription — requires VAD + streaming Whisper; complexity vs. reliability trade-off favors push-to-talk for demo
- Multi-language TTS — KittenTTS is English-only; requires swapping TTS provider

**Anti-features to reject explicitly:**
- Fully autonomous agent execution without approval (violates hard constraint and removes demo's best interaction)
- Custom TTS voice training (explicitly out-of-scope per PROJECT.md)
- Production auth / multi-tenant (zero demo value, high complexity)

### Architecture Approach

The architecture is a strictly layered brownfield addition: all new code is isolated in `voice/`, `coordinator/`, `agents/`, `poc/`, and two new `ui/` files, while every existing `src/` module remains unmodified. The voice layer is Streamlit-free (pure functions: bytes in → text out for STT; text in → bytes out for TTS), making it independently testable. The coordinator layer manages intent parsing and the approval state machine in session state. The agent orchestration layer runs in background daemon threads bridged to the UI via `queue.Queue` + `@st.fragment(run_every=2)` polling — never blocking the Streamlit script thread. Agent tool wrappers are thin adapters (10-30 lines) that call existing `src/` service functions without modifying their signatures, preserving the 392-test baseline.

**Major components:**
1. **Voice Bridge** (`voice/bridge.py`, `stt.py`, `tts.py`) — browser mic capture → faster-whisper transcript → KittenTTS WAV bytes → `st.audio` playback; no Streamlit imports inside this layer
2. **Jarvis Coordinator** (`coordinator/intent.py`, `proposal.py`, `approval.py`, `response.py`) — Gemini-powered intent parsing, `AgentAction` proposal generation, approval state machine (`PENDING → APPROVED/REJECTED → EXECUTING → DONE/FAILED`)
3. **NemoClaw Orchestrator** (`agents/orchestrator.py`) — lead agent that decomposes approved actions into parallel sub-agent dispatches via `agents/result_bus.py` background thread
4. **Agent Tool Wrappers** (`agents/tools/scraper_tool.py`, `matcher_tool.py`, `outreach_tool.py`, `poc_tool.py`) — MCP tool callables wrapping existing `src/` services; no business logic duplication
5. **Command Center Tab** (`ui/command_center.py`) — live agent status board, proposal queue, approval UI rendered at page top; uses `@st.fragment(run_every=2)` for polling
6. **POC Contact Store** (`poc/store.py`, `history.py`) — CSV-backed, immutable update pattern; feeds proactive suggestion triggers

**Key patterns:**
- Approval state machine in `st.session_state["pending_actions"]` — never a blocking wait loop
- Background thread + `queue.Queue` — all agent execution off the script thread; results polled by `@st.fragment`
- Thin MCP tool adapters — existing service functions are not modified; wrappers call them directly
- KittenTTS as sentence-chunked pure function — generate per sentence, cache model at startup to avoid 3-5s cold-start on every call

### Critical Pitfalls

1. **KittenTTS is TTS-only — full duplex requires a separate STT layer** — KittenTTS has zero STT capability. Plans that mention "KittenTTS for voice" without naming an explicit STT provider will produce a deaf Jarvis. Mitigation: split voice pipeline into discrete STT (faster-whisper) and TTS (KittenTTS) components from the first line of code; wire through a common `VoiceIO` abstraction.

2. **NemoClaw is seven-day-old alpha software with NVIDIA-only model support** — APIs change between releases, Gemini is not a supported model provider, and the SDK is marked "do not use in production." Mitigation: build Phases 1-3 against a direct async dispatch contract that NemoClaw can slot into in Phase 4; if NemoClaw proves unusable on demo day, the Phase 3 direct-dispatch path is the fallback.

3. **Streamlit's rerun model kills long-running agent tasks** — any UI interaction reruns the script, terminating in-progress agent execution (10-30s scraping/LLM calls). Mitigation: all agent execution in background daemon threads via `queue.Queue`; never call agent logic in a button callback; use `@st.fragment(run_every=2)` for status polling.

4. **Session state corruption from concurrent agent writes** — `st.session_state` is not thread-safe; parallel sub-agents writing to shared keys (`match_results_df`, `scraped_events`) produce corrupted DataFrames. Mitigation: each agent writes only to a namespaced key (`agent_scrape_result`); main thread merges on rerun; use `threading.Lock` for any shared key.

5. **Agent wrapping breaks the 392-test baseline** — adding `agent_context` parameters to existing function signatures breaks mocks in existing tests. Mitigation: adapters are new functions that call existing functions unchanged; run `pytest tests/ -x` after every adapter addition before continuing; never modify existing function signatures.

**Additional watch items:**
- HITL approval gate must be a session-state state machine (not a blocking loop or `st.experimental_dialog` modal that dismisses on rerender)
- Browser microphone requires HTTPS — demo served via IP address (not localhost) will silently deny mic access; use `ngrok` or run on presenter's own machine
- KittenTTS model must be loaded once at startup into `st.session_state["tts_model"]` — cold start is 3-5s per call if not cached
- TTS/STT feedback loop: mute STT while TTS is playing via a `tts_speaking` flag in session state

## Implications for Roadmap

Based on research, suggested phase structure (4 phases, strictly ordered by dependency):

### Phase 1: Voice I/O Foundation

**Rationale:** KittenTTS and faster-whisper are medium-confidence (alpha APIs, reported install issues); validate them in isolation before any agent or coordinator complexity is added. This phase is also the primary prevention point for Pitfall 1 (KittenTTS treated as duplex). A working voice demo (hardcoded Jarvis reply, real TTS+STT) is independently demoable.

**Delivers:** `voice/stt.py`, `voice/tts.py`, `voice/bridge.py`, `ui/voice_panel.py` — coordinator speaks into mic, sees transcript, hears hardcoded Jarvis reply via KittenTTS

**Features addressed:** Voice TTS output, Voice STT input (push-to-talk), Text command interface (added as fallback in the same panel)

**Pitfalls prevented:** KittenTTS-as-duplex assumption, KittenTTS model cold-start on every call, HTTPS/microphone preflight discovery

**Stack elements:** kittentts 0.8.1 (wheel install), faster-whisper, soundfile, streamlit-webrtc 0.6.0

**Research flag:** Needs validation — KittenTTS pip install has reported dependency failures; test wheel install on demo hardware before coding begins. streamlit-webrtc requires localhost for microphone during development.

### Phase 2: Coordinator Core and HITL Approval Gate

**Rationale:** The approval state machine is the hard architectural constraint from PROJECT.md. It must exist and be proven correct before any real agent is wired to it — otherwise the HITL constraint is impossible to retrofit later. Gemini (already integrated) handles intent parsing, so no new LLM dependency is added. Phase 2 is demoable as "Jarvis listens, proposes an action, coordinator approves or rejects" with stubbed agent execution.

**Delivers:** `coordinator/intent.py`, `coordinator/proposal.py`, `coordinator/approval.py`, `coordinator/response.py`, `ui/command_center.py` (approval UI), extended `runtime_state.py` — full voice → Gemini intent → `AgentAction(PENDING)` → Approve/Reject cycle, no real agent execution

**Features addressed:** HITL approval flow, Agent status indicators, Conversation history

**Pitfalls prevented:** Blocking approval loop (use state machine pattern), approval buttons disappearing on rerender (render in `st.fragment` with stable key), pending approvals hard to find (render at top of Command Center tab)

**Architecture component:** Jarvis Coordinator + Approval State Machine

**Research flag:** Standard patterns — LangGraph + Streamlit human-in-the-loop pattern is well-documented; `st.stop()` + state machine approach is established. No additional research needed.

### Phase 3: Agent Tool Wrappers and Result Bus

**Rationale:** With the approval gate proven, approved actions can now safely be dispatched to real services. Tool wrappers must be built before the NemoClaw orchestrator because NemoClaw requires OpenClaw tool callables to dispatch. This phase also establishes the threading foundation (Pitfall 3 and 4 prevention) and the adapter-without-signature-modification rule (Pitfall 7 prevention). Stubbing NemoClaw with direct tool calls here creates the fallback that protects Phase 4.

**Delivers:** `agents/tools/scraper_tool.py`, `agents/tools/matcher_tool.py`, `agents/tools/outreach_tool.py`, `agents/tools/poc_tool.py`, `agents/result_bus.py`, `poc/store.py`, `poc/history.py` — approved actions dispatch to real SmartMatch services via background thread; results appear in Command Center

**Features addressed:** Existing SmartMatch tools wrapped as OpenClaw callables, POC contact management with history (data layer), agent results surfaced in UI

**Pitfalls prevented:** 392-test baseline regression (adapter-only pattern, no signature changes), session state corruption (namespaced agent result keys + threading.Lock), Streamlit rerun killing agent tasks (background thread + queue.Queue)

**Architecture component:** Agent Tool Wrappers + Result Bus (background threading pattern)

**Research flag:** Standard patterns for threading and MCP tool schemas. However, test the OpenClaw tool callable schema format early — openclaw-sdk is independently maintained (LOW confidence) and the tool registration API may differ from documented examples.

### Phase 4: NemoClaw Lead Agent and Live Dashboard

**Rationale:** NemoClaw is the highest-risk component (seven-day-old alpha, Gemini not supported). It goes last so a demo-ready fallback (Phase 3 direct dispatch) exists. The Command Center dashboard is only meaningful with real parallel agents running, so it completes here alongside the NemoClaw integration. If NemoClaw proves unusable, Phase 3's direct-dispatch path is the demo.

**Delivers:** `agents/orchestrator.py`, full `ui/command_center.py` with real-time per-agent status (PENDING → EXECUTING → DONE/FAILED), end-to-end voice → intent → approve → parallel NemoClaw sub-agents → TTS voice response demo

**Features addressed:** NemoClaw/OpenClaw sub-agent dispatch, Visual multi-agent Command Center dashboard, Parallel agent dispatch with live status, Proactive Jarvis suggestions (trigger layer added to response.py)

**Pitfalls prevented:** NemoClaw inside Streamlit script thread (invoke only from background thread), Gemini credentials passed to NemoClaw (use Nemotron for sub-agents, Gemini for intent parsing only), NemoClaw blueprint schema changes (pin version in requirements.txt)

**Architecture component:** NemoClaw Orchestrator + Command Center dashboard

**Research flag:** Needs research — NemoClaw is alpha with documented breaking changes. Before Phase 4 begins, verify: (1) openclaw-sdk agent dispatch API with current package version, (2) whether Nemotron model endpoints are accessible from the demo environment, (3) whether parallel mode works with the tool schema built in Phase 3. Have the asyncio direct-dispatch fallback ready to swap in if NemoClaw fails on demo day.

### Phase Ordering Rationale

- **Voice before coordinator:** KittenTTS and faster-whisper must be validated on demo hardware before coordinator or agent logic depends on them. A broken voice layer discovered in Phase 3 would be catastrophic.
- **Approval gate before any real agent:** The HITL constraint is non-negotiable; it cannot be added as an afterthought once agents are wired and running. Phase 2 makes the constraint testable in isolation.
- **Tool wrappers before NemoClaw:** NemoClaw dispatches tools; tools must exist and be independently callable before the orchestrator is wired. This also creates the fallback dispatch path.
- **NemoClaw last:** Highest risk, lowest documentation confidence, requires NVIDIA API access. Everything before it delivers a demoable product independently.
- **POC contact management deferred to Phase 3-4 boundary:** It depends on outreach agent output (Phase 3) and enriches proactive suggestions (Phase 4). It fits naturally at the Phase 3/4 seam.

### Research Flags

**Needs research before implementation:**
- **Phase 1:** KittenTTS wheel install on demo hardware — validate `misaki>=0.9.4` dependency resolves; validate model download (~25MB) succeeds in demo environment
- **Phase 1:** streamlit-webrtc push-to-talk UX — validate browser mic capture works at localhost in development before building around it
- **Phase 4:** NemoClaw/openclaw-sdk API stability — verify current tool callable schema, parallel dispatch mode, and Nemotron endpoint availability before writing orchestrator code; have asyncio fallback ready

**Standard patterns (skip additional research):**
- **Phase 2:** LangGraph + Streamlit HITL state machine pattern is thoroughly documented across multiple sources with working code examples
- **Phase 3:** Background threading with `queue.Queue` in Streamlit is an established pattern documented in official Streamlit multithreading guide
- **Phase 3:** MCP FastMCP tool wrapping pattern is stable and well-documented

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | KittenTTS and faster-whisper HIGH confidence (multiple sources, working code confirmed); openclaw-sdk LOW confidence (independently maintained, alpha); streamlit-webrtc MEDIUM (established library but HTTPS/TURN requirements need demo environment validation) |
| Features | MEDIUM | Table stakes and HITL patterns HIGH confidence from multiple framework references; NemoClaw-specific features LOW confidence due to alpha status; KittenTTS feature boundary (TTS-only) HIGH confidence |
| Architecture | MEDIUM | Streamlit threading patterns and layer separation HIGH confidence from official docs; NemoClaw orchestration layer LOW confidence (API subject to change); overall component decomposition MEDIUM (consistent across research files) |
| Pitfalls | HIGH | Streamlit threading pitfalls HIGH confidence backed by official docs and multiple GitHub issues; KittenTTS TTS-only limitation HIGH confidence; NemoClaw model lock-in HIGH confidence from release notes explicitly stating NVIDIA-only; HTTPS microphone pitfall HIGH confidence from Streamlit community |

**Overall confidence:** MEDIUM

### Gaps to Address

- **openclaw-sdk API surface:** The package is independently maintained at `github.com/masteryodaa/openclaw-sdk` — not an official NVIDIA package. Verify the tool registration API, authentication flow, and parallel dispatch syntax against the installed version before Phase 3 begins. May need to fall back to direct asyncio task dispatch if the SDK is non-functional.

- **NemoClaw + Gemini coexistence:** NemoClaw currently supports only Nemotron models for inference. The existing SmartMatch app uses Gemini for matching and intent parsing. The architecture keeps these as parallel LLM backends with distinct roles, but the seam (coordinator uses Gemini, sub-agents use Nemotron) has not been integration-tested. Validate this boundary early in Phase 4.

- **Demo environment HTTPS:** streamlit-webrtc requires HTTPS for non-localhost deployments. Demo presentation environment (projected from laptop vs. shared via network URL) must be confirmed before Phase 1 completes. Add an explicit check to the preflight script.

- **KittenTTS `misaki>=0.9.4` dependency:** Reported PyPI install failures exist. The wheel method should resolve this, but must be validated on the actual demo hardware (OS, Python version) before it becomes a Phase 1 blocker.

- **NemoClaw API key availability:** NemoClaw requires NVIDIA NGC API keys from `build.nvidia.com/settings/api-keys`. Confirm key provisioning before Phase 4 begins — this is a demo-day risk if account setup is delayed.

## Sources

### Primary (HIGH confidence)
- [GitHub - KittenML/KittenTTS](https://github.com/KittenML/KittenTTS) — TTS-only capability confirmed, installation method, voice list, Python API
- [KittenML/kitten-tts-nano-0.1 on Hugging Face](https://huggingface.co/KittenML/kitten-tts-nano-0.1) — model sizes, output format
- [Streamlit threading documentation](https://docs.streamlit.io/develop/concepts/design/multithreading) — ScriptRunContext constraints, background thread patterns
- [Streamlit st.fragment docs](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) — run_every parameter, stable in Streamlit 1.37+
- [Streamlit st.audio_input docs](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input) — clip-only (not streaming) confirmed
- [GitHub - SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 4x speed, bundled FFmpeg via PyAV, CPU-optimized
- [NVIDIA NemoClaw Developer Guide](https://docs.nvidia.com/nemoclaw/latest/about/overview.html) — alpha status, OpenShell architecture, "do not use in production"

### Secondary (MEDIUM confidence)
- [streamlit-webrtc PyPI](https://pypi.org/project/streamlit-webrtc/) — version 0.6.0, Python >=3.10, TURN server requirements
- [How to Build Human-in-the-Loop Agents with LangGraph and Streamlit](https://www.marktechpost.com/2026/02/16/how-to-build-human-in-the-loop-plan-and-execute-ai-agents-with-explicit-user-approval-using-langgraph-and-streamlit/) — state-machine approval pattern
- [OpenClaw Python Integration Guide](https://openclaw-ai.net/en/blog/openclaw-python-integration) — tool callable schema, parallel dispatch mode
- [Streamlit GitHub issue #6818](https://github.com/streamlit/streamlit/issues/6818) — async session state failure patterns
- [Streamlit discussion: HITL approval patterns](https://discuss.streamlit.io/t/implementing-human-in-the-loop-to-decide-whether-to-continue/113911) — st.stop() approval gate pattern

### Tertiary (LOW confidence — needs validation before use)
- [GitHub - masteryodaa/openclaw-sdk](https://github.com/masteryodaa/openclaw-sdk) — Python SDK for OpenClaw/NemoClaw; independently maintained, not official NVIDIA package
- [NemoClaw on DEV Community](https://dev.to/arhtechpro/nemoclaw-nvidias-open-source-stack-for-running-ai-agents-you-can-actually-trust-50gl) — NVIDIA-only model support in current alpha
- [KittenTTS on Hacker News](https://news.ycombinator.com/item?id=44807868) — streaming API planned but not yet available; latency benchmarks (~8.5s for 23 words) need validation on demo hardware

---
*Research completed: 2026-03-23*
*Ready for roadmap: yes*
