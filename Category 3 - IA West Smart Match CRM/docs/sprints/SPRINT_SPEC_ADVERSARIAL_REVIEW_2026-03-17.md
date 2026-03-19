# Sprint Spec Adversarial Review — 2026-03-17

> Historical review artifact against the pre-reconciliation sprint draft. Keep for traceability, but use `Category 3 - IA West Smart Match CRM/docs/README.md` and the current sprint specs for the up-to-date source map and contracts.

## Executive Summary
The sprint specs are not ready for implementation agents as written. The biggest blockers are contract drift across sprint boundaries, plus a handoff prompt that misstates source-of-truth and simplifies real data contracts in ways that would let a reviewer miss guaranteed breakages.

The architecture and sprint decomposition are still salvageable, but the package/import contract, cache contract, event schema contract, and final deployment/demo contract need revision before implementation begins.

## Handoff Prompt Findings

| # | Severity | Finding | Recommended Fix | Impact if Unfixed |
|---|---|---|---|---|
| H-P1 | Critical | The handoff marks `PLAN.md` as a canonical upstream even though `PLAN.md` explicitly says it is background-only, and it omits the portfolio-level upstreams that the real canonical docs defer to. | Replace the upstream list with: `SPRINT_PLAN.md` as execution authority, `PRD_SECTION_CAT3.md` as feature-detail authority, and `MASTER_SPRINT_PLAN.md` / `STRATEGIC_REVIEW.md` only for schedule/conflict context. Treat `PLAN.md` as background. | A downstream reviewer can approve specs against the wrong source, especially where background analysis conflicts with execution decisions. |
| H-P2 | High | The handoff's schema summary rewrites literal CSV headers into simplified aliases like `Event/Program`, `Host/Unit`, and `Volunteer Roles`, but Sprint 0 validates the real headers (`Event / Program`, `Host / Unit`, `Volunteer Roles (fit)`). | Use literal header names from the CSVs in the handoff, or explicitly say that downstream specs may normalize names only if Sprint 0 defines that normalization contract. | A reviewer can miss real interface drift between Sprint 0 and later sprints. |
| H-P3 | Medium | The required output format has no first-class place for findings about `REVIEW_HANDOFF.md` itself; it assumes all findings are about sprint specs. | Add a `Handoff Prompt Findings` section ahead of sprint-spec findings. | A literal reviewer following the template may omit prompt-level defects entirely. |

## Critical Findings (Must Fix Before Implementation)

| # | Sprint | Task | Finding | Recommended Fix | Impact if Unfixed |
|---|---|---|---|---|---|
| C1 | S0 -> S1 | A0.3-A1.1 | Sprint 0 writes embeddings to flat `cache/` files, but Sprint 1 documents `cache/embeddings/` as the input location for `compute_match_score()`. | Pick one cache layout and use it everywhere. The simplest fix is to keep Sprint 0's flat files and update Sprint 1 references accordingly. | Sprint 1 cannot load the embedding artifacts Sprint 0 produced. |
| C2 | S1 -> S2 | A1.2-A2.4/A2.5 | Sprint 1 ranking results expose `total_score` and factor keys like `topic_relevance`, while Sprint 2 email and `.ics` helpers consume `total`, `topic`, `geo` and also expect event keys like `Event/Program` and `Host/Unit` instead of Sprint 0's literal event schema. | Define one canonical match-result schema and one canonical event schema, then either update Sprint 2 consumers or insert an explicit adapter layer. | Email generation and calendar invites will render generic fallbacks and zero-value score data against real Sprint 0/Sprint 1 outputs. |
| C3 | S2 -> S4 | A2.1-A4.5/A4.9 | Sprint 2 defines scrape cache files under hashed paths in `cache/scrapes/`, but Sprint 4 prewarm and verification expect named files like `cache/ucla_events.json`. Sprint 4 also expects `cache/emails/`, which no prior sprint defines. | Make Sprint 4 verify the actual Sprint 2 cache layout, or redefine Sprint 2 to create the named artifacts and email cache explicitly. | Demo-day verification steps will fail even if scraping and email generation work as specified earlier. |
| C4 | S2 -> S4 | A2.1-A4.5 | Sprint 2 defines `scrape_university()` as returning a metadata dict with `html`, `scraped_at`, `source`, etc., but Sprint 4's cloud workaround redefines it as returning `str` and calls nonexistent helpers `live_scrape_with_playwright()` / `live_scrape_with_bs4()`. | Preserve the Sprint 2 public API in Sprint 4 and use the real helper names and return shape. | Discovery-tab call sites expecting `scrape_result["html"]` and `scrape_result["scraped_at"]` will break in the deployment path. |

## High-Priority Findings (Should Fix)

