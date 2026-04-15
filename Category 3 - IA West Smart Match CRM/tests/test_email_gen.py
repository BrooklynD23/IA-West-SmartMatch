"""Tests for outreach email generation (A2.4)."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_speaker(**overrides: Any) -> dict[str, Any]:
    """Return a canonical speaker profile for tests."""
    base: dict[str, Any] = {
        "Name": "Alice Johnson",
        "Title": "VP, Data Science",
        "Company": "Acme Analytics",
        "Board Role": "Director",
        "Metro Region": "Los Angeles — East",
        "Expertise Tags": "AI, machine learning, market research",
    }
    return {**base, **overrides}


def _make_event(**overrides: Any) -> dict[str, Any]:
    """Return a canonical event dict for tests."""
    base: dict[str, Any] = {
        "Event / Program": "AI for a Better Future Hackathon",
        "Category": "AI / Hackathon",
        "Host / Unit": "Cal Poly Pomona",
        "Volunteer Roles (fit)": "Judge; Mentor",
        "Primary Audience": "Students (business/tech)",
        "IA Event Date": "2026-04-15",
    }
    return {**base, **overrides}


def _make_match_scores(**overrides: Any) -> dict[str, Any]:
    """Return canonical match scores for tests."""
    base: dict[str, Any] = {
        "total_score": 0.87,
        "factor_scores": {
            "topic_relevance": 0.90,
            "role_fit": 0.80,
            "geographic_proximity": 0.75,
            "calendar_fit": 0.70,
            "historical_conversion": 0.50,
            "student_interest": 0.60,
        },
    }
    return {**base, **overrides}


FAKE_LLM_RESPONSE = json.dumps({
    "subject_line": "Volunteer Opportunity: Judge at AI Hackathon",
    "greeting": "Dear Alice,",
    "body": "Your expertise in AI makes you a great fit.",
    "closing": "Best regards,\nIA West Leadership",
    "full_email": (
        "Subject: Volunteer Opportunity: Judge at AI Hackathon\n\n"
        "Dear Alice,\n\n"
        "Your expertise in AI makes you a great fit.\n\n"
        "Best regards,\nIA West Leadership"
    ),
})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGenerateOutreachEmail:
    """Core email generation tests."""

    def test_generate_email_returns_all_fields(self, tmp_path: Path) -> None:
        """generate_outreach_email returns dict with all required keys."""
        from src.outreach.email_gen import generate_outreach_email

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", return_value=FAKE_LLM_RESPONSE):
            result = generate_outreach_email(
                _make_speaker(),
                _make_event(),
                _make_match_scores(),
            )

        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        assert required_keys.issubset(result.keys())
        assert result["subject_line"] != ""
        assert result["greeting"] != ""
        assert result["body"] != ""
        assert result["full_email"] != ""

    def test_generate_email_uses_cache(self, tmp_path: Path) -> None:
        """Second call uses cache, not LLM."""
        from src.outreach.email_gen import (
            EMAIL_CACHE_DIR,
            generate_outreach_email,
        )

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", return_value=FAKE_LLM_RESPONSE) as mock_gen:
            speaker = _make_speaker()
            event = _make_event()
            scores = _make_match_scores()

            first = generate_outreach_email(speaker, event, scores)
            second = generate_outreach_email(speaker, event, scores)

        # generate_text should be called only once (second call uses cache)
        assert mock_gen.call_count == 1
        assert first == second

    def test_generate_email_fallback_on_api_error(self, tmp_path: Path) -> None:
        """Falls back to template email when LLM raises an exception."""
        from src.outreach.email_gen import generate_outreach_email

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", side_effect=RuntimeError("API down")):
            result = generate_outreach_email(
                _make_speaker(),
                _make_event(),
                _make_match_scores(),
            )

        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        assert required_keys.issubset(result.keys())
        assert "Alice Johnson" in result["greeting"]
        assert "AI for a Better Future Hackathon" in result["full_email"]

    def test_prompt_includes_speaker_and_event_details(self, tmp_path: Path) -> None:
        """The LLM prompt includes speaker name, expertise, and event name."""
        from src.outreach.email_gen import generate_outreach_email

        captured_messages: list[Any] = []
        captured_system: list[str] = []

        def capture_generate_text(messages: Any, **kwargs: Any) -> str:
            captured_messages.extend(messages)
            captured_system.append(str(kwargs.get("system_instruction", "")))
            return FAKE_LLM_RESPONSE

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", side_effect=capture_generate_text):
            generate_outreach_email(
                _make_speaker(),
                _make_event(),
                _make_match_scores(),
            )

        # The user message should contain speaker and event details
        user_messages = [m for m in captured_messages if m.get("role") == "user"]
        assert len(user_messages) >= 1
        user_content = user_messages[-1]["content"]
        assert "Alice Johnson" in user_content
        assert "AI, machine learning, market research" in user_content
        assert "AI for a Better Future Hackathon" in user_content
        assert "87%" in user_content  # match score as percentage
        assert "Cal Poly Pomona" in user_content
        assert "school or campus event coordinator" in user_content
        assert captured_system and "school" in captured_system[0].lower()
        assert "not an ia west administrator" in captured_system[0].lower()


class TestEmailCacheKey:
    """Cache key determinism tests."""

    def test_email_cache_key_deterministic(self) -> None:
        """Same inputs always produce the same cache key."""
        from src.outreach.email_gen import _email_cache_key

        speaker = _make_speaker()
        event = _make_event()
        scores = _make_match_scores()

        key1 = _email_cache_key(speaker, event, scores, "school_coordinator")
        key2 = _email_cache_key(speaker, event, scores, "school_coordinator")
        assert key1 == key2

    def test_different_speakers_produce_different_keys(self) -> None:
        """Different speaker names produce different cache keys."""
        from src.outreach.email_gen import _email_cache_key

        event = _make_event()
        scores = _make_match_scores()

        key1 = _email_cache_key(_make_speaker(Name="Alice"), event, scores, "school_coordinator")
        key2 = _email_cache_key(_make_speaker(Name="Bob"), event, scores, "school_coordinator")
        assert key1 != key2

    def test_different_events_produce_different_keys(self) -> None:
        """Different event names produce different cache keys."""
        from src.outreach.email_gen import _email_cache_key

        speaker = _make_speaker()
        scores = _make_match_scores()

        key1 = _email_cache_key(speaker, _make_event(**{"Event / Program": "Event A"}), scores, "school_coordinator")
        key2 = _email_cache_key(speaker, _make_event(**{"Event / Program": "Event B"}), scores, "school_coordinator")
        assert key1 != key2

    def test_different_voice_produces_different_keys(self) -> None:
        """Same speaker/event but different voice must not share cache."""
        from src.outreach.email_gen import _email_cache_key

        speaker = _make_speaker()
        event = _make_event()
        scores = _make_match_scores()
        school = _email_cache_key(speaker, event, scores, "school_coordinator")
        chapter = _email_cache_key(speaker, event, scores, "ia_west_chapter")
        assert school != chapter


class TestCachePersistence:
    """Disk cache round-trip tests."""

    def test_save_and_load_cached_email(self, tmp_path: Path) -> None:
        """Round-trip save then load from disk cache."""
        from src.outreach.email_gen import (
            load_cached_email,
            save_cached_email,
        )

        speaker = _make_speaker()
        event = _make_event()
        scores = _make_match_scores()
        email = {
            "subject_line": "Test Subject",
            "greeting": "Hi",
            "body": "Body text",
            "closing": "Bye",
            "full_email": "Hi\n\nBody text\n\nBye",
        }

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path):
            save_cached_email(speaker, event, scores, "school_coordinator", email)
            loaded = load_cached_email(speaker, event, scores, "school_coordinator")

        assert loaded is not None
        assert loaded["subject_line"] == "Test Subject"
        assert loaded["full_email"] == email["full_email"]

    def test_load_returns_none_when_no_cache(self, tmp_path: Path) -> None:
        """Returns None when no cached email exists."""
        from src.outreach.email_gen import load_cached_email

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path):
            result = load_cached_email(_make_speaker(), _make_event(), _make_match_scores(), "school_coordinator")

        assert result is None


class TestFallbackEmail:
    """Fallback template tests."""

    def test_fallback_email_has_all_fields(self) -> None:
        """Fallback email contains all required keys."""
        from src.outreach.email_gen import _fallback_email

        result = _fallback_email(
            speaker_name="Alice",
            speaker_expertise="AI",
            event_name="Hackathon",
            volunteer_role="Judge",
            voice="school_coordinator",
        )

        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        assert required_keys.issubset(result.keys())
        assert "Alice" in result["greeting"]
        assert "Hackathon" in result["body"]

    def test_fallback_with_missing_fields(self) -> None:
        """Fallback works even with empty strings."""
        from src.outreach.email_gen import _fallback_email

        result = _fallback_email(
            speaker_name="",
            speaker_expertise="",
            event_name="",
            volunteer_role="",
            voice="school_coordinator",
        )

        assert "subject_line" in result
        assert "full_email" in result

    def test_fallback_ia_west_chapter_voice(self) -> None:
        """IA West chapter voice uses legacy chapter-leadership template."""
        from src.outreach.email_gen import _fallback_email

        result = _fallback_email(
            speaker_name="Dr. Chen",
            speaker_expertise="analytics",
            event_name="Hackathon",
            volunteer_role="Judge",
            voice="ia_west_chapter",
        )
        assert "IA West (Insights Association West Chapter)" in result["body"]
        assert "IA West Chapter Leadership" in result["closing"]


class TestGenerateEmailJsonParsing:
    """Tests for handling LLM JSON output edge cases."""

    def test_handles_partial_json_response(self, tmp_path: Path) -> None:
        """When LLM returns JSON missing some keys, fills defaults."""
        from src.outreach.email_gen import generate_outreach_email

        partial_response = json.dumps({
            "subject_line": "Test Subject",
            "greeting": "Dear Alice,",
            "body": "Test body.",
        })

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", return_value=partial_response):
            result = generate_outreach_email(
                _make_speaker(),
                _make_event(),
                _make_match_scores(),
            )

        assert "subject_line" in result
        assert "full_email" in result
        assert result["full_email"] != ""

    def test_handles_non_json_response(self, tmp_path: Path) -> None:
        """When LLM returns non-JSON, falls back to template."""
        from src.outreach.email_gen import generate_outreach_email

        with patch("src.outreach.email_gen.EMAIL_CACHE_DIR", tmp_path), \
             patch("src.outreach.email_gen.generate_text", return_value="Not valid JSON"):
            result = generate_outreach_email(
                _make_speaker(),
                _make_event(),
                _make_match_scores(),
            )

        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        assert required_keys.issubset(result.keys())
