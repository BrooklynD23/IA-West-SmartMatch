"""
Matching engine for IA SmartMatch CRM.

Provides composite scoring, speaker ranking for events and courses,
and pipeline data generation for funnel visualisation.
"""

import logging
import random
from typing import Any, Optional

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
from src.utils import format_course_display_name

logger = logging.getLogger(__name__)

# Pipeline stage definitions (label, cumulative-retention rate relative to Matched)
_PIPELINE_STAGES: list[tuple[str, float]] = [
    ("Matched", 1.00),
    ("Contacted", 0.80),
    ("Confirmed", 0.36),   # 80% * 45%
    ("Attended", 0.27),    # 36% * 75%
    ("Member Inquiry", 0.0405),  # 27% * 15%
]

_PIPELINE_STAGE_ORDER: dict[str, int] = {
    stage: order for order, (stage, _) in enumerate(_PIPELINE_STAGES)
}


# ---------------------------------------------------------------------------
# Core scoring
# ---------------------------------------------------------------------------


def _normalize_weights(weights: Optional[dict[str, float]] = None) -> dict[str, float]:
    """Return weights normalized to sum to 1.0 across the known factor set."""
    raw_weights = weights if weights is not None else DEFAULT_WEIGHTS
    weight_sum = sum(raw_weights.values())
    if weight_sum <= 0:
        return {factor: 0.0 for factor in DEFAULT_WEIGHTS}

    return {
        factor: raw_weights.get(factor, 0.0) / weight_sum
        for factor in DEFAULT_WEIGHTS
    }


def compute_match_score(
    speaker_embedding: np.ndarray,
    event_embedding: np.ndarray,
    speaker_board_role: str,
    event_volunteer_roles: str,
    speaker_metro_region: str,
    event_region: str,
    event_date_or_recurrence: object,
    ia_event_calendar: pd.DataFrame,
    speaker_name: str,
    event_category: str,
    weights: Optional[dict[str, float]] = None,
    conversion_overrides: Optional[dict[str, float]] = None,
    student_interest_override: Optional[float] = None,
) -> dict[str, Any]:
    """
    Compute a composite match score for one speaker–event pair.

    Args:
        speaker_embedding: 1-D numpy array for the speaker.
        event_embedding: 1-D numpy array for the event.
        speaker_board_role: Speaker's board role string.
        event_volunteer_roles: Semicolon/comma-separated volunteer roles for event.
        speaker_metro_region: Speaker's metro region canonical string.
        event_region: Raw event location / region string.
        event_date_or_recurrence: Specific event date or recurrence description.
        ia_event_calendar: DataFrame with IA event calendar data.
        speaker_name: Speaker's full name (used for conversion lookup).
        event_category: Event category string.
        weights: Optional override for factor weights dict.
        conversion_overrides: Optional speaker-name → conversion score mapping.
        student_interest_override: Optional precomputed student interest score.

    Returns:
        Dict with keys:
            total_score (float),
            factor_scores (dict[str, float]),
            weighted_factor_scores (dict[str, float]).
    """
    active_weights = _normalize_weights(weights)

    factor_scores: dict[str, float] = {
        "topic_relevance": topic_relevance(speaker_embedding, event_embedding),
        "role_fit": role_fit(speaker_board_role, event_volunteer_roles),
        "geographic_proximity": geographic_proximity(speaker_metro_region, event_region),
        "calendar_fit": calendar_fit(
            event_date_or_recurrence, ia_event_calendar, speaker_metro_region
        ),
        "historical_conversion": historical_conversion(speaker_name, conversion_overrides),
        "student_interest": max(
            0.0,
            min(
                1.0,
                student_interest_override
                if student_interest_override is not None
                else student_interest(event_category),
            ),
        ),
    }

    weighted_factor_scores: dict[str, float] = {
        factor: round(score * active_weights.get(factor, 0.0), 4)
        for factor, score in factor_scores.items()
    }

    total_score = round(sum(weighted_factor_scores.values()), 4)

    return {
        "total_score": total_score,
        "factor_scores": factor_scores,
        "weighted_factor_scores": weighted_factor_scores,
    }


# ---------------------------------------------------------------------------
# Ranking helpers
# ---------------------------------------------------------------------------

