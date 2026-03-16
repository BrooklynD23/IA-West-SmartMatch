# Category 2 — PhishGuard AI: Sprint Plan

**Owner:** Person A (dedicated lead, full 2 weeks)
**Prep Window:** March 15 -- March 28, 2026 (14 days)
**Hackathon Date:** April 16, 2026
**Total Budget:** ~106 productive hours (14 days x 7.5 hrs avg; Days 1-2 shared with infra = ~4h/day for Cat 2)
**Tier:** 1 — Highest priority

---

## 1. Sprint Breakdown

---

### Sprint 0 — Foundation & Shared Infra (Days 1--2 | Mar 15--16 | ~8h Cat 2)

**Sprint Goal:** Validate all external APIs, establish shared infra, lock the micro-lesson content matrix and UI wireframes BEFORE any coding.

**Rationale:** Person A splits time with shared infra (LLM wrapper, Streamlit template, deployment config). Cat 2 work is research-only — no implementation code this sprint.

| # | Task | Est. Hours | Depends On | Deliverable |
|---|------|-----------|------------|-------------|
| 0.1 | Build shared LLM wrapper (OpenAI SDK, retry, error handling, response parsing) | 2.0 | — | `shared/llm_wrapper.py` usable by all categories |
| 0.2 | Build shared Streamlit template (header, sidebar, custom CSS base, color scheme) | 2.0 | — | `shared/streamlit_template/` fork-ready |
| 0.3 | Validate PhishTank API: register key, test 10 URLs, measure response time, document rate limits | 1.0 | — | API validation doc in `docs/api-validation.md` |
| 0.4 | Validate Google Safe Browsing API v4: obtain key, test 10 URLs, measure response time | 1.0 | — | Appended to `docs/api-validation.md` |
| 0.5 | Test OpenAI GPT-4o-mini classification prompt with 5 sample inputs, validate JSON output schema | 1.0 | 0.1 | Prompt v1 saved in `src/prompts/classify.txt` |
| 0.6 | Define micro-lesson content matrix: 6 threat types x (title, 2-sentence lesson, actionable tip) | 1.5 | — | `data/micro-lessons.json` — MUST be complete before coding |
| 0.7 | Create UI wireframes: all screens (input tabs, results, micro-lesson card, redaction toggle, settings) | 1.5 | — | `docs/wireframes.md` or sketches in `docs/wireframes/` |
| 0.8 | Draft 10+ demo scenario cards (input text, expected classification, expected reasons) | 1.0 | — | `data/demo-scenarios.json` |

**Sprint 0 Total: 11.0 hours** (4h Cat 2 on Day 1, 4h Cat 2 on Day 2, plus 3h shared infra counted once)

> Note: Tasks 0.1--0.2 are shared infra (counted as infra, not Cat 2). Effective Cat 2 budget: ~8h.

**Definition of Done:**
- All 3 APIs (OpenAI, PhishTank, Google Safe Browsing) validated with documented response times and rate limits
- Classification prompt returns valid JSON for 5/5 test inputs
- Micro-lesson content matrix has 6+ threat types fully written (not placeholders)
- UI wireframes reviewed and approved (even if hand-drawn)
- 10+ demo scenarios drafted with expected outputs

**Go/No-Go Gate:**
- GO if: All 3 APIs return valid responses within 10 seconds. Prompt produces structured JSON.
- NO-GO if: Any API is unavailable or rate-limited below 1 req/sec. Action: switch to cached/mock fallback and document the degradation plan.

---

### Sprint 1 — Core Classification Engine + Base UI (Days 3--6 | Mar 17--20 | ~30h)

**Sprint Goal:** Working end-to-end classification pipeline with a functional (not polished) Streamlit UI. A user can paste text or a URL and receive a risk verdict with reasons and an action checklist.

