"""Tests for the FastAPI calendar router."""

from __future__ import annotations

import asyncio

from src.api.main import app
from src.api.routers import calendar as calendar_router
from src.api.routers.calendar import assignments, events

from tests.asgi_client import request


def test_calendar_router_is_mounted_on_app() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/calendar/events" in paths
    assert "/api/calendar/assignments" in paths


def test_calendar_events_endpoint_returns_coverage_metadata() -> None:
    payload = asyncio.run(events())
    assert isinstance(payload, list)
    assert payload

    first = payload[0]
    assert "event_name" in first
    assert "event_date" in first
    assert "coverage_status" in first
    assert "status_color" in first
    assert "assignment_count" in first
    assert "assigned_volunteers" in first
    assert first["coverage_status"] in {"covered", "partial", "needs_coverage"}


def test_calendar_assignments_endpoint_returns_overlay_metadata() -> None:
    payload = asyncio.run(assignments())
    assert isinstance(payload, list)
    assert payload

    first = payload[0]
    assert "event_name" in first
    assert "volunteer_name" in first
    assert "region" in first
    assert "event_date" in first
    assert "coverage_status" in first
    assert "volunteer_fatigue" in first
    assert "recovery_status" in first
    assert "recent_assignment_count" in first
    assert "status_color" in first
    assert first["coverage_status"] in {"covered", "partial", "needs_coverage"}
    assert first["recovery_status"] in {"Available", "Needs Rest", "Rest Recommended"}


def test_calendar_events_http_boundary_returns_json_payload() -> None:
    response = asyncio.run(request("GET", "/api/calendar/events"))
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert "coverage_status" in payload[0]


def test_calendar_router_cors_allows_local_dev() -> None:
    response = asyncio.run(
        request(
            "OPTIONS",
            "/api/calendar/events",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_calendar_events_fall_back_to_demo_rows_when_live_data_is_empty(monkeypatch) -> None:
    monkeypatch.setattr(calendar_router, "_live_event_rows", lambda: [])
    monkeypatch.setattr(
        calendar_router,
        "load_demo_calendar_events",
        lambda: [
            {
                "event_id": "demo-event-01",
                "event_name": "Demo Event",
                "event_date": "2026-04-09",
                "region": "Los Angeles - West",
                "nearby_universities": ["Cal Poly Pomona"],
                "suggested_lecture_window": "Apr 7-10",
                "coverage_status": "covered",
                "coverage_label": "IA covered",
                "coverage_ratio": 0.8,
                "assigned_volunteers": ["Demo Speaker"],
                "assignment_count": 1,
                "open_slots": 2,
                "status_color": "#005394",
            }
        ],
    )

    payload = asyncio.run(calendar_router.events())

    assert payload[0]["event_name"] == "Demo Event"
    assert payload[0]["coverage_status"] == "covered"
    assert payload[0]["source"] == "demo"


def test_calendar_assignments_fall_back_to_demo_rows_when_live_data_errors(monkeypatch) -> None:
    def _boom():
        raise RuntimeError("calendar offline")

    monkeypatch.setattr(calendar_router, "_assignment_rows", _boom)
    monkeypatch.setattr(
        calendar_router,
        "load_demo_calendar_assignments",
        lambda: [
            {
                "assignment_id": "demo-assignment-01",
                "event_id": "demo-event-01",
                "event_name": "Demo Event",
                "event_date": "2026-04-09",
                "region": "Los Angeles - West",
                "volunteer_name": "Demo Speaker",
                "volunteer_title": "VP Data Science",
                "volunteer_company": "Demo Co",
                "stage": "Confirmed",
                "coverage_status": "partial",
                "coverage_label": "Partial coverage",
                "volunteer_fatigue": 0.42,
                "recovery_status": "Needs Rest",
                "recovery_label": "Needs Rest",
                "recent_assignment_count": 2,
                "days_since_last_assignment": 6,
                "travel_burden": 0.2,
                "event_cadence": 0.4,
                "status_color": "#c47c00",
            }
        ],
    )

    payload = asyncio.run(calendar_router.assignments())

    assert payload[0]["event_name"] == "Demo Event"
    assert payload[0]["recovery_status"] == "Needs Rest"
    assert payload[0]["source"] == "demo"
