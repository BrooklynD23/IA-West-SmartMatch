# Phase 3: Adversarial Audit and Sprint Closure - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning
**Source:** Resumed session handoff plus current local Sprint 5 worktree state

<domain>
## Phase Boundary

Close Sprint 5 for Category 3 by turning the accepted review findings into scoped fixes, preserving the current local rerun fix, rerunning the required verification commands, and refreshing the closeout evidence/docs to the final truthful baseline. This phase does not add new product scope and does not reopen already-complete Phase 1 or Phase 2 work beyond direct fallout from accepted review findings.

</domain>

<decisions>
## Implementation Decisions

### Scope and acceptance
- **D-01:** Treat the four review findings from the prior sidecar audit as accepted closeout work: missing event embeddings for discovered events, missing stable `event_id` or dedupe contract for discovered events, wrong `Host / Unit` semantics for discovered events in proximity scoring, and Volunteer Dashboard undercounting because it still reads only `datasets.events`.
- **D-02:** Preserve the current local rerun fix in `Category 3 - IA West Smart Match CRM/src/ui/discovery_tab.py` and `Category 3 - IA West Smart Match CRM/tests/test_discovery_tab.py` as the starting point for Phase 3 rather than discarding it.
- **D-03:** Keep Sprint 5 scoped to contract fixes, verification, and truthful closure evidence. Do not introduce broader refactors or new product features under the banner of cleanup.

### Data contract and integration behavior
- **D-04:** Discovered events must follow one stable downstream contract across Discovery, Matches, feedback/acceptance, and volunteer/dashboard surfaces so matching, dedupe, persistence, and reporting all refer to the same event identity and field meanings.
- **D-05:** The discovered-event representation must support topic relevance scoring when caches are otherwise healthy; a discovered event silently dropping to `0.0` because no embedding exists is considered broken behavior for this closeout.
- **D-06:** The field used for geographic or regional proximity scoring must not be overloaded with the university display name for discovered events.

### Verification and evidence
- **D-07:** Phase 3 is not complete without rerunning targeted tests for touched modules, full `pytest -q` from the Category 3 project root, and `scripts/sprint4_preflight.py`.
- **D-08:** Closure docs must be updated to the final post-fix verification baseline and must include a code-review artifact for the Sprint 5 diff.
- **D-09:** Because the repo has unrelated dirty files, all Phase 3 commits must use explicit pathspecs and must not touch `.claude/settings.local.json`, `Category 3 - IA West Smart Match CRM/.claude/`, `Category 3 - IA West Smart Match CRM/claude-progress.txt`, or `Category 3 - IA West Smart Match CRM/init.sh`.

### the agent's Discretion
- The exact shape of helper functions, where to centralize discovered-event normalization, and whether to use one or multiple internal helpers is open as long as the final contract is consistent and the code changes stay targeted.
- The exact split between targeted regression commands and broader verification commands is flexible as long as the required baseline commands above are preserved before closeout.

</decisions>

<specifics>
## Specific Ideas

- Current uncommitted fix already adds a flash-message key plus `st.rerun()` so "Add to Matching" becomes visible in the same interaction.
- Current local verification from the handoff:
  - `timeout 180s ./.venv/bin/python -m pytest tests/test_discovery_tab.py tests/test_matches_tab.py tests/test_app.py -q` -> `23 passed in 35.49s`
  - `timeout 300s ./.venv/bin/python -m pytest -q` -> `387 passed in 34.25s`
  - `timeout 180s ./.venv/bin/python scripts/sprint4_preflight.py` -> passes with the same expected cache warnings
- Likely files called out in the handoff:
  - `Category 3 - IA West Smart Match CRM/src/ui/discovery_tab.py`
  - `Category 3 - IA West Smart Match CRM/src/runtime_state.py`
  - `Category 3 - IA West Smart Match CRM/src/ui/matches_tab.py`
  - `Category 3 - IA West Smart Match CRM/src/matching/engine.py`
  - `Category 3 - IA West Smart Match CRM/src/feedback/acceptance.py`
  - `Category 3 - IA West Smart Match CRM/src/app.py`
  - paired tests in discovery, matches, acceptance, and volunteer-dashboard coverage

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Sprint 5 planning and scope
- `.planning/PROJECT.md` — Sprint 5 closeout boundary, core value, constraints, and current decisions.
- `.planning/REQUIREMENTS.md` — `REV-01` and `REV-02` requirements plus the overall Sprint 5 traceability map.
- `.planning/ROADMAP.md` — Phase 3 goal, success criteria, and expected plan breakdown (`03-01` through `03-03`).
- `.planning/STATE.md` — current phase state, blockers, and session continuity.
- `tasks/todo.md` — active Sprint 5 execution board and verification history.

### Category 3 product and closeout authority
- `Category 3 - IA West Smart Match CRM/docs/SPRINT_PLAN.md` — Category 3 sprint authority and scope history.
- `Category 3 - IA West Smart Match CRM/docs/README.md` — current closeout-facing runtime and documentation status.
- `Category 3 - IA West Smart Match CRM/.status.md` — current Category 3 status surface for truthful closeout reporting.

### Current implementation touchpoints
- `Category 3 - IA West Smart Match CRM/src/ui/discovery_tab.py` — existing discovery-to-matching handoff plus the local rerun fix.
- `Category 3 - IA West Smart Match CRM/tests/test_discovery_tab.py` — regression coverage for the local rerun fix and discovery helpers.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `transform_event_for_matching()` in `src/ui/discovery_tab.py`: current normalization point for discovered events entering the matching pool.
- `st.session_state["matching_discovered_events"]`: current session bridge from Discovery to Matches.
- Existing pytest coverage in discovery, matches, app, and acceptance modules: already exercises the high-risk runtime path and can be extended rather than replaced.

### Established Patterns
- Sprint 5 work so far has used targeted runtime fixes plus regression tests, followed by one authoritative verification baseline for docs and governance.
- Streamlit rerender behavior matters for same-interaction visibility; state mutations alone are not sufficient when the app renders Matches before Discovery in the same pass.
- Closeout changes must stay narrow and evidence-driven; doc and governance surfaces are reconciled from live command output rather than inferred totals.

### Integration Points
- Discovered-event data flows from Discovery into Matches, then into acceptance/feedback logging and app-level dashboard views.
- Any new discovered-event identity or embedding behavior must stay compatible with the existing matching engine and post-match persistence/reporting paths.
- Volunteer Dashboard reporting likely needs the same merged-event source used by Matches rather than the base dataset-only event frame.

</code_context>

<deferred>
## Deferred Ideas

- Broader modularization of hot runtime files remains out of scope for Sprint 5.
- New dashboard features, new persistence mechanisms, and non-closeout UX redesign are deferred.

</deferred>

---

*Phase: 03-adversarial-audit-and-sprint-closure*
*Context gathered: 2026-03-21*
