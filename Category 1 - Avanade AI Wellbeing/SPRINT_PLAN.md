# Category 1 — BalanceIQ Sprint Plan

**Category:** Avanade AI Wellbeing | **Tier:** 3/Optional | **Win Probability:** 25-35% ceiling
**Prep Window:** 14 days (April 2-15, 2026) | **Hackathon Demo:** April 16, 2026
**Staffing:** 1 developer (6-8 productive hrs/day) + possible part-time support
**Total Budget:** 84-112 person-hours

**Scheduling Note:** Day numbers in `MASTER_SPRINT_PLAN.md` are the canonical portfolio schedule. The exact dates below assume a kickoff on April 2, 2026.

---

## Strategic Review Corrections (Applied Throughout)

These mandates from the strategic review are woven into the sprint tasks below:

1. **Viva Insights pricing correction:** Was "$57 E5 license" — actually $6/user/month add-on. All copy, pitch deck, and UI text must use the corrected figure.
2. **Repositioning:** From "Viva for non-E5" to "teams outside the Microsoft ecosystem." The value prop targets orgs that do NOT use M365 at all, not those that want cheaper M365.
3. **Must-add features:** What-If Schedule Simulator (6-8h), Week-over-Week Trend Detection (4-6h), Nudge A/B Comparison (1-2h).
4. **Heatmap polish:** 40% of total polish time (estimated 4-5h of the ~12h polish budget).
5. **Shared Streamlit theme:** Use the cross-category Streamlit theme template for consistent branding.

---

## 1. Sprint Breakdown

### Sprint 0 — Foundation & Research (April 2-3 | 2 days | 12-16h)

**Sprint Goal:** Establish the project skeleton, validate the scoring formula, and generate synthetic data so all subsequent sprints build on a working data layer.

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 0.1 | Set up project structure: Streamlit app scaffold using shared theme template, directory layout, `.env` config, dependency install | 1.5 |  |
| 0.2 | Research evidence-based thresholds for 4 wellbeing dimensions (meetings/day, focus hours, after-hours activity, social connection). Cite sources (SO Developer Survey, Viva Insights docs, WHO-5). Document in `docs/scoring-thresholds.md` | 2.0 |  |
| 0.3 | Define the wellbeing score formula: 4 dimensions x 0-100 scale, configurable thresholds, weighting scheme. Write as a design doc in `docs/score-engine-spec.md` | 1.5 |  |
| 0.4 | Build synthetic data generator: 20 employees, 14 days, realistic variance (crunch weeks, healthy weeks, mixed). Output as JSON matching Viva Insights schema patterns. Include edge cases (all-green employee, all-red employee, declining trend employee) | 3.0 |  |
| 0.5 | Validate generated data: spot-check distributions, confirm edge cases present, write 3-5 unit tests for the generator | 1.5 |  |
| 0.6 | Correct all positioning text: update pricing from "$57/E5" to "$6/user/month add-on," rewrite value prop as "for teams outside the Microsoft ecosystem." Update PLAN.md and any copy files | 1.0 |  |
| 0.7 | Create 2 demo personas with backstories: "Sarah the SWE" (individual view) and "Marcus the EM" (manager view). Write persona cards in `docs/personas.md` | 1.0 |  |
|  | **Sprint 0 Total** | **11.5h** |  |

**Definition of Done:**
- Streamlit app runs locally with shared theme applied
- Synthetic dataset loads and passes validation tests
- Score formula is documented with cited thresholds
- All pricing/positioning text uses corrected figures
- Two demo personas written

**Go/No-Go Gate:**
- Synthetic data generator produces valid, diverse output (verified by tests)
- Score formula is defined and documented
- If data generation takes >4h or produces unrealistic patterns, STOP and simplify to 10 employees x 7 days

---

### Sprint 1 — Core Engine & Individual Dashboard (April 4-8 | 5 days | 30-40h)

