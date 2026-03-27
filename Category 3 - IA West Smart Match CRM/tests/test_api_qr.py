"""Tests for the FastAPI QR router and QR persistence helpers."""

from __future__ import annotations

import asyncio
import base64
from urllib.parse import parse_qs, urlsplit

import pytest
from starlette.requests import Request

from src.api.main import app
from src.api.routers.qr import QRGenerateRequest, generate as generate_qr, scan as scan_qr, stats as stats_qr
from src.qr import service as qr_service
from src.ui import data_helpers

from tests.asgi_client import request


@pytest.fixture()
def qr_storage(tmp_path, monkeypatch):
    """Redirect QR persistence into an isolated temp data directory."""
    data_dir = tmp_path / "data"
    (data_dir / "qr").mkdir(parents=True)

    monkeypatch.setattr(data_helpers, "_data_dir", lambda: data_dir)
    monkeypatch.setattr(qr_service, "_data_dir", lambda: data_dir)
    data_helpers._load_qr_manifest_cached.cache_clear()
    data_helpers._load_qr_scan_log_cached.cache_clear()

    yield data_dir

    data_helpers._load_qr_manifest_cached.cache_clear()
    data_helpers._load_qr_scan_log_cached.cache_clear()


def _request(path: str = "/api/qr/generate", scheme: str = "https", host: str = "example.org") -> Request:
    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {
        "type": "http",
        "method": "POST",
        "scheme": scheme,
        "path": path,
        "root_path": "",
        "query_string": b"",
        "server": (host, 443 if scheme == "https" else 80),
        "client": ("127.0.0.1", 12345),
        "headers": [(b"host", host.encode("utf-8"))],
    }
    return Request(scope, _receive)


def test_qr_router_is_mounted_on_app() -> None:
    paths = {route.path for route in app.routes}
    assert "/api/qr/generate" in paths
    assert "/api/qr/scan/{referral_code}" in paths
    assert "/api/qr/stats" in paths


def test_generate_qr_http_rejects_unapproved_destination_url(qr_storage) -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/qr/generate",
            json_body={
            "speaker_name": "Alice Speaker",
            "event_name": "Annual Summit",
            "destination_url": "https://evil.example/phish",
            },
        )
    )
    assert response.status_code == 400
    assert "approved Insights Association domain" in response.json()["detail"]


def test_generate_qr_http_ignores_client_base_url_override(qr_storage) -> None:
    response = asyncio.run(
        request(
            "POST",
            "/api/qr/generate",
            json_body={
            "speaker_name": "Alice Speaker",
            "event_name": "Annual Summit",
            "base_url": "https://evil.example",
            },
        )
    )
    assert response.status_code == 200
    assert response.json()["scan_url"].startswith("http://testserver/api/qr/scan/")


def test_generate_qr_artifact_is_deterministic_and_persists_manifest(qr_storage) -> None:
    referral_code_a = qr_service.deterministic_referral_code("Alice Speaker", "Annual Summit")
    referral_code_b = qr_service.deterministic_referral_code("  alice   speaker  ", "annual summit")
    assert referral_code_a == referral_code_b
    assert referral_code_a.startswith("IAW-")

    body = QRGenerateRequest(
        speaker_name="Alice Speaker",
        event_name="Annual Summit",
        base_url="https://example.org",
    )

    first = asyncio.run(generate_qr(body, _request()))
    second = asyncio.run(generate_qr(body, _request()))

    assert first["referral_code"] == referral_code_a
    assert second["referral_code"] == referral_code_a
    assert first["scan_url"] == f"https://example.org/api/qr/scan/{referral_code_a}"
    assert first["generation_count"] == 1
    assert second["generation_count"] == 2
    assert second["qr_data_url"].startswith("data:image/png;base64,")

    png_bytes = base64.b64decode(second["qr_png_base64"])
    assert png_bytes.startswith(b"\x89PNG\r\n\x1a\n")

    manifest = data_helpers.load_qr_manifest()
    assert len(manifest) == 1
    record = manifest[0]
    assert record["referral_code"] == referral_code_a
    assert record["generation_count"] == 2
    assert record["scan_count"] == 0
    assert record["membership_interest_count"] == 0


def test_scan_endpoint_records_redirect_metadata(qr_storage) -> None:
    artifact = qr_service.generate_qr_artifact(
        speaker_name="Alice Speaker",
        event_name="Annual Summit",
        base_url="https://example.org",
    )

    response = asyncio.run(scan_qr(artifact["referral_code"], membership_interest=True))

    assert response.status_code == 307
    parsed = urlsplit(response.headers["location"])
    params = {key: values[0] for key, values in parse_qs(parsed.query).items()}
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == artifact["destination_url"]
    assert params["referral_code"] == artifact["referral_code"]
    assert params["speaker_name"] == "Alice Speaker"
    assert params["event_name"] == "Annual Summit"
    assert params["membership_interest"] == "true"

    manifest = data_helpers.load_qr_manifest()
    scan_log = data_helpers.load_qr_scan_log()
    assert len(manifest) == 1
    assert len(scan_log) == 1
    assert manifest[0]["scan_count"] == 1
    assert manifest[0]["membership_interest_count"] == 1
    assert manifest[0]["last_scanned_at"]
    assert scan_log[0]["membership_interest"] is True


def test_stats_endpoint_returns_roi_summary(qr_storage) -> None:
    artifact = qr_service.generate_qr_artifact(
        speaker_name="Alice Speaker",
        event_name="Annual Summit",
        base_url="https://example.org",
    )
    asyncio.run(scan_qr(artifact["referral_code"], membership_interest=True))
    asyncio.run(scan_qr(artifact["referral_code"], membership_interest=False))

    payload = asyncio.run(stats_qr(speaker_name="Alice Speaker"))

    assert payload["generated_count"] == 1
    assert payload["scan_count"] == 2
    assert payload["membership_interest_count"] == 1
    assert payload["conversion_rate"] == 0.5
    assert payload["filters"]["speaker_name"] == "Alice Speaker"
    assert payload["filters"]["event_name"] is None
    assert payload["filters"]["referral_code"] is None
    assert len(payload["referral_codes"]) == 1
    assert payload["referral_codes"][0]["referral_code"] == artifact["referral_code"]
    assert payload["referral_codes"][0]["scan_count"] == 2
    assert payload["referral_codes"][0]["membership_interest_count"] == 1
    assert payload["recent_scans"][0]["referral_code"] == artifact["referral_code"]


def test_scan_http_redirect_serializes_location_header(qr_storage) -> None:
    generate_response = asyncio.run(
        request(
            "POST",
            "/api/qr/generate",
            json_body={
            "speaker_name": "Alice Speaker",
            "event_name": "Annual Summit",
            "destination_url": "http://testserver/join",
            },
        )
    )
    assert generate_response.status_code == 200
    referral_code = generate_response.json()["referral_code"]

    response = asyncio.run(
        request(
            "GET",
            f"/api/qr/scan/{referral_code}",
            query={"membership_interest": "true"},
        )
    )
    assert response.status_code == 307
    assert response.headers["location"].startswith("http://testserver/join?")
