# Sprint 3 Swarm Orchestration Plan

**Branch:** `sprint3-cat3` (from `sprint2-cat3`)
**Orchestrator:** Opus 4.6 (harness engineer)
**Workers:** Sonnet 4.6 via Claude Swarm MCP
**Methodology:** Everything Claude Code TDD (RED-GREEN-IMPROVE per worker)
**Sprint Spec:** `docs/sprints/sprint-3-polish-freeze.md` (canonical source of truth)
**Feature Freeze:** End of Day 9. Day 10 is integration + bug fixes only.

---

## 1. Dependency Graph

```
Phase 1 (Day 9, 3 parallel)     Phase 2 (2 parallel)    Phase 3          Phase 4
────────────────────────────     ───────────────────     ─────────        ─────────
[feat-1: Expansion Map]  ──┐
[feat-2: Feedback Loop]  ──┼──> [feat-4: UI Polish]  ──┐
[feat-3: Vol Dashboard]  ──┘    [feat-5: Real Pipeline] ┼──> [feat-6: Demo] ──> [feat-7: Screenshots]
```

| Feature ID | Task | Dependencies | Phase | Est. Time |
|---|---|---|---|---|
| `feature-1` | A3.1 Expansion Map | none | 1 | 60-90 min |
| `feature-2` | A3.2 Feedback Loop | none | 1 | 60-90 min |
| `feature-3` | A3.3 Volunteer Dashboard | none | 1 | 50-75 min |
| `feature-4` | A3.4 UI Polish + CSS | feat-1,2,3 | 2 | 45-60 min |
| `feature-5` | A3.6 Real Pipeline Data | feat-2 (optional) | 2 | 30-45 min |
| `feature-6` | A3.5 Demo Flow Hardening | feat-4,5 | 3 | 40-60 min |
| `feature-7` | A3.7 Screenshots | feat-6 | 4 | 15-20 min |

**Max concurrent workers:** 3 (Phase 1: features 1, 2, 3)

---

## 2. File Ownership Matrix (Conflict Prevention)

Each worker owns a disjoint set of files. Shared files are serialized by the `app.py` serialization order below.

| Worker | Owns (creates) | Modifies (shared) |
|---|---|---|
| feature-1 (Expansion Map) | `src/ui/expansion_map.py`, `tests/test_expansion_map.py` | `src/app.py` (add Expansion tab at L234) |
| feature-2 (Feedback Loop) | `src/feedback/__init__.py`, `src/feedback/acceptance.py`, `tests/test_acceptance.py` | `src/ui/matches_tab.py` (add buttons after L299), `src/app.py` (sidebar call) |
| feature-3 (Vol Dashboard) | `src/ui/volunteer_dashboard.py`, `tests/test_volunteer_dashboard.py` | `src/app.py` (add Volunteers tab at L234) |
| feature-4 (UI Polish) | `src/ui/styles.py`, `tests/test_styles.py` | `src/app.py` (CSS injection after L14), `.streamlit/config.toml` |
| feature-5 (Real Pipeline) | — | `src/ui/pipeline_tab.py` (update existing) |
| feature-6 (Demo Mode) | `src/demo_mode.py`, `tests/test_demo_mode.py`, `cache/demo_fixtures/*` | `src/app.py` (demo toggle), discovery/explanations/email call sites |
| feature-7 (Screenshots) | `scripts/capture_screenshots.py`, `docs/screenshots/*.png` | — |

### app.py Serialization Order (Critical)

`src/app.py` is modified by 5 features. Strict serialization:

1. **feat-1** adds Expansion tab to `st.tabs()` at L234 → commit
2. **feat-3** adds Volunteers tab to `st.tabs()` at L234 → commit (after feat-1)
3. **feat-2** adds `render_feedback_sidebar()` call in sidebar → commit (after feat-3)
4. **feat-4** injects `CUSTOM_CSS` after `st.set_page_config()` at L14 → commit
5. **feat-6** adds `init_demo_mode()` in sidebar → commit

### Shared File Serialization

