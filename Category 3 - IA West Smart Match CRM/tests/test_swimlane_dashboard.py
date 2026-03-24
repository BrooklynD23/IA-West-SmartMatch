"""Tests for swimlane_dashboard.py — agent status card rendering."""

from __future__ import annotations

import sys
import time
from unittest.mock import MagicMock, call

import pytest

# conftest.py already mocks streamlit before any src import
import streamlit as st

from src.ui.swimlane_dashboard import _update_swimlane, render_swimlane_dashboard


@pytest.fixture(autouse=True)
def reset_streamlit_mocks():
    """Reset Streamlit session state and mock call history before each test."""
    st.session_state.clear()
    st.markdown.reset_mock()
    st.columns.reset_mock()
    st.button.reset_mock()
    yield


class TestRenderSwimlaneDashboard:
    """Tests for render_swimlane_dashboard() rendering logic."""

    def test_render_noop_when_no_swimlanes(self) -> None:
        """render_swimlane_dashboard() does not call st.columns when agent_swimlanes is empty."""
        st.session_state["agent_swimlanes"] = {}
        render_swimlane_dashboard()
        st.columns.assert_not_called()

    def test_render_noop_when_swimlanes_missing(self) -> None:
        """render_swimlane_dashboard() does not call st.columns when agent_swimlanes key is absent."""
        # Do NOT set agent_swimlanes in session_state
        render_swimlane_dashboard()
        st.columns.assert_not_called()

    def test_render_single_agent_card(self) -> None:
        """With 1 entry in agent_swimlanes, st.columns(1) is called and
        st.markdown receives HTML containing agent name and status."""
        st.session_state["agent_swimlanes"] = {
            "pid-1": {
                "proposal_id": "pid-1",
                "agent_name": "Discovery Agent",
                "status": "running",
                "summary": "Searching...",
                "elapsed_s": 5.0,
                "started_at": time.monotonic(),
            }
        }
        render_swimlane_dashboard()
        st.columns.assert_called_once_with(1)

    def test_render_multiple_agent_cards(self) -> None:
        """With 3 entries, st.columns(3) is called."""
        st.session_state["agent_swimlanes"] = {
            f"pid-{i}": {
                "proposal_id": f"pid-{i}",
                "agent_name": f"Agent {i}",
                "status": "idle",
                "summary": "",
                "elapsed_s": 0.0,
                "started_at": time.monotonic(),
            }
            for i in range(3)
        }
        render_swimlane_dashboard()
        st.columns.assert_called_once_with(3)

    def test_render_max_8_cards(self) -> None:
        """With 10 entries, st.columns(8) is called (capped at 8)."""
        st.session_state["agent_swimlanes"] = {
            f"pid-{i}": {
                "proposal_id": f"pid-{i}",
                "agent_name": f"Agent {i}",
                "status": "idle",
                "summary": "",
                "elapsed_s": 0.0,
                "started_at": time.monotonic(),
            }
            for i in range(10)
        }
        render_swimlane_dashboard()
        st.columns.assert_called_once_with(8)

    def test_status_css_class_mapping(self) -> None:
        """Each status value maps to the correct CSS class string in the rendered HTML."""
        from src.ui.swimlane_dashboard import STATUS_CSS_CLASS

        assert STATUS_CSS_CLASS["idle"] == "status-idle"
        assert STATUS_CSS_CLASS["running"] == "status-running"
        assert STATUS_CSS_CLASS["awaiting"] == "status-awaiting"
        assert STATUS_CSS_CLASS["completed"] == "status-completed"
        assert STATUS_CSS_CLASS["failed"] == "status-failed"

    def test_compact_card_after_30s(self) -> None:
        """Entry with status 'completed' and started_at older than 30s renders
        compact single-line HTML (class swimlane-compact)."""
        old_start = time.monotonic() - 60  # 60 seconds ago
        st.session_state["agent_swimlanes"] = {
            "pid-old": {
                "proposal_id": "pid-old",
                "agent_name": "Outreach Agent",
                "status": "completed",
                "summary": "Done",
                "elapsed_s": 60.0,
                "started_at": old_start,
            }
        }
        render_swimlane_dashboard()
        # Collect all HTML strings passed to st.markdown via context manager __enter__
        # The column mock returns MagicMock; markdown is called on the column context
        all_markdown_calls = st.markdown.call_args_list
        # At least one markdown call should contain 'swimlane-compact'
        html_calls = [str(c) for c in all_markdown_calls]
        assert any("swimlane-compact" in c for c in html_calls), (
            f"Expected 'swimlane-compact' in one of: {html_calls}"
        )


class TestUpdateSwimlane:
    """Tests for _update_swimlane() session state mutation."""

    def test_update_swimlane_creates_entry(self) -> None:
        """_update_swimlane with new proposal_id creates a new entry in session state."""
        st.session_state["agent_swimlanes"] = {}
        _update_swimlane("pid-new", "running", "Searching...", "Discovery Agent")
        assert "pid-new" in st.session_state["agent_swimlanes"]

    def test_update_swimlane_updates_existing(self) -> None:
        """_update_swimlane with existing proposal_id updates status and summary fields."""
        st.session_state["agent_swimlanes"] = {
            "pid-1": {
                "proposal_id": "pid-1",
                "agent_name": "Old Agent",
                "status": "running",
                "summary": "old summary",
                "started_at": time.monotonic(),
                "elapsed_s": 1.0,
            }
        }
        _update_swimlane("pid-1", "completed", "new summary", "New Agent")
        entry = st.session_state["agent_swimlanes"]["pid-1"]
        assert entry["status"] == "completed"
        assert entry["summary"] == "new summary"
        assert entry["agent_name"] == "New Agent"

    def test_update_swimlane_sets_started_at_once(self) -> None:
        """Calling _update_swimlane twice does not overwrite the started_at timestamp."""
        st.session_state["agent_swimlanes"] = {}
        _update_swimlane("pid-1", "running", "First", "Agent")
        first_started_at = st.session_state["agent_swimlanes"]["pid-1"]["started_at"]

        # Small sleep to ensure time.monotonic() advances
        time.sleep(0.05)
        _update_swimlane("pid-1", "completed", "Second", "Agent")
        second_started_at = st.session_state["agent_swimlanes"]["pid-1"]["started_at"]

        assert first_started_at == second_started_at, (
            "started_at should not be overwritten on second update"
        )

    def test_update_swimlane_summary_truncated_at_80(self) -> None:
        """Summary is truncated to 80 characters."""
        st.session_state["agent_swimlanes"] = {}
        long_summary = "x" * 200
        _update_swimlane("pid-1", "running", long_summary, "Agent")
        entry = st.session_state["agent_swimlanes"]["pid-1"]
        assert len(entry["summary"]) == 80

    def test_update_swimlane_elapsed_increases(self) -> None:
        """elapsed_s increases on subsequent calls."""
        st.session_state["agent_swimlanes"] = {}
        _update_swimlane("pid-1", "running", "First", "Agent")
        first_elapsed = st.session_state["agent_swimlanes"]["pid-1"]["elapsed_s"]

        time.sleep(0.05)
        _update_swimlane("pid-1", "running", "Second", "Agent")
        second_elapsed = st.session_state["agent_swimlanes"]["pid-1"]["elapsed_s"]

        assert second_elapsed > first_elapsed