| # | Sprint | Task | Finding | Recommended Fix |
|---|---|---|---|---|
| H1 | S0 vs S1+ | A0.2-A1.1 | Import style is unresolved: Sprint 0 uses bare imports like `from config import ...`, while Sprint 1+ uses `from src.config import ...`. The project tree also places `app.py` under `src/`, not repo root. | Standardize on one import model and one launch command. If `src/` is the package root, add an explicit package strategy and use `from src...` consistently. |
| H2 | S0/S1 | Overview / DoD | The specs repeatedly claim 77 embeddings are generated, but Sprint 0 only defines embedding artifacts for speakers, events, and courses. Calendar entries are loaded, not embedded. | Change all "77 embeddings" statements to 68, or explicitly add a calendar-embedding task and artifacts. |
| H3 | S3/S4 | A3.7/A4.1/A4.8/A4.9 | `streamlit run app.py` appears in Sprint 3 and Sprint 4, while Sprint 0 and Sprint 1 consistently launch `streamlit run src/app.py`. | Standardize the launch command everywhere and align it with the documented project structure. |
| H4 | S2 | A2.3 | The `Custom URL` path accepts arbitrary user input but the spec only checks for non-empty input; it does not define hostname allowlists, scheme validation beyond browser habit, or private-network blocking. | Add explicit SSRF/input-validation rules for custom URLs: `http/https` only, deny localhost/private IPs/file URLs, and optionally restrict to university domains for demo scope. |

## Medium-Priority Findings (Nice to Fix)

| # | Sprint | Task | Finding | Recommended Fix |
|---|---|---|---|---|
| M1 | S4 | A4.8 | Sprint 4's cleanup table references wrong public names (`rank_matches`, `generate_explanation`, `extract_events_from_html`) and also drifts from the actual scraper helper names. | Update the cleanup checklist to the names actually specified in S1/S2. |
| M2 | S3 | A3.1/A3.2 | Sprint 3 duplicates `DEFAULT_WEIGHTS` locally instead of importing from `src.config`, creating a second source of truth for feedback-based weight suggestions. | Import `DEFAULT_WEIGHTS` from `src.config` and remove the local copy. |
| M3 | S1/S3 | A1.1/A3.1 | Sprint 1 says its canonical metro-region list must match the speaker CSV, but it adds `Orange County / Long Beach`, and Sprint 3 then omits that region from `SPEAKER_METRO_COORDS`. | Either remove that region from the canonical list until the data actually uses it, or define the normalization path that introduces it. |
| M4 | S2 | A2.2/A2.4 | The handoff checklist asks whether malformed GPT JSON has retry handling, but Sprint 2 only parses once and falls back immediately to `[]` or a template email. | Define a bounded retry/backoff policy for malformed JSON and transient API failures. |
| M5 | S3/S4 | A3.5/A4.1 | Demo-mode fixture absence is called out as a failure mode, but the spec only says "don't forget to test it" rather than defining a required validation step or fixture-audit command. | Add an explicit fixture validation step that runs before demo rehearsal and before day-of preflight. |
| M6 | Cross-sprint | A1.2/A3.2 | Speaker and event identity are name-based (`speaker_name`, `event_name`, `speaker_id: Speaker name`), so caches, feedback logs, and `.ics` UIDs are collision-prone if duplicate names ever appear. | Define stable synthetic IDs for speakers and events at load time and use them in caches, logs, and UI state. |

## Low-Priority / Stylistic

- Sprint 4 step 8 hard-codes "Travis Miller expected" in the E2E flow, which is brittle once weights are tunable.
- Sprint 0 project-structure comments mention row-count uncertainty in the data files; that belongs in the audit report, not the canonical folder tree.
- Sprint 2's `check_robots_txt()` falls back to "allowed" on robots fetch errors. That is pragmatic for a demo, but the spec should label it as a conscious hackathon tradeoff.

## Known Issues Confirmation

- H1 `Import style conflict`: Confirmed. It is a real unresolved contract mismatch, though exact runtime failure depends on how Streamlit seeds `sys.path`.
- H2 `Cache path mismatch`: Confirmed.
- H3 `Dict key mismatch`: Confirmed, and the problem is broader than stated because event-field names drift too.
- M1 `cache/embeddings.pkl`: Confirmed.
- M2 `Missing metro region in expansion map`: Partially confirmed. The omission exists, but impact is lower because the current speaker CSV has no `Orange County / Long Beach` rows.
- M3 `Wrong function names in cleanup table`: Confirmed, and Sprint 4 also invents scraper helper names not defined earlier.
- M4 `Incorrect embedding count`: Confirmed, and the same incorrect claim also appears in Sprint 0's overview.
- L1 `Duplicated DEFAULT_WEIGHTS`: Confirmed.
- L2 `Inconsistent run command`: Confirmed, and the inconsistency also appears in Sprint 3.

## Hour Budget Assessment

