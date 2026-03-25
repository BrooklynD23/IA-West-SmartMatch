"""
LLM-based structured data extraction from scraped HTML.

Module: src/extraction/llm_extractor.py
Dependencies: Gemini API helper in ``src/gemini_client.py``, beautifulsoup4
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

try:
    from bs4 import BeautifulSoup  # type: ignore[import-untyped]

    _HAS_BS4 = True
except ImportError:
    BeautifulSoup = None  # type: ignore[assignment,misc]
    _HAS_BS4 = False

from src.config import (
    EXTRACTION_CACHE_DIR,
    EXTRACTION_MAX_TOKENS,
    EXTRACTION_MODEL,
    EXTRACTION_TEMPERATURE,
    GEMINI_API_KEY,
)
from src.gemini_client import generate_text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

EXTRACTED_EVENT_SCHEMA: dict[str, str] = {
    "event_name": "str -- name of the event",
    "category": (
        "str -- one of: hackathon, career_fair, case_competition, "
        "symposium, guest_lecture, networking, workshop, other"
    ),
    "date_or_recurrence": (
        "str -- specific date (YYYY-MM-DD) or recurrence "
        "pattern (e.g., 'Every Tuesday in Fall quarter')"
    ),
    "volunteer_roles": (
        "list[str] -- roles needed: judge, mentor, speaker, "
        "panelist, advisor, reviewer"
    ),
    "primary_audience": (
        "str -- e.g., 'undergraduate CS students', "
        "'MBA candidates', 'all majors'"
    ),
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

<content>
{content}
</content>

Return a JSON array of events.  Include ONLY events where industry \
professionals could volunteer as judges, mentors, speakers, or panelists.\
"""

