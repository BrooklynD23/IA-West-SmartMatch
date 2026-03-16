# Master Sprint Plan — CPP AI Hackathon 2026

**Generated:** 2026-03-15 | **Hackathon:** April 16, 2026
**Prep Window:** 14 days | **Team Size:** 3-5 people

---

## How to Read This Document

This is the **cross-category orchestration plan**. Each category has its own detailed sprint plan:

| Category | Sprint Plan Location | Hours | Lead |
|----------|---------------------|-------|------|
| Cat 1 (BalanceIQ) | `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md` | 88.5h | Person E (if 5-person team) |
| Cat 2 (PhishGuard) | `Category 2 - ISACA Cyber Safety Coach/SPRINT_PLAN.md` | 100.5h | Person A |
| Cat 3 (SmartMatch) | `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` | 146-176h | Person B + Person C |
| Cat 4 (SimResearch) | `Category 4 - Aytm x Neo Smart Living/docs/SPRINT_PLAN.md` | 40h | Person C (Days 1-5) |
| Cat 5 (CropSense) | `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md` | 107.5h | Person D |

For adversarial review findings and strategic rationale, see `STRATEGIC_REVIEW.md`.

---

## Revised Tier Rankings

| Tier | Category | Win Prob | Condition |
|------|----------|----------|-----------|
| **1** | Cat 2 — PhishGuard AI | 55-85% | P0/P1 scope discipline |
| **1** | Cat 3 — IA SmartMatch CRM | 55-75% | Written deliverables start Day 1 |
| **1.5** | Cat 5 — CropSense AI | 25-70% | Working vertical slice by Day 4 |
| **2** | Cat 4 — SimResearch | 25-65% | Must-add features, not polish |
| **3** | Cat 1 — BalanceIQ | 25-35% | Only with 5th person |

Use these as conditional planning ranges, not unconditional forecasts. Working midpoints from the strategic review are Cat 2 = 70%, Cat 3 = 65%, Cat 4 = 50%, Cat 5 = 50%; Cat 1 stays parked for 3-4 person teams and only reaches the 25-35% upside case with a confirmed 5th person.

---

## Team Resource Allocation

### 4-Person Team (Recommended)

| Person | Days 1-2 | Days 3-5 | Days 6-9 | Days 10-14 |
|--------|----------|----------|----------|------------|
| **A** | Shared infra + Cat 2 APIs | Cat 2 core engine | Cat 2 P0 features + P1 decisions | Cat 2 polish + demo prep |
| **B** | Cat 3 data + embeddings | Cat 3 matching engine | Cat 3 discovery + email + pipeline | Cat 3 polish + demo prep |
| **C** | Cat 4 "before" capture | Cat 4 must-add features | Cat 3 written deliverables (Growth Strategy, Measurement Plan) | Cat 3 docs finalize + Cat 4 demo prep |
| **D** | Cat 5 Azure setup + data | Cat 5 vertical slice (DAY 4 GATE) | Cat 5 weather + multilingual + Extension Officer Mode | Cat 5 narrative + demo prep |

### 5-Person Team

Same as above, plus:

| Person | Days 1-5 | Days 6-9 | Days 10-14 |
|--------|----------|----------|------------|
| **E** | Cat 1 foundation + scoring engine | Cat 1 heatmap + What-If Simulator | Cat 1 polish + demo prep |

### 3-Person Team (Minimal)

Drop Cat 1 and Cat 4 entirely. Focus on Cat 2 + Cat 3 + Cat 5.

| Person | Focus |
|--------|-------|
| **A** | Cat 2 (full 2 weeks) |
| **B** | Cat 3 code + written deliverables |
| **D** | Cat 5 (full 2 weeks) |

---

## Master Timeline (14 Days)

Day numbers are the canonical portfolio schedule. Exact calendar dates inside category sprint plans should be treated as draft kickoff placeholders unless they are explicitly re-anchored to the final team start date.

### Sprint 0: Foundation (Days 1-2)

**Shared Infrastructure (Person A leads, all contribute):**

| Task | Hours | Owner | Used By |
|------|-------|-------|---------|
| LLM API wrapper (configurable: OpenAI / Azure OpenAI / OpenRouter) | 4h | A + D | All |
| Streamlit theme template (header, sidebar, CSS, color scheme) | 3h | A | All |
| Demo script template (5-min structure) | 1h | All | All |
| Responsible AI doc template | 2h | B | All |
| Demo scenario caching utility | 3h | A | 2, 4 |
| **Total shared infra** | **13h** | | |

**Category-Specific Day 0 Actions (NON-NEGOTIABLE):**

