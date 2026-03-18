"""Tests for cosine similarity validation — Sprint 0 Go/No-Go gate."""

import numpy as np
import pytest

from src.similarity import (
    cosine_similarity_matrix,
    cosine_similarity_pair,
    get_top_k_matches,
    keyword_overlap_score,
    validate_similarity_scores,
)


class TestCosineSimilarityMatrix:
    """Unit tests for the cosine_similarity_matrix function."""

    def test_identical_vectors_return_1(self) -> None:
        a = np.random.randn(3, 128).astype(np.float32)
        sim = cosine_similarity_matrix(a, a)
        np.testing.assert_allclose(np.diag(sim), 1.0, atol=1e-5)

    def test_orthogonal_vectors_return_0(self) -> None:
        a = np.array([[1, 0, 0]], dtype=np.float32)
        b = np.array([[0, 1, 0]], dtype=np.float32)
        sim = cosine_similarity_matrix(a, b)
        assert abs(sim[0, 0]) < 1e-5

    def test_output_shape(self) -> None:
        a = np.random.randn(18, 1536).astype(np.float32)
        b = np.random.randn(15, 1536).astype(np.float32)
        sim = cosine_similarity_matrix(a, b)
        assert sim.shape == (18, 15)

    def test_dimension_mismatch_raises(self) -> None:
        a = np.random.randn(5, 128).astype(np.float32)
        b = np.random.randn(3, 256).astype(np.float32)
        with pytest.raises(ValueError, match="dimensions don't match"):
            cosine_similarity_matrix(a, b)

    def test_values_in_valid_range(self) -> None:
        a = np.random.randn(10, 64).astype(np.float32)
        b = np.random.randn(8, 64).astype(np.float32)
        sim = cosine_similarity_matrix(a, b)
        assert np.all(sim >= -1.0 - 1e-5)
        assert np.all(sim <= 1.0 + 1e-5)

    def test_zero_vector_handled(self) -> None:
        a = np.array([[0, 0, 0]], dtype=np.float32)
        b = np.array([[1, 0, 0]], dtype=np.float32)
        # Should not raise — zero norm clamped to 1e-10
        sim = cosine_similarity_matrix(a, b)
        assert sim.shape == (1, 1)


class TestCosineSimilarityPair:
    def test_same_vector_is_1(self) -> None:
        v = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        assert abs(cosine_similarity_pair(v, v) - 1.0) < 1e-5

    def test_zero_vector_returns_0(self) -> None:
        a = np.zeros(5, dtype=np.float32)
        b = np.ones(5, dtype=np.float32)
        assert cosine_similarity_pair(a, b) == 0.0

    def test_returns_float(self) -> None:
        a = np.random.randn(64).astype(np.float32)
        b = np.random.randn(64).astype(np.float32)
        result = cosine_similarity_pair(a, b)
        assert isinstance(result, float)


class TestGetTopKMatches:
    """Unit tests for the top-k matching function."""

    def test_returns_correct_k(self) -> None:
        sim = np.random.randn(10, 5).astype(np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(10)]
        target_meta = [{"event_name": f"e{i}"} for i in range(5)]
        results = get_top_k_matches(sim, source_meta, target_meta, k=3)
        assert len(results) == 5
        for r in results:
            assert len(r["matches"]) == 3

    def test_matches_sorted_descending(self) -> None:
        sim = np.random.randn(10, 3).astype(np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(10)]
        target_meta = [{"event_name": f"e{i}"} for i in range(3)]
        results = get_top_k_matches(sim, source_meta, target_meta, k=5)
        for r in results:
            scores = [m["score"] for m in r["matches"]]
            assert scores == sorted(scores, reverse=True)

    def test_k_capped_at_n_sources(self) -> None:
        sim = np.random.randn(3, 2).astype(np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(3)]
        target_meta = [{"event_name": f"e{i}"} for i in range(2)]
        results = get_top_k_matches(sim, source_meta, target_meta, k=100)
        for r in results:
            assert len(r["matches"]) == 3

    def test_result_structure(self) -> None:
        sim = np.array([[0.9, 0.3], [0.2, 0.8]], dtype=np.float32)
        source_meta = [{"name": "s0"}, {"name": "s1"}]
        target_meta = [{"event_name": "e0"}, {"event_name": "e1"}]
        results = get_top_k_matches(sim, source_meta, target_meta, k=1)
        assert "target" in results[0]
        assert "matches" in results[0]
        match = results[0]["matches"][0]
        assert "source" in match
        assert "score" in match
        assert "rank" in match
        assert match["rank"] == 1


class TestValidateSimilarityScores:
    """Tests for the Go/No-Go gate validation."""

    def test_high_spread_passes(self) -> None:
        sim = np.array([
            [0.95, 0.30],
            [0.20, 0.90],
            [0.50, 0.50],
        ], dtype=np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(3)]
        target_meta = [{"event_name": "e0"}, {"event_name": "e1"}]
        result = validate_similarity_scores(sim, source_meta, target_meta, min_spread=0.15)
        assert result["passed"] is True

    def test_flat_scores_fail(self) -> None:
        rng = np.random.default_rng(42)
        sim = np.full((5, 3), 0.75, dtype=np.float32)
        sim += rng.standard_normal((5, 3)).astype(np.float32) * 0.01
        source_meta = [{"name": f"s{i}"} for i in range(5)]
        target_meta = [{"event_name": f"e{i}"} for i in range(3)]
        result = validate_similarity_scores(sim, source_meta, target_meta, min_spread=0.15)
        assert result["passed"] is False

    def test_result_has_required_keys(self) -> None:
        sim = np.random.randn(5, 3).astype(np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(5)]
        target_meta = [{"event_name": f"e{i}"} for i in range(3)]
        result = validate_similarity_scores(sim, source_meta, target_meta)
        required = {"passed", "overall_max", "overall_min", "overall_spread",
                    "per_target_spreads", "targets_passing", "targets_total", "message"}
        assert required.issubset(result.keys())

    def test_message_contains_pass_or_fail(self) -> None:
        sim = np.random.randn(5, 3).astype(np.float32)
        source_meta = [{"name": f"s{i}"} for i in range(5)]
        target_meta = [{"event_name": f"e{i}"} for i in range(3)]
        result = validate_similarity_scores(sim, source_meta, target_meta)
        assert "PASS" in result["message"] or "FAIL" in result["message"]


class TestKeywordOverlap:
    """Tests for the keyword overlap baseline."""

    def test_perfect_overlap(self) -> None:
        score = keyword_overlap_score("AI, innovation", "AI innovation hackathon")
        assert score > 0.0

    def test_no_overlap(self) -> None:
        score = keyword_overlap_score("cooking, baking", "quantum physics research")
        assert score == 0.0

    def test_empty_input_tags(self) -> None:
        assert keyword_overlap_score("", "some text") == 0.0

    def test_empty_event_text(self) -> None:
        assert keyword_overlap_score("tags", "") == 0.0

    def test_returns_float_in_range(self) -> None:
        score = keyword_overlap_score("data collection, analytics, AI", "data analytics research hackathon")
        assert 0.0 <= score <= 1.0

    def test_short_words_excluded(self) -> None:
        # "AI" is 2 chars, should be excluded (len > 2 filter)
        score = keyword_overlap_score("AI", "AI")
        assert score == 0.0
