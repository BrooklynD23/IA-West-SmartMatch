---
doc_role: background
authority_scope:
- category.3.background_analysis
canonical_upstreams:
- PRD_SECTION_CAT3.md
- Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md
- archived/general_project_docs/MASTER_SPRINT_PLAN.md
- archived/general_project_docs/STRATEGIC_REVIEW.md
last_reconciled: '2026-03-17'
managed_by: repo-governance
---

# Category 3 — IA West: Smart Match CRM
**Sponsor:** Insights Association West Chapter | **Event:** CPP AI Hackathon "AI for a Better Future" | April 16, 2026

> **Governance notice (repo-governance):** This file is background analysis only. Use it for ideation and history, not as an authority for current planning decisions. Canonical upstreams: `PRD_SECTION_CAT3.md`, `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`, `archived/general_project_docs/MASTER_SPRINT_PLAN.md`, `archived/general_project_docs/STRATEGIC_REVIEW.md`.

---

## 🎯 Challenge Prompt

> *"How might IA West systematically discover university engagement opportunities — guest lectures, competitions, career programs, and campus events — match them with the right board member volunteers, and convert that engagement into a measurable pipeline to IA membership?"*

**The core problem:** IA West is entirely volunteer-run, lacks a central system for discovering university opportunities, has no tracking from engagement touchpoints to membership conversion, and cannot scale manually across 8+ events/year and dozens of universities spanning Portland to San Diego.

---

## 📦 Deliverable Requirements

### 1. Working Prototype CRM
A functional prototype (Streamlit, Airtable, or similar) that:
- Ingests speaker profiles and university opportunity data (courses + campus events)
- Recommends optimal volunteer-to-opportunity matches
- Generates outreach communications (emails + calendar invites)
- Tracks the engagement → event → membership conversion pipeline
- **Demonstrates automated method for discovering new campus opportunities beyond CPP** (web scraping, API calls, or LLM-assisted extraction from university event pages)
- Must demonstrate at least the matching engine and opportunity discovery **live**

### 2. Growth Strategy (2–3 pages)
How Smart Match drives the campus engagement → IA event → membership pipeline:
- Target audience segments
- Value proposition for volunteers and universities
- Rollout plan (starting with CPP, expanding to 3+ universities)
- Channel strategy

### 3. Measurement Plan
- KPIs for pipeline conversion, event scoring, and volunteer utilization
- At least one proposed validation experiment
- Feedback loop for improving match quality over time

### 4. Responsible AI Note (half page)
- Privacy — handling of speaker, faculty, and student data
- Bias — ensuring the matching algorithm doesn't favor certain speakers/universities/topics
- Transparency — how match scores and event ratings are explained to stakeholders
- Data handling — consent and storage practices

---

## 🏆 Judging Criteria (50 Points)

| Criterion | Points | Description |
|---|---|---|
| **Prototype Quality** | ~15 | Does the matching engine work live? Does opportunity discovery demonstrate automation? |
| **Growth Strategy** | ~10 | Realistic, specific rollout from CPP to 3+ universities |
| **Measurement Plan** | ~10 | Are KPIs actionable? Is there a real feedback loop? |
| **Responsible AI** | ~10 | Are privacy, bias, and transparency addressed concretely? |
| **Scalability** | ~5 | Can a volunteer reasonably add a new university with minimal effort? |

---

## 💡 Winning Concept Strategy

### Why This Category is Winnable
The provided data files give a **massive head start**: real CPP events, real speaker profiles, real course schedules. The challenge is well-scoped and practically oriented — judges want a demo that works, not a theoretical framework.

### Recommended Concept: "IA SmartMatch" — AI-Orchestrated Engagement CRM

