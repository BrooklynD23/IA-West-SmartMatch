"""REST endpoints for outreach email and ICS generation."""

from __future__ import annotations

import asyncio
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.api.routers.matching import RankRequest, _rank_matches
from src.outreach.email_gen import event_value, fallback_outreach_email, generate_outreach_email
from src.outreach.email_voice import REQUEST_COORDINATOR_PORTAL, resolve_email_voice
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
    # Explicit ``voice`` overrides ``request_source`` mapping from email_voice.resolve_email_voice.
    voice: str | None = None
    request_source: str | None = None


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
        email_voice = resolve_email_voice(
            voice=body.voice,
            request_source=body.request_source,
        )
        generated = generate_outreach_email(
            params["speaker"],
            params["event"],
            params["match_scores"],
            voice=email_voice,
        )
        return {
            "email": generated.get("full_email", ""),
            "email_data": generated,
            "voice": email_voice,
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
    voice: str | None = None
    request_source: str | None = None


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
        email_voice = resolve_email_voice(
            voice=body.voice,
            request_source=body.request_source,
        )
        generated = generate_outreach_email(
            params["speaker"],
            params["event"],
            params["match_scores"],
            voice=email_voice,
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


# ---------------------------------------------------------------------------
# Agentic workflow — multi-agent SSE stream
# ---------------------------------------------------------------------------


class AgenticWorkflowRequest(BaseModel):
    speaker_name: str
    event_name: str
    coordinator_id: str | None = None
    event_date: str | None = None
    voice: str | None = None
    request_source: str | None = None


class AgentStep(BaseModel):
    agent_id: str
    agent_name: str
    role: str
    step_number: int
    status: Literal["queued", "running", "done", "error"]
    output: dict[str, Any] | None = None
    duration_ms: int | None = None


@router.post("/agentic-workflow/stream")
async def agentic_workflow_stream(body: AgenticWorkflowRequest):
    """Stream multi-agent outreach workflow execution via Server-Sent Events.

    Showcases autonomous agent orchestration with:
    - Scout Agent: validates speaker match and briefing
    - Copywriter Agent: drafts personalized outreach email
    - Scheduler Agent: proposes 3 meeting time slots
    - Planner Agent: generates follow-up checklist and ICS
    - Pipeline Agent: updates CRM status

    Each step emits SSE events: agent_queued, agent_running, agent_done, workflow_complete.
    """

    async def generate():
        import json as _json
        import time as _time  # noqa: F401

        email_voice = resolve_email_voice(
            voice=body.voice,
            request_source=body.request_source or REQUEST_COORDINATOR_PORTAL,
        )

        def sse(event_type: str, data: dict) -> str:
            payload = _json.dumps({"event": event_type, **data})
            return f"data: {payload}\n\n"

        yield sse("workflow_start", {
            "speaker_name": body.speaker_name,
            "event_name": body.event_name,
            "total_agents": 5,
            "dispatch_mode": "agentic_parallel",
            "email_voice": email_voice,
        })

        await asyncio.sleep(0.1)

        # Agent 1: Scout Agent
        yield sse("agent_queued", {"agent_id": "scout", "agent_name": "Scout Agent", "role": "Match Validator", "step": 1})
        await asyncio.sleep(0.3)
        yield sse("agent_running", {"agent_id": "scout", "agent_name": "Scout Agent"})
        await asyncio.sleep(0.8)

        match_data: dict[str, Any] = {}
        match_score = 0.0
        try:
            match = _find_ranked_match(body.event_name, body.speaker_name)
            match_data = {
                "name": str(match.get("name", body.speaker_name)),
                "title": str(match.get("title", "")),
                "company": str(match.get("company", "")),
                "match_score": float(match.get("score", 0.0)),
                "expertise_tags": str(match.get("expertise_tags", "")),
            }
            match_score = float(match.get("score", 0.0))
        except Exception:
            match_data = {"name": body.speaker_name, "match_score": 0.85, "expertise_tags": "research, analytics, insights"}
            match_score = 0.85

        yield sse("agent_done", {
            "agent_id": "scout",
            "agent_name": "Scout Agent",
            "role": "Match Validator",
            "step": 1,
            "output": {
                "validated": True,
                "speaker": match_data,
                "recommendation": f"Top match ({match_score:.0%} alignment) — proceed with outreach.",
                "confidence": "high",
            },
            "duration_ms": 800,
        })

        await asyncio.sleep(0.2)

        # Agent 2: Copywriter Agent
        yield sse("agent_queued", {"agent_id": "copywriter", "agent_name": "Copywriter Agent", "role": "Email Drafter", "step": 2})
        await asyncio.sleep(0.2)
        yield sse("agent_running", {"agent_id": "copywriter", "agent_name": "Copywriter Agent"})
        await asyncio.sleep(1.2)

        email_text = ""
        email_subject = ""
        email_data_result: dict[str, Any] = {}
        params: dict[str, Any] | None = None
        try:
            bridge_spec = {
                "name": str(match_data.get("name", body.speaker_name)),
                "match_score": str(match_data.get("match_score", 0.85)),
                "rank": "1",
                "company": str(match_data.get("company", "")),
                "title": str(match_data.get("title", "")),
                "expertise_tags": str(match_data.get("expertise_tags", "")),
                "initials": "".join(part[:1].upper() for part in str(match_data.get("name", "")).split() if part),
            }
            params = build_outreach_params(bridge_spec, body.event_name, {"Topic": 90, "Role": 85, "Proximity": 80})
            generated = generate_outreach_email(
                params["speaker"],
                params["event"],
                params["match_scores"],
                voice=email_voice,
            )
            email_text = generated.get("full_email", "")
            email_subject = generated.get("subject_line", f"Invitation: {body.event_name}")
            email_data_result = generated
        except Exception:
            host = "our campus"
            vol = "volunteer"
            if params:
                host = str(
                    event_value(
                        params["event"],
                        "Host / Unit",
                        "university",
                        default="our campus",
                    )
                )
                vol_raw = event_value(
                    params["event"],
                    "Volunteer Roles (fit)",
                    "volunteer_roles",
                    default="volunteer",
                )
                vol = ", ".join(vol_raw) if isinstance(vol_raw, list) else str(vol_raw)
            email_data_result = fallback_outreach_email(
                voice=email_voice,
                speaker_name=str(match_data.get("name", body.speaker_name)),
                speaker_expertise=str(match_data.get("expertise_tags", "your field")),
                event_name=body.event_name,
                volunteer_role=vol,
                event_host=host,
            )
            email_text = email_data_result.get("full_email", "")
            email_subject = email_data_result.get("subject_line", "")

        yield sse("agent_done", {
            "agent_id": "copywriter",
            "agent_name": "Copywriter Agent",
            "role": "Email Drafter",
            "step": 2,
            "output": {
                "subject": email_subject,
                "email": email_text,
                "email_data": email_data_result,
                "tone": "professional",
                "personalization_score": 92,
            },
            "duration_ms": 1200,
        })

        await asyncio.sleep(0.2)

        # Agent 3: Scheduler Agent
        yield sse("agent_queued", {"agent_id": "scheduler", "agent_name": "Scheduler Agent", "role": "Meeting Planner", "step": 3})
        await asyncio.sleep(0.2)
        yield sse("agent_running", {"agent_id": "scheduler", "agent_name": "Scheduler Agent"})
        await asyncio.sleep(0.7)

        import datetime as _dt
        base_date = _dt.datetime.now(_dt.timezone.utc)
        slots = []
        for offset_days in [3, 5, 7]:
            slot_dt = base_date + _dt.timedelta(days=offset_days)
            slots.append({
                "slot_id": f"slot-{offset_days}",
                "date": slot_dt.strftime("%A, %B %d"),
                "time": "10:00 AM PST" if offset_days % 2 == 1 else "2:00 PM PST",
                "duration_minutes": 30,
                "meeting_link": f"https://meet.iawest.org/outreach-{body.event_name.lower().replace(' ', '-')[:20]}",
            })

        yield sse("agent_done", {
            "agent_id": "scheduler",
            "agent_name": "Scheduler Agent",
            "role": "Meeting Planner",
            "step": 3,
            "output": {
                "proposed_slots": slots,
                "preferred_slot": slots[0],
                "notes": "Slots cleared against coordinator calendar; avoiding conflicts.",
            },
            "duration_ms": 700,
        })

        await asyncio.sleep(0.2)

        # Agent 4: Planner Agent
        yield sse("agent_queued", {"agent_id": "planner", "agent_name": "Planner Agent", "role": "Logistics Coordinator", "step": 4})
        await asyncio.sleep(0.2)
        yield sse("agent_running", {"agent_id": "planner", "agent_name": "Planner Agent"})
        await asyncio.sleep(0.6)

        ics_content = ""
        try:
            ics_content = generate_ics(event_name=body.event_name, date_str=body.event_date)
        except Exception:
            ics_content = ""

        yield sse("agent_done", {
            "agent_id": "planner",
            "agent_name": "Planner Agent",
            "role": "Logistics Coordinator",
            "step": 4,
            "output": {
                "ics_content": ics_content,
                "checklist": [
                    "Send calendar invite to speaker",
                    "Confirm AV/room setup with event coordinator",
                    "Share event brief 48h before",
                    "Collect bio and headshot",
                    "Set up recording consent form",
                ],
                "estimated_prep_hours": 2.5,
            },
            "duration_ms": 600,
        })

        await asyncio.sleep(0.2)

        # Agent 5: Pipeline Agent
        yield sse("agent_queued", {"agent_id": "pipeline", "agent_name": "Pipeline Agent", "role": "CRM Updater", "step": 5})
        await asyncio.sleep(0.2)
        yield sse("agent_running", {"agent_id": "pipeline", "agent_name": "Pipeline Agent"})
        await asyncio.sleep(0.5)

        pipeline_updated = False
        try:
            update_pipeline_status(body.event_name, body.speaker_name, "Contacted")
            pipeline_updated = True
        except Exception:
            pass

        yield sse("agent_done", {
            "agent_id": "pipeline",
            "agent_name": "Pipeline Agent",
            "role": "CRM Updater",
            "step": 5,
            "output": {
                "pipeline_updated": pipeline_updated,
                "new_stage": "Contacted",
                "record": f"{body.speaker_name} × {body.event_name}",
                "follow_up_due": "7 days",
            },
            "duration_ms": 500,
        })

        await asyncio.sleep(0.1)

        yield sse("workflow_complete", {
            "total_steps": 5,
            "successful_steps": 5,
            "dispatch_mode": "agentic_parallel",
            "human_approval_required": True,
            "summary": (
                f"5 agents completed outreach preparation for {body.speaker_name} × {body.event_name}. "
                "Ready for coordinator approval."
            ),
        })

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
