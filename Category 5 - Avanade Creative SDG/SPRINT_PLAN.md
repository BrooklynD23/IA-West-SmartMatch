# Category 5 — CropSense AI: Sprint Plan

**Lead:** Person D (dedicated, full 2 weeks)
**Tier:** 1.5 (conditional on Day 4 vertical slice gate)
**Win Probability:** 25-70%, realistic midpoint 50%
**Total Budget:** ~108 person-hours (Person D: ~8h/day x 14 days = 112h, minus ~4h buffer)
**Constraint:** Everything from scratch -- no prototype, no starter code, no pre-trained model
**Frontend:** Streamlit (per PM/CTO mandate -- NOT Next.js)

**Scheduling Note:** Day numbers in `MASTER_SPRINT_PLAN.md` are the canonical portfolio schedule. The exact dates below are draft kickoff placeholders and must be re-anchored once the team confirms the build window.

---

## 1. Sprint Breakdown

---

### Sprint 0 — Foundation (Days 0-1 | March 15-16 | 16h)

**Sprint Goal:** Azure services provisioned, data downloaded, project scaffolded, first Custom Vision training run initiated.

| # | Task | Est. Hours | Notes |
|---|------|-----------|-------|
| 0.1 | Azure for Students account activation + credit verification ($100) | 1h | BLOCKER if credits unavailable -- fallback: Azure free trial ($200) |
| 0.2 | Provision Azure Custom Vision resource (F0 free tier initially) | 0.5h | Create project, select "Classification" + "Multiclass" |
| 0.3 | Provision Azure OpenAI resource + deploy GPT-4o-mini | 1h | Request access if not already approved; deploy model in East US region |
| 0.4 | Download PlantVillage dataset (full 54K images from GitHub) | 0.5h | Clone `spMohanty/PlantVillage-Dataset` repo |
| 0.5 | Curate PlantVillage subset: select 5-7 diseases with highest visual distinctiveness | 2h | Target diseases: Tomato Late Blight, Tomato Bacterial Spot, Corn Gray Leaf Spot, Corn Common Rust, Potato Early Blight, Potato Late Blight, Healthy (control). ~100-150 images per class = 700-1050 total. Prioritize diseases relevant to sub-Saharan Africa maize/potato farming. |
| 0.6 | Upload curated images to Azure Custom Vision + start first training iteration | 1.5h | Tag all images by disease class. Use "Quick Training" for first pass (~15-20 min training time). |
| 0.7 | Contribute to shared infrastructure: LLM API wrapper + Streamlit theme template | 3h | Coordinate with Person A. Build configurable wrapper (Azure OpenAI endpoint). Fork shared Streamlit theme. |
| 0.8 | Scaffold project structure | 1h | See structure below |
| 0.9 | Verify Open-Meteo API with Kenyan coordinates (Nairobi: -1.2921, 36.8219) | 0.5h | Confirm data availability, resolution, response format for sub-Saharan Africa |
| 0.10 | Research: compile FAO/World Bank statistics for impact narrative | 1.5h | Cost-of-inaction calculation, SDG data points, Amina persona details |
| 0.11 | Research competitive landscape (Plantix, DigiFarm, Hello Tractor) | 1h | Document gaps CropSense fills |
| 0.12 | Source 3-5 REAL diseased leaf photos (not from PlantVillage training set) | 1h | Search agricultural extension websites, iNaturalist, or photograph real leaves. These are for demo day -- must not be training images. |
| 0.13 | Document Sprint 0 outcomes in `.memory/` | 0.5h | Azure resource IDs, accuracy baseline, blockers |

**Subtotal:** 15h

**Project Structure (Task 0.8):**
```
Category 5 - Avanade Creative SDG/
  app/
    app.py                  # Streamlit main entry
    pages/
      farmer_mode.py        # Amina persona -- upload + diagnosis
      extension_officer.py  # Extension officer dual persona
      sdg_dashboard.py      # SDG impact visualization
    components/
      image_upload.py       # Photo upload widget
      diagnosis_card.py     # Disease result + confidence display
      advisory_card.py      # LLM advisory display
      weather_panel.py      # Weather context widget
      sms_preview.py        # SMS-format output
      confidence_gradient.py # Confidence gradient UI component
    services/
      cv_service.py         # Azure Custom Vision API client
      llm_service.py        # Azure OpenAI advisory generation
      weather_service.py    # Open-Meteo API client
    utils/
      config.py             # Environment variables, constants
      prompts.py            # LLM prompt templates
      translations.py       # Language handling
    assets/
      demo_images/          # Real leaf photos for demo
      amina_story/          # Narrative assets
  tests/
    test_cv_service.py
    test_llm_service.py
    test_weather_service.py
    test_integration.py
  data/
    diseases.json           # Disease metadata (name, treatment, severity)
    demo_scenarios.json     # Pre-cached demo results (backup)
  requirements.txt
  .env.example
```

**Definition of Done:**
- [ ] Azure Custom Vision project exists with first training iteration complete
- [ ] Azure OpenAI GPT-4o-mini endpoint responds to a test prompt
- [ ] Open-Meteo API returns weather data for Nairobi coordinates
- [ ] PlantVillage subset curated and uploaded (700+ images, 5-7 classes)
- [ ] Project scaffolded with all directories and placeholder files
- [ ] Shared LLM wrapper integrated
- [ ] At least 1 real leaf photo sourced (not from training set)
- [ ] FAO statistics documented: cost-of-inaction = $144/season for Amina

**Go/No-Go Gate:** If Azure for Students credits are unavailable AND Azure free trial signup fails, escalate immediately. This is a Day 0 blocker with no workaround.

