"""Tests for Volunteer Dashboard (A3.3)."""

import pandas as pd
import plotly.graph_objects as go
import pytest


@pytest.fixture
def match_results() -> pd.DataFrame:
    """Sample match results with multiple speakers and events."""
    return pd.DataFrame([
        {"event_id": "E1", "speaker_id": "Alice", "total_score": 0.95,
         "topic_relevance": 0.9, "role_fit": 0.8, "geographic_proximity": 0.7,
         "calendar_fit": 0.6, "historical_conversion": 0.5, "student_interest": 0.4},
        {"event_id": "E2", "speaker_id": "Alice", "total_score": 0.85,
         "topic_relevance": 0.8, "role_fit": 0.7, "geographic_proximity": 0.6,
         "calendar_fit": 0.5, "historical_conversion": 0.4, "student_interest": 0.3},
        {"event_id": "E3", "speaker_id": "Alice", "total_score": 0.75,
         "topic_relevance": 0.7, "role_fit": 0.6, "geographic_proximity": 0.5,
         "calendar_fit": 0.4, "historical_conversion": 0.3, "student_interest": 0.2},
        {"event_id": "E1", "speaker_id": "Bob", "total_score": 0.90,
         "topic_relevance": 0.85, "role_fit": 0.75, "geographic_proximity": 0.65,
         "calendar_fit": 0.55, "historical_conversion": 0.45, "student_interest": 0.35},
        {"event_id": "E2", "speaker_id": "Bob", "total_score": 0.70,
         "topic_relevance": 0.65, "role_fit": 0.55, "geographic_proximity": 0.45,
         "calendar_fit": 0.35, "historical_conversion": 0.25, "student_interest": 0.15},
        {"event_id": "E4", "speaker_id": "Alice", "total_score": 0.60,
         "topic_relevance": 0.5, "role_fit": 0.4, "geographic_proximity": 0.3,
         "calendar_fit": 0.2, "historical_conversion": 0.1, "student_interest": 0.05},
        {"event_id": "E5", "speaker_id": "Alice", "total_score": 0.50,
         "topic_relevance": 0.4, "role_fit": 0.3, "geographic_proximity": 0.2,
         "calendar_fit": 0.1, "historical_conversion": 0.05, "student_interest": 0.02},
        {"event_id": "E6", "speaker_id": "Alice", "total_score": 0.40,
         "topic_relevance": 0.3, "role_fit": 0.2, "geographic_proximity": 0.1,
         "calendar_fit": 0.05, "historical_conversion": 0.02, "student_interest": 0.01},
    ])


class TestComputeSpeakerMatches:
    def test_filters_by_name(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_speaker_matches

        result = compute_speaker_matches("Alice", match_results)
        assert all(result["speaker_id"] == "Alice")
        assert "Bob" not in result["speaker_id"].values

    def test_returns_top_n(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_speaker_matches

        result = compute_speaker_matches("Alice", match_results, top_n=3)
        assert len(result) == 3

    def test_sorted_descending(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_speaker_matches

        result = compute_speaker_matches("Alice", match_results, top_n=5)
        scores = result["total_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_empty_results(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_speaker_matches

        result = compute_speaker_matches("NonExistent", match_results)
        assert result.empty


class TestComputeUtilizationMetrics:
    def test_basic(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_utilization_metrics

        metrics = compute_utilization_metrics(
            "Alice", match_results, total_events=6, feedback_log=[]
        )
        assert metrics["events_available"] == 6
        assert metrics["events_matched"] > 0
        assert isinstance(metrics["utilization_rate"], float)
        assert 0.0 <= metrics["utilization_rate"] <= 1.0
        assert isinstance(metrics["avg_match_score"], float)

    def test_with_feedback(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_utilization_metrics

        feedback_log = [
            {"speaker_id": "Alice", "decision": "accept"},
            {"speaker_id": "Alice", "decision": "accept"},
            {"speaker_id": "Alice", "decision": "decline"},
        ]
        metrics = compute_utilization_metrics(
            "Alice", match_results, total_events=6, feedback_log=feedback_log
        )
        # With feedback, accepted should come from feedback log (2 accepts)
        assert metrics["events_accepted"] == 2

    def test_zero_events(self, match_results: pd.DataFrame) -> None:
        from src.ui.volunteer_dashboard import compute_utilization_metrics

        metrics = compute_utilization_metrics(
            "Alice", match_results, total_events=0, feedback_log=[]
        )
        assert metrics["events_available"] == 0
        assert metrics["utilization_rate"] == 0.0


class TestRenderUtilizationBarChart:
    def test_returns_figure(self) -> None:
        from src.ui.volunteer_dashboard import render_utilization_bar_chart

        metrics = {
            "events_matched": 4,
            "events_accepted": 2,
            "events_attended": 1,
        }
        fig = render_utilization_bar_chart(metrics, "Alice")
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == "bar"
        assert list(fig.data[0].x) == ["Matched", "Accepted", "Attended"]
        assert list(fig.data[0].y) == [4, 2, 1]


class TestConversionRates:
    def test_values(self) -> None:
        from src.ui.volunteer_dashboard import CONVERSION_RATES

        assert CONVERSION_RATES["matched"] == 1.00
        assert CONVERSION_RATES["accepted"] == 0.60
        assert CONVERSION_RATES["attended"] == 0.75


class TestRenderVolunteerDashboardIntegration:
    def test_integration(self, match_results: pd.DataFrame) -> None:
        """Smoke test: render_volunteer_dashboard is importable and callable."""
        from src.ui.volunteer_dashboard import render_volunteer_dashboard

        assert callable(render_volunteer_dashboard)
