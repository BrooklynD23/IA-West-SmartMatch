"""Swimlane dashboard — horizontal row of agent status cards.

Reads from ``st.session_state["agent_swimlanes"]`` (a dict keyed by proposal_id)
and renders a compact horizontal status strip for the Command Center tab.

No external dependencies beyond Streamlit.
"""

from __future__ import annotations

import time

import streamlit as st

# ---------------------------------------------------------------------------
# Status → CSS class mapping
# ---------------------------------------------------------------------------

STATUS_CSS_CLASS: dict[str, str] = {
    "idle": "status-idle",
    "running": "status-running",
    "awaiting": "status-awaiting",
    "completed": "status-completed",
    "failed": "status-failed",
}

# ---------------------------------------------------------------------------
# Public rendering function
# ---------------------------------------------------------------------------

_COMPACT_AFTER_SECONDS: float = 30.0
_MAX_CARDS: int = 8


def render_swimlane_dashboard() -> None:
    """Render a horizontal row of agent status cards from session state.

    Reads ``st.session_state["agent_swimlanes"]`` dict.  If empty or absent,
    returns immediately without rendering anything.  Caps display at 8 cards
    (most recently inserted entries).
    """
    swimlanes: dict = st.session_state.get("agent_swimlanes", {})
    if not swimlanes:
        return

    entries = list(swimlanes.values())[-_MAX_CARDS:]
    if not entries:
        return

    st.markdown("### Agent Status")
    cols = st.columns(len(entries))

    for col, entry in zip(cols, entries):
        status: str = entry.get("status", "idle")
        css_class: str = STATUS_CSS_CLASS.get(status, "status-idle")
        elapsed: float = entry.get("elapsed_s", 0.0)
        summary: str = entry.get("summary", "")
        agent_name: str = entry.get("agent_name", "Agent")
        started_at: float = entry.get("started_at", 0.0)
        proposal_id: str = entry.get("proposal_id", "")

        # Compact card for completed tasks older than 30 seconds
        is_compact = status == "completed" and (time.monotonic() - started_at) > _COMPACT_AFTER_SECONDS

        with col:
            if is_compact:
                html = f'<div class="swimlane-compact">{agent_name} -- Done</div>'
            else:
                html = (
                    f'<div class="swimlane-card {css_class}">'
                    f"<b>{agent_name}</b><br>"
                    f'<span class="swimlane-status" style="color:inherit;">{status.upper()}</span><br>'
                    f"<small>{elapsed:.0f}s</small><br>"
                    f"<small>{summary}</small>"
                    f"</div>"
                )
            st.markdown(html, unsafe_allow_html=True)

            if status == "failed":
                st.button("Retry", key=f"retry_{proposal_id}")


# ---------------------------------------------------------------------------
# Session state update helper (used by Plan 02 poll loop)
# ---------------------------------------------------------------------------


def _update_swimlane(
    proposal_id: str,
    status: str,
    summary: str,
    agent_name: str = "Agent",
) -> None:
    """Create or update a swimlane entry in session state.

    Preserves the ``started_at`` timestamp once set — calling this function
    twice for the same proposal_id will NOT reset the start time.

    Args:
        proposal_id: Unique identifier for the action proposal.
        status: Status string (idle, running, awaiting, completed, failed).
        summary: Short progress or result description (truncated to 80 chars).
        agent_name: Display name for the agent card.
    """
    swimlanes: dict = st.session_state.setdefault("agent_swimlanes", {})
    entry: dict = swimlanes.get(proposal_id, {})

    entry["status"] = status
    entry["summary"] = summary[:80]
    entry["agent_name"] = agent_name
    entry["proposal_id"] = proposal_id

    if "started_at" not in entry:
        entry["started_at"] = time.monotonic()

    entry["elapsed_s"] = time.monotonic() - entry["started_at"]
    swimlanes[proposal_id] = entry
