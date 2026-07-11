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

echo -e "${GREEN}Starting Theosis dev environment...${NC}"

# --- Start Postgres (pgvector) ---
echo -e "${YELLOW}Starting PostgreSQL...${NC}"
if ! pg_isready -q 2>/dev/null; then
  pg_ctlcluster 16 main start
  sleep 2
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

if [ ! -d "$API_DIR/venv" ]; then
  echo "No venv found, creating one..."
  python3 -m venv "$API_DIR/.venv"
  "$API_DIR/venv/bin/pip" install -r "$API_DIR/requirements.txt"
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

if [ ! -d "$WEB_DIR/node_modules" ]; then
  echo "node_modules not found, running npm install..."
  npm --prefix "$WEB_DIR" install
fi

npm --prefix "$WEB_DIR" run dev &
WEB_PID=$!

echo -e "${GREEN}
====================================
  Theosis is running!
  API:      http://localhost:8000
  Web:      http://localhost:3000
  API Docs: http://localhost:8000/docs
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