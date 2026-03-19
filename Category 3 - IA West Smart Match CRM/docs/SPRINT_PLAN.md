---
doc_role: canonical
authority_scope:
- category.3.execution_plan
canonical_upstreams:
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-17'
managed_by: repo-governance
---

# Category 3 — IA SmartMatch CRM: Sprint Plan (Dual-Track)

> **Governance notice (repo-governance):** This document owns category execution decisions for this track. Portfolio schedule, ranking, and conflict-resolution context must follow: `archived/general_project_docs/MASTER_SPRINT_PLAN.md`, `archived/general_project_docs/STRATEGIC_REVIEW.md`.

**Prep Window:** March 15 - April 15, 2026 (14 working days before April 16 hackathon)
**Track A (Person B):** Code — Days 1-14 (~100-112 hours, ~7-8h/day)
**Track B (Person C):** Writing — Days 6-14 (~54-72 hours, ~6-8h/day)
**Feature Freeze:** Day 9 (hard cutoff for new code features)
**Total Budget:** ~154-184 person-hours

**Provider Decision Update (March 18, 2026):** New provider work should target the Gemini Developer API rather than OpenAI. Use `gemini-embedding-001` for embeddings and `gemini-2.5-flash-lite` for text generation tasks unless a stronger model is explicitly required. See `Category 3 - IA West Smart Match CRM/docs/gemini_provider_decision_2026-03-18.md` for the rationale and migration notes.

---

## 1. Sprint Breakdown (Dual-Track)

### Sprint 0: Foundation (Day 1-2) — "Data In, Signals Out"

**Track A (Person B) — 14-16h**

| Task | Hours | Description |
|------|-------|-------------|
| A0.1 Environment setup | 1.5 | Python 3.10+ venv, install deps (streamlit, Gemini SDK or Gemini OpenAI-compat client, pandas, plotly, beautifulsoup4, playwright), configure `.env` with `GEMINI_API_KEY`, scaffold project structure under `src/` |
| A0.2 Data ingestion + quality audit | 3.0 | Load all 4 CSVs into Pandas. Document: column names, dtypes, missing values, encoding issues. Produce `data_quality_report.md` with row counts (18 speakers, 15 events, 35 courses, 9 calendar entries = 77 total). Flag any join keys that don't align. |
| A0.3 Embedding pipeline — speakers | 2.5 | Generate `gemini-embedding-001` vectors for all 18 speaker profiles, using `output_dimensionality=1536` to preserve the current matrix shape. Compose embedding text from: `f"{expertise_tags} {title} {company} {board_role}"`. Cache embeddings as `.npy` or `.pkl` to avoid re-calling API. |
| A0.4 Embedding pipeline — events + courses | 2.5 | Generate `gemini-embedding-001` vectors for 15 CPP events and 35 course sections, using `output_dimensionality=1536` to preserve the current matrix shape. Compose event embedding text from: `f"{event_name} {category} {volunteer_roles} {primary_audience}"`. For courses: `f"{title} {guest_lecture_fit}"`. Cache results. |
| A0.5 Cosine similarity validation | 2.0 | Compute speaker-event cosine similarity matrix (18x15=270 pairs). Manually inspect top-5 and bottom-5 matches for sanity. Compare embedding results vs. keyword overlap — document which produces better rankings on 5 known-good matches. |
| A0.6 Streamlit skeleton | 2.5 | 3-tab layout: Matches / Discovery / Pipeline. Sidebar with IA West branding. Load data, display raw tables. Verify deployment to Streamlit Community Cloud works with test data. |
| A0.7 Research: Growth Strategy data points | 1.0 | While exploring data, note: geographic distribution of speakers, event categories, course-fit distribution (High/Medium/Low), IA event calendar coverage. These feed Track B's Growth Strategy. Write findings to `.memory/context/cat3-data-insights.md`. |

**Track B (Person C) — NOT YET ACTIVE (Day 1-5 is Person B solo)**

*Person B captures raw data insights for Person C's use starting Day 6.*

**Sprint 0 Definition of Done:**
- [ ] All 4 CSVs load without errors, data quality report complete
- [ ] 68 embedding vectors generated and cached locally; 9 calendar rows loaded for `calendar_fit`
- [ ] Cosine similarity produces sensible speaker-event rankings (validated on 5+ known pairs)
- [ ] Streamlit app runs locally with 3 empty tabs + data tables
- [ ] Data insights memo saved for Track B handoff

**Go/No-Go Gate (End of Day 2):**
- PASS: Embeddings produce meaningfully different match scores (top match score > bottom match score by 0.15+). Proceed to Sprint 1.
- FAIL: Embeddings produce flat/random scores. Pivot to TF-IDF + keyword overlap for matching. Budget: 2h to implement alternative. No schedule slip — Sprint 1 starts Day 3 regardless.

---

### Sprint 1: Matching Engine Core (Day 3-5) — "The Brain"

**Track A (Person B) — 21-24h**

