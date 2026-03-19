---
doc_role: canonical
authority_scope:
- category.3.sprint.1
canonical_upstreams:
- Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md
- PRD_SECTION_CAT3.md
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-18'
managed_by: planning-agent
---

# Sprint 1: Matching Engine Core -- "The Brain"

**Duration:** Days 3-5
**Track:** A (Person B)
**Hours:** 21-24h

> **Governance notice:** This sprint spec derives its authority from `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` and `PRD_SECTION_CAT3.md`. Portfolio scheduling context comes from `archived/general_project_docs/MASTER_SPRINT_PLAN.md` and `archived/general_project_docs/STRATEGIC_REVIEW.md`. `Category 3 - IA West Smart Match CRM/PLAN.md` remains background-only.

**Prerequisite:** Sprint 0 complete -- all 4 CSVs loading, 68 embeddings cached, cosine similarity validated on 5+ known pairs, Streamlit skeleton running with 3 tabs.

**Go/No-Go Gate from Sprint 0:** Embeddings produce meaningfully different match scores (top match score > bottom match score by 0.15+). If FAIL, matching engine uses TF-IDF + keyword overlap instead of cosine similarity (2h pivot budget already consumed in Sprint 0).

---

## Table of Contents

1. [A1.1: MATCH_SCORE Formula Implementation (4.0h)](#a11-match_score-formula-implementation-40h)
2. [A1.2: Match Ranking Engine (2.5h)](#a12-match-ranking-engine-25h)
3. [A1.3: Match Explanation Cards (3.0h)](#a13-match-explanation-cards-30h)
4. [A1.4: Matches Tab UI (5.0h)](#a14-matches-tab-ui-50h)
5. [A1.5: Course Matching Integration (2.5h)](#a15-course-matching-integration-25h)
6. [A1.6: Pipeline Sample Data (2.0h)](#a16-pipeline-sample-data-20h)
7. [A1.7: University Scraping Research (2.0h)](#a17-university-scraping-research-20h)
8. [Definition of Done](#definition-of-done)
9. [Go/No-Go Gate](#gono-go-gate-end-of-day-5)
10. [Memory Update Triggers](#memory-update-triggers)
11. [Dependencies](#dependencies)

---

## File Map

All files created or modified in this sprint, relative to `Category 3 - IA West Smart Match CRM/`:

```
src/
  config.py              # DEFAULT_WEIGHTS, METRO_REGIONS, CATEGORY_WEIGHTS (new)
  matching/
    __init__.py           # (new)
    engine.py             # compute_match_score, rank_speakers_for_event, rank_speakers_for_course (new)
    explanations.py       # generate_match_explanation, load_cached_explanation (new)
    factors.py            # topic_relevance, role_fit, geographic_proximity, calendar_fit, historical_conversion, student_interest (new)
  ui/
    __init__.py           # (new)
    matches_tab.py        # render_matches_tab (new)
  app.py                  # Modify: wire Matches tab to render_matches_tab()
cache/
  explanations/           # JSON files keyed by speaker_id-event_id (new directory)
data/
  pipeline_sample_data.csv # Generated output (new)
docs/
  scraping_research.md    # University scraping feasibility notes (new)
```

---

## A1.1: MATCH_SCORE Formula Implementation (4.0h)

### Specification

**File:** `src/matching/factors.py` -- individual factor computation functions
**File:** `src/matching/engine.py` -- composite score orchestration
**File:** `src/config.py` -- weights, lookup tables, constants

#### 1. Configuration Constants (`src/config.py`)

```python
"""
Central configuration for the IA SmartMatch matching engine.
All tunable parameters live here so the UI weight sliders and
the matching engine share a single source of truth.
"""

from typing import Final

# ---------- Default Matching Weights ----------
# Must sum to 1.0. UI sliders override these at runtime.
DEFAULT_WEIGHTS: Final[dict[str, float]] = {
    "topic_relevance": 0.30,
    "role_fit": 0.25,
    "geographic_proximity": 0.20,
    "calendar_fit": 0.15,
    "historical_conversion": 0.05,
    "student_interest": 0.05,
}

# ---------- Metro Regions ----------
# Canonical region names (must match data_speaker_profiles.csv "Metro Region" values)
METRO_REGIONS: Final[list[str]] = [
    "Ventura / Thousand Oaks",
    "Los Angeles — West",
    "Los Angeles — East",
    "Los Angeles — North",
    "Los Angeles — Long Beach",
    "Los Angeles",
    "San Francisco",
    "San Diego",
    "Portland",
    "Seattle",
    "Orange County / Long Beach",
]

# ---------- Geographic Proximity Lookup Table ----------
# Values: 1.0 = same region, 0.0 = opposite ends of corridor.
# Symmetric matrix keyed by canonical region names.
# Distances estimated from drive-time bands:
#   1.0  = same metro (<30 min)
#   0.90 = adjacent metro (30-60 min)
#   0.75 = nearby metro (1-2 hr)
#   0.55 = moderate distance (2-4 hr)
#   0.35 = far (4-6 hr)
#   0.15 = very far (6-8 hr)
#   0.05 = extreme (8+ hr)
#
# "Los Angeles" variants (West, East, North, Long Beach, bare "Los Angeles")
# are treated as 0.90 to each other (intra-metro travel).
GEO_PROXIMITY: Final[dict[tuple[str, str], float]] = {
    # ------ Ventura / Thousand Oaks ------
    ("Ventura / Thousand Oaks", "Ventura / Thousand Oaks"): 1.00,
    ("Ventura / Thousand Oaks", "Los Angeles — West"): 0.85,
    ("Ventura / Thousand Oaks", "Los Angeles — East"): 0.75,
    ("Ventura / Thousand Oaks", "Los Angeles — North"): 0.85,
    ("Ventura / Thousand Oaks", "Los Angeles — Long Beach"): 0.70,
    ("Ventura / Thousand Oaks", "Los Angeles"): 0.80,
    ("Ventura / Thousand Oaks", "San Francisco"): 0.35,
    ("Ventura / Thousand Oaks", "San Diego"): 0.45,
    ("Ventura / Thousand Oaks", "Portland"): 0.10,
    ("Ventura / Thousand Oaks", "Seattle"): 0.05,
    ("Ventura / Thousand Oaks", "Orange County / Long Beach"): 0.65,
    # ------ Los Angeles — West ------
    ("Los Angeles — West", "Los Angeles — West"): 1.00,
    ("Los Angeles — West", "Los Angeles — East"): 0.85,
    ("Los Angeles — West", "Los Angeles — North"): 0.90,
    ("Los Angeles — West", "Los Angeles — Long Beach"): 0.80,
    ("Los Angeles — West", "Los Angeles"): 0.90,
    ("Los Angeles — West", "Ventura / Thousand Oaks"): 0.85,
    ("Los Angeles — West", "San Francisco"): 0.35,
    ("Los Angeles — West", "San Diego"): 0.50,
    ("Los Angeles — West", "Portland"): 0.10,
    ("Los Angeles — West", "Seattle"): 0.05,
    ("Los Angeles — West", "Orange County / Long Beach"): 0.75,
    # ------ Los Angeles — East (CPP is here) ------
    ("Los Angeles — East", "Los Angeles — East"): 1.00,
    ("Los Angeles — East", "Los Angeles — West"): 0.85,
    ("Los Angeles — East", "Los Angeles — North"): 0.85,
    ("Los Angeles — East", "Los Angeles — Long Beach"): 0.85,
    ("Los Angeles — East", "Los Angeles"): 0.90,
    ("Los Angeles — East", "Ventura / Thousand Oaks"): 0.75,
    ("Los Angeles — East", "San Francisco"): 0.30,
    ("Los Angeles — East", "San Diego"): 0.50,
    ("Los Angeles — East", "Portland"): 0.10,
    ("Los Angeles — East", "Seattle"): 0.05,
    ("Los Angeles — East", "Orange County / Long Beach"): 0.80,
    # ------ Los Angeles — North ------
    ("Los Angeles — North", "Los Angeles — North"): 1.00,
    ("Los Angeles — North", "Los Angeles — West"): 0.90,
    ("Los Angeles — North", "Los Angeles — East"): 0.85,
    ("Los Angeles — North", "Los Angeles — Long Beach"): 0.80,
    ("Los Angeles — North", "Los Angeles"): 0.90,
    ("Los Angeles — North", "Ventura / Thousand Oaks"): 0.85,
    ("Los Angeles — North", "San Francisco"): 0.35,
    ("Los Angeles — North", "San Diego"): 0.45,
    ("Los Angeles — North", "Portland"): 0.10,
    ("Los Angeles — North", "Seattle"): 0.05,
    ("Los Angeles — North", "Orange County / Long Beach"): 0.75,
    # ------ Los Angeles — Long Beach ------
    ("Los Angeles — Long Beach", "Los Angeles — Long Beach"): 1.00,
    ("Los Angeles — Long Beach", "Los Angeles — West"): 0.80,
    ("Los Angeles — Long Beach", "Los Angeles — East"): 0.85,
    ("Los Angeles — Long Beach", "Los Angeles — North"): 0.80,
    ("Los Angeles — Long Beach", "Los Angeles"): 0.85,
    ("Los Angeles — Long Beach", "Ventura / Thousand Oaks"): 0.70,
    ("Los Angeles — Long Beach", "San Francisco"): 0.30,
    ("Los Angeles — Long Beach", "San Diego"): 0.55,
    ("Los Angeles — Long Beach", "Portland"): 0.10,
    ("Los Angeles — Long Beach", "Seattle"): 0.05,
    ("Los Angeles — Long Beach", "Orange County / Long Beach"): 0.90,
    # ------ Los Angeles (bare / general) ------
    ("Los Angeles", "Los Angeles"): 1.00,
    ("Los Angeles", "Los Angeles — West"): 0.90,
    ("Los Angeles", "Los Angeles — East"): 0.90,
    ("Los Angeles", "Los Angeles — North"): 0.90,
    ("Los Angeles", "Los Angeles — Long Beach"): 0.85,
    ("Los Angeles", "Ventura / Thousand Oaks"): 0.80,
    ("Los Angeles", "San Francisco"): 0.35,
    ("Los Angeles", "San Diego"): 0.50,
    ("Los Angeles", "Portland"): 0.10,
    ("Los Angeles", "Seattle"): 0.05,
    ("Los Angeles", "Orange County / Long Beach"): 0.80,
    # ------ San Francisco ------
    ("San Francisco", "San Francisco"): 1.00,
    ("San Francisco", "Los Angeles — West"): 0.35,
    ("San Francisco", "Los Angeles — East"): 0.30,
    ("San Francisco", "Los Angeles — North"): 0.35,
    ("San Francisco", "Los Angeles — Long Beach"): 0.30,
    ("San Francisco", "Los Angeles"): 0.35,
    ("San Francisco", "Ventura / Thousand Oaks"): 0.35,
    ("San Francisco", "San Diego"): 0.15,
    ("San Francisco", "Portland"): 0.35,
    ("San Francisco", "Seattle"): 0.20,
    ("San Francisco", "Orange County / Long Beach"): 0.30,
    # ------ San Diego ------
    ("San Diego", "San Diego"): 1.00,
    ("San Diego", "Los Angeles — West"): 0.50,
    ("San Diego", "Los Angeles — East"): 0.50,
    ("San Diego", "Los Angeles — North"): 0.45,
    ("San Diego", "Los Angeles — Long Beach"): 0.55,
    ("San Diego", "Los Angeles"): 0.50,
    ("San Diego", "Ventura / Thousand Oaks"): 0.45,
    ("San Diego", "San Francisco"): 0.15,
    ("San Diego", "Portland"): 0.05,
    ("San Diego", "Seattle"): 0.05,
    ("San Diego", "Orange County / Long Beach"): 0.60,
    # ------ Portland ------
    ("Portland", "Portland"): 1.00,
    ("Portland", "Los Angeles — West"): 0.10,
    ("Portland", "Los Angeles — East"): 0.10,
    ("Portland", "Los Angeles — North"): 0.10,
    ("Portland", "Los Angeles — Long Beach"): 0.10,
    ("Portland", "Los Angeles"): 0.10,
    ("Portland", "Ventura / Thousand Oaks"): 0.10,
    ("Portland", "San Francisco"): 0.35,
    ("Portland", "San Diego"): 0.05,
    ("Portland", "Seattle"): 0.75,
    ("Portland", "Orange County / Long Beach"): 0.10,
    # ------ Seattle ------
    ("Seattle", "Seattle"): 1.00,
    ("Seattle", "Los Angeles — West"): 0.05,
    ("Seattle", "Los Angeles — East"): 0.05,
    ("Seattle", "Los Angeles — North"): 0.05,
    ("Seattle", "Los Angeles — Long Beach"): 0.05,
    ("Seattle", "Los Angeles"): 0.05,
    ("Seattle", "Ventura / Thousand Oaks"): 0.05,
    ("Seattle", "San Francisco"): 0.20,
    ("Seattle", "San Diego"): 0.05,
    ("Seattle", "Portland"): 0.75,
    ("Seattle", "Orange County / Long Beach"): 0.05,
    # ------ Orange County / Long Beach ------
    ("Orange County / Long Beach", "Orange County / Long Beach"): 1.00,
    ("Orange County / Long Beach", "Los Angeles — West"): 0.75,
    ("Orange County / Long Beach", "Los Angeles — East"): 0.80,
    ("Orange County / Long Beach", "Los Angeles — North"): 0.75,
    ("Orange County / Long Beach", "Los Angeles — Long Beach"): 0.90,
    ("Orange County / Long Beach", "Los Angeles"): 0.80,
    ("Orange County / Long Beach", "Ventura / Thousand Oaks"): 0.65,
    ("Orange County / Long Beach", "San Francisco"): 0.30,
    ("Orange County / Long Beach", "San Diego"): 0.60,
    ("Orange County / Long Beach", "Portland"): 0.10,
    ("Orange County / Long Beach", "Seattle"): 0.05,
}

# ---------- Event Region Mapping ----------
# Maps IA event calendar "Region" values and CPP event locations to
# canonical Metro Region keys for geographic proximity lookups.
# All CPP events are mapped to "Los Angeles — East" (Pomona).
EVENT_REGION_MAP: Final[dict[str, str]] = {
    "Portland": "Portland",
    "San Diego": "San Diego",
    "Los Angeles": "Los Angeles",
    "San Francisco": "San Francisco",
    "Seattle": "Seattle",
    "Ventura / Thousand Oaks": "Ventura / Thousand Oaks",
    "Orange County / Long Beach": "Orange County / Long Beach",
    # CPP-specific events default to LA East
    "Cal Poly Pomona": "Los Angeles — East",
    "CPP": "Los Angeles — East",
}

# Default region for events that don't have a mapped region.
DEFAULT_EVENT_REGION: Final[str] = "Los Angeles — East"

# ---------- Student Interest Category Weights ----------
# Maps event "Category" values to a student interest score [0.0, 1.0].
# Higher values = higher expected student engagement and IA pipeline value.
CATEGORY_INTEREST_WEIGHTS: Final[dict[str, float]] = {
    "AI / Hackathon": 0.95,
    "Case competition": 0.85,
    "Hackathon": 0.90,
    "Entrepreneurship / Pitch": 0.80,
    "Tech symposium / Speakers": 0.75,
    "Research showcase": 0.60,
    "Research symposium": 0.60,
    "Career services": 0.70,
    "Career fairs": 0.75,
}

# Default student interest score when category is not found in the map.
DEFAULT_CATEGORY_INTEREST: Final[float] = 0.50

# ---------- Role Aliases ----------
# Maps common variations of volunteer role names to canonical forms
# for fuzzy matching in role_fit computation.
ROLE_ALIASES: Final[dict[str, list[str]]] = {
    "judge": ["judge", "reviewer", "evaluator", "external discussant"],
    "mentor": ["mentor", "advisor", "coach"],
    "speaker": [
        "guest speaker", "speaker", "workshop speaker",
        "workshop lead", "panelist", "industry panelist",
        "employer-side speaker",
    ],
    "volunteer": ["volunteer"],
}

# ---------- Historical Conversion Defaults ----------
# Default historical conversion rate for all speakers.
# Tunable per speaker in future iterations.
DEFAULT_HISTORICAL_CONVERSION: Final[float] = 0.50

# ---------- Embedding Config ----------
EMBEDDING_MODEL: Final[str] = "gemini-embedding-001"
# Sprint 0 writes embedding artifacts as flat files directly under cache/.
EMBEDDING_CACHE_DIR: Final[str] = "cache"

# ---------- Explanation Config ----------
EXPLANATION_CACHE_DIR: Final[str] = "cache/explanations"
EXPLANATION_MODEL: Final[str] = "gemini-2.5-flash-lite"
EXPLANATION_MAX_TOKENS: Final[int] = 250
EXPLANATION_TEMPERATURE: Final[float] = 0.4
```

#### 2. Factor Computation Functions (`src/matching/factors.py`)

Each function takes the relevant data and returns a `float` in [0.0, 1.0].

```python
"""
Individual factor computation functions for the 6-factor MATCH_SCORE.
Every function returns a float in [0.0, 1.0].
"""

import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz

from src.config import (
    CATEGORY_INTEREST_WEIGHTS,
    DEFAULT_CATEGORY_INTEREST,
    DEFAULT_EVENT_REGION,
    DEFAULT_HISTORICAL_CONVERSION,
    EVENT_REGION_MAP,
    GEO_PROXIMITY,
    ROLE_ALIASES,
)


def topic_relevance(
    speaker_embedding: np.ndarray,
    event_embedding: np.ndarray,
) -> float:
    """
    Compute cosine similarity between speaker and event embeddings.

    Args:
        speaker_embedding: 1-D numpy array from gemini-embedding-001.
            Composed during Sprint 0 from:
            f"{expertise_tags} {title} {company} {board_role}"
        event_embedding: 1-D numpy array from gemini-embedding-001.
            Composed during Sprint 0 from:
            f"{event_name} {category} {volunteer_roles} {primary_audience}"

    Returns:
        Cosine similarity in [0.0, 1.0]. Returns 0.0 if either embedding
        is a zero vector (edge case: speaker with no expertise tags).

    Edge cases:
        - speaker_embedding is all zeros -> return 0.0
        - event_embedding is all zeros -> return 0.0
        - NaN in either embedding -> return 0.0
    """
    # Guard: check for NaN or zero-length vectors
    if speaker_embedding is None or event_embedding is None:
        return 0.0
    if np.any(np.isnan(speaker_embedding)) or np.any(np.isnan(event_embedding)):
        return 0.0

    norm_speaker = np.linalg.norm(speaker_embedding)
    norm_event = np.linalg.norm(event_embedding)

    if norm_speaker == 0.0 or norm_event == 0.0:
        return 0.0

    cosine_sim = float(
        np.dot(speaker_embedding, event_embedding) / (norm_speaker * norm_event)
    )
    # Clamp to [0.0, 1.0] -- cosine similarity can theoretically be negative
    # for opposing vectors, but embeddings from the same model are typically >= 0.
    return max(0.0, min(1.0, cosine_sim))


def role_fit(
    speaker_board_role: str,
    event_volunteer_roles: str,
) -> float:
    """
    Score how well the speaker's board role maps to the event's needed volunteer roles.

    Uses a two-pass approach:
    1. Exact substring match against canonical role aliases -> 1.0
    2. Fuzzy token-set-ratio match -> scaled score

    Args:
        speaker_board_role: e.g. "President", "Metro Director — Seattle",
            "Director of Events". From data_speaker_profiles.csv "Board Role".
        event_volunteer_roles: Semicolon-separated string, e.g.
            "Judge; Mentor; Guest speaker". From data_cpp_events_contacts.csv
            "Volunteer Roles (fit)".

    Returns:
        Float in [0.0, 1.0].

    Edge cases:
        - event_volunteer_roles is empty/NaN -> return 0.0
        - speaker_board_role is empty/NaN -> return 0.0

    Scoring logic:
        1. Parse event_volunteer_roles into a list by splitting on ";" and stripping.
        2. For each canonical role in ROLE_ALIASES, check if ANY alias appears
           as a substring (case-insensitive) in the speaker_board_role.
           Collect the set of canonical roles the speaker maps to.
        3. For each canonical role in ROLE_ALIASES, check if ANY alias appears
           as a substring in any of the event volunteer role strings.
           Collect the set of canonical roles the event needs.
        4. If the intersection is non-empty, base_score = |intersection| / |event_needs|.
        5. Otherwise, fall back to fuzzy matching:
           For each event role string, compute fuzz.token_set_ratio(speaker_board_role, event_role).
           Take the max ratio, divide by 100, and apply a 0.6x penalty
           (fuzzy matches are less confident than exact canonical matches).
        6. The final score is max(base_score, fuzzy_score), clamped to [0.0, 1.0].
    """
    if pd.isna(speaker_board_role) or pd.isna(event_volunteer_roles):
        return 0.0

    speaker_role_lower = str(speaker_board_role).lower().strip()
    if not speaker_role_lower:
        return 0.0

    # Parse event volunteer roles
    event_roles_raw = [r.strip() for r in str(event_volunteer_roles).split(";")]
    event_roles_lower = [r.lower() for r in event_roles_raw if r]
    if not event_roles_lower:
        return 0.0

    # Map speaker to canonical roles
    speaker_canonical: set[str] = set()
    for canonical, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            if alias in speaker_role_lower:
                speaker_canonical.add(canonical)

    # All board members can plausibly serve as speakers/panelists due to seniority.
    # Add a baseline "speaker" capability for any director-level or above role.
    director_keywords = ["president", "director", "treasurer", "secretary"]
    if any(kw in speaker_role_lower for kw in director_keywords):
        speaker_canonical.add("speaker")

    # Map event to canonical roles
    event_canonical: set[str] = set()
    for canonical, aliases in ROLE_ALIASES.items():
        for alias in aliases:
            for event_role in event_roles_lower:
                if alias in event_role:
                    event_canonical.add(canonical)

    # Exact canonical match scoring
    if event_canonical:
        intersection = speaker_canonical & event_canonical
        base_score = len(intersection) / len(event_canonical) if event_canonical else 0.0
    else:
        base_score = 0.0

    # Fuzzy fallback
    fuzzy_scores = []
    for event_role in event_roles_lower:
        ratio = fuzz.token_set_ratio(speaker_role_lower, event_role)
        fuzzy_scores.append(ratio / 100.0 * 0.6)  # 0.6x confidence penalty
    fuzzy_score = max(fuzzy_scores) if fuzzy_scores else 0.0

    return min(1.0, max(base_score, fuzzy_score))


def geographic_proximity(
    speaker_metro_region: str,
    event_region: str,
) -> float:
    """
    Look up the geographic proximity score between a speaker's metro region
    and an event's region using the GEO_PROXIMITY table.

    Args:
        speaker_metro_region: From data_speaker_profiles.csv "Metro Region".
            e.g. "Ventura / Thousand Oaks", "Los Angeles — West".
        event_region: Either from data_event_calendar.csv "Region" or
            derived from the event source (CPP events -> "Los Angeles — East").
            Looked up in EVENT_REGION_MAP first.

    Returns:
        Float in [0.0, 1.0].

    Edge cases:
        - speaker_metro_region not found in GEO_PROXIMITY -> return 0.3
          (assume moderate distance as a conservative default)
        - event_region not found in EVENT_REGION_MAP -> use DEFAULT_EVENT_REGION
        - Both are the same string -> return 1.0
    """
    if pd.isna(speaker_metro_region) or pd.isna(event_region):
        return 0.3

    speaker_region = str(speaker_metro_region).strip()
    event_region_raw = str(event_region).strip()

    # Map event region to canonical form
    event_region_canonical = EVENT_REGION_MAP.get(event_region_raw, None)
    if event_region_canonical is None:
        # Try partial matching: check if any key is a substring
        for key, val in EVENT_REGION_MAP.items():
            if key.lower() in event_region_raw.lower():
                event_region_canonical = val
                break
        if event_region_canonical is None:
            event_region_canonical = DEFAULT_EVENT_REGION

    # Same region shortcut
    if speaker_region == event_region_canonical:
        return 1.0

    # Lookup in both orderings (table is populated symmetrically but
    # we check both to be safe)
    key_forward = (speaker_region, event_region_canonical)
    key_reverse = (event_region_canonical, speaker_region)

    score = GEO_PROXIMITY.get(key_forward, GEO_PROXIMITY.get(key_reverse, None))
    if score is not None:
        return score

    # Fallback: conservative default for unknown region pairs
    return 0.3


def calendar_fit(
    event_date_or_recurrence: str,
    ia_event_calendar: pd.DataFrame,
    speaker_metro_region: str,
) -> float:
    """
    Score how well an event aligns with the IA event calendar timing windows.

    The logic rewards events that fall within IA event "Suggested Lecture Window"
    for the speaker's geographic region, creating a natural handoff from campus
    engagement to IA event attendance.

    Args:
        event_date_or_recurrence: From data_cpp_events_contacts.csv
            "Recurrence (typical)" column. Often values like "Annual",
            "Recurring each term/year", "Ongoing series + pitch events".
            For discovered (scraped) events, may be an actual date string.
        ia_event_calendar: Full DataFrame from data_event_calendar.csv.
            Columns: IA Event Date, Region, Nearby Universities,
            Suggested Lecture Window, Course Alignment
        speaker_metro_region: Speaker's metro region for regional affinity.

    Returns:
        Float in [0.0, 1.0].

    Scoring rules:
        1. If event_date_or_recurrence is an actual date (parseable):
           - Check if it falls within any "Suggested Lecture Window" from the
             IA event calendar.
           - If match found in same region as speaker: 1.0
           - If match found in adjacent region: 0.8
           - If match found in any region: 0.6
           - If no match but within +/- 30 days of any IA event: 0.4
           - Otherwise: 0.2

        2. If event_date_or_recurrence is a recurrence pattern (e.g., "Annual"):
           - "Annual" or "Recurring": 0.7 (likely aligns with at least one window)
           - "Ongoing" or "Ongoing series": 0.8 (flexible timing = high fit)
           - Unknown pattern: 0.5 (neutral)

        3. If event_date_or_recurrence is NaN/empty: 0.5 (neutral default)

    Note: For the CPP dataset, most events have recurrence patterns rather
    than specific dates. The calendar_fit factor becomes more valuable for
    scraped events with actual dates (Sprint 2).
    """
    if pd.isna(event_date_or_recurrence):
        return 0.5

    date_str = str(event_date_or_recurrence).strip().lower()

    # Attempt date parsing
    parsed_date = None
    try:
        parsed_date = pd.to_datetime(date_str, format="mixed", dayfirst=False)
    except (ValueError, TypeError):
        parsed_date = None

    if parsed_date is not None and ia_event_calendar is not None:
        # Date-based scoring
        best_score = 0.2  # default: no alignment
        for _, ia_row in ia_event_calendar.iterrows():
            try:
                ia_date = pd.to_datetime(ia_row["IA Event Date"])
            except (ValueError, TypeError):
                continue

            days_diff = abs((parsed_date - ia_date).days)
            ia_region = str(ia_row.get("Region", "")).strip()

            if days_diff <= 14:
                # Within suggested lecture window
                if ia_region == speaker_metro_region:
                    best_score = max(best_score, 1.0)
                elif geographic_proximity(speaker_metro_region, ia_region) >= 0.7:
                    best_score = max(best_score, 0.8)
                else:
                    best_score = max(best_score, 0.6)
            elif days_diff <= 30:
                best_score = max(best_score, 0.4)
        return best_score

    # Recurrence-pattern-based scoring
    if "ongoing" in date_str:
        return 0.8
    if "annual" in date_str or "recurring" in date_str:
        return 0.7
    if "varies" in date_str or "semester" in date_str or "term" in date_str:
        return 0.6

    return 0.5


def historical_conversion(
    speaker_name: str,
    conversion_overrides: dict[str, float] | None = None,
) -> float:
    """
    Return the speaker's historical conversion rate.

    In the initial prototype, all speakers default to DEFAULT_HISTORICAL_CONVERSION
    (0.5). This factor exists as a hook for future tuning based on actual
    match acceptance data collected via the feedback loop (Sprint 3, A3.2).

    Args:
        speaker_name: Speaker's full name from data_speaker_profiles.csv "Name".
        conversion_overrides: Optional dict mapping speaker names to custom
            conversion rates. If provided and the speaker is found, use that
            value. Otherwise use the default.

    Returns:
        Float in [0.0, 1.0].

    Edge cases:
        - speaker_name is NaN/empty -> return DEFAULT_HISTORICAL_CONVERSION
        - speaker not in overrides -> return DEFAULT_HISTORICAL_CONVERSION
    """
    if pd.isna(speaker_name) or not str(speaker_name).strip():
        return DEFAULT_HISTORICAL_CONVERSION

    if conversion_overrides and str(speaker_name).strip() in conversion_overrides:
        rate = conversion_overrides[str(speaker_name).strip()]
        return max(0.0, min(1.0, rate))

    return DEFAULT_HISTORICAL_CONVERSION


def student_interest(
    event_category: str,
) -> float:
    """
    Return the student interest weight for a given event category.

    Maps event categories to expected student engagement levels using the
    CATEGORY_INTEREST_WEIGHTS lookup table. Higher values indicate events
    that are more likely to generate student interest, foot traffic, and
    downstream IA membership pipeline value.

    Args:
        event_category: From data_cpp_events_contacts.csv "Category" column.
            e.g. "AI / Hackathon", "Case competition", "Career services".

    Returns:
        Float in [0.0, 1.0].

    Edge cases:
        - event_category is NaN/empty -> return DEFAULT_CATEGORY_INTEREST (0.50)
        - event_category not in map -> attempt case-insensitive partial match,
          then return DEFAULT_CATEGORY_INTEREST if no match found
    """
    if pd.isna(event_category) or not str(event_category).strip():
        return DEFAULT_CATEGORY_INTEREST

    category = str(event_category).strip()

    # Exact match
    if category in CATEGORY_INTEREST_WEIGHTS:
        return CATEGORY_INTEREST_WEIGHTS[category]

    # Case-insensitive partial match
    category_lower = category.lower()
    for key, value in CATEGORY_INTEREST_WEIGHTS.items():
        if key.lower() in category_lower or category_lower in key.lower():
            return value

    return DEFAULT_CATEGORY_INTEREST
```

#### 3. Composite Score Function (`src/matching/engine.py`)

```python
"""
Core matching engine: composite scoring and ranking.
"""

import numpy as np
import pandas as pd

from src.config import DEFAULT_WEIGHTS
from src.matching.factors import (
    calendar_fit,
    geographic_proximity,
    historical_conversion,
    role_fit,
    student_interest,
    topic_relevance,
)


def compute_match_score(
    speaker: pd.Series,
    event: pd.Series,
    weights: dict[str, float] | None = None,
    speaker_embedding: np.ndarray | None = None,
    event_embedding: np.ndarray | None = None,
    ia_event_calendar: pd.DataFrame | None = None,
    conversion_overrides: dict[str, float] | None = None,
) -> tuple[float, dict[str, float]]:
    """
    Compute the composite MATCH_SCORE for a speaker-event pair.

    The score is a weighted sum of 6 factors, each normalized to [0.0, 1.0].
    The weights are user-tunable via sidebar sliders; if not provided,
    DEFAULT_WEIGHTS from config.py are used.

    Args:
        speaker: A single row (pd.Series) from data_speaker_profiles.csv.
            Required keys: "Name", "Board Role", "Metro Region",
            "Company", "Title", "Expertise Tags"
        event: A single row (pd.Series) from data_cpp_events_contacts.csv.
            Required keys: "Event / Program", "Category",
            "Volunteer Roles (fit)", "Primary Audience"
            Optional keys: "Recurrence (typical)" (for calendar fit)
        weights: Dict mapping factor names to float weights.
            Keys must be a subset of DEFAULT_WEIGHTS keys.
            If None, DEFAULT_WEIGHTS are used.
            Weights are normalized to sum to 1.0 before use.
        speaker_embedding: Pre-computed embedding for the speaker.
            Loaded from Sprint 0 flat cache files under cache/ (for example
            cache/speaker_embeddings.npy + cache/speaker_metadata.pkl).
        event_embedding: Pre-computed embedding for the event.
            Loaded from Sprint 0 flat cache files under cache/ (for example
            cache/event_embeddings.npy + cache/event_metadata.pkl).
        ia_event_calendar: Full DataFrame from data_event_calendar.csv.
            Passed through to calendar_fit(). If None, calendar_fit
            returns the recurrence-based default.
        conversion_overrides: Optional per-speaker conversion rates.
            Passed through to historical_conversion().

    Returns:
        A tuple of:
        - composite_score (float): Weighted sum in [0.0, 1.0].
        - factor_scores (dict[str, float]): Per-factor breakdown, e.g.:
          {
              "topic_relevance": 0.85,
              "role_fit": 0.67,
              "geographic_proximity": 0.90,
              "calendar_fit": 0.70,
              "historical_conversion": 0.50,
              "student_interest": 0.95,
          }

    Edge cases:
        - All weights are 0.0 -> return (0.0, {all factors: computed values})
        - Missing speaker embedding -> topic_relevance = 0.0
        - Missing event volunteer roles -> role_fit = 0.0
        - Unknown metro region -> geographic_proximity = 0.3 (conservative)
    """
    # Use default weights if none provided
    w = dict(DEFAULT_WEIGHTS) if weights is None else dict(weights)

    # Normalize weights to sum to 1.0
    weight_sum = sum(w.values())
    if weight_sum > 0:
        w = {k: v / weight_sum for k, v in w.items()}
    else:
        # All weights are zero: return 0.0 composite but still compute factors
        w = {k: 0.0 for k in DEFAULT_WEIGHTS}

    # Compute each factor
    factor_scores: dict[str, float] = {}

    # Factor 1: Topic Relevance (cosine similarity)
    factor_scores["topic_relevance"] = topic_relevance(
        speaker_embedding=speaker_embedding,
        event_embedding=event_embedding,
    )

    # Factor 2: Role Fit
    factor_scores["role_fit"] = role_fit(
        speaker_board_role=speaker.get("Board Role", ""),
        event_volunteer_roles=event.get("Volunteer Roles (fit)", ""),
    )

    # Factor 3: Geographic Proximity
    # For CPP events, the event region is "Los Angeles — East"
    event_region = event.get("Region", None)
    if pd.isna(event_region) or event_region is None:
        # CPP events don't have a Region column; default to LA East
        event_region = "Los Angeles — East"
    factor_scores["geographic_proximity"] = geographic_proximity(
        speaker_metro_region=speaker.get("Metro Region", ""),
        event_region=event_region,
    )

    # Factor 4: Calendar Fit
    factor_scores["calendar_fit"] = calendar_fit(
        event_date_or_recurrence=event.get("Recurrence (typical)", ""),
        ia_event_calendar=ia_event_calendar,
        speaker_metro_region=speaker.get("Metro Region", ""),
    )

    # Factor 5: Historical Conversion
    factor_scores["historical_conversion"] = historical_conversion(
        speaker_name=speaker.get("Name", ""),
        conversion_overrides=conversion_overrides,
    )

    # Factor 6: Student Interest
    factor_scores["student_interest"] = student_interest(
        event_category=event.get("Category", ""),
    )

    # Compute weighted composite
    composite = sum(
        w.get(factor_name, 0.0) * score
        for factor_name, score in factor_scores.items()
    )

    # Clamp to [0.0, 1.0]
    composite = max(0.0, min(1.0, composite))

    return composite, factor_scores
```

### Acceptance Criteria

- [ ] `compute_match_score()` returns a `tuple[float, dict[str, float]]` for any valid speaker-event pair
- [ ] All 6 factor functions return values in [0.0, 1.0]
- [ ] Weights are normalized to sum to 1.0 before computation
- [ ] `GEO_PROXIMITY` table covers all 11 metro regions (11 x 11 = 121 entries, symmetric)
- [ ] Edge case: speaker with empty "Expertise Tags" -> `topic_relevance` returns 0.0
- [ ] Edge case: event with empty "Volunteer Roles (fit)" -> `role_fit` returns 0.0
- [ ] Edge case: unknown metro region -> `geographic_proximity` returns 0.3
- [ ] Edge case: all weights set to 0.0 -> composite returns 0.0, factor_scores still computed
- [ ] `CATEGORY_INTEREST_WEIGHTS` covers all 9 event categories in the CPP data
- [ ] `ROLE_ALIASES` maps all volunteer role strings found in data_cpp_events_contacts.csv
- [ ] Factor scores for all 270 speaker-event pairs (18 speakers x 15 events) compute without errors

### Harness Guidelines

- Store `DEFAULT_WEIGHTS` and all lookup tables in `src/config.py` -- never hardcode in `engine.py`
- Import factor functions from `src/matching/factors.py` into `src/matching/engine.py`
- All factor functions must be independently testable (no cross-factor dependencies)
- Use `np.ndarray` for embeddings, not lists -- consistency with Sprint 0 cache format
- The `GEO_PROXIMITY` table must be symmetric: if `(A, B)` is defined, `(B, A)` must have the same value

### Steer Guidelines

- If the coding agent defines `GEO_PROXIMITY` as a 2D numpy array instead of a dict, that is acceptable as long as there is a name-to-index mapping
- If the coding agent adds additional factors beyond the 6 specified, reject -- scope creep
- The `role_fit` function must include the "director+ implies speaker" heuristic to avoid zero-scoring board members who clearly can serve as speakers
- `calendar_fit` MUST handle the recurrence-pattern case gracefully because most CPP events do NOT have specific dates
- If the agent tries to call the Gemini API from within any factor function, reject -- factors must be pure computation using pre-cached embeddings

---

## A1.2: Match Ranking Engine (2.5h)

### Specification

**File:** `src/matching/engine.py` (add to same file as `compute_match_score`)

#### 1. Event-Based Ranking

```python
def rank_speakers_for_event(
    event: pd.Series,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embedding: np.ndarray | None = None,
    ia_event_calendar: pd.DataFrame | None = None,
    weights: dict[str, float] | None = None,
    top_n: int = 3,
    conversion_overrides: dict[str, float] | None = None,
) -> list[dict]:
    """
    Rank all speakers for a given event and return the top N matches.

    Args:
        event: A single row (pd.Series) from the events DataFrame.
        speakers: Full DataFrame of speaker profiles (18 rows).
        speaker_embeddings: Dict mapping speaker "Name" to pre-computed
            embedding np.ndarray. From Sprint 0 cache.
        event_embedding: Pre-computed embedding for this event.
        ia_event_calendar: Full DataFrame from data_event_calendar.csv.
        weights: User-tuned weights dict. Passed to compute_match_score().
        top_n: Number of top matches to return. Default 3.
        conversion_overrides: Optional per-speaker conversion rates.

    Returns:
        List of dicts, sorted by total_score descending, length = top_n.
        Each dict has the structure:

        {
            "rank": 1,                          # 1-indexed rank
            "speaker_name": "Travis Miller",
            "speaker_title": "SVP, Sales & Client Development",
            "speaker_company": "PureSpectrum",
            "speaker_board_role": "President",
            "speaker_metro_region": "Ventura / Thousand Oaks",
            "speaker_expertise_tags": "data collection, MR technology...",
            "event_name": "AI for a Better Future Hackathon",
            "total_score": 0.823,               # Composite score
            "factor_scores": {                  # Per-factor breakdown
                "topic_relevance": 0.85,
                "role_fit": 0.67,
                "geographic_proximity": 0.90,
                "calendar_fit": 0.70,
                "historical_conversion": 0.50,
                "student_interest": 0.95,
            },
            "weighted_factor_scores": {         # factor_score * weight
                "topic_relevance": 0.255,       # 0.85 * 0.30
                "role_fit": 0.168,              # 0.67 * 0.25
                "geographic_proximity": 0.180,  # 0.90 * 0.20
                "calendar_fit": 0.105,          # 0.70 * 0.15
                "historical_conversion": 0.025, # 0.50 * 0.05
                "student_interest": 0.048,      # 0.95 * 0.05
            },
        }

        This is the downstream contract for Sprint 2+ consumers.
        Do not abbreviate keys such as `total_score` or `topic_relevance`.

    Implementation:
        1. Iterate over each row in speakers DataFrame.
        2. Call compute_match_score() for each speaker-event pair.
        3. Collect results into a list of dicts.
        4. Sort by total_score descending.
        5. Return the top top_n entries with 1-indexed ranks.
    """
    results = []
    w = dict(DEFAULT_WEIGHTS) if weights is None else dict(weights)
    weight_sum = sum(w.values())
    normalized_w = (
        {k: v / weight_sum for k, v in w.items()} if weight_sum > 0
        else {k: 0.0 for k in DEFAULT_WEIGHTS}
    )

    for _, speaker in speakers.iterrows():
        speaker_name = str(speaker.get("Name", ""))
        speaker_emb = speaker_embeddings.get(speaker_name, None)

        total_score, factor_scores = compute_match_score(
            speaker=speaker,
            event=event,
            weights=weights,
            speaker_embedding=speaker_emb,
            event_embedding=event_embedding,
            ia_event_calendar=ia_event_calendar,
            conversion_overrides=conversion_overrides,
        )

        weighted_factors = {
            k: round(v * normalized_w.get(k, 0.0), 4)
            for k, v in factor_scores.items()
        }

        results.append({
            "rank": 0,  # placeholder, set after sorting
            "speaker_name": speaker_name,
            "speaker_title": str(speaker.get("Title", "")),
            "speaker_company": str(speaker.get("Company", "")),
            "speaker_board_role": str(speaker.get("Board Role", "")),
            "speaker_metro_region": str(speaker.get("Metro Region", "")),
            "speaker_expertise_tags": str(speaker.get("Expertise Tags", "")),
            "event_name": str(event.get("Event / Program", "")),
            "total_score": round(total_score, 4),
            "factor_scores": {k: round(v, 4) for k, v in factor_scores.items()},
            "weighted_factor_scores": weighted_factors,
        })

    # Sort descending by total_score, then by speaker_name for stable ordering
    results.sort(key=lambda x: (-x["total_score"], x["speaker_name"]))

    # Assign ranks and truncate
    for i, result in enumerate(results[:top_n]):
        result["rank"] = i + 1

    return results[:top_n]
```

#### 2. Course-Based Ranking Variant

```python
def rank_speakers_for_course(
    course: pd.Series,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    course_embedding: np.ndarray | None = None,
    ia_event_calendar: pd.DataFrame | None = None,
    weights: dict[str, float] | None = None,
    top_n: int = 3,
    conversion_overrides: dict[str, float] | None = None,
) -> list[dict]:
    """
    Rank speakers for a course section (guest lecture matching).

    This is a thin wrapper around compute_match_score that adapts
    the course row to look like an event row for scoring purposes.

    Args:
        course: A single row from data_cpp_course_schedule.csv.
            Keys: "Instructor", "Course", "Section", "Title", "Days",
            "Start Time", "End Time", "Enrl Cap", "Mode",
            "Guest Lecture Fit"
        speakers, speaker_embeddings, ia_event_calendar, weights,
        top_n, conversion_overrides: Same as rank_speakers_for_event.

    Returns:
        Same structure as rank_speakers_for_event, but with course-specific
        fields:
        - "event_name" is replaced with course title:
          f"{course['Course']}-{course['Section']}: {course['Title']}"
        - "factor_scores" still has all 6 factors, but:
          - role_fit defaults to 0.7 for courses (all board members are
            qualified guest lecturers at a university)
          - student_interest is set based on Guest Lecture Fit:
            High -> 0.9, Medium -> 0.6, Low -> 0.3

    Adaptation mapping (course -> event-like Series for scoring):
        course["Title"]            -> event["Event / Program"]
        "Guest speaker"            -> event["Volunteer Roles (fit)"]
        "Students"                 -> event["Primary Audience"]
        "Los Angeles — East"       -> event["Region"]  (all CPP courses)
        "Recurring each term/year" -> event["Recurrence (typical)"]
        course["Guest Lecture Fit"] mapped to category -> event["Category"]
    """
    # Build an event-like Series from the course row
    guest_fit = str(course.get("Guest Lecture Fit", "Medium")).strip()
    fit_to_category = {
        "High": "Research showcase",      # maps to 0.60 interest
        "Medium": "Career services",      # maps to 0.70 interest
        "Low": "Career services",         # maps to 0.70 interest
    }

    course_title = (
        f"{course.get('Course', '')}-{course.get('Section', '')}: "
        f"{course.get('Title', '')}"
    )

    event_proxy = pd.Series({
        "Event / Program": course_title,
        "Category": fit_to_category.get(guest_fit, "Career services"),
        "Volunteer Roles (fit)": "Guest speaker",
        "Primary Audience": "Students",
        "Region": "Los Angeles — East",
        "Recurrence (typical)": "Recurring each term/year",
    })

    results = rank_speakers_for_event(
        event=event_proxy,
        speakers=speakers,
        speaker_embeddings=speaker_embeddings,
        event_embedding=course_embedding,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=top_n,
        conversion_overrides=conversion_overrides,
    )

    # Override event_name with course-specific format
    for r in results:
        r["event_name"] = course_title
        # Override student_interest based on Guest Lecture Fit directly
        fit_map = {"High": 0.9, "Medium": 0.6, "Low": 0.3}
        r["factor_scores"]["student_interest"] = fit_map.get(guest_fit, 0.5)

    return results
```

### Acceptance Criteria

- [ ] `rank_speakers_for_event()` returns a list of exactly `top_n` dicts (or fewer if fewer speakers exist)
- [ ] Results are sorted by `total_score` descending
- [ ] Each result dict contains all fields specified: rank, speaker_name, speaker_title, speaker_company, speaker_board_role, speaker_metro_region, speaker_expertise_tags, event_name, total_score, factor_scores, weighted_factor_scores
- [ ] Ranks are 1-indexed and consecutive
- [ ] `rank_speakers_for_course()` successfully adapts course data to event-like format
- [ ] `rank_speakers_for_course()` only runs for courses with `Guest Lecture Fit != "Low"` (filtering happens at call site, but the function itself works for any course)
- [ ] Running ranking for all 15 events produces 15 x 3 = 45 match entries without errors
- [ ] Running ranking for all 10 High-fit courses produces 10 x 3 = 30 match entries without errors

### Harness Guidelines

- Both functions live in `src/matching/engine.py` alongside `compute_match_score`
- The `speaker_embeddings` dict key must be the speaker "Name" string exactly as it appears in the CSV
- `weighted_factor_scores` values should be rounded to 4 decimal places for display clarity
- Sort stability: when two speakers have identical total_score, sort alphabetically by speaker_name

### Steer Guidelines

- The coding agent may want to vectorize the scoring across all speakers using numpy broadcasting. This is acceptable only if the per-factor breakdown dict is still produced for each speaker-event pair. The UI needs per-factor scores for radar charts.
- If the agent caches ranking results in session state, that is acceptable and encouraged for performance
- The `top_n` parameter must be honored -- do not return all 18 speakers and let the UI truncate

---

## A1.3: Match Explanation Cards (3.0h)

### Specification

**File:** `src/matching/explanations.py`

#### 1. Prompt Template

```python
"""
LLM-powered match explanation card generation.
Uses Gemini `gemini-2.5-flash-lite` to produce 2-3 sentence natural language explanations
of why a speaker was matched to an event.
"""

import hashlib
import json
import os
from pathlib import Path

from gemini import Gemini

from src.config import (
    EXPLANATION_CACHE_DIR,
    EXPLANATION_MAX_TOKENS,
    EXPLANATION_MODEL,
    EXPLANATION_TEMPERATURE,
)

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
- Overall Match Score: {total_score:.0%}
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


def _cache_key(speaker_name: str, event_name: str, total_score: float) -> str:
    """
    Generate a deterministic cache key for an explanation.

    The key includes the total_score so that explanations are regenerated
    when weight tuning changes the scores. Score is rounded to 2 decimal
    places to avoid excessive cache misses from floating point noise.

    Returns:
        A filesystem-safe string like "travis_miller__ai_hackathon__087"
    """
    raw = f"{speaker_name}__{event_name}__{total_score:.2f}"
    safe = raw.lower().replace(" ", "_").replace("/", "_").replace("—", "_")
    # Truncate to avoid filesystem path length issues, add hash suffix
    if len(safe) > 100:
        hash_suffix = hashlib.md5(raw.encode()).hexdigest()[:8]
        safe = safe[:92] + "__" + hash_suffix
    return safe


def load_cached_explanation(
    speaker_name: str,
    event_name: str,
    total_score: float,
) -> str | None:
    """
    Load a previously cached explanation from disk.

    Args:
        speaker_name: Speaker full name.
        event_name: Event name.
        total_score: Current match score (rounded to 2dp for cache lookup).

    Returns:
        The cached explanation string, or None if not found.
    """
    cache_dir = Path(EXPLANATION_CACHE_DIR)
    key = _cache_key(speaker_name, event_name, total_score)
    cache_file = cache_dir / f"{key}.json"

    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            return data.get("explanation", None)
        except (json.JSONDecodeError, KeyError):
            return None
    return None


def save_cached_explanation(
    speaker_name: str,
    event_name: str,
    total_score: float,
    explanation: str,
) -> None:
    """Save an explanation to the disk cache."""
    cache_dir = Path(EXPLANATION_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)

    key = _cache_key(speaker_name, event_name, total_score)
    cache_file = cache_dir / f"{key}.json"

    data = {
        "speaker_name": speaker_name,
        "event_name": event_name,
        "total_score": round(total_score, 4),
        "explanation": explanation,
    }
    cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_match_explanation(
    match_result: dict,
    event_category: str = "",
    event_volunteer_roles: str = "",
    event_audience: str = "",
    use_cache: bool = True,
) -> str:
    """
    Generate a natural language explanation for a match result.

    Checks the disk cache first. If no cached explanation exists,
    calls Gemini `gemini-2.5-flash-lite` with the few-shot prompt template.

    Args:
        match_result: A single dict from rank_speakers_for_event() output.
            Required keys: speaker_name, speaker_title, speaker_company,
            speaker_board_role, speaker_metro_region, speaker_expertise_tags,
            event_name, total_score, factor_scores.
        event_category: Event category string for the prompt.
        event_volunteer_roles: Semicolon-separated volunteer roles.
        event_audience: Primary audience string.
        use_cache: Whether to check/write the disk cache. Default True.

    Returns:
        A 2-3 sentence explanation string.

    Error handling:
        - Gemini API timeout (>10s) -> return fallback explanation
        - Gemini API error -> return fallback explanation
        - Empty response -> return fallback explanation
    """
    speaker_name = match_result["speaker_name"]
    event_name = match_result["event_name"]
    total_score = match_result["total_score"]
    factor_scores = match_result["factor_scores"]

    # Check cache
    if use_cache:
        cached = load_cached_explanation(speaker_name, event_name, total_score)
        if cached:
            return cached

    # Build the user message
    user_message = EXPLANATION_USER_TEMPLATE.format(
        speaker_name=speaker_name,
        speaker_title=match_result["speaker_title"],
        speaker_company=match_result["speaker_company"],
        speaker_board_role=match_result["speaker_board_role"],
        speaker_metro_region=match_result["speaker_metro_region"],
        speaker_expertise_tags=match_result["speaker_expertise_tags"],
        event_name=event_name,
        event_category=event_category,
        event_volunteer_roles=event_volunteer_roles,
        event_audience=event_audience,
        total_score=total_score,
        topic_relevance=factor_scores.get("topic_relevance", 0.0),
        role_fit=factor_scores.get("role_fit", 0.0),
        geographic_proximity=factor_scores.get("geographic_proximity", 0.0),
        calendar_fit=factor_scores.get("calendar_fit", 0.0),
        historical_conversion=factor_scores.get("historical_conversion", 0.0),
        student_interest=factor_scores.get("student_interest", 0.0),
    )

    # Build messages array with few-shot examples
    messages = [
        {"role": "system", "content": EXPLANATION_SYSTEM_PROMPT},
        *FEW_SHOT_EXAMPLES,
        {"role": "user", "content": user_message},
    ]

    # Call Gemini API
    fallback = _fallback_explanation(match_result)
    try:
        client = Gemini()  # uses GEMINI_API_KEY from environment
        response = client.chat.completions.create(
            model=EXPLANATION_MODEL,
            messages=messages,
            max_tokens=EXPLANATION_MAX_TOKENS,
            temperature=EXPLANATION_TEMPERATURE,
            timeout=10.0,
        )
        explanation = response.choices[0].message.content.strip()
        if not explanation:
            explanation = fallback
    except Exception:
        explanation = fallback

    # Cache the result
    if use_cache:
        save_cached_explanation(speaker_name, event_name, total_score, explanation)

    return explanation


def _fallback_explanation(match_result: dict) -> str:
    """
    Generate a template-based fallback explanation when the LLM is unavailable.

    This ensures the UI always has something to display even if the
    Gemini API is down or times out.
    """
    fs = match_result["factor_scores"]
    # Find the top 2 factors
    sorted_factors = sorted(fs.items(), key=lambda x: x[1], reverse=True)
    top1_name, top1_score = sorted_factors[0]
    top2_name, top2_score = sorted_factors[1]

    factor_labels = {
        "topic_relevance": "topic alignment",
        "role_fit": "role compatibility",
        "geographic_proximity": "geographic proximity",
        "calendar_fit": "calendar alignment",
        "historical_conversion": "engagement history",
        "student_interest": "student interest potential",
    }

    return (
        f"{match_result['speaker_name']} ({match_result['speaker_title']}, "
        f"{match_result['speaker_company']}) is recommended for "
        f"{match_result['event_name']} based on strong "
        f"{factor_labels.get(top1_name, top1_name)} ({top1_score:.2f}) and "
        f"{factor_labels.get(top2_name, top2_name)} ({top2_score:.2f}), "
        f"with an overall match score of {match_result['total_score']:.0%}."
    )
```

#### 2. Cache Structure

Cache directory: `cache/explanations/`

Each cached explanation is a JSON file:

```
cache/explanations/
  travis_miller__ai_for_a_better_future_hackathon__087.json
  rob_kaiser__swift_tech_symposium__082.json
  ...
```

JSON file format:
```json
{
  "speaker_name": "Travis Miller",
  "event_name": "AI for a Better Future Hackathon",
  "total_score": 0.8700,
  "explanation": "Travis Miller (SVP Sales & Client Development, PureSpectrum) is a strong match..."
}
```

### Acceptance Criteria

- [ ] `generate_match_explanation()` returns a non-empty string for any valid match_result dict
- [ ] Prompt includes system message, 2 few-shot examples, and the formatted user message
- [ ] Cache hit skips the API call and returns the cached explanation
- [ ] Cache key includes the total_score (rounded to 2dp) so explanations regenerate when weights change
- [ ] API timeout (>10s) produces a fallback explanation (not an error)
- [ ] API error produces a fallback explanation (not an error)
- [ ] Fallback explanation names the top 2 scoring factors with their numeric scores
- [ ] Cache directory is created automatically if it does not exist
- [ ] Explanation text is 2-3 sentences (validated by character count: 100-500 chars typical)
- [ ] No secrets are logged or printed during API calls

### Harness Guidelines

- All explanation logic lives in `src/matching/explanations.py`
- Cache files go in `cache/explanations/` relative to project root
- The Gemini client is instantiated inside the function (not at module level) to defer API key validation
- Use `gemini.Gemini()` (v1.x client), not the legacy `gemini.ChatCompletion.create()`

### Steer Guidelines

- If the coding agent tries to call `generate_match_explanation()` synchronously during ranking (A1.2), redirect -- explanations should be generated lazily when the user views a match card, not during bulk ranking
- The few-shot examples must use real speaker names from the data (Travis Miller, Rob Kaiser) to demonstrate the expected output quality
- If the agent omits the fallback, require it -- the demo must never show an error where an explanation should be
- Temperature should be low (0.3-0.5) to keep explanations factual and deterministic

---

## A1.4: Matches Tab UI (5.0h)

### Specification

**File:** `src/ui/matches_tab.py`
**Modify:** `src/app.py` (wire the tab)

#### 1. UI Wireframe (ASCII)

```
+======================================================================+
|                        IA SmartMatch CRM                             |
|======================================================================|
| SIDEBAR                | MAIN CONTENT AREA                          |
|                        |                                             |
| [IA West Logo]         |  [ Matches ]  [ Discovery ]  [ Pipeline ]  |
|                        |                                             |
| --- Match Weights ---  |  Event: [  AI for a Better Future Hacka.. v]|
|                        |                                             |
| Topic Relevance        |  Showing top 3 matches for:                 |
| [====|======] 0.30     |  "AI for a Better Future Hackathon"         |
|                        |                                             |
| Role Fit               |  +------------------------------------------+
| [===|=======] 0.25     |  | #1  Travis Miller            Score: 87% |
|                        |  | SVP, Sales & Client Dev  | PureSpectrum |
| Geographic Proximity   |  | Ventura / Thousand Oaks  | President    |
| [==|========] 0.20     |  |                                          |
|                        |  |  +--- Radar Chart ---+  +-- Explain ---+ |
| Calendar Fit           |  |  |    Topic: 0.85    |  | Travis Miller |
| [=|=========] 0.15     |  |  |   Role: 0.80      |  | is a strong   |
|                        |  |  | Geo: 0.75         |  | match for the |
| Hist. Conversion       |  |  | Calendar: 0.70    |  | AI Hackathon  |
| [|==========] 0.05     |  |  | Hist: 0.50        |  | because...    |
|                        |  |  | Student: 0.95     |  +---------------+|
| Student Interest       |  |  +-------------------+                   |
| [|==========] 0.05     |  |                                          |
|                        |  |  [ Generate Email ]  [ Generate .ics ]   |
| --- View Mode ---      |  +------------------------------------------+
| ( ) Events             |                                             |
| ( ) Courses            |  +------------------------------------------+
|                        |  | #2  Rob Kaiser                Score: 82% |
| --- Filters ---        |  | Marketing Science Leader | PSB          |
| [x] High-fit courses   |  | LA — Long Beach | Treasurer              |
| [ ] Medium-fit courses |  |  ... (same card layout) ...              |
| [ ] Show all speakers  |  +------------------------------------------+
|                        |                                             |
|                        |  +------------------------------------------+
|                        |  | #3  Katrina Noelle          Score: 78%   |
|                        |  | Founder & CEO | KNow Research            |
|                        |  | San Francisco | Treasurer Elect          |
|                        |  |  ... (same card layout) ...              |
|                        |  +------------------------------------------+
+======================================================================+
```

#### 2. Streamlit Component Structure

```python
"""
Matches tab UI component for IA SmartMatch CRM.
"""

import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

from src.config import DEFAULT_WEIGHTS
from src.matching.engine import rank_speakers_for_event, rank_speakers_for_course
from src.matching.explanations import generate_match_explanation


def render_matches_tab(
    events: pd.DataFrame,
    courses: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """
    Render the Matches tab in the Streamlit app.

    This function is called from app.py when the user selects the Matches tab.
    It manages its own session state for weights, selected event, and cached
    results.

    Args:
        events: DataFrame from data_cpp_events_contacts.csv (15 rows).
        courses: DataFrame from data_cpp_course_schedule.csv (35 rows).
        speakers: DataFrame from data_speaker_profiles.csv (18 rows).
        speaker_embeddings: Dict mapping speaker name -> embedding array.
        event_embeddings: Dict mapping event name -> embedding array.
        course_embeddings: Dict mapping course key -> embedding array.
        ia_event_calendar: DataFrame from data_event_calendar.csv (9 rows).
    """

    # --- Sidebar: Weight Sliders ---
    _render_weight_sliders()

    # --- Sidebar: View Mode ---
    view_mode = st.sidebar.radio(
        "View Mode",
        options=["Events", "Courses"],
        index=0,
        key="matches_view_mode",
    )

    if view_mode == "Events":
        _render_event_matches(
            events, speakers, speaker_embeddings, event_embeddings,
            ia_event_calendar,
        )
    else:
        _render_course_matches(
            courses, speakers, speaker_embeddings, course_embeddings,
            ia_event_calendar,
        )


def _render_weight_sliders() -> None:
    """
    Render 6 weight-tuning sliders in the sidebar.

    Sliders use st.slider with step=0.05, min=0.0, max=1.0.
    When any slider changes, st.rerun() is triggered via the
    on_change callback to recompute rankings.

    Weights are stored in st.session_state["match_weights"].
    """
    st.sidebar.markdown("### Match Weights")
    st.sidebar.caption("Adjust weights to change ranking priorities. Weights are normalized automatically.")

    factor_labels = {
        "topic_relevance": "Topic Relevance",
        "role_fit": "Role Fit",
        "geographic_proximity": "Geographic Proximity",
        "calendar_fit": "Calendar Fit",
        "historical_conversion": "Historical Conversion",
        "student_interest": "Student Interest",
    }

    # Initialize weights in session state if not present
    if "match_weights" not in st.session_state:
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)

    for factor_key, label in factor_labels.items():
        current_val = st.session_state["match_weights"].get(
            factor_key, DEFAULT_WEIGHTS[factor_key]
        )
        new_val = st.sidebar.slider(
            label,
            min_value=0.0,
            max_value=1.0,
            value=current_val,
            step=0.05,
            key=f"slider_{factor_key}",
        )
        st.session_state["match_weights"][factor_key] = new_val

    # Display normalized weights summary
    w = st.session_state["match_weights"]
    total = sum(w.values())
    if total > 0:
        st.sidebar.markdown("---")
        st.sidebar.caption("Normalized weights:")
        for k, v in w.items():
            normalized = v / total
            st.sidebar.text(f"  {factor_labels[k]}: {normalized:.0%}")
    else:
        st.sidebar.warning("All weights are zero. Scores will be 0.0.")

    # Reset button
    if st.sidebar.button("Reset to Defaults", key="reset_weights"):
        st.session_state["match_weights"] = dict(DEFAULT_WEIGHTS)
        st.rerun()


def _render_event_matches(
    events: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render the event-based matching view."""

    # Event selector dropdown
    event_names = events["Event / Program"].tolist()
    selected_event_name = st.selectbox(
        "Select an Event",
        options=event_names,
        index=0,
        key="selected_event",
    )

    # Get the selected event row
    selected_event = events[
        events["Event / Program"] == selected_event_name
    ].iloc[0]

    st.markdown(f"### Top 3 Matches for: *{selected_event_name}*")

    # Get current weights from session state
    weights = st.session_state.get("match_weights", DEFAULT_WEIGHTS)

    # Get event embedding
    event_emb = event_embeddings.get(selected_event_name, None)

    # Compute rankings
    top_matches = rank_speakers_for_event(
        event=selected_event,
        speakers=speakers,
        speaker_embeddings=speaker_embeddings,
        event_embedding=event_emb,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=3,
    )

    # Render match cards
    for match in top_matches:
        _render_match_card(
            match=match,
            event=selected_event,
        )


def _render_course_matches(
    courses: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    course_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
) -> None:
    """Render the course-based matching view (guest lectures)."""

    # Sidebar filters
    show_high = st.sidebar.checkbox("High-fit courses", value=True, key="filter_high")
    show_medium = st.sidebar.checkbox("Medium-fit courses", value=False, key="filter_medium")

    # Filter courses
    fit_values = []
    if show_high:
        fit_values.append("High")
    if show_medium:
        fit_values.append("Medium")

    if not fit_values:
        st.info("Select at least one course fit level in the sidebar.")
        return

    filtered_courses = courses[courses["Guest Lecture Fit"].isin(fit_values)]
    st.markdown(f"**{len(filtered_courses)} courses** matching filter criteria")

    # Course selector
    course_labels = [
        f"{row['Course']}-{row['Section']}: {row['Title']} ({row['Guest Lecture Fit']})"
        for _, row in filtered_courses.iterrows()
    ]
    if not course_labels:
        st.info("No courses match the selected filters.")
        return

    selected_label = st.selectbox(
        "Select a Course Section",
        options=course_labels,
        index=0,
        key="selected_course",
    )

    # Find the selected course row
    selected_idx = course_labels.index(selected_label)
    selected_course = filtered_courses.iloc[selected_idx]

    course_key = f"{selected_course['Course']}-{selected_course['Section']}"
    st.markdown(f"### Top 3 Guest Lecture Matches: *{selected_label}*")

    weights = st.session_state.get("match_weights", DEFAULT_WEIGHTS)
    course_emb = course_embeddings.get(course_key, None)

    top_matches = rank_speakers_for_course(
        course=selected_course,
        speakers=speakers,
        speaker_embeddings=speaker_embeddings,
        course_embedding=course_emb,
        ia_event_calendar=ia_event_calendar,
        weights=weights,
        top_n=3,
    )

    for match in top_matches:
        _render_match_card(
            match=match,
            event=pd.Series({
                "Category": "",
                "Volunteer Roles (fit)": "Guest speaker",
                "Primary Audience": "Students",
            }),
        )


def _render_match_card(
    match: dict,
    event: pd.Series,
) -> None:
    """
    Render a single match card with radar chart and explanation.

    Layout within each card:
    +-------------------------------------------------+
    | #1  Speaker Name                    Score: 87%  |
    | Title | Company                                 |
    | Metro Region | Board Role                       |
    |                                                 |
    |  [Radar Chart (left col)]  [Explanation (right)]|
    |                                                 |
    |  [Generate Email]  [Generate .ics]              |
    +-------------------------------------------------+
    """
    score_pct = f"{match['total_score']:.0%}"
    rank = match["rank"]

    with st.container():
        st.markdown("---")

        # Header row
        col_rank, col_info, col_score = st.columns([1, 6, 2])
        with col_rank:
            st.markdown(f"### #{rank}")
        with col_info:
            st.markdown(f"**{match['speaker_name']}**")
            st.caption(
                f"{match['speaker_title']} | {match['speaker_company']}  \n"
                f"{match['speaker_metro_region']} | {match['speaker_board_role']}"
            )
        with col_score:
            st.metric(label="Match Score", value=score_pct)

        # Radar chart + Explanation
        col_chart, col_explain = st.columns([1, 1])

        with col_chart:
            fig = _create_radar_chart(match["factor_scores"])
            st.plotly_chart(fig, use_container_width=True, key=f"radar_{rank}_{match['speaker_name']}")

        with col_explain:
            # Lazy-load explanation (generates on first view, caches thereafter)
            explanation = generate_match_explanation(
                match_result=match,
                event_category=str(event.get("Category", "")),
                event_volunteer_roles=str(event.get("Volunteer Roles (fit)", "")),
                event_audience=str(event.get("Primary Audience", "")),
            )
            st.markdown("**Why this match?**")
            st.info(explanation)

        # Action buttons
        col_email, col_ics, col_spacer = st.columns([2, 2, 4])
        with col_email:
            st.button(
                "Generate Email",
                key=f"email_{rank}_{match['speaker_name']}",
                # Email generation is Sprint 2 (A2.4).
                # For now, store the match in session state for later use.
                on_click=lambda m=match: st.session_state.update(
                    {"pending_email_match": m}
                ),
            )
        with col_ics:
            st.button(
                "Generate .ics",
                key=f"ics_{rank}_{match['speaker_name']}",
                disabled=True,  # Enabled in Sprint 2 (A2.5)
            )


def _create_radar_chart(factor_scores: dict[str, float]) -> go.Figure:
    """
    Create a Plotly radar (polar/spider) chart for the 6 match factors.

    Args:
        factor_scores: Dict of factor_name -> score (0.0 to 1.0).

    Returns:
        A Plotly go.Figure configured as a radar chart.

    Plotly configuration:
        - go.Scatterpolar trace with fill='toself'
        - 6 radial axes, one per factor
        - Radial range: [0, 1]
        - Angular labels: short factor names
        - Fill color: rgba(49, 130, 189, 0.3)  (IA-style blue, 30% opacity)
        - Line color: rgba(49, 130, 189, 1.0)
        - Compact layout: 280px height, minimal margins
    """
    # Factor display order and labels
    factor_order = [
        "topic_relevance",
        "role_fit",
        "geographic_proximity",
        "calendar_fit",
        "historical_conversion",
        "student_interest",
    ]
    display_labels = [
        "Topic",
        "Role Fit",
        "Proximity",
        "Calendar",
        "History",
        "Student Int.",
    ]

    values = [factor_scores.get(f, 0.0) for f in factor_order]
    # Close the polygon by repeating the first value
    values_closed = values + [values[0]]
    labels_closed = display_labels + [display_labels[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill="toself",
        fillcolor="rgba(49, 130, 189, 0.3)",
        line=dict(color="rgba(49, 130, 189, 1.0)", width=2),
        marker=dict(size=6, color="rgba(49, 130, 189, 1.0)"),
        name="Match Factors",
        hovertemplate="%{theta}: %{r:.2f}<extra></extra>",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickvals=[0.0, 0.25, 0.50, 0.75, 1.0],
                ticktext=["0", "0.25", "0.50", "0.75", "1.0"],
                tickfont=dict(size=9),
            ),
            angularaxis=dict(
                tickfont=dict(size=11),
            ),
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=20, b=20),
        height=280,
    )

    return fig
```

#### 3. App.py Integration

In `src/app.py`, add the following to the Matches tab section:

```python
# Inside the Matches tab callback:
from src.ui.matches_tab import render_matches_tab

with tab_matches:
    render_matches_tab(
        events=events_df,
        courses=courses_df,
        speakers=speakers_df,
        speaker_embeddings=speaker_embeddings,
        event_embeddings=event_embeddings,
        course_embeddings=course_embeddings,
        ia_event_calendar=ia_calendar_df,
    )
```

### Acceptance Criteria

- [ ] Matches tab renders without errors when selected
- [ ] Event selector dropdown shows all 15 events from data_cpp_events_contacts.csv
- [ ] Selecting a different event shows different top-3 matches
- [ ] Each match card displays: rank, name, title, company, metro region, board role, match score percentage
- [ ] Radar chart renders with 6 axes and correct factor scores
- [ ] Radar chart uses `go.Scatterpolar` with `fill='toself'`
- [ ] Explanation card displays 2-3 sentence explanation text
- [ ] "Generate Email" button is present and clickable (stores match in session state)
- [ ] Weight sliders appear in sidebar with correct default values
- [ ] Moving any weight slider triggers score recomputation and UI update
- [ ] "Reset to Defaults" button restores DEFAULT_WEIGHTS
- [ ] "Courses" view mode shows course selector with High-fit filter active by default
- [ ] Normalized weight summary appears below sliders
- [ ] No crashes when switching between Events and Courses views rapidly

### Harness Guidelines

- UI components live in `src/ui/matches_tab.py`
- Session state keys: `match_weights`, `matches_view_mode`, `selected_event`, `selected_course`, `filter_high`, `filter_medium`, `pending_email_match`
- Radar chart height: 280px (compact to fit 3 cards on screen)
- Use `st.container()` to group each match card for clean visual separation
- Use `st.columns([1, 6, 2])` for the card header layout

### Steer Guidelines

- Weight sliders MUST use `st.slider` (not `st.number_input`) for intuitive UX
- Radar chart MUST use `go.Scatterpolar` (not `px.line_polar`) for full customization
- The "Generate .ics" button should be `disabled=True` in Sprint 1 -- it is enabled in Sprint 2 (A2.5)
- Handle the case where `event_embeddings` returns None for a given event key (use topic_relevance = 0.0)
- If the agent tries to add authentication or login, reject -- this is a hackathon demo
- Explanation cards should load lazily (only when the card is visible), not all at once during page load. This avoids unnecessary API calls and improves load time.

---

## A1.5: Course Matching Integration (2.5h)

### Specification

**File:** `src/matching/engine.py` (the `rank_speakers_for_course` function from A1.2)
**File:** `src/ui/matches_tab.py` (the `_render_course_matches` function from A1.4)

This task connects the course matching logic (already specified in A1.2 and A1.4) to the actual data and verifies it works end-to-end.

#### 1. High-Fit Course Filtering

From `data_cpp_course_schedule.csv`, the 10 High-fit sections are:

| # | Instructor | Course-Section | Title | Guest Lecture Fit |
|---|-----------|----------------|-------|-------------------|
| 1 | Chie Ishihara | IBM 4121-01 | Intl Marketing Research | High |
| 2 | Megan Good | IBM 3302-02 | Marketing Research | High |
| 3 | Yufan Lin | IBM 3302-03 | Marketing Research | High |
| 4 | Yufan Lin | GBA 6520-02 | Marketing Mgmt Applications | High |
| 5 | Maha Ghosn | GBA 6830-01 | Business Research Methods | High |
| 6 | Maha Ghosn | IBM 3202-03 | Market Analysis and Control | High |
| 7 | Maha Ghosn | IBM 3202-04 | Market Analysis and Control | High |
| 8 | Olga Di Franco | IBM 4112-01 | Consumer Behavior | High |
| 9 | Olga Di Franco | IBM 4112-02 | Consumer Behavior | High |
| 10 | L. Lin Ong | IBM 4112-04 | Consumer Behavior | High |

#### 2. Course Embedding Composition

Course embeddings (generated in Sprint 0, A0.4) use the following text composition:

```python
course_embedding_text = f"{title} {guest_lecture_fit}"
# Example: "Intl Marketing Research High"
# Example: "Consumer Behavior High"
```

The course embedding dict key format is `"{Course}-{Section}"`, e.g. `"IBM 4121-01"`.

#### 3. Course-Specific Matching Considerations

- All CPP courses are in `"Los Angeles -- East"` region, so `geographic_proximity` heavily favors LA-area speakers. This is expected and correct behavior.
- `role_fit` for all courses is based on the generic "Guest speaker" role, so all board members with director+ titles get a baseline role_fit of ~0.7. Differentiation comes primarily from `topic_relevance`.
- Dr. Yufan Lin (Director of New Professionals) teaches 2 of the 10 High-fit courses (IBM 3302-03, GBA 6520-02). The matching engine should NOT exclude the instructor from their own course matches -- the system treats all speakers equally. (In a production system, you would add an exclusion rule, but for the hackathon demo this is fine.)

### Acceptance Criteria

- [ ] Course view mode shows exactly 10 sections when "High-fit courses" filter is checked
- [ ] Course view mode shows 17 additional sections when "Medium-fit courses" is also checked
- [ ] Each course shows top-3 speaker matches with the same card layout as event matches
- [ ] Course title in match card uses format: `"IBM 4121-01: Intl Marketing Research"`
- [ ] Switching between Events and Courses view modes does not lose weight slider state
- [ ] `rank_speakers_for_course()` produces different top-3 rankings for different course topics (e.g., Consumer Behavior vs. Marketing Research vs. Business Research Methods)

### Harness Guidelines

- Course filtering logic (`Guest Lecture Fit == "High"`) lives in `_render_course_matches()` in the UI layer, not in the engine
- The engine function `rank_speakers_for_course()` works for ANY course regardless of fit level -- the UI decides what to show
- Course embedding dict uses `"{Course}-{Section}"` as key (e.g., `"IBM 4121-01"`)

### Steer Guidelines

- Do NOT build a separate "Course Matching" tab -- courses are a sub-view within the Matches tab, toggled by the sidebar radio button
- The "Generate Email" button on course match cards should work identically to event match cards (same session state storage)
- If the coding agent adds a "schedule conflict" check (comparing course times to speaker availability), that is nice-to-have but not required for Sprint 1

---

## A1.6: Pipeline Sample Data (2.0h)

### Specification

**File:** `src/matching/engine.py` (add helper function)
**Output:** `data/pipeline_sample_data.csv`

#### 1. Pipeline Generation Function

```python
def generate_pipeline_data(
    events: pd.DataFrame,
    speakers: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embeddings: dict[str, np.ndarray],
    ia_event_calendar: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Generate the pipeline sample data from actual match results.

    Takes the real match results from rank_speakers_for_event() and
    simulates downstream pipeline stages with realistic conversion rates.

    Pipeline stages and conversion rates (from nonprofit volunteer data):
        1. Scored:       270 pairs (18 speakers x 15 events, all scored)
        2. Matched:      45 entries (top-3 per event, 15 events x 3)
        3. Contacted:    36 entries (80% of matched -- outreach email sent)
        4. Confirmed:    16 entries (45% of contacted -- speaker accepts)
        5. Attended:     12 entries (75% of confirmed -- speaker attends)
        6. Member Inq.:   2 entries (15% of attended -- student membership inquiry)

    Conversion rate sources:
        - 80% contact rate: ASAE benchmark for personalized association outreach
        - 45% confirmation: IA West estimates for volunteer acceptance
        - 75% attendance: industry standard for confirmed volunteer events
        - 15% member inquiry: aggressive but defensible for high-quality touchpoints

    Args:
        events, speakers, speaker_embeddings, event_embeddings,
        ia_event_calendar, weights: Same as rank_speakers_for_event.

    Returns:
        DataFrame with columns:
        - event_name: str
        - speaker_name: str
        - match_score: float
        - rank: int (1-3)
        - stage: str (one of: "Matched", "Contacted", "Confirmed",
                      "Attended", "Member Inquiry")
        - stage_order: int (1-5, for funnel ordering)

    Implementation:
        1. For each event, call rank_speakers_for_event(top_n=3).
        2. All top-3 are stage="Matched" (45 entries).
        3. Randomly select 80% as "Contacted" (seed=42 for reproducibility).
        4. Of contacted, randomly select 45% as "Confirmed".
        5. Of confirmed, randomly select 75% as "Attended".
        6. Of attended, randomly select 15% as "Member Inquiry".
        7. Each entry gets the DEEPEST stage it reaches
           (a "Confirmed" speaker is also Matched and Contacted).
    """
```

#### 2. Output CSV Schema (`data/pipeline_sample_data.csv`)

```csv
event_name,speaker_name,match_score,rank,stage,stage_order
AI for a Better Future Hackathon,Travis Miller,0.87,1,Attended,4
AI for a Better Future Hackathon,Rob Kaiser,0.82,2,Confirmed,3
AI for a Better Future Hackathon,Katrina Noelle,0.78,3,Contacted,2
Information Technology Competition (ITC),Amanda Keller-Grill,0.79,1,Confirmed,3
...
```

#### 3. Funnel Summary (expected output)

| Stage | Count | Rate | Cumulative % |
|-------|-------|------|-------------|
| Matched | 45 | -- | 100% |
| Contacted | ~36 | 80% of matched | 80% |
| Confirmed | ~16 | 45% of contacted | 36% |
| Attended | ~12 | 75% of confirmed | 27% |
| Member Inquiry | ~2 | 15% of attended | 4% |

(Exact counts will vary slightly due to random selection with seed=42)

### Acceptance Criteria

- [ ] `pipeline_sample_data.csv` is generated and saved to `data/` directory
- [ ] CSV contains all required columns: event_name, speaker_name, match_score, rank, stage, stage_order
- [ ] All 45 matched entries (15 events x top-3) are present
- [ ] Stage assignments use the specified conversion rates (80%, 45%, 75%, 15%)
- [ ] Random selection uses `seed=42` for reproducibility across runs
- [ ] `match_score` values are the actual scores from the matching engine, not fabricated
- [ ] `speaker_name` and `event_name` values are real names from the CSVs
- [ ] Pipeline data is self-consistent (every "Attended" entry also has Matched + Contacted + Confirmed stages implicitly)

### Harness Guidelines

- The generation function lives in `src/matching/engine.py`
- Output file goes to `data/pipeline_sample_data.csv`
- Use `numpy.random.seed(42)` or `random.seed(42)` for reproducible stage assignments
- This CSV feeds the Pipeline tab (Sprint 2, A2.6) and Track B's Growth Strategy

### Steer Guidelines

- The coding agent may be tempted to create a more complex simulation with per-stage timestamps or funnel IDs -- reject this scope creep. The simple flat CSV with `stage` and `stage_order` columns is sufficient.
- The stage column records only the DEEPEST stage reached. The Pipeline tab (Sprint 2) will compute funnel counts by counting entries at each stage_order or deeper.
- If the agent uses non-deterministic randomness (no seed), require the seed for demo reproducibility

---

## A1.7: University Scraping Research (2.0h)

### Specification

**Output:** `docs/scraping_research.md`

This is a research task, not a coding task. The output is a structured document that Sprint 2 (A2.1) will use to build the web scraping pipeline.

#### 1. Target Universities

| # | University | Event Page URL | Region |
|---|-----------|----------------|--------|
| 1 | UCLA | https://career.ucla.edu/events/ | Los Angeles |
| 2 | SDSU | https://www.sdsu.edu/events-calendar | San Diego |
| 3 | UC Davis | https://careercenter.ucdavis.edu/career-center-services/career-fairs | San Francisco (nearby) |
| 4 | USC | https://careers.usc.edu/events/ | Los Angeles |
| 5 | Portland State | (TBD -- research during this task) | Portland |

#### 2. Test Matrix

For each university, document the following:

```markdown
### [University Name]

**URL:** [URL]
**robots.txt check:** [Allowed / Disallowed / No robots.txt]
**Rendering method:** [Static HTML (BeautifulSoup) / Dynamic JS (Playwright required)]
**Page structure:**
  - Events container: [CSS selector, e.g., "div.event-list"]
  - Event title: [CSS selector]
  - Event date: [CSS selector]
  - Event description: [CSS selector]
  - Event URL: [CSS selector for link, if available]
**Sample event count:** [Number of events visible on page]
**Rate limiting notes:** [Any observed throttling or CAPTCHA]
**Reliability assessment:** [High / Medium / Low] -- likelihood of stable scraping
**Notes:** [Any special considerations]
```

#### 3. robots.txt Check Procedure

For each URL:
1. Access `https://[domain]/robots.txt`
2. Check if the specific path is allowed for `User-agent: *`
3. Document any `Crawl-delay` directive
4. If no robots.txt exists, document that and note scraping should still be respectful

#### 4. Static vs. Dynamic Determination

Test method:
1. Fetch the page with `requests.get()` (no JS rendering)
2. Check if the response HTML contains the expected event data
3. If yes: BeautifulSoup is sufficient (faster, no browser dependency)
4. If no: Playwright is required (heavier, but handles JS-rendered content)

Document the test result and reasoning for each university.

### Acceptance Criteria

- [ ] `docs/scraping_research.md` exists with entries for all 5 target universities
- [ ] Each entry includes: URL, robots.txt status, rendering method, CSS selectors, reliability assessment
- [ ] At least 3 of 5 universities are confirmed as viable scraping targets
- [ ] Portland State University event page URL is identified (was TBD)
- [ ] Static vs. dynamic rendering is determined for each university with evidence
- [ ] Rate limiting notes are documented for each target
- [ ] The document is structured so a coding agent can implement scrapers from it directly

### Harness Guidelines

- Output goes to `docs/scraping_research.md` within the project directory
- Use `requests` for static page testing and `playwright` for dynamic page testing
- Do NOT build the actual scraping pipeline -- that is Sprint 2 (A2.1)
- Keep testing minimal: 1-2 page loads per university, with 5+ seconds between requests

### Steer Guidelines

- If a university blocks scraping entirely (403, CAPTCHA, robots.txt disallow), mark it as "Not viable" and note that pre-cached HTML will be used instead
- If the agent starts building a full scraper during this research task, redirect -- this is research only
- The agent should save raw HTML samples for universities that work, as these become the cached fallback for demo day
- Portland State alternatives if their events page is unusable: Oregon State University or University of Oregon

---

## Definition of Done

All items must be checked before proceeding to Sprint 2:

- [ ] `compute_match_score()` computes correctly for all 270 speaker-event pairs (18 x 15) without errors
- [ ] All 6 factor functions return values in [0.0, 1.0] for every input combination in the dataset
- [ ] Top-3 matches per event are displayed in the Matches tab with radar charts and explanation cards
- [ ] Weight sliders in the sidebar recompute rankings in real time when adjusted
- [ ] Course matching works for all 10 High-fit sections, showing top-3 speaker matches per course
- [ ] Pipeline sample data (`data/pipeline_sample_data.csv`) is generated from real match outputs with 45 matched entries
- [ ] Scraping feasibility is confirmed for at least 3 of 5 target universities, documented in `docs/scraping_research.md`
- [ ] All functions have docstrings with argument types and return types documented
- [ ] No hardcoded API keys in source code (uses environment variables via `GEMINI_API_KEY`)
- [ ] `cache/explanations/` directory structure works and explanations are cached after first generation
- [ ] App runs without errors: `streamlit run src/app.py`

## Phase Closeout

- At the end of every phase in this sprint, invoke a dedicated agent in code-review mode against the completed work.
- Do not mark the phase complete until review findings are resolved.
- After the review passes with no open issues, update the affected documentation and commit the changes.

---

## Go/No-Go Gate (End of Day 5)

**PASS criteria (all must be met):**
- Matching engine produces explainable, sensible top-3 matches per event
- Weight sliders visibly change rankings when adjusted
- At least 3 of 5 university scrape targets confirmed viable in research doc
- Pipeline sample data generated with real speaker/event names

**FAIL on matching:**
- Debug scoring formula. Use Day 6 morning (2h) to fix.
- Non-negotiable -- matching engine IS the MVP.
- Common failure modes:
  - All scores cluster near 0.5 -> embedding quality issue, check Sprint 0 validation
  - Same speaker ranked #1 for every event -> geographic_proximity or role_fit weights too dominant
  - Explanation cards are generic/unhelpful -> refine few-shot examples in prompt

**FAIL on scraping:**
- Reduce to 3 universities
- Use pre-cached HTML as primary data source, live scrape as demo enhancement only
- No schedule impact on Sprint 2 -- scraping pipeline still gets built, just with fewer targets

---

## Memory Update Triggers

Update the following memory files when Sprint 1 completes:

1. **`.memory/context/cat3-data-insights.md`** -- Add:
   - Match score distribution (mean, median, std) across 270 pairs
   - Top-3 speaker-event pairings with scores
   - Any surprising matches or mismatches found during validation
   - Geographic distribution of top matches (are LA speakers over-represented?)

2. **`.memory/context/cat3-daily-standups.md`** -- Add Day 3, 4, 5 standup entries

3. **`.memory/decisions/cat3-weight-tuning.md`** -- Create:
   - Document the default weight rationale
   - Note any weight adjustments made during testing
   - Record which weight configurations produce the most sensible rankings

---

## Dependencies

**Depends on:** Sprint 0 (Foundation)
- All 4 CSVs loading into Pandas DataFrames
- 68 embedding vectors generated and cached (18 speakers + 15 events + 35 courses = 68); calendar rows remain tabular inputs only
- Cosine similarity validated on 5+ known pairs
- Streamlit skeleton with 3 tabs running

**Blocks:** Sprint 2 (Discovery + Email + Track B Kickoff)
- Sprint 2 A2.1 (web scraping pipeline) depends on A1.7 (scraping research)
- Sprint 2 A2.4 (outreach email generation) depends on A1.2 (match ranking results)
- Sprint 2 A2.6 (pipeline funnel chart) depends on A1.6 (pipeline sample data)
- Sprint 2 A2.7 (Track B data package) depends on all Sprint 1 outputs
- Sprint 2 B2.1-B2.5 (Track B writing) depends on real match data from Sprint 1

**Parallel with:** None -- Sprint 1 is single-track (Person B only). Track B (Person C) does not start until Day 6 (Sprint 2).
