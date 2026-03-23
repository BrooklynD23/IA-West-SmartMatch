# Feature Research

**Domain:** Voice-driven AI coordinator with sub-agent orchestration (Jarvis-style CRM command center)
**Researched:** 2026-03-23
**Confidence:** MEDIUM — KittenTTS capabilities verified HIGH via multiple sources; NemoClaw is early-alpha (announced March 16, 2026) so API details are LOW confidence and may shift; HITL patterns are HIGH confidence from multiple framework sources.

---

## Context: What Already Exists

The following SmartMatch features are **already built** and must be treated as agent-callable services, not re-implemented:

| Existing Feature | Agent Service Name |
|------------------|--------------------|
| Event discovery via web scraping | `discovery_agent` |
| Six-factor speaker ranking | `matching_agent` |
| Outreach email + calendar generation | `outreach_agent` |
| Demo mode with caching | (infrastructure, not an agent) |
| Streamlit UI: Discovery, Matches, Volunteer Dashboard tabs | (host shell for new Command Center tab) |

All new features described below are **additive only** — they extend the existing app without replacing it.

---

## Feature Landscape

### Table Stakes (Demo Judges Expect These)

Features required for the "Jarvis command center" demo to feel credible. Missing any of these makes the demo feel like a chatbot, not a coordinator.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Text input command interface | Every AI coordinator demo has a text fallback; voice alone is brittle in noisy demo environments | LOW | `st.chat_input` in a new "Command Center" tab; feeds same intent parser as voice |
| Voice synthesis output (TTS) | "Jarvis" is defined by a voice that speaks back — silence breaks the demo illusion | LOW | KittenTTS v0.8: pip install, Python API, 8 built-in voices (Bella, Hugo, etc.), 24kHz output, CPU-only, 15-80MB model. No GPU required. Returns numpy array or writes WAV. English-only. |
| Voice speech-to-text input (STT) | Coordinator speaks to Jarvis; text-only is not "full-duplex voice" | MEDIUM | KittenTTS is **TTS only** — no STT. Must use a separate STT library. Best pairing: `RealtimeSTT` (KoljaB/RealtimeSTT) for low-latency microphone capture + Whisper for transcription. Alternatively: `SpeechRecognition` + PyAudio for simpler setup. VoicePipe wraps KittenTTS + STT as one pipeline. |
| Proposed action display before execution | HITL gate is the core architectural constraint; agents must show "I want to do X — approve?" | MEDIUM | Approval card UI: show agent name, proposed action, reasoning, Approve/Reject/Edit buttons. Streamlit supports this with `st.expander` + `st.button`. |
| Approve / Reject / Edit actions | Coordinator must be able to greenlight, kill, or modify every agent proposal | MEDIUM | Three-button pattern per pending action. "Edit" opens a text area to modify the parameters before approval. State managed in `st.session_state`. |
| Agent status indicators | Show which sub-agents are idle / running / waiting for approval / complete | MEDIUM | Progress indicators per agent lane. `st.status` or custom colored badges. Updates via `st.rerun()` polling or Streamlit's built-in streaming. |
| Conversation history | Coordinator needs to see what Jarvis said and what was approved/rejected | LOW | `st.chat_message` component renders assistant and user turns. Persist in session state list. |

### Differentiators (Competitive Advantage for Hackathon)