| Task | Hours | Description |
|------|-------|-------------|
| A1.1 MATCH_SCORE formula implementation | 4.0 | Implement 6-factor weighted scoring: `topic_relevance` (w1=0.30, cosine similarity), `role_fit` (w2=0.25, exact/fuzzy match of speaker roles to event volunteer roles), `geographic_proximity` (w3=0.20, metro-region distance lookup table), `calendar_fit` (w4=0.15, date overlap scoring using IA event calendar), `historical_conversion` (w5=0.05, default=0.5 for all, tunable), `student_interest` (w6=0.05, event category weight map). Return: composite score + per-factor breakdown. |
| A1.2 Match ranking engine | 2.5 | For each event, rank all 18 speakers by MATCH_SCORE. Return top-3 with score breakdowns. For each course section, rank speakers similarly. Build match result data structure: `{event_id, speaker_id, total_score, factor_scores: {topic_relevance: X, role_fit: Y, geographic_proximity: Z, ...}, weighted_factor_scores: {...}}`. |
| A1.3 Match explanation cards (LLM) | 3.0 | `gemini-2.5-flash-lite` prompt: given speaker profile + event details + score breakdown, generate 2-3 sentence natural language explanation. Example: "Travis Miller (SVP Sales, Ventura) is recommended for the UCLA Data Analytics Hackathon because his MR technology expertise closely aligns with the event's data science focus (Topic: 0.85), and Ventura is within commuting distance (Proximity: 0.90)." Cache generated explanations. |
| A1.4 Matches tab — UI build | 5.0 | Event selector dropdown. Top-3 speaker cards per event with: photo placeholder, name, title, company, match score (large number), 6-factor radar chart (Plotly), natural language explanation card, "Generate Email" button. Weight-tuning sliders in sidebar (6 sliders, real-time score recomputation). |
| A1.5 Course matching integration | 2.5 | Extend matching engine to course schedule data. Filter by `guest_lecture_fit == "High"` (10 sections). Show top-3 speaker matches per high-fit course. Display in a sub-tab or collapsible section within Matches tab. |
| A1.6 Real-data pipeline funnel — initial | 2.0 | Using the ACTUAL match results from A1.2, create a simple dataset of match outcomes: 270 speaker-event pairs scored, top-3 per event selected (45 "Matched" entries), simulate downstream stages (Contacted/Confirmed/Attended/Member Inquiry) using realistic conversion rates from real nonprofit data. This feeds both Pipeline tab and Track B's Growth Strategy. Save as `pipeline_sample_data.csv`. |
| A1.7 University scraping research | 2.0 | Test-scrape all 5 target university event pages (UCLA, SDSU, UC Davis, USC, Portland State). Document: which load via static HTML (BeautifulSoup sufficient) vs. which require JS rendering (Playwright needed). Note page structure, CSS selectors, and robots.txt compliance. Save scraping notes. |

**Track B (Person C) — NOT YET ACTIVE**

**Sprint 1 Definition of Done:**
- [ ] MATCH_SCORE computes correctly for all 270 speaker-event pairs
- [ ] Top-3 matches per event displayed with radar charts and explanation cards
- [ ] Weight sliders recompute rankings in real time
- [ ] Course matching works for 10 high-fit sections
- [ ] Pipeline sample data generated from real match outputs
- [ ] Scraping feasibility confirmed for 5 universities

**Go/No-Go Gate (End of Day 5):**
- PASS: Matching engine produces explainable, sensible top-3 per event. Weight sliders visibly change rankings. At least 3/5 university scrape targets confirmed viable. Proceed to Sprint 2.
- FAIL on matching: Debug scoring formula. Use Day 6 morning (2h) to fix. Non-negotiable — matching engine IS the MVP.
- FAIL on scraping: Reduce to 3 universities. Use pre-cached HTML as primary, live scrape as demo enhancement.

---

### Sprint 2: Discovery + Email + Track B Kickoff (Day 6-8) — "The Reach"

**Track A (Person B) — 21-24h**

| Task | Hours | Description |
|------|-------|-------------|
| A2.1 Web scraping pipeline — core | 5.0 | Build modular scraper: `scrape_university(url, method="bs4"|"playwright") -> {html, scraped_at, url, method, source, ttl_hours, robots_ok}`. Implement for all 5 universities. Add hashed JSON cache under `cache/scrapes/<sha256(url)>.json`. Respect robots.txt. Rate limit: 1 request per 5 seconds. Reject non-public custom URLs that are not `http/https`, that resolve to localhost/private networks, or that fall outside demo-approved university domains. |
| A2.2 LLM extraction pipeline | 4.0 | `gemini-2.5-flash-lite` prompt: given raw HTML/text, extract structured JSON array of events: `{event_name, category, date_or_recurrence, volunteer_roles, primary_audience, contact_name, contact_email, url}`. Few-shot examples in prompt. Parse and validate JSON output. Handle extraction failures gracefully (return empty + log). |
| A2.3 Discovery tab — UI | 3.5 | University selector (5 pre-loaded + "Custom URL" input). "Discover Events" button triggers scrape + extract. Results table showing extracted events with "Add to Matching" button. Status indicators: "Cached" vs. "Live Scrape" vs. "Failed — Using Cached". Show scrape timestamp. For Custom URL, validate `http/https` only, deny localhost/private-network/file URLs, and restrict demo scope to public university hosts. |
| A2.4 Outreach email generation | 3.0 | `gemini-2.5-flash-lite` prompt: given speaker profile + event details + match score breakdown, generate personalized outreach email. Include: subject line, greeting referencing speaker's specific expertise, event details, value proposition for volunteering, call-to-action. Add "Copy to Clipboard" button. Email preview panel in Matches tab. |
| A2.5 Calendar invite preview (.ics) | 1.5 | Generate downloadable .ics file for matched events. Fields: event name, date/time (from event data or IA calendar), location, description (auto-generated summary of the match + event). Download button next to email preview. |
| A2.6 Pipeline funnel — real data integration | 2.0 | Connect pipeline data from A1.6 to Plotly funnel chart. Stages: Discovered (raw count of all events across 5 universities + CPP data) -> Matched (top-3 per event) -> Contacted (simulated at 80% of matched) -> Confirmed (simulated at 45% of contacted) -> Attended (simulated at 75% of confirmed) -> Member Inquiry (simulated at 15% of attended). Use ACTUAL event/speaker names from real data in the funnel hover tooltips. |
| A2.7 Handoff data package for Track B | 1.0 | Compile and document for Person C: (1) match results summary with real speaker-event pairings, (2) pipeline funnel numbers with real data, (3) university coverage map data (which metros, which universities, speaker proximity), (4) ROI calculation inputs: volunteer hours per event, events per quarter, membership LTV estimate. Save as `track_b_data_package.md`. |

**Track B (Person C) — STARTS DAY 6 — 18-24h this sprint**

