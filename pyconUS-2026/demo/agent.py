"""Tier-agnostic agent loop.

Runs: stream LLM → collect tool_calls → execute each tool → loop
until finish_reason == "stop".

The loop owns all diagram state (activate/deactivate) and all streaming
bubble lifecycle.  Callers only need to supply:
  on_tool_call(tc)          — render a tool-call pill
  on_tool_result(tc, res)   — render the tool result block

Step mode:
  When window.agentStepMode is truthy the loop pauses before every
  meaningful boundary and calls window.agentPaused(label) so the UI can
  show a "▶ next step" button.  window.agentResumeStep() unblocks it.
"""

import asyncio
import json
from streaming import Delta, ToolCall
from tools import call_tool, PYODIDE_TOOLS
from ui import (
    agent_log, agent_activate, agent_deactivate,
    add_streaming_message, update_streaming_message, finish_streaming_message,
    add_message,
)


# ---------------------------------------------------------------------------
# Step-mode gate
# ---------------------------------------------------------------------------

_step_gate: asyncio.Event | None = None


def _is_step_mode() -> bool:
    try:
        from pyscript import window
        return bool(window.agentStepMode)
    except Exception:
        return False


async def _checkpoint(label: str):
    """Pause here when step mode is active; resume when JS calls agentResumeStep()."""
    global _step_gate
    if not _is_step_mode():
        return
    _step_gate = asyncio.Event()
    agent_log("step", f"⏸ paused — {label}")
    try:
        from pyscript import window
        window.agentPaused(label)
    except Exception:
        pass
    await _step_gate.wait()
    agent_log("step", f"▶ resumed — continuing from: {label}")


def resume_step():
    """Called by JS (via PyScript) to unblock the current checkpoint."""
    global _step_gate
    if _step_gate and not _step_gate.is_set():
        _step_gate.set()


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

def _push_context(messages: list):
    """Push the current messages[] to the JS Context tab."""
    try:
        from pyscript import window
        from pyodide.ffi import to_js
        window.archUpdateContext(to_js(messages))
    except Exception:
        pass


def _assistant_with_tool_calls(tool_calls: list[ToolCall]) -> dict:
    return {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.name, "arguments": json.dumps(tc.args)},
            }
            for tc in tool_calls
        ],
    }


def _tool_result_message(tc: ToolCall, result_text: str) -> dict:
    return {
        "role": "tool",
        "tool_call_id": tc.id,
        "content": result_text,
    }


# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

