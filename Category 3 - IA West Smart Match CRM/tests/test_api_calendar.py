"""Tests for the FastAPI calendar router."""

from __future__ import annotations

import asyncio

from src.api.main import app
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
    assert first["recovery_status"] in {"Available", "Needs Rest", "On Cooldown"}


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
