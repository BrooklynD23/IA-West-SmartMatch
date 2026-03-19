"""
LLM-powered match explanation card generation.
Uses Gemini to produce 2-3 sentence natural language explanations
of why a speaker was matched to an event.
"""

import hashlib
import json
import logging
import re
from pathlib import Path

from src.config import (
    EXPLANATION_CACHE_DIR,
    EXPLANATION_MAX_TOKENS,
    EXPLANATION_MODEL,
    EXPLANATION_TEMPERATURE,
    GEMINI_API_KEY,
)
from src.gemini_client import generate_text

logger = logging.getLogger(__name__)

# ---------- Prompt Template ----------
EXPLANATION_SYSTEM_PROMPT = """You are a volunteer coordination assistant for IA West, \
a regional chapter of the Insights Association covering the West Coast. \
You write concise, professional explanations of why a specific board member \
volunteer was recommended for a university event or guest lecture opportunity.

Your explanations must:
1. Be 2-3 sentences maximum.
2. Reference the speaker's specific expertise and title (not generic praise).
3. Reference the specific event/course and why it aligns.
4. Mention the strongest 1-2 match factors by name with their scores.
5. Use a professional, warm tone appropriate for chapter leadership.
6. Never fabricate information not present in the provided data."""

EXPLANATION_USER_TEMPLATE = """Generate a match explanation for the following speaker-event pairing.

SPEAKER PROFILE:
- Name: {speaker_name}
- Title: {speaker_title}
- Company: {speaker_company}
- Board Role: {speaker_board_role}
- Metro Region: {speaker_metro_region}
- Expertise: {speaker_expertise_tags}

EVENT/OPPORTUNITY:
- Name: {event_name}
- Category: {event_category}
- Volunteer Roles Needed: {event_volunteer_roles}
- Primary Audience: {event_audience}

MATCH SCORES (0.0 to 1.0 scale):
- Topic Relevance: {topic_relevance:.2f}
- Role Fit: {role_fit:.2f}
- Geographic Proximity: {geographic_proximity:.2f}
- Calendar Fit: {calendar_fit:.2f}
- Historical Conversion: {historical_conversion:.2f}
- Student Interest: {student_interest:.2f}

Write a 2-3 sentence explanation of why this speaker is a strong match for this event. \
Reference specific expertise tags, the event type, and the top 1-2 scoring factors."""

# ---------- Few-Shot Examples ----------
FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": EXPLANATION_USER_TEMPLATE.format(
            speaker_name="Travis Miller",
            speaker_title="SVP, Sales & Client Development",
            speaker_company="PureSpectrum",
            speaker_board_role="President",
            speaker_metro_region="Ventura / Thousand Oaks",
            speaker_expertise_tags="data collection, MR technology adoption, sales, innovation",
            event_name="AI for a Better Future Hackathon",
            event_category="AI / Hackathon",
            event_volunteer_roles="Judge; Mentor; Guest speaker",
            event_audience="Students (business/tech)",
            total_score=0.87,
            topic_relevance=0.85,
            role_fit=0.80,
            geographic_proximity=0.75,
            calendar_fit=0.70,
            historical_conversion=0.50,
            student_interest=0.95,
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Travis Miller (SVP Sales & Client Development, PureSpectrum) is a strong "
            "match for the AI for a Better Future Hackathon because his expertise in MR "
            "technology adoption and data collection innovation directly aligns with the "
            "event's AI and technology focus (Topic Relevance: 0.85). As IA West President, "
            "he brings leadership credibility to the Judge and Mentor roles the event needs, "
            "and Ventura is within commuting distance of the campus (Proximity: 0.75)."
        ),
    },
    {
        "role": "user",
        "content": EXPLANATION_USER_TEMPLATE.format(
            speaker_name="Rob Kaiser",
            speaker_title="Marketing Science Leader",
            speaker_company="PSB",
            speaker_board_role="Treasurer",
            speaker_metro_region="Los Angeles — Long Beach",
            speaker_expertise_tags="AI innovation, creative analytics, marketing science, brand research",
            event_name="SWIFT Tech Symposium",
            event_category="Tech symposium / Speakers",
            event_volunteer_roles="Guest speaker; Workshop lead; Panelist",
            event_audience="Students (tech + business)",
            total_score=0.82,
            topic_relevance=0.88,
            role_fit=0.73,
            geographic_proximity=0.85,
            calendar_fit=0.70,
            historical_conversion=0.50,
            student_interest=0.75,
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Rob Kaiser (Marketing Science Leader, PSB) is an excellent fit for the "
            "SWIFT Tech Symposium given his dual expertise in AI innovation and creative "
            "analytics, which closely matches the symposium's tech-focused agenda "
            "(Topic Relevance: 0.88). Based in Long Beach, he is conveniently located "
            "near campus (Proximity: 0.85) and is well-suited for the Guest Speaker "
            "or Workshop Lead roles the event requires."
        ),
    },
]

