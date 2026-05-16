# Demo Build Log

Chronological record of every phase executed to reach the current demo state.
Each entry lists what was done, what files changed, and any non-obvious decisions made.

---

## Phase 1 — Correctness fixes

Starting point: a prototype with routing logic and UI scaffolding in place but three hard blockers preventing any demo from running.

### 1.1 — Fixed WebLLM API call (`tiers.py`)
The original call passed a Python dict as kwargs to `engine.chat.completions.create()`, which doesn't survive Pyodide's JS proxy boundary. Fixed by converting options to a JS object via `to_js(..., dict_converter=js.Object.fromEntries)` and passing it as a single positional argument. Also discovered that JS proxy values (chunk content, finish_reason) must be extracted to plain Python strings **before** any `yield` or `await` — Pyodide destroys borrowed proxies at suspension points.

### 1.2 — Wired streaming through all demos (`main.py`)
`add_streaming_message` / `update_streaming_message` / `finish_streaming_message` existed in `ui.py` but were never called. Added `_stream_into_bubble()` shared helper in `main.py` and wired it through all three demo handlers and the free-form input handler.

### 1.3 — Killed dead hardcoded Demo 3 block (`main.py`)
Demo 3 had an `asyncio.sleep` loop with hardcoded "climate story" strings. Replaced with the real agent loop (Phase 4).

### 1.4 — Replaced MCP server tools (`spike/mcp_test_server/server.py`)
Replaced `get_weather` and `calculate` with `web_search(query, k=3)` (returns plausible climate story objects) and `save_to_file(filename, content)` (writes to `./notes/`). Added `/health` endpoint for the M2 probe.

---

## Phase 2 — Tier abstraction + selector

### 2.1 — Defined `Delta` and `ToolCall` dataclasses (`streaming.py`)
Single normalized shape for all tier output: `Delta(text, tool_call, finish_reason)` and `ToolCall(id, name, args)`. Shared by all tiers and the agent loop.

### 2.2 — Implemented three tiers (`tiers.py`)
- `InBrowserTier` — wraps WebLLM engine with `create_proxy` for the progress callback, `to_js` for options, and pre-flight checks for WebGPU + Cache API availability
- `LocalTier` — `fetch` to `localhost:11434/v1/chat/completions`, OpenAI-compatible SSE
- `RemoteTier` — same SSE path; uses `REMOTE_API_KEY` if set, falls back to mock SSE server on `:8766`
- `get_tier(name)` factory function

### 2.3 — SSE parser (`streaming.py`)
`parse_openai_sse(response)` reads `response.body.getReader()` via JS `TextDecoder`, accumulates tool-call argument fragments across chunks, and yields normalized `Delta` objects. Handles both text streaming and `finish_reason=tool_calls`.

### 2.4 — Tool-call normalization (`tools.py`)
`normalize_tool_calls(raw, source_tier)` handles shape differences between OpenAI (`{id, function: {name, arguments}}`), Ollama (no `id`), and small in-browser models that produce JSON-in-text.

### 2.5 — Global tier selector (`index.html`, `ui.py`)
Replaced per-demo dropdowns (original design) with a single 3-button selector at the top of the page. Decision: simpler for live switching on stage, unambiguous for the audience. JS `selectTier()` updates active state and tints demo buttons to match. `ui.py` reads selection via `window.getDemoTier()`.

### 2.6 — Config reshape (`config.py`)
Removed all `USE_MOCK_*` boolean flags. Replaced with endpoint URLs and model IDs, all readable from env vars. Unavailable tiers surface as errors rather than silent mocks.

---

## Phase 3 — Demo 1 + Demo 2 wiring

### 3.1 — Demo 1 (`main.py`)
Wired tier selector → `get_tier()` → `_stream_into_bubble()`. Pre-warm (`_prewarm()`) kicks off `_init_browser_engine()` in the background on page load so the in-browser model is ready before the first stage click.

### 3.2 — Demo 2 (`main.py`, `data/sales.csv`)
Added two-step flow: `fetch('./data/sales.csv')` → Pandas analysis in Pyodide → rendered monospace block labeled IN-BROWSER → framing prompt sent to selected tier → streamed narrative below. Created `data/sales.csv` (156 rows, Q1–Q2 2026, columns: date/product/region/revenue/qty). Added `pandas` to `pyscript.toml` packages (fixing an earlier `a.map is not a function` error caused by wrong TOML syntax).

### 3.3 — TTFT metric (`metrics.py`, `main.py`)
`start_timer()` / `record_ttft()` helpers call `window.recordTtft(ms)` on first token arrival. JS side updates the metrics strip and the drawer's live section.

