"""Tests for shared utility helpers."""

from src.utils import (
    format_course_display_name,
    format_course_identifier,
    normalize_course_section,
    summarize_missing_keys,
)


def test_normalize_course_section_zero_pads_numeric_values() -> None:
    assert normalize_course_section("1") == "01"
    assert normalize_course_section(2) == "02"


def test_format_course_identifier_uses_canonical_course_section() -> None:
    assert format_course_identifier("IBM 4121", "1") == "IBM 4121-01"


def test_format_course_display_name_includes_canonical_section_and_title() -> None:
    assert (
        format_course_display_name("IBM 4121", "1", "Intl Marketing Research")
        == "IBM 4121-01: Intl Marketing Research"
    )


def test_summarize_missing_keys_reports_count_and_examples() -> None:
    missing_count, examples = summarize_missing_keys(
        expected_keys=["A", "B", "C"],
        loaded_keys=["A"],
        sample_size=2,
    )

    assert missing_count == 2
    assert examples == ["B", "C"]
