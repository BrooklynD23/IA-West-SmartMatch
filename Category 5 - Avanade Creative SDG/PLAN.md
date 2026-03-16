# Category 5 — Avanade Creative Category: AI-Powered SDG Solution
**Sponsor:** Avanade | **Event:** CPP AI Hackathon "AI for a Better Future" | April 16, 2026

> **Status update (2026-03-15):** This file is now background ideation only. Canonical planning decisions live in `SPRINT_PLAN.md`, `../MASTER_SPRINT_PLAN.md`, and `../STRATEGIC_REVIEW.md`. Current MVP scope is a 3-system Streamlit build: Azure Custom Vision + Azure OpenAI + Open-Meteo. Earlier references to broader Microsoft platform options are not implementation authority.

---

## 🎯 Challenge Prompt

> *"Identify a real-world problem that you are passionate about and propose an innovative, AI-powered solution — grounded in the United Nations Sustainable Development Goals (SDGs)."*

This is the **most open-ended and creatively free** category. Teams have complete latitude to choose any real-world problem, as long as the solution:
1. Uses AI in a meaningful and describable way
2. Aligns with **up to 3 UN SDGs**
3. Is genuinely innovative — differentiated from what already exists

---

## 📦 Deliverable Requirements

### Required Components

1. **Problem Statement**
   - Clearly identify a real-world problem you care about
   - Explain why it matters (quantify the impact where possible)

2. **SDG Alignment (up to 3 SDGs)**
   - Select the most relevant SDGs
   - Explain HOW each SDG connects to the problem
   - Explain WHY addressing each SDG matters

3. **AI-Powered Solution Proposal**
   - Describe how AI is used (be specific): data analysis, prediction, automation, personalization, accessibility, decision support, generative AI, computer vision, NLP, etc.
   - Explain the potential impact: who benefits, at what scale (local/national/global)

4. **Innovation Framing**
   - What makes this different from existing solutions?
   - How does it reimagine what's possible with AI?

---

## 🏆 Judging Rubric

| Criterion | Weight | What Judges Look For |
|---|---|---|
| **Innovation** | Very High | Is this genuinely creative? Does it reimagine what's possible? |
| **Impact Potential** | High | Who benefits? At what scale? Is the impact concrete and measurable? |
| **AI Application** | High | Is AI used in a meaningful, non-trivial way? Multiple AI types = bonus |
| **SDG Alignment** | Medium | Are the SDG connections genuine and well-argued (not just buzzwords)? |
| **Feasibility** | Medium | Is there a plausible path from concept to prototype to deployment? |
| **Storytelling** | High | Is the passion for the problem genuine and communicated compellingly? |

---

## 💡 Winning Concept Strategy

### Why Avanade Sponsors This Category
Avanade is a Microsoft joint-venture consulting firm with deep focus on:
- **Responsible/inclusive AI** (diversity, accessibility, equity)
- **Sustainability** (Microsoft has a carbon-negative commitment)
- **Digital transformation** for public sector, healthcare, education

**Strong submissions should leverage Microsoft AI ecosystem:**
- **Azure AI / Azure OpenAI** — GPT-4o for core intelligence
- **Microsoft Copilot Studio** — for conversational AI components
- **Azure AI Vision / Document Intelligence** — for computer vision use cases
- **Power Platform** — for no-code/low-code accessibility demonstrations
- **Azure AI for Earth / Planetary Computer** — for sustainability/climate SDG use cases
- **Microsoft Accessibility tools** — for inclusion-focused SDG solutions

---

## 🔥 Recommended Winning Concept: "CropSense AI" — Smallholder Farm Intelligence for Food Security

### Why This Concept Wins

**Passion-driven:** 820+ million people face food insecurity. 500 million smallholder farms feed 70% of the world's population yet have no access to precision agriculture tools.

**SDG Alignment (3 strong picks):**
- **SDG 2: Zero Hunger** — Directly improves crop yields and food security for smallholder farmers
- **SDG 13: Climate Action** — Reduces fertilizer overuse and water waste; helps farmers adapt to climate volatility
- **SDG 10: Reduced Inequalities** — Democratizes precision agriculture tech previously available only to large industrial farms

