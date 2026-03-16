# Category 1 — Avanade Challenge: AI for Wellbeing (Option B)
**Sponsor:** Avanade | **Event:** CPP AI Hackathon "AI for a Better Future" | April 16, 2026

> **Status update (2026-03-15):** This file is now background ideation only. Canonical planning decisions live in `SPRINT_PLAN.md`, `../MASTER_SPRINT_PLAN.md`, and `../STRATEGIC_REVIEW.md`. Corrected pricing is `$6/user/month` for Viva Insights as an add-on, and the current positioning is "teams outside the Microsoft ecosystem," not "Viva for non-E5."

---

## 🎯 Challenge Prompt

> *"How might we use AI to support wellbeing for students OR tech-industry workers by enabling healthier work- or school-life balance — while clearly avoiding AI as a replacement for professional mental health care?"*

This is **Option B** of the Avanade Challenge. Teams choose **one population** to focus on:
- **Student Wellbeing** — academic load, time management, financial pressure, social stress, transitions into academic life
- **Tech Industry Wellbeing** — burnout risk, boundary-setting, meeting overload, on-call fatigue, hybrid/remote work strain

---

## 📦 Deliverable Requirements

Teams must deliver a **working AI-powered prototype** that:

1. Targets one clearly defined population (students OR tech workers)
2. Uses AI to support wellbeing in a **preventive, supportive, or awareness-based** way
3. Explicitly avoids clinical use cases (no diagnosis, crisis response, or therapy)
4. Demonstrates thoughtful ethical design with safety guardrails clearly stated
5. Considers accessibility and inclusion across diverse user backgrounds

**Suggested formats:** Web app, mobile mockup, dashboard, chatbot interface, or AI-augmented tool

---

## 🚫 Hard Constraints (Non-Negotiable)

Solutions **must not**:
- Diagnose mental health conditions
- Provide counseling, therapy, or crisis intervention
- Position AI as a replacement for licensed mental health professionals

*Reference: The American Psychological Association (APA) has cautioned that generative AI wellness tools should not substitute for professional mental health care.*

---

## 🏆 Judging Rubric

| Criterion | Weight | What Judges Look For |
|---|---|---|
| **Impact** | High | Does it meaningfully improve wellbeing habits for the target population? |
| **Ethical AI Design** | High | Are guardrails clear? Is AI role appropriate (non-clinical)? |
| **Feasibility** | Medium | Can this realistically be built and deployed? |
| **User Experience** | Medium | Is it accessible, inclusive, and intuitive? |
| **Innovation** | Medium | Does it go beyond a simple chatbot — novel use of AI? |
| **Storytelling** | Low-Medium | Is the 5-minute demo narrative compelling and clear? |

---

## 💡 Winning Concept Strategy

### Why Avanade? Leverage Their Ecosystem
Avanade is a Microsoft joint venture. **Strong submissions should incorporate Microsoft's AI stack:**
- **Microsoft Azure AI / Copilot** — for the core AI engine
- **Microsoft Viva Insights** — wellbeing data schemas for tech worker scenarios
- **Microsoft Teams integration** — for tech worker meeting overload use cases
- **Azure AI Health Bot** — for non-clinical wellbeing check-ins
- **Power BI + Azure** — for personal analytics dashboards

Using Microsoft technologies will resonate strongly with Avanade judges and signals real-world viability.

### Recommended Concept: "BalanceIQ" — AI Wellbeing Advisor for Tech Workers

**Why tech workers (not students)?** The overlap with Avanade's consulting practice (enterprise tech, Microsoft ecosystem) is stronger, and the pain points (burnout, after-hours work, meeting overload) are more concrete and data-rich.

**Core idea:** An AI-powered personal wellbeing coach for tech workers that:
1. **Passively monitors** work patterns (meeting load, after-hours emails, focus time) using Microsoft Viva Insights data
2. **Generates weekly wellbeing scores** across 4 dimensions: focus, boundaries, rest, social connection
3. **Delivers personalized micro-nudges** — not therapy, but habit suggestions ("You have 4 meetings before 9am tomorrow — here's a 5-minute breathing exercise to start your day")
4. **Surfaces team-level anonymized trends** so managers can understand aggregate burnout signals — not individual tracking
5. **Escalates appropriately** — if signals are severe, it surfaces professional resources (EAP links, HR contacts) — never attempts to intervene directly