Features that elevate the demo above "a chatbot with buttons" to "a real AI coordination platform."

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Visual multi-agent orchestration dashboard | Shows parallel agents running simultaneously — the "command center" wow factor | HIGH | Swimlane or card-grid layout: one card per agent (Discovery, Matching, Outreach, POC). Each card shows status, last action, result count. Plotly or pure Streamlit components. Depends on: agent dispatch infrastructure being wired up first. |
| NemoClaw sub-agent dispatching | NVIDIA branding + structured orchestration differentiates from "just LangChain"; OpenClaw routes tasks to specialist agents | HIGH | NemoClaw is early-alpha (released March 16, 2026). It wraps OpenClaw with NVIDIA OpenShell sandbox + Nemotron inference. For hackathon: use OpenClaw directly (simpler) with NemoClaw as the named orchestration layer. OpenClaw Python SDK (`pip install openclaw`) supports sequential, parallel, and hierarchical modes. API key from NVIDIA NGC for Nemotron inference. **Expect rough edges.** |
| Parallel agent dispatch with live status | Dispatch discovery + matching simultaneously and show progress in real-time, not sequentially | HIGH | OpenClaw parallel mode dispatches independent subtasks concurrently. Streamlit `st.empty()` or fragment-based updates for live status. Critical differentiator: shows multi-agent coordination visually, not just sequentially. |
| POC contact management with history | Tracks who was contacted, when, outcome, follow-up needed — extends the outreach tab | MEDIUM | New data structure: `contact_log` entries (speaker_id, event_id, contacted_at, channel, outcome, follow_up_date). Session-state or CSV persistence for demo. Jarvis can surface "you haven't followed up with X" as a proactive suggestion. Depends on: existing outreach agent output. |
| Proactive Jarvis suggestions | Jarvis notices when discovery results are stale or outreach is overdue and volunteers actions without being prompted | MEDIUM | Trigger-based: check last_discovery_ts, check pending outreach count, check follow-up dates. Surface as `st.toast` or inline suggestion card. Coordinator approves before any action runs. |
| Voice wake word / push-to-talk toggle | Activates the mic only on button hold or keyword, preventing runaway transcription | MEDIUM | Push-to-talk via `st.button` (hold to record) is simpler and more demo-reliable than wake word detection. Wake word requires always-on mic loop — brittle in demo. Recommend push-to-talk for hackathon. |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Fully autonomous agent execution without approval | Faster, fewer clicks | Violates the hard architectural constraint in PROJECT.md; also removes the demo's most impressive interaction — the approval flow | Keep every agent action gated on coordinator confirmation; make the approval cards polished and fast |
| Always-on microphone listening (wake word activation) | More "Jarvis-like" | Unreliable in hackathon demo environments (background noise, mic permissions, browser sandboxing); long transcription loops cause Streamlit rerenders | Push-to-talk button held while speaking; text fallback always available |
| Custom TTS voice training | Unique Jarvis persona voice | PROJECT.md explicitly out-of-scope; adds weeks of work; KittenTTS built-in voices (Hugo for deep Jarvis-style) are sufficient for demo | Use KittenTTS `Hugo` or `Bruno` voice at speed 0.9 for a measured AI coordinator tone |
| Production-grade auth / multi-tenant | Feels "enterprise ready" | Out-of-scope per PROJECT.md; adds infrastructure complexity with zero demo value | Single-user local Streamlit session is appropriate for hackathon demo |
| Real-time streaming transcription during speech | Impressive live visual | Requires VAD (voice activity detection) + streaming Whisper — significant complexity. Adds latency unpredictability to demos | Record full utterance (push-to-talk), transcribe once, display result — simpler and more reliable |
| Mobile / native app interface | Broader reach | Out-of-scope per PROJECT.md; Streamlit web is the target shell | Streamlit in a browser window is the demo surface; ensure layout is clean at 1080p |
| Agent self-modification / rewriting its own tools | Advanced agent demo point | High risk of runaway behavior; contradicts HITL constraint | Agents call fixed tool wrappers; coordinator edits parameters in the approval card before executing |

---

## Feature Dependencies

```
[Voice STT Input]
    └──requires──> [Push-to-Talk Button / Mic Capture]
    └──requires──> [STT Library (RealtimeSTT or SpeechRecognition+PyAudio)]

[Voice TTS Output]
    └──requires──> [KittenTTS installed (pip install kittentts)]
    └──requires──> [Audio playback in Streamlit (st.audio with BytesIO)]

[HITL Approval Flow]
    └──requires──> [Pending Action Queue in session_state]
    └──requires──> [Approve/Reject/Edit UI components]

[NemoClaw Sub-Agent Dispatching]
    └──requires──> [OpenClaw installed and configured]
    └──requires──> [NVIDIA NGC API key for Nemotron inference]
    └──requires──> [Existing SmartMatch functions wrapped as OpenClaw tool callables]
        └──requires──> [discovery_agent tool wrapper (wraps existing scraper)]
        └──requires──> [matching_agent tool wrapper (wraps existing ranker)]
        └──requires──> [outreach_agent tool wrapper (wraps existing email/calendar gen)]

[Visual Multi-Agent Dashboard]
    └──requires──> [NemoClaw Sub-Agent Dispatching]
    └──requires──> [Per-agent status state in session_state]
    └──enhances──> [HITL Approval Flow] (approval cards appear in dashboard lanes)

[POC Contact Management]
    └──requires──> [Existing outreach agent output (speaker_id, event_id)]
    └──enhances──> [Proactive Jarvis Suggestions] (surfaces overdue follow-ups)

[Proactive Jarvis Suggestions]
    └──requires──> [HITL Approval Flow] (suggestions are proposed actions, not auto-executed)
    └──enhances──> [Voice TTS Output] (Jarvis speaks the suggestion aloud)

[Text Command Interface] ──alternative to──> [Voice STT Input]
    (both feed the same intent parser / Jarvis coordinator logic)
```

### Dependency Notes

