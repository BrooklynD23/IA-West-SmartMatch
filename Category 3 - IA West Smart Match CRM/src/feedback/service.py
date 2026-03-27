"""Shared file-backed feedback persistence and optimizer logic."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.config import (
    DEFAULT_WEIGHTS,
    FACTOR_KEYS,
    OPTIMIZER_MAX_FACTOR_DELTA,
    OPTIMIZER_REASON_WEIGHT_BUMP,
    OPTIMIZER_TARGET_RATING,
)
from src.ui.data_helpers import (
    _data_dir,
    _load_feedback_log_cached,
    _load_weight_history_cached,
    load_feedback_log,
    load_weight_history,
)

FEEDBACK_DIRNAME = "feedback"
FEEDBACK_LOG_FILENAME = "feedback-log.jsonl"
WEIGHT_HISTORY_FILENAME = "weight-history.json"

DECLINE_REASON_TO_FACTOR: dict[str, str] = {
    "Too far (geographic distance)": "geographic_proximity",
    "Schedule conflict": "calendar_fit",
    "Topic mismatch": "topic_relevance",
    "Speaker already committed": "volunteer_fatigue",
    "Other": "role_fit",
}


def _feedback_dir() -> Path:
    return _data_dir() / FEEDBACK_DIRNAME


def _feedback_log_path() -> Path:
    return _feedback_dir() / FEEDBACK_LOG_FILENAME


def _weight_history_path() -> Path:
    return _feedback_dir() / WEIGHT_HISTORY_FILENAME


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _normalize_text(value: str) -> str:
    return " ".join(value.split()).casefold()


def _normalize_weights(weights: dict[str, float] | None = None) -> dict[str, float]:
    raw_weights = dict(DEFAULT_WEIGHTS if weights is None else weights)
    weight_sum = sum(float(raw_weights.get(factor, 0.0) or 0.0) for factor in FACTOR_KEYS)
    if weight_sum <= 0:
        return {factor: 0.0 for factor in FACTOR_KEYS}
    return {
        factor: round(float(raw_weights.get(factor, 0.0) or 0.0) / weight_sum, 4)
        for factor in FACTOR_KEYS
    }


def _feedback_entry_id(timestamp: str, event_name: str, speaker_name: str) -> str:
    payload = f"{timestamp}|{_normalize_text(event_name)}|{_normalize_text(speaker_name)}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"fb-{digest}"


def _append_feedback_entry(entry: dict[str, Any]) -> None:
    feedback_dir = _feedback_dir()
    feedback_dir.mkdir(parents=True, exist_ok=True)
    with _feedback_log_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True))
        fh.write("\n")
    _load_feedback_log_cached.cache_clear()


def _write_weight_history(snapshots: list[dict[str, Any]]) -> None:
    feedback_dir = _feedback_dir()
    feedback_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": _utc_now(),
        "snapshot_count": len(snapshots),
        "snapshots": snapshots,
    }
    _weight_history_path().write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    _load_weight_history_cached.cache_clear()


def _normalize_factor_scores(payload: Any) -> dict[str, float]:
    if not isinstance(payload, dict):
        return {}
    scores: dict[str, float] = {}
    for factor, value in payload.items():
        if factor not in FACTOR_KEYS:
            continue
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            continue
        scores[factor] = max(0.0, min(parsed, 1.0))
    return scores


def _normalize_rating(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return max(1.0, min(parsed, 5.0))


def _trend_rows(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_date: dict[str, dict[str, Any]] = {}
    for entry in entries:
        timestamp = str(entry.get("timestamp", ""))
        date_label = timestamp.split("T", 1)[0] if "T" in timestamp else timestamp[:10] or "unknown"
        bucket = by_date.setdefault(
            date_label,
            {"date": date_label, "feedback_count": 0, "accepted": 0, "declined": 0},
        )
        bucket["feedback_count"] += 1
        if entry.get("decision") == "accept":
            bucket["accepted"] += 1
        if entry.get("decision") == "decline":
            bucket["declined"] += 1

    trend = []
    for bucket in sorted(by_date.values(), key=lambda item: item["date"]):
        total = int(bucket["feedback_count"])
        accepted = int(bucket["accepted"])
        trend.append(
            {
                **bucket,
                "acceptance_rate": round(accepted / total, 4) if total else 0.0,
            }
        )
    return trend[-8:]


def _pain_score(
    *,
    total_feedback: int,
    declined: int,
    accepted: int,
    attended_count: int,
    membership_interest_count: int,
    average_rating: float | None,
) -> float:
    if total_feedback <= 0:
        return 0.0

    decline_pressure = declined / total_feedback
    attendance_gap = 0.0 if accepted <= 0 else max(0.0, 1.0 - (attended_count / accepted))
    rating_gap = (
        0.0
        if average_rating is None
        else max(0.0, (OPTIMIZER_TARGET_RATING - average_rating) / OPTIMIZER_TARGET_RATING)
    )
    conversion_gap = (
        0.0
        if accepted <= 0
        else max(0.0, 1.0 - (membership_interest_count / accepted))
    )
    score = (
        (decline_pressure * 0.45)
        + (attendance_gap * 0.25)
        + (rating_gap * 0.20)
        + (conversion_gap * 0.10)
    ) * 100
    return round(max(0.0, min(score, 100.0)), 1)


def _optimizer_snapshot(entries: list[dict[str, Any]]) -> dict[str, Any]:
    baseline = _normalize_weights(DEFAULT_WEIGHTS)
    total_feedback = len(entries)
    accepted = sum(1 for entry in entries if entry.get("decision") == "accept")
    declined = sum(1 for entry in entries if entry.get("decision") == "decline")
    attended_count = sum(1 for entry in entries if entry.get("event_outcome") == "attended")
    membership_interest_count = sum(
        1 for entry in entries if bool(entry.get("membership_interest"))
    )
    ratings = [
        float(entry["coordinator_rating"])
        for entry in entries
        if entry.get("coordinator_rating") not in (None, "")
    ]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
    acceptance_rate = round(accepted / total_feedback, 4) if total_feedback else 0.0

    raw_weights = dict(baseline)
    rationales: dict[str, list[str]] = {factor: [] for factor in FACTOR_KEYS}
    decline_reasons: dict[str, int] = {}
    for entry in entries:
        reason = str(entry.get("decline_reason", "") or "").strip()
        if not reason:
            continue
        decline_reasons[reason] = decline_reasons.get(reason, 0) + 1

    for reason, count in decline_reasons.items():
        factor = DECLINE_REASON_TO_FACTOR.get(reason)
        if factor is None:
            continue
        delta = min(OPTIMIZER_MAX_FACTOR_DELTA, OPTIMIZER_REASON_WEIGHT_BUMP * count)
        raw_weights[factor] += delta
        rationales[factor].append(f"{count} feedback entries cited '{reason}'")

    if accepted > 0 and attended_count < accepted:
        delta = min(OPTIMIZER_MAX_FACTOR_DELTA / 2, 0.02)
        raw_weights["calendar_fit"] += delta
        rationales["calendar_fit"].append(
            "Attendance is lagging behind accepted matches"
        )

    if membership_interest_count > 0:
        delta = min(OPTIMIZER_MAX_FACTOR_DELTA / 2, 0.02)
        raw_weights["historical_conversion"] += delta
        raw_weights["student_interest"] += delta / 2
        rationales["historical_conversion"].append(
            "Membership-interest outcomes are available for attribution"
        )
        rationales["student_interest"].append(
            "Membership-interest outcomes indicate student-facing signal strength"
        )

    if average_rating is not None and average_rating < OPTIMIZER_TARGET_RATING:
        delta = min(
            OPTIMIZER_MAX_FACTOR_DELTA / 2,
            round((OPTIMIZER_TARGET_RATING - average_rating) / 10, 4),
        )
        raw_weights["topic_relevance"] += delta
        raw_weights["role_fit"] += delta
        rationales["topic_relevance"].append(
            f"Average coordinator rating ({average_rating:.2f}) is below target"
        )
        rationales["role_fit"].append(
            f"Average coordinator rating ({average_rating:.2f}) is below target"
        )

    if total_feedback > 0 and acceptance_rate < 0.55:
        delta = min(OPTIMIZER_MAX_FACTOR_DELTA / 2, 0.015)
        raw_weights["role_fit"] += delta
        rationales["role_fit"].append(
            "Acceptance rate is below the desired threshold"
        )

    for factor in FACTOR_KEYS:
        lower_bound = max(0.01, baseline[factor] - OPTIMIZER_MAX_FACTOR_DELTA)
        upper_bound = baseline[factor] + OPTIMIZER_MAX_FACTOR_DELTA
        raw_weights[factor] = max(lower_bound, min(raw_weights[factor], upper_bound))

    current_weights = _normalize_weights(raw_weights)
    adjustments = []
    for factor in FACTOR_KEYS:
        delta = round(current_weights[factor] - baseline[factor], 4)
        if abs(delta) < 0.001:
            continue
        adjustments.append(
            {
                "factor": factor,
                "from_weight": baseline[factor],
                "to_weight": current_weights[factor],
                "delta": delta,
                "rationale": "; ".join(rationales[factor]) or "Rebalanced from aggregate feedback",
            }
        )

    return {
        "timestamp": _utc_now(),
        "total_feedback": total_feedback,
        "accepted": accepted,
        "declined": declined,
        "acceptance_rate": acceptance_rate,
        "pain_score": _pain_score(
            total_feedback=total_feedback,
            declined=declined,
            accepted=accepted,
            attended_count=attended_count,
            membership_interest_count=membership_interest_count,
            average_rating=average_rating,
        ),
        "weights": current_weights,
        "baseline_weights": baseline,
        "adjustments": adjustments,
    }


def get_effective_weights() -> dict[str, float]:
    history = load_weight_history()
    if history:
        weights = history[-1].get("weights")
        if isinstance(weights, dict):
            return _normalize_weights(weights)
    return _normalize_weights(DEFAULT_WEIGHTS)


def record_feedback(payload: dict[str, Any]) -> dict[str, Any]:
    timestamp = str(payload.get("timestamp") or _utc_now())
    event_name = str(payload.get("event_name") or payload.get("event_id") or "").strip()
    speaker_name = str(payload.get("speaker_name") or payload.get("speaker_id") or "").strip()
    if not event_name or not speaker_name:
        raise ValueError("event_name and speaker_name are required")

    decision = str(payload.get("decision") or "").strip().lower()
    if decision not in {"accept", "decline"}:
        raise ValueError("decision must be 'accept' or 'decline'")

    weights_used = (
        payload.get("weights_used")
        if isinstance(payload.get("weights_used"), dict)
        else get_effective_weights()
    )

    feedback_entry = {
        "entry_id": _feedback_entry_id(timestamp, event_name, speaker_name),
        "timestamp": timestamp,
        "event_name": event_name,
        "speaker_name": speaker_name,
        "match_score": max(0.0, min(float(payload.get("match_score", 0.0) or 0.0), 1.0)),
        "decision": decision,
        "decline_reason": str(payload.get("decline_reason") or "").strip() or None,
        "decline_notes": str(payload.get("decline_notes") or "").strip() or None,
        "event_outcome": str(payload.get("event_outcome") or "").strip() or None,
        "membership_interest": bool(payload.get("membership_interest", False)),
        "coordinator_rating": _normalize_rating(payload.get("coordinator_rating")),
        "factor_scores": _normalize_factor_scores(payload.get("factor_scores")),
        "weights_used": _normalize_weights(weights_used),
    }
    _append_feedback_entry(feedback_entry)

    entries = load_feedback_log()
    history = load_weight_history()
    snapshot = _optimizer_snapshot(entries)
    history.append(snapshot)
    _write_weight_history(history)

    return {
        "feedback": feedback_entry,
        "optimizer_snapshot": snapshot,
    }


def build_feedback_stats() -> dict[str, Any]:
    entries = load_feedback_log()
    history = load_weight_history()
    snapshot = history[-1] if history else _optimizer_snapshot(entries)

    total_feedback = len(entries)
    accepted = sum(1 for entry in entries if entry.get("decision") == "accept")
    declined = sum(1 for entry in entries if entry.get("decision") == "decline")
    attended_count = sum(1 for entry in entries if entry.get("event_outcome") == "attended")
    membership_interest_count = sum(
        1 for entry in entries if bool(entry.get("membership_interest"))
    )
    ratings = [
        float(entry["coordinator_rating"])
        for entry in entries
        if entry.get("coordinator_rating") not in (None, "")
    ]
    average_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

    decline_reasons: dict[str, int] = {}
    event_outcomes: dict[str, int] = {}
    accepted_scores: list[float] = []
    declined_scores: list[float] = []
    for entry in entries:
        reason = str(entry.get("decline_reason") or "").strip()
        if reason:
            decline_reasons[reason] = decline_reasons.get(reason, 0) + 1
        outcome = str(entry.get("event_outcome") or "").strip()
        if outcome:
            event_outcomes[outcome] = event_outcomes.get(outcome, 0) + 1
        score = float(entry.get("match_score", 0.0) or 0.0)
        if entry.get("decision") == "accept":
            accepted_scores.append(score)
        elif entry.get("decision") == "decline":
            declined_scores.append(score)

    decline_rows = [
        {"reason": reason, "count": count}
        for reason, count in sorted(
            decline_reasons.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]
    outcome_rows = [
        {"outcome": outcome, "count": count}
        for outcome, count in sorted(
            event_outcomes.items(),
            key=lambda item: (-item[1], item[0]),
        )
    ]

    return {
        "total_feedback": total_feedback,
        "accepted": accepted,
        "declined": declined,
        "acceptance_rate": round(accepted / total_feedback, 4) if total_feedback else 0.0,
        "attended_count": attended_count,
        "membership_interest_count": membership_interest_count,
        "membership_interest_rate": round(
            membership_interest_count / accepted, 4
        ) if accepted else 0.0,
        "average_coordinator_rating": average_rating,
        "average_match_score_accepted": round(sum(accepted_scores) / len(accepted_scores), 4)
        if accepted_scores
        else 0.0,
        "average_match_score_declined": round(sum(declined_scores) / len(declined_scores), 4)
        if declined_scores
        else 0.0,
        "decline_reasons": decline_rows,
        "event_outcomes": outcome_rows,
        "pain_score": float(snapshot.get("pain_score", 0.0) or 0.0),
        "trend": _trend_rows(entries),
        "default_weights": _normalize_weights(DEFAULT_WEIGHTS),
        "current_weights": _normalize_weights(snapshot.get("weights") if isinstance(snapshot.get("weights"), dict) else None),
        "suggested_weights": _normalize_weights(snapshot.get("weights") if isinstance(snapshot.get("weights"), dict) else None),
        "recommended_adjustments": list(snapshot.get("adjustments", [])),
        "weight_history": history[-8:],
    }
