# Phase 3 Implementation Hand-Off
# Session Date: 2026-03-21
# Status: READY TO IMPLEMENT

## NEXT SESSION PROMPT

```
Read ".claude/handoff-phase3.md" in "Category 3 - IA West Smart Match CRM/" and follow it step by step:

1. Implement event_urgency() factor in factors.py
2. Implement coverage_diversity() factor in factors.py
3. Add 2 FactorSpec entries to config.py FACTOR_REGISTRY + rebalance weights
4. Add dispatch entries in engine.py compute_match_score()
5. Create tests/test_factors_extended.py with TDD
6. Update weight-asserting tests in test_engine.py
7. Run full test suite: .venv/bin/python -m pytest -v
8. Write handoff for Phase 4
```

---

## PROJECT CONTEXT

- **Project:** Category 3 - IA West Smart Match CRM
- **Branch:** sprint5-cat3
- **Venv:** `.venv/bin/python` (python3.12)
- **Test command:** `.venv/bin/python -m pytest -v`
- **Baseline:** 424 passed, 1 pre-existing failure (`test_embeddings.py::test_get_api_key_requires_real_gemini_key` — environment-dependent, IGNORE)
- **Master plan:** `/home/danny/.claude/plans/deep-wiggling-cupcake.md` (Phase 3: lines 238-291)
- **Phase sequence:** Phase 0 (done) -> Phase 1 (done) -> Phase 2 (done) -> **Phase 3 (implement)** -> Phase 4 (next)

## COMPLETED PHASES

| Phase | Commit | Summary |
|-------|--------|---------|
| 0 — Engine Factor Registry | `1443fdb` | FactorSpec registry in config.py, single source of truth for 6 factors |
| 1 — Landing Page | `21d41bc` | Academic Curator design system, view switching, 21 new tests |
| 2 — Geodesic Fallback | pending | Haversine geodesic fallback, OC coordinate fix, 12 new tests |

---

## PHASE 3 GOAL

Add `event_urgency` and `coverage_diversity` factors (6-factor -> 8-factor matching). Leverages Phase 0's dynamic FactorSpec registry.

---

## FILE-BY-FILE IMPLEMENTATION GUIDE

### 1. `src/config.py` — FACTOR_REGISTRY (lines 79-92) + DEFAULT_WEIGHTS (line 96)

**Current state (6 factors):**
```python
FACTOR_REGISTRY: Final[tuple[FactorSpec, ...]] = (
    FactorSpec("topic_relevance", "Topic Relevance", "Topic", 0.30,
               "topic alignment", "Topic Match"),
    FactorSpec("role_fit", "Role Fit", "Role Fit", 0.25,
               "role compatibility", "Role Fit"),
    FactorSpec("geographic_proximity", "Geographic Proximity", "Proximity", 0.20,
               "geographic proximity", "Geographic Fit"),
    FactorSpec("calendar_fit", "Calendar Fit", "Calendar", 0.15,
               "calendar alignment", "Calendar Fit"),
    FactorSpec("historical_conversion", "Historical Conversion", "History", 0.05,
               "engagement history", "Engagement History"),
    FactorSpec("student_interest", "Student Interest", "Student Int.", 0.05,
               "student interest potential", "Student Interest"),
)
```

**Target state (8 factors with rebalanced weights):**
```python
FACTOR_REGISTRY: Final[tuple[FactorSpec, ...]] = (
    FactorSpec("topic_relevance", "Topic Relevance", "Topic", 0.25,          # was 0.30
               "topic alignment", "Topic Match"),
    FactorSpec("role_fit", "Role Fit", "Role Fit", 0.20,                     # was 0.25
               "role compatibility", "Role Fit"),
    FactorSpec("geographic_proximity", "Geographic Proximity", "Proximity", 0.20,
               "geographic proximity", "Geographic Fit"),
    FactorSpec("calendar_fit", "Calendar Fit", "Calendar", 0.15,
               "calendar alignment", "Calendar Fit"),
    FactorSpec("historical_conversion", "Historical Conversion", "History", 0.05,
               "engagement history", "Engagement History"),
    FactorSpec("student_interest", "Student Interest", "Student Int.", 0.05,
               "student interest potential", "Student Interest"),
    FactorSpec("event_urgency", "Event Urgency", "Urgency", 0.05,            # NEW
               "scheduling urgency", "Event Urgency"),
    FactorSpec("coverage_diversity", "Coverage Diversity", "Coverage", 0.05,  # NEW
               "assignment diversity", "Coverage Balance"),
)
```

