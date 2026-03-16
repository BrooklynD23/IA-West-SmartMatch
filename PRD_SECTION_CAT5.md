## Category 5: CropSense AI — Precision Agriculture for Smallholder Farmers
**Sponsor:** Avanade (Creative SDG Track) | **CTO Tier:** 1.5 (conditional on Day 4 gate) | **Verdict:** Approved with Revisions

**Planning Note (2026-03-15):** For implementation sequencing and canonical scope, treat `STRATEGIC_REVIEW.md`, `MASTER_SPRINT_PLAN.md`, and `Category 5 - Avanade Creative SDG/SPRINT_PLAN.md` as the source of truth. Canonical MVP scope is a 3-system Streamlit build: Azure Custom Vision + Azure OpenAI + Open-Meteo.

### Problem Statement

Globally, 570 million farms are smallholdings under 2 hectares, operating on just 9% of agricultural land yet producing roughly 60% of local food in low- and middle-income countries (FAO). An estimated 1.7 billion people now live in areas where crop yields are falling due to human-induced land degradation (FAO State of Food and Agriculture 2025). The WFP 2026 Global Outlook reports a 20% increase in the number of people facing acute food insecurity since 2020, with 16 hunger hotspots deepening across sub-Saharan Africa and South Asia. Crop diseases and pests cause an estimated 20-40% of global crop production losses annually (FAO), costing developing economies over $220 billion per year. Smallholder farmers -- who lack access to diagnostic specialists, weather intelligence, and precision agriculture tools designed for industrial-scale operations -- bear a disproportionate share of these losses. Existing solutions like Plantix and DigiFarm address fragments of this problem but none integrate computer vision diagnostics, contextual LLM advisory, and weather intelligence into a single SMS-accessible platform designed for low-bandwidth, multilingual environments.

### Proposed Solution

CropSense AI is a mobile-first agricultural intelligence platform that enables smallholder farmers to photograph a diseased crop leaf and receive an AI-generated diagnosis with actionable, localized treatment advice -- all within a single interaction. The system combines three AI subsystems within CTO-mandated limits: (1) Azure Custom Vision trained on the PlantVillage dataset for crop disease classification, (2) Azure OpenAI GPT-4o-mini for generating plain-language, multilingual agricultural advisory grounded in the diagnosis and local context, and (3) Open-Meteo weather API integration to contextualize recommendations with hyperlocal forecast data. The platform outputs SMS-length advisories (under 160 characters) alongside a full web dashboard, making it accessible to farmers on feature phones in low-connectivity regions. The entire experience is anchored around "Amina," a composite persona representing a 2-acre maize farmer in Kenya, whose story drives both the product design and the demo narrative.

### Tech Stack

| Layer | Technology | Purpose | Free Tier? | Cost Estimate (2 weeks) |
|-------|-----------|---------|------------|------------------------|
| Computer Vision | Azure Custom Vision (S0) | Crop disease classification from leaf images (PlantVillage: 54K images, 14 crops, 26 diseases) | F0: 2 projects, 5K images, 10K predictions/mo | $0 with Azure for Students credits ($100 budget); S0 training ~$10/hr, predictions ~$2/1K |
| LLM Advisory | Azure OpenAI GPT-4o-mini | Multilingual plain-language treatment recommendations, contextual farming advice | No free tier; pay-per-token | ~$2-5 total (est. 5M input + 2M output tokens over 2 weeks at $0.15/$0.60 per 1M tokens) |
| Weather Intelligence | Open-Meteo API | 14-day hyperlocal weather forecast, historical climate data for sub-Saharan Africa | Yes -- free for non-commercial use, no API key required | $0 |
| Frontend/App Shell | Streamlit | Farmer Mode, Extension Officer Mode, SDG dashboard, SMS output preview, confidence-aware UI | Yes — open source, local-first demo flow | $0 |
| SMS Output Mode | UI-simulated SMS view (no Twilio) | Renders advisory in SMS-format (<=160 chars) within the web UI; demonstrates SMS-readiness without requiring Twilio integration | N/A (UI only) | $0 |
| Hosting/Backup | Local Streamlit runtime + Streamlit Community Cloud backup | Local demo as primary; cloud backup if local environment fails | Yes | $0 |
| Data | PlantVillage Dataset (GitHub) | 54,306 labeled leaf images for Custom Vision training | Open access (GitHub/Kaggle) | $0 |

