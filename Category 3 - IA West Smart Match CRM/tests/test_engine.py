"""Tests for the matching engine — Sprint 1 scoring, ranking, and pipeline."""

import numpy as np
import pandas as pd
import pytest

from src.config import DEFAULT_WEIGHTS
from src.matching.engine import (
    compute_match_score,
    generate_pipeline_data,
    rank_speakers_for_course,
    rank_speakers_for_event,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_speakers_df() -> pd.DataFrame:
    """DataFrame with 3 speakers for ranking tests."""
    return pd.DataFrame(
        [
            {
                "Name": "Alice Nguyen",
                "Title": "VP of Engineering",
                "Company": "Acme Corp",
                "Board Role": "Judge",
                "Metro Region": "Los Angeles — West",
                "Expertise Tags": "AI, machine learning",
            },
            {
                "Name": "Bob Martinez",
                "Title": "CTO",
                "Company": "Beta Inc",
                "Board Role": "Speaker",
                "Metro Region": "San Francisco",
                "Expertise Tags": "cloud, DevOps",
            },
            {
                "Name": "Carol Zhang",
                "Title": "Director of Data Science",
                "Company": "Gamma LLC",
                "Board Role": "Mentor",
                "Metro Region": "Los Angeles — East",
                "Expertise Tags": "data science, analytics",
            },
        ]
    )


@pytest.fixture()
def mock_event_row() -> pd.Series:
    """Single event row for ranking tests."""
    return pd.Series(
        {
            "Event / Program": "AI Hackathon 2026",
            "Category": "AI / Hackathon",
            "Volunteer Roles (fit)": "judge; guest speaker",
            "Host / Unit": "Cal Poly Pomona",
            "Recurrence (typical)": "Annual",
        }
    )


@pytest.fixture()
def mock_calendar_df() -> pd.DataFrame:
    """IA event calendar with two rows for calendar fit tests."""
    return pd.DataFrame(
        {
            "IA Event Date": ["2026-04-10", "2026-05-15"],
            "Region": ["Los Angeles", "San Francisco"],
        }
    )


@pytest.fixture()
def mock_embeddings() -> dict[str, np.ndarray]:
    """Deterministic random embeddings keyed by speaker name."""
    rng = np.random.default_rng(99)
    dim = 64
    return {
        "Alice Nguyen": rng.standard_normal(dim).astype(np.float32),
        "Bob Martinez": rng.standard_normal(dim).astype(np.float32),
        "Carol Zhang": rng.standard_normal(dim).astype(np.float32),
    }


@pytest.fixture()
def mock_event_embedding() -> np.ndarray:
    """Deterministic event embedding."""
    rng = np.random.default_rng(42)
    return rng.standard_normal(64).astype(np.float32)


@pytest.fixture()
def mock_course_row() -> pd.Series:
    """Single course row for rank_speakers_for_course tests."""
    return pd.Series(
        {
            "Course": "CIS 4350",
            "Section": "1",
            "Title": "Advanced Machine Learning",
            "Days": "MWF",
            "Guest Lecture Fit": "High",
        }
    )


# ---------------------------------------------------------------------------
# compute_match_score
# ---------------------------------------------------------------------------


class TestComputeMatchScore:
    """Unit tests for compute_match_score."""

    def test_returns_required_keys(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        result = compute_match_score(
            speaker_embedding=np.random.randn(64).astype(np.float32),
            event_embedding=np.random.randn(64).astype(np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Cal Poly Pomona",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Alice Nguyen",
            event_category="AI / Hackathon",
        )
        assert "total_score" in result
        assert "factor_scores" in result
        assert "weighted_factor_scores" in result

    def test_total_score_equals_sum_of_weighted(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        result = compute_match_score(
            speaker_embedding=np.random.randn(64).astype(np.float32),
            event_embedding=np.random.randn(64).astype(np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge; speaker",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles",
            event_date_or_recurrence="Monthly",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="Hackathon",
        )
        expected = round(sum(result["weighted_factor_scores"].values()), 4)
        assert abs(result["total_score"] - expected) < 1e-6

    def test_factor_scores_in_unit_range(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        result = compute_match_score(
            speaker_embedding=np.random.randn(64).astype(np.float32),
            event_embedding=np.random.randn(64).astype(np.float32),
            speaker_board_role="Mentor",
            event_volunteer_roles="mentor; advisor",
            speaker_metro_region="San Francisco",
            event_region="San Francisco",
            event_date_or_recurrence="Weekly",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Jane Doe",
            event_category="Career fairs",
        )
        for factor_name, score in result["factor_scores"].items():
            assert 0.0 <= score <= 1.0, (
                f"Factor {factor_name!r} out of [0, 1]: {score}"
            )

    def test_default_weights_produce_nonzero_total(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        result = compute_match_score(
            speaker_embedding=np.ones(64, dtype=np.float32),
            event_embedding=np.ones(64, dtype=np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles — West",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="AI / Hackathon",
        )
        assert result["total_score"] > 0.0

    def test_custom_weights_override_defaults(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        custom_weights = {
            "topic_relevance": 1.0,
            "role_fit": 0.0,
            "geographic_proximity": 0.0,
            "calendar_fit": 0.0,
            "historical_conversion": 0.0,
            "student_interest": 0.0,
        }
        result = compute_match_score(
            speaker_embedding=np.ones(64, dtype=np.float32),
            event_embedding=np.ones(64, dtype=np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles — West",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="AI / Hackathon",
            weights=custom_weights,
        )
        # Only topic_relevance should contribute
        assert result["weighted_factor_scores"]["role_fit"] == 0.0
        assert result["weighted_factor_scores"]["geographic_proximity"] == 0.0
        assert result["total_score"] == result["weighted_factor_scores"]["topic_relevance"]

    def test_empty_embeddings_give_zero_topic_relevance(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        result = compute_match_score(
            speaker_embedding=np.array([]),
            event_embedding=np.array([]),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles — West",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="AI / Hackathon",
        )
        assert result["factor_scores"]["topic_relevance"] == 0.0

    def test_weight_normalization(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        """Weights that do not sum to 1.0 should be normalized before scoring."""
        heavy_weights = {
            "topic_relevance": 3.0,
            "role_fit": 2.5,
            "geographic_proximity": 2.0,
            "calendar_fit": 1.5,
            "historical_conversion": 0.5,
            "student_interest": 0.5,
        }
        result = compute_match_score(
            speaker_embedding=np.ones(64, dtype=np.float32),
            event_embedding=np.ones(64, dtype=np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles — West",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="AI / Hackathon",
            weights=heavy_weights,
        )
        # total_score should be <= 1.0 after normalization
        assert result["total_score"] <= 1.0 + 1e-6

    def test_all_zero_weights_give_zero_total(
        self,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        zero_weights = {
            "topic_relevance": 0.0,
            "role_fit": 0.0,
            "geographic_proximity": 0.0,
            "calendar_fit": 0.0,
            "historical_conversion": 0.0,
            "student_interest": 0.0,
        }
        result = compute_match_score(
            speaker_embedding=np.ones(64, dtype=np.float32),
            event_embedding=np.ones(64, dtype=np.float32),
            speaker_board_role="Judge",
            event_volunteer_roles="judge",
            speaker_metro_region="Los Angeles — West",
            event_region="Los Angeles — West",
            event_date_or_recurrence="Annual",
            ia_event_calendar=mock_calendar_df,
            speaker_name="Test Speaker",
            event_category="AI / Hackathon",
            weights=zero_weights,
        )
        assert result["total_score"] == 0.0


# ---------------------------------------------------------------------------
# rank_speakers_for_event
# ---------------------------------------------------------------------------


class TestRankSpeakersForEvent:
    """Unit tests for rank_speakers_for_event."""

    def test_returns_list_sorted_descending(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            event_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        scores = [r["total_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_result_dict_has_required_keys(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            event_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        required_keys = {
            "rank",
            "speaker_name",
            "speaker_title",
            "speaker_company",
            "event_name",
            "total_score",
            "factor_scores",
            "weighted_factor_scores",
        }
        for entry in results:
            assert required_keys.issubset(entry.keys())

    def test_rank_numbering_sequential(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            event_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        ranks = [r["rank"] for r in results]
        assert ranks == list(range(1, len(results) + 1))

    def test_top_n_limits_results(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            event_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
            top_n=2,
        )
        assert len(results) == 2

    def test_empty_embeddings_handled(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
    ) -> None:
        """Empty embedding dict should not raise; topic_relevance will be 0."""
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings={},
            event_embedding=np.array([]),
            ia_event_calendar=mock_calendar_df,
        )
        assert len(results) == len(mock_speakers_df)
        for entry in results:
            assert entry["factor_scores"]["topic_relevance"] == 0.0

    def test_stable_sort_alphabetical_tiebreaker(self) -> None:
        """Speakers with identical scores should be ordered alphabetically."""
        speakers = pd.DataFrame(
            [
                {
                    "Name": "Zara Adams",
                    "Title": "CTO",
                    "Company": "Co",
                    "Board Role": "",
                    "Metro Region": "",
                    "Expertise Tags": "",
                },
                {
                    "Name": "Alice Adams",
                    "Title": "CTO",
                    "Company": "Co",
                    "Board Role": "",
                    "Metro Region": "",
                    "Expertise Tags": "",
                },
            ]
        )
        event = pd.Series(
            {
                "Event / Program": "Test Event",
                "Category": "",
                "Volunteer Roles (fit)": "",
                "Host / Unit": "",
                "Recurrence (typical)": "",
            }
        )
        results = rank_speakers_for_event(
            event_row=event,
            speakers_df=speakers,
            speaker_embeddings={},
            event_embedding=np.array([]),
            ia_event_calendar=pd.DataFrame(),
        )
        names = [r["speaker_name"] for r in results]
        # Same total_score → alphabetical order
        assert names == sorted(names)

    def test_event_name_propagated(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_event_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_event(
            event_row=mock_event_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            event_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        for entry in results:
            assert entry["event_name"] == "AI Hackathon 2026"


# ---------------------------------------------------------------------------
# rank_speakers_for_course
# ---------------------------------------------------------------------------


class TestRankSpeakersForCourse:
    """Unit tests for rank_speakers_for_course."""

    def test_returns_ranked_list(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_course_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_course(
            course_row=mock_course_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        assert isinstance(results, list)
        assert len(results) == len(mock_speakers_df)

    def test_event_name_from_course(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_course_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_course(
            course_row=mock_course_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        expected_name = "CIS 4350-01: Advanced Machine Learning"
        for entry in results:
            assert entry["event_name"] == expected_name

    def test_student_interest_override_high(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_course_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        """Guest Lecture Fit = High should override student_interest to 0.9."""
        results = rank_speakers_for_course(
            course_row=mock_course_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        for entry in results:
            assert entry["factor_scores"]["student_interest"] == 0.9
            assert entry["weighted_factor_scores"]["student_interest"] == pytest.approx(
                round(0.9 * DEFAULT_WEIGHTS["student_interest"], 4),
                abs=1e-6,
            )
            assert entry["total_score"] == pytest.approx(
                round(sum(entry["weighted_factor_scores"].values()), 4),
                abs=1e-6,
            )

    def test_student_interest_override_medium(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        course = pd.Series(
            {
                "Course": "MKT 3010",
                "Title": "Marketing Principles",
                "Days": "TTh",
                "Guest Lecture Fit": "Medium",
            }
        )
        results = rank_speakers_for_course(
            course_row=course,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        for entry in results:
            assert entry["factor_scores"]["student_interest"] == 0.6

    def test_student_interest_override_low(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        course = pd.Series(
            {
                "Course": "ENG 1010",
                "Title": "Technical Writing",
                "Days": "MWF",
                "Guest Lecture Fit": "Low",
            }
        )
        results = rank_speakers_for_course(
            course_row=course,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
        )
        for entry in results:
            assert entry["factor_scores"]["student_interest"] == 0.3

    def test_student_interest_override_recomputes_weighted_scores(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_course_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        """Course overrides must update weighted scores and total_score together."""
        custom_weights = {
            "topic_relevance": 0.10,
            "role_fit": 0.10,
            "geographic_proximity": 0.10,
            "calendar_fit": 0.10,
            "historical_conversion": 0.10,
            "student_interest": 0.50,
        }
        results = rank_speakers_for_course(
            course_row=mock_course_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
            weights=custom_weights,
        )

        for entry in results:
            assert entry["weighted_factor_scores"]["student_interest"] == pytest.approx(0.45, abs=1e-6)
            assert entry["total_score"] == pytest.approx(
                round(sum(entry["weighted_factor_scores"].values()), 4),
                abs=1e-6,
            )

    def test_top_n_limits_course_results(
        self,
        mock_speakers_df: pd.DataFrame,
        mock_course_row: pd.Series,
        mock_calendar_df: pd.DataFrame,
        mock_embeddings: dict[str, np.ndarray],
        mock_event_embedding: np.ndarray,
    ) -> None:
        results = rank_speakers_for_course(
            course_row=mock_course_row,
            speakers_df=mock_speakers_df,
            speaker_embeddings=mock_embeddings,
            course_embedding=mock_event_embedding,
            ia_event_calendar=mock_calendar_df,
            top_n=1,
        )
        assert len(results) == 1


# ---------------------------------------------------------------------------
# generate_pipeline_data
# ---------------------------------------------------------------------------


class TestGeneratePipelineData:
    """Unit tests for generate_pipeline_data."""

    _EXPECTED_COLUMNS = [
        "event_name",
        "speaker_name",
        "match_score",
        "rank",
        "stage",
        "stage_order",
    ]

    _VALID_STAGES = {
        "Matched",
        "Contacted",
        "Confirmed",
        "Attended",
        "Member Inquiry",
    }

    def test_empty_input_returns_empty_df(self) -> None:
        df = generate_pipeline_data([], seed=42)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == self._EXPECTED_COLUMNS
        assert len(df) == 0

    def test_columns_present(self) -> None:
        ranked = [
            {
                "event_name": "Hackathon",
                "speaker_name": "Alice",
                "total_score": 0.85,
                "rank": 1,
            }
        ]
        df = generate_pipeline_data(ranked, seed=42)
        assert list(df.columns) == self._EXPECTED_COLUMNS

    def test_reproducibility_with_same_seed(self) -> None:
        ranked = [
            {
                "event_name": "Event",
                "speaker_name": f"Speaker {i}",
                "total_score": 0.9 - i * 0.1,
                "rank": i + 1,
            }
            for i in range(20)
        ]
        df1 = generate_pipeline_data(ranked, seed=42)
        df2 = generate_pipeline_data(ranked, seed=42)
        pd.testing.assert_frame_equal(df1, df2)

    def test_different_seed_may_differ(self) -> None:
        ranked = [
            {
                "event_name": "Event",
                "speaker_name": f"Speaker {i}",
                "total_score": 0.9 - i * 0.01,
                "rank": i + 1,
            }
            for i in range(50)
        ]
        df1 = generate_pipeline_data(ranked, seed=42)
        df2 = generate_pipeline_data(ranked, seed=999)
        # With 50 entries, different seeds should very likely produce
        # different stage assignments
        assert not df1["stage"].equals(df2["stage"])

    def test_all_stages_valid(self) -> None:
        ranked = [
            {
                "event_name": "Event",
                "speaker_name": f"Speaker {i}",
                "total_score": 0.8,
                "rank": i + 1,
            }
            for i in range(100)
        ]
        df = generate_pipeline_data(ranked, seed=42)
        assert set(df["stage"].unique()).issubset(self._VALID_STAGES)

    def test_stage_order_values_valid(self) -> None:
        ranked = [
            {
                "event_name": "Event",
                "speaker_name": f"Speaker {i}",
                "total_score": 0.7,
                "rank": i + 1,
            }
            for i in range(50)
        ]
        df = generate_pipeline_data(ranked, seed=42)
        assert df["stage_order"].min() >= 0
        assert df["stage_order"].max() <= 4

    def test_stage_order_matches_stage_label(self) -> None:
        label_to_order = {
            "Matched": 0,
            "Contacted": 1,
            "Confirmed": 2,
            "Attended": 3,
            "Member Inquiry": 4,
        }
        ranked = [
            {
                "event_name": "Event",
                "speaker_name": f"Speaker {i}",
                "total_score": 0.6,
                "rank": i + 1,
            }
            for i in range(80)
        ]
        df = generate_pipeline_data(ranked, seed=42)
        for _, row in df.iterrows():
            assert row["stage_order"] == label_to_order[row["stage"]]

    def test_match_score_propagated(self) -> None:
        ranked = [
            {
                "event_name": "E",
                "speaker_name": "S",
                "total_score": 0.7777,
                "rank": 1,
            }
        ]
        df = generate_pipeline_data(ranked, seed=42)
        assert df.iloc[0]["match_score"] == 0.7777

    def test_row_count_equals_input_length(self) -> None:
        n = 15
        ranked = [
            {
                "event_name": "E",
                "speaker_name": f"S{i}",
                "total_score": 0.5,
                "rank": i + 1,
            }
            for i in range(n)
        ]
        df = generate_pipeline_data(ranked, seed=42)
        assert len(df) == n
