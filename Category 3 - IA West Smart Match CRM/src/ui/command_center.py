"""Command Center tab -- voice panel + text input + conversation history."""
from __future__ import annotations

import datetime
import io
import logging

import numpy as np
import soundfile as sf
import streamlit as st

from src.coordinator.approval import ActionProposal
from src.coordinator.intent_parser import ACTION_REGISTRY, ParsedIntent, parse_intent
from src.coordinator.suggestions import check_staleness_conditions

logger = logging.getLogger(__name__)


def render_command_center_tab() -> None:
    """Render Command Center tab: voice panel + text input + conversation history."""
    st.markdown(
        '<h2 style="font-family: var(--font-headline);">Jarvis -- Voice Command Center</h2>',
        unsafe_allow_html=True,
    )

    # Lazy-load TTS model
    if st.session_state.get("tts_model") is None:
        try:
            with st.spinner("Loading voice model (first use)..."):
                from src.voice.tts import load_tts_model
                st.session_state["tts_model"] = load_tts_model()
        except Exception as exc:
            logger.error("TTS model load failed: %s", exc)
            st.warning("Voice synthesis unavailable. Jarvis response shown as text above.")

    # Lazy-load STT model
    if st.session_state.get("stt_model") is None:
        try:
            with st.spinner("Loading speech recognition..."):
                from src.voice.stt import load_stt_model
                st.session_state["stt_model"] = load_stt_model()
        except Exception as exc:
            logger.error("STT model load failed: %s", exc)
            st.warning("Speech recognition unavailable. Please use text commands.")

    # Proactive suggestions
    _inject_proactive_suggestions()

    # Voice panel
    st.markdown('<div class="voice-panel">', unsafe_allow_html=True)
    col_input, col_mic = st.columns([6, 1])
    with col_input:
        user_text = st.text_input(
            "Command",
            placeholder="Type a command or use the mic...",
            key="jarvis_command_input",
            label_visibility="collapsed",
        )
        if st.button("Send Command", key="jarvis_send_btn", type="primary"):
            if user_text and user_text.strip():
                _handle_text_command(user_text.strip())
    with col_mic:
        _render_push_to_talk()
    st.markdown('</div>', unsafe_allow_html=True)

    # Conversation history
    st.divider()
    _render_conversation_history()


def _handle_text_command(text: str, source: str = "text") -> None:
    """Parse intent from command text and create an ActionProposal or unknown reply."""
    ts = datetime.datetime.now().strftime("%H:%M:%S")

    history: list[dict] = st.session_state.get("conversation_history", [])

    history.append({
        "role": "user",
        "text": text,
        "intent": None,
        "timestamp": ts,
        "source": source,
    })

    parsed: ParsedIntent = parse_intent(text)

    if parsed.intent == "unknown":
        unknown_reply = (
            f"I couldn't understand that command. You said: '{text}'. "
            "Try rephrasing — for example, 'find new events' or 'rank speakers for event X'."
        )
        history.append({
            "role": "assistant",
            "text": unknown_reply,
            "intent": "unknown",
            "timestamp": ts,
        })
        st.session_state["conversation_history"] = history

        # TTS playback for unknown reply
        _speak_text(unknown_reply)

        st.rerun()
        return

    # Known intent: create and store action proposal
    description = next(
        (a["description"] for a in ACTION_REGISTRY if a["intent"] == parsed.intent),
        parsed.agent,
    )
    proposal = ActionProposal(
        intent=parsed.intent,
        agent=parsed.agent,
        description=description,
        reasoning=parsed.reasoning,
        params=parsed.params,
    )
    st.session_state["action_proposals"][proposal.id] = proposal
    history.append({
        "role": "proposal",
        "action_id": proposal.id,
        "timestamp": ts,
    })
    st.session_state["conversation_history"] = history

    st.rerun()


def _speak_text(text: str) -> None:
    """Speak text via TTS if model is available. Silently skips if unavailable."""
    tts_model = st.session_state.get("tts_model")
    if tts_model:
        try:
            from src.voice.tts import split_into_sentences, synthesize_to_wav_bytes
            for sentence in split_into_sentences(text):
                wav_bytes = synthesize_to_wav_bytes(sentence, tts_model, voice="Bella")
                st.audio(wav_bytes, format="audio/wav", autoplay=True)
        except Exception as exc:
            logger.error("TTS failed: %s", exc)
            st.info("Voice synthesis unavailable. Jarvis response shown as text above.")