FACTOR_LABELS = {
    "topic_relevance": "topic alignment",
    "role_fit": "role compatibility",
    "geographic_proximity": "geographic proximity",
    "calendar_fit": "calendar alignment",
    "historical_conversion": "engagement history",
    "student_interest": "student interest potential",
}


def _normalize_text(value: object, default: str = "") -> str:
    """Return a trimmed string with a fallback default for empty values."""
    if value is None:
        return default

    text = str(value).strip()
    return text or default


def _coerce_unit_score(value: object, default: float = 0.0) -> float:
    """Coerce a value to a float in [0.0, 1.0]."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, score))


def _normalized_factor_scores(raw_factor_scores: object) -> dict[str, float]:
    """Return a complete, ordered factor score mapping with safe defaults."""
    factor_scores = raw_factor_scores if isinstance(raw_factor_scores, dict) else {}
    return {
        factor: _coerce_unit_score(factor_scores.get(factor, 0.0))
        for factor in FACTOR_LABELS
    }


def _normalized_match_result(match_result: dict | None) -> dict:
    """Return a match payload with defaults suitable for cache and fallback use."""
    raw = match_result if isinstance(match_result, dict) else {}
    return {
        "speaker_name": _normalize_text(raw.get("speaker_name"), "Unknown speaker"),
        "speaker_title": _normalize_text(raw.get("speaker_title")),
        "speaker_company": _normalize_text(raw.get("speaker_company")),
        "speaker_board_role": _normalize_text(raw.get("speaker_board_role")),
        "speaker_metro_region": _normalize_text(raw.get("speaker_metro_region")),
        "speaker_expertise_tags": _normalize_text(raw.get("speaker_expertise_tags")),
        "event_name": _normalize_text(raw.get("event_name"), "Unknown event"),
        "total_score": _coerce_unit_score(raw.get("total_score", 0.0)),
        "factor_scores": _normalized_factor_scores(raw.get("factor_scores")),
    }


def _cache_identity(
    match_result: dict | None,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
) -> dict:
    """Return the stable prompt inputs used to identify an explanation cache entry."""
    normalized = _normalized_match_result(match_result)
    return {
        "speaker_name": normalized["speaker_name"],
        "speaker_title": normalized["speaker_title"],
        "speaker_company": normalized["speaker_company"],
        "speaker_board_role": normalized["speaker_board_role"],
        "speaker_metro_region": normalized["speaker_metro_region"],
        "speaker_expertise_tags": normalized["speaker_expertise_tags"],
        "event_name": normalized["event_name"],
        "event_category": _normalize_text(event_category),
        "event_volunteer_roles": _normalize_text(event_volunteer_roles),
        "event_audience": _normalize_text(event_audience),
        "factor_scores": normalized["factor_scores"],
    }


def _slugify(value: str) -> str:
    """Return a filesystem-safe lowercase slug."""
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "match"


def _cache_key(
    match_result: dict,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
) -> str:
    """Generate a deterministic cache key from stable explanation inputs."""
    identity = _cache_identity(
        match_result,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
    )
    raw = json.dumps(identity, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    hash_suffix = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    prefix = _slugify(f"{identity['speaker_name']}__{identity['event_name']}")[:80].rstrip("_")
    prefix = prefix or "match"
    return f"{prefix}__{hash_suffix}"


def load_cached_explanation(
    match_result: dict,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
) -> str | None:
    """Load a previously cached explanation from disk."""
    cache_dir = Path(EXPLANATION_CACHE_DIR)
    key = _cache_key(
        match_result,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
    )
    cache_file = cache_dir / f"{key}.json"

    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return data.get("explanation", None)
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def save_cached_explanation(
    match_result: dict,
    explanation: str,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
) -> None:
    """Save an explanation to the disk cache."""
    cache_dir = Path(EXPLANATION_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)

    normalized_match = _normalized_match_result(match_result)
    identity = _cache_identity(
        normalized_match,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
    )
    key = _cache_key(
        normalized_match,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
    )
    cache_file = cache_dir / f"{key}.json"

    data = {
        **identity,
        "cache_key_version": 2,
        "total_score": round(normalized_match["total_score"], 4),
        "explanation": explanation,
    }
    cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def fallback_match_explanation(match_result: dict) -> str:
    """Return the non-LLM fallback explanation for display or degraded operation."""
    return _fallback_explanation(match_result)


def generate_match_explanation(
    match_result: dict,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
    use_cache: bool = True,
) -> str:
    """Generate a natural language explanation for a match result.

    Checks disk cache first. If no cached explanation, calls Gemini.
    On any API error, returns a template-based fallback.
    """
    normalized_match = _normalized_match_result(match_result)
    factor_scores = normalized_match["factor_scores"]

    if use_cache:
        cached = load_cached_explanation(
            normalized_match,
            event_category=event_category,
            event_volunteer_roles=event_volunteer_roles,
            event_audience=event_audience,
        )
        if cached:
            return cached

    user_message = EXPLANATION_USER_TEMPLATE.format(
        speaker_name=normalized_match["speaker_name"],
        speaker_title=normalized_match["speaker_title"],
        speaker_company=normalized_match["speaker_company"],
        speaker_board_role=normalized_match["speaker_board_role"],
        speaker_metro_region=normalized_match["speaker_metro_region"],
        speaker_expertise_tags=normalized_match["speaker_expertise_tags"],
        event_name=normalized_match["event_name"],
        event_category=_normalize_text(event_category),
        event_volunteer_roles=_normalize_text(event_volunteer_roles),
        event_audience=_normalize_text(event_audience),
        topic_relevance=factor_scores.get("topic_relevance", 0.0),
        role_fit=factor_scores.get("role_fit", 0.0),
        geographic_proximity=factor_scores.get("geographic_proximity", 0.0),
        calendar_fit=factor_scores.get("calendar_fit", 0.0),
        historical_conversion=factor_scores.get("historical_conversion", 0.0),
        student_interest=factor_scores.get("student_interest", 0.0),
    )

    messages = [
        *FEW_SHOT_EXAMPLES,
        {"role": "user", "content": user_message},
    ]

    fallback = _fallback_explanation(normalized_match)
    try:
        explanation = generate_text(
            messages,
            api_key=GEMINI_API_KEY,
            model=EXPLANATION_MODEL,
            system_instruction=EXPLANATION_SYSTEM_PROMPT,
            max_output_tokens=EXPLANATION_MAX_TOKENS,
            temperature=EXPLANATION_TEMPERATURE,
            timeout=10.0,
        )
        if not explanation:
            explanation = fallback
    except Exception as exc:
        logger.warning("Gemini API error for explanation generation: %s", exc)
        explanation = fallback

    if use_cache:
        save_cached_explanation(
            normalized_match,
            explanation,
            event_category=event_category,
            event_volunteer_roles=event_volunteer_roles,
            event_audience=event_audience,
        )

    return explanation


def _fallback_explanation(match_result: dict) -> str:
    """Template-based fallback when LLM is unavailable."""
    normalized_match = _normalized_match_result(match_result)
    fs = normalized_match["factor_scores"]
    sorted_factors = sorted(fs.items(), key=lambda item: (-item[1], item[0]))
    top1_name, top1_score = sorted_factors[0]
    top2_name, top2_score = sorted_factors[1]

    speaker_context = ", ".join(
        part
        for part in [
            normalized_match["speaker_title"],
            normalized_match["speaker_company"],
        ]
        if part
    )
    speaker_label = (
        f"{normalized_match['speaker_name']} ({speaker_context})"
        if speaker_context
        else normalized_match["speaker_name"]
    )

    return (
        f"{speaker_label} is recommended for {normalized_match['event_name']} "
        f"because the match is strongest on "
        f"{FACTOR_LABELS.get(top1_name, top1_name)} ({top1_score:.2f}) and "
        f"{FACTOR_LABELS.get(top2_name, top2_name)} ({top2_score:.2f})."
    )
