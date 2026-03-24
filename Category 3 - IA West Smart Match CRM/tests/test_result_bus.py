"""Tests for result_bus dispatch/poll machinery."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest
import streamlit as st


class TestResultBus:
    """Tests for result_bus.dispatch() and result_bus.poll_results()."""

    def setup_method(self):
        st.session_state["result_queues"] = {}

    def test_dispatch_posts_completed_result(self):
        from src.coordinator import result_bus
        result_bus.dispatch("pid-1", lambda params: {"events": ["A"]}, {})
        time.sleep(0.1)
        results = result_bus.poll_results()
        assert len(results) == 1
        pid, payload = results[0]
        assert pid == "pid-1"
        assert payload["status"] == "completed"
        assert payload["result"] == {"events": ["A"]}

    def test_dispatch_posts_failed_on_exception(self):
        from src.coordinator import result_bus

        def boom(params):
            raise RuntimeError("boom")

        result_bus.dispatch("pid-fail", boom, {})
        time.sleep(0.1)
        results = result_bus.poll_results()
        assert len(results) == 1
        pid, payload = results[0]
        assert pid == "pid-fail"
        assert payload["status"] == "failed"
        assert "boom" in payload["error"]

    def test_two_parallel_tasks_are_independent(self):
        from src.coordinator import result_bus

        def tool_a(params):
            return {"val": params.get("val", "a")}

        def tool_b(params):
            return {"val": params.get("val", "b")}

        result_bus.dispatch("pid-a", tool_a, {"val": "alpha"})
        result_bus.dispatch("pid-b", tool_b, {"val": "beta"})
        time.sleep(0.2)
        results = result_bus.poll_results()
        assert len(results) == 2
        by_pid = {pid: payload for pid, payload in results}
        assert by_pid["pid-a"]["result"]["val"] == "alpha"
        assert by_pid["pid-b"]["result"]["val"] == "beta"

    def test_poll_results_returns_empty_when_no_results(self):
        from src.coordinator import result_bus
        results = result_bus.poll_results()
        assert results == []

    def test_dispatch_creates_fresh_queue(self):
        from src.coordinator import result_bus
        result_bus.dispatch("pid-x", lambda params: {"n": 1}, {})
        time.sleep(0.1)
        first_q = st.session_state["result_queues"]["pid-x"]
        # Second dispatch with same proposal_id should create a new queue
        result_bus.dispatch("pid-x", lambda params: {"n": 2}, {})
        second_q = st.session_state["result_queues"]["pid-x"]
        assert first_q is not second_q
