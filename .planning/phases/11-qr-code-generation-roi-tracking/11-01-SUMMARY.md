---
phase: 11-qr-code-generation-roi-tracking
plan: "01"
subsystem: backend
tags: [fastapi, qr, analytics, local-storage, pytest]
dependency_graph:
  requires: []
  provides: [deterministic_referral_codes, qr_api_contract, qr_roi_stats]
  affects:
    - "Category 3 - IA West Smart Match CRM/requirements.txt"
    - "Category 3 - IA West Smart Match CRM/src/api/main.py"
    - "Category 3 - IA West Smart Match CRM/src/api/routers/qr.py"
    - "Category 3 - IA West Smart Match CRM/src/qr/service.py"
    - "Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_qr.py"
tech_stack:
  added: [qrcode, Pillow]
  patterns: [deterministic referral-code hashing, json manifest plus jsonl event log, direct route pytest coverage]
key_files:
  created:
    - "Category 3 - IA West Smart Match CRM/src/api/routers/qr.py"
    - "Category 3 - IA West Smart Match CRM/src/qr/service.py"
    - "Category 3 - IA West Smart Match CRM/tests/test_api_qr.py"
  modified:
    - "Category 3 - IA West Smart Match CRM/requirements.txt"
    - "Category 3 - IA West Smart Match CRM/src/api/main.py"
    - "Category 3 - IA West Smart Match CRM/src/ui/data_helpers.py"
decisions:
  - "Use one deterministic referral code per speaker-event pair so repeated QR generation refreshes the same attribution key"
  - "Persist QR definitions in a JSON manifest and scans in append-only JSONL under `data/qr` to keep the audit trail reconstructable"
  - "Verify the QR API via direct route/helper calls instead of `TestClient`, matching the environment-safe test pattern already used in Phase 10"
metrics:
  completed_date: "2026-03-26"
  tasks_completed: 2
  files_changed: 6
---

# Phase 11 Plan 01: Backend QR and ROI Summary

One-liner: added a deterministic QR generation and scan-tracking backend with local persistence, redirect attribution, and aggregate ROI stats for the React app.

## Tasks Completed

| Task | Name | Result |
|------|------|--------|
| 1 | Add QR dependencies and a deterministic QR service module | Completed in worktree |
| 2 | Expose QR generate/scan/stats endpoints through FastAPI | Completed in worktree |

## What Was Built

### Deterministic QR service

- Added `qrcode` and `Pillow` to `requirements.txt`.
- Created `src/qr/service.py` with deterministic referral-code generation based on normalized speaker-event pairs.
- Added PNG QR rendering, manifest persistence, scan-log persistence, and aggregate stat helpers.
- Persisted QR artifacts under `data/qr/` using `manifest.json` plus append-only `scan-log.jsonl`.

### FastAPI QR contract

- Added `src/api/routers/qr.py` and mounted it from `src/api/main.py` at `/api/qr`.
- `POST /api/qr/generate` returns the deterministic referral metadata plus QR image payload.
- `GET /api/qr/scan/{referral_code}` records the scan and redirects with referral metadata attached as query params.
- `GET /api/qr/stats` returns per-referral and rollup ROI data, including membership-interest conversions.

### Focused backend coverage

- Extended `src/ui/data_helpers.py` with cache-aware loaders for the QR manifest and scan log.
- Added `tests/test_api_qr.py` to verify deterministic code reuse, redirect logging, mounted routes, and stats shape.
- Tests run against isolated temp storage and the real QR service path.

## Verification Results

```bash
cd "Category 3 - IA West Smart Match CRM" && timeout 60s ./.venv/bin/python -m pytest tests/test_api_qr.py -q
```

Result:

```text
4 passed in focused QR coverage
```

## Success Criteria Verification

- [x] QR generation is deterministic for a speaker-event pair
- [x] Scans are recorded before redirect and retain referral metadata
- [x] ROI stats expose scan and conversion counts in a React-consumable shape
- [x] Local persistence remains file-backed and test-covered

## Deviations from Plan

- The QR image contract currently standardizes on PNG data URLs rather than adding a second SVG rendering pipeline. This kept the backend simpler while still satisfying preview and download behavior.

## Known Stubs

- Browser-backed scan/redirect verification is still pending because the Playwright browser runtime was unavailable in-session.

## Self-Check

PASSED
