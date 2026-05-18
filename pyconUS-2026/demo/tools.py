"""MCP tool client, Pyodide-backed tools, and tool-call normalization helpers."""

import json
from pyscript import fetch

from config import MCP_SERVER_URL
from fs_bridge import save_file
from ui import agent_log


# =============================================================================
# PYODIDE-BACKED TOOLS
# These run entirely in the browser — no network call, no backend.
# The LLM decides to call them just like any other tool.
# =============================================================================

PYODIDE_TOOLS = [
    {
        "name": "analyze_csv",
        "description": (
            "Analyze a CSV file using Pandas running in the browser (Pyodide). "
            "Returns column names, row count, total revenue, top product by revenue, and QoQ growth. "
            "Call this tool whenever the user asks about the file structure, column names, or data analysis. "
            "No data leaves the browser."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the CSV file, relative to the demo root (e.g. './data/sales.csv')",
                }
            },
            "required": ["path"],
        },
    }
]


async def _call_analyze_csv(arguments: dict) -> dict:
    """Run Pandas analysis in Pyodide. Returns a structured summary string."""
    import io as _io
    try:
        import pandas as pd
    except ImportError:
        agent_log("error", "analyze_csv: pandas not available in this environment")
        return {"content": [{"type": "text", "text": "Pandas not available in this environment."}]}

    path = arguments.get("path", "./data/sales.csv")
    agent_log("tool_pyodide", f"analyze_csv: fetching {path} (Pyodide/Pandas — in-browser)")
    try:
        response = await fetch(path)
        csv_text = await response.text()
        agent_log("tool_pyodide", f"analyze_csv: loaded {len(csv_text)} bytes — running Pandas")
        df = pd.read_csv(_io.StringIO(csv_text))

        rows = len(df)
        total_rev = df["revenue"].sum()
        top_product = df.groupby("product")["revenue"].sum().idxmax()
        top_rev = df.groupby("product")["revenue"].sum().max()

        try:
            df["date"] = pd.to_datetime(df["date"])
            df["quarter"] = df["date"].dt.quarter
            q_rev = df.groupby("quarter")["revenue"].sum()
            qoq = ((q_rev.iloc[-1] - q_rev.iloc[-2]) / q_rev.iloc[-2] * 100) if len(q_rev) >= 2 else 0
            qoq_str = f"{qoq:+.1f}% QoQ"
        except Exception:
            qoq_str = "N/A"

        columns = ", ".join(df.columns.tolist())
        summary = (
            f"Columns: {columns} | "
            f"Rows: {rows:,} | "
            f"Total revenue: ${total_rev:,.0f} | "
            f"Top product: {top_product} (${top_rev:,.0f}) | "
            f"QoQ growth: {qoq_str}"
        )
        agent_log("tool_pyodide", f"analyze_csv: done — {summary}")
        return {"content": [{"type": "text", "text": summary}]}

    except Exception as e:
        agent_log("error", f"analyze_csv: failed — {e}")
        return {"content": [{"type": "text", "text": f"CSV analysis failed: {e}"}]}


# =============================================================================
# MCP HTTP CLIENT
# =============================================================================

async def list_tools() -> list:
    """Return MCP tool definitions from the server."""
    url = f"{MCP_SERVER_URL}/tools"
    agent_log("mcp", f"list_tools: GET {url}")
    try:
        response = await fetch(url)
        data = await response.json()
        tools = data.get("tools", [])
        agent_log("mcp", f"list_tools: {len(tools)} tool(s) — {', '.join(t['name'] for t in tools)}")
        return tools
    except Exception as e:
        agent_log("error", f"list_tools: failed — {e}")
        return []


async def call_tool(name: str, arguments: dict) -> dict:
    """Execute a tool by name.

    Dispatch order:
      1. analyze_csv  → Pyodide (in-browser Pandas, no network)
      2. save_to_file → File System Access API / download (no backend)
      3. everything else → MCP HTTP server
    """
    if name == "analyze_csv":
        return await _call_analyze_csv(arguments)

    if name == "save_to_file":
        filename = arguments.get("filename", "notes.md")
        content = arguments.get("content", "")
        agent_log("tool_pyodide", f"save_to_file: writing '{filename}' via File System Access API ({len(content)} chars)")
        status = await save_file(filename, content)
        agent_log("tool_pyodide", f"save_to_file: {status}")
        return {"content": [{"type": "text", "text": status}]}

    url = f"{MCP_SERVER_URL}/call-tool"
    agent_log("mcp", f"call_tool: POST {url} — {name}({json.dumps(arguments)})")
    try:
        response = await fetch(
            url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": name, "arguments": arguments}),
        )
        result = await response.json()
        texts = [i.get("text", "") for i in result.get("content", []) if i.get("type") == "text"]
        preview = " ".join(texts)[:120]
        agent_log("mcp", f"call_tool: {name} → {preview}")
        return result
    except Exception as e:
        agent_log("error", f"call_tool {name}: {e}")
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
