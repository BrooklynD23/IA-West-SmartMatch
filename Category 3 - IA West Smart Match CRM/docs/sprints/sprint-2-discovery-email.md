---
doc_role: canonical
authority_scope:
- category.3.sprint.2
canonical_upstreams:
- Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md
- PRD_SECTION_CAT3.md
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-18'
managed_by: planning-agent
---

# Sprint 2: Discovery + Email + Track B Kickoff -- "The Reach"

**Duration:** Days 6-8
**Track:** Both (A + B start)
**Hours:** Track A 21-24h, Track B 18-24h

> **Governance notice:** This sprint spec is downstream of `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` and `PRD_SECTION_CAT3.md`. Use `archived/general_project_docs/MASTER_SPRINT_PLAN.md` and `archived/general_project_docs/STRATEGIC_REVIEW.md` only for portfolio context. Do not treat `Category 3 - IA West Smart Match CRM/PLAN.md` as a source of execution authority.

**Prerequisites (from Sprint 1 Go/No-Go Gate):**
- Matching engine produces explainable, sensible top-3 per event
- Weight sliders visibly change rankings
- At least 3/5 university scrape targets confirmed viable (from A1.7 research)
- `pipeline_sample_data.csv` generated with real match outputs

---

## Track A Tasks

---

### A2.1: Web Scraping Pipeline -- Core (5.0h)

**File:** `src/scraping/scraper.py`

#### Specification

```python
"""
Web scraping pipeline for university event discovery.

Module: src/scraping/scraper.py
Dependencies: beautifulsoup4, playwright, requests, urllib.robotparser
"""

from typing import Literal, Any
import json
import time
import hashlib
import ipaddress
import os
import socket
from datetime import datetime, timedelta
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

UNIVERSITY_TARGETS: dict[str, dict[str, str]] = {
    "UCLA": {
        "url": "https://career.ucla.edu/events/",
        "method": "bs4",
        "label": "UCLA Career Center Events",
    },
    "SDSU": {
        "url": "https://www.sdsu.edu/events-calendar",
        "method": "playwright",
        "label": "San Diego State University Events",
    },
    "UC Davis": {
        "url": "https://careercenter.ucdavis.edu/career-center-services/career-fairs",
        "method": "bs4",
        "label": "UC Davis Career Fairs",
    },
    "USC": {
        "url": "https://careers.usc.edu/events/",
        "method": "bs4",
        "label": "USC Career Center Events",
    },
    "Portland State": {
        "url": "https://www.pdx.edu/careers/events",
        "method": "bs4",
        "label": "Portland State University Career Events",
    },
}

DEFAULT_CACHE_DIR: str = "cache/scrapes"
RATE_LIMIT_SECONDS: float = 5.0
CACHE_TTL_HOURS: int = 24
ALLOWED_CUSTOM_HOST_SUFFIXES: tuple[str, ...] = (".edu",)
USER_AGENT: str = (
    "IASmartMatchBot/1.0 (+https://github.com/ia-west-smartmatch; "
    "educational-hackathon-project)"
)


# ---------------------------------------------------------------------------
# Cache helpers
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

    try:
        resolved_ips = {
            ipaddress.ip_address(info[4][0])
            for info in socket.getaddrinfo(hostname, None)
        }
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

    if normalized_host not in allowed_hosts and not normalized_host.endswith(ALLOWED_CUSTOM_HOST_SUFFIXES):
        raise ValueError("Custom URL must target a public university domain")


def _cache_key(url: str) -> str:
    """Generate a filesystem-safe cache key from a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def _cache_path(url: str, cache_dir: str) -> str:
    """Return the full path for a cached scrape result."""
    return os.path.join(cache_dir, f"{_cache_key(url)}.json")


def load_from_cache(
    url: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> dict[str, Any] | None:
    """
    Load a cached scrape result if it exists and has not expired.

    Returns
    -------
    dict with keys {html, scraped_at, url, method, ttl_hours}
        if cache hit and TTL has not expired.
    None
        if cache miss or expired.
    """
    path = _cache_path(url, cache_dir)
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as fh:
        data: dict[str, Any] = json.load(fh)

    scraped_at = datetime.fromisoformat(data["scraped_at"])
    ttl = timedelta(hours=data.get("ttl_hours", CACHE_TTL_HOURS))
    if datetime.utcnow() - scraped_at > ttl:
        return None  # expired
    return data


def save_to_cache(
    url: str,
    html: str,
    method: str,
    cache_dir: str = DEFAULT_CACHE_DIR,
) -> str:
    """
    Persist a scrape result to the JSON cache.

    Cache JSON structure
    --------------------
    {
        "url": "https://career.ucla.edu/events/",
        "html": "<html>...</html>",
        "scraped_at": "2026-03-17T14:30:00",
        "ttl_hours": 24,
        "method": "bs4"
    }

    Returns the path of the written cache file.
    """
    os.makedirs(cache_dir, exist_ok=True)
    path = _cache_path(url, cache_dir)
    payload = {
        "url": url,
        "html": html,
        "scraped_at": datetime.utcnow().isoformat(),
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
    from urllib.parse import urlparse

    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        # If robots.txt is unreachable, assume allowed but log warning
        return True
    return rp.can_fetch(USER_AGENT, url)


# ---------------------------------------------------------------------------
# Rate limiter (module-level state)
# ---------------------------------------------------------------------------

_last_request_time: float = 0.0


def _rate_limit() -> None:
    """Block until RATE_LIMIT_SECONDS have elapsed since the last request."""
    global _last_request_time
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


def _scrape_playwright(url: str) -> str:
    """
    Fetch a page via Playwright (JS-rendered content).

    IMPORTANT: Playwright requires an async context.  Streamlit runs its own
    event loop, so we use asyncio.run() inside a synchronous wrapper.

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

    Parameters
    ----------
    url : str
        The target URL to scrape.
    method : {"bs4", "playwright"}
        Which backend to use.  "bs4" for static HTML pages; "playwright"
        for pages that require JavaScript rendering.
    cache_dir : str
        Directory for the JSON file cache.  Defaults to "cache/scrapes".

    Returns
    -------
    dict with keys:
        html        : str   -- raw HTML content
        scraped_at  : str   -- ISO-8601 timestamp of the scrape
        url         : str   -- the original URL
        method      : str   -- scraping method used
        source      : str   -- "cache" | "live"
        ttl_hours   : int   -- cache time-to-live
        robots_ok   : bool  -- whether robots.txt permits scraping

    Raises
    ------
    PermissionError
        If robots.txt disallows scraping the URL.
    requests.HTTPError
        On non-2xx HTTP responses (bs4 backend).
    playwright._impl._errors.TimeoutError
        On page load timeout (playwright backend).
    """
    validate_public_demo_url(url)

    # 1. Check cache first
    cached = load_from_cache(url, cache_dir)
    if cached is not None:
        cached["source"] = "cache"
        cached["robots_ok"] = True  # was checked on original scrape
        return cached

    # 2. robots.txt compliance
    robots_ok = check_robots_txt(url)
    if not robots_ok:
        raise PermissionError(
            f"robots.txt disallows scraping {url} for user-agent {USER_AGENT}"
        )

    # 3. Live scrape
    if method == "playwright":
        html = _scrape_playwright(url)
    else:
        html = _scrape_bs4(url)

    # 4. Cache the result
    save_to_cache(url, html, method, cache_dir)

    return {
        "html": html,
        "scraped_at": datetime.utcnow().isoformat(),
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

    Returns a dict keyed by university name.  Each value is the result
    of scrape_university() on success, or an error dict on failure:
        {"error": str, "url": str, "source": "failed"}
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
            results[name] = {
                "error": str(exc),
                "url": cfg["url"],
                "source": "failed",
            }
    return results
```

#### Acceptance Criteria

- [ ] `scrape_university()` returns valid HTML for all 5 university targets
- [ ] Cache correctly stores results as JSON with `scraped_at` timestamp
- [ ] Cache returns stored result when called within 24h TTL
- [ ] Cache returns `None` (cache miss) after TTL expiration
- [ ] `check_robots_txt()` correctly reads and respects robots.txt directives
- [ ] `validate_public_demo_url()` rejects localhost, private IPs, link-local ranges, and non-`http/https` schemes
- [ ] Custom URLs outside approved public university hosts fail closed with a user-visible validation error
- [ ] Rate limiter enforces minimum 5-second gap between requests
- [ ] `_scrape_playwright()` handles JS-rendered pages (SDSU confirmed from Sprint 1 A1.7)
- [ ] `_scrape_bs4()` handles static HTML pages (UCLA, UC Davis, USC confirmed)
- [ ] `scrape_all_universities()` returns results or error dicts for all 5 targets
- [ ] Graceful failure: network errors return error dict, do not crash the app
- [ ] `PermissionError` raised when robots.txt disallows scraping

#### Harness Guidelines

- Place all scraping code in `src/scraping/scraper.py`
- Create `src/scraping/__init__.py` with public exports: `scrape_university`, `scrape_all_universities`, `UNIVERSITY_TARGETS`
- Cache files go in `cache/scrapes/` (add `cache/` to `.gitignore`)
- Keep custom-URL validation in `src/scraping/scraper.py` so every caller shares the same SSRF guard
- Unit tests in `tests/test_scraper.py` -- mock HTTP responses, do not make live requests in tests
- Use `pytest-httpserver` or `responses` library for mocking HTTP

#### Steer Guidelines

- Playwright requires an async context -- use `asyncio.run()` wrapper for Streamlit compatibility
- If Playwright is not installed in the environment, fall back to `bs4` with a logged warning
- Portland State URL is TBD -- use `https://www.pdx.edu/careers/events` as the best guess; if it fails during testing, replace with the actual URL from Sprint 1 A1.7 research notes
- SDSU uses heavy JavaScript -- confirm Playwright works for this target; if not, pre-cache HTML and mark as "cached-only" in the UI
- On Streamlit Community Cloud, Playwright will likely not work (no browser binary) -- the UI must gracefully fall back to cached results

---

### A2.2: LLM Extraction Pipeline (4.0h)

**File:** `src/extraction/llm_extractor.py`

#### Specification

