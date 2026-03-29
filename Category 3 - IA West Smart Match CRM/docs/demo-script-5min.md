# IA West SmartMatch CRM — 5-Minute Executive Demo Script

> **Presenter guide:** Two-column format — left is what you say, right is what you do on screen.
> Target pace: calm and deliberate. Do not rush. Let animations breathe.
> Total runtime: 5:00 – 5:15 with natural pauses.

---

## Pre-Demo Setup Checklist

- [ ] Backend running: `python scripts/start_fullstack.py` (FastAPI on `:8000`)
- [ ] Frontend running: `npm run dev` inside `frontend/` (Vite on `:5173`)
- [ ] Browser open to `http://localhost:5173` — **Dashboard** tab visible
- [ ] `.env` populated: `GEMINI_API_KEY`, optionally `TAVILY_API_KEY`
- [ ] `smartmatch.db` seeded (run `python -m src.scripts.seed_db` if empty)
- [ ] Zoom / OBS screen share ready. Mirror mode off.

---

## The One-Liner (memorize this)

> *"IA West has 18 volunteers and hundreds of university opportunities.
> SmartMatch makes sure the right person shows up to the right room —
> and proves it was worth it."*

---

## Script

---

### [0:00 – 0:35] — The Problem

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "IA West is a volunteer-run professional chapter. Eighteen board members — researchers, analysts, strategists — scattered across ten metro regions from Seattle to San Diego." | Stay on **Dashboard**. Let the metric cards speak. Point to the board-member count. |
| "Every semester, hundreds of university events need a guest speaker, a judge, a career fair panelist. Right now, the coordination happens over email chains and spreadsheets. Nobody knows who's available, who's already overloaded, or which event is the best fit for which expert." | Scroll down to the **Pipeline funnel** widget. Point to the early stages — 'Discovered' and 'Matched' — still thin. |
| "Three things fall through the cracks every cycle: the right match never gets made, burned-out volunteers get asked again, and nobody can measure whether any of it drove membership growth. We built SmartMatch to fix all three." | Pause one beat. Let it land. |

---

### [0:35 – 1:15] — Live Discovery: The Web Crawler

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "Step one: find the opportunities. Instead of relying on someone to manually search university websites, SmartMatch crawls them automatically." | Navigate to **Dashboard → Web Crawler Feed** widget. |
| "When we press Start Crawl, the system fans out across seed URLs — Cal Poly Pomona, IA West pages, UCLA, UCSD, Portland State — and fires five targeted search queries through the Gemini grounded web-search API, with Tavily as a live fallback." | Click **Start Crawl**. Watch the SSE stream animate in real time — green checkmarks, crawling spinners. |
| "Critically — and this is something we added after noticing the early crawl was returning university homepages — every result passes through an event-relevance filter before it ever touches the database. If the title or URL doesn't contain terms like 'hackathon,' 'summit,' 'lecture,' 'career fair,' or 'workshop,' it gets silently dropped. Only actual events are persisted to Layer 0." | Point to the feed. Show a "found" item. If a homepage appears in the stream, note that it is shown in the UI for transparency but *not saved*. |
| "The result: a clean, structured table of real opportunities — no noise — ready for matching." | If crawl finishes quickly, show the count badge. Otherwise move on while it streams in the background. |

---

### [1:15 – 2:30] — The Matching Engine: 8-Factor Weighted Scoring

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "Step two: match. Navigate to the AI Matching tab." | Click **AI Matching** in the sidebar. |
| "Every speaker-event pair receives a composite score built from eight independent factors. Let me walk through the ones that matter most." | Point to the match results table. Find the top-ranked result — ideally an 80%+ match. |
| "**Topic Relevance** — 22% of the score — uses cosine similarity between 1,536-dimensional Gemini embeddings of the speaker's expertise and the event topic. This is not keyword matching. 'Consumer insights' and 'market research analytics' score high together even if they share no words." | Hover over / expand the factor breakdown. |
| "**Geographic Proximity** — 18% — uses a lookup table of our eleven canonical metro pairs. If a pair isn't in the table, we fall back to Haversine great-circle distance. A speaker in Ventura presenting at UCLA scores higher than one in Seattle. Travel burden is real." | Point to the Geo score bar. |
| "**Role Fit** — 18% — combines exact canonical matching (judge to judge, speaker to speaker) with fuzzy token-set similarity. A board president is inferred to be a capable speaker even if their title doesn't say it." | Point to the Role Fit bar. |
| "**Calendar Fit** — 12% — finds the nearest IA West chapter event within a 30-day window of the opportunity date. The score decays linearly: a perfect same-week alignment scores 1.0; a 30-day gap scores 0.5. We want speakers engaged when IA West already has regional momentum." | Point to the Calendar Fit bar. |
| "And the one judges always ask about: **Volunteer Fatigue**." | Pause. |
| "Fatigue is a composite of four sub-pressures: how many active pipeline assignments the speaker currently holds, how far those assignments have progressed through the funnel, the travel burden of recent events, and the intensity of event recurrence — weekly commitments cost more than one-off appearances. We invert that pressure into a recovery score. Anyone above 0.75 fatigue is marked 'On Cooldown' and dropped from recommendations entirely. Between 0.40 and 0.75 is 'Needs Rest' — they still show up in results but ranked lower." | If the UI has a volunteer recovery panel or fatigue indicator, point to it. |
| "The composite score is a weighted sum across all eight factors. The weights are tunable — if IA West decides geographic proximity matters more than calendar fit this quarter, they slide one number." | If there are weight sliders, briefly show them. |

---

