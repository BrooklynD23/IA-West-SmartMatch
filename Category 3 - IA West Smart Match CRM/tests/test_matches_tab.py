"""Integration tests for Matches tab runtime-state behavior."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pandas as pd


@contextmanager
def _noop_context():
    yield


class TestMatchesRuntimeState:
    @patch("streamlit.session_state", new_callable=dict)
    def test_render_matches_tab_merges_discovered_events_into_event_view(
        self,
        mock_state: dict,
        monkeypatch,
    ) -> None:
        import src.ui.matches_tab as mod

        base_events = pd.DataFrame(
            [
                {
                    "Event / Program": "AI Hackathon",
                    "Category": "hackathon",
                    "Recurrence (typical)": "Annual",
                    "Host / Unit": "UCLA",
                    "Volunteer Roles (fit)": "Judge",
                    "Primary Audience": "Students",
                    "Public URL": "https://ucla.edu/hackathon",
                    "Point(s) of Contact (published)": "Alice",
                    "Contact Email / Phone (published)": "alice@ucla.edu",
                }
            ]
        )
        mock_state["matching_discovered_events"] = [
            {
                "event_id": "disc-fresh-1",
                "Event / Program": "Fresh Discovery Event",
                "Category": "career_fair",
                "Volunteer Roles (fit)": "Speaker",
                "Primary Audience": "Graduate students",
                "Host / Unit": "USC",
                "Event Region": "Los Angeles",
                "Date": "2026-05-02",
                "URL": "https://usc.edu/events/fresh-discovery",
                "Contact Name": "Dr. Gomez",
                "Contact Email": "gomez@usc.edu",
                "source": "discovery",
            }
        ]

        captured: dict[str, pd.DataFrame] = {}
        monkeypatch.setattr(mod, "_render_weight_sliders", lambda: None)
        monkeypatch.setattr(mod.st.sidebar, "radio", lambda *args, **kwargs: "Events")
        monkeypatch.setattr(
            mod,
            "_render_event_matches",
            lambda events, *args, **kwargs: captured.setdefault("events", events.copy()),
        )
        monkeypatch.setattr(mod, "_render_course_matches", lambda *args, **kwargs: None)

        mod.render_matches_tab(
            events=base_events,
            courses=pd.DataFrame(),
            speakers=pd.DataFrame(),
            speaker_embeddings={},
            event_embeddings={},
            course_embeddings={},
            ia_event_calendar=pd.DataFrame(),
        )

        merged_events = captured["events"]
        assert list(merged_events["Event / Program"]) == [
            "AI Hackathon",
            "Fresh Discovery Event",
        ]
        assert list(merged_events["event_id"]) == [
            "AI Hackathon",
            "disc-fresh-1",
        ]
        assert merged_events.iloc[1]["Recurrence (typical)"] == "2026-05-02"
        assert merged_events.iloc[1]["Public URL"] == "https://usc.edu/events/fresh-discovery"
        assert merged_events.iloc[1]["Point(s) of Contact (published)"] == "Dr. Gomez"
        assert merged_events.iloc[1]["Contact Email / Phone (published)"] == "gomez@usc.edu"
        assert merged_events.iloc[1]["Date"] == "2026-05-02"
        assert list(base_events["Event / Program"]) == ["AI Hackathon"]

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
                "event_id": "evt-ai-hackathon",
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
        assert list(stored["event_id"]) == ["evt-ai-hackathon"]
        assert list(stored["speaker_id"]) == ["Alice"]
        assert list(stored["speaker_name"]) == ["Alice"]
        assert list(stored["total_score"]) == [0.91]

    @patch("streamlit.session_state", new_callable=dict)
    def test_event_matches_selects_by_stable_event_id_when_names_collide(
        self,
        mock_state: dict,
        monkeypatch,
    ) -> None:
        import src.ui.matches_tab as mod

        events = pd.DataFrame(
            [
                {
                    "event_id": "evt-1",
                    "Event / Program": "Career Fair",
                    "Volunteer Roles (fit)": "Judge",
                    "Host / Unit": "UCLA",
                    "Category": "career_fair",
                },
                {
                    "event_id": "evt-2",
                    "Event / Program": "Career Fair",
                    "Volunteer Roles (fit)": "Speaker",
                    "Host / Unit": "USC",
                    "Category": "career_fair",
                },
            ]
        )
        captured: dict[str, pd.Series] = {}

        def fake_rank(**kwargs):
            captured["event_row"] = kwargs["event_row"]
            return []

        monkeypatch.setattr(mod.st, "selectbox", lambda *args, **kwargs: "evt-2")
        monkeypatch.setattr(mod.st, "markdown", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "_render_match_card", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "rank_speakers_for_event", fake_rank)

        mod._render_event_matches(
            events=events,
            speakers=pd.DataFrame([{"Name": "Alice"}]),
            speaker_embeddings={},
            event_embeddings={},
            ia_event_calendar=pd.DataFrame(),
        )

        assert captured["event_row"]["event_id"] == "evt-2"
        assert captured["event_row"]["Host / Unit"] == "USC"

    def test_render_match_card_uses_event_id_for_feedback_buttons(
        self,
        monkeypatch,
    ) -> None:
        import src.ui.matches_tab as mod

        captured: dict[str, str] = {}

        def fake_columns(spec, *args, **kwargs):
            return tuple(_noop_context() for _ in range(len(spec)))

        monkeypatch.setattr(mod.st, "container", _noop_context)
        monkeypatch.setattr(mod.st, "markdown", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "caption", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "metric", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "columns", fake_columns)
        monkeypatch.setattr(mod.st, "plotly_chart", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod.st, "button", lambda *args, **kwargs: False)
        monkeypatch.setattr(mod.st, "download_button", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "_render_match_explanation", lambda *args, **kwargs: None)
        monkeypatch.setattr(mod, "_create_radar_chart", lambda *args, **kwargs: object())
        monkeypatch.setattr(mod, "render_email_preview", lambda *args, **kwargs: None)
        monkeypatch.setattr(
            mod,
            "render_feedback_buttons",
            lambda **kwargs: captured.update({"event_id": kwargs["event_id"]}),
        )

        mod._render_match_card(
            match={
                "rank": 1,
                "event_id": "disc-123",
                "event_name": "Career Fair",
                "speaker_name": "Alice",
                "speaker_title": "VP",
                "speaker_company": "Acme",
                "speaker_metro_region": "Los Angeles",
                "speaker_board_role": "Judge",
                "speaker_expertise_tags": "AI",
                "total_score": 0.9,
                "factor_scores": {
                    "topic_relevance": 0.9,
                    "role_fit": 0.8,
                    "geographic_proximity": 0.7,
                    "calendar_fit": 0.6,
                    "historical_conversion": 0.5,
                    "student_interest": 0.4,
                },
            },
            event=pd.Series({"Host / Unit": "UCLA"}),
        )

        assert captured["event_id"] == "disc-123"

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