---

### Sprint 1 — Vertical Slice + Core AI Pipeline (Days 2-7 | March 17-22 | 48h)

**Sprint Goal:** Working end-to-end pipeline: photo upload -> disease classification -> LLM advisory -> display. This is the Day 4 vertical slice gate. The remaining days build out weather integration and multilingual support.

#### Phase 1A: Vertical Slice (Days 2-4 | 24h) -- CRITICAL PATH

| # | Task | Est. Hours | Notes |
|---|------|-----------|-------|
| 1.1 | Build `cv_service.py`: Azure Custom Vision prediction client | 2h | Accept image bytes, return top prediction + confidence score + all class probabilities |
| 1.2 | Evaluate Custom Vision model accuracy on held-out test set | 1.5h | Target: >85% accuracy on selected diseases. If <80%, re-curate training data (add augmented variants, remove ambiguous images). If <70% after re-training, trigger fallback (see Risk Gates). |
| 1.3 | Iterate Custom Vision model if needed (add images, re-train) | 2h | Use "Advanced Training" option (up to 1h training). Review per-class precision/recall. Focus on worst-performing class. |
| 1.4 | Build `prompts.py`: advisory prompt template | 2h | System prompt includes: disease name, confidence %, crop type, region, severity context. Output format: actionable steps, tone appropriate for smallholder farmer, SMS-length version. Include "consult extension officer" for <70% confidence. |
| 1.5 | Build `llm_service.py`: Azure OpenAI advisory generation | 2h | Takes CV output + optional weather context -> returns advisory in requested language. Handle API errors gracefully. |
| 1.6 | Build `image_upload.py` + `diagnosis_card.py` Streamlit components | 2h | File uploader, image preview, loading spinner during classification |
| 1.7 | Build `advisory_card.py` Streamlit component | 1.5h | Display advisory text, confidence score, recommended actions, escalation notice |
| 1.8 | Build `farmer_mode.py` page: wire upload -> CV -> LLM -> display | 3h | Full vertical slice. Upload photo, show diagnosis result, show advisory. |
| 1.9 | Build `sms_preview.py`: SMS-format output (<=160 chars) | 1h | Render advisory condensed to SMS length with "SMS-ready" label |
| 1.10 | Test vertical slice with 5+ images (mix of diseases + healthy) | 2h | Document accuracy, response time, advisory quality. Test at least 1 real (non-PlantVillage) leaf photo. |
| 1.11 | Cache 5 demo scenarios to `demo_scenarios.json` | 1h | Backup: if Azure API fails during demo, load cached results |
| 1.12 | Write unit tests for cv_service + llm_service | 2h | Mock API responses, test error handling, test confidence thresholds |

**Phase 1A Subtotal:** 22h

**--- DAY 4 VERTICAL SLICE GATE (End of Day 4, ~March 19) ---**

Gate Criteria:
- Can upload a leaf photo and receive a disease classification with >80% confidence on known diseases? **YES/NO**
- Does the LLM generate a coherent, actionable advisory based on the classification? **YES/NO**
- Does the Streamlit UI display results in under 15 seconds end-to-end? **YES/NO**

**If all YES:** Proceed to Phase 1B.
**If any NO:** See Risk Gates section -- trigger fallback plan.

#### Phase 1B: Weather + Multilingual (Days 5-7 | 24h)

| # | Task | Est. Hours | Notes |
|---|------|-----------|-------|
| 1.13 | Build `weather_service.py`: Open-Meteo API client | 2h | Accept GPS coordinates, return 7-day forecast (temperature, precipitation, humidity). Parse response into structured format for LLM prompt injection. |
| 1.14 | Build weather-aware advisory logic | 2h | Inject weather context into LLM prompt: "Rain expected in 2 days -- delay outdoor fungicide application" / "Dry spell forecast -- increase irrigation frequency." |
| 1.15 | Build `weather_panel.py` Streamlit component | 2h | Display 7-day forecast, highlight weather-relevant advisory context |
| 1.16 | Add multilingual output: English + Swahili + French | 3h | Add language selector to UI. Update prompt template to request output in target language. Test advisory quality in all 3 languages with native speaker review if possible. |
| 1.17 | Build `translations.py`: UI string translations | 1.5h | Translate all UI labels, buttons, headers into Swahili + French. Static strings only -- LLM handles dynamic advisory text. |
| 1.18 | Build `confidence_gradient.py` component (must-add per Strategic Review) | 2.5h | Visual gradient bar showing confidence level (green >90%, yellow 70-90%, red <70%). Color-coded with clear labels. Makes responsible AI visible in the UI. |
| 1.19 | Integrate weather into farmer_mode.py flow | 1.5h | After classification, fetch weather for Amina's location, inject into advisory, display weather panel |
| 1.20 | Add "consult extension officer" escalation UI for low confidence | 1h | If confidence <70%, show prominent warning with extension officer contact information |
| 1.21 | End-to-end integration test: all 3 AI systems together | 2h | Upload photo -> CV classification -> weather fetch -> LLM advisory (weather-aware, multilingual) -> display with confidence gradient |
| 1.22 | Write integration tests | 1.5h | Test full pipeline with mocked services |
| 1.23 | Document Sprint 1 outcomes in `.memory/` | 0.5h | Accuracy metrics, response times, language quality assessment |

**Phase 1B Subtotal:** 19.5h (allowing ~2.5h buffer from 24h allocation)

**Sprint 1 Total:** 41.5h (within 48h budget with buffer)

