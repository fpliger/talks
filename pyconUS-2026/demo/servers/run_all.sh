#!/usr/bin/env bash
# Start all servers needed for the router demo.
# Run from the repo root: ./demo/servers/run_all.sh

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

# Kill any leftover processes on our ports before starting
for port in 8000 8765 8766; do
    lsof -ti ":$port" | xargs kill -9 2>/dev/null || true
done

cleanup() {
    echo ""
    echo "Stopping all servers..."
    # Kill the entire process group so subshells and their children all die
    kill -9 -- -$$ 2>/dev/null || true
    # Belt-and-suspenders: also kill by port in case PGIDs differ
    for port in 8000 8765 8766; do
        lsof -ti ":$port" | xargs kill -9 2>/dev/null || true
    done
    echo "Done."
    exit 0
}

trap cleanup INT TERM

# Run all three in the same process group (setsid not used — $$ is the group leader)
python "$REPO_ROOT/spike/mcp_test_server/server.py" &
python "$REPO_ROOT/spike/validation_2_sse/sse_server.py" &
python -m http.server 8000 --directory "$REPO_ROOT/demo" &

echo ""
echo "All servers running:"
echo "  Demo:   http://localhost:8000"
echo "  MCP:    http://localhost:8765"
echo "  Remote: http://localhost:8766 (mock SSE)"
echo ""
echo "Press Ctrl+C to stop all."

wait