**Four-module architecture (as specified by the challenge brief):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    IA SMART MATCH PLATFORM                       │
├──────────────────┬──────────────────┬──────────────────────────┤
│  MODULE 1        │  MODULE 2        │  MODULE 3                │
│  SUPPLY SIDE     │  DEMAND SIDE     │  MATCHING ENGINE         │
│  (Volunteers)    │  (Opportunities) │  (AI Orchestrator)       │
├──────────────────┼──────────────────┼──────────────────────────┤
│ Board profiles   │ CPP events data  │ Scoring function:        │
│ Expertise tags   │ Course schedules │  Topic_Relevance (w1)    │
│ Role prefs:      │ LLM-discovered   │  Role_Fit (w2)           │
│  judge/mentor/   │  events from     │  Geographic_Proximity    │
│  speaker/panelist│  other campuses  │  (w3)                    │
│ Availability     │                  │  Calendar_Fit (w4)       │
│ Engagement hist. │                  │  Hist_Conversion (w5)    │
│                  │                  │  Student_Interest (w6)   │
└──────────────────┴──────────────────┴──────────────────────────┘
                              │
                              ▼
              ┌──────────────────────────────┐
              │  MODULE 4                    │
              │  MEMBER JOURNEY PIPELINE     │
              │  Campus engagement           │
              │  → IA student member         │
              │  → local event attendee      │
              │  → mentee match              │
              │  → young professional        │
              │  → corporate member          │
              └──────────────────────────────┘
