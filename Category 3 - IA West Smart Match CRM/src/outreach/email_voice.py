"""Routing for outreach email generation voice / sender perspective.

Callers identify *where* the request originates; we map that to an :class:`EmailVoice`
unless the client sends an explicit ``voice`` override.
"""

from __future__ import annotations

from typing import Literal

EmailVoice = Literal["school_coordinator", "ia_west_chapter"]

VALID_VOICES: tuple[EmailVoice, ...] = ("school_coordinator", "ia_west_chapter")

# Request-source hints (HTTP / tool); extensible without breaking clients.
REQUEST_COORDINATOR_PORTAL = "coordinator_portal"
REQUEST_IA_WEST_ADMIN = "ia_west_admin"
REQUEST_AGENTIC_DEMO = "agentic_coordinator_demo"


def normalize_voice(value: str | None) -> EmailVoice | None:
    """Return a canonical voice if *value* is valid, else ``None``."""
    if value is None:
        return None
    v = value.strip().lower().replace("-", "_")
    if v in ("school_coordinator", "school", "campus_coordinator"):
        return "school_coordinator"
    if v in ("ia_west_chapter", "ia_west", "chapter_leadership", "ia_west_admin"):
        return "ia_west_chapter"
    return None


def resolve_email_voice(*, voice: str | None, request_source: str | None) -> EmailVoice:
    """Pick the email voice: explicit ``voice`` wins, then ``request_source``, then default.

    Defaults to *school_coordinator* so unknown callers do not impersonate IA West.
    """
    explicit = normalize_voice(voice)
    if explicit is not None:
        return explicit

    src = (request_source or "").strip().lower()
    if src in (REQUEST_IA_WEST_ADMIN, "admin", "ia_admin", "dashboard"):
        return "ia_west_chapter"
    if src in (
        REQUEST_COORDINATOR_PORTAL,
        REQUEST_AGENTIC_DEMO,
        "coordinator",
        "event_coordinator",
    ):
        return "school_coordinator"

    return "school_coordinator"
