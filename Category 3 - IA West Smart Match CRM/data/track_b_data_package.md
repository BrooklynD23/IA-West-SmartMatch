# Track B Data Package -- IA SmartMatch CRM

**Compiled:** 2026-03-19 (Sprint 2 complete)
**Source:** Automated pipeline outputs from Sprint 1 + Sprint 2

---

## 1. Match Results Summary

### Top Matches by Event (Top-1 per event, sorted by score)

| Event | Top Speaker | Match Score | Stage |
|---|---|---|---|
| CPP Career Center -- Business college coaching liaison | Dr. Yufan Lin | 0.630 | Contacted |
| CPP Career Center -- Employer relations / on-campus recruiting | Dr. Yufan Lin | 0.630 | Attended |
| CPP Career Center -- Career Fairs | Dr. Yufan Lin | 0.618 | Attended |
| SWIFT Tech Symposium | Dr. Yufan Lin | 0.618 | Contacted |
| CPP Career Center -- Employer Engagement | Dr. Yufan Lin | 0.615 | Confirmed |
| OUR -- RSCA Conference | Dr. Yufan Lin | 0.485 | Contacted |
| OUR -- Director contact | Dr. Yufan Lin | 0.485 | Contacted |
| OUR -- CARS (Creative Activities & Research Symposium) | Dr. Yufan Lin | 0.485 | Matched |
| College of Science Research Symposium | Dr. Yufan Lin | 0.485 | Attended |
| Bronco Startup Challenge (SIIL) | Dr. Yufan Lin | 0.468 | Contacted |
| Bronco Startup Challenge (staff contact) | Dr. Yufan Lin | 0.468 | Contacted |
| AI for a Better Future Hackathon | Dr. Yufan Lin | 0.461 | Attended |
| AI Hackathon (CPP hub page) | Dr. Yufan Lin | 0.461 | Attended |
| BroncoHacks | Dr. Yufan Lin | 0.458 | Attended |
| Information Technology Competition (ITC) | Dr. Yufan Lin | 0.456 | Contacted |

### Speaker Coverage

| Speaker | Events Matched (Top-3) | Avg Score |
|---|---|---|
| Dr. Yufan Lin | 15 | 0.527 |
| Amber Jawaid | 15 | 0.507 |
| Calvin Friesth | 15 | 0.507 |

---

## 2. Pipeline Funnel Numbers

### 6-Stage Engagement Funnel (from pipeline_sample_data.csv)

| Stage | Count | Conversion from Prior |
|---|---|---|
| Discovered | 15 events | -- |
| Matched | 8 speaker-event pairs | 53% of discovered |
| Contacted | 17 speaker-event pairs | active outreach |
| Confirmed | 4 speaker-event pairs | 24% of contacted |
| Attended | 14 speaker-event pairs | 82% of contacted |
| Member Inquiry | 2 speaker-event pairs | 14% of attended |

**Key metric:** 2 member inquiries from 15 discovered events = 13.3% top-of-funnel to bottom conversion.

---

## 3. University Coverage Map

### Discovery Pipeline Targets (Sprint 2 A2.1)

| University | Region | Scrape Method | Status |
|---|---|---|---|
| UCLA | Los Angeles -- West | BeautifulSoup (static) | Configured |
| USC | Los Angeles -- West | BeautifulSoup (static) | Configured |
| UC Davis | San Francisco (NorCal) | BeautifulSoup (static) | Configured |
| SDSU | San Diego | Playwright (JS-rendered) | Configured |
| Portland State | Portland | BeautifulSoup (static) | Configured |

### Existing Event Data (Sprint 1)

- **Cal Poly Pomona (CPP):** 15 events from data_cpp_events_contacts.csv
- **IA West Calendar:** Events from data_event_calendar.csv
- **Course Schedule:** Guest lecture opportunities from data_cpp_course_schedule.csv

### Geographic Coverage

| Metro Region | Universities | Speaker Pool |
|---|---|---|
| Los Angeles -- West | UCLA, USC | Board members in LA metro |
| Los Angeles -- East | Cal Poly Pomona (CPP) | Primary demo data source |
| San Diego | SDSU | Expanding reach |
| San Francisco / NorCal | UC Davis | NorCal coverage |
| Portland | Portland State | Pacific NW coverage |

---

## 4. ROI Inputs for Track B Analysis

### Engagement Value Estimates

| Metric | Value | Source |
|---|---|---|
| Events discovered | 15 | CPP event data (Sprint 1) |
| Universities scraped | 5 | Discovery pipeline (Sprint 2) |
| Top matches generated | 45 | 15 events x 3 speakers |
| Avg match score (top-1) | 0.527 | Matching engine output |
| Match score range | 0.456 -- 0.630 | Min/max top-1 scores |
| Pipeline conversion (discovered -> member inquiry) | 13.3% | Funnel data |
| Outreach emails generatable | 45 | Email gen module (Sprint 2) |

### Cost Assumptions (for Track B ROI model)

| Input | Estimate | Notes |
|---|---|---|
| Manual event discovery (per university) | 2-3 hours | Without automation |
| Automated discovery (per university) | < 1 minute | Scrape + LLM extraction |
| Manual speaker-event matching | 1-2 hours per event | Without SmartMatch |
| Automated matching | < 5 seconds per event | 6-factor scoring engine |
| Manual outreach email drafting | 15-20 min per email | Without templates |
| Automated email generation | < 10 seconds per email | Gemini-powered with personalization |
| Estimated time savings per engagement cycle | 80-90% | Discovery + matching + outreach |

### Membership Pipeline Assumptions

| Stage Transition | Estimated Rate | Data Source |
|---|---|---|
| Discovered -> Matched | 53% | Pipeline data |
| Matched -> Contacted | 100% (outreach sent) | Automated email gen |
| Contacted -> Confirmed | 24% | Pipeline data |
| Confirmed -> Attended | 82% | Pipeline data |
| Attended -> Member Inquiry | 14% | Pipeline data |
| Member Inquiry -> New Member | 30-50% (estimate) | Industry benchmark |

---

## 5. Sprint 2 Technical Deliverables

| Module | File | Lines | Tests | Description |
|---|---|---|---|---|
| Web Scraper | src/scraping/scraper.py | 345 | 15 | BS4+Playwright, SSRF protection, robots.txt, cache |
| LLM Extractor | src/extraction/llm_extractor.py | ~300 | 12 | Gemini extraction, HTML preprocessing, few-shot |
| Discovery Tab | src/ui/discovery_tab.py | 260 | 10 | University selector, results table, Add to Matching |
| Email Generator | src/outreach/email_gen.py | 339 | 13 | Gemini emails, cache, fallback, preview panel |
| ICS Generator | src/outreach/ics_generator.py | ~100 | 6 | RFC 5545 calendar invites |
| Pipeline Funnel | src/ui/pipeline_tab.py | 136 | 11 | Plotly 6-stage funnel, hover tooltips |

**Total Sprint 2:** ~1,480 lines of code, ~67 new tests, 258+ tests passing.
