"""faster-whisper wrapper — audio bytes to text. No Streamlit imports."""
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

WHISPER_MODEL_SIZE = "base"
WHISPER_COMPUTE_TYPE = "int8"


def load_stt_model():
    """Load faster-whisper model. Call once; cache result in session_state."""
    from faster_whisper import WhisperModel
    return WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type=WHISPER_COMPUTE_TYPE)


def transcribe_audio_bytes(audio_bytes: bytes, model) -> str:
    """Transcribe WAV audio bytes to text."""
    if not audio_bytes:
        return ""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        segments, _info = model.transcribe(
            tmp_path,
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 300},
        )
        texts = [seg.text for seg in segments]
        return " ".join(texts).strip()
    except Exception as exc:
        logger.error("STT transcription failed: %s", exc)
        return ""
    finally:
        Path(tmp_path).unlink(missing_ok=True)
