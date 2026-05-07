"""
MCP Tools for the Router Demo.

Handles communication with MCP (Model Context Protocol) servers.
"""

import json
from pyscript import fetch

from config import MCP_SERVER_URL


async def list_tools() -> list:
    """List available tools from the MCP server.

    Returns:
        List of tool definitions, each with name, description, inputSchema
    """
    try:
        response = await fetch(f"{MCP_SERVER_URL}/tools")
        data = await response.json()
        return data.get("tools", [])
    except Exception as e:
        print(f"MCP list_tools failed: {e}")
        return []


async def call_tool(name: str, arguments: dict) -> dict:
    """Call a tool on the MCP server.

    Args:
        name: Tool name
        arguments: Tool arguments dict

    Returns:
        Tool result dict with "content" key
    """
    try:
        response = await fetch(
            f"{MCP_SERVER_URL}/call-tool",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": name, "arguments": arguments})
        )
        result = await response.json()
        return result
    except Exception as e:
        return {"content": [{"type": "text", "text": f"Tool error: {e}"}]}


def format_tools_for_llm(mcp_tools: list) -> list:
    """Convert MCP tool definitions to OpenAI function format.

    Args:
        mcp_tools: List of MCP tool dicts

    Returns:
        List of OpenAI-compatible tool definitions
    """
    tools = []
    for tool in mcp_tools:
        tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool.get("inputSchema", {"type": "object", "properties": {}})
            }
        })
    return tools