- **`src/app.py`**: 5 features modify, serialized in order above. Each commit gates the next.
- **`src/ui/matches_tab.py`**: feature-2 adds feedback buttons after L299. No other feature touches this area.
- **`src/ui/pipeline_tab.py`**: feature-5 is sole modifier.
- **`.streamlit/config.toml`**: feature-4 is sole modifier.

---

## 3. Swarm MCP Orchestration Commands (Step-by-Step)

### Step 0: Branch (Already Done)

```bash
git checkout sprint2-cat3
git checkout -b sprint3-cat3
```

### Step 1: Initialize Swarm

```
orchestrator_init(
  projectDir = "Category 3 - IA West Smart Match CRM",
  taskDescription = "Sprint 3: Polish + Feature Freeze. 7 features: expansion map, feedback loop, volunteer dashboard, UI polish, real pipeline data, demo mode, screenshots. TDD required. Feature freeze end of Day 9.",
  existingFeatures = [
    "A3.1: Board-to-Campus Expansion Map - Plotly scatter_geo, 3 layers (speakers/universities/connections), Haversine distance, expertise clustering",
    "A3.2: Match Acceptance Feedback Loop - Accept/decline buttons, decline reasons, CSV persistence, weight adjustment suggestions",
    "A3.3: Volunteer Dashboard - Speaker-centric view, top-5 matched events, utilization metrics, bar chart",
    "A3.4: UI Polish + CSS - CUSTOM_CSS injection, IA West brand colors, error handling cards, loading spinners",
    "A3.6: Real Pipeline Data - Replace simulated funnel with real prototype match data, keep CSV fallback",
    "A3.5: Demo Flow Hardening - demo_or_live() dispatch, 7 fixture files, wrap all API call sites",
    "A3.7: Screenshots - Playwright capture script, 6 PNGs for Track B documentation"
  ]
)
```

### Step 2: Set Dependencies

```
set_dependencies(featureId="feature-4", dependsOn=["feature-1", "feature-2", "feature-3"])
set_dependencies(featureId="feature-5", dependsOn=["feature-2"])
set_dependencies(featureId="feature-6", dependsOn=["feature-4", "feature-5"])
set_dependencies(featureId="feature-7", dependsOn=["feature-6"])
```

### Step 3: Configure Verification

```
configure_verification(
  commands = ["pytest tests/ -v --tb=short"],
  failOnError = True
)
```

### Step 4: Set Feature Context (per worker)

Each worker receives:
1. **TDD Protocol** (priority: "required") - see Section 4
2. **Sprint Spec Reference** - the relevant section of `docs/sprints/sprint-3-polish-freeze.md`
3. **Architecture Reference Files** - key existing modules to follow
4. **Existing test count** - 107+ tests must still pass after each worker completes

```
set_feature_context(featureId="feature-N", documentation=[...], prepared=[...])
```

#### Context for feature-1 (Expansion Map)

```
documentation:
  - src/ui/matches_tab.py (UI module pattern to follow)
  - src/app.py (L234, st.tabs() to extend)
  - src/data_loader.py (speakers DataFrame loading)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.1, complete code spec)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Create src/ui/expansion_map.py following the COMPLETE code in the sprint spec
      2. FULL SPEC IS IN docs/sprints/sprint-3-polish-freeze.md task A3.1
      3. Plotly scatter_geo with 3 layers: speakers (circles), universities (diamonds), connections (lines)
      4. Haversine distance via compute_geographic_proximity()
      5. SPEAKER_METRO_COORDS and UNIVERSITY_COORDS coordinate lookup tables (hardcoded, from spec)
      6. EXPERTISE_CLUSTER_COLORS and SPEAKER_CLUSTERS mappings (from spec)
      7. build_connection_data() returns connections above proximity_threshold
      8. render_expansion_map(speakers_df, proximity_threshold) -> go.Figure
      9. Tests in tests/test_expansion_map.py - 12 tests minimum
      10. DO NOT modify app.py yet - orchestrator will serialize app.py changes
```

#### Context for feature-2 (Feedback Loop)

