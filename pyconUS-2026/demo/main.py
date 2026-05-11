"""Router Demo — main entry point.

Demo 1: In-browser date conversion (default tier: in-browser)
Demo 2: LLM calls analyze_csv Pyodide tool, then narrates results (default tier: remote)
Demo 3: LLM calls MCP tools over HTTP — web_search + save_to_file (default tier: remote)

Each demo reads its tier selector, then streams through the chosen tier.
"""

import asyncio
from pyscript import document

from ui import (
    add_message, clear_messages, update_status,
    add_streaming_message, update_streaming_message, finish_streaming_message,
    add_tool_call_pill, add_tool_result, get_selected_tier, agent_log,
)
from router import route_request
from tiers import get_tier
from tools import list_tools, format_tools_for_llm, PYODIDE_TOOLS
from agent import run_agent_loop
from metrics import start_timer, record_ttft


# =============================================================================
# SHARED STREAMING HELPER
# =============================================================================

async def _stream_into_bubble(tier, messages, tools=None, route=None):
    """Stream tier.stream_chat() into a new message bubble. Returns full text."""
    msg = add_streaming_message(route=route)
    full_text = ""
    t = start_timer()
    first_token = True
    async for delta in tier.stream_chat(messages, tools):
        if delta.text:
            if first_token:
                record_ttft(t)
                first_token = False
            update_streaming_message(msg, delta.text)
            full_text += delta.text
    finish_streaming_message(msg)
    return full_text


# =============================================================================
# DEMO 1 — In-browser date conversion
# =============================================================================

