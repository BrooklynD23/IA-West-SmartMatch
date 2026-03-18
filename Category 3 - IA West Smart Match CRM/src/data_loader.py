"""Load and validate all 4 CSV data sources for IA SmartMatch."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import (
    CPP_COURSES_CSV,
    CPP_EVENTS_CSV,
    DATA_DIR,
    EVENT_CALENDAR_CSV,
    SPEAKER_PROFILES_CSV,
)

logger = logging.getLogger(__name__)


# ── Column Schemas ──────────────────────────────────────────────────────────

SPEAKER_COLUMNS = {
    "Name": {"dtype": "str", "nullable": False, "description": "Full name of board member"},
    "Board Role": {"dtype": "str", "nullable": False, "description": "IA West board role title"},
    "Metro Region": {"dtype": "str", "nullable": False, "description": "Geographic metro area"},
    "Company": {"dtype": "str", "nullable": True, "description": "Current employer or firm"},
    "Title": {"dtype": "str", "nullable": True, "description": "Professional job title"},
    "Expertise Tags": {"dtype": "str", "nullable": False, "description": "Comma-separated expertise keywords"},
}

EVENT_COLUMNS = {
    "Event / Program": {"dtype": "str", "nullable": False, "description": "Event or program name"},
    "Category": {"dtype": "str", "nullable": False, "description": "Event type category"},
    "Recurrence (typical)": {"dtype": "str", "nullable": True, "description": "How often the event recurs"},
    "Host / Unit": {"dtype": "str", "nullable": True, "description": "Hosting department or org"},
    "Volunteer Roles (fit)": {"dtype": "str", "nullable": False, "description": "Semicolon-separated volunteer roles"},
    "Primary Audience": {"dtype": "str", "nullable": False, "description": "Target student audience"},
    "Public URL": {"dtype": "str", "nullable": True, "description": "Public-facing event page URL"},
    "Point(s) of Contact (published)": {"dtype": "str", "nullable": True, "description": "Contact name(s)"},
    "Contact Email / Phone (published)": {"dtype": "str", "nullable": True, "description": "Contact email or phone"},
}

COURSE_COLUMNS = {
    "Instructor": {"dtype": "str", "nullable": False, "description": "Faculty member name"},
    "Course": {"dtype": "str", "nullable": False, "description": "Course code (e.g., IBM 3302)"},
    "Section": {"dtype": "str", "nullable": False, "description": "Section number"},
    "Title": {"dtype": "str", "nullable": False, "description": "Course title"},
    "Days": {"dtype": "str", "nullable": False, "description": "Meeting days (e.g., T TH, M W)"},
    "Start Time": {"dtype": "str", "nullable": True, "description": "Class start time"},
    "End Time": {"dtype": "str", "nullable": True, "description": "Class end time"},
    "Enrl Cap": {"dtype": "int", "nullable": False, "description": "Enrollment capacity"},
    "Mode": {"dtype": "str", "nullable": False, "description": "Delivery mode (Face-to-Face, Hybrid Sync, etc.)"},
    "Guest Lecture Fit": {"dtype": "str", "nullable": False, "description": "Fit rating: High, Medium, Low"},
}

CALENDAR_COLUMNS = {
    "IA Event Date": {"dtype": "datetime", "nullable": False, "description": "Event date in YYYY-MM-DD format"},
    "Region": {"dtype": "str", "nullable": False, "description": "IA West metro region"},
    "Nearby Universities": {"dtype": "str", "nullable": False, "description": "Comma-separated university names"},
    "Suggested Lecture Window": {"dtype": "str", "nullable": True, "description": "Optimal guest lecture date range"},
    "Course Alignment": {"dtype": "str", "nullable": True, "description": "Aligned course topics"},
}


# ── Data Classes ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class DataQualityResult:
    """Immutable result of a data quality check for one CSV."""

    file_name: str
    row_count: int
    column_count: int
    expected_columns: list[str]
    actual_columns: list[str]
    missing_columns: list[str]
    extra_columns: list[str]
    null_counts: dict[str, int]
    encoding_used: str
    issues: list[str]


@dataclass(frozen=True)
class LoadedDatasets:
    """Container for all 4 loaded DataFrames."""

    speakers: pd.DataFrame
    events: pd.DataFrame
    courses: pd.DataFrame
    calendar: pd.DataFrame
    quality_results: list[DataQualityResult]


# ── Loading Functions ───────────────────────────────────────────────────────

def _try_read_csv(file_path: Path) -> tuple[pd.DataFrame, str]:
    """
    Attempt to read a CSV with multiple encodings.

    Returns:
        Tuple of (DataFrame, encoding_used).

    Raises:
        ValueError: If no encoding succeeds.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df, enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Failed to read {file_path} with encodings: {encodings}")


