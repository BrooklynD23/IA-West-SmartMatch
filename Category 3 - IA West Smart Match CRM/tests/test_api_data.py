"""Tests for the FastAPI data router."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_get_specialists_returns_json_array() -> None:
    response = client.get("/api/data/specialists")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload
    assert "name" in payload[0]


def test_get_events_returns_json_array() -> None:
    response = client.get("/api/data/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_pipeline_returns_json_array() -> None:
    response = client.get("/api/data/pipeline")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_calendar_returns_json_array() -> None:
    response = client.get("/api/data/calendar")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_contacts_returns_json_array() -> None:
    response = client.get("/api/data/contacts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_cors_allows_localhost_5173() -> None:
    response = client.options(
        "/api/data/specialists",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
