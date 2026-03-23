# Stack Research

**Domain:** Voice + agent orchestration layer added to existing Streamlit CRM (v2.0 Jarvis milestone)
**Researched:** 2026-03-23
**Confidence:** MEDIUM — KittenTTS and NemoClaw are both in early/alpha releases; APIs subject to change

---

## Context: What Already Exists (Do NOT Re-Add)

The following are validated and in production in `Category 3 - IA West Smart Match CRM/src/`. Research scope covers additions only.

| Capability | Technology | Status |
|------------|-----------|--------|
| Web UI | Streamlit | In production |
| Data manipulation | pandas | In production |
| Charts | Plotly | In production |
| LLM inference | Gemini (google-generativeai) | In production |
| Web scraping + caching | requests + BeautifulSoup | In production |
| Testing | pytest | 392 passing tests |

---

## New Stack Additions for v2.0 Jarvis

### Core Technologies (New)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| kittentts | 0.8.1 | Text-to-speech (TTS) output for Jarvis voice responses | Project constraint; ultra-lightweight ONNX model (15–80 MB), CPU-only, 8 built-in voices, Apache 2.0. Install via wheel release, not PyPI. |
| faster-whisper | latest (pip) | Speech-to-text (STT) for coordinator voice input | KittenTTS is TTS-only — it has no microphone/STT capability. Faster-whisper is 4× faster than openai-whisper, bundles FFmpeg via PyAV (no system FFmpeg needed), CPU-optimized, same accuracy. Required to close the full-duplex loop. |
| streamlit-webrtc | 0.6.0 | Browser microphone capture and real-time audio frame streaming | Native `st.audio_input` records full clips only (no streaming). streamlit-webrtc uses WebRTC for continuous audio frame callbacks, enabling live STT. Latest release: Nov 2025, requires Python >=3.10. |
| openclaw-sdk | 2026.3.20 | Python SDK for NemoClaw/OpenClaw agent dispatch | NemoClaw itself is a TypeScript CLI runtime (OpenShell sandbox). The Python SDK (`pip install openclaw-sdk`) is the programmatic interface for dispatching sub-agents, managing workspaces, and scheduling tasks from Python code. SDK version 2026.3.20 on PyPI; requires Python >=3.9. |

### Supporting Libraries (New)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| soundfile | latest | Write KittenTTS numpy audio arrays to in-memory WAV buffers for Streamlit playback | Every TTS response before piping to `st.audio()` |
| numpy | (already likely present) | KittenTTS returns raw numpy float32 arrays at 24 kHz | Dependency of KittenTTS; verify it's in requirements.txt |
| pyav | latest (bundled with faster-whisper) | Audio decoding without system FFmpeg | Pulled in automatically by faster-whisper |
| aiortc | latest (pulled by streamlit-webrtc) | WebRTC peer connection handling | Pulled in automatically by streamlit-webrtc |
| python-dotenv | latest | Load NVIDIA_INTEGRATE_API_KEY and NVIDIA_API_KEY from .env | NemoClaw requires API key from build.nvidia.com; never hardcode |
| threading / queue | stdlib | Bridge between Streamlit's script-thread model and background agent workers | Streamlit session_state is not asyncio-safe; stdlib threading with a Queue is the recommended pattern for background agent status updates to the UI |

### Development Tools (New)

| Tool | Purpose | Notes |
|------|---------|-------|
| streamlit-server-state | Cross-session shared state for agent status panel | Use when agent status must be readable from background threads. Provides lock primitives. Alternative to threading.Queue if cross-session visibility is needed. |
| pytest-asyncio | Async test support | If any new async agent code needs unit tests; already common in pytest ecosystem |

---

## Installation

```bash
# TTS output (KittenTTS — install from GitHub wheel, NOT PyPI)
pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl

# STT input (faster-whisper — closes the duplex loop KittenTTS cannot)
pip install faster-whisper

# Browser mic capture for Streamlit
pip install streamlit-webrtc

# NemoClaw / OpenClaw Python SDK
pip install openclaw-sdk

# Audio buffer serialization for st.audio()
pip install soundfile

# Environment variable management (already common; add if not present)
pip install python-dotenv
```