def _render_action_card(proposal: ActionProposal) -> None:
    """Render an action card with agent info, status, and approve/reject/edit controls."""
    with st.container():
        st.markdown(
            f"**{proposal.agent}** | Status: `{proposal.status}`",
            unsafe_allow_html=True,
        )
        st.markdown(proposal.description)
        st.caption(f"Reasoning: {proposal.reasoning}")

        if proposal.status == "proposed":
            with st.expander("Edit Parameters", expanded=False):
                for k in list(proposal.params.keys()):
                    new_val = st.text_input(
                        k,
                        value=str(proposal.params[k]),
                        key=f"param_{proposal.id}_{k}",
                    )
                    proposal.params[k] = new_val

            col_approve, col_reject = st.columns(2)
            with col_approve:
                if st.button("Approve", key=f"approve_{proposal.id}", type="primary"):
                    proposal.approve()
                    proposal.stub_execute()
                    if proposal.result:
                        _speak_text(proposal.result)
                    st.rerun()
            with col_reject:
                if st.button("Reject", key=f"reject_{proposal.id}"):
                    proposal.reject()
                    st.rerun()

        elif proposal.status == "completed":
            st.success(f"Result: {proposal.result}")

        elif proposal.status == "rejected":
            st.warning("Action rejected by coordinator.")

        elif proposal.status in ("approved", "executing"):
            st.info(f"Status: {proposal.status}...")


def _inject_proactive_suggestions() -> None:
    """Inject proactive suggestions into the conversation if data is stale or empty."""
    proposals: dict = st.session_state.get("action_proposals", {})

    # Guard: at most one active proactive suggestion
    for p in proposals.values():
        if p.source == "proactive" and p.status in ("proposed", "approved"):
            return

    suggestions = check_staleness_conditions(
        st.session_state.get("scraped_events", []),
        st.session_state.get("scraped_events_timestamp"),
    )

    for suggestion in suggestions:
        st.session_state["action_proposals"][suggestion.id] = suggestion
        st.session_state.setdefault("conversation_history", []).append({
            "role": "proposal",
            "action_id": suggestion.id,
            "timestamp": suggestion.created_at,
        })


def _render_push_to_talk() -> None:
    """Render push-to-talk mic button; transcribe on stop."""
    try:
        from streamlit_webrtc import WebRtcMode, webrtc_streamer
    except ImportError:
        st.warning("streamlit-webrtc not installed. Use text commands.")
        return

    webrtc_ctx = webrtc_streamer(
        key="jarvis-ptt",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=256,
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
    )

    if not webrtc_ctx.state.playing and webrtc_ctx.audio_receiver:
        frames = []
        try:
            while True:
                frames.extend(webrtc_ctx.audio_receiver.get_frames(timeout=0))
        except Exception:
            pass

        if frames:
            wav_bytes = _frames_to_wav_bytes(frames)
            stt_model = st.session_state.get("stt_model")
            if stt_model and wav_bytes:
                with st.spinner("Transcribing..."):
                    from src.voice.stt import transcribe_audio_bytes
                    transcript = transcribe_audio_bytes(wav_bytes, stt_model)
                if transcript:
                    st.session_state["jarvis_command_input"] = transcript
                    _handle_text_command(transcript, source="voice")
                else:
                    st.warning("No speech detected. Please try again.")
            elif not stt_model:
                st.error("Speech recognition not loaded. Please use text commands.")


def _frames_to_wav_bytes(frames: list) -> bytes:
    """Convert av.AudioFrame list to WAV bytes at 16 kHz."""
    arrays = []
    sample_rate = 16000
    for frame in frames:
        arr = frame.to_ndarray().flatten().astype(np.float32)
        if arr.max() > 1.0:
            arr = arr / 32768.0
        arrays.append(arr)
        sample_rate = getattr(frame, "sample_rate", 16000)
    audio = np.concatenate(arrays)
    buffer = io.BytesIO()
    sf.write(buffer, audio, samplerate=sample_rate, format="WAV")
    return buffer.getvalue()


def _render_conversation_history() -> None:
    """Render chronological conversation history with chat bubbles."""
    history: list[dict] = st.session_state.get("conversation_history", [])
    if not history:
        st.markdown(
            '<div class="chat-container">'
            '<p style="text-align:center; color: var(--secondary);">'
            '<strong>No conversation yet</strong><br>'
            'Type a command above or press the mic button to speak. Jarvis will respond here.'
            '</p></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for entry in history:
        role = entry.get("role", "user")

        if role == "proposal":
            proposal_id = entry.get("action_id")
            proposal = st.session_state.get("action_proposals", {}).get(proposal_id)
            if proposal:
                _render_action_card(proposal)
            continue

        text = entry.get("text", "")
        intent = entry.get("intent")
        timestamp = entry.get("timestamp", "")
        bubble_class = "coordinator" if role == "user" else "jarvis"

        intent_html = ""
        if intent:
            intent_html = f' <span class="intent-badge">[Intent: {intent}]</span>'

        meta_html = f'<div class="chat-meta">{timestamp}{intent_html}</div>'

        st.markdown(
            f'<div class="chat-bubble {bubble_class}">'
            f'{text}'
            f'{meta_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