**Definition of Done:**
- [ ] Vertical slice works: upload -> classify -> advise -> display in <15 seconds
- [ ] Custom Vision accuracy >85% on test set across 5-7 diseases
- [ ] Weather integration: advisory adjusts based on 7-day forecast
- [ ] Multilingual: advisory generates in English, Swahili, French
- [ ] Confidence gradient UI displays and color-codes prediction confidence
- [ ] Low-confidence escalation path ("consult extension officer") works
- [ ] SMS-format preview renders advisory in <=160 characters
- [ ] 5 demo scenarios cached as backup
- [ ] Unit tests pass for all service modules
- [ ] Integration test passes for full pipeline

---

### Sprint 2 — Extension Officer Mode + Polish + Narrative (Days 8-11 | March 23-26 | 32h)

**Sprint Goal:** Build Extension Officer Mode (dual persona), SDG dashboard, narrative storyboard, and begin demo rehearsal.

| # | Task | Est. Hours | Notes |
|---|------|-----------|-------|
| 2.1 | Build `extension_officer.py` page (must-add, 6-8h per Strategic Review) | 7h | Dual persona toggle in sidebar or tab. Extension Officer Mode shows: (a) batch upload capability for multiple leaf images, (b) technical disease details (pathogen name, severity classification, spread risk), (c) treatment recommendations with chemical names and dosages, (d) regional disease trend summary, (e) farmer advisory history log. This is NOT just a reskin -- it shows different LLM output (technical vs. plain-language). |
| 2.2 | Build `sdg_dashboard.py` page | 4h | Visual dashboard showing: SDG 2 (Zero Hunger) impact counter, SDG 13 (Climate Action) metrics, SDG 10 (Reduced Inequalities) access statistics. Use Plotly for interactive charts. Include verified FAO/World Bank citations. Show "Diagnoses performed," "Farmers helped," "Estimated yield saved (kg)." |
| 2.3 | Treatment Cost Estimator (should-add, 3-4h per Strategic Review) | 3h | After diagnosis, show estimated treatment cost in local currency (KES). Compare cost-of-treatment vs. cost-of-inaction ($144/season loss for Amina). Use hardcoded but researched price data for common fungicides/pesticides in Kenya. |
| 2.4 | Diagnosis History Timeline (should-add, 3-4h per Strategic Review) | 3h | Session-based timeline showing all diagnoses in current session. Each entry: thumbnail, disease, confidence, timestamp, advisory summary. Demonstrates "over time, CropSense builds a picture of your farm's health." Uses Streamlit session state (no database needed). |
| 2.5 | Amina narrative storyboard + demo script | 4h | Write the full "Amina's Story" narrative: (a) Opening hook: "Amina farms 2 acres of maize in Machakos County, Kenya. Last season she lost 40% of her crop to gray leaf spot -- $144 she could not afford to lose." (b) The problem: diagnosis takes 2-4 weeks via extension officer visit. Disease spreads. (c) The CropSense moment: 10-second diagnosis. Multilingual advisory. Weather-aware timing. (d) The impact: scale from Amina to 500M smallholder farmers. SDG alignment. (e) The ask: "What if every farmer had an agronomist in their pocket?" |
| 2.6 | Research and compile competitive comparison slide | 1.5h | CropSense vs. Plantix vs. DigiFarm vs. Climate Corporation. Column: feature, price, languages, offline capability, target user, AI types used. CropSense wins on: multilingual, weather-aware, SMS-ready, open-source, free. |
| 2.7 | Azure ecosystem callout integration | 1.5h | Add "Powered by Microsoft Azure" badge. In SDG dashboard, show architecture diagram: Azure Custom Vision + Azure OpenAI + Open-Meteo. Add tooltip explanations. Script verbal Azure callouts for demo. |
| 2.8 | Responsible AI panel in UI | 1.5h | Dedicated section showing: confidence disclaimers, data privacy statement, bias acknowledgment (lab vs. field images), "AI-generated guidance" label, model limitations, extension officer escalation. |
| 2.9 | UI polish: consistent styling, mobile-responsive layout | 2h | Apply shared Streamlit theme. Ensure all pages look cohesive. Test on mobile viewport (many demos are shown on projectors). |
| 2.10 | Add demo-day error handling | 1.5h | Graceful fallbacks: if CV API timeout -> load cached result. If LLM API timeout -> show pre-generated advisory. If weather API fails -> show "illustrative" weather with label. Never show a stack trace during demo. |
| 2.11 | First demo rehearsal (Day 11) | 2h | Run through full 5-minute demo: Problem (30s) -> Solution overview (45s) -> Live demo: Farmer Mode (90s) -> Extension Officer Mode (60s) -> SDG Dashboard (30s) -> Impact + Responsible AI (30s) -> Close (15s). Time it. Identify weak spots. |
| 2.12 | Write memory entry for Sprint 2 decisions | 0.5h | Document feature scope decisions, narrative choices |

**Sprint 2 Total:** 31.5h (within 32h budget)

**Definition of Done:**
- [ ] Extension Officer Mode works with dual persona toggle
- [ ] SDG dashboard displays impact metrics with real citations
- [ ] Treatment Cost Estimator shows cost-of-inaction ($144/season)
- [ ] Diagnosis History Timeline tracks session diagnoses
- [ ] Demo script written and timed at ~5 minutes
- [ ] Competitive comparison slide complete
- [ ] Azure ecosystem callouts integrated into UI and script
- [ ] Responsible AI panel visible in app
- [ ] First demo rehearsal completed, weak spots documented
- [ ] Feature freeze enforced at end of Sprint 2

---

### Sprint 3 — Demo Readiness + Buffer (Days 12-14 | March 27-29 | 20h)

