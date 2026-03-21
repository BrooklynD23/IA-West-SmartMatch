# IA West Smart Match CRM (Category 3)

Local app for speaker-event matching, discovery, and outreach workflows.

## Prerequisites

- Python 3.11+
- A virtual environment at `.venv`
- `GEMINI_API_KEY` in `Category 3 - IA West Smart Match CRM/.env`

## Setup

From `Category 3 - IA West Smart Match CRM/`:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
cp .env.example .env
```

Set your real Gemini key in `.env`:

```env
GEMINI_API_KEY=your_real_key_here
```

## Run App (Single Command)

The scripts below start both:
- Backend: local dev backend on `http://127.0.0.1:8000`
- Frontend: Streamlit app on `http://127.0.0.1:8501`

### WSL / Linux

```bash
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

### Windows (CMD)

```cmd
scripts\start_dev.cmd
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_dev.ps1
```

## Run From Repo Root (One Click)

If you are at repository root (`HackathonForBetterFuture2026/`), use:

### WSL / Linux

```bash
./start_cat3_dev.sh
```

### Windows (CMD)

```cmd
start_cat3_dev.cmd
```

### Windows (PowerShell)

```powershell
powershell -ExecutionPolicy Bypass -File .\start_cat3_dev.ps1
```

## Health Checks

- Backend health: `http://127.0.0.1:8000/health`
- Frontend: `http://127.0.0.1:8501`

## Stop Services

- WSL script: `Ctrl+C` in the terminal running `start_dev.sh`
- Windows script: close both launched terminal windows (`CAT3 Backend`, `CAT3 Frontend`)