| Task | Hours | Description |
|------|-------|-------------|
| B2.1 Growth Strategy — research phase | 4.0 | Read challenge brief (`IA_West_Smart_Match_Challenge.docx`), sponsor intro deck, all 4 CSVs, Track B data package from Person B. Research: IA West membership value proposition (website), university engagement program benchmarks (SSIR, CASE), professional association membership funnels (ASAE data). |
| B2.2 Growth Strategy — outline + Section 1 draft | 4.0 | Draft detailed outline (see Section 4 below). Write Section 1: Executive Summary + Problem Statement. Write Section 2: Target Audience Segments (board members/volunteers, university program coordinators, students/young professionals, IA West chapter leadership). Use real speaker data to illustrate segments. |
| B2.3 Growth Strategy — Section 3 draft | 3.0 | Write Section 3: Rollout Plan. Phase 1: CPP (current data, 15 events + 35 courses). Phase 2: LA Metro expansion (UCLA, USC — closest to existing speaker base in LA West, Ventura). Phase 3: West Coast corridor (SDSU, UC Davis, Portland State). Include board-member-to-campus expansion map: which speakers are geographically positioned to serve which universities. |
| B2.4 Measurement Plan — draft | 3.0 | Write Measurement Plan (1 page). KPIs: match acceptance rate (target: 60%+), email response rate (target: 25%+), event attendance rate (target: 70%+ of confirmed), membership conversion rate (target: 10-15% of engaged students within 12 months), volunteer utilization rate (target: each board member matched 2+ times/quarter). Proposed A/B test: randomize match weight configurations across events and measure acceptance rates. |
| B2.5 ROI quantification — initial | 2.0 | Calculate: volunteer hours saved per match cycle (manual: ~3h research + 1h email drafting + 0.5h coordination = 4.5h; SmartMatch: <5 min = 0.08h; savings: 4.42h/match). At ~45 matches/quarter = ~199h saved/quarter = ~$9,950/quarter at $50/h volunteer opportunity cost. Membership LTV: estimate annual dues x avg retention years. |
| B2.6 Responsible AI Note — draft | 2.0 | Write half-page Responsible AI Note. Sections: Privacy (public data only, no student PII, aggregate pipeline metrics), Bias (geographic over-matching mitigation, expertise-tag balance audit, diversity flag), Transparency (score breakdown + explanation cards + weight sliders), Data Handling (consent for speaker profiles, publicly scraped university data only, cache-and-delete policy). |

**Sprint 2 Definition of Done:**

Track A:
- [ ] Web scraping works for 5 universities with cached fallback
- [ ] LLM extraction produces valid structured JSON for 80%+ of scraped pages
- [ ] Discovery tab shows scraped events with "Add to Matching" button
- [ ] Outreach emails generate correctly for any top match
- [ ] Calendar .ics file downloads correctly
- [ ] Pipeline funnel displays with real data labels
- [ ] Track B data package delivered

Track B:
- [ ] Growth Strategy outline complete, Sections 1-3 drafted (~60% of document)
- [ ] Measurement Plan first draft complete
- [ ] ROI quantification draft with specific numbers
- [ ] Responsible AI Note first draft complete

**Go/No-Go Gate (End of Day 8):**
- PASS on Track A: Live scrape of at least 1 university works during demo. Cached scrapes available for all 5. Email generation produces quality output. Proceed to Sprint 3 polish.
- PASS on Track B: Growth Strategy is 60%+ drafted with real data integrated. Proceed to Sprint 3 for completion and polish.
- FAIL on scraping: Reduce to 3 cached universities + 1 live demo target. No new scraping features after Day 8.
- FAIL on writing: Reallocate Person B's Day 9-10 evenings (2h/day) to support writing with data/screenshots.

---

### Sprint 3: Polish, Integration, Feature Freeze (Day 9-10) — "Lock and Load"

**FEATURE FREEZE: END OF DAY 9.** No new features after Day 9. Day 10 is integration + bug fixes only.

**Track A (Person B) — 14-16h**

| Task | Hours | Description |
|------|-------|-------------|
| A3.1 Board-to-campus expansion map | 3.0 | Plotly map visualization: plot speaker metro locations (Ventura, LA West, SF, LA Long Beach, Portland, San Diego, Seattle) and university locations. Draw connection lines showing which speakers can serve which campuses (based on geographic_proximity scores). Color-code by speaker expertise cluster. Display in Pipeline tab or new "Expansion" section. |
| A3.2 Match acceptance feedback loop | 3.0 | Add "Accept Match" / "Decline Match" buttons to match cards. Store decisions in session state (or CSV append). When declined, prompt: "Why? (Too far / Schedule conflict / Topic mismatch / Other)". Feed feedback back into weight adjustment suggestions: "Based on 5 declines citing distance, consider increasing geographic_proximity weight from 0.20 to 0.30." Display feedback summary in sidebar. |
| A3.3 Volunteer dashboard view | 2.5 | Speaker-centric view (vs. event-centric in Matches tab): select a board member, see their top-5 matched events ranked by score. Show: events matched, events accepted, events attended (simulated), utilization rate. Mini bar chart per speaker. |
| A3.4 UI polish + custom CSS | 2.5 | Custom Streamlit theme: IA West brand colors (if available from intro deck, else professional blue/gray). Consistent card styling. Loading spinners for API calls. Error handling for all user interactions. Mobile-responsive layout check. |
| A3.5 Demo flow hardening | 2.0 | Pre-generate and cache ALL demo-path outputs: (1) UCLA live scrape result, (2) Travis Miller match explanation, (3) outreach email for top match, (4) .ics calendar invite. Store as JSON fixtures. Build demo mode toggle in sidebar: when ON, use cached outputs with artificial 2-second delays for "live" feel. When OFF, use real API calls. |
| A3.6 Pipeline funnel — real prototype outputs | 1.5 | Replace any remaining simulated funnel data with ACTUAL outputs from the prototype: real scraped event counts, real match scores, real email generation results. Annotate funnel stages with real speaker/event names. Ensure funnel hover text references actual data. |
| A3.7 Data export for Track B screenshots | 0.5 | Generate high-resolution screenshots/exports of: match cards, pipeline funnel, expansion map, discovery results. Save as PNG files for inclusion in Growth Strategy and Measurement Plan documents. |

