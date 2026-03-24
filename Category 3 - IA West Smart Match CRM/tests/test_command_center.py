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
from src.coordinator.tools import TOOL_REGISTRY
from src.ui.command_center import (
    _format_result,
    _handle_text_command,
    _inject_proactive_suggestions,
    _poll_result_bus,
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
        st.button.side_effect = None  # type: ignore[attr-defined]
        st.button.return_value = False  # type: ignore[attr-defined]
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


# ── Tests: dispatch wiring ───────────────────────────────────────────────────


class TestDispatchWiring:
    def setup_method(self) -> None:
        _reset_history()
        st.button.reset_mock()  # type: ignore[attr-defined]
        st.button.side_effect = None  # type: ignore[attr-defined]
        st.button.return_value = False  # type: ignore[attr-defined]
        st.success.reset_mock()  # type: ignore[attr-defined]
        st.info.reset_mock()  # type: ignore[attr-defined]
        st.error.reset_mock()  # type: ignore[attr-defined]
        st.container.reset_mock()  # type: ignore[attr-defined]
        st.columns.reset_mock()  # type: ignore[attr-defined]
        st.expander.reset_mock()  # type: ignore[attr-defined]

    @patch("src.ui.command_center.dispatch")
    def test_approve_dispatches_real_tool(self, mock_dispatch: MagicMock) -> None:
        """Approve button calls dispatch() with correct args for known intent."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="Find events",
            reasoning="test",
            params={"university": "CPP"},
        )
        st.session_state["action_proposals"] = {p.id: p}
        # Return True only for the approve button key, False for reject
        def _button_side_effect(label, key=None, **kwargs):
            return key == f"approve_{p.id}"
        st.button.side_effect = _button_side_effect  # type: ignore[attr-defined]
        _render_action_card(p)
        mock_dispatch.assert_called_once_with(
            p.id, TOOL_REGISTRY["discover_events"], p.params
        )
        assert p.status == "executing"

    @patch("src.ui.command_center.dispatch")
    def test_approve_unknown_intent_uses_stub(self, mock_dispatch: MagicMock) -> None:
        """Approve button falls back to stub_execute() for unknown intents."""
        p = ActionProposal(
            intent="unknown_intent_xyz",
            agent="Jarvis",
            description="Unknown action",
            reasoning="test",
            params={},
        )
        st.session_state["action_proposals"] = {p.id: p}
        # Return True only for the approve button key, False for reject
        def _button_side_effect(label, key=None, **kwargs):
            return key == f"approve_{p.id}"
        st.button.side_effect = _button_side_effect  # type: ignore[attr-defined]
        _render_action_card(p)
        mock_dispatch.assert_not_called()
        assert p.status == "completed"


# ── Tests: _format_result ────────────────────────────────────────────────────


class TestFormatResult:
    def test_format_result_events(self) -> None:
        """Events result returns count and source."""
        result = _format_result({"status": "ok", "events": [{"name": "Fair"}], "source": "cache"})
        assert "1 event(s)" in result
        assert "cache" in result

    def test_format_result_rankings(self) -> None:
        """Rankings result returns speaker count."""
        result = _format_result({"status": "ok", "rankings": [{}, {}]})
        assert "2 speaker(s)" in result

    def test_format_result_contacts(self) -> None:
        """Contacts result returns total and overdue count."""
        result = _format_result({"status": "ok", "contacts": [], "total": 5, "overdue_count": 2})
        assert "5 contacts" in result
        assert "2 overdue" in result

    def test_format_result_email(self) -> None:
        """Email result returns subject line."""
        result = _format_result({"status": "ok", "email": {"subject": "Hello CPP"}})
        assert "Hello CPP" in result

    def test_format_result_error(self) -> None:
        """Error key returns error message."""
        result = _format_result({"error": "timeout"})
        assert "timeout" in result


# ── Tests: _poll_result_bus ──────────────────────────────────────────────────


class TestPollResultBus:
    def setup_method(self) -> None:
        _reset_history()

    @patch("src.ui.command_center.poll_results")
    def test_poll_result_bus_updates_proposal(self, mock_poll: MagicMock) -> None:
        """Polling completed result sets proposal status to completed."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="Find events",
            reasoning="test",
            params={},
        )
        p.status = "executing"  # type: ignore[assignment]
        st.session_state["action_proposals"] = {p.id: p}
        mock_poll.return_value = [
            (p.id, {"status": "completed", "result": {"events": [], "source": "cache"}})
        ]
        _poll_result_bus()
        assert p.status == "completed"
        assert "event(s)" in p.result

    @patch("src.ui.command_center.poll_results")
    def test_poll_result_bus_handles_failure(self, mock_poll: MagicMock) -> None:
        """Polling failed result sets proposal status to failed with error in result."""
        p = ActionProposal(
            intent="discover_events",
            agent="Discovery Agent",
            description="Find events",
            reasoning="test",
            params={},
        )
        p.status = "executing"  # type: ignore[assignment]
        st.session_state["action_proposals"] = {p.id: p}
        mock_poll.return_value = [
            (p.id, {"status": "failed", "error": "timeout"})
        ]
        _poll_result_bus()
        assert p.status == "failed"
        assert "timeout" in p.result