```python
"""
LLM-based structured data extraction from scraped HTML.

Module: src/extraction/llm_extractor.py
Dependencies: Gemini API helper in `src/gemini_client.py`, beautifulsoup4
"""

from typing import Any
import json
import logging

from gemini import Gemini
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

EXTRACTED_EVENT_SCHEMA: dict[str, str] = {
    "event_name": "str -- name of the event",
    "category": "str -- one of: hackathon, career_fair, case_competition, "
                "symposium, guest_lecture, networking, workshop, other",
    "date_or_recurrence": "str -- specific date (YYYY-MM-DD) or recurrence "
                          "pattern (e.g., 'Every Tuesday in Fall quarter')",
    "volunteer_roles": "list[str] -- roles needed: judge, mentor, speaker, "
                       "panelist, advisor, reviewer",
    "primary_audience": "str -- e.g., 'undergraduate CS students', "
                        "'MBA candidates', 'all majors'",
    "contact_name": "str | null -- name of event organizer if found",
    "contact_email": "str | null -- email of event organizer if found",
    "url": "str -- direct URL to the event page",
}


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT: str = """\
You are a structured data extraction assistant for the IA SmartMatch CRM \
system.  Your job is to extract university event information from raw HTML \
or text content.

You MUST return ONLY a valid JSON array.  No markdown fencing, no \
explanation text, no commentary.  If you find zero events, return an \
empty array: []

Each object in the array MUST conform to this schema:
{
  "event_name": "<string>",
  "category": "<hackathon|career_fair|case_competition|symposium|guest_lecture|networking|workshop|other>",
  "date_or_recurrence": "<YYYY-MM-DD or recurrence description>",
  "volunteer_roles": ["<judge|mentor|speaker|panelist|advisor|reviewer>"],
  "primary_audience": "<string>",
  "contact_name": "<string or null>",
  "contact_email": "<string or null>",
  "url": "<string>"
}

Focus on events where industry professionals are needed as judges, mentors, \
speakers, panelists, or advisors.  Ignore purely student-only social events, \
athletic events, or administrative meetings.

If a field cannot be determined from the content, use null for optional \
fields (contact_name, contact_email) or "unknown" for required string \
fields.\
"""

EXTRACTION_USER_PROMPT_TEMPLATE: str = """\
Extract structured event data from the following {university} webpage content.

Source URL: {url}

--- BEGIN CONTENT ---
{content}
--- END CONTENT ---

Return a JSON array of events.  Include ONLY events where industry \
professionals could volunteer as judges, mentors, speakers, or panelists.\
"""


# ---------------------------------------------------------------------------
# Few-shot examples (included in the system prompt for better extraction)
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES: str = """\

Here are examples of correct extractions:

Example Input (partial HTML):
<div class="event-card">
  <h3>Spring Data Science Hackathon 2026</h3>
  <p>Date: April 20, 2026</p>
  <p>Looking for industry judges and mentors in data science, ML, and AI.</p>
  <p>Open to all undergraduate and graduate students.</p>
  <p>Contact: Dr. Sarah Chen, schen@university.edu</p>
</div>

Example Output:
[
  {
    "event_name": "Spring Data Science Hackathon 2026",
    "category": "hackathon",
    "date_or_recurrence": "2026-04-20",
    "volunteer_roles": ["judge", "mentor"],
    "primary_audience": "undergraduate and graduate students",
    "contact_name": "Dr. Sarah Chen",
    "contact_email": "schen@university.edu",
    "url": "https://university.edu/events/hackathon-2026"
  }
]

Example Input (partial HTML):
<div class="event-listing">
  <h2>Industry Speaker Series</h2>
  <span class="date">Every Wednesday, Winter Quarter</span>
  <p>We invite professionals from tech, marketing, and research to share
  career insights with our business students.</p>
  <a href="mailto:speakerseries@uni.edu">Apply to speak</a>
</div>

Example Output:
[
  {
    "event_name": "Industry Speaker Series",
    "category": "guest_lecture",
    "date_or_recurrence": "Every Wednesday, Winter Quarter",
    "volunteer_roles": ["speaker"],
    "primary_audience": "business students",
    "contact_name": null,
    "contact_email": "speakerseries@uni.edu",
    "url": "https://uni.edu/events/speaker-series"
  }
]

Example Input (partial HTML):
<article>
  <h3>Career Expo: Meet the Firms</h3>
  <time datetime="2026-10-15">October 15, 2026</time>
  <p>Annual career fair connecting students with employers.  Recruiters
  and hiring managers from 50+ companies.  All majors welcome.</p>
  <p>Employer registration: careers@university.edu</p>
</article>

Example Output:
[
  {
    "event_name": "Career Expo: Meet the Firms",
    "category": "career_fair",
    "date_or_recurrence": "2026-10-15",
    "volunteer_roles": ["panelist", "advisor"],
    "primary_audience": "all majors",
    "contact_name": null,
    "contact_email": "careers@university.edu",
    "url": "https://university.edu/career-expo"
  }
]
"""


# ---------------------------------------------------------------------------
# HTML pre-processing
# ---------------------------------------------------------------------------

def preprocess_html(raw_html: str, max_chars: int = 12_000) -> str:
    """
    Strip non-content HTML (scripts, styles, nav, footer) and truncate
    to fit within LLM context limits.

    Parameters
    ----------
    raw_html : str
        Full HTML page content.
    max_chars : int
        Maximum character count for the extracted text.  Gemini
        has a 128k context window, but we keep input small for cost
        and speed.  12,000 chars ~ 3,000 tokens.

    Returns
    -------
    str
        Cleaned text content suitable for LLM extraction.
    """
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove non-content elements
    for tag in soup.find_all(
        ["script", "style", "nav", "footer", "header", "noscript", "iframe"]
    ):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse excessive whitespace
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n[TRUNCATED]"

    return cleaned


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_events(
    raw_html: str,
    university: str,
    url: str,
    model: str = "gemini-2.5-flash-lite",
    temperature: float = 0.1,
) -> list[dict[str, Any]]:
    """
    Extract structured event data from raw HTML using Gemini.

    Parameters
    ----------
    raw_html : str
        The scraped HTML content.
    university : str
        Name of the university (e.g., "UCLA").
    url : str
        Source URL of the scraped page.
    model : str
        Gemini model identifier.
    temperature : float
        Sampling temperature.  Low (0.1) for deterministic extraction.

    Returns
    -------
    list[dict]
        A list of extracted event dictionaries conforming to
        EXTRACTED_EVENT_SCHEMA.  Returns an empty list on any failure.
    """
    content = preprocess_html(raw_html)

    if len(content.strip()) < 50:
        logger.warning("Preprocessed HTML too short (%d chars) for %s", len(content), url)
        return []

    system_message = EXTRACTION_SYSTEM_PROMPT + FEW_SHOT_EXAMPLES

    user_message = EXTRACTION_USER_PROMPT_TEMPLATE.format(
        university=university,
        url=url,
        content=content,
    )

    client = Gemini()  # reads GEMINI_API_KEY from env

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )

        raw_output = response.choices[0].message.content or ""
        events = _parse_and_validate(raw_output, url)
        return events

    except Exception as exc:
        logger.error("LLM extraction failed for %s: %s", url, exc)
        return []


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

VALID_CATEGORIES: set[str] = {
    "hackathon", "career_fair", "case_competition", "symposium",
    "guest_lecture", "networking", "workshop", "other",
}

VALID_ROLES: set[str] = {
    "judge", "mentor", "speaker", "panelist", "advisor", "reviewer",
}


def _parse_and_validate(
    raw_json: str,
    source_url: str,
) -> list[dict[str, Any]]:
    """
    Parse LLM JSON output and validate each event against the schema.

    Handles two response shapes:
    - Direct JSON array: [{ ... }, { ... }]
    - Wrapped object: {"events": [{ ... }, { ... }]}

    Invalid events are logged and skipped (not included in output).
    """
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error for %s: %s", source_url, exc)
        return []

    # Handle wrapped response
    if isinstance(parsed, dict):
        if "events" in parsed:
            parsed = parsed["events"]
        else:
            # Single event wrapped in an object
            parsed = [parsed]

    if not isinstance(parsed, list):
        logger.error("Expected list, got %s for %s", type(parsed).__name__, source_url)
        return []

    validated: list[dict[str, Any]] = []
    for i, event in enumerate(parsed):
        if not isinstance(event, dict):
            logger.warning("Skipping non-dict event at index %d for %s", i, source_url)
            continue

        # Required fields
        if not event.get("event_name"):
            logger.warning("Skipping event without event_name at index %d", i)
            continue

        # Normalize category
        cat = event.get("category", "other")
        if cat not in VALID_CATEGORIES:
            event["category"] = "other"

        # Normalize volunteer_roles
        roles = event.get("volunteer_roles", [])
        if isinstance(roles, str):
            roles = [roles]
        event["volunteer_roles"] = [r for r in roles if r in VALID_ROLES]

        # Ensure url field
        if not event.get("url"):
            event["url"] = source_url

        validated.append(event)

    logger.info("Extracted %d valid events from %s", len(validated), source_url)
    return validated
```

#### JSON Output Schema (complete)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": ["event_name", "category", "date_or_recurrence", "volunteer_roles", "primary_audience", "url"],
    "properties": {
      "event_name": { "type": "string", "minLength": 1 },
      "category": {
        "type": "string",
        "enum": ["hackathon", "career_fair", "case_competition", "symposium", "guest_lecture", "networking", "workshop", "other"]
      },
      "date_or_recurrence": { "type": "string" },
      "volunteer_roles": {
        "type": "array",
        "items": {
          "type": "string",
          "enum": ["judge", "mentor", "speaker", "panelist", "advisor", "reviewer"]
        }
      },
      "primary_audience": { "type": "string" },
      "contact_name": { "type": ["string", "null"] },
      "contact_email": { "type": ["string", "null"] },
      "url": { "type": "string", "format": "uri" }
    }
  }
}
```

#### Acceptance Criteria

- [ ] `preprocess_html()` removes script/style/nav/footer tags and truncates to 12,000 chars
- [ ] `extract_events()` returns a list of dicts conforming to `EXTRACTED_EVENT_SCHEMA`
- [ ] Few-shot examples are included in the system prompt (3 examples provided)
- [ ] `response_format={"type": "json_object"}` used for reliable JSON output
- [ ] `_parse_and_validate()` handles both direct arrays `[{...}]` and wrapped objects `{"events": [{...}]}`
- [ ] Invalid categories are normalized to "other"
- [ ] Invalid volunteer roles are filtered out
- [ ] Events without `event_name` are skipped with a warning log
- [ ] LLM API failures return an empty list (not an exception)
- [ ] Extraction produces valid JSON for 80%+ of scraped university pages
- [ ] Temperature set to 0.1 for deterministic extraction
- [ ] Token usage is logged for cost tracking

#### Harness Guidelines

- Place extraction code in `src/extraction/llm_extractor.py`
- Create `src/extraction/__init__.py` with public exports: `extract_events`, `preprocess_html`, `EXTRACTED_EVENT_SCHEMA`
- Unit tests in `tests/test_llm_extractor.py` -- mock Gemini API responses
- Include a fixture file `tests/fixtures/sample_university_html.html` with a realistic university event page for testing
- Integration test (marked `@pytest.mark.integration`) that calls the real Gemini API with a small HTML sample

#### Steer Guidelines

- Use `response_format={"type": "json_object"}` to force JSON output from Gemini; this avoids markdown fencing issues
- Pre-process HTML aggressively: remove nav, footer, scripts, styles -- these waste tokens and confuse extraction
- 12,000 character limit for preprocessed text keeps API costs low (~3,000 tokens input per call)
- If the model returns a wrapped object like `{"events": [...]}`, unwrap it before validation
- Log extraction failures with full context (URL, error message) but never raise -- callers expect empty list on failure

---

### A2.3: Discovery Tab UI (3.5h)

**File:** `src/ui/discovery_tab.py`

#### Specification

```python
"""
Discovery tab UI for the IA SmartMatch Streamlit application.

Module: src/ui/discovery_tab.py
Dependencies: streamlit, pandas
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from src.scraping.scraper import (
    scrape_university,
    UNIVERSITY_TARGETS,
    load_from_cache,
)
from src.extraction.llm_extractor import extract_events


def render_discovery_tab() -> None:
    """Render the Discovery tab in the Streamlit application."""

    st.header("University Event Discovery")
    st.caption(
        "Automatically discover volunteer opportunities at universities "
        "across the West Coast corridor."
    )

    # ---------------------------------------------------------------
    # University selector
    # ---------------------------------------------------------------
    col_select, col_custom = st.columns([2, 1])

    with col_select:
        university_options = list(UNIVERSITY_TARGETS.keys()) + ["Custom URL"]
        selected = st.selectbox(
            "Select University",
            options=university_options,
            index=0,
            key="discovery_university_select",
        )

    with col_custom:
        custom_url = ""
        if selected == "Custom URL":
            custom_url = st.text_input(
                "Enter URL",
                placeholder="https://university.edu/events/",
                key="discovery_custom_url",
            )

    # ---------------------------------------------------------------
    # Status indicators
    # ---------------------------------------------------------------
    if selected != "Custom URL":
        target_url = UNIVERSITY_TARGETS[selected]["url"]
        cached = load_from_cache(target_url)
        if cached is not None:
            scraped_at = datetime.fromisoformat(cached["scraped_at"])
            st.info(
                f"Cached -- last scraped {scraped_at.strftime('%Y-%m-%d %H:%M UTC')}"
            )
        else:
            st.warning("No cache available -- will perform live scrape")
    else:
        target_url = custom_url

    # ---------------------------------------------------------------
    # Discover Events button
    # ---------------------------------------------------------------
    if st.button(
        "Discover Events",
        type="primary",
        key="discovery_scrape_button",
        disabled=(selected == "Custom URL" and not custom_url),
    ):
        with st.spinner("Scraping and extracting events..."):
            _run_discovery(target_url, selected)

    # ---------------------------------------------------------------
    # Results display
    # ---------------------------------------------------------------
    if "discovery_results" in st.session_state:
        _render_results()


def _run_discovery(url: str, university: str) -> None:
    """Execute scrape + extraction and store results in session state."""
    try:
        scrape_result = scrape_university(
            url=url,
            method=UNIVERSITY_TARGETS.get(university, {}).get("method", "bs4"),
        )
        source = scrape_result["source"]  # "cache" or "live"

        events = extract_events(
            raw_html=scrape_result["html"],
            university=university,
            url=url,
        )

        st.session_state["discovery_results"] = events
        st.session_state["discovery_source"] = source
        st.session_state["discovery_url"] = url
        st.session_state["discovery_university"] = university
        st.session_state["discovery_scraped_at"] = scrape_result["scraped_at"]

        if source == "live":
            st.success(f"Live scrape complete -- {len(events)} events found")
        else:
            st.info(f"Using cached data -- {len(events)} events found")

    except ValueError as exc:
        st.error(str(exc))
    except PermissionError:
        st.error("robots.txt disallows scraping this URL.")
    except Exception as exc:
        # Try cached fallback
        cached = load_from_cache(url)
        if cached is not None:
            events = extract_events(
                raw_html=cached["html"],
                university=university,
                url=url,
            )
            st.session_state["discovery_results"] = events
            st.session_state["discovery_source"] = "failed_using_cached"
            st.warning(
                f"Live scrape failed ({exc}). Using cached data -- "
                f"{len(events)} events found."
            )
        else:
            st.error(f"Scraping failed and no cached data available: {exc}")


def _render_results() -> None:
    """Render the extracted events table with action buttons."""
    events = st.session_state["discovery_results"]
    source = st.session_state["discovery_source"]

    if not events:
        st.info("No volunteer-relevant events found on this page.")
        return

    # Status badge
    source_labels = {
        "live": "Live Scrape",
        "cache": "Cached",
        "failed_using_cached": "Failed -- Using Cached",
    }
    st.caption(f"Source: **{source_labels.get(source, source)}** | "
               f"Scraped: {st.session_state.get('discovery_scraped_at', 'unknown')}")

    # Build dataframe for display
    df = pd.DataFrame(events)
    display_cols = [
        "event_name", "category", "date_or_recurrence",
        "volunteer_roles", "primary_audience",
    ]
    existing_cols = [c for c in display_cols if c in df.columns]

    st.dataframe(
        df[existing_cols],
        use_container_width=True,
        hide_index=True,
    )

    # "Add to Matching" buttons per event
    st.subheader("Add Events to Matching Engine")
    for i, event in enumerate(events):
        col_name, col_cat, col_btn = st.columns([3, 2, 1])
        with col_name:
            st.write(event["event_name"])
        with col_cat:
            st.caption(event.get("category", "other"))
        with col_btn:
            if st.button(
                "Add to Matching",
                key=f"add_match_{i}",
            ):
                _add_to_matching(event)
                st.success(f"Added: {event['event_name']}")


def _add_to_matching(event: dict) -> None:
    """Add a discovered event to the matching engine's event pool."""
    if "discovered_events" not in st.session_state:
        st.session_state["discovered_events"] = []

    # Avoid duplicates
    existing_names = {
        e["event_name"] for e in st.session_state["discovered_events"]
    }
    if event["event_name"] not in existing_names:
        st.session_state["discovered_events"].append(event)
