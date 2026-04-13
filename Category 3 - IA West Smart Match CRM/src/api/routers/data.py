"""REST endpoints exposing static CRM data files."""

from typing import Any, Callable

from fastapi import APIRouter, HTTPException

from src.api.demo_db import (
    load_demo_cpp_events,
    load_demo_event_calendar,
    load_demo_pipeline,
    load_demo_specialists,
)
from src.api.smartmatch_db import (
    load_live_cpp_events,
    load_live_event_calendar,
    load_live_pipeline,
    load_live_poc_contacts,
    load_live_specialists,
)
from src.data_loader import load_courses
from src.ui.data_helpers import (
    load_cpp_events,
    load_event_calendar,
    load_pipeline_data,
    load_poc_contacts,
    load_specialists,
)
from src.utils import format_course_display_name, format_course_identifier

router = APIRouter()


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


def _demo_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**row, "source": "demo"} for row in rows]


def _load_rows_with_fallback(
    live_loader: Callable[[], list[dict[str, Any]]],
    demo_loader: Callable[[], list[dict[str, Any]]],
    csv_loader: Callable[[], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    for loader, tag in [
        (live_loader, "live"),
        (demo_loader, "demo"),
        (csv_loader, "csv"),
    ]:
        try:
            rows = loader()
            if rows:
                return [{**row, "source": tag} for row in rows]
        except Exception:
            pass
    return []


@router.get("/specialists")
async def specialists() -> list[dict]:
    """Return the specialist roster consumed by the frontend."""
    return _load_rows_with_fallback(
        load_live_specialists, load_demo_specialists, load_specialists
    )


@router.get("/events")
async def events() -> list[dict]:
    """Return the CPP events dataset."""
    return _load_rows_with_fallback(
        load_live_cpp_events, load_demo_cpp_events, load_cpp_events
    )


@router.get("/pipeline")
async def pipeline() -> list[dict]:
    """Return pipeline sample rows for dashboard views."""
    return _load_rows_with_fallback(
        load_live_pipeline, load_demo_pipeline, load_pipeline_data
    )


@router.get("/calendar")
async def calendar() -> list[dict]:
    """Return IA event calendar rows."""
    return _load_rows_with_fallback(
        load_live_event_calendar, load_demo_event_calendar, load_event_calendar
    )


@router.get("/courses")
async def courses() -> list[dict]:
    """Return the CPP course schedule with enriched display keys."""
    try:
        df, _ = load_courses()
        rows = []
        for _, row in df.iterrows():
            course_key = format_course_identifier(row.get("Course"), row.get("Section"))
            display_name = format_course_display_name(
                row.get("Course"), row.get("Section"), row.get("Title")
            )
            rows.append({
                "course_key": course_key,
                "display_name": display_name,
                "Instructor": str(row.get("Instructor", "") or ""),
                "Course": str(row.get("Course", "") or ""),
                "Section": str(row.get("Section", "") or ""),
                "Title": str(row.get("Title", "") or ""),
                "Days": str(row.get("Days", "") or ""),
                "Start Time": str(row.get("Start Time", "") or ""),
                "End Time": str(row.get("End Time", "") or ""),
                "Enrl Cap": int(row.get("Enrl Cap", 0) or 0),
                "Mode": str(row.get("Mode", "") or ""),
                "Guest Lecture Fit": str(row.get("Guest Lecture Fit", "") or ""),
                "source": "csv",
            })
        return rows
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/university-contacts")
async def university_contacts() -> list[dict]:
    """University contacts from data_cpp_events_contacts.csv."""
    try:
        rows = load_cpp_events()
        contacts: list[dict] = []
        seen: set[str] = set()
        skip_names = {"", "see page", "see hub page for current routing/contact"}
        for row in rows:
            name = row.get("Point(s) of Contact (published)", "").strip()
            if name.lower() in skip_names:
                continue
            key = f"{name}|{row.get('Event / Program', '')}"
            if key in seen:
                continue
            seen.add(key)
            contacts.append({
                "name": name,
                "email": row.get("Contact Email / Phone (published)", "").strip(),
                "host_unit": row.get("Host / Unit", "").strip(),
                "event_name": row.get("Event / Program", "").strip(),
                "source": "university",
            })
        return contacts
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/contacts")
async def contacts() -> list[dict]:
    """Return point-of-contact records."""
    try:
        rows = load_live_poc_contacts()
        if rows:
            return [{**row, "source": "live"} for row in rows]
    except Exception:
        pass
    try:
        rows = load_poc_contacts()
        if rows:
            return [{**row, "source": "csv"} for row in rows]
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc
    return []
