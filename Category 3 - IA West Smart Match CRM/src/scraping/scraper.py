"""
Web scraping pipeline for university event discovery.

Module: src/scraping/scraper.py
Dependencies: beautifulsoup4, playwright, requests, urllib.robotparser
"""

import hashlib
import ipaddress
import json
import logging
import os
import socket
import threading
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup  # noqa: F401 – used downstream

from src.config import CACHE_DIR

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNIVERSITY_TARGETS: dict[str, dict[str, str]] = {
    "UCLA": {
        "url": "https://career.ucla.edu/events/",
        "method": "bs4",
        "label": "UCLA Career Center Events",
        "region": "Los Angeles",
    },
    "SDSU": {
        "url": "https://www.sdsu.edu/events-calendar",
        "method": "playwright",
        "label": "San Diego State University Events",
        "region": "San Diego",
    },
    "UC Davis": {
        "url": "https://careercenter.ucdavis.edu/career-center-services/career-fairs",
        "method": "bs4",
        "label": "UC Davis Career Fairs",
        "region": "San Francisco",
    },
    "USC": {
        "url": "https://careers.usc.edu/events/",
        "method": "bs4",
        "label": "USC Career Center Events",
        "region": "Los Angeles",
    },
    "Portland State": {
        "url": "https://www.pdx.edu/careers/events",
        "method": "bs4",
        "label": "Portland State University Career Events",
        "region": "Portland",
    },
}

DEFAULT_CACHE_DIR: str = str(CACHE_DIR / "scrapes")
RATE_LIMIT_SECONDS: float = 5.0
CACHE_TTL_HOURS: int = 24
ALLOWED_CUSTOM_HOST_SUFFIXES: tuple[str, ...] = (".edu",)
USER_AGENT: str = (
    "IASmartMatchBot/1.0 (+https://github.com/ia-west-smartmatch; "
    "educational-hackathon-project)"
)
CACHE_ONLY_SCRAPE_ENV: str = "SMARTMATCH_CACHE_ONLY"


# ---------------------------------------------------------------------------
# DNS resolution & SSRF protection
# ---------------------------------------------------------------------------


def _resolve_validated_ips(hostname: str) -> frozenset:
    """Resolve hostname to IPs and validate all are public.

    Returns a frozenset of validated ``ipaddress`` objects.
    Raises ValueError on DNS failure or if any resolved IP is non-public.
    """
    try:
        resolved_ips = frozenset(
            ipaddress.ip_address(info[4][0])
            for info in socket.getaddrinfo(hostname, None)
        )
    except socket.gaierror as exc:
        raise ValueError(f"Could not resolve hostname: {hostname}") from exc

    for ip in resolved_ips:
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        ):
            raise ValueError("Custom URL must resolve to a public internet host")

    return resolved_ips


# ---------------------------------------------------------------------------
# URL validation
# ---------------------------------------------------------------------------


def validate_public_demo_url(url: str) -> None:
    """
    Reject SSRF-style targets and constrain demo scraping to public university
    hosts only.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Custom URL must use http:// or https://")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("Custom URL must include a valid hostname")

    normalized_host = hostname.lower()
    if normalized_host in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Localhost targets are not allowed")

    allowed_hosts = {
        urlparse(cfg["url"]).hostname.lower()
        for cfg in UNIVERSITY_TARGETS.values()
        if urlparse(cfg["url"]).hostname
    }

    _resolve_validated_ips(hostname)

    if normalized_host not in allowed_hosts and not normalized_host.endswith(
        ALLOWED_CUSTOM_HOST_SUFFIXES
    ):
        raise ValueError("Custom URL must target a public university domain")


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


def _cache_key(url: str) -> str:
    """Generate a filesystem-safe cache key from a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def _cache_path(url: str, cache_dir: str) -> str:
    """Return the full path for a cached scrape result."""
    return os.path.join(cache_dir, f"{_cache_key(url)}.json")


