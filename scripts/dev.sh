#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Resolve project root (wherever the script is called from)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/apps/backend"
FRONTEND_DIR="$PROJECT_ROOT/apps/frontend"

echo -e "${GREEN}Starting CoopWise dev environment...${NC}"

# --- Start Postgres ---
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

# --- Backend ---
echo -e "${YELLOW}Starting backend...${NC}"

if [ ! -d "$BACKEND_DIR/venv" ]; then
  echo "No venv found, creating one..."
  python3 -m venv "$BACKEND_DIR/venv"
  "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

(
  cd "$BACKEND_DIR" && \
  "$BACKEND_DIR/venv/bin/uvicorn" main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload
) &
BACKEND_PID=$!

# --- Frontend (disabled for now — backend-only dev) ---
echo -e "${YELLOW}Starting frontend...${NC}"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
  echo "node_modules not found, running npm install..."
  npm --prefix "$FRONTEND_DIR" install
fi

npm --prefix "$FRONTEND_DIR" run dev &
FRONTEND_PID=$!

echo -e "${GREEN}
====================================
  CoopWise is running!
  Backend:  http://localhost:8000
  Frontend: http://localhost:3000
  API Docs: http://localhost:8000/docs
====================================
${NC}"

# --- Cleanup on Ctrl+C ---
cleanup() {
  echo -e "\n${RED}Shutting down...${NC}"
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  echo -e "${YELLOW}Stopping Redis...${NC}"
  redis-cli shutdown 2>/dev/null || true
  echo -e "${GREEN}All services stopped. (Postgres left running)${NC}"
}

trap cleanup SIGINT SIGTERM
wait