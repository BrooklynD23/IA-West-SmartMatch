"""Shared helpers for IA SmartMatch CRM."""

import logging
import sys
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