| # | Task | Est. Hours | Depends On | Deliverable |
|---|------|-----------|------------|-------------|
| 1.1 | Implement rule-based pre-filter engine: urgency word detection, domain mismatch regex, credential request patterns | 3.0 | — | `src/rules_engine.py` with unit tests |
| 1.2 | Implement LLM classification module: send input + prompt to GPT-4o-mini, parse JSON response (risk level, confidence, reasons, actions, micro-lesson) | 3.0 | 0.1, 0.5 | `src/llm_classifier.py` with unit tests |
| 1.3 | Implement URL reputation module: Google Safe Browsing lookup + PhishTank lookup, unified response | 2.5 | 0.3, 0.4 | `src/url_reputation.py` with unit tests |
| 1.4 | Implement tri-layer conflict resolution logic: rule-based + LLM + URL reputation arbitration per CTO spec | 2.5 | 1.1, 1.2, 1.3 | `src/classifier.py` (orchestrator) with unit tests |
| 1.5 | Build Streamlit UI: tabbed input (Text / URL / SMS), risk badge display (green/yellow/red), reason cards, action checklist | 4.0 | 0.2, 0.7 | `app.py` — functional UI |
| 1.6 | Wire classification pipeline to UI: input -> classify -> display results | 2.0 | 1.4, 1.5 | End-to-end functional prototype |
| 1.7 | Implement confidence score display with uncertainty messaging (< 80% threshold triggers "I'm not sure" language) | 1.5 | 1.2 | Confidence bar component in UI |
| 1.8 | Implement micro-lesson card display: load from content matrix, show contextual lesson based on threat type | 2.0 | 0.6, 1.5 | Micro-lesson UI component |
| 1.9 | Implement Visual Phishing Anatomy Highlighter: annotate input text with colored highlights on detected red flags (urgency words, suspicious URLs, credential asks) | 4.5 | 1.1, 1.2 | `src/anatomy_highlighter.py` + UI component |
| 1.10 | Write integration tests: 10 demo scenarios run through full pipeline, validate outputs | 2.5 | 1.6, 0.8 | `tests/test_integration.py` — all 10 pass |
| 1.11 | Add "Try This Example" clickable demo scenario cards to sidebar | 2.5 | 0.8, 1.6 | 10+ scenario cards in sidebar |

**Sprint 1 Total: 30.0 hours** (4 days x 7.5h)

**Definition of Done:**
- Paste any text/URL/SMS and get: risk label, confidence score, 3 reasons, action checklist, micro-lesson
- Visual Phishing Anatomy Highlighter shows colored annotations on flagged text segments
- Rule-based + LLM + URL reputation conflict resolution works correctly for all 10 test scenarios
- URL reputation hard-overrides LLM when URL is flagged (verified by test)
- Confidence < 80% shows uncertainty messaging (verified by test)
- All 10+ demo scenarios pass integration tests
- "Try This Example" cards work and populate the input field

**Go/No-Go Gate:**
- GO if: 10/10 demo scenarios produce correct risk labels. End-to-end response time < 12 seconds. No API errors.
- NO-GO trigger: If classification accuracy is < 80% on test scenarios, STOP new features and fix prompt engineering before proceeding.

---

### Sprint 2 — P0 Polish + P1 Features (Days 7--9 | Mar 21--23 | ~22.5h)

**Sprint Goal:** Complete all P0 features to 95% quality. Begin P1 features. Feature freeze at end of Day 9.

| # | Task | Est. Hours | Depends On | Deliverable |
|---|------|-----------|------------|-------------|
| 2.1 | UI polish pass #1: custom CSS, branded colors (ISACA-inspired), professional typography, consistent spacing, color-blind-safe palette (blue/orange supplements) | 3.5 | 1.5 | Polished `style.css` applied |
| 2.2 | Expand micro-lesson library to 8+ threat types with high-quality content (review and rewrite all lessons for 6th-grade reading level) | 2.0 | 0.6 | Updated `data/micro-lessons.json` |
| 2.3 | Add 2-3 more demo scenarios (total 12+), refine existing ones based on integration test results | 1.5 | 1.10 | Updated `data/demo-scenarios.json` |
| 2.4 | Anatomy Highlighter polish: improve color contrast, add tooltip explanations per highlight, ensure mobile-friendly rendering | 2.0 | 1.9 | Refined highlighter component |
| 2.5 | **P1: PII redaction toggle** — spaCy NER (en_core_web_sm) + regex for emails/phones/addresses, before/after preview UI | 3.5 | 1.6 | `src/pii_redactor.py` + toggle in UI |
| 2.6 | **P1: Spanish language toggle** — LLM re-generates explanation, reasons, actions, and micro-lesson in Spanish | 2.5 | 1.2 | Language toggle in settings/sidebar |
| 2.7 | **P1: Live Judge Challenge Mode** — timer UI (60s countdown), judge pastes their own input, result appears with timer display, "challenge accepted" animation | 3.0 | 1.6 | Challenge mode tab/button in UI |
| 2.8 | **P1: Report export** — generate downloadable text/PDF summary of analysis results | 2.5 | 1.6 | Download button in results panel |
| 2.9 | **P1: Screenshot OCR** — GPT-4o Vision integration for image upload, extract text, run through classifier (keep in code, CUT from demo flow) | 2.0 | 1.2 | `src/ocr_pipeline.py` + file upload UI (hidden from demo nav) |

