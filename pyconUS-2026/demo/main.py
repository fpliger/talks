"""
Main entry point for the Router Demo.

This file:
- Imports all modules
- Defines demo handlers (run_demo_1, run_demo_2, run_demo_3)
- Handles user input
- Initializes the app
"""

import asyncio
from pyscript import document

# Import our modules
from config import USE_MOCK_BROWSER, USE_MOCK_LOCAL, USE_MOCK_REMOTE
from config import LOCAL_API_URL, REMOTE_API_URL
from ui import add_message, clear_messages, update_status
from router import route_request
from models import browser_generate, local_generate, remote_generate
from tools import list_tools, call_tool


# =============================================================================
# DEMO HANDLERS
# =============================================================================

async def run_demo_1(event=None):
    """Demo 1: In-browser only — Date conversion via WebLLM.

    Shows the BROWSER path: simple task handled entirely in the browser.
    """
    clear_messages()

    prompt = "Convert this date to ISO format: May 5, 2026"
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(f"<em>Routing: {routing['reason']}</em>", role="system")

    # In-browser generation (WebLLM)
    result = await browser_generate(prompt)
    add_message(f"The ISO format is: <strong>{result}</strong>", route="browser")


async def run_demo_2(event=None):
    """Demo 2: Hybrid — CSV analysis with local Pandas + remote model.

    Shows the HYBRID path: local data processing + remote model framing.
    """
    clear_messages()

    prompt = "Summarize the sales data in this CSV"
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(f"<em>Routing: {routing['reason']}</em>", role="system")

    # Simulate local Pandas processing
    add_message("📊 Processing data locally with Pandas...", role="system")
    await asyncio.sleep(0.5)

    # Mock Pandas analysis (in real version, would use actual Pandas)
    local_analysis = """
    Local analysis results:
    - Total rows: 1,247
    - Date range: Jan 2025 - Apr 2026
    - Total revenue: $2.4M
    - Top product: Widget Pro (34% of sales)
    - Growth trend: +12% QoQ
    """

    add_message("<em>Local Pandas analysis complete</em>", role="system")

    # Remote model frames the results
    framing_prompt = f"Based on this data analysis, provide a brief executive summary:\n{local_analysis}"
    content, _ = await remote_generate([{"role": "user", "content": framing_prompt}])

    add_message(content, route="hybrid")


async def run_demo_3(event=None):
    """Demo 3: Remote + Tools — Web search agent.

    Shows the REMOTE path with MCP tool calls.
    """
    clear_messages()

    prompt = "Find the top 3 climate stories this week and save them to my notes"
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(
        f"<em>Routing: {routing['reason']}</em><br>"
        f"<em>Tools needed: {', '.join(routing['needs_tools'])}</em>",
        role="system"
    )

    # Discover available MCP tools
    tools = await list_tools()
    tool_names = [t["name"] for t in tools] if tools else ["(none found)"]
    add_message(f"<em>Available MCP tools: {', '.join(tool_names)}</em>", role="system")

    # Get response from remote model
    content, tool_calls = await remote_generate([{"role": "user", "content": prompt}])
    add_message(content if content else "Planning tool calls...", route="remote")

    # Simulate tool execution (in production, would actually call tools)
    await asyncio.sleep(0.5)

    add_message(
        "Searching for climate news...",
        route="tool",
        tool_calls=[{"name": "web_search", "args": {"query": "climate news this week"}}]
    )

    await asyncio.sleep(0.8)

    add_message(
        "Saving to notes...",
        route="tool",
        tool_calls=[{"name": "save_to_file", "args": {"filename": "climate_notes.txt"}}]
    )

    await asyncio.sleep(0.5)

    # Final response
    add_message(
        "Done! I found 3 top climate stories and saved them to your notes:<br><br>"
        "1. <strong>Global Carbon Emissions Plateau</strong> - First decline in decade<br>"
        "2. <strong>EU Green Deal Milestone</strong> - 50% renewable target reached<br>"
        "3. <strong>Ocean Cleanup Success</strong> - Pacific patch reduced by 30%<br><br>"
        "<em>Saved to: climate_notes.txt</em>",
        route="remote"
    )


# =============================================================================
# USER INPUT HANDLERS
# =============================================================================

async def send_message(event=None):
    """Handle user input from the text field."""
    input_el = document.getElementById("user-input")
    prompt = input_el.value.strip()

    if not prompt:
        return

    input_el.value = ""
    add_message(prompt, role="user")

    routing = route_request(prompt)
    add_message(f"<em>Routing: {routing['reason']}</em>", role="system")

    if routing["path"] == "browser":
        result = await browser_generate(prompt)
        add_message(result, route="browser")

    elif routing["path"] == "local":
        content, _ = await local_generate([{"role": "user", "content": prompt}])
        add_message(content, route="local")

    elif routing["path"] == "hybrid":
        content, _ = await remote_generate([{"role": "user", "content": prompt}])
        add_message(content, route="hybrid")

    else:  # remote
        content, _ = await remote_generate([{"role": "user", "content": prompt}])
        add_message(content, route="remote")


async def handle_keydown(event):
    """Handle Enter key in the input field."""
    if event.key == "Enter":
        await send_message()


# =============================================================================
# INITIALIZATION
# =============================================================================

print("=" * 50)
print("Router Demo - PyCon US 2026")
print("=" * 50)
print(f"Backend modes:")
print(f"  Browser (WebLLM): {'Mock' if USE_MOCK_BROWSER else 'Real'}")
print(f"  Local server:     {'Mock' if USE_MOCK_LOCAL else LOCAL_API_URL}")
print(f"  Remote API:       {'Mock' if USE_MOCK_REMOTE else REMOTE_API_URL}")
print("=" * 50)

# Set initial status
if USE_MOCK_BROWSER:
    update_status("ready", "Browser: Mock")
else:
    update_status("", "Browser: Not loaded")

print("Ready! Click a demo button or type a message.")
