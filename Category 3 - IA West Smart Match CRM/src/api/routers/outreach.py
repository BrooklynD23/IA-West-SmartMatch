"""REST endpoints for outreach email and ICS generation."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.routers.matching import RankRequest, _rank_matches
from src.outreach.email_gen import generate_outreach_email
from src.outreach.ics_generator import generate_ics
from src.outreach.pipeline_updater import update_pipeline_status
from src.ui.outreach_bridge import build_outreach_params

router = APIRouter()

_CANONICAL_TO_DISPLAY = {
    "topic_relevance": "Topic",
    "role_fit": "Role",
    "geographic_proximity": "Proximity",
    "calendar_fit": "Calendar",
    "historical_conversion": "History",
    "student_interest": "Impact",
}


class EmailRequest(BaseModel):
    speaker_name: str
    event_name: str


class IcsRequest(BaseModel):
    event_name: str
    event_date: str | None = None
    location: str | None = None
    description: str | None = None


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


def _factor_scores_for_bridge(canonical_scores: dict[str, Any]) -> dict[str, int]:
    display_scores: dict[str, int] = {}
    for canonical_key, display_key in _CANONICAL_TO_DISPLAY.items():
        raw_score = float(canonical_scores.get(canonical_key, 0.0) or 0.0)
        display_scores[display_key] = int(round(raw_score * 100))
    return display_scores


def _find_ranked_match(event_name: str, speaker_name: str) -> dict[str, Any]:
    matches = _rank_matches(RankRequest(event_name=event_name, limit=100))
    target = speaker_name.casefold()
    for match in matches:
        name = str(match.get("name", ""))
        if name.casefold() == target or target in name.casefold():
            return match
    raise HTTPException(
        status_code=404,
        detail=f"Speaker not found for event '{event_name}': {speaker_name}",
    )


@router.post("/email")
async def email(body: EmailRequest) -> dict[str, Any]:
    """Generate outreach email text for a ranked speaker-event pair."""
    try:
        match = _find_ranked_match(body.event_name, body.speaker_name)
        bridge_spec = {
            "name": str(match.get("name", "")),
            "match_score": str(match.get("score", 0.0)),
            "rank": str(match.get("rank", "")),
            "company": str(match.get("company", "")),
            "title": str(match.get("title", "")),
            "expertise_tags": str(match.get("expertise_tags", "")),
            "initials": "".join(part[:1].upper() for part in str(match.get("name", "")).split() if part),
        }
        params = build_outreach_params(
            bridge_spec,
            body.event_name,
            _factor_scores_for_bridge(dict(match.get("factor_scores", {}))),
        )
        generated = generate_outreach_email(
            params["speaker"],
            params["event"],
            params["match_scores"],
        )
        return {
            "email": generated.get("full_email", ""),
            "email_data": generated,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.post("/ics")
async def ics(body: IcsRequest) -> dict[str, str]:
    """Generate ICS content for an event."""
    try:
        return {
            "ics_content": generate_ics(
                event_name=body.event_name,
                date_str=body.event_date,
                location=body.location,
                description=body.description,
            )
        }
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


# ---------------------------------------------------------------------------
# Workflow endpoint — orchestrates email + ICS + pipeline in one call
# ---------------------------------------------------------------------------


class WorkflowRequest(BaseModel):
    speaker_name: str
    event_name: str


class StepResult(BaseModel):
    status: Literal["ok", "error"]
    error: str | None = None


@router.post("/workflow")
async def workflow(body: WorkflowRequest) -> dict[str, Any]:
    """Orchestrate outreach email, ICS generation, and pipeline update in one call.

    Returns all three results alongside per-step statuses so callers can
    distinguish partial failures (e.g. email step errored but ICS succeeded).

    Raises:
        HTTPException 404: If the speaker is not found for the event.
    """
    steps: dict[str, dict] = {}
    email_text = ""
    email_data_result: dict = {}
    ics_content = ""
    pipeline_updated = False

    # 404 propagates naturally — do not catch
    match = _find_ranked_match(body.event_name, body.speaker_name)

    # Step 1: email generation
    try:
        bridge_spec = {
            "name": str(match.get("name", "")),
            "match_score": str(match.get("score", 0.0)),
            "rank": str(match.get("rank", "")),
            "company": str(match.get("company", "")),
            "title": str(match.get("title", "")),
            "expertise_tags": str(match.get("expertise_tags", "")),
            "initials": "".join(
                part[:1].upper()
                for part in str(match.get("name", "")).split()
                if part
            ),
        }
        params = build_outreach_params(
            bridge_spec,
            body.event_name,
            _factor_scores_for_bridge(dict(match.get("factor_scores", {}))),
        )
        generated = generate_outreach_email(
            params["speaker"],
            params["event"],
            params["match_scores"],
        )
        email_text = generated.get("full_email", "")
        email_data_result = generated
        steps["email"] = {"status": "ok"}
    except Exception as exc:
        steps["email"] = {"status": "error", "error": str(exc)}

    # Step 2: ICS generation
    try:
        ics_content = generate_ics(event_name=body.event_name)
        steps["ics"] = {"status": "ok"}
    except Exception as exc:
        steps["ics"] = {"status": "error", "error": str(exc)}

    # Step 3: pipeline status update
    try:
        update_pipeline_status(body.event_name, body.speaker_name, "Contacted")
        pipeline_updated = True
        steps["pipeline"] = {"status": "ok"}
    except Exception as exc:
        steps["pipeline"] = {"status": "error", "error": str(exc)}

    return {
        "email": email_text,
        "email_data": email_data_result,
        "ics_content": ics_content,
        "pipeline_updated": pipeline_updated,
        "steps": steps,
        "dispatch_mode": "serial",
    }
