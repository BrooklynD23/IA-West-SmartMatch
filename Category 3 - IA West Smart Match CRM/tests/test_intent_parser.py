"""Tests for intent_parser.py with mocked Gemini."""

import json
from unittest.mock import patch

import pytest

from src.coordinator.intent_parser import (
    ACTION_REGISTRY,
    MULTI_STEP_INTENTS,
    SUPPORTED_INTENTS,
    ParsedIntent,
    parse_intent,
)
from src.gemini_client import GeminiAPIError


_FAKE_API_KEY = "test-key-for-unit-tests"


class TestParseIntent:
    """Intent parsing tests using mocked generate_text."""

    def _make_gemini_response(self, intent: str, agent: str = "Discovery Agent", reasoning: str = "test") -> str:
        return json.dumps({"intent": intent, "agent": agent, "params": {}, "reasoning": reasoning})

    def test_parse_discover_events(self) -> None:
        response = self._make_gemini_response("discover_events", "Discovery Agent")
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch("src.coordinator.intent_parser.generate_text", return_value=response),
        ):
            result = parse_intent("find events at UCLA")
        assert result.intent == "discover_events"

    def test_parse_intent_returns_unknown_on_malformed_json(self) -> None:
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch("src.coordinator.intent_parser.generate_text", return_value="not json"),
        ):
            result = parse_intent("something")
        assert result.intent == "unknown"

    def test_parse_intent_returns_unknown_on_gemini_error(self) -> None:
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch(
                "src.coordinator.intent_parser.generate_text",
                side_effect=GeminiAPIError("API error"),
            ),
        ):
            result = parse_intent("something")
        assert result.intent == "unknown"

    def test_parse_intent_returns_unknown_for_unsupported_intent(self) -> None:
        response = self._make_gemini_response("fly_to_moon")
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch("src.coordinator.intent_parser.generate_text", return_value=response),
        ):
            result = parse_intent("do something weird")
        assert result.intent == "unknown"

    def test_parse_intent_preserves_raw_text(self) -> None:
        user_text = "find events at UCLA"
        response = self._make_gemini_response("discover_events")
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch("src.coordinator.intent_parser.generate_text", return_value=response),
        ):
            result = parse_intent(user_text)
        assert result.raw_text == user_text

    def test_parse_intent_strips_markdown_fences(self) -> None:
        inner = json.dumps({"intent": "discover_events", "agent": "Discovery Agent", "params": {}, "reasoning": "r"})
        fenced = f"```json\n{inner}\n```"
        with (
            patch("src.coordinator.intent_parser.GEMINI_API_KEY", _FAKE_API_KEY),
            patch("src.coordinator.intent_parser.generate_text", return_value=fenced),
        ):
            result = parse_intent("find events")
        assert result.intent == "discover_events"

    def test_keyword_fallback_discover_events(self) -> None:
        """Without API key, keyword fallback should match 'find new events'."""
        with patch("src.coordinator.intent_parser.GEMINI_API_KEY", ""):
            result = parse_intent("Find new events")
        assert result.intent == "discover_events"
        assert result.agent == "Discovery Agent"

    def test_keyword_fallback_rank_speakers(self) -> None:
        with patch("src.coordinator.intent_parser.GEMINI_API_KEY", ""):
            result = parse_intent("Rank speakers for CPP Career Fair")
        assert result.intent == "rank_speakers"

    def test_keyword_fallback_unknown(self) -> None:
        """Unrecognized text with no API key should return unknown."""
        with patch("src.coordinator.intent_parser.GEMINI_API_KEY", ""):
            result = parse_intent("make me a sandwich")
        assert result.intent == "unknown"

    def test_parsed_intent_is_frozen(self) -> None:
        pi = ParsedIntent(intent="unknown", agent="Jarvis", params={}, reasoning="", raw_text="x")
        with pytest.raises((AttributeError, TypeError)):
            pi.intent = "discover_events"  # type: ignore[misc]

    def test_supported_intents_contains_core_five(self) -> None:
        # Core intents must always be present (prepare_campaign added in Phase 7)
        core = frozenset({
            "discover_events",
            "rank_speakers",
            "generate_outreach",
            "check_contacts",
            "unknown",
        })
        assert core.issubset(SUPPORTED_INTENTS)

    def test_action_registry_has_at_least_four_entries(self) -> None:
        assert len(ACTION_REGISTRY) >= 4

    def test_action_registry_entries_have_correct_fields(self) -> None:
        intents = {entry["intent"] for entry in ACTION_REGISTRY}
        agents = {entry["agent"] for entry in ACTION_REGISTRY}
        assert {"discover_events", "rank_speakers", "generate_outreach", "check_contacts"}.issubset(intents)
        assert "Discovery Agent" in agents
        assert "Matching Agent" in agents
        assert "Outreach Agent" in agents
        assert "Contacts Agent" in agents


class TestPrepareIntent:
    """Tests for the prepare_campaign multi-step intent registration."""

    def test_prepare_campaign_in_supported_intents(self) -> None:
        assert "prepare_campaign" in SUPPORTED_INTENTS

    def test_prepare_campaign_in_action_registry(self) -> None:
        intents_in_registry = {entry["intent"] for entry in ACTION_REGISTRY}
        assert "prepare_campaign" in intents_in_registry

    def test_multi_step_intents_maps_prepare_campaign(self) -> None:
        assert MULTI_STEP_INTENTS["prepare_campaign"] == [
            "discover_events",
            "rank_speakers",
            "generate_outreach",
        ]

    def test_prepare_campaign_agent_is_campaign_orchestrator(self) -> None:
        entry = next(
            (e for e in ACTION_REGISTRY if e["intent"] == "prepare_campaign"),
            None,
        )
        assert entry is not None
        assert entry["agent"] == "Campaign Orchestrator"