async def run_demo_1(event=None):
    clear_messages()
    tier_name = get_selected_tier()
    tier = get_tier(tier_name)

    prompt = "Convert this date to ISO format: May 5, 2026. Reply with only the ISO date string, nothing else."
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(f"<em>Routing → {tier_name.upper()} · {routing['reason']}</em>", role="system")
    from pyscript import window as _win
    _win.animateRoute(tier_name, routing.get("keyword", "date"))

    agent_log("route",  f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",   f"inference tier: {tier_name} (no tools — pure LLM call)")
    agent_log("llm_start", f"sending 1 message to {tier_name} LLM")

    messages = [{"role": "user", "content": prompt}]
    await _stream_into_bubble(tier, messages, route=tier_name)

    agent_log("agent_done", "response complete")


# =============================================================================
# DEMO 2 — LLM calls analyze_csv (Pyodide tool) then narrates results
# =============================================================================

async def run_demo_2(event=None):
    clear_messages()
    tier_name = get_selected_tier()
    tier = get_tier(tier_name)

    prompt = "Analyze the sales CSV at ./data/sales.csv and write a 3-sentence executive summary suitable for a board slide."
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(
        f"<em>Routing → {tier_name.upper()} + Pyodide tool · {routing['reason']}</em>",
        role="system",
    )
    from pyscript import window as _win
    _win.animateRoute(tier_name, "CSV")

    agent_log("route",       f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",        f"inference tier: {tier_name} | tool: analyze_csv (pyodide — in-browser Pandas)")
    agent_log("info",        "tool schema sent to LLM — waiting for tool_call decision")

    tools_for_llm = format_tools_for_llm(PYODIDE_TOOLS)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a data analyst assistant. You have access to an analyze_csv tool "
                "that runs Pandas in the browser — no data leaves the device. "
                "When asked to analyze a CSV, always call analyze_csv first, "
                "then write your summary based on the tool result."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    current_bubble = [None]

    def on_turn_start():
        current_bubble[0] = add_streaming_message(route=tier_name)
        agent_log("llm_start", f"LLM turn started ({tier_name})")

    def on_turn_end():
        if current_bubble[0]:
            finish_streaming_message(current_bubble[0])
            current_bubble[0] = None

    def on_delta(text):
        if current_bubble[0]:
            update_streaming_message(current_bubble[0], text)

    def on_tool_call(tc):
        add_tool_call_pill(tc)
        if tc.name == "analyze_csv":
            agent_log("tool_pyodide", f"tool_call → {tc.name}({tc.args}) — dispatching to Pyodide")
        else:
            agent_log("tool_call", f"tool_call → {tc.name}({tc.args})")

    def on_tool_result(tc, result_text):
        add_tool_result(tc, result_text)
        preview = result_text[:80] + ("…" if len(result_text) > 80 else "")
        if tc.name == "analyze_csv":
            agent_log("tool_result", f"pyodide result: {preview}")
            agent_log("llm_start",   "tool result appended to context — LLM generating narrative")
        else:
            agent_log("tool_result", f"result from {tc.name}: {preview}")

    await run_agent_loop(
        tier=tier,
        messages=messages,
        tools=tools_for_llm,
        on_delta=on_delta,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
        on_turn_start=on_turn_start,
        on_turn_end=on_turn_end,
    )

    agent_log("agent_done", "agent loop complete")


# =============================================================================
# DEMO 3 — Remote + MCP tool-calling agent loop
# =============================================================================

async def run_demo_3(event=None):
    clear_messages()
    tier_name = get_selected_tier()
    tier = get_tier(tier_name)

    prompt = "Find the top 3 climate stories from this week and save them to my notes"
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(
        f"<em>Routing → {tier_name.upper()} + MCP tools · {routing['reason']}</em>",
        role="system",
    )
    from pyscript import window as _win
    _win.animateRoute(tier_name, routing.get("keyword", "agent"))

    # Discover tools
    mcp_tools = await list_tools()
    tool_names = [t["name"] for t in mcp_tools] if mcp_tools else ["(none found)"]
    add_message(f"<em>MCP tools available: {', '.join(tool_names)}</em>", role="system")

    agent_log("route",     f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",      f"inference tier: {tier_name} | transport: MCP over HTTP (localhost:8765)")
    agent_log("info",      f"tools discovered: {', '.join(tool_names)}")
    agent_log("info",      "tool schemas sent to LLM — waiting for tool_call decision")

    tools_for_llm = format_tools_for_llm(mcp_tools)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant with access to tools. "
                "When asked to find information, call web_search first. "
                "When asked to save results, call save_to_file. "
                "Always use the tools available — do not fabricate results."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    current_bubble = [None]

    def on_turn_start():
        current_bubble[0] = add_streaming_message(route=tier_name)
        agent_log("llm_start", f"LLM turn started ({tier_name})")

    def on_turn_end():
        if current_bubble[0]:
            finish_streaming_message(current_bubble[0])
            current_bubble[0] = None

    def on_delta(text):
        if current_bubble[0]:
            update_streaming_message(current_bubble[0], text)

    def on_tool_call(tc):
        add_tool_call_pill(tc)
        agent_log("tool_call", f"tool_call → {tc.name}({tc.args}) — dispatching to MCP HTTP server")

    def on_tool_result(tc, result_text):
        add_tool_result(tc, result_text)
        preview = result_text[:80] + ("…" if len(result_text) > 80 else "")
        agent_log("tool_result", f"mcp result from {tc.name}: {preview}")
        agent_log("llm_start",   "tool result appended to context — continuing agent loop")

    await run_agent_loop(
        tier=tier,
        messages=messages,
        tools=tools_for_llm,
        on_delta=on_delta,
        on_tool_call=on_tool_call,
        on_tool_result=on_tool_result,
        on_turn_start=on_turn_start,
        on_turn_end=on_turn_end,
    )

    agent_log("agent_done", "agent loop complete")


# =============================================================================
# FREE-FORM INPUT
# =============================================================================

async def send_message(event=None):
    input_el = document.getElementById("user-input")
    prompt = input_el.value.strip()
    if not prompt:
        return
    input_el.value = ""

    add_message(prompt, role="user")
    tier_name = get_selected_tier()
    add_message(f"<em>Tier: {tier_name}</em>", role="system")

    routing = route_request(prompt)
    from pyscript import window as _win
    _win.animateRoute(tier_name, routing.get("keyword", ""))

    tier = get_tier(tier_name)
    messages = [{"role": "user", "content": prompt}]
    await _stream_into_bubble(tier, messages, route=tier_name)


async def handle_keydown(event):
    if event.key == "Enter":
        await send_message()


# =============================================================================
# INIT
# =============================================================================

print("Router Demo — PyCon US 2026")
update_status("", "In-browser: Not loaded")
agent_log("info", "PyScript + Pyodide ready — Python running in the browser")

async def _prewarm():
    """Background pre-warm of WebLLM so Demo 1 in-browser is fast on stage."""
    from pyscript import window
    from tiers import _init_browser_engine
    # Only attempt if the browser reports WebGPU + Cache API are available
    if not getattr(window.navigator, "gpu", None):
        return
    if str(getattr(window, "caches", None)) in ("None", "undefined", ""):
        return
    await _init_browser_engine()

asyncio.ensure_future(_prewarm())
print("Ready.")
