---
doc_role: canonical
authority_scope:
- category.3.sprint.4
canonical_upstreams:
- Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md
- PRD_SECTION_CAT3.md
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-18'
managed_by: planning-agent
---

# Sprint 4: Testing, Demo Prep, Final Polish — "Ship It"

**Duration:** Days 11-14
**Track:** Both (A + B)
**Hours:** Track A 28-32h, Track B 18-24h

> **Governance notice:** This sprint spec is a deployment/testing derivative of `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` and `PRD_SECTION_CAT3.md`. Use `archived/general_project_docs/MASTER_SPRINT_PLAN.md` and `archived/general_project_docs/STRATEGIC_REVIEW.md` only for portfolio guardrails. `Category 3 - IA West Smart Match CRM/PLAN.md` is background-only.

> This is the final sprint. Feature freeze was enforced at end of Day 9 (Sprint 3). No new code features are permitted. This sprint is exclusively for testing, bug fixing, performance optimization, deployment, demo rehearsal, document finalization, and day-of preparation. Everything must be buttoned up by end of Day 14 for the April 16, 2026 hackathon.

---

## Track A Tasks (Person B) — 28-32h

---

### A4.1: End-to-End Testing — Day 11 (4.0h)

#### Specification

Complete the full demo flow checklist three times in sequence, logging every defect encountered. Each run must exercise every feature path that will be shown during the live demo.

**Test Flow Checklist (run 3x):**

| Step | Action | Expected Result | Pass/Fail |
|------|--------|-----------------|-----------|
| 1 | Launch app (`streamlit run src/app.py`) | App loads in <3s, sidebar renders with IA West branding, Discovery tab is default | |
| 2 | Discovery tab: select "UCLA" from university dropdown | UCLA appears selected, status shows "Ready" or "Cached" | |
| 3 | Click "Discover Events" | Scrape initiates (or loads from cache), progress indicator visible, results populate within 5s | |
| 4 | Review extracted events table | Minimum 3 events displayed with valid event_name, category, date, volunteer_roles fields | |
| 5 | Click "Add to Matching" on first event | Confirmation message, event appears in Matches tab data | |
| 6 | Navigate to Matches tab | Tab loads, event selector dropdown populated | |
| 7 | Select the UCLA event added in step 5 | Top-3 speaker cards render with match scores | |
| 8 | Review top match card | Name, title, company, match score (numeric), radar chart (6 factors), explanation card text all visible | |
| 9 | Adjust weight slider (increase geographic_proximity to 0.40) | Rankings recompute in <1s, order may change, scores update visibly | |
| 10 | Reset weights to defaults | Original rankings restored | |
| 11 | Click "Generate Email" on top match | Personalized outreach email renders in preview panel within 2s | |
| 12 | Click "Copy to Clipboard" on email | Clipboard confirmation message | |
| 13 | Click "Download Calendar Invite" | `.ics` file downloads, valid when opened in calendar app | |
| 14 | Navigate to Pipeline tab | Funnel chart renders with real data labels | |
| 15 | Hover over funnel stages | Tooltips show real speaker/event names, not placeholder text | |
| 16 | Review funnel numbers | Stages: Discovered > Matched > Contacted > Confirmed > Attended > Member Inquiry, each smaller than previous | |
| 17 | Navigate to Volunteer Dashboard (if built) | Per-speaker view loads, bar chart shows utilization | |
| 18 | Select a board member | Top-5 matched events display with scores | |
| 19 | Navigate to Expansion Map (if built) | Map renders with speaker locations + university locations + connection lines | |
| 20 | Toggle Demo Mode in sidebar | App switches to cached outputs, artificial delays visible | |
| 21 | Repeat steps 2-16 in Demo Mode | All features work identically using cached data | |

**Bug Logging Template:**

Each bug must be logged in `docs/testing/test_log.md` using this exact format:

```markdown
### BUG-{NNN}: {Short title}

| Field | Value |
|-------|-------|
| **ID** | BUG-{NNN} |
| **Severity** | P0 / P1 / P2 / P3 |
| **Test Run** | Run 1 / Run 2 / Run 3 |
| **Step** | Step {N} of test flow |
| **Description** | {What went wrong} |
| **Steps to Reproduce** | 1. ... 2. ... 3. ... |
| **Expected Behavior** | {What should happen} |
| **Actual Behavior** | {What actually happened} |
| **Screenshot** | {path to screenshot or "N/A"} |
| **Status** | OPEN / FIXING / FIXED / VERIFIED / WONTFIX |
| **Fixed In** | {commit hash or "pending"} |
| **Verified By** | {Person B / Person C} |
```

**Severity Classification:**

| Severity | Definition | Examples | Fix Deadline |
|----------|-----------|----------|-------------|
| **P0 — Crash** | App crashes, becomes unresponsive, or loses data | Unhandled exception on tab switch, Streamlit white screen, infinite spinner | Must fix before Day 12 EOD |
| **P1 — Incorrect Scores** | Match scores, rankings, or pipeline data are wrong | Wrong speaker in top-3, score breakdown doesn't sum to total, funnel numbers impossible | Must fix before Day 12 EOD |
| **P2 — UI Issues** | Visual defects that don't affect functionality | Chart overlaps text, button doesn't align, color scheme broken on one card | Fix if time permits, Day 12-13 |
| **P3 — Performance** | Slow but functional | Page load >5s, email generation >4s, slider lag >2s | Optimize if time permits |

**Test Log Location:** `docs/testing/test_log.md`

**Test Log Header:**

```markdown
# SmartMatch End-to-End Test Log

**Tester:** Person B
**App Version:** {git commit hash}
**Date:** {YYYY-MM-DD}
**Environment:** {Local / Streamlit Cloud}
**Python Version:** {3.10.x / 3.11.x}

## Test Runs Summary

| Run | Date | Time | P0 | P1 | P2 | P3 | Total | Pass Rate |
|-----|------|------|----|----|----|----|----|-----------|
| Run 1 | | | | | | | | |
| Run 2 | | | | | | | | |
| Run 3 | | | | | | | | |

## Bugs

{bugs follow using template above}
```

#### Acceptance Criteria

- [ ] Test flow checklist completed 3 times in full
- [ ] Every step in the 21-step checklist has a Pass/Fail recorded per run
- [ ] All bugs logged in `docs/testing/test_log.md` with correct template format
- [ ] Every bug assigned a severity level (P0/P1/P2/P3)
- [ ] Test runs summary table populated with counts per severity
- [ ] Demo Mode tested in at least 1 full run

#### Harness Guidelines

- Create `docs/testing/test_log.md` before starting first run
- Commit test log after each full run (3 commits minimum)
- If a P0 bug is found during Run 1, do NOT continue to Run 2 until the P0 is fixed (switch to A4.2)
- Take screenshots of all P0 and P1 bugs

#### Steer Guidelines

- If Run 1 produces 3+ P0 bugs, STOP testing and escalate to full bug-fix session (A4.2)
- If Demo Mode fails completely, escalate immediately — this is the primary backup plan
- Track time per test run; target is 20-30 minutes per run including logging
- If test run takes >45 minutes, the demo is too slow and needs performance work (A4.4)

---

### A4.2: Bug Fixes — Days 11-12 (4.0h)

#### Specification

Fix all bugs found in A4.1, strictly following priority order. Each fix must be verified through the specific test-flow step where the bug was discovered, plus a regression test of adjacent steps.

**Priority Order (non-negotiable):**

1. **P0 — Crash bugs** (fix immediately, before any other work)
2. **P1 — Incorrect scores** (fix same day as discovery)
3. **P2 — UI issues** (fix if time permits after all P0/P1 resolved)
4. **P3 — Performance** (defer to A4.4 unless trivially fixable)

**Fix Verification Procedure:**

```
For each bug:
1. REPRODUCE: Confirm the bug still exists (follow Steps to Reproduce)
2. DIAGNOSE: Identify root cause; note affected file(s) and line(s)
3. FIX: Implement the minimal fix (no refactoring, no feature additions)
4. VERIFY: Re-run the exact Steps to Reproduce — expected behavior now occurs
5. REGRESSION: Run test flow steps {N-1} through {N+2} to ensure no side effects
6. UPDATE: Set bug status to FIXED, record commit hash in test_log.md
7. COMMIT: Commit with message "fix: {BUG-NNN} {short description}"
```

**Bug Tracker Location:** `docs/testing/bug_log.md`

**Bug Tracker Template:**

```markdown
# SmartMatch Bug Tracker

## Active Bugs (sorted by severity, then ID)

| ID | Severity | Title | Status | Assigned | Fix Commit | Verified |
|----|----------|-------|--------|----------|-----------|----------|
| BUG-001 | P0 | {title} | OPEN | Person B | — | — |

## Resolved Bugs

| ID | Severity | Title | Fix Commit | Verified By | Regression Passed |
|----|----------|-------|-----------|-------------|-------------------|

## Fix Session Log

| Session | Date | Duration | Bugs Fixed | Bugs Remaining (P0/P1/P2/P3) |
|---------|------|----------|------------|-------------------------------|
| Session 1 | | | | |
| Session 2 | | | | |
```

**Escalation Rules:**

- If a P0 bug cannot be fixed within 1 hour: disable the affected feature and update Demo Mode to skip it
- If total P0+P1 bugs exceed 5: trigger scope cut discussion — refer to SPRINT_PLAN.md Cut Priority list
- If a P1 bug is in the matching engine (MATCH_SCORE formula): this is effectively P0 — the matching engine is the MVP

#### Acceptance Criteria

- [ ] Zero P0 bugs remaining (all FIXED and VERIFIED)
- [ ] Zero P1 bugs remaining (all FIXED and VERIFIED)
- [ ] Bug tracker `docs/testing/bug_log.md` is up to date
- [ ] Every fix has a corresponding commit with `fix:` prefix
- [ ] Regression tests passed for every fixed bug
- [ ] Test flow run completed cleanly after all P0/P1 fixes

#### Harness Guidelines

- Bug tracker in `docs/testing/bug_log.md` — create before first fix session
- Cross-reference bugs between `test_log.md` (discovery) and `bug_log.md` (resolution)
- Each fix session logged with duration and bugs fixed

#### Steer Guidelines

- Do NOT attempt to fix P2/P3 bugs until all P0 and P1 bugs are resolved
- Do NOT refactor code while fixing bugs — minimal fixes only
- If the matching engine has a P1 bug, drop everything else and fix it first
- Budget: 1 hour max per P0 bug, 30 minutes max per P1 bug — if exceeded, consider disabling the feature

---

### A4.3: Edge Case Hardening — Day 12 (3.0h)

#### Specification

Systematically test failure modes that could occur during the live demo and implement graceful handling for each.

**Edge Case Test Matrix:**

| # | Scenario | Trigger Method | Expected Behavior | Error Message / Fallback |
|---|----------|---------------|-------------------|--------------------------|
| 1 | Scraping failure mid-demo | Disconnect WiFi, then click "Discover Events" | App detects network failure, loads cached results with status "Using cached data (scraped {date})" | `"Live scrape unavailable. Showing cached results from {timestamp}."` |
| 2 | Gemini API timeout | Set API key to invalid value or block `generativelanguage.googleapis.com` | App shows cached explanation card with status indicator "(cached)" | `"AI explanation temporarily unavailable. Showing previously generated explanation."` |
| 3 | All weights set to 0 | Move all 6 weight sliders to 0.00 | App shows error message in sidebar, does not compute scores | `"At least one weight must be greater than 0. Please adjust weights."` |
| 4 | Custom URL with garbage HTML | Enter `https://example.com` in custom URL field, click Discover | App attempts extraction, returns empty results with error status | `"Could not extract events from this page. The page may not contain recognizable event listings."` |
| 5 | Empty CSV file | Replace a data CSV with headers-only file, restart app | App detects empty data, shows informative error on relevant tab | `"No {speakers/events/courses} found in data file. Please check {filename}."` |
| 6 | Network disconnection (full offline) | Disconnect all network, use app in Demo Mode | App operates fully in Demo Mode using cached data for all features | `"Offline mode: all features using cached data."` |
| 7 | Very long speaker name or expertise tags | Manually add a speaker with 500-char expertise field | UI card does not overflow, text truncates with ellipsis | N/A (graceful rendering) |
| 8 | Concurrent widget interactions | Rapidly click multiple buttons while slider is adjusting | No race conditions, no duplicate API calls, UI remains responsive | N/A (no crash) |
| 9 | Browser back/forward during multi-tab use | Use browser navigation buttons within Streamlit | App state preserved or gracefully resets | N/A (Streamlit handles) |
| 10 | Stale cache (>24h old) | Manually set cache timestamp to >24h ago | App shows warning but still uses cache | `"Cached data is {N} hours old. Live scrape recommended."` |

