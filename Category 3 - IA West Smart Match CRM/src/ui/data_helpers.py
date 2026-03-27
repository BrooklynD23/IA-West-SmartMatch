"""Data loading and formatting functions for UI templates.

This module decouples data loading from page rendering. Each UI page
imports helpers from here and receives pre-formatted data ready for
string interpolation into HTML templates.

All functions cache their results to avoid redundant disk reads.
Missing data files are handled gracefully: an empty list is returned
and a warning is emitted via the standard logging module.
"""

from __future__ import annotations

import csv
import functools
import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


def _data_dir() -> Path:
    """Return the ``data/`` directory path relative to the project root."""
    return Path(__file__).resolve().parent.parent.parent / "data"


def get_initials(name: str) -> str:
    """Return uppercase initials derived from a full name.

    Examples::

        >>> get_initials("Travis Miller")
        'TM'
        >>> get_initials("Dr. Yufan Lin")
        'DYL'
    """
    parts = name.split()
    return "".join(part[0].upper() for part in parts if part)


# ---------------------------------------------------------------------------
# Internal cached loaders (return tuples so lru_cache works on unhashable
# list results without losing the public list[dict] API).
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _load_specialists_cached() -> tuple[dict[str, str], ...]:
    csv_path = _data_dir() / "data_speaker_profiles.csv"
    try:
        with csv_path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        _log.warning("data file not found: %s", csv_path)
        return ()
    result: list[dict[str, str]] = []
    for row in rows:
        result.append(
            {
                "name": row.get("Name", ""),
                "board_role": row.get("Board Role", ""),
                "metro_region": row.get("Metro Region", ""),
                "company": row.get("Company", ""),
                "title": row.get("Title", ""),
                "expertise_tags": row.get("Expertise Tags", ""),
                "initials": get_initials(row.get("Name", "")),
            }
        )
    return tuple(result)


@functools.lru_cache(maxsize=1)
def _load_poc_contacts_cached() -> tuple[Any, ...]:
    json_path = _data_dir() / "poc_contacts.json"
    try:
        with json_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        _log.warning("data file not found: %s", json_path)
        return ()
    return tuple(data)


