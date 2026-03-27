# Hackathon for a Better Future 2026

Repository for the **Hackathon for a Better Future 2026** competition entries.

## Category 3 — IA West Smart Match CRM

AI-orchestrated speaker-event matching platform for the Insights Association West Chapter. Uses Gemini LLMs to discover university engagement opportunities, match them with board member volunteers via an 8-factor scoring algorithm, and coordinate outreach through a voice-enabled command center.

**Tech Stack:** Python 3.11 | Streamlit | Gemini API | KittenTTS | faster-whisper | Plotly | pandas | scikit-learn

**Highlights:**
- 8-factor AI matching engine with interactive weight tuning and radar chart visualization
- Voice-enabled Command Center with TTS/STT and natural language intent parsing
- Human-in-the-loop approval workflow with action proposal cards
- Background agent tool dispatch with live swimlane dashboard
- University event discovery via web scraping with LLM extraction
- 580 tests | 25/25 requirements delivered across v1.0 and v2.0 milestones

See [Category 3 - IA West Smart Match CRM/README.md](Category%203%20-%20IA%20West%20Smart%20Match%20CRM/README.md) for full setup and usage instructions.

Quick launch (React + FastAPI testing path):
- Windows PowerShell: `powershell -ExecutionPolicy Bypass -File .\start_cat3_fullstack.ps1`
- Windows CMD: `start_cat3_fullstack.cmd`
- WSL/Linux: `./start_cat3_fullstack.sh`

Those launchers now install the slim `requirements-fullstack.txt` set by default so React + FastAPI startup does not pull the optional Streamlit voice/ML stack on every run. Use `--full-install` when you need the full `requirements.txt` environment.
If the CAT3 backend is already running on `:8000`, the launcher now reuses it; otherwise occupied `:8000`/`:5173` ports are reported explicitly instead of surfacing as a generic startup exit.

## Repository Structure

```
HackathonForBetterFuture2026/
  Category 3 - IA West Smart Match CRM/   # Main application
    src/                                   # Python source code
    tests/                                 # pytest test suite (580 tests)
    data/                                  # CSV datasets and POC contacts
    cache/                                 # Embedding and demo fixture cache
    docs/                                  # Specs, deliverables, and reviews
    scripts/                               # Dev server and E2E test scripts
  .planning/                               # Phase plans and milestone archives
```

## License

Hackathon competition entry — all rights reserved.