```

#### UI Wireframe

```
+============================================================+
|  IA SmartMatch                              [Weight Sliders] |
|  [Matches] [*Discovery*] [Pipeline]         in sidebar       |
+============================================================+
|                                                              |
|  University Event Discovery                                  |
|  Automatically discover volunteer opportunities at           |
|  universities across the West Coast corridor.                |
|                                                              |
|  +---------------------------+  +-------------------------+  |
|  | Select University    [v]  |  | Enter URL               |  |
|  | > UCLA                   |  | (greyed out unless       |  |
|  |   SDSU                   |  |  "Custom URL" selected)  |  |
|  |   UC Davis               |  +-------------------------+  |
|  |   USC                    |                                |
|  |   Portland State         |                                |
|  |   Custom URL             |                                |
|  +---------------------------+                               |
|                                                              |
|  [i] Cached -- last scraped 2026-03-17 14:30 UTC            |
|                                                              |
|  [ Discover Events ]  (primary button)                       |
|                                                              |
|  ---------------------------------------------------------- |
|                                                              |
|  Source: **Live Scrape** | Scraped: 2026-03-17T14:35:00     |
|                                                              |
|  +----------------------------------------------------------+
|  | event_name          | category     | date       | roles  |
|  |---------------------|--------------|------------|--------|
|  | Spring Hackathon    | hackathon    | 2026-04-20 | judge  |
|  | Career Expo 2026    | career_fair  | 2026-10-15 | panel  |
|  | Speaker Series      | guest_lec... | Weekly     | speak  |
|  +----------------------------------------------------------+
|                                                              |
|  Add Events to Matching Engine                               |
|  +--------------------------------------------------------+ |
|  | Spring Hackathon 2026       hackathon   [Add to Match]  | |
|  | Career Expo 2026            career_fair [Add to Match]  | |
|  | Industry Speaker Series     guest_lect  [Add to Match]  | |
|  +--------------------------------------------------------+ |
|                                                              |
+==============================================================+
```

#### Acceptance Criteria

- [ ] University selector dropdown displays all 5 pre-loaded universities plus "Custom URL"
- [ ] Custom URL text input appears only when "Custom URL" is selected
- [ ] "Discover Events" button is disabled when "Custom URL" is selected but no URL is entered
- [ ] Status indicator shows "Cached" with timestamp when cache exists
- [ ] Status indicator shows "No cache available" when no cache exists
- [ ] Spinner displays during scrape + extraction
- [ ] Results table shows event_name, category, date_or_recurrence, volunteer_roles, primary_audience
- [ ] "Add to Matching" button stores event in `st.session_state["discovered_events"]`
- [ ] Duplicate events are not added twice (deduplication by event_name)
- [ ] On scrape failure, falls back to cached data with warning message
- [ ] Source badge shows "Live Scrape" / "Cached" / "Failed -- Using Cached"
- [ ] Invalid custom URLs fail before any network call with a clear validation message

#### Harness Guidelines

- Place UI code in `src/ui/discovery_tab.py`
- `render_discovery_tab()` is called from the main app file within the Discovery tab context
- All state stored in `st.session_state` -- no global variables
- Reuse `validate_public_demo_url()` from `src.scraping.scraper` rather than duplicating URL checks in the UI
- Keep UI logic separate from scraping/extraction logic (thin UI layer)

#### Steer Guidelines

- `st.spinner()` wraps the entire scrape + extract flow to show progress
- Use `st.session_state` for all persistent data -- Streamlit re-runs the entire script on every interaction
- The "Add to Matching" button must integrate with the matching engine from Sprint 1 -- discovered events get embedded and scored alongside CPP events
- `_add_to_matching()` should trigger re-embedding of the added event (call the embedding pipeline from Sprint 0 A0.4)

---

### A2.4: Outreach Email Generation (3.0h)

**File:** `src/outreach/email_gen.py`

#### Specification

```python
"""
Outreach email generation using Gemini.

Module: src/outreach/email_gen.py
Dependencies: Gemini API helper in `src/gemini_client.py`
"""

from typing import Any
import hashlib
import json
import logging
from pathlib import Path

from gemini import Gemini


logger = logging.getLogger(__name__)
EMAIL_CACHE_DIR = Path("cache/emails")


def _event_value(event: dict[str, Any], *keys: str, default: str = "") -> Any:
    """Return the first present event value across literal CSV and derived keys."""
    for key in keys:
        value = event.get(key)
        if value not in (None, ""):
            return value
    return default


def _match_score_value(match_scores: dict[str, Any], canonical_key: str) -> float:
    """
    Support Sprint 1's canonical match-result schema:
      total_score
      factor_scores.topic_relevance / role_fit / geographic_proximity / ...
    while tolerating legacy shorthand aliases if they appear in cached/demo data.
    """
    alias_map = {
        "total_score": ("total_score", "total"),
        "topic_relevance": ("topic_relevance", "topic"),
        "role_fit": ("role_fit", "role"),
        "geographic_proximity": ("geographic_proximity", "geo"),
        "calendar_fit": ("calendar_fit", "calendar"),
        "historical_conversion": ("historical_conversion", "historical"),
        "student_interest": ("student_interest", "student_interest"),
    }

    if canonical_key in match_scores:
        return float(match_scores.get(canonical_key, 0.0) or 0.0)

    factor_scores = match_scores.get("factor_scores", {})
    if isinstance(factor_scores, dict) and canonical_key in factor_scores:
        return float(factor_scores.get(canonical_key, 0.0) or 0.0)

    for alias in alias_map.get(canonical_key, (canonical_key,)):
        if alias in match_scores:
            return float(match_scores.get(alias, 0.0) or 0.0)
        if isinstance(factor_scores, dict) and alias in factor_scores:
            return float(factor_scores.get(alias, 0.0) or 0.0)

    return 0.0


def _email_cache_key(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
) -> str:
    raw = "::".join(
        [
            str(speaker.get("Name", "")),
            str(event.get("event_id", _event_value(event, "Event / Program", "event_name", default=""))),
            f"{_match_score_value(match_scores, 'total_score'):.4f}",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_cached_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
) -> dict[str, str] | None:
    path = EMAIL_CACHE_DIR / f"{_email_cache_key(speaker, event, match_scores)}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_cached_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
    email: dict[str, str],
) -> None:
    EMAIL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = EMAIL_CACHE_DIR / f"{_email_cache_key(speaker, event, match_scores)}.json"
    path.write_text(json.dumps(email, ensure_ascii=True, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

EMAIL_SYSTEM_PROMPT: str = """\
You are a professional outreach coordinator for IA West (Insights Association \
West Chapter), a volunteer-run professional association for market research \
and data analytics professionals.

Your job is to draft personalized outreach emails inviting board member \
volunteers to participate in university events.  The emails should be:

1. Professional but warm -- not stiff corporate language
2. Specific -- reference the speaker's actual expertise and the event's \
   actual details
3. Concise -- 150-200 words maximum for the email body
4. Action-oriented -- clear call-to-action at the end

You MUST return a JSON object with exactly these keys:
{
  "subject_line": "<string>",
  "greeting": "<string>",
  "body": "<string>",
  "closing": "<string>",
  "full_email": "<string -- the complete email ready to send>"
}
"""

EMAIL_USER_PROMPT_TEMPLATE: str = """\
Generate a personalized outreach email for the following volunteer-event match.

SPEAKER PROFILE:
- Name: {speaker_name}
- Title: {speaker_title}
- Company: {speaker_company}
- Board Role: {speaker_board_role}
- Metro Region: {speaker_metro}
- Expertise: {speaker_expertise}

EVENT DETAILS:
- Event: {event_name}
- Category: {event_category}
- University/Host: {event_host}
- Volunteer Role Needed: {volunteer_role}
- Primary Audience: {primary_audience}
- Date: {event_date}

MATCH QUALITY:
- Overall Match Score: {match_score:.0%}
- Topic Relevance: {topic_score:.0%}
- Role Fit: {role_score:.0%}
- Geographic Proximity: {geo_score:.0%}

Compose an email from IA West chapter leadership inviting {speaker_name} to \
volunteer as a {volunteer_role} at {event_name}.  Reference their specific \
expertise in {speaker_expertise} and explain why this is a great match.

The value proposition should emphasize:
- Impact on students (next generation of market researchers)
- Visibility for the speaker and their company
- IA West community building
- Low time commitment (typically 2-4 hours)\
"""


# ---------------------------------------------------------------------------
# Email generation
# ---------------------------------------------------------------------------

def generate_outreach_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, float],
    model: str = "gemini-2.5-flash-lite",
    temperature: float = 0.7,
) -> dict[str, str]:
    """
    Generate a personalized outreach email for a speaker-event match.

    Parameters
    ----------
    speaker : dict
        Speaker profile with keys: Name, Title, Company, Board Role,
        Metro Region, Expertise Tags.
    event : dict
        Event details may come from:
        - Sprint 0/Sprint 1 CSV-backed rows with literal keys such as
          "Event / Program", "Host / Unit", "Volunteer Roles (fit)",
          "Primary Audience", "Public URL"
        - Sprint 2 discovery output with keys such as event_name,
          category, university, volunteer_roles, primary_audience,
          date_or_recurrence, url
    match_scores : dict
        Canonical contract is Sprint 1's ranking schema:
        total_score plus factor_scores.{topic_relevance, role_fit,
        geographic_proximity, calendar_fit, historical_conversion,
        student_interest}. Legacy shorthand keys are tolerated only for
        backward-compatible demo fixtures.
    model : str
        Gemini model identifier.
    temperature : float
        Sampling temperature.  0.7 for creative but professional emails.

    Returns
    -------
    dict with keys:
        subject_line  : str
        greeting      : str
        body          : str
        closing       : str
        full_email    : str
    Returns a fallback template on any failure.
    """
    cached = load_cached_email(speaker, event, match_scores)
    if cached is not None:
        return cached

    # Graceful handling of missing fields
    speaker_name = speaker.get("Name", "Valued Board Member")
    speaker_title = speaker.get("Title", "your role")
    speaker_company = speaker.get("Company", "your organization")
    speaker_board_role = speaker.get("Board Role", "Board Member")
    speaker_metro = speaker.get("Metro Region", "your region")
    speaker_expertise = speaker.get("Expertise Tags", "your expertise")

    event_name = _event_value(event, "Event / Program", "event_name", default="the upcoming event")
    event_category = _event_value(event, "Category", "category", default="event")
    event_host = _event_value(event, "Host / Unit", "university", default="the university")
    volunteer_role = _event_value(event, "Volunteer Roles (fit)", "volunteer_roles", default="volunteer")
    primary_audience = _event_value(event, "Primary Audience", "primary_audience", default="students")
    event_date = _event_value(event, "Date", "IA Event Date", "date_or_recurrence", "Recurrence (typical)", default="TBD")

    # Handle list-type volunteer_roles
    if isinstance(volunteer_role, list):
        volunteer_role = ", ".join(volunteer_role) if volunteer_role else "volunteer"

    total_score = _match_score_value(match_scores, "total_score")
    topic_score = _match_score_value(match_scores, "topic_relevance")
    role_score = _match_score_value(match_scores, "role_fit")
    geo_score = _match_score_value(match_scores, "geographic_proximity")

    user_prompt = EMAIL_USER_PROMPT_TEMPLATE.format(
        speaker_name=speaker_name,
        speaker_title=speaker_title,
        speaker_company=speaker_company,
        speaker_board_role=speaker_board_role,
        speaker_metro=speaker_metro,
        speaker_expertise=speaker_expertise,
        event_name=event_name,
        event_category=event_category,
        event_host=event_host,
        volunteer_role=volunteer_role,
        primary_audience=primary_audience,
        event_date=event_date,
        match_score=total_score,
        topic_score=topic_score,
        role_score=role_score,
        geo_score=geo_score,
    )

    client = Gemini()

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or ""
        result = json.loads(raw)

        # Validate required keys
        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        if not required_keys.issubset(result.keys()):
            missing = required_keys - result.keys()
            logger.warning("Email response missing keys: %s", missing)
            # Fill missing keys
            for key in missing:
                result[key] = ""
            if not result.get("full_email"):
                result["full_email"] = (
                    f"{result.get('greeting', '')}\n\n"
                    f"{result.get('body', '')}\n\n"
                    f"{result.get('closing', '')}"
                )

        save_cached_email(speaker, event, match_scores, result)
        return result

    except Exception as exc:
        logger.error("Email generation failed: %s", exc)
        fallback = _fallback_email(speaker_name, speaker_expertise, event_name, volunteer_role)
        save_cached_email(speaker, event, match_scores, fallback)
        return fallback


