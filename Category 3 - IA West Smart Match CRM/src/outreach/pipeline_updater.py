"""Pipeline CSV updater with LRU cache invalidation.

Provides ``update_pipeline_status`` to transition a speaker-event row's
stage in ``pipeline_sample_data.csv`` and immediately invalidate the
``_load_pipeline_data_cached`` LRU cache so subsequent reads return fresh data.
"""

from __future__ import annotations

import csv
from pathlib import Path

from src.config import get_writable_dir
from src.ui.data_helpers import _data_dir, _load_pipeline_data_cached

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIPELINE_STAGES: dict[str, int] = {
    "Matched": 0,
    "Contacted": 1,
    "Confirmed": 2,
    "Attended": 3,
    "Member Inquiry": 4,
}

def _pipeline_write_path() -> Path:
    return get_writable_dir("data") / "pipeline_sample_data.csv"


def _pipeline_read_path() -> Path:
    p = _pipeline_write_path()
    return p if p.exists() else (_data_dir() / "pipeline_sample_data.csv")

CSV_FIELDNAMES: list[str] = [
    "event_name",
    "speaker_name",
    "match_score",
    "rank",
    "stage",
    "stage_order",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _write_pipeline_csv(rows: list[dict]) -> None:
    """Write *rows* back to the pipeline CSV (overwrites the file)."""
    with _pipeline_write_path().open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def update_pipeline_status(event_name: str, speaker_name: str, new_stage: str) -> bool:
    """Update the pipeline stage for a speaker-event pair.

    Reads current rows from the LRU-cached pipeline data, applies an
    immutable update to the matching row, writes the result back, and
    clears the cache.

    Args:
        event_name: The event name to match (exact, case-sensitive).
        speaker_name: The speaker name to match (exact, case-sensitive).
        new_stage: The new stage value (must be a key in ``PIPELINE_STAGES``).

    Returns:
        ``True`` if an existing row was updated; ``False`` if a new row was
        appended (speaker/event combination not previously present).
    """
    current_rows: list[dict] = list(_load_pipeline_data_cached())

    found = False
    updated_rows: list[dict] = []

    for row in current_rows:
        if row.get("event_name") == event_name and row.get("speaker_name") == speaker_name:
            # Immutable update — build a new dict
            updated_row = {
                **row,
                "stage": new_stage,
                "stage_order": str(PIPELINE_STAGES.get(new_stage, 0)),
            }
            updated_rows.append(updated_row)
            found = True
        else:
            updated_rows.append(dict(row))

    if not found:
        updated_rows.append(
            {
                "event_name": event_name,
                "speaker_name": speaker_name,
                "match_score": "",
                "rank": "",
                "stage": new_stage,
                "stage_order": str(PIPELINE_STAGES.get(new_stage, 0)),
            }
        )

    _write_pipeline_csv(updated_rows)

    # CRITICAL: invalidate cache so GET /api/data/pipeline returns fresh data
    _load_pipeline_data_cached.cache_clear()

    return found
