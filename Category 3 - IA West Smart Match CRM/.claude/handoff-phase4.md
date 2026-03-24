# Phase 4 Handoff — Voice I/O Foundation
# Session Date: 2026-03-23
# Status: PLANNED — READY TO EXECUTE

## NEXT SESSION PROMPT

```
Resume GSD autonomous execution for Category 3 - IA West Smart Match CRM.

Phase 4 (Voice I/O Foundation) is fully planned with 3 verified plans.
Run from repo root: /mnt/c/Users/DangT/Documents/GitHub/HackathonForBetterFuture2026

/gsd:autonomous --from 4
```

---

## PROJECT CONTEXT

- **Project:** Category 3 - IA West Smart Match CRM
- **Branch:** sprint5-cat3
- **Venv:** `.venv/bin/python` (python3.12) — inside `Category 3 - IA West Smart Match CRM/`
- **Test command:** `cd "Category 3 - IA West Smart Match CRM" && .venv/bin/python -m pytest tests/ -x -q --timeout=30`
- **Baseline:** 392+ tests, 1 pre-existing failure (test_embeddings — environment-dependent, IGNORE)
- **GSD .planning directory:** At REPO ROOT (not inside Category 3 subdirectory)
- **Milestone:** v2.0 — Jarvis Agent Coordinator (4 phases: 4-7)
- **Phase sequence:** v1.0 Phases 1-3 (done) → **Phase 4 (execute)** → Phase 5-7 (not started)

## COMPLETED IN THIS SESSION

| Artifact | Path | Status |
|----------|------|--------|
| UI-SPEC | `.planning/phases/04-voice-i-o-foundation/04-UI-SPEC.md` | Verified (5 PASS, 1 FLAG non-blocking) |
| Plan 04-01 | `.planning/phases/04-voice-i-o-foundation/04-01-PLAN.md` | Verified — Voice services (TTS + STT) + unit tests |
| Plan 04-02 | `.planning/phases/04-voice-i-o-foundation/04-02-PLAN.md` | Verified — Command Center UI tab + conversation history |
| Plan 04-03 | `.planning/phases/04-voice-i-o-foundation/04-03-PLAN.md` | Verified — Integration wiring + human verification |
| RESEARCH.md | `.planning/phases/04-voice-i-o-foundation/04-RESEARCH.md` | Updated (af_heart → Bella fix) |
| VALIDATION.md | `.planning/phases/04-voice-i-o-foundation/04-VALIDATION.md` | Updated (file name alignment) |

## PHASE 4 PLAN STRUCTURE

### Wave 1 (parallel)
- **Plan 04-01:** Voice service modules — `src/voice/tts.py` (KittenTTS wrapper), `src/voice/stt.py` (faster-whisper wrapper), dependencies in requirements.txt, TDD tests
- **Plan 04-02:** Command Center UI — `src/ui/command_center.py` (text input, echo replies, chat bubbles), CSS classes in `src/ui/styles.py`, session state keys in `src/runtime_state.py`, TDD tests

### Wave 2 (depends on 04-01 + 04-02)
- **Plan 04-03:** Integration wiring — wire Command Center tab into `src/app.py` as first tab, add TTS playback (sentence-chunked), add push-to-talk STT via streamlit-webrtc, human verification checkpoint

### Requirement Coverage
| Requirement | Plans |
|-------------|-------|
| VOICE-01 (text commands) | 04-02, 04-03 |
| VOICE-02 (TTS playback) | 04-01, 04-03 |
| VOICE-03 (push-to-talk STT) | 04-01, 04-03 |
| VOICE-04 (conversation history) | 04-02, 04-03 |

## KEY DECISIONS LOCKED IN CONTEXT.MD

1. **TTS Voice:** "Bella" (NOT "af_heart" — that was a Kokoro voice, corrected in research)
2. **Sentence-chunked TTS:** Split on `.`/`?`, generate per sentence, play sequentially
3. **Push-to-talk:** streamlit-webrtc SENDONLY, faster-whisper "base" model
4. **Command Center:** First tab, voice panel at top, chat bubbles (coordinator left, Jarvis right)
5. **Transcript insertion:** STT transcript appears in shared input field before processing
6. **Graceful degradation:** All voice features degrade to text-only if libraries unavailable

## BLOCKERS / PREREQUISITES

Before execution begins, these must be validated:
- [ ] KittenTTS wheel installs: `pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl`
- [ ] faster-whisper installs: `pip install faster-whisper`
- [ ] streamlit-webrtc installs: `pip install streamlit-webrtc`
- [ ] soundfile installs: `pip install soundfile`
- [ ] KittenTTS `misaki>=0.9.4` dependency resolves (flagged as concern in STATE.md)

## KNOWN MINOR ISSUES (non-blocking)

1. **VALIDATION.md Per-Task Verification Map** has some requirement IDs slightly mismatched (e.g., 04-01-01 shows VOICE-01 but should be VOICE-02). The plans themselves are correct — this is cosmetic in the tracking doc only.
2. **UI-SPEC Dimension 2 FLAG:** No explicit focal point declaration — visual hierarchy is implied by layout. Non-blocking recommendation only.

## REMAINING PHASES AFTER PHASE 4

| Phase | Name | Status |
|-------|------|--------|
| 5 | Coordinator Core and HITL Approval Gate | Not started (needs discuss → plan → execute) |
| 6 | Agent Tool Wrappers and Result Bus | Not started |
| 7 | NemoClaw Lead Agent and Live Dashboard | Not started |

## GSD AUTONOMOUS WORKFLOW STATE

The autonomous workflow (`/gsd:autonomous --from 4`) will:
1. **Phase 4:** Skip discuss (context exists) → skip plan (plans exist) → EXECUTE → verify
2. **Phases 5-7:** Full cycle: smart discuss → plan → execute → verify each
3. After all phases: audit → complete → cleanup

The workflow should detect that Phase 4 already has plans and proceed directly to execution.
