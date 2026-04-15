"""REST endpoints for QR generation, scan tracking, and ROI stats."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from src.api.demo_db import load_demo_qr_stats
from src.api.smartmatch_db import load_live_qr_stats
from src.qr.service import build_qr_stats, generate_qr_artifact, record_qr_scan

router = APIRouter()


class QRGenerateRequest(BaseModel):
    speaker_name: str = Field(min_length=1)
    event_name: str = Field(min_length=1)
    destination_url: str | None = None
    base_url: str | None = None


class QRGenerateResponse(BaseModel):
    referral_code: str
    speaker_name: str
    event_name: str
    destination_url: str
    scan_url: str
    generated_at: str
    updated_at: str
    generation_count: int
    scan_count: int
    membership_interest_count: int
    qr_png_base64: str
    qr_data_url: str


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


@router.post("/generate")
async def generate(body: QRGenerateRequest, request: Request) -> dict[str, Any]:
    """Generate or refresh a QR asset for one speaker-event pair."""
    try:
        artifact = generate_qr_artifact(
            speaker_name=body.speaker_name,
            event_name=body.event_name,
            destination_url=body.destination_url,
            base_url=str(request.base_url),
        )
        return artifact
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc


@router.get("/scan/{referral_code}")
async def scan(referral_code: str, membership_interest: bool = False) -> RedirectResponse:
    """Log the scan then redirect to the recorded destination URL."""
    try:
        result = record_qr_scan(referral_code, membership_interest=membership_interest)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive API boundary
        raise _server_error(exc) from exc

    return RedirectResponse(url=str(result["redirect_url"]), status_code=307)


class AttendanceCheckinRequest(BaseModel):
    event_id: str
    student_id: str
    check_in_time: str
    scan_duration_minutes: int | None = None


@router.post("/attendance/checkin")
async def attendance_checkin(body: AttendanceCheckinRequest) -> dict[str, Any]:
    """Record a student QR attendance check-in."""
    try:
        from src.qr.service import record_attendance_checkin
        return record_attendance_checkin(
            event_id=body.event_id,
            student_id=body.student_id,
            check_in_time=body.check_in_time,
            scan_duration_minutes=body.scan_duration_minutes,
        )
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/attendance/history/{student_id}")
async def attendance_history(student_id: str) -> dict[str, Any]:
    """Return QR attendance history for a student."""
    try:
        from src.qr.service import get_student_attendance_history
        records = get_student_attendance_history(student_id)
        return {"student_id": student_id, "records": records, "total": len(records)}
    except Exception as exc:
        raise _server_error(exc) from exc


@router.get("/stats")
async def stats(
    speaker_name: str | None = None,
    event_name: str | None = None,
    referral_code: str | None = None,
) -> dict[str, Any]:
    """Return aggregate QR generation, scan, and ROI stats."""
    try:
        payload = load_live_qr_stats()
        if payload:
            return {**payload, "source": "live"}
    except Exception:
        pass
    try:
        payload = build_qr_stats(
            speaker_name=speaker_name,
            event_name=event_name,
            referral_code=referral_code,
        )
        if payload.get("generated_count", 0):
            return payload
    except Exception:
        pass
    return {
        **load_demo_qr_stats(),
        "source": "demo",
    }