**Sprint Goal:** Demo-ready application with rehearsed presentation, tested backup plan, and polished narrative. Zero new features.

| # | Task | Est. Hours | Notes |
|---|------|-----------|-------|
| 3.1 | Full end-to-end testing with real leaf photos | 2h | Test every disease class. Test healthy leaf. Test ambiguous/unclear image. Test non-leaf image (error handling). Document results. |
| 3.2 | Multilingual output quality review | 1.5h | Review Swahili and French advisory outputs for accuracy, cultural appropriateness, and actionability. Fix prompt if translations are awkward. Ideally get native speaker review. |
| 3.3 | Demo dry run #2 with full script | 2h | Full 5-minute rehearsal. Practice transitions. Test live API calls. Practice with backup cached results. Time each section. |
| 3.4 | Prepare Q&A responses | 2h | Rehearse answers to: (1) "PlantVillage is lab data -- real field accuracy?" (2) "Custom Vision retiring 2028 -- why build on it?" (3) "Seen PlantVillage classifiers before -- what's different?" (4) "How does this actually reach farmers without smartphones?" (5) "What about crops not in your training set?" |
| 3.5 | Build demo failure contingency plan | 1.5h | Document and test: (a) API timeout -> cached results with "live demo experienced temporary delay" script. (b) Wrong classification -> "This demonstrates why confidence scores and extension officer escalation are built into the system." (c) Internet down -> fully cached demo with all results pre-loaded. |
| 3.6 | SDG impact statistics final review | 1h | Verify all cited numbers have sources. Ensure $144/season calculation is defensible. Verify "10 seconds vs 2-4 weeks" claim. |
| 3.7 | Demo dry run #3 (final) | 2h | Full rehearsal with Person B support (if available Day 12-14 per resource allocation). Practice the "Amina Moment": upload real leaf -> Swahili advisory -> SMS preview -> weather context. This must land perfectly. |
| 3.8 | Polish UI edge cases | 1.5h | Fix any visual glitches found in rehearsals. Ensure loading states are smooth. Ensure error messages are user-friendly. |
| 3.9 | Verify Azure credit usage + remaining budget | 0.5h | Check Azure portal. Ensure no surprise charges. Confirm all services will remain active through April 16. |
| 3.10 | Prepare presentation materials | 2h | Architecture diagram slide, SDG alignment slide, competitive comparison slide, impact statistics slide. These supplement the live demo. |
| 3.11 | Final deployment verification | 1h | Confirm app runs in the canonical demo targets (local primary, Streamlit Community Cloud backup). Test from a clean browser. Clear cache and verify cold-start experience. |
| 3.12 | Record backup demo video | 2h | Screen-record a perfect run of the full demo flow. If live demo fails catastrophically on April 16, this video saves the presentation. |
| 3.13 | Final memory entry + status update | 0.5h | Update `.status.md`, write final memory entry with ship state |

**Sprint 3 Total:** 19.5h (within 20h budget with 0.5h slack)

**Definition of Done:**
- [ ] All 3 AI systems tested with real inputs
- [ ] Demo rehearsed 3+ times, timed at ~5 minutes
- [ ] Q&A responses rehearsed for top 5 anticipated questions
- [ ] Backup plan tested (cached results load correctly)
- [ ] Backup demo video recorded
- [ ] Azure credits verified sufficient through April 16
- [ ] Presentation slides complete
- [ ] App deployed and verified on target platform
- [ ] All written deliverables (narrative, competitive comparison, SDG alignment) finalized

---

## 2. Milestone Checkpoints

| Milestone | Day | Date | Deliverable | Success Criteria |
|-----------|-----|------|-------------|-----------------|
| **M0: Azure Live** | 1 | Mar 16 | Azure Custom Vision + OpenAI provisioned, first model training run complete | Both API endpoints respond successfully |
| **M1: Data Ready** | 1 | Mar 16 | PlantVillage subset curated (700+ images, 5-7 classes), uploaded to Custom Vision | Training initiated, initial accuracy metric available |
| **M2: Vertical Slice** | 4 | Mar 19 | **CRITICAL GATE** -- Working pipeline: photo upload -> disease classification -> LLM advisory -> Streamlit display | End-to-end flow completes in <15s with >80% accuracy on known diseases |
| **M3: 3-System Integration** | 7 | Mar 22 | All 3 AI systems (CV + LLM + Weather) working together, multilingual output verified | Weather-aware advisory generates in 3 languages |
| **M4: Feature Complete** | 9 | Mar 24 | Extension Officer Mode, SDG dashboard, cost estimator, history timeline all functional | Dual persona toggle works, all pages render correctly |
| **M5: Feature Freeze** | 9 | Mar 24 | No new features after this point | Code changes limited to bug fixes and polish |
| **M6: Narrative Ready** | 11 | Mar 26 | Demo script written, first rehearsal complete | Script timed at ~5 minutes, Amina story arc complete |
| **M7: Demo Ready** | 13 | Mar 28 | 3 rehearsals complete, backup plan tested, slides done | Can run demo with and without live API |
| **M8: Ship** | 14 | Mar 29 | Final deployment verified, backup video recorded | Clean cold-start, all deliverables committed |

---

## 3. Risk Gates

### Day 4 Gate: Vertical Slice (HIGHEST PRIORITY)

**Pass Criteria:** Photo upload -> classification (>80% on known diseases, <15s) -> advisory display.

**If PASS:** Proceed to Sprint 1B (weather + multilingual). Full plan continues.

