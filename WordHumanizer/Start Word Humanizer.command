#!/usr/bin/env bash
# macOS / Linux: double-click (or run) to start Word Humanizer.
cd "$(dirname "$0")" || exit 1
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then
  echo "Python 3.10+ is required: https://www.python.org/downloads/"; read -r; exit 1
fi
if [ ! -x venv/bin/python ]; then
  echo "First start: setting up Word Humanizer (1-2 minutes)..."
  "$PY" -m venv venv || { echo "Setup failed."; read -r; exit 1; }
fi
if ! venv/bin/python -c "import docx, fastapi, uvicorn, requests, dotenv, tenacity, multipart" 2>/dev/null; then
  echo "Installing the required libraries..."
  venv/bin/python -m pip install --disable-pip-version-check -q -r requirements.txt || { echo "Setup failed."; read -r; exit 1; }
fi
[ -f .env ] || cp .env.example .env
echo
echo "Word Humanizer is running at http://localhost:8000 (close this window to stop)"
( sleep 4; open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null ) &
exec venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