async def run_agent_loop(
    tier,
    messages: list,
    tools: list,
    route: str = "",
    on_tool_call=None,
    on_tool_result=None,
    max_turns: int = 8,
):
    """Run the agentic loop until stop or max_turns.

    Args:
        tier:           Tier instance (InBrowserTier / LocalTier / RemoteTier).
        messages:       Initial message list (mutated in place).
        tools:          Tool schemas in OpenAI format (empty list = no tools).
        route:          Tier name string used as the streaming bubble badge.
        on_tool_call:   Optional callback(tc) — render a tool-call pill.
        on_tool_result: Optional callback(tc, result_text) — render result block.
        max_turns:      Safety cap on loop iterations.
    """
    _pyodide_tool_names = {t["name"] for t in PYODIDE_TOOLS}
    on_tool_call = on_tool_call or (lambda tc: None)
    on_tool_result = on_tool_result or (lambda tc, r: None)

    agent_activate("user", "user-agent")
    agent_activate("agent")
    turn_num = 0
    _push_context(messages)

    for _ in range(max_turns):
        turn_num += 1
        n_msgs = len(messages)
        agent_log("agent", f"turn {turn_num} — {n_msgs} message(s) in context, calling {tier.name} LLM")

        # ① Before sending anything to the LLM
        await _checkpoint(f"turn {turn_num}: about to send {n_msgs} message(s) to {tier.name} LLM")

        agent_activate("llm", "agent-llm")
        agent_log("llm_start", f"LLM turn {turn_num} started ({tier.name})")
        bubble = add_streaming_message(route=route)
        collected_tool_calls: list[ToolCall] = []
        assistant_text = ""
        token_count = 0

        async for delta in tier.stream_chat(messages, tools):
            if delta.text:
                token_count += 1
                if token_count == 1:
                    agent_log("llm_start", f"first token received from {tier.name}")
                assistant_text += delta.text
                update_streaming_message(bubble, delta.text)
            if delta.tool_call:
                collected_tool_calls.append(delta.tool_call)
                agent_log("tool_call", f"LLM requested: {delta.tool_call.name}({json.dumps(delta.tool_call.args)})")
            if delta.finish_reason == "stop":
                agent_log("agent", f"turn {turn_num} — LLM finished: stop ({token_count} token(s))")
                finish_streaming_message(bubble)
                agent_deactivate("llm")
                if assistant_text:
                    messages.append({"role": "assistant", "content": assistant_text})
                    _push_context(messages)
                # Tools were offered but ignored — model doesn't support function calling
                if tools and turn_num == 1 and not collected_tool_calls:
                    tool_names = ", ".join(t.get("function", t).get("name", "?") for t in tools)
                    agent_log("error", f"{tier.name} LLM did not call any tools — model may not support function calling")
                    add_message(
                        f"⚠️ The <strong>{tier.name}</strong> model responded without calling "
                        f"any tools (<code>{tool_names}</code>). This model likely does not "
                        "support function calling. Try switching to the <strong>remote</strong> "
                        "or <strong>local</strong> tier.",
                        role="system",
                    )
                    agent_deactivate("agent")
                    agent_deactivate("user")
                    return
                # ② Normal stop — pause so it can be read before loop exits
                await _checkpoint(f"turn {turn_num}: LLM delivered final answer ({token_count} token(s)) — loop will end")
                agent_deactivate("agent")
                agent_deactivate("user")
                return
            if delta.finish_reason == "tool_calls":
                tool_names = ", ".join(tc.name for tc in collected_tool_calls)
                agent_log("agent", f"turn {turn_num} — LLM finished: tool_calls → [{tool_names}]")
                break

        finish_streaming_message(bubble)
        agent_deactivate("llm")

        if not collected_tool_calls:
            agent_log("agent", f"turn {turn_num} — stream ended with no tool calls — treating as final answer")
            if assistant_text:
                messages.append({"role": "assistant", "content": assistant_text})
                _push_context(messages)
            await _checkpoint(f"turn {turn_num}: stream ended (implicit stop, no tool calls) — loop will end")
            agent_deactivate("agent")
            agent_deactivate("user")
            return

        # ③ LLM declared which tools it wants — pause before any tool fires
        tool_names = ", ".join(tc.name for tc in collected_tool_calls)
        await _checkpoint(f"LLM decided to call {len(collected_tool_calls)} tool(s): {tool_names} — about to dispatch")

        messages.append(_assistant_with_tool_calls(collected_tool_calls))
        _push_context(messages)

        for tc in collected_tool_calls:
            agent_log("tool_call", f"dispatching → {tc.name}({json.dumps(tc.args)})")

            if tc.name in _pyodide_tool_names:
                agent_activate("pyodide", "agent-pyodide")
            else:
                agent_activate("mcp", "agent-mcp")

            # ④ Right before each individual tool executes
            await _checkpoint(f"about to run: {tc.name}({json.dumps(tc.args)})")

            on_tool_call(tc)
            result = await call_tool(tc.name, tc.args)
            result_text = " ".join(
                item.get("text", "") for item in result.get("content", [])
                if item.get("type") == "text"
            ) or str(result)
            preview = result_text[:120] + ("…" if len(result_text) > 120 else "")
            agent_log("tool_result", f"{tc.name} → {preview}")
            on_tool_result(tc, result_text)

            if tc.name in _pyodide_tool_names:
                agent_deactivate("pyodide")
            else:
                agent_deactivate("mcp")

            # ⑤ Tool returned — pause so the raw result can be read before it enters context
            await _checkpoint(f"✓ {tc.name} returned {len(result_text)} char(s): {preview[:80]} — about to add to context")

            messages.append(_tool_result_message(tc, result_text))
            _push_context(messages)

        n_results = len(collected_tool_calls)
        agent_log("agent", f"{n_results} tool result(s) added to context — starting turn {turn_num + 1}")

        # ⑥ All results are in context — pause before handing back to the LLM
        await _checkpoint(f"{n_results} tool result(s) now in context — about to call {tier.name} LLM (turn {turn_num + 1})")

    # max_turns reached
    agent_deactivate("agent")
    agent_deactivate("user")