**AI types to incorporate:**
- **LLM** (GPT-4 / Azure OpenAI) for personalized nudge generation
- **Time-series anomaly detection** (Azure ML) for identifying deviation from healthy baselines
- **NLP sentiment analysis** on meeting transcripts (with consent) for meeting fatigue scoring
- **Behavioral pattern recognition** for routine analysis

---

## 🔬 Research Directions for the Agent

### Key Questions to Investigate
1. What are the most evidence-backed non-clinical interventions for tech worker burnout? (mindfulness, work structuring, meeting hygiene, sleep routines)
2. How does Microsoft Viva Insights structure its wellbeing data? What metrics does it track?
3. What existing wellbeing apps exist (Calm, Headspace, BetterUp) and where are their gaps for tech workers?
4. What does the Stack Overflow Developer Survey say about the top stressors for developers?
5. What ethical frameworks exist for AI in non-clinical wellbeing (APA, WHO-5 index)?

### Datasets to Use
- **Stack Overflow Developer Survey** — https://survey.stackoverflow.co/ (work patterns, satisfaction, burnout)
- **Microsoft Viva Insights sample schemas** — https://learn.microsoft.com/en-us/viva/insights/advanced/analyst/meeting-query/
- **American Time Use Survey (ATUS)** — https://www.bls.gov/tus/ (how people allocate time across work/rest)
- **UK ONS Personal Wellbeing Data** — https://www.ons.gov.uk/peoplepopulationandcommunity/wellbeing
- **WHO-5 Wellbeing Index** — https://www.who.int/publications/m/item/WHO-UCN-MSD-MHE-2024.01
- **CDC Physical Activity & Sleep Data** — https://www.cdc.gov/physical-activity/php/data/index.html

### Prototype Architecture Ideas
```
User Data Layer (with consent)
  └── Meeting calendar data (Teams/Outlook)
  └── Work hours & after-hours signals
  └── Focus time tracking (MyAnalytics)
        ↓
AI Processing Layer
  └── Azure ML: Baseline learning (first 2 weeks)
  └── Anomaly detection: Flag deviations from healthy patterns
  └── Azure OpenAI GPT-4: Generate personalized nudge text
        ↓
Output Layer
  └── Weekly "Wellbeing Digest" card (Teams adaptive card)
  └── Manager-level anonymized heatmap dashboard (Power BI)
  └── In-app EAP resource surfacing (when threshold crossed)
```

---

## 🎨 Prototype MVP Scope (48 hours)

**Must have:**
- Landing page / onboarding that clearly states what the tool IS and IS NOT (not therapy)
- At least one working AI inference: e.g., analyze sample meeting data → output wellbeing score + nudge
- Safety guardrail UI element (clearly visible "This is not a substitute for professional care" + resource links)
- Demo with synthetic/simulated data (no real user data needed)

**Nice to have:**
- Teams bot integration mockup
- Manager dashboard mockup (anonymized)
- Multi-language support (accessibility)

---

## 🧠 Differentiation Angles (How to Win)

1. **Microsoft ecosystem integration** — judges from Avanade will recognize and reward this
2. **Dual-layer design** (individual + manager aggregate) — shows systems thinking
3. **Responsible AI statement** — explicitly address APA guidelines, data consent, bias risks
4. **Non-obvious AI application** — pattern recognition on work rhythms is more sophisticated than a simple chatbot
5. **Demo narrative**: Frame the story around a relatable persona (e.g., "Sarah, a software engineer at a consulting firm, hasn't taken a real lunch break in 3 weeks...")

---

## 📋 Responsible AI Checklist

- [ ] Explicit non-clinical positioning stated in UI
- [ ] Consent model for any data collection described
- [ ] Professional resource escalation path built in
- [ ] No individual worker surveillance — aggregate/anonymized team insights only
- [ ] Bias audit: does the system work equitably across genders, roles, remote vs. in-office?
- [ ] Transparency: can users understand why a nudge was generated?

---

## 📎 Source Files Reference
- `Avanade Challenge Track Option B_AI_Wellbeing_Student_Resource_Guide.docx` — Full resource guide with datasets
- `FY26 Avanade Challenge Question_Cal Poly Pomona AI Hackathon.pdf` — Official challenge statement
