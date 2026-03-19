"""Shared helpers for IA SmartMatch CRM."""

import logging
import re
import sys
from collections.abc import Iterable
from pathlib import Path

from src.config import DATA_DIR


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a standard format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def ensure_dir(path: Path) -> Path:
    """Create directory if it does not exist. Returns path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def check_data_files_present(data_dir: Path = DATA_DIR) -> list[str]:
    """
    Check that all required CSV files exist.

    Returns:
        List of missing file names (empty if all present).
    """
    required = [
        "data_speaker_profiles.csv",
        "data_cpp_events_contacts.csv",
        "data_cpp_course_schedule.csv",
        "data_event_calendar.csv",
    ]
    return [f for f in required if not (data_dir / f).exists()]


def normalize_course_section(section: object) -> str:
    """Return a canonical zero-padded course section string when possible."""
    if section is None:
        return ""

    section_text = str(section).strip()
    if not section_text or section_text.lower() == "nan":
        return ""

    return section_text.zfill(2) if section_text.isdigit() else section_text


def format_course_identifier(course: object, section: object) -> str:
    """Return the canonical `Course-Section` identifier used across the app."""
    course_text = "" if course is None else str(course).strip()
    section_text = normalize_course_section(section)

    if course_text and section_text:
        return f"{course_text}-{section_text}"
    return course_text or section_text


def format_course_display_name(course: object, section: object, title: object) -> str:
    """Return the canonical course display label used in matching views."""
    identifier = format_course_identifier(course, section)
    title_text = "" if title is None else str(title).strip()

    if identifier and title_text:
        return f"{identifier}: {title_text}"
    return identifier or title_text or "Unknown Course"


def summarize_missing_keys(
    expected_keys: Iterable[object],
    loaded_keys: Iterable[object],
    sample_size: int = 3,
) -> tuple[int, list[str]]:
    """Return count and a short sample of expected keys missing from a lookup."""
    expected = {
        re.sub(r"\s+", " ", str(value).strip())
        for value in expected_keys
        if value is not None and str(value).strip()
    }
    loaded = {
        re.sub(r"\s+", " ", str(value).strip())
        for value in loaded_keys
        if value is not None and str(value).strip()
    }

    missing = sorted(expected - loaded)
    return len(missing), missing[:sample_size]
