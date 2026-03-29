"""REST endpoints for web crawler: trigger crawls, stream live activity, retrieve results."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse

from src.api.smartmatch_db import delete_all_crawler_events, insert_crawler_event, load_crawler_events
from src.config import GEMINI_API_KEY
from src.gemini_client import web_search

router = APIRouter()
_log = logging.getLogger(__name__)

# Module-level queue: single-crawl demo scope. maxsize=100 prevents unbounded growth.
_crawler_queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue(maxsize=100)

# Module-level crawl state: tracks whether a crawl is idle, running, or done.
_crawl_state: dict[str, Any] = {
    "state": "idle",
    "started_at": None,
    "finished_at": None,
    "error": None,
}

# Directed school seed URLs derived from IA West CSV data
SEED_URLS: tuple[str, ...] = (
    "https://www.cpp.edu/cba/digital-innovation/what-we-do/ai-hackathon.shtml",
    "https://www.cpp.edu/cba/ai-hackathon/index.shtml",
    "https://www.cpp.edu/",
    "https://www.insightsassociation.org/ai-hackathon",
    "https://www.insightsassociation.org/itc",
    "https://www.insightsassociation.org/ia-west-summit",
    "https://www.sdsu.edu/",
    "https://www.ucsd.edu/",
    "https://www.ucla.edu/",
    "https://www.pdx.edu/",
)

# Keywords that suggest a URL/title represents an actual event rather than a homepage.
_EVENT_KEYWORDS: frozenset[str] = frozenset({
    "hackathon", "conference", "summit", "workshop", "seminar", "symposium",
    "webinar", "expo", "forum", "panel", "lecture", "career fair", "networking",
    "competition", "challenge", "event", "bootcamp", "colloquium", "congress",
    "showcase", "demo day", "info session", "orientation", "itc", "ia west",
})


def _is_event_relevant(url: str, title: str) -> bool:
    """Return True only when the URL/title looks like a real event, not a homepage.

    Rejects:
    - Root/near-root URLs (path depth < 2) unless the title contains an event keyword.
    - Entries where neither the URL path nor the title contain any event keyword.
    """
    from urllib.parse import urlparse
    parsed = urlparse(url.lower())
    path_parts = [p for p in parsed.path.split("/") if p]
    combined = (title + " " + " ".join(path_parts)).lower()
    return any(kw in combined for kw in _EVENT_KEYWORDS)


SEARCH_QUERIES: tuple[str, ...] = (
    "Cal Poly Pomona AI hackathon 2026 directed schools",
    "Insights Association West chapter events directed schools",
    "UC San Diego SDSU data science events speakers",
    "UCLA community outreach analytics events",
    "Portland State University industry partnerships speakers",
)


def _tavily_api_key() -> str:
    """Read TAVILY_API_KEY from environment."""
    import os
    return os.getenv("TAVILY_API_KEY", "")


async def _search_gemini(query: str) -> list[dict[str, str]]:
    """Run Gemini web search in executor to avoid blocking event loop."""
    if not GEMINI_API_KEY:
        return []
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(
            None, lambda: web_search(query, api_key=GEMINI_API_KEY)
        )
    except Exception as exc:
        _log.warning("Gemini search failed for %r: %s", query, exc)
        return []


async def _search_tavily(query: str) -> list[dict[str, str]]:
    """Run Tavily search in executor to avoid blocking event loop."""
    api_key = _tavily_api_key()
    if not api_key:
        return []
    loop = asyncio.get_event_loop()
    try:
        def _do_search() -> list[dict[str, str]]:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            response = client.search(query)
            raw_results = response.get("results", []) if isinstance(response, dict) else []
            return [
                {"url": str(r.get("url", "")), "title": str(r.get("title", ""))}
                for r in raw_results
                if isinstance(r, dict) and r.get("url")
            ]
        return await loop.run_in_executor(None, _do_search)
    except Exception as exc:
        _log.warning("Tavily search failed for %r: %s", query, exc)
        return []


async def _push_event(event: dict[str, Any]) -> None:
    """Push event to queue, dropping if full (no consumer connected)."""
    try:
        _crawler_queue.put_nowait(event)
    except asyncio.QueueFull:
        pass


async def _run_crawl() -> None:
    """Crawl IA West directed school pages; push events to SSE queue and persist to DB."""
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    _crawl_state["state"] = "running"
    _crawl_state["started_at"] = now()
    _crawl_state["finished_at"] = None
    _crawl_state["error"] = None

    try:
        await _run_crawl_body(now)
    except Exception as exc:
        _crawl_state["error"] = str(exc)
        raise
    finally:
        _crawl_state["state"] = "done"
        _crawl_state["finished_at"] = now()
        try:
            _crawler_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass


async def _run_crawl_body(now: Any) -> None:
    """Inner crawl steps (``_run_crawl`` ``finally`` emits the SSE done sentinel)."""

    # Phase 1: Emit "crawling" for each seed URL
    for url in SEED_URLS:
        await _push_event({
            "url": url,
            "title": "",
            "status": "crawling",
            "timestamp": now(),
        })
        await asyncio.sleep(0.3)  # Pacing for visual effect in UI

        # Simulate a basic "found" for seed URLs
        title = url.split("//")[1].split("/")[0] if "//" in url else url
        if _is_event_relevant(url, title):
            event_record = {
                "url": url,
                "title": title,
                "description": f"Seed URL: {url}",
                "school_name": title,
                "crawled_at": now(),
                "source": "seed",
                "status": "found",
            }
            try:
                insert_crawler_event(event_record)
            except Exception as exc:
                _log.warning("Failed to persist seed event %s: %s", url, exc)
        else:
            _log.debug("Skipping non-event seed URL: %s", url)

        await _push_event({
            "url": url,
            "title": title,
            "status": "found",
            "timestamp": now(),
        })

    # Phase 2: Run search queries through Gemini then Tavily
    for query in SEARCH_QUERIES:
        await _push_event({
            "url": "",
            "title": f"Searching: {query}",
            "status": "crawling",
            "timestamp": now(),
        })

        results = await _search_gemini(query)
        search_source = "gemini"
        if not results:
            results = await _search_tavily(query)
            search_source = "tavily"

        for result in results:
            url = result.get("url", "")
            title = result.get("title", "")
            if not _is_event_relevant(url, title):
                _log.debug("Skipping non-event search result: %s | %s", title, url)
                continue
            event_record = {
                "url": url,
                "title": title,
                "description": f"Discovered via {search_source}: {query}",
                "school_name": title,
                "crawled_at": now(),
                "source": search_source,
                "status": "found",
            }
            try:
                insert_crawler_event(event_record)
            except Exception as exc:
                _log.warning("Failed to persist search result %s: %s", url, exc)

            await _push_event({
                "url": url,
                "title": title,
                "status": "found",
                "timestamp": now(),
            })
            await asyncio.sleep(0.2)  # Pacing

        if not results:
            await _push_event({
                "url": "",
                "title": f"No results for: {query}",
                "status": "error",
                "timestamp": now(),
            })


async def _event_stream() -> AsyncIterator[str]:
    """Drain the crawler queue, yielding SSE-formatted strings."""
    while True:
        try:
            event = await asyncio.wait_for(_crawler_queue.get(), timeout=30.0)
        except asyncio.TimeoutError:
            yield ": keepalive\n\n"
            continue
        if event is None:
            yield 'data: {"status": "done"}\n\n'
            break
        yield f"data: {json.dumps(event)}\n\n"


@router.get("/feed")
async def crawler_feed() -> StreamingResponse:
    """SSE endpoint streaming real-time crawler activity."""
    return StreamingResponse(
        _event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/status")
async def crawler_status() -> dict[str, Any]:
    """Return current crawl state: idle | running | done."""
    return {**_crawl_state}


@router.post("/start")
async def start_crawl(background_tasks: BackgroundTasks) -> dict[str, str]:
    """Trigger a background crawl targeting IA West directed school pages.

    Returns 409 if a crawl is already in progress.
    """
    if _crawl_state["state"] == "running":
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Crawl already running")
    background_tasks.add_task(_run_crawl)
    return {"status": "started"}


@router.get("/results")
async def crawler_results() -> dict[str, Any]:
    """Return stored crawl results from smartmatch.db."""
    try:
        events = load_crawler_events()
        return {"events": events, "count": len(events), "source": "live"}
    except Exception:
        return {"events": [], "count": 0, "source": "none"}


@router.delete("/results")
async def clear_crawler_results() -> dict[str, Any]:
    """Delete all crawler events from smartmatch.db (Layer 0 reset).

    Use this to flush non-event entries before re-running a crawl.
    """
    try:
        deleted = delete_all_crawler_events()
        _crawl_state["state"] = "idle"
        _crawl_state["started_at"] = None
        _crawl_state["finished_at"] = None
        _crawl_state["error"] = None
        return {"deleted": deleted, "status": "cleared"}
    except Exception as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(exc)) from exc
