"""Tests for individual scoring factor functions in src/matching/factors.py."""

from datetime import date, datetime

import numpy as np
import pandas as pd
import pytest

from src.matching.factors import (
    _haversine_miles,
    _parse_date_flexible,
    _resolve_event_region,
    calendar_fit,
    geographic_proximity,
    historical_conversion,
    role_fit,
    student_interest,
    topic_relevance,
)


class TestTopicRelevance:
    """Cosine-similarity-based topic relevance scoring."""

    def test_identical_vectors_near_one(self) -> None:
        v = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        assert topic_relevance(v, v) == pytest.approx(1.0, abs=1e-5)

    def test_orthogonal_vectors_near_zero(self) -> None:
        a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        assert topic_relevance(a, b) == pytest.approx(0.0, abs=1e-5)

    def test_none_speaker_returns_zero(self) -> None:
        b = np.array([1.0, 0.0], dtype=np.float32)
        assert topic_relevance(None, b) == 0.0

    def test_none_event_returns_zero(self) -> None:
        a = np.array([1.0, 0.0], dtype=np.float32)
        assert topic_relevance(a, None) == 0.0

    def test_empty_speaker_returns_zero(self) -> None:
        a = np.array([], dtype=np.float32)
        b = np.array([1.0, 2.0], dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_empty_event_returns_zero(self) -> None:
        a = np.array([1.0, 2.0], dtype=np.float32)
        b = np.array([], dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_nan_speaker_returns_zero(self) -> None:
        a = np.array([np.nan, 1.0], dtype=np.float32)
        b = np.array([1.0, 0.0], dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_nan_event_returns_zero(self) -> None:
        a = np.array([1.0, 0.0], dtype=np.float32)
        b = np.array([np.nan, 1.0], dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_zero_vector_speaker_returns_zero(self) -> None:
        a = np.zeros(3, dtype=np.float32)
        b = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_zero_vector_event_returns_zero(self) -> None:
        a = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        b = np.zeros(3, dtype=np.float32)
        assert topic_relevance(a, b) == 0.0

    def test_result_clipped_to_unit_range(self) -> None:
        rng = np.random.default_rng(42)
        a = rng.standard_normal(128).astype(np.float32)
        b = rng.standard_normal(128).astype(np.float32)
        score = topic_relevance(a, b)
        assert 0.0 <= score <= 1.0

    def test_similar_vectors_high_score(self) -> None:
        a = np.array([1.0, 1.0, 0.0], dtype=np.float32)
        b = np.array([1.0, 1.0, 0.1], dtype=np.float32)
        assert topic_relevance(a, b) > 0.9


class TestRoleFit:
    """Role matching with canonical aliases and fuzzy fallback."""

    def test_exact_match_high_score(self) -> None:
        score = role_fit("Judge", "Judge; Mentor")
        assert score >= 0.5

    def test_alias_match(self) -> None:
        score = role_fit("reviewer", "Judge; Mentor")
        assert score > 0.0

    def test_no_match_low_score(self) -> None:
        score = role_fit("Caterer", "Judge; Mentor")
        assert score < 0.5

    def test_nan_speaker_returns_zero(self) -> None:
        assert role_fit(float("nan"), "Judge") == 0.0

    def test_nan_event_returns_zero(self) -> None:
        assert role_fit("Judge", float("nan")) == 0.0

    def test_empty_speaker_returns_zero(self) -> None:
        assert role_fit("", "Judge; Mentor") == 0.0

    def test_empty_event_returns_zero(self) -> None:
        assert role_fit("Judge", "") == 0.0

    def test_director_implies_speaker(self) -> None:
        score = role_fit("Director of Operations", "Guest Speaker")
        assert score > 0.0

    def test_president_implies_speaker(self) -> None:
        score = role_fit("President", "Speaker; Panelist")
        assert score > 0.0

    def test_treasurer_implies_speaker(self) -> None:
        score = role_fit("Treasurer", "Speaker")
        assert score > 0.0

    def test_fuzzy_matching_partial_overlap(self) -> None:
        score = role_fit("Workshop Leader", "Workshop Lead; Speaker")
        assert score > 0.0

    def test_result_in_unit_range(self) -> None:
        score = role_fit("Judge", "Judge; Mentor; Speaker")
        assert 0.0 <= score <= 1.0

    def test_multiple_event_roles_semicolon(self) -> None:
        score = role_fit("Judge", "Judge; Mentor; Volunteer")
        assert score > 0.0

    def test_multiple_event_roles_comma(self) -> None:
        score = role_fit("Judge", "Judge, Mentor, Volunteer")
        assert score > 0.0

    def test_alias_matching_avoids_word_substring_false_positive(self) -> None:
        score = role_fit("speakerphone support", "Speaker")
        assert score < 0.5


class TestGeographicProximity:
    """Lookup-table-based geographic proximity scoring."""

    def test_same_region_returns_one(self) -> None:
        # Speaker region is the first arg; event region (second arg) goes through
        # _resolve_event_region which maps via EVENT_REGION_MAP / substring match.
        # "Ventura / Thousand Oaks" maps to itself in both lookup paths.
        assert geographic_proximity("Ventura / Thousand Oaks", "Ventura / Thousand Oaks") == 1.0

    def test_known_pair_returns_expected(self) -> None:
        # "Cal Poly Pomona" resolves to "Los Angeles — East" via EVENT_REGION_MAP
        score = geographic_proximity("Ventura / Thousand Oaks", "Cal Poly Pomona")
        assert score == pytest.approx(0.75, abs=0.01)

    def test_unknown_region_returns_default(self) -> None:
        # Unknown event region resolves to DEFAULT_EVENT_REGION ("Los Angeles — East")
        # So this looks up ("Seattle", "Los Angeles — East") which is 0.05
        score = geographic_proximity("Seattle", "Timbuktu")
        assert score == pytest.approx(0.05, abs=0.01)

    def test_empty_speaker_returns_zero(self) -> None:
        assert geographic_proximity("", "Los Angeles — East") == 0.0

    def test_none_speaker_returns_zero(self) -> None:
        assert geographic_proximity(None, "Los Angeles — East") == 0.0

    def test_empty_event_uses_default_region(self) -> None:
        score = geographic_proximity("Los Angeles — East", "")
        assert score == 1.0

    def test_result_in_unit_range(self) -> None:
        score = geographic_proximity("Seattle", "Portland")
        assert 0.0 <= score <= 1.0

    def test_symmetry(self) -> None:
        ab = geographic_proximity("Portland", "Seattle")
        ba = geographic_proximity("Seattle", "Portland")
        assert ab == pytest.approx(ba, abs=0.01)

    def test_resolve_event_region_cal_poly(self) -> None:
        assert _resolve_event_region("Cal Poly Pomona") == "Los Angeles — East"

    def test_resolve_event_region_cpp(self) -> None:
        assert _resolve_event_region("CPP") == "Los Angeles — East"

    def test_resolve_event_region_empty_returns_default(self) -> None:
        assert _resolve_event_region("") == "Los Angeles — East"

    def test_resolve_event_region_known_city(self) -> None:
        assert _resolve_event_region("Portland campus") == "Portland"

    def test_resolve_event_region_prefers_specific_los_angeles_subregion(self) -> None:
        assert _resolve_event_region("Los Angeles — West campus") == "Los Angeles — West"

    def test_resolve_event_region_does_not_collapse_long_beach_to_bare_la(self) -> None:
        assert _resolve_event_region("Los Angeles — Long Beach") == "Los Angeles — Long Beach"


class TestHaversineMiles:
    """Unit tests for the _haversine_miles helper."""

    def test_same_point_returns_zero(self) -> None:
        assert _haversine_miles((34.0, -118.0), (34.0, -118.0)) == pytest.approx(0.0, abs=0.01)

    def test_la_to_sf_roughly_350_miles(self) -> None:
        la = (34.0522, -118.2437)
        sf = (37.7749, -122.4194)
        distance = _haversine_miles(la, sf)
        assert 340.0 < distance < 390.0

    def test_la_to_seattle_roughly_960_miles(self) -> None:
        la = (34.0522, -118.2437)
        seattle = (47.6062, -122.3321)
        distance = _haversine_miles(la, seattle)
        assert 940.0 < distance < 980.0

    def test_symmetry(self) -> None:
        a = (34.0522, -118.2437)
        b = (37.7749, -122.4194)
        assert _haversine_miles(a, b) == pytest.approx(_haversine_miles(b, a), abs=0.01)


class TestGeodesicFallback:
    """Tests for the geodesic distance fallback in geographic_proximity."""

    def test_existing_lookup_pairs_unchanged(self) -> None:
        """All 121 known GEO_PROXIMITY pairs should still use the lookup table."""
        # Spot-check a few known pairs to confirm lookup still takes precedence
        assert geographic_proximity("Seattle", "Portland") == pytest.approx(0.75, abs=0.01)
        assert geographic_proximity("San Diego", "San Diego") == 1.0
        assert geographic_proximity("Los Angeles — West", "Los Angeles — East") == pytest.approx(0.85, abs=0.01)

    def test_fallback_returns_no_coordinates(self) -> None:
        """Speaker region with no coordinates and no lookup entry falls back to 0.3."""
        # "Narnia" is not in REGION_COORDINATES or GEO_PROXIMITY
        score = geographic_proximity("Narnia", "Narnia")
        assert score == pytest.approx(0.3, abs=0.01)

    def test_fallback_near_regions_high_score(self) -> None:
        """Two nearby regions not in lookup table should get a high geodesic score.

        We can't easily create this scenario with existing regions (all are in GEO_PROXIMITY),
        so we test _haversine_miles directly and verify the formula.
        """
        # LA to LA-East: ~30 miles → score = 1.0 - (30/600) = 0.95
        la = (34.0522, -118.2437)
        la_east = (34.0579, -117.8214)
        distance = _haversine_miles(la, la_east)
        expected_score = max(0.0, 1.0 - (distance / 600.0))
        assert expected_score > 0.9  # nearby = high score

    def test_fallback_distant_regions_low_score(self) -> None:
        """Distant regions should produce low geodesic scores."""
        la = (34.0522, -118.2437)
        seattle = (47.6062, -122.3321)
        distance = _haversine_miles(la, seattle)
        expected_score = max(0.0, 1.0 - (distance / 600.0))
        assert expected_score == 0.0  # > 600mi → clamped to 0.0

    def test_fallback_score_in_unit_range(self) -> None:
        """Geodesic fallback scores must be in [0.0, 1.0]."""
        sf = (37.7749, -122.4194)
        sd = (32.7157, -117.1611)
        distance = _haversine_miles(sf, sd)
        score = max(0.0, 1.0 - (distance / 600.0))
        assert 0.0 <= score <= 1.0

    def test_geodesic_path_integration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Integration test: geographic_proximity uses geodesic when coords exist but pair is not in GEO_PROXIMITY.

        Injects a temporary region into REGION_COORDINATES so the lookup table
        misses but the geodesic fallback fires with real coordinates.
        """
        import src.config as config_module

        # "Test Metro" is near LA (~30 mi east) — should produce a high score
        patched_coords = {**config_module.REGION_COORDINATES, "Test Metro": (34.05, -117.75)}
        monkeypatch.setattr(config_module, "REGION_COORDINATES", patched_coords)
        # Also patch the local reference in factors module
        import src.matching.factors as factors_module
        monkeypatch.setattr(factors_module, "REGION_COORDINATES", patched_coords)

        score = geographic_proximity("Test Metro", "Los Angeles")
        # "Test Metro" is ~30 mi from LA → score ≈ 1.0 - (30/600) ≈ 0.95
        assert 0.8 < score < 1.0, f"Expected high geodesic score, got {score}"

    def test_geodesic_path_distant_integration(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Integration test: distant injected region produces low geodesic score."""
        import src.config as config_module

        # "Far Away Metro" near Seattle coords — ~960 mi from LA → score = 0.0
        patched_coords = {**config_module.REGION_COORDINATES, "Far Away Metro": (47.6, -122.3)}
        monkeypatch.setattr(config_module, "REGION_COORDINATES", patched_coords)
        import src.matching.factors as factors_module
        monkeypatch.setattr(factors_module, "REGION_COORDINATES", patched_coords)

        score = geographic_proximity("Far Away Metro", "San Diego")
        # ~1100 mi → clamped to 0.0
        assert score == pytest.approx(0.0, abs=0.05)


class TestCalendarFit:
    """Date/recurrence-based calendar fit scoring."""

    def _make_calendar(
        self, dates: list[str], regions: list[str] | None = None
    ) -> pd.DataFrame:
        data: dict[str, list[str]] = {"IA Event Date": dates}
        if regions is not None:
            data["Region"] = regions
        return pd.DataFrame(data)

    def test_recurrence_monthly(self) -> None:
        score = calendar_fit("Monthly", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.70, abs=0.01)

    def test_recurrence_ongoing(self) -> None:
        score = calendar_fit("ongoing", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.80, abs=0.01)

    def test_recurrence_weekly(self) -> None:
        score = calendar_fit("Weekly", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.80, abs=0.01)

    def test_recurrence_one_time(self) -> None:
        score = calendar_fit("one-time", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.40, abs=0.01)

    def test_recurrence_unknown_string(self) -> None:
        score = calendar_fit("totally random", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.50, abs=0.01)

    def test_specific_date_exact_match(self) -> None:
        cal = self._make_calendar(
            ["2026-04-15"],
            ["Los Angeles — East"],
        )
        score = calendar_fit("2026-04-15", cal, "Los Angeles — East")
        assert score == pytest.approx(1.0, abs=0.01)

    def test_specific_date_close_high_score(self) -> None:
        cal = self._make_calendar(
            ["2026-04-15"],
            ["Los Angeles — East"],
        )
        score = calendar_fit("2026-04-10", cal, "Los Angeles — East")
        assert score > 0.8

    def test_specific_date_far_low_score(self) -> None:
        cal = self._make_calendar(
            ["2026-01-01"],
            ["Los Angeles — East"],
        )
        score = calendar_fit("2026-06-15", cal, "Los Angeles — East")
        assert score <= 0.30

    def test_none_calendar_returns_half(self) -> None:
        score = calendar_fit("2026-04-15", None, "Los Angeles — East")
        assert score == pytest.approx(0.50, abs=0.01)

    def test_empty_calendar_returns_half(self) -> None:
        score = calendar_fit("2026-04-15", pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.50, abs=0.01)

    def test_none_date_empty_recurrence(self) -> None:
        score = calendar_fit(None, pd.DataFrame(), "Los Angeles — East")
        assert score == pytest.approx(0.50, abs=0.01)

    def test_result_in_unit_range(self) -> None:
        cal = self._make_calendar(
            ["2026-04-15", "2026-05-20"],
            ["Los Angeles — East", "Portland"],
        )
        score = calendar_fit("2026-04-20", cal, "Los Angeles — East")
        assert 0.0 <= score <= 1.0

    def test_parse_date_iso(self) -> None:
        assert _parse_date_flexible("2026-04-15") == date(2026, 4, 15)

    def test_parse_date_us_format(self) -> None:
        assert _parse_date_flexible("04/15/2026") == date(2026, 4, 15)

    def test_parse_date_long_format(self) -> None:
        assert _parse_date_flexible("April 15, 2026") == date(2026, 4, 15)

    def test_parse_date_datetime_object(self) -> None:
        dt = datetime(2026, 4, 15, 10, 30)
        assert _parse_date_flexible(dt) == date(2026, 4, 15)

    def test_parse_date_date_object(self) -> None:
        d = date(2026, 4, 15)
        assert _parse_date_flexible(d) == d

    def test_parse_date_invalid_returns_none(self) -> None:
        assert _parse_date_flexible("not a date") is None

    def test_parse_date_none_returns_none(self) -> None:
        assert _parse_date_flexible(None) is None


class TestHistoricalConversion:
    """Override-based historical conversion scoring."""

    def test_no_overrides_returns_default(self) -> None:
        assert historical_conversion("Alice Smith") == pytest.approx(0.50)

    def test_none_overrides_returns_default(self) -> None:
        assert historical_conversion("Alice Smith", None) == pytest.approx(0.50)

    def test_empty_overrides_returns_default(self) -> None:
        assert historical_conversion("Alice Smith", {}) == pytest.approx(0.50)

    def test_exact_match_override(self) -> None:
        overrides = {"Alice Smith": 0.85}
        assert historical_conversion("Alice Smith", overrides) == pytest.approx(0.85)

    def test_case_insensitive_match(self) -> None:
        overrides = {"Alice Smith": 0.85}
        assert historical_conversion("alice smith", overrides) == pytest.approx(0.85)

    def test_unknown_speaker_returns_default(self) -> None:
        overrides = {"Alice Smith": 0.85}
        assert historical_conversion("Bob Jones", overrides) == pytest.approx(0.50)

    def test_whitespace_tolerance(self) -> None:
        overrides = {"Alice Smith": 0.85}
        assert historical_conversion("  Alice Smith  ", overrides) == pytest.approx(0.85)

    def test_result_in_unit_range(self) -> None:
        overrides = {"Test": 0.75}
        score = historical_conversion("Test", overrides)
        assert 0.0 <= score <= 1.0


class TestStudentInterest:
    """Category-based student interest weight lookup."""

    def test_known_category_ai_hackathon(self) -> None:
        assert student_interest("AI / Hackathon") == pytest.approx(0.95)

    def test_known_category_hackathon(self) -> None:
        assert student_interest("Hackathon") == pytest.approx(0.90)

    def test_known_category_case_competition(self) -> None:
        assert student_interest("Case competition") == pytest.approx(0.85)

    def test_unknown_category_returns_default(self) -> None:
        assert student_interest("Underwater Basket Weaving") == pytest.approx(0.50)

    def test_empty_string_returns_default(self) -> None:
        assert student_interest("") == pytest.approx(0.50)

    def test_none_returns_default(self) -> None:
        assert student_interest(None) == pytest.approx(0.50)

    def test_case_insensitive_partial_match(self) -> None:
        score = student_interest("hackathon")
        assert score > 0.50

    def test_partial_match_substring(self) -> None:
        score = student_interest("Research showcase event")
        assert score == pytest.approx(0.60)

    def test_result_in_unit_range(self) -> None:
        for cat in ["AI / Hackathon", "Career fairs", "unknown", "", None]:
            score = student_interest(cat)
            assert 0.0 <= score <= 1.0, f"Out of range for category={cat!r}"
