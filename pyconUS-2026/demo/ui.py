"""UI helpers: messages, streaming, tier selector, tool-call pills."""

from pyscript import document


# =============================================================================
# TIER SELECTOR
# =============================================================================

def get_selected_tier() -> str:
    """Return the globally selected tier."""
    from pyscript import window
    try:
        value = window.getDemoTier()
        if value:
            return str(value)
    except Exception:
        pass
    return "remote"


# =============================================================================
# MESSAGES
# =============================================================================

def add_message(content, role="assistant", route=None, tool_calls=None):
    messages_div = document.getElementById("messages")
    msg = document.createElement("div")
    msg.className = f"message {role}"

    html = ""
    if route:
        html += f'<span class="route-badge {route}">{route.upper()}</span><br>'
    if tool_calls:
        for tool in tool_calls:
            html += (
                f'<div class="tool-call" data-name="{tool["name"]}">'
                f'🔧 {tool["name"]}({tool.get("args", {})})</div>'
            )
    html += f'<span class="content">{content}</span>'
    msg.innerHTML = html

    messages_div.appendChild(msg)
    messages_div.scrollTop = messages_div.scrollHeight
    return msg


def add_streaming_message(route=None):
    """Create an empty streaming bubble; update with update_streaming_message()."""
    messages_div = document.getElementById("messages")
    msg = document.createElement("div")
    msg.className = "message assistant"

    html = ""
    if route:
        html += f'<span class="route-badge {route}">{route.upper()}</span><br>'
    html += '<span class="content"></span><span class="streaming-cursor"></span>'
    msg.innerHTML = html

    messages_div.appendChild(msg)
    messages_div.scrollTop = messages_div.scrollHeight
    return msg


def update_streaming_message(msg, token):
    content_span = msg.querySelector(".content")
    content_span.textContent += token
    msg.parentElement.scrollTop = msg.parentElement.scrollHeight


def finish_streaming_message(msg):
    cursor = msg.querySelector(".streaming-cursor")
    if cursor:
        cursor.remove()


_PYODIDE_TOOLS = {"analyze_csv"}

def add_tool_call_pill(tc):
    """Render a tool-call pill. Pyodide tools get a purple PYODIDE badge; MCP tools get amber TOOL."""
    messages_div = document.getElementById("messages")
    div = document.createElement("div")
    div.className = "message tool-call-pill"
    import json
    args_str = json.dumps(tc.args, ensure_ascii=False)
    if tc.name in _PYODIDE_TOOLS:
        badge = '<span class="route-badge pyodide">PYODIDE</span>'
        icon = "🐍"
    else:
        badge = '<span class="route-badge tool">MCP TOOL</span>'
        icon = "🔧"
    div.innerHTML = (
        f'{badge}<br>'
        f'<div class="tool-call" data-name="{tc.name}">'
        f'{icon} <strong>{tc.name}</strong>({args_str})</div>'
    )
    messages_div.appendChild(div)
    messages_div.scrollTop = messages_div.scrollHeight
    return div


def add_tool_result(tc, result_text):
    """Render a collapsible tool result block."""
    messages_div = document.getElementById("messages")
    div = document.createElement("div")
    div.className = "message tool-result"
    escaped = result_text.replace("<", "&lt;").replace(">", "&gt;")
    div.innerHTML = (
        f'<details><summary>🔍 Result from <strong>{tc.name}</strong></summary>'
        f'<pre class="tool-result-body">{escaped}</pre></details>'
    )
    messages_div.appendChild(div)
    messages_div.scrollTop = messages_div.scrollHeight
    return div


def clear_messages():
    document.getElementById("messages").innerHTML = ""


# =============================================================================
# STATUS BAR
# =============================================================================

def update_status(status, text):
    label = document.getElementById("local-status-text")
    if label:
        label.textContent = text


def update_progress(pct: int, text: str):
    bar = document.getElementById("progress-fill")
    label = document.getElementById("progress-text")
    if bar:
        bar.style.width = f"{max(0, min(100, pct))}%"
    if label:
        label.textContent = text
