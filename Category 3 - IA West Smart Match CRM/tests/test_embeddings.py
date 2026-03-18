"""Tests for embedding composition and caching — Sprint 0 A0.3 / A0.4."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from src.embeddings import (
    _get_client,
    compose_course_text,
    compose_event_text,
    compose_speaker_text,
    embed_courses,
    embed_events,
    embed_speakers,
    generate_embeddings,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture()
def mock_openai_response():
    """Return a factory for mock OpenAI embedding responses."""
    def _make_response(n: int, dim: int = 1536) -> list[list[float]]:
        return [list(np.random.randn(dim).astype(float)) for _ in range(n)]
    return _make_response


# ── Tests: compose_speaker_text ───────────────────────────────────────────────

class TestComposeSpeakerText:
    def test_basic_composition(self) -> None:
        row = {
            "Expertise Tags": "data collection, sales",
            "Title": "SVP Sales",
            "Company": "AcmeCo",
            "Board Role": "President",
        }
        text = compose_speaker_text(row)
        assert "data collection" in text
        assert "SVP Sales" in text
        assert "AcmeCo" in text
        assert "President" in text

    def test_handles_none_company(self) -> None:
        row = {
            "Expertise Tags": "research",
            "Title": "Researcher",
            "Company": None,
            "Board Role": "Member",
        }
        text = compose_speaker_text(row)
        assert "research" in text
        assert "None" not in text

    def test_handles_nan_company(self) -> None:
        row = {
            "Expertise Tags": "research",
            "Title": "Researcher",
            "Company": float("nan"),
            "Board Role": "Member",
        }
        text = compose_speaker_text(row)
        # nan converts to "nan" string; we just want it handled gracefully
        assert isinstance(text, str)
        assert len(text) > 0

    def test_handles_missing_keys(self) -> None:
        row = {"Expertise Tags": "AI, analytics"}
        text = compose_speaker_text(row)
        assert "AI" in text
        assert isinstance(text, str)

    def test_order_is_expertise_title_company_role(self) -> None:
        row = {
            "Expertise Tags": "TAG",
            "Title": "TITLE",
            "Company": "COMPANY",
            "Board Role": "ROLE",
        }
        text = compose_speaker_text(row)
        assert text.index("TAG") < text.index("TITLE") < text.index("COMPANY") < text.index("ROLE")


# ── Tests: compose_event_text ─────────────────────────────────────────────────

class TestComposeEventText:
    def test_basic_composition(self) -> None:
        row = {
            "Event / Program": "AI Hackathon",
            "Category": "AI / Hackathon",
            "Volunteer Roles (fit)": "Judge; Mentor",
            "Primary Audience": "Students",
        }
        text = compose_event_text(row)
        assert "AI Hackathon" in text
        assert "Judge; Mentor" in text
        assert "Students" in text

    def test_handles_missing_keys(self) -> None:
        row = {"Event / Program": "MyEvent"}
        text = compose_event_text(row)
        assert "MyEvent" in text


# ── Tests: compose_course_text ────────────────────────────────────────────────

class TestComposeCourseText:
    def test_basic_composition(self) -> None:
        row = {"Title": "Marketing Research", "Guest Lecture Fit": "High"}
        text = compose_course_text(row)
        assert "Marketing Research" in text
        assert "High" in text

    def test_empty_fit_defaults_to_medium(self) -> None:
        row = {"Title": "Some Course", "Guest Lecture Fit": ""}
        text = compose_course_text(row)
        assert "Medium" in text


# ── Tests: generate_embeddings ────────────────────────────────────────────────

class TestGenerateEmbeddings:
    def test_empty_texts_returns_empty_array(self) -> None:
        result = generate_embeddings([])
        assert result.shape == (0, 1536)
        assert result.dtype == np.float32

    def test_raises_on_empty_text(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            generate_embeddings(["valid text", ""])

    def test_calls_api_and_returns_correct_shape(self, mock_openai_response) -> None:
        texts = ["text one", "text two", "text three"]
        fake_embeddings = mock_openai_response(3)

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in fake_embeddings]

        with patch("src.embeddings._get_client") as mock_client:
            mock_client.return_value.embeddings.create.return_value = mock_response
            result = generate_embeddings(texts)

        assert result.shape == (3, 1536)
        assert result.dtype == np.float32

    def test_get_client_requires_real_openai_key(self, monkeypatch) -> None:
        monkeypatch.setattr("src.embeddings.OPENAI_API_KEY", "")

        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            _get_client()


# ── Tests: embed_speakers caching ────────────────────────────────────────────

class TestEmbedSpeakersCaching:
    def _make_speakers_df(self):
        import pandas as pd
        return pd.DataFrame({
            "Name": ["Alice", "Bob"],
            "Board Role": ["President", "Treasurer"],
            "Metro Region": ["LA", "SF"],
            "Company": ["AcmeCo", "BetaCo"],
            "Title": ["SVP", "Director"],
            "Expertise Tags": ["sales, AI", "research, analytics"],
        })

    def test_embed_speakers_creates_cache_files(self, tmp_path: Path, mock_openai_response) -> None:
        df = self._make_speakers_df()
        fake_embs = mock_openai_response(2)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in fake_embs]

        with patch("src.embeddings._get_client") as mock_client:
            mock_client.return_value.embeddings.create.return_value = mock_response
            embeddings, metadata = embed_speakers(df, cache_dir=tmp_path)

        assert (tmp_path / "speaker_embeddings.npy").exists()
        assert (tmp_path / "speaker_metadata.pkl").exists()
        assert (tmp_path / "cache_manifest.json").exists()
        assert embeddings.shape == (2, 1536)
        assert len(metadata) == 2

    def test_second_call_uses_cache(self, tmp_path: Path, mock_openai_response) -> None:
        df = self._make_speakers_df()
        fake_embs = mock_openai_response(2)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in fake_embs]

        with patch("src.embeddings._get_client") as mock_client:
            mock_client.return_value.embeddings.create.return_value = mock_response
            embed_speakers(df, cache_dir=tmp_path)

        # Second call — API should NOT be called again
        with patch("src.embeddings._get_client") as mock_client2:
            embed_speakers(df, cache_dir=tmp_path)
            mock_client2.assert_not_called()

    def test_cache_invalidated_when_embedding_text_changes(self, tmp_path: Path) -> None:
        df = self._make_speakers_df()
        changed_df = df.copy()
        changed_df.loc[0, "Expertise Tags"] = "completely different tags"

        first = np.ones((2, 1536), dtype=np.float32)
        second = np.full((2, 1536), 2.0, dtype=np.float32)

        with patch("src.embeddings.generate_embeddings", side_effect=[first, second]) as mock_generate:
            emb1, _ = embed_speakers(df, cache_dir=tmp_path)
            emb2, metadata = embed_speakers(changed_df, cache_dir=tmp_path)

        assert mock_generate.call_count == 2
        assert not np.array_equal(emb1, emb2)
        assert "completely different tags" in metadata[0]["embedding_text"]

    def test_cache_invalidated_when_model_changes(self, tmp_path: Path) -> None:
        df = self._make_speakers_df()
        first = np.ones((2, 1536), dtype=np.float32)
        second = np.full((2, 1536), 3.0, dtype=np.float32)

        with patch("src.embeddings.generate_embeddings", side_effect=[first, second]) as mock_generate:
            with patch("src.embeddings.OPENAI_EMBEDDING_MODEL", "model-a"):
                emb1, _ = embed_speakers(df, cache_dir=tmp_path)
            with patch("src.embeddings.OPENAI_EMBEDDING_MODEL", "model-b"):
                emb2, _ = embed_speakers(df, cache_dir=tmp_path)

        assert mock_generate.call_count == 2
        assert not np.array_equal(emb1, emb2)

    def test_metadata_keys(self, tmp_path: Path, mock_openai_response) -> None:
        df = self._make_speakers_df()
        fake_embs = mock_openai_response(2)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in fake_embs]

        with patch("src.embeddings._get_client") as mock_client:
            mock_client.return_value.embeddings.create.return_value = mock_response
            _, metadata = embed_speakers(df, cache_dir=tmp_path)

        required_keys = {"name", "board_role", "metro_region", "company", "title", "expertise_tags", "embedding_text"}
        for entry in metadata:
            assert required_keys.issubset(entry.keys())

    def test_manifest_contains_speaker_entry(self, tmp_path: Path, mock_openai_response) -> None:
        df = self._make_speakers_df()
        fake_embs = mock_openai_response(2)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=e) for e in fake_embs]

        with patch("src.embeddings._get_client") as mock_client:
            mock_client.return_value.embeddings.create.return_value = mock_response
            embed_speakers(df, cache_dir=tmp_path)

        manifest = json.loads((tmp_path / "cache_manifest.json").read_text())
        assert "speaker_embeddings" in manifest
        assert "generated_at" in manifest["speaker_embeddings"]
        assert manifest["speaker_embeddings"]["row_count"] == 2
        assert "text_hash" in manifest["speaker_embeddings"]