@functools.lru_cache(maxsize=1)
def _load_pipeline_data_cached() -> tuple[dict[str, str], ...]:
    csv_path = _data_dir() / "pipeline_sample_data.csv"
    try:
        with csv_path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        _log.warning("data file not found: %s", csv_path)
        return ()
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _load_event_calendar_cached() -> tuple[dict[str, str], ...]:
    csv_path = _data_dir() / "data_event_calendar.csv"
    try:
        with csv_path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        _log.warning("data file not found: %s", csv_path)
        return ()
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _load_cpp_events_cached() -> tuple[dict[str, str], ...]:
    csv_path = _data_dir() / "data_cpp_events_contacts.csv"
    try:
        with csv_path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
    except FileNotFoundError:
        _log.warning("data file not found: %s", csv_path)
        return ()
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _load_qr_manifest_cached() -> tuple[dict[str, Any], ...]:
    json_path = _data_dir() / "qr" / "manifest.json"
    try:
        with json_path.open(encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        return ()
    except json.JSONDecodeError:
        _log.warning("qr manifest is malformed: %s", json_path)
        return ()

    records = payload.get("records", []) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        return ()
    return tuple(record for record in records if isinstance(record, dict))


@functools.lru_cache(maxsize=1)
def _load_qr_scan_log_cached() -> tuple[dict[str, Any], ...]:
    jsonl_path = _data_dir() / "qr" / "scan-log.jsonl"
    try:
        with jsonl_path.open(encoding="utf-8") as fh:
            rows = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    _log.warning("qr scan log entry is malformed: %s", jsonl_path)
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except FileNotFoundError:
        return ()
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _load_feedback_log_cached() -> tuple[dict[str, Any], ...]:
    jsonl_path = _data_dir() / "feedback" / "feedback-log.jsonl"
    try:
        with jsonl_path.open(encoding="utf-8") as fh:
            rows = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    _log.warning("feedback log entry is malformed: %s", jsonl_path)
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except FileNotFoundError:
        return ()
    return tuple(rows)


@functools.lru_cache(maxsize=1)
def _load_weight_history_cached() -> tuple[dict[str, Any], ...]:
    json_path = _data_dir() / "feedback" / "weight-history.json"
    try:
        with json_path.open(encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        return ()
    except json.JSONDecodeError:
        _log.warning("weight history is malformed: %s", json_path)
        return ()

    snapshots = payload.get("snapshots", []) if isinstance(payload, dict) else payload
    if not isinstance(snapshots, list):
        return ()
    return tuple(snapshot for snapshot in snapshots if isinstance(snapshot, dict))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_specialists() -> list[dict[str, str]]:
    """Load specialist profiles from ``data_speaker_profiles.csv``.

    Returns a list of dicts with keys: ``name``, ``board_role``,
    ``metro_region``, ``company``, ``title``, ``expertise_tags``,
    ``initials``.

    Returns an empty list if the file is missing.
    """
    return list(_load_specialists_cached())


def load_poc_contacts() -> list[dict]:
    """Load POC contacts from ``poc_contacts.json``.

    Returns the parsed JSON array as a list of dicts.
    Returns an empty list if the file is missing.
    """
    return list(_load_poc_contacts_cached())


def load_pipeline_data() -> list[dict[str, str]]:
    """Load pipeline data from ``pipeline_sample_data.csv``.

    Returns a list of dicts with keys matching the CSV columns:
    ``event_name``, ``speaker_name``, ``match_score``, ``rank``,
    ``stage``, ``stage_order``.

    Returns an empty list if the file is missing.
    """
    return list(_load_pipeline_data_cached())


def load_event_calendar() -> list[dict[str, str]]:
    """Load event calendar from ``data_event_calendar.csv``.

    Returns a list of dicts with keys matching the CSV columns.
    Returns an empty list if the file is missing.
    """
    return list(_load_event_calendar_cached())


def load_cpp_events() -> list[dict[str, str]]:
    """Load CPP events from ``data_cpp_events_contacts.csv``.

    Returns a list of dicts with keys matching the CSV columns.
    Returns an empty list if the file is missing.
    """
    return list(_load_cpp_events_cached())


def load_qr_manifest() -> list[dict[str, Any]]:
    """Load the QR manifest records from ``data/qr/manifest.json``."""
    return list(_load_qr_manifest_cached())


def load_qr_scan_log() -> list[dict[str, Any]]:
    """Load the append-only QR scan log from ``data/qr/scan-log.jsonl``."""
    return list(_load_qr_scan_log_cached())


def load_feedback_log() -> list[dict[str, Any]]:
    """Load the append-only feedback log from ``data/feedback/feedback-log.jsonl``."""
    return list(_load_feedback_log_cached())


def load_weight_history() -> list[dict[str, Any]]:
    """Load optimizer snapshots from ``data/feedback/weight-history.json``."""
    return list(_load_weight_history_cached())


def get_event_by_name(event_name: str) -> dict[str, str] | None:
    """Find a CPP event row by its ``Event / Program`` column value.

    Uses substring matching so that partial event names (e.g. from
    pipeline data) can find their full CPP event row.

    Returns the first matching dict, or None if not found.
    """
    cpp_events = load_cpp_events()
    for row in cpp_events:
        if row.get("Event / Program", "") == event_name:
            return dict(row)
    # Fallback: substring match
    for row in cpp_events:
        if event_name in row.get("Event / Program", ""):
            return dict(row)
    return None


def get_top_specialists_for_event(
    event_name: str, limit: int = 3
) -> list[dict]:
    """Return the top-ranked specialist matches for a given event.

    Filters ``pipeline_sample_data.csv`` rows by *event_name*, sorts
    by ``match_score`` descending, takes the top *limit* entries, and
    enriches each with specialist profile data (``company``, ``title``,
    ``expertise_tags``, ``initials``).

    Args:
        event_name: Exact event name string to filter on.
        limit: Maximum number of specialists to return (default 3).

    Returns:
        List of dicts with keys: ``name``, ``match_score``, ``rank``,
        ``stage``, ``company``, ``title``, ``expertise_tags``,
        ``initials``.
    """
    pipeline = load_pipeline_data()
    specialists_by_name = {s["name"]: s for s in load_specialists()}

    matches = [row for row in pipeline if row.get("event_name") == event_name]
    matches_sorted = sorted(
        matches,
        key=lambda r: float(r.get("match_score", 0)),
        reverse=True,
    )

    result: list[dict] = []
    for row in matches_sorted[:limit]:
        speaker_name = row.get("speaker_name", "")
        profile = specialists_by_name.get(speaker_name, {})
        result.append(
            {
                "name": speaker_name,
                "match_score": row.get("match_score", ""),
                "rank": row.get("rank", ""),
                "stage": row.get("stage", ""),
                "company": profile.get("company", ""),
                "title": profile.get("title", ""),
                "expertise_tags": profile.get("expertise_tags", ""),
                "initials": profile.get("initials", get_initials(speaker_name)),
            }
        )
    return result


def get_recent_poc_activity(limit: int = 5) -> list[dict]:
    """Return the most recent POC communication history entries.

    Flattens all ``comm_history`` entries across all POC contacts,
    sorts by date descending, and returns the top *limit* entries.

    Args:
        limit: Maximum number of activity entries to return (default 5).

    Returns:
        List of dicts with keys: ``poc_name``, ``org``, ``date``,
        ``type``, ``summary``.
    """
    contacts = load_poc_contacts()

    all_activity: list[dict] = []
    for contact in contacts:
        poc_name = contact.get("name", "")
        org = contact.get("org", "")
        for entry in contact.get("comm_history", []):
            all_activity.append(
                {
                    "poc_name": poc_name,
                    "org": org,
                    "date": entry.get("date", ""),
                    "type": entry.get("type", ""),
                    "summary": entry.get("summary", ""),
                }
            )

    all_activity_sorted = sorted(
        all_activity,
        key=lambda e: e.get("date", ""),
        reverse=True,
    )
    return all_activity_sorted[:limit]
