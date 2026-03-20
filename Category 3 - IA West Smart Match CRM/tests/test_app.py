"""Tests for app-level embedding cache bootstrap behavior."""

from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from src.app import _resolve_embedding_lookup_dicts
from src.app import _empty_dataset_issues


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