### [2:30 – 3:10] — AI-Generated Outreach

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "Once we have a top match, step three is outreach. Click the Match Volunteers button on any opportunity." | Navigate to **Opportunities** page. Click **Match Volunteers** on a card. This routes to AI Matching with the event pre-selected. |
| "The system generates a personalized email using Gemini Flash. The prompt is structured: it passes the speaker's actual title, company, expertise tags, their match score breakdown, and the event's volunteer role need. The output is JSON — subject line, greeting, body, closing — and we validate the schema before rendering." | Point to the generated email in the Outreach panel or navigate to the **Outreach** tab. |
| "Every email mandatorily includes an IA West chapter link — a compliance requirement we baked into the system prompt, not left to chance. And results are cached by a SHA-256 key so re-generating the same pair is instant." | Briefly show the email text. Point out the IA West link embedded naturally. |
| "Alongside the email, coordinators can download a `.ics` calendar invite — pre-filled with event date, location, speaker email, and the match explanation in the description field." | If the ICS download button is visible, point to it. |

---

### [3:10 – 3:50] — Pipeline Tracking & Data Funnel

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "Step four: track what happens. Navigate to the Pipeline tab." | Click **Pipeline** in the sidebar. |
| "Every speaker-event pair has a stage: Discovered, Matched, Contacted, Confirmed, Attended, Member Inquiry. This is not a status field — it is an ordered funnel. We can see at a glance where volume is dropping off." | Point to the funnel visualization or stage column in the pipeline table. |
| "The data powering this comes from three CSV layers — speaker profiles, event contacts, and the IA West event calendar — enriched with live match scores and persisted to SQLite. The layer architecture means if the live database is unavailable, the app falls back to demo data automatically. No crashes during the demo." | Show a calm confidence here — this is a robustness point. |
| "Conversion history is also factored into matching. If a specific speaker has historically converted 75% of their speaking engagements to student membership inquiries, that number lives in the model and biases future recommendations toward them for high-stakes events." | Reference the Historical Conversion factor score if visible. |

---

### [3:50 – 4:35] — QR Code ROI Tracking

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "The hardest question for any volunteer-run organization is: did this actually grow membership? That's what the QR system answers." | Navigate to the **Dashboard** and find the QR stats panel, or navigate directly to the QR card if it's a separate section. |
| "For every confirmed speaker-event pair, SmartMatch generates a unique referral QR code. The code is deterministic — SHA-256 of the speaker name and event name encoded in base-32 — so the same pair always produces the same code. You can regenerate without losing history." | Point to a QR code card showing a referral code like `IAW-ABCD1234`. |
| "When a student scans the code at the event, we log the timestamp, the referral code, and whether they indicated membership interest. That data rolls up to a live dashboard: scan count, membership interest count, and a conversion rate." | Point to the stats: generated count, scan count, conversion rate. |
| "A coordinator can now tell the board: 'Travis Miller spoke at the UCLA Hackathon, 23 students scanned his QR, 5 indicated interest in IA West membership — a 21.7% conversion rate.' That is a measurable return on a volunteer's time." | Say the numbers slowly. This is the money moment for an executive audience. |

---

### [4:35 – 5:00] — Closing: What This Unlocks

| WHAT YOU SAY | WHAT YOU DO |
|---|---|
| "What we've built is a closed loop. The crawler finds opportunities. The matching engine ranks them by eight evidence-based factors — including burnout prevention. The outreach module personalizes every ask. The pipeline tracks conversion. The QR system proves ROI." | Navigate back to **Dashboard**. Let the metrics card view be the closing visual. |
| "Every algorithm is explainable. Every weight is adjustable. Every recommendation comes with a factor breakdown that a coordinator can read, understand, and override. This is not a black box — it is a decision-support tool built to make eighteen volunteers feel like a team of eighty." | Hold on the dashboard. |
| "SmartMatch is live, running on real IA West data, today." | Nod. Done. |

---

## Anticipated Executive Questions

| Question | Talking Point |
|---|---|
| *"What happens if Gemini is unavailable?"* | Three-layer fallback: Gemini → Tavily → cached results. UI never shows an error to end users; falls back to demo data. |
| *"How do you prevent the same volunteer being spammed?"* | The fatigue score. Anyone above 0.75 fatigue is programmatically excluded from the recommendation list before results are rendered. |
| *"Can the weights be changed by IA West staff, not developers?"* | Yes. The weight vector is configuration, not code. A non-technical coordinator can adjust sliders in the UI and see rankings shift in real time. |
| *"What data do you store about students who scan QR codes?"* | Only: timestamp, referral code, and a boolean membership-interest flag. No PII, no device fingerprinting. |
| *"How does this scale to other chapters?"* | The chapter identity is a config variable. Seed URLs, search queries, and metro region tables are all data, not code. A new chapter onboards by updating a config file. |
| *"What's the accuracy of the match scores?"* | The model is calibrated against IA West's historical decisions. Factor weights were tuned to match known good pairings. The score is a ranking tool, not a prediction — coordinators make the final call. |

---

## Key Numbers to Memorize

| Metric | Value |
|---|---|
| Board member volunteers | **18** |
| West Coast metro regions covered | **10** |
| Matching factors | **8** |
| Embedding dimensions (Gemini) | **1,536** |
| CPP courses in dataset | **35** (10 high-fit) |
| Fatigue "On Cooldown" threshold | **≥ 0.75** |
| Pipeline stages | **6** |
| Test suite coverage | **82%** (358+ tests) |

---

*Script prepared for IA West Smart Match CRM — Hackathon for a Better Future 2026, Category 3.*
