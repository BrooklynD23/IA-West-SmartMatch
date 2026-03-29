"""Helpers for loading live data from the persistent smartmatch SQLite database.

This is the Layer 0 reader module. All public functions attempt to load from
``data/smartmatch.db``. Callers should fall back to demo_db (Layer 1) then
CSV loaders (Layer 2) when this module raises an exception.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_SMARTMATCH_DB_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "smartmatch.db"
)


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(str(_SMARTMATCH_DB_PATH))
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


def load_live_specialists() -> list[dict[str, Any]]:
    """Return all specialist rows from smartmatch.db ordered by name."""
    return _load_rows("SELECT * FROM specialists ORDER BY name")


def load_live_cpp_events() -> list[dict[str, Any]]:
    """Return all CPP event rows from smartmatch.db ordered by event/program name."""
    return _load_rows('SELECT * FROM cpp_events ORDER BY "Event / Program"')


def load_live_pipeline() -> list[dict[str, Any]]:
    """Return pipeline rows from smartmatch.db ordered by stage then rank."""
    return _load_rows(
        "SELECT * FROM pipeline ORDER BY CAST(stage_order AS INTEGER), CAST(rank AS INTEGER), speaker_name"
    )


def load_live_event_calendar() -> list[dict[str, Any]]:
    """Return event calendar rows from smartmatch.db ordered by IA Event Date."""
    return _load_rows('SELECT * FROM event_calendar ORDER BY "IA Event Date"')


def load_live_calendar_events() -> list[dict[str, Any]]:
    """Return calendar event rows from smartmatch.db with JSON field decoding."""
    return _load_rows(
        "SELECT * FROM calendar_events ORDER BY event_date, event_name",
        json_fields=("nearby_universities", "assigned_volunteers"),
    )


def load_live_calendar_assignments() -> list[dict[str, Any]]:
    """Return calendar assignment rows from smartmatch.db ordered by date, event, rank."""
    return _load_rows(
        "SELECT * FROM calendar_assignments ORDER BY event_date, event_name, rank"
    )


def load_live_qr_stats() -> dict[str, Any]:
    """Return the latest QR stats payload from smartmatch.db."""
    return _load_json_payload(
        "SELECT payload_json FROM qr_stats ORDER BY id DESC LIMIT 1"
    )


def load_live_feedback_stats() -> dict[str, Any]:
    """Return the latest feedback stats payload from smartmatch.db."""
    return _load_json_payload(
        "SELECT payload_json FROM feedback_stats ORDER BY id DESC LIMIT 1"
    )


def load_live_poc_contacts() -> list[dict[str, Any]]:
    """Return point-of-contact rows from smartmatch.db with comm_history decoded."""
    return _load_rows(
        "SELECT * FROM poc_contacts ORDER BY name",
        json_fields=("comm_history",),
    )


def load_crawler_events() -> list[dict[str, Any]]:
    """Return web crawler event rows from smartmatch.db ordered by crawl timestamp."""
    return _load_rows(
        "SELECT * FROM web_crawler_events ORDER BY crawled_at DESC"
    )


def delete_all_crawler_events() -> int:
    """Delete all rows from web_crawler_events. Returns the number of rows deleted."""
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM web_crawler_events")
        conn.commit()
        return cursor.rowcount


def insert_crawler_event(event: dict[str, Any]) -> None:
    """Insert a single web crawler event record into smartmatch.db.

    Required keys in event: url, title, description, school_name, crawled_at,
    source, status.
    """
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO web_crawler_events (
                url, title, description, school_name, crawled_at, source, status
            ) VALUES (
                :url, :title, :description, :school_name, :crawled_at, :source, :status
            )
            """,
            event,
        )
        conn.commit()