- **STT is not KittenTTS**: KittenTTS is TTS-only. The voice input side requires a separate STT library. RealtimeSTT is the best match for low-latency Python microphone capture. VoicePipe (`pip install voicepipe`) bundles KittenTTS + STT as a combined pipeline — evaluate for simplicity.
- **NemoClaw requires OpenClaw**: NemoClaw is a security/enterprise wrapper around OpenClaw. For a hackathon demo, the underlying OpenClaw Python SDK is the practical integration point. NemoClaw adds the NVIDIA branding narrative and OpenShell sandbox.
- **OpenClaw requires wrapping existing functions**: The existing scraper, ranker, and outreach generator must be exposed as OpenClaw tool callables. This is the critical integration work — without it, NemoClaw has nothing to dispatch.
- **Dashboard requires dispatch to be wired**: The visual command center is only meaningful if real agents are actually running. Build dispatch first, then add the visualization layer.
- **Audio playback in Streamlit**: `st.audio(bytes, format='audio/wav')` works for pre-generated audio. For near-real-time playback, write KittenTTS output to a BytesIO buffer and pass it to `st.audio`. Autoplay requires the `autoplay=True` parameter (Streamlit 1.28+).

---

## MVP Definition

### Launch With (Hackathon Demo — v2.0)

Minimum set that demonstrates the Jarvis coordinator concept and satisfies the PROJECT.md active requirements.

- [ ] **Text command interface** — coordinator types intent; Jarvis responds in chat; no voice required for basic function
- [ ] **Voice TTS output** — Jarvis speaks responses using KittenTTS Hugo/Bruno voice; audio played via `st.audio`
- [ ] **Voice STT input (push-to-talk)** — coordinator holds button, speaks, releases; transcription shown in chat input
- [ ] **HITL approval flow** — every agent action surfaces an approval card (proposed action + Approve/Reject/Edit); no agent executes without sign-off
- [ ] **Existing SmartMatch tools wrapped as OpenClaw agent callables** — discovery, matching, outreach callable via NemoClaw dispatch
- [ ] **NemoClaw/OpenClaw sub-agent dispatch** — Jarvis routes intent to correct sub-agent via OpenClaw; NemoClaw provides the named orchestration layer
- [ ] **Visual multi-agent dashboard** — Command Center tab showing per-agent status cards (idle/running/awaiting approval/complete)

### Add After Validation (v2.1)

- [ ] **POC contact management** — add once core approval flow is working; moderate complexity, strong demo story for hackathon judges focused on CRM use case
- [ ] **Proactive Jarvis suggestions** — add after contact log exists; Jarvis surfaces "outreach overdue for X" without being asked

### Future Consideration (v3+)

- [ ] **Always-on wake word activation** — too brittle for demo; revisit only for post-hackathon production path
- [ ] **Parallel agent streaming UI** — real-time progress bars per agent mid-execution; adds polish but requires more Streamlit threading work
- [ ] **Multi-language TTS** — KittenTTS is English-only; would require swapping TTS provider

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| HITL approval flow (pending queue + approve/reject/edit) | HIGH | MEDIUM | P1 |
| Text command interface | HIGH | LOW | P1 |
| Voice TTS output (KittenTTS) | HIGH | LOW | P1 |
| Wrap existing tools as OpenClaw callables | HIGH | MEDIUM | P1 |
| NemoClaw/OpenClaw dispatch | HIGH | HIGH | P1 |
| Voice STT input (push-to-talk + Whisper/RealtimeSTT) | MEDIUM | MEDIUM | P1 |
| Visual multi-agent dashboard | HIGH | HIGH | P2 |
| POC contact management with history | MEDIUM | MEDIUM | P2 |
| Proactive Jarvis suggestions | MEDIUM | MEDIUM | P2 |
| Parallel agent dispatch with live status | MEDIUM | HIGH | P2 |
| Voice wake word activation | LOW | HIGH | P3 |
| Real-time streaming transcription | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for hackathon demo launch
- P2: Should have — add in implementation order once P1 is stable
- P3: Nice to have, defer post-hackathon

---

## Competitor / Reference Analysis

| Feature | LangGraph + Streamlit (reference impl) | OpenAI Agents SDK | Our Approach (NemoClaw + KittenTTS) |
|---------|----------------------------------------|-------------------|--------------------------------------|
| HITL approval | interrupt() node pauses graph; human resumes | `on_tool_call` hook + approval wrapper | Session-state pending queue; Approve/Reject/Edit cards in Command Center tab |
| Multi-agent dispatch | Graph nodes with parallel branches | Handoffs between agents | OpenClaw parallel mode; NemoClaw for NVIDIA branding + sandboxing |
| Voice output | External TTS (ElevenLabs, etc.) | External TTS | KittenTTS (local, no API cost, 25MB, CPU-only) |
| Voice input | Whisper via OpenAI API | Whisper | RealtimeSTT + Whisper local or SpeechRecognition+PyAudio |
| Dashboard | Custom Streamlit components | N/A | Streamlit cards/swimlanes; Plotly for agent activity timeline |

