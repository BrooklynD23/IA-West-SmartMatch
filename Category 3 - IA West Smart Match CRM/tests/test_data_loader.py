"""Tests for data loading and validation — Sprint 0 A0.2."""

import textwrap
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    DataQualityResult,
    LoadedDatasets,
    _try_read_csv,
    _validate_columns,
    generate_quality_report,
    load_all,
    load_calendar,
    load_courses,
    load_events,
    load_speakers,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

SPEAKER_CSV = textwrap.dedent("""\
    Name,Board Role,Metro Region,Company,Title,Expertise Tags
    Alice Smith,President,Los Angeles — West,AcmeCo,SVP Sales,"sales, innovation"
    Bob Jones,Treasurer,San Francisco,BetaCo,Director,"research, analytics"
""")

EVENT_CSV = textwrap.dedent("""\
    Event / Program,Category,Recurrence (typical),Host / Unit,Volunteer Roles (fit),Primary Audience,Public URL,Point(s) of Contact (published),Contact Email / Phone (published)
    Hackathon 2026,AI / Hackathon,Annual,College of Business,Judge; Mentor,Students (business/tech),http://example.com,Contact Name,contact@example.com
    Case Comp,Case competition,Annual,Business Dept,Judge,Students,http://example2.com,Jane Doe,jane@example.com
""")

COURSE_CSV = textwrap.dedent("""\
    Instructor,Course,Section,Title,Days,Start Time,End Time,Enrl Cap,Mode,Guest Lecture Fit
    Dr. Lee,IBM 3302,01,Marketing Research,T TH,9:00 AM,10:15 AM,30,Face-to-Face,High
    Dr. Kim,IBM 4121,02,Intl Marketing Research,M W,1:00 PM,2:15 PM,25,Hybrid Sync,Medium
""")

CALENDAR_CSV = textwrap.dedent("""\
    IA Event Date,Region,Nearby Universities,Suggested Lecture Window,Course Alignment
    2026-04-16,Portland,"Portland State, U of Oregon",Apr 7-14,"Marketing Research"
    2026-05-14,San Diego,"SDSU, USD",May 5-12,Analytics capstones
""")


@pytest.fixture()
def data_dir(tmp_path: Path) -> Path:
    """Create a temp data directory with all 4 CSV files."""
    (tmp_path / "data_speaker_profiles.csv").write_text(SPEAKER_CSV, encoding="utf-8")
    (tmp_path / "data_cpp_events_contacts.csv").write_text(EVENT_CSV, encoding="utf-8")
    (tmp_path / "data_cpp_course_schedule.csv").write_text(COURSE_CSV, encoding="utf-8")
    (tmp_path / "data_event_calendar.csv").write_text(CALENDAR_CSV, encoding="utf-8")
    return tmp_path


# ── Tests: _try_read_csv ──────────────────────────────────────────────────────