**If FAIL -- Classification accuracy <70%:**
1. Re-curate training data: reduce to 3-4 most visually distinct diseases only
2. Use "Advanced Training" with 1-hour budget
3. If still <70% after re-training: switch from Azure Custom Vision to a pre-trained PlantVillage model from Hugging Face (e.g., `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`). This sacrifices the Azure ecosystem story but saves the pipeline.

**If FAIL -- LLM advisory quality poor:**
1. Iterate on prompt template (2h budget)
2. Switch from GPT-4o-mini to GPT-4o (higher quality, higher cost -- still within $100 budget for demo-level usage)
3. If Azure OpenAI access delayed: temporarily use OpenAI API directly, then migrate back to Azure endpoint before demo

**If FAIL -- Streamlit integration broken:**
1. Debug for 2h maximum
2. If unresolvable: build a minimal Flask app with HTML form upload + JSON response display
3. Migrate back to Streamlit once issue is identified

**If ALL THREE FAIL by end of Day 5:** Escalate to team. Consider pivoting to a simpler concept (EduBridge -- adaptive LLM tutor, no CV pipeline needed). This is a last resort.

### Weather Integration Gate (Day 7)

**Pass:** Open-Meteo API returns forecast data for Kenyan coordinates and LLM incorporates weather context.

**If FAIL -- API data gaps for sub-Saharan Africa:**
1. Use mock weather data with clear "illustrative data" label in UI
2. Weather panel still shows in demo with disclaimer
3. Verbal script: "In production, CropSense integrates live weather. For this demo, we show representative forecast data for Machakos County."

**If FAIL -- LLM does not meaningfully use weather context:**
1. Hardcode weather-advisory mapping rules (rain forecast -> delay fungicide, dry spell -> increase irrigation)
2. Inject weather-adjusted text without LLM involvement
3. Still counts as "weather-aware" for judging purposes

### De-Scoping Priority (what gets cut first)

If time pressure forces cuts, remove in this order (last item = cut first):

1. **KEEP (non-negotiable):** Vertical slice (CV + LLM + display), confidence gradient, multilingual
2. **KEEP (high value):** Extension Officer Mode, SDG dashboard, weather integration
3. **CUT THIRD:** Diagnosis History Timeline (3h saved)
4. **CUT SECOND:** Treatment Cost Estimator (3h saved)
5. **CUT FIRST:** Backup demo video recording (2h saved)

### Azure Credit Risk

**If Azure for Students credits unavailable:**
1. Try Azure free trial ($200 credits, requires credit card)
2. If neither works: use Custom Vision F0 free tier (5K images, 10K predictions) + OpenAI API directly (not Azure OpenAI)
3. Re-script Azure callouts as: "Designed for the Azure ecosystem" rather than "Built on Azure"

---

## 4. Narrative Development Plan

### Narrative Timeline

| Day | Narrative Activity | Output |
|-----|-------------------|--------|
| 0-1 | Research: FAO/World Bank statistics, Amina persona details, competitive landscape | Fact sheet with all cited statistics |
| 4 | Draft opening hook (2 sentences that frame the problem) | "Amina farms 2 acres of maize in Machakos County, Kenya..." |
| 7 | Draft full narrative arc (500 words) | Problem -> Discovery -> Transformation -> Scale |
| 8-9 | Write demo script (5-minute timed) | Section-by-section script with transitions |
| 10 | Compile SDG impact slide + competitive comparison slide | Presentation materials |
| 11 | First rehearsal -- identify narrative weak spots | Rehearsal notes |
| 12 | Revise script based on rehearsal | Updated script |
| 13 | Second + third rehearsal | Polished delivery |

### The "Amina" Story Arc

**Act 1 -- The Problem (30 seconds):**
"Amina farms 2 acres of maize in Machakos County, Kenya. She feeds her family and sells surplus at the local market -- $360 per season when yields are good. Last season, gray leaf spot destroyed 40% of her crop before she could identify it. That is $144 she will never recover. To get a diagnosis, Amina must walk 12 kilometers to the nearest agricultural extension office, wait days for an officer to visit, and by then the disease has spread to her neighbor's fields. This is not Amina's problem alone. 500 million smallholder farms face the same reality."

**Act 2 -- The Solution (45 seconds):**
"CropSense AI puts an agronomist in Amina's pocket. She photographs a diseased leaf with her phone. In 10 seconds -- not 2 to 4 weeks -- she receives a diagnosis, a treatment plan, and a weather-aware recommendation, all in Swahili. No app download required for the SMS version. No subscription fee. No agronomist visit needed for the 85% of cases CropSense can identify with high confidence."

**Act 3 -- Live Demo (2.5 minutes):**
- Upload real leaf photo (not a PlantVillage training image)
- Show classification result with confidence gradient
- Show multilingual advisory (toggle English -> Swahili)
- Show weather panel: "Rain in 3 days -- apply fungicide TODAY"
- Show SMS preview: full advisory in <=160 characters
- Toggle to Extension Officer Mode: technical view with batch processing
- Show SDG dashboard with impact metrics

**Act 4 -- Impact + Close (1 minute):**
- Cost-of-inaction: $144/season per farmer, $72 billion/year globally
- Time-to-diagnosis: 10 seconds vs. 2-4 weeks
- SDG 2: Reducing the 20-40% crop loss that costs $220B/year
- SDG 13: Weather-aware recommendations reduce fertilizer waste
- SDG 10: Democratizing precision agriculture for the 500M farms that have never had it
- "Every precision agriculture tool on the market is built for John Deere tractors. CropSense is the first built for Amina."

### SDG Impact Statistics (with sources)

