# IA West Smart Match CRM

AI-orchestrated speaker-event matching for the **Insights Association West Chapter**. Built for **Hackathon for a Better Future 2026** (Category 3).

---

## Run the full application

The “full” dev stack is **two processes**:

| Service | Purpose | Default URL |
|--------|---------|-------------|
| **Streamlit** | Main UI (`src/app.py`) | [http://127.0.0.1:8501](http://127.0.0.1:8501) |
| **Dev backend** | Small health API used by demos/ops | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) |

Use the **start scripts** below. They sync the slim React + FastAPI dependency set from `requirements-fullstack.txt` by default, then launch both services with staged terminal status output. Use `--full-install` or `pip install -r requirements.txt` if you also need the legacy Streamlit + Jarvis voice stack in the same venv.

**First-time setup** (once): create a virtualenv, install deps, copy env — see [Environment setup](#environment-setup). All commands assume your **current working directory** is this folder:

`Category 3 - IA West Smart Match CRM/`

---

### Quick start for teammates: React + FastAPI (v3 path)

If you want the React app (`:5173`) with the FastAPI backend (`:8000`), use the launcher below.
It auto-detects **Windows vs WSL/Linux**, syncs deps (unless skipped), starts both services, and prints the exact URLs.

From the repo root (`HackathonForBetterFuture2026/`):

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy Bypass -File .\start_cat3_fullstack.ps1
```

**Windows (CMD):**

```cmd
start_cat3_fullstack.cmd
```

**WSL2 / Linux:**

```bash
chmod +x ./start_cat3_fullstack.sh
./start_cat3_fullstack.sh
```

What it launches:
- React UI: `http://127.0.0.1:5173`
- FastAPI health: `http://127.0.0.1:8000/api/health`

Optional flags:
- `--skip-install` to skip dependency sync
- `--force-install` to ignore the cached install state and resync dependencies
- `--full-install` to use `requirements.txt` instead of `requirements-fullstack.txt`
- `--no-browser` to suppress auto-open
- `--frontend-port <port>` and `--backend-port <port>` to change ports
- `--frontend-host <host>` and `--backend-host <host>` to change bind hosts

If `:8000` is already serving the CAT3 FastAPI health endpoint, the launcher reuses it instead of failing on a duplicate bind. If another process owns `:8000` or `:5173`, the launcher now reports the occupied port explicitly so you can stop it or pick a different port.

---

### Option 1 — Start scripts (recommended)

#### Windows (PowerShell)

```powershell
cd "C:\path\to\HackathonForBetterFuture2026\Category 3 - IA West Smart Match CRM"
powershell -ExecutionPolicy Bypass -File .\scripts\start_dev.ps1
```

Optional: custom Python or ports:

```powershell
.\scripts\start_dev.ps1 -PythonExe "C:\Python312\python.exe" -BackendPort 8000 -FrontendPort 8501
```

The script opens **two** windows (backend + Streamlit). Close both to stop.

#### Windows (Command Prompt)

```cmd
cd /d "C:\path\to\HackathonForBetterFuture2026\Category 3 - IA West Smart Match CRM"
scripts\start_dev.cmd
```

Uses `.venv\Scripts\python.exe` by default. Override with `set PYTHON_EXE=C:\path\to\python.exe` before running if needed.

#### WSL2 or Linux (Bash)

From a clone on a Linux filesystem (recommended under WSL: `~/projects/...` rather than `/mnt/c/...` for faster I/O):

```bash
cd "/path/to/HackathonForBetterFuture2026/Category 3 - IA West Smart Match CRM"
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

If the repo lives under `/mnt/c/...`, the same commands work; just ensure `.venv` was created **inside WSL** with Linux Python (`python3 -m venv .venv`).

Environment overrides:

```bash
export BACKEND_PORT=8000
export FRONTEND_PORT=8501
# Optional: use a specific interpreter
export PYTHON_BIN="$PWD/.venv/bin/python"
./scripts/start_dev.sh
```

Stop: `Ctrl+C` in the terminal (the script runs Streamlit in the foreground and kills the backend on exit).

---

### Option 2 — Manual (two terminals)

Same result as the scripts; useful for debugging.

**Terminal A — backend**

```bash
# Windows (venv activated or full path to python)
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts\dev_backend.py --host 127.0.0.1 --port 8000
```

```bash
# WSL2 / Linux
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/dev_backend.py --host 127.0.0.1 --port 8000
```

**Terminal B — Streamlit**

```bash
# Windows
.venv\Scripts\python.exe -m streamlit run src\app.py --server.port 8501 --server.address 127.0.0.1
```

```bash
# WSL2 / Linux
.venv/bin/python -m streamlit run src/app.py --server.port 8501 --server.address 127.0.0.1
```

**Streamlit** is pinned in `requirements.txt` (e.g. **1.42.2**) for reproducible behavior.

---

### Open the app in your browser

- UI: **http://127.0.0.1:8501** (or **http://localhost:8501**)
- Health check: **http://127.0.0.1:8000/health**

**WSL2:** On current Windows + WSL, `localhost` from Windows usually forwards to WSL. If the page does not load from Edge/Chrome on Windows, try from a browser inside WSL, or run `ip addr show eth0` in WSL and use that address (less common).

---

### Troubleshooting (run)

| Issue | What to try |
|--------|-------------|
| `ModuleNotFoundError: No module named 'src'` | Run Streamlit from **this** directory (the Category 3 root), not from `src/`. Use `python -m streamlit run src/app.py`. |
| Port already in use | Change ports: PowerShell `-FrontendPort 8502 -BackendPort 8001`, or set `FRONTEND_PORT` / `BACKEND_PORT` before `start_dev.sh`. |
| No `.venv` | Follow [Environment setup](#environment-setup). |
| Voice / WebRTC warnings | See [docs/handoffs/jarvis-voice-webrtc-enablement.md](docs/handoffs/jarvis-voice-webrtc-enablement.md). |

---

## Environment setup

### Prerequisites

- **Python 3.11+** (3.11 or 3.12 recommended if you want full **KittenTTS**; on 3.13+, `requirements.txt` may skip the KittenTTS wheel — Jarvis **TTS** can be off until you use a 3.11/3.12 venv).
- **Git** and a terminal (PowerShell, CMD, or WSL Ubuntu, etc.).

### Create the virtualenv and install dependencies

**WSL2 / Linux / macOS**

```bash
cd "/path/to/.../Category 3 - IA West Smart Match CRM"
python3 -m venv .venv
.venv/bin/pip install -U pip
.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
cd "C:\path\to\...\Category 3 - IA West Smart Match CRM"
py -3 -m venv .venv
.\.venv\Scripts\pip.exe install -U pip
.\.venv\Scripts\pip.exe install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set secrets as needed (never commit real keys). **`GEMINI_API_KEY`** is optional if you use **Demo Mode** in the UI.

### New venv on Python 3.12 (Jarvis TTS on a 3.13 machine)

Step-by-step: **section 3** in [docs/handoffs/jarvis-voice-webrtc-enablement.md](docs/handoffs/jarvis-voice-webrtc-enablement.md).

---

## Demo Mode

In the app sidebar, enable **Demo Mode (offline fixtures)** to run without live Gemini calls. No API key required for basic exploration.

---

## Features (overview)

### Landing Page

Branded experience with mission, “How It Works,” and campaign/curator views.

### Command Center (v2.0)

Voice-capable coordinator: text/voice input, STT/TTS (when installed), Gemini intents, HITL approval cards, swimlane status, optional **NemoClaw** hook (dormant by default — see `src/coordinator/nemoclaw_adapter.py` and README note below).

### Matches, Discovery, Pipeline

8-factor matching, scraper + LLM extraction, funnel visualization; see codebase under `src/ui/` and `src/matching/`.

### Volunteer Dashboard & Expansion Map

Utilization analytics and geographic views.

---

## Architecture (high level)

```
src/
  app.py                 # Streamlit entry
  config.py              # Configuration
  data_loader.py         # CSV pipeline
  matching/              # Engine + factors
  scraping/              # University scraper
  coordinator/           # Intent, approval, tools, optional NemoClaw adapter
  ui/                    # Pages, command center, tabs
  voice/                 # TTS / STT wrappers
```

---

## Testing

From this directory, with venv activated:

```bash
# Linux / WSL / macOS
.venv/bin/python -m pytest -q

# Windows
.venv\Scripts\python.exe -m pytest -q
```

With coverage:

```bash
.venv/bin/python -m pytest --cov=src --cov-report=term-missing
```

---

## Environment variables

See `.env.example`. Important:

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | For live LLM/embeddings | Google Gemini API key |
| `GEMINI_TEXT_MODEL` | No | Default in `.env.example` |
| `GEMINI_EMBEDDING_MODEL` | No | Default in `.env.example` |
| `USE_NEMOCLAW` | No | Optional orchestration (`0` / `1`) |
| `NVIDIA_NGC_API_KEY` | If NemoClaw enabled | NVIDIA NGC key |

---

## NemoClaw status

`USE_NEMOCLAW` and `openclaw-sdk` are optional. The shipped Command Center uses the direct dispatch path; `nemoclaw_adapter.py` is a future-integration hook, not a required runtime dependency.

---

## Deliverables

See `docs/deliverables/` (demo script, growth strategy, measurement plan, responsible AI note, etc.).
