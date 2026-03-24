"""KittenTTS wrapper — text to WAV bytes. No Streamlit imports."""
import io
import logging
import re

import numpy as np
import soundfile as sf

logger = logging.getLogger(__name__)

KITTENTTS_MODEL_ID = "KittenML/kitten-tts-mini-0.8"
KITTENTTS_SAMPLE_RATE = 24000


def load_tts_model():
    """Load KittenTTS model. Call once; cache result in session_state."""
    from kittentts import KittenTTS
    return KittenTTS(KITTENTTS_MODEL_ID)


def synthesize_to_wav_bytes(text: str, model, voice: str = "Bella") -> bytes:
    """Return WAV bytes for the given text using the provided KittenTTS model."""
    if not text.strip():
        raise ValueError("Cannot synthesize empty text")
    audio: np.ndarray = model.generate(text, voice=voice)
    buffer = io.BytesIO()
    sf.write(buffer, audio, samplerate=KITTENTTS_SAMPLE_RATE, format="WAV")
    return buffer.getvalue()


def split_into_sentences(text: str) -> list[str]:
    """Split text on sentence boundaries for chunked TTS generation."""
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    return [s for s in sentences if s.strip()]
