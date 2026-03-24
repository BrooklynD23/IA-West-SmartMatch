# Phase 6: Agent Tool Wrappers and Result Bus - Context

**Gathered:** 2026-03-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver real agent execution for approved actions — wrapping existing SmartMatch services as background-threaded tool wrappers, establishing a result bus for non-blocking result delivery to the Command Center, adding POC contact management, and proving parallel task isolation. Phase 6 replaces Phase 5's stub execution with real service calls while maintaining the same approval state machine contract.

</domain>

<decisions>
## Implementation Decisions

### Tool Wrapper Architecture
- Tool wrappers live in `src/coordinator/tools/` package with one module per service — consistent with Phase 5's `src/coordinator/` pattern
- Thin adapter functions that import and call existing functions unchanged (e.g., `scrape_university()`, `rank_speakers_for_event()`) — per STATE.md "zero signature changes" constraint
- Dict mapping intent names to tool callables, registered at module level — mirrors Phase 5's intent→agent mapping
- Tools call existing functions directly (no NemoClaw) — this IS the fallback path; Phase 7 adds NemoClaw as an optional orchestration layer on top

### Background Threading & Result Bus
- `threading.Thread(daemon=True)` + `queue.Queue` per task — per STATE.md decision; each approved action spawns a daemon thread, result posted to queue
- `st.fragment(run_every=2)` polling loop checks queue, updates `action_proposals[id].status` — per STATE.md decision
- Each `ActionProposal` gets its own `Queue` instance stored in session state — independent status, no cross-task corruption
- Thread catches exceptions, posts `{status: "failed", error: str}` to its queue — action card shows error with retry option

### POC Contact Data Layer & Display
- JSON file (`data/poc_contacts.json`) loaded into session state — hackathon-appropriate, no DB needed; seed with sample contacts from CPP event data
- Contact schema: `{name, email, org, role, comm_history: [{date, type, summary}], last_contact, follow_up_due}` — covers POC-01 (history) and POC-02 (follow-up tracking)
- New section within Command Center — expandable contact cards, overdue contacts highlighted, triggered by `check_contacts` intent
- Proactive suggestion (same as Phase 5 staleness check) — on Command Center load, check `follow_up_due < today`, inject suggestion card for overdue contacts

### Claude's Discretion
- Exact thread naming and daemon configuration
- Queue timeout values for polling
- POC seed data content (derived from CPP event contacts)
- Result formatting for Command Center display
- Retry logic details for failed actions

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/coordinator/approval.py` — ActionProposal dataclass with UUID and state machine (proposed→approved→executing→completed/failed)
- `src/coordinator/intent_parser.py` — ParsedIntent with intent names mapping to services
- `src/coordinator/suggestions.py` — Proactive suggestion engine with staleness checks
- `src/scraping/scraper.py` — `scrape_university()` for discovery tool wrapper
- `src/matching/engine.py` — `rank_speakers_for_event()`, `rank_speakers_for_course()` for matching tool wrapper
- `src/outreach/email_gen.py` — `generate_outreach_email()` for outreach tool wrapper
- `src/runtime_state.py` — Session state initialization pattern
- `src/ui/command_center.py` — Command Center tab with conversation history and action cards

### Established Patterns
- Pure Python service modules with no Streamlit imports (coordinator/, matching/, scraping/)
- Session state initialization with `if key not in st.session_state` guards
- Action proposals stored in `st.session_state["action_proposals"]` keyed by UUID
- Chat history as list of dicts with `role`, `text`, `intent`, `timestamp`, `action_id` keys
- `st.fragment(run_every=2)` for polling (established in Phase 5 decisions)

### Integration Points
- `approval.py` state machine transitions — `approved` status triggers tool dispatch instead of stub
- `_handle_text_command()` in command_center.py — already routes through intent parser → approval
- `init_runtime_state()` — extend with result bus keys and POC contact state
- Proactive suggestions — extend with overdue contact check alongside staleness check

</code_context>

<specifics>
## Specific Ideas

- Discovery tool: `src/coordinator/tools/discovery_tool.py` — wraps `scrape_university()`, returns structured event list
- Matching tool: `src/coordinator/tools/matching_tool.py` — wraps `rank_speakers_for_event()`, returns ranked speaker list with scores
- Outreach tool: `src/coordinator/tools/outreach_tool.py` — wraps `generate_outreach_email()`, returns generated email content
- Contacts tool: `src/coordinator/tools/contacts_tool.py` — manages POC contacts CRUD and follow-up queries
- Result bus: `src/coordinator/result_bus.py` — thread dispatch, queue management, status polling helper
- POC data: `data/poc_contacts.json` — seeded from CPP event contacts data
- All 453+ existing tests must continue to pass — zero changes to existing function signatures

</specifics>

<deferred>
## Deferred Ideas

- NemoClaw orchestrator integration replacing direct dispatch (Phase 7)
- Live per-agent swimlane dashboard with real-time status (Phase 7 — DASH-01, DASH-02)
- Jarvis speaking result summaries via TTS (Phase 7)
- POC follow-up as proactive Jarvis suggestion in HITL flow (Phase 7 — POC-03)
- Agent self-modification or dynamic tool creation (out of scope — ORCH-05)

</deferred>
