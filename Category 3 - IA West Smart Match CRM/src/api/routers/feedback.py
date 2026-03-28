"""REST endpoints for continuous-improvement feedback and optimizer stats."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.demo_db import load_demo_feedback_stats
from src.api.smartmatch_db import load_live_feedback_stats
from src.feedback.service import build_feedback_stats, record_feedback

router = APIRouter()


class FeedbackSubmitRequest(BaseModel):
    event_name: str = Field(min_length=1)
    speaker_name: str = Field(min_length=1)
    decision: Literal["accept", "decline"]
    match_score: float = Field(default=0.0, ge=0.0, le=1.0)
    decline_reason: str | None = None
    decline_notes: str | None = None
    event_outcome: str | None = None
    membership_interest: bool = False
    coordinator_rating: int | None = Field(default=None, ge=1, le=5)
    factor_scores: dict[str, float] = Field(default_factory=dict)
    weights_used: dict[str, float] | None = None


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


@router.post("/submit")
async def submit(body: FeedbackSubmitRequest) -> dict[str, Any]:
    """Persist a feedback event and return the updated optimizer snapshot."""
    try:
        return record_feedback(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/stats")
async def stats() -> dict[str, Any]:
    """Return aggregate feedback stats, pain score, and weight history."""
    try:
        payload = load_live_feedback_stats()
        if payload:
            return {**payload, "source": "live"}
    except Exception:
        pass
    try:
        payload = build_feedback_stats()
        if payload.get("total_feedback", 0):
            return payload
    except Exception:
        pass
    return {
        **load_demo_feedback_stats(),
        "source": "demo",
    }
