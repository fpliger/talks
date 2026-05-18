"""
Router for the Demo.

Decides which model backend to use based on the prompt.
"""


def route_request(prompt: str) -> dict:
    """Determine the routing path for a prompt.

    Routing logic:
    - BROWSER: Simple tasks that can run in-browser (fast, private)
    - LOCAL: Moderate tasks for local server (if available)
    - HYBRID: Data processing + reasoning (local data + remote model)
    - REMOTE: Complex queries or tasks needing tools

    Args:
        prompt: User's input prompt

    Returns:
        dict with:
            - path: "browser" | "local" | "hybrid" | "remote"
            - reason: Human-readable explanation
            - needs_tools: List of required tool names (if any)
    """
    prompt_lower = prompt.lower()

    # Patterns for in-browser handling (simple, quick, private)
    browser_patterns = [
        "convert", "format", "translate to", "what is",
        "calculate", "count", "spell", "define"
    ]

    # Patterns that need external tools
    tool_patterns = {
        "search": "web_search",
        "find": "web_search",
        "look up": "web_search",
        "save": "save_to_file",
        "store": "save_to_file",
        "remember": "save_to_file",
        "notes": "save_to_file",
    }

    # Patterns for hybrid processing (local data + remote reasoning)
    hybrid_patterns = ["summarize", "analyze", "csv", "data", "file"]

    # Check for tool needs → remote path
    needed_tools = []
    for pattern, tool in tool_patterns.items():
        if pattern in prompt_lower:
            if tool not in needed_tools:
                needed_tools.append(tool)

    if needed_tools:
        matched_kw = next((p for p in tool_patterns if p in prompt_lower), needed_tools[0])
        return {
            "path": "remote",
            "reason": f"Requires tools: {', '.join(needed_tools)}",
            "needs_tools": needed_tools,
            "keyword": matched_kw,
        }

    # Check for hybrid patterns
    for pattern in hybrid_patterns:
        if pattern in prompt_lower:
            return {
                "path": "hybrid",
                "reason": "Data processing + reasoning needed",
                "needs_tools": [],
                "keyword": pattern,
            }

    # Check for browser-local patterns (simple, fast, private)
    for pattern in browser_patterns:
        if pattern in prompt_lower:
            return {
                "path": "browser",
                "reason": "Simple task → in-browser (WebLLM)",
                "needs_tools": [],
                "keyword": pattern,
            }

    # Default to remote for complex queries
    return {
        "path": "remote",
        "reason": "Complex query → remote model",
        "needs_tools": [],
        "keyword": "",
    }