| Statistic | Value | Source |
|-----------|-------|--------|
| People facing food insecurity | 820+ million | FAO State of Food Security 2025 |
| Smallholder farms globally | 500 million | FAO |
| Share of local food from smallholders (LMICs) | ~60% | FAO |
| Annual crop loss from disease/pests | 20-40% of production | FAO |
| Economic cost of crop losses | $220 billion/year | FAO |
| Amina's seasonal revenue (2 acres maize, Kenya) | ~$360 | World Bank agricultural data |
| Amina's cost-of-inaction (40% loss) | $144/season | Calculated: $360 x 0.40 |
| Time to traditional diagnosis | 2-4 weeks | Agricultural extension service averages |
| CropSense diagnosis time | ~10 seconds | Measured pipeline latency |
| ROI of agricultural development investment | $8 return per $1 invested | World Bank |

### Competitive Positioning

| Feature | CropSense AI | Plantix (PEAT) | DigiFarm (Safaricom) | Climate Corp |
|---------|-------------|----------------|---------------------|-------------|
| Disease detection | Yes (Azure CV) | Yes (proprietary) | No | No |
| Multilingual advisory | 3 languages | 18 languages | Swahili only | English only |
| Weather-aware advice | Yes (Open-Meteo) | No | Basic | Yes |
| SMS-ready output | Yes (<160 chars) | No (app only) | Yes | No |
| Cost | Free (open-source) | Free (ad-supported) | Carrier-tied | $1000+/year |
| Target user | Smallholder farmers | All farmers | Kenyan farmers | Industrial farms |
| AI types | CV + LLM + Weather | CV only | SMS chatbot | ML + Weather |
| Open-source | Yes | No | No | No |

**Key differentiator script line:** "Plantix can identify diseases but cannot advise. DigiFarm can advise but cannot diagnose. Climate Corporation can do both but costs $1,000 per year and only works in English on industrial farms. CropSense is the first platform that diagnoses, advises, and contextualizes with weather -- in the farmer's language, at zero cost."

### Demo Choreography (Minute-by-Minute)

| Time | Action | Speaker Notes | Screen Shows |
|------|--------|---------------|-------------|
| 0:00-0:30 | Tell Amina's story | Memorized, no reading. Eye contact with judges. | Title slide with Amina's photo (stock or AI-generated Kenyan farmer) |
| 0:30-1:15 | Explain CropSense concept + architecture | Point to architecture diagram. Name Azure Custom Vision, Azure OpenAI, Open-Meteo explicitly. | Architecture slide with Azure logos |
| 1:15-1:30 | Transition to live demo | "Let me show you what Amina sees." Switch to Streamlit app. | App loads -- Farmer Mode |
| 1:30-2:00 | Upload real leaf photo | Use a REAL photo, not PlantVillage. Narrate while loading: "This is a maize leaf photographed in Machakos County." | Image upload + loading spinner |
| 2:00-2:30 | Show diagnosis result | "Gray leaf spot, 91% confidence. Notice the confidence gradient -- green means CropSense is highly certain." | Diagnosis card + confidence gradient |
| 2:30-3:00 | Show advisory + toggle language | "Here is the treatment advisory in English. Now watch -- I switch to Swahili." Toggle language. Read the Swahili advisory aloud (or phonetically). | Advisory card, language selector |
| 3:00-3:15 | Show weather context | "Open-Meteo shows rain in 3 days. CropSense adjusts: apply fungicide TODAY, not Thursday." | Weather panel |
| 3:15-3:30 | Show SMS preview | "This is the same advisory in 152 characters. SMS-ready for feature phones." | SMS preview card |
| 3:30-4:00 | Toggle to Extension Officer Mode | "Now the same data, but for the agricultural officer who serves 200 farmers." Show batch view, technical details. | Extension officer page |
| 4:00-4:30 | Show SDG dashboard | "Three SDGs. Quantified impact. Not aspirational -- grounded in FAO data." | SDG dashboard with charts |
| 4:30-5:00 | Close with impact statement | Return to Amina. "$144 saved. 10 seconds instead of 2 weeks. Built entirely on Azure." End: "What if every farmer had an agronomist in their pocket?" | Impact slide or return to title |

---

## 5. Demo Readiness Checklist

### Working AI Pipeline (3 Systems)

- [ ] **System 1 -- Azure Custom Vision:** Classifies 5-7 crop diseases with >85% accuracy. Returns disease label + confidence in <5 seconds.
- [ ] **System 2 -- Azure OpenAI GPT-4o-mini:** Generates contextual, actionable advisory. Works in English, Swahili, and French. Advisory is culturally appropriate and uses local terminology.
- [ ] **System 3 -- Open-Meteo Weather:** Returns 7-day forecast for specified coordinates. Weather context is injected into LLM advisory and adjusts recommendations.

### Real Leaf Photo

- [ ] At least 1 real diseased leaf photo sourced (NOT from PlantVillage training set)
- [ ] Photo tested through full pipeline -- classification is correct
- [ ] Photo is visually compelling on screen (clear, well-lit)

### Multilingual Output

- [ ] English advisory tested -- accurate and actionable
- [ ] Swahili advisory tested -- grammatically correct, culturally appropriate
- [ ] French advisory tested -- grammatically correct
- [ ] Language toggle works smoothly in UI

### Extension Officer Mode Toggle

- [ ] Dual persona toggle works (Farmer Mode <-> Extension Officer Mode)
- [ ] Extension Officer view shows technical disease details
- [ ] Extension Officer view shows batch processing capability
- [ ] Different LLM prompt produces appropriately technical output

### SDG Dashboard

- [ ] SDG 2 (Zero Hunger) metrics displayed with citations
- [ ] SDG 13 (Climate Action) metrics displayed with citations
- [ ] SDG 10 (Reduced Inequalities) metrics displayed with citations
- [ ] Interactive Plotly charts render correctly
- [ ] All statistics have source attributions