```
documentation:
  - src/ui/matches_tab.py (L268-299, integration point for feedback buttons)
  - src/matching/factors.py (DEFAULT_WEIGHTS reference)
  - src/config.py (DEFAULT_WEIGHTS import)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.2, complete code spec)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Create src/feedback/__init__.py and src/feedback/acceptance.py
      2. FULL SPEC IS IN docs/sprints/sprint-3-polish-freeze.md task A3.2
      3. FeedbackEntry dataclass with frozen fields
      4. Session state management: feedback_log, feedback_decisions
      5. CSV persistence to data/feedback_log.csv
      6. render_feedback_buttons() called inside match cards in matches_tab.py
      7. render_feedback_sidebar() called from app.py sidebar
      8. generate_weight_suggestions() based on decline reason patterns
      9. Wire feedback buttons into src/ui/matches_tab.py AFTER L299 (after .ics download button)
      10. Tests in tests/test_acceptance.py - 14 tests minimum
      11. DO NOT modify app.py yet - orchestrator will serialize app.py changes
      12. Import DEFAULT_WEIGHTS from src.config (check if it exists, if not from src.matching.factors)
```

#### Context for feature-3 (Volunteer Dashboard)

```
documentation:
  - src/ui/matches_tab.py (UI module pattern to follow)
  - src/app.py (L234, st.tabs() to extend)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.3, complete code spec)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Create src/ui/volunteer_dashboard.py
      2. FULL SPEC IS IN docs/sprints/sprint-3-polish-freeze.md task A3.3
      3. Speaker-centric view: selectbox for speaker, top-5 matched events table
      4. compute_speaker_matches() filters match_results DataFrame
      5. compute_utilization_metrics() calculates matched/accepted/attended counts
      6. render_utilization_bar_chart() mini Plotly bar chart
      7. match_results adapter: build from existing scoring engine outputs
      8. CONVERSION_RATES simulated metrics for attended/accepted
      9. Tests in tests/test_volunteer_dashboard.py - 10 tests minimum
      10. DO NOT modify app.py yet - orchestrator will serialize app.py changes
      11. This is the FIRST CUT CANDIDATE if time runs short
```

#### Context for feature-4 (UI Polish)

```
documentation:
  - src/app.py (L9-14, st.set_page_config area for CSS injection)
  - .streamlit/config.toml (theme configuration, create if missing)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.4)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Create src/ui/styles.py with CUSTOM_CSS constant and helper functions
      2. inject_custom_css() - st.markdown with unsafe_allow_html for brand CSS
      3. api_call_spinner(label) - context manager wrapping st.spinner
      4. render_error_card(title, message) - styled error display
      5. IA West brand colors: navy #1E3A5F, gold #F59E0B, blue #2563EB
      6. .streamlit/config.toml with [theme] section for base colors
      7. Tests in tests/test_styles.py - 8 tests minimum
      8. DO NOT modify app.py yet - orchestrator will serialize app.py changes
```

#### Context for feature-5 (Real Pipeline Data)

```
documentation:
  - src/ui/pipeline_tab.py (direct update target)
  - src/matching/engine.py (match scoring functions)
  - data/pipeline_sample_data.csv (existing CSV data)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.6)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Modify src/ui/pipeline_tab.py (sole owner of this file)
      2. Add compute_real_funnel_data() that pulls from match scoring outputs
      3. Keep existing load_pipeline_data() CSV fallback for when real data unavailable
      4. render_pipeline_tab() tries real data first, falls back to CSV
      5. No new files needed, just modify pipeline_tab.py
      6. Tests: update tests/test_pipeline_tab.py with 7 additional tests
      7. Preserve all existing pipeline_tab tests (they must still pass)
```

#### Context for feature-6 (Demo Mode)

