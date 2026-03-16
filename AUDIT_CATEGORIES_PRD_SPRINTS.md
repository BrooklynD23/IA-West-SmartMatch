# Categories, PRD, and Sprint Audit

**Audited:** 2026-03-15  
**Scope:** Category plans, PRD sections, master PRD, sprint plans, status trackers  
**Audit lens:** Strategy, consistency, feasibility, staffing, and judge-readiness

## Executive Summary

**Portfolio verdict:** Strong strategy, uneven document control.

- **Best-positioned categories:** Cat 2 and Cat 3
- **Best leverage if disciplined:** Cat 4
- **Most document drift:** Cat 1 and Cat 5
- **Biggest portfolio problem:** there is no single trusted source of truth for dates, tiers, and canonical stack decisions

**Inference:** the latest intended direction is `STRATEGIC_REVIEW.md` plus `MASTER_SPRINT_PLAN.md` and the detailed sprint plans, because they are newer (dated 2026-03-15) and explicitly revise earlier material.

## Portfolio Scorecard

| Category | Strategy | Consistency | Execution Readiness | Judge Readiness | Overall |
|---|---|---|---|---|---|
| Cat 1 — BalanceIQ | Yellow | Red | Yellow | Yellow | Yellow-Red |
| Cat 2 — PhishGuard | Green | Yellow | Green | Green | Green |
| Cat 3 — SmartMatch | Green | Yellow | Green | Green | Green |
| Cat 4 — SimResearch | Green | Yellow | Green | Green | Green |
| Cat 5 — CropSense | Green | Red | Yellow | Green | Yellow-Red |

## Portfolio-Level Findings

### Red

1. **Canonical decisions are not propagated consistently**
   - Cat 1 still contains stale pricing/positioning and stale architecture signals after the strategic correction:
     - `STRATEGIC_REVIEW.md:42`
     - `STRATEGIC_REVIEW.md:43`
     - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:14`
     - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:15`
     - `PRD_SECTION_CAT1.md:85`
     - `PRD_SECTION_CAT1.md:89`
     - `Category 1 - Avanade AI Wellbeing/PLAN.md:71`
     - `Category 1 - Avanade AI Wellbeing/PLAN.md:79`
     - `Category 1 - Avanade AI Wellbeing/PLAN.md:115`
   - Cat 5 still has unresolved stack drift:
     - `STRATEGIC_REVIEW.md:42`
     - `PRD_SECTION_CAT5.md:19`
     - `PRD_SECTION_CAT5.md:76`
     - `PRD_SECTION_CAT5.md:84`
     - `PRD_SECTION_CAT5.md:90`
     - `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md:8`
     - `Category 5 - Avanade Creative SDG/.status.md:28`
     - `Category 5 - Avanade Creative SDG/PLAN.md:82`
     - `Category 5 - Avanade Creative SDG/PLAN.md:84`
     - `Category 5 - Avanade Creative SDG/PLAN.md:86`
     - `Category 5 - Avanade Creative SDG/PLAN.md:87`

2. **The sprint calendar is inconsistent across the portfolio**
   - Top-level portfolio assumes the prep window is roughly April 2-16:
     - `HACKATHON_PRD.md:5`
     - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:4`
   - Category sprint plans use different calendar anchors:
     - `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md:4`
     - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:3`
     - `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md:16`
   - This breaks shared infra planning, handoffs, and milestone comparison.

3. **Status tracking is not trustworthy**
   - Cat 1 marks `DOC` done:
     - `Category 1 - Avanade AI Wellbeing/.status.md:15`
   - Cats 2-5 still mark `DOC` pending even though detailed sprint plans exist:
     - `Category 2 - ISACA Cyber Safety Coach/.status.md:15`
     - `Category 3 - IA West Smart Match CRM/.status.md:15`
     - `Category 4 - Aytm x Neo Smart Living/.status.md:15`
     - `Category 5 - Avanade Creative SDG/.status.md:15`
   - Result: the portfolio tracker cannot be used as an execution dashboard.

### Yellow

1. **Tier and win-probability numbers drift between documents**
   - Original portfolio ranges:
     - `HACKATHON_PRD.md:18`
     - `HACKATHON_PRD.md:20`
     - `HACKATHON_PRD.md:22`
     - `HACKATHON_PRD.md:24`
     - `HACKATHON_PRD.md:26`
   - Revised ranges:
     - `STRATEGIC_REVIEW.md:18`
     - `STRATEGIC_REVIEW.md:19`
     - `STRATEGIC_REVIEW.md:20`
     - `STRATEGIC_REVIEW.md:21`
     - `STRATEGIC_REVIEW.md:22`
     - `MASTER_SPRINT_PLAN.md:28`
     - `MASTER_SPRINT_PLAN.md:30`
     - `MASTER_SPRINT_PLAN.md:32`
   - Status files still mostly reflect the older tier framing:
     - `Category 1 - Avanade AI Wellbeing/.status.md:3`
     - `Category 4 - Aytm x Neo Smart Living/.status.md:3`
     - `Category 5 - Avanade Creative SDG/.status.md:3`