**Derived constants auto-update:** `FACTOR_KEYS`, `DEFAULT_WEIGHTS`, `FACTOR_DISPLAY_LABELS`, etc. are all derived from `FACTOR_REGISTRY` (lines 95-100), so they update automatically.

---

### 2. `src/matching/factors.py` — Add 2 new factor functions

**Insert after line 500 (after `student_interest()`):**

#### `event_urgency` Scoring Table (from plan)

| Condition | Score |
|-----------|-------|
| Specific date, <=14 days away | 1.00 |
| Specific date, 15-30 days | 0.85 |
| Specific date, 31-60 days | 0.70 |
| Specific date, 61-90 days | 0.55 |
| Specific date, >90 days | 0.40 |
| Recurrence "Weekly" | 0.75 |
| Recurrence "Monthly" | 0.65 |
| Recurrence "Quarterly" | 0.55 |
| Recurrence "Annual" / "Annually" | 0.50 |
| Recurrence "One-time" | 0.85 |
| Unknown / missing | 0.50 |

**Signature:**
```python
def event_urgency(
    event_date_or_recurrence: object,
    reference_date: date | None = None,
) -> float:
```

**IMPORTANT:** The primary data source is `Recurrence (typical)` column. "Event Date" is NOT a CSV column — it's a transient runtime key in engine.py:215. Date parsing is secondary.

#### `coverage_diversity` Scoring Table (from plan)

| Assignments | Score |
|-------------|-------|
| 0 | 1.00 |
| 1 | 0.85 |
| 2 | 0.70 |
| 3 | 0.55 |
| 4+ | 0.40 |
| No data | 0.50 |

**Signature:**
```python
def coverage_diversity(
    speaker_name: str,
    current_assignments: dict[str, int] | None = None,
) -> float:
```

**Data source:** `st.session_state["feedback_decisions"]` — but the function is PURE. The caller extracts the assignment count and passes it. The function receives a dict of `{speaker_name: assignment_count}` or None.

**IMPORTANT:** `feedback_decisions` requires `init_feedback_state()` to be called first. The dispatch wrapper in engine.py should handle this gracefully — if `current_assignments` is None, return 0.50.

---

### 3. `src/matching/engine.py` — Add dispatch for 2 new factors

**Current `compute_match_score()` (lines 105-126) builds `factor_scores` dict inline:**
```python
factor_scores: dict[str, float] = {
    "topic_relevance": ...,
    "role_fit": role_fit(speaker_board_role, event_volunteer_roles),
    "geographic_proximity": geographic_proximity(speaker_metro_region, event_region),
    "calendar_fit": calendar_fit(...),
    "historical_conversion": historical_conversion(speaker_name, conversion_overrides),
    "student_interest": ...,
}
```

**Add to this dict:**
```python
    "event_urgency": event_urgency(event_date_or_recurrence),
    "coverage_diversity": coverage_diversity(speaker_name, coverage_assignments),
```

**Required changes:**
1. Add `event_urgency` and `coverage_diversity` to the import block (line 16-23)
2. Add `coverage_assignments: Optional[dict[str, int]] = None` parameter to `compute_match_score()` (line 78)
3. Pass `coverage_assignments` through from `rank_speakers_for_event()` (add parameter, line 189)
4. Pass through from `rank_speakers_for_course()` too (line 306)

---

### 4. `tests/test_factors_extended.py` — CREATE NEW FILE