**Environment variables required at runtime:**
```bash
NVIDIA_API_KEY=<from build.nvidia.com/settings/api-keys>
NVIDIA_INTEGRATE_API_KEY=<NemoClaw runtime key>
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| faster-whisper (STT) | openai-whisper | Never for this project — faster-whisper is strictly better: same accuracy, 4× speed, no system FFmpeg required. Use openai-whisper only if CTranslate2 binary fails on target hardware. |
| faster-whisper (STT) | Google Cloud Speech-to-Text API | If offline/CPU usage is not a constraint and cloud latency is acceptable. Adds external dependency and cost. |
| streamlit-webrtc (mic) | `st.audio_input` (native) | Use `st.audio_input` only for one-shot clip recording (simpler), not for continuous real-time STT. Full-duplex requires streamlit-webrtc. |
| openclaw-sdk | Direct NVIDIA REST API calls | Use direct REST only if SDK proves unstable (alpha software). SDK is cleaner for agent dispatch, workspace management, and scheduled tasks. |
| threading + Queue | asyncio + asyncio.Queue | asyncio queues have documented issues with Streamlit's ScriptRunContext (session_state is not asyncio-safe). stdlib threading + Queue is the safe pattern for background agents updating Streamlit UI. |
| KittenTTS | Coqui TTS / pyttsx3 / ElevenLabs | Project constraint mandates KittenTTS. pyttsx3 is lower quality. ElevenLabs adds API cost and cloud dependency. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| KittenTTS for STT | KittenTTS is TTS-only — it has no microphone input, speech recognition, or VAD capability whatsoever | faster-whisper for STT pipeline |
| `st.audio_input` for full-duplex | Records a complete audio clip and returns it as a file — not a streaming interface; cannot drive real-time VAD or live transcription | streamlit-webrtc with audio_frame_callback |
| asyncio.Queue for agent ↔ UI bridge | Streamlit's session_state expects to be called from the script thread; asyncio coroutines running in background threads cause ScriptRunContext errors | threading.Queue + `st.fragment(run_every=...)` polling |
| `pip install kittentts` (PyPI) | The PyPI package name may differ or be absent; reported install failures exist; use the official wheel from GitHub releases | `pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl` |
| NemoClaw as a Python import | NemoClaw itself is a TypeScript CLI / OpenShell runtime, not a Python library | `openclaw-sdk` is the Python interface layer to OpenClaw/NemoClaw |
| PortAudio / PyAudio for browser audio | PortAudio is a system-level device API; it cannot capture browser microphone input in a served Streamlit app | streamlit-webrtc (WebRTC runs in the browser) |

---

## Stack Patterns by Variant

**For the TTS output pipeline (Jarvis speaks):**
- KittenTTS `generate(text, voice="Bella")` returns `numpy.ndarray` at 24 kHz
- `soundfile.write(buffer, audio, 24000, format="WAV")` serializes to BytesIO
- `st.audio(buffer, format="audio/wav", autoplay=True)` plays in browser

**For the STT input pipeline (coordinator speaks):**
- `streamlit-webrtc` captures mic frames via `audio_frame_callback`
- Accumulate frames into a buffer with voice-activity detection (faster-whisper includes VAD)
- Call `faster-whisper` `WhisperModel.transcribe()` on completed utterances
- Push transcript to `threading.Queue`; UI polls via `@st.fragment(run_every="1s")`

**For agent dispatch (NemoClaw sub-agents):**
- `openclaw-sdk` `OpenClawClient` authenticates from env vars automatically
- Dispatch sub-agents (scraping, matching, outreach, POC management) as separate OpenClaw tasks
- Poll task status in background thread; push status updates to `threading.Queue`
- Human-in-the-loop gate: Jarvis proposes action → coordinator clicks Approve/Reject in Streamlit before `client.execute_agent()` is called

**For the command center dashboard:**
- `@st.fragment(run_every="2s")` decorator on agent status panel — rerenders only the panel, not the full page (requires Streamlit >=1.37)
- Each sub-agent represented as a card: name, status (queued/running/awaiting approval/done/error), result summary
- `st.session_state` holds the approval-pending queue; buttons trigger state transitions

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| kittentts 0.8.1 | Python >=3.8, <3.13 | Uses ONNX runtime; avoid Python 3.13 until wheel is tested |
| streamlit-webrtc 0.6.0 | Python >=3.10, aiortc, aioice | Requires HTTPS in non-localhost deployments (hackathon demo on localhost is fine) |
| faster-whisper | Python >=3.8 | CTranslate2 binary wheels available for Linux/macOS/Windows |
| openclaw-sdk 2026.3.20 | Python >=3.9 | Alpha: check changelog before upgrading; interfaces change |
| st.fragment run_every | Streamlit >=1.37 | Released July 2024; stable (non-experimental) in 1.37+ |

---

## Critical Risk Flags

**KittenTTS (MEDIUM confidence):** Labeled "developer preview — APIs may change." Reported pip install failures with dependency `misaki>=0.9.4` not found on PyPI. Use the wheel install method, not `pip install kittentts`.

**NemoClaw / openclaw-sdk (LOW confidence):** NemoClaw announced at GTC 2026, alpha since March 16, 2026. The `openclaw-sdk` Python package is independently maintained and may not be the official NVIDIA SDK. Verify the package at `https://pypi.org/project/openclaw-sdk/` and cross-check against `https://docs.nvidia.com/nemoclaw/latest/` before implementation. Breaking changes are expected between releases.

