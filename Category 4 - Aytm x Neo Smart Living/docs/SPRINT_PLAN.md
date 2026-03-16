# Category 4 Sprint Plan -- Compressed 5-Day Build
## Simulated Market Research (Aytm x Neo Smart Living)

**Owner:** Person C | **Days Available:** 0-5 (~40 productive hours)
**Tier:** 2 (Strong Contender) | **Win Probability:** 25-65%, target 50%+
**Head Start:** 2,500+ lines, ~49.5 hours of pre-built work
**Methodology Name:** **VALIDATE** (Verification and Analysis via LLM-Integrated Dual-Agent Testing & Evaluation)
**After Day 5:** Autopilot mode -- cached data, pre-built features. Polish window Days 12-14 if buffer exists.

---

## 1. Sprint Breakdown (Compressed 5-Day Sprint)

### Day 0: "Before" Baseline Capture (Pre-Sprint, ~2 hours)

**NON-NEGOTIABLE. Do this before touching a single line of code.**

| Time | Task | Output |
|------|------|--------|
| 0:00-0:30 | Set up environment, install deps, run `streamlit run dashboard.py` | Confirm prototype boots |
| 0:30-1:00 | Screenshot every tab of quantitative dashboard (7 tabs) | 7 PNGs in `docs/baseline/quant/` |
| 1:00-1:15 | Screenshot every tab of interview dashboard (6 tabs) | 6 PNGs in `docs/baseline/qual/` |
| 1:15-1:30 | Export all existing CSVs from `output/` | Copy to `docs/baseline/data/` |
| 1:30-1:45 | Run `python report.py`, capture all 5 charts + 4 CSV reports | Copy to `docs/baseline/reports/` |
| 1:45-2:00 | Write `docs/baseline/BASELINE_LOG.md` with prototype state notes (bugs found, tab counts, respondent counts, model names, any errors) | Timestamped log |

**Total Day 0: 2 hours** (does not count against the 40-hour budget)

See Section 4 below for the full capture protocol.

---

### Day 1: Ground Truth Dashboard + Live Cost Ticker (8 hours)

**Theme: The two features that make the demo unforgettable.**

| Block | Hours | Task | Feature | Priority |
|-------|-------|------|---------|----------|
| Morning 1 | 2h | Build Ground Truth Comparison Dashboard -- Side-by-side panels: synthetic output (left) vs. real data images (right) for all 4 ground truth PNGs. Structure: concept test comparison, demographic comparison, interview theme comparison, transcript comparison. | Must-Add #1 | P0 |
| Morning 2 | 2h | Add interpretation annotations to each comparison panel. For each pair: "Agreement" / "Divergence" badge + 2-3 sentence interpretation. Add an overall agreement score (% of findings that directionally match). | Must-Add #1 (cont.) | P0 |
| Afternoon 1 | 2h | Build Live Cost Ticker -- Add `tiktoken` token counting to `synthetic_interviews.py` and `synthetic_respondents.py`. Create a persistent cost accumulator that tracks tokens in/out per API call. Display running total in dashboard sidebar: "This study cost: $X.XX" vs. "$12,000-$24,000 traditional". | Must-Add #2 | P0 |
| Afternoon 2 | 1h | Integrate cost ticker into both dashboards (sidebar widget). Add cost-per-insight metric: total cost / number of statistically significant findings. | Must-Add #2 (cont.) | P0 |
| End of Day | 1h | Run full pipeline with new cost tracking. Capture "after" screenshots of Ground Truth tab and Cost Ticker. Commit working state. | Checkpoint | -- |

**Day 1 Exit Criteria:**
- [ ] Ground Truth Dashboard shows all 4 real data images alongside synthetic equivalents
- [ ] Each comparison has Agreement/Divergence badge + interpretation text
- [ ] Cost Ticker displays in sidebar of both dashboards
- [ ] Cost-per-insight metric visible
- [ ] Day 1 "after" screenshots captured

---

### Day 2: Krippendorff's Alpha Reliability Panel (8 hours)

**Theme: The feature that earns academic credibility with Aytm judges.**