**Sprint Goal:** Build the working scoring engine, GPT-4o-mini nudge generation, and a complete individual employee dashboard with trend lines.

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 1.1 | Implement rules-based scoring engine: 4 dimensions (focus, boundaries, rest, social connection), each 0-100. Configurable thresholds. Pure functions, no mutation. Return new score objects | 4.0 |  |
| 1.2 | Unit tests for scoring engine: test each dimension independently, test composite score, test edge cases (perfect score, worst score, boundary values) | 2.0 |  |
| 1.3 | Build GPT-4o-mini nudge generation: system prompt with hard constraints (no diagnosis, no clinical language, always append resources), input = dimension scores + work pattern summary, output = personalized micro-nudge. Include prompt template in `src/prompts/` | 3.0 |  |
| 1.4 | Pre-generate and cache nudges for all 20 synthetic employees (avoid live API calls during demo). Store in `data/cached_nudges.json` | 1.5 |  |
| 1.5 | Build consent onboarding flow: 2-3 screen Streamlit flow — what data is collected, how it is used, opt-in/opt-out, "This is NOT a substitute for professional care" banner | 2.5 |  |
| 1.6 | Build individual dashboard page: employee selector, composite wellbeing score gauge, 4-dimension breakdown (radar chart or bar chart), current nudge display, transparency panel ("About this score") | 5.0 |  |
| 1.7 | Add trend line charts: 14-day score history per dimension using Plotly line charts. Highlight declining trends visually | 3.0 |  |
| 1.8 | **Week-over-Week Trend Detection** (strategic review mandate): compare current week vs. prior week across all 4 dimensions. Flag dimensions with >15% decline. Display trend arrows and delta values on the dashboard | 5.0 |  |
| 1.9 | Professional resource escalation: when any dimension is in the "red" zone (<30), surface EAP links, HR contacts, and professional mental health resource links. Non-dismissable card | 2.0 |  |
| 1.10 | Integration tests: end-to-end flow from data load through scoring through nudge display. Test with 3 personas (healthy, at-risk, critical) | 2.5 |  |
|  | **Sprint 1 Total** | **30.5h** |  |

**Definition of Done:**
- Scoring engine passes all unit tests
- Individual dashboard displays scores, trends, nudges for any selected employee
- Week-over-week trend detection flags declining dimensions
- Consent flow works end-to-end
- Red-zone escalation surfaces professional resources
- All nudges pre-cached for demo reliability

**Go/No-Go Gate:**
- Scoring engine produces correct, interpretable results for all 20 employees
- Dashboard renders without errors for all employee selections
- If nudge generation quality is poor, fall back to template-based nudges with variable insertion (2h rework)
- If week-over-week detection takes >6h, cut to simple "up/down arrow" indicators (save 3h)

---

### Sprint 2 — Manager Heatmap & Advanced Features (April 9-12 | 4 days | 24-32h)

**Sprint Goal:** Build the demo-anchor manager heatmap, add the What-If Simulator and Nudge A/B comparison, and begin UI polish.

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 2.1 | **Manager Heatmap (THE demo moment):** Plotly heatmap — 20 employees (anonymized, row labels = "Employee 1-20") x 14 days. Color gradient: green (healthy) to yellow (caution) to red (at-risk). Composite wellbeing score per cell | 5.0 |  |
| 2.2 | Heatmap interactivity: hover tooltips showing dimension breakdown per cell. Click-to-drill-down showing which dimensions drove the score. Team-wide average trend line below the heatmap | 3.0 |  |
| 2.3 | Anonymization enforcement: minimum 5-employee aggregation for any team-level stat. No manager should be able to identify individual employees. Add visual indicator "Anonymized — minimum 5 employees" | 1.5 |  |
| 2.4 | **Heatmap polish (40% of polish budget):** Color calibration (colorblind-safe palette option), axis labels, title, legend, responsive sizing, loading animation. Ensure the heatmap is screenshot-worthy | 4.5 |  |
| 2.5 | **What-If Schedule Simulator (strategic review mandate):** User inputs a hypothetical schedule change (e.g., "remove 2 meetings from Wednesday," "add 1h focus block daily"). System recalculates the wellbeing score and shows before/after comparison with delta highlighting | 7.0 |  |
| 2.6 | **Nudge A/B Comparison (strategic review mandate):** For a given employee state, show 2 GPT-4o-mini generated nudges side-by-side (different tone/approach). Let the user vote on which is more helpful. Display vote tallies. Demonstrates AI iteration capability | 2.0 |  |
| 2.7 | Navigation and page structure: sidebar with pages — Onboarding, Individual Dashboard, Manager Heatmap, What-If Simulator, About/Ethics. Consistent layout using shared theme | 2.0 |  |
| 2.8 | Unit tests for heatmap data preparation and What-If score recalculation logic | 2.0 |  |
|  | **Sprint 2 Total** | **27.0h** |  |