**Error Handler Function Signatures:**

```python
def handle_scrape_failure(url: str, cache_path: str) -> dict:
    """Handle web scraping failure by falling back to cached results.

    Args:
        url: The URL that failed to scrape.
        cache_path: Path to the JSON cache file for this URL.

    Returns:
        Dict with keys: 'events' (list), 'source' ('cache'|'error'),
        'message' (str), 'cached_at' (str|None).

    Raises:
        FileNotFoundError: When no cache exists for this URL (show empty state).
    """


def handle_api_timeout(
    speaker_id: str,
    event_id: str,
    cache_key: str,
    timeout_seconds: float = 10.0
) -> dict:
    """Handle Gemini API timeout by returning cached explanation.

    Args:
        speaker_id: ID of the speaker being explained.
        event_id: ID of the event being matched.
        cache_key: Key for looking up cached explanation.
        timeout_seconds: Seconds before declaring timeout.

    Returns:
        Dict with keys: 'explanation' (str), 'source' ('api'|'cache'|'error'),
        'message' (str).
    """


def validate_weights(weights: dict[str, float]) -> tuple[bool, str]:
    """Validate that weight configuration is valid for scoring.

    Args:
        weights: Dict mapping factor names to float weights.

    Returns:
        Tuple of (is_valid, error_message). error_message is empty string if valid.
    """


def handle_extraction_failure(url: str, raw_html: str) -> dict:
    """Handle LLM extraction failure from scraped HTML.

    Args:
        url: Source URL for the HTML.
        raw_html: The HTML content that could not be parsed.

    Returns:
        Dict with keys: 'events' (empty list), 'source' ('error'),
        'message' (str explaining the failure).
    """


def validate_data_files(data_dir: str) -> dict[str, dict]:
    """Validate all required CSV data files on startup.

    Args:
        data_dir: Path to directory containing CSV files.

    Returns:
        Dict mapping filename to {'valid': bool, 'rows': int, 'message': str}.

    Raises:
        SystemExit: If ALL data files are missing or empty (cannot operate).
    """
```

**Implementation Procedure:**

For each edge case:
1. Write the trigger code / manual test steps
2. Implement the error handler (if not already implemented)
3. Test the edge case
4. Verify the user-facing message is clear and non-technical
5. Log result in `docs/testing/test_log.md` under "Edge Case Tests" section

#### Acceptance Criteria

- [ ] All 10 edge cases tested and results logged
- [ ] Scraping failure falls back to cache with user-visible message
- [ ] API timeout returns cached explanation with "(cached)" indicator
- [ ] Zero-weights shows clear error and does not crash
- [ ] Garbage HTML shows graceful error, not a stack trace
- [ ] Empty CSV shows informative error referencing the specific file
- [ ] Full offline mode works with Demo Mode toggle
- [ ] No unhandled exceptions in any edge case test

#### Harness Guidelines

- Log edge case results in `docs/testing/test_log.md` under a separate "Edge Case Tests" section
- Each edge case gets a Pass/Fail with notes
- Screenshots of error messages for P0/P1 scenarios

#### Steer Guidelines

- If any edge case causes a crash (P0), fix it immediately before testing the next edge case
- Prioritize scenarios 1 (scrape failure), 2 (API timeout), and 6 (offline) — these are the most likely demo-day failures
- Do NOT spend more than 20 minutes implementing a single error handler — if it takes longer, use a simple try/except with st.error()
- The goal is "graceful degradation," not "perfect error handling"

---

### A4.4: Performance Optimization — Day 12 (2.0h)

#### Specification

Profile the Streamlit app and optimize to meet target performance metrics.

**Profiling Procedure:**

1. **Streamlit built-in profiling:**
   ```bash
   # Run with Streamlit's built-in timing
   streamlit run src/app.py --logger.level=debug
   ```
   Monitor the terminal for render times per component.

2. **cProfile for Python hotspots:**
   ```python
   import cProfile
   import pstats

   # Profile the matching engine
   profiler = cProfile.Profile()
   profiler.enable()
   # ... run matching for all 270 pairs ...
   profiler.disable()
   stats = pstats.Stats(profiler)
   stats.sort_stats('cumulative')
   stats.print_stats(20)  # Top 20 hotspots
   ```

3. **Memory profiling:**
   ```bash
   pip install memory-profiler
   python -m memory_profiler app.py
   ```

**Target Metrics:**

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Initial app load (cold start) | < 3 seconds | Stopwatch from `streamlit run` to first full render |
| Tab switch | < 0.5 seconds | Stopwatch from click to full render |
| Scrape + extract (cached) | < 2 seconds | Stopwatch from "Discover Events" click to results table |
| Scrape + extract (live) | < 5 seconds | Stopwatch from "Discover Events" click to results table |
| Match score recomputation (slider change) | < 1 second | Stopwatch from slider release to updated cards |
| Email generation (cached) | < 0.5 seconds | Stopwatch from "Generate Email" click to preview |
| Email generation (live API) | < 2 seconds | Stopwatch from "Generate Email" click to preview |
| Explanation card (cached) | < 0.5 seconds | Stopwatch from event selection to explanation text |
| Pipeline funnel render | < 1 second | Stopwatch from Pipeline tab click to chart visible |
| Memory footprint (steady state) | < 500 MB | `memory-profiler` output |

**Optimization Techniques Checklist:**

- [ ] **Pre-compute embeddings at startup:**
  ```python
  @st.cache_resource
  def load_embeddings():
      """Load Sprint 0 flat embedding artifacts. Never recompute during session."""
      return {
          "speaker_embeddings": np.load("cache/speaker_embeddings.npy"),
          "event_embeddings": np.load("cache/event_embeddings.npy"),
          "course_embeddings": np.load("cache/course_embeddings.npy"),
      }
  ```

- [ ] **Cache data loading:**
  ```python
  @st.cache_data
  def load_csv_data():
      """Load all 4 CSVs once per session. Returns tuple of DataFrames."""
      speakers = pd.read_csv("data/data_speaker_profiles.csv")
      events = pd.read_csv("data/data_cpp_events_contacts.csv")
      courses = pd.read_csv("data/data_cpp_course_schedule.csv")
      calendar = pd.read_csv("data/data_event_calendar.csv")
      return speakers, events, courses, calendar
  ```

- [ ] **Cache scraping results:**
  ```python
  @st.cache_data(ttl=86400)  # 24-hour TTL
  def get_cached_scrape(url: str) -> dict:
      """Return cached scrape results. TTL ensures freshness."""
      ...
  ```

- [ ] **Cache LLM responses:**
  ```python
  @st.cache_data
  def get_match_explanation(speaker_id: str, event_id: str, score_breakdown: dict) -> str:
      """Cache explanation cards to avoid redundant API calls."""
      ...
  ```

- [ ] **Lazy load scraping results:**
  - Do NOT scrape all 5 universities on app load
  - Scrape only when user clicks "Discover Events"
  - Show cached timestamp if results already exist

- [ ] **Minimize re-renders with `st.fragment`:**
  ```python
  @st.fragment
  def match_cards_section(event_id: str):
      """Render match cards without re-running entire page."""
      ...
  ```

- [ ] **Pre-compute cosine similarity matrix:**
  ```python
  @st.cache_data
  def compute_similarity_matrix(speaker_embeddings, event_embeddings):
      """Compute full 18x15 matrix once, index into it for lookups."""
      from numpy import dot
      from numpy.linalg import norm
      # Vectorized computation, not loop
      ...
  ```

- [ ] **Optimize Plotly chart rendering:**
  - Use `st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})`
  - Disable unnecessary Plotly toolbar buttons
  - Pre-build chart figures for Demo Mode

**Performance Log:**

```markdown
## Performance Measurements

| Metric | Before Optimization | After Optimization | Target | Status |
|--------|--------------------|--------------------|--------|--------|
| Initial load | | | <3s | |
| Tab switch | | | <0.5s | |
| Scrape (cached) | | | <2s | |
| Scrape (live) | | | <5s | |
| Slider recompute | | | <1s | |
| Email gen (cached) | | | <0.5s | |
| Email gen (live) | | | <2s | |
| Memory | | | <500MB | |
```

#### Acceptance Criteria

- [ ] All target metrics measured and logged (before/after)
- [ ] Initial app load under 3 seconds
- [ ] Scrape + extract under 5 seconds (live), under 2 seconds (cached)
- [ ] Email generation under 2 seconds
- [ ] Slider recomputation under 1 second (real-time feel)
- [ ] Memory footprint under 500 MB
- [ ] All `@st.cache_data` and `@st.cache_resource` decorators applied appropriately
- [ ] No unnecessary API calls on page re-render

#### Harness Guidelines

- Log performance measurements in `docs/testing/test_log.md` under "Performance" section
- Record before/after for each optimization applied

#### Steer Guidelines

- Spend maximum 30 minutes on any single optimization
- If a metric cannot be met, document the bottleneck and note it as a known limitation
- Prioritize: slider responsiveness > initial load > email generation > scraping speed
- Do NOT introduce caching bugs — test the cache invalidation path after every change
- If memory exceeds 800 MB, investigate DataFrame copies and Plotly figure retention

---

### A4.5: Streamlit Cloud Deployment — Day 12 (2.0h)

#### Specification

Deploy the application to Streamlit Community Cloud for public access and judge review.

**Deployment Checklist:**

1. **Repository preparation:**
   - [ ] `requirements.txt` verified and minimal (no dev-only packages)
   - [ ] All import paths are relative (no absolute local paths)
   - [ ] No hardcoded file paths (use `pathlib.Path` or `os.path`)
   - [ ] `.gitignore` excludes: `.env`, `cache/`, `*.pyc`, `__pycache__/`, `.pkl` files >50MB

