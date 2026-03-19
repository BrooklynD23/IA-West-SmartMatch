"""
Individual scoring factors for IA SmartMatch speaker-event matching.

Each factor function returns a float in [0.0, 1.0].
All functions are pure computation — no API calls or I/O side effects.
"""

import logging
import re
from datetime import date, datetime
from typing import Optional

import numpy as np
import pandas as pd

from src.config import (
    CATEGORY_INTEREST_WEIGHTS,
    DEFAULT_CATEGORY_INTEREST,
    DEFAULT_EVENT_REGION,
    DEFAULT_HISTORICAL_CONVERSION,
    EVENT_REGION_MAP,
    GEO_PROXIMITY,
    ROLE_ALIASES,
)
from src.similarity import cosine_similarity_pair

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Factor 1: Topic Relevance
# ---------------------------------------------------------------------------

def topic_relevance(
    speaker_embedding: np.ndarray,
    event_embedding: np.ndarray,
) -> float:
    """
    Compute topic relevance as cosine similarity between speaker and event embeddings.

    Returns 0.0 when either embedding is missing, empty, zero-vector, or contains NaN.

    Args:
        speaker_embedding: 1-D numpy array representing the speaker's expertise.
        event_embedding: 1-D numpy array representing the event's topic profile.

    Returns:
        Similarity score in [0.0, 1.0].  Negative cosine values are clipped to 0.
    """
    if speaker_embedding is None or event_embedding is None:
        return 0.0
    if speaker_embedding.size == 0 or event_embedding.size == 0:
        return 0.0
    if np.any(np.isnan(speaker_embedding)) or np.any(np.isnan(event_embedding)):
        return 0.0

    norm_speaker = np.linalg.norm(speaker_embedding)
    norm_event = np.linalg.norm(event_embedding)
    if norm_speaker == 0.0 or norm_event == 0.0:
        return 0.0

    raw = cosine_similarity_pair(speaker_embedding, event_embedding)
    return float(max(0.0, min(1.0, raw)))


# ---------------------------------------------------------------------------
# Factor 2: Role Fit
# ---------------------------------------------------------------------------

def _tokenize_role_text(raw_role: str) -> tuple[str, ...]:
    """Split a role string into normalized word tokens."""
    return tuple(token for token in re.split(r"[^a-z0-9]+", raw_role.lower()) if token)


def _matches_role_alias(raw_role: str, alias: str) -> bool:
    """Return whether an alias matches on whole-token phrase boundaries."""
    role_tokens = _tokenize_role_text(raw_role)
    alias_tokens = _tokenize_role_text(alias)
    if not role_tokens or not alias_tokens:
        return False

    window_size = len(alias_tokens)
    return any(
        role_tokens[index:index + window_size] == alias_tokens
        for index in range(len(role_tokens) - window_size + 1)
    )


def _canonical_role(raw_role: str) -> Optional[str]:
    """
    Map a raw role string to a canonical alias group key.

    Returns the canonical key (e.g. "judge", "speaker") or None if no match.
    """
    normalized = raw_role.strip().lower()
    for canonical, aliases in ROLE_ALIASES.items():
        if any(_matches_role_alias(normalized, candidate) for candidate in [canonical, *aliases]):
            return canonical
    return None


def role_fit(
    speaker_board_role: str,
    event_volunteer_roles: str,
) -> float:
    """
    Score how well the speaker's board role aligns with the roles an event needs.

    Strategy:
    1. Exact / alias match on canonical role groups → 1.0
    2. Fuzzy token-set ratio via fuzzywuzzy as a fallback → score / 100

    Args:
        speaker_board_role: The speaker's board role string (e.g. "Judge").
        event_volunteer_roles: Semicolon- or comma-separated volunteer roles
            listed for the event.

    Returns:
        Role fit score in [0.0, 1.0].
    """
    if pd.isna(speaker_board_role) or pd.isna(event_volunteer_roles):
        return 0.0
    if not str(speaker_board_role).strip() or not str(event_volunteer_roles).strip():
        return 0.0

    speaker_role_lower = str(speaker_board_role).strip().lower()

    # Parse event volunteer roles (semicolon-separated)
    event_role_tokens = [
        r.strip()
        for r in str(event_volunteer_roles).replace(";", ",").split(",")
        if r.strip()
    ]
    event_roles_lower = [r.lower() for r in event_role_tokens if r]
    if not event_roles_lower:
        return 0.0

    # Map speaker to canonical roles
    speaker_canonical: set[str] = set()
    for canonical, aliases in ROLE_ALIASES.items():
        if any(_matches_role_alias(speaker_role_lower, alias) for alias in [canonical, *aliases]):
            speaker_canonical.add(canonical)

    # Director+ implies speaker capability (board leadership = qualified speaker)
    director_keywords = ["president", "director", "treasurer", "secretary"]
    if any(_matches_role_alias(speaker_role_lower, keyword) for keyword in director_keywords):
        speaker_canonical.add("speaker")

    # Map event to canonical roles
    event_canonical: set[str] = set()
    for canonical, aliases in ROLE_ALIASES.items():
        for event_role in event_roles_lower:
            if any(_matches_role_alias(event_role, alias) for alias in [canonical, *aliases]):
                event_canonical.add(canonical)

    # --- Pass 1: canonical set intersection scoring ---
    base_score = 0.0
    if event_canonical:
        intersection = speaker_canonical & event_canonical
        base_score = len(intersection) / len(event_canonical)

    # --- Pass 2: fuzzy matching via fuzzywuzzy (0.6x penalty) ---
    fuzzy_score = 0.0
    try:
        from fuzzywuzzy import fuzz  # type: ignore[import]

        fuzzy_scores = []
        for event_role in event_roles_lower:
            ratio = fuzz.token_set_ratio(speaker_role_lower, event_role)
            fuzzy_scores.append(ratio / 100.0 * 0.6)  # 0.6x confidence penalty
        fuzzy_score = max(fuzzy_scores) if fuzzy_scores else 0.0
    except ImportError:
        logger.warning(
            "fuzzywuzzy not installed; role_fit falling back to exact-only matching. "
            "Install with: pip install fuzzywuzzy python-Levenshtein"
        )

    return min(1.0, max(base_score, fuzzy_score))


