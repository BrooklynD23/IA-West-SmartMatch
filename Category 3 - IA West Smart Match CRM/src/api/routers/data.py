"""REST endpoints exposing static CRM data files."""

from fastapi import APIRouter, HTTPException

from src.ui.data_helpers import (
    load_cpp_events,
    load_event_calendar,
    load_pipeline_data,
    load_poc_contacts,
    load_specialists,
)

router = APIRouter()


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


@router.get("/specialists")
async def specialists() -> list[dict]:
    """Return the specialist roster consumed by the frontend."""
    try:
        return load_specialists()
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/events")
async def events() -> list[dict]:
    """Return the CPP events dataset."""
    try:
        return load_cpp_events()
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/pipeline")
async def pipeline() -> list[dict]:
    """Return pipeline sample rows for dashboard views."""
    try:
        return load_pipeline_data()
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/calendar")
async def calendar() -> list[dict]:
    """Return IA event calendar rows."""
    try:
        return load_event_calendar()
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/contacts")
async def contacts() -> list[dict]:
    """Return point-of-contact records."""
    try:
        return load_poc_contacts()
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc
