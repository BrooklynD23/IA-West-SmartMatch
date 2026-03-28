"""FastAPI calendar endpoints for master calendar and assignment overlays."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from src.api.demo_db import load_demo_calendar_assignments, load_demo_calendar_events
from src.api.smartmatch_db import load_live_calendar_assignments, load_live_calendar_events
from src.data_loader import load_calendar, load_events, load_speakers
from src.matching.factors import resolve_event_region, volunteer_recovery_details
from src.ui.data_helpers import load_pipeline_data

router = APIRouter()

_STATUS_META: dict[str, dict[str, str]] = {
    "covered": {
        "label": "IA covered",
        "color": "#005394",
        "tone": "blue",
    },
    "partial": {
        "label": "Partial coverage",
        "color": "#c47c00",
        "tone": "amber",
    },
    "needs_coverage": {
        "label": "Needs volunteers",
        "color": "#d14343",
        "tone": "red",
    },
}


def _server_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=500, detail=str(exc))


def _demo_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{**row, "source": "demo"} for row in rows]


def _as_date_string(value: object) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:  # pragma: no cover - defensive formatting guard
            pass
    return str(value)


def _stable_slot_index(key: str, length: int) -> int:
    if length <= 0:
        return 0
    return sum(ord(char) for char in key) % length


def _coverage_status(coverage_ratio: float) -> str:
    if coverage_ratio >= 0.70:
        return "covered"
    if coverage_ratio >= 0.30:
        return "partial"
    return "needs_coverage"


def _calendar_slots() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    calendar_df, _ = load_calendar()
    slots: list[dict[str, Any]] = []
    slots_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in calendar_df.sort_values("IA Event Date").reset_index(drop=True).iterrows():
        slot = {
            "event_id": f"calendar-{index + 1:02d}",
            "event_name": f"{str(row.get('Region', '')).strip()} planning window",
            "event_date": _as_date_string(row.get("IA Event Date", "")),
            "region": str(row.get("Region", "")).strip(),
            "nearby_universities": str(row.get("Nearby Universities", "")),
            "suggested_lecture_window": str(row.get("Suggested Lecture Window", "")),
            "course_alignment": str(row.get("Course Alignment", "")),
        }
        slots.append(slot)
        slots_by_region[slot["region"]].append(slot)
    return slots, slots_by_region


def _event_metadata() -> dict[str, dict[str, str]]:
    events_df, _ = load_events()
    metadata: dict[str, dict[str, str]] = {}
    for row in events_df.to_dict("records"):
        event_name = str(row.get("Event / Program", "")).strip()
        raw_region = str(row.get("Event Region", row.get("Host / Unit", "")) or "")
        metadata[event_name] = {
            "event_name": event_name,
            "region": resolve_event_region(raw_region),
            "event_date_or_recurrence": str(
                row.get("Event Date", row.get("Recurrence (typical)", "")) or ""
            ),
            "host_unit": str(row.get("Host / Unit", "") or ""),
        }
    return metadata


def _speaker_metadata() -> dict[str, dict[str, str]]:
    speakers_df, _ = load_speakers()
    metadata: dict[str, dict[str, str]] = {}
    for row in speakers_df.to_dict("records"):
        name = str(row.get("Name", "")).strip()
        metadata[name] = {
            "speaker_region": str(row.get("Metro Region", "") or ""),
            "volunteer_title": str(row.get("Title", "") or ""),
            "volunteer_company": str(row.get("Company", "") or ""),
        }
    return metadata


def _slot_for_event(
    event_name: str,
    event_region: str,
    slots: list[dict[str, Any]],
    slots_by_region: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    candidate_slots = slots_by_region.get(event_region) or slots
    if not candidate_slots:
        return {
            "event_id": f"calendar-fallback-{event_name}",
            "event_name": event_name,
            "event_date": "",
            "region": event_region,
            "nearby_universities": "",
            "suggested_lecture_window": "",
            "course_alignment": "",
        }
    return candidate_slots[_stable_slot_index(event_name, len(candidate_slots))]


def _assignment_rows() -> list[dict[str, Any]]:
    slots, slots_by_region = _calendar_slots()
    event_by_name = _event_metadata()
    speaker_by_name = _speaker_metadata()
    pipeline_rows = load_pipeline_data()
    pipeline_df = pd.DataFrame(pipeline_rows)

    overlays: list[dict[str, Any]] = []
    for row in pipeline_rows:
        event_name = str(row.get("event_name", "")).strip()
        speaker_name = str(row.get("speaker_name", "")).strip()
        speaker_meta = speaker_by_name.get(speaker_name, {})
        event_meta = event_by_name.get(event_name, {})

        event_region = str(event_meta.get("region", "") or speaker_meta.get("speaker_region", ""))
        slot = _slot_for_event(event_name, event_region, slots, slots_by_region)
        recovery = volunteer_recovery_details(
            speaker_name=speaker_name,
            speaker_metro_region=str(speaker_meta.get("speaker_region", "") or ""),
            event_region=str(slot.get("region", event_region) or event_region),
            event_date_or_recurrence=event_meta.get("event_date_or_recurrence", ""),
            ia_event_calendar=pd.DataFrame(
                [
                    {"IA Event Date": calendar_slot["event_date"], "Region": calendar_slot["region"]}
                    for calendar_slot in slots
                ]
            ),
            pipeline_rows=pipeline_df,
        )

        overlays.append(
            {
                "assignment_id": f"{event_name}::{speaker_name}",
                "event_id": str(slot.get("event_id", "")),
                "event_name": event_name,
                "event_date": str(slot.get("event_date", "")),
                "calendar_event_date": str(slot.get("event_date", "")),
                "region": str(slot.get("region", event_region)),
                "calendar_region": str(slot.get("region", event_region)),
                "volunteer_name": speaker_name,
                "speaker_name": speaker_name,
                "volunteer_title": str(speaker_meta.get("volunteer_title", "")),
                "volunteer_company": str(speaker_meta.get("volunteer_company", "")),
                "speaker_region": str(speaker_meta.get("speaker_region", "")),
                "stage": str(row.get("stage", "Matched")),
                "stage_order": int(float(row.get("stage_order", 0) or 0)),
                "match_score": float(row.get("match_score", 0.0) or 0.0),
                "rank": int(float(row.get("rank", 0) or 0)),
                "travel_burden": float(recovery["travel_burden"]),
                "event_cadence": float(recovery["event_cadence"]),
                "recent_assignment_count": int(recovery["recent_assignment_count"]),
                "days_since_last_assignment": recovery["days_since_last_assignment"],
                "volunteer_fatigue": float(recovery["volunteer_fatigue"]),
                "recovery_status": str(recovery["recovery_status"]),
                "recovery_label": str(recovery["recovery_label"]),
            }
        )

    assignments_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for overlay in overlays:
        assignments_by_event[str(overlay["event_id"])].append(overlay)

    for overlay in overlays:
        related = assignments_by_event[str(overlay["event_id"])]
        stage_orders = [int(item.get("stage_order", 0) or 0) for item in related]
        coverage_ratio = round(sum(stage_orders) / max(len(stage_orders) * 4.0, 1.0), 4)
        coverage_status = _coverage_status(coverage_ratio)
        status_meta = _STATUS_META[coverage_status]
        overlay.update(
            {
                "coverage_status": coverage_status,
                "coverage_label": status_meta["label"],
                "status_color": status_meta["color"],
                "status_tone": status_meta["tone"],
                "coverage_ratio": coverage_ratio,
            }
        )

    return overlays


def _live_event_rows() -> list[dict[str, Any]]:
    slots, _ = _calendar_slots()
    assignments = _assignment_rows()
    assignments_by_event: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for assignment in assignments:
        assignments_by_event[str(assignment["event_id"])].append(assignment)

    rows: list[dict[str, Any]] = []
    for slot in slots:
        related = assignments_by_event.get(str(slot["event_id"]), [])
        stage_orders = [int(item.get("stage_order", 0) or 0) for item in related]
        coverage_ratio = round(sum(stage_orders) / max(len(stage_orders) * 4.0, 1.0), 4) if related else 0.0
        coverage_status = _coverage_status(coverage_ratio)
        status_meta = _STATUS_META[coverage_status]
        assigned_volunteers = sorted(
            {
                str(item.get("volunteer_name", ""))
                for item in related
                if str(item.get("volunteer_name", "")).strip()
            }
        )
        assignment_count = len(related)

        rows.append(
            {
                **slot,
                "coverage_status": coverage_status,
                "coverage_label": status_meta["label"],
                "coverage_ratio": coverage_ratio,
                "assigned_volunteers": assigned_volunteers,
                "assignment_count": assignment_count,
                "open_slots": max(0, 3 - assignment_count),
                "status_color": status_meta["color"],
            }
        )

    return rows


@router.get("/events")
async def events() -> list[dict[str, Any]]:
    """Return normalized calendar event rows with coverage metadata."""
    try:
        rows = load_live_calendar_events()
        if rows:
            return [{**row, "source": "live"} for row in rows]
    except Exception:
        pass
    try:
        rows = _live_event_rows()
        if rows:
            return rows
    except Exception:
        pass
    return _demo_rows(load_demo_calendar_events())


@router.get("/assignments")
async def assignments() -> list[dict[str, Any]]:
    """Return assignment overlays derived from the pipeline sample rows."""
    try:
        rows = load_live_calendar_assignments()
        if rows:
            return [{**row, "source": "live"} for row in rows]
    except Exception:
        pass
    try:
        rows = _assignment_rows()
        if rows:
            return rows
    except Exception:
        pass
    return _demo_rows(load_demo_calendar_assignments())