def load_from_cache(
    url: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
    *,
    allow_expired: bool = False,
) -> dict[str, Any] | None:
    """
    Load a cached scrape result if it exists and has not expired.

    Returns
    -------
    dict with keys {html, scraped_at, url, method, ttl_hours}
        if cache hit and TTL has not expired.
    None
        if cache miss, expired, or corrupted timestamp.
    """
    path = _cache_path(url, cache_dir)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load scrape cache for %s: %s", url, exc)
        return None

    if not isinstance(data, dict):
        logger.warning("Invalid scrape cache payload for %s: expected object", url)
        return None

    try:
        scraped_at = datetime.fromisoformat(data["scraped_at"])
    except (ValueError, KeyError):
        return None

    # Backward compat: assume UTC if naive timestamp
    if scraped_at.tzinfo is None:
        scraped_at = scraped_at.replace(tzinfo=UTC)

    ttl = timedelta(hours=data.get("ttl_hours", CACHE_TTL_HOURS))
    cache_age = datetime.now(UTC) - scraped_at
    is_stale = cache_age > ttl
    if is_stale and not allow_expired:
        return None  # expired

    hydrated = dict(data)
    hydrated["scraped_at"] = scraped_at.isoformat()
    hydrated["cache_age_hours"] = round(cache_age.total_seconds() / 3600, 2)
    hydrated["is_stale"] = is_stale
    return hydrated


def _cache_result_payload(
    cached: dict[str, Any],
    *,
    source: str,
    message: str | None = None,
) -> dict[str, Any]:
    """Return a normalized scrape payload for cached or stale cache hits."""
    payload = dict(cached)
    payload["source"] = source
    payload["robots_ok"] = True
    if message:
        payload["message"] = message
    return payload


def _cache_only_mode_enabled() -> bool:
    """Return whether scraping should avoid live network calls."""
    return os.getenv(CACHE_ONLY_SCRAPE_ENV, "").strip().lower() in {"1", "true", "yes", "on"}