class TestTryReadCsv:
    def test_reads_utf8_csv(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test.csv"
        csv_path.write_text("col1,col2\nval1,val2\n", encoding="utf-8")
        df, encoding = _try_read_csv(csv_path)
        assert len(df) == 1
        assert encoding == "utf-8"

    def test_falls_back_to_latin1(self, tmp_path: Path) -> None:
        csv_path = tmp_path / "test.csv"
        # Write a file with latin-1 encoded content (non-UTF-8 byte)
        csv_path.write_bytes(b"col1,col2\nval\xe9,val2\n")
        df, encoding = _try_read_csv(csv_path)
        assert len(df) == 1
        assert encoding in ("utf-8-sig", "latin-1")

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(Exception):
            _try_read_csv(tmp_path / "nonexistent.csv")


# ── Tests: _validate_columns ──────────────────────────────────────────────────

class TestValidateColumns:
    def test_detects_missing_columns(self) -> None:
        df = pd.DataFrame({"col_a": ["x"]})
        schema = {
            "col_a": {"dtype": "str", "nullable": False, "description": ""},
            "col_b": {"dtype": "str", "nullable": False, "description": ""},
        }
        result = _validate_columns(df, schema, "test.csv")
        assert "col_b" in result.missing_columns
        assert any("Missing expected columns" in i for i in result.issues)

    def test_detects_extra_columns(self) -> None:
        df = pd.DataFrame({"col_a": ["x"], "extra_col": ["y"]})
        schema = {"col_a": {"dtype": "str", "nullable": False, "description": ""}}
        result = _validate_columns(df, schema, "test.csv")
        assert "extra_col" in result.extra_columns

    def test_detects_nulls_in_non_nullable(self) -> None:
        df = pd.DataFrame({"col_a": ["x", None]})
        schema = {"col_a": {"dtype": "str", "nullable": False, "description": ""}}
        result = _validate_columns(df, schema, "test.csv")
        assert result.null_counts["col_a"] == 1
        assert any("null" in i.lower() for i in result.issues)

    def test_no_issues_for_valid_df(self) -> None:
        df = pd.DataFrame({"col_a": ["x", "y"]})
        schema = {"col_a": {"dtype": "str", "nullable": False, "description": ""}}
        result = _validate_columns(df, schema, "test.csv")
        assert result.issues == []

    def test_detects_dtype_mismatch(self) -> None:
        df = pd.DataFrame({"col_a": ["not-an-int"]})
        schema = {"col_a": {"dtype": "int", "nullable": False, "description": ""}}
        result = _validate_columns(df, schema, "test.csv")
        assert any("expected dtype" in issue for issue in result.issues)


# ── Tests: load_* functions ────────────────────────────────────────────────────

class TestLoadFunctions:
    def test_load_speakers_row_count(self, data_dir: Path) -> None:
        df, quality = load_speakers(data_dir)
        assert len(df) == 2
        assert quality.file_name == "data_speaker_profiles.csv"

    def test_load_events_row_count(self, data_dir: Path) -> None:
        df, quality = load_events(data_dir)
        assert len(df) == 2

    def test_load_courses_row_count(self, data_dir: Path) -> None:
        df, quality = load_courses(data_dir)
        assert len(df) == 2

    def test_load_courses_enrl_cap_is_int(self, data_dir: Path) -> None:
        df, _ = load_courses(data_dir)
        assert df["Enrl Cap"].dtype == "int64"

    def test_load_courses_reports_invalid_enrl_cap_values(self, data_dir: Path) -> None:
        invalid_course_csv = textwrap.dedent("""\
            Instructor,Course,Section,Title,Days,Start Time,End Time,Enrl Cap,Mode,Guest Lecture Fit
            Dr. Lee,IBM 3302,01,Marketing Research,T TH,9:00 AM,10:15 AM,not-a-number,Face-to-Face,High
        """)
        (data_dir / "data_cpp_course_schedule.csv").write_text(invalid_course_csv, encoding="utf-8")

        df, quality = load_courses(data_dir)

        assert df["Enrl Cap"].iloc[0] == 0
        assert any("Enrl Cap" in issue and "invalid numeric" in issue for issue in quality.issues)

    def test_load_calendar_row_count(self, data_dir: Path) -> None:
        df, quality = load_calendar(data_dir)
        assert len(df) == 2

    def test_load_calendar_date_parsed(self, data_dir: Path) -> None:
        df, _ = load_calendar(data_dir)
        assert pd.api.types.is_datetime64_any_dtype(df["IA Event Date"])

    def test_string_columns_stripped(self, data_dir: Path) -> None:
        # Add whitespace to test stripping
        csv_with_spaces = "Name,Board Role,Metro Region,Company,Title,Expertise Tags\n  Alice  , President , LA ,AcmeCo,SVP, tags\n"
        (data_dir / "data_speaker_profiles.csv").write_text(csv_with_spaces)
        df, _ = load_speakers(data_dir)
        assert df["Name"].iloc[0] == "Alice"
        assert df["Board Role"].iloc[0] == "President"


# ── Tests: load_all ────────────────────────────────────────────────────────────

class TestLoadAll:
    def test_returns_loaded_datasets(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        assert isinstance(datasets, LoadedDatasets)

    def test_all_four_dataframes_present(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        assert len(datasets.speakers) > 0
        assert len(datasets.events) > 0
        assert len(datasets.courses) > 0
        assert len(datasets.calendar) > 0

    def test_quality_results_has_four_entries(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        assert len(datasets.quality_results) == 4

    def test_quality_result_is_frozen(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        with pytest.raises(Exception):
            datasets.quality_results[0].row_count = 999  # type: ignore[misc]


# ── Tests: generate_quality_report ────────────────────────────────────────────

class TestGenerateQualityReport:
    def test_report_contains_file_names(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        report = generate_quality_report(datasets)
        assert "data_speaker_profiles.csv" in report
        assert "data_cpp_events_contacts.csv" in report
        assert "data_cpp_course_schedule.csv" in report
        assert "data_event_calendar.csv" in report

    def test_report_contains_row_counts(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        report = generate_quality_report(datasets)
        assert "**Rows:**" in report

    def test_report_is_markdown(self, data_dir: Path) -> None:
        datasets = load_all(data_dir)
        report = generate_quality_report(datasets)
        assert report.startswith("# Data Quality Report")
