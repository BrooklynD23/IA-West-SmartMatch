# Phase 4: Voice I/O Foundation - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver a working voice + text I/O layer in the Streamlit Command Center tab — push-to-talk mic capture with STT, text input fallback, KittenTTS voice output, and chronological conversation history — before any agent or coordinator intelligence is wired in. Phase 4 proves the voice pipeline works with hardcoded Jarvis echo replies; real intent parsing arrives in Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Voice Input Method
- Use streamlit-webrtc with audio_frame_callback for browser mic capture — enables real-time frame streaming for live STT
- Use faster-whisper "base" model (~150MB) for STT — fast enough for CPU demo, good accuracy balance
- Transcribe per-utterance: push-to-talk captures a full clip, transcribes on release, shows in the input field
- Single shared input field for both text typing and STT transcript insertion — unified conversation flow

### TTS Voice and Playback
- Use KittenTTS voice "Bella" for Jarvis — warm, clear female voice (NOTE: "af_heart" from discuss was invalid; research confirmed valid voices are Bella, Jasper, Luna, Bruno, Rosie, Hugo, Kiki, Leo)
- Auto-play TTS output via `st.audio(autoplay=True)` — more natural demo UX, Jarvis "speaks" immediately after each response
- Sentence-chunked TTS generation — split response text on `.`/`?`, generate per sentence, play sequentially to reduce perceived latency
- Cache TTS model in `st.session_state["tts_model"]` — load once per session on first use, avoids 3-5s cold start on every call

### Command Center Tab Layout
- Command Center is the first tab in the tab bar — primary interaction surface for v2.0 Jarvis, existing tabs shift right
- Voice panel (input field + mic button + TTS audio player) positioned at the top of the Command Center tab
- Chat-style conversation bubbles — coordinator messages aligned left, Jarvis responses aligned right, with timestamps
- Subtle intent badge on Jarvis responses (e.g., `[Intent: echo]`) — in Phase 4 this is a hardcoded echo; real parsing arrives Phase 5

### UI Mockup Bridge Strategy
- UI team React/Tailwind mockup exists at `docs/mockup/V1.1/IA-West_UI/` — 7 pages (Dashboard, Opportunities, Volunteers, AI Matching, Pipeline, Calendar, Outreach)
- Design tokens: purple-centric (#8b5cf6 primary), white cards with rounded-xl/border-gray-200/shadow-sm, gradient icon badges, Sparkles icon for AI elements
- Phase 4 builds Command Center in Streamlit with basic styling — NOT matching mockup CSS yet
- Full React migration planned as a future phase; mockup serves as design reference for that migration
- No Command Center page exists in the mockup — it's net-new for v2.0

### Claude's Discretion
- Exact CSS styling of chat bubbles and Command Center layout
- streamlit-webrtc configuration details (STUN server, codec selection)
- WAV buffer encoding details for TTS pipeline
- Error messaging and fallback UX when mic access is denied or TTS fails

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/runtime_state.py` — shared `st.session_state` initialization pattern; extend with voice/conversation keys
- `src/ui/styles.py` — CSS injection via `inject_custom_css()`; extend for chat bubble styling
- `src/config.py` — centralized config with env var loading via `python-dotenv`; add TTS/STT model config
- `src/utils.py` — cross-cutting helpers; `configure_logging()` for new voice modules

### Established Patterns
- Tab rendering: each tab has a `render_*_tab()` function in `src/ui/`; Command Center follows same pattern as `render_command_center_tab()`
- Session state: keys initialized in `init_runtime_state()` with `if key not in st.session_state` guards
- Imports: `from src...` package-root imports; `st.set_page_config()` must remain first Streamlit call in `app.py`
- Error handling: graceful degradation (empty DataFrames, cache fallbacks); `st.error()` for user-facing + `logger.exception()` for server-side
- No Streamlit imports in service modules — voice/stt.py and voice/tts.py must be pure Python (testable without Streamlit)

### Integration Points
- `src/app.py` line ~9-14: `st.set_page_config()` is first; new tab import goes after existing `# noqa: E402` imports
- `src/app.py` tab creation: existing tabs use `st.tabs(["label1", "label2", ...])` — prepend "Command Center" tab
- `src/runtime_state.py:init_runtime_state()` — add `conversation_history`, `tts_model`, `stt_model` session keys
- `requirements.txt` — add `kittentts`, `faster-whisper`, `streamlit-webrtc`, `soundfile`

</code_context>

<specifics>
## Specific Ideas

- Architecture research specifies `voice/` as an isolated subsystem: `voice/stt.py` (bytes->text), `voice/tts.py` (text->bytes), `voice/bridge.py` (orchestrates the pipeline)
- KittenTTS install must use the GitHub wheel: `pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl`
- KittenTTS returns `numpy.ndarray` at 24kHz; use `soundfile.write(buffer, audio, 24000, format="WAV")` to serialize
- faster-whisper: `WhisperModel("base").transcribe(audio_file)` on the captured clip
- The 392 existing tests must continue to pass — zero changes to existing function signatures

</specifics>

<deferred>
## Deferred Ideas

- Real-time streaming transcription during speech (VOICE-05 — requires VAD + streaming Whisper)
- Wake word activation ("Hey Jarvis") for hands-free operation (VOICE-06)
- Intent parsing and action proposal (Phase 5 scope — HITL-01 through HITL-03)
- Agent dispatch and execution (Phase 6 scope — ORCH-01 through ORCH-03)

</deferred>
