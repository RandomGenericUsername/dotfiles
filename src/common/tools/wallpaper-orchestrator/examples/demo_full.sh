#!/bin/bash
# Demo script to show socket integration working

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOCKET_DIR="/tmp/sockets"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Wallpaper Orchestrator Socket Integration Demo           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Clean up any existing socket
rm -f "$SOCKET_DIR/wallpaper_progress.sock"
mkdir -p "$SOCKET_DIR"

# Get Python from socket module venv
SOCKET_PYTHON="$SCRIPT_DIR/../../modules/socket/.venv/bin/python"

if [ ! -f "$SOCKET_PYTHON" ]; then
    echo -e "${YELLOW}⚠️  Socket module venv not found, using system python${NC}"
    SOCKET_PYTHON="python3"
fi

echo -e "${GREEN}Starting socket client (listener)...${NC}"
echo ""

# Start client in background
$SOCKET_PYTHON "$SCRIPT_DIR/demo_socket_integration.py" &
CLIENT_PID=$!

# Give client time to start
sleep 1

echo ""
echo -e "${GREEN}Starting wallpaper orchestrator (sender)...${NC}"
echo ""

# Run orchestrator
$SOCKET_PYTHON "$SCRIPT_DIR/demo_run_orchestrator.py"

# Wait for client to finish
wait $CLIENT_PID

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Demo Complete!                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