- Sprint 0: Tight. Playwright setup plus embeddings, caching, data audit, and Streamlit skeleton is more likely a full 2-day sprint than a comfortable 14-16h.
- Sprint 1: Tight. The 6-factor scoring engine is manageable, but 5h for the full Matches tab with radar charts, sliders, and explanation cards is optimistic.
- Sprint 2: Unrealistic. Five-university scraping with cache/fallbacks plus extraction, UI, email, `.ics`, pipeline, and Track B writing work is too much for 3 days.
- Sprint 3: Unrealistic. Feature-freeze on Day 9 is incompatible with the amount of new UI, demo-mode, screenshot, and feedback work still being added here.
- Sprint 4: Tight. The total sprint can work, but 4h for full E2E across all flows and 2h for recording plus editing a reliable backup video are both optimistic.

## Missing Specifications

- Explicit package/import strategy for `src/` and a single supported local/cloud launch command.
- A canonical normalized event schema, if later sprints want aliases instead of literal CSV headers.
- Stable IDs for speakers/events instead of name-based identity.
- A real email-cache contract, if Sprint 4 expects pre-generated cached emails.
- Custom URL validation and SSRF protections.
- Retry/backoff policy for malformed JSON and transient Gemini failures.
- A deterministic fixture-validation step for demo mode.

## Verdict
- [ ] APPROVED — Ready for implementation agents
- [ ] APPROVED WITH REQUIRED FIXES — Fix critical findings, then proceed
- [x] REVISE — Significant rework needed before implementation
- [ ] REJECT — Fundamental issues require re-planning

## Evidence References

- Handoff upstream/source-of-truth section: `REVIEW_HANDOFF.md:34-40`
- Handoff schema summary: `REVIEW_HANDOFF.md:42-51`
- Handoff attack-vector checklist: `REVIEW_HANDOFF.md:124-139`
- `PLAN.md` governance notice: `PLAN.md:17`
- `PRD_SECTION_CAT3.md` governance notice: `PRD_SECTION_CAT3.md:16`
- `SPRINT_PLAN.md` governance notice: `docs/SPRINT_PLAN.md:14`
- Sprint 0 flat cache layout: `sprint-0-foundation.md:41-48`
- Sprint 0 bare imports and literal event schema: `sprint-0-foundation.md:260-283`
- Sprint 0 launch command: `sprint-0-foundation.md:1928-1932`
- Sprint 0 incorrect 77-embeddings overview: `sprint-0-foundation.md:20-22`
- Sprint 1 metro-region claim: `sprint-1-matching-core.md:96-109`
- Sprint 1 cache dir + package imports: `sprint-1-matching-core.md:320-343`
- Sprint 1 ranking result schema: `sprint-1-matching-core.md:930-1006`
- Sprint 1 explanation cache key uses speaker/event names: `sprint-1-matching-core.md:1272-1285`
- Sprint 1 "77 embeddings" DoD: `sprint-1-matching-core.md:2359`
- Sprint 2 scrape cache contract: `sprint-2-discovery-email.md:88-114`, `sprint-2-discovery-email.md:264-293`
- Sprint 2 discovery-tab consumers expect scrape result dict: `sprint-2-discovery-email.md:920-949`
- Sprint 2 email contract drift: `sprint-2-discovery-email.md:1210-1253`
- Sprint 2 `.ics` contract drift: `sprint-2-discovery-email.md:1574-1599`
- Sprint 2 no email-cache path defined: search result only finds scrape cache under `cache/scrapes/`
- Sprint 2 malformed JSON handling: `sprint-2-discovery-email.md:661-678`, `sprint-2-discovery-email.md:708-712`, `sprint-2-discovery-email.md:1278-1310`
- Sprint 2 Custom URL input: `sprint-2-discovery-email.md:864-905`
- Sprint 3 missing metro coord: `sprint-3-polish-freeze.md:48-60`
- Sprint 3 duplicate weights: `sprint-3-polish-freeze.md:596-626`
- Sprint 3 name-based IDs: `sprint-3-polish-freeze.md:396-400`
- Sprint 3 wrong launch command: `sprint-3-polish-freeze.md:1756-1759`
- Sprint 3 fixture-missing callout without validation contract: `sprint-3-polish-freeze.md:1524-1538`, `sprint-3-polish-freeze.md:1577`
- Sprint 4 wrong launch command: `sprint-4-ship.md:34-36`, `sprint-4-ship.md:1138-1149`
- Sprint 4 nonexistent `cache/embeddings.pkl`: `sprint-4-ship.md:411-414`
- Sprint 4 cloud workaround API drift: `sprint-4-ship.md:585-598`
- Sprint 4 wrong cleanup names: `sprint-4-ship.md:947-956`
- Sprint 4 wrong cache prewarm paths: `sprint-4-ship.md:1069-1088`