### API & Service Pricing Breakdown

**Azure Custom Vision (as of March 2026):**
- F0 (Free): 2 projects, 5,000 training images, 10,000 predictions/month, 1 hour training/month
- S0 (Standard): Training at $10/hour, image storage at $0.70/1,000 images, predictions at $2/1,000 transactions
- Source: [Azure Custom Vision Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/custom-vision-service/)
- Note: Azure Custom Vision is scheduled for retirement on 9/25/2028 but remains fully supported through that date

**Azure OpenAI (as of March 2026):**
- GPT-4o: $2.50/1M input tokens, $10.00/1M output tokens (global deployment)
- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens (global deployment)
- Recommendation: Use GPT-4o-mini for all advisory generation (sufficient quality for agricultural advice, 16x cheaper than GPT-4o)
- Source: [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)

**Open-Meteo API:**
- Free for non-commercial use (hackathon qualifies), no API key required
- Global coverage at up to 1 km resolution, including sub-Saharan Africa
- Commercial plans available if needed post-hackathon
- Source: [Open-Meteo Pricing](https://open-meteo.com/en/pricing)

**Twilio SMS (reference only -- NOT included in MVP):**
- US: $0.0083/message outbound; Kenya: $0.0085-$0.2336/message depending on carrier
- Phone number rental: $1.15/month (local US), $2.15/month (toll-free)
- Per CTO directive: Do not implement Twilio unless core CV + LLM + weather pipeline is complete. Simulate SMS output in UI instead.
- Source: [Twilio SMS Pricing](https://www.twilio.com/en-us/sms/pricing/us)

**Azure for Students Credits:**
- $100 in Azure credits valid for 12 months, no credit card required
- Covers the Azure services needed for this project (Custom Vision and OpenAI)
- Eligibility: Full-time students at accredited degree-granting institutions
- Source: [Azure for Students](https://azure.microsoft.com/en-us/free/students)

**Total estimated cost for 2-week build: $0-$15** (within Azure for Students $100 credit budget, assuming efficient token usage and moderate training iterations)

### Complexity Assessment

| Dimension | Score (1-5) | Justification |
|-----------|-------------|---------------|
| AI/ML Complexity | 3 | Azure Custom Vision abstracts model training; PlantVillage is pre-labeled. LLM advisory uses prompt engineering, not fine-tuning. No custom model architecture needed. |
| Data Requirements | 2 | PlantVillage dataset is open-access with 54K labeled images ready for upload. Open-Meteo requires no data preparation. No proprietary data needed. |
| UI/UX Complexity | 3 | Image upload + diagnosis display + weather panel + SDG dashboard + SMS preview mode. Moderate scope but no real-time features or complex state management. |
| Integration Complexity | 3 | Three API integrations (Custom Vision, Azure OpenAI, Open-Meteo) with sequential orchestration: image -> diagnosis -> LLM advisory enriched with weather context. Straightforward REST APIs. |
| Demo Polish Required | 4 | Avanade judges weight storytelling and innovation highly. The "Amina" narrative, SDG impact visualization, and multilingual demo require significant polish beyond technical functionality. |
| **Average** | **3.0** | Technically manageable within 2 weeks; primary investment is in narrative polish and demo quality rather than engineering complexity. |

### 2-Week Implementation Timeline

| Milestone | Days | Deliverables |
|-----------|------|-------------|
| M1: Azure CV Setup + Data | 1-3 | Azure Custom Vision project created; PlantVillage dataset downloaded, curated (top 10 crops/diseases for demo relevance), and uploaded; initial model trained and validated; baseline accuracy metrics documented (target: >85% on test set) |
| M2: LLM Advisory System (40% dev time) | 4-6 | GPT-4o-mini prompt engineering for agricultural advisory; system prompt with disease-specific treatment templates; multilingual output (English + Swahili + French); confidence-aware responses ("consult local extension officer if confidence < 70%"); SMS-length output formatter (<=160 chars) |
| M3: Weather Integration | 7-8 | Open-Meteo API integration for 14-day forecast by GPS coordinates; weather context injected into LLM advisory prompts ("rain expected in 48 hours -- delay fungicide application"); weather widget in dashboard UI |
| M4: Frontend + SDG Dashboard | 9-10 | Streamlit app with Farmer Mode, diagnosis results page, treatment advisory card, weather panel, confidence gradient UI, SDG impact counter (crops analyzed, farmers helped, estimated yield improvement), SMS output preview mode; responsive design for mobile demo |
| M5: Narrative + Demo Prep | 11-14 | "Amina's Story" narrative video/walkthrough scripted and rehearsed; end-to-end demo flow polished (upload leaf photo -> disease detected -> advisory generated -> weather context shown -> SMS output rendered); SDG alignment slide deck; edge case handling (healthy leaf, unclear image, low confidence); responsible AI disclaimers integrated into UI |

### Team Allocation

**3-Person Team:**
- **Person 1 (ML/Backend Lead):** Azure Custom Vision setup, PlantVillage data curation and upload, model training and iteration, service orchestration connecting CV -> LLM -> Weather, and backup caching for demo reliability
- **Person 2 (LLM/Integration Specialist):** GPT-4o-mini prompt engineering and advisory system (40% of total dev effort), Open-Meteo weather API integration, multilingual output tuning, SMS-format output logic, responsible AI guardrails in prompts
- **Person 3 (Frontend/Narrative Lead):** Streamlit page development, image upload UX, diagnosis results display, SDG impact dashboard, SMS preview mode, "Amina" narrative development, demo script and presentation preparation, slide deck

**5-Person Team:**
- **Person 1 (ML Engineer):** Azure Custom Vision setup, PlantVillage data curation/upload, model training iterations, accuracy benchmarking, confidence calibration
- **Person 2 (Backend/API Developer):** Service integration layer (CV -> LLM -> Weather pipeline), error handling, API response caching, request validation, and demo fallback logic
- **Person 3 (LLM Specialist):** GPT-4o-mini prompt engineering (primary focus), multilingual advisory quality, SMS-format output, confidence-aware response templates, responsible AI guardrails
- **Person 4 (Frontend Developer):** Streamlit frontend, image upload flow, diagnosis UI, weather widget, SDG dashboard, SMS preview mode, mobile-responsive design
- **Person 5 (Narrative/Demo Lead):** "Amina" persona development, demo script and rehearsal, SDG alignment storytelling, presentation materials, user journey video, edge case scenarios for demo, competition research on other teams

### Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Azure Custom Vision accuracy below 80% on real-world images (PlantVillage images are lab-controlled, not field photos) | High | High | Curate training set to most visually distinct diseases; augment with color/segmented variants available in PlantVillage repo; show confidence scores honestly in UI; add "uncertain -- consult expert" fallback for low-confidence predictions |
| Azure for Students credits unavailable or insufficient for team members | Medium | High | Apply for credits immediately (Day 0); use F0 free tier for Custom Vision (5K images, 10K predictions sufficient for demo); GPT-4o-mini is extremely cheap (~$2-5 total); fallback to Azure free trial ($200 credits) if student credits fail |
| LLM generates inaccurate or harmful agricultural advice (wrong treatment, toxic chemical recommendation) | Medium | Critical | Constrain LLM output with structured prompts referencing verified treatment databases; always display confidence scores; include "This is AI-generated guidance -- consult your local agricultural extension officer" disclaimer; test with agronomic expert if available |
| Open-Meteo API has poor resolution or data gaps for sub-Saharan Africa demo regions | Low | Medium | Open-Meteo claims 1 km global resolution; pre-test with Kenyan coordinates during M3; fallback to displaying weather as "illustrative" with mock data for specific demo locations if API gaps found |
| Demo narrative fails to emotionally resonate with judges despite strong tech | Medium | High | Invest 30% of final milestone in narrative polish; use specific, named persona (Amina) rather than abstract "smallholder farmer"; include real FAO statistics; rehearse demo 3+ times; have backup demo script if live API calls fail |
| Scope creep into price prediction, IoT sensors, or Twilio SMS (features explicitly excluded by CTO) | Medium | Medium | Print CTO red lines on team workspace: "Max 3 AI systems (CV + LLM + Weather). No price prediction. No Twilio unless core is done." Review scope at each milestone boundary. |

### Win Probability Assessment
- **CTO Tier:** 1.5 (conditional on Day 4 vertical slice gate)
- **Independent Analysis:** This category rewards storytelling and genuine passion as much as technical depth. CropSense AI has the strongest possible SDG alignment (Zero Hunger, Climate Action, Reduced Inequalities) with quantifiable impact claims backed by FAO data. The 3-system AI architecture (CV + LLM + Weather) demonstrates meaningful AI application without overengineering. The "Amina" narrative -- a named persona with a specific 2-acre maize plot in Kenya -- is exactly the kind of emotionally anchored storytelling that wins creative categories. The primary weakness is the from-scratch build: no existing prototype, no pre-trained model, no provided dataset. Everything must be assembled in 2 weeks. However, Azure Custom Vision dramatically reduces ML complexity, and PlantVillage provides ready-to-use labeled data. The real risk is not technical failure but insufficient demo polish.
- **Demo Moment:** The demo climax is the live "Amina Moment": upload a real photo of a diseased maize leaf, watch Azure Custom Vision identify gray leaf spot with 92% confidence, then see GPT-4o-mini generate a Swahili-language advisory that reads: "Majani yako ya mahindi yanaonyesha ugonjwa wa madoa ya kijivu. Punguza umwagiliaji kwa 30% na weka dawa ya shaba ndani ya saa 48." Below it, the same advice rendered in SMS format under 160 characters. On the side panel, Open-Meteo shows rain forecast in 3 days with an automatic note: "Delay fungicide -- rain expected Thursday." This sequence -- image to multilingual actionable advice in under 10 seconds -- is the moment judges remember.
- **Overall Win Probability:** Execution-dependent: 25-70% with a realistic midpoint around 50%. The newer planning docs are right to widen the range because this category can swing from non-functional to standout based on whether the Day 4 vertical slice lands. A narrow single-point confidence band would be too optimistic for portfolio planning.

### Existing Assets Inventory

This project starts entirely from scratch. The team has no existing prototype, pre-trained model, or provided starter code.

**Available open resources (no team-owned assets):**
- PlantVillage Dataset: 54,306 labeled leaf images across 14 crop species and 26 diseases, available at [github.com/spMohanty/PlantVillage-Dataset](https://github.com/spMohanty/PlantVillage-Dataset) and via Kaggle, TensorFlow Datasets, and Hugging Face Hub
- Open-Meteo API: Free weather API with global coverage, no API key required
- Azure for Students: $100 credits available to eligible team members (requires .edu email verification)
- Azure Custom Vision: Managed service with GUI-based training workflow (no ML framework expertise required)
- FAO/World Bank open data: Statistics for SDG impact quantification

**What must be built from scratch:**
- Custom Vision model trained on curated PlantVillage subset
- LLM advisory prompt system with multilingual output
- Weather integration pipeline
- Full Streamlit application
- Demo narrative and presentation materials

### Responsible AI Considerations

**Accuracy and Harm Prevention:** Agricultural advice directly affects livelihoods and food security. A misdiagnosis could lead a farmer to apply the wrong treatment, wasting scarce resources or damaging crops further. Every advisory must include confidence scores, and predictions below 70% confidence must trigger an explicit "consult your local agricultural extension officer" recommendation rather than potentially incorrect treatment advice.

**Bias in Training Data:** The PlantVillage dataset contains lab-photographed leaves on uniform backgrounds, primarily from North American and Indian crop varieties. Real-world field photos from sub-Saharan Africa -- taken on low-resolution phone cameras, in variable lighting, with soil and debris -- will likely produce lower accuracy. The team must be transparent about this domain gap in the demo and not overstate real-world performance based on test-set accuracy.

**Language and Cultural Sensitivity:** Advisory text generated by GPT-4o-mini in Swahili, French, or other target languages must be reviewed for cultural appropriateness. Agricultural terminology, measurement units (acres vs. hectares), and chemical names must match local conventions. Generic Western farming advice (e.g., "call your agronomist") is meaningless in contexts where extension services are days away.

**Dependency and Access Equity:** The system requires internet connectivity for all three AI subsystems. While the SMS output mode demonstrates awareness of low-bandwidth needs, the actual product still requires a smartphone with camera and data connection. The team should acknowledge this limitation honestly rather than claiming the tool works offline.

**Data Privacy:** No personally identifiable information should be collected or stored. Uploaded leaf images should not be geotagged or linked to individual farmer identities. The system should process images transiently and not retain them beyond the diagnostic session.

**Avoiding Over-Promise:** The impact framing ("10% yield improvement for 500M farms") is powerful for the demo but must be presented as aspirational potential, not a guaranteed outcome. The prototype demonstrates feasibility, not proven field efficacy. Claiming otherwise would be irresponsible, especially to judges evaluating real-world impact potential.
