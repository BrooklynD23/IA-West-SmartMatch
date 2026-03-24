---
phase: 04-voice-i-o-foundation
plan: "01"
subsystem: voice
tags: [tts, stt, kittentts, faster-whisper, python, pure-python, tdd]
dependency_graph:
  requires: []
  provides:
    - src/voice/tts.py — KittenTTS wrapper: text -> WAV bytes
    - src/voice/stt.py — faster-whisper wrapper: audio bytes -> text
  affects:
    - Category 3 - IA West Smart Match CRM/requirements.txt
    - Category 3 - IA West Smart Match CRM/src/config.py
    - Category 3 - IA West Smart Match CRM/tests/conftest.py
tech_stack:
  added:
    - faster-whisper (STT engine)
    - streamlit-webrtc==0.6.0 (mic capture, used in Plan 02)
    - soundfile (WAV encoding)
    - KittenTTS (TTS engine, installed from GitHub wheel)
  patterns:
    - Lazy imports for heavy model libraries (kittentts, faster_whisper)
    - Module-level mock injection in conftest.py for CI
    - io.BytesIO buffer for in-memory WAV generation
    - tempfile + Path.unlink(missing_ok=True) for safe cleanup
key_files:
  created:
    - Category 3 - IA West Smart Match CRM/src/voice/__init__.py
    - Category 3 - IA West Smart Match CRM/src/voice/tts.py
    - Category 3 - IA West Smart Match CRM/src/voice/stt.py
    - Category 3 - IA West Smart Match CRM/tests/test_voice_tts.py
    - Category 3 - IA West Smart Match CRM/tests/test_voice_stt.py
  modified:
    - Category 3 - IA West Smart Match CRM/requirements.txt
    - Category 3 - IA West Smart Match CRM/src/config.py
    - Category 3 - IA West Smart Match CRM/tests/conftest.py
decisions:
  - Patch sf module at module level in tests (patch src.voice.tts.sf) rather than patching soundfile globally, giving precise control per test
  - Use types.ModuleType stubs for voice libraries in conftest so modules can be imported without library installation
  - Use lazy imports inside functions (from kittentts import KittenTTS) so the module can be imported without the library present at module load time
metrics:
  duration_seconds: 1004
  completed_date: "2026-03-24"
  tasks_completed: 3
  files_created: 5
  files_modified: 3
---

# Phase 04 Plan 01: Voice I/O Foundation Summary

**One-liner:** Pure Python TTS+STT service layer — KittenTTS WAV synthesis and faster-whisper transcription with lazy imports, 15 unit tests, zero Streamlit dependencies.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add Phase 4 dependencies and voice config constants | 8bd749f | requirements.txt, src/config.py, src/voice/__init__.py, tests/conftest.py |
| 2 | Create TTS service module with tests | 85a3e33 | src/voice/tts.py, tests/test_voice_tts.py |
| 3 | Create STT service module with tests | c7be045 | src/voice/stt.py, tests/test_voice_stt.py |

## What Was Built

### TTS Service (`src/voice/tts.py`)
- `load_tts_model()` — lazy-imports KittenTTS, constructs `KittenTTS("KittenML/kitten-tts-mini-0.8")`
- `synthesize_to_wav_bytes(text, model, voice)` — validates input, calls `model.generate()`, encodes to WAV via soundfile
- `split_into_sentences(text)` — regex split on `[.?!]` boundaries for chunked TTS

### STT Service (`src/voice/stt.py`)
- `load_stt_model()` — lazy-imports faster-whisper, constructs `WhisperModel("base", device="cpu", compute_type="int8")`
- `transcribe_audio_bytes(audio_bytes, model)` — handles empty/None input, writes to temp file, calls model.transcribe() with VAD, joins segment texts, cleans up temp file

### Config Constants (`src/config.py`)
```python
KITTENTTS_VOICE: Final[str] = "Bella"
KITTENTTS_MODEL_ID: Final[str] = "KittenML/kitten-tts-mini-0.8"
KITTENTTS_SAMPLE_RATE: Final[int] = 24000
WHISPER_MODEL_SIZE: Final[str] = "base"
WHISPER_COMPUTE_TYPE: Final[str] = "int8"
```

## Test Results

- **15 new unit tests** — all passing
  - 9 TTS tests: WAV bytes, empty/whitespace validation, sentence splitting, model constructor
  - 6 STT tests: string return, empty/None input, temp file cleanup, multi-segment join, model constructor
- **439 existing tests pass** (392 baseline + 13 from Plan 02 + 15 new — minus 6 test files ignored as out-of-scope)
- Pre-existing failure: `test_embeddings.py::test_get_api_key_requires_real_gemini_key` (existed before Phase 4, unrelated to this plan)

## Verification

```
$ grep -c "import streamlit" src/voice/tts.py src/voice/stt.py
src/voice/tts.py:0
src/voice/stt.py:0
```

Both modules have zero Streamlit imports — pure Python testable.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Patched soundfile mock at test level instead of module level**
- **Found during:** Task 2
- **Issue:** The conftest.py mock for `soundfile` was an empty `types.ModuleType` with no attributes. `sf.write()` called in `synthesize_to_wav_bytes()` raised `AttributeError: module 'soundfile' has no attribute 'write'`
- **Fix:** Tests patch `src.voice.tts.sf` directly per-test using `unittest.mock.patch`. A helper `_sf_write_side_effect` writes a real WAV header to the BytesIO buffer so `result[:4] == b"RIFF"` is assertable.
- **Files modified:** tests/test_voice_tts.py
- **Commit:** 85a3e33

## Known Stubs

None — all functions are fully implemented with real logic (lazy imports, real WAV encoding path, real temp file lifecycle). The model libraries (KittenTTS, faster-whisper) are mocked only in tests, not in production code.

## Self-Check: PASSED

- [x] `Category 3 - IA West Smart Match CRM/src/voice/__init__.py` — FOUND
- [x] `Category 3 - IA West Smart Match CRM/src/voice/tts.py` — FOUND
- [x] `Category 3 - IA West Smart Match CRM/src/voice/stt.py` — FOUND
- [x] `Category 3 - IA West Smart Match CRM/tests/test_voice_tts.py` — FOUND
- [x] `Category 3 - IA West Smart Match CRM/tests/test_voice_stt.py` — FOUND
- [x] Commit 8bd749f — Task 1 config/deps
- [x] Commit a4a6ad6 — Task 2 RED tests
- [x] Commit 85a3e33 — Task 2 GREEN implementation
- [x] Commit 84c1191 — Task 3 RED tests
- [x] Commit c7be045 — Task 3 GREEN implementation
