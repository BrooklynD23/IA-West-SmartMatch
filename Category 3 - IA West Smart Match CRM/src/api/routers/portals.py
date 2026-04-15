"""REST endpoints for student and event coordinator portals, plus mock auth."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from src.api.demo_db import (
    load_demo_calendar_events,
    load_demo_event_coordinators,
    load_demo_meeting_bookings,
    load_demo_mock_roles,
    load_demo_outreach_threads,
    load_demo_retention_nudges,
    load_demo_student_connection_suggestions,
    load_demo_student_registrations,
    load_demo_students,
)

router = APIRouter()


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=404, detail=detail)


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


def _interests_overlap(student_interests: str, course_alignment: str) -> bool:
    """Return True if any student interest keyword appears in the course alignment text."""
    if not student_interests or not course_alignment:
        return False
    tags = [t.strip().casefold() for t in student_interests.split(",") if t.strip()]
    alignment_lower = course_alignment.casefold()
    return any(tag in alignment_lower for tag in tags)


# ---------------------------------------------------------------------------
# Student endpoints
# ---------------------------------------------------------------------------


@router.get("/student-connections")
async def student_connection_suggestions_query(
    student_id: str = Query(..., min_length=1, description="Demo student id, e.g. stu-001"),
) -> dict[str, Any]:
    """Same payload as ``/students/{student_id}/connection-suggestions`` but avoids path
    collisions where ``/students/connection-suggestions`` would be parsed as
    ``GET /students/{student_id}`` with ``student_id=\"connection-suggestions\"`` (404).
    """
    try:
        return load_demo_student_connection_suggestions(student_id)
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/students")
async def list_students() -> dict[str, Any]:
    """Return all students (admin view)."""
    try:
        students = load_demo_students()
        return {"data": students, "source": "demo", "total": len(students)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/students/{student_id}/recommendations")
async def student_recommendations(student_id: str) -> dict[str, Any]:
    """Return recommended events for a student based on interest overlap."""
    try:
        students = load_demo_students()
    except Exception as exc:
        raise _server_error(exc) from exc

    student = next((s for s in students if s.get("student_id") == student_id), None)
    if student is None:
        raise _not_found(f"Student not found: {student_id}")

    try:
        events = load_demo_calendar_events()
    except Exception as exc:
        raise _server_error(exc) from exc

    interests = str(student.get("interests") or "")
    enriched = [
        {
            **event,
            "is_recommended": _interests_overlap(interests, str(event.get("course_alignment") or "")),
        }
        for event in events
    ]
    return {
        "student_id": student_id,
        "recommendations": enriched,
        "total": len(enriched),
        "source": "demo",
    }


@router.get("/students/{student_id}/registrations")
async def student_registrations(student_id: str) -> dict[str, Any]:
    """Return all event registrations for a student."""
    try:
        registrations = load_demo_student_registrations(student_id=student_id)
        return {"data": registrations, "source": "demo", "total": len(registrations)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/students/{student_id}/connection-suggestions")
async def student_connection_suggestions(student_id: str) -> dict[str, Any]:
    """Peers to connect with, ranked by count of events both students attended."""
    try:
        return load_demo_student_connection_suggestions(student_id)
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/students/{student_id}/nudge")
async def student_nudge(student_id: str) -> dict[str, Any]:
    """Return the retention nudge for a student."""
    try:
        nudges = load_demo_retention_nudges(student_id=student_id)
    except Exception as exc:
        raise _server_error(exc) from exc

    if not nudges:
        raise _not_found(f"No nudge found for student: {student_id}")
    return {**nudges[0], "source": "demo"}


@router.get("/students/{student_id}")
async def get_student(student_id: str) -> dict[str, Any]:
    """Return a single student profile (registered after sub-routes so paths like
    ``/students/connection-suggestions`` are not captured as a student id).
    """
    try:
        students = load_demo_students()
    except Exception as exc:
        raise _server_error(exc) from exc

    for student in students:
        if student.get("student_id") == student_id:
            return {**student, "source": "demo"}
    raise _not_found(f"Student not found: {student_id}")


# ---------------------------------------------------------------------------
# Event coordinator endpoints
# ---------------------------------------------------------------------------


@router.get("/event-coordinators")
async def list_event_coordinators() -> dict[str, Any]:
    """Return all event coordinators."""
    try:
        coordinators = load_demo_event_coordinators()
        return {"data": coordinators, "source": "demo", "total": len(coordinators)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/event-coordinators/{coordinator_id}")
async def get_event_coordinator(coordinator_id: str) -> dict[str, Any]:
    """Return a single event coordinator."""
    try:
        coordinators = load_demo_event_coordinators()
    except Exception as exc:
        raise _server_error(exc) from exc

    for coordinator in coordinators:
        if coordinator.get("coordinator_id") == coordinator_id:
            return {**coordinator, "source": "demo"}
    raise _not_found(f"Coordinator not found: {coordinator_id}")


@router.get("/event-coordinators/{coordinator_id}/threads")
async def coordinator_threads(coordinator_id: str) -> dict[str, Any]:
    """Return outreach threads for an event coordinator."""
    try:
        threads = load_demo_outreach_threads(coordinator_id=coordinator_id)
        return {"data": threads, "source": "demo", "total": len(threads)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/event-coordinators/{coordinator_id}/meetings")
async def coordinator_meetings(coordinator_id: str) -> dict[str, Any]:
    """Return meeting bookings for an event coordinator."""
    try:
        bookings = load_demo_meeting_bookings(coordinator_id=coordinator_id)
        return {"data": bookings, "source": "demo", "total": len(bookings)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/event-coordinators/{coordinator_id}/events")
async def coordinator_events(coordinator_id: str) -> dict[str, Any]:
    """Return calendar events hosted by this coordinator."""
    try:
        coordinators = load_demo_event_coordinators()
    except Exception as exc:
        raise _server_error(exc) from exc

    coordinator = next((c for c in coordinators if c.get("coordinator_id") == coordinator_id), None)
    if coordinator is None:
        raise _not_found(f"Coordinator not found: {coordinator_id}")

    hosted_raw = str(coordinator.get("hosted_events") or "")
    hosted_ids = {eid.strip() for eid in hosted_raw.split(",") if eid.strip()}

    try:
        all_events = load_demo_calendar_events()
    except Exception as exc:
        raise _server_error(exc) from exc

    events_out: list[dict[str, Any]] = []
    for e in all_events:
        if e.get("event_id") not in hosted_ids:
            continue
        open_slots = int(e.get("open_slots") or 0)
        coverage = str(e.get("coverage_status") or "")
        staffing_open = open_slots > 0 or coverage in ("needs_coverage", "partial")
        events_out.append({**e, "staffing_open": staffing_open})
    events = events_out
    # Frontend expects `data` (same shape as other portal list endpoints); keep `events` for compatibility.
    return {
        "coordinator_id": coordinator_id,
        "data": events,
        "events": events,
        "total": len(events),
        "source": "demo",
    }


# ---------------------------------------------------------------------------
# Mock auth endpoint
# ---------------------------------------------------------------------------


class MockLoginRequest(BaseModel):
    email: str
    role: str | None = None


def _infer_role_from_email(email: str) -> str:
    """Infer default portal role from email (used when UI does not send an explicit role)."""
    if email.endswith("@iawest.org"):
        return "ia_admin"
    if any(
        email.endswith(domain)
        for domain in ("@cpp.edu", "@uci.edu", "@csuf.edu", "@ucsd.edu", "@usc.edu")
    ):
        return "event_coordinator"
    return "student"


def _redirect_for_role(role: str) -> str:
    if role == "ia_admin":
        return "/dashboard"
    if role == "event_coordinator":
        return "/coordinator-portal"
    return "/student-portal"


@router.post("/auth/mock-login")
async def mock_login(body: MockLoginRequest) -> dict[str, Any]:
    """Accept an email and return a mock session with role and redirect path.

    When ``role`` is sent from the login UI (student / event_coordinator / ia_admin), it is honored
    so the picker and manual form cannot disagree with server-side email-domain inference (which
    previously caused confusing sessions and hard-to-debug failures when proxies returned 5xx).
    """
    try:
        email = body.email.strip().casefold()
        if not email or "@" not in email:
            raise HTTPException(status_code=400, detail="Valid email is required")

        raw_role = (body.role or "").strip().casefold().replace(" ", "_")
        if raw_role in ("student", "event_coordinator", "ia_admin"):
            role = raw_role
        else:
            role = _infer_role_from_email(email)

        redirect_path = _redirect_for_role(role)

        # Look up matching user record for the resolved role
        user: dict[str, Any] = {"id": "guest", "name": "Guest User", "email": body.email.strip()}
        try:
            if role == "student":
                students = load_demo_students()
                match = next((s for s in students if str(s.get("email", "")).strip().casefold() == email), None)
                if match:
                    user = dict(match)
            elif role == "event_coordinator":
                coordinators = load_demo_event_coordinators()
                match = next((c for c in coordinators if str(c.get("email", "")).strip().casefold() == email), None)
                if match:
                    user = dict(match)
            elif role == "ia_admin":
                roles = load_demo_mock_roles()
                match = next((r for r in roles if str(r.get("email", "")).strip().casefold() == email), None)
                if match:
                    user = dict(match)
        except Exception:
            pass

        try:
            available_roles = load_demo_mock_roles()
        except Exception:
            available_roles = []

        return {
            "user": jsonable_encoder(user),
            "role": role,
            "redirect_path": redirect_path,
            "available_roles": jsonable_encoder(available_roles),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise _server_error(exc) from exc