**AI Stack (Multi-type):**
1. **Computer Vision (Azure AI Vision)** — Smartphone photo → crop disease detection (identify blight, fungal infection, pest damage from leaf images)
2. **Predictive ML (Azure ML)** — Yield forecasting based on soil data, weather patterns, planting dates
3. **LLM (GPT-4o via Azure OpenAI)** — Multi-language advisory ("Your maize shows early signs of gray leaf spot. Reduce irrigation by 30% and apply copper-based fungicide within 48 hours") in the farmer's local language
4. **Time-series forecasting** — Weather + market price prediction to optimize planting/selling timing
5. **RAG (Retrieval-Augmented Generation)** — Ground LLM responses in agronomic research databases

**Architecture:**
```
Input Layer
  └── Smartphone photo of crop/field
  └── SMS/WhatsApp text query (low-bandwidth markets)
  └── Optional: IoT soil sensor data
        ↓
AI Processing Layer
  └── CV model: crop disease classification (confidence + severity)
  └── Weather API integration: 14-day forecast
  └── LLM + RAG: advisory generation in local language
  └── Price prediction: optimal harvest/sell timing
        ↓
Output Layer
  └── Plain-language advisory (SMS-friendly, <160 chars option)
  └── Action priority list (top 3 steps)
  └── Market timing recommendation
  └── Confidence level + "consult local extension officer if..."
```

**Why it's innovative:**
- Offline-first design (SMS fallback for areas with low connectivity)
- Multi-lingual AI advisory (not English-only like most precision ag tools)
- Integrates CV + NLP + forecasting in one accessible tool
- Designed for feature phones, not just smartphones

**Impact framing:**
- A 10% yield improvement for 500M smallholder farms = feeding 50M+ additional people
- Reducing fertilizer overuse by 20% cuts agricultural emissions equivalent to taking 15M cars off the road
- Each $1 invested in agricultural development generates $8 in economic growth in developing economies

---

## 🔬 Alternative Concept Options

### Option B: "EduBridge" — AI Tutor for Underserved Students
**SDGs:** SDG 4 (Quality Education), SDG 10 (Reduced Inequalities), SDG 8 (Decent Work)
**AI:** Adaptive learning LLM tutor that adjusts explanation complexity to reading level, generates practice problems, provides multi-language support, works offline via cached models
**Why it works for Avanade:** Microsoft's education vertical, Accessibility commitments, Azure AI in Education

### Option C: "ClimateGuard" — Community Disaster Preparedness AI
**SDGs:** SDG 13 (Climate Action), SDG 11 (Sustainable Cities), SDG 3 (Good Health)
**AI:** Real-time flood/fire/storm risk prediction at hyper-local level using satellite + weather data; multilingual evacuation route AI; post-disaster resource matching
**Why it works:** Azure AI for Earth/Planetary Computer integration

### Option D: "HealthAccess" — AI Health Navigator for Underserved Communities
**SDGs:** SDG 3 (Good Health), SDG 10 (Reduced Inequalities), SDG 17 (Partnerships)
**AI:** Symptom checker + care navigation for uninsured populations; insurance enrollment guide; appointment scheduling with language support
**Why it works:** Microsoft Health + Accessibility focus

---

## 🔬 Research Directions for the Agent

### Key Questions to Investigate (for CropSense AI)
1. What crop disease datasets exist for training CV models? (PlantVillage dataset — 50K+ images, 26 diseases)
2. What are the leading precision agriculture platforms and their pricing? (John Deere Operations Center, Climate Corporation, Trimble) — where are their gaps for smallholders?
3. How does Azure AI Vision's Custom Vision service work for custom crop disease classification?
4. What languages are most needed for agricultural AI in sub-Saharan Africa, South Asia, and Latin America?
5. What SMS/WhatsApp AI delivery architectures work in low-bandwidth environments?
6. What existing smallholder AI projects exist? (Plantix by PEAT, Hello Tractor, DigiFarm by Safaricom)

### Key Questions (general SDG research)
1. Which SDGs have the most quantifiable impact metrics for demonstration?
2. What does the UN say are the most underfunded/underaddressed SDGs as of 2025-2026?
3. What open datasets exist for each SDG area? (World Bank Open Data, UN Data, NASA Earth Data)
4. What has Microsoft specifically committed to regarding SDG progress? (Microsoft Sustainability commitments)

### Datasets to Use
- **PlantVillage Dataset** — 54,000+ crop disease images: https://github.com/spMohanty/PlantVillage-Dataset
- **FAOSTAT** — UN Food & Agriculture Organization data: https://www.fao.org/faostat/
- **World Bank Open Data** — Poverty, agriculture, development indicators: https://data.worldbank.org/
- **NASA Earthdata** — Climate, weather, land use: https://earthdata.nasa.gov/
- **Microsoft Planetary Computer** — Geospatial analysis + satellite data: https://planetarycomputer.microsoft.com/

