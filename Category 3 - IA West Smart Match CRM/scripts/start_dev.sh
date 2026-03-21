#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8501}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Missing python executable at $PYTHON_BIN"
  echo "Create the virtualenv first: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

echo "Starting CAT3 dev backend on http://127.0.0.1:${BACKEND_PORT}"
"$PYTHON_BIN" scripts/dev_backend.py --host 127.0.0.1 --port "$BACKEND_PORT" &
BACKEND_PID=$!

cleanup() {
  if kill -0 "$BACKEND_PID" >/dev/null 2>&1; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

echo "Starting Streamlit frontend on http://127.0.0.1:${FRONTEND_PORT}"
"$PYTHON_BIN" -m streamlit run src/app.py --server.port "$FRONTEND_PORT" --server.address 127.0.0.1
