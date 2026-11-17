#!/bin/bash
set -e
set -m

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Resolve project root (wherever the script is called from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
API_DIR="$PROJECT_ROOT/apps/api"
WEB_DIR="$PROJECT_ROOT/apps/web"

# The API uses Python 3.11 features (for example enum.StrEnum). Prefer the
# newest supported interpreter commonly installed on macOS.
if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.11)"
else
  PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
fi

if [ -z "$PYTHON_BIN" ] || ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  echo -e "${RED}Python 3.11 or newer is required for the API.${NC}"
  echo "Install Python 3.11+ and run 'make dev' again."
  exit 1
fi

echo -e "${GREEN}Starting Theosis dev environment...${NC}"

# --- Start Postgres (pgvector) ---
echo -e "${YELLOW}Starting PostgreSQL...${NC}"
if ! pg_isready -q 2>/dev/null; then
  if command -v pg_ctlcluster >/dev/null 2>&1; then
    # Debian/Ubuntu PostgreSQL installation.
    pg_ctlcluster 16 main start
  elif [ "$(uname -s)" = "Darwin" ] && [ -f "/Library/LaunchDaemons/postgresql-18.plist" ]; then
    # EnterpriseDB PostgreSQL installation on macOS.
    sudo launchctl load -w /Library/LaunchDaemons/postgresql-18.plist
  elif command -v brew >/dev/null 2>&1 && brew list postgresql@16 >/dev/null 2>&1; then
    brew services start postgresql@16
  else
    echo -e "${RED}PostgreSQL is not running and no supported startup method was found.${NC}"
    echo "Start PostgreSQL, then run 'make dev' again."
    exit 1
  fi
  sleep 2
  if ! pg_isready -q 2>/dev/null; then
    echo -e "${RED}PostgreSQL could not be started.${NC}"
    exit 1
  fi
else
  echo "PostgreSQL already running."
fi

# --- Start Redis ---
echo -e "${YELLOW}Starting Redis...${NC}"
if ! redis-cli ping &>/dev/null; then
  redis-server --daemonize yes --logfile /tmp/redis.log
  sleep 1
else
  echo "Redis already running."
fi

echo -e "${GREEN}Postgres and Redis are up.${NC}"

# --- API (FastAPI) ---
echo -e "${YELLOW}Starting API...${NC}"

if [ ! -x "$API_DIR/.venv/bin/python" ] || ! "$API_DIR/.venv/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
  echo "Creating a Python 3.11+ virtual environment with $PYTHON_BIN..."
  "$PYTHON_BIN" -m venv --clear "$API_DIR/.venv"
  "$API_DIR/.venv/bin/python" -m pip install --upgrade pip
fi

if ! "$API_DIR/.venv/bin/python" -c 'import greenlet' 2>/dev/null; then
  echo "Installing API dependencies..."
  "$API_DIR/.venv/bin/python" -m pip install -r "$API_DIR/requirements.txt"
fi

(
  cd "$API_DIR" && \
  "$API_DIR/.venv/bin/uvicorn" app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
) &
API_PID=$!

# --- Web (Next.js) ---
echo -e "${YELLOW}Starting web...${NC}"

if [ ! -x "$WEB_DIR/node_modules/.bin/next" ]; then
  echo "Next.js executable not found, running npm install..."
  npm --prefix "$WEB_DIR" install
fi

npm --prefix "$WEB_DIR" run dev &
WEB_PID=$!

echo -e "${GREEN}
====================================
  Theosis is running!
  API:      http://localhost:8000
  Web:      http://localhost:3000
  API Docs: http://localhost:8000/api/docs
====================================
${NC}"

# --- Cleanup on Ctrl+C ---
cleanup() {
  echo -e "\n${RED}Shutting down...${NC}"
  kill -- -$API_PID 2>/dev/null
  kill -- -$WEB_PID 2>/dev/null
  redis-cli shutdown 2>/dev/null || true
  echo -e "${GREEN}All services stopped. (Postgres left running)${NC}"
}

trap cleanup SIGINT SIGTERM
wait
