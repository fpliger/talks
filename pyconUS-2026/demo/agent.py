"""Tier-agnostic agent loop for Demo 3.

Runs: stream LLM → collect tool_calls → execute each via MCP → loop
until finish_reason == "stop".

Callbacks let callers update the UI as each phase happens:
  on_delta(text)           — stream a token into the current bubble
  on_tool_call(tc)         — render a tool-call pill
  on_tool_result(tc, res)  — render the tool result block
  on_turn_start()          — open a new assistant bubble
  on_turn_end()            — close the current bubble (remove cursor)
"""

import json
from streaming import Delta, ToolCall
from tools import call_tool
from ui import agent_log


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


async def run_agent_loop(
    tier,
    messages: list,
    tools: list,
    on_delta,
    on_tool_call,
    on_tool_result,
    on_turn_start,
    on_turn_end,
    max_turns: int = 8,
):
    """Run the agentic loop until stop or max_turns."""
    turn_num = 0
    for _ in range(max_turns):
        turn_num += 1
        n_msgs = len(messages)
        agent_log("agent", f"turn {turn_num} — sending {n_msgs} message(s) to {tier.name} LLM")
        on_turn_start()
        collected_tool_calls: list[ToolCall] = []
        token_count = 0

        async for delta in tier.stream_chat(messages, tools):
            if delta.text:
                token_count += 1
                if token_count == 1:
                    agent_log("llm_start", f"first token received from {tier.name}")
                on_delta(delta.text)
            if delta.tool_call:
                collected_tool_calls.append(delta.tool_call)
                agent_log("tool_call", f"LLM requested tool: {delta.tool_call.name}({json.dumps(delta.tool_call.args)})")
            if delta.finish_reason == "stop":
                agent_log("agent", f"turn {turn_num} complete — finish_reason: stop ({token_count} tokens)")
                on_turn_end()
                return
            if delta.finish_reason == "tool_calls":
                agent_log("agent", f"turn {turn_num} complete — finish_reason: tool_calls ({len(collected_tool_calls)} call(s))")
                break

        on_turn_end()

        if not collected_tool_calls:
            agent_log("agent", "no tool calls and no stop signal — exiting loop")
            return

        # Append assistant turn with tool_calls, then execute each tool
        messages.append(_assistant_with_tool_calls(collected_tool_calls))

        for tc in collected_tool_calls:
            on_tool_call(tc)
            agent_log("tool_call", f"dispatching {tc.name} → args: {json.dumps(tc.args)}")
            result = await call_tool(tc.name, tc.args)
            # Extract text from MCP content array
            result_text = " ".join(
                item.get("text", "") for item in result.get("content", [])
                if item.get("type") == "text"
            ) or str(result)
            preview = result_text[:120] + ("…" if len(result_text) > 120 else "")
            agent_log("tool_result", f"{tc.name} → {preview}")
            on_tool_result(tc, result_text)
            messages.append(_tool_result_message(tc, result_text))
        agent_log("agent", f"tool results appended — starting turn {turn_num + 1}")