---

## Technology Notes

### KittenTTS (HIGH confidence)
- Python package: `pip install kittentts`
- TTS only — no microphone input, no STT
- Three model sizes: 15M, ~40M, 80M parameters (nano/small/medium)
- 8 voices: Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo
- Output: 24kHz numpy array or WAV file
- CPU-only (ONNX backend), no GPU required
- English-only
- Speed parameter: default 1.0, adjustable
- For demo: `Hugo` voice at speed 0.9 gives a measured AI coordinator tone
- Streamlit playback: write to BytesIO WAV buffer, pass to `st.audio(buffer, format='audio/wav', autoplay=True)`

### STT Recommendation (MEDIUM confidence)
- KittenTTS does NOT provide STT — this is a common assumption to avoid
- For hackathon: `RealtimeSTT` (GitHub: KoljaB/RealtimeSTT) gives low-latency mic capture + Whisper
- Simpler alternative: `SpeechRecognition` + `PyAudio` — more brittle but fewer dependencies
- VoicePipe (`pip install voicepipe`) bundles KittenTTS + STT — evaluate if it simplifies integration

### NemoClaw / OpenClaw (LOW confidence — early alpha as of 2026-03-16)
- NemoClaw = OpenClaw + NVIDIA OpenShell sandbox + Nemotron inference routing
- For hackathon: OpenClaw Python SDK (`pip install openclaw`) is the practical integration path
- OpenClaw supports: sequential, parallel, hierarchical agent modes
- Requires: NVIDIA NGC API key for Nemotron inference via build.nvidia.com
- `openclaw agent --agent main --local -m "message"` for CLI testing
- Agent tools are defined as Python callables wrapped in OpenClaw tool schema
- "Expect rough edges" — APIs may change; test integration early in implementation
- Fallback plan: if NemoClaw proves too unstable for hackathon, use direct Python async dispatch (asyncio) with NemoClaw cited as the intended orchestration layer

---

## Sources

- [GitHub: KittenML/KittenTTS — State-of-the-art TTS model under 25MB](https://github.com/KittenML/KittenTTS)
- [KittenML/kitten-tts-nano-0.1 on Hugging Face](https://huggingface.co/KittenML/kitten-tts-nano-0.1)
- [Introducing Kitten TTS v0.8: Compact, Efficient Voice Synthesis](https://conzit.com/post/introducing-kitten-tts-v08-compact-efficient-voice-synthesis)
- [VoicePipe on PyPI — KittenTTS + STT combined pipeline](https://pypi.org/project/voicepipe/)
- [GitHub: KoljaB/RealtimeSTT — Low-latency speech-to-text with voice activity detection](https://github.com/KoljaB/RealtimeSTT)
- [NVIDIA NemoClaw Developer Guide: How It Works](https://docs.nvidia.com/nemoclaw/latest/about/how-it-works.html)
- [NVIDIA NemoClaw Overview](https://docs.nvidia.com/nemoclaw/latest/about/overview.html)
- [GitHub: NVIDIA/NemoClaw](https://github.com/NVIDIA/NemoClaw)
- [OpenClaw Python Integration: SDK, API & Custom Skills Guide (2026)](https://openclaw-ai.net/en/blog/openclaw-python-integration)
- [OpenClaw Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)
- [openclaw on PyPI](https://pypi.org/project/openclaw/)
- [MindStudio: What Is NemoClaw?](https://www.mindstudio.ai/blog/what-is-nemoclaw-nvidia-enterprise-ai-agents)
- [How to Build Human-in-the-Loop Plan-and-Execute AI Agents with LangGraph and Streamlit](https://www.marktechpost.com/2026/02/16/how-to-build-human-in-the-loop-plan-and-execute-ai-agents-with-explicit-user-approval-using-langgraph-and-streamlit/)
- [Human-in-the-Loop Architecture: When Humans Approve Agent Decisions](https://www.agentpatterns.tech/en/architecture/human-in-the-loop-architecture)
- [Building a Real-Time Voice Agent in Python (Whisper + Ollama + VAD + Streamlit)](https://medium.com/@TechSnazAI/building-a-real-time-voice-agent-in-python-whisper-ollama-vad-streamlit-3a19c5e91b15)
- [OpenJarvis: Personal AI, On Personal Devices — Stanford Scaling Intelligence Lab](https://scalingintelligence.stanford.edu/blogs/openjarvis/)

---
*Feature research for: Jarvis-style voice + agent orchestration layer on SmartMatch CRM (v2.0)*
*Researched: 2026-03-23*