```
documentation:
  - src/app.py (sidebar area for demo toggle)
  - src/ui/discovery_tab.py (API call site to wrap)
  - src/matching/explanations.py (API call site to wrap)
  - src/outreach/email_gen.py (API call site to wrap)
  - docs/sprints/sprint-3-polish-freeze.md (task A3.5)

prepared:
  - key: "tdd-protocol" (see Section 4)
  - key: "architecture"
    content: |
      1. Create src/demo_mode.py with demo_or_live() dispatch function
      2. Create 7 fixture files in cache/demo_fixtures/
      3. demo_or_live(func, *args, fixture_key) -> returns fixture data or calls live func
      4. init_demo_mode() adds sidebar toggle (st.checkbox)
      5. Wrap API call sites: discovery scanning, match explanations, email generation
      6. Fixture files: JSON snapshots of real API responses
      7. Tests in tests/test_demo_mode.py - 7 tests minimum
      8. app.py modification: add init_demo_mode() call in sidebar
      9. DO NOT modify app.py yet - orchestrator will serialize app.py changes
```

#### Context for feature-7 (Screenshots)

```
documentation:
  - docs/sprints/sprint-3-polish-freeze.md (task A3.7)

prepared:
  - key: "architecture"
    content: |
      1. Create scripts/capture_screenshots.py (Playwright-based)
      2. Launch streamlit app, navigate to each tab, capture screenshots
      3. Save 6 PNGs to docs/screenshots/: matches, discovery, pipeline, expansion, volunteers, demo
      4. Each screenshot > 100KB (full-width viewport)
      5. NO TDD required (script task, not library code)
      6. If Playwright unavailable, provide manual screenshot instructions
```

### Step 5: Route Features

```
route_feature(featureId="feature-1", preferredWorkerType="frontend")
route_feature(featureId="feature-2", preferredWorkerType="backend")
route_feature(featureId="feature-3", preferredWorkerType="frontend")
route_feature(featureId="feature-4", preferredWorkerType="frontend")
route_feature(featureId="feature-5", preferredWorkerType="backend")
route_feature(featureId="feature-6", preferredWorkerType="backend")
route_feature(featureId="feature-7", preferredWorkerType="backend")
```

### Step 6: Launch Phase 1 (3 parallel workers)

```
start_parallel_workers(
  featureIds = ["feature-1", "feature-2", "feature-3"],
  customPrompts = {
    "feature-1": <EXPANSION_MAP_PROMPT>,
    "feature-2": <FEEDBACK_LOOP_PROMPT>,
    "feature-3": <VOLUNTEER_DASHBOARD_PROMPT>
  }
)
```

See Section 5 for full custom prompts.

### Step 7: Monitor & Steer

```
# Heartbeat check every 2-3 minutes
check_all_workers(heartbeat=True)

# Deep inspection when needed
check_worker(featureId="feature-1", lines=50)
get_worker_confidence(featureId="feature-1")

# Course-correct if needed
send_worker_message(featureId="feature-1", message="...")
```

### Step 8: Gate, Serialize app.py, & Chain

When Phase 1 workers complete:

```
# 1. Verify each worker's tests pass
run_verification(command="pytest tests/ -v --tb=short", featureId="feature-N")

# 2. Review output
check_worker(featureId="feature-N", lines=100)

# 3. Mark complete
mark_complete(featureId="feature-N", success=True)

# 4. Serialize app.py changes (CRITICAL ORDER)
#    a. feat-1: add Expansion tab to st.tabs()
#    b. feat-3: add Volunteers tab to st.tabs()
#    c. feat-2: add render_feedback_sidebar() in sidebar
commit_progress(message="feat(cat3): add board-to-campus expansion map with Plotly scatter_geo")
commit_progress(message="feat(cat3): add volunteer dashboard with speaker-centric view")
commit_progress(message="feat(cat3): add match acceptance feedback loop with weight suggestions")

# 5. Launch Phase 2 (dependencies met)
start_parallel_workers(featureIds=["feature-4", "feature-5"])
```

### Step 9: Phase 2 Completion

```
# Gate feature-4 and feature-5
run_verification(command="pytest tests/ -v --tb=short", featureId="feature-4")
run_verification(command="pytest tests/ -v --tb=short", featureId="feature-5")
mark_complete(featureId="feature-4", success=True)
mark_complete(featureId="feature-5", success=True)

# Serialize app.py: feat-4 CSS injection
commit_progress(message="feat(cat3): add UI polish with IA West brand CSS and error handling")
commit_progress(message="feat(cat3): replace simulated pipeline funnel with real prototype data")

# Launch Phase 3
start_worker(featureId="feature-6", customPrompt=<DEMO_MODE_PROMPT>)
```