| Block | Hours | Task | Feature | Priority |
|-------|-------|------|---------|----------|
| Morning 1 | 2h | Install `krippendorff` package. Implement intra-persona consistency test: run the same 5 personas through the survey 3x each (15 API calls per model, 30 total). Store results in `output/consistency_runs.csv`. | Must-Add #3 | P0 |
| Morning 2 | 2h | Calculate Krippendorff's alpha per Likert question across the 3 runs. Build a reliability summary table: Question | Alpha | Interpretation (Poor <0.667, Acceptable 0.667-0.8, Good >0.8). Flag any questions where alpha < 0.667 as "low intra-persona consistency -- validate with real respondents." | Must-Add #3 (cont.) | P0 |
| Afternoon 1 | 2h | Build the Reliability Panel as a new Streamlit tab in `dashboard.py`. Include: (a) alpha heatmap by question x segment, (b) overall pipeline reliability score, (c) comparison to published benchmarks from STAMP paper, (d) "what this means for decision-making" interpretation box. | Must-Add #3 (cont.) | P0 |
| Afternoon 2 | 1h | Add cross-model reliability: compute alpha between GPT-4.1-mini and Gemini 2.5 Flash responses for the same persona. This extends the existing Mann-Whitney U with a complementary metric. | Must-Add #3 (cont.) | P0 |
| End of Day | 1h | Integration test: verify alpha calculations match expected ranges. Capture screenshots of Reliability tab. Commit. | Checkpoint | -- |

**Day 2 Exit Criteria:**
- [ ] `krippendorff` package integrated
- [ ] 3x repeat runs for 5 personas stored in CSV
- [ ] Alpha computed per question, visualized as heatmap
- [ ] Reliability tab functional in quantitative dashboard
- [ ] Cross-model alpha calculated alongside Mann-Whitney U
- [ ] Day 2 "after" screenshots captured

---

### Day 3: Tony Koo Business Recommendation Generator (8 hours)

**Theme: The feature that proves business relevance to judges.**

| Block | Hours | Task | Feature | Priority |
|-------|-------|------|---------|----------|
| Morning 1 | 2h | Build recommendation engine logic. Inputs: (a) winning positioning concept from Stage 5 concept test, (b) top 2 segments by purchase interest, (c) key barriers from barrier heatmap, (d) agreement score from ground truth comparison. Output: structured JSON with recommendation, confidence level, and supporting evidence. | Must-Add #4 | P0 |
| Morning 2 | 2h | Build Tony Koo Recommendation tab in `dashboard.py`. Structure: (1) Executive Summary box -- "Neo Smart Living should..." one sentence, (2) Evidence panel -- 3-4 supporting data points with chart references, (3) Confidence Assessment -- which findings are dual-LLM validated vs. single-model, (4) Next Steps -- "Validate these 2 findings with real research before launch." | Must-Add #4 (cont.) | P0 |
| Afternoon 1 | 2h | Add the "VALIDATE Methodology" overview page to the dashboard. Single tab that explains: (a) What VALIDATE stands for, (b) 6-stage pipeline diagram, (c) How dual-LLM reliability works, (d) Known limitations (5 funhouse mirror distortions), (e) When to use synthetic vs. real research. This is both a feature AND the Responsible AI note in one. | Methodology + Responsible AI | P0 |
| Afternoon 2 | 1h | Write `docs/RESPONSIBLE_AI.md` (half page) pulling from the VALIDATE methodology tab content. Cover: synthetic data transparency, known distortions, when real research is required, no PII risk. | Deliverable | P0 |
| End of Day | 1h | End-to-end run: generate data, view Ground Truth, Cost Ticker, Reliability, and Tony Koo tabs in sequence. Verify the demo narrative flows. Commit. | Checkpoint | -- |

