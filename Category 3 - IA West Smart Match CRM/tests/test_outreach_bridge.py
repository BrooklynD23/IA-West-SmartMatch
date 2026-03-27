"""Unit tests for src.ui.outreach_bridge."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.ui.outreach_bridge import (
    build_event_dict,
    build_match_scores,
    build_outreach_params,
    build_speaker_dict,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SPECIALISTS: list[dict[str, str]] = [
    {
        "name": "Alice Smith",
        "board_role": "VP Programs",
        "metro_region": "Los Angeles",
        "company": "Acme Corp",
        "title": "Director of Analytics",
        "expertise_tags": "ML, NLP, Analytics",
        "initials": "AS",
    },
    {
        "name": "Bob Jones",
        "board_role": "Treasurer",
        "metro_region": "San Diego",
        "company": "Beta Inc",
        "title": "Data Scientist",
        "expertise_tags": "Statistics, Python",
        "initials": "BJ",
    },
]

_SPEC: dict = {
    "name": "Alice Smith",
    "match_score": "0.92",
    "rank": "1",
    "stage": "Matched",
    "company": "Acme Corp",
    "title": "Director of Analytics",
    "expertise_tags": "ML, NLP, Analytics",
    "initials": "AS",
}

_FACTOR_SCORES: dict[str, int] = {
    "Topic": 98,
    "Role": 95,
    "Proximity": 90,
    "Calendar": 85,
    "History": 100,
    "Impact": 96,
}

_CPP_EVENT_ROW: dict[str, str] = {
    "Event / Program": "CPP Career Center — Career Fairs",
    "Category": "Career Fair",
    "Recurrence (typical)": "Annual",
    "Host / Unit": "Cal Poly Pomona",
    "Volunteer Roles (fit)": "Guest speaker; Mentor",
    "Primary Audience": "Students",
}


# ---------------------------------------------------------------------------
# build_speaker_dict
# ---------------------------------------------------------------------------


class TestBuildSpeakerDict:
    def test_maps_keys_correctly(self) -> None:
        result = build_speaker_dict(_SPEC, _SPECIALISTS)
        assert result["Name"] == "Alice Smith"
        assert result["Title"] == "Director of Analytics"
        assert result["Company"] == "Acme Corp"
        assert result["Board Role"] == "VP Programs"
        assert result["Metro Region"] == "Los Angeles"
        assert result["Expertise Tags"] == "ML, NLP, Analytics"

    def test_missing_profile_uses_spec_data(self) -> None:
        unknown_spec = {**_SPEC, "name": "Unknown Person"}
        result = build_speaker_dict(unknown_spec, _SPECIALISTS)
        assert result["Name"] == "Unknown Person"
        assert result["Title"] == "Director of Analytics"
        assert result["Company"] == "Acme Corp"
        assert result["Board Role"] == ""
        assert result["Metro Region"] == ""

    def test_loads_specialists_when_none(self) -> None:
        with patch(
            "src.ui.outreach_bridge.load_specialists", return_value=_SPECIALISTS
        ):
            result = build_speaker_dict(_SPEC)
            assert result["Board Role"] == "VP Programs"


# ---------------------------------------------------------------------------
# build_event_dict
# ---------------------------------------------------------------------------


class TestBuildEventDict:
    def test_found(self) -> None:
        with patch(
            "src.ui.outreach_bridge.get_event_by_name",
            return_value=_CPP_EVENT_ROW,
        ):
            result = build_event_dict("CPP Career Center — Career Fairs")
            assert result["Category"] == "Career Fair"
            assert result["Host / Unit"] == "Cal Poly Pomona"

    def test_not_found_returns_fallback(self) -> None:
        with patch(
            "src.ui.outreach_bridge.get_event_by_name", return_value=None
        ):
            result = build_event_dict("Nonexistent Event")
            assert result == {"Event / Program": "Nonexistent Event"}


# ---------------------------------------------------------------------------
# build_match_scores
# ---------------------------------------------------------------------------


class TestBuildMatchScores:
    def test_normalizes_to_0_1(self) -> None:
        result = build_match_scores(_SPEC, _FACTOR_SCORES)
        factors = result["factor_scores"]
        assert factors["topic_relevance"] == pytest.approx(0.98)
        assert factors["role_fit"] == pytest.approx(0.95)
        assert factors["geographic_proximity"] == pytest.approx(0.90)
        assert factors["calendar_fit"] == pytest.approx(0.85)
        assert factors["historical_conversion"] == pytest.approx(1.0)
        assert factors["student_interest"] == pytest.approx(0.96)

    def test_maps_display_to_canonical(self) -> None:
        result = build_match_scores(_SPEC, _FACTOR_SCORES)
        factors = result["factor_scores"]
        assert set(factors.keys()) == {
            "topic_relevance",
            "role_fit",
            "geographic_proximity",
            "calendar_fit",
            "historical_conversion",
            "student_interest",
        }

    def test_total_score_from_spec(self) -> None:
        result = build_match_scores(_SPEC, _FACTOR_SCORES)
        assert result["total_score"] == pytest.approx(0.92)

    def test_invalid_match_score_defaults(self) -> None:
        bad_spec = {**_SPEC, "match_score": "invalid"}
        result = build_match_scores(bad_spec, _FACTOR_SCORES)
        assert result["total_score"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# build_outreach_params
# ---------------------------------------------------------------------------


class TestBuildOutreachParams:
    def test_composes_all_three(self) -> None:
        with patch(
            "src.ui.outreach_bridge.get_event_by_name",
            return_value=_CPP_EVENT_ROW,
        ):
            result = build_outreach_params(
                spec=_SPEC,
                event_name="CPP Career Center — Career Fairs",
                factor_scores=_FACTOR_SCORES,
                specialists=_SPECIALISTS,
            )
            assert "speaker" in result
            assert "event" in result
            assert "match_scores" in result
            assert result["speaker"]["Name"] == "Alice Smith"
            assert result["event"]["Category"] == "Career Fair"
            assert result["match_scores"]["total_score"] == pytest.approx(0.92)
