---
phase: 18
slug: tech-debt-cleanup-code-fixes
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-28
---

# Phase 18 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (Python) + tsc --noEmit (TypeScript) |
| **Config file** | No pytest.ini — uses defaults |
| **Quick run command** | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -x -q 2>&1 \| tail -5` |
| **TS check command** | `cd "Category 3 - IA West Smart Match CRM/frontend" && npx tsc --noEmit` |
| **Full suite command** | `cd "Category 3 - IA West Smart Match CRM" && python -m pytest tests/ -v && cd frontend && npx tsc --noEmit` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `npx tsc --noEmit` for TS tasks; `pytest tests/ -k crawler -x` for Python task
- **After every plan wave:** Run full suite (pytest + tsc --noEmit + npm run build)
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 18-01-00 | 01 | 0 | DEBT-02 | unit (Python) | `python -m pytest tests/test_crawler_timestamp.py -x -q` | **Created by Task 0** | ⬜ pending |
| 18-01-01 | 01 | 1 | DEBT-02 | unit (Python) | `python -m pytest tests/test_crawler_timestamp.py -x -q` | ✅ (from Task 0) | ⬜ pending |
| 18-01-02 | 01 | 1 | DEBT-01 | type check (TS) | `npx tsc --noEmit` | ✅ existing | ⬜ pending |
| 18-01-03 | 01 | 1 | DEBT-03 | manual | Visual inspection of REQUIREMENTS.md | ✅ manual | ⬜ pending |
| 18-01-04 | 01 | 1 | DEBT-04 | build check | `npx tsc --noEmit 2>&1 \| grep -E "LandingPage\|LoginPage"` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_crawler_timestamp.py` — created by Task 0 with 3 tests: behavioral timestamp uniqueness, ISO-8601 format validation, and source-inspection (RED until Task 1 fix)
- [ ] TypeScript compile-time assertion for DEBT-01 — ensure `"csv"` is a valid `WithSource.source` type

*Existing tsc and pytest infrastructure covers DEBT-03 (manual) and DEBT-04 (build check).*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| REQUIREMENTS.md traceability rows present and DEBT-03 marked complete | DEBT-03 | Documentation check, not automatable | Open `.planning/REQUIREMENTS.md` and confirm DB-01–CRAWLER-03 rows exist with Phase 17 mapped |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