**Day 3 Exit Criteria:**
- [ ] Tony Koo recommendation generates from pipeline data (no hardcoding)
- [ ] Recommendation tab shows executive summary, evidence, confidence, next steps
- [ ] VALIDATE methodology tab explains the full approach
- [ ] Responsible AI note drafted (half page)
- [ ] All 4 must-add features are functional (Ground Truth, Cost Ticker, Krippendorff's, Tony Koo)

---

### Day 4: Before/After Panels + Integration Polish (8 hours)

**Theme: Build the narrative evidence for the demo.**

| Block | Hours | Task | Feature | Priority |
|-------|-------|------|---------|----------|
| Morning 1 | 2h | Build "Before vs. After" comparison page in the dashboard. For each improvement: (a) "Before" screenshot from Day 0 baseline, (b) "After" current state, (c) What changed and why it matters. Cover: Ground Truth (before: no validation vs. after: 4-image comparison), Cost Ticker (before: no tracking vs. after: real-time cost), Reliability (before: Mann-Whitney only vs. after: Krippendorff's alpha), Recommendation (before: no business output vs. after: structured recommendation). | Before/After Panels | P0 |
| Morning 2 | 2h | Product-agnostic config layer (should-add if time). Extract all Neo Smart Living-specific content (product name, price, segments, survey questions) into a `config.yaml` or `config.py`. Make the pipeline runnable for any product by changing one config file. Even partial progress here strengthens the "open-source reusable tool" judging criterion. | Should-Add | P1 |
| Afternoon 1 | 2h | GenAI documentation. Create `docs/GENAI_USAGE.md`: (a) Every prompt template used in the pipeline (interview system prompt, survey system prompt, emotion classification prompt), (b) Which code was AI-generated vs. human-written, (c) Tools used (GPT-4.1-mini, Gemini 2.5 Flash, Claude for development), (d) Human modifications to AI-generated code. | Deliverable | P0 |
| Afternoon 2 | 2h | Dashboard tab cleanup and navigation. Ensure all tabs have consistent headers, "(Synthetic)" labels on every chart title, proper loading states, and no crashes on missing data. Test both dashboards end-to-end with fresh data AND cached data. | Integration | P0 |

**Day 4 Exit Criteria:**
- [ ] Before/After comparison page functional with real baseline screenshots
- [ ] Config layer at least partially extracted (product name, price at minimum)
- [ ] GenAI documentation complete
- [ ] All tabs labeled "(Synthetic)" consistently
- [ ] Both dashboards run cleanly on cached data (zero API calls)

---

### Day 5: Demo Hardening + Handoff Preparation (8 hours)

**Theme: Make it bulletproof for demo day and lock it down for autopilot.**

| Block | Hours | Task | Feature | Priority |
|-------|-------|------|---------|----------|
| Morning 1 | 2h | Cache all demo data. Run the full pipeline one final time with API calls. Save all outputs to `output/` (interviews, analysis, survey responses, consistency runs). Verify every dashboard tab renders correctly from cached data. This is the dataset that will be used on demo day. | Demo Prep | P0 |
| Morning 2 | 2h | Write the 5-minute demo script. Structure: (0:00-0:30) Cost hook -- "$0.08 vs. $24,000", (0:30-1:30) VALIDATE methodology overview, (1:30-3:00) Live dashboard walkthrough -- Ground Truth tab, Reliability tab, Concept Test tab, (3:00-4:00) Tony Koo recommendation reveal, (4:00-4:30) Before/After improvement story, (4:30-5:00) Responsible AI + open-source vision. Save to `docs/DEMO_SCRIPT.md`. | Demo Prep | P0 |
| Afternoon 1 | 2h | Deployment test. Push to Streamlit Community Cloud or verify local deployment works. Test on a second machine if possible. Ensure `requirements.txt` is complete (add `krippendorff`, `tiktoken`, `pyyaml` if config layer was built). Create `docs/DEPLOYMENT.md` with setup instructions. | Deployment | P0 |
| Afternoon 2 | 1h | Final "after" screenshots of every tab. Update `docs/baseline/` with the complete before/after image set. Update `.status.md` for Category 4. | Documentation | P0 |
| Final Hour | 1h | Write handoff notes in `docs/HANDOFF.md`: what is done, what is not done, what polish could happen on Days 12-14, known bugs, how to run the demo. This is for the team member who presents on demo day. | Handoff | P0 |

**Day 5 Exit Criteria:**
- [ ] All demo data cached and verified
- [ ] Demo script written with time-stamped sections
- [ ] Deployment tested (Streamlit Cloud or local fallback documented)
- [ ] Complete before/after screenshot set
- [ ] Handoff document for demo day presenter
- [ ] All code committed to repo

---

## 2. Milestone Checkpoints

| Milestone | Day | Deliverable | Verification |
|-----------|-----|-------------|-------------|
| M0: Baseline Captured | Day 0 | 13 screenshots, 8 CSVs, baseline log | Files exist in `docs/baseline/` |
| M1: Ground Truth + Cost Ticker | Day 1 EOD | Ground Truth comparison tab, cost ticker in sidebar | Run dashboard, verify both features render |
| M2: Reliability Panel | Day 2 EOD | Krippendorff's alpha tab with heatmap | Alpha values computed, tab renders, heatmap shows per-question breakdown |
| M3: Tony Koo + VALIDATE | Day 3 EOD | Recommendation tab, methodology tab, Responsible AI draft | Recommendation generates from data (not hardcoded), methodology tab explains pipeline |
| M4: Narrative Complete | Day 4 EOD | Before/After page, GenAI docs, config layer (partial) | Before/After shows real Day 0 screenshots vs. current state |
| M5: Demo-Ready | Day 5 EOD | Demo script, cached data, deployment, handoff | Full demo runs in <5 minutes on cached data with zero API calls |

**Daily Standup Check (5 min, start of each day):**
1. Did yesterday's exit criteria all pass?
2. Any blockers for today?
3. Are we on budget? (Track hours spent vs. planned)

---

## 3. Risk Gates

### Risk Gate Framework: "What Gets Cut?"

The 4 must-add features are priority-ordered. If any feature takes longer than estimated, cut from the bottom.

**Priority Stack (highest to lowest):**

| Rank | Feature | Estimated Hours | Cut Threshold | What Happens If Cut |
|------|---------|----------------|---------------|---------------------|
| 1 | Ground Truth Dashboard | 4-6h | If exceeds 7h, simplify to static image comparison (no annotations) | Lose the interpretation layer, but the visual comparison still works |
| 2 | Live Cost Ticker | 2-3h | If exceeds 4h, hardcode a pre-calculated cost instead of real-time tracking | Lose the "live" element but the $0.08 vs. $24K story still lands |
| 3 | Tony Koo Recommendation | 3-4h | If exceeds 5h, write a static recommendation slide instead of a dynamic generator | Lose the "generates from data" angle but the business relevance is preserved |
| 4 | Krippendorff's Alpha | 4-5h | If exceeds 6h, fall back to Fleiss' kappa or simple % agreement (1h to implement) | Lose the academic prestige of alpha but still have a consistency metric |

### Escalation Rules

| Scenario | Action |
|----------|--------|
| Day 1 feature bleeds into Day 2 | Steal 2h from Day 4 "config layer" (should-add, not must-add) |
| Day 2 feature bleeds into Day 3 | Drop config layer entirely. Reduce GenAI docs to a single-page bullet list |
| Day 3 feature bleeds into Day 4 | Drop Before/After as a dashboard tab; do it as 4 static slides instead |
| Any feature takes 2x its estimate | STOP. Implement the 1-hour fallback version. Move on. |
| API errors or rate limiting | Switch to cached/test data immediately. All features must work on cached data |
| Krippendorff package issues | Fall back to `scipy` percent agreement + Fleiss' kappa. Do NOT spend >1h debugging package issues |

### Buffer Budget
- Days 1-3: Zero buffer. Every hour is allocated.
- Day 4: 2h buffer (config layer is expendable).
- Day 5: 1h buffer (deployment can be local-only if Streamlit Cloud has issues).
- **Total buffer: 3 hours.**

---

## 4. "Before" Baseline Capture Protocol

### What to Capture

**A. Dashboard Screenshots (13 total)**

Quantitative Dashboard (`streamlit run dashboard.py`) -- 7 tabs:
1. `quant_01_overview.png` -- Overview tab (respondent counts, model split, segment split)
2. `quant_02_purchase_interest.png` -- Purchase Interest tab (boxplots, segment bars)
3. `quant_03_use_case_barriers.png` -- Use Case & Barriers tab (barrier heatmap)
4. `quant_04_concept_test.png` -- Concept Test tab (5 positioning concepts)
5. `quant_05_value_drivers.png` -- Value Drivers & Sponsorship tab
6. `quant_06_model_comparison.png` -- Model Comparison tab (Mann-Whitney U results)
7. `quant_07_demographics.png` -- Demographics tab (if present)

Qualitative Dashboard (`streamlit run interview_dashboard.py`) -- 6 tabs:
8. `qual_01_overview.png` -- Overview tab (interview counts, model split, demographics)
9. `qual_02_sentiment.png` -- Sentiment tab (VADER scores)
10. `qual_03_emotional_tone.png` -- Emotional Tone tab
11. `qual_04_thematic.png` -- Thematic Analysis tab (LDA topics)
12. `qual_05_segment_discovery.png` -- Segment Discovery tab
13. `qual_06_transcripts.png` -- Full Transcripts tab (sample view)

**B. Data Files (8 total)**

Copy these from `prototype/output/` to `docs/baseline/data/`:
1. `interview_transcripts.csv` (135 KB, 30 rows)
2. `interview_analysis.csv` (141 KB, 30 rows)
3. `interview_themes.json` (7.7 KB)
4. `synthetic_responses.csv` (78 KB, 60 rows)
5. `report/descriptive_likert.csv`
6. `report/descriptive_categorical.csv`
7. `report/model_comparison.csv`
8. `report/segment_profiles.csv`

**C. Report Charts (5 total)**

Copy from `prototype/output/report/charts/`:
1. `concept_appeal.png`
2. `purchase_interest_by_segment.png`
3. `barrier_heatmap.png`
4. `radar_by_segment.png`
5. `model_comparison_bars.png`

**D. Baseline Log**

Create `docs/baseline/BASELINE_LOG.md`:
```markdown
# Baseline Log -- Category 4 Prototype
**Captured:** [DATE] [TIME]
**Captured by:** Person C
**Prototype commit:** [git hash if applicable]

## Environment
- Python version: [X.X.X]
- Streamlit version: [X.X.X]
- OS: [Windows/Mac/Linux]

## Prototype State
- Quant dashboard tabs: [count]
- Qual dashboard tabs: [count]
- Total respondents (quant): [N]
- Total interviews (qual): [N]
- Models used: [list]
- Known errors on load: [none / describe]

## Key Metrics (Before)
- Respondent count: 60 (5 segments x 2 models x 6 each)
- Interview count: 30
- Statistical tests: Mann-Whitney U only
- Reliability metric: None
- Ground truth comparison: None
- Cost tracking: None
- Business recommendation: None
- Responsible AI note: None

## Missing Features (To Be Added)
1. Ground Truth Comparison Dashboard
2. Live Cost Ticker
3. Krippendorff's Alpha Reliability Panel
4. Tony Koo Business Recommendation
5. Before/After Comparison Panels
6. VALIDATE Methodology Page
7. Product-Agnostic Config Layer
```

### Capture Procedure (Step by Step)

```bash
# 1. Create baseline directory structure
mkdir -p "Category 4 - Aytm x Neo Smart Living/docs/baseline/quant"
mkdir -p "Category 4 - Aytm x Neo Smart Living/docs/baseline/qual"
mkdir -p "Category 4 - Aytm x Neo Smart Living/docs/baseline/data"
mkdir -p "Category 4 - Aytm x Neo Smart Living/docs/baseline/reports"

# 2. Copy data files
cp prototype/output/*.csv docs/baseline/data/
cp prototype/output/*.json docs/baseline/data/
cp prototype/output/report/*.csv docs/baseline/data/

# 3. Copy report charts
cp prototype/output/report/charts/*.png docs/baseline/reports/

# 4. Launch dashboards and take screenshots manually
# (Use browser screenshot or Snipping Tool)
# Save to docs/baseline/quant/ and docs/baseline/qual/

# 5. Write BASELINE_LOG.md
```

**CRITICAL:** These files are the "before" in every "before vs. after" comparison. If they are not captured before Day 1 begins, the entire narrative falls apart. There is no recovering this later.

---

## 5. Demo Readiness Checklist

### Must Work (Non-Negotiable for a Compelling Demo)

| # | Element | Verification | Fallback |
|---|---------|-------------|----------|
| 1 | Both dashboards boot on cached data (zero API calls) | `streamlit run dashboard.py` loads all tabs in <10 seconds | Pre-record a video of the dashboard |
| 2 | Ground Truth tab shows real vs. synthetic side-by-side | All 4 ground truth images visible with synthetic counterparts | Show images as static slides |
| 3 | Cost ticker shows "$0.XX" total cost | Sidebar displays running cost | Show hardcoded "$0.08" with calculation breakdown |
| 4 | Krippendorff's alpha heatmap renders | Tab loads, heatmap shows green/yellow/red per question | Show alpha table as static image |
| 5 | Tony Koo recommendation generates | "Neo Smart Living should..." sentence appears with evidence | Show pre-written recommendation slide |
| 6 | Before/After panels show visible improvement | At least 3 before/after pairs visible | Show as presentation slides outside the dashboard |
| 7 | "(Synthetic)" label on every chart | Visual scan confirms no chart lacks the label | Add in final polish |
| 8 | VALIDATE methodology explanation accessible | Tab or page explains the approach | Include in presentation slides |
| 9 | Responsible AI note exists | `docs/RESPONSIBLE_AI.md` is written | Verbal explanation during demo |
| 10 | GenAI documentation exists | `docs/GENAI_USAGE.md` is written | Verbal explanation during demo |

### Demo Narrative Arc (5 Minutes)

```
0:00-0:30  THE HOOK
           "We ran a complete market research study for Neo Smart Living.
            Traditional cost: $24,000 and 6 weeks.
            Our cost: 8 cents and 3 minutes."
           [Show cost ticker in sidebar]

0:30-1:30  THE METHOD (VALIDATE)
           "We built VALIDATE -- an open-source methodology for simulated
            market research using dual-LLM cross-validation."
           [Show VALIDATE methodology tab]
           "Two LLMs independently generate responses. Where they agree,
            we have high confidence. Where they diverge, we flag it for
            real-world validation."

1:30-3:00  THE EVIDENCE
           [Show Ground Truth tab]
           "Here is what real research found. Here is what our simulation
            predicted. Agreement rate: X%."
           [Show Reliability tab]
           "Krippendorff's alpha shows which questions produce consistent
            responses across repeated runs."
           [Show Concept Test tab]
           "The Adventure positioning wins for Active Adventurers.
            The Home Office positioning wins for Remote Professionals.
            Both LLMs agree."

3:00-4:00  THE RECOMMENDATION
           [Show Tony Koo tab]
           "Based on dual-LLM consensus validated against real research:
            Neo Smart Living should lead with the [X] positioning for [Y]
            segment. Here's the supporting evidence."

4:00-4:30  THE IMPROVEMENT STORY
           [Show Before/After tab]
           "The prototype we started with had no reliability metrics,
            no ground truth comparison, no cost tracking, and no
            business recommendation. Here is what we added."

4:30-5:00  THE VISION
           "This is open-source. Change the config file and run it for
            any product. Responsible AI is built in -- every chart says
            'Synthetic', every limitation is disclosed. This is not a
            replacement for real research. It's a $0.08 first draft that
            tells you what to validate next."
```

### Pre-Demo Checklist (Day of Event)

- [ ] Laptop charged, charger accessible
- [ ] Dashboard tested on the actual presentation display/projector
- [ ] WiFi tested (or confirm zero API calls needed)
- [ ] Both dashboards pre-loaded in browser tabs
- [ ] Demo script printed or on second screen
- [ ] Backup: presentation slides exported as PDF
- [ ] Backup: 2-minute video recording of dashboard walkthrough
- [ ] `docs/RESPONSIBLE_AI.md` printed for judge Q&A
- [ ] `docs/GENAI_USAGE.md` printed for judge Q&A
- [ ] Timer set for 5-minute practice run

---

## 6. Critical Path Analysis

### If Time Runs Short: Priority Order

```
HIGHEST PRIORITY
|
|  1. Ground Truth Comparison Dashboard (4-6h)
|     WHY FIRST: This is the single most memorable demo moment. The
|     "$0.08 vs. $24K" hook only works if you PROVE the synthetic data
|     is directionally valid. No other hackathon team will have real
|     data to validate against. This is your unfair advantage.
|     MINIMUM VIABLE: Show 4 real images + 4 synthetic equivalents
|     side by side with Agreement/Divergence labels. No interpretation
|     text needed -- the visual comparison speaks for itself.
|
|  2. Tony Koo Business Recommendation (3-4h)
|     WHY SECOND: Judges score "Business Relevance" explicitly. Without
|     a concrete "Neo Smart Living should do X" output, you have a
|     methodology demo but not a business tool. Tony Koo is a CPP alumnus
|     and the live client -- judges will ask "what would Tony do with this?"
|     MINIMUM VIABLE: A single tab with one executive summary sentence,
|     the winning concept, and the top segment. No evidence breakdown needed.
|
|  3. Live Cost Ticker (2-3h)
|     WHY THIRD: The cost story is the emotional hook of the entire demo.
|     "$0.08 vs. $24,000" is the number judges will remember. Making it
|     live (not just a claim) adds credibility.
|     MINIMUM VIABLE: Sidebar text showing total token count and dollar
|     cost from the last pipeline run. Even a static display works.
|
|  4. Krippendorff's Alpha Reliability Panel (4-5h)
|     WHY LAST: This is the most academically impressive feature but
|     also the most complex and the least visible in a 5-minute demo.
|     Aytm judges will appreciate it, but the demo can survive without it.
|     The existing Mann-Whitney U test provides basic cross-model
|     reliability. Alpha adds depth but is not essential for the narrative.
|     MINIMUM VIABLE: If alpha is cut, add a text box to the existing
|     Model Comparison tab saying "Intra-persona consistency: X% agreement
|     across 3 repeated runs" using simple percent agreement (1h to build).
|
LOWEST PRIORITY
```

### Time Budget Summary

| Feature | Planned Hours | Buffer Hours | Hard Deadline |
|---------|--------------|-------------|---------------|
| Ground Truth Dashboard | 4h (Day 1 AM) | +2h from Day 1 PM | End of Day 1 |
| Cost Ticker | 3h (Day 1 PM) | +1h from Day 4 config layer | End of Day 1 |
| Krippendorff's Alpha | 5h (Day 2 AM-PM) | +1h from Day 4 config layer | End of Day 2 |
| Tony Koo Recommendation | 4h (Day 3 AM) | +1h from Day 5 deployment | End of Day 3 |
| VALIDATE + Responsible AI | 3h (Day 3 PM) | None | End of Day 3 |
| Before/After Panels | 2h (Day 4 AM) | None | End of Day 4 |
| Config Layer (should-add) | 2h (Day 4 AM) | EXPENDABLE -- first thing cut | End of Day 4 |
| GenAI Docs | 2h (Day 4 PM) | Can reduce to 1h bullet list | End of Day 4 |
| Demo Script + Cache | 4h (Day 5 AM) | None | End of Day 5 |
| Deployment + Handoff | 4h (Day 5 PM) | Can skip Cloud, do local only | End of Day 5 |
| **Total** | **33h planned + 4h buffer + 3h expendable = 40h** | | |

### Dependency Chain

```
Day 0 (Baseline)
  |
  v
Day 1 (Ground Truth + Cost Ticker)
  |   \
  |    These two are independent of each other.
  |    Ground Truth needs the 4 real PNG images.
  |    Cost Ticker needs tiktoken integration.
  |   /
  v
Day 2 (Krippendorff's Alpha)
  |
  |   Depends on: working pipeline from Day 1 (needs to run
  |   repeat persona surveys, which uses the cost ticker).
  |
  v
Day 3 (Tony Koo + VALIDATE Methodology)
  |
  |   Depends on: Ground Truth agreement scores (Day 1),
  |   reliability metrics (Day 2), concept test results (existing).
  |   Tony Koo recommendation pulls from all prior features.
  |
  v
Day 4 (Before/After + Docs)
  |
  |   Depends on: Day 0 baseline screenshots + Days 1-3 features.
  |   Cannot build Before/After without having both states.
  |
  v
Day 5 (Demo Hardening + Handoff)
  |
  |   Depends on: everything above being functional.
  |   This day is about caching, scripting, and bulletproofing.
```

---

## Appendix A: Files to Create / Modify

### New Files

| File | Day Created | Purpose |
|------|------------|---------|
| `docs/baseline/BASELINE_LOG.md` | Day 0 | Prototype state before changes |
| `docs/baseline/quant/*.png` | Day 0 | 7 quantitative dashboard screenshots |
| `docs/baseline/qual/*.png` | Day 0 | 6 qualitative dashboard screenshots |
| `docs/baseline/data/*.csv` | Day 0 | Copies of all baseline CSVs |
| `docs/baseline/reports/*.png` | Day 0 | Copies of all baseline report charts |
| `docs/RESPONSIBLE_AI.md` | Day 3 | Half-page Responsible AI note |
| `docs/GENAI_USAGE.md` | Day 4 | GenAI documentation |
| `docs/DEMO_SCRIPT.md` | Day 5 | 5-minute demo script |
| `docs/DEPLOYMENT.md` | Day 5 | Setup and deployment instructions |
| `docs/HANDOFF.md` | Day 5 | Handoff notes for demo day presenter |
| `output/consistency_runs.csv` | Day 2 | Krippendorff's alpha raw data |

### Modified Files

| File | Day Modified | Change |
|------|-------------|--------|
| `dashboard.py` | Days 1-4 | Add tabs: Ground Truth, Reliability, Tony Koo, VALIDATE, Before/After. Add cost ticker sidebar. |
| `interview_dashboard.py` | Day 1 | Add cost ticker sidebar |
| `synthetic_interviews.py` | Day 1 | Add tiktoken token counting |
| `synthetic_respondents.py` | Days 1-2 | Add tiktoken token counting, add repeat-run mode for alpha |
| `analytics.py` | Day 2 | Add Krippendorff's alpha calculation functions |
| `requirements.txt` | Day 2 | Add: `krippendorff`, `tiktoken`, `pyyaml` (if config layer built) |
| `segments.py` or new `config.py` | Day 4 | Extract product-specific content (if config layer built) |

---

## Appendix B: Commit Convention

All commits for Category 4 follow the project convention:

```
<type>(cat4): <description>
```

Suggested commit sequence:

| Day | Commit Message |
|-----|---------------|
| 0 | `docs(cat4): capture baseline screenshots and data before modifications` |
| 1 | `feat(cat4): add ground truth comparison dashboard with 4-image validation` |
| 1 | `feat(cat4): add live cost ticker with tiktoken token tracking` |
| 2 | `feat(cat4): add Krippendorff's alpha reliability panel with heatmap` |
| 3 | `feat(cat4): add Tony Koo business recommendation generator` |
| 3 | `feat(cat4): add VALIDATE methodology tab and responsible AI note` |
| 4 | `feat(cat4): add before/after comparison panels with baseline images` |
| 4 | `docs(cat4): add GenAI usage documentation` |
| 5 | `chore(cat4): cache demo data and finalize deployment config` |
| 5 | `docs(cat4): add demo script, deployment guide, and handoff notes` |

---

## Appendix C: Days 12-14 Polish Window (If Buffer Exists)

If the team has capacity in the final 48 hours before demo day, these are the highest-value polish tasks for someone other than Person C:

| Priority | Task | Hours | Impact |
|----------|------|-------|--------|
| 1 | Run the demo script 3x with timer | 1.5h | Catches pacing issues, identifies weak transitions |
| 2 | Improve chart aesthetics (consistent color palette, larger fonts, branded header) | 2h | "Looks professional" scores points |
| 3 | Complete the product-agnostic config layer if not finished on Day 4 | 2h | Strengthens "open-source reusable tool" criterion |
| 4 | Add multi-turn interview probing (should-add, 5-7h) | SKIP | Not enough time; save for post-hackathon |
| 5 | Record a 2-minute backup video of the dashboard walkthrough | 1h | Insurance against demo-day technical failure |