# ---------------------------------------------------------------------------
# Factor 3: Geographic Proximity
# ---------------------------------------------------------------------------

def _resolve_event_region(raw_region: str) -> str:
    """
    Resolve a raw event location string to a canonical metro region name.

    Uses EVENT_REGION_MAP for known keywords, falls back to substring search
    against METRO_REGIONS, and finally returns DEFAULT_EVENT_REGION.
    """
    if not raw_region:
        return DEFAULT_EVENT_REGION

    normalized_region = raw_region.strip().lower()
    canonical_regions = {region for pair in GEO_PROXIMITY for region in pair}

    # Exact matches first, including canonical region names.
    for key, canonical in EVENT_REGION_MAP.items():
        if key.lower() == normalized_region:
            return canonical
    for region in canonical_regions:
        if region.lower() == normalized_region:
            return region

    # Prefer the longest canonical region substring before broad alias fallbacks.
    matching_regions = [
        region for region in canonical_regions
        if region.lower() in normalized_region
    ]
    if matching_regions:
        return max(matching_regions, key=len)

    matching_aliases = [
        (key, canonical) for key, canonical in EVENT_REGION_MAP.items()
        if key.lower() in normalized_region
    ]
    if matching_aliases:
        return max(matching_aliases, key=lambda item: len(item[0]))[1]

    logger.debug("Unknown event region %r — using default %r", raw_region, DEFAULT_EVENT_REGION)
    return DEFAULT_EVENT_REGION


def geographic_proximity(
    speaker_metro_region: str,
    event_region: str,
) -> float:
    """
    Look up the geographic proximity score between a speaker's metro region
    and an event's region.

    Args:
        speaker_metro_region: Speaker's canonical metro region string.
        event_region: Raw event region / location string.

    Returns:
        Proximity score in [0.0, 1.0].
    """
    if not speaker_metro_region:
        return 0.0

    canonical_event_region = _resolve_event_region(event_region)

    # Try (speaker, event) key, then (event, speaker) for symmetry
    score = GEO_PROXIMITY.get(
        (speaker_metro_region, canonical_event_region),
        GEO_PROXIMITY.get(
            (canonical_event_region, speaker_metro_region),
        ),
    )

    if score is None:
        logger.debug(
            "No GEO_PROXIMITY entry for (%r, %r); defaulting to 0.3",
            speaker_metro_region,
            canonical_event_region,
        )
        return 0.3

    return float(score)


# ---------------------------------------------------------------------------
# Factor 4: Calendar Fit
# ---------------------------------------------------------------------------

