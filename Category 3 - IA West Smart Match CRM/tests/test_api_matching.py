"""Tests for the FastAPI matching and outreach routers."""

from __future__ import annotations

import asyncio

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from src.api.main import app
from src.config import DEFAULT_WEIGHTS
from src.api.routers.matching import RankRequest, ScoreRequest, rank as rank_matches, score as score_match
from src.api.routers.outreach import EmailRequest, IcsRequest, email as generate_email, ics as generate_ics
from src.feedback import service as feedback_service
from src.matching.engine import compute_match_score
from src.ui import data_helpers

from tests.asgi_client import request


@pytest.fixture()
def feedback_storage(tmp_path, monkeypatch):
    """Redirect feedback persistence into an isolated temp data directory."""
    data_dir = tmp_path / "data"
    (data_dir / "feedback").mkdir(parents=True)

    monkeypatch.setattr(data_helpers, "_data_dir", lambda: data_dir)
    monkeypatch.setattr(feedback_service, "_data_dir", lambda: data_dir)
    data_helpers._load_feedback_log_cached.cache_clear()
    data_helpers._load_weight_history_cached.cache_clear()

    yield data_dir

    data_helpers._load_feedback_log_cached.cache_clear()
    data_helpers._load_weight_history_cached.cache_clear()


def test_rank_endpoint_returns_normalized_matches() -> None:
    payload = asyncio.run(
        rank_matches(
            RankRequest(event_name="AI for a Better Future Hackathon", limit=3)
        )
    )
    assert isinstance(payload, list)
    assert payload
    first = payload[0]
    assert "name" in first
    assert "score" in first
    assert "rank" in first
    assert "factor_scores" in first
    assert "volunteer_fatigue" in first
    assert "recovery_status" in first
    assert "volunteer_fatigue" in first["factor_scores"]
    assert "volunteer_fatigue" in first["weighted_factor_scores"]


def test_rank_endpoint_requires_event_name() -> None:
    with pytest.raises(ValidationError):
        RankRequest(limit=3)


def test_rank_endpoint_rejects_missing_event_name_over_http() -> None:
    response = asyncio.run(request("POST", "/api/matching/rank", json_body={"limit": 3}))
    assert response.status_code == 422


def test_ics_endpoint_returns_calendar_text() -> None:
    payload = asyncio.run(
        generate_ics(
            IcsRequest(
                event_name="Test Event",
                event_date="2026-04-15",
                location="CPP",
                description="Career event",
            )
        )
    )
    assert "ics_content" in payload
    assert "BEGIN:VCALENDAR" in payload["ics_content"]


def test_email_endpoint_returns_generated_email_text() -> None:
    ranking_response = asyncio.run(
        rank_matches(
            RankRequest(event_name="AI for a Better Future Hackathon", limit=1)
        )
    )
    top_match = ranking_response[0]

    payload = asyncio.run(
        generate_email(
            EmailRequest(
                speaker_name=top_match["name"],
                event_name="AI for a Better Future Hackathon",
            )
        )
    )
    assert "email" in payload
    assert isinstance(payload["email"], str)
    assert payload["email"]


def test_score_endpoint_exposes_volunteer_fatigue_breakdown() -> None:
    ranking_response = asyncio.run(
        rank_matches(
            RankRequest(event_name="AI for a Better Future Hackathon", limit=1)
        )
    )
    top_match = ranking_response[0]

    payload = asyncio.run(
        score_match(
            ScoreRequest(
                speaker_name=top_match["name"],
                event_name="AI for a Better Future Hackathon",
            )
        )
    )
    assert "volunteer_fatigue" in payload
    assert "recovery_status" in payload
    assert "volunteer_fatigue" in payload["factor_scores"]
    assert "volunteer_fatigue" in payload["weighted_factor_scores"]
    assert 0.0 <= payload["factor_scores"]["volunteer_fatigue"] <= 1.0


def test_volunteer_fatigue_weight_override_changes_score_materially() -> None:
    fatigue_only_weights = {factor: 0.0 for factor in DEFAULT_WEIGHTS}
    fatigue_only_weights["volunteer_fatigue"] = 1.0

    base_kwargs = dict(
        speaker_embedding=np.array([1.0, 0.0]),
        event_embedding=np.array([1.0, 0.0]),
        speaker_board_role="President",
        event_volunteer_roles="Judge; Mentor",
        speaker_metro_region="Los Angeles — West",
        event_region="Los Angeles",
        event_date_or_recurrence="Monthly",
        ia_event_calendar=pd.DataFrame(
            [{"IA Event Date": "2026-04-16", "Region": "Los Angeles"}]
        ),
        speaker_name="Demo Speaker",
        event_category="AI / Hackathon",
    )

    fresh_history = pd.DataFrame(
        [{"speaker_name": "Demo Speaker", "stage_order": "0", "stage": "Matched"}]
    )
    busy_history = pd.DataFrame(
        [
            {"speaker_name": "Demo Speaker", "stage_order": "4", "stage": "Attended"},
            {"speaker_name": "Demo Speaker", "stage_order": "3", "stage": "Confirmed"},
            {"speaker_name": "Demo Speaker", "stage_order": "2", "stage": "Contacted"},
        ]
    )

    fresh_result = compute_match_score(
        **base_kwargs,
        pipeline_rows=fresh_history,
        weights=fatigue_only_weights,
    )
    busy_result = compute_match_score(
        **base_kwargs,
        pipeline_rows=busy_history,
        weights=fatigue_only_weights,
    )

    assert fresh_result["factor_scores"]["volunteer_fatigue"] > busy_result["factor_scores"]["volunteer_fatigue"]
    assert fresh_result["total_score"] > busy_result["total_score"]
    assert fresh_result["weighted_factor_scores"]["volunteer_fatigue"] == fresh_result["factor_scores"]["volunteer_fatigue"]
    assert busy_result["weighted_factor_scores"]["volunteer_fatigue"] == busy_result["factor_scores"]["volunteer_fatigue"]


def test_rank_http_endpoint_uses_effective_server_weights(feedback_storage) -> None:
    for speaker_name in ("Alice Speaker", "Bob Volunteer", "Casey Mentor"):
        response = asyncio.run(
            request(
                "POST",
                "/api/feedback/submit",
                json_body={
                "event_name": "AI for a Better Future Hackathon",
                "speaker_name": speaker_name,
                "decision": "decline",
                "match_score": 0.79,
                "decline_reason": "Too far (geographic distance)",
                "coordinator_rating": 3,
                "factor_scores": {"geographic_proximity": 0.25},
                },
            )
        )
        assert response.status_code == 200

    stats_response = asyncio.run(request("GET", "/api/feedback/stats"))
    assert stats_response.status_code == 200
    current_weights = stats_response.json()["current_weights"]

    rank_response = asyncio.run(
        request(
            "POST",
            "/api/matching/rank",
            json_body={"event_name": "AI for a Better Future Hackathon", "limit": 1},
        )
    )
    assert rank_response.status_code == 200

    match = rank_response.json()[0]
    factor_score = float(match["factor_scores"]["geographic_proximity"])
    weighted_score = float(match["weighted_factor_scores"]["geographic_proximity"])
    expected_weighted_score = round(factor_score * float(current_weights["geographic_proximity"]), 4)
    default_weighted_score = round(factor_score * float(DEFAULT_WEIGHTS["geographic_proximity"]), 4)

    assert abs(weighted_score - expected_weighted_score) <= 0.0001
    assert weighted_score != default_weighted_score
