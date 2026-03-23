---
phase: 4
slug: voice-i-o-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.3.4 |
| **Config file** | none — uses pytest defaults via Makefile |
| **Quick run command** | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x -q --timeout=30` |
| **Full suite command** | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x` |
| **Estimated runtime** | ~12 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x -q --timeout=30`
- **After every plan wave:** Run `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | VOICE-01 | unit | `pytest tests/test_command_center.py -x` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | VOICE-04 | unit | `pytest tests/test_command_center.py -x` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | VOICE-02 | unit | `pytest tests/test_tts.py -x` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 1 | VOICE-02 | manual | Browser TTS playback | N/A | ⬜ pending |
| 04-03-01 | 03 | 2 | VOICE-03 | unit | `pytest tests/test_stt.py -x` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 2 | VOICE-03 | manual | Browser mic capture | N/A | ⬜ pending |
| 04-ALL | ALL | ALL | baseline | regression | `pytest tests/ -x` (392 pass) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tts.py` — stubs for VOICE-02 (KittenTTS synthesis returns valid WAV bytes)
- [ ] `tests/test_stt.py` — stubs for VOICE-03 (faster-whisper transcription returns text from audio)
- [ ] `tests/test_command_center.py` — stubs for VOICE-01, VOICE-04 (text input handling, conversation history state)
- [ ] KittenTTS wheel installed: `pip install https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl`
- [ ] faster-whisper installed: `pip install faster-whisper`
- [ ] streamlit-webrtc installed: `pip install streamlit-webrtc`
- [ ] soundfile installed: `pip install soundfile`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| TTS audio plays in browser | VOICE-02 | Requires browser audio context + user interaction | 1. Submit text command 2. Verify st.audio widget appears 3. Click play (or verify autoplay) 4. Hear Jarvis voice |
| Push-to-talk mic capture | VOICE-03 | Requires browser mic access + WebRTC | 1. Click push-to-talk 2. Speak a sentence 3. Click stop 4. Verify transcript appears in input field |
| Conversation history scrollable | VOICE-04 | Visual layout verification | 1. Submit 5+ commands 2. Verify scroll appears 3. Verify all exchanges visible in chronological order |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