---

## 🎨 Prototype MVP Scope (48 hours)

**Must have for CropSense AI:**
- Working crop disease classifier: upload a leaf photo → get disease label + confidence
- Plain-language advisory text (LLM-generated, grounded in disease detected)
- SDG impact visualization: show which SDGs are addressed and quantified impact claims
- Multi-language demo: show same advisory in English + Spanish + one other language

**Nice to have:**
- SMS-friendly output format (under 160 chars)
- Price/market timing integration (mock data okay)
- Demo video of the use case ("Amina, a maize farmer in Kenya, photographs a sick leaf...")

---

## 🧠 Differentiation Angles (How to Win)

1. **Genuine passion narrative** — this category rewards authentic storytelling; the best demos feel like the team *cares* about the problem
2. **Multi-type AI stack** — using CV + LLM + forecasting together signals sophistication beyond a simple chatbot
3. **Equity angle** — design for users who are *not* like Silicon Valley engineers; low-bandwidth, low-literacy, multi-lingual
4. **Quantified impact** — "10% yield improvement × 500M farms = feeding 50M more people" is more memorable than vague impact claims
5. **Microsoft ecosystem** — Azure AI Vision + Azure OpenAI + Planetary Computer = Avanade will recognize and reward this
6. **Innovation framing**: "Every precision ag tool is built for John Deere tractors, not for Amina's 2-acre maize plot. We're the first open-source, SMS-first precision agriculture AI in her language."

---

## 📋 Responsible AI Checklist

- [ ] AI advisory comes with confidence scores + escalation to local agricultural experts
- [ ] No PII collected from farmers
- [ ] Offline/SMS fallback to ensure access equity (not just app-dependent)
- [ ] Transparency: explain why the disease was identified
- [ ] Bias audit: does the CV model work equally well on crop varieties from different regions?
- [ ] Avoid dependency risks: don't create solutions that fail when API is down (resilient design)
- [ ] Cultural sensitivity: advisory language is appropriate for local farming context

---

## 🌍 UN SDGs Reference Guide

| SDG | Title | Strong AI Application Areas |
|---|---|---|
| SDG 1 | No Poverty | Income prediction, economic mobility tools |
| SDG 2 | Zero Hunger | Crop disease detection, yield optimization, food waste reduction |
| SDG 3 | Good Health | Disease prediction, health access navigation, mental health support |
| SDG 4 | Quality Education | Adaptive tutoring, literacy tools, accessibility in learning |
| SDG 5 | Gender Equality | Bias detection, women's economic empowerment tools |
| SDG 6 | Clean Water | Water quality monitoring, leak detection |
| SDG 7 | Affordable Energy | Smart grid optimization, energy access prediction |
| SDG 8 | Decent Work | Skills matching, upskilling platforms |
| SDG 9 | Industry & Innovation | Open-source infrastructure, manufacturing optimization |
| SDG 10 | Reduced Inequalities | Accessibility AI, equity auditing tools |
| SDG 11 | Sustainable Cities | Urban planning AI, smart infrastructure |
| SDG 13 | Climate Action | Emissions forecasting, climate adaptation planning |
| SDG 14 | Life Below Water | Ocean pollution monitoring, fishery management |
| SDG 15 | Life on Land | Deforestation detection, biodiversity monitoring |
| SDG 16 | Peace & Justice | Disinformation detection, legal access tools |
| SDG 17 | Partnerships | Data-sharing platforms, cross-sector collaboration tools |

---

## 🏗️ Technical Stack Recommendation (for CropSense AI)

| Component | Recommended Tool |
|---|---|
| Crop disease CV | Azure Custom Vision OR fine-tuned EfficientNet on PlantVillage |
| LLM advisory | Azure OpenAI GPT-4o (Avanade = Microsoft = aligned) |
| Multi-language | GPT-4o multilingual OR Azure AI Translator |
| Weather data | Open-Meteo API (free) or Azure Weather Maps |
| Price data | FAOSTAT API or World Bank commodities |
| Frontend | Streamlit (fast) or React PWA (for offline capability) |
| Demo | Video walkthrough of full farmer journey |

---

## 📎 Source Files Reference
- `Category 5.txt` — Official challenge prompt text
- No additional files provided — this category requires original research and concept development