def _build_speaker_result(
    rank: int,
    speaker_row: pd.Series,
    event_name: str,
    score_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Build the downstream-contract ranking result dict for a single speaker.

    All keys required by downstream consumers are present even when the
    source data is missing (defaults to empty string / 0).
    """
    return {
        "rank": rank,
        "speaker_name": str(speaker_row.get("Name", "")),
        "speaker_title": str(speaker_row.get("Title", "")),
        "speaker_company": str(speaker_row.get("Company", "")),
        "speaker_board_role": str(speaker_row.get("Board Role", "")),
        "speaker_metro_region": str(speaker_row.get("Metro Region", "")),
        "speaker_expertise_tags": str(speaker_row.get("Expertise Tags", "")),
        "event_name": event_name,
        "total_score": score_data["total_score"],
        "factor_scores": score_data["factor_scores"],
        "weighted_factor_scores": score_data["weighted_factor_scores"],
    }


# ---------------------------------------------------------------------------
# Public ranking API
# ---------------------------------------------------------------------------

def rank_speakers_for_event(
    event_row: pd.Series,
    speakers_df: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    event_embedding: np.ndarray,
    ia_event_calendar: pd.DataFrame,
    top_n: int = 10,
    weights: Optional[dict[str, float]] = None,
    conversion_overrides: Optional[dict[str, float]] = None,
    student_interest_override: Optional[float] = None,
) -> list[dict[str, Any]]:
    """
    Rank all speakers for a given event and return the top N results.

    Args:
        event_row: A single row from the CPP events DataFrame.
        speakers_df: Full speakers DataFrame.
        speaker_embeddings: Dict mapping speaker Name → embedding array.
        event_embedding: Pre-computed 1-D numpy embedding for the event.
        ia_event_calendar: DataFrame with IA event calendar data.
        top_n: Maximum number of results to return.
        weights: Optional factor weight overrides.
        conversion_overrides: Optional speaker conversion score overrides.
        student_interest_override: Optional precomputed student interest score.

    Returns:
        List of result dicts sorted by total_score descending, each containing
        the downstream-contract keys (rank, speaker_name, speaker_title, etc.).
    """
    event_name = str(event_row.get("Event / Program", "Unknown Event"))
    event_volunteer_roles = str(event_row.get("Volunteer Roles (fit)", ""))
    event_region = str(event_row.get("Host / Unit", ""))
    event_category = str(event_row.get("Category", ""))
    event_date_or_recurrence = event_row.get(
        "Event Date", event_row.get("Recurrence (typical)", "")
    )

    scored: list[dict[str, Any]] = []

    for _, speaker_row in speakers_df.iterrows():
        speaker_name = str(speaker_row.get("Name", ""))
        speaker_embedding = speaker_embeddings.get(speaker_name)

        # Embeddings are optional; topic_relevance returns 0.0 for None/empty/NaN
        _speaker_emb = speaker_embedding if speaker_embedding is not None else np.array([])
        _event_emb = event_embedding if event_embedding is not None else np.array([])

        score_data = compute_match_score(
            speaker_embedding=_speaker_emb,
            event_embedding=_event_emb,
            speaker_board_role=str(speaker_row.get("Board Role", "")),
            event_volunteer_roles=event_volunteer_roles,
            speaker_metro_region=str(speaker_row.get("Metro Region", "")),
            event_region=event_region,
            event_date_or_recurrence=event_date_or_recurrence,
            ia_event_calendar=ia_event_calendar,
            speaker_name=speaker_name,
            event_category=event_category,
            weights=weights,
            conversion_overrides=conversion_overrides,
            student_interest_override=student_interest_override,
        )
        scored.append(
            _build_speaker_result(
                rank=0,  # placeholder — assigned after sorting
                speaker_row=speaker_row,
                event_name=event_name,
                score_data=score_data,
            )
        )

    # Sort descending by total_score, then alphabetically by name for stability
    scored.sort(key=lambda x: (-x["total_score"], x["speaker_name"]))
    ranked = [
        {**entry, "rank": idx + 1}
        for idx, entry in enumerate(scored[:top_n])
    ]

    logger.info(
        "Ranked %d speakers for event %r (top_n=%d).",
        len(ranked), event_name, top_n,
    )
    return ranked


def rank_speakers_for_course(
    course_row: pd.Series,
    speakers_df: pd.DataFrame,
    speaker_embeddings: dict[str, np.ndarray],
    course_embedding: np.ndarray,
    ia_event_calendar: pd.DataFrame,
    top_n: int = 10,
    weights: Optional[dict[str, float]] = None,
    conversion_overrides: Optional[dict[str, float]] = None,
) -> list[dict[str, Any]]:
    """
    Rank all speakers for a course by treating the course as an event-like object.

    Courses are mapped to "guest speaker" volunteer roles and "Cal Poly Pomona"
    as the default event region.

    Args:
        course_row: A single row from the CPP courses DataFrame.
        speakers_df: Full speakers DataFrame.
        speaker_embeddings: Dict mapping speaker Name → embedding array.
        course_embedding: Pre-computed 1-D numpy embedding for the course.
        ia_event_calendar: DataFrame with IA event calendar data.
        top_n: Maximum number of results to return.
        weights: Optional factor weight overrides.
        conversion_overrides: Optional speaker conversion score overrides.

    Returns:
        List of result dicts sorted by total_score descending.
    """
    course_title = str(course_row.get("Title", "Unknown Course"))
    course_code = str(course_row.get("Course", ""))
    course_section = course_row.get("Section", "")
    event_name = format_course_display_name(course_code, course_section, course_title)

    guest_fit = str(course_row.get("Guest Lecture Fit", "Medium")).strip()
    fit_to_interest = {"High": 0.9, "Medium": 0.6, "Low": 0.3}
    override_interest = fit_to_interest.get(guest_fit, 0.5)

    pseudo_event = pd.Series(
        {
            "Event / Program": event_name,
            "Category": "Guest Lecture",
            "Volunteer Roles (fit)": "guest speaker",
            "Host / Unit": "Cal Poly Pomona",
            "Recurrence (typical)": str(course_row.get("Days", "Weekly")),
            "Event Date": None,
        }
    )

    results = rank_speakers_for_event(
        event_row=pseudo_event,
        speakers_df=speakers_df,
        speaker_embeddings=speaker_embeddings,
        event_embedding=course_embedding,
        ia_event_calendar=ia_event_calendar,
        top_n=top_n,
        weights=weights,
        conversion_overrides=conversion_overrides,
        student_interest_override=override_interest,
    )
    return results


# ---------------------------------------------------------------------------
# Pipeline data generation
# ---------------------------------------------------------------------------

def generate_pipeline_data(
    ranked_results: list[dict[str, Any]],
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate a pipeline sample DataFrame with simulated conversion stages.

    Starting from the full ranked list ("Matched"), each subsequent stage
    retains a fixed proportion of the previous stage:
        Matched (all) → Contacted (80%) → Confirmed (45%) → Attended (75%)
        → Member Inquiry (15%)

    Each entry is assigned the DEEPEST stage reached.

    Args:
        ranked_results: List of ranking dicts from rank_speakers_for_event
            or rank_speakers_for_course.
        seed: Random seed for reproducibility.

    Returns:
        DataFrame with columns:
            event_name, speaker_name, match_score, rank, stage, stage_order.
    """
    if not ranked_results:
        return pd.DataFrame(
            columns=["event_name", "speaker_name", "match_score", "rank", "stage", "stage_order"]
        )

    rng = random.Random(seed)

    # Stage transitions: (label, retention_rate_from_previous_stage)
    stage_transitions: list[tuple[str, float]] = [
        ("Matched", 1.00),
        ("Contacted", 0.80),
        ("Confirmed", 0.45),
        ("Attended", 0.75),
        ("Member Inquiry", 0.15),
    ]

    # For each speaker, determine the deepest stage reached
    rows: list[dict[str, Any]] = []

    for entry in ranked_results:
        deepest_stage = "Matched"
        deepest_order = 0

        survived = True
        for idx, (stage_label, retention) in enumerate(stage_transitions):
            if idx == 0:
                # Everyone starts at Matched
                deepest_stage = stage_label
                deepest_order = idx
                continue
            if not survived:
                break
            if rng.random() <= retention:
                deepest_stage = stage_label
                deepest_order = idx
            else:
                survived = False

        rows.append(
            {
                "event_name": entry.get("event_name", ""),
                "speaker_name": entry.get("speaker_name", ""),
                "match_score": entry.get("total_score", 0.0),
                "rank": entry.get("rank", 0),
                "stage": deepest_stage,
                "stage_order": deepest_order,
            }
        )

    return pd.DataFrame(rows)
