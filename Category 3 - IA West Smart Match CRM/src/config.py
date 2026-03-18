"""Centralized configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Project paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
CACHE_DIR = PROJECT_ROOT / os.getenv("CACHE_DIR", "cache")

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# --- Embedding ---
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "20"))
EMBEDDING_MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))

# --- Data file names ---
SPEAKER_PROFILES_CSV = "data_speaker_profiles.csv"
CPP_EVENTS_CSV = "data_cpp_events_contacts.csv"
CPP_COURSES_CSV = "data_cpp_course_schedule.csv"
EVENT_CALENDAR_CSV = "data_event_calendar.csv"

# --- Streamlit ---
PAGE_TITLE = os.getenv("STREAMLIT_PAGE_TITLE", "IA SmartMatch CRM")


# --- Validation ---
def has_openai_api_key() -> bool:
    """Return whether a non-placeholder OpenAI API key is configured."""
    return bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-...")


def validate_config(require_openai: bool = False) -> list[str]:
    """Return list of configuration errors. Empty list means all good."""
    errors = []
    if require_openai and not has_openai_api_key():
        errors.append("OPENAI_API_KEY is not set or is still the placeholder value")
    if not DATA_DIR.exists():
        errors.append(f"DATA_DIR does not exist: {DATA_DIR}")
    for csv_name in [SPEAKER_PROFILES_CSV, CPP_EVENTS_CSV, CPP_COURSES_CSV, EVENT_CALENDAR_CSV]:
        csv_path = DATA_DIR / csv_name
        if not csv_path.exists():
            errors.append(f"Required data file missing: {csv_path}")
    return errors