| Action | Owner | Why |
|--------|-------|-----|
| Capture Cat 4 "before" baselines (screenshots + CSVs) | C | Before/after narrative dies without this |
| Validate Cat 2 APIs (PhishTank, Google Safe Browsing, OpenAI) | A | Go/no-go for entire Cat 2 architecture |
| Provision Azure Custom Vision + Azure OpenAI for Cat 5 | D | Longest lead time of any setup task |
| Load Cat 3 CSV data, generate embeddings, validate similarity | B | Go/no-go on embedding vs TF-IDF approach |
| Correct Cat 1 Viva pricing in all documents | E (or whoever) | Avanade judges will catch wrong pricing |

### Sprint 1: Core Build (Days 3-7)

| Category | Goal | Key Deliverable | Gate |
|----------|------|-----------------|------|
| Cat 2 | Core classification engine + base UI | Tri-layer classification works on 10/10 demo scenarios | Response time <12s |
| Cat 3 | Matching engine + UI | Top-3 matches per event with explanation cards | Matches are sensible and explainable |
| Cat 4 | 4 must-add features | Ground truth dashboard + cost ticker + Krippendorff's alpha + Tony Koo recommendation | All 4 features working by Day 5 |
| Cat 5 | **Vertical slice (DAY 4 GATE)** | Photo upload → disease classification → advisory display | If not working by Day 4, fallback to simpler architecture |
| Cat 1 | Scoring engine + individual dashboard | Rules engine + GPT nudges + trend lines | Score formula produces meaningful differentiation |

**DAY 4 GATE (Cat 5 only):**
- **PASS:** Vertical slice works end-to-end → proceed with weather + multilingual
- **FAIL:** Architecture too complex → fallback: mock CV responses, focus on advisory quality + narrative

### Sprint 2: Features + Polish (Days 8-11)

| Category | Must-Add Features | Should-Add Features | Feature Freeze |
|----------|-------------------|---------------------|----------------|
| Cat 2 | Visual Highlighter, Judge Challenge Mode | PII redaction, Spanish toggle, report export | **Day 9** |
| Cat 3 | Real-data pipeline funnel, calendar .ics preview | Board expansion map, feedback loop, volunteer dashboard | **Day 9** |
| Cat 4 | Before/after panels, VALIDATE methodology tab | Product-agnostic config layer | **Day 5** (already frozen) |
| Cat 5 | Confidence gradient UI, Extension Officer Mode | Treatment cost estimator, diagnosis history timeline | **Day 9** |
| Cat 1 | Heatmap polish (40% of polish budget), What-If Simulator | Week-over-week trend detection, Nudge A/B comparison | **Day 9** |

**HARD RULE: Feature freeze Day 9. No new features after this point.**

### Sprint 3: Demo Prep (Days 12-14)

| Day | Activity | All Categories |
|-----|----------|----------------|
| **Day 11** | First demo rehearsals begin | Each category does a timed 5-minute run-through |
| **Day 12** | Written deliverables complete | Cat 3 Growth Strategy + Measurement Plan finalized |
| **Day 12** | End-to-end testing | All demo flows tested 3+ times with cached fallbacks |
| **Day 13** | Full dress rehearsal | Complete demo with backup plans tested |
| **Day 13** | Backup assets created | Screen recordings, cached API responses, offline data |
| **Day 14** | Final polish + deploy | Streamlit Cloud deployment verified, slides finalized |

---

## Cross-Category Dependency Map

```
Days 1-2:  Shared Infra ──┬──> Cat 2 (P0 features)
                           ├──> Cat 3 (matching engine)
                           ├──> Cat 5 (vertical slice)
                           └──> Cat 1 (if applicable)

Day 0:     Cat 4 "before" capture ──> Cat 4 must-adds (Days 1-5)

Day 5:     Cat 4 features complete ──> Person C transitions to Cat 3 writing

Day 6:     Cat 3 data package ──> Cat 3 written deliverables (Person C)
           (Person B hands off prototype outputs, data insights, ROI numbers)

Day 9:     FEATURE FREEZE (all categories)

Day 11:    Demo rehearsals begin (all categories)

Day 12:    Written deliverables due (Cat 3)

Day 14:    Ship
```

**Critical Handoff Points:**
1. **Day 0:** Person C captures Cat 4 baselines BEFORE any code changes
2. **Day 4:** Cat 5 vertical slice gate — Person D go/no-go decision
3. **Day 5-6:** Person C transitions from Cat 4 → Cat 3 writing; Person B hands off data package
4. **Day 7-8:** Cat 2 P0/P1 go/no-go decisions (Person A)
5. **Day 12:** Cat 3 written deliverables due from Person C

---

## Risk Escalation Protocol