```

### AI Types to Incorporate
- **LLM (GPT-4o / Claude)** — for opportunity discovery (extract event data from raw HTML), outreach email generation, match explanation text
- **Vector embeddings + cosine similarity** — for semantic matching between speaker expertise tags and event topic requirements
- **Web scraping + LLM extraction** — automated discovery of opportunities at new universities
- **Scoring/ranking model** — weighted multi-criteria decision function (MATCH SCORE formula)
- **NLP** — entity extraction from unstructured event descriptions

### Sponsor Technology Angle
IA West is a **market research** organization. Use language and tools that resonate:
- Position the matching algorithm as a "research-grade recommendation engine"
- Reference A/B testing for weight tuning (they understand experimental design)
- Frame the pipeline tracking as a "conversion funnel" — language they use daily

---

## 🔬 Research Directions for the Agent

### Key Questions to Investigate
1. What are the best approaches for LLM-assisted structured data extraction from university event pages? (few-shot prompting, HTML → JSON extraction)
2. What open-source CRM tools integrate well with Python/Streamlit for rapid prototyping? (Airtable API, Notion API, Google Sheets as backend)
3. How can vector embeddings (Gemini `gemini-embedding-001`) be used to match expertise tags to event descriptions?
4. What universities in the IA West region (Portland to San Diego) have well-structured public event calendars? (UCLA, USC, SDSU, UC Davis, UO, PSU)
5. What are the best approaches for generating personalized outreach email templates via LLM?

### Data Files Available (in Category 3 folder)
- `data_speaker_profiles.csv` — IA West board member profiles: name, board role, metro region, company, title, expertise tags
- `data_cpp_events_contacts.csv` — CPP event opportunities: event name, category, recurrence, volunteer roles, contact info
- `data_cpp_course_schedule.csv` — CPP course schedules for guest lecture matching
- `data_event_calendar.csv` — IA West event calendar for calendar-fit matching
- `IA_West_Smart_Match_Challenge.docx` — Full challenge specification
- `IA_West_Smart_Match_Challenge_Intro.pptx` — Sponsor intro deck

### Key Speaker Profiles (from data)
The board has members across: Ventura/Thousand Oaks, LA West, San Francisco, LA Long Beach — covering major expertise in: data collection, MR technology, qualitative research, AI innovation, marketing science, brand research.

### Matching Algorithm Specification
```python
MATCH_SCORE = (
    w1 * topic_relevance(speaker_tags, event_topic) +   # semantic similarity
    w2 * role_fit(speaker_roles, event_volunteer_role) + # exact match
    w3 * geographic_proximity(speaker_metro, event_location) + # distance score
    w4 * calendar_fit(speaker_availability, event_date) + # overlap score
    w5 * historical_conversion_rate(speaker_id) +        # past performance
    w6 * student_interest_signal(event_type, audience)   # event category weight
)
```
Default weights: w1=0.30, w2=0.25, w3=0.20, w4=0.15, w5=0.05, w6=0.05
(Tunable by chapter leadership)

### University Discovery Automation
```python
# LLM-assisted university event extraction
DISCOVERY_PROMPT = """
You are extracting structured event data from a university webpage.
Given this HTML/text content from [UNIVERSITY] career center or events page,
extract all events where industry professionals are needed as judges, mentors,
speakers, or panelists.

Return JSON array with:
[{
  "event_name": str,
  "category": str,  // hackathon/career_fair/case_competition/symposium/guest_lecture
  "date_or_recurrence": str,
  "volunteer_roles": [str],
  "primary_audience": str,
  "contact_name": str,
  "contact_email": str,
  "url": str
}]
"""
```

---

## 🎨 Prototype MVP Scope (48 hours)

**Must have:**
- Load `data_speaker_profiles.csv` and `data_cpp_events_contacts.csv`
- Compute MATCH SCORE for all speaker-event pairs
- Display top 3 recommended matches per event with score breakdown
- Generate a sample outreach email for the top match (LLM-generated)
- One live demo of automated discovery: scrape one external university URL → extract event data

**Nice to have:**
- Full Streamlit dashboard with 3 tabs: Matches / Pipeline / Discovery
- Pipeline tracker: drag-drop kanban or table showing engagement stages
- Automated discovery of 2-3 additional university event pages
- Match explanation: "Why was this speaker recommended?" natural language card

---

## 🧠 Differentiation Angles (How to Win)

1. **Live automated discovery** — demonstrating LLM extraction from a real university website is the highest-impact differentiator
2. **Explainable matches** — show the score breakdown and generate a natural language explanation; "black box" is explicitly called out as bad by the brief
3. **Generated outreach emails** — judges love seeing AI do actual work in the demo
4. **Pipeline visualization** — a Sankey or funnel chart showing conversion stages will land well with market researchers
5. **Realistic scalability story** — "add a university in 3 clicks" is more compelling than theoretical scale claims
6. **Demo flow**: "A new hackathon was just announced at UCLA. SmartMatch automatically detected it, matched Travis Miller (SVP Sales, Ventura region) as a judge, drafted his outreach email, and added him to the pipeline tracker — in under 60 seconds."

---

## 📋 Responsible AI Checklist

- [ ] No invasive scraping — only publicly available university event data
- [ ] No individual student tracking — only aggregate conversion metrics
- [ ] Match algorithm transparency — show score components, not just final score
- [ ] Bias audit: are some regions/speakers systematically over-matched?
- [ ] Data consent: describe how speaker profiles are collected and updated
- [ ] Privacy: faculty/contact information handling and storage policy

---

## 🏗️ Technical Stack Recommendation

| Component | Recommended Tool |
|---|---|
| Frontend/Dashboard | Streamlit (fast, Python-native) |
| Vector matching | Gemini `gemini-embedding-001` + cosine similarity |
| LLM for email gen + extraction | GPT-4o-mini (fast, cheap) or Claude Haiku |
| Web scraping | BeautifulSoup + requests / Playwright for JS pages |
| Data storage | CSV files → Pandas (hackathon scope) or Airtable |
| Visualization | Plotly (Sankey/funnel) + Streamlit charts |

---

## 📎 Source Files Reference
- `data_speaker_profiles.csv` — Board member profiles (supply side)
- `data_cpp_events_contacts.csv` — CPP event opportunities (demand side)
- `data_cpp_course_schedule.csv` — Course schedules for guest lectures
- `data_event_calendar.csv` — IA West event calendar
- `IA_West_Smart_Match_Challenge.docx` — Full challenge specification with judging criteria
- `IA_West_Smart_Match_Challenge_Intro.pptx` — Sponsor intro presentation
