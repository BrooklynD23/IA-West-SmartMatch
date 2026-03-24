# Phase 5: Coordinator Core and HITL Approval Gate - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Deliver the Gemini-powered intent parser and the human-in-the-loop approval state machine — proving the full voice/text command → intent → propose → approve/reject cycle with stubbed agent execution. Phase 5 replaces the hardcoded echo replies from Phase 4 with real intent parsing and action proposal cards. Real agent dispatch arrives in Phase 6.

</domain>

<decisions>
## Implementation Decisions

### Intent Parsing Design
- Use structured JSON prompt via existing `gemini_client.py` REST pattern — send user text + available actions list, expect `{intent, agent, params, reasoning}` JSON response
- Support 4 core intents: `discover_events`, `rank_speakers`, `generate_outreach`, `check_contacts`, plus `unknown` fallback — maps 1:1 to existing SmartMatch services
- Handle parsing failures with a graceful fallback card showing "Could not understand" with raw text and a rephrase suggestion — no crash, no silent failure
- Run intent parsing inline in Streamlit script thread (~1-2s Gemini call) — result needed immediately to render action card

### Action Card UI
- Each action card shows: agent name, action description, Jarvis reasoning, and editable parameters — matches HITL-01 requirement exactly
- Action cards appear inline in conversation history as Jarvis message bubbles with embedded approve/reject buttons — maintains chronological flow from Phase 4
- Approve/reject via `st.button` with `session_state` tracking per card — each card gets a unique key, button click updates `action_proposals[id].status`, triggers `st.rerun()`
- Edit params flow uses `st.expander` within the card, collapsed by default — expand to edit, then approve

### Approval State Machine
- 5 states: `proposed` → `approved` → `executing` → `completed`/`failed`, plus `rejected` — clean lifecycle matching Phase 6 dispatch contract
- Store approval state in `st.session_state["action_proposals"]` as a dict keyed by UUID — follows established session_state pattern from runtime_state.py
- Multiple proposals queue and coexist with independent state — coordinator can issue several commands before approving
- Phase 5 stub execution: immediate transition to "completed" with mock result after ~1s delay — proves state machine end-to-end without real agents

### Proactive Suggestions (ORCH-04)
- Trigger: data staleness check — if `scraped_events` timestamp > 24h old or empty, Jarvis suggests "Discovery data is stale — re-run scraper?"
- Surface on Command Center tab load — check staleness conditions during render, inject suggestion if not already present
- Use same action card format as parsed intents with `source: "proactive"` flag — consistent approve/reject UX
- Max 1 active proactive suggestion at a time — avoid overwhelming the coordinator

### Claude's Discretion
- Exact Gemini prompt template wording and JSON schema for intent parsing
- CSS styling of action cards (borders, colors, status indicators)
- UUID generation strategy for action proposals
- Mock result text content for stub execution
- Staleness threshold tuning (24h is the starting point)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/gemini_client.py` — `generate_text()` and `_post_json()` for Gemini REST calls; extend with intent-parsing prompt
- `src/ui/command_center.py` — existing Command Center tab with conversation history, voice panel, chat bubbles; extend with action card rendering
- `src/runtime_state.py` — `init_runtime_state()` with session_state initialization pattern; add `action_proposals` key
- `src/voice/tts.py` — TTS synthesis for Jarvis replies; action card results should also be spoken
- `src/config.py` — centralized config with env vars; add intent parsing model config if needed

### Established Patterns
- Tab rendering: `render_command_center_tab()` in `src/ui/command_center.py` — extend, don't replace
- Session state: keys initialized with `if key not in st.session_state` guards in `init_runtime_state()`
- Chat history: `conversation_history` list of dicts with `role`, `text`, `intent`, `timestamp` keys
- HTML rendering: `st.markdown(..., unsafe_allow_html=True)` for chat bubbles with CSS classes
- Service modules: pure Python (no Streamlit imports) — intent parser should follow same pattern

### Integration Points
- `_handle_text_command()` in command_center.py — currently echoes; replace with intent parsing → action proposal flow
- `conversation_history` list — extend entry schema with `action_id` for proposal-type messages
- `init_runtime_state()` — add `action_proposals: {}` session state key
- Existing SmartMatch services: `scrape_university()`, `rank_speakers_for_event()`, `generate_outreach_email()` — these become the real dispatch targets in Phase 6

</code_context>

<specifics>
## Specific Ideas

- Intent parser module at `src/coordinator/intent_parser.py` — pure Python, takes text + action registry, returns structured ParsedIntent dataclass
- Approval engine at `src/coordinator/approval.py` — ActionProposal dataclass with UUID, state machine transitions, no Streamlit dependency
- Proactive suggestion engine at `src/coordinator/suggestions.py` — checks staleness conditions, returns suggestion proposals
- Action card rendering integrated into `_render_conversation_history()` — proposals are entries in conversation_history with `role: "proposal"`
- The 392 existing tests must continue to pass — zero changes to existing function signatures

</specifics>

<deferred>
## Deferred Ideas

- Real agent dispatch and background execution (Phase 6 — ORCH-01, ORCH-02, ORCH-03)
- POC contact management integration (Phase 6 — POC-01, POC-02)
- NemoClaw orchestrator integration (Phase 7)
- Live per-agent dashboard swimlanes (Phase 7 — DASH-01, DASH-02)
- Multiple proactive trigger types beyond data staleness (future enhancement)

</deferred>