# ---------------------------------------------------------------------------
# Few-shot examples (included in the system prompt for better extraction)
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES: str = """

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
    """Strip non-content HTML and truncate to fit within LLM context limits.

    Parameters
    ----------
    raw_html:
        Full HTML page content.
    max_chars:
        Maximum character count for the extracted text.

    Returns
    -------
    str
        Cleaned text content suitable for LLM extraction.
    """
    if not _HAS_BS4:
        logger.warning(
            "beautifulsoup4 is not installed; falling back to raw text truncation. "
            "Install it with: pip install beautifulsoup4"
        )
        text = raw_html
    else:
        soup = BeautifulSoup(raw_html, "html.parser")

        for tag in soup.find_all(
            ["script", "style", "nav", "footer", "header", "noscript", "iframe"]
        ):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n[TRUNCATED]"

    return cleaned


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

VALID_CATEGORIES: frozenset[str] = frozenset({
    "hackathon", "career_fair", "case_competition", "symposium",
    "guest_lecture", "networking", "workshop", "other",
})

VALID_ROLES: frozenset[str] = frozenset({
    "judge", "mentor", "speaker", "panelist", "advisor", "reviewer",
})


def _parse_and_validate(
    raw_json: str,
    source_url: str,
) -> list[dict[str, Any]]:
    """Parse LLM JSON output and validate each event against the schema.

    Handles two response shapes:
    - Direct JSON array: [{ ... }, { ... }]
    - Wrapped object: {"events": [{ ... }, { ... }]}
    """
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        logger.error("JSON parse error for %s: %s", source_url, exc)
        return []

    if isinstance(parsed, dict):
        if "events" in parsed:
            parsed = parsed["events"]
        else:
            parsed = [parsed]

    if not isinstance(parsed, list):
        logger.error("Expected list, got %s for %s", type(parsed).__name__, source_url)
        return []

    validated: list[dict[str, Any]] = []
    for i, event in enumerate(parsed):
        if not isinstance(event, dict):
            logger.warning("Skipping non-dict event at index %d for %s", i, source_url)
            continue

        if not event.get("event_name"):
            logger.warning("Skipping event without event_name at index %d", i)
            continue

        cat = event.get("category", "other")
        if cat not in VALID_CATEGORIES:
            event = {**event, "category": "other"}

        roles = event.get("volunteer_roles", [])
        if isinstance(roles, str):
            roles = [roles]
        event = {**event, "volunteer_roles": [r for r in roles if r in VALID_ROLES]}

        if not event.get("url"):
            event = {**event, "url": source_url}

        validated.append(event)

    logger.info("Extracted %d valid events from %s", len(validated), source_url)
    return validated


# ---------------------------------------------------------------------------
# Extraction cache
# ---------------------------------------------------------------------------

def _cache_key(url: str) -> str:
    """Generate a filesystem-safe cache key from a URL."""
    return hashlib.sha256(url.encode()).hexdigest()


def _validated_cached_events(payload: Any) -> list[dict[str, Any]] | None:
    """Return cached events only when the payload is a list of dicts."""
    if not isinstance(payload, list):
        return None
    if not all(isinstance(event, dict) for event in payload):
        return None
    return list(payload)


def load_extraction_cache(
    url: str,
    cache_dir: str | None = None,
) -> list[dict[str, Any]] | None:
    """Load previously cached extraction results for a URL.

    Returns
    -------
    list[dict] if cache hit, None if cache miss.
    """
    cache_dir = cache_dir or EXTRACTION_CACHE_DIR
    path = os.path.join(cache_dir, f"{_cache_key(url)}.json")
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            return _validated_cached_events(data)
        if not isinstance(data, dict):
            return None
        return _validated_cached_events(data.get("events"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load extraction cache for %s: %s", url, exc)
        return None


def save_extraction_cache(
    url: str,
    events: list[dict[str, Any]],
    cache_dir: str | None = None,
) -> str:
    """Persist extraction results to the JSON cache.

    Returns the path of the written cache file.
    """
    cache_dir = cache_dir or EXTRACTION_CACHE_DIR
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{_cache_key(url)}.json")
    payload = {
        "url": url,
        "events": events,
        "event_count": len(events),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


# ---------------------------------------------------------------------------
# Prompt sanitisation
# ---------------------------------------------------------------------------


def _sanitize_for_prompt(text: str) -> str:
    """Escape content delimiter patterns to prevent prompt injection."""
    return (
        text.replace("</content>", "&lt;/content&gt;")
        .replace("<content>", "&lt;content&gt;")
        .replace("--- BEGIN CONTENT ---", "--- BEGIN_CONTENT ---")
        .replace("--- END CONTENT ---", "--- END_CONTENT ---")
    )


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def extract_events(
    raw_html: str,
    university: str,
    url: str,
    model: str = EXTRACTION_MODEL,
    temperature: float = EXTRACTION_TEMPERATURE,
    prefer_cache: bool = False,
) -> list[dict[str, Any]]:
    """Extract structured event data from raw HTML using Gemini.

    Parameters
    ----------
    raw_html:
        The scraped HTML content.
    university:
        Name of the university (e.g., "UCLA").
    url:
        Source URL of the scraped page.
    model:
        Gemini model identifier.
    temperature:
        Sampling temperature. Low (0.1) for deterministic extraction.

    Returns
    -------
    list[dict]
        Extracted event dicts conforming to EXTRACTED_EVENT_SCHEMA.
        Empty list on any failure.
    """
    cached_events = load_extraction_cache(url)
    if prefer_cache and cached_events is not None:
        return cached_events

    content = preprocess_html(raw_html)

    if len(content.strip()) < 50:
        logger.warning(
            "Preprocessed HTML too short (%d chars) for %s", len(content), url,
        )
        return []

    system_message = EXTRACTION_SYSTEM_PROMPT + FEW_SHOT_EXAMPLES

    user_message = EXTRACTION_USER_PROMPT_TEMPLATE.format(
        university=university,
        url=url,
        content=_sanitize_for_prompt(content),
    )

    messages = [
        {"role": "user", "content": user_message},
    ]

    try:
        raw_output = generate_text(
            messages,
            api_key=GEMINI_API_KEY,
            model=model,
            system_instruction=system_message,
            temperature=temperature,
            max_output_tokens=EXTRACTION_MAX_TOKENS,
            timeout=30.0,
        )

        if not raw_output or not raw_output.strip():
            logger.warning("Empty LLM response for %s", url)
            return []

        events = _parse_and_validate(raw_output, url)
        if events and prefer_cache:
            save_extraction_cache(url, events)
        return events

    except Exception as exc:
        logger.error("LLM extraction failed for %s: %s", url, exc)
        fallback = load_extraction_cache(url)
        if fallback is not None:
            return fallback
        return []