**Track B (Person C) — 12-16h**

| Task | Hours | Description |
|------|-------|-------------|
| B3.1 Growth Strategy — Section 4 + 5 | 3.0 | Write Section 4: Channel Strategy (direct outreach via SmartMatch emails, IA West event cross-promotion, university career center partnerships, LinkedIn targeting of CPP alumni in MR). Write Section 5: Value Proposition (for volunteers: reduce coordination overhead, match expertise to opportunities, track impact; for universities: access to industry professionals, reduce recruiter fatigue, structured engagement pipeline). |
| B3.2 Growth Strategy — integration of real data | 2.5 | Embed real prototype outputs throughout the document: actual match examples (e.g., "Travis Miller matched to CPP Data Analytics Hackathon at 87% match score"), actual pipeline funnel numbers, actual university discovery counts. Add screenshots from prototype (from A3.7). Replace any placeholder text with real data references. |
| B3.3 Growth Strategy — ROI section + finalization | 2.0 | Add ROI section: volunteer hours saved (4.42h/match x 45 matches/quarter = 199h/quarter), membership LTV analysis, pipeline conversion projections. Add board-to-campus expansion map description with screenshot. Final formatting pass: headers, page numbers, consistent font, professional layout. Target: 2.5 pages, no more than 3. |
| B3.4 Measurement Plan — revision with real data | 1.5 | Update KPIs with actual prototype performance data: how many matches produced at >70% score, how many universities successfully scraped, email generation success rate. Update A/B test proposal: "Randomize weight configurations across 3 IA West events in Q3 2026 and measure match acceptance rate differences (n=15 matches per condition)." |
| B3.5 Responsible AI Note — final polish | 1.0 | Integrate specific bias audit results: run the matching engine across all 18 speakers and check for geographic over-representation. Report: "Speaker X was matched 12 times vs. Speaker Y 3 times — investigation shows topic coverage gap, not algorithmic bias." Add concrete mitigation: diversity-of-speaker rotation flag. |
| B3.6 Demo script — first draft | 2.0 | Write the 5-minute demo script. Structure: Problem (30s) -> Solution Overview (45s) -> Live Demo: Discovery (60s, UCLA scrape) -> Live Demo: Matching (45s, Travis Miller match card) -> Live Demo: Email + Calendar (30s) -> Pipeline Funnel (30s) -> Written Deliverables callout (15s) -> Responsible AI (15s). Include exact click paths, talking points, and backup plan notes. |

**Sprint 3 Definition of Done:**

Track A:
- [ ] ALL code features complete and working (feature freeze enforced)
- [ ] Board-to-campus expansion map renders correctly
- [ ] Match acceptance feedback loop stores and summarizes feedback
- [ ] Volunteer dashboard view shows per-speaker utilization
- [ ] Demo mode toggle works with cached outputs
- [ ] Pipeline funnel uses real prototype data
- [ ] Screenshots exported for Track B

Track B:
- [ ] Growth Strategy complete draft (2.5-3 pages) with real data integrated
- [ ] Measurement Plan finalized with real prototype performance data
- [ ] Responsible AI Note finalized with bias audit results
- [ ] Demo script first draft complete

**Go/No-Go Gate (End of Day 10):**
- PASS: All code features work. Written deliverables are 90%+ complete. Proceed to Sprint 4 testing.
- PARTIAL: If any should-add feature (expansion map, feedback loop, volunteer dashboard) is incomplete, cut it. Core MVP (matching + discovery + email + pipeline) is non-negotiable.
- FAIL on writing: Escalate. Person B shifts 50% of Day 11-12 to support writing. Code is frozen — only bug fixes.

---

### Sprint 4: Testing, Demo Prep, Final Polish (Day 11-14) — "Ship It"

**Track A (Person B) — 28-32h**

| Task | Hours | Description |
|------|-------|-------------|
| A4.1 End-to-end testing — Day 11 | 4.0 | Run complete demo flow 3x: app launch -> Discovery tab (UCLA scrape) -> Matches tab (select event, review top-3) -> Generate email -> Download .ics -> Pipeline tab (view funnel) -> Volunteer dashboard -> Expansion map. Log every bug, UI glitch, and slow response. |
| A4.2 Bug fixes — Day 11-12 | 4.0 | Fix all bugs found in A4.1. Priority: (1) anything that crashes the app, (2) incorrect match scores, (3) UI display issues, (4) slow API responses (add caching). |
| A4.3 Edge case hardening — Day 12 | 3.0 | Test: What happens when scraping fails mid-demo? (fallback to cache). What happens when the Gemini API times out? (show cached explanation). What happens when user adjusts all weights to 0? (show error message). What happens with custom URL that returns garbage HTML? (graceful error). |
| A4.4 Performance optimization — Day 12 | 2.0 | Profile Streamlit app: page load time, API call latency, memory usage. Target: <3s initial load, <5s for scrape+extract, <2s for email generation. Pre-compute all embeddings at startup. Lazy-load scraping results. |
| A4.5 Streamlit Cloud deployment — Day 12 | 2.0 | Deploy to Streamlit Community Cloud. Configure secrets (`GEMINI_API_KEY`). Test on cloud: verify all features work within 1GB RAM limit. Preserve Sprint 2's `scrape_university()` response contract on cloud; when Playwright is unavailable, serve hashed cache artifacts from `cache/scrapes/` and keep the same `{html, scraped_at, source, ...}` dict shape. |
| A4.6 Demo rehearsal with Person C — Day 13 | 3.0 | Full 5-minute demo rehearsal with Person C presenting, Person B operating the app. Time each section. Identify weak transitions. Practice backup plan: if live scrape fails, switch to cached. If API fails, show pre-generated outputs. Run 3 full rehearsals. |
| A4.7 Backup demo video recording — Day 13 | 2.0 | Screen-record a perfect demo run (with narration). Edit to 5 minutes. This is the emergency backup if everything fails on demo day. |
| A4.8 Final code cleanup — Day 14 | 2.0 | Remove debug prints, clean up imports, add docstrings to key functions (matching engine, scraper, email generator). Verify `.gitignore` excludes `.env`, API keys, cached embeddings (if large). Final commit. |
| A4.9 Day-of prep — Day 14 | 3.0 | Pre-warm all caches: run every scrape into `cache/scrapes/`, generate every explanation into `cache/explanations/`, generate every email into `cache/emails/`, and verify demo mode works against those actual cache layouts. Check internet connectivity backup plan. Charge laptop. Test projector output. |
| A4.10 Buffer for Track B support | 3.0 | Available to help Person C with: generating additional screenshots, running specific prototype queries to produce data for documents, formatting written deliverables. |

