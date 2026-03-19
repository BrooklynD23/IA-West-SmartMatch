"""Tests for LLM-powered match explanation generation."""

import json
from pathlib import Path
from unittest.mock import patch

from src.matching.explanations import (
    _cache_key,
    _fallback_explanation,
    fallback_match_explanation,
    generate_match_explanation,
    load_cached_explanation,
    save_cached_explanation,
)


def _make_match_result(total_score: float = 0.85) -> dict:
    """Return a canonical match result used across explanation tests."""
    factor_scores = {
        "topic_relevance": 0.90,
        "role_fit": 0.80,
        "geographic_proximity": 0.75,
        "calendar_fit": 0.70,
        "historical_conversion": 0.50,
        "student_interest": 0.60,
    }
    return {
        "speaker_name": "Test Speaker",
        "speaker_title": "VP Research",
        "speaker_company": "TestCorp",
        "speaker_board_role": "Director",
        "speaker_metro_region": "Los Angeles — East",
        "speaker_expertise_tags": "AI, analytics",
        "event_name": "Test Event",
        "total_score": total_score,
        "factor_scores": factor_scores,
        "weighted_factor_scores": {
            factor: round(score * 0.20, 4)
            for factor, score in factor_scores.items()
        },
    }


class TestCacheKey:
    """Unit tests for deterministic explanation cache keys."""

    def test_same_inputs_produce_same_key(self) -> None:
        match_result = _make_match_result()
        assert _cache_key(match_result) == _cache_key(match_result)

    def test_score_only_changes_do_not_invalidate_cache_key(self) -> None:
        assert _cache_key(_make_match_result(0.85)) == _cache_key(_make_match_result(0.42))

    def test_factor_changes_produce_different_keys(self) -> None:
        first = _make_match_result()
        second = _make_match_result()
        second["factor_scores"]["student_interest"] = 0.90

        assert _cache_key(first) != _cache_key(second)

    def test_raw_name_collisions_hash_separately(self) -> None:
        slash_name = _make_match_result()
        space_name = _make_match_result()
        slash_name["speaker_name"] = "A/B"
        space_name["speaker_name"] = "A B"

        assert _cache_key(slash_name) != _cache_key(space_name)


class TestCachePersistence:
    """Disk cache tests for explanation persistence."""

    def test_round_trip_save_then_load(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)):
            save_cached_explanation(match_result, "Cached explanation.")
            loaded = load_cached_explanation(match_result)

        assert loaded == "Cached explanation."

    def test_reuses_cache_when_only_total_score_changes(self, tmp_path: Path) -> None:
        original = _make_match_result(0.85)
        reranked = _make_match_result(0.35)

        with patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)):
            save_cached_explanation(original, "Stable cached explanation.")
            loaded = load_cached_explanation(reranked)

        assert loaded == "Stable cached explanation."

    def test_malformed_json_returns_none(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)):
            key = _cache_key(match_result)
            (tmp_path / f"{key}.json").write_text("{bad json", encoding="utf-8")

            assert load_cached_explanation(match_result) is None

    def test_missing_explanation_field_returns_none(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)):
            key = _cache_key(match_result)
            (tmp_path / f"{key}.json").write_text(json.dumps({"other": "value"}), encoding="utf-8")

            assert load_cached_explanation(match_result) is None


class TestFallbackExplanation:
    """Fallback explanation behavior."""

    def test_contains_speaker_and_event(self) -> None:
        result = _fallback_explanation(_make_match_result())
        assert "Test Speaker" in result
        assert "Test Event" in result

    def test_contains_top_factor_labels(self) -> None:
        result = _fallback_explanation(_make_match_result())
        assert "topic alignment" in result
        assert "role compatibility" in result

    def test_does_not_raise_on_partial_match_payload(self) -> None:
        partial_result = {"speaker_name": "Partial Speaker"}
        result = fallback_match_explanation(partial_result)

        assert "Partial Speaker" in result
        assert "Unknown event" in result


class TestGenerateMatchExplanation:
    """Main generation-path tests."""

    def test_cache_hit_returns_cached_value(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)):
            save_cached_explanation(match_result, "Cached explanation.")

            with patch("src.matching.explanations.generate_text") as mock_generate_text:
                result = generate_match_explanation(match_result, use_cache=True)

        assert result == "Cached explanation."
        mock_generate_text.assert_not_called()

    def test_use_cache_false_bypasses_cache(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with (
            patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)),
            patch("src.matching.explanations.generate_text") as mock_generate_text,
        ):
            save_cached_explanation(match_result, "Cached explanation.")

            mock_generate_text.return_value = "Fresh API explanation."

            result = generate_match_explanation(match_result, use_cache=False)

        assert result == "Fresh API explanation."

    def test_api_error_returns_fallback_for_partial_payload(self, tmp_path: Path) -> None:
        partial_result = {"speaker_name": "Partial Speaker"}
        with (
            patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)),
            patch("src.matching.explanations.generate_text") as mock_generate_text,
        ):
            mock_generate_text.side_effect = RuntimeError("API unreachable")
            result = generate_match_explanation(partial_result, use_cache=False)

        assert "Partial Speaker" in result
        assert "Unknown event" in result

    def test_api_success_saves_to_cache(self, tmp_path: Path) -> None:
        match_result = _make_match_result()
        with (
            patch("src.matching.explanations.EXPLANATION_CACHE_DIR", str(tmp_path)),
            patch("src.matching.explanations.generate_text") as mock_generate_text,
        ):
            mock_generate_text.return_value = "LLM explanation to cache."

            generate_match_explanation(match_result, use_cache=True)
            cached = load_cached_explanation(match_result)

        assert cached == "LLM explanation to cache."
