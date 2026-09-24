#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment…"
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies…"
pip install -q -r backend/requirements.txt

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "No .env found — copying .env.example as .env"
  cp .env.example .env
  echo "Edit .env to add your API keys, then re-run this script."
fi

echo "Starting Just Wright on http://localhost:8000"
PYTHONPATH="$(pwd)" uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
