# Router Demo — PyCon US 2026

**Talk:** *Distributing AI with Python in the Browser: Edge Inference and Flexibility Without Infrastructure*
PyCon US 2026 · 30 min · AI track

A single-page PyScript app that runs an agentic loop across three inference tiers — in-browser (WebLLM/WebGPU), local (Ollama or any OpenAI-compatible server), and remote (real API or mock SSE server) — and makes the architecture visible to the audience in real time.

The core talking point: **the agent loop runs entirely in the browser as Python**. The LLM can run anywhere; the loop, tool calls, and UI updates stay local.

---

## Quick start

```bash
./demo/servers/run_all.sh
# then open http://localhost:8000
```

This starts three servers:

| Server | Port | Purpose |
|---|---|---|
| Static HTTP | 8000 | Serves `index.html` + all demo assets |
| MCP tools | 8765 | `web_search` + `save_to_file` tools (`demo/servers/mcp_server.py`) |
| Mock remote SSE | 8766 | Prompt-aware streaming stand-in for a real API (`demo/servers/sse_server.py`) |

To use a real remote API instead of the mock, export before running:

```bash
export REMOTE_API_URL=https://api.anthropic.com/v1
export REMOTE_API_KEY=sk-ant-...
./demo/servers/run_all.sh
```

---

## The three demos

### Demo 1 — CSV analysis (default tier: in-browser)
LLM calls the `analyze_csv` Pyodide tool (Pandas, runs in-browser), then narrates the results.
No data leaves the device.

### Demo 2 — Agent + MCP tools (default tier: remote)
LLM calls `web_search` and `save_to_file` over HTTP via an MCP server.
`save_to_file` is intercepted client-side: the browser's File System Access API writes the file directly to the user's disk — the MCP server never touches it.

### Demo 3 — Folder agent (default tier: remote)
User picks a local folder containing an `agent.yaml` definition. The demo reads the YAML, injects any documents from `documents/`, builds a system prompt, and instantiates that agent in the browser for a live conversation.

Expected folder structure:
```
my-agent/
├── agent.yaml          # name, description, system_prompt, ai config
├── documents/          # optional — text files injected into system prompt
│   └── reference.md
└── tools/
    └── mcp.json        # optional — informational tool config (future)
```

Minimal `agent.yaml`:
```yaml
name: My Agent
description: A short description
system_prompt: You are a helpful assistant specialised in ...
ai:
  model: claude-sonnet-4-6
```

---

## Configuration

All endpoints and model IDs live in `config.py` and can be overridden with env vars:

| Var | Default | Purpose |
|---|---|---|
| `REMOTE_API_URL` | `http://localhost:8766` | Remote completions endpoint |
| `REMOTE_API_KEY` | *(empty)* | Set for a real API; empty → mock SSE |
| `REMOTE_API_MODEL` | `claude-sonnet-4-6` | Model name for remote requests |
| `LOCAL_API_URL` | `http://localhost:11434` | Local model endpoint (Ollama default) |
| `LOCAL_API_MODEL` | `Qwen3-8B` | Model name for local requests |
| `MCP_SERVER_URL` | `http://localhost:8765` | MCP tools server |
| `BROWSER_MODEL_ID` | `Qwen2.5-1.5B-Instruct-q4f16_1-MLC` | WebLLM model (WebGPU) |

---

## Key files

| File | Purpose |
|---|---|
| `index.html` | All UI + JS (tier selector, health probes, routing animation, arch diagram, font/panel controls) |
| `main.py` | Demo handlers, free-form input, pre-warm |
| `agent.py` | Tier-agnostic agent loop |
| `agent_loader.py` | Parses a local agent folder (agent.yaml + documents) via JS File System Access API |
| `tiers.py` | `InBrowserTier`, `LocalTier`, `RemoteTier` + `get_tier()` factory |
| `streaming.py` | SSE reader, `Delta`, `ToolCall` dataclasses |
| `tools.py` | MCP HTTP client + `save_to_file` intercept + schema helpers |
| `fs_bridge.py` | File System Access API wrapper (folder mount + download fallback) |
| `router.py` | Keyword routing — returns `path`, `reason`, `keyword` for animation |
| `ui.py` | Message rendering, streaming bubbles, tool-call pills, arch diagram bridge |
| `config.py` | Endpoints, model IDs — all readable from env vars |
| `metrics.py` | TTFT timer helpers |
| `pyscript.toml` | Package list (`pandas`, `pyyaml`) + Python file load order |
| `data/sales.csv` | Synthetic 2026 sales data for Demo 1 |
| `metrics_snapshot.json` | Pre-captured bundle/TTFT numbers for the trade-offs drawer |

