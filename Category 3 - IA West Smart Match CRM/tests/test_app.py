"""Tests for app-level embedding cache bootstrap behavior."""

from contextlib import ExitStack, contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from src.app import _resolve_embedding_lookup_dicts
from src.app import _empty_dataset_issues


@contextmanager
def _noop_context():
    yield


def _sample_datasets() -> SimpleNamespace:
    return SimpleNamespace(
        speakers=pd.DataFrame([{"Name": "Alice"}]),
        events=pd.DataFrame([{"Event / Program": "AI Hackathon"}]),
        courses=pd.DataFrame([{"Course": "BUS 101", "Section": "01"}]),
        calendar=pd.DataFrame([{"Event Name": "Annual Conference"}]),
        quality_results=[SimpleNamespace(issues=[])],
    )


class TestResolveEmbeddingLookupDicts:
    def test_bootstraps_missing_cache_when_gemini_key_is_available(self) -> None:
        datasets = SimpleNamespace(speakers=object(), events=object(), courses=object())
        generated_speakers = {"Alice": np.array([1.0], dtype=np.float32)}
        generated_events = {"AI Hackathon": np.array([2.0], dtype=np.float32)}
        generated_courses = {"BUS 101-01": np.array([3.0], dtype=np.float32)}

        with (
            patch("src.app.load_embedding_lookup_dicts", return_value=({}, {}, {})),
            patch("src.app.has_gemini_api_key", return_value=True),
            patch(
                "src.app.generate_embedding_lookup_dicts",
                return_value=(generated_speakers, generated_events, generated_courses),
            ) as mock_generate,
            patch("src.app._embedding_cache_issues", side_effect=[["missing cache"], []]),
        ):
            speakers, events, courses, issues, bootstrap_error, cache_generated = _resolve_embedding_lookup_dicts(
                datasets
            )

        mock_generate.assert_called_once_with(
            speakers_df=datasets.speakers,
            events_df=datasets.events,
            courses_df=datasets.courses,
        )
        assert list(speakers) == ["Alice"]
        assert list(events) == ["AI Hackathon"]
        assert list(courses) == ["BUS 101-01"]
        assert np.array_equal(speakers["Alice"], generated_speakers["Alice"])
        assert issues == []
        assert bootstrap_error is None
        assert cache_generated is True

    def test_skips_bootstrap_without_gemini_key(self) -> None:
        datasets = SimpleNamespace(speakers=object(), events=object(), courses=object())

        with (
            patch("src.app.load_embedding_lookup_dicts", return_value=({}, {}, {})),
            patch("src.app.has_gemini_api_key", return_value=False),
            patch("src.app.generate_embedding_lookup_dicts") as mock_generate,
            patch("src.app._embedding_cache_issues", return_value=["missing cache"]),
        ):
            _, _, _, issues, bootstrap_error, cache_generated = _resolve_embedding_lookup_dicts(datasets)

        mock_generate.assert_not_called()
        assert issues == ["missing cache"]
        assert bootstrap_error is None
        assert cache_generated is False

    @patch("streamlit.session_state", new_callable=dict)
    def test_skips_bootstrap_in_demo_mode_even_with_gemini_key(self, mock_state: dict) -> None:
        datasets = SimpleNamespace(speakers=object(), events=object(), courses=object())
        mock_state["demo_mode"] = True

        with (
            patch("src.app.load_embedding_lookup_dicts", return_value=({}, {}, {})),
            patch("src.app.has_gemini_api_key", return_value=True),
            patch("src.app.generate_embedding_lookup_dicts") as mock_generate,
            patch("src.app._embedding_cache_issues", return_value=["missing cache"]),
        ):
            _, _, _, issues, bootstrap_error, cache_generated = _resolve_embedding_lookup_dicts(datasets)

        mock_generate.assert_not_called()
        assert issues == ["missing cache"]
        assert bootstrap_error is None
        assert cache_generated is False


