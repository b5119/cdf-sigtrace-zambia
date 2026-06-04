#!/usr/bin/env bash
# ── CDF Integrity — one-command local run (zero external dependencies) ──────────
# Runs the whole stack on SQLite + mock ledgers. No Postgres, Redis, or
# blockchain needed. Completely free, runs on any laptop.
#
# Usage:  ./run-local.sh
# Then open:  http://localhost:5173  (public portal)
# Logins:  admin@cdf.zm / AdminPass123!  ·  officer@oag.gov.zm / Officer123!
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/src/backend"
PUBLIC="$ROOT/src/frontend-public-app"
export DATABASE_URL="sqlite+aiosqlite:///./cdf_local.db"
export MFA_ENFORCE=false
export DEBUG=true

echo "▶ 1/4  Backend venv + deps"
cd "$BACKEND"
[ -d .venv ] || python3 -m venv .venv
./.venv/bin/pip install -q -r requirements.txt "pydantic[email]" aiosqlite 2>/dev/null || true

echo "▶ 2/4  Seeding SQLite demo data"
./.venv/bin/python scripts/local_seed.py

echo "▶ 3/4  Starting backend  →  http://localhost:8000"
./.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level warning &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null" EXIT
sleep 4

echo "▶ 4/4  Starting public portal  →  http://localhost:5173"
cd "$PUBLIC"
[ -d node_modules ] || npm install
VITE_API_BASE_URL=http://localhost:8000/api/v1 npx vite --host --port 5173

# (Oversight console: cd src/frontend-oversight-app && VITE_API_BASE_URL=http://localhost:8000/api/v1 npx vite --port 5174)
# (CDF Pulse PWA:     cd src/pulse-pwa-app        && VITE_API_BASE_URL=http://localhost:8000/api/v1 npx vite --port 5175)
