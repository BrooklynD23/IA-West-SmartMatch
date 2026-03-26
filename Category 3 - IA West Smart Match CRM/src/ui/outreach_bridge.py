"""Data bridge between match engine specialist dicts and outreach tool params.

Pure-function module — no Streamlit imports, testable in isolation.
Transforms the simplified specialist dicts from get_top_specialists_for_event()
into the shape expected by outreach_tool.run() / generate_outreach_email().
"""

from __future__ import annotations

from typing import Any

from src.ui.data_helpers import get_event_by_name, load_specialists


# ---------------------------------------------------------------------------
# Display-key → canonical factor key mapping
# ---------------------------------------------------------------------------

_DISPLAY_TO_CANONICAL: dict[str, str] = {
    "Topic": "topic_relevance",
    "Role": "role_fit",
    "Proximity": "geographic_proximity",
    "Calendar": "calendar_fit",
    "History": "historical_conversion",
    "Impact": "student_interest",
}


def build_speaker_dict(
    spec: dict[str, Any],
    specialists: list[dict[str, str]] | None = None,
) -> dict[str, str]:
    """Build the speaker dict expected by generate_outreach_email().

    Looks up the full specialist profile by name to get board_role and
    metro_region, which are not present in the simplified match engine dicts.

    Args:
        spec: Simplified specialist dict from get_top_specialists_for_event().
        specialists: Optional pre-loaded specialist list (avoids re-read).

    Returns:
        Dict with keys: Name, Title, Company, Board Role, Metro Region,
        Expertise Tags.
    """
    if specialists is None:
        specialists = load_specialists()

    profiles_by_name = {s["name"]: s for s in specialists}
    name = spec.get("name", "")
    profile = profiles_by_name.get(name, {})

    return {
        "Name": name,
        "Title": spec.get("title", "") or profile.get("title", ""),
        "Company": spec.get("company", "") or profile.get("company", ""),
        "Board Role": profile.get("board_role", ""),
        "Metro Region": profile.get("metro_region", ""),
        "Expertise Tags": spec.get("expertise_tags", "") or profile.get("expertise_tags", ""),
    }


def build_event_dict(event_name: str) -> dict[str, str]:
    """Build the event dict expected by generate_outreach_email().

    Looks up the CPP event row by name. Returns a fallback dict with
    just the event name if no match is found.

    Args:
        event_name: The event name to look up.

    Returns:
        Dict with CSV column keys from data_cpp_events_contacts.csv,
        or a minimal fallback dict.
    """
    row = get_event_by_name(event_name)
    if row is not None:
        return row
    return {"Event / Program": event_name}


def build_match_scores(
    spec: dict[str, Any],
    factor_scores: dict[str, int],
) -> dict[str, Any]:
    """Build the match_scores dict expected by generate_outreach_email().

    Maps display keys (Topic, Role, etc.) to canonical keys
    (topic_relevance, role_fit, etc.) and normalizes 0-100 scale to 0.0-1.0.

    Args:
        spec: Specialist dict containing match_score (0.0-1.0 float string).
        factor_scores: Display-key factor scores on 0-100 int scale.

    Returns:
        Dict with total_score (float) and factor_scores sub-dict.
    """
    try:
        total = float(spec.get("match_score", 0))
    except (ValueError, TypeError):
        total = 0.8

    canonical_factors: dict[str, float] = {}
    for display_key, canonical_key in _DISPLAY_TO_CANONICAL.items():
        raw = factor_scores.get(display_key, 0)
        canonical_factors[canonical_key] = raw / 100.0

    return {
        "total_score": total,
        "factor_scores": canonical_factors,
    }


def build_outreach_params(
    spec: dict[str, Any],
    event_name: str,
    factor_scores: dict[str, int],
    specialists: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Compose all bridge functions into the params dict for outreach_tool.run().

    Args:
        spec: Simplified specialist dict from get_top_specialists_for_event().
        event_name: Event name string.
        factor_scores: Display-key factor scores on 0-100 int scale.
        specialists: Optional pre-loaded specialist list.

    Returns:
        Dict with keys: speaker, event, match_scores — the exact shape
        expected by outreach_tool.run().
    """
    return {
        "speaker": build_speaker_dict(spec, specialists),
        "event": build_event_dict(event_name),
        "match_scores": build_match_scores(spec, factor_scores),
    }
