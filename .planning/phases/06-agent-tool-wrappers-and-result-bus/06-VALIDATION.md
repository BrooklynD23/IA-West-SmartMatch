---
phase: 06
slug: agent-tool-wrappers-and-result-bus
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-24
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `Category 3 - IA West Smart Match CRM/pytest.ini` or pyproject.toml |
| **Quick run command** | `cd "Category 3 - IA West Smart Match CRM" && .venv/bin/python -m pytest tests/ -q --ignore=tests/test_e2e_flows.py -x` |
| **Full suite command** | `cd "Category 3 - IA West Smart Match CRM" && .venv/bin/python -m pytest tests/ -q --ignore=tests/test_e2e_flows.py` |
| **Estimated runtime** | ~70 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 70 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | ORCH-01 | unit | `pytest tests/test_tools_discovery.py -x` | ❌ W0 | ⬜ pending |
| 06-01-02 | 01 | 1 | ORCH-01 | unit | `pytest tests/test_tools_matching.py -x` | ❌ W0 | ⬜ pending |
| 06-01-03 | 01 | 1 | ORCH-01 | unit | `pytest tests/test_tools_outreach.py -x` | ❌ W0 | ⬜ pending |
| 06-02-01 | 02 | 1 | ORCH-02, ORCH-03 | unit+integration | `pytest tests/test_result_bus.py -x` | ❌ W0 | ⬜ pending |
| 06-02-02 | 02 | 1 | ORCH-03 | unit | `pytest tests/test_result_bus.py::TestParallelDispatch -x` | ❌ W0 | ⬜ pending |
| 06-03-01 | 03 | 2 | POC-01, POC-02 | unit | `pytest tests/test_contacts_tool.py -x` | ❌ W0 | ⬜ pending |
| 06-04-01 | 04 | 2 | ORCH-01 | integration | `pytest tests/test_command_center.py -x` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_tools_discovery.py` — stubs for discovery tool wrapper (ORCH-01)
- [ ] `tests/test_tools_matching.py` — stubs for matching tool wrapper (ORCH-01)
- [ ] `tests/test_tools_outreach.py` — stubs for outreach tool wrapper (ORCH-01)
- [ ] `tests/test_result_bus.py` — stubs for result bus dispatch + parallel isolation (ORCH-02, ORCH-03)
- [ ] `tests/test_contacts_tool.py` — stubs for POC contacts CRUD + follow-up (POC-01, POC-02)
- [ ] `tests/conftest.py` — add `st.fragment` mock: `_mock_st.fragment = lambda **kw: (lambda f: f)`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real scraped events appear in Command Center after background thread | ORCH-01 | Requires live Gemini API + network | 1. Start app with GEMINI_API_KEY 2. Type "discover events at UCLA" 3. Approve action 4. Wait for results |
| Two parallel agent tasks show independent status | ORCH-03 | Requires visual inspection of UI state | 1. Approve two actions rapidly 2. Verify both show "Executing" 3. Verify results arrive independently |
| POC contacts display in Command Center | POC-01 | Requires visual inspection | 1. Type "check contacts" 2. Approve action 3. Verify contact cards render with history |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 70s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
