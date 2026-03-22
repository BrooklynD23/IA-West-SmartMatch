# Phase 2 Review + Commit Hand-Off
# Session Date: 2026-03-21
# Status: IMPLEMENTED — awaiting code review, fixes, docs update, commit

## NEXT SESSION PROMPT

```
Read ".claude/handoff-phase2-review.md" in "Category 3 - IA West Smart Match CRM/" and follow it step by step:

1. Code-review all Phase 2 changes (4 files listed below) — flag ALL issues by severity
2. Fix every finding (CRITICAL, HIGH, MEDIUM)
3. Re-run full test suite: .venv/bin/python -m pytest -v
4. Update documentation (see docs section below)
5. Commit with message template provided
6. Write handoff for Phase 3 at .claude/handoff-phase3.md
```

---

## PROJECT CONTEXT

- **Project:** Category 3 - IA West Smart Match CRM
- **Branch:** sprint5-cat3
- **Venv:** `.venv/bin/python` (python3.12)
- **Test command:** `.venv/bin/python -m pytest -v`
- **Baseline:** 422 passed, 1 pre-existing failure (`test_embeddings.py::test_get_api_key_requires_real_gemini_key` — environment-dependent, IGNORE)
- **Master plan:** `/home/danny/.claude/plans/deep-wiggling-cupcake.md`
- **Phase sequence:** Phase 0 (done) → Phase 1 (done) → **Phase 2 (done, needs review)** → Phase 3 (next)

## COMPLETED PHASES

| Phase | Commit | Summary |
|-------|--------|---------|
| 0 — Engine Factor Registry | `1443fdb` | FactorSpec registry in config.py, single source of truth for 6 factors |
| 1 — Landing Page | `21d41bc` | Academic Curator design system, view switching, 21 new tests |

---

## PHASE 2 CHANGES TO REVIEW

### Goal
Replace the hardcoded `return 0.3` fallback in `geographic_proximity()` with a Haversine-based geodesic distance score. Move coordinate data to config.py as single source of truth. Fix OC/Long Beach coordinate bug.

### Files Changed (4 files, +181 -32 lines)

#### 1. `src/config.py` — Lines 297-332 (new block)
**What was added:**
- `REGION_COORDINATES: Final[dict[str, tuple[float, float]]]` — 11 metro region centroids
- `UNIVERSITY_COORDINATES: Final[dict[str, tuple[float, float]]]` — 11 university campus coordinates
- `MAX_FALLBACK_DISTANCE_MILES: Final[float] = 600.0`

**Bug fix applied:**
- "Orange County / Long Beach" coordinates changed from `(33.7701, -118.1937)` (was copy-paste of Long Beach) to `(33.7175, -117.8311)` (actual OC centroid near Irvine/Santa Ana)

**Review focus:**
- Verify all 11 metro region keys match `METRO_REGIONS` list (config.py:103-115)
- Verify all 11 metro region keys match `GEO_PROXIMITY` table keys (config.py:120-253)
- Verify OC coordinate fix is reasonable (should be ~25mi east of Long Beach)
- Verify `UNIVERSITY_COORDINATES` values match what expansion_map.py previously had

#### 2. `src/matching/factors.py` — Two change sites
**Change A — Lines 8, 21-22 (imports):**
```python
from math import atan2, cos, radians, sin, sqrt  # NEW
from src.config import (
    ...
    MAX_FALLBACK_DISTANCE_MILES,  # NEW
    REGION_COORDINATES,           # NEW
    ...
)
```

**Change B — Lines 36-52 (new helper):**
```python
_EARTH_RADIUS_MILES: float = 3959.0

def _haversine_miles(
    coord1: tuple[float, float],
    coord2: tuple[float, float],
) -> float:
    """Compute great-circle distance in miles between two (lat, lng) points."""
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return _EARTH_RADIUS_MILES * c
```

**Change C — Lines ~280-298 (fallback replacement):**
Previously: `return 0.3`
Now: Three-tier fallback:
1. Try `GEO_PROXIMITY` lookup (unchanged, covers 121 pairs)
2. If miss → try geodesic via `REGION_COORDINATES` for both regions
3. If coordinates missing → `return 0.3` (ultimate fallback preserved)

