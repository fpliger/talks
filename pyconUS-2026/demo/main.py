"""Router Demo — main entry point.

Demo 1: In-browser date conversion (default tier: in-browser)
Demo 2: Hybrid — Pandas in Pyodide + LLM narrative (default tier: remote)
Demo 3: Remote + MCP tools agent loop (default tier: remote)

Each demo reads its tier selector, then streams through the chosen tier.
"""

import asyncio
import io
from pyscript import document, fetch

from ui import (
    add_message, clear_messages, update_status,
    add_streaming_message, update_streaming_message, finish_streaming_message,
    add_tool_call_pill, add_tool_result, get_selected_tier,
)
from router import route_request
from tiers import get_tier
from tools import list_tools, format_tools_for_llm
from agent import run_agent_loop


# =============================================================================
# SHARED STREAMING HELPER
# =============================================================================

async def _stream_into_bubble(tier, messages, tools=None, route=None):
    """Stream tier.stream_chat() into a new message bubble. Returns full text."""
    msg = add_streaming_message(route=route)
    full_text = ""
    async for delta in tier.stream_chat(messages, tools):
        if delta.text:
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

    messages = [{"role": "user", "content": prompt}]
    await _stream_into_bubble(tier, messages, route=tier_name)


# =============================================================================
# DEMO 2 — Hybrid: Pandas in-browser + LLM narrative
# =============================================================================

async def run_demo_2(event=None):
    clear_messages()
    tier_name = get_selected_tier()
    tier = get_tier(tier_name)

    prompt = "Summarize this 200-line CSV I just dropped in"
    add_message(prompt, role="user")
    add_message("<em>Step 1 → Local Pandas (browser) — no network</em>", role="system")

    # --- Pandas analysis in Pyodide ---
    try:
        import pandas as pd

        response = await fetch("./data/sales.csv")
        csv_text = await response.text()
        df = pd.read_csv(io.StringIO(csv_text))

        rows = len(df)
        total_rev = df["revenue"].sum()
        top_product = df.groupby("product")["revenue"].sum().idxmax()
        top_rev = df.groupby("product")["revenue"].sum().max()

        # QoQ growth: compare Q2 vs Q1 if date column present
        try:
            df["date"] = pd.to_datetime(df["date"])
            df["quarter"] = df["date"].dt.quarter
            q_rev = df.groupby("quarter")["revenue"].sum()
            qoq = ((q_rev.iloc[-1] - q_rev.iloc[-2]) / q_rev.iloc[-2] * 100) if len(q_rev) >= 2 else 0
            qoq_str = f"{qoq:+.1f}% QoQ"
        except Exception:
            qoq_str = "N/A"

        summary = (
            f"Rows: {rows:,} · "
            f"Total revenue: ${total_rev:,.0f} · "
            f"Top product: {top_product} (${top_rev:,.0f}) · "
            f"Growth: {qoq_str}"
        )

        pandas_msg = document.getElementById("messages")
        div = document.createElement("div")
        div.className = "message assistant"
        div.innerHTML = (
            f'<span class="route-badge in-browser">IN-BROWSER</span><br>'
            f'<span class="content">'
            f'<strong>Pandas analysis</strong><br>'
            f'<code style="display:block;margin-top:.5rem;white-space:pre-wrap">{summary}</code>'
            f'</span>'
        )
        pandas_msg.appendChild(div)
        pandas_msg.scrollTop = pandas_msg.scrollHeight

    except Exception as e:
        summary = f"(Pandas unavailable: {e} — using placeholder data)"
        add_message(f"<em>{summary}</em>", role="system")
        summary = "Rows: 200 · Total revenue: $2,400,000 · Top product: Widget Pro · Growth: +12% QoQ"

    # --- Remote / selected tier frames the results ---
    add_message(
        f"<em>Step 2 → {tier_name.upper()} model frames the narrative</em>",
        role="system",
    )

    framing_prompt = (
        f"You are a data analyst. Based on this sales summary, write a 3-sentence "
        f"executive summary suitable for a board slide:\n\n{summary}"
    )
    messages = [{"role": "user", "content": framing_prompt}]
    await _stream_into_bubble(tier, messages, route=tier_name)


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

    # Discover tools
    mcp_tools = await list_tools()
    tool_names = [t["name"] for t in mcp_tools] if mcp_tools else ["(none found)"]
    add_message(f"<em>MCP tools available: {', '.join(tool_names)}</em>", role="system")

    tools_for_llm = format_tools_for_llm(mcp_tools)
    messages = [{"role": "user", "content": prompt}]

    # Streaming bubble state — held across turns
    current_bubble = [None]

    def on_turn_start():
        current_bubble[0] = add_streaming_message(route=tier_name)

    def on_turn_end():
        if current_bubble[0]:
            finish_streaming_message(current_bubble[0])
            current_bubble[0] = None

    def on_delta(text):
        if current_bubble[0]:
            update_streaming_message(current_bubble[0], text)

    def on_tool_call(tc):
        add_tool_call_pill(tc)

    def on_tool_result(tc, result_text):
        add_tool_result(tc, result_text)

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
print("Ready.")