| Risk Level | Trigger | Action |
|------------|---------|--------|
| **Green** | On schedule, all gates passed | Continue as planned |
| **Yellow** | 1 feature behind by >50% of estimate | Cut lowest-priority should-add feature |
| **Orange** | Core feature blocked or 2+ features behind | Emergency scope cut: drop to P0 only, extend hours |
| **Red** | Critical API failure or team member unavailable | Fallback to cached/mock data, redistribute work |

**Per-Category Scope Cut Order (first to last):**

| Cat 2 | Cat 3 | Cat 4 | Cat 5 | Cat 1 |
|--------|--------|--------|--------|--------|
| Screenshot OCR | Volunteer dashboard | Config layer | Diagnosis history | Nudge A/B |
| Report export | Feedback loop | GenAI doc length | Treatment cost est. | What-If free-form |
| Spanish toggle | Expansion map | -- | Seasonal calendar | Trend detection |
| Judge Challenge | Calendar .ics | -- | Extension Officer Mode | What-If entirely |
| PII redaction | -- | -- | -- | Heatmap drill-down |

**Never cut (per category):**
- Cat 2: Tri-layer classification, micro-lessons, demo scenarios, polished UI
- Cat 3: Matching engine, discovery, email gen, Growth Strategy, Measurement Plan
- Cat 4: Ground truth dashboard, cost ticker, Tony Koo recommendation
- Cat 5: CV classifier, LLM advisory, multilingual output, Amina narrative
- Cat 1: Heatmap, scoring engine, consent flow, resource escalation

---

## Demo Day Checklist (April 16, 2026)

### Pre-Demo (Morning)

- [ ] All Streamlit apps tested locally
- [ ] Streamlit Cloud deployments verified (backup)
- [ ] Cached API responses loaded for offline fallback
- [ ] Screen recordings available as final fallback
- [ ] Slides loaded on presentation laptop
- [ ] Demo script printed (one per presenter)
- [ ] Backup laptop available
- [ ] Internet connectivity tested at venue

### Per-Category Demo Ready

| Cat | Working Pipeline | Demo Script | Backup Plan | Written Docs |
|-----|-----------------|-------------|-------------|--------------|
| 2 | Tri-layer classification on 10+ scenarios | Maria narrative timed | Cached responses + video | Responsible AI page |
| 3 | Match → discover → email in 60 seconds | Live scrape + funnel demo | Cached scrape results | Growth Strategy + Measurement Plan |
| 4 | Ground truth comparison + cost ticker | $0.08 vs $24K hook | All data pre-cached | VALIDATE methodology + Responsible AI |
| 5 | Photo → diagnosis → Swahili SMS advisory | Amina Moment live | Cached CV results | SDG impact dashboard |
| 1 | Heatmap + scoring + nudges | Sarah + Marcus personas | Local + screenshots | Ethical guardrails page |

---

## Budget Summary

| Category | Person-Hours | Cost Estimate | Key Constraint |
|----------|-------------|---------------|----------------|
| Shared Infra | 13h | $0 | Days 1-2 only |
| Cat 2 (PhishGuard) | 100.5h | $5-13 | Feature sprawl discipline |
| Cat 3 (SmartMatch) | 146-176h | <$0.50 | Written deliverables scheduling |
| Cat 4 (SimResearch) | 40h | $0.50-2 | Compressed 5-day sprint |
| Cat 5 (CropSense) | 107.5h | $0-15 | From-scratch + Day 4 gate |
| Cat 1 (BalanceIQ) | 88.5h | $1-2 | Only with 5th person |
| **Total (4-person)** | **~407h** | **~$7-31** | |
| **Total (5-person)** | **~496h** | **~$8-33** | |

Available capacity (4 people x 14 days x 7.5h/day) = 420h. Budget fits with ~13h slack.
Available capacity (5 people x 14 days x 7.5h/day) = 525h. Budget fits with ~29h slack.

---

## Documents Generated by This Planning Process

| Document | Location | Purpose |
|----------|----------|---------|
| `STRATEGIC_REVIEW.md` | Root | PM/CTO consolidated assessment with revisions |
| `MASTER_SPRINT_PLAN.md` | Root (this file) | Cross-category orchestration |
| `Category 1/SPRINT_PLAN.md` | Cat 1 folder | BalanceIQ detailed sprints |
| `Category 2/SPRINT_PLAN.md` | Cat 2 folder | PhishGuard detailed sprints |
| `Category 3/docs/SPRINT_PLAN.md` | Cat 3 folder | SmartMatch dual-track sprints |
| `Category 4/docs/SPRINT_PLAN.md` | Cat 4 folder | SimResearch compressed 5-day plan |
| `Category 5/SPRINT_PLAN.md` | Cat 5 folder | CropSense detailed sprints |

---

*This plan assumes the team votes on primary categories before April 2. If the team decides to focus on fewer categories, redistribute hours from dropped categories to increase polish depth on remaining ones.*