**Definition of Done:**
- Manager heatmap renders correctly with 20x14 grid, correct color mapping, and drill-down
- What-If Simulator recalculates scores for schedule changes and shows before/after
- Nudge A/B comparison displays two alternatives side-by-side
- Anonymization layer enforced
- Navigation between all pages works smoothly
- Heatmap passes the "screenshot test" — visually compelling at first glance

**Go/No-Go Gate:**
- Heatmap must be visually compelling and functionally correct — this is non-negotiable
- If What-If Simulator exceeds 8h, cut scope to 2 preset scenarios (dropdown) instead of free-form input (saves 3h)
- If total Sprint 2 hours exceed budget, cut Nudge A/B Comparison first (lowest impact, 2h saved)
- Heatmap polish is protected — do not cut below 3h even under time pressure

---

### Sprint 3 — Polish, Testing & Demo Prep (April 13-15 | 3 days | 18-24h)

**Sprint Goal:** Achieve demo-ready state with full end-to-end testing, deployment backup, demo script, and rehearsal.

| # | Task | Est. Hours | Priority |
|---|------|-----------|----------|
| 3.1 | End-to-end testing: complete walkthrough with synthetic data. Test all pages, all employee selections, all edge cases (all-green team, all-red team, mixed). Fix any bugs found | 3.0 |  |
| 3.2 | UI polish (remaining 60% of polish budget): consistent spacing, font sizes, color scheme from shared theme, loading states, error handling for edge cases, mobile-responsive spot checks | 3.0 |  |
| 3.3 | Responsible AI page: "About BalanceIQ" page with non-clinical positioning statement, APA guidelines reference, data consent model explanation, bias awareness notes, AI transparency statement, professional resource directory | 2.0 |  |
| 3.4 | Write demo script (5 minutes): Problem (30s — burnout stats, Viva pricing correction, "teams outside Microsoft ecosystem"), Solution overview (45s), Live demo: consent flow (30s) then Sarah's individual dashboard with trends (60s) then Manager heatmap with drill-down (60s) then What-If Simulator (30s), Responsible AI (15s), Close (10s) | 2.0 |  |
| 3.5 | Deploy to Streamlit Community Cloud as backup. Verify deployment works. Pre-warm the app | 1.5 |  |
| 3.6 | Create fallback assets: screenshots of every key screen, 2-minute screen recording of the full demo flow. Store in `docs/demo-backup/` | 1.5 |  |
| 3.7 | Demo rehearsal: run through the full 5-minute demo at least 3 times. Time each section. Identify and fix any stumbles, slow loads, or confusing transitions | 2.0 |  |
| 3.8 | Presentation slide deck: 3-5 slides for non-demo portions (problem statement with corrected Viva pricing, architecture diagram, responsible AI framework, team/contact info) | 2.0 |  |
| 3.9 | Final code cleanup: remove debug prints, ensure `.env` is in `.gitignore`, verify no hardcoded API keys, add README with setup instructions | 1.5 |  |
| 3.10 | Pre-warm and freeze demo state: ensure cached nudges are loaded, synthetic data is in place, app starts in <5 seconds, no API calls needed during live demo | 1.0 |  |
|  | **Sprint 3 Total** | **19.5h** |  |

**Definition of Done:**
- Full demo runs without errors for 5 minutes straight
- Backup deployment on Streamlit Cloud is live and functional
- Screen recording fallback exists
- Demo script is written and rehearsed 3+ times
- No hardcoded secrets in codebase
- Responsible AI page is complete
- All positioning uses corrected Viva pricing and "outside Microsoft ecosystem" framing

**Go/No-Go Gate:**
- Demo must run error-free for the full 5-minute script — if not, cut the weakest feature
- Streamlit Cloud backup must be accessible — if deployment fails, screen recording becomes primary backup
- If any feature is buggy during rehearsal, hide it from the demo flow rather than showing a broken feature

---

## 2. Milestone Checkpoints

| Milestone | Date | Deliverable | Verification |
|-----------|------|-------------|-------------|
| **M0: Skeleton Ready** | April 3 (end of day) | Streamlit app runs with shared theme, synthetic data loads, scoring formula documented | `pytest` passes, app renders |
| **M1: Engine Complete** | April 6 (end of day) | Scoring engine + nudge generation working for all 20 employees | Unit tests pass, manual spot-check of 5 employees |
| **M2: Individual Dashboard** | April 8 (end of day) | Full individual view with trends, week-over-week detection, consent flow, escalation | End-to-end test of 3 personas |
| **M3: Heatmap Anchor** | April 10 (end of day) | Manager heatmap renders with drill-down, anonymization, polish | Screenshot review — is this demo-worthy? |
| **M4: Advanced Features** | April 12 (end of day) | What-If Simulator and Nudge A/B working | Manual test of 3 scenarios each |
| **M5: Demo-Ready** | April 14 (end of day) | Full demo rehearsed 3x, backup deployed, fallback assets created | Timed run-through under 5 minutes |
| **M6: Ship** | April 15 (end of day) | Final code committed, demo state frozen, slide deck done | Team sign-off |