### Azure Ecosystem Callouts

- [ ] "Powered by Azure" badge visible in app
- [ ] Architecture diagram shows Azure Custom Vision + Azure OpenAI
- [ ] Demo script includes 3+ verbal Azure mentions
- [ ] Microsoft sustainability commitment referenced in SDG section

### Backup Plan

- [ ] `demo_scenarios.json` contains cached results for 5+ scenarios
- [ ] Fallback code loads cached results when API times out
- [ ] Tested: disable internet -> demo still runs with cached data
- [ ] Backup demo video recorded (screen capture of perfect run)
- [ ] Scripted recovery lines for common failure modes

### Additional Demo Elements

- [ ] Confidence Gradient UI component works and is visually clear
- [ ] SMS preview shows advisory in <=160 characters
- [ ] Treatment Cost Estimator shows $144/season cost-of-inaction
- [ ] Diagnosis History Timeline shows session activity
- [ ] Responsible AI disclaimers visible in app
- [ ] Competitive comparison slide ready
- [ ] Presentation slides complete (architecture, SDG, impact, competitive)
- [ ] Demo rehearsed 3+ times
- [ ] Q&A responses prepared for top 5 questions

---

## 6. Critical Path

```
Day 0: Azure provisioning ─────────────────────────────────────────────────┐
                                                                           │
Day 0-1: PlantVillage data curation + upload + first training ─────────────┤
                                                                           │
Day 2: Custom Vision model evaluation ────────────────────────┐            │
  (BLOCKER: >80% accuracy needed)                             │            │
                                                              v            │
Day 2-3: CV service + LLM service build ──────────────────────┤            │
                                                              │            │
Day 3-4: Streamlit UI + vertical slice wiring ────────────────┤            │
                                                              v            │
Day 4: *** VERTICAL SLICE GATE *** ───────────────────────────┤            │
  (BLOCKER: full pipeline must work)                          │            │
                                                              v            │
Day 5-6: Weather integration ─────────────────────────────────┤            │
                                                              │            │
Day 5-7: Multilingual + confidence UI ────────────────────────┤            │
                                                              v            │
Day 7: 3-system integration verified ─────────────────────────┤            │
                                                              │            │
Day 8-9: Extension Officer Mode ──────────────────────────────┤            │
  (FEATURE FREEZE Day 9)                                      │            │
                                                              v            │
Day 10-11: Narrative + first rehearsal ───────────────────────┤            │
                                                              v            │
Day 12-14: Rehearsal + polish + backup ───────────────────────┘            │
                                                                           │
Azure credits ─────────────────────────────────────────── must last ───────┘
```

### Highest Risk AI System: Azure Custom Vision

**Why:** This is the only system that cannot be "prompt-engineered" into working. Either the model classifies diseases accurately or it does not. Unlike the LLM (where prompt iteration can fix quality issues) and the weather API (where mock data is an acceptable fallback), the CV model accuracy is a hard technical constraint that determines whether the entire project has credibility.

**Risk factors:**
- PlantVillage images are lab-controlled; real-world field photos will have lower accuracy
- Azure Custom Vision is a managed service -- limited control over model architecture
- Training data quality directly determines demo quality
- Re-training takes 15-60 minutes per iteration (limits how many iterations fit in Days 1-3)

**Mitigation:** Prioritize data curation quality over data quantity. Select the 5-7 most visually distinct diseases. Allocate 4 training iterations (Sprint 0 + Sprint 1 Days 2-3). If accuracy stalls below 80%, reduce to 3-4 diseases immediately.

### Zero-Slack Items

These items have NO buffer. If they slip, downstream tasks are delayed:

| Item | Day | Consequence of Slip |
|------|-----|---------------------|
| Azure account provisioning | 0 | Cannot start any Azure work. Entire Sprint 0 blocked. |
| Custom Vision first training run | 1 | Cannot evaluate accuracy Day 2. Vertical slice gate at risk. |
| Vertical slice working | 4 | Triggers fallback planning. Sprint 1B scope changes. |
| Feature freeze | 9 | Narrative development delayed. Demo rehearsal compressed. |
| First demo rehearsal | 11 | Fewer iterations to fix narrative problems. |

---

## 7. Azure Setup Checklist (Day 0-1)

### Hour 1: Account and Credits

