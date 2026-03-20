# Sprint 4 Testing Artifacts

These files support the Sprint 4 ship checklist in `docs/sprints/sprint-4-ship.md`.

## Files

- `test_log.md`
  Manual record for the three end-to-end demo runs.
- `bug_log.md`
  Active and resolved bug tracker for Sprint 4 fix sessions.
- `rehearsal_log.md`
  Manual record for timed rehearsals, backup triggers, and operator notes.

## Preflight

Run the local preflight check before rehearsals or deployment:

```bash
./.venv/bin/python scripts/sprint4_preflight.py
```

Optional JSON report:

```bash
./.venv/bin/python scripts/sprint4_preflight.py --json-out docs/testing/preflight_report.json
```

Optional discovery cache prewarm when network and `GEMINI_API_KEY` are available:

```bash
./.venv/bin/python scripts/sprint4_preflight.py --prewarm-discovery
```

Runtime/deploy contract for Sprint 4:
- `runtime.txt` is pinned to `python-3.11` for Streamlit Cloud.
- `scripts/sprint4_preflight.py` validates runtime content, not just file existence.