class TestMainMatchesAvailability:
    def _run_main(
        self,
        *,
        demo_mode: bool,
        has_gemini_key: bool,
        embedding_issues: list[str],
    ) -> tuple[MagicMock, MagicMock, MagicMock]:
        import src.app as app

        warning_mock = MagicMock()
        error_mock = MagicMock()
        render_matches_mock = MagicMock()

        with ExitStack() as stack:
            stack.enter_context(patch("streamlit.session_state", new={"demo_mode": demo_mode, "current_view": "crm"}))
            stack.enter_context(patch("src.app.init_runtime_state"))
            stack.enter_context(patch("src.app.validate_config", return_value=[]))
            stack.enter_context(patch("src.app.render_sidebar", return_value=_noop_context()))
            stack.enter_context(patch("src.app.load_all", return_value=_sample_datasets()))
            stack.enter_context(patch("src.app._resolve_embedding_lookup_dicts", return_value=({}, {}, {}, embedding_issues, None, False)))
            stack.enter_context(patch("src.app.has_gemini_api_key", return_value=has_gemini_key))
            stack.enter_context(patch("src.app.render_command_center_tab"))
            stack.enter_context(patch("src.app.render_matches_tab_ui", render_matches_mock))
            stack.enter_context(patch("src.app.render_discovery_tab"))
            stack.enter_context(patch("src.app.render_pipeline_tab"))
            stack.enter_context(patch("src.app.render_expansion_map", return_value=object()))
            stack.enter_context(patch("src.app.render_volunteer_dashboard"))
            stack.enter_context(patch("src.feedback.acceptance.init_feedback_state"))
            stack.enter_context(patch("src.app.render_feedback_sidebar"))
            stack.enter_context(patch("src.app.get_match_results_df", return_value=pd.DataFrame()))
            stack.enter_context(patch.object(app.st, "tabs", return_value=tuple(_noop_context() for _ in range(6))))
            stack.enter_context(patch.object(app.st, "expander", side_effect=lambda *args, **kwargs: _noop_context()))
            stack.enter_context(patch.object(app.st, "slider", return_value=0.30))
            stack.enter_context(patch.object(app.st, "warning", new=warning_mock))
            stack.enter_context(patch.object(app.st, "error", new=error_mock))
            app.main()

        return render_matches_mock, warning_mock, error_mock

    def test_main_renders_matches_when_demo_mode_is_enabled(self) -> None:
        render_matches_mock, warning_mock, error_mock = self._run_main(
            demo_mode=True,
            has_gemini_key=True,
            embedding_issues=["Missing cache files: speaker_embeddings.npy."],
        )

        render_matches_mock.assert_called_once()
        warning_mock.assert_called()
        error_mock.assert_not_called()

    def test_main_renders_matches_when_gemini_key_is_unavailable(self) -> None:
        render_matches_mock, warning_mock, error_mock = self._run_main(
            demo_mode=False,
            has_gemini_key=False,
            embedding_issues=["Missing cache files: speaker_embeddings.npy."],
        )

        render_matches_mock.assert_called_once()
        warning_mock.assert_called()
        error_mock.assert_not_called()

    def test_main_blocks_matches_when_live_generation_is_expected(self) -> None:
        render_matches_mock, warning_mock, error_mock = self._run_main(
            demo_mode=False,
            has_gemini_key=True,
            embedding_issues=["Missing cache files: speaker_embeddings.npy."],
        )

        render_matches_mock.assert_not_called()
        warning_mock.assert_not_called()
        error_mock.assert_called()

    def test_main_passes_merged_events_to_volunteer_dashboard(self) -> None:
        import src.app as app

        captured_events: dict[str, pd.DataFrame] = {}

        def capture_dashboard(**kwargs) -> None:
            captured_events["events_df"] = kwargs["events_df"].copy()

        with ExitStack() as stack:
            stack.enter_context(patch("streamlit.session_state", new={
                "demo_mode": True,
                "current_view": "crm",
                "matching_discovered_events": [
                    {
                        "event_id": "disc-1",
                        "Event / Program": "Fresh Discovery Event",
                        "Category": "career_fair",
                        "Host / Unit": "USC",
                        "Event Region": "Los Angeles",
                    }
                ],
            }))
            stack.enter_context(patch("src.app.init_runtime_state"))
            stack.enter_context(patch("src.app.validate_config", return_value=[]))
            stack.enter_context(patch("src.app.render_sidebar", return_value=_noop_context()))
            stack.enter_context(patch("src.app.load_all", return_value=_sample_datasets()))
            stack.enter_context(patch("src.app._resolve_embedding_lookup_dicts", return_value=({}, {}, {}, [], None, False)))
            stack.enter_context(patch("src.app.has_gemini_api_key", return_value=False))
            stack.enter_context(patch("src.app.render_command_center_tab"))
            stack.enter_context(patch("src.app.render_matches_tab_ui"))
            stack.enter_context(patch("src.app.render_discovery_tab"))
            stack.enter_context(patch("src.app.render_pipeline_tab"))
            stack.enter_context(patch("src.app.render_expansion_map", return_value=object()))
            stack.enter_context(patch("src.app.render_volunteer_dashboard", side_effect=capture_dashboard))
            stack.enter_context(patch("src.feedback.acceptance.init_feedback_state"))
            stack.enter_context(patch("src.app.render_feedback_sidebar"))
            stack.enter_context(patch("src.app.get_match_results_df", return_value=pd.DataFrame()))
            stack.enter_context(patch.object(app.st, "tabs", return_value=tuple(_noop_context() for _ in range(6))))
            stack.enter_context(patch.object(app.st, "expander", side_effect=lambda *args, **kwargs: _noop_context()))
            stack.enter_context(patch.object(app.st, "slider", return_value=0.30))
            stack.enter_context(patch.object(app.st, "warning"))
            stack.enter_context(patch.object(app.st, "error"))
            app.main()

        merged_events = captured_events["events_df"]
        assert "Fresh Discovery Event" in merged_events["Event / Program"].tolist()


class TestEmptyDatasetIssues:
    def test_reports_headers_only_csvs(self) -> None:
        datasets = SimpleNamespace(
            speakers=[],
            events=[{"id": 1}],
            courses=[],
            calendar=[{"id": 1}],
        )

        issues = _empty_dataset_issues(datasets)

        assert "data_speaker_profiles.csv" in issues[0]
        assert any("data_cpp_course_schedule.csv" in issue for issue in issues)
