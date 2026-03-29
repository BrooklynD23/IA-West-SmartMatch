# Category 3 Documentation Guide

Use this page as the entry point for Category 3 planning and implementation docs.

## Canonical Read Order

1. `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md`
   Owns execution scope, sprint tasks, milestones, and go/no-go gates.
2. `PRD_SECTION_CAT3.md`
   Owns feature detail, stack, risks, and dataset inventory.
3. `archived/general_project_docs/MASTER_SPRINT_PLAN.md`
   Owns portfolio calendar, staffing model, and shared schedule context.
4. `archived/general_project_docs/STRATEGIC_REVIEW.md`
   Owns portfolio conflict-resolution and strategic rationale.

## Category-Specific Supporting Docs

- `Category 3 - IA West Smart Match CRM/docs/gemini_provider_decision_2026-03-18.md`
  Provider decision memo documenting the Gemini Developer API runtime adoption, recommended models, and migration notes.
- `Category 3 - IA West Smart Match CRM/docs/sprints/sprint-3-swarm-orchestration-plan.md`
  Historical orchestration artifact for the Sprint 3 feature burst. Use it as execution history, not as an authority over the canonical sprint plan.
- `Category 3 - IA West Smart Match CRM/docs/sprints/sprint-0-foundation.md` through `sprint-4-ship.md`
  Derived implementation specs. These should stay aligned with the canonical docs above.
- `Category 3 - IA West Smart Match CRM/PLAN.md`
  Background analysis only. Useful for rationale and demo framing, but not authoritative for execution decisions.
- `Category 3 - IA West Smart Match CRM/.status.md`
  Owns stage state only.

## Review-Only Artifacts

These are useful for audit history, but they are not implementation authority:

- `Category 3 - IA West Smart Match CRM/docs/sprints/REVIEW_HANDOFF.md`
- `Category 3 - IA West Smart Match CRM/docs/sprints/SPRINT_SPEC_ADVERSARIAL_REVIEW_2026-03-17.md`

## Data Location Contract

- Raw challenge assets currently live in `archived/Categories list/Category 3 IA West Smart Watch/`.
- Sprint specs assume working copies are staged into `Category 3 - IA West Smart Match CRM/data/` during implementation setup.

## Cross-Sprint Contract Summary

- Imports: use `from src...`
- Launch command: `streamlit run src/app.py`
- AI provider decision: new provider work should target the Gemini Developer API; the checked-in runtime now uses Gemini for embeddings and text generation
- **Web Intelligence crawler (FastAPI):** optional **`TAVILY_API_KEY`** in `.env` backs Tavily search when Gemini grounded web search returns no results for crawler queries; seed URL phases do not require API keys (see `.env.example` and project `README.md`)
- Embedding cache: flat artifacts under `cache/` using `.npy` vectors, `.json` metadata, and `cache_manifest.json`; the app can bootstrap missing caches on first load when `GEMINI_API_KEY` is configured
- Scrape cache: `cache/scrapes/<sha256(url)>.json`
- Email cache: `cache/emails/<hashed-key>.json`
- Explanation cache: `cache/explanations/<cache-key>.json`, and only successful Gemini responses should be persisted there
- Canonical match-result keys: `total_score` and `factor_scores.{topic_relevance, role_fit, geographic_proximity, calendar_fit, historical_conversion, student_interest, event_urgency, coverage_diversity}` (8 factors)
- Shared runtime contract: dynamic cross-tab state lives in `st.session_state`, with `match_results_df`, `scraped_events`, `feedback_log`, `emails_generated`, and `demo_mode` treated as the live session contract
- CSV-backed event rows use literal headers such as `Event / Program`, `Host / Unit`, and `Volunteer Roles (fit)`
- Pipeline and Volunteer views should consume normalized runtime state, not assume dynamic fields on `LoadedDatasets`
- Demo Mode must affect production call sites, not only helper utilities or isolated tests
- Custom URL discovery is restricted to public `http/https` university hosts and must reject localhost/private-network targets

## Current Sprint Status

- Sprint 5 closeout engineering work is complete on `sprint5-cat3`.
- Latest live verification baseline from the project virtualenv is green: `./.venv/bin/python -m pytest -q` -> `424 passed in 66.40s` (82% coverage).
- Latest targeted Phase 3 regression set is green: `tests/test_discovery_tab.py tests/test_matches_tab.py tests/test_engine.py tests/test_app.py tests/test_acceptance.py tests/test_volunteer_dashboard.py` -> `87 passed in 6.56s`.
- Latest preflight baseline passes with warnings only for un-warmed live caches: missing embedding artifacts plus empty or absent `cache/scrapes/`, `cache/extractions/`, `cache/explanations/`, and `cache/emails/`.
- Sprint 5 review artifact: `Category 3 - IA West Smart Match CRM/docs/reviews/2026-03-21-sprint5-code-review.md`.
- Manual demo-day steps still require a machine with `GEMINI_API_KEY` to warm live caches, a rehearsal pass using the real environment, and completion of the human-run logs under `docs/testing/`. For **Web Intelligence** crawler demos with rich search hits, add **`TAVILY_API_KEY`** (and/or ensure `GEMINI_API_KEY` is set) per `.env.example`.
