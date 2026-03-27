---
phase: 13
slug: demo-polish
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-26
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — no test framework configured in this project |
| **Config file** | None |
| **Quick run command** | `grep -rn "Phase [0-9]\+" "Category 3 - IA West Smart Match CRM/frontend/src" --include="*.tsx" --include="*.ts"` (expect no output) |
| **Full suite command** | Manual visual review — open all pages in browser |
| **Estimated runtime** | ~30 seconds (grep) + ~5 minutes (visual review) |

---

## Sampling Rate

- **After every task commit:** Run the grep command above — expect zero matches
- **After every plan wave:** Open browser, navigate all routes, confirm scroll-to-top behavior
- **Before `/gsd:verify-work`:** All three requirements pass manual visual review

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 13-01 | 01 | 1 | POLISH-01 | Smoke (grep) | `grep -rn "Phase [0-9]\+" ... --include="*.tsx"` → no output | N/A | ⬜ pending |
| 13-02 | 01 | 1 | POLISH-02 | Manual visual | Open each page, inspect headings and pills | N/A | ⬜ pending |
| 13-03 | 01 | 1 | POLISH-03 | Manual visual | Navigate from scrolled page to new route, confirm scroll resets | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure (grep commands) covers all phase requirements. No Wave 0 test file creation is needed.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| No dev-flavored strings in visible headings/pills | POLISH-02 | No test framework; visual copy review | Open Landing, Dashboard, AIMatching, Volunteers, Outreach, Pipeline, Calendar in browser; inspect all headings and body text |
| Scroll resets to top on route change | POLISH-03 | Browser interaction required | Scroll down on any page, click a sidebar nav link, confirm viewport jumps to top smoothly |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: grep check after each task covers POLISH-01 continuously
- [ ] Wave 0: not applicable (no test framework)
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