### Step 10: Phase 3 & 4 Completion

```
# feat-6 (Demo Mode)
run_verification(command="pytest tests/ -v --tb=short", featureId="feature-6")
mark_complete(featureId="feature-6", success=True)
# Serialize app.py: feat-6 demo toggle
commit_progress(message="feat(cat3): add demo mode toggle with cached fixtures")

# feat-7 (Screenshots)
start_worker(featureId="feature-7", customPrompt=<SCREENSHOTS_PROMPT>)
mark_complete(featureId="feature-7", success=True)
commit_progress(message="docs(cat3): capture Track B screenshots for all key views")
```

### Step 11: Final Verification

```
run_verification(command="pytest tests/ -v --cov=src --cov-report=term-missing")
# Target: 140+ tests, 80%+ coverage
```

---

## 4. TDD Protocol (All Workers)

Every worker receives this as a `prepared` context block with `priority: "required"`:

```
TDD PROTOCOL -- MANDATORY

You MUST follow test-driven development. No exceptions.

PHASE 1 - RED (Write Failing Tests First)
1. Create test file(s) in tests/ directory
2. Write test classes with descriptive names
3. Use pytest fixtures: tmp_path for cache, monkeypatch for env vars
4. Use unittest.mock.patch for external deps (Gemini API, HTTP, Streamlit)
5. Run: pytest tests/test_<module>.py -v
6. Confirm: ALL tests FAIL (import errors or assertion errors)

PHASE 2 - GREEN (Minimal Implementation)
1. Create source file(s) in src/ directory
2. Implement the MINIMUM code to pass each test
3. Follow the EXACT code spec from docs/sprints/sprint-3-polish-freeze.md
4. Run: pytest tests/test_<module>.py -v
5. Confirm: ALL tests PASS

PHASE 3 - IMPROVE (Refactor)
1. Add type annotations to ALL function signatures
2. Use logging module (never print())
3. Run FULL test suite: pytest tests/ -v --tb=short
4. Confirm: ALL existing 107+ tests STILL PASS plus your new tests
5. No hardcoded secrets. No print() statements.

RULES:
- Mock ALL external calls (HTTP, Gemini API, Playwright, Streamlit). No real network access in tests.
- Follow existing patterns in src/ui/matches_tab.py for UI modules.
- Follow existing patterns in src/matching/explanations.py for LLM and cache code.
- Use generate_text() from src/gemini_client.py, NOT a Gemini SDK import.
- Append-only to src/config.py (never modify existing constants).
- Keep functions under 50 lines, files under 400 lines.
- DO NOT modify src/app.py - the orchestrator serializes app.py changes.
```

---

## 5. Custom Worker Prompts

### feature-1 (Expansion Map) Prompt

```
Sprint 3 Task A3.1: Board-to-Campus Expansion Map

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.1. The spec contains COMPLETE function code and implementation details.
Follow them exactly.

STEP 1 (RED): Write tests/test_expansion_map.py with:
- test_speaker_metro_coords_complete (all 18 speakers have metro in lookup)
- test_university_coords_complete (all 11 universities in lookup)
- test_compute_geographic_proximity_same_location_returns_1
- test_compute_geographic_proximity_max_distance_returns_0
- test_compute_geographic_proximity_mid_distance
- test_build_connection_data_filters_by_threshold
- test_build_connection_data_empty_when_threshold_too_high
- test_build_connection_data_skips_unknown_metros
- test_render_expansion_map_returns_figure
- test_render_expansion_map_has_speaker_traces
- test_render_expansion_map_has_university_traces
- test_expertise_cluster_colors_has_six_entries

STEP 2 (GREEN): Create src/ui/expansion_map.py following the spec exactly.
- Plotly scatter_geo with 3 layers
- Haversine distance computation
- Coordinate lookup tables from spec

STEP 3 (IMPROVE): Type annotations, docstrings, run full suite.

IMPORTANT: Do NOT modify src/app.py. The orchestrator handles app.py integration.

After implementation: pytest tests/ -v --tb=short
```