**Track B (Person C) — 18-24h**

| Task | Hours | Description |
|------|-------|-------------|
| B4.1 Growth Strategy — final revision | 3.0 | Final editing pass: tighten language to market-research terminology ("conversion funnel," "engagement pipeline," "panel recruitment," "response optimization"). Ensure every claim has a data point (real from prototype or cited from research). Format for submission: clean headers, professional layout, 2.5-3 pages. |
| B4.2 Measurement Plan — final revision | 1.5 | Final editing pass. Ensure KPI targets are specific and realistic. Verify the A/B test proposal is methodologically sound (sample size, duration, success metric). Add feedback loop diagram: Match Score -> Acceptance Decision -> Feedback Capture -> Weight Adjustment -> Improved Match Score. |
| B4.3 Responsible AI Note — final revision | 1.0 | Final editing pass. Ensure concrete mitigations are stated (not just "we will address bias" but "we implemented a diversity-of-speaker rotation flag and conducted a bias audit showing geographic distribution of matches"). |
| B4.4 Demo script — revision + practice | 3.0 | Revise demo script based on actual app behavior (from Sprint 3 testing). Add exact quotes for narration. Practice presenting: 3 solo rehearsals timed to 5 minutes. Memorize key transitions and backup-plan triggers. |
| B4.5 Demo rehearsal with Person B — Day 13 | 3.0 | Joint rehearsals (same as A4.6). Person C handles narration and talking points. Person B handles app operation and troubleshooting. Practice the handoff between presenting written deliverables and showing the prototype. |
| B4.6 Presentation slides (if needed) | 2.0 | If the hackathon format includes slides: build 8-10 slides. Structure: Title, Problem (IA West pain points), Solution (SmartMatch overview), Architecture (4-module diagram from PLAN.md), Demo (live), Results (pipeline funnel + ROI), Written Deliverables (Growth Strategy highlights), Responsible AI, Next Steps. |
| B4.7 Q&A preparation | 2.0 | Anticipate judge questions: "How does this scale beyond 5 universities?" "What happens when event pages change?" "How do you handle speaker fatigue?" "What's the actual membership conversion evidence?" "How did you validate match quality?" Prepare concise answers with data. |
| B4.8 Final document compilation | 1.5 | Compile all written deliverables into submission package: Growth Strategy (2.5-3 pages), Measurement Plan (1 page), Responsible AI Note (0.5 page). Verify formatting, page counts, and that all required sections are present per the challenge rubric. |
| B4.9 Day-of prep — Day 14 | 1.0 | Print backup copies of written deliverables. Prepare USB with backup demo video. Review Q&A answers one more time. |

**Sprint 4 Definition of Done:**

Track A:
- [ ] Zero critical bugs in demo flow
- [ ] App deploys and runs on Streamlit Cloud
- [ ] Demo mode works with cached outputs (backup plan verified)
- [ ] Backup demo video recorded
- [ ] 3+ full rehearsals completed
- [ ] All caches pre-warmed for demo day

Track B:
- [ ] Growth Strategy final (2.5-3 pages, real data, market research language)
- [ ] Measurement Plan final (1 page, specific KPIs, A/B test proposal)
- [ ] Responsible AI Note final (0.5 page, concrete mitigations)
- [ ] Demo script memorized, 3+ rehearsals completed
- [ ] Q&A answers prepared for 5+ anticipated questions
- [ ] Submission package compiled

**Go/No-Go Gate (End of Day 14 — FINAL):**
- PASS: Demo runs cleanly in rehearsal. Written deliverables complete. Team confident. Ship it.
- CONDITIONAL PASS: Minor bugs exist but demo mode (cached) works. Written deliverables complete. Ship it with demo mode as primary.
- FAIL: This should not happen if feature freeze was respected on Day 9. If it does: use backup video for demo, submit written deliverables as-is, present with slides only.

---

## 2. Milestone Checkpoints

| Milestone | Date (Day) | Deliverable | Success Metric | Owner |
|-----------|-----------|-------------|----------------|-------|
| **M0: Data Validated** | Day 1 | Data quality report, all CSVs loading | 77 records load, no critical data issues | Person B |
| **M1: Embeddings Work** | Day 2 | Speaker + event embeddings cached | Cosine similarity produces meaningful rankings (sanity check on 5 known pairs) | Person B |
| **M2: Matching MVP** | Day 5 | Matching engine + Matches tab UI | Top-3 matches per event with explanation cards, weight sliders functional | Person B |
| **M3: Track B Kickoff** | Day 6 | Track B data package delivered | Person C has all data needed to begin Growth Strategy | Both |
| **M4: Discovery Works** | Day 8 | Web scraping + Discovery tab | 5 universities scraped + cached, LLM extraction produces valid JSON | Person B |
| **M5: Email + Pipeline** | Day 8 | Outreach email gen + pipeline funnel | Emails generate correctly, funnel displays with real data | Person B |
| **M6: Growth Strategy 60%** | Day 8 | Sections 1-3 drafted | ~1.5 pages of Growth Strategy complete with real data | Person C |
| **M7: Feature Freeze** | Day 9 | All code features locked | Expansion map, feedback loop, volunteer dashboard complete (or cut) | Person B |
| **M8: Writing Complete** | Day 10 | All written deliverables at 90%+ | Growth Strategy, Measurement Plan, Responsible AI Note near-final | Person C |
| **M9: Testing Complete** | Day 12 | Bug-free demo flow | 3 clean demo runs, zero crashes, all edge cases handled | Person B |
| **M10: Rehearsals Done** | Day 13 | Joint rehearsals complete | 3+ timed rehearsals at 5 minutes, backup plan tested | Both |
| **M11: Ship** | Day 14 | Everything submitted | Code deployed, docs compiled, caches warm, backup video ready | Both |

