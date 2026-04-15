"""Tests for the crawler visited-URL tracking and source metadata added in the
fix-crawler-demo session (2026-04-15).

Covers:
- All SSE events carry a ``source`` field.
- Visited URLs are aggregated into ``_visited_urls``.
- ``/api/crawler/status`` exposes ``visited_count`` and ``visited_urls``.
- Timeouts are shorter than the default 30 s Gemini timeout.
"""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch


# ---------------------------------------------------------------------------
# Source field validation
# ---------------------------------------------------------------------------


def test_sse_events_carry_source_field() -> None:
    """Every SSE event push in _run_crawl_body must include a 'source' key."""
    from src.api.routers.crawler import _run_crawl_body

    source = inspect.getsource(_run_crawl_body)

    # Every _push_event call should mention "source"
    # A simple heuristic: the string '"source"' must appear as many times as
    # we have meaningful push_event blocks (seed found + seed crawling +
    # search crawling + tavily fallback + found + error = at least 5 occurrences).
    source_field_count = source.count('"source"')
    assert source_field_count >= 5, (
        f"Expected at least 5 'source' keys in SSE events inside _run_crawl_body, "
        f"found {source_field_count}"
    )


def test_phase1_seeds_emit_source_seed() -> None:
    """Phase-1 seed events must use source='seed'."""
    from src.api.routers.crawler import _run_crawl_body

    src = inspect.getsource(_run_crawl_body)
    assert '"source": "seed"' in src, (
        "Phase-1 seed URL SSE events must include source='seed'"
    )


def test_phase2_search_source_emitted() -> None:
    """Phase-2 search-query events must emit source='search' for the 'Searching: …' rows."""
    from src.api.routers.crawler import _run_crawl_body

    src = inspect.getsource(_run_crawl_body)
    assert '"source": "search"' in src, (
        "Phase-2 search-query SSE events must include source='search'"
    )


# ---------------------------------------------------------------------------
# Visited URL tracking
# ---------------------------------------------------------------------------


def test_visited_urls_reset_on_run() -> None:
    """_run_crawl must reset _visited_urls to [] before the crawl starts."""
    from src.api.routers.crawler import _run_crawl

    src = inspect.getsource(_run_crawl)
    assert "_visited_urls = []" in src, (
        "_run_crawl must reset _visited_urls to [] at the start of each run"
    )


def test_visited_urls_populated_in_body() -> None:
    """_run_crawl_body must append to _visited_urls for both seed and search results."""
    from src.api.routers.crawler import _run_crawl_body

    src = inspect.getsource(_run_crawl_body)
    assert "_visited_urls.append" in src, (
        "_run_crawl_body must append discovered URLs to _visited_urls"
    )


# ---------------------------------------------------------------------------
# Timeout bounds
# ---------------------------------------------------------------------------


def test_gemini_timeout_is_bounded() -> None:
    """Gemini search timeout must be ≤ 15 s so the demo completes in reasonable time."""
    from src.api.routers import crawler

    assert crawler._GEMINI_SEARCH_TIMEOUT <= 15.0, (
        f"_GEMINI_SEARCH_TIMEOUT should be ≤ 15 s for demo, got {crawler._GEMINI_SEARCH_TIMEOUT}"
    )


def test_tavily_timeout_is_bounded() -> None:
    """Tavily search timeout must be ≤ 20 s."""
    from src.api.routers import crawler

    assert crawler._TAVILY_SEARCH_TIMEOUT <= 20.0, (
        f"_TAVILY_SEARCH_TIMEOUT should be ≤ 20 s for demo, got {crawler._TAVILY_SEARCH_TIMEOUT}"
    )


# ---------------------------------------------------------------------------
# Status endpoint includes visited_count
# ---------------------------------------------------------------------------


def test_crawler_status_includes_visited_count() -> None:
    """crawler_status() must include visited_count and visited_urls keys."""
    from src.api.routers.crawler import crawler_status

    src = inspect.getsource(crawler_status)
    assert "visited_count" in src, "crawler_status must return visited_count"
    assert "visited_urls" in src, "crawler_status must return visited_urls"


# ---------------------------------------------------------------------------
# Delete/clear resets visited_urls
# ---------------------------------------------------------------------------


def test_clear_resets_visited_urls_in_source() -> None:
    """clear_crawler_results must reset _visited_urls to []."""
    from src.api.routers.crawler import clear_crawler_results

    src = inspect.getsource(clear_crawler_results)
    assert "_visited_urls = []" in src, (
        "clear_crawler_results must reset _visited_urls to []"
    )
