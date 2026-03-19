"""Tests for the Discovery tab UI component."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Test: UNIVERSITY_TARGETS importable from scraper
# ---------------------------------------------------------------------------


class TestUniversityConfigsAvailable:
    def test_university_targets_importable(self) -> None:
        from src.scraping.scraper import UNIVERSITY_TARGETS

        assert isinstance(UNIVERSITY_TARGETS, dict)
        assert len(UNIVERSITY_TARGETS) > 0

    def test_each_target_has_required_keys(self) -> None:
        from src.scraping.scraper import UNIVERSITY_TARGETS

        for name, cfg in UNIVERSITY_TARGETS.items():
            assert "url" in cfg, f"{name} missing 'url'"
            assert "method" in cfg, f"{name} missing 'method'"
            assert "label" in cfg, f"{name} missing 'label'"


# ---------------------------------------------------------------------------
# Test: Add-to-matching transforms event data
# ---------------------------------------------------------------------------


class TestAddToMatchingTransform:
    def test_transforms_extracted_event_to_matching_format(self) -> None:
        from src.ui.discovery_tab import transform_event_for_matching

        extracted: dict[str, Any] = {
            "event_name": "Spring Hackathon 2026",
            "category": "hackathon",
            "date_or_recurrence": "2026-04-20",
            "volunteer_roles": ["judge", "mentor"],
            "primary_audience": "undergraduate CS students",
            "contact_name": "Dr. Chen",
            "contact_email": "chen@ucla.edu",
            "url": "https://career.ucla.edu/events/hackathon",
        }

        result = transform_event_for_matching(extracted, university="UCLA")

        assert result["Event / Program"] == "Spring Hackathon 2026"
        assert result["Category"] == "hackathon"
        assert "judge" in result["Volunteer Roles (fit)"]
        assert result["Primary Audience"] == "undergraduate CS students"
        assert result["Host / Unit"] == "UCLA"
        assert result["source"] == "discovery"

    def test_handles_missing_optional_fields(self) -> None:
        from src.ui.discovery_tab import transform_event_for_matching

        extracted: dict[str, Any] = {
            "event_name": "Career Fair",
            "category": "career_fair",
            "date_or_recurrence": "2026-05-01",
            "volunteer_roles": ["speaker"],
            "primary_audience": "all majors",
            "contact_name": None,
            "contact_email": None,
            "url": "https://example.edu/fair",
        }

        result = transform_event_for_matching(extracted, university="USC")
        assert result["Event / Program"] == "Career Fair"
        assert result["Host / Unit"] == "USC"


# ---------------------------------------------------------------------------
# Test: Custom URL validation
# ---------------------------------------------------------------------------


class TestCustomUrlValidation:
    @patch("src.ui.discovery_tab.validate_public_demo_url")
    def test_validate_called_for_custom_url(
        self, mock_validate: MagicMock
    ) -> None:
        from src.ui.discovery_tab import validate_custom_url

        validate_custom_url("https://example.edu/events")
        mock_validate.assert_called_once_with("https://example.edu/events")

    @patch("src.ui.discovery_tab.validate_public_demo_url")
    def test_returns_error_on_invalid_url(
        self, mock_validate: MagicMock
    ) -> None:
        from src.ui.discovery_tab import validate_custom_url

        mock_validate.side_effect = ValueError("Custom URL must use http://")
        result = validate_custom_url("ftp://bad-url")
        assert result is not None
        assert "http://" in result


# ---------------------------------------------------------------------------
# Test: Discovery results formatted for DataFrame
# ---------------------------------------------------------------------------


class TestDiscoveryResultsFormatted:
    def test_formats_events_for_dataframe(self) -> None:
        from src.ui.discovery_tab import format_events_for_dataframe

        events: list[dict[str, Any]] = [
            {
                "event_name": "Hackathon A",
                "category": "hackathon",
                "date_or_recurrence": "2026-04-20",
                "volunteer_roles": ["judge", "mentor"],
                "primary_audience": "CS students",
                "contact_name": "Alice",
                "contact_email": "alice@uni.edu",
                "url": "https://uni.edu/hack",
            },
            {
                "event_name": "Career Fair B",
                "category": "career_fair",
                "date_or_recurrence": "2026-05-01",
                "volunteer_roles": ["speaker"],
                "primary_audience": "all majors",
                "contact_name": None,
                "contact_email": None,
                "url": "https://uni.edu/fair",
            },
        ]

        df = format_events_for_dataframe(events)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "Event Name" in df.columns
        assert "Category" in df.columns
        assert "Date" in df.columns
        assert "Roles Needed" in df.columns
        assert "Audience" in df.columns
        assert "Contact" in df.columns
        assert df.iloc[0]["Event Name"] == "Hackathon A"
        assert "judge" in df.iloc[0]["Roles Needed"]

    def test_empty_events_returns_empty_dataframe(self) -> None:
        from src.ui.discovery_tab import format_events_for_dataframe

        df = format_events_for_dataframe([])
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
