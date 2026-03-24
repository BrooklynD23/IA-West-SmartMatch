---
phase: 07
slug: nemoclaw-lead-agent-and-live-dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 07 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | Category 3 - IA West Smart Match CRM/tests/conftest.py |
| **Quick run command** | `cd "Category 3 - IA West Smart Match CRM" && .venv/bin/python -m pytest tests/ -x -q --tb=short` |
| **Full suite command** | `cd "Category 3 - IA West Smart Match CRM" && .venv/bin/python -m pytest tests/ -q --tb=short` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | DASH-01 | unit | `pytest tests/test_swimlane_dashboard.py -x` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | DASH-02 | unit | `pytest tests/test_swimlane_dashboard.py -x` | ❌ W0 | ⬜ pending |
| 07-01-03 | 01 | 1 | POC-03 | unit | `pytest tests/test_suggestions.py -x` | ✅ | ⬜ pending |
| 07-02-01 | 02 | 2 | DASH-01 | unit | `pytest tests/test_nemoclaw_adapter.py -x` | ❌ W0 | ⬜ pending |
| 07-02-02 | 02 | 2 | DASH-02 | integration | `pytest tests/test_command_center.py -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_swimlane_dashboard.py` — stubs for DASH-01, DASH-02
- [ ] `tests/test_nemoclaw_adapter.py` — stubs for NemoClaw adapter with fallback
- [ ] Existing `tests/conftest.py` — already has shared fixtures and Streamlit mocks

*Existing infrastructure covers most phase requirements. New test files needed for new modules only.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Swimlane cards update visually within 2s | DASH-02 | Requires live Streamlit render + timing observation | Load Command Center, dispatch agent, observe card status changes within 2s polling interval |
| TTS speaks result summary aloud | N/A (demo polish) | Requires audio hardware | Approve an action, listen for TTS output |
| NemoClaw dispatch via NGC API | DASH-01 | Requires NGC API key + network | Set USE_NEMOCLAW=1, approve action, verify NemoClaw log entries |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