def _validate_columns(
    df: pd.DataFrame,
    expected_schema: dict[str, dict],
    file_name: str,
    extra_issues: Optional[list[str]] = None,
) -> DataQualityResult:
    """
    Validate a DataFrame against its expected column schema.

    Returns:
        DataQualityResult with all quality metrics.
    """
    expected_cols = list(expected_schema.keys())
    actual_cols = list(df.columns)
    missing_cols = [c for c in expected_cols if c not in actual_cols]
    extra_cols = [c for c in actual_cols if c not in expected_cols]

    null_counts = {}
    issues = list(extra_issues or [])

    for col_name, col_spec in expected_schema.items():
        if col_name not in df.columns:
            continue
        null_count = int(df[col_name].isna().sum())
        null_counts[col_name] = null_count
        expected_dtype = col_spec.get("dtype")
        if expected_dtype == "str":
            non_null_values = df[col_name].dropna()
            if not non_null_values.map(lambda value: isinstance(value, str)).all():
                issues.append(f"Column '{col_name}' expected dtype str but contains non-string values")
        elif expected_dtype == "int" and not pd.api.types.is_integer_dtype(df[col_name]):
            issues.append(f"Column '{col_name}' expected dtype int but found {df[col_name].dtype}")
        elif expected_dtype == "datetime" and not pd.api.types.is_datetime64_any_dtype(df[col_name]):
            issues.append(f"Column '{col_name}' expected dtype datetime but found {df[col_name].dtype}")

        if not col_spec["nullable"] and null_count > 0:
            issues.append(
                f"Column '{col_name}' has {null_count} null(s) but is marked non-nullable"
            )

    if missing_cols:
        issues.append(f"Missing expected columns: {missing_cols}")
    if extra_cols:
        issues.append(f"Unexpected extra columns: {extra_cols}")

    return DataQualityResult(
        file_name=file_name,
        row_count=len(df),
        column_count=len(df.columns),
        expected_columns=expected_cols,
        actual_columns=actual_cols,
        missing_columns=missing_cols,
        extra_columns=extra_cols,
        null_counts=null_counts,
        encoding_used="",  # filled by caller
        issues=issues,
    )


def _with_encoding(quality: DataQualityResult, encoding: str) -> DataQualityResult:
    """Return a new DataQualityResult with the encoding field set."""
    return DataQualityResult(
        file_name=quality.file_name,
        row_count=quality.row_count,
        column_count=quality.column_count,
        expected_columns=quality.expected_columns,
        actual_columns=quality.actual_columns,
        missing_columns=quality.missing_columns,
        extra_columns=quality.extra_columns,
        null_counts=quality.null_counts,
        encoding_used=encoding,
        issues=quality.issues,
    )


def load_speakers(data_dir: Optional[Path] = None) -> tuple[pd.DataFrame, DataQualityResult]:
    """Load and validate speaker profiles CSV."""
    data_dir = data_dir or DATA_DIR
    file_path = data_dir / SPEAKER_PROFILES_CSV
    df, encoding = _try_read_csv(file_path)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    quality = _validate_columns(df, SPEAKER_COLUMNS, SPEAKER_PROFILES_CSV)
    return df, _with_encoding(quality, encoding)


def load_events(data_dir: Optional[Path] = None) -> tuple[pd.DataFrame, DataQualityResult]:
    """Load and validate CPP events contacts CSV."""
    data_dir = data_dir or DATA_DIR
    file_path = data_dir / CPP_EVENTS_CSV
    df, encoding = _try_read_csv(file_path)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    quality = _validate_columns(df, EVENT_COLUMNS, CPP_EVENTS_CSV)
    return df, _with_encoding(quality, encoding)


