# Audit: Pre-Demo 1.0

**IA West Smart Match CRM** — end-to-end browser + persistence verification (Cursor browser MCP + local shell).

**Audit date:** 2026-03-28  
**SPA base URL used:** `http://localhost:5174` (Vite chose **5174** because **5173** was in use.)

---

## Environment

| Component | Expected | Actual during audit |
|-----------|----------|---------------------|
| Vite | `npm run dev` / port 5173 | **5174** (port conflict) |
| FastAPI | `127.0.0.1:8000` | **8002** for full routes (see blockers) |
| Proxy | `/api` → backend | Temporarily pointed at **8002** for this session; repo `vite.config.ts` reverted to **8000** after audit |

---

## Functional checklist

| Item | Result | URL tested | Notes |
|------|--------|------------|--------|
| Landing — hero metrics, regional pills, opportunity density / school context | **Pass** | `http://localhost:5174/` | Metrics and LA / San Diego / Bay Area surfaced. |
| Login → dashboard | **Pass** | `http://localhost:5174/login` → `/dashboard` | Demo credentials accepted. |
| Dashboard — KPIs/charts | **Pass** | `/dashboard` | Live summary cards and charts present. |
| Connect → Outreach Workflow modal, dismiss | **Pass** | `/dashboard` | Modal opened and closed cleanly. |
| Web Crawler Feed + Start Crawl | **Pass** | `/dashboard` | “Crawling…” then completion ~41s. |
| Opportunities — Find Best Matches → AI Matching | **Pass** | `/opportunities` → `/ai-matching` | Navigation OK. |
| Match Volunteers — event pre-selected (router state) | **Fail** | `/opportunities` → `/ai-matching` | `Opportunities` passes `navigate(..., { state: { eventName } })`, but `AIMatching` overwrites selection with `data[0]` in `fetchEvents`; combobox stayed default event. |
| AI Matching — rankings, Record Feedback | **Pass** | `/ai-matching` | Rankings loaded; feedback submitted. |
| Outreach — templates, Web Intelligence, Start Crawl | **Pass** | `/outreach` | Templates, quick actions, crawler section present. |
| Volunteers / Pipeline / Calendar — load | **Pass (light)** | `/volunteers`, `/pipeline`, `/calendar` | No hard route failures; thin initial a11y snapshots before full paint. |
| Sidebar nav click (automation) | **Fail (tooling)** | `/dashboard` | MCP could not scroll “Opportunities” into view; direct navigation worked. |

---

## Local persistence evidence

### A) SQLite — `data/smartmatch.db`

| Phase | `LastWriteTime` (local) | `SELECT COUNT(*) FROM web_crawler_events` |
|-------|-------------------------|-------------------------------------------|
| Before crawl | `3/27/2026 10:48:53 PM` | **0** |
| After crawl | `3/28/2026 12:57:01 AM` | **35** |

**Sample rows** (`ORDER BY crawled_at DESC LIMIT 5` — seed batch shared one timestamp):

- `https://www.cpp.edu/cba/digital-innovation/what-we-do/ai-hackathon.shtml`, `found`, `2026-03-28T07:56:44.789405+00:00`
- Additional seed URLs in the same insert batch.

**API alignment** (live app on port used during audit):

```http
GET http://127.0.0.1:8002/api/crawler/results
```

Response included `"count": 35`, `"source": "live"`, consistent with SQLite.

### B) File-backed feedback — `data/feedback/`

| Phase | `feedback-log.jsonl` line count | `feedback-log.jsonl` mtime | `weight-history.json` mtime |
|-------|---------------------------------|------------------------------|-----------------------------|
| Before UI feedback | **1** | `3/27/2026 6:15:35 PM` | `3/27/2026 6:15:36 PM` |
| After Record Feedback | **2** | `3/28/2026 12:57:47 AM` | `3/28/2026 12:57:47 AM` |

**New JSONL entry (abridged, demo data):**

```json
{
  "entry_id": "fb-690277bc1c67",
  "event_name": "AI Hackathon (CPP hub page)",
  "speaker_name": "Rob Kaiser",
  "timestamp": "2026-03-28T07:57:47.942503Z",
  "decision": "accept"
}
```

---

## Console / UX notes

- Vite HMR + React DevTools suggestion (informational).
- **Radix:** `DialogContent` / `DialogTitle` accessibility warnings when modals open.
- **React:** `forwardRef` warning on `DialogOverlay` / `SlotClone` when opening Outreach workflow and AI Matching dialogs.

No uncaught exceptions observed on exercised flows.

---

## Blockers encountered and mitigations

1. **Port 8000 — wrong or stale API**  
   Listener on `8000` served an older surface: OpenAPI had **no** `/api/crawler/*`; `GET /api/crawler/results` returned **404**.  
   **Mitigation:** Run current `src.api.main:app` on **8002** for the audit; align Vite proxy to the same process for demo.

2. **Vite 5173 busy**  
   Dev server bound to **5174**. Use the printed Local URL for the SPA and EventSource via proxy.

3. **Missing `qrcode` on default Python**  
   `ModuleNotFoundError: qrcode` when starting uvicorn without venv deps.  
   **Mitigation:** `python -m pip install "qrcode[pil]"` or use a Windows-native venv with `requirements.txt` installed.

4. **Project `.venv`**  
   Unix-style layout (`bin/`, no `Scripts\python.exe`) on this machine — use a working Python environment with project dependencies.

5. **Browser automation**  
   Sidebar link required scroll recovery; **direct URL navigation** was reliable.

---

## Recommended fix before Demo 1.0 (product)

**Router state for event pre-selection on AI Matching:** In `AIMatching`, read `useLocation().state?.eventName` and set `selectedEventName` after events load **without** unconditionally overwriting with `data[0]` when navigation state is present.

---

## Sign-off

- **Crawler persistence:** Verified (0 → 35 rows, DB mtime + API `count` aligned).  
- **Feedback persistence:** Verified (JSONL +1 line, weight-history touched).  
- **Gating issues for demo narrative:** Free **8000** for canonical setup **or** document proxy port; fix **Match Volunteers → pre-selected event** if that story is part of 1.0.