def _parse_date_flexible(value: object) -> Optional[date]:
    """
    Parse a value to a date object, accepting datetime, date, or ISO string.

    Returns None if parsing fails.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%B %d, %Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return None


def _recurrence_to_score(recurrence: str) -> float:
    """
    Map a recurrence description to a base calendar fit score.

    Higher frequency = higher score because there are more scheduling windows.
    """
    recurrence_lower = recurrence.strip().lower()
    recurrence_map = {
        "ongoing": 0.80,
        "ongoing series": 0.80,
        "weekly": 0.80,
        "bi-weekly": 0.75,
        "biweekly": 0.75,
        "annual": 0.70,
        "annually": 0.70,
        "recurring": 0.70,
        "recurring each term/year": 0.70,
        "monthly": 0.70,
        "quarterly": 0.65,
        "varies": 0.60,
        "semester": 0.60,
        "term": 0.60,
        "semi-annual": 0.55,
        "semiannual": 0.55,
        "one-time": 0.40,
        "once": 0.40,
        "tbd": 0.50,
    }
    for keyword, score in recurrence_map.items():
        if keyword in recurrence_lower:
            return score
    return 0.50


def calendar_fit(
    event_date_or_recurrence: object,
    ia_event_calendar: pd.DataFrame,
    speaker_metro_region: str,
) -> float:
    """
    Score calendar fit based on proximity of event date to IA events in the
    speaker's metro region.

    If a concrete date is provided, look for IA events within a 30-day window
    in the speaker's region and return a decay score based on proximity.

    If only a recurrence string is available, fall back to _recurrence_to_score.

    Args:
        event_date_or_recurrence: A date/datetime/ISO-string for a specific
            event date, or a recurrence description string (e.g. "Monthly").
        ia_event_calendar: DataFrame with columns "IA Event Date" and "Region".
        speaker_metro_region: Speaker's canonical metro region.

    Returns:
        Calendar fit score in [0.0, 1.0].
    """
    parsed_date = _parse_date_flexible(event_date_or_recurrence)

    if parsed_date is None:
        # Fall back to recurrence-based scoring
        recurrence_str = str(event_date_or_recurrence) if event_date_or_recurrence else ""
        return _recurrence_to_score(recurrence_str)

    if ia_event_calendar is None or ia_event_calendar.empty:
        return 0.50

    # Filter calendar to speaker's region if possible
    if "Region" in ia_event_calendar.columns and speaker_metro_region:
        region_mask = ia_event_calendar["Region"].str.lower().str.contains(
            speaker_metro_region.split("—")[0].strip().lower(),
            na=False,
        )
        region_df = ia_event_calendar[region_mask]
        if region_df.empty:
            region_df = ia_event_calendar
    else:
        region_df = ia_event_calendar

    if "IA Event Date" not in region_df.columns:
        return 0.50

    # Find the nearest IA event date within ±30 days
    window_days = 30
    best_score = 0.0

    for raw_ia_date in region_df["IA Event Date"].dropna():
        ia_date = _parse_date_flexible(raw_ia_date)
        if ia_date is None:
            continue
        delta = abs((parsed_date - ia_date).days)
        if delta <= window_days:
            # Linear decay: delta=0 → 1.0, delta=window_days → 0.5
            proximity_score = 1.0 - (delta / (2.0 * window_days))
            if proximity_score > best_score:
                best_score = proximity_score

    return round(best_score, 4) if best_score > 0.0 else 0.30


# ---------------------------------------------------------------------------
# Factor 5: Historical Conversion
# ---------------------------------------------------------------------------

def historical_conversion(
    speaker_name: str,
    conversion_overrides: Optional[dict[str, float]] = None,
) -> float:
    """
    Return the historical conversion score for a speaker.

    Uses explicit overrides when available, otherwise defaults to
    DEFAULT_HISTORICAL_CONVERSION (0.5).

    Args:
        speaker_name: Full name of the speaker (used as lookup key).
        conversion_overrides: Optional dict mapping speaker names to
            conversion scores in [0.0, 1.0].

    Returns:
        Conversion score in [0.0, 1.0].
    """
    if not conversion_overrides:
        return DEFAULT_HISTORICAL_CONVERSION

    # Try exact match, then case-insensitive match
    if speaker_name in conversion_overrides:
        return float(conversion_overrides[speaker_name])

    speaker_lower = speaker_name.strip().lower()
    for name_key, score in conversion_overrides.items():
        if name_key.strip().lower() == speaker_lower:
            return float(score)

    return DEFAULT_HISTORICAL_CONVERSION


# ---------------------------------------------------------------------------
# Factor 6: Student Interest
# ---------------------------------------------------------------------------

def student_interest(event_category: str) -> float:
    """
    Return the student interest weight for an event category.

    Args:
        event_category: The event category string (e.g. "Hackathon").

    Returns:
        Interest weight in [0.0, 1.0].
    """
    if not event_category:
        return DEFAULT_CATEGORY_INTEREST

    # Direct lookup
    if event_category in CATEGORY_INTEREST_WEIGHTS:
        return CATEGORY_INTEREST_WEIGHTS[event_category]

    # Case-insensitive partial match
    category_lower = event_category.strip().lower()
    for key, weight in CATEGORY_INTEREST_WEIGHTS.items():
        if key.lower() in category_lower or category_lower in key.lower():
            return weight

    logger.debug(
        "Unknown event category %r; using default interest weight %s",
        event_category,
        DEFAULT_CATEGORY_INTEREST,
    )
    return DEFAULT_CATEGORY_INTEREST
