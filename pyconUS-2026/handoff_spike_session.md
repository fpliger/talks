# Handoff prompt — PyCon US 2026 talk: demo spike session

Paste this into a new chat. The folder being shared is `pyconUS_2026/`.

---

You're picking up a PyCon US 2026 talk prep project. The talk is **"Distributing AI with Python in the Browser: Edge Inference and Flexibility Without Infrastructure"** — 30 minutes (25+5) on the AI track, accepted, scheduled. The talk demos an agent built in PyScript using a hybrid (local + remote) architecture with MCP for tools.

This folder (`pyconUS_2026/`) contains:
- `talk_brainstorm.ipynb` — the full brainstorm. **It's the source of truth; read it first.**
- Subfolders / files of previous PyScript agents we've built. Use them for code patterns and inspiration.

**Your job this session: the demo spike.**

1. Read `talk_brainstorm.ipynb` start to finish, paying close attention to **§6** (PyScript implementation), **§8** (demo candidates and the router demo flow), and **§11** (spike goals + validation order).

2. Validate the three technical risks in §11 in this order — roughly 1 hour each:
   - MCP Python SDK under Pyodide (`list_tools` + `call_tool` round-trip against an HTTP MCP server)
   - SSE streaming through Pyodide's `fetch` shim (token streaming from Anthropic / OpenAI APIs)
   - WebLLM or Transformers.js called from PyScript via JS interop

   If any of the three fail, **flag loudly and propose alternatives before building further** — that's the most valuable spike output.

3. If all three pass, build the **router demo (§8 #4)**: three prompts hitting three routing paths, with the routing decision visible on the UI. Reuse patterns from the prior PyScript agents in this folder where they fit.

4. Capture findings in a fresh `spike_log.ipynb` next to the brainstorm. Keep `talk_brainstorm.ipynb` as a stable reference; new decisions and learnings go in the log.

**Done =** working router demo + recorded fallback video + bundle size measured + cold start measured + notes on what was harder than expected (those notes feed the trade-offs slide later).

**Out of scope:** slide design, speaker rehearsal, anything that needs more than `python -m http.server` to run.

Push back if anything in the brainstorm conflicts with what you find in code — the brainstorm is current as of May 5, 2026, but the spike is where reality meets the plan.