---

## 3. Risk Gates

### Scope Cut Triggers

| Trigger | When | What Gets Cut | Impact |
|---------|------|---------------|--------|
| Embeddings produce flat scores | Day 2 | Cut vector embeddings, switch to TF-IDF + keyword overlap | 2h rework, no schedule slip. Matching still works, less impressive in demo. |
| University scraping fails for 3+ targets | Day 7 | Reduce to 2 cached universities + 1 live demo target | Discovery tab less impressive but still functional. Announce "extensible to any university." |
| Feature freeze violated (Day 9 features incomplete) | Day 9 | Cut should-add features in order: (1) Volunteer Dashboard, (2) Match Feedback Loop, (3) Board-to-Campus Map | Each cut saves 2.5-3h. Core MVP is unaffected. |
| Written deliverables behind schedule (Day 10 <75%) | Day 10 | Person B shifts 50% of Day 11-12 to writing support. Cut: backup video quality (use raw recording). | Written deliverables are 40% of judging — this is a P0 escalation. |
| API outage during testing | Day 11-12 | Pre-generate ALL demo outputs. Demo mode becomes primary, not backup. | No impact if caching is thorough. Add 2h to pre-generation. |
| Streamlit Cloud deployment fails | Day 12 | Run demo locally. Streamlit Cloud becomes "available for judges to try after" not live demo. | Minor impact — most hackathon demos run locally anyway. |

### Cut Priority (First to Last)

1. **First cut:** Volunteer Dashboard View (3h saved, minimal demo impact)
2. **Second cut:** Match Acceptance Feedback Loop (3h saved, no demo impact)
3. **Third cut:** Board-to-Campus Expansion Map (3h saved, moderate demo impact)
4. **Fourth cut:** Calendar .ics Preview (1.5h saved, minimal demo impact)
5. **NEVER cut:** Matching engine, discovery/scraping, email generation, pipeline funnel, written deliverables

---

## 4. Written Deliverables Plan

### Growth Strategy (2.5-3 pages)

**Section 1: Executive Summary + Problem Statement (0.5 page)**
- IA West's volunteer coordination bottleneck: 8+ events/year, 18 board members, 6 metro regions, zero centralized infrastructure
- Quantify the gap: 35 CPP course sections go largely untapped, no funnel tracking, no ROI measurement
- SmartMatch as the solution: AI-orchestrated discovery, matching, outreach, and pipeline tracking
- Key data points to include:
  - Stanford Social Innovation Review: volunteer-run chapters lose 30-40% of engagement opportunities
  - Number of board members (18), events (15 CPP), courses (35), universities in corridor (8+)

**Section 2: Target Audience Segments (0.5 page)**
- Segment A: Board Members / Volunteers — pain: ad-hoc coordination, unclear where to invest time
- Segment B: University Program Coordinators — pain: finding qualified industry speakers/judges
- Segment C: Students / Young Professionals — pain: no pathway from campus event to IA membership
- Segment D: IA West Chapter Leadership — pain: no data to measure engagement ROI
- Key data points to include:
  - Real speaker profile data: geographic distribution, expertise clusters
  - CPP event categories and volunteer role types

**Section 3: Rollout Plan — CPP to West Coast Corridor (0.5 page)**
- Phase 1 (Q2-Q3 2026): CPP pilot — 15 events + 35 course sections, 18 board members
- Phase 2 (Q4 2026): LA Metro expansion — UCLA, USC (closest to LA West and Ventura speaker clusters)
- Phase 3 (Q1-Q2 2027): West Coast corridor — SDSU, UC Davis, Portland State
- Board-to-Campus Expansion Map: which board members serve which campuses (use geographic proximity data)
- Key data points to include:
  - Actual geographic proximity scores from prototype
  - Event count projections per phase (15 -> 35 -> 60+ events)
  - Speaker utilization targets per phase

**Section 4: Channel Strategy (0.5 page)**
- Channel 1: SmartMatch outreach emails (automated, personalized, generated by prototype)
- Channel 2: IA West event cross-promotion (match campus contacts to IA events via calendar)
- Channel 3: University career center partnerships (formal MOU for recurring engagement)
- Channel 4: LinkedIn targeting (CPP alumni in market research — warm pipeline)
- Key data points to include:
  - Email response rate benchmarks for professional associations (ASAE: 20-30%)
  - IA event calendar (9 events across 2026) as touchpoints

**Section 5: Value Proposition + ROI (0.5 page)**
- For Volunteers: 4.42 hours saved per match cycle (manual: 4.5h -> SmartMatch: 0.08h), expertise-aligned opportunities, impact tracking
- For Universities: qualified industry professionals on demand, reduced recruiter fatigue, structured engagement
- For IA West: 199 volunteer hours saved per quarter ($9,950 at $50/h opportunity cost), measurable pipeline, data-driven expansion decisions
- Membership LTV: estimate annual dues ($X) x average retention (Y years) x conversion rate (10-15%) = projected membership revenue per cohort
- Key data points to include:
  - Real match counts from prototype (X matches generated)
  - Volunteer hours calculation (specific to 18 board members x estimated events/quarter)

**Research Needed:**
- [ ] IA West membership dues structure (check website or challenge docs)
- [ ] ASAE benchmarks for professional association email response rates
- [ ] CASE (Council for Advancement and Support of Education) data on university-industry engagement programs
- [ ] Stanford Social Innovation Review citation for volunteer coordination overhead

### Measurement Plan (1 page)

**Section 1: KPI Framework (0.4 page)**