**streamlit-webrtc TURN server (MEDIUM confidence):** On any non-localhost deployment, WebRTC requires a TURN server for peer connection. For hackathon demo on localhost this is not needed. Flag if demo environment changes.

---

## Sources

- [GitHub - KittenML/KittenTTS](https://github.com/KittenML/KittenTTS) — installation method, version 0.8.1, Python requirements, TTS-only capability confirmed (no STT)
- [KittenML/kitten-tts-nano-0.1 · Hugging Face](https://huggingface.co/KittenML/kitten-tts-nano-0.1) — model sizes and voice list
- [NVIDIA NemoClaw Developer Guide](https://docs.nvidia.com/nemoclaw/latest/about/overview.html) — alpha status, OpenShell architecture, API key requirement
- [GitHub - NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw) — TypeScript CLI nature confirmed, Python SDK is separate
- [openclaw · PyPI](https://pypi.org/project/openclaw/) — SDK install method
- [openclaw-sdk GitHub](https://github.com/masteryodaa/openclaw-sdk) — agent dispatch API (LOW confidence — independently maintained)
- [streamlit-webrtc · PyPI](https://pypi.org/project/streamlit-webrtc/) — version 0.6.0, Python >=3.10
- [st.audio_input — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input) — confirmed clip-only (not streaming)
- [st.fragment — Streamlit Docs](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment) — run_every parameter, stable in Streamlit 1.37+
- [Threading in Streamlit — Streamlit Docs](https://docs.streamlit.io/develop/concepts/design/multithreading) — ScriptRunContext constraints for background threads
- [GitHub - SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) — 4× speed, bundled FFmpeg via PyAV, CPU-optimized
- [LangGraph + Streamlit human-in-the-loop pattern](https://www.marktechpost.com/2026/02/16/how-to-build-human-in-the-loop-plan-and-execute-ai-agents-with-explicit-user-approval-using-langgraph-and-streamlit/) — approval gate UI pattern (MEDIUM confidence)

---
*Stack research for: Jarvis voice + agent orchestration layer on SmartMatch CRM*
*Researched: 2026-03-23*
