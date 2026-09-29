#!/usr/bin/env bash
# Start the web interface on http://localhost:8000
cd "$(dirname "$0")"
exec python -m uvicorn app:app --host 127.0.0.1 --port "${PORT:-8000}"