- [ ] Navigate to [azure.microsoft.com/free/students](https://azure.microsoft.com/en-us/free/students)
- [ ] Sign in with .edu email
- [ ] Verify student status (may take 10-30 minutes for verification)
- [ ] Confirm $100 credit appears in billing dashboard
- [ ] **If student verification fails:** Sign up for Azure free trial at [azure.microsoft.com/free](https://azure.microsoft.com/en-us/free) ($200 credits, requires credit card)
- [ ] Set up billing alert at $50 and $80 thresholds to avoid surprise charges

### Hour 2: Azure Custom Vision

- [ ] Navigate to [customvision.ai](https://www.customvision.ai)
- [ ] Create new project:
  - **Name:** CropSense-Disease-Classifier
  - **Resource:** Create new Custom Vision resource (S0 tier if using credits, F0 if conserving)
  - **Project Type:** Classification
  - **Classification Type:** Multiclass (one disease per image)
  - **Domain:** General (compact) -- enables edge export if needed later
- [ ] Note the **Prediction Endpoint URL** and **Prediction Key**
- [ ] Note the **Training Endpoint URL** and **Training Key**
- [ ] Store keys in `.env` file (never commit to git):
  ```
  CUSTOM_VISION_ENDPOINT=https://<region>.api.cognitive.microsoft.com
  CUSTOM_VISION_PREDICTION_KEY=<key>
  CUSTOM_VISION_PROJECT_ID=<project-id>
  CUSTOM_VISION_PUBLISHED_NAME=<iteration-name>
  ```

### Hour 3: Azure OpenAI

- [ ] Navigate to Azure Portal -> Create Resource -> Azure OpenAI
- [ ] **If access not pre-approved:** Submit access request form (may take 1-2 business days -- do this FIRST on Day 0)
- [ ] **Fallback if access delayed:** Use OpenAI API directly (`api.openai.com`) with same GPT-4o-mini model. Migrate to Azure OpenAI endpoint once approved.
- [ ] Create Azure OpenAI resource:
  - **Region:** East US (best availability for GPT-4o-mini)
  - **Pricing tier:** S0
- [ ] Deploy model:
  - **Model:** gpt-4o-mini
  - **Deployment name:** cropsense-advisory
  - **Tokens per minute rate limit:** 30K (sufficient for demo usage)
- [ ] Note the **Endpoint URL** and **API Key**
- [ ] Store in `.env`:
  ```
  AZURE_OPENAI_ENDPOINT=https://<resource-name>.openai.azure.com
  AZURE_OPENAI_KEY=<key>
  AZURE_OPENAI_DEPLOYMENT=cropsense-advisory
  AZURE_OPENAI_API_VERSION=2024-10-21
  ```

### Hour 4: Verify All Services

- [ ] Test Custom Vision: upload a sample image via the web UI, verify prediction returns
- [ ] Test Azure OpenAI: send a test prompt via REST API or Python SDK, verify response
- [ ] Test Open-Meteo: `curl "https://api.open-meteo.com/v1/forecast?latitude=-1.2921&longitude=36.8219&daily=temperature_2m_max,precipitation_sum&timezone=Africa/Nairobi"` -- verify JSON response with Kenyan weather data
- [ ] Create `.env.example` with all variable names (no values) and commit to repo
- [ ] **Critical:** Verify `.env` is in `.gitignore` -- never commit API keys

### Budget Tracking

| Service | Estimated Usage (2 weeks) | Estimated Cost |
|---------|--------------------------|----------------|
| Custom Vision training | 3-5 iterations x 15-60 min | $10-50 |
| Custom Vision predictions | ~500 predictions (dev + testing + demo) | $1 |
| Azure OpenAI GPT-4o-mini | ~2M input + 500K output tokens | $0.60 |
| Streamlit Community Cloud | Backup deployment only | $0 |
| Open-Meteo | Unlimited (free tier) | $0 |
| **Total** | | **$12-52** (well within $100 budget) |

---

## Hour Budget Summary

| Sprint | Days | Hours | Key Deliverable |
|--------|------|-------|----------------|
| Sprint 0 | 0-1 | 15h | Azure provisioned, data curated, project scaffolded |
| Sprint 1A | 2-4 | 22h | Vertical slice working (Day 4 gate) |
| Sprint 1B | 5-7 | 19.5h | Weather + multilingual + confidence UI |
| Sprint 2 | 8-11 | 31.5h | Extension Officer Mode, SDG dashboard, narrative, first rehearsal |
| Sprint 3 | 12-14 | 19.5h | Polish, rehearsal x2, backup plan, deployment |
| **Total** | | **107.5h** | **~4.5h buffer from 112h allocation** |

### Narrative Effort Distribution

Per the Strategic Review mandate that narrative needs 45% of effort:

| Activity | Hours | % of Total |
|----------|-------|-----------|
| Pure technical (CV, LLM, weather, services, tests) | 45h | 42% |
| Technical with narrative value (SDG dashboard, confidence UI, Extension Officer Mode, SMS preview, treatment cost estimator) | 22h | 20% |
| Pure narrative (story writing, demo script, rehearsals, Q&A prep, slides, competitive analysis, backup video) | 22h | 20% |
| Infrastructure + setup (Azure, scaffolding, shared infra) | 11h | 10% |
| Research (statistics, competitive landscape, real photo sourcing) | 5h | 5% |
| Buffer + documentation | 3.5h | 3% |
| **Technical + narrative-adjacent** | **67h** | **62%** |
| **Narrative + research** | **27h** | **25%** |

Note: The 45% narrative target from the Strategic Review is interpreted as narrative-impacting work (features that directly serve the demo story + pure narrative work), which totals ~44h or 41%. The remaining gap is covered by the fact that features like the confidence gradient and Extension Officer Mode exist solely to strengthen the narrative, not to add technical depth.

---

## Appendix: Key Decisions Log

| Decision | Rationale | Source |
|----------|-----------|--------|
| Streamlit, not Next.js | PM/CTO mandate. Consistency with other categories. Faster to build. | Strategic Review |
| GPT-4o-mini, not GPT-4o | 16x cheaper, sufficient quality for agricultural advisory, stays within $100 budget | PRD Section Cat 5 |
| 5-7 diseases, not 26 | Higher accuracy on fewer classes. Demo only needs to show capability, not exhaustive coverage. | CTO Review |
| Open-Meteo, not Azure Weather Maps | Free, no API key, global coverage, sufficient for demo | PLAN.md |
| Cached demo backup | Live API calls during demo are high-risk. Cached results ensure demo never fails. | Strategic Review |
| Feature freeze Day 9 | Protects 5 days of narrative development and rehearsal | Strategic Review |
| Extension Officer Mode as must-add | Doubles impact narrative, highest ROI feature per Strategic Review | Strategic Review |