| KPI | Definition | Target | Data Source |
|-----|-----------|--------|-------------|
| Match Acceptance Rate | % of top-3 recommendations accepted by chapter leadership | 60%+ | Feedback loop in SmartMatch |
| Email Response Rate | % of outreach emails that receive a reply | 25%+ | Email tracking (future integration) |
| Event Attendance Rate | % of confirmed volunteers who attend | 70%+ | Post-event check-in |
| Membership Conversion Rate | % of engaged students who join IA within 12 months | 10-15% | IA membership database |
| Volunteer Utilization Rate | Average matches per board member per quarter | 2+ | SmartMatch pipeline tracker |
| Discovery Efficiency | New events discovered per university per quarter | 5+ | Discovery tab logs |
| Time Savings | Hours saved per match cycle vs. manual process | 4+ hours | Process comparison audit |

**Section 2: Proposed Validation Experiment (0.3 page)**
- A/B test design: For 6 IA West events in Q3-Q4 2026, randomly assign 3 events to "SmartMatch-recommended" matching and 3 events to "manual chapter leadership" matching
- Success metric: Compare match acceptance rates, volunteer satisfaction scores, and event attendance rates between conditions
- Sample size: 15 matches per condition (3 events x 5 matches each), sufficient for directional signal
- Duration: 6 months (Q3-Q4 2026)
- Secondary test: Within SmartMatch events, randomize weight configurations (high topic relevance vs. high geographic proximity) across matches to optimize the scoring formula

**Section 3: Feedback Loop (0.3 page)**
- Diagram: Match Generated -> Chapter Leadership Review -> Accept/Decline with reason -> Feedback aggregated -> Weight adjustment recommendation -> Improved next-cycle matches
- Quarterly review cadence: analyze patterns in decline reasons (too far, topic mismatch, schedule conflict) and adjust default weights accordingly
- Annual model refresh: re-embed all speaker profiles with updated expertise tags and new event data
- Continuous improvement: match explanation quality rated by users (helpful/not helpful), low-rated explanations trigger prompt refinement

---

## 5. Demo Readiness Checklist

### Working Features (Must Demonstrate Live)

- [ ] **Matching Engine:** Select an event, see top-3 speaker matches with scores + radar charts
- [ ] **Explanation Cards:** Natural language "why this match" for each recommendation
- [ ] **Weight Sliders:** Adjust weights, see rankings change in real time
- [ ] **Live Discovery:** Scrape UCLA (or cached fallback), show extracted events
- [ ] **Email Generation:** Generate personalized outreach email for top match, copy to clipboard
- [ ] **Pipeline Funnel:** Plotly funnel showing Discovered -> Matched -> Contacted -> Confirmed -> Attended -> Member Inquiry with real data labels

### Should Demonstrate (If Built)

- [ ] **Calendar .ics Download:** Generate and download calendar invite for matched event
- [ ] **Expansion Map:** Board-to-campus geographic map with connection lines
- [ ] **Feedback Loop:** Accept/decline match and see feedback summary
- [ ] **Volunteer Dashboard:** Per-speaker view with utilization metrics

### Written Deliverables (Must Submit)

- [ ] **Growth Strategy:** 2.5-3 pages, printed/PDF, real data integrated, market research language
- [ ] **Measurement Plan:** 1 page, specific KPIs with targets, A/B test proposal
- [ ] **Responsible AI Note:** 0.5 page, concrete mitigations with audit results

### Demo Flow (5 Minutes)

| Time | Section | Content | Backup Plan |
|------|---------|---------|-------------|
| 0:00-0:30 | Problem | "IA West coordinates 18 board members across 6 metro regions for 8+ events/year — entirely via email chains and gut feel." Show pain point stats. | Slide with stats |
| 0:30-1:15 | Solution Overview | "SmartMatch uses AI to automate the full lifecycle." Show 4-module architecture diagram. | Slide with architecture |
| 1:15-2:15 | Live Demo: Discovery | Navigate to Discovery tab. Select UCLA. Click "Discover Events." Show extracted events appearing. Click "Add to Matching" on one. | Switch to cached results. "Here's what SmartMatch found when we scanned UCLA earlier today." |
| 2:15-3:15 | Live Demo: Matching | Navigate to Matches tab. Select the UCLA event. Show top-3 speaker cards with radar charts. Read Travis Miller explanation card. Adjust weight slider — show rankings change. | Show pre-generated screenshot. |
| 3:15-3:45 | Live Demo: Email + Calendar | Click "Generate Email" on Travis Miller match. Show personalized email. Click "Download Calendar Invite." | Show pre-generated email text. |
| 3:45-4:15 | Pipeline + ROI | Navigate to Pipeline tab. Show funnel: "From 60+ discovered events across 5 universities, SmartMatch generated 45 top matches, projected to 199 volunteer hours saved per quarter." | Show funnel screenshot. |
| 4:15-4:45 | Written Deliverables | "Our Growth Strategy details a 3-phase rollout from CPP to the full West Coast corridor, with specific KPIs in our Measurement Plan." Hold up / reference documents. | Read key stats from Growth Strategy. |
| 4:45-5:00 | Responsible AI | "Every match is explainable — no black boxes. We conducted a bias audit across all 18 speakers." | Reference Responsible AI Note. |

### Backup Plan Summary

| Failure Mode | Trigger | Response |
|-------------|---------|----------|
| Internet dies | No connectivity at venue | Demo mode uses all cached data. Every feature works offline except live scrape. |
| Gemini API down | API timeout > 10s | All explanations, emails, and extraction results pre-cached. Switch to demo mode. |
| Live scrape fails | HTTP error or malformed HTML | "Here's what SmartMatch found when we ran this earlier" — show cached UCLA results. |
| App crashes | Unhandled exception | Restart app (Streamlit restarts in <5s). If persistent: switch to backup video. |
| Total meltdown | Everything fails | Play backup demo video. Present written deliverables. Answer Q&A from prepared answers. |

---

## 6. Critical Path

The critical path identifies tasks with zero slack — any delay on these tasks directly delays the final deliverable.

