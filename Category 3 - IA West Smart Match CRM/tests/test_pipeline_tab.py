"""Tests for the pipeline funnel visualization tab."""

from unittest.mock import patch

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.ui.pipeline_tab import (
    FUNNEL_STAGES,
    aggregate_funnel_stages,
    compute_real_funnel_data,
    create_funnel_chart,
    load_pipeline_data,
    render_pipeline_tab,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_pipeline_csv(tmp_path: object) -> str:
    """Create a minimal pipeline CSV for testing."""
    csv_path = tmp_path / "pipeline_sample_data.csv"  # type: ignore[union-attr]
    csv_path.write_text(
        "event_name,speaker_name,match_score,rank,stage,stage_order\n"
        "Event A,Speaker 1,0.90,1,Attended,3\n"
        "Event A,Speaker 2,0.80,2,Contacted,1\n"
        "Event A,Speaker 3,0.70,3,Matched,0\n"
        "Event B,Speaker 1,0.85,1,Member Inquiry,4\n"
        "Event B,Speaker 2,0.75,2,Confirmed,2\n"
        "Event B,Speaker 3,0.65,3,Contacted,1\n"
    )
    return str(csv_path)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Return a small pipeline DataFrame."""
    return pd.DataFrame({
        "event_name": ["E1", "E1", "E2", "E2", "E3"],
        "speaker_name": ["S1", "S2", "S1", "S2", "S1"],
        "match_score": [0.9, 0.8, 0.7, 0.6, 0.5],
        "rank": [1, 2, 1, 2, 1],
        "stage": ["Attended", "Contacted", "Matched", "Member Inquiry", "Confirmed"],
        "stage_order": [3, 1, 0, 4, 2],
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLoadPipelineData:
    def test_load_pipeline_data_from_csv(self, sample_pipeline_csv: str) -> None:
        df = load_pipeline_data(sample_pipeline_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 6
        assert "stage" in df.columns
        assert "event_name" in df.columns

    def test_load_pipeline_data_missing_file(self, tmp_path: object) -> None:
        missing = str(tmp_path / "no_such_file.csv")  # type: ignore[union-attr]
        df = load_pipeline_data(missing)
        assert isinstance(df, pd.DataFrame)
        assert df.empty


class TestAggregateFunnelStages:
    def test_aggregate_funnel_stages_monotonically_decreasing(
        self, sample_df: pd.DataFrame
    ) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        values = list(stage_counts.values())
        for i in range(len(values) - 1):
            assert values[i] >= values[i + 1], (
                f"Funnel not monotonically decreasing at index {i}: "
                f"{values[i]} < {values[i + 1]}"
            )

    def test_funnel_stages_correct_order(self, sample_df: pd.DataFrame) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        stage_names = list(stage_counts.keys())
        expected = [
            "Discovered",
            "Matched",
            "Contacted",
            "Confirmed",
            "Attended",
            "Member Inquiry",
        ]
        assert stage_names == expected

    def test_funnel_stages_count_is_six(self, sample_df: pd.DataFrame) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        assert len(stage_counts) == 6

    def test_discovered_equals_total_rows(self, sample_df: pd.DataFrame) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        assert stage_counts["Discovered"] == len(sample_df)


class TestHoverData:
    def test_hover_data_includes_names(self, sample_df: pd.DataFrame) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        fig = create_funnel_chart(sample_df, stage_counts)
        trace = fig.data[0]
        assert trace.hovertext is not None
        hover_str = str(trace.hovertext)
        # Speaker and event names should appear in hover tooltips
        assert any(
            name in hover_str
            for name in ["S1", "S2", "E1", "E2", "E3"]
        )

    def test_create_funnel_chart_preserves_explicit_hover_text(self) -> None:
        stage_counts = FUNNEL_STAGES.copy()
        hover_text = [f"hover {idx}" for idx, _ in enumerate(stage_counts)]
        fig = create_funnel_chart(pd.DataFrame(), stage_counts, hover_texts=hover_text)
        trace = fig.data[0]
        assert list(trace.hovertext) == hover_text


class TestEmptyData:
    def test_empty_data_handled_gracefully(self) -> None:
        empty_df = pd.DataFrame(
            columns=["event_name", "speaker_name", "match_score", "rank", "stage", "stage_order"]
        )
        stage_counts = aggregate_funnel_stages(empty_df)
        assert len(stage_counts) == 6
        assert all(v == 0 for v in stage_counts.values())

    def test_empty_data_chart_returns_figure(self) -> None:
        empty_df = pd.DataFrame(
            columns=["event_name", "speaker_name", "match_score", "rank", "stage", "stage_order"]
        )
        stage_counts = aggregate_funnel_stages(empty_df)
        fig = create_funnel_chart(empty_df, stage_counts)
        assert isinstance(fig, go.Figure)


# ---------------------------------------------------------------------------
# Fixtures for real funnel data tests
# ---------------------------------------------------------------------------

@pytest.fixture
def scraped_events() -> list[dict]:
    """Sample scraped events list."""
    return [
        {"university": "UCLA", "title": "AI Symposium"},
        {"university": "USC", "title": "Tech Fair"},
        {"university": "UCLA", "title": "Hackathon"},
    ]


@pytest.fixture
def match_results_df() -> pd.DataFrame:
    """Sample match results DataFrame with event_id, speaker_id, total_score."""
    return pd.DataFrame({
        "event_id": ["E1", "E1", "E1", "E1", "E2", "E2", "E2"],
        "speaker_id": ["S1", "S2", "S3", "S4", "S1", "S2", "S3"],
        "total_score": [0.95, 0.85, 0.75, 0.60, 0.90, 0.80, 0.70],
    })


@pytest.fixture
def feedback_log_with_accepts() -> list[dict]:
    """Feedback log with some accept decisions."""
    return [
        {"decision": "accept", "event_id": "E1", "speaker_id": "S1"},
        {"decision": "accept", "event_id": "E1", "speaker_id": "S2"},
        {"decision": "decline", "event_id": "E2", "speaker_id": "S3"},
        {"decision": "accept", "event_id": "E2", "speaker_id": "S1"},
    ]


@pytest.fixture
def empty_feedback_log() -> list[dict]:
    """Empty feedback log."""
    return []


# ---------------------------------------------------------------------------
# Tests: compute_real_funnel_data
# ---------------------------------------------------------------------------


class TestComputeRealFunnelData:
    def test_compute_real_funnel_data_returns_ordered_dict(
        self,
        scraped_events: list[dict],
        match_results_df: pd.DataFrame,
        feedback_log_with_accepts: list[dict],
    ) -> None:
        result = compute_real_funnel_data(
            scraped_events=scraped_events,
            match_results=match_results_df,
            feedback_log=feedback_log_with_accepts,
            emails_generated=5,
        )
        assert isinstance(result, dict)
        assert "stages" in result
        assert "counts" in result
        assert "hover_text" in result
        expected_stages = [
            "Discovered", "Matched", "Contacted",
            "Confirmed", "Attended", "Member Inquiry",
        ]
        assert result["stages"] == expected_stages

    def test_compute_real_funnel_data_counts_match_stages(
        self,
        scraped_events: list[dict],
        match_results_df: pd.DataFrame,
        feedback_log_with_accepts: list[dict],
    ) -> None:
        result = compute_real_funnel_data(
            scraped_events=scraped_events,
            match_results=match_results_df,
            feedback_log=feedback_log_with_accepts,
            emails_generated=5,
        )
        assert len(result["counts"]) == len(result["stages"])
        assert len(result["hover_text"]) == len(result["stages"])

    def test_compute_real_funnel_data_monotonically_decreasing(
        self,
        scraped_events: list[dict],
        match_results_df: pd.DataFrame,
        feedback_log_with_accepts: list[dict],
    ) -> None:
        result = compute_real_funnel_data(
            scraped_events=scraped_events,
            match_results=match_results_df,
            feedback_log=feedback_log_with_accepts,
            emails_generated=5,
        )
        counts = result["counts"]
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i + 1], (
                f"Funnel not monotonically decreasing at index {i}: "
                f"{counts[i]} < {counts[i + 1]}"
            )

    def test_compute_real_funnel_data_empty_input(self) -> None:
        result = compute_real_funnel_data(
            scraped_events=[],
            match_results=pd.DataFrame(
                columns=["event_id", "speaker_id", "total_score"]
            ),
            feedback_log=[],
            emails_generated=0,
        )
        assert result["stages"][0] == "Discovered"
        # CPP events (15) + 0 scraped
        assert result["counts"][0] == 15
        # Matched should be 0 with no match results
        assert result["counts"][1] == 0

    def test_compute_real_funnel_data_partial_stages(
        self,
        scraped_events: list[dict],
        match_results_df: pd.DataFrame,
    ) -> None:
        """With no feedback and no emails, stages 3+ use simulation percentages."""
        result = compute_real_funnel_data(
            scraped_events=scraped_events,
            match_results=match_results_df,
            feedback_log=[],
            emails_generated=0,
        )
        matched = result["counts"][1]
        # Contacted should be 80% of matched when no emails generated
        assert result["counts"][2] == int(matched * 0.80)
        # Confirmed should be 45% of contacted when no feedback
        contacted = result["counts"][2]
        assert result["counts"][3] == int(contacted * 0.45)


# ---------------------------------------------------------------------------
# Tests: render_pipeline_tab prefers real data / falls back to CSV
# ---------------------------------------------------------------------------


_ST_PATCHES = [
    "src.ui.pipeline_tab.st.header",
    "src.ui.pipeline_tab.st.subheader",
    "src.ui.pipeline_tab.st.plotly_chart",
    "src.ui.pipeline_tab.st.dataframe",
    "src.ui.pipeline_tab.st.info",
]


class TestRenderPipelineTabDataSource:
    @patch("streamlit.session_state", new_callable=dict)
    def test_render_pipeline_tab_prefers_real_data(
        self,
        mock_state: dict,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When runtime state has match data, render_pipeline_tab uses compute_real_funnel_data."""
        import src.ui.pipeline_tab as mod

        real_called = {"count": 0}
        csv_called = {"count": 0}
        chart_hover: list[str] = []

        def fake_compute_real(
            scraped_events: list,
            match_results: pd.DataFrame,
            feedback_log: list,
            emails_generated: int,
        ) -> dict:
            real_called["count"] += 1
            return {
                "stages": list(FUNNEL_STAGES.keys()),
                "counts": [100, 80, 60, 40, 30, 5],
                "hover_text": [f"hover {idx}" for idx in range(6)],
                "annotations": [],
            }

        def fake_load_pipeline(_path: str | None = None) -> pd.DataFrame:
            csv_called["count"] += 1
            return pd.DataFrame()

        def fake_create_chart(
            df: pd.DataFrame,
            stage_counts: object,
            hover_texts: list[str] | None = None,
        ) -> go.Figure:
            chart_hover[:] = list(hover_texts or [])
            return go.Figure()

        monkeypatch.setattr(mod, "compute_real_funnel_data", fake_compute_real)
        monkeypatch.setattr(mod, "load_pipeline_data", fake_load_pipeline)
        monkeypatch.setattr(mod, "create_funnel_chart", fake_create_chart)
        monkeypatch.setattr(mod.st, "header", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "plotly_chart", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "subheader", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "dataframe", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "info", lambda *args, **kwargs: None)

        mock_state["match_results_df"] = pd.DataFrame({
            "event_id": ["E1"],
            "speaker_id": ["S1"],
            "speaker_name": ["S1"],
            "total_score": [0.9],
        })
        mock_state["scraped_events"] = [{"university": "UCLA", "title": "Test"}]
        mock_state["feedback_log"] = [{"decision": "accept"}]
        mock_state["emails_generated"] = 3
        mock_state["demo_mode"] = False

        render_pipeline_tab(None)
        assert real_called["count"] == 1
        assert csv_called["count"] == 0
        assert chart_hover == [f"hover {idx}" for idx in range(6)]

    @patch("streamlit.session_state", new_callable=dict)
    def test_render_pipeline_tab_falls_back_to_csv(
        self,
        mock_state: dict,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When datasets has no match data, render_pipeline_tab falls back to CSV."""
        import src.ui.pipeline_tab as mod

        csv_called = {"count": 0}

        def fake_load_pipeline(_path: str | None = None) -> pd.DataFrame:
            csv_called["count"] += 1
            return pd.DataFrame({
                "event_name": ["E1"],
                "speaker_name": ["S1"],
                "match_score": [0.9],
                "rank": [1],
                "stage": ["Matched"],
                "stage_order": [0],
            })

        monkeypatch.setattr(mod, "load_pipeline_data", fake_load_pipeline)
        monkeypatch.setattr(mod.st, "header", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "plotly_chart", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "subheader", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "dataframe", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "info", lambda *args, **kwargs: None)

        mock_state["demo_mode"] = False
        render_pipeline_tab(None)
        assert csv_called["count"] == 1

    @patch("streamlit.session_state", new_callable=dict)
    def test_render_pipeline_tab_uses_demo_fixture(
        self,
        mock_state: dict,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        import src.ui.pipeline_tab as mod

        chart_y: list[str] = []

        def fake_create_chart(
            df: pd.DataFrame,
            stage_counts: object,
            hover_texts: list[str] | None = None,
        ) -> go.Figure:
            chart_y[:] = list(stage_counts.keys())
            return go.Figure()

        monkeypatch.setattr(mod, "create_funnel_chart", fake_create_chart)
        monkeypatch.setattr(mod.st, "header", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "plotly_chart", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "subheader", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "dataframe", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "info", lambda *args, **kwargs: None)

        mock_state["demo_mode"] = True
        render_pipeline_tab(None)
        assert chart_y == [
            "Discovered",
            "Matched",
            "Contacted",
            "Confirmed",
            "Attended",
            "Member Inquiry",
        ]


class TestCreateFunnelChart:
    def test_create_funnel_chart_returns_figure(
        self, sample_df: pd.DataFrame
    ) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        fig = create_funnel_chart(sample_df, stage_counts)
        assert isinstance(fig, go.Figure)
        assert len(fig.data) >= 1

    def test_funnel_chart_has_correct_stage_labels(
        self, sample_df: pd.DataFrame
    ) -> None:
        stage_counts = aggregate_funnel_stages(sample_df)
        fig = create_funnel_chart(sample_df, stage_counts)
        trace = fig.data[0]
        expected_stages = list(FUNNEL_STAGES.keys())
        assert list(trace.y) == expected_stages
