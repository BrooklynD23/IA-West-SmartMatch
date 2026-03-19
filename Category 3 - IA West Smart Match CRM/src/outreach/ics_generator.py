"""Calendar invite (.ics) generation for matched events.

Pure Python RFC 5545 string building — no external icalendar library required.
Generates downloadable .ics files with VEVENT fields for matched events.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

ICS_CONTENT_TYPE: str = "text/calendar"

_DEFAULT_DURATION_HOURS: int = 1


def _parse_date(date_str: Optional[str]) -> datetime:
    """Parse a date string into a datetime, falling back to 30 days from now.

    Handles ISO formats (YYYY-MM-DD) and falls back gracefully for
    unparseable strings like "Every Tuesday".
    """
    if date_str is None:
        return datetime.now(UTC) + timedelta(days=30)

    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    logger.warning("Could not parse date '%s', using 30-day default", date_str)
    return datetime.now(UTC) + timedelta(days=30)


def _make_uid(event_name: str, date_str: Optional[str]) -> str:
    """Generate a deterministic UID from event_name + date_str."""
    raw = f"{event_name}|{date_str or ''}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{digest}@ia-smartmatch.local"


def _escape_ics_text(text: str) -> str:
    """Escape special characters per RFC 5545 TEXT rules."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def generate_ics(
    event_name: str,
    date_str: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """Generate an RFC 5545 .ics calendar invite string.

    Parameters
    ----------
    event_name : str
        Name of the event (used as SUMMARY).
    date_str : str or None
        Date string (e.g. "2026-04-15"). Falls back to 30 days from now
        if None or unparseable.
    location : str or None
        Event location. Omitted from output if None.
    description : str or None
        Event description. Omitted from output if None.

    Returns
    -------
    str
        The .ics file content as a string, ready for download.
    """
    dt_start = _parse_date(date_str)
    dt_end = dt_start + timedelta(hours=_DEFAULT_DURATION_HOURS)

    uid = _make_uid(event_name, date_str)
    dtstamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    dtstart = dt_start.strftime("%Y%m%dT%H%M%SZ")
    dtend = dt_end.strftime("%Y%m%dT%H%M%SZ")

    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//IA SmartMatch//Event Invite//EN",
        "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{_escape_ics_text(event_name)}",
    ]

    if location is not None:
        lines.append(f"LOCATION:{_escape_ics_text(location)}")

    if description is not None:
        lines.append(f"DESCRIPTION:{_escape_ics_text(description)}")

    lines.extend([
        "END:VEVENT",
        "END:VCALENDAR",
    ])

    return "\r\n".join(lines) + "\r\n"