### feature-2 (Feedback Loop) Prompt

```
Sprint 3 Task A3.2: Match Acceptance Feedback Loop

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.2. The spec contains COMPLETE function code.

STEP 1 (RED): Write tests/test_acceptance.py with:
- test_feedback_entry_creation
- test_feedback_entry_fields_correct
- test_init_feedback_state_creates_keys
- test_record_feedback_adds_to_log
- test_record_feedback_sets_decision
- test_get_decision_returns_none_when_missing
- test_get_decision_returns_accept
- test_persist_to_csv_creates_file (use tmp_path)
- test_persist_to_csv_appends (use tmp_path)
- test_aggregate_feedback_empty
- test_aggregate_feedback_with_entries
- test_generate_weight_suggestions_below_threshold
- test_generate_weight_suggestions_above_threshold
- test_render_feedback_buttons_shows_accepted_badge

STEP 2 (GREEN): Create:
- src/feedback/__init__.py
- src/feedback/acceptance.py (follow spec exactly)

Wire into src/ui/matches_tab.py: Add render_feedback_buttons() call
AFTER the .ics download button area (after L299). Add import at top of file.

STEP 3 (IMPROVE): Type annotations, run full suite.

IMPORTANT: Do NOT modify src/app.py. The orchestrator handles app.py integration.
Check if DEFAULT_WEIGHTS exists in src/config.py. If not, check src/matching/factors.py.

After implementation: pytest tests/ -v --tb=short
```

### feature-3 (Volunteer Dashboard) Prompt

```
Sprint 3 Task A3.3: Volunteer Dashboard View

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.3.

STEP 1 (RED): Write tests/test_volunteer_dashboard.py with:
- test_compute_speaker_matches_filters_by_name
- test_compute_speaker_matches_returns_top_n
- test_compute_speaker_matches_sorted_descending
- test_compute_speaker_matches_empty_results
- test_compute_utilization_metrics_basic
- test_compute_utilization_metrics_with_feedback
- test_compute_utilization_metrics_zero_events
- test_render_utilization_bar_chart_returns_figure
- test_conversion_rates_values
- test_render_volunteer_dashboard_integration

STEP 2 (GREEN): Create src/ui/volunteer_dashboard.py following the spec.
- Speaker-centric view: selectbox, top-5 events table
- compute_speaker_matches(), compute_utilization_metrics()
- render_utilization_bar_chart() with Plotly bar chart
- CONVERSION_RATES simulated metrics

STEP 3 (IMPROVE): Type annotations, run full suite.

IMPORTANT: Do NOT modify src/app.py. The orchestrator handles app.py integration.
This feature is the FIRST CUT CANDIDATE if time runs short.

After implementation: pytest tests/ -v --tb=short
```

### feature-4 (UI Polish) Prompt

```
Sprint 3 Task A3.4: UI Polish + CSS

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.4.

STEP 1 (RED): Write tests/test_styles.py with:
- test_custom_css_contains_ia_west_colors
- test_custom_css_is_valid_css_string
- test_inject_custom_css_callable
- test_api_call_spinner_is_context_manager
- test_render_error_card_callable
- test_render_error_card_includes_title
- test_brand_colors_constants_defined
- test_streamlit_config_toml_exists

STEP 2 (GREEN): Create:
- src/ui/styles.py with CUSTOM_CSS, inject_custom_css(), api_call_spinner(), render_error_card()
- .streamlit/config.toml with [theme] section

IA West brand colors: navy #1E3A5F, gold #F59E0B, blue #2563EB.

STEP 3 (IMPROVE): Type annotations, run full suite.

IMPORTANT: Do NOT modify src/app.py. The orchestrator handles app.py integration.

After implementation: pytest tests/ -v --tb=short
```

### feature-5 (Real Pipeline Data) Prompt

