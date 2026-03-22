"""Helpers for shared Streamlit runtime state across tabs."""

from __future__ import annotations

from typing import Any, Sequence

import pandas as pd
import streamlit as st

from src.config import FACTOR_KEYS

MATCH_RESULTS_COLUMNS: list[str] = [
    "event_id",
    "event_name",
    "speaker_id",
    "speaker_name",
    "rank",
    "total_score",
    *FACTOR_KEYS,
]

DISCOVERED_EVENT_ALIASES: dict[str, str] = {
    "Recurrence (typical)": "Date",
    "Public URL": "URL",
    "Point(s) of Contact (published)": "Contact Name",
    "Contact Email / Phone (published)": "Contact Email",
}


def empty_match_results_df() -> pd.DataFrame:
    """Return an empty DataFrame matching the cross-tab contract."""
    return pd.DataFrame(columns=MATCH_RESULTS_COLUMNS)


def init_runtime_state() -> None:
    """Initialize shared runtime keys used by multiple tabs."""
    if "match_results_df" not in st.session_state:
        st.session_state["match_results_df"] = empty_match_results_df()
    if "matching_discovered_events" not in st.session_state:
        st.session_state["matching_discovered_events"] = []
    if "scraped_events" not in st.session_state:
        st.session_state["scraped_events"] = []
    if "emails_generated" not in st.session_state:
        st.session_state["emails_generated"] = 0
    if "generated_email_keys" not in st.session_state:
        st.session_state["generated_email_keys"] = []


def get_matching_events_df(events_df: pd.DataFrame) -> pd.DataFrame:
    """Return the canonical events DataFrame plus in-session discovered rows."""
    init_runtime_state()

    base_events = events_df.copy()
    if "event_id" not in base_events.columns and "Event / Program" in base_events.columns:
        base_events["event_id"] = base_events["Event / Program"].astype(str)
    discovered_rows = st.session_state.get("matching_discovered_events", [])
    if not isinstance(discovered_rows, list):
        return base_events

    discovered_dicts = [
        row for row in discovered_rows
        if isinstance(row, dict)
    ]
    if not discovered_dicts:
        return base_events

    discovered_df = pd.DataFrame(discovered_dicts).copy()
    _hydrate_discovered_event_contract(
        discovered_df,
        base_columns=base_events.columns.tolist(),
    )
    if "event_id" in discovered_df.columns:
        discovered_df = discovered_df.drop_duplicates(subset=["event_id"], keep="last")

    ordered_columns = list(base_events.columns) + [
        column for column in discovered_df.columns
        if column not in base_events.columns
    ]
    return pd.concat(
        [base_events, discovered_df],
        ignore_index=True,
        sort=False,
    ).reindex(columns=ordered_columns)


def _hydrate_discovered_event_contract(
    discovered_df: pd.DataFrame,
    base_columns: Sequence[str],
) -> None:
    """Fill canonical event columns from legacy discovery aliases."""
    for canonical_column, alias_column in DISCOVERED_EVENT_ALIASES.items():
        if canonical_column not in discovered_df.columns and alias_column in discovered_df.columns:
            discovered_df[canonical_column] = discovered_df[alias_column]

    for column in base_columns:
        if column not in discovered_df.columns:
            discovered_df[column] = pd.NA
    if "event_id" not in discovered_df.columns and "Event / Program" in discovered_df.columns:
        discovered_df["event_id"] = discovered_df["Event / Program"].astype(str)


def normalize_match_results(match_results: list[dict[str, Any]]) -> pd.DataFrame:
    """Normalize match results into a DataFrame that all tabs can consume."""
    if not match_results:
        return empty_match_results_df()

    rows: list[dict[str, Any]] = []
    for match in match_results:
        factor_scores = match.get("factor_scores", {})
        event_name = str(match.get("event_name", "") or "")
        event_id = str(match.get("event_id", "") or event_name)
        speaker_name = str(
            match.get("speaker_name")
            or match.get("speaker_id")
            or ""
        )
        row_dict: dict[str, Any] = {
            "event_id": event_id,
            "event_name": event_name,
            "speaker_id": speaker_name,
            "speaker_name": speaker_name,
            "rank": int(match.get("rank", 0) or 0),
            "total_score": float(match.get("total_score", 0.0) or 0.0),
        }
        for fk in FACTOR_KEYS:
            row_dict[fk] = float(factor_scores.get(fk, 0.0) or 0.0)
        rows.append(row_dict)

    return pd.DataFrame(rows, columns=MATCH_RESULTS_COLUMNS)


def set_match_results(match_results: list[dict[str, Any]]) -> pd.DataFrame:
    """Persist normalized match results into session state."""
    init_runtime_state()
    normalized = normalize_match_results(match_results)
    st.session_state["match_results_df"] = normalized
    return normalized


def get_match_results_df() -> pd.DataFrame:
    """Return the normalized match results from session state."""
    init_runtime_state()
    current = st.session_state.get("match_results_df")
    if isinstance(current, pd.DataFrame):
        missing_columns = [
            column for column in MATCH_RESULTS_COLUMNS if column not in current.columns
        ]
        if not missing_columns:
            return current
        normalized = current.copy()
        for column in missing_columns:
            normalized[column] = "" if column.endswith("_id") or column.endswith("_name") else 0.0
        return normalized.reindex(columns=MATCH_RESULTS_COLUMNS)
    return empty_match_results_df()