---

## 3. Risk Gates

### Scope Cut Triggers

| Trigger Condition | Action |
|-------------------|--------|
| Sprint 1 exceeds 36h (4.5h/day overage) | Cut Week-over-Week Trend Detection to simple up/down arrows |
| Sprint 2 exceeds 30h | Cut Nudge A/B Comparison (2h saved) |
| What-If Simulator exceeds 8h | Reduce to 2 preset scenarios via dropdown instead of free-form input |
| Heatmap takes >6h before polish | Simplify to static heatmap (no drill-down), redirect time to polish |
| Total project exceeds 95h by end of Sprint 2 | Cut What-If Simulator entirely, focus on core demo path |
| GPT-4o-mini nudge quality is poor | Switch to template nudges with variable insertion (2h rework) |
| Streamlit Cloud deployment fails | Rely on local demo + screen recording backup |
| 5th team member does NOT join | Already planned for single developer — no change |
| 5th team member joins part-time (10-15h) | Assign them: Responsible AI page (2h) + demo script (2h) + slide deck (2h) + rehearsal support + What-If Simulator UI (4-6h) |

### Cut Order (first cut to last cut)

1. **Nudge A/B Comparison** (1-2h feature, lowest demo impact)
2. **What-If Simulator free-form input** (downgrade to preset scenarios)
3. **Week-over-Week Trend Detection** (downgrade to simple arrows)
4. **What-If Simulator entirely** (if severely behind)
5. **Heatmap drill-down interactivity** (keep static heatmap — NEVER cut the heatmap itself)
6. **Individual trend lines** (keep current-state scores only)

### Features That Must NEVER Be Cut

- Manager anonymized heatmap (the demo moment)
- Rules-based scoring engine (the core product)
- Consent onboarding flow (responsible AI requirement)
- Professional resource escalation (ethical red line)
- Non-clinical positioning text (hackathon hard constraint)

---

## 4. Demo Readiness Checklist

### Must Be Working (non-negotiable)

- [ ] Consent onboarding flow completes without errors
- [ ] Individual dashboard loads for any of 20 employees in <3 seconds
- [ ] Wellbeing score displays correctly across all 4 dimensions
- [ ] At least one nudge displays per employee (cached, no live API call)
- [ ] Manager heatmap renders 20x14 grid with correct color mapping
- [ ] Heatmap hover tooltips show dimension breakdown
- [ ] Professional resource links appear for red-zone employees
- [ ] "This is not a substitute for professional care" banner visible on every page
- [ ] All text uses corrected Viva pricing ($6/user/month) and "outside Microsoft ecosystem" positioning

### Must Be Rehearsed

- [ ] Full 5-minute demo script run through 3+ times
- [ ] Transitions between pages are smooth (no loading spinners >2 seconds)
- [ ] Demo narrative follows persona flow: Sarah (individual) then Marcus (manager)
- [ ] Speaker can explain the scoring formula in 15 seconds if asked
- [ ] Speaker can articulate "why not just use Viva Insights?" in 20 seconds
- [ ] Speaker can describe the responsible AI framework in 30 seconds if asked

### Must Be Backed Up

- [ ] Streamlit Community Cloud deployment live and tested
- [ ] Screen recording of complete demo flow (2 minutes, no audio)
- [ ] Screenshots of all key screens saved in `docs/demo-backup/`
- [ ] Cached nudges file (`data/cached_nudges.json`) committed to repo
- [ ] Synthetic dataset committed to repo (no API calls needed to regenerate)
- [ ] Slide deck exported as PDF (not dependent on internet/cloud)

### Pre-Demo Day Checklist (April 15, night)

- [ ] Laptop charged, charger packed
- [ ] App tested on demo laptop (not just dev machine)
- [ ] Browser bookmarks set for local app URL and Streamlit Cloud URL
- [ ] Demo script printed (paper backup)
- [ ] API key is NOT needed for demo (all outputs cached)
- [ ] Internet failure plan: local demo works fully offline with cached data

