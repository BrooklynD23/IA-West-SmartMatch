"""Outreach tool wrapper — thin adapter over generate_outreach_email().

No Streamlit imports.
"""

from __future__ import annotations

from typing import Any

from src.outreach.email_gen import generate_outreach_email
from src.outreach.email_voice import resolve_email_voice

TOOL_NAME: str = "generate_outreach"

_REQUIRED_KEYS: tuple[str, ...] = ("speaker", "event", "match_scores")


def run(params: dict[str, Any]) -> dict[str, Any]:
    """Run outreach email generation for a speaker-event match.

    Args:
        params: Must contain "speaker", "event", "match_scores".

    Returns:
        {"status": "ok", "email": {...}} on success.
        {"status": "error", "error": "Missing required param: <key>"} if a
        required param is absent.
    """
    for key in _REQUIRED_KEYS:
        if key not in params:
            return {"status": "error", "error": f"Missing required param: {key}"}

    voice = resolve_email_voice(
        voice=params.get("voice") if isinstance(params.get("voice"), str) else None,
        request_source=params.get("request_source") if isinstance(params.get("request_source"), str) else None,
    )
    email = generate_outreach_email(
        speaker=params["speaker"],
        event=params["event"],
        match_scores=params["match_scores"],
        voice=voice,
    )
    return {"status": "ok", "email": email}