def save_to_cache(
    url: str,
    html: str,
    method: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> str:
    """
    Persist a scrape result to the JSON cache.

    Returns the path of the written cache file.
    """
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(url, cache_dir)
    payload = {
        "url": url,
        "html": html,
        "scraped_at": datetime.now(UTC).isoformat(),
        "ttl_hours": CACHE_TTL_HOURS,
        "method": method,
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    return path


# ---------------------------------------------------------------------------
# robots.txt compliance
# ---------------------------------------------------------------------------


def check_robots_txt(url: str) -> bool:
    """
    Return True if our user-agent is allowed to fetch *url* per robots.txt.

    Falls back to True (allowed) on network errors so that the scrape can
    still proceed with a logged warning.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        logger.warning("Could not read robots.txt for %s, assuming allowed", url)
        return True
    return rp.can_fetch(USER_AGENT, url)


# ---------------------------------------------------------------------------
# Rate limiter (module-level state, thread-safe)
# ---------------------------------------------------------------------------

_last_request_time: float = 0.0
_rate_limit_lock = threading.Lock()


def _rate_limit() -> None:
    """Block until RATE_LIMIT_SECONDS have elapsed since the last request."""
    global _last_request_time
    with _rate_limit_lock:
        elapsed = time.time() - _last_request_time
        if elapsed < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - elapsed)
        _last_request_time = time.time()


# ---------------------------------------------------------------------------
# Scraping backends
# ---------------------------------------------------------------------------


def _scrape_bs4(url: str) -> str:
    """
    Fetch a page via requests + BeautifulSoup (static HTML).

    Returns raw HTML as a string.
    Raises requests.HTTPError on non-2xx status.
    """
    _rate_limit()
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def _validated_scrape_bs4(url: str, resolved_ips: frozenset) -> str:
    """Fetch a page using pre-resolved IPs to prevent DNS rebinding (TOCTOU).

    Temporarily pins ``socket.getaddrinfo`` for the target hostname to a
    pre-validated public IP, ensuring the HTTP request connects to the
    same address that was verified as non-private.  TLS certificate
    verification works normally because the original hostname is retained.
    """
    _rate_limit()
    parsed = urlparse(url)
    target_ip = str(next(iter(resolved_ips)))

    original_getaddrinfo = socket.getaddrinfo

    def _pinned_getaddrinfo(host, port, *args, **kwargs):
        if host == parsed.hostname:
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "",
                     (target_ip, port or 443))]
        return original_getaddrinfo(host, port, *args, **kwargs)

    socket.getaddrinfo = _pinned_getaddrinfo
    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    finally:
        socket.getaddrinfo = original_getaddrinfo


def _scrape_playwright(url: str) -> str:
    """
    Fetch a page via Playwright (JS-rendered content).

    Returns rendered HTML as a string.
    """
    import asyncio

    async def _fetch() -> str:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=USER_AGENT)
            _rate_limit()
            await page.goto(url, wait_until="networkidle", timeout=30_000)
            content = await page.content()
            await browser.close()
            return content

    return asyncio.run(_fetch())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scrape_university(
    url: str,
    method: Literal["bs4", "playwright"] = "bs4",
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> dict[str, Any]:
    """
    Scrape a university event page with caching, rate-limiting, and
    robots.txt compliance.

    Raises
    ------
    PermissionError
        If robots.txt disallows scraping the URL.
    """
    validate_public_demo_url(url)

    # 1. Check cache first
    cached = load_from_cache(url, cache_dir)
    if cached is not None:
        return _cache_result_payload(cached, source="cache")

    stale_cached = load_from_cache(url, cache_dir, allow_expired=True)

    if _cache_only_mode_enabled():
        if stale_cached is not None:
            source = "cache" if not stale_cached.get("is_stale") else "stale_cache"
            message = None
            if source == "stale_cache":
                message = (
                    "Live scrape unavailable. Showing cached results from "
                    f"{stale_cached.get('scraped_at')}."
                )
            return _cache_result_payload(stale_cached, source=source, message=message)
        raise RuntimeError(
            "Cache-only scraping mode is enabled, but no cached scrape artifact exists "
            f"for {url}."
        )

    # 2. robots.txt compliance
    robots_ok = check_robots_txt(url)
    if not robots_ok:
        raise PermissionError(
            f"robots.txt disallows scraping {url} for user-agent {USER_AGENT}"
        )

    # 3. Re-resolve DNS just-in-time to close the TOCTOU gap between
    #    validate_public_demo_url() and the actual HTTP request.
    parsed = urlparse(url)
    resolved_ips = _resolve_validated_ips(parsed.hostname)

    # 4. Live scrape
    try:
        if method == "playwright":
            html = _scrape_playwright(url)
        else:
            html = _validated_scrape_bs4(url, resolved_ips)
    except Exception as exc:
        if stale_cached is not None:
            return _cache_result_payload(
                stale_cached,
                source="stale_cache",
                message=(
                    "Live scrape unavailable. Showing cached results from "
                    f"{stale_cached.get('scraped_at')}."
                ),
            )
        raise exc

    # 5. Cache the result
    save_to_cache(url, html, method, cache_dir)

    return {
        "html": html,
        "scraped_at": datetime.now(UTC).isoformat(),
        "url": url,
        "method": method,
        "source": "live",
        "ttl_hours": CACHE_TTL_HOURS,
        "robots_ok": True,
    }


def scrape_all_universities(
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> dict[str, dict[str, Any]]:
    """
    Scrape all pre-configured universities.

    Returns a dict keyed by university name. Each value is the result
    of scrape_university() on success, or an error dict on failure.
    """
    results: dict[str, dict[str, Any]] = {}
    for name, cfg in UNIVERSITY_TARGETS.items():
        try:
            result = scrape_university(
                url=cfg["url"],
                method=cfg["method"],  # type: ignore[arg-type]
                cache_dir=cache_dir,
            )
            results[name] = result
        except Exception as exc:
            logger.error("Failed to scrape %s: %s", name, exc)
            results[name] = {
                "error": str(exc),
                "url": cfg["url"],
                "source": "failed",
            }
    return results
