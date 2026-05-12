"""Router Demo — main entry point.

Demo 1: In-browser date conversion (default tier: in-browser)
Demo 2: LLM calls analyze_csv Pyodide tool, then narrates results (default tier: remote)
Demo 3: LLM calls MCP tools over HTTP — web_search + save_to_file (default tier: remote)

Each demo builds a messages list and calls run_agent_loop.
All streaming, bubble management, diagram state, and logging live in agent.py.
"""

import asyncio
from pyscript import document

from ui import add_message, clear_messages, update_status, get_selected_tier, agent_log
from router import route_request
from tiers import get_tier
from tools import list_tools, format_tools_for_llm, PYODIDE_TOOLS
from agent import run_agent_loop

# Shared conversation history — seeded by each demo, extended by send_message.
# run_agent_loop mutates this list in place (appending assistant + tool messages),
# so follow-up questions automatically have full context.
_history: list = []
_current_tools: list = []  # tool schemas active for the current demo session


# =============================================================================
# DEMO 1 — Pure LLM call, no tools
# =============================================================================

async def run_demo_1(event=None):
    global _history, _current_tools
    clear_messages()
    tier_name = get_selected_tier()
    tier = get_tier(tier_name)

    prompt = "Convert this date to ISO format: May 5, 2026. Reply with only the ISO date string, nothing else."
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(f"<em>Routing → {tier_name.upper()} · {routing['reason']}</em>", role="system")
    from pyscript import window as _win
    _win.animateRoute(tier_name, routing.get("keyword", "date"))

    agent_log("route", f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",  f"inference tier: {tier_name} (no tools — pure LLM call)")

    _current_tools = []
    _history = [{"role": "user", "content": prompt}]
    await run_agent_loop(tier=tier, messages=_history, tools=_current_tools, route=tier_name)

    agent_log("agent_done", "response complete")


# =============================================================================
# DEMO 2 — LLM calls analyze_csv (Pyodide tool) then narrates results
# =============================================================================

async def run_demo_2(event=None):
    global _history, _current_tools
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

    agent_log("route", f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",  f"inference tier: {tier_name} | tool: analyze_csv (pyodide — in-browser Pandas)")
    agent_log("info",  "tool schema sent to LLM — waiting for tool_call decision")

    _current_tools = format_tools_for_llm(PYODIDE_TOOLS)
    _history = [
        {
            "role": "system",
            "content": (
                "You are a data analyst assistant. You have access to an analyze_csv tool "
                "that runs Pandas in the browser — no data leaves the device. "
                "The tool returns: column names, row count, total revenue, top product, and QoQ growth. "
                "Call analyze_csv first before answering any question about a CSV file. "
                "For follow-up questions, answer directly from the tool result already in the conversation — "
                "do not claim the tool lacks information that is already present in the tool result."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    await run_agent_loop(tier=tier, messages=_history, tools=_current_tools, route=tier_name)

    agent_log("agent_done", "agent loop complete")


# =============================================================================
# DEMO 3 — LLM calls MCP tools over HTTP
# =============================================================================

async def run_demo_3(event=None):
    global _history, _current_tools
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

    mcp_tools = await list_tools()
    tool_names = [t["name"] for t in mcp_tools] if mcp_tools else ["(none found)"]
    add_message(f"<em>MCP tools available: {', '.join(tool_names)}</em>", role="system")

    agent_log("route", f"keyword match: \"{routing.get('keyword', '')}\" → {routing['reason']}")
    agent_log("tier",  f"inference tier: {tier_name} | transport: MCP over HTTP (localhost:8765)")
    agent_log("info",  f"tools discovered: {', '.join(tool_names)}")
    agent_log("info",  "tool schemas sent to LLM — waiting for tool_call decision")

    _current_tools = format_tools_for_llm(mcp_tools)
    _history = [
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
    await run_agent_loop(tier=tier, messages=_history, tools=_current_tools, route=tier_name)

    agent_log("agent_done", "agent loop complete")


# =============================================================================
# FREE-FORM INPUT
# =============================================================================

async def send_message(event=None):
    global _history, _current_tools
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

    _history.append({"role": "user", "content": prompt})

    await run_agent_loop(
        tier=get_tier(tier_name),
        messages=_history,
        tools=_current_tools,
        route=tier_name,
    )


async def handle_keydown(event):
    if event.key == "Enter":
        await send_message()


# =============================================================================
# INIT
# =============================================================================

print("Router Demo — PyCon US 2026")
update_status("", "In-browser: Not loaded")
agent_log("info", "PyScript + Pyodide ready — Python running in the browser")

# Expose step-mode resume to JS
from pyscript import window as _win
from pyodide.ffi import create_proxy
from agent import resume_step
_win.agentResumeStep = create_proxy(resume_step)

async def _prewarm():
    """Background pre-warm of WebLLM so Demo 1 in-browser is fast on stage."""
    from pyscript import window
    from tiers import _init_browser_engine
    if not getattr(window.navigator, "gpu", None):
        return
    if str(getattr(window, "caches", None)) in ("None", "undefined", ""):
        return
    await _init_browser_engine()

asyncio.ensure_future(_prewarm())
print("Ready.")