---

## Phase 4 — Demo 3 agent loop + File System Access

### 4.1 — Agent loop (`agent.py`)
Tier-agnostic loop: stream LLM turn → collect tool calls → execute each via `call_tool()` → append assistant + tool-result messages → loop. UI callbacks (`on_delta`, `on_tool_call`, `on_tool_result`, `on_turn_start`, `on_turn_end`) keep the loop decoupled from rendering. `max_turns=8` safety cap.

### 4.2 — MCP tool client (`tools.py`)
`list_tools()` → `GET /tools`. `call_tool()` intercepts `save_to_file` for the FS bridge before falling through to `POST /call-tool`. `format_tools_for_llm()` converts MCP schemas to OpenAI function-calling format.

### 4.3 — File System Access bridge (`fs_bridge.py`)
On first `save_to_file` call in a session, shows a modal: "Mount a local folder" or "Download". Mount path uses `window.showDirectoryPicker()` → `FileSystemDirectoryHandle` → `createWritable()` → writes directly to the user's disk. Download path creates a `Blob` and triggers `<a download>`. Falls back to download automatically if the API is unavailable (Safari, Firefox). `create_proxy` used for the modal button event listeners to prevent proxy destruction before the choice is read.

### 4.4 — Demo 3 system prompt (`main.py`)
Added a system message instructing the model to call tools rather than fabricate results — necessary for smaller and mock models to reliably enter the tool-calling path.

---

## Phase 5 — Polish

### 5.1 — Routing animation (`index.html`, `main.py`, `router.py`)
Added a three-lane strip between demo buttons and metrics bar. CSS `@keyframes lane-sweep` sweeps a colored highlight down the active lane. `window.animateRoute(tier, keyword)` JS function resets all lanes and triggers the animation on the correct one. `router.py` updated to return a `keyword` field on every path. Python wires `animateRoute` calls in all four entry points (Demo 1, Demo 2, Demo 3, free-form input).

### 5.2 — Metrics strip (`index.html`)
Footer strip shows bundle size (from `performance.getEntriesByType('resource')`), page start time (from navigation timing, cold vs. cached), and last TTFT. Updates after each demo run.

### 5.3 — Cold-cache toggle (`index.html`)
`↺ Cold reload` button clears all HTTP caches via `caches.keys()` + deletes the WebLLM IndexedDB model cache + reloads. Lets the speaker demonstrate honest cold-start timing on stage.

### 5.4 — Trade-offs drawer (`index.html`)
Fixed side drawer with comparison table (latency, model quality, tool-call quality, privacy, cost/1k tokens, offline capability, first-load cost, GPU requirement), live measurements section (mirrors metrics strip), and pre-captured snapshot section (loaded from `metrics_snapshot.json`). "When to use each tier" narrative. Toggle button fixed bottom-right.

### 5.5 — Visual pass (`index.html`)
- Font size bumped to `1.1rem` (readable from back row)
- Active tier buttons get a colored `box-shadow` glow
- Route badges glow while streaming (`:has(.streaming-cursor)` CSS selector removes glow on completion)
- Subtitle updated to match talk title

---

## Phase 6 — Reliability

### 6.M1 — Selector as fallback
Free with Phase 2. The tier selector is the escape hatch: if in-browser fails on stage, switch to Remote.

### 6.M2 — Health banner + pre-warm (`index.html`, `main.py`)
JS probes each tier endpoint with `AbortSignal.timeout(1500)` on page load and every 15 s. Tier button dots update to green/yellow/red. MCP probe separately disables Demo 3 button if unreachable. `_prewarm()` in `main.py` checks for WebGPU + Cache API availability before attempting WebLLM init, so it silently no-ops in unsupported environments.

### 6.M3 — Dropped
Decided not to embed MP4 fallbacks in the demo page. If a backup recording is needed on stage, it will be played externally.

---

## Servers

### Mock SSE server made prompt-aware (`spike/validation_2_sse/sse_server.py`)
Original server returned a hardcoded generic sentence regardless of input. Rewrote to be prompt-aware:
- Detects tool-capable first turn → emits `finish_reason=tool_calls` SSE with `web_search` + `save_to_file` calls
- Detects tool results in history → streams final narrative summary
- ISO date prompt → `2026-05-05`
- Executive summary prompt → 3-sentence board-slide summary
- Generic fallback for free-form input

### `run_all.sh` hardened (`demo/servers/run_all.sh`)
Added port cleanup on startup and process-group kill (`kill -9 -- -$$`) on Ctrl+C so no ghost processes linger on ports 8000/8765/8766 between runs.

