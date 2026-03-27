"""Tests for the FastAPI feedback router and optimizer service."""

from __future__ import annotations

import asyncio

import pytest

from src.api.main import app
from src.api.routers.feedback import FeedbackSubmitRequest, stats as feedback_stats, submit as submit_feedback
from src.config import DEFAULT_WEIGHTS
from src.feedback import service as feedback_service
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


def test_feedback_router_is_mounted_on_app() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/feedback/submit" in paths
    assert "/api/feedback/stats" in paths


def test_submit_feedback_http_validation_rejects_out_of_range_rating(feedback_storage) -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/feedback/submit",
            json_body={
            "event_name": "AI for a Better Future Hackathon",
            "speaker_name": "Alice Speaker",
            "decision": "accept",
            "coordinator_rating": 7,
            },
        )
    )
    assert response.status_code == 422


def test_submit_feedback_persists_log_and_weight_history(feedback_storage) -> None:
    payload = asyncio.run(
        submit_feedback(
            FeedbackSubmitRequest(
                event_name="AI for a Better Future Hackathon",
                speaker_name="Alice Speaker",
                decision="accept",
                match_score=0.82,
                event_outcome="attended",
                membership_interest=True,
                coordinator_rating=5,
                factor_scores={"topic_relevance": 0.9, "role_fit": 0.8},
            )
        )
    )

    assert payload["feedback"]["event_name"] == "AI for a Better Future Hackathon"
    assert payload["feedback"]["speaker_name"] == "Alice Speaker"
    assert payload["feedback"]["membership_interest"] is True
    assert payload["optimizer_snapshot"]["total_feedback"] == 1

    feedback_log = data_helpers.load_feedback_log()
    weight_history = data_helpers.load_weight_history()
    assert len(feedback_log) == 1
    assert len(weight_history) == 1
    assert feedback_log[0]["decision"] == "accept"
    assert weight_history[0]["weights"]


def test_stats_returns_pain_score_and_feedback_rollups(feedback_storage) -> None:
    asyncio.run(
        submit_feedback(
            FeedbackSubmitRequest(
                event_name="AI for a Better Future Hackathon",
                speaker_name="Alice Speaker",
                decision="accept",
                match_score=0.88,
                event_outcome="attended",
                membership_interest=True,
                coordinator_rating=5,
                factor_scores={"topic_relevance": 0.92},
            )
        )
    )
    asyncio.run(
        submit_feedback(
            FeedbackSubmitRequest(
                event_name="Case Competition",
                speaker_name="Bob Volunteer",
                decision="decline",
                match_score=0.74,
                decline_reason="Topic mismatch",
                coordinator_rating=2,
                factor_scores={"topic_relevance": 0.31},
            )
        )
    )

    payload = asyncio.run(feedback_stats())

    assert payload["total_feedback"] == 2
    assert payload["accepted"] == 1
    assert payload["declined"] == 1
    assert payload["acceptance_rate"] == 0.5
    assert payload["membership_interest_count"] == 1
    assert 0.0 <= payload["pain_score"] <= 100.0
    assert payload["decline_reasons"][0]["reason"] == "Topic mismatch"
    assert payload["trend"]
    assert payload["weight_history"]


def test_decline_reasons_shift_effective_weights_within_bounds(feedback_storage) -> None:
    for speaker_name in ("Alice Speaker", "Bob Volunteer", "Casey Mentor"):
        asyncio.run(
            submit_feedback(
                FeedbackSubmitRequest(
                    event_name="AI for a Better Future Hackathon",
                    speaker_name=speaker_name,
                    decision="decline",
                    match_score=0.79,
                    decline_reason="Too far (geographic distance)",
                    coordinator_rating=3,
                    factor_scores={"geographic_proximity": 0.2},
                )
            )
        )

    payload = asyncio.run(feedback_stats())
    current_weights = payload["current_weights"]
    weight_sum = round(sum(current_weights.values()), 4)

    assert current_weights["geographic_proximity"] > DEFAULT_WEIGHTS["geographic_proximity"]
    assert abs(weight_sum - 1.0) <= 0.0002
    assert payload["recommended_adjustments"]
    assert any(
        adjustment["factor"] == "geographic_proximity"
        for adjustment in payload["recommended_adjustments"]
    )


def test_feedback_stats_http_returns_serialized_optimizer_state(feedback_storage) -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/feedback/submit",
            json_body={
            "event_name": "AI for a Better Future Hackathon",
            "speaker_name": "Alice Speaker",
            "decision": "accept",
            "match_score": 0.82,
            "event_outcome": "attended",
            "membership_interest": True,
            "coordinator_rating": 5,
            "factor_scores": {"topic_relevance": 0.9, "role_fit": 0.8},
            },
        )
    )
    assert response.status_code == 200

    stats_response = asyncio.run(request("GET", "/api/feedback/stats"))
    assert stats_response.status_code == 200
    assert stats_response.headers["content-type"].startswith("application/json")

    payload = stats_response.json()
    assert payload["total_feedback"] == 1
    assert payload["current_weights"]
    assert payload["weight_history"]