**Review focus:**
- Verify `_haversine_miles` math matches `expansion_map.py:90-98` (`compute_geographic_proximity`)
- Verify the fallback cascade is correct: lookup → geodesic → 0.3
- Verify `REGION_COORDINATES.get()` handles missing keys gracefully
- Check type annotations are complete (PEP 8 compliance)
- Check that `_EARTH_RADIUS_MILES` should be `Final` since it's a module-level constant

#### 3. `src/ui/expansion_map.py` — Lines 12-17 (replaced coordinate dicts)
**Before:** Two inline dicts (`SPEAKER_METRO_COORDS`, `UNIVERSITY_COORDS`) — 30 lines
**After:**
```python
from src.config import REGION_COORDINATES, UNIVERSITY_COORDINATES

SPEAKER_METRO_COORDS = REGION_COORDINATES
UNIVERSITY_COORDS = UNIVERSITY_COORDINATES
```

**Review focus:**
- Verify no other code in expansion_map.py references the old dict variable names directly
- Verify the aliases `SPEAKER_METRO_COORDS` / `UNIVERSITY_COORDS` are used throughout the rest of the file (they are: lines 115, 117, 119, 172, 174, 199)
- Check if `Dict`, `Tuple` type imports are still needed (they are — used in function signatures and `EXPERTISE_CLUSTER_COLORS`)

#### 4. `tests/test_factors.py` — Lines 7, 200-270 (new imports + 2 test classes)
**New import:** `_haversine_miles`

**New class `TestHaversineMiles` (4 tests):**
- `test_same_point_returns_zero` — identical coords → 0.0 distance
- `test_la_to_sf_roughly_350_miles` — LA↔SF → 340-390mi range
- `test_la_to_seattle_roughly_960_miles` — LA↔Seattle → 940-980mi range
- `test_symmetry` — haversine(A,B) == haversine(B,A)

**New class `TestGeodesicFallback` (5 tests):**
- `test_existing_lookup_pairs_unchanged` — spot-checks 3 known GEO_PROXIMITY pairs
- `test_fallback_returns_no_coordinates` — "Narnia"↔"Narnia" → 0.3
- `test_fallback_near_regions_high_score` — verifies formula yields >0.9 for nearby coords
- `test_fallback_distant_regions_low_score` — verifies LA↔Seattle → 0.0 (>600mi)
- `test_fallback_score_in_unit_range` — SF↔SD score in [0, 1]

**Review focus:**
- Are the geodesic fallback tests actually exercising the fallback path? The `TestGeodesicFallback` tests mostly test `_haversine_miles` directly — consider whether an integration test that actually calls `geographic_proximity()` with a speaker region NOT in `GEO_PROXIMITY` is needed
- The "Narnia" test tests the ULTIMATE fallback (no coordinates), but is there a test for the GEODESIC path (coordinates exist, but pair not in GEO_PROXIMITY)?
- All 8 existing `TestGeographicProximity` tests MUST still pass — they test lookup-table paths that Phase 2 doesn't modify

---

## REVIEW CHECKLIST

### Code Quality
- [ ] Type annotations on all new functions (PEP 8, type hints)
- [ ] `_EARTH_RADIUS_MILES` should use `Final` annotation for consistency with other config constants
- [ ] No mutation — all new code returns new values (immutability)
- [ ] Functions under 50 lines
- [ ] No hardcoded values (constants in config)
- [ ] Error handling: what happens if `REGION_COORDINATES` has bad data (e.g., lat=999)?

### Correctness
- [ ] All 121 GEO_PROXIMITY lookup pairs produce identical scores (no behavior change)
- [ ] Geodesic fallback only fires when lookup returns None AND both coords exist
- [ ] `max(0.0, ...)` prevents negative scores for >600mi distances
- [ ] OC coordinate `(33.7175, -117.8311)` is geographically reasonable
- [ ] `expansion_map.py` still renders correctly (aliases resolve to same data)

### Test Coverage
- [ ] 422 tests pass (was 412 before Phase 2 — 10 new tests added)
- [ ] All 8 existing `TestGeographicProximity` tests pass unchanged
- [ ] All 12 existing `test_expansion_map.py` tests pass
- [ ] New tests cover: haversine math, geodesic fallback path, no-coordinates fallback
- [ ] POTENTIAL GAP: integration test calling `geographic_proximity()` with a region pair that triggers the geodesic codepath (not just unit-testing `_haversine_miles` in isolation)