```
CRITICAL PATH (zero slack):

Day 1-2:  A0.2 Data ingestion ──> A0.3-4 Embeddings ──> A0.5 Validation
                                                              │
Day 3-5:  A1.1 MATCH_SCORE formula ──> A1.2 Ranking engine ──> A1.4 Matches UI
                                                                      │
Day 6:    A2.7 Track B data package ──────────────────────────────────┤
              │                                                       │
Day 6-8:  A2.1 Scraping ──> A2.2 LLM extraction ──> A2.3 Discovery UI│
              │                                                       │
Day 6-8:  B2.1 Research ──> B2.2 Growth Strategy Sec 1-2 ──> B2.3 Sec 3
                                                                      │
Day 9:    ═══════ FEATURE FREEZE ═════════════════════════════════════╡
              │                                                       │
Day 9-10: B3.1 Growth Strategy Sec 4-5 ──> B3.2 Real data integration│
              │                                                       │
Day 11-12:A4.1 Testing ──> A4.2 Bug fixes                            │
              │                                                       │
Day 11-12:B4.1 Growth Strategy final ──> B4.2 Measurement Plan final │
              │                                                       │
Day 13:   A4.6 + B4.5 Joint rehearsal (BOTH TRACKS CONVERGE)         │
              │                                                       │
Day 14:   A4.9 + B4.9 Day-of prep ──> DEMO DAY                      ▼
```

### Key Handoff Points (Zero Slack)

| Handoff | From | To | Deadline | Content | Risk if Late |
|---------|------|----|----------|---------|-------------|
| **H1: Data Package** | Person B (A2.7) | Person C (B2.1) | Day 6 morning | Match results, pipeline data, ROI inputs, university coverage | Person C starts Growth Strategy without real data — must rewrite later. 4h wasted. |
| **H2: Screenshots** | Person B (A3.7) | Person C (B3.2) | Day 10 morning | Match card screenshots, pipeline funnel, expansion map images | Growth Strategy lacks visual evidence. Weaker submission. |
| **H3: Real Pipeline Data** | Person B (A3.6) | Person C (B3.4) | Day 10 morning | Actual funnel numbers from prototype | Measurement Plan uses estimates instead of real performance data. Less credible. |
| **H4: Bias Audit Results** | Person B (matching engine) | Person C (B3.5) | Day 10 morning | Geographic distribution of matches, speaker match frequency | Responsible AI Note is generic instead of specific. Weaker on 10-point judging criterion. |
| **H5: Demo Rehearsal** | Both | Both | Day 13 | Joint 5-min timed rehearsal x3 | Unrehearsed demo risks overtime, awkward transitions, missed backup triggers. |

### Parallel vs. Sequential Constraints

**Can run in parallel (no dependency):**
- A0.3 Speaker embeddings + A0.4 Event embeddings (Day 1-2)
- A2.1 Web scraping + A2.4 Email generation (Day 6-8, both depend on matching engine but not on each other)
- B2.2 Growth Strategy drafting + B2.4 Measurement Plan drafting (Day 6-8)
- A4.1 Testing + B4.1 Final writing revisions (Day 11-12)

**Must be sequential (hard dependency):**
- A0.2 Data ingestion BEFORE A0.3-4 Embeddings (need data to embed)
- A0.5 Validation BEFORE A1.1 MATCH_SCORE (must confirm embeddings work)
- A1.1 MATCH_SCORE BEFORE A1.4 Matches UI (UI displays scores)
- A2.7 Data package BEFORE B2.2 Growth Strategy (writing needs real data)
- A3.7 Screenshots BEFORE B3.2 Data integration (documents need images)
- A4.2 Bug fixes BEFORE A4.6 Rehearsal (rehearse the fixed version)
- A4.6 Rehearsal BEFORE A4.7 Backup video (record after rehearsal polish)

---

## Hour Budget Summary

### Track A (Person B) — Days 1-14

| Sprint | Days | Hours | Cumulative |
|--------|------|-------|-----------|
| Sprint 0: Foundation | 1-2 | 14-16h | 14-16h |
| Sprint 1: Matching Core | 3-5 | 21-24h | 35-40h |
| Sprint 2: Discovery + Email | 6-8 | 21-24h | 56-64h |
| Sprint 3: Polish + Feature Freeze | 9-10 | 14-16h | 70-80h |
| Sprint 4: Testing + Demo | 11-14 | 28-32h | **98-112h** |

### Track B (Person C) — Days 6-14

| Sprint | Days | Hours | Cumulative |
|--------|------|-------|-----------|
| Sprint 2: Research + Drafting | 6-8 | 18-24h | 18-24h |
| Sprint 3: Completion + Integration | 9-10 | 12-16h | 30-40h |
| Sprint 4: Final Polish + Demo | 11-14 | 18-24h | **48-64h** |

### Combined Total: **146-176 person-hours** (within 154-184h budget)

### Hour Allocation by Judging Criterion

| Criterion | Points (of 50) | % of Judging | Hours Invested | % of Budget |
|-----------|---------------|-------------|----------------|-------------|
| Prototype Quality | ~15 | 30% | ~75-90h (Track A code) | ~48-51% |
| Growth Strategy | ~10 | 20% | ~22-28h (Track B) | ~14-16% |
| Measurement Plan | ~10 | 20% | ~8-10h (Track B) | ~5-6% |
| Responsible AI | ~10 | 20% | ~5-6h (Track B) | ~3-4% |
| Scalability | ~5 | 10% | ~8-10h (discovery + expansion map) | ~5-6% |
| Demo prep + testing | — | — | ~28-32h | ~18-19% |

Written deliverables (40% of judging) receive ~35-44h (~22-25% of total budget). This is a deliberate overweight vs. strict proportional allocation because the prototype work simultaneously serves the demo, which IS the other 30% of judging (Prototype Quality).

---

## Appendix: Daily Standup Questions

Each day, each person answers:
1. What did I complete yesterday?
2. What will I complete today?
3. What is blocking me?
4. Am I on track for the next milestone?

Track these in `.memory/context/cat3-daily-standups.md` to maintain continuity across sessions.
