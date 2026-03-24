"""Unit tests for TTS service module (src/voice/tts.py)."""

import io
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


class TestSynthesizeToWavBytes:
    """Tests for synthesize_to_wav_bytes function."""

    def test_synthesize_returns_wav_bytes(self) -> None:
        """synthesize_to_wav_bytes with mocked model returns bytes starting with RIFF header."""
        from src.voice.tts import synthesize_to_wav_bytes

        mock_model = MagicMock()
        mock_model.generate.return_value = np.zeros(4800, dtype=np.float32)

        result = synthesize_to_wav_bytes("Hello world.", mock_model, voice="Bella")

        assert isinstance(result, bytes)
        assert result[:4] == b"RIFF"

    def test_synthesize_raises_on_empty_text(self) -> None:
        """synthesize_to_wav_bytes raises ValueError when text is empty string."""
        from src.voice.tts import synthesize_to_wav_bytes

        mock_model = MagicMock()
        with pytest.raises(ValueError, match="empty"):
            synthesize_to_wav_bytes("", mock_model)

    def test_synthesize_raises_on_whitespace_text(self) -> None:
        """synthesize_to_wav_bytes raises ValueError when text is whitespace only."""
        from src.voice.tts import synthesize_to_wav_bytes

        mock_model = MagicMock()
        with pytest.raises(ValueError, match="empty"):
            synthesize_to_wav_bytes("   ", mock_model)

    def test_synthesize_calls_model_generate(self) -> None:
        """synthesize_to_wav_bytes calls model.generate with correct args."""
        from src.voice.tts import synthesize_to_wav_bytes

        mock_model = MagicMock()
        mock_model.generate.return_value = np.zeros(4800, dtype=np.float32)

        synthesize_to_wav_bytes("Test sentence.", mock_model, voice="Bella")

        mock_model.generate.assert_called_once_with("Test sentence.", voice="Bella")


class TestSplitIntoSentences:
    """Tests for split_into_sentences function."""

    def test_split_two_sentences(self) -> None:
        """split_into_sentences splits on period followed by space."""
        from src.voice.tts import split_into_sentences

        result = split_into_sentences("Hello world. How are you?")
        assert result == ["Hello world.", "How are you?"]

    def test_split_single_sentence(self) -> None:
        """split_into_sentences returns single item for single sentence."""
        from src.voice.tts import split_into_sentences

        result = split_into_sentences("Single sentence")
        assert result == ["Single sentence"]

    def test_split_question_and_exclamation(self) -> None:
        """split_into_sentences splits on question mark and exclamation."""
        from src.voice.tts import split_into_sentences

        result = split_into_sentences("Question? Answer!")
        assert result == ["Question?", "Answer!"]

    def test_split_strips_empty(self) -> None:
        """split_into_sentences filters empty strings."""
        from src.voice.tts import split_into_sentences

        result = split_into_sentences("  Hello world.  ")
        assert all(s.strip() for s in result)
        assert len(result) >= 1


class TestLoadTtsModel:
    """Tests for load_tts_model function."""

    def test_load_tts_model_calls_kittentts_constructor(self) -> None:
        """load_tts_model calls KittenTTS with the correct model ID."""
        from src.voice import tts as tts_module

        mock_kittentts_cls = MagicMock()
        mock_kittentts_cls.return_value = MagicMock()

        with patch.dict("sys.modules", {"kittentts": MagicMock(KittenTTS=mock_kittentts_cls)}):
            from importlib import reload
            reload(tts_module)
            result = tts_module.load_tts_model()

        mock_kittentts_cls.assert_called_once_with(tts_module.KITTENTTS_MODEL_ID)
        assert result is not None
