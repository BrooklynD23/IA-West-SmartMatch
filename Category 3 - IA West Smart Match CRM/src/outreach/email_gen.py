"""Outreach email generation using Gemini.

Uses generate_text() from src.gemini_client to produce personalized
outreach emails inviting board member volunteers to university events.
Follows the caching pattern from src/matching/explanations.py.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from src.config import (
    EMAIL_CACHE_DIR,
    EMAIL_MAX_TOKENS,
    EMAIL_MODEL,
    EMAIL_TEMPERATURE,
    GEMINI_API_KEY,
)
from src.gemini_client import generate_text

logger = logging.getLogger(__name__)

# Intentionally shadows config import; tests patch this attribute.
EMAIL_CACHE_DIR = Path(EMAIL_CACHE_DIR)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def event_value(event: dict[str, Any], *keys: str, default: str = "") -> Any:
    """Return the first present event value across literal CSV and derived keys."""
    for key in keys:
        value = event.get(key)
        if value not in (None, ""):
            return value
    return default


def _match_score_value(match_scores: dict[str, Any], canonical_key: str) -> float:
    """Extract a score from the canonical match-result schema.

    Supports Sprint 1's total_score + factor_scores.{...} layout
    and tolerates legacy shorthand aliases.
    """
    alias_map: dict[str, tuple[str, ...]] = {
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


# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

def _email_cache_key(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
) -> str:
    """Generate a deterministic cache key from speaker + event + score."""
    raw = "::".join([
        str(speaker.get("Name", "")),
        str(event_value(event, "Event / Program", "event_name", default="")),
        f"{_match_score_value(match_scores, 'total_score'):.4f}",
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_cached_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
) -> dict[str, str] | None:
    """Load a previously cached email from disk."""
    path = EMAIL_CACHE_DIR / f"{_email_cache_key(speaker, event, match_scores)}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError):
        return None


def save_cached_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
    email: dict[str, str],
) -> None:
    """Save a generated email to the disk cache."""
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
}\
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
# Fallback
# ---------------------------------------------------------------------------

def _fallback_email(
    speaker_name: str,
    speaker_expertise: str,
    event_name: str,
    volunteer_role: str,
) -> dict[str, str]:
    """Return a template email when LLM generation fails."""
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


# ---------------------------------------------------------------------------
# Email generation
# ---------------------------------------------------------------------------

def generate_outreach_email(
    speaker: dict[str, Any],
    event: dict[str, Any],
    match_scores: dict[str, Any],
    model: str = EMAIL_MODEL,
    temperature: float = EMAIL_TEMPERATURE,
) -> dict[str, str]:
    """Generate a personalized outreach email for a speaker-event match.

    Checks disk cache first. If no cached email, calls Gemini via
    generate_text(). On any API or JSON error, returns a template fallback.

    Returns dict with keys: subject_line, greeting, body, closing, full_email.
    """
    cached = load_cached_email(speaker, event, match_scores)
    if cached is not None:
        return cached

    speaker_name = speaker.get("Name", "Valued Board Member")
    speaker_title = speaker.get("Title", "your role")
    speaker_company = speaker.get("Company", "your organization")
    speaker_board_role = speaker.get("Board Role", "Board Member")
    speaker_metro = speaker.get("Metro Region", "your region")
    speaker_expertise = speaker.get("Expertise Tags", "your expertise")

    event_name = event_value(
        event, "Event / Program", "event_name", default="the upcoming event",
    )
    event_category = event_value(event, "Category", "category", default="event")
    event_host = event_value(
        event, "Host / Unit", "university", default="the university",
    )
    volunteer_role = event_value(
        event, "Volunteer Roles (fit)", "volunteer_roles", default="volunteer",
    )
    primary_audience = event_value(
        event, "Primary Audience", "primary_audience", default="students",
    )
    event_date = event_value(
        event, "Date", "IA Event Date", "date_or_recurrence",
        "Recurrence (typical)", default="TBD",
    )

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

    messages = [{"role": "user", "content": user_prompt}]

    fallback = _fallback_email(
        speaker_name, speaker_expertise, event_name, volunteer_role,
    )

    try:
        raw_response = generate_text(
            messages,
            api_key=GEMINI_API_KEY,
            model=model,
            system_instruction=EMAIL_SYSTEM_PROMPT,
            max_output_tokens=EMAIL_MAX_TOKENS,
            temperature=temperature,
            timeout=15.0,
        )

        result = json.loads(raw_response)

        required_keys = {"subject_line", "greeting", "body", "closing", "full_email"}
        if not required_keys.issubset(result.keys()):
            missing = required_keys - result.keys()
            logger.warning("Email response missing keys: %s", missing)
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

    except (json.JSONDecodeError, TypeError, KeyError) as exc:
        logger.warning("Email generation JSON parse error: %s", exc)
        return fallback
    except Exception as exc:
        logger.error("Email generation failed: %s", exc)
        return fallback