---

## Phase 7 — Demo restructure + UI polish

### 7.1 — Demo renumbering and new Demo 3 (`main.py`)
Removed the original Demo 1 (date conversion — not interesting enough for stage). Renumbered:
- Demo 1 = CSV analysis (was Demo 2) — LLM calls `analyze_csv` Pyodide tool, narrates results
- Demo 2 = MCP agent loop (was Demo 3) — LLM calls `web_search` + `save_to_file` over HTTP
- Demo 3 = Folder agent (new) — user picks a local folder with `agent.yaml`, demo instantiates that agent in the browser

### 7.2 — Folder agent loader (`agent_loader.py`, `index.html`, `pyscript.toml`)
New `agent_loader.py` module: calls `window.readAgentFolder(dirHandle)` JS bridge, uses PyYAML to parse `agent.yaml`, reads files from `documents/` and `tools/mcp.json`, returns a config dict. `readAgentFolder` JS function uses the File System Access API to read the folder contents and returns a plain object (`yaml`, `documentsJson`, `mcpJson`, `error`). Added `pyyaml` to `pyscript.toml` packages.

System prompt is built by concatenating `system_prompt` from the YAML with any documents injected as markdown sections. A greeting message seeds the conversation so the agent introduces itself immediately.

### 7.3 — Font size controls (`index.html`)
Added `−` / `+` / display buttons in the footer. Font scaling applies `zoom: var(--font-scale)` to `.chat-container` and `.right-col` only — header, footer, and controls are unaffected. Root `--font-scale` CSS custom property drives the zoom value. `adjustFont(delta)` re-syncs the row-divider position after scale changes to compensate for zoom coordinate offset.

### 7.4 — Resizable panels (`index.html`)
Main area converted to CSS Grid (`var(--split-chat) 10px var(--split-right)`). Vertical drag handle between chat and right panel: drag resizes, click toggles open/close, double-click resets to 1/1. Horizontal drag handle inside the right column: drag resizes log vs. arch panel, double-click resets to 50%. `snapFocus(mode)` snaps splits to presets: `◀ chat`, `debug ▶`, `⊡ reset`. Row-divider drag coordinates are divided by `_fontScale` to compensate for zoom applied to the parent.

### 7.5 — Focus mode (`index.html`)
`toggleUiFocus()` toggles `.ui-collapsed` on `body`, which hides header, tier selector, and demo buttons via `display: none !important`. Gives more vertical space to the working demo area during a live run.

### 7.6 — Orchestrator → Agent rename (`agent.py`, `ui.py`, `index.html`)
All `"orchestrator"` node references replaced with `"agent"` throughout. SVG node updated to `id="arch-agent"`, label "Agent", subtext "PyScript · agent loop". CSS class `.lit-orchestrator` → `.lit-agent`. ARCH_LIT and ARCH_EDGES maps updated. Pyodide SVG label changed to "PyScript tool".

Fixed a proxy-conversion bug: Python strings passed from PyScript to JS window functions can arrive as proxy objects rather than native JS strings. Added `to_js()` wrapping in `ui.py`'s `agent_activate`, `agent_deactivate`, and `agent_highlight`, and `String()` conversion at the entry of the corresponding JS functions.

### 7.7 — Documentation consolidation
Merged `DESIGN.md` and `PREFLIGHT.md` into a single `README.md`. Deleted both source files and the two handoff prompt files (`handoff_slides_session.md`, `handoff_spike_session.md`).

---

## Supporting documents

| File | Purpose |
|---|---|
| `demo/README.md` | Setup, demos, configuration, pre-flight checklist, UI controls reference |
| `demo/ARCHITECTURE.md` | System diagram, agent loop internals, component details |
| `demo/metrics_snapshot.json` | Pre-captured timing numbers for the trade-offs drawer |

---

## Known issues / future work at handoff

- **WebGPU in incognito** — Chrome disables WebGPU in incognito mode; in-browser tier will fail. Use a normal profile or Safari.
- **Tool-call quality on in-browser model** — the 1.5B Qwen model may produce malformed tool calls. Intentional trade-offs talking point; Demo 1 in-browser mode may not complete the loop cleanly.
- **`metrics_snapshot.json` numbers** — re-capture manually before the talk if the demo machine differs significantly from when they were recorded.
- **Local tier probe** — health probe hits `localhost:11434/health` (Ollama's endpoint). Update `PROBES.local` in `index.html` if using a different local model server.
- **Arch diagram agent highlighting** — PyScript proxy-to-JS string conversion fix applied in Phase 7.6; confirm working after reload.
