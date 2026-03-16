# Strategic Review — PM/CTO Final Assessment

**Reviewer:** PM/CTO Agent | **Date:** 2026-03-15
**Inputs:** 5 Adversarial Review Reports, CTO Review, 5 PRD Sections, 5 PLAN.md files

---

## Executive Summary

Five parallel adversarial reviews were conducted on all hackathon categories. The original CTO review was **strategically correct but tactically optimistic** about execution risk. Every category has at least one scheduling error, scope issue, or under-specified deliverable that the adversarial agents identified. This document consolidates findings and mandates revisions before sprint planning begins.

---

## Revised Win Probability Matrix

| Category | Original | Revised Range | Realistic Midpoint | Key Risk |
|----------|----------|---------------|---------------------|----------|
| Cat 1 (BalanceIQ) | 15-25% | 25-35% ceiling | 20% | Crowded field, low AI depth |
| Cat 2 (PhishGuard) | 70-80% | 55-85% | 70% | Feature sprawl, field size |
| Cat 3 (SmartMatch) | 65-75% | 55-75% | 65% | Written deliverables at grade D |
| Cat 4 (SimResearch) | 45-60% | 25-65% | 50% | Differentiators are vaporware |
| Cat 5 (CropSense) | 45-55% | 25-70% | 50% | From-scratch + framework risk |

---

## Revised Tier Rankings

| Tier | Category | Condition |
|------|----------|-----------|
| **Tier 1** | Cat 2 (PhishGuard) | Enforce P0/P1 scope split |
| **Tier 1** | Cat 3 (SmartMatch) | Written deliverables start Day 1 |
| **Tier 1.5** | Cat 5 (CropSense) | Working vertical slice by Day 4 |
| **Tier 2** | Cat 4 (SimResearch) | Must-add features over polish |
| **Tier 3/Optional** | Cat 1 (BalanceIQ) | Only with 5th team member |

---

## Critical Revisions Mandated

### IMMEDIATE (Day 0 — before any coding)

1. **RESOLVE Cat 5 frontend:** Default to Streamlit unless a team member has prior Next.js experience. The tech-stack.md and CTO review both say Streamlit; only the PRD says Next.js. Consistency matters.
2. **CORRECT Cat 1 pricing:** Viva Insights is $6/user/month add-on, NOT $57 E5 licensing. Avanade judges will know this. Reposition as "teams outside the Microsoft ecosystem entirely."
3. **CAPTURE Cat 4 "before" baselines:** Run prototype TODAY, screenshot every dashboard tab, save all output CSVs. If code is modified first, the before/after narrative is permanently lost.
4. **DECIDE team size and Cat 1 scope:** If 3-4 people, drop Cat 1. If 5, assign the 5th person.
5. **ASSIGN a dedicated writer for Cat 3:** Growth Strategy + Measurement Plan = 40% of judging score. Must start Day 1 with a full-time owner.

### Sprint Structure Revisions

6. **Cat 2:** Enforce P0 (8 features) / P1 (5 features) split. Feature freeze Day 9.
7. **Cat 3:** Move written deliverables from Days 11-12 to Days 1-14 (continuous parallel track).
8. **Cat 4:** Lock dashboard UI for week 1. Build 4 must-add features. Polish last 3 days only.
9. **Cat 5:** Build vertical slice (photo upload → advisory display) by Day 4. If not working by Day 4, fallback to simpler architecture.
10. **All:** Build shared infrastructure (LLM wrapper, Streamlit theme, demo template) Days 1-2.

### Must-Add Features per Category

| Cat | Feature | Effort | Why |
|-----|---------|--------|-----|
| 2 | Visual Phishing Anatomy Highlighter | 4-6h | Visual differentiator, mirrors ISACA training materials |
| 2 | Live Judge Challenge Mode (unscripted with timer) | 2-3h | Highest trust signal in any hackathon demo |
| 3 | Growth Strategy Document (consulting quality) | 6-8h | 10 of 50 judging points, currently at grade D |
| 3 | Real-Data Pipeline Funnel | 2-3h | Market research judges will spot fake funnel data |
| 3 | Calendar Invite Preview (.ics) | 1-2h | Directly addresses stated challenge requirement |
| 4 | Ground Truth Comparison Dashboard | 4-6h | THE demo moment — without it, no validation story |
| 4 | Live Cost Ticker ($0.08 vs $24K) | 2-3h | Makes cost claim visceral, not verbal |
| 4 | Krippendorff's Alpha Reliability Panel | 4-5h | Methodological credibility, Aytm judges recognize this |
| 4 | Tony Koo Business Recommendation | 3-4h | Judging rubric explicitly asks for this |
| 5 | Confidence Gradient UI | 2-3h | Makes responsible AI visible in the UI |
| 5 | Extension Officer Mode (dual persona) | 6-8h | Doubles impact narrative, highest ROI feature |

