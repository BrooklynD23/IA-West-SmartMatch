"""Helpers for loading demo fallback data from the seeded SQLite database."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_DEMO_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "demo.db"
)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(str(_DEMO_DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection


def _decode_json_fields(
    record: dict[str, Any],
    *,
    fields: tuple[str, ...] = (),
) -> dict[str, Any]:
    decoded = dict(record)
    for field in fields:
        value = decoded.get(field)
        if not isinstance(value, str) or not value:
            continue
        try:
            decoded[field] = json.loads(value)
        except json.JSONDecodeError:
            continue
    return decoded


def _load_rows(
    query: str,
    *,
    json_fields: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    with _connect() as connection:
        rows = connection.execute(query).fetchall()
    return [_decode_json_fields(dict(row), fields=json_fields) for row in rows]


def _load_json_payload(query: str) -> dict[str, Any]:
    with _connect() as connection:
        row = connection.execute(query).fetchone()
    if row is None:
        return {}
    payload = dict(row).get("payload_json")
    if not isinstance(payload, str) or not payload:
        return {}
    return json.loads(payload)


def load_demo_specialists() -> list[dict[str, Any]]:
    return _load_rows("SELECT * FROM specialists ORDER BY name")


def load_demo_cpp_events() -> list[dict[str, Any]]:
    return _load_rows('SELECT * FROM cpp_events ORDER BY "Event / Program"')


def load_demo_pipeline() -> list[dict[str, Any]]:
    return _load_rows(
        "SELECT * FROM pipeline ORDER BY CAST(stage_order AS INTEGER), CAST(rank AS INTEGER), speaker_name"
    )


def load_demo_event_calendar() -> list[dict[str, Any]]:
    return _load_rows('SELECT * FROM event_calendar ORDER BY "IA Event Date"')


def load_demo_calendar_events() -> list[dict[str, Any]]:
    return _load_rows(
        "SELECT * FROM calendar_events ORDER BY event_date, event_name",
        json_fields=("nearby_universities", "assigned_volunteers"),
    )


def load_demo_calendar_assignments() -> list[dict[str, Any]]:
    return _load_rows(
        "SELECT * FROM calendar_assignments ORDER BY event_date, event_name, rank"
    )


def load_demo_qr_stats() -> dict[str, Any]:
    return _load_json_payload(
        "SELECT payload_json FROM qr_stats ORDER BY id DESC LIMIT 1"
    )


def load_demo_feedback_stats() -> dict[str, Any]:
    return _load_json_payload(
        "SELECT payload_json FROM feedback_stats ORDER BY id DESC LIMIT 1"
    )


def load_demo_students() -> list[dict[str, Any]]:
    """Return all students from demo.db, or empty list if unavailable."""
    try:
        return _load_rows("SELECT * FROM students ORDER BY name")
    except Exception:
        return []


def load_demo_mock_roles() -> list[dict[str, Any]]:
    """Return all mock role personas from demo.db, or empty list if unavailable."""
    try:
        return _load_rows("SELECT * FROM mock_roles ORDER BY email")
    except Exception:
        return []


def load_demo_event_coordinators() -> list[dict[str, Any]]:
    """Return all event coordinators from demo.db, or empty list if unavailable."""
    try:
        return _load_rows("SELECT * FROM event_coordinators ORDER BY name")
    except Exception:
        return []


def load_demo_student_registrations(student_id: str | None = None) -> list[dict[str, Any]]:
    """Return student registrations, optionally filtered by student_id."""
    try:
        if student_id:
            with _connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        sr.*,
                        ce.event_date AS event_date
                    FROM student_registrations sr
                    LEFT JOIN calendar_events ce
                        ON ce.event_id = sr.event_id
                    WHERE sr.student_id = ?
                    ORDER BY sr.registered_at DESC
                    """,
                    (student_id,),
                ).fetchall()
            return [dict(row) for row in rows]
        return _load_rows(
            """
            SELECT
                sr.*,
                ce.event_date AS event_date
            FROM student_registrations sr
            LEFT JOIN calendar_events ce
                ON ce.event_id = sr.event_id
            ORDER BY sr.registered_at DESC
            """
        )
    except Exception:
        return []