def _fallback_email(
    speaker_name: str,
    speaker_expertise: str,
    event_name: str,
    volunteer_role: str,
) -> dict[str, str]:
    """
    Return a template email when LLM generation fails.

    Uses generic but professional language that works for any match.
    """
    subject = f"Volunteer Opportunity: {volunteer_role} at {event_name}"
    greeting = f"Dear {speaker_name},"
    body = (
        f"I hope this message finds you well. On behalf of IA West, "
        f"I am reaching out because your expertise in {speaker_expertise} "
        f"makes you an excellent match for an upcoming opportunity.\n\n"
        f"We are looking for a {volunteer_role} for {event_name}, and "
        f"your background would bring tremendous value to the students "
        f"and professionals attending.\n\n"
        f"This is a great opportunity to give back to the next generation "
        f"of market researchers while increasing your visibility in the "
        f"IA West community. The typical time commitment is just 2-4 hours."
    )
    closing = (
        "Would you be available to participate? I would be happy to share "
        "more details.\n\nBest regards,\nIA West Chapter Leadership"
    )
    full_email = f"Subject: {subject}\n\n{greeting}\n\n{body}\n\n{closing}"

    return {
        "subject_line": subject,
        "greeting": greeting,
        "body": body,
        "closing": closing,
        "full_email": full_email,
    }
```

#### Email Preview UI Component (in Matches tab)

```python
def render_email_preview(
    speaker: dict,
    event: dict,
    match_scores: dict,
) -> None:
    """
    Render the email preview panel within the Matches tab.

    Called when user clicks "Generate Email" on a match card.
    """
    with st.expander("Outreach Email Preview", expanded=True):
        email = generate_outreach_email(speaker, event, match_scores)

        st.markdown(f"**Subject:** {email['subject_line']}")
        st.divider()

        # Display formatted email
        st.markdown(email["full_email"])

        st.divider()

        # Copy to clipboard via st.code (allows easy select-all + copy)
        st.caption("Click inside the box below and use Ctrl+A, Ctrl+C to copy:")
        st.code(email["full_email"], language=None)

        # Alternative: download as .txt
        st.download_button(
            label="Download Email as .txt",
            data=email["full_email"],
            file_name=(
                f"outreach_{speaker.get('Name', 'speaker')}_"
                f"{_event_value(event, 'Event / Program', 'event_name', default='event')}.txt"
            ),
            mime="text/plain",
        )
```

#### Acceptance Criteria

- [ ] `generate_outreach_email()` produces a JSON dict with keys: subject_line, greeting, body, closing, full_email
- [ ] Email references the speaker's specific expertise (not generic "your skills")
- [ ] Email references the event name, category, and volunteer role
- [ ] Email includes match score percentage in the talking points
- [ ] Email mentions value proposition: student impact, visibility, community, low time commitment
- [ ] Missing speaker fields gracefully fall back to generic phrasing ("your expertise", "your organization")
- [ ] `_fallback_email()` returns a usable template email when LLM fails
- [ ] Email preview panel renders in the Matches tab with formatted display
- [ ] `st.code()` block allows easy copy-to-clipboard
- [ ] Download button generates a `.txt` file with the full email
- [ ] Generated emails are cached under `cache/emails/` using speaker/event/score-aware keys for demo-day reuse
- [ ] Real CSV-backed event rows and discovered-event dicts both render specific event details without falling back to generic placeholders
- [ ] Temperature set to 0.7 for professional but varied language

#### Harness Guidelines

- Place email generation in `src/outreach/email_gen.py`
- Email preview UI component can live in `src/ui/matches_tab.py` alongside match cards
- Create `src/outreach/__init__.py` with public export: `generate_outreach_email`
- Cache generated emails in `cache/emails/` so Sprint 4 demo pre-warm uses the same artifacts as runtime
- Unit tests in `tests/test_email_gen.py` -- mock Gemini responses
- Test `_fallback_email()` with various combinations of missing fields

#### Steer Guidelines

- Email generation should gracefully handle missing speaker fields -- use "your expertise" as fallback, not crash
- `response_format={"type": "json_object"}` ensures structured output
- Temperature 0.7 produces varied but professional emails; lower (0.3) for more consistent output during demos
- The "Copy to Clipboard" approach uses `st.code()` which lets users select and copy; native clipboard API requires JavaScript injection and is unreliable in Streamlit
- For the demo, pre-generate emails for the top 3 matches and cache them to avoid live API calls

---

### A2.5: Calendar Invite Preview (.ics) (1.5h)

**File:** `src/outreach/calendar_invite.py`

#### Specification

```python
"""
Calendar invite (.ics) generation for matched events.

Module: src/outreach/calendar_invite.py
Dependencies: icalendar
"""

from typing import Any, Optional
from datetime import datetime, timedelta
import logging

from icalendar import Calendar, Event, vText


logger = logging.getLogger(__name__)


def generate_ics(
    event_name: str,
    event_date: Optional[str] = None,
    event_time_start: Optional[str] = None,
    event_time_end: Optional[str] = None,
    location: Optional[str] = None,
    description: Optional[str] = None,
    speaker_name: Optional[str] = None,
    volunteer_role: Optional[str] = None,
    organizer_email: Optional[str] = None,
) -> bytes:
    """
    Generate a .ics calendar invite file.

    Parameters
    ----------
    event_name : str
        Name of the event (used as SUMMARY).
    event_date : str, optional
        Date string in YYYY-MM-DD format.  Defaults to 30 days from now.
    event_time_start : str, optional
        Start time in HH:MM format (24h).  Defaults to "09:00".
    event_time_end : str, optional
        End time in HH:MM format (24h).  Defaults to start + 2 hours.
    location : str, optional
        Event location / venue.
    description : str, optional
        Event description.  Auto-generated if not provided.
    speaker_name : str, optional
        Name of the matched speaker (included in description).
    volunteer_role : str, optional
        Role the speaker will fill (included in description).
    organizer_email : str, optional
        Email of the event organizer (ORGANIZER field).

    Returns
    -------
    bytes
        The .ics file content as bytes, ready for download.
    """
    cal = Calendar()
    cal.add("prodid", "-//IA SmartMatch//Event Invite//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")

    evt = Event()

    # SUMMARY
    if volunteer_role:
        evt.add("summary", f"{event_name} -- {volunteer_role}")
    else:
        evt.add("summary", event_name)

    # DATE/TIME
    if event_date:
        try:
            dt_date = datetime.strptime(event_date, "%Y-%m-%d")
        except ValueError:
            dt_date = datetime.utcnow() + timedelta(days=30)
    else:
        dt_date = datetime.utcnow() + timedelta(days=30)

    if event_time_start:
        try:
            t_start = datetime.strptime(event_time_start, "%H:%M")
            dt_start = dt_date.replace(hour=t_start.hour, minute=t_start.minute)
        except ValueError:
            dt_start = dt_date.replace(hour=9, minute=0)
    else:
        dt_start = dt_date.replace(hour=9, minute=0)

    if event_time_end:
        try:
            t_end = datetime.strptime(event_time_end, "%H:%M")
            dt_end = dt_date.replace(hour=t_end.hour, minute=t_end.minute)
        except ValueError:
            dt_end = dt_start + timedelta(hours=2)
    else:
        dt_end = dt_start + timedelta(hours=2)

    evt.add("dtstart", dt_start)
    evt.add("dtend", dt_end)
    evt.add("dtstamp", datetime.utcnow())

    # LOCATION
    if location:
        evt["location"] = vText(location)

    # DESCRIPTION
    if description:
        evt.add("description", description)
    else:
        desc_parts = [f"Event: {event_name}"]
        if speaker_name:
            desc_parts.append(f"Volunteer: {speaker_name}")
        if volunteer_role:
            desc_parts.append(f"Role: {volunteer_role}")
        desc_parts.append("")
        desc_parts.append("Matched and scheduled via IA SmartMatch CRM.")
        desc_parts.append("Contact IA West chapter leadership for questions.")
        evt.add("description", "\n".join(desc_parts))

    # ORGANIZER
    if organizer_email:
        evt.add("organizer", f"mailto:{organizer_email}")

    # UID (unique per event+speaker combo)
    uid_base = f"{event_name}-{speaker_name or 'unknown'}"
    import hashlib
    uid = hashlib.md5(uid_base.encode()).hexdigest()
    evt.add("uid", f"{uid}@ia-smartmatch")

    cal.add_component(evt)
    return cal.to_ical()