**Sprint 2 Total: 22.5 hours** (3 days x 7.5h)

**FEATURE FREEZE: End of Day 9 (March 23).** No new features after this point. Only bug fixes, polish, and demo prep.

**Definition of Done:**
- All 8 P0 features at 95% quality — no visual bugs, no broken flows
- UI looks professional and branded (not default Streamlit gray)
- PII redaction toggle works with before/after preview
- Spanish toggle produces readable, accurate Spanish output
- Live Judge Challenge Mode has working timer and accepts arbitrary input
- Report export generates a clean, downloadable summary
- Screenshot OCR works in code but is NOT in the demo navigation flow
- 12+ demo scenarios all pass

**Go/No-Go Gate:**
- GO if: All 8 P0 features work end-to-end without errors. UI passes visual inspection (no layout breaks, readable text, correct colors).
- SCOPE CUT trigger: If any P0 feature is below 90% quality at end of Day 8, cut the lowest-priority P1 feature to reallocate time. See Risk Gates (Section 3) for cut order.

---

### Sprint 3 — Demo Prep, Testing & Hardening (Days 10--14 | Mar 24--28 | ~37.5h)

**Sprint Goal:** Lock the demo flow, rehearse, harden for live performance, prepare backup plan, finalize submission materials.

| # | Task | Est. Hours | Depends On | Deliverable |
|---|------|-----------|------------|-------------|
| 3.1 | End-to-end QA: run all 12+ demo scenarios across all input types, fix any failures | 3.0 | Sprint 2 | QA report, all scenarios green |
| 3.2 | Edge case testing: empty input, extremely long input (10K chars), non-English input, URLs with redirects, Unicode edge cases, malformed URLs | 2.5 | 1.6 | Edge case test suite, graceful error handling confirmed |
| 3.3 | Response caching for demo scenarios: pre-compute and cache all 12+ demo scenario results locally so demo works without live API | 2.5 | 3.1 | `data/cached-responses.json` |
| 3.4 | Demo flow script v1: write the exact 5-minute narrative (Maria story), mark which features to show, which buttons to click, in what order | 2.0 | 3.1 | `docs/demo-script.md` |
| 3.5 | Demo rehearsal #1: run through full demo, time it, note stumbles | 1.5 | 3.4 | Rehearsal notes with timestamps |
| 3.6 | Fix issues from rehearsal #1 (UI timing, transitions, layout issues under demo conditions) | 2.0 | 3.5 | Bug fixes committed |
| 3.7 | Demo rehearsal #2: run again with fixes, verify under 5 minutes | 1.0 | 3.6 | Confirmed < 5 min, smooth flow |
| 3.8 | Record backup demo video: screen capture of full demo flow in case live API fails on demo day | 2.0 | 3.7 | `docs/backup-demo.mp4` |
| 3.9 | Security review: verify no user inputs stored, PII redaction works correctly, no phishing crafting instructions leak, adversarial prompt testing (5 attack prompts) | 2.5 | 3.1 | Security checklist signed off |
| 3.10 | Streamlit Cloud deployment: deploy to Streamlit Community Cloud, verify 1GB resource limit not exceeded, test live URL | 2.0 | 3.1 | Live deployment URL working |
| 3.11 | Load testing on Streamlit Cloud: 10 rapid sequential requests, verify no crashes or timeouts | 1.0 | 3.10 | Load test results documented |
| 3.12 | UI polish pass #2: final visual review, fix any spacing/alignment/color issues, verify color-blind-safe palette | 2.0 | 3.6 | Final UI sign-off |
| 3.13 | Demo rehearsal #3 (on deployed version): full run on Streamlit Cloud, verify live environment matches local | 1.5 | 3.10, 3.12 | Live rehearsal confirmed |
| 3.14 | Responsible AI documentation: finalize checklist, write the "About this tool" page in the app (privacy statement, limitations, framework references) | 2.0 | — | In-app responsible AI page |
| 3.15 | Submission materials: README with setup instructions, screenshots, architecture diagram, team attribution | 2.5 | 3.12 | Complete README.md |
| 3.16 | Presentation slides: 5-7 slides (problem, solution, live demo placeholder, impact, responsible AI, next steps) | 3.0 | 3.4 | Slide deck ready |
| 3.17 | Demo rehearsal #4 (full dress): slides + live demo + backup video tested, with timer | 1.5 | 3.16, 3.13 | Final dress rehearsal complete |
| 3.18 | Final bug fix buffer | 2.5 | — | Any last-minute fixes |
| 3.19 | Prepare "judge challenge" talking points: have answers ready for "what if someone pastes X?", "how do you handle Y?" | 1.5 | 3.9 | Q&A prep doc |