```
Sprint 3 Task A3.6: Real Pipeline Data

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.6.

STEP 1 (RED): Add tests to tests/test_pipeline_tab.py:
- test_compute_real_funnel_data_returns_ordered_dict
- test_compute_real_funnel_data_counts_match_stages
- test_compute_real_funnel_data_monotonically_decreasing
- test_render_pipeline_tab_prefers_real_data
- test_render_pipeline_tab_falls_back_to_csv
- test_compute_real_funnel_data_empty_input
- test_compute_real_funnel_data_partial_stages

STEP 2 (GREEN): Modify src/ui/pipeline_tab.py:
- Add compute_real_funnel_data() function
- Update render_pipeline_tab() to try real data first, fall back to CSV
- Keep existing load_pipeline_data() and aggregate_funnel_stages() unchanged
- All existing tests must still pass

STEP 3 (IMPROVE): Type annotations, run full suite.

After implementation: pytest tests/ -v --tb=short
```

### feature-6 (Demo Mode) Prompt

```
Sprint 3 Task A3.5: Demo Flow Hardening

YOU MUST FOLLOW TDD. Read the full spec at docs/sprints/sprint-3-polish-freeze.md
task A3.5.

STEP 1 (RED): Write tests/test_demo_mode.py with:
- test_demo_or_live_returns_fixture_in_demo_mode
- test_demo_or_live_calls_func_in_live_mode
- test_init_demo_mode_creates_session_state
- test_fixture_files_exist
- test_fixture_files_valid_json
- test_demo_mode_wraps_discovery_scan
- test_demo_mode_wraps_email_gen

STEP 2 (GREEN): Create:
- src/demo_mode.py with demo_or_live(), init_demo_mode(), load_fixture()
- cache/demo_fixtures/ with 7 JSON fixture files

demo_or_live(func, *args, fixture_key) pattern:
  if st.session_state.get("demo_mode"): return load_fixture(fixture_key)
  else: return func(*args)

STEP 3 (IMPROVE): Type annotations, run full suite.

IMPORTANT: Do NOT modify src/app.py. The orchestrator handles app.py integration.

After implementation: pytest tests/ -v --tb=short
```

### feature-7 (Screenshots) Prompt

```
Sprint 3 Task A3.7: Screenshots for Track B Documentation

NO TDD required for this task (script, not library code).

Create scripts/capture_screenshots.py:
- Use Playwright to launch the Streamlit app
- Navigate to each tab: Matches, Discovery, Pipeline, Expansion, Volunteers
- Also capture with demo mode enabled
- Save 6 PNGs to docs/screenshots/:
  1. matches_tab.png
  2. discovery_tab.png
  3. pipeline_tab.png
  4. expansion_map.png
  5. volunteer_dashboard.png
  6. demo_mode.png
- Viewport: 1920x1080
- Each screenshot should be > 100KB
- If Playwright is unavailable, create a README with manual screenshot instructions
- Create docs/screenshots/ directory

After implementation: verify PNGs exist and are > 100KB
```

---

## 6. Commit Messages (Per Feature)

```
feat(cat3): add board-to-campus expansion map with Plotly scatter_geo
feat(cat3): add match acceptance feedback loop with weight suggestions
feat(cat3): add volunteer dashboard with speaker-centric view
feat(cat3): add UI polish with IA West brand CSS and error handling
feat(cat3): replace simulated pipeline funnel with real prototype data
feat(cat3): add demo mode toggle with cached fixtures
docs(cat3): capture Track B screenshots for all key views
```

---

