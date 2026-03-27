# Requirements: IA West SmartMatch CRM

**Defined:** 2026-03-26
**Core Value:** A coordinator can use voice or text to command an AI assistant that orchestrates parallel agents for event discovery, speaker matching, and outreach, with human approval gating every action.

## v3.1 Requirements

Requirements for the Demo Readiness milestone. Each maps to roadmap phases.

### Verification

- [ ] **VERIFY-01**: Playwright automated test demonstrates QR code generation and scan attribution flowing end-to-end in the browser
- [ ] **VERIFY-02**: Playwright automated test demonstrates coordinator feedback submission and weight-shift analytics rendering in the browser
- [ ] **VERIFY-03**: UAT guide documents live voice/mic workflow steps with expected outcomes so a human reviewer can run a structured walkthrough

### Build Quality

- [ ] **BUILD-01**: React production build completes without chunk-size warnings

### Demo Polish

- [x] **POLISH-01**: All internal "Phase #N" labels removed from user-facing UI text across all pages
- [x] **POLISH-02**: All page headings, button labels, and body copy are concrete and demo-ready (no placeholder or dev-flavored text)
- [x] **POLISH-03**: Smooth scrolling applied across all pages and view transitions
- [ ] **POLISH-04**: All charts, images, and data visualizations load real data or fall back gracefully to hardcoded mock data when unavailable
- [ ] **POLISH-05**: Any view displaying fallback/mock data shows a discrete "Demo Mode" indicator visible to the coordinator

## Future Requirements

Tracked but deferred beyond v3.1.

### Testing

- Gmail integration for generated outreach emails — captured as future phase

### Infrastructure

- Browser-backed smoke pass for additional coordinator workflows (expanded beyond QR/feedback)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Production auth/scaling | Hackathon scope — demo-first constraints remain |
| Cloud database | Local CSV/JSON storage sufficient for demo |
| Mobile app | Web-first, not required for hackathon submission |
| Multi-tenant support | Single-tenant demo scope |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| POLISH-01 | Phase 13 | Complete |
| POLISH-02 | Phase 13 | Complete |
| POLISH-03 | Phase 13 | Complete |
| POLISH-04 | Phase 14 | Pending |
| POLISH-05 | Phase 14 | Pending |
| BUILD-01 | Phase 15 | Pending |
| VERIFY-01 | Phase 15 | Pending |
| VERIFY-02 | Phase 15 | Pending |
| VERIFY-03 | Phase 16 | Pending |

**Coverage:**
- v3.1 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-26*
*Last updated: 2026-03-26 after v3.1 roadmap creation*
