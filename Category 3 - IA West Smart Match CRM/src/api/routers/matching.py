"""REST endpoints wrapping the core matching engine."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.data_loader import load_calendar, load_events, load_speakers
from src.embeddings import load_embedding_lookup_dicts
from src.matching.engine import rank_speakers_for_event

router = APIRouter()


class RankRequest(BaseModel):
    event_name: str
    limit: int = Field(default=5, ge=1, le=100)
    weights: dict[str, float] | None = None


class ScoreRequest(BaseModel):
    speaker_name: str
    event_name: str
    weights: dict[str, float] | None = None


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


def _load_matching_context() -> tuple[Any, Any, Any, dict[str, Any], dict[str, Any]]:
    speakers_df, _ = load_speakers()
    events_df, _ = load_events()
    calendar_df, _ = load_calendar()
    speaker_embeddings, event_embeddings, _ = load_embedding_lookup_dicts()
    return speakers_df, events_df, calendar_df, speaker_embeddings, event_embeddings


def _find_event_row(events_df: Any, event_name: str) -> Any:
    exact = events_df[events_df["Event / Program"].astype(str) == event_name]
    if not exact.empty:
        return exact.iloc[0]

    lowered = event_name.casefold()
    contains = events_df[
        events_df["Event / Program"].astype(str).str.casefold().str.contains(lowered, na=False)
    ]
    if not contains.empty:
        return contains.iloc[0]
    return None


def _normalize_ranked_match(result: dict[str, Any]) -> dict[str, Any]:
    score = float(result.get("total_score", 0.0) or 0.0)
    factor_scores = dict(result.get("factor_scores", {}))
    weighted_factor_scores = dict(result.get("weighted_factor_scores", {}))
    recovery_score = float(factor_scores.get("volunteer_fatigue", 0.0) or 0.0)
    fatigue_burden = round(max(0.0, min(1.0, 1.0 - recovery_score)), 4)
    recovery_status = (
        "On Cooldown"
        if fatigue_burden >= 0.75
        else "Needs Rest"
        if fatigue_burden >= 0.40
        else "Available"
    )
    normalized = {
        "rank": int(result.get("rank", 0) or 0),
        "name": str(result.get("speaker_name", "")),
        "title": str(result.get("speaker_title", "")),
        "company": str(result.get("speaker_company", "")),
        "board_role": str(result.get("speaker_board_role", "")),
        "metro_region": str(result.get("speaker_metro_region", "")),
        "expertise_tags": str(result.get("speaker_expertise_tags", "")),
        "event_id": str(result.get("event_id", "")),
        "event_name": str(result.get("event_name", "")),
        "score": score,
        "match_score": score,
        "total_score": score,
        "factor_scores": factor_scores,
        "weighted_factor_scores": weighted_factor_scores,
        "volunteer_fatigue": fatigue_burden,
        "recovery_status": recovery_status,
        "recovery_label": recovery_status,
        # Compatibility aliases while the frontend migrates off the engine field names.
        "speaker_name": str(result.get("speaker_name", "")),
        "speaker_title": str(result.get("speaker_title", "")),
        "speaker_company": str(result.get("speaker_company", "")),
        "speaker_board_role": str(result.get("speaker_board_role", "")),
        "speaker_metro_region": str(result.get("speaker_metro_region", "")),
        "speaker_expertise_tags": str(result.get("speaker_expertise_tags", "")),
    }
    return normalized


def _rank_matches(body: RankRequest) -> list[dict[str, Any]]:
    speakers_df, events_df, calendar_df, speaker_embeddings, event_embeddings = _load_matching_context()
    event_row = _find_event_row(events_df, body.event_name)
    if event_row is None:
        raise HTTPException(status_code=404, detail=f"Event not found: {body.event_name}")

    event_name = str(event_row.get("Event / Program", body.event_name))
    event_id = str(event_row.get("event_id", "") or event_name)
    event_embedding = event_embeddings.get(event_name)
    if event_embedding is None:
        event_embedding = event_embeddings.get(event_id)

    ranked = rank_speakers_for_event(
        event_row=event_row,
        speakers_df=speakers_df,
        speaker_embeddings=speaker_embeddings,
        event_embedding=event_embedding,
        ia_event_calendar=calendar_df,
        top_n=body.limit,
        weights=body.weights,
    )
    return [_normalize_ranked_match(result) for result in ranked]


@router.post("/rank")
async def rank(body: RankRequest) -> list[dict[str, Any]]:
    """Return frontend-oriented ranked matches for a target event."""
    try:
        return _rank_matches(body)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.post("/score")
async def score(body: ScoreRequest) -> dict[str, Any]:
    """Return the detailed factor scores for one speaker-event pair."""
    try:
        matches = _rank_matches(
            RankRequest(
                event_name=body.event_name,
                limit=100,
                weights=body.weights,
            )
        )
        target = body.speaker_name.casefold()
        for match in matches:
            name = str(match.get("name", ""))
            if name.casefold() == target or target in name.casefold():
                return {
                    "speaker_name": name,
                    "event_name": str(match.get("event_name", body.event_name)),
                    "total_score": float(match.get("total_score", 0.0) or 0.0),
                    "volunteer_fatigue": float(match.get("volunteer_fatigue", 0.0) or 0.0),
                    "recovery_status": str(match.get("recovery_status", "")),
                    "recovery_label": str(match.get("recovery_label", "")),
                    "factor_scores": dict(match.get("factor_scores", {})),
                    "weighted_factor_scores": dict(match.get("weighted_factor_scores", {})),
                }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc

    raise HTTPException(
        status_code=404,
        detail=f"Speaker not found for event '{body.event_name}': {body.speaker_name}",
    )
