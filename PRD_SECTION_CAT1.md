## Category 1: BalanceIQ — AI Wellbeing Advisor for Tech Workers
**Sponsor:** Avanade | **CTO Tier:** 3/Optional | **Verdict:** Approved with Revisions

**Planning Note (2026-03-15):** For implementation sequencing and staffing, treat `STRATEGIC_REVIEW.md`, `MASTER_SPRINT_PLAN.md`, and `Category 1 - Avanade AI Wellbeing/SPRINT_PLAN.md` as the source of truth. This category is optional and should only be staffed with a 5th team member.

### Problem Statement

Tech worker burnout has reached critical levels. According to the 2024-2025 State of Engineering Management Report, 65% of engineers experienced burnout in the past year. LeadDev's 2025 Engineering Leadership Report found 22% of developers face critical burnout levels, with another 24% moderately burned out. A broader industry survey shows 68% of tech workers report burnout symptoms, up from 49% three years prior. The root causes are structural: 65% of developers report expanded responsibilities, 40% manage more direct reports than before, and the push to adopt AI tools while maintaining output has added a new pressure layer. Meanwhile, Microsoft Viva Insights is a $6/user/month add-on within the Microsoft ecosystem, which makes it a poor fit for teams that do not use Microsoft 365 at all. There is a gap between Microsoft-native workplace analytics and generic consumer wellness apps (Calm, Headspace) that do not understand the specific rhythms of engineering work — on-call rotations, sprint cycles, meeting overload, and after-hours Slack culture.

### Proposed Solution

BalanceIQ is a lightweight, AI-powered wellbeing dashboard for tech workers that analyzes work pattern data (calendar density, after-hours activity, focus time ratios, meeting load) and generates actionable micro-nudges to prevent burnout. Rather than using ML-based anomaly detection (which would require training data and time the hackathon does not afford), it uses a configurable rules engine with evidence-based thresholds (e.g., >6 meetings/day = high meeting load, <2 hours focus time = low deep work). The centerpiece demo moment is a manager-level anonymized heatmap showing team-wide burnout risk patterns across a two-week period — visually striking and immediately actionable. GPT-4o-mini generates personalized, context-aware nudge text that goes beyond generic advice. The system is positioned for teams outside the Microsoft ecosystem rather than as a cheaper Viva tier, which keeps the story accurate and avoids sounding like a licensing workaround.

### Tech Stack

| Layer | Technology | Purpose | Free Tier? | Cost Estimate (2 weeks) |
|-------|-----------|---------|------------|------------------------|
| Frontend/Dashboard | Streamlit | Interactive wellbeing dashboard, manager heatmap, nudge display | Yes — Community Cloud (1 GB RAM, public repo required) | $0 |
| AI Text Generation | OpenAI GPT-4o-mini API | Personalized nudge generation, wellbeing digest summaries | No free tier; pay-per-use | ~$0.50-$2.00 (est. 2-5M tokens total during dev/demo) |
| Rules Engine | Python (custom) | Threshold-based work pattern scoring across 4 dimensions | N/A (custom code) | $0 |
| Data Visualization | Plotly + Streamlit Charts | Manager heatmap, individual trend lines, team aggregate views | Yes (open source) | $0 |
| Synthetic Data | Faker + custom scripts | Simulated calendar, email, and focus time data for 20+ synthetic employees | Yes (open source) | $0 |
| Hosting (backup) | Streamlit Community Cloud | Demo deployment if local demo fails | Yes | $0 |
| Version Control | GitHub | Code repository, CI | Yes | $0 |
| Design Assets | Figma (free tier) | UI mockups, persona cards for demo narrative | Yes | $0 |

### API & Service Pricing Breakdown