**Template:**
```python
"""Tests for Phase 3 factors: event_urgency and coverage_diversity."""

from datetime import date, timedelta

import pytest

from src.matching.factors import coverage_diversity, event_urgency


class TestEventUrgency:
    """Event urgency scoring based on date proximity and recurrence."""

    def test_specific_date_within_14_days(self) -> None: ...
    def test_specific_date_15_to_30_days(self) -> None: ...
    def test_specific_date_31_to_60_days(self) -> None: ...
    def test_specific_date_61_to_90_days(self) -> None: ...
    def test_specific_date_over_90_days(self) -> None: ...
    def test_recurrence_weekly(self) -> None: ...
    def test_recurrence_monthly(self) -> None: ...
    def test_recurrence_quarterly(self) -> None: ...
    def test_recurrence_annual(self) -> None: ...
    def test_recurrence_one_time(self) -> None: ...
    def test_unknown_recurrence_returns_default(self) -> None: ...
    def test_none_returns_default(self) -> None: ...
    def test_result_in_unit_range(self) -> None: ...


class TestCoverageDiversity:
    """Coverage diversity scoring based on assignment count."""

    def test_zero_assignments_returns_one(self) -> None: ...
    def test_one_assignment(self) -> None: ...
    def test_two_assignments(self) -> None: ...
    def test_three_assignments(self) -> None: ...
    def test_four_plus_assignments(self) -> None: ...
    def test_no_data_returns_default(self) -> None: ...
    def test_none_assignments_returns_default(self) -> None: ...
    def test_unknown_speaker_returns_default(self) -> None: ...
    def test_result_in_unit_range(self) -> None: ...
```

---

### 5. Tests Requiring Mechanical Updates

**Weight-asserting tests that reference `DEFAULT_WEIGHTS` values:**

| File | Line | What to Update |
|------|------|----------------|
| `tests/test_engine.py` | 7 | Import is fine (already imports `DEFAULT_WEIGHTS`) |
| `tests/test_engine.py` | 180 | `test_default_weights_produce_nonzero_total` — should still pass since it just checks > 0 |
| `tests/test_engine.py` | 576 | Uses `DEFAULT_WEIGHTS["student_interest"]` — value unchanged (0.05), but `compute_match_score` call needs `event_urgency` + `coverage_diversity` entries in result |
| `tests/test_landing_page.py` | 99-111 | `test_donut_uses_default_weights` — checks `len(DEFAULT_WEIGHTS) == 6` → will fail, needs update to 8 |
| `tests/test_landing_page.py` | 118-126 | Checks `f"The Bridge: {len(DEFAULT_WEIGHTS)}-Factor MATCH_SCORE"` → "6-Factor" becomes "8-Factor" |

**Engine tests that call `compute_match_score()`:** These will need the new factors in results. Since `FACTOR_KEYS` is derived from `FACTOR_REGISTRY`, the engine will automatically include the new factors — but existing assertions on `factor_scores` dict may need updating if they check exact key counts.

---

### 6. Demo Fixtures to Update

**`cache/demo_fixtures/match_explanations.json`** — if this file contains hardcoded factor score examples, add `event_urgency` and `coverage_diversity` entries.

---

## KEY DESIGN DECISIONS

1. **`event_urgency` vs `calendar_fit`:** These are different. `calendar_fit` measures proximity to IA events in the speaker's region. `event_urgency` measures how soon the event needs a speaker (time pressure).

2. **`coverage_diversity` data source:** Uses `feedback_decisions` from session state, but the factor function is PURE — caller extracts and passes the data. If no data, return 0.50 (neutral).

3. **Radar chart auto-expansion:** If the radar chart reads from `FACTOR_KEYS` (which it should after Phase 0), it will auto-expand to 8 axes. Verify this.

4. **Weight rebalance is minimal:** Only `topic_relevance` (0.30->0.25) and `role_fit` (0.25->0.20) change. The other 4 factors keep their weights. The 0.10 freed up goes to the 2 new factors (0.05 each).

---

## AFTER IMPLEMENTATION

1. Run full test suite: `.venv/bin/python -m pytest -v`
2. Verify 8-factor radar chart renders (if UI is testable)
3. Commit with message:
```
feat: add event_urgency + coverage_diversity factors (Phase 3)

Sprint 6 Phase 3. Expands matching from 6 to 8 factors. Adds
event_urgency (date proximity / recurrence urgency) and
coverage_diversity (speaker assignment balancing). Rebalances
default weights: topic_relevance 0.30->0.25, role_fit 0.25->0.20.

Radar chart auto-expands to 8 axes via FACTOR_REGISTRY.
All existing tests updated for new weight values.
```
4. Write handoff for Phase 4 (QR Code Generation)