2. **The 4-person operating model is viable but brittle**
   - The plan leaves only about 13 hours of slack:
     - `MASTER_SPRINT_PLAN.md:235`
     - `MASTER_SPRINT_PLAN.md:239`
   - It also depends on one high-risk handoff from Cat 4 to Cat 3 writing:
     - `MASTER_SPRINT_PLAN.md:44`
     - `MASTER_SPRINT_PLAN.md:145`
   - This is workable, but only if Cat 4 truly freezes after Day 5 and Cat 3 writing starts on schedule.

3. **Cat 1 remains too “active” for an optional category**
   - The strategic guidance says Cat 1 is only for a 5-person team:
     - `STRATEGIC_REVIEW.md:45`
     - `MASTER_SPRINT_PLAN.md:32`
     - `MASTER_SPRINT_PLAN.md:57`
   - But Cat 1 still has a fully detailed primary sprint plan and top-level PRD presence:
     - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:1`
     - `HACKATHON_PRD.md:80`
   - That creates planning ambiguity unless the team explicitly parks it.

### Green

1. **Cat 2 is the cleanest sponsor-fit plan**
   - Strong problem-solution fit, clear P0/P1 logic, and a polished demo path:
     - `PRD_SECTION_CAT2.md:10`
     - `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md:17`
     - `MASTER_SPRINT_PLAN.md:96`

2. **Cat 3 has the strongest execution model**
   - The dual-track sprint plan correctly treats writing as first-class work:
     - `STRATEGIC_REVIEW.md:51`
     - `MASTER_SPRINT_PLAN.md:29`
     - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:4`
     - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:134`

3. **Cat 4 has the clearest “demo story” architecture**
   - Baseline capture, must-add features, and VALIDATE framing are all coherent:
     - `STRATEGIC_REVIEW.md:44`
     - `STRATEGIC_REVIEW.md:65`
     - `STRATEGIC_REVIEW.md:80`
     - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:14`
     - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:33`

## Category-by-Category Audit

### Cat 1 — BalanceIQ

**Verdict:** Good concept, poor propagation.

- The sprint plan reflects the corrected strategy: rules engine, corrected Viva pricing, and “outside the Microsoft ecosystem” framing:
  - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:14`
  - `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md:15`
- The PRD section still carries stale pricing and stale value-prop language:
  - `PRD_SECTION_CAT1.md:85`
  - `PRD_SECTION_CAT1.md:89`
- The original category plan still describes the older architecture direction:
  - `Category 1 - Avanade AI Wellbeing/PLAN.md:71`
  - `Category 1 - Avanade AI Wellbeing/PLAN.md:79`
  - `Category 1 - Avanade AI Wellbeing/PLAN.md:115`
- Net effect: a builder could easily implement the wrong story or wrong system if they open the wrong file first.

### Cat 2 — PhishGuard

**Verdict:** Best overall category, minor tracker drift.

- The PRD and sprint plan are directionally aligned around tri-layer classification, education-first UX, and demo scenario coverage:
  - `PRD_SECTION_CAT2.md:10`
  - `PRD_SECTION_CAT2.md:81`
  - `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md:17`
  - `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md:28`
- Main issues:
  - `DOC` is still marked pending in status:
    - `Category 2 - ISACA Cyber Safety Coach/.status.md:15`
  - The plan uses a March 15-28 calendar while the portfolio-level docs frame a different prep window:
    - `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md:4`
    - `HACKATHON_PRD.md:5`

### Cat 3 — SmartMatch

**Verdict:** Strongest execution system, but still date-noisy.

- This is the best-written sprint plan in the repo for actual delivery:
  - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:1`
  - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:134`
  - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:232`
- It properly elevates writing and real data:
  - `Category 3 - IA West Smart Match CRM/.status.md:32`
  - `MASTER_SPRINT_PLAN.md:29`
- Main issues:
  - The prep-window wording is internally confusing:
    - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:3`
  - Status still says `DOC pending`:
    - `Category 3 - IA West Smart Match CRM/.status.md:15`

### Cat 4 — SimResearch

**Verdict:** High-leverage category with the clearest differentiated demo.