2. **`requirements.txt` verification:**
   ```
   streamlit>=1.32.0
   # Gemini API helper in src/gemini_client.py (no separate SDK required)
   pandas>=2.0.0
   plotly>=5.18.0
   beautifulsoup4>=4.12.0
   requests>=2.31.0
   numpy>=1.24.0
   icalendar>=5.0.0
   ```
   - [ ] Every import in `src/` has a corresponding entry in `requirements.txt`
   - [ ] No version conflicts (run `pip check` locally)
   - [ ] Playwright is NOT in `requirements.txt` (doesn't work on Streamlit Cloud)

3. **`runtime.txt` for Python version:**
   ```
   python-3.11
   ```
   - [ ] File exists at repo root
   - [ ] Python version matches local development version

4. **Secrets configuration:**
   - [ ] In Streamlit Cloud dashboard: Settings > Secrets
   - [ ] Add `GEMINI_API_KEY = "AIza..."` (from `.env`)
   - [ ] Verify in code: `st.secrets["GEMINI_API_KEY"]` is used, NOT `os.environ`
   - [ ] Code handles both methods for local vs. cloud:
     ```python
     import os
     import streamlit as st

     def get_api_key() -> str:
         """Get Gemini API key from Streamlit secrets (cloud) or env var (local)."""
         try:
             return st.secrets["GEMINI_API_KEY"]
         except (FileNotFoundError, KeyError):
             key = os.environ.get("GEMINI_API_KEY")
             if not key:
                 st.error("GEMINI_API_KEY not found. Set it in .env or Streamlit Cloud secrets.")
                 st.stop()
             return key
     ```

5. **Memory limit considerations (1 GB RAM):**
   - [ ] Total DataFrame memory < 50 MB (77 rows should be ~1 MB)
   - [ ] Embeddings cache < 100 MB (68 vectors x 1536 dims x 4 bytes = ~0.4 MB)
   - [ ] No Playwright loaded (dynamically skip)
   - [ ] Plotly figures rendered one at a time (not all simultaneously)
   - [ ] Test: monitor cloud app logs for OOM errors

6. **Playwright workaround:**
   ```python
   import importlib

   def is_cloud_environment() -> bool:
       """Detect if running on Streamlit Community Cloud."""
       return os.environ.get("STREAMLIT_SERVER_HEADLESS") == "true"

   def scrape_university(
       url: str,
       method: Literal["bs4", "playwright"] = "bs4",
       cache_dir: str = DEFAULT_CACHE_DIR,
   ) -> dict[str, Any]:
       """Preserve Sprint 2's scrape contract on cloud and local."""
       if is_cloud_environment():
           cached = load_from_cache(url, cache_dir)
           if cached is None:
               raise FileNotFoundError(f"No cached scrape available for {url}")
           cached["source"] = "cache"
           cached["robots_ok"] = cached.get("robots_ok", True)
           return cached
       return sprint2_scrape_university(url=url, method=method, cache_dir=cache_dir)
   ```

7. **Post-deployment verification:**
   - [ ] App loads on `https://{app-name}.streamlit.app`
   - [ ] All 3 tabs render correctly
   - [ ] Matching engine produces correct results
   - [ ] Email generation works (API key properly configured)
   - [ ] Discovery tab shows cached results (live scrape disabled on cloud)
   - [ ] Pipeline funnel renders
   - [ ] No errors in Streamlit Cloud logs
   - [ ] Share URL with Person C for verification

**Fallback Plan:**
If Streamlit Cloud deployment fails after 1 hour of troubleshooting:
- Run demo locally on Day 14
- Note for judges: "Live app available at [URL] — today's demo runs locally for reliability"
- This is explicitly acceptable per SPRINT_PLAN.md risk gates

#### Acceptance Criteria

- [ ] App deployed to Streamlit Community Cloud
- [ ] Secrets configured (GEMINI_API_KEY accessible)
- [ ] All tabs load without errors on cloud
- [ ] Memory usage stays below 1 GB
- [ ] Playwright is gracefully disabled on cloud (no import errors)
- [ ] `requirements.txt` has no extraneous packages
- [ ] `runtime.txt` specifies correct Python version
- [ ] Deployment URL shared with team

#### Harness Guidelines

- Deployment URL and status recorded in `docs/testing/test_log.md`
- Cloud-specific issues logged as bugs in `docs/testing/bug_log.md`

#### Steer Guidelines

- If deployment fails due to a dependency issue, strip the problematic package and use the fallback
- Maximum 1 hour on deployment troubleshooting — after that, commit to local demo
- Do NOT install Playwright on Streamlit Cloud — it will exceed memory limits
- Test with a fresh incognito browser to catch cookie/state issues

---

### A4.6: Demo Rehearsal with Person C — Day 13 (3.0h)

#### Specification

Conduct three full 5-minute demo rehearsals with Person C narrating and Person B operating the app. Each rehearsal must be timed, logged, and reviewed.

**Rehearsal Checklist (3 full runs):**

**Run 1 — Discovery Run (focus: flow and timing)**
- [ ] Full flow executed without consulting notes
- [ ] Each section timed individually (use stopwatch)
- [ ] Note any hesitations, fumbles, or unclear transitions
- [ ] Test all app interactions (clicks, slider, email gen, download)
- [ ] Log section timings in timing template
- [ ] Debrief: identify top 3 improvements needed

**Run 2 — Backup Plan Run (focus: failure recovery)**
- [ ] At 1:15 mark, deliberately trigger scraping failure (disconnect WiFi)
- [ ] Person C: practice the transition phrase for cached results
- [ ] At 3:15 mark, deliberately trigger API timeout (invalid key)
- [ ] Person C: practice the transition phrase for cached email
- [ ] Test "Total Meltdown" scenario: switch to backup video mid-demo
- [ ] Debrief: rate confidence in backup plan (1-5)

**Run 3 — Timed Competition Run (focus: exactly 5 minutes)**
- [ ] Start timer at 0:00, aim for finish at 4:50-5:00
- [ ] No stops, no do-overs — simulate actual presentation
- [ ] Person C narrates continuously, Person B operates silently
- [ ] If overtime (>5:15): identify which section to cut 15 seconds from
- [ ] If undertime (<4:30): identify where to add depth or pause for effect
- [ ] Debrief: final timing adjustments

**Timing Log Template:**

```markdown
# Demo Rehearsal Timing Log

## Run {N} — {Date} {Time}

| Section | Target Time | Actual Time | Delta | Notes |
|---------|------------|-------------|-------|-------|
| Problem Statement | 0:00-0:30 (30s) | | | |
| Solution Overview | 0:30-1:15 (45s) | | | |
| Live Demo: Discovery | 1:15-2:15 (60s) | | | |
| Live Demo: Matching | 2:15-3:15 (60s) | | | |
| Live Demo: Email + Calendar | 3:15-3:45 (30s) | | | |
| Pipeline + ROI | 3:45-4:15 (30s) | | | |
| Written Deliverables | 4:15-4:45 (30s) | | | |
| Responsible AI | 4:45-5:00 (15s) | | | |
| **Total** | **5:00** | | | |

### Transition Notes
- Problem → Solution: "{exact transition phrase}"
- Solution → Discovery: "{exact transition phrase}"
- Discovery → Matching: "{exact transition phrase}"
- Matching → Email: "{exact transition phrase}"
- Email → Pipeline: "{exact transition phrase}"
- Pipeline → Deliverables: "{exact transition phrase}"
- Deliverables → Responsible AI: "{exact transition phrase}"

### Issues Identified
1. {issue}
2. {issue}

### Action Items
1. {action}
2. {action}
```

**Role Split:**

| Person | Responsibility | Notes |
|--------|---------------|-------|
| **Person C (Narrator)** | All spoken content, transitions, audience engagement, pointing to screen elements, referring to written deliverables | Must NOT touch the keyboard |
| **Person B (Operator)** | All app interactions: clicks, slider adjustments, scrolling, switching tabs, triggering fallback if needed | Must operate silently, follow Person C's verbal cues |

**Verbal Cues (Person C to Person B):**

| Cue Phrase | Person B Action |
|-----------|----------------|
| "Let's see what SmartMatch finds at UCLA" | Click "Discover Events" |
| "Now let's look at who SmartMatch recommends" | Navigate to Matches tab, select UCLA event |
| "Watch what happens when we prioritize geographic proximity" | Adjust proximity slider to 0.40 |
| "SmartMatch can draft the outreach email automatically" | Click "Generate Email" |
| "And even create a calendar invite" | Click "Download Calendar Invite" |
| "Let's look at the bigger picture" | Navigate to Pipeline tab |
| "We can switch to demo mode if needed" (backup only) | Toggle Demo Mode |

**Transition Practice Points:**

1. Problem → Solution: "So how do we fix this? Meet SmartMatch." (gesture to app)
2. Solution → Discovery: "Let me show you SmartMatch in action. First, discovery." (nod to Person B)
3. Discovery → Matching: "Now that we've found opportunities, who should go?" (transition naturally)
4. Matching → Email: "Once we have the right match, outreach is one click away." (pause for email gen)
5. Email → Pipeline: "Every interaction feeds into our engagement pipeline." (tab switch)
6. Pipeline → Deliverables: "The data from this pipeline drives our growth strategy." (hold up document or reference)
7. Deliverables → AI: "And every recommendation is fully explainable." (final 15 seconds)

#### Acceptance Criteria

- [ ] 3 full rehearsals completed
- [ ] Timing log filled out for each run
- [ ] All 3 runs complete without app crashes
- [ ] Run 3 completes within 4:45-5:15 window
- [ ] Backup plan tested in Run 2 with successful recovery
- [ ] Both team members confident in their roles (self-assessment 4+ out of 5)
- [ ] Transition phrases practiced and smooth
- [ ] Written deliverables handoff practiced in at least 1 run

#### Harness Guidelines

- Timing logs saved to `docs/demo/rehearsal_log.md`
- Record Run 3 as a reference (not the backup video — that's A4.7)

#### Steer Guidelines

- If Run 1 takes >7 minutes, immediately identify which section to cut
- If the app crashes during any rehearsal, treat it as a P0 bug — go back to A4.2
- Person C must NOT read from notes during Run 3 — this simulates actual conditions
- If Person C and Person B are out of sync (operator too fast/slow), practice verbal cues until natural
- Never cut: matching demo, discovery demo, email generation, pipeline funnel

---

### A4.7: Backup Demo Video — Day 13 (2.0h)

#### Specification

Record a screen capture of a perfect demo run with narration. This is the emergency backup if everything fails on demo day.

**Recording Setup:**

| Setting | Value |
|---------|-------|
| Resolution | 1920x1080 (1080p) |
| Frame Rate | 30 fps |
| Audio | System audio + microphone (Person C narration) |
| Format | MP4 (H.264 codec) |
| Max Duration | 5 minutes (hard limit) |
| File Size Target | < 200 MB |

**Recording Tools (in preference order):**
1. OBS Studio (free, cross-platform, best quality)
2. Windows Game Bar (Win+G, built-in, quick)
3. PowerPoint screen recording (available if Office installed)
4. Loom (browser-based, requires account)

**OBS Studio Settings (if used):**
```
Output:
  Recording Path: docs/demo/
  Recording Format: mp4
  Encoder: x264
  Rate Control: CRF (23)

Video:
  Base Resolution: 1920x1080
  Output Resolution: 1920x1080
  FPS: 30

Audio:
  Desktop Audio: enabled
  Mic/Aux: enabled (Person C's mic)
```

**Recording Script (matches demo flow exactly):**

```
[0:00-0:03] Title card: "IA SmartMatch — AI-Orchestrated Speaker-Event Matching CRM"
             (Create in any presentation tool, display fullscreen before starting app)

[0:03-0:30] PROBLEM
             Narration: "IA West coordinates 18 board members across 6 metro regions
             for 8+ events per year — entirely via email chains and gut feel. With 35
             CPP course sections going untapped and no measurement of the engagement
             pipeline, IA West is leaving impact on the table."
             Visual: Show app landing page or a problem summary slide

[0:30-1:15] SOLUTION OVERVIEW
             Narration: "SmartMatch automates the full lifecycle: discover university
             opportunities, match them with the right board member volunteers, generate
             personalized outreach, and track the entire engagement funnel."
             Visual: Show architecture diagram or navigate through tabs overview

[1:15-2:15] LIVE DEMO: DISCOVERY
             Narration: "Let's say a new hackathon was just announced at UCLA.
             SmartMatch automatically discovers it."
             Visual: Navigate to Discovery tab, select UCLA, click "Discover Events",
             show results populating. Click "Add to Matching" on first event.

[2:15-3:15] LIVE DEMO: MATCHING
             Narration: "Now SmartMatch recommends the best volunteers. Travis Miller,
             SVP of Sales from Ventura, matches at 87% because his MR technology
             expertise aligns with the event's data science focus."
             Visual: Navigate to Matches tab, select event, show top-3 cards with
             radar charts. Read explanation card. Adjust weight slider — show
             rankings change.

[3:15-3:45] LIVE DEMO: EMAIL + CALENDAR
             Narration: "One click generates a personalized outreach email referencing
             Travis's specific expertise and the event details. We can even create
             a calendar invite."
             Visual: Click "Generate Email", show email preview. Click "Download
             Calendar Invite".

[3:45-4:15] PIPELINE + ROI
             Narration: "Every interaction feeds into our engagement pipeline. From 60+
             discovered events across 5 universities, SmartMatch generated 45 top
             matches, projected to save 199 volunteer hours per quarter — nearly
             $10,000 in opportunity cost."
             Visual: Navigate to Pipeline tab, show funnel chart. Hover over stages.

[4:15-4:45] WRITTEN DELIVERABLES
             Narration: "Our Growth Strategy details a 3-phase rollout from CPP to
             the full West Coast corridor, with specific KPIs in our Measurement Plan."
             Visual: Show document thumbnails or reference printed copies.

[4:45-5:00] RESPONSIBLE AI
             Narration: "Every match is explainable — no black boxes. We conducted a
             bias audit across all 18 speakers and implemented a diversity rotation
             flag to ensure fair matching."
             Visual: Point to score breakdown, explanation card.

[5:00] End card: "Thank you — IA SmartMatch"
```

**Editing Requirements:**
- Title card at start (3 seconds)
- End card at finish (3 seconds)
- No mid-video cuts unless absolutely necessary (continuous flow preferred)
- If the recording has a stumble, re-record rather than editing
- Audio levels consistent throughout (normalize in post if needed)

**Output:** `docs/demo/backup_demo.mp4`

#### Acceptance Criteria

- [ ] Video recorded at 1920x1080, 30fps
- [ ] Duration between 4:45 and 5:15
- [ ] Audio is clear and audible (test playback on laptop speakers)
- [ ] All demo features visible and functional in recording
- [ ] Title card and end card present
- [ ] File saved to `docs/demo/backup_demo.mp4`
- [ ] File size under 200 MB
- [ ] Video plays correctly on at least 2 different players (VLC + browser)
- [ ] Person C has reviewed and approved the recording

#### Harness Guidelines

- Output file: `docs/demo/backup_demo.mp4`
- If file is too large for git, store on Google Drive/OneDrive and link in `docs/demo/README.md`
- Keep raw recording as well (do not delete source after export)

#### Steer Guidelines

- Record AFTER rehearsals (A4.6) — use the polished flow from Run 3
- If the first recording has a stumble in the first 2 minutes, re-record from scratch
- If a stumble happens after 3 minutes, decide whether to re-record or keep (time vs. quality)
- Maximum 3 recording attempts — after that, use the best take
- This is insurance — spend the time, but do not obsess over perfection

---

### A4.8: Final Code Cleanup — Day 14 (2.0h)

#### Specification

Clean up the codebase for submission. No functional changes — only documentation, formatting, and hygiene.

**Docstring Template for Key Functions:**

Apply this docstring format to every public function in these critical modules:
- `src/matching.py` (or equivalent matching engine module)
- `src/scraper.py` (or equivalent scraping module)
- `src/email_generator.py` (or equivalent email module)
- `src/pipeline.py` (or equivalent pipeline module)
- `app.py` (main Streamlit app)

```python
def function_name(param: type, other_param: type = default) -> return_type:
    """One-line summary of what this function does.

    Longer description if the function is complex (matching engine,
    scoring formula, etc.). Include the business logic rationale.

    Args:
        param: Description of this parameter.
        other_param: Description with default value noted.

    Returns:
        Description of the return value, including structure if it's
        a dict or complex type.

    Raises:
        ValueError: When invalid input is provided (e.g., all weights zero).
        FileNotFoundError: When required data file is missing.

    Example:
        >>> compute_match_score("speaker_001", "event_003", default_weights)
        {'total': 0.87, 'factors': {'topic': 0.92, 'role': 0.80, ...}}
    """
```

**Minimum functions to document (if they exist):**

| Function | Module | Priority |
|----------|--------|----------|
| `compute_match_score()` | matching | MUST |
| `rank_speakers_for_event()` | matching | MUST |
| `generate_match_explanation()` | matching | MUST |
| `scrape_university()` | scraper | MUST |
| `extract_events()` | scraper | MUST |
| `generate_outreach_email()` | email_generator | MUST |
| `generate_ics()` | email_generator | SHOULD |
| `build_pipeline_data()` | pipeline | SHOULD |
| `render_funnel_chart()` | pipeline | SHOULD |
| `validate_weights()` | matching | SHOULD |
| `handle_scrape_failure()` | scraper | SHOULD |

**Import Cleanup Checklist:**

For every `.py` file in `src/` including `src/app.py`:

- [ ] Remove all unused imports (use `pylint` or manual review)
- [ ] Organize imports in this order (separated by blank lines):
  1. Standard library (`os`, `json`, `pathlib`, `pickle`, etc.)
  2. Third-party (`streamlit`, `pandas`, `plotly`, `gemini`, `bs4`, etc.)
  3. Local imports (`from src.matching import ...`, etc.)
- [ ] Remove any `import *` statements
- [ ] Remove any commented-out imports

**Debug Cleanup:**

- [ ] Remove all `print()` debug statements (use `logging` if needed)
- [ ] Remove all `st.write("DEBUG: ...")` statements
- [ ] Remove any `breakpoint()` or `pdb` imports
- [ ] Remove any `TODO` comments that are no longer relevant (keep those that are genuine future work)

**`.gitignore` Verification:**

The `.gitignore` must exclude these patterns:

```gitignore
# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/
dist/
build/

# Cache
cache/
*.pkl
*.npy

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml
```

- [ ] Every pattern above is present in `.gitignore`
- [ ] No `.env` files exist in the repo (check with `git ls-files | grep -i env`)
- [ ] No API keys appear in any committed file

**Final Commit:**

```
chore: final code cleanup — docstrings, imports, debug removal

- Add Google-style docstrings to all key functions (matching, scraping, email)
- Clean up imports across all modules
- Remove debug print/st.write statements
- Verify .gitignore excludes .env, cache, __pycache__
- Ready for submission
```

#### Acceptance Criteria

- [ ] All MUST-priority functions have docstrings
- [ ] All imports organized (stdlib / third-party / local)
- [ ] Zero `print()` debug statements in codebase
- [ ] Zero `st.write("DEBUG")` statements in codebase
- [ ] `.gitignore` verified with all required patterns
- [ ] No API keys or secrets in any committed file
- [ ] Final commit made with descriptive message

#### Harness Guidelines

- Run a final `git diff` review before committing to catch any accidental changes
- Do NOT change any functional code — this is documentation and hygiene only

#### Steer Guidelines

- If cleanup reveals a bug, log it in `bug_log.md` but do NOT fix it here — only fix if it is P0/P1 and there is time
- Do NOT refactor code during cleanup — resist the urge
- Time-box at 2 hours maximum — if not all functions are documented, prioritize the matching engine
- The goal is "professional and reviewable," not "perfect documentation"

---

### A4.9: Day-of Prep — Day 14 (3.0h)

#### Specification

Final preparation for demo day. Every cache must be warm, every backup must be verified, every device must be ready.

**Cache Pre-Warming Checklist:**

Execute each step and verify the output is cached:

- [ ] **University scrapes:** Run scrape for all 5 universities and verify cached results
  ```
  Universities to pre-warm:
  1. UCLA (https://career.ucla.edu/events/) — verify `load_from_cache(url)` returns a record from `cache/scrapes/<sha256(url)>.json`
  2. SDSU (https://www.sdsu.edu/events-calendar) — verify `load_from_cache(url)` returns a record from `cache/scrapes/<sha256(url)>.json`
  3. UC Davis (https://careercenter.ucdavis.edu/career-center-services/career-fairs) — verify `load_from_cache(url)` returns a record from `cache/scrapes/<sha256(url)>.json`
  4. USC (https://careers.usc.edu/events/) — verify `load_from_cache(url)` returns a record from `cache/scrapes/<sha256(url)>.json`
  5. Portland State (URL per scraping notes) — verify `load_from_cache(url)` returns a record from `cache/scrapes/<sha256(url)>.json`
  ```

- [ ] **Explanation cards:** Generate explanation cards for ALL top-3 matches across all events
  ```
  Expected: 15 events x 3 matches = 45 explanation cards cached
  Verify: cache/explanations/ directory has 45+ entries
  ```

- [ ] **Demo match email:** Generate outreach email for Travis Miller matched to the demo event
  ```
  Verify: `cache/emails/` contains the hashed file produced by Sprint 2's email cache helper
  Read the email — does it reference Travis's specific expertise?
  Does it mention the specific event details?
  ```

- [ ] **Demo calendar invite:** Generate .ics file for the demo event
  ```
  Verify: Open the .ics file in a calendar app — correct date, time, location?
  ```

- [ ] **Demo Mode toggle:** Toggle Demo Mode ON, run through full demo flow
  ```
  Every feature must work in Demo Mode:
  - Discovery tab loads cached UCLA results (not live scrape)
  - Matching tab shows cached match cards
  - Email generation shows cached email (with artificial 2s delay)
  - Pipeline funnel renders cached data
  - Expansion map renders (if built)
  - Volunteer dashboard renders (if built)
  ```

**Connectivity Backup Plan:**

| Scenario | Primary | Backup |
|----------|---------|--------|
| WiFi at venue | Venue WiFi | Mobile hotspot (verify phone has data plan) |
| Venue WiFi is slow | Mobile hotspot | Demo Mode (fully offline) |
| No connectivity at all | Demo Mode | Backup video (`docs/demo/backup_demo.mp4`) |

- [ ] Mobile hotspot tested (connect laptop, verify internet access)
- [ ] Demo Mode verified to work with WiFi disabled
- [ ] Backup video accessible without internet (local file, not cloud link)

**Projector / Display Test:**

- [ ] HDMI cable tested (or USB-C adapter if needed)
- [ ] Screen resolution set to 1920x1080 (or 1280x720 if projector is lower res)
- [ ] Streamlit app tested at projected resolution (check no UI elements cut off)
- [ ] Browser zoom level set to 100% (or 110% if text too small for audience)
- [ ] Dark mode vs. light mode decision made (light mode generally projects better)
- [ ] Font size check: can someone 20 feet away read the match scores?

**Laptop Checklist:**

- [ ] Battery fully charged (100%)
- [ ] Charger packed and accessible
- [ ] Sleep mode disabled (set to "Never" for both plugged in and battery)
- [ ] Screen saver disabled
- [ ] Notifications disabled (Do Not Disturb / Focus mode ON)
- [ ] All unnecessary apps closed (especially: Slack, Discord, email clients)
- [ ] Browser bookmarks set: Streamlit Cloud URL, backup Google Drive link
- [ ] Terminal ready: `cd` to project directory, `streamlit run src/app.py` tested
- [ ] Second browser tab with backup demo video loaded (pause at 0:00)

**Pre-demo Verification (run morning of, if possible):**

```bash
# Quick verification script — run 30 minutes before demo
cd "Category 3 - IA West Smart Match CRM"
source .venv/bin/activate  # or however venv is activated

# 1. Verify app starts
streamlit run src/app.py &
sleep 5

# 2. Verify cache files exist
find cache/scrapes -maxdepth 1 -type f | head
ls cache/explanations/
ls cache/emails/

# 3. Verify data files
python -c "import pandas as pd; print(pd.read_csv('data/data_speaker_profiles.csv').shape)"
# Expected: (18, N)

# 4. Verify Gemini key
python -c "import os; print('GEMINI_API_KEY' if os.environ.get('GEMINI_API_KEY') else 'MISSING')"

# 5. Kill test instance
pkill -f streamlit
```

#### Acceptance Criteria

- [ ] All 5 university scrapes cached and verified
- [ ] All 45 explanation cards cached
- [ ] Demo match email cached and content verified
- [ ] Demo .ics file cached and opens correctly
- [ ] Demo Mode tested end-to-end (full flow without internet)
- [ ] Mobile hotspot tested
- [ ] Laptop checklist completed (all items checked)
- [ ] Pre-demo verification script runs clean

#### Harness Guidelines

- Cache verification results logged in `docs/testing/test_log.md` under "Cache Pre-Warming" section
- Any failed cache warming treated as P0 bug

#### Steer Guidelines

- If any cache warming fails, fix it immediately — this is critical path
- Do NOT generate new content here — only verify that previously generated content is cached
- If the pre-demo verification script reveals issues, you have 3 hours of buffer to fix them
- Person B should be available on call the morning of demo day for last-minute issues

---

### A4.10: Buffer for Track B Support (3.0h)

#### Specification

Reserve time for supporting Person C with prototype-related requests for written deliverables and presentation materials.

**Typical Requests and Turnaround:**

| Request Type | Expected Turnaround | Example |
|-------------|---------------------|---------|
| Screenshot of specific app feature | 10 minutes | "Screenshot of Travis Miller's match card with radar chart" |
| Specific match score data | 15 minutes | "What are the top-3 matches for the CPP Data Analytics Hackathon with scores?" |
| Pipeline funnel numbers | 10 minutes | "What are the exact funnel numbers: Discovered → Matched → Contacted → ... → Member Inquiry?" |
| Run a specific scenario | 20 minutes | "Show what happens when we increase geographic weight — what changes in the top match?" |
| Export chart as image | 10 minutes | "Export the expansion map as a PNG for the Growth Strategy" |
| Bias audit data | 30 minutes | "How many times was each speaker matched across all events? Is anyone over/under-represented?" |
| Custom data query | 15 minutes | "How many events are in the LA Metro area? How many speakers are within 50 miles?" |

**Process for Handling Requests:**

1. Person C submits request via agreed channel (Slack, text, in-person)
2. Person B acknowledges within 5 minutes
3. Person B provides deliverable within the turnaround time listed above
4. Person C confirms receipt and adequacy
5. If revisions needed, Person B provides within 10 minutes

**Prototype Queries Person C Might Need:**

```python
# Query 1: Match distribution across speakers
speaker_match_counts = matches_df.groupby('speaker_name').size().sort_values(ascending=False)
# Output: "Travis Miller: 8 matches, Jane Doe: 6 matches, ..."

# Query 2: Geographic coverage
speaker_regions = speakers_df['metro_region'].value_counts()
# Output: "LA West: 5, Ventura: 4, SF: 3, ..."

# Query 3: Average match scores by factor
factor_averages = matches_df[['topic', 'role', 'proximity', 'calendar', 'historical', 'interest']].mean()
# Output: "topic: 0.72, role: 0.65, proximity: 0.58, ..."

# Query 4: High-fit course sections
high_fit = courses_df[courses_df['guest_lecture_fit'] == 'High']
# Output: 10 rows with course details

# Query 5: Pipeline conversion rates
funnel_data = pipeline_df.groupby('stage').size()
# Output: "Discovered: 60, Matched: 45, Contacted: 36, Confirmed: 16, Attended: 12, Member Inquiry: 2"
```

#### Acceptance Criteria

- [ ] All Person C requests fulfilled within specified turnaround times
- [ ] All screenshots saved as high-resolution PNGs
- [ ] All data queries answered with specific numbers (not approximations)
- [ ] No Track B support request took longer than 30 minutes

#### Harness Guidelines

- Screenshots saved to `docs/deliverables/screenshots/` for reuse
- Data query results logged for reference

#### Steer Guidelines

- If Person C requests something that requires code changes, decline and explain the feature freeze
- Prioritize requests that directly feed the Growth Strategy and Measurement Plan (40% of judging)
- If requests pile up, ask Person C to prioritize — handle highest-impact first

---

## Track B Tasks (Person C) — 18-24h

---

### B4.1: Growth Strategy — Final Revision (3.0h)

#### Specification

Final editing pass on the Growth Strategy document. Transform draft language into polished, market-research-professional prose with every claim backed by data.

**Editing Checklist:**

- [ ] **Language tightening — market research terminology:**
  Replace generic terms with industry-specific language throughout:

  | Generic Term | Market Research Term |
  |-------------|---------------------|
  | "matching people to events" | "audience-engagement optimization" |
  | "finding events" | "opportunity discovery pipeline" |
  | "email outreach" | "panel recruitment outreach" |
  | "tracking results" | "conversion funnel analytics" |
  | "getting members" | "membership pipeline conversion" |
  | "sending volunteers" | "deploying engagement assets" |
  | "measuring success" | "response optimization metrics" |
  | "reaching out to universities" | "academic channel activation" |
  | "growing the chapter" | "market penetration strategy" |
  | "volunteer sign-ups" | "engagement pipeline enrollment" |

- [ ] **Data point verification — every claim has evidence:**

  | Claim | Required Data Point | Source |
  |-------|-------------------|--------|
  | "IA West loses engagement opportunities" | "30-40% of potential engagement" | SSIR citation |
  | "Manual matching takes hours" | "4.5h per match cycle (manual) vs. 0.08h (SmartMatch)" | ROI calculation from B2.5 |
  | "SmartMatch saves volunteer hours" | "199 hours/quarter, $9,950 at $50/h opportunity cost" | ROI calculation from B2.5 |
  | "CPP courses are untapped" | "35 course sections, 10 rated High for guest lectures" | data_cpp_course_schedule.csv |
  | "Pipeline tracks conversion" | Actual funnel numbers from prototype | Pipeline data from Person B |
  | "Geographic coverage spans West Coast" | "18 board members across 6 metro regions" | data_speaker_profiles.csv |
  | "Match quality is high" | "Top match average score: X%" | Matching engine output from Person B |
  | "Email response rates expected" | "20-30% for professional associations" | ASAE benchmark |
  | "Phase 1 coverage" | "15 CPP events + 35 course sections" | data_cpp_events_contacts.csv + course_schedule.csv |
  | "Scalability demonstrated" | "5 universities scraped automatically" | Discovery tab output |

- [ ] **Format for submission:**
  - Title page or header: "Growth Strategy: IA SmartMatch — Campus Engagement to Membership Pipeline"
  - Section headers: bold, numbered (1. Executive Summary, 2. Target Segments, etc.)
  - Professional font (Calibri, Helvetica, or similar), 11-12pt
  - 1-inch margins
  - Page numbers (bottom center)
  - Target length: 2.5-3 pages (no less than 2.5, no more than 3.0)
  - Include at least 1 prototype screenshot (match card or pipeline funnel)
  - Include the board-to-campus expansion map if available

- [ ] **Section-by-section review:**

  | Section | Target Length | Key Content to Verify |
  |---------|-------------|----------------------|
  | 1. Executive Summary + Problem | 0.5 page | Pain points quantified, SmartMatch solution stated |
  | 2. Target Audience Segments | 0.5 page | 4 segments defined with real data |
  | 3. Rollout Plan | 0.5 page | 3 phases with specific universities and timelines |
  | 4. Channel Strategy | 0.5 page | 4 channels with expected metrics |
  | 5. Value Proposition + ROI | 0.5 page | Hours saved, dollar value, membership LTV |

#### Acceptance Criteria

- [ ] All 10 generic terms replaced with market research equivalents
- [ ] Every factual claim has a data point with source
- [ ] Document is 2.5-3 pages (measured in final PDF)
- [ ] At least 1 prototype screenshot embedded
- [ ] Professional formatting applied (consistent headers, font, margins)
- [ ] No placeholder text remaining ("{insert number}", "TBD", "TODO")
- [ ] Read aloud for flow — no awkward sentences or transitions

#### Harness Guidelines

- Final document saved to `docs/deliverables/growth_strategy.pdf`
- Source file (Word/Google Docs) also saved for last-minute edits

#### Steer Guidelines

- If missing data points from Person B, submit the request via A4.10 process — do not fabricate numbers
- If document exceeds 3 pages, cut the least impactful paragraph (usually Channel Strategy detail)
- If document is under 2.5 pages, expand ROI section with membership LTV projections
- Read the document from the judge's perspective: "Would a market research professional find this credible?"

---

### B4.2: Measurement Plan — Final Revision (1.5h)

#### Specification

Final editing pass on the Measurement Plan. Ensure KPIs are specific, the A/B test is methodologically sound, and the feedback loop is clearly diagrammed.

**Editing Checklist for KPIs:**

| KPI | Check: Specific? | Check: Measurable? | Check: Realistic? | Check: Data Source Clear? |
|-----|------------------|--------------------|--------------------|--------------------------|
| Match Acceptance Rate (60%+) | Is "acceptance" defined? (top-3 recommendation acted on by chapter leadership) | Can this be measured in the prototype? (yes, via feedback buttons) | 60% — is this achievable? (check against industry benchmarks for recommendation acceptance) | Feedback loop in SmartMatch |
| Email Response Rate (25%+) | Is "response" defined? (reply to outreach email within 7 days) | Can this be measured? (future integration with email tracking) | 25% — realistic for professional association outreach? (ASAE: 20-30%, yes) | Email tracking integration |
| Event Attendance Rate (70%+) | Is "attendance" defined? (confirmed volunteer shows up at event) | Can this be measured? (post-event check-in) | 70% — realistic? (compare to typical event no-show rates: 20-30%, so yes) | Post-event check-in data |
| Membership Conversion (10-15%) | Is "conversion" defined? (engaged student joins IA within 12 months) | Can this be measured? (IA membership database cross-reference) | 10-15% — realistic? (marketing funnel industry average: 2-5% for cold leads, 10-15% for warm leads) | IA membership database |
| Volunteer Utilization (2+/quarter) | Is "utilization" defined? (matches accepted and attended per board member per quarter) | Can this be measured? (SmartMatch pipeline tracker) | 2+/quarter — realistic? (18 speakers, ~45 matches/quarter, average = 2.5) | SmartMatch pipeline |
| Discovery Efficiency (5+/quarter) | Is "efficiency" defined? (new events discovered per university per quarter) | Can this be measured? (Discovery tab logs) | 5+/quarter — realistic? (most university career centers list 10+ events/quarter) | Discovery tab logs |
| Time Savings (4+ hours/match) | Is "savings" defined? (manual process time minus SmartMatch process time) | Can this be measured? (process comparison audit) | 4+ hours — realistic? (manual: 4.5h, SmartMatch: 0.08h = 4.42h savings) | Process audit |

**A/B Test Methodological Soundness Check:**

- [ ] **Hypothesis stated:** "SmartMatch-recommended matching produces higher match acceptance rates than manual chapter leadership matching"
- [ ] **Treatment groups defined:** 3 events use SmartMatch recommendations; 3 events use manual matching
- [ ] **Randomization method:** Events randomly assigned (not cherry-picked)
- [ ] **Sample size justified:** 15 matches per condition (3 events x 5 matches). Note: this is a pilot — sufficient for "directional signal" but not statistical significance. State this explicitly: "This pilot provides directional evidence (n=30 total); a larger-scale study (n=100+) would be needed for statistical significance at p<0.05."
- [ ] **Duration:** 6 months (Q3-Q4 2026) — sufficient for one full event cycle
- [ ] **Success metric:** Primary: match acceptance rate. Secondary: volunteer satisfaction score, event attendance rate
- [ ] **Confounds addressed:** "Event type and size may vary between conditions; we control by matching event categories across groups"
- [ ] **Secondary test described:** Within SmartMatch events, randomize weight configurations to optimize the scoring formula

**Feedback Loop Diagram Finalization:**

```
┌──────────────────┐
│  Match Generated │
│  (SmartMatch)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Chapter Review  │
│  (Leadership)    │
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌────────┐
│ Accept │ │Decline │
└───┬────┘ └───┬────┘
    │          │
    │          ▼
    │    ┌──────────┐
    │    │ Reason   │
    │    │ Captured │
    │    │ (dropdown)│
    │    └────┬─────┘
    │         │
    ▼         ▼
┌──────────────────┐
│ Feedback         │
│ Aggregated       │
│ (quarterly)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Weight Adjustment│
│ Recommendation   │
│ (data-driven)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Improved Matches │
│ (next cycle)     │
└──────────────────┘
```

Verify this diagram (or equivalent) appears in the Measurement Plan document.

#### Acceptance Criteria

- [ ] All 7 KPIs pass the specificity, measurability, realism, and data-source checks
- [ ] A/B test includes: hypothesis, treatment groups, randomization, sample size justification, duration, success metric, confound mitigation
- [ ] Sample size limitation explicitly acknowledged ("directional signal, not statistical significance")
- [ ] Feedback loop diagram included in document (text or image)
- [ ] Document is exactly 1 page (not 0.8, not 1.3)
- [ ] No placeholder text remaining

#### Harness Guidelines

- Final document saved to `docs/deliverables/measurement_plan.pdf`
- Source file also saved for last-minute edits

#### Steer Guidelines

- If the A/B test section feels thin, expand the "secondary test" (weight configuration randomization)
- If the document exceeds 1 page, reduce the KPI table font size or remove the least impactful KPI
- The feedback loop diagram is high-impact for judges — make sure it is clear and readable

---

### B4.3: Responsible AI Note — Final Revision (1.0h)

#### Specification

Final editing pass on the Responsible AI Note. Replace all vague commitments with concrete, auditable mitigations.

**Concreteness Checklist:**

| Topic | Vague (WRONG) | Concrete (RIGHT) |
|-------|--------------|-------------------|
| **Privacy** | "We will address privacy concerns" | "SmartMatch uses only publicly available speaker profile data from the IA West website and publicly listed university event pages. No student PII is collected — pipeline metrics are tracked at the aggregate level only (e.g., '12 students attended' not 'Student Jane Doe attended'). Speaker profiles are updated only with explicit board member consent." |
| **Bias** | "We are aware of potential bias" | "We conducted a bias audit across all 18 speakers: Speaker match frequency ranged from {min} to {max} matches per speaker. Geographic distribution analysis showed {X}% of matches went to LA-metro speakers. To mitigate over-matching, we implemented a diversity-of-speaker rotation flag that penalizes recommending the same speaker more than {N} times per quarter." |
| **Transparency** | "Our algorithm is transparent" | "Every match recommendation displays: (a) a 6-factor score breakdown showing the numeric contribution of topic relevance, role fit, geographic proximity, calendar fit, historical conversion, and student interest; (b) a Gemini generated natural language explanation card; and (c) interactive weight sliders allowing chapter leadership to adjust priorities and see rankings change in real time." |
| **Data Handling** | "We handle data responsibly" | "Scraped university event pages are cached locally with a 24-hour TTL and deleted after processing. No login-gated content is accessed. Scraping respects robots.txt and rate-limits to 1 request per 5 seconds. Speaker profile data is stored as CSV files — no cloud database, no external data sharing." |

**Bias Audit Results to Include:**

Request from Person B (via A4.10 process) if not already provided:

| Audit Metric | Value | Interpretation |
|-------------|-------|----------------|
| Speaker match frequency range | {min}-{max} matches | Is anyone over/under-matched? |
| Geographic distribution of top-3 matches | {% LA, % Ventura, % SF, etc.} | Is LA over-represented? |
| Most-matched speaker | {name}: {N} top-3 appearances | Potential over-reliance |
| Least-matched speaker | {name}: {N} top-3 appearances | Potential under-utilization |
| Expertise tag coverage | {N} unique tags represented in top-3 matches out of {M} total | Is expertise diversity maintained? |

**Target Length:** Half page (250-300 words). Not less than 200 words, not more than 350.

#### Acceptance Criteria

- [ ] All 4 topics (Privacy, Bias, Transparency, Data Handling) have concrete, specific statements
- [ ] Bias audit includes at least 3 specific numbers from the actual prototype
- [ ] No vague phrases ("we will address," "we are aware," "we plan to")
- [ ] Concrete mitigation stated for each concern (what was DONE, not what will be done)
- [ ] Document is approximately half a page (250-300 words)
- [ ] Language is professional and suitable for a judging panel that includes AI ethics evaluators

#### Harness Guidelines

- Final document saved to `docs/deliverables/responsible_ai_note.pdf`
- Source file also saved for last-minute edits

#### Steer Guidelines

- If bias audit data is not yet available from Person B, request it immediately (via A4.10) — this is blocking
- Responsible AI is worth 10 points (20% of judging) — this half page has an outsized impact per word
- Judges will look for SPECIFICITY — "we implemented X and measured Y" beats "we believe in Z" every time

---

### B4.4: Demo Script — Revision + Practice (3.0h)

#### Specification

Revise the demo script based on actual app behavior from Sprint 3 testing, add exact narration quotes, and practice solo.

**Revision Checklist:**

- [ ] Verify every app interaction in the script matches the actual app (button labels, tab names, timing)
- [ ] Update any screenshots or screen references to match final UI
- [ ] Add exact narration quotes for every section (see below)
- [ ] Add pause points for audience engagement (e.g., "Notice how the radar chart shows...")
- [ ] Add backup plan trigger cues (what to say when switching to cached)
- [ ] Time each section narration by reading aloud

**Exact Narration Script:**

```
[0:00] "IA West coordinates 18 board members across 6 metro regions for over
8 events per year. Today, this is managed entirely through email chains and
gut feel. Research shows volunteer-run chapters lose 30 to 40 percent of
engagement opportunities to coordination overhead. And with 35 CPP course
sections going without industry speakers, that's impact left on the table."

[0:30] "SmartMatch changes that. It's an AI-orchestrated CRM that automates
four critical steps: discovering university opportunities, matching them with
the right board member, generating personalized outreach, and tracking the
entire engagement pipeline. Let me show you."

[1:15] "First, discovery. Let's say UCLA just posted new events. I'll click
'Discover Events' — SmartMatch scrapes the UCLA career center page, extracts
structured event data using Gemini, and shows us what it found."
[Wait for results to populate]
"We found {N} events. Let's add this one to our matching pool."

[BACKUP: If scrape fails] "Here's what SmartMatch found when we scanned UCLA
earlier today — we cache results to ensure reliability."

[2:15] "Now, who should attend? SmartMatch evaluates all 18 board members
across six dimensions: topic relevance, role fit, geographic proximity,
calendar fit, historical performance, and student interest signal."
[Point to top match card]
"Travis Miller, SVP of Sales from Ventura, scores {X}% — notice the radar
chart showing why. His MR technology expertise aligns with the event's data
science focus, and Ventura is within commuting distance."
[Adjust weight slider]
"Chapter leadership can adjust priorities. Watch what happens when I increase
geographic proximity — the rankings shift because we're now weighting location
more heavily. Every score is transparent and tunable."

[3:15] "Once we have the right match, outreach is one click away."
[Click Generate Email]
"SmartMatch drafted a personalized email referencing Travis's specific expertise
and the event details. We can also generate a calendar invite for seamless
scheduling."

[BACKUP: If email gen fails] "Here's a pre-generated outreach email — notice
how it references Travis's specific MR technology background."

[3:45] "Every interaction feeds into our engagement pipeline."
[Navigate to Pipeline tab]
"From {N} discovered events across 5 universities, SmartMatch generated 45 top
matches. Using industry conversion benchmarks, that projects to 199 volunteer
hours saved per quarter — nearly $10,000 in opportunity cost."

[4:15] "Our Growth Strategy details a three-phase rollout: starting with CPP's
15 events and 35 courses, expanding to UCLA and USC in the LA Metro, then
covering the full West Coast corridor from Portland to San Diego. Our
Measurement Plan includes specific KPIs and a proposed A/B test to validate
match quality."

[4:45] "Finally, every recommendation is fully explainable. We conducted a bias
audit across all 18 speakers and implemented a diversity rotation flag. There
are no black boxes in SmartMatch."

[5:00] "Thank you."
```

**Solo Practice Protocol:**

| Run | Focus | Target Time | Notes |
|-----|-------|------------|-------|
| Solo Run 1 | Read through with script in hand | No time limit | Focus on pronunciation, emphasis, natural pacing |
| Solo Run 2 | Timed with script visible | 5:00-5:30 | Identify sections that run long |
| Solo Run 3 | Timed WITHOUT script | 4:45-5:15 | Note where memory fails — add memory anchors |

**Memory Anchors (mnemonic for section order):**

```
P-S-D-M-E-P-W-R
Problem → Solution → Discovery → Matching → Email → Pipeline → Written → Responsible

"Please Send Direct Messages Explaining Pipeline Work Results"
```

**Backup Plan Trigger Phrases:**

| Failure | What Person C Says | What Person B Does |
|---------|-------------------|-------------------|
| Scrape fails | "Here's what SmartMatch found when we scanned UCLA earlier today" | Toggle to cached results, continue |
| API timeout for email | "Here's a pre-generated outreach email" | Show cached email in preview panel |
| App crash | "While we restart, let me walk you through what you just saw" | Restart Streamlit (5s), or switch to backup video |
| Total meltdown | "Let me show you a recording of SmartMatch in action" | Play backup video |

#### Acceptance Criteria

- [ ] Narration script updated to match actual app behavior
- [ ] Every section has exact narration quotes (not bullet points)
- [ ] 3 solo practice runs completed
- [ ] Run 3 completes within 4:45-5:15 without reading from script
- [ ] Backup trigger phrases memorized for all 4 failure scenarios
- [ ] Memory anchors created and practiced

#### Harness Guidelines

- Final demo script saved to `docs/demo/demo_script.md`
- Practice run timings logged

#### Steer Guidelines

- If any section consistently runs over time across 3 runs, cut content from that section (do not speed up delivery)
- The discovery demo (1:15-2:15) is the highest-impact section — practice it the most
- If Person C cannot memorize the full script, it is acceptable to have bullet-point notes on a card (but NOT reading from a paper)
- Natural delivery beats word-perfect delivery — practice the gist, not the exact words

---

### B4.5: Demo Rehearsal with Person B — Day 13 (3.0h)

#### Specification

Joint rehearsal with Person B. This is the same activity as A4.6 — the specification is shared.

**Rehearsal Protocol:**

Same as A4.6, with these Person C-specific additions:

- [ ] Person C narrates ALL spoken content — Person B does not speak during demo
- [ ] Person C uses verbal cues to signal Person B (see A4.6 cue table)
- [ ] Person C gestures to screen elements while narrating (practice pointing without blocking view)
- [ ] Person C practices the handoff for written deliverables:
  - Hold up printed Growth Strategy (or reference it clearly)
  - State specific numbers from the document: "Our Growth Strategy projects coverage of 60+ events by Q2 2027"
  - Transition naturally from prototype demo to document references

**Person C Self-Assessment After Each Run:**

| Dimension | Run 1 (1-5) | Run 2 (1-5) | Run 3 (1-5) |
|-----------|-------------|-------------|-------------|
| Narration clarity | | | |
| Pacing (not too fast/slow) | | | |
| Sync with Person B | | | |
| Transition smoothness | | | |
| Backup plan confidence | | | |
| Written deliverables handoff | | | |
| Overall confidence | | | |

Target: All dimensions at 4+ by Run 3.

#### Acceptance Criteria

- [ ] 3 full joint rehearsals completed
- [ ] Self-assessment completed after each run
- [ ] Run 3: all dimensions rated 4+ out of 5
- [ ] Written deliverables handoff practiced in at least 2 runs
- [ ] No verbal cue misfires in Run 3 (Person B executes correct action on each cue)
- [ ] Run 3 completes within 4:45-5:15

#### Harness Guidelines

- Self-assessment results logged in `docs/demo/rehearsal_log.md` alongside Person B's timing log

#### Steer Guidelines

- If sync between Person C and Person B is poor after Run 2, simplify the verbal cues (fewer cues, more obvious)
- If confidence is below 3 on any dimension after Run 3, schedule a 4th rehearsal before backup video recording
- Person C must NOT look at laptop screen while narrating to audience — practice making eye contact with an imaginary audience

---

### B4.6: Presentation Slides (if needed) (2.0h)

#### Specification

Build a slide deck for the hackathon presentation if the format requires slides alongside the live demo.

**Slide Structure (8-10 slides):**

| Slide # | Title | Content | Duration | Visual |
|---------|-------|---------|----------|--------|
| 1 | IA SmartMatch | Subtitle: "AI-Orchestrated Speaker-Event Matching CRM for IA West" + team members | 5s | Clean title slide, IA West logo if available |
| 2 | The Problem | 3 pain points: (1) 18 board members, 6 regions, zero centralized system, (2) 35 CPP course sections untapped, (3) No engagement-to-membership pipeline tracking. Stat: "30-40% of engagement opportunities lost" (SSIR) | 25s | Icons or simple graphics, no walls of text |
| 3 | Meet SmartMatch | 4-module architecture: Discovery, Matching, Outreach, Pipeline. One-sentence value prop: "From campus event to IA membership — automated." | 40s | Architecture diagram from PLAN.md |
| 4 | Architecture | Detailed 4-module diagram: Supply Side (Volunteers), Demand Side (Opportunities), Matching Engine (AI Orchestrator), Member Journey Pipeline | shown during solution overview | Diagram with labeled boxes and arrows |
| 5 | [LIVE DEMO] | Placeholder slide: "Live Demo" with instructions to switch to app | 3 min | Minimal — just a title card |
| 6 | Results | Pipeline funnel screenshot + ROI: "199 volunteer hours saved/quarter ($9,950)" + "5 universities scanned automatically" | 30s | Funnel chart screenshot + bold ROI number |
| 7 | Growth Strategy | Key highlights: 3-phase rollout (CPP → LA Metro → West Coast Corridor), expansion map screenshot, target: 60+ events by Q2 2027 | 15s | Expansion map screenshot or phase diagram |
| 8 | Responsible AI | 4 bullets: (1) Public data only — no student PII, (2) Bias audit conducted — diversity rotation flag, (3) Transparent scores — 6-factor breakdown + explanation cards, (4) Ethical scraping — robots.txt respected, 1 req/5s rate limit | 15s | Checkmark icons |
| 9 | Next Steps | Phase 2 timeline, partnership expansion, weight optimization via A/B testing | 10s | Timeline graphic |
| 10 | Q&A | "Thank you — Questions?" + team contact info + Streamlit Cloud URL | — | Clean slide |

**Design Guidelines:**

- Maximum 6 words per bullet point (slides support narration, they don't replace it)
- One key number or visual per slide (pipeline funnel, ROI figure, expansion map)
- Consistent color scheme (professional blue/gray or IA West brand colors)
- No animations or transitions (waste of time, can break on projector)
- 16:9 aspect ratio
- Font: sans-serif (Calibri, Helvetica, Arial), minimum 24pt for body text
- Include slide numbers (bottom right)

**Tool Options:**
1. Google Slides (easiest to share, collaborative)
2. PowerPoint (best for offline reliability)
3. Canva (best for design quality with templates)

#### Acceptance Criteria

- [ ] 8-10 slides created with content matching the structure above
- [ ] Maximum 6 words per bullet point (no text walls)
- [ ] At least 2 prototype screenshots embedded (funnel chart, match card or expansion map)
- [ ] Architecture diagram included
- [ ] Consistent visual design throughout
- [ ] Slides tested on projector resolution (1920x1080 or 1280x720)
- [ ] File saved to `docs/deliverables/presentation.pptx` (or equivalent)

#### Harness Guidelines

- Slides saved to `docs/deliverables/presentation.pptx`
- Screenshots sourced from Person B (via A4.10 process)

#### Steer Guidelines

- Slides are OPTIONAL — only build if the hackathon format requires them
- If time is tight, cut slides 4 (Architecture detail) and 9 (Next Steps) — focus on Problem, Demo, Results
- Slides should SUPPORT the live demo, not compete with it — keep them minimal
- Person C owns the slide content; if needed, Person B provides screenshots only

---

### B4.7: Q&A Preparation (2.0h)

#### Specification

Prepare data-backed answers for anticipated judge questions. Each answer must be concise (30-60 seconds spoken) and reference specific data.

**Anticipated Questions and Answer Templates:**

---

**Q1: "How does this scale beyond 5 universities?"**

> **Answer:** "SmartMatch is designed for extensibility. Adding a new university takes three steps: enter the events page URL, click 'Discover,' and our Gemini extraction pipeline handles the rest. We tested with 5 universities across the West Coast — UCLA, SDSU, UC Davis, USC, and Portland State — and the extraction pipeline successfully parsed {N}% of event pages. The modular scraping architecture supports both static HTML pages via BeautifulSoup and JavaScript-rendered pages via Playwright. To scale to 20+ universities, we'd add a scheduled scraping job that runs weekly and auto-discovers new events, feeding them directly into the matching pipeline. The matching engine already handles dynamic event sets — no code changes needed per university."

**Key data points to cite:** {N}% extraction success rate, 5 universities tested, 3 steps to add a new one

---

**Q2: "What happens when event pages change their structure?"**

> **Answer:** "Great question — this is a real-world concern. We handle it at two levels. First, our LLM extraction pipeline uses Gemini `gemini-2.5-flash-lite` with few-shot prompting, which is inherently flexible to HTML structure changes — it extracts semantic meaning, not CSS selectors. We tested this by feeding it pages with different structures and achieved {N}% extraction accuracy. Second, we cache every successful scrape with a 24-hour TTL, so even if a live scrape fails, we have recent data to fall back on. In production, we'd add a monitoring layer that alerts chapter leadership when extraction confidence drops below a threshold."

**Key data points to cite:** LLM-based extraction (not CSS-dependent), 24h cache TTL, {N}% accuracy across varied page structures

---

**Q3: "How do you handle speaker fatigue — the same person getting matched repeatedly?"**

> **Answer:** "We identified this in our bias audit. When we ran the matching engine across all 18 speakers and 15 events, we found that {most_matched_speaker} appeared in {N} top-3 rankings while {least_matched_speaker} appeared in only {M}. To address this, we implemented a diversity-of-speaker rotation flag. When enabled, it penalizes recommending any speaker who has already been matched more than twice in the current quarter, redistributing opportunities more evenly. Chapter leadership can also use the volunteer dashboard to see each speaker's utilization rate and manually balance assignments."

**Key data points to cite:** Bias audit results (specific match counts), rotation flag mechanism, volunteer dashboard utilization view

---

**Q4: "What's the actual membership conversion evidence?"**

> **Answer:** "Honest answer: we don't have longitudinal membership conversion data yet — this is a prototype. What we do have is the pipeline infrastructure to measure it. Our funnel tracks from Discovered ({D}) to Matched ({M}) to Contacted ({C}) to Confirmed ({CF}) to Attended ({A}) to Member Inquiry ({MI}). The conversion rates we used — 80% contact rate, 45% confirmation, 75% attendance, 15% membership inquiry — are benchmarked against ASAE data for professional association engagement. Our Measurement Plan proposes an A/B test across 6 IA West events in Q3-Q4 2026 to validate these rates with real data. The key innovation is that SmartMatch provides the tracking infrastructure that doesn't exist today — right now, IA West has zero visibility into this funnel."

**Key data points to cite:** Funnel numbers from prototype, ASAE benchmarks, proposed A/B test (6 events, Q3-Q4 2026), current state = zero tracking

---

**Q5: "How did you validate match quality?"**

> **Answer:** "Three ways. First, we sanity-checked the embedding-based matching by manually reviewing the top-5 and bottom-5 matches from our 270 speaker-event pairs — the top matches had clear topical alignment (e.g., Travis Miller's MR technology expertise matched to data analytics events) while bottom matches were nonsensical (e.g., a qualitative researcher matched to a coding bootcamp). Second, we compared our embedding results against keyword-overlap baseline — embeddings captured semantic relationships that keyword matching missed, like connecting 'survey methodology' expertise to 'data collection workshop' events. Third, we built interactive weight sliders so chapter leadership can tune the scoring formula to match their institutional knowledge — if they know geographic proximity matters more for a specific event, they can increase that weight and immediately see the impact."

**Key data points to cite:** 270 pairs evaluated, top-5/bottom-5 manual review, embedding vs. keyword comparison, interactive weight tuning

---

**Additional Questions to Prepare (brief answers):**

**Q6: "What's the cost to run this?"**
> "Under $0.50 per month for API costs. Gemini `gemini-embedding-001` costs $0.02 per million tokens — our 77 records use about 50,000 tokens total. Gemini `gemini-2.5-flash-lite` for extraction and email generation costs about $0.09 for 100 calls. Streamlit Community Cloud hosting is free."

**Q7: "Why Streamlit instead of a full web app?"**
> "Speed of prototyping. Streamlit gave us an interactive dashboard in days instead of weeks. For production, we'd migrate to a full web framework with a database backend, but for validating the matching algorithm and pipeline concept, Streamlit is the right tool."

**Q8: "How does the matching compare to just asking the board president?"**
> "The board president's mental model covers maybe 5-6 speakers and their top expertise. SmartMatch evaluates all 18 speakers across 6 dimensions simultaneously, finds non-obvious matches like a brand researcher who's also perfect for a product management panel, and does it in seconds instead of a 20-minute email thread."

**Q9: "What about privacy of scraped university data?"**
> "We only scrape publicly available event listings — the same pages any student or visitor can see. No login-gated content, no student data, no PII. We respect robots.txt and rate-limit to 1 request per 5 seconds. Cached data is deleted after 24 hours."

**Q10: "Could this work for other professional associations?"**
> "Absolutely. The architecture is association-agnostic — any organization that matches volunteers to opportunities can use this. The CSVs could be swapped with AMA chapter data, IEEE section data, or any similar structure. The only customization needed is the scoring weights, which are adjustable in the UI."

#### Acceptance Criteria

- [ ] Answers prepared for all 10 anticipated questions
- [ ] Each answer references at least 1 specific data point
- [ ] Q1-Q5 answers are 30-60 seconds when spoken (practice timing)
- [ ] Q6-Q10 answers are 15-30 seconds when spoken
- [ ] No answer says "I don't know" without a follow-up of what IS known
- [ ] Both Person B and Person C know which questions they should answer (Person B = technical, Person C = strategy/business)

#### Harness Guidelines

- Q&A answers saved to `docs/demo/qa_preparation.md`
- Data points placeholders (in braces) filled in with actual numbers from Person B

#### Steer Guidelines

- Person C answers Q1 (scale), Q4 (conversion), Q8 (comparison), Q10 (other associations)
- Person B answers Q2 (page changes), Q5 (validation), Q6 (cost), Q7 (Streamlit)
- Q3 (speaker fatigue) and Q9 (privacy) can be answered by either
- Practice the transition: "Great question — {Person B/C} can speak to that"
- If a question comes up that wasn't anticipated, default to: "That's a great point. In our current prototype, [what we do have], and in production, [what we'd add]."

---

### B4.8: Final Document Compilation (1.5h)

#### Specification

Compile all written deliverables into a polished submission package.

**Submission Package Checklist:**

| Document | Target Length | Format | Filename | Status |
|----------|-------------|--------|----------|--------|
| Growth Strategy | 2.5-3 pages | PDF | `growth_strategy.pdf` | [ ] |
| Measurement Plan | 1 page | PDF | `measurement_plan.pdf` | [ ] |
| Responsible AI Note | 0.5 page | PDF | `responsible_ai_note.pdf` | [ ] |

**Formatting Consistency Check:**

- [ ] All documents use the same font (Calibri 11pt or Helvetica 11pt)
- [ ] All documents use the same header style (Bold, 14pt, numbered sections)
- [ ] All documents use the same margin size (1 inch all sides)
- [ ] All documents include page numbers (bottom center)
- [ ] All documents include the header: "IA SmartMatch — Cal Poly Pomona AI Hackathon 2026"
- [ ] All documents include team name and members on the first page

**Page Count Verification:**

| Document | Min Pages | Max Pages | Actual | Status |
|----------|-----------|-----------|--------|--------|
| Growth Strategy | 2.5 | 3.0 | | [ ] |
| Measurement Plan | 0.8 | 1.0 | | [ ] |
| Responsible AI Note | 0.4 | 0.6 | | [ ] |
| **Total** | **3.7** | **4.6** | | |

**Challenge Rubric Requirements Cross-Check:**

| Rubric Criterion | Requirement | Document | Section | Verified |
|-----------------|-------------|----------|---------|----------|
| Growth Strategy — Target audience | Segments defined | Growth Strategy | Section 2 | [ ] |
| Growth Strategy — Value proposition | For volunteers AND universities | Growth Strategy | Section 5 | [ ] |
| Growth Strategy — Rollout plan | CPP + 3+ universities | Growth Strategy | Section 3 | [ ] |
| Growth Strategy — Channel strategy | Multiple channels identified | Growth Strategy | Section 4 | [ ] |
| Measurement Plan — KPIs | Pipeline conversion, event scoring, volunteer utilization | Measurement Plan | Section 1 | [ ] |
| Measurement Plan — Validation experiment | At least one proposed | Measurement Plan | Section 2 | [ ] |
| Measurement Plan — Feedback loop | For improving match quality | Measurement Plan | Section 3 | [ ] |
| Responsible AI — Privacy | Speaker, faculty, student data handling | Responsible AI Note | Para 1 | [ ] |
| Responsible AI — Bias | Matching algorithm bias addressed | Responsible AI Note | Para 2 | [ ] |
| Responsible AI — Transparency | Score explanation method | Responsible AI Note | Para 3 | [ ] |
| Responsible AI — Data handling | Consent and storage | Responsible AI Note | Para 4 | [ ] |

**Final Quality Gate:**

Before marking compilation complete:
- [ ] Read each document from start to finish one final time
- [ ] Check for typos, grammatical errors, and formatting inconsistencies
- [ ] Verify all data points are accurate (cross-reference with prototype data)
- [ ] Ensure no "TBD", "TODO", "{placeholder}", or "[insert]" text remains
- [ ] Export all documents to PDF and verify formatting is preserved
- [ ] Test PDF files open correctly on a different device

#### Acceptance Criteria

- [ ] All 3 documents compiled and saved as PDFs in `docs/deliverables/`
- [ ] Formatting is consistent across all documents
- [ ] Page counts verified within target ranges
- [ ] All challenge rubric requirements satisfied (checklist complete)
- [ ] No placeholder text in any document
- [ ] PDFs open correctly on at least 2 devices
- [ ] Submission package ready for judges

#### Harness Guidelines

- All final documents saved to `docs/deliverables/`:
  - `docs/deliverables/growth_strategy.pdf`
  - `docs/deliverables/measurement_plan.pdf`
  - `docs/deliverables/responsible_ai_note.pdf`
- Source files (.docx, .gdoc) also saved in same directory for emergency edits

#### Steer Guidelines

- If a document fails the rubric cross-check, fix it immediately — do not submit without all requirements met
- PDF export can introduce formatting bugs (especially tables and diagrams) — always verify the PDF, not just the source
- Print one copy of each document as a backup (for B4.9)

---

### B4.9: Day-of Prep (1.0h)

#### Specification

Final personal preparation for demo day.

**Preparation Checklist:**

- [ ] **Print backup copies:**
  - 2 copies of Growth Strategy (1 for judges, 1 for reference)
  - 2 copies of Measurement Plan
  - 2 copies of Responsible AI Note
  - 1 copy of demo script (for Person C's pocket)
  - Total: 7 printed documents

- [ ] **Prepare USB drive:**
  - Backup demo video (`backup_demo.mp4`)
  - All PDF deliverables
  - Presentation slides (if created)
  - Verify USB drive is readable on at least 1 other computer

- [ ] **Review Q&A answers one final time:**
  - Read through all 10 Q&A answers
  - Practice saying the top-5 answers out loud (30 seconds each)
  - Confirm which questions Person C answers vs. Person B

- [ ] **Personal readiness:**
  - Know the venue location and arrival time
  - Dress code confirmed (business casual typical for hackathons)
  - Water bottle packed
  - Phone on silent (not vibrate)

- [ ] **Communication check with Person B:**
  - Confirm meeting time and location
  - Confirm who brings the laptop, charger, HDMI cable
  - Confirm pre-demo cache verification timing (30 min before slot)
  - Agree on a signal for "switch to backup plan" (e.g., subtle hand gesture)

#### Acceptance Criteria

- [ ] All documents printed (7 total)
- [ ] USB drive prepared and tested
- [ ] Q&A answers reviewed
- [ ] Communication plan confirmed with Person B
- [ ] Personal readiness checklist completed

#### Harness Guidelines

- Printed documents and USB drive are physical deliverables — no digital tracking needed

#### Steer Guidelines

- If printing is not possible, have all PDFs accessible on a phone or tablet as backup
- The USB drive is insurance for the backup video — but also have the video on the laptop
- Arrive 30 minutes before the demo slot to run the pre-demo verification script (A4.9)

---

## Definition of Done

### Track A (Person B):

- [ ] Zero critical (P0) bugs in demo flow
- [ ] Zero incorrect-score (P1) bugs in matching engine
- [ ] App deploys and runs on Streamlit Cloud (or fallback plan documented)
- [ ] Demo Mode works with cached outputs (verified end-to-end)
- [ ] All edge cases handled with graceful error messages (10/10 tested)
- [ ] Performance targets met (initial load <3s, slider <1s, email <2s)
- [ ] Backup demo video recorded and verified (4:45-5:15 duration)
- [ ] 3+ full rehearsals completed with Person C (timing logs saved)
- [ ] All caches pre-warmed for demo day (5 universities, 45 explanations, demo email, demo .ics)
- [ ] Code cleanup complete (docstrings, imports, no debug statements, .gitignore verified)
- [ ] Pre-demo verification script runs clean

### Track B (Person C):

- [ ] Growth Strategy final (2.5-3 pages, real data, market research language, PDF)
- [ ] Measurement Plan final (1 page, specific KPIs, A/B test with sample size justification, feedback loop diagram, PDF)
- [ ] Responsible AI Note final (0.5 page, concrete mitigations with bias audit numbers, PDF)
- [ ] Demo script memorized, 3+ solo rehearsals completed, backup trigger phrases practiced
- [ ] 3+ joint rehearsals completed with Person B (timing within 4:45-5:15)
- [ ] Q&A answers prepared for 10+ anticipated questions with data points
- [ ] Submission package compiled (all 3 documents as PDFs, formatting verified)
- [ ] Presentation slides ready (if required by hackathon format)
- [ ] Printed backup copies and USB drive prepared

## Phase Closeout

- At the end of every phase in this sprint, invoke a dedicated agent in code-review mode against the completed work.
- Do not mark the phase complete until review findings are resolved.
- After the review passes with no open issues, update the affected documentation and commit the changes.

---

## Go/No-Go Gate (End of Day 14 — FINAL)

### PASS Criteria:

| Criterion | Threshold | Verified |
|-----------|-----------|----------|
| Demo runs cleanly in rehearsal | 3/3 runs without app crash | [ ] |
| Demo completes within time limit | Run 3 within 4:45-5:15 | [ ] |
| Written deliverables complete | All 3 documents as PDF, rubric cross-check passed | [ ] |
| Backup plan verified | Demo Mode + backup video both functional | [ ] |
| Team confidence | Both members rate confidence 4+ out of 5 | [ ] |

**Decision: SHIP IT.**

### CONDITIONAL PASS Criteria:

| Criterion | Condition | Mitigation |
|-----------|-----------|------------|
| Minor P2 bugs exist | Demo Mode (cached) works cleanly | Run demo in Demo Mode as primary |
| One edge case unhandled | Specific scenario unlikely in demo | Avoid triggering that scenario; note in backup plan |
| Streamlit Cloud fails | Local demo works perfectly | Demo locally; mention "cloud version available for review" |
| Slides not ready | Demo is strong without slides | Present without slides; use printed deliverables for structure |

**Decision: SHIP IT with noted limitations.**

### FAIL Criteria:

This should NOT happen if feature freeze was respected on Day 9.

| Criterion | Response |
|-----------|----------|
| P0 bugs persist in demo flow | Use backup video for demo portion; present written deliverables; answer Q&A from prepared answers |
| Written deliverables incomplete | EMERGENCY: Person B drops all code work and supports writing. Code is frozen. This is worth 40% of judging. |
| Both demo AND video broken | Present written deliverables + slides only. Reference the deployed Streamlit Cloud URL for judges to try later. |

**Decision: SHIP with degraded presentation. Do NOT skip the hackathon.**

---

## Memory Update Triggers

Update `.memory/context/cat3-sprint4-status.md` when any of the following occur:

| Trigger | What to Record |
|---------|---------------|
| Test run completed | Run number, bug counts by severity, pass rate |
| P0 bug found | Bug ID, description, affected feature, estimated fix time |
| P0 bug fixed | Bug ID, fix description, commit hash, regression status |
| Deployment to Streamlit Cloud | Success/failure, URL, issues encountered |
| Rehearsal completed | Run number, total time, section timings, confidence ratings |
| Written deliverable finalized | Document name, page count, rubric check status |
| Cache pre-warming completed | Universities cached, explanation count, email/ics verified |
| Go/No-Go decision made | PASS/CONDITIONAL/FAIL with justification |

---

## Dependencies

### Internal Dependencies (within Sprint 4):

```
A4.1 (Testing) ──────→ A4.2 (Bug Fixes) ──────→ A4.3 (Edge Cases)
                                                        │
A4.4 (Performance) ←──── can start parallel ────────────┘
                                                        │
A4.5 (Deployment) ←──── can start parallel ─────────────┘
                                                        │
A4.2 (Bug Fixes) ──────→ A4.6 (Rehearsal) ──────→ A4.7 (Backup Video)
                              ↑
B4.4 (Script Practice) ──────┘
                              │
                         A4.6 = B4.5 (same activity, both tracks)
                              │
                              ▼
                         A4.8 (Code Cleanup)
                         A4.9 (Day-of Prep)
                         B4.8 (Document Compilation)
                         B4.9 (Day-of Prep)
```

### External Dependencies (from previous sprints):

| Dependency | Source | Required By | Status |
|-----------|--------|-------------|--------|
| Feature-complete codebase | Sprint 3 (Feature Freeze Day 9) | A4.1 | Must be done |
| Growth Strategy draft (90%+) | Sprint 3 (B3.1-B3.3) | B4.1 | Must be done |
| Measurement Plan draft | Sprint 3 (B3.4) | B4.2 | Must be done |
| Responsible AI Note draft | Sprint 3 (B3.5) | B4.3 | Must be done |
| Demo script first draft | Sprint 3 (B3.6) | B4.4 | Must be done |
| Screenshots from prototype | Sprint 3 (A3.7) | B4.1, B4.6 | Must be done |
| Bias audit results | Sprint 3 (matching engine) | B4.3, B4.7 | Must be done |
| Pipeline funnel real data | Sprint 3 (A3.6) | B4.1, B4.2 | Must be done |
| Demo Mode toggle | Sprint 3 (A3.5) | A4.1, A4.6, A4.9 | Must be done |

### Cross-Track Dependencies (Sprint 4 internal):

| From | To | What | Deadline |
|------|----|------|----------|
| Person B (A4.10) | Person C (B4.1) | Screenshots, data queries for Growth Strategy | Day 11-12 |
| Person B (A4.10) | Person C (B4.3) | Bias audit specific numbers | Day 11-12 |
| Person B (A4.2) | Person B (A4.6) | All P0/P1 bugs fixed before rehearsal | Day 12 EOD |
| Person C (B4.4) | Both (A4.6/B4.5) | Demo script finalized before joint rehearsal | Day 13 morning |
| Both (A4.6/B4.5) | Person B (A4.7) | Rehearsals done before backup video recording | Day 13 |
| Person C (B4.8) | Person C (B4.9) | Documents compiled before printing | Day 14 morning |

---

## Never Cut List (from SPRINT_PLAN.md)

These features and deliverables must be present in the final demo, regardless of any scope pressure:

1. **Matching engine** — MATCH_SCORE computes, top-3 per event displayed
2. **Discovery / scraping** — At least cached results for 1+ university
3. **Email generation** — Personalized outreach email for at least 1 match
4. **Pipeline funnel** — Plotly funnel chart with real data labels
5. **Written deliverables** — All 3 documents (Growth Strategy, Measurement Plan, Responsible AI Note)

If any of these are broken on Day 14, it is a P0 emergency regardless of other priorities.
