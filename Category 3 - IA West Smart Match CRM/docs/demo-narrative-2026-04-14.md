# IA West Smart Match CRM — Demo Narrative
**Date:** 2026-04-14  
**Category:** Insights Association (Category 3 — Techxedo Team)

---

## Verification snapshot (automated pass, 2026-04-14)

| Check | Result |
|-------|--------|
| Backend `py_compile` | **Passed** — `scripts/seed_demo_db.py`, `src/api/main.py`, `src/api/routers/portals.py`, `src/api/routers/qr.py`, `src/api/routers/outreach.py`, `src/qr/service.py`, `src/api/demo_db.py` (exit code 0) |
| `python scripts/seed_demo_db.py` | **Success** — rewrote `data/demo.db` (students, coordinators, registrations, outreach, meetings, retention nudges, specialists, pipeline, calendar data, mock roles, QR/feedback stats payloads, and related demo tables per seed script) |
| `npm run build` (frontend) | **Success** — Vite production build completed in ~6.5s |
| Demo DB row counts | See table below (post-seed) |

**Post-seed `data/demo.db` row counts**

| Table | Rows |
|-------|------:|
| students | 8 |
| event_coordinators | 5 |
| student_registrations | 12 |
| outreach_threads | 6 |
| meeting_bookings | 5 |
| retention_nudges | 8 |
| mock_roles | 3 |
| calendar_events | 5 |
| calendar_assignments | 3 |
| specialists | 10 |
| pipeline | 40 |

---

## Demo Story (3-Role Journey)

This demo walks judges through three personas, showing how the IA West Smart Match CRM serves students, event coordinators, and IA West administrators.

### Scene 1 — Landing & Role Picker (30 seconds)
- Open `http://localhost:5173`
- Show the landing page: three entry points (Student, Event Coordinator, IA West Admin)
- Click "Student Portal" CTA — note it pre-selects the student role on the login page

### Scene 2 — Student Portal (2 minutes)
- Log in as: alex.rivera@cal.edu (student)
- **Home**: Show the personalized welcome, the membership pipeline nudge (4 events attended → membership invite), and recommended upcoming events
- **My Events**: Show the upcoming registrations with "Add to Calendar" ICS download
- **Past Events**: Show attended event history (from QR check-in data), streak indicator, total engagement
- **Connect**: Show 2 suggested peer connections with shared AI/ML interests highlighted
- **Key message**: "Students discover, register, track their journey, and get nudged toward IA membership — all from one surface."

### Scene 3 — Event Coordinator Portal (2 minutes)
- Log in as: jordan.lee@cpp.edu (event coordinator, Cal Poly Pomona)
- **Home**: Show hosted events summary (2 events), active outreach threads (4), upcoming meetings
- **My Events**: Show the "AI for a Better Future Hackathon" with partial staffing + "Request Match" CTA that leads to AI Matching
- **IA West Contact**: Show outreach threads with IA West contacts, send message, "Launch AI Outreach Agents" button
- **Meetings**: Show confirmed and pending meetings with IA contacts, Join links, Book Meeting dialog
- **Key message**: "Campus coordinators have a dedicated workspace to request speakers, track conversations, and schedule logistics — reducing back-and-forth with IA West."

### Scene 4 — AI Outreach Agents (2.5 minutes)
- From Event Coordinator Portal → Outreach → "Launch AI Outreach Agents"
- Watch 5 agents run in real time: Scout → Copywriter → Scheduler → Planner → Pipeline
- Show the generated email, 3 meeting slot proposals, 5-item follow-up checklist
- Click "Approve & Send" — pipeline updates to "Contacted"
- **Key message**: "Instead of a coordinator manually drafting emails, proposing times, and updating CRM — 5 AI agents do it autonomously. Coordinator just approves."