def load_demo_outreach_threads(coordinator_id: str | None = None) -> list[dict[str, Any]]:
    """Return outreach threads, optionally filtered by coordinator_id."""
    try:
        if coordinator_id:
            with _connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM outreach_threads WHERE coordinator_id = ? ORDER BY last_message_at DESC",
                    (coordinator_id,),
                ).fetchall()
            return [dict(row) for row in rows]
        return _load_rows("SELECT * FROM outreach_threads ORDER BY last_message_at DESC")
    except Exception:
        return []


def load_demo_meeting_bookings(coordinator_id: str | None = None) -> list[dict[str, Any]]:
    """Return meeting bookings, optionally filtered by coordinator_id."""
    try:
        if coordinator_id:
            with _connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM meeting_bookings WHERE coordinator_id = ? ORDER BY scheduled_at",
                    (coordinator_id,),
                ).fetchall()
            return [dict(row) for row in rows]
        return _load_rows("SELECT * FROM meeting_bookings ORDER BY scheduled_at")
    except Exception:
        return []


def _attended_event_map(registrations: list[dict[str, Any]], student_id: str) -> dict[str, str]:
    """Map event_id -> event_name for rows where this student attended (check-in completed)."""
    out: dict[str, str] = {}
    for row in registrations:
        if str(row.get("student_id") or "") != student_id:
            continue
        if str(row.get("status") or "").casefold() != "attended":
            continue
        eid = row.get("event_id")
        if not eid:
            continue
        eid_s = str(eid)
        out[eid_s] = str(row.get("event_name") or eid_s)
    return out


def load_demo_student_connection_suggestions(student_id: str) -> dict[str, Any]:
    """Peers who share at least one attended event with ``student_id``, ranked by overlap count."""
    try:
        students = load_demo_students()
    except Exception:
        students = []

    valid_ids = {str(s.get("student_id")) for s in students if s.get("student_id")}
    if student_id not in valid_ids:
        return {
            "student_id": student_id,
            "attended_past_events": [],
            "suggestions": [],
            "total": 0,
            "source": "demo",
        }

    try:
        all_regs = load_demo_student_registrations()
    except Exception:
        all_regs = []

    self_events = _attended_event_map(all_regs, student_id)
    attended_past_events = [
        {"event_id": eid, "event_name": name} for eid, name in sorted(self_events.items(), key=lambda x: x[1].casefold())
    ]

    suggestions: list[dict[str, Any]] = []
    student_by_id = {str(s.get("student_id")): s for s in students if s.get("student_id")}

    for peer_id, peer in student_by_id.items():
        if peer_id == student_id:
            continue
        peer_events = _attended_event_map(all_regs, peer_id)
        shared_ids = sorted(set(self_events) & set(peer_events))
        if not shared_ids:
            continue
        shared_events = [
            {
                "event_id": eid,
                "event_name": self_events.get(eid) or peer_events.get(eid) or eid,
            }
            for eid in shared_ids
        ]
        suggestions.append(
            {
                "peer_student_id": peer_id,
                "name": peer.get("name"),
                "school": peer.get("school"),
                "major": peer.get("major"),
                "interests": peer.get("interests"),
                "shared_events": shared_events,
                "shared_event_count": len(shared_events),
            }
        )

    suggestions.sort(key=lambda s: (-int(s.get("shared_event_count") or 0), str(s.get("name") or "")))

    return {
        "student_id": student_id,
        "attended_past_events": attended_past_events,
        "suggestions": suggestions,
        "total": len(suggestions),
        "source": "demo",
    }


def load_demo_retention_nudges(student_id: str | None = None) -> list[dict[str, Any]]:
    """Return retention nudges, optionally filtered by student_id."""
    try:
        if student_id:
            with _connect() as connection:
                rows = connection.execute(
                    "SELECT * FROM retention_nudges WHERE student_id = ?",
                    (student_id,),
                ).fetchall()
            return [dict(row) for row in rows]
        return _load_rows("SELECT * FROM retention_nudges")
    except Exception:
        return []