## 7. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Worker stuck in loop | `get_worker_confidence` to detect, `send_worker_message` to redirect, `rollback_feature` if irrecoverable |
| Worker modifies app.py | Custom prompts explicitly say "DO NOT modify src/app.py". Orchestrator serializes. |
| Worker modifies wrong files | `check_rollback_conflicts` before merge, `rollback_feature` to restore |
| Tests fail after completion | `mark_complete(success=False)` for retry; orchestrator diagnoses before re-launch |
| Merge conflict on app.py | Strict serialization order (feat-1 -> feat-3 -> feat-2 -> feat-4 -> feat-6). Each committed before next. |
| Worker imports Gemini SDK | Custom prompts explicitly say "use generate_text() from src/gemini_client.py, NOT SDK" |
| Worker uses print() | TDD protocol requires logging module; orchestrator reviews before mark_complete |
| DEFAULT_WEIGHTS not in config | feat-2 prompt says "check src/config.py, fallback to src/matching/factors.py" |
| Plotly scatter_geo slow | Steer: fall back to px.scatter_mapbox with OSM tiles (no API key) |
| Volunteer Dashboard cut | Marked as FIRST CUT CANDIDATE; can be deferred to Day 10 bug-fix window |
| Context window overflow | Each task scoped to 1-5 files; Sonnet 4.6 has ample context for single-task focus |

---

## 8. Verification Gates

### Gate 1: Per-Worker (after each feature)

```
# Worker's own tests
run_verification(command="pytest tests/test_<module>.py -v", featureId="feature-N")

# Full regression suite
run_verification(command="pytest tests/ -v --tb=short", featureId="feature-N")
```

### Gate 2: Orchestrator Review (before mark_complete)

The orchestrator (Opus 4.6) checks:
1. `check_worker(featureId, lines=100)` -- read worker output
2. Tests were written FIRST (TDD compliance)
3. Type annotations present on all functions
4. No `print()`, no hardcoded secrets
5. Return contracts match spec
6. Worker did NOT modify src/app.py
7. Only then: `mark_complete(success=True)`

### Gate 3: Integration (after all features)

```
pytest tests/ -v --cov=src --cov-report=term-missing
# Target: 140+ tests, 80%+ coverage
```

### Gate 4: Smoke Test (manual)

```
streamlit run src/app.py
```
- Matches tab: match cards render with feedback buttons
- Discovery tab: university scanner works
- Pipeline tab: funnel chart renders with real data
- Expansion tab: geographic map renders with speaker/university markers
- Volunteers tab: speaker-centric view with bar chart
- Demo mode: sidebar toggle switches between live and fixture data

---

## 9. Timeline Estimate

| Phase | Workers | Wall Clock |
|---|---|---|
| Phase 1: features 1, 2, 3 (parallel) | 3 | ~60-90 min |
| Phase 1 app.py serialization | orchestrator | ~15 min |
| Phase 2: features 4, 5 (parallel) | 2 | ~45-60 min |
| Phase 3: feature 6 | 1 | ~40-60 min |
| Phase 4: feature 7 | 1 | ~15-20 min |
| Integration + smoke test | orchestrator | ~20 min |
| **Total** | | **~3.5-4.5 hours** |

vs. sequential human dev: ~25+ hours

---

## 10. Orchestrator Checklist

```
[ ] Branch sprint3-cat3 created from sprint2-cat3
[ ] orchestrator_init called with all 7 features
[ ] Dependencies set (4->[1,2,3], 5->[2], 6->[4,5], 7->[6])
[ ] Verification configured (pytest)
[ ] Feature context set for all 7 features
[ ] Phase 1 launched: features 1, 2, 3
[ ] Phase 1 monitored: heartbeat checks every 2-3 min
[ ] feature-1 complete -> app.py: add Expansion tab
[ ] feature-3 complete -> app.py: add Volunteers tab
[ ] feature-2 complete -> app.py: add feedback sidebar + matches_tab wired
[ ] Phase 1 committed (3 commits)
[ ] Phase 2 launched: features 4, 5
[ ] feature-4 complete -> app.py: CSS injection
[ ] feature-5 complete -> pipeline_tab.py updated
[ ] Phase 2 committed (2 commits)
[ ] Phase 3 launched: feature 6
[ ] feature-6 complete -> app.py: demo toggle
[ ] Phase 3 committed
[ ] Phase 4 launched: feature 7
[ ] feature-7 complete -> screenshots captured
[ ] Phase 4 committed
[ ] Full test suite: 140+ tests, 80%+ coverage
[ ] Smoke test: app runs, all 5 tabs functional, demo mode works
[ ] Final commit on sprint3-cat3
```