---

## 5. Critical Path

```
Synthetic Data Generator (0.4, 3h)
    |
    v
Scoring Engine (1.1, 4h) ──────> Individual Dashboard (1.6, 5h) ──> Manager Heatmap (2.1, 5h)
    |                                    |                                    |
    v                                    v                                    v
Nudge Generation (1.3, 3h)      Trend Lines (1.7, 3h)               Heatmap Polish (2.4, 4.5h)
    |                                    |                                    |
    v                                    v                                    v
Cache Nudges (1.4, 1.5h)       W-o-W Detection (1.8, 5h)           E2E Testing (3.1, 3h)
                                                                              |
                                                                              v
                                                                    Demo Script + Rehearsal (3.4+3.7, 4h)
```

### Critical Path Sequence (zero slack)

These tasks form the longest dependency chain. Any delay here directly delays the demo:

| Step | Task | Hours | Cumulative | Slack |
|------|------|-------|------------|-------|
| 1 | Synthetic Data Generator (0.4) | 3.0 | 3.0 | 0h |
| 2 | Scoring Engine (1.1) | 4.0 | 7.0 | 0h |
| 3 | Individual Dashboard (1.6) | 5.0 | 12.0 | 0h |
| 4 | Manager Heatmap (2.1) | 5.0 | 17.0 | 0h |
| 5 | Heatmap Polish (2.4) | 4.5 | 21.5 | 0h |
| 6 | E2E Testing (3.1) | 3.0 | 24.5 | 0h |
| 7 | Demo Script + Rehearsal (3.4 + 3.7) | 4.0 | 28.5 | 0h |
| **Critical Path Total** | | **28.5h** | | |

### Near-Critical Path (limited slack)

| Task | Hours | Slack |
|------|-------|-------|
| Nudge Generation + Caching (1.3 + 1.4) | 4.5 | ~3h (can run parallel to dashboard work) |
| Week-over-Week Trend Detection (1.8) | 5.0 | ~4h (can be cut to arrows if needed) |
| What-If Simulator (2.5) | 7.0 | ~8h (can be cut entirely) |
| Consent Flow (1.5) | 2.5 | ~6h (quick to build, flexible timing) |

### Tasks with Most Slack (safe to defer or cut)

| Task | Hours | Slack |
|------|-------|-------|
| Nudge A/B Comparison (2.6) | 2.0 | ~16h — first to cut |
| Responsible AI page (3.3) | 2.0 | ~12h — can be written last |
| Slide deck (3.8) | 2.0 | ~10h — can be done night before |
| Persona cards (0.7) | 1.0 | ~14h — nice to have for planning |

---

## Hour Budget Summary

| Sprint | Estimated Hours | Budget Range (6-8h/day) | Buffer |
|--------|----------------|------------------------|--------|
| Sprint 0 (2 days) | 11.5h | 12-16h available | 0.5-4.5h |
| Sprint 1 (5 days) | 30.5h | 30-40h available | 0-9.5h |
| Sprint 2 (4 days) | 27.0h | 24-32h available | 0-5h |
| Sprint 3 (3 days) | 19.5h | 18-24h available | 0-4.5h |
| **Total** | **88.5h** | **84-112h available** | **0-23.5h** |

The plan fits within the single-developer budget at 88.5h estimated against 84-112h available. At the low end (6h/day), the plan is tight with essentially no buffer — scope cuts from Section 3 would activate. At the high end (8h/day), there is a 23.5h buffer that could absorb overruns or enable additional polish.

---

## Appendix: Strategic Review Mandate Tracking

| Mandate | Sprint | Task # | Hours | Status |
|---------|--------|--------|-------|--------|
| Correct Viva Insights pricing ($6/user/month) | Sprint 0 | 0.6 | 1.0h | Planned |
| Reposition as "teams outside Microsoft ecosystem" | Sprint 0 | 0.6 | (included) | Planned |
| What-If Schedule Simulator | Sprint 2 | 2.5 | 7.0h | Planned |
| Week-over-Week Trend Detection | Sprint 1 | 1.8 | 5.0h | Planned |
| Nudge A/B Comparison | Sprint 2 | 2.6 | 2.0h | Planned |
| Heatmap gets 40% of polish time | Sprint 2 | 2.4 | 4.5h | Planned |
| Shared Streamlit theme template | Sprint 0 | 0.1 | (included) | Planned |
