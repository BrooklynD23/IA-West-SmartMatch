"""Result bus — thread-based dispatch and non-blocking queue polling.

Dispatches tool functions in daemon threads with per-proposal queues stored
in st.session_state["result_queues"].
"""

from __future__ import annotations

import queue
import threading
from typing import Any, Callable

import streamlit as st


def dispatch(
    proposal_id: str,
    tool_fn: Callable[[dict[str, Any]], dict[str, Any]],
    params: dict[str, Any],
) -> None:
    """Dispatch a tool function in a daemon thread.

    Creates a fresh queue.Queue(maxsize=1) for this proposal, unconditionally
    replacing any previous queue for the same proposal_id.

    Args:
        proposal_id: Unique identifier for the action proposal.
        tool_fn: Callable that accepts params dict and returns result dict.
        params: Parameters to pass to the tool function.
    """
    result_queues: dict[str, queue.Queue] = st.session_state.setdefault("result_queues", {})
    q: queue.Queue = queue.Queue(maxsize=1)
    result_queues[proposal_id] = q

    def _worker() -> None:
        try:
            result = tool_fn(params)
            q.put({"status": "completed", "result": result})
        except Exception as exc:  # noqa: BLE001
            q.put({"status": "failed", "error": str(exc)})

    thread = threading.Thread(
        target=_worker,
        name=f"tool-{proposal_id[:8]}",
        daemon=True,
    )
    thread.start()


def poll_results() -> list[tuple[str, dict[str, Any]]]:
    """Poll all queues for available results without blocking.

    Returns:
        List of (proposal_id, payload) tuples for completed/failed proposals.
        Returns [] when no results are ready.
    """
    result_queues: dict[str, queue.Queue] = st.session_state.get("result_queues", {})
    ready: list[tuple[str, dict[str, Any]]] = []
    for proposal_id, q in result_queues.items():
        try:
            payload = q.get_nowait()
            ready.append((proposal_id, payload))
        except queue.Empty:
            pass
    return ready