### Narrative/Demo Revisions

| Cat | Revision |
|-----|----------|
| 2 | Define micro-lesson content matrix (threat_type x lesson content x 10+ types) |
| 2 | Create UI wireframes BEFORE coding starts |
| 3 | Quantify ROI: volunteer hours saved + membership LTV |
| 3 | Map specific board members to expansion campuses in Growth Strategy |
| 4 | Name the methodology (e.g., "VALIDATE"), present as original contribution |
| 4 | Frame as "we built a methodology, not polished a prototype" |
| 5 | Calculate Amina-specific cost-of-inaction ($144/season) |
| 5 | Add "time to diagnosis" metric (10 seconds vs 2-4 weeks) |
| All | Demo rehearsal starts Day 11, not Day 14 |

---

## Shared Infrastructure (Build Days 1-2)

| Component | Effort | Categories |
|-----------|--------|------------|
| LLM API wrapper (configurable provider) | 4h | All |
| Streamlit theme template (shared styling) | 3h | 1, 2, 3, 4, 5 |
| Demo script template (5-min structure) | 1h | All |
| Responsible AI doc template | 2h | All |
| Demo scenario caching utility | 3h | 2, 4 |
| **Total** | **13h** | |

---

## Resource Allocation (Revised for 4-Person Team)

| Person | Primary | Secondary | Schedule |
|--------|---------|-----------|----------|
| A | Cat 2 (PhishGuard) lead | Shared infra Days 1-2 | Full 2 weeks |
| B | Cat 3 backend + matching engine | Cat 5 support (Day 12-14 polish) | Full 2 weeks |
| C | Cat 4 must-adds (Days 1-5) → Cat 3 written deliverables (Days 6-14) | — | Split |
| D | Cat 5 (CropSense) lead | — | Full 2 weeks |

**If 5-person team:** Person E takes Cat 1 (BalanceIQ) lead and supports Cat 3 written deliverables.

**If 3-person team:** Drop Cat 1 and Cat 4. Focus on Cat 2 + Cat 3 + Cat 5.

---

## Sprint Framework (All Categories)

| Sprint | Days | Focus |
|--------|------|-------|
| Sprint 0 | 0-1 | Shared infra, Day 0 actions, project setup |
| Sprint 1 | 2-7 | Core MVP build, critical features |
| Sprint 2 | 8-11 | Must-add features, UI polish, written deliverables |
| Sprint 3 | 12-14 | Demo prep, rehearsal, testing, buffer |

**Hard Rules:**
- Feature freeze: Day 9
- Demo rehearsal starts: Day 11
- All written deliverables complete: Day 12
- Full demo run-through with backup plan: Day 13

---

## Adversarial Q&A Prep (Top 3 per Category)

### Cat 2 (PhishGuard)
1. "You're mostly calling the OpenAI API. What happens when it's wrong?" → Demo the tri-layer conflict resolution live
2. "Norton has Genie, Google has Safe Browsing. Why does this need to exist?" → Education, not detection. 30-sec micro-doses vs $15-50/employee training with 4% completion rate
3. "How do you prevent someone from using this to refine phishing attacks?" → Generic explanations, no storage, output scanning

### Cat 3 (SmartMatch)
1. "Your matching algorithm has 6 factors but real data for only 2. How?" → Low weights on bootstrapped factors, system designed to learn over time
2. "Your pipeline funnel data is entirely fictional, isn't it?" → Use real prototype outputs for top-of-funnel stages
3. "Growth Strategy says expand to 3+ universities. How without existing relationships?" → Map board members to campuses by geography

### Cat 4 (SimResearch)
1. "Your synthetic respondents come from prompts YOU wrote. How is this different from writing the results yourself?" → Dual-LLM validation + Krippendorff's alpha + ground truth comparison
2. "You're building on someone else's prototype. What did YOUR team contribute?" → Named methodology, ground truth validation, reliability metrics, business recommendation engine
3. "Peng et al. identify 5 distortions. How do you address central tendency bias?" → Temperature 0.8, personality variation seeds, distribution reporting

### Cat 5 (CropSense)
1. "PlantVillage images are lab-controlled. What about real field photos?" → Confidence thresholds, visually distinct diseases, triage tool framing
2. "Azure Custom Vision is being retired 2028. Why build on it?" → 2+ years runway, documented migration path, focus on advisory not infrastructure
3. "I've seen 5 PlantVillage classifiers at hackathons. What's different?" → Classifier is 20%. Advisory + weather + multilingual SMS is the 80%

---

## Final Verdict

The adversarial reviews were **high quality and actionable**. All 5 agents identified genuine blind spots that the original CTO review missed. The biggest systemic issue is that every PRD over-indexes on technical features and under-indexes on storytelling, judge Q&A preparation, and demo rehearsal.

**The plan is strategically sound. The revisions above address execution risk.**

Ready for sprint planning breakdown.