def render_ics_download_button(
    event: dict[str, Any],
    speaker: dict[str, Any],
    match_scores: dict[str, float],
) -> None:
    """
    Render a Streamlit download button for the .ics calendar invite.

    Called from the Matches tab alongside the email preview.
    """
    import streamlit as st

    speaker_name = speaker.get("Name", "Volunteer")
    event_name = event.get("Event / Program", event.get("event_name", "Event"))
    volunteer_role = event.get("Volunteer Roles (fit)", event.get("volunteer_roles", ""))

    if isinstance(volunteer_role, list):
        volunteer_role = ", ".join(volunteer_role) if volunteer_role else "volunteer"

    # Build description with match context
    score_pct = float(
        match_scores.get("total_score", match_scores.get("total", 0.0)) or 0.0
    )
    description = (
        f"IA SmartMatch Volunteer Assignment\n\n"
        f"Event: {event_name}\n"
        f"Volunteer: {speaker_name}\n"
        f"Role: {volunteer_role}\n"
        f"Match Score: {score_pct:.0%}\n\n"
        f"Auto-generated by IA SmartMatch CRM."
    )

    ics_bytes = generate_ics(
        event_name=event_name,
        event_date=event.get(
            "Date",
            event.get("IA Event Date", event.get("date_or_recurrence", event.get("Recurrence (typical)"))),
        ),
        location=event.get("Host / Unit", event.get("university", "")),
        description=description,
        speaker_name=speaker_name,
        volunteer_role=volunteer_role,
        organizer_email=event.get("Contact Email", event.get("contact_email")),
    )

    st.download_button(
        label="Download Calendar Invite (.ics)",
        data=ics_bytes,
        file_name=f"invite_{speaker_name}_{event_name}.ics".replace(" ", "_"),
        mime="text/calendar",
        key=f"ics_download_{speaker_name}_{event_name}",
    )