### Scene 5 — IA West Coordinator Admin (1 minute)
- Log in as: admin@iawest.org (IA Admin)
- Show the AI Matching page — 8-factor score with radar chart
- Show Pipeline — volunteer journey from Matched → Attended → Member Inquiry
- Show QR Stats — referral tracking and membership conversion rates
- **Key message**: "IA West's full toolkit: smart matching, live pipeline visibility, and QR ROI tracking."

### Scene 6 — QR Attendance (30 seconds)
- POST to `/api/qr/attendance/checkin` to simulate a student check-in
- Show that `/api/qr/attendance/history/stu-001` returns the attendance log
- **Key message**: "QR codes don't just track membership interest — they track who showed up, how long they stayed, and feed back into student history."

---

## What We Fixed vs Competitors

| Competitor Feedback | Our Response |
|---|---|
| "Personalization features could be strengthened" | Student portal shows personalized events, suggested peers, streak nudges |
| "Not user-friendly, text heavy" | Separate role portals with focused screens; 3-role login picker |
| "Show how this works for different events" | Coordinator portal shows event-specific staffing, outreach threads, meeting booking |
| "Add sponsorships and interviews" | Outreach thread model supports multi-stakeholder contact management |
| "Interface was not appealing and intuitive" | Design token system used throughout; Apple-aesthetic prep (no raw hex colors); role-specific navigation |

---

## Technical Highlights

- **Synchronized mock dataset**: `seed_demo_db.py` seeds 8 students, 5 coordinators, 12 registrations, 5 meeting bookings, 6 outreach threads, and 8 retention nudges in one script — all linked by stable IDs (verified row counts on 2026-04-14; also 10 specialists, 40 pipeline rows, 5 calendar events, 3 calendar assignments, 3 mock roles)
- **QR dual-mode**: referral/membership ROI (existing) + new attendance check-in log (`attendance-log.jsonl`)
- **5-agent agentic workflow**: SSE stream, named agents, human approval gate — no external dependencies (NemoClaw/OpenClaw not required)
- **3 portals, 1 dataset**: Student, Event Coordinator, and IA Admin all read from the same `demo.db` — data is always synchronized

---

## UI Issues Inventory (for Gemini/Sonnet design pass)

From the 2026-04-14 UI audit:

| # | File | Category | Description |
|---|------|----------|-------------|
| 1 | `CoordinatorOutreach.tsx` | Dense text | Thread cards can be hard to scan on small screens |
| 2 | `StudentHome.tsx` | Dense stats | Stats bar items lack visible labels on mobile |
| 3 | `OutreachWorkflowModal.tsx` | Scroll | Long email body in modal needs scroll affordance |
| 4 | `CoordinatorMeetings.tsx` | Spacing rhythm | ARIA improvements added; spacing could be tightened |
| 5 | Various | Apple aesthetic | All raw palette colors replaced with tokens; remaining improvements are layout hierarchy and whitespace |

**Recommended next design pass:**
- Increase whitespace between sections (more breathing room = Apple feel)
- Replace page headers with subtle `<h1>` + light caption format (less border-heavy)
- Add smooth Framer Motion transitions between pages
- Consider a minimal top navigation bar instead of left sidebar for student portal (more mobile-friendly)
- Use system font stack or Inter for primary text (already using Inter partially)

---

## Where this narrative is referenced

- `Category 3 - IA West Smart Match CRM/README.md` — runbook, portal feature summary, `seed_demo_db.py`, architecture tree
- `Category 3 - IA West Smart Match CRM/docs/README.md` — doc index + current sprint status blurb
- `Category 3 - IA West Smart Match CRM/.status.md` — category status notes (2026-04-14)
- `Category 3 - IA West Smart Match CRM/.planning/STATE.md` — project state vs roadmap distinction
- `tasks/todo.md` — closed execution board for this drop
- `.memory/context/2026-04-14-cat3-portals-demo-narrative.md` — cross-repo handoff
- `.claude/docs/pipeline.md`, `.claude/docs/tech-stack.md` — pipeline + stack rows for Cat 3 fullstack

---

*Generated: 2026-04-14 by Techxedo Team verification pass*
