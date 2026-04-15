"""Tests for outreach email voice routing."""

from src.outreach.email_voice import resolve_email_voice


def test_explicit_voice_overrides_source() -> None:
    assert resolve_email_voice(voice="ia_west_chapter", request_source="coordinator_portal") == "ia_west_chapter"
    assert resolve_email_voice(voice="school_coordinator", request_source="ia_west_admin") == "school_coordinator"


def test_coordinator_portal_defaults_school() -> None:
    assert resolve_email_voice(voice=None, request_source="coordinator_portal") == "school_coordinator"


def test_ia_west_admin_defaults_chapter() -> None:
    assert resolve_email_voice(voice=None, request_source="ia_west_admin") == "ia_west_chapter"


def test_unknown_source_defaults_school() -> None:
    assert resolve_email_voice(voice=None, request_source=None) == "school_coordinator"
