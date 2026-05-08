#!/usr/bin/env bash
# Start all servers needed for the router demo.
# Run from the repo root: ./demo/servers/run_all.sh

set -e
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "Starting MCP server (port 8765)..."
python "$REPO_ROOT/spike/mcp_test_server/server.py" &
MCP_PID=$!

echo "Starting mock SSE server (port 8766)..."
python "$REPO_ROOT/spike/validation_2_sse/sse_server.py" &
SSE_PID=$!

echo "Starting demo HTTP server (port 8000)..."
(cd "$REPO_ROOT/demo" && python -m http.server 8000) &
HTTP_PID=$!

echo ""
echo "All servers running:"
echo "  Demo:   http://localhost:8000"
echo "  MCP:    http://localhost:8765"
echo "  Remote: http://localhost:8766 (mock SSE)"
echo ""
echo "Press Ctrl+C to stop all."

trap "kill $MCP_PID $SSE_PID $HTTP_PID 2>/dev/null; echo 'Stopped.'" EXIT INT TERM
wait