**OpenAI GPT-4o-mini (primary model for nudge generation):**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- Estimated hackathon usage: ~3M input tokens, ~1M output tokens = $0.45 + $0.60 = **~$1.05 total**
- Source: [OpenAI Pricing](https://openai.com/api/pricing/), [PricePerToken GPT-4o-mini](https://pricepertoken.com/pricing-page/model/openai-gpt-4o-mini)

**OpenAI GPT-4o (fallback/higher quality nudges):**
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens
- Not recommended for this project; GPT-4o-mini is sufficient for nudge text generation
- Source: [OpenAI API Pricing](https://developers.openai.com/api/docs/pricing/)

**Azure OpenAI Service (alternative if team has Azure credits):**
- GPT-4o: $2.50 input / $10.00 output per 1M tokens (same as OpenAI direct)
- GPT-4o-mini: $0.15 input / $0.60 output per 1M tokens
- Provisioned throughput: starts at $2,448/month (overkill for hackathon)
- Azure for Students provides $100 credit — sufficient for this project
- Source: [Azure OpenAI Pricing](https://azure.microsoft.com/en-us/pricing/details/azure-openai/)

**Streamlit Community Cloud:**
- Free tier: unlimited public apps, 1 GB RAM per app, apps sleep after inactivity
- Constraint: must use public GitHub repository
- No concurrent user limit stated, but performance degrades under load
- Source: [Streamlit Community Cloud Status](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)

### Complexity Assessment

| Dimension | Score (1-5) | Justification |
|-----------|-------------|---------------|
| AI/ML Complexity | 2 | Rules engine replaces ML; GPT-4o-mini API calls are straightforward prompt engineering. No model training, no fine-tuning, no embeddings. |
| Data Requirements | 2 | All synthetic data generated via scripts. No real user data, no API integrations, no OAuth flows. Faker library handles generation. |
| UI/UX Complexity | 3 | Streamlit simplifies UI, but the manager heatmap requires thoughtful Plotly configuration. Individual dashboards need 4-dimension scoring display. |
| Integration Complexity | 1 | No external system integrations for MVP. Synthetic data eliminates calendar API, Teams API, and Outlook API complexity entirely. |
| Demo Polish Required | 4 | The heatmap must be visually compelling — it IS the demo moment. Persona narrative ("Meet Sarah...") needs scripting. Ethical guardrails UI must be prominent. |
| **Average** | **2.4** | Low-to-moderate complexity overall. The challenge is in polish and storytelling, not technical difficulty. |

### 2-Week Implementation Timeline

| Milestone | Days | Deliverables |
|-----------|------|-------------|
| M1: Research & Design | 1-2 | Evidence-based threshold research (meeting load, focus time, after-hours benchmarks). Synthetic data schema design. Wireframes for individual dashboard and manager heatmap. Persona creation (2 personas: "Sarah the SWE" and "Marcus the EM"). |
| M2: Core Development | 3-7 | Synthetic data generator (20 employees, 14 days of data). Rules engine with 4 scoring dimensions (focus, boundaries, rest, social connection). GPT-4o-mini nudge generation prompts. Individual wellbeing score calculation and display. |
| M3: Dashboard & Polish | 8-10 | Manager heatmap (Plotly heatmap: employees x days, color-coded by risk). Individual trend line charts. Nudge history panel. Ethical guardrails UI (banner, resource links, disclaimers). |
| M4: Testing & Demo Prep | 11-12 | End-to-end walkthrough with synthetic data. Edge case testing (all-green team, all-red team, mixed). Demo script writing and rehearsal. Streamlit Cloud deployment as backup. |
| M5: Presentation & Buffer | 13-14 | 5-minute demo rehearsal (3+ run-throughs). Slide deck for non-demo portions. Backup plan if live demo fails (screenshots/video). Final code cleanup. |

### Team Allocation

**3-Person Team:**
- **Person 1 (Backend + Data):** Synthetic data generator, rules engine, scoring algorithms, GPT-4o-mini prompt engineering and API integration. Owns the data pipeline from generation through scoring.
- **Person 2 (Frontend + Visualization):** Streamlit app structure, Plotly heatmap implementation, individual dashboard layout, ethical guardrails UI elements, responsive design. Owns everything the user sees.
- **Person 3 (Demo + Research + QA):** Burnout research for threshold calibration, persona development, demo script authoring, presentation slides, end-to-end testing, Streamlit Cloud deployment. Owns the narrative and quality.

**5-Person Team:**
- **Person 1 (Rules Engine Lead):** Scoring algorithms, threshold configuration, dimension weighting logic. Collaborates with researcher on evidence-based thresholds.
- **Person 2 (AI/Prompt Engineer):** GPT-4o-mini nudge generation, prompt templates for different risk levels and dimensions, tone calibration (supportive, not clinical).
- **Person 3 (Frontend - Individual View):** Individual dashboard, trend charts, nudge display, onboarding flow, ethical disclaimers.
- **Person 4 (Frontend - Manager View):** Manager heatmap (the demo moment), team aggregate statistics, anonymization layer, drill-down interactions.
- **Person 5 (Research + Demo + PM):** Threshold research, persona creation, synthetic data design, demo script, presentation, QA, deployment.

### Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Crowded category — many teams attempt wellbeing chatbots | High | High | Differentiate hard: no chatbot interface. Lead with the manager heatmap as a systems-thinking artifact. Position as B2B analytics tool, not consumer app. |
| Judges perceive solution as "just a dashboard" lacking AI depth | Medium | High | Ensure GPT-4o-mini nudges are contextually rich and clearly AI-generated. Show prompt engineering sophistication in the demo. Include a side-by-side of template nudge vs. AI-generated nudge. |
| Streamlit performance issues during live demo (app sleeping, slow load) | Medium | Medium | Run demo locally as primary. Streamlit Cloud as backup only. Pre-warm the app before presentation slot. Have a screen recording as final fallback. |
| Ethical pushback — judges concerned about workplace surveillance framing | Medium | High | Lead with consent model in the onboarding screen. Manager view is strictly anonymized and aggregated. Include prominent "This is not a substitute for professional mental health care" messaging. Reference APA guidelines explicitly. |
| GPT-4o-mini generates inappropriate or clinical-sounding advice | Low | Critical | System prompt includes hard constraints: no diagnosis language, no clinical terminology, always append professional resource links. Pre-generate and cache nudges for demo to eliminate live generation risk. |
| Team deprioritizes this category due to Tier 3 status | Medium | Medium | Acknowledge Tier 3 honestly. Frame as a low-risk, high-learning project. The simplicity of the tech stack means less wasted effort if the team pivots focus to higher-tier categories. |

### Win Probability Assessment
- **CTO Tier:** 3/Optional
- **Independent Analysis:** This is a crowded category where the default approach (wellbeing chatbot) is explicitly what judges say they do not want. The strategic correction is directionally right: remove ML complexity, keep the manager heatmap as the demo anchor, and stop framing the product as discounted Viva. The more defensible story is "opt-in wellbeing analytics for engineering teams outside the Microsoft ecosystem." That is more accurate, but it is also a narrower wedge and still difficult to prove in a 5-minute demo. Competitive pressure remains high: BetterUp ($300-500/user/month for coaching), Calm Business (~$64/employee/year), and Viva Insights ($6/user/month add-on) all exist.
- **Demo Moment:** The manager heatmap is the anchor. A split-screen showing "Sarah's individual dashboard" (personal, actionable) next to "Engineering Team Heatmap" (aggregate, anonymized, leadership-actionable) tells a story no chatbot demo can match. The heatmap should use a red-yellow-green gradient over a 14-day x 20-employee grid, with clear patterns emerging (e.g., crunch week visible as a red band across the team).
- **Overall Win Probability:** Conditional. Treat 25-35% as the upside case only if a 5th person is confirmed and the team protects polish time for the heatmap, simulator, and responsible-AI flow. For a 3-4 person team, this category should stay parked.

### Existing Assets Inventory
- **Stack Overflow Developer Survey data** (publicly available) — burnout statistics, work pattern benchmarks for calibrating thresholds
- **Microsoft Viva Insights sample data schemas** (Microsoft Learn docs) — structure for synthetic data generation
- **WHO-5 Wellbeing Index** — validated 5-question wellbeing assessment framework that can inform scoring dimensions
- **Faker (Python library)** — synthetic data generation, no licensing cost
- **Plotly open-source** — heatmap and chart components, extensive documentation
- **Streamlit component library** — pre-built UI components for dashboards
- **OpenAI Python SDK** — well-documented, minimal integration effort
- **APA AI wellness guidelines** — ethical framework language for disclaimers and responsible AI positioning

### Responsible AI Considerations
- **No mental health diagnosis claims:** The system scores work patterns (meeting load, focus time, after-hours activity), not psychological states. Language must say "high meeting load detected" rather than "you may be experiencing anxiety." This is a red line from the CTO review and the hackathon rules.
- **No individual surveillance:** The manager heatmap must be strictly anonymized. Minimum aggregation threshold of 5 employees per view to prevent re-identification. No manager should be able to identify a specific employee's score.
- **Consent-first data model:** Even with synthetic data, the demo must show a consent onboarding flow — users explicitly opt in, understand what data is analyzed, and can opt out at any time.
- **Professional resource escalation:** When any dimension scores in the "red" zone, the system surfaces EAP (Employee Assistance Program) links and professional mental health resources — it never attempts to intervene directly.
- **Bias awareness:** Work pattern thresholds (e.g., "after 6 PM = after-hours") may not account for different time zones, cultural work norms, caregiving responsibilities, or flexible schedules. The system should allow personalized baseline configuration.
- **Transparency in AI-generated content:** All GPT-4o-mini generated nudges must be clearly labeled as AI-generated. Users should understand why a particular nudge was triggered (e.g., "This nudge was generated because you had 8 meetings yesterday with no focus blocks").
- **No chatbot-first interface:** Per the CTO review red line, the primary interface is a dashboard, not a conversational AI. This avoids the trap of users treating the system as a therapist or counselor.
