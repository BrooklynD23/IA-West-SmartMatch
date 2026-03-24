"""Unit tests for Command Center tab: text command handling and conversation history."""
from __future__ import annotations

import re
import sys
from unittest.mock import MagicMock, call, patch

import pytest

# conftest.py ensures streamlit is mocked before import
import streamlit as st

from src.coordinator.approval import ActionProposal
from src.coordinator.intent_parser import ParsedIntent
from src.ui.command_center import (
    _handle_text_command,
    _inject_proactive_suggestions,
    _render_action_card,
    _render_conversation_history,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _reset_history() -> None:
    """Clear session_state before each test."""
    st.session_state["conversation_history"] = []
    st.session_state["action_proposals"] = {}
    st.session_state["scraped_events"] = []
    st.session_state["scraped_events_timestamp"] = None


# ── Tests: _handle_text_command ─────────────────────────────────────────────


class TestHandleTextCommand:
    def setup_method(self) -> None:
        _reset_history()
        st.rerun.reset_mock()  # type: ignore[attr-defined]
        st.markdown.reset_mock()  # type: ignore[attr-defined]

    @patch("src.ui.command_center.parse_intent")
    def test_text_command_appends_user_entry(self, mock_parse: MagicMock) -> None:
        """handle_text_command appends a user entry first."""
        mock_parse.return_value = ParsedIntent(
            intent="discover_events",
            agent="Discovery Agent",
            params={},
            reasoning="test",
            raw_text="find events",
        )
        _handle_text_command("find events")
        history = st.session_state["conversation_history"]
        assert history[0]["role"] == "user"
        assert history[0]["text"] == "find events"

    @patch("src.ui.command_center.parse_intent")
    def test_known_intent_creates_proposal_entry(self, mock_parse: MagicMock) -> None:
        """Known intent appends a proposal entry with action_id."""
        mock_parse.return_value = ParsedIntent(
            intent="discover_events",
            agent="Discovery Agent",
            params={},
            reasoning="test",
            raw_text="find events",
        )
        _handle_text_command("find events")
        history = st.session_state["conversation_history"]
        assert history[1]["role"] == "proposal"
        assert isinstance(history[1]["action_id"], str)

    @patch("src.ui.command_center.parse_intent")
    def test_known_intent_stores_proposal_in_session(self, mock_parse: MagicMock) -> None:
        """Known intent stores ActionProposal in action_proposals session key."""
        mock_parse.return_value = ParsedIntent(
            intent="discover_events",
            agent="Discovery Agent",
            params={},
            reasoning="test",
            raw_text="find events",
        )
        _handle_text_command("find events")
        proposals = st.session_state["action_proposals"]
        assert len(proposals) == 1
        proposal = list(proposals.values())[0]
        assert proposal.intent == "discover_events"

    @patch("src.ui.command_center.parse_intent")
    def test_unknown_intent_creates_assistant_entry(self, mock_parse: MagicMock) -> None:
        """Unknown intent creates an assistant entry with helpful guidance text."""
        mock_parse.return_value = ParsedIntent(
            intent="unknown",
            agent="Jarvis",
            params={},
            reasoning="",
            raw_text="gibberish xyz",
        )
        _handle_text_command("gibberish xyz")
        history = st.session_state["conversation_history"]
        assert history[1]["role"] == "assistant"
        assert "couldn't understand" in history[1]["text"].lower()

    @patch("src.ui.command_center.parse_intent")
    def test_rerun_called_after_command(self, mock_parse: MagicMock) -> None:
        """st.rerun() is called after any command."""
        mock_parse.return_value = ParsedIntent(
            intent="discover_events",
            agent="Discovery Agent",
            params={},
            reasoning="test",
            raw_text="find events",
        )
        _handle_text_command("find events")
        st.rerun.assert_called()  # type: ignore[attr-defined]

    @patch("src.ui.command_center.parse_intent")
    def test_multiple_commands_grow_history(self, mock_parse: MagicMock) -> None:
        """Two commands produce at least 4 history entries."""
        mock_parse.return_value = ParsedIntent(
            intent="discover_events",
            agent="Discovery Agent",
            params={},
            reasoning="test",
            raw_text="find events",
        )
        _handle_text_command("find events")
        mock_parse.return_value = ParsedIntent(
            intent="rank_speakers",
            agent="Matching Agent",
            params={},
            reasoning="test",
            raw_text="rank speakers",
        )
        _handle_text_command("rank speakers")
        history = st.session_state["conversation_history"]
        assert len(history) >= 4


# ── Tests: _render_action_card ───────────────────────────────────────────────


class TestRenderActionCard:
    def setup_method(self) -> None:
        _reset_history()
        st.button.reset_mock()  # type: ignore[attr-defined]
        st.success.reset_mock()  # type: ignore[attr-defined]
        st.warning.reset_mock()  # type: ignore[attr-defined]
        st.info.reset_mock()  # type: ignore[attr-defined]
        st.markdown.reset_mock()  # type: ignore[attr-defined]
        st.caption.reset_mock()  # type: ignore[attr-defined]
        st.container.reset_mock()  # type: ignore[attr-defined]
        st.columns.reset_mock()  # type: ignore[attr-defined]
        st.expander.reset_mock()  # type: ignore[attr-defined]

    def test_render_proposed_card_shows_approve_button(self) -> None:
        """Proposed card renders at least the approve button."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="test description",
            reasoning="test reasoning",
        )
        st.session_state["action_proposals"] = {p.id: p}
        _render_action_card(p)
        assert st.button.called  # type: ignore[attr-defined]

    def test_render_completed_card_shows_result(self) -> None:
        """Completed card calls st.success with result."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="test description",
            reasoning="test reasoning",
        )
        p.approve()
        p.stub_execute()
        _render_action_card(p)
        assert st.success.called  # type: ignore[attr-defined]

    def test_render_rejected_card_shows_warning(self) -> None:
        """Rejected card calls st.warning."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="test description",
            reasoning="test reasoning",
        )
        p.reject()
        _render_action_card(p)
        assert st.warning.called  # type: ignore[attr-defined]


# ── Tests: _inject_proactive_suggestions ────────────────────────────────────


class TestProactiveSuggestion:
    def setup_method(self) -> None:
        _reset_history()

    def test_no_duplicate_injection(self) -> None:
        """Active proactive suggestion prevents injecting another."""
        existing = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="Re-run event discovery scraper",
            reasoning="stale",
            source="proactive",
        )
        # Status is already "proposed" by default
        st.session_state["action_proposals"] = {existing.id: existing}
        st.session_state["conversation_history"] = [
            {"role": "proposal", "action_id": existing.id, "timestamp": existing.created_at}
        ]
        _inject_proactive_suggestions()
        # Should still have only 1 proposal (no duplicate added)
        assert len(st.session_state["action_proposals"]) == 1

    def test_suggestion_injected_when_no_active(self) -> None:
        """Proactive suggestion is injected when no active proactive proposal exists."""
        # Empty state: stale/empty data will trigger a suggestion
        st.session_state["action_proposals"] = {}
        st.session_state["scraped_events"] = []
        st.session_state["scraped_events_timestamp"] = None
        _inject_proactive_suggestions()
        assert len(st.session_state["action_proposals"]) == 1
        proposal = list(st.session_state["action_proposals"].values())[0]
        assert proposal.source == "proactive"


# ── Tests: _render_conversation_history ─────────────────────────────────────


class TestRenderConversationHistory:
    def setup_method(self) -> None:
        _reset_history()
        st.markdown.reset_mock()  # type: ignore[attr-defined]

    def test_render_empty_history_shows_guidance_text(self) -> None:
        """Empty history renders 'No conversation yet' guidance."""
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "No conversation yet" in rendered_html

    def test_render_empty_history_uses_chat_container(self) -> None:
        """Empty history renders a chat-container div."""
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "chat-container" in rendered_html

    def test_render_with_entries_shows_chat_bubbles(self) -> None:
        """Entries are rendered with chat-bubble class."""
        st.session_state["conversation_history"] = [
            {"role": "user", "text": "hi", "intent": None, "timestamp": "12:00:00"},
            {"role": "assistant", "text": "Hello!", "intent": "unknown", "timestamp": "12:00:00"},
        ]
        st.markdown.reset_mock()
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "chat-bubble" in rendered_html

    def test_render_coordinator_bubble_for_user(self) -> None:
        """User entry uses coordinator bubble class."""
        st.session_state["conversation_history"] = [
            {"role": "user", "text": "hi", "intent": None, "timestamp": "12:00:00"},
        ]
        st.markdown.reset_mock()
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "coordinator" in rendered_html

    def test_render_jarvis_bubble_for_assistant(self) -> None:
        """Assistant entry uses jarvis bubble class."""
        st.session_state["conversation_history"] = [
            {"role": "assistant", "text": "Hello!", "intent": "unknown", "timestamp": "12:00:00"},
        ]
        st.markdown.reset_mock()
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "jarvis" in rendered_html

    def test_render_intent_badge_for_assistant(self) -> None:
        """Assistant entry with intent renders an intent-badge span."""
        st.session_state["conversation_history"] = [
            {"role": "assistant", "text": "Hello!", "intent": "unknown", "timestamp": "12:00:00"},
        ]
        st.markdown.reset_mock()
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "intent-badge" in rendered_html
        assert "unknown" in rendered_html

    def test_no_guidance_text_when_history_not_empty(self) -> None:
        """'No conversation yet' text is absent when history has entries."""
        st.session_state["conversation_history"] = [
            {"role": "user", "text": "hello", "intent": None, "timestamp": "12:00:00"},
        ]
        st.markdown.reset_mock()
        _render_conversation_history()
        all_calls = st.markdown.call_args_list
        rendered_html = " ".join(str(c) for c in all_calls)
        assert "No conversation yet" not in rendered_html
