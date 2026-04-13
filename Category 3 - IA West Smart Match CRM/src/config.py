"""Centralized configuration loaded from environment variables and secrets."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from dotenv import load_dotenv

load_dotenv()

# --- Project paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / os.getenv("DATA_DIR", "data")
CACHE_DIR = PROJECT_ROOT / os.getenv("CACHE_DIR", "cache")


def get_writable_dir(subpath: str) -> Path:
    """Return /tmp/iawest-crm/<subpath> on Vercel, PROJECT_ROOT/<subpath> locally."""
    import os as _os
    if _os.getenv("VERCEL") or str(PROJECT_ROOT).startswith("/var/task"):
        base = Path("/tmp/iawest-crm") / subpath
    else:
        base = PROJECT_ROOT / subpath
    base.mkdir(parents=True, exist_ok=True)
    return base


def _secret_or_env(name: str, default: str = "") -> str:
    """Read a config value from env first, then Streamlit secrets if available."""
    env_value = os.getenv(name)
    if env_value:
        return env_value

    if "streamlit" not in sys.modules:
        return default
    st = sys.modules["streamlit"]

    secrets = getattr(st, "secrets", None)
    if secrets is None:
        return default

    try:
        value = secrets.get(name)
    except Exception:
        return default

    if value in (None, ""):
        return default
    return str(value)

# --- Gemini ---
GEMINI_API_KEY = _secret_or_env("GEMINI_API_KEY", "")
GEMINI_BASE_URL = os.getenv(
    "GEMINI_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta",
)
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
GEMINI_TEXT_MODEL = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash-lite")

# --- Voice I/O (Phase 4) ---
KITTENTTS_VOICE: Final[str] = os.getenv("KITTENTTS_VOICE", "Bella")
KITTENTTS_MODEL_ID: Final[str] = "KittenML/kitten-tts-mini-0.8"
KITTENTTS_SAMPLE_RATE: Final[int] = 24000
WHISPER_MODEL_SIZE: Final[str] = os.getenv("WHISPER_MODEL_SIZE", "base")
WHISPER_COMPUTE_TYPE: Final[str] = "int8"

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


# ---------- Factor Registry (single source of truth) ----------

@dataclass(frozen=True)
class FactorSpec:
    """Immutable specification for a matching factor."""
    key: str
    display_label: str
    short_label: str
    default_weight: float
    prompt_label: str
    email_alias: str


FACTOR_REGISTRY: Final[tuple[FactorSpec, ...]] = (
    FactorSpec("topic_relevance", "Topic Relevance", "Topic", 0.22,
               "topic alignment", "Topic Match"),
    FactorSpec("role_fit", "Role Fit", "Role Fit", 0.18,
               "role compatibility", "Role Fit"),
    FactorSpec("geographic_proximity", "Geographic Proximity", "Proximity", 0.18,
               "geographic proximity", "Geographic Fit"),
    FactorSpec("calendar_fit", "Calendar Fit", "Calendar", 0.12,
               "calendar alignment", "Calendar Fit"),
    FactorSpec("volunteer_fatigue", "Volunteer Fatigue", "Recovery", 0.10,
               "volunteer recovery", "Recovery Readiness"),
    FactorSpec("historical_conversion", "Historical Conversion", "History", 0.05,
               "engagement history", "Engagement History"),
    FactorSpec("student_interest", "Student Interest", "Student Int.", 0.05,
               "student interest potential", "Student Interest"),
    FactorSpec("event_urgency", "Event Urgency", "Urgency", 0.05,
               "scheduling urgency", "Event Urgency"),
    FactorSpec("coverage_diversity", "Coverage Diversity", "Coverage", 0.05,
               "assignment diversity", "Coverage Balance"),
)

# Derived constants — identical values to pre-refactor
FACTOR_KEYS: Final[tuple[str, ...]] = tuple(f.key for f in FACTOR_REGISTRY)
DEFAULT_WEIGHTS: Final[dict[str, float]] = {f.key: f.default_weight for f in FACTOR_REGISTRY}
FACTOR_DISPLAY_LABELS: Final[dict[str, str]] = {f.key: f.display_label for f in FACTOR_REGISTRY}
FACTOR_SHORT_LABELS: Final[dict[str, str]] = {f.key: f.short_label for f in FACTOR_REGISTRY}
FACTOR_PROMPT_LABELS: Final[dict[str, str]] = {f.key: f.prompt_label for f in FACTOR_REGISTRY}
FACTOR_EMAIL_ALIASES: Final[dict[str, str]] = {f.key: f.email_alias for f in FACTOR_REGISTRY}
OPTIMIZER_REASON_WEIGHT_BUMP: Final[float] = float(
    os.getenv("OPTIMIZER_REASON_WEIGHT_BUMP", "0.03")
)
OPTIMIZER_MAX_FACTOR_DELTA: Final[float] = float(
    os.getenv("OPTIMIZER_MAX_FACTOR_DELTA", "0.08")
)
OPTIMIZER_TARGET_RATING: Final[float] = float(
    os.getenv("OPTIMIZER_TARGET_RATING", "4.2")
)

# ---------- Metro Regions ----------
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
# Values: 1.0 = same region, 0.0 = opposite ends.
# Symmetric matrix keyed by canonical region names.
GEO_PROXIMITY: Final[dict[tuple[str, str], float]] = {
    # Ventura / Thousand Oaks
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
    # Los Angeles — West
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
    # Los Angeles — East
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
    # Los Angeles — North
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
    # Los Angeles — Long Beach
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
    # Los Angeles (bare)
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
    # San Francisco
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
    # San Diego
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
    # Portland
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
    # Seattle
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
    # Orange County / Long Beach
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
EVENT_REGION_MAP: Final[dict[str, str]] = {
    "Portland": "Portland",
    "San Diego": "San Diego",
    "Los Angeles": "Los Angeles",
    "San Francisco": "San Francisco",
    "Seattle": "Seattle",
    "Ventura / Thousand Oaks": "Ventura / Thousand Oaks",
    "Orange County / Long Beach": "Orange County / Long Beach",
    "Cal Poly Pomona": "Los Angeles — East",
    "CPP": "Los Angeles — East",
}

DEFAULT_EVENT_REGION: Final[str] = "Los Angeles — East"

# ---------- Student Interest Category Weights ----------
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

DEFAULT_CATEGORY_INTEREST: Final[float] = 0.50

# ---------- Role Aliases ----------
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

# ---------- Region Coordinates (lat, lng) ----------
# Centroid coordinates for speaker metro regions and university campuses.
# Used by geographic_proximity geodesic fallback and expansion map visualization.
REGION_COORDINATES: Final[dict[str, tuple[float, float]]] = {
    "Ventura / Thousand Oaks": (34.2164, -119.0376),
    "Los Angeles — West":     (34.0259, -118.4965),
    "Los Angeles":            (34.0522, -118.2437),
    "Los Angeles — North":    (34.1808, -118.3090),
    "Los Angeles — East":     (34.0579, -117.8214),
    "Los Angeles — Long Beach": (33.7701, -118.1937),
    "Orange County / Long Beach": (33.7175, -117.8311),
    "San Francisco":          (37.7749, -122.4194),
    "Portland":               (45.5152, -122.6784),
    "San Diego":              (32.7157, -117.1611),
    "Seattle":                (47.6062, -122.3321),
}

UNIVERSITY_COORDINATES: Final[dict[str, tuple[float, float]]] = {
    "UCLA":                   (34.0689, -118.4452),
    "SDSU":                   (32.7757, -117.0719),
    "UC Davis":               (38.5382, -121.7617),
    "USC":                    (34.0224, -118.2851),
    "Portland State":         (45.5116, -122.6857),
    "Cal Poly Pomona":        (34.0565, -117.8215),
    "CSULB":                  (33.7838, -118.1141),
    "UC San Diego":           (32.8801, -117.2340),
    "UW (Seattle)":           (47.6553, -122.3035),
    "USF":                    (37.7765, -122.4506),
    "SFSU":                   (37.7219, -122.4782),
}

MAX_FALLBACK_DISTANCE_MILES: Final[float] = 600.0

# ---------- Historical Conversion Defaults ----------
DEFAULT_HISTORICAL_CONVERSION: Final[float] = 0.50

# ---------- Explanation Config ----------
EXPLANATION_CACHE_DIR: Final[str] = str(CACHE_DIR / "explanations")
EXPLANATION_MODEL: Final[str] = GEMINI_TEXT_MODEL
EXPLANATION_MAX_TOKENS: Final[int] = 250
EXPLANATION_TEMPERATURE: Final[float] = 0.4


# ---------- Email Generation Config ----------
# ---------- Extraction Config ----------
EXTRACTION_CACHE_DIR: Final[str] = str(CACHE_DIR / "extractions")
EXTRACTION_MODEL: Final[str] = GEMINI_TEXT_MODEL
EXTRACTION_MAX_TOKENS: Final[int] = 4000
EXTRACTION_TEMPERATURE: Final[float] = 0.1

EMAIL_CACHE_DIR: Final[str] = str(CACHE_DIR / "emails")
EMAIL_MODEL: Final[str] = GEMINI_TEXT_MODEL
EMAIL_MAX_TOKENS: Final[int] = 500
EMAIL_TEMPERATURE: Final[float] = 0.7


# --- Validation ---
def has_gemini_api_key() -> bool:
    """Return whether a non-placeholder Gemini API key is configured."""
    return bool(GEMINI_API_KEY and GEMINI_API_KEY != "AIza...")


def validate_config(require_gemini: bool = False) -> list[str]:
    """Return list of configuration errors. Empty list means all good."""
    errors = []
    if require_gemini and not has_gemini_api_key():
        errors.append("GEMINI_API_KEY is not set or is still the placeholder value")
    if not DATA_DIR.exists():
        errors.append(f"DATA_DIR does not exist: {DATA_DIR}")
    for csv_name in [SPEAKER_PROFILES_CSV, CPP_EVENTS_CSV, CPP_COURSES_CSV, EVENT_CALENDAR_CSV]:
        csv_path = DATA_DIR / csv_name
        if not csv_path.exists():
            errors.append(f"Required data file missing: {csv_path}")
    return errors