- The sprint plan is disciplined and anchored on four must-add features:
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:33`
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:70`
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:101`
- The methodology naming and before/after story are strong:
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:7`
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:14`
- Main issues:
  - Status is outdated on documentation state:
    - `Category 4 - Aytm x Neo Smart Living/.status.md:15`
  - The plan is compressed enough that any slip on Days 1-3 will cannibalize polish.

### Cat 5 — CropSense

**Verdict:** Excellent narrative, unresolved implementation spec.

- The sprint plan is coherent and constrained:
  - `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md:8`
  - `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md:93`
  - `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md:114`
- The PRD section is not aligned to that sprint plan:
  - `PRD_SECTION_CAT5.md:19`
  - `PRD_SECTION_CAT5.md:21`
  - `PRD_SECTION_CAT5.md:75`
  - `PRD_SECTION_CAT5.md:76`
  - `PRD_SECTION_CAT5.md:84`
  - `PRD_SECTION_CAT5.md:90`
- The original plan still carries a broader five-system concept that violates the tighter three-system direction:
  - `Category 5 - Avanade Creative SDG/PLAN.md:82`
  - `Category 5 - Avanade Creative SDG/PLAN.md:84`
  - `Category 5 - Avanade Creative SDG/PLAN.md:86`
  - `Category 5 - Avanade Creative SDG/PLAN.md:87`
- The status file introduces another stack mismatch by naming Planetary Computer:
  - `Category 5 - Avanade Creative SDG/.status.md:28`
- This is the single most dangerous category for implementation drift.

## Sprint Cycle Audit

### What Works

- Shared infra is clearly called out and small enough to be manageable:
  - `MASTER_SPRINT_PLAN.md:71`
- Feature freeze and rehearsal timing are explicit:
  - `MASTER_SPRINT_PLAN.md:110`
  - `STRATEGIC_REVIEW.md:84`
- Cat 3 and Cat 4 have concrete go/no-go gates, which is good planning hygiene:
  - `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md:60`
  - `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md:27`

### What Breaks the System

1. **The portfolio is scheduled in “day numbers,” but categories are scheduled in competing real dates**
   - This blocks clean orchestration and makes milestone tracking ambiguous.

2. **The status files are not coupled to the sprint-planning outputs**
   - A PM reading the status docs would conclude docs are missing when they already exist.

3. **Cat 5 and Cat 1 can still send an implementer to the wrong stack**
   - Cat 5: Next.js/Vercel/App Service/Planetary Computer vs Streamlit/Open-Meteo
   - Cat 1: older Viva/Teams/Power BI/anomaly framing vs revised rules-engine/synthetic-data framing

## Top 10 Corrective Actions

1. **Declare the canonical source set**
   - Make `STRATEGIC_REVIEW.md`, `MASTER_SPRINT_PLAN.md`, and the category `SPRINT_PLAN.md` files the operative documents.
   - Mark older `PLAN.md` files as background only unless refreshed.

2. **Resolve Cat 5 immediately**
   - Standardize on one stack everywhere: Streamlit, Azure Custom Vision, Azure OpenAI, Open-Meteo, 3-system scope.

3. **Resolve Cat 1 immediately**
   - Propagate the corrected pricing and positioning into the PRD and either rewrite or clearly supersede the old category plan.

4. **Normalize the calendar**
   - Add one portfolio-wide mapping from Day 0-14 to exact dates and use it in every sprint plan.

5. **Repair the status files**
   - Update Cats 2-5 so `DOC` is done and add a `Last drift review` note.

6. **Reconcile tiers and win probabilities**
   - Update the master PRD and statuses to the revised March 15 ranges, or explicitly tag them as “original CTO ranges.”

7. **Make Cat 1’s optional status unmistakable**
   - If the team is 4 people, label Cat 1 as parked across the portfolio docs.

8. **Preserve Cat 4’s baseline evidence**
   - If baseline capture is not already complete, do that before any implementation work touches the prototype.

9. **Protect Cat 3’s writing track**
   - Keep a dedicated writer from Day 1 and treat the written outputs as P0, not “wrap-up work.”

10. **Re-run capacity math after drift cleanup**
   - Once canonical scope is fixed, recompute actual person-hours and contingency, especially for the 4-person model.

## Final Call

If the team had to choose today based on the audited materials:

1. **Cat 2** is the safest and clearest path to a polished, judge-friendly win attempt.
2. **Cat 3** is the strongest “serious systems” entry if the writing track stays protected.
3. **Cat 4** is the best dark horse if the team wants maximum differentiation with minimum greenfield build.
4. **Cat 5** is still attractive, but only after the stack/spec drift is cleaned up.
5. **Cat 1** should be treated as optional unless a 5th person is confirmed.