```

#### Field Mapping

```
Event Data Field            -> .ics Field
-----------------------------------------
Event / Program (or event_name) -> SUMMARY (+ volunteer_role suffix)
Date / IA Event Date / date_or_recurrence -> DTSTART (parsed as YYYY-MM-DD when possible)
(computed: start + 2h)        -> DTEND
Host / Unit (or university)   -> LOCATION
(auto-generated)              -> DESCRIPTION
Contact Email                 -> ORGANIZER
(hash of event+speaker)       -> UID
```

#### Acceptance Criteria

- [ ] `generate_ics()` returns valid `.ics` bytes that can be imported into Google Calendar, Outlook, and Apple Calendar
- [ ] SUMMARY includes event name and volunteer role
- [ ] DTSTART and DTEND parsed correctly from date strings
- [ ] Missing date defaults to 30 days from now at 09:00
- [ ] Missing end time defaults to start + 2 hours
- [ ] DESCRIPTION includes event name, speaker name, role, and match score
- [ ] UID is unique per event+speaker combination
- [ ] `render_ics_download_button()` integrates with Streamlit download mechanism
- [ ] Downloaded file has `.ics` extension and `text/calendar` MIME type
- [ ] `.ics` generation reads literal Sprint 0 CSV event keys before any simplified aliases

#### Harness Guidelines

- Place calendar invite code in `src/outreach/calendar_invite.py`
- Add `icalendar` to `requirements.txt`
- Unit tests in `tests/test_calendar_invite.py` -- validate .ics output parses correctly
- Test with `icalendar.Calendar.from_ical()` to verify roundtrip

#### Steer Guidelines

- The `icalendar` library is the standard Python library for .ics generation; install via `pip install icalendar`
- Date parsing from event data may fail because `date_or_recurrence` can be "Every Tuesday" instead of "2026-04-20" -- handle gracefully with the 30-day default
- For the demo, pre-generate one .ics file for the Travis Miller match to ensure it works smoothly

---

### A2.6: Pipeline Funnel -- Real Data Integration (2.0h)

**File:** `src/ui/pipeline_tab.py` (update existing from Sprint 1)

#### Specification

```python
"""
Pipeline funnel visualization with real match data.

Module: src/ui/pipeline_tab.py
Dependencies: plotly, pandas, streamlit
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Conversion rates (based on nonprofit engagement benchmarks)
# ---------------------------------------------------------------------------

CONVERSION_RATES: dict[str, float] = {
    "discovered_to_matched": 1.0,    # all discovered events get matched
    "matched_to_contacted": 0.80,    # 80% of top matches get outreach emails
    "contacted_to_confirmed": 0.45,  # 45% of contacted volunteers confirm
    "confirmed_to_attended": 0.75,   # 75% of confirmed actually attend
    "attended_to_member_inquiry": 0.15,  # 15% of attendees spark membership inquiry
}

FUNNEL_STAGES: list[str] = [
    "Discovered",
    "Matched",
    "Contacted",
    "Confirmed",
    "Attended",
    "Member Inquiry",
]


def compute_funnel_data(
    discovered_count: int,
    matched_count: int,
    pipeline_df: pd.DataFrame | None = None,
    match_details: list[dict] | None = None,
) -> dict[str, dict]:
    """
    Compute funnel stage counts and build hover text with real data.

    Parameters
    ----------
    discovered_count : int
        Total events discovered across all universities + CPP data.
    matched_count : int
        Total top-3 matches generated.
    pipeline_df : pd.DataFrame, optional
        Pipeline sample data from Sprint 1 (pipeline_sample_data.csv).
    match_details : list[dict], optional
        List of match results with speaker/event names for hover text.

    Returns
    -------
    dict keyed by stage name, each containing:
        count     : int
        hover     : str  -- hover text with real names
        examples  : list[str]  -- sample speaker-event pairings at this stage
    """
    contacted = int(matched_count * CONVERSION_RATES["matched_to_contacted"])
    confirmed = int(contacted * CONVERSION_RATES["contacted_to_confirmed"])
    attended = int(confirmed * CONVERSION_RATES["confirmed_to_attended"])
    member_inq = int(attended * CONVERSION_RATES["attended_to_member_inquiry"])

    # Build hover text with real data
    hover_discovered = f"{discovered_count} events across 5 universities + CPP data"
    hover_matched = f"{matched_count} top speaker-event matches generated"
    hover_contacted = f"{contacted} outreach emails sent (80% of matched)"
    hover_confirmed = f"{confirmed} volunteers confirmed (45% of contacted)"
    hover_attended = f"{attended} volunteers attended events (75% of confirmed)"
    hover_member = f"{member_inq} student membership inquiries (15% of attended)"

    # Add real speaker-event examples if available
    examples: dict[str, list[str]] = {stage: [] for stage in FUNNEL_STAGES}
    if match_details:
        for match in match_details[:5]:
            speaker = match.get("speaker_name", "Unknown Speaker")
            event = match.get("event_name", "Unknown Event")
            score = match.get("total_score", 0.0)
            examples["Matched"].append(f"{speaker} -> {event} ({score:.0%})")

        for match in match_details[:int(len(match_details) * 0.8)]:
            speaker = match.get("speaker_name", "Unknown Speaker")
            event = match.get("event_name", "Unknown Event")
            examples["Contacted"].append(f"{speaker} contacted for {event}")

    return {
        "Discovered": {"count": discovered_count, "hover": hover_discovered, "examples": examples["Discovered"]},
        "Matched": {"count": matched_count, "hover": hover_matched, "examples": examples["Matched"]},
        "Contacted": {"count": contacted, "hover": hover_contacted, "examples": examples["Contacted"]},
        "Confirmed": {"count": confirmed, "hover": hover_confirmed, "examples": examples["Confirmed"]},
        "Attended": {"count": attended, "hover": hover_attended, "examples": examples["Attended"]},
        "Member Inquiry": {"count": member_inq, "hover": hover_member, "examples": examples["Member Inquiry"]},
    }


def render_pipeline_funnel(
    discovered_count: int,
    matched_count: int,
    match_details: list[dict] | None = None,
) -> None:
    """
    Render the Plotly funnel chart in the Pipeline tab.
    """
    st.header("Engagement Pipeline Funnel")
    st.caption(
        "Track the full lifecycle from event discovery to IA membership inquiry."
    )

    funnel_data = compute_funnel_data(
        discovered_count=discovered_count,
        matched_count=matched_count,
        match_details=match_details,
    )

    stage_names = FUNNEL_STAGES
    stage_counts = [funnel_data[s]["count"] for s in stage_names]
    hover_texts = [funnel_data[s]["hover"] for s in stage_names]

    # Color gradient: dark blue (top) -> light blue (bottom)
    colors = [
        "#003f5c",  # Discovered
        "#2f4b7c",  # Matched
        "#665191",  # Contacted
        "#a05195",  # Confirmed
        "#d45087",  # Attended
        "#f95d6a",  # Member Inquiry
    ]

    fig = go.Figure(
        go.Funnel(
            y=stage_names,
            x=stage_counts,
            textinfo="value+percent initial",
            textposition="inside",
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(color=colors),
            connector=dict(line=dict(color="gray", width=1)),
        )
    )

    fig.update_layout(
        title="IA SmartMatch Engagement Pipeline",
        font=dict(size=14),
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    # Summary metrics below the funnel
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Conversion: Discovered to Matched",
            f"{matched_count / max(discovered_count, 1):.0%}",
        )
    with col2:
        st.metric(
            "Projected Quarterly Matches",
            f"{matched_count * 4}",
            help="Assuming quarterly refresh of discovery + matching",
        )
    with col3:
        hours_saved = matched_count * 4.42
        st.metric(
            "Volunteer Hours Saved/Quarter",
            f"{hours_saved:.0f}h",
            help="4.42 hours saved per match cycle vs. manual process",
        )

    # Real data examples
    if match_details:
        with st.expander("Sample Match Details (Real Data)"):
            for match in match_details[:5]:
                speaker = match.get("speaker_name", "Unknown")
                event = match.get("event_name", "Unknown")
                score = match.get("total_score", 0.0)
                st.write(f"- **{speaker}** matched to **{event}** ({score:.0%})")
```

#### Acceptance Criteria

- [ ] Funnel chart renders with 6 stages using `go.Funnel()`
- [ ] Stage counts computed from real discovered/matched counts and conversion rates
- [ ] Hover tooltips show descriptive text with real numbers
- [ ] `textinfo="value+percent initial"` shows both count and percentage
- [ ] Colors form a coherent gradient across stages
- [ ] Summary metrics display below the funnel: conversion rate, projected quarterly matches, hours saved
- [ ] Real speaker-event names appear in hover tooltips when match_details is provided
- [ ] "Sample Match Details" expander shows top-5 real matches
- [ ] Funnel connects to `pipeline_sample_data.csv` from Sprint 1 A1.6

#### Harness Guidelines

- Update existing `src/ui/pipeline_tab.py` from Sprint 1
- Import `pipeline_sample_data.csv` via `pd.read_csv("data/pipeline_sample_data.csv")`
- `render_pipeline_funnel()` is called from the main app within the Pipeline tab context
- Unit tests in `tests/test_pipeline.py` -- test `compute_funnel_data()` with known inputs

#### Steer Guidelines

- Use `go.Funnel()` (not `go.Figure(go.Funnelarea())`) -- the former produces a traditional horizontal funnel
- `textinfo="value+percent initial"` shows both the count and the percentage relative to the first stage
- Connect real data: after Sprint 1, `pipeline_sample_data.csv` should have columns for speaker names, event names, match scores -- use these for hover text
- The funnel should update when discovered events are added via the Discovery tab (check `st.session_state["discovered_events"]`)

---

### A2.7: Handoff Data Package for Track B (1.0h)

**File:** `docs/deliverables/track_b_data_package.md`

#### Specification

Generate a data package document with the following template structure:

```markdown
# Track B Data Package -- Sprint 2 Handoff

**Generated:** YYYY-MM-DD
**Generated By:** Track A (Person B)
**For:** Track B (Person C)

---

## 1. Match Results Summary

### Top Matches by Event (Real Data)

| Event | #1 Speaker | Score | #2 Speaker | Score | #3 Speaker | Score |
|-------|-----------|-------|-----------|-------|-----------|-------|
| [from pipeline_sample_data.csv -- fill with actual results] | | | | | | |

### Match Score Distribution
- Mean match score: X.XX
- Median match score: X.XX
- Score range: X.XX - X.XX
- Matches above 70%: N of M total

---

## 2. Pipeline Funnel Numbers

| Stage | Count | Conversion Rate |
|-------|-------|-----------------|
| Discovered | XX | -- |
| Matched | XX | XX% of discovered |
| Contacted | XX | 80% of matched |
| Confirmed | XX | 45% of contacted |
| Attended | XX | 75% of confirmed |
| Member Inquiry | XX | 15% of attended |

### Quarterly Projections
- Matches per quarter: XX
- Hours saved per quarter: XX (at 4.42h per match cycle)
- Dollar value per quarter: $XX (at $50/h opportunity cost)

---

## 3. University Coverage Map Data

| University | Metro Region | Nearby Speakers | Events Found | Scrape Status |
|-----------|-------------|----------------|--------------|---------------|
| CPP (Cal Poly Pomona) | LA East | [names] | 15 (events) + 35 (courses) | Pre-loaded |
| UCLA | LA West | [names] | [count] | [live/cached/failed] |
| USC | LA Central | [names] | [count] | [live/cached/failed] |
| SDSU | San Diego | [names] | [count] | [live/cached/failed] |
| UC Davis | Sacramento | [names] | [count] | [live/cached/failed] |
| Portland State | Portland | [names] | [count] | [live/cached/failed] |

### Geographic Coverage
- Metro regions with board members: [list from speaker_profiles.csv]
- Metro regions without board members: [identify gaps]
- Board member utilization potential: [avg matches per speaker]

---

## 4. ROI Calculation Inputs

### Time Savings per Match Cycle
| Step | Manual Process | SmartMatch | Savings |
|------|---------------|-----------|---------|
| Research events | 3.0h | 0.02h (auto-scrape) | 2.98h |
| Draft outreach email | 1.0h | 0.03h (AI-generated) | 0.97h |
| Coordination | 0.5h | 0.03h (calendar invite) | 0.47h |
| **Total** | **4.5h** | **0.08h** | **4.42h** |

### Quarterly Volume
- Active board members: 18
- Average matches per member per quarter: [from data]
- Total matches per quarter: [compute]
- Total hours saved per quarter: [compute]
- Dollar value (at $50/h): $[compute]

### Membership LTV Framework
- Annual dues: $[research needed -- check IA website]
- Average retention: [years -- estimate or research]
- Membership conversion rate from engagement: 10-15% (industry benchmark)
- LTV per converted member: $[compute]

---

## 5. Data Quality Notes

- Speaker profiles: [any missing fields, encoding issues]
- Event data: [any missing contacts, URL issues]
- Course data: [guest_lecture_fit distribution: X High, Y Medium, Z Low]
- Calendar data: [coverage gaps, date format issues]

---

## 6. Screenshots Available

After Sprint 2, the following screenshots will be generated (Sprint 3 A3.7):
- [ ] Match card with radar chart (Travis Miller example)
- [ ] Pipeline funnel with real data
- [ ] Discovery tab with UCLA results
- [ ] Email preview panel
- [ ] Weight slider demonstration
```

#### Acceptance Criteria

- [ ] Template saved to `docs/deliverables/track_b_data_package.md`
- [ ] All sections filled with real data from Sprint 1 and Sprint 2 outputs
- [ ] Match results table uses actual speaker names and event names from the data
- [ ] Pipeline funnel numbers are computed from actual match counts
- [ ] University coverage map reflects actual scraping results from A2.1
- [ ] ROI calculations use correct formulas (4.42h savings per match)
- [ ] Data quality notes reflect actual issues found during Sprint 0 A0.2

#### Harness Guidelines

- Place in `docs/deliverables/track_b_data_package.md`
- This is a generated document -- code should produce it from real data, not be hand-written
- Consider adding a script `src/utils/generate_data_package.py` that reads CSVs and match results to auto-populate the template

#### Steer Guidelines

- This document is the primary input for Track B's Growth Strategy writing
- Fill as many fields as possible with real data; mark remaining fields with `[PENDING -- will update from Sprint 3]`
- The ROI calculation inputs are critical for Section 5 of the Growth Strategy
- University coverage map data feeds the rollout plan (Section 3 of Growth Strategy)

---

## Track B Tasks

---

### B2.1: Growth Strategy -- Research Phase (4.0h)

**Output:** `docs/deliverables/research_notes.md`

#### Specification

**Documents to Read:**
1. `archived/Categories list/Category 3 IA West Smart Watch/IA_West_Smart_Match_Challenge.docx` -- full challenge specification
2. `archived/Categories list/Category 3 IA West Smart Watch/IA_West_Smart_Match_Challenge_Intro.pptx` -- sponsor intro deck
3. `data/data_speaker_profiles.csv` -- 18 board member profiles
4. `data/data_cpp_events_contacts.csv` -- 15 CPP events
5. `data/data_cpp_course_schedule.csv` -- 35 course sections
6. `data/data_event_calendar.csv` -- 9 IA events
7. `docs/deliverables/track_b_data_package.md` -- Track A data handoff

**Research Queries:**
- IA West membership structure and value proposition: search IA West chapter website, Insights Association national site
- University engagement benchmarks: Stanford Social Innovation Review (SSIR) -- "volunteer coordination in nonprofit chapters", "university-industry engagement models"
- Professional association membership funnels: ASAE (American Society of Association Executives) -- email response rates for professional associations (benchmark: 20-30%), membership conversion rates
- CASE (Council for Advancement and Support of Education) -- university-industry partnership models, career center engagement benchmarks

**Note-Taking Template:**

```markdown
# Growth Strategy Research Notes

## Source: Challenge Brief
- Key requirements: ...
- Judging emphasis: ...
- Specific asks: ...

## Source: Sponsor Deck
- IA West mission: ...
- Current pain points: ...
- Desired outcomes: ...

## Source: Data Analysis
- Speaker geographic distribution: ...
- Event category breakdown: ...
- Course guest-lecture-fit distribution: High=X, Medium=Y, Low=Z
- Calendar coverage: ...

## Source: Track B Data Package
- Top match examples: ...
- Pipeline funnel projections: ...
- ROI inputs: ...

## External Research
- SSIR volunteer coordination: [citation + key stat]
- ASAE email response benchmarks: [citation + key stat]
- CASE university-industry engagement: [citation + key stat]
- IA membership dues/structure: [findings]

## Key Data Points for Growth Strategy
1. ...
2. ...
3. ...
```

#### Acceptance Criteria

- [ ] All 7 documents read and key points captured
- [ ] Research notes organized by source
- [ ] At least 3 external research citations identified (SSIR, ASAE, CASE or equivalent)
- [ ] Key data points listed for direct inclusion in Growth Strategy
- [ ] Speaker geographic distribution documented
- [ ] Event category breakdown documented
- [ ] ROI calculation inputs validated against Track A data package

#### Harness Guidelines

- Save research notes to `docs/deliverables/research_notes.md`
- This is a working document, not a polished deliverable
- Person C should spend 2h reading/analyzing and 2h on external research

#### Steer Guidelines

- The Growth Strategy is worth 20% of judging (10 points of 50) -- research quality directly impacts final score
- Focus external research on finding 2-3 credible statistics that support the ROI narrative
- If IA West membership dues cannot be found online, use industry benchmarks for professional association dues ($150-$500/year range)
- SSIR citation about volunteer coordination overhead (30-40% engagement loss) is a powerful data point for the problem statement

---

### B2.2: Growth Strategy -- Outline + Section 1-2 Draft (4.0h)

**Output:** `docs/deliverables/growth_strategy_draft.md`

#### Specification

**Detailed Outline:**

```markdown
# Growth Strategy: IA SmartMatch -- Campus Engagement to Membership Pipeline

## Section 1: Executive Summary + Problem Statement (0.5 page)
### 1.1 The Challenge
### 1.2 The Gap (quantified)
### 1.3 The Solution

## Section 2: Target Audience Segments (0.5 page)
### 2.1 Segment A: Board Members / Volunteers
### 2.2 Segment B: University Program Coordinators
### 2.3 Segment C: Students / Young Professionals
### 2.4 Segment D: IA West Chapter Leadership

## Section 3: Rollout Plan -- CPP to West Coast Corridor (0.5 page)
### 3.1 Phase 1: CPP Pilot (Q2-Q3 2026)
### 3.2 Phase 2: LA Metro Expansion (Q4 2026)
### 3.3 Phase 3: West Coast Corridor (Q1-Q2 2027)
### 3.4 Board-to-Campus Expansion Map

## Section 4: Channel Strategy (0.5 page)
### 4.1 SmartMatch Outreach Emails
### 4.2 IA West Event Cross-Promotion
### 4.3 University Career Center Partnerships
### 4.4 LinkedIn Targeting

## Section 5: Value Proposition + ROI (0.5 page)
### 5.1 Value for Volunteers
### 5.2 Value for Universities
### 5.3 Value for IA West
### 5.4 ROI Quantification
```

**Section 1 Template:**

```markdown
## Executive Summary

IA West coordinates [18] board member volunteers across [6] metro regions
for [8+] university and industry events per year -- entirely through ad-hoc
email chains and personal networks.  This manual process results in
[mismatched volunteer assignments / missed engagement opportunities /
zero pipeline tracking from campus engagement to IA membership].

[SSIR citation]: Volunteer-run professional chapters lose 30-40% of
engagement opportunities due to coordination overhead.

SmartMatch addresses this gap with an AI-orchestrated CRM that automates
the full engagement lifecycle:
- **Discovery:** Automated web scraping identifies volunteer opportunities
  at [5] universities spanning Portland to San Diego
- **Matching:** A 6-factor weighted scoring algorithm recommends the
  optimal board member for each opportunity
- **Outreach:** AI-generated personalized emails and calendar invites
  reduce coordination time from [4.5 hours to under 5 minutes]
- **Pipeline:** A conversion funnel tracks engagement from discovery
  through IA membership inquiry

## Problem Statement

Today, IA West has:
- [18] board members with diverse expertise in [expertise clusters from data]
- [15] CPP events and [35] course sections as known engagement opportunities
- [9] IA events across the West Coast corridor
- **Zero** centralized system for matching, tracking, or measuring engagement

The result: [X]% of board members are underutilized, [Y] events go
unfilled, and the chapter cannot quantify the ROI of its university
engagement program.
```

**Section 2 Template -- with real data integration points:**

```markdown
## Target Audience Segments

### Segment A: Board Members / Volunteers
**Pain:** Ad-hoc coordination, unclear where to invest limited volunteer hours
**Profile:** [18] professionals across [list metro regions from data].
Key expertise clusters: [list from Expertise Tags column].
**SmartMatch Value:** Automated matching surfaces the highest-impact
opportunities aligned with each member's expertise and location.

*Example (from prototype data):* [Speaker Name], [Title] at [Company],
is based in [Metro Region] with expertise in [Tags].  SmartMatch matched
them to [Event Name] with a [X%] match score, citing [top factor].

### Segment B: University Program Coordinators
**Pain:** Finding qualified industry professionals for events is
time-consuming and relies on personal networks.
**Profile:** Event organizers at university career centers, department
offices, and student organizations.
**SmartMatch Value:** A curated roster of pre-qualified, expertise-matched
volunteers delivered proactively.

### Segment C: Students / Young Professionals
**Pain:** No clear pathway from campus event attendance to IA membership.
**Profile:** Undergraduate and graduate students in market research,
data analytics, business, and related fields.
**SmartMatch Value:** The pipeline funnel creates a visible, measurable
pathway from "attended an event with an IA volunteer" to "inquired about
IA membership."

### Segment D: IA West Chapter Leadership
**Pain:** No data to measure engagement ROI or justify volunteer time
investment.
**Profile:** Chapter officers responsible for strategic decisions about
resource allocation.
**SmartMatch Value:** Dashboard with pipeline metrics, volunteer
utilization rates, and projected membership impact.
```

#### Acceptance Criteria

- [ ] Detailed outline with all 5 sections and subsections
- [ ] Section 1 drafted with specific numbers from real data (18 speakers, 15 events, etc.)
- [ ] Problem statement includes at least one external citation (SSIR or equivalent)
- [ ] Section 2 drafted with all 4 segments defined
- [ ] At least one real speaker example integrated into Section 2 (from prototype match results)
- [ ] Sections 1-2 total approximately 1 page (500-600 words)
- [ ] Market research language used throughout (conversion funnel, engagement pipeline, panel recruitment)

#### Harness Guidelines

- Save draft to `docs/deliverables/growth_strategy_draft.md`
- Use real data from CSVs and Track B data package; mark any missing data with `[PENDING]`
- Sections 3-5 can be outlined but not yet drafted (those are B2.3 and Sprint 3 tasks)

#### Steer Guidelines

- The Growth Strategy is a judging document, not a technical spec -- write in polished business prose, not bullet points
- Use market research terminology: "conversion funnel" not "pipeline", "engagement pipeline" not "workflow"
- Each claim should have a data point (real from prototype or cited from research)
- Total target: 2.5-3 pages across all 5 sections -- Sections 1-2 should be ~1 page

---

### B2.3: Growth Strategy -- Section 3 Draft (3.0h)

**Output:** Update `docs/deliverables/growth_strategy_draft.md`

#### Specification

**Section 3 Template:**

```markdown
## Rollout Plan: CPP to West Coast Corridor

### Phase 1: CPP Pilot (Q2-Q3 2026)
**Scope:** [15] CPP events + [35] course sections, [18] board members
**Goal:** Validate matching engine accuracy and measure baseline KPIs
**Key Metrics:**
- Match acceptance rate target: 60%+
- Email response rate target: 25%+
- Volunteer utilization: each board member matched 2+ times
**Data Points:**
- [X] high-fit course sections identified (Guest Lecture Fit = "High")
- [Y] unique event categories across CPP data
- [Z] board members within commuting distance of Pomona

### Phase 2: LA Metro Expansion (Q4 2026)
**Scope:** Add UCLA and USC to the discovery pipeline
**Rationale:** [N] board members are based in LA West and Ventura --
the closest metro regions to UCLA and USC campuses.
**Projected Volume:**
- Estimated [X] additional events discovered via web scraping
- [Y] new speaker-event matches generated
- [Z] outreach emails sent automatically
**Key Actions:**
- Activate automated discovery for UCLA and USC career center pages
- Onboard university career center contacts
- Begin tracking cross-campus volunteer utilization

### Phase 3: West Coast Corridor (Q1-Q2 2027)
**Scope:** Add SDSU, UC Davis, and Portland State
**Rationale:** Extends coverage to the full West Coast corridor
(Portland to San Diego), reaching [X] additional metro regions
where IA West board members are based.
**Projected Volume:**
- Total university coverage: [8+] campuses
- Estimated [X] events per quarter across all campuses
- [Y] unique board member-event matches per quarter
**Key Actions:**
- Deploy automated discovery for 3 additional universities
- Establish formal MOU with career centers
- Launch quarterly engagement reports for chapter leadership

### Board-to-Campus Expansion Map
[Describe which board members are geographically positioned to serve
which universities.  Use the geographic_proximity scores from the
matching engine.]

| Board Member | Metro Region | Nearest Universities | Proximity Score |
|-------------|-------------|---------------------|-----------------|
| [from data] | [from data] | [computed]          | [from engine]   |
```

#### Acceptance Criteria

- [ ] Section 3 drafted with all 3 phases defined and specific numbers
- [ ] Phase 1 uses actual CPP data counts (15 events, 35 courses, 10 high-fit)
- [ ] Phase 2 references real board member geographic data for UCLA/USC rationale
- [ ] Phase 3 covers SDSU, UC Davis, Portland State
- [ ] Board-to-campus expansion map includes at least 5 board member rows with real data
- [ ] Section 3 approximately 0.5 page (250-350 words)
- [ ] Projected volumes are realistic (based on actual scraping results from Track A)

#### Harness Guidelines

- Update `docs/deliverables/growth_strategy_draft.md` by appending Section 3
- Integrate data from `data_speaker_profiles.csv` for geographic distribution
- Use scraping results from A2.1 for projected event discovery counts

#### Steer Guidelines

- Phase 1 is the most detail-rich because we have real CPP data -- leverage this
- Phase 2 and 3 projections should be conservative; judges will appreciate realism over hype
- The board-to-campus expansion map is a high-impact visual for judges -- if Track A produces the Plotly map (Sprint 3 A3.1), reference it here

---

### B2.4: Measurement Plan -- Draft (3.0h)

**Output:** `docs/deliverables/measurement_plan_draft.md`

#### Specification

**KPI Table (complete):**

```markdown
# Measurement Plan: IA SmartMatch

## KPI Framework

| # | KPI | Definition | Target | Data Source | Measurement Frequency |
|---|-----|-----------|--------|-------------|----------------------|
| 1 | Match Acceptance Rate | % of top-3 recommendations accepted by chapter leadership | 60%+ | SmartMatch feedback loop (Accept/Decline buttons) | Per match cycle |
| 2 | Email Response Rate | % of outreach emails that receive a reply from the volunteer | 25%+ | Email tracking integration (future) | Monthly |
| 3 | Event Attendance Rate | % of confirmed volunteers who actually attend the event | 70%+ | Post-event check-in form | Per event |
| 4 | Membership Conversion Rate | % of students engaged through IA volunteer events who join IA within 12 months | 10-15% | IA membership database cross-referenced with event attendance | Annually |
| 5 | Volunteer Utilization Rate | Average number of matches per board member per quarter | 2+ events/quarter | SmartMatch pipeline tracker | Quarterly |
| 6 | Discovery Efficiency | Number of new events discovered per university per scrape cycle | 5+ events/university | Discovery tab logs | Per scrape cycle |
| 7 | Time Savings | Hours saved per match cycle compared to manual process | 4+ hours/cycle | Process comparison audit (manual vs. SmartMatch) | Quarterly audit |
```

**A/B Test Specification:**

```markdown
## Proposed Validation Experiment

### Design
- **Type:** Randomized controlled experiment
- **Population:** 6 IA West events in Q3-Q4 2026
- **Treatment Group (n=3 events):** SmartMatch-recommended volunteer matching
  - Top-3 speakers selected by the matching engine
  - Outreach via AI-generated personalized emails
  - Calendar invites auto-generated
- **Control Group (n=3 events):** Manual chapter leadership matching
  - Volunteers selected by chapter president's judgment
  - Outreach via standard email template
  - Manual calendar coordination

### Success Metrics
| Metric | Treatment Hypothesis | Control Baseline |
|--------|---------------------|-----------------|
| Match acceptance rate | 60%+ | ~40% (estimated manual) |
| Email response rate | 25%+ | ~15% (estimated manual) |
| Event attendance rate | 75%+ | ~55% (estimated manual) |
| Time per match cycle | <5 minutes | ~4.5 hours |

### Sample Size
- 3 events per condition x 5 matches per event = 15 matches per condition
- Total: 30 matches (sufficient for directional signal, not statistical significance)
- Power analysis note: for detecting a 20 percentage point difference in acceptance rate
  (40% -> 60%) at alpha=0.05, power=0.80, we would need ~50 per group.
  This pilot provides directional evidence for a larger rollout.

### Duration
- Q3-Q4 2026 (6 months)
- Interim check at 3 months (after first 3 events)

### Secondary Experiment
Within the treatment group, randomize weight configurations:
- Config A: High topic relevance (w1=0.40, w3=0.15)
- Config B: High geographic proximity (w1=0.25, w3=0.30)
- Measure: which configuration produces higher acceptance rates
```

**Feedback Loop Diagram Description:**

```markdown
## Feedback Loop

### Flow Diagram

Match Generated
    |
    v
Chapter Leadership Reviews Match Card
(sees: speaker profile, match score, radar chart, explanation)
    |
    +---> ACCEPT --> Outreach email sent --> Confirmation tracking
    |                                            |
    |                                            v
    |                                    Event attendance logged
    |                                            |
    |                                            v
    |                                    Student engagement tracked
    |                                            |
    |                                            v
    |                                    Membership inquiry flagged
    |
    +---> DECLINE --> Reason captured:
                      - "Too far" --> increase geographic_proximity weight
                      - "Schedule conflict" --> improve calendar_fit scoring
                      - "Topic mismatch" --> refine embedding model
                      - "Speaker fatigue" --> add utilization cap
                      - "Other" (free text) --> manual review
                          |
                          v
                  Feedback aggregated quarterly
                          |
                          v
                  Weight adjustment recommendation generated
                  (e.g., "5 of 8 declines cited distance --
                   consider increasing w3 from 0.20 to 0.30")
                          |
                          v
                  Next-cycle matches improved

### Cadence
- **Per-match:** Accept/decline + reason captured
- **Monthly:** Feedback summary report generated
- **Quarterly:** Weight adjustment recommendations reviewed by chapter leadership
- **Annually:** Full model refresh -- re-embed all speaker profiles with updated
  expertise tags, re-score all events, recalibrate conversion rates
```

#### Acceptance Criteria

- [ ] KPI table includes all 7 KPIs with definitions, targets, data sources, and frequency
- [ ] A/B test specification includes design, success metrics, sample size, and duration
- [ ] Power analysis note acknowledges sample size limitations honestly
- [ ] Secondary experiment (weight configuration randomization) is specified
- [ ] Feedback loop describes the full cycle: match -> review -> accept/decline -> reason -> weight adjustment
- [ ] Quarterly and annual review cadences defined
- [ ] Total document approximately 1 page
- [ ] Language uses market research terminology (A/B test, treatment/control, conversion rate)

#### Harness Guidelines

- Save draft to `docs/deliverables/measurement_plan_draft.md`
- This document will be revised in Sprint 3 B3.4 with real prototype performance data

#### Steer Guidelines

- Judges are market research professionals -- they understand experimental design, so the A/B test should be methodologically sound
- Be honest about sample size limitations; "directional signal" is acceptable for a pilot
- The feedback loop is a key differentiator -- it shows the system improves over time, not just a static recommendation engine

---

### B2.5: ROI Quantification -- Initial (2.0h)

**Output:** Section within `docs/deliverables/growth_strategy_draft.md` (Section 5) or standalone `docs/deliverables/roi_analysis.md`

#### Specification

**Calculation Formulas:**

```markdown
## ROI Quantification

### Variable Definitions
- T_manual = time for manual match process = 4.5 hours
  - Research events: 3.0h (searching university websites, reading event pages)
  - Draft outreach email: 1.0h (writing personalized email from scratch)
  - Coordination: 0.5h (back-and-forth scheduling, calendar management)
- T_smart = time for SmartMatch-assisted match = 0.08 hours (< 5 minutes)
  - Review match card: 0.03h
  - Approve and send AI-generated email: 0.03h
  - Download calendar invite: 0.02h
- T_savings = T_manual - T_smart = 4.42 hours per match cycle

### Quarterly Volume Calculation
- M = matches per quarter = top-3 per event x events/quarter
- For CPP alone: 15 events x 3 matches = 45 matches/quarter
  (not all matches result in outreach -- 80% conversion = 36 outreach actions)
- H_saved = M x T_savings = 45 x 4.42 = 198.9 hours/quarter ~ 199 hours/quarter

### Dollar Value
- V_opportunity = volunteer opportunity cost rate = $50/hour
  (based on average salary of market research professionals / 2,080 annual hours)
- Dollar_savings = H_saved x V_opportunity = 199 x $50 = $9,950/quarter
- Annual_savings = $9,950 x 4 = $39,800/year

### Membership LTV Framework
- D = annual membership dues (estimate: $200-$400 for individual members)
- R = average retention period (estimate: 3-5 years)
- C = conversion rate from engaged student to member (target: 10-15%)
- LTV = D x R = $200 x 3 = $600 (conservative) to $400 x 5 = $2,000 (optimistic)
- Students_engaged_per_quarter = attended_events x avg_students_per_event
  = [from funnel] x [estimate 25-50 students per event]
- Projected_new_members_per_year = students_engaged x C
  = [compute] x 0.10 = [result]
- Membership_revenue_per_year = projected_new_members x LTV
  = [compute]

### Total Value Proposition
- Direct savings: $39,800/year in volunteer coordination time
- Indirect value: [X] new members/year x $[LTV] = $[revenue]/year
- Total projected annual value: $[sum]
```

#### Acceptance Criteria

- [ ] Time savings calculation: 4.42h per match cycle documented with breakdown
- [ ] Quarterly volume: 45 matches from CPP data, 199 hours saved
- [ ] Dollar value: $9,950/quarter, $39,800/year at $50/h
- [ ] Membership LTV framework with variable definitions and range estimates
- [ ] All formulas shown with variable definitions (reproducible by reader)
- [ ] Conservative and optimistic scenarios provided

#### Harness Guidelines

- Can be a standalone file (`docs/deliverables/roi_analysis.md`) or integrated directly into Section 5 of the Growth Strategy draft
- Keep calculations simple and transparent -- judges should be able to verify the math

#### Steer Guidelines

- Use conservative estimates; judges will be skeptical of inflated numbers
- The $50/h opportunity cost is based on average market research professional salary (~$104k/year / 2,080 hours)
- Membership LTV is the weakest part of the calculation because we don't know actual IA dues -- bracket with conservative/optimistic ranges
- The 4.42h savings per match cycle is the strongest, most defensible number -- lead with it

---

### B2.6: Responsible AI Note -- Draft (2.0h)

**Output:** `docs/deliverables/responsible_ai_draft.md`

#### Specification

```markdown
# Responsible AI Note: IA SmartMatch

## Privacy

SmartMatch processes two categories of data:

**Board member profiles** (18 records): Names, titles, companies, metro
regions, and expertise tags.  All data is provided directly by IA West
chapter leadership with volunteer consent.  No data is collected from
social media, scraped from personal websites, or inferred from
third-party sources.  Profiles are stored locally in CSV files and
are not transmitted to third parties beyond the Gemini API for
embedding generation (subject to Gemini's data usage policy -- API
inputs are not used for model training).

**University event data** (publicly available): Event names, dates,
categories, and contact information scraped from public university
career center and events pages.  No student personally identifiable
information (PII) is collected.  Pipeline metrics (Discovered ->
Matched -> Contacted -> Confirmed -> Attended -> Member Inquiry)
track aggregate counts only -- no individual student tracking.

## Bias

SmartMatch's 6-factor matching algorithm introduces potential bias
vectors that we actively monitor:

**Geographic over-matching:** Board members in densely covered metro
regions (e.g., LA West with [X] members) may receive disproportionately
more match recommendations than members in under-represented regions
(e.g., Portland with [Y] members).

*Mitigation:* [Describe the diversity-of-speaker rotation flag from
prototype.  Reference bias audit results showing match distribution
across all 18 speakers.  Example: "Our bias audit found Speaker A
was matched [X] times while Speaker B was matched [Y] times.
Investigation revealed this reflects topic coverage gaps in
[specific area], not algorithmic bias.  We implemented a utilization
cap (max [N] matches per speaker per quarter) to ensure equitable
distribution."]

**Expertise tag bias:** Speakers with more detailed or more numerous
expertise tags receive higher topic_relevance scores due to richer
embedding vectors.

*Mitigation:* Minimum tag count requirement during profile creation.
Score normalization across speakers to prevent tag-count inflation.

## Transparency

Every match recommendation includes:
- **Composite score** (0-100%) with 6-factor breakdown
- **Radar chart** showing per-factor scores visually
- **Natural language explanation** generated by Gemini
  (e.g., "Travis Miller is recommended for the UCLA Hackathon
  because his MR technology expertise closely aligns with the
  event's data science focus")
- **Weight sliders** that allow chapter leadership to adjust
  scoring priorities in real time

No match is a black box.  Chapter leadership can inspect why any
speaker was recommended and can override the algorithm's ranking.

## Data Handling

- **Consent:** Board member profiles are provided by IA West chapter
  leadership.  Members consent to profile use during onboarding.
- **Public data only:** University event scraping targets only publicly
  accessible event pages.  robots.txt compliance is enforced.
- **Cache-and-delete:** Scraped HTML is cached for 24 hours and
  automatically purged.  No long-term storage of raw HTML.
- **API data:** Text sent to Gemini API for embeddings and generation
  is subject to Gemini's API data usage policy (not used for training).
- **No student PII:** The system never collects, stores, or processes
  individual student information.
```

#### Acceptance Criteria

- [ ] Four sections: Privacy, Bias, Transparency, Data Handling
- [ ] Privacy section distinguishes between board member data and public university data
- [ ] Bias section identifies at least 2 specific bias vectors with concrete mitigations
- [ ] Transparency section describes score breakdown, radar chart, explanation cards, and weight sliders
- [ ] Data handling covers consent, public-data-only scraping, cache-and-delete, API policy
- [ ] Total length approximately 0.5 page (300-400 words)
- [ ] Specific data points from prototype will be integrated in Sprint 3 B3.5

#### Harness Guidelines

- Save draft to `docs/deliverables/responsible_ai_draft.md`
- This is a first draft; Sprint 3 B3.5 will add real bias audit data from the prototype
- Keep placeholders like `[X]` where real data will be inserted

#### Steer Guidelines

- Responsible AI is worth 10 points (20% of judging) -- this is not a throwaway section
- Judges will look for concrete mitigations, not vague promises; "we will address bias" scores poorly vs. "we implemented a utilization cap and conducted a bias audit showing..."
- The Gemini API data usage policy note is important -- mention that API inputs are not used for training
- robots.txt compliance is a specific, demonstrable privacy practice

---

## Definition of Done

### Track A

- [ ] Web scraping works for 5 universities with cached fallback (`src/scraping/scraper.py`)
- [ ] LLM extraction produces valid structured JSON for 80%+ of scraped pages (`src/extraction/llm_extractor.py`)
- [ ] Discovery tab shows scraped events with "Add to Matching" button (`src/ui/discovery_tab.py`)
- [ ] Outreach emails generate correctly for any top match (`src/outreach/email_gen.py`)
- [ ] Calendar .ics file downloads correctly (`src/outreach/calendar_invite.py`)
- [ ] Pipeline funnel displays with real data labels (`src/ui/pipeline_tab.py`)
- [ ] Track B data package delivered (`docs/deliverables/track_b_data_package.md`)
- [ ] All new modules have `__init__.py` with public exports
- [ ] Unit tests exist for `scraper.py`, `llm_extractor.py`, `email_gen.py`, `calendar_invite.py`

### Track B

- [ ] Growth Strategy outline complete, Sections 1-3 drafted (~60% of document, ~1.5 pages)
- [ ] Measurement Plan first draft complete (KPI table, A/B test, feedback loop)
- [ ] ROI quantification draft with specific numbers (4.42h savings, $9,950/quarter)
- [ ] Responsible AI Note first draft complete (4 sections, ~0.5 page)
- [ ] Research notes documented with external citations
- [ ] All drafts saved in `docs/deliverables/`

## Phase Closeout

- At the end of every phase in this sprint, invoke a dedicated agent in code-review mode against the completed work.
- Do not mark the phase complete until review findings are resolved.
- After the review passes with no open issues, update the affected documentation and commit the changes.

---

## Go/No-Go Gate (End of Day 8)

### PASS Criteria

**Track A:**
- Live scrape of at least 1 university works during demo
- Cached scrapes available for all 5 universities
- Email generation produces quality output for any speaker-event match
- Pipeline funnel renders with real data from Sprint 1

**Track B:**
- Growth Strategy is 60%+ drafted with real data integrated (Sections 1-3)
- Measurement Plan first draft is complete with KPI table and A/B test
- Responsible AI Note first draft exists

### FAIL Responses

**Scraping fails for 3+ universities:**
- Reduce to 3 cached universities + 1 live demo target (UCLA recommended)
- No new scraping features after Day 8
- Mark remaining universities as "extensible" in the Growth Strategy

**LLM extraction produces invalid JSON for 50%+ pages:**
- Switch to regex-based extraction for the 2 most common page formats
- Pre-populate extracted event JSON as fixtures for demo
- Budget: 2h to implement regex fallback

**Email generation fails:**
- Use `_fallback_email()` template for all matches
- Pre-generate 3 emails for demo and cache as fixtures
- This is a non-negotiable feature; escalate if API is down

**Track B behind schedule (<40% Growth Strategy):**
- Reallocate Person B's Day 9 evening (2h) to help with data lookups
- Focus on Sections 1-2 (Executive Summary + Segments) -- these are highest-impact

---

## Memory Update Triggers

The following events should trigger updates to `.memory/context/`:

| Trigger | File to Update | Content |
|---------|---------------|---------|
| Scraping results for each university | `cat3-scraping-results.md` | URL, method, success/fail, event count, cache status |
| LLM extraction quality | `cat3-extraction-quality.md` | Per-university: events extracted, validation pass rate, common failures |
| Email generation quality | `cat3-email-quality.md` | Sample email, token usage, generation time, subjective quality rating |
| Track B data package delivered | `cat3-track-b-handoff.md` | Delivery timestamp, completeness rating, missing fields |
| Sprint 2 completion status | `cat3-sprint2-status.md` | Per-task status (done/partial/blocked), hours actual vs. planned |

---

## Dependencies

### Internal (from prior sprints)

| Dependency | Source | Required By | Status |
|-----------|--------|-------------|--------|
| Embedding pipeline | Sprint 0 A0.3-A0.4 | A2.2, A2.3 (for embedding discovered events) | Must be complete |
| Matching engine | Sprint 1 A1.1-A1.2 | A2.4 (match scores for email), A2.6 (match counts for funnel) | Must be complete |
| Match explanation cards | Sprint 1 A1.3 | A2.4 (reference style for email tone) | Must be complete |
| Matches tab UI | Sprint 1 A1.4 | A2.4 (email preview panel added to existing tab) | Must be complete |
| Pipeline sample data | Sprint 1 A1.6 | A2.6 (real data for funnel), A2.7 (data for Track B) | Must be complete |
| Scraping research notes | Sprint 1 A1.7 | A2.1 (which method per university) | Must be complete |

### External

| Dependency | Notes | Fallback |
|-----------|-------|----------|
| Gemini API (gemini-embedding-001) | For embedding discovered events | Use cached embeddings; flag as "cached-only" |
| Gemini API (gemini-2.5-flash-lite) | For LLM extraction and email generation | Use pre-generated fixtures; `_fallback_email()` template |
| University websites (5 targets) | Must be accessible for live scraping | Use 24h cached HTML; mark as "Cached" in UI |
| `icalendar` Python package | For .ics generation | Pure Python; no external service dependency |
| Internet connectivity | For live scraping demo | Demo mode with cached data |

### Cross-Track

| Dependency | From | To | Deadline | Content |
|-----------|------|----|----------|---------|
| Track B Data Package | A2.7 (Person B) | B2.1 (Person C) | Day 6 morning | Match results, pipeline data, ROI inputs, university coverage |
| Scraping results | A2.1 (Person B) | B2.3 (Person C) | Day 7 | University event counts for rollout plan projections |
| Email generation sample | A2.4 (Person B) | B2.2 (Person C) | Day 7 | Example output for Growth Strategy Section 4 |

---

## File Structure After Sprint 2

```
Category 3 - IA West Smart Match CRM/
  src/
    __init__.py
    scraping/
      __init__.py              # exports: scrape_university, scrape_all_universities, UNIVERSITY_TARGETS
      scraper.py               # NEW (A2.1)
    extraction/
      __init__.py              # exports: extract_events, preprocess_html
      llm_extractor.py         # NEW (A2.2)
    outreach/
      __init__.py              # exports: generate_outreach_email, generate_ics
      email_gen.py             # NEW (A2.4)
      calendar_invite.py       # NEW (A2.5)
    ui/
      __init__.py
      discovery_tab.py         # NEW (A2.3)
      matches_tab.py           # UPDATED (add email preview + .ics download)
      pipeline_tab.py          # UPDATED (A2.6 -- real data integration)
    matching/                  # from Sprint 1
      __init__.py
      scoring.py
      engine.py
    embeddings/                # from Sprint 0
      __init__.py
      pipeline.py
  data/
    data_speaker_profiles.csv
    data_cpp_events_contacts.csv
    data_cpp_course_schedule.csv
    data_event_calendar.csv
    pipeline_sample_data.csv   # from Sprint 1 A1.6
  cache/
    scrapes/                   # NEW -- JSON cache files (gitignored)
    emails/                    # NEW -- cached outreach emails for demo/runtime reuse
  docs/
    deliverables/
      track_b_data_package.md       # NEW (A2.7)
      research_notes.md             # NEW (B2.1)
      growth_strategy_draft.md      # NEW (B2.2, B2.3)
      measurement_plan_draft.md     # NEW (B2.4)
      roi_analysis.md               # NEW (B2.5) -- or integrated into growth strategy
      responsible_ai_draft.md       # NEW (B2.6)
    sprints/
      sprint-2-discovery-email.md   # this file
  tests/
    test_scraper.py            # NEW
    test_llm_extractor.py      # NEW
    test_email_gen.py          # NEW
    test_calendar_invite.py    # NEW
    fixtures/
      sample_university_html.html  # NEW
  requirements.txt             # UPDATED (add: icalendar, playwright)
  .gitignore                   # UPDATED (add: cache/)
```