---

## Pre-flight checklist

Run through this on the morning of the talk.

### 1 — Repo state
- [ ] `git status` is clean
- [ ] On the correct branch

### 2 — Services
```bash
./demo/servers/run_all.sh
```
- [ ] `curl -s http://localhost:8000/ | head -3` — HTML returned
- [ ] `curl -s http://localhost:8765/health` → `{"status": "ok"}` (MCP)
- [ ] `curl -s http://localhost:8766/health` → `{"status": "ok"}` (mock remote)
- [ ] *(if using local model)* `curl -s http://localhost:11434/health` → 200

### 3 — Browser setup
- [ ] Open `http://localhost:8000` in **Chrome** (WebGPU required for in-browser tier; Safari also works)
- [ ] DevTools closed
- [ ] Full-screen (`F11` / `⌘⇧F`)

### 4 — Health banner
Wait ~3 s after page load, then confirm tier button dots:
- [ ] **In-browser**: green (`WebGPU ready`) — or red/yellow → switch default to Remote
- [ ] **Local**: green if using a local model on stage, otherwise ignore
- [ ] **Remote**: green (`connected`)
- [ ] **Demo 2** button enabled (MCP server reachable)

### 5 — Demo run-through

| Demo | Default tier | What to verify |
|---|---|---|
| Demo 1 | In-browser | `analyze_csv` pill appears, then LLM narrative streams |
| Demo 2 | Remote | `web_search` pill → result → `save_to_file` pill → file saved → summary |
| Demo 3 | Remote | Folder picker opens, agent loads, greeting streams |

- [ ] Routing animation fires on each demo click
- [ ] Arch diagram nodes light up during execution
- [ ] Font `+`/`−` buttons scale only the chat and right panels
- [ ] Vertical / horizontal drag handles resize panels correctly
- [ ] `Focus mode` button hides header and demo controls
- [ ] Trade-offs drawer opens and shows snapshot numbers

### 6 — WebLLM pre-warm
Demo 1 in-browser downloads ~700 MB the first time. To avoid on stage:
- [ ] Click **Demo 1** with **In-browser** selected before the talk — let the model download fully
- [ ] Confirm status reads `In-browser: Ready`
- [ ] Re-clicking responds in ~200 ms (no download bar)

Do **not** click `↺ Cold reload` after this step.

### 7 — Planned tier-switching order
1. Demo 1 → **In-browser** — shows cold-start cost; re-run shows cached speed
2. Demo 1 → **Remote** — immediate response, same Python call
3. Demo 2 → **Remote** — full agent + MCP tool loop
4. Demo 3 → **Remote** — folder agent with injected documents
5. *(optional)* Any demo → **Local** — show quality/speed trade-off on smaller model

### 8 — Final checks
- [ ] `metrics_snapshot.json` numbers reflect the demo machine (re-capture manually if hardware changed significantly)
- [ ] No console errors before closing DevTools
- [ ] Laptop plugged in (WebGPU inference drains battery)
- [ ] Projector / external display confirmed
- [ ] **Backup plan**: if in-browser fails → select **Remote** and continue

---

## UI controls reference

| Control | What it does |
|---|---|
| Tier buttons (top) | Select inference tier for all demos |
| `−` / `+` / `1.2×` (footer) | Scale font size in chat + right panels only |
| `Focus mode` (footer) | Hide/show header, tier row, and demo buttons for more vertical space |
| `◀ chat` (footer) | Snap vertical split to expand chat panel |
| `debug ▶` (footer) | Snap vertical split to expand log/arch panel |
| `⊡ reset` (footer) | Reset vertical split to 50/50 |
| Vertical drag handle | Drag to resize chat vs. right panel; click to toggle; double-click to reset |
| Horizontal drag handle | Drag to resize log vs. arch panel inside the right column |
| Step mode toggle | Pause agent loop at each meaningful boundary; `▶ next step` resumes |
| `↺ Cold reload` | Clear all caches (HTTP + WebLLM IndexedDB) and reload |
| `⚖ Trade-offs` | Open the comparison drawer |

---

## Reliability design

**Tier selector as escape hatch** — if in-browser fails on stage, switch to Remote and continue. No special code needed.

**Health banner** — JS probes each tier endpoint with a 1.5 s timeout on page load and every 15 s. Tier buttons show green/yellow/red dots. Demo 2 button is disabled if the MCP server is unreachable.

**No video fallbacks** — if a backup is needed on stage, play it externally from a phone or second device.

---

## Further reading

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — system diagram, agent loop internals, component details
- [`CHANGELOG.md`](./CHANGELOG.md) — chronological build log; every phase, decision, and non-obvious fix
