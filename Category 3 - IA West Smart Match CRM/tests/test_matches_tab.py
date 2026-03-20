"""Integration tests for Matches tab runtime-state behavior."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pandas as pd


class TestMatchesRuntimeState:
    @patch("streamlit.session_state", new_callable=dict)
    def test_event_matches_populate_session_state(
        self,
        mock_state: dict,
        monkeypatch,
    ) -> None:
        import src.ui.matches_tab as mod

        events = pd.DataFrame(
            [
                {
                    "Event / Program": "AI Hackathon",
                    "Volunteer Roles (fit)": "Judge",
                    "Host / Unit": "UCLA",
                    "Category": "hackathon",
                }
            ]
        )
        speakers = pd.DataFrame([{"Name": "Alice"}])
        calendar = pd.DataFrame()
        top_matches = [
            {
                "rank": 1,
                "event_name": "AI Hackathon",
                "speaker_name": "Alice",
                "total_score": 0.91,
                "factor_scores": {
                    "topic_relevance": 0.9,
                    "role_fit": 0.8,
                    "geographic_proximity": 0.7,
                    "calendar_fit": 0.6,
                    "historical_conversion": 0.5,
                    "student_interest": 0.4,
                },
            }
        ]

        monkeypatch.setattr(mod.st, "selectbox", lambda *args, **kwargs: "AI Hackathon")
        monkeypatch.setattr(mod.st, "markdown", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "_render_match_card", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "rank_speakers_for_event", lambda **kwargs: top_matches)

        mod._render_event_matches(
            events=events,
            speakers=speakers,
            speaker_embeddings={},
            event_embeddings={},
            ia_event_calendar=calendar,
        )

        stored = mock_state["match_results_df"]
        assert list(stored["event_id"]) == ["AI Hackathon"]
        assert list(stored["speaker_id"]) == ["Alice"]
        assert list(stored["speaker_name"]) == ["Alice"]
        assert list(stored["total_score"]) == [0.91]

    @patch("streamlit.session_state", new_callable=dict)
    def test_demo_mode_uses_fixture_for_match_explanations(
        self,
        mock_state: dict,
        monkeypatch,
    ) -> None:
        import src.ui.matches_tab as mod

        @contextmanager
        def fake_spinner(_message: str):
            yield

        captured: list[str] = []
        monkeypatch.setattr(mod.st, "button", lambda *args, **kwargs: True)
        monkeypatch.setattr(mod.st, "spinner", fake_spinner)
        monkeypatch.setattr(mod.st, "markdown", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "caption", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "info", lambda value: captured.append(str(value)))
        monkeypatch.setattr(mod, "load_cached_explanation", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "fallback_match_explanation", lambda *args, **kwargs: "fallback")
        monkeypatch.setattr(mod, "generate_match_explanation", MagicMock(return_value="live"))

        mock_state["demo_mode"] = True
        mod._render_match_explanation(
            match={
                "speaker_name": "Ignored",
                "event_name": "Ignored Event",
                "factor_scores": {},
            },
            event=pd.Series(
                {
                    "Category": "hackathon",
                    "Volunteer Roles (fit)": "Judge",
                    "Primary Audience": "Students",
                }
            ),
        )

        mod.generate_match_explanation.assert_not_called()
        assert captured
        assert "Travis Miller" in captured[-1]


class TestWeightValidation:
    def test_validate_weights_rejects_all_zero_values(self) -> None:
        from src.ui.matches_tab import validate_weights

        error = validate_weights(
            {
                "topic_relevance": 0.0,
                "role_fit": 0.0,
                "geographic_proximity": 0.0,
                "calendar_fit": 0.0,
                "historical_conversion": 0.0,
                "student_interest": 0.0,
            }
        )

        assert error is not None
        assert "At least one weight" in error

    def test_validate_weights_accepts_positive_total(self) -> None:
        from src.ui.matches_tab import validate_weights

        assert validate_weights({"topic_relevance": 0.25, "role_fit": 0.75}) is None
