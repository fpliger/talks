"""MCP tool client and tool-call normalization helpers."""

import json
from pyscript import fetch

from config import MCP_SERVER_URL
from fs_bridge import save_file


# =============================================================================
# MCP HTTP CLIENT
# =============================================================================

async def list_tools() -> list:
    """Return MCP tool definitions from the server."""
    try:
        response = await fetch(f"{MCP_SERVER_URL}/tools")
        data = await response.json()
        return data.get("tools", [])
    except Exception as e:
        print(f"MCP list_tools failed: {e}")
        return []


async def call_tool(name: str, arguments: dict) -> dict:
    """Execute a tool: intercept save_to_file for FS Access API, else call MCP."""
    if name == "save_to_file":
        filename = arguments.get("filename", "notes.md")
        content = arguments.get("content", "")
        status = await save_file(filename, content)
        return {"content": [{"type": "text", "text": status}]}

    try:
        response = await fetch(
            f"{MCP_SERVER_URL}/call-tool",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": name, "arguments": arguments}),
        )
        return await response.json()
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Tool error: {e}"}]}


# =============================================================================
# SCHEMA HELPERS
# =============================================================================

def format_tools_for_llm(mcp_tools: list) -> list:
    """Convert MCP tool defs to OpenAI function-calling format."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
            },
        }
        for tool in mcp_tools
    ]


def normalize_tool_calls(raw_tool_calls: list, source_tier: str) -> list:
    """Normalize tool_call objects from different tier response shapes.

    OpenAI:  [{id, type, function: {name, arguments}}]
    Ollama:  [{function: {name, arguments}}]   (no id)
    Returns: [{id, name, args: dict}]
    """
    normalized = []
    for i, tc in enumerate(raw_tool_calls):
        fn = tc.get("function", tc)
        name = fn.get("name", "")
        raw_args = fn.get("arguments", "{}")
        try:
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        except json.JSONDecodeError:
            args = {"raw": raw_args}
        normalized.append({
            "id": tc.get("id", f"call_{i}"),
            "name": name,
            "args": args,
        })
    return normalized