**Sprint 3 Total: 37.0 hours** (5 days x 7.5h = 37.5h, with 0.5h buffer)

**Definition of Done:**
- All demo scenarios work on deployed Streamlit Cloud instance
- 5-minute demo rehearsed 4+ times, confirmed under 5 minutes
- Backup demo video recorded and tested
- Response cache populated for all demo scenarios (offline fallback)
- Security checklist complete — no data storage, redaction works, no adversarial leaks
- Submission materials (README, slides, responsible AI page) complete
- Q&A prep document ready for judge questions

**Go/No-Go Gate:**
- GO if: Deployed app works. 4 rehearsals complete. Backup video ready. Under 5 minutes.
- EMERGENCY protocol: If Streamlit Cloud fails on Day 13+, fall back to local demo with screen share. Backup video covers worst case.

---

## 2. Milestone Checkpoints

| Milestone | Date | Day | Specific Deliverables | Verification |
|-----------|------|-----|----------------------|--------------|
| **M0: APIs Validated** | Mar 16 | 2 | PhishTank, Google Safe Browsing, OpenAI APIs all return valid responses. Response times documented. | Run validation script, all 3 APIs green |
| **M1: Content Matrix Locked** | Mar 16 | 2 | Micro-lesson matrix (6+ types), demo scenarios (10+), UI wireframes complete | Review content files, no TODOs or placeholders |
| **M2: Core Engine Working** | Mar 18 | 4 | Tri-layer classification returns correct results for 5/5 basic test cases | `pytest tests/` — all pass |
| **M3: End-to-End Prototype** | Mar 20 | 6 | User can paste text, see risk label + reasons + actions + micro-lesson + confidence | Manual walkthrough of 3 scenarios in browser |
| **M4: Anatomy Highlighter Live** | Mar 20 | 6 | Visual highlighting of phishing indicators in input text | Demo with 2 phishing samples showing colored annotations |
| **M5: P0 Complete** | Mar 22 | 8 | All 8 P0 features working at 90%+ quality | Run all 12+ integration tests, visual inspection |
| **M6: Feature Freeze** | Mar 23 | 9 | All P1 features either shipped or explicitly cut. No new feature work after this point. | Feature checklist signed off |
| **M7: Demo Script Locked** | Mar 25 | 11 | 5-minute demo script finalized, first rehearsal complete | Timed rehearsal < 5 min |
| **M8: Deployed & Tested** | Mar 27 | 13 | Live on Streamlit Cloud, load-tested, security-reviewed | Access live URL, run 10 test queries |
| **M9: Submission Ready** | Mar 28 | 14 | All materials (slides, README, backup video, Q&A prep) complete | Checklist complete, 4th rehearsal done |

---

## 3. Risk Gates

### Scope Cut Triggers

| Trigger | When | Action |
|---------|------|--------|
| Any P0 feature below 90% quality | End of Day 8 | Cut lowest-priority P1 feature, reallocate hours to P0 fix |
| End-to-end response time > 15 seconds | Any time | Optimize: reduce prompt length, add caching, parallelize API calls |
| Classification accuracy < 80% on test scenarios | End of Day 6 | STOP all new features. Fix prompt engineering and conflict resolution. |
| API downtime (any external API) | Any time | Switch to cached/mock responses. Document degradation. |
| Streamlit Cloud resource limit hit | Day 13+ | Remove spaCy (use regex-only PII redaction), reduce dependencies |
| Person A capacity reduced (illness, other obligation) | Any time | Immediately cut all P1 features. Focus P0-only with reduced scope. |

### P1 Feature Cut Order (first cut = least demo impact)

If time runs short, cut P1 features in this order:

| Cut Order | Feature | Hours Saved | Demo Impact | Rationale |
|-----------|---------|-------------|-------------|-----------|
| 1st cut | Screenshot OCR (P1.5) | 2.0h | None (already cut from demo flow per mandate) | Already excluded from demo. Keep in code only. |
| 2nd cut | Report export (P1.4) | 2.5h | Low | Nice but not a demo highlight. Judges won't miss it. |
| 3rd cut | Spanish toggle (P1.2) | 2.5h | Medium | Strong ISACA alignment but not core. Cut only if desperate. |
| 4th cut | PII redaction (P1.1) | 3.5h | Medium-High | Live redaction is a strong demo moment. Protect if possible. |
| 5th cut (LAST RESORT) | Live Judge Challenge Mode (P1.3) | 3.0h | High | Interactive judge engagement is a differentiator. Protect strongly. |

**Never cut:** Any P0 feature. The 8 P0 features are non-negotiable.

---

## 4. Demo Readiness Checklist

### Working Features (must verify on deployed instance)

- [ ] **Text/URL/SMS tabbed input** — all 3 tabs work, input clears between analyses
- [ ] **Tri-layer classification** — rule-based + LLM + URL reputation produces correct verdict
- [ ] **Top 3 reasons with visual highlighting** — Phishing Anatomy Highlighter shows colored annotations inline
- [ ] **Action checklist** — contextual actions per threat type (don't click, verify, report)
- [ ] **Micro-lessons** — correct lesson displays for detected threat type, 6th-grade reading level
- [ ] **Confidence score + uncertainty** — percentage displayed, < 80% triggers "verify safely" messaging
- [ ] **10+ demo scenario cards** — clickable sidebar cards populate input and run classification
- [ ] **Polished, branded UI** — custom CSS, ISACA-inspired colors, professional typography, no default Streamlit gray

### P1 Features (verify if shipped)

- [ ] PII redaction toggle with before/after preview
- [ ] Spanish language toggle
- [ ] Live Judge Challenge Mode with timer
- [ ] Report export (PDF/text download)
- [ ] Screenshot OCR (works in code but NOT shown in demo)

### Rehearsed Demo Flow (5 minutes)

```
0:00 - 0:30  PROBLEM (slide): "16% of breaches start with phishing.
              The median time to fall for it? Under 60 seconds."
0:30 - 1:00  SOLUTION (slide): "PhishGuard AI: classify AND educate.
              Tri-layer analysis in under 10 seconds."
1:00 - 1:15  SWITCH TO LIVE APP
1:15 - 2:00  MARIA MOMENT: Paste Netflix suspension SMS.
              Show: red badge, 3 reasons, anatomy highlights,
              action checklist, micro-lesson.
2:00 - 2:30  CONTRAST: Paste legitimate newsletter.
              Show: green badge, "Safe" with confidence, reasons why safe.
2:30 - 3:00  PII REDACTION: Toggle on, show before/after.
              "Maria's phone number never reaches the AI."
3:00 - 3:15  SPANISH TOGGLE: Same analysis in Spanish.
              "Maria's first language."
3:15 - 3:45  JUDGE CHALLENGE: "Want to try your own? Paste anything."
              (Have backup scenario ready if judge declines.)
3:45 - 4:15  IMPACT (slide): "Deploy at CPP — 30,000 students protected.
              NIST framework alignment. Zero data storage."
4:15 - 4:45  RESPONSIBLE AI (slide): Privacy-by-design, explainability,
              uncertainty signaling, no phishing instruction generation.
4:45 - 5:00  CLOSE: "PhishGuard AI: don't just detect — educate."
```

### Backup Plan

| Failure Mode | Backup |
|-------------|--------|
| OpenAI API down during demo | Pre-cached responses for all 12+ scenarios. Demo runs from cache with "(cached)" indicator hidden. |
| Streamlit Cloud down | Run locally on laptop with `streamlit run app.py`. Screen share. |
| Internet completely down | Play backup demo video (recorded Day 12). |
| PhishTank/Google Safe Browsing down | Graceful degradation — LLM + rules still classify. Show "(URL reputation unavailable)" note. |
| Judge asks about a scenario not in the 12+ | LLM handles arbitrary input. Confidence + uncertainty messaging covers edge cases. |

---

## 5. Critical Path

The critical path is the longest chain of dependent tasks with zero slack. Any delay on these tasks delays the entire project.

```
0.5 Prompt Engineering
  |
  v
1.2 LLM Classification Module ──> 1.4 Conflict Resolution ──> 1.6 Wire Pipeline to UI
  |                                       |                           |
  |                                       v                           v
  |                                 1.10 Integration Tests      Sprint 2 Features
  |                                       |
  |                                       v
  |                                 3.1 End-to-End QA
  |                                       |
  |                                       v
  |                                 3.3 Response Caching
  |                                       |
  |                                       v
  |                                 3.4 Demo Script
  |                                       |
  |                                       v
  |                                 3.5 Rehearsal #1 ──> 3.6 Fix ──> 3.7 Rehearsal #2
  |                                                                        |
  v                                                                        v
1.9 Anatomy Highlighter ──────────────────────────────────────> 2.4 Highlighter Polish
```

### Critical Path Tasks (zero slack)

| Task | Day | Hours | Why Critical |
|------|-----|-------|-------------|
| 0.5 Classification prompt validation | 2 | 1.0 | Everything downstream depends on working LLM output |
| 1.2 LLM classification module | 3--4 | 3.0 | Core engine — all features build on this |
| 1.4 Tri-layer conflict resolution | 4--5 | 2.5 | The "intelligence" of the system — directly demo'd |
| 1.6 Wire pipeline to UI | 5--6 | 2.0 | Without this, nothing is visible |
| 1.9 Visual Anatomy Highlighter | 5--6 | 4.5 | New feature per mandate, high demo impact, complex UI work |
| 1.10 Integration tests (all 10 scenarios) | 6 | 2.5 | Gates Sprint 2 go/no-go |
| 3.1 End-to-end QA | 10 | 3.0 | Gates demo prep |
| 3.4 Demo script | 11 | 2.0 | Gates rehearsals |
| 3.5 Rehearsal #1 | 11 | 1.5 | Must start Day 11 per mandate |
| 3.10 Streamlit Cloud deployment | 12--13 | 2.0 | Must verify live environment before final rehearsals |

**Total critical path length: ~24 hours across 14 days.** Slack exists primarily in Sprint 2 (P1 features can be cut) and Sprint 3 (buffer time on Days 13-14).

---

## 6. P0/P1 Decision Points

### P0 Features — No Decision Needed (Must Ship)

All 8 P0 features are non-negotiable. They are built in Sprints 1--2 and polished in Sprint 3.

| P0 Feature | Sprint | Built By (Day) | 95% Quality By (Day) |
|-----------|--------|----------------|----------------------|
| Text/URL/SMS tabbed input | Sprint 1 | Day 5 | Day 8 |
| Tri-layer classification | Sprint 1 | Day 5 | Day 8 |
| Top 3 reasons + anatomy highlighter | Sprint 1 | Day 6 | Day 9 |
| Action checklist per threat type | Sprint 1 | Day 5 | Day 8 |
| Micro-lessons (6+ types) | Sprint 1 | Day 6 | Day 9 |
| Confidence score + uncertainty | Sprint 1 | Day 5 | Day 8 |
| 10+ demo scenario cards | Sprint 1 | Day 6 | Day 9 |
| Polished, branded UI (custom CSS) | Sprint 2 | Day 8 | Day 12 |

### P1 Features — Go/No-Go Decision Schedule

Each P1 feature has a specific decision point. The decision is binary: **GO** (build it) or **CUT** (skip it, reallocate hours).

| P1 Feature | Decision Point | Decision Criteria | Hours at Risk |
|-----------|---------------|-------------------|---------------|
| **Screenshot OCR** | Day 7 (start of Sprint 2) | GO if: All P0 features on track. Person A has bandwidth. OCR kept in code only (not demo). CUT if: Any P0 behind schedule. | 2.0h |
| **PII Redaction Toggle** | Day 7 (start of Sprint 2) | GO if: Sprint 1 integration tests all pass. spaCy loads within Streamlit Cloud resource limits. CUT if: Streamlit Cloud memory issues with spaCy, or P0 behind schedule. | 3.5h |
| **Spanish Language Toggle** | Day 7 (start of Sprint 2) | GO if: LLM prompt produces quality Spanish in testing. No P0 debt. CUT if: Spanish output quality is poor (requires too much prompt iteration), or P0 behind. | 2.5h |
| **Live Judge Challenge Mode** | Day 8 (mid Sprint 2) | GO if: All P0 features at 90%+ quality. Core UI stable enough to add a new interaction mode. CUT if: Any P0 feature below 85% quality. UI instability. | 3.0h |
| **Report Export** | Day 8 (mid Sprint 2) | GO if: All other P1 features shipped. Remaining hours > 4. CUT if: Time pressure. This is lowest demo-impact P1. | 2.5h |

### Decision Flowchart (Day 7 Morning)

```
Are all 10 integration tests passing?
  |
  YES ──> Are all P0 features on track for Day 8 completion?
  |         |
  |         YES ──> BUILD all P1 features (Days 7-9)
  |         |
  |         NO ──> How many P0 features are behind?
  |                   |
  |                   1-2 behind ──> Cut Screenshot OCR + Report Export.
  |                   |               Build PII + Spanish + Challenge Mode.
  |                   |
  |                   3+ behind ──> Cut ALL P1 features.
  |                                 Dedicate Days 7-9 to P0 completion.
  |
  NO ──> STOP. Fix integration test failures.
         Re-evaluate P1 on Day 8.
```

### Decision Flowchart (Day 8 Evening — Final P1 Call)

```
Are all P0 features at 90%+ quality?
  |
  YES ──> Ship all remaining P1 features by Day 9 EOD.
  |
  NO ──> Which P0 features are below 90%?
           |
           Fix those P0 features.
           Cut P1 features in order (Section 3 cut order)
           until enough hours are freed.
```

---

## Hour Budget Summary

| Sprint | Days | Available Hours | Allocated Hours | Buffer |
|--------|------|----------------|-----------------|--------|
| Sprint 0 | 1--2 | ~8h (Cat 2) + 4h infra | 11.0h (8h Cat 2 + 3h infra) | 1.0h |
| Sprint 1 | 3--6 | 30.0h | 30.0h | 0h (tight) |
| Sprint 2 | 7--9 | 22.5h | 22.5h | 0h (P1 cuts create buffer) |
| Sprint 3 | 10--14 | 37.5h | 37.0h | 0.5h + flex from cut P1 |
| **Total** | **1--14** | **~98--102h** | **~100.5h** | **~1.5h base + P1 cut buffer** |

> The budget is tight by design. The P1 cut order (Section 3) is the pressure release valve. Cutting Screenshot OCR (2h) + Report Export (2.5h) frees 4.5 hours — enough to absorb most schedule slips.

---

## Appendix: Micro-Lesson Content Matrix (Pre-Coding Requirement)

This matrix MUST be completed in Sprint 0, Day 2, before any coding begins.

| # | Threat Type | Lesson Title | 2-Sentence Lesson | Actionable Tip |
|---|------------|-------------|-------------------|----------------|
| 1 | Phishing (email) | "Spot the Fake Sender" | TBD — write in Sprint 0 | TBD |
| 2 | Smishing (SMS) | "Why Texts Feel Urgent" | TBD | TBD |
| 3 | Credential Harvesting | "Your Password Is the Prize" | TBD | TBD |
| 4 | Gift Card Scam | "No Real Company Asks for Gift Cards" | TBD | TBD |
| 5 | Fake Shipping Notification | "Track It Yourself" | TBD | TBD |
| 6 | Social Media Impersonation | "When Your Friend Isn't Your Friend" | TBD | TBD |
| 7 | Tech Support Scam | "Microsoft Will Never Cold-Call You" | TBD | TBD |
| 8 | Job Scam | "If the Pay Is Too Good..." | TBD | TBD |

> Content must be written at a 6th-grade reading level. Each lesson must be 2 sentences max. Each tip must be a single concrete action.

---

## Appendix: Demo Scenario Template

Each of the 12+ demo scenarios must follow this format (completed in Sprint 0):

```json
{
  "id": "scenario-01",
  "title": "Netflix Suspension SMS (Maria)",
  "input_type": "sms",
  "input_text": "NETFLIX: Your account will be suspended in 24hrs. Verify your payment at http://netf1ix-verify.com/update",
  "expected_risk": "High Risk",
  "expected_reasons": [
    "Urgency language ('24hrs', 'suspended')",
    "Mismatched domain (netf1ix-verify.com is not netflix.com)",
    "Credential/payment request"
  ],
  "expected_threat_type": "smishing",
  "demo_order": 1,
  "notes": "The 'Maria Moment' — opening demo scenario"
}
```