### Security
- [ ] No new dependencies added
- [ ] No network calls
- [ ] No user input in coordinate lookups (all from internal config)

---

## DOCUMENTATION TO UPDATE

### 1. Sprint plan progress (`docs/SPRINT_PLAN.md`)
Add Phase 2 completion entry if sprint tracking is maintained there.

### 2. Progress log (`claude-progress.txt`)
This file tracks orchestrator progress from Sprint 3. Phase 2 is Sprint 6 work. Add entry if appropriate, or note that Sprint 6 progress is tracked via the plan file and handoff docs.

### 3. Review findings doc
Create `docs/reviews/2026-03-21-phase2-code-review.md` with:
- Summary of findings by severity
- What was fixed
- Test results before/after

---

## COMMIT TEMPLATE

```
feat: geodesic distance fallback for geographic_proximity (Phase 2)

Sprint 6 Phase 2. Replaces hardcoded 0.3 fallback with Haversine-based
geodesic distance for region pairs not in the GEO_PROXIMITY lookup table.
Moves SPEAKER_METRO_COORDS and UNIVERSITY_COORDS to config.py as shared
REGION_COORDINATES. Fixes OC/Long Beach copy-paste coordinate error.

All 121 existing GEO_PROXIMITY pairs produce identical scores.
No new dependencies — reuses math-based Haversine from expansion_map.
422 tests pass (10 new tests for haversine + geodesic fallback).
```

Files to stage:
```
git add "Category 3 - IA West Smart Match CRM/src/config.py" \
       "Category 3 - IA West Smart Match CRM/src/matching/factors.py" \
       "Category 3 - IA West Smart Match CRM/src/ui/expansion_map.py" \
       "Category 3 - IA West Smart Match CRM/tests/test_factors.py"
```

Do NOT stage `.claude/settings.local.json` — that's a local config file.

---

## AFTER COMMIT: WRITE PHASE 3 HANDOFF

Create `.claude/handoff-phase3.md` for the next agent to implement Phase 3 (Enhanced Matching — 2 new factors).

Phase 3 details from the plan (`/home/danny/.claude/plans/deep-wiggling-cupcake.md` lines 238-291):

### Phase 3 Summary
- **Goal:** Add `event_urgency` and `coverage_diversity` factors (8-factor matching)
- **Depends on:** Phase 0 (FactorSpec registry) — already complete
- **Weight rebalance:** topic_relevance 0.30→0.25, role_fit 0.25→0.20, others unchanged, +0.05 each for new factors

### Phase 3 Files to Create/Modify
| File | Change |
|------|--------|
| `src/config.py` | Add 2 FactorSpec entries to FACTOR_REGISTRY, adjust default weights |
| `src/matching/factors.py` | Add `event_urgency()` + `coverage_diversity()` (~60 lines total) |
| `src/matching/engine.py` | Add dispatch entries for 2 new factors in `_FACTOR_DISPATCH` |
| `tests/test_factors_extended.py` (create) | Tests for new factors |
| `cache/demo_fixtures/match_explanations.json` | Include new factor scores |

### Phase 3 Key Design Decisions
- `event_urgency`: Primary data source is `Recurrence (typical)` column (NOT "Event Date" which is a transient runtime key)
- `coverage_diversity`: Uses `st.session_state["feedback_decisions"]` — requires `init_feedback_state()` call first
- Weight-asserting tests in `test_engine.py` will need updates for new default values
- Radar chart should auto-expand to 8 axes if FACTOR_REGISTRY is used correctly

### Phase 3 Handoff Should Include
- Exact current line numbers for all files to modify (read fresh — Phase 2 shifted lines)
- The `_FACTOR_DISPATCH` dict pattern from engine.py (copy relevant code)
- Current FactorSpec entries and where to insert new ones
- Recurrence scoring table from plan
- Coverage diversity scoring table from plan
- Template for `test_factors_extended.py`
- Note about `init_feedback_state()` guard requirement
- List of tests that assert on DEFAULT_WEIGHTS values (will need mechanical updates)