def load_courses(data_dir: Optional[Path] = None) -> tuple[pd.DataFrame, DataQualityResult]:
    """Load and validate CPP course schedule CSV."""
    data_dir = data_dir or DATA_DIR
    file_path = data_dir / CPP_COURSES_CSV
    df, encoding = _try_read_csv(file_path)
    extra_issues: list[str] = []

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    if "Enrl Cap" in df.columns:
        raw_enrollment = df["Enrl Cap"].copy()
        parsed_enrollment = pd.to_numeric(df["Enrl Cap"], errors="coerce")
        invalid_count = int(raw_enrollment.notna().sum() - parsed_enrollment.notna().sum())
        if invalid_count > 0:
            extra_issues.append(f"Column 'Enrl Cap' has {invalid_count} invalid numeric value(s)")
        df["Enrl Cap"] = parsed_enrollment.fillna(0).astype(int)

    quality = _validate_columns(df, COURSE_COLUMNS, CPP_COURSES_CSV, extra_issues=extra_issues)
    return df, _with_encoding(quality, encoding)


def load_calendar(data_dir: Optional[Path] = None) -> tuple[pd.DataFrame, DataQualityResult]:
    """Load and validate IA event calendar CSV."""
    data_dir = data_dir or DATA_DIR
    file_path = data_dir / EVENT_CALENDAR_CSV
    df, encoding = _try_read_csv(file_path)
    extra_issues: list[str] = []

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    if "IA Event Date" in df.columns:
        raw_dates = df["IA Event Date"].copy()
        parsed_dates = pd.to_datetime(df["IA Event Date"], errors="coerce")
        invalid_count = int(raw_dates.notna().sum() - parsed_dates.notna().sum())
        if invalid_count > 0:
            extra_issues.append(f"Column 'IA Event Date' has {invalid_count} invalid datetime value(s)")
        df["IA Event Date"] = parsed_dates

    quality = _validate_columns(df, CALENDAR_COLUMNS, EVENT_CALENDAR_CSV, extra_issues=extra_issues)
    return df, _with_encoding(quality, encoding)


def load_all(data_dir: Optional[Path] = None) -> LoadedDatasets:
    """
    Load all 4 data sources and return them with quality results.

    Returns:
        LoadedDatasets with all DataFrames and quality audit results.

    Raises:
        ValueError: If any CSV cannot be read.
    """
    speakers, sq = load_speakers(data_dir)
    events, eq = load_events(data_dir)
    courses, cq = load_courses(data_dir)
    calendar, calq = load_calendar(data_dir)

    return LoadedDatasets(
        speakers=speakers,
        events=events,
        courses=courses,
        calendar=calendar,
        quality_results=[sq, eq, cq, calq],
    )


def generate_quality_report(datasets: LoadedDatasets) -> str:
    """
    Generate a Markdown quality report from loaded datasets.

    Returns:
        String containing the full Markdown report.
    """
    lines = [
        "# Data Quality Report — IA SmartMatch",
        "",
        "**Generated:** auto",
        f"**Total records:** {sum(qr.row_count for qr in datasets.quality_results)}",
        "",
        "---",
        "",
    ]

    for qr in datasets.quality_results:
        lines.append(f"## {qr.file_name}")
        lines.append("")
        lines.append(f"- **Rows:** {qr.row_count}")
        lines.append(f"- **Columns:** {qr.column_count}")
        lines.append(f"- **Encoding:** {qr.encoding_used}")
        lines.append("")

        if qr.null_counts:
            lines.append("### Null Values")
            lines.append("")
            lines.append("| Column | Null Count |")
            lines.append("|--------|-----------|")
            for col, count in qr.null_counts.items():
                flag = " **!!**" if count > 0 else ""
                lines.append(f"| {col} | {count}{flag} |")
            lines.append("")

        if qr.issues:
            lines.append("### Issues")
            lines.append("")
            for issue in qr.issues:
                lines.append(f"- {issue}")
            lines.append("")
        else:
            lines.append("### Issues")
            lines.append("")
            lines.append("None detected.")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("## Join Key Alignment")
    lines.append("")
    lines.append("### Speaker Metro Region <-> Calendar Region")
    lines.append("")
    lines.append("| Speaker Metro Regions | Calendar Regions | Aligned? |")
    lines.append("|----------------------|-----------------|----------|")
    lines.append("| *(populated at runtime)* | *(populated at runtime)* | *(check)* |")
    lines.append("")
    lines.append("### Course Guest Lecture Fit Distribution")
    lines.append("")
    lines.append("| Fit Level | Count |")
    lines.append("|-----------|-------|")
    lines.append("| *(populated at runtime)* | *(count)* |")
    lines.append("")

    return "\n".join(lines)
