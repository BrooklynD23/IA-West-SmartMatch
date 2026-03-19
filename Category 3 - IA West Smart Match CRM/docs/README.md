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
  Provider decision memo for the planned switch from OpenAI to the Gemini Developer API, including the recommended Gemini models and migration notes.
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
- Embedding cache: flat Sprint 0 artifacts under `cache/`
- Scrape cache: `cache/scrapes/<sha256(url)>.json`
- Email cache: `cache/emails/<hashed-key>.json`
- Canonical match-result keys: `total_score` and `factor_scores.{topic_relevance, role_fit, geographic_proximity, calendar_fit, historical_conversion, student_interest}`
- CSV-backed event rows use literal headers such as `Event / Program`, `Host / Unit`, and `Volunteer Roles (fit)`
- Custom URL discovery is restricted to public `http/https` university hosts and must reject localhost/private-network targets
