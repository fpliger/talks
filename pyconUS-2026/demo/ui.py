"""
UI Helpers for the Router Demo.

Handles all DOM manipulation: messages, status indicators, etc.
"""

from pyscript import document


def add_message(content, role="assistant", route=None, tool_calls=None):
    """Add a message to the chat UI.

    Args:
        content: The message text/HTML
        role: "user", "assistant", or "system"
        route: Optional route badge ("browser", "local", "remote", "hybrid", "tool")
        tool_calls: Optional list of tool call dicts to display
    """
    messages_div = document.getElementById("messages")

    msg = document.createElement("div")
    msg.className = f"message {role}"

    html = ""
    if route:
        html += f'<span class="route-badge {route}">{route.upper()}</span><br>'

    if tool_calls:
        for tool in tool_calls:
            html += f'<div class="tool-call">🔧 {tool["name"]}({tool.get("args", {})})</div>'

    html += content
    msg.innerHTML = html

    messages_div.appendChild(msg)
    messages_div.scrollTop = messages_div.scrollHeight

    return msg


def add_streaming_message(route=None):
    """Add an empty message for streaming content.

    Returns the message element so you can update it with update_streaming_message().
    """
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
    """Append a token to a streaming message."""
    content_span = msg.querySelector(".content")
    content_span.textContent += token
    msg.parentElement.scrollTop = msg.parentElement.scrollHeight


def finish_streaming_message(msg):
    """Remove the cursor from a streaming message."""
    cursor = msg.querySelector(".streaming-cursor")
    if cursor:
        cursor.remove()


def clear_messages():
    """Clear all messages from the chat."""
    messages_div = document.getElementById("messages")
    messages_div.innerHTML = ""


def update_status(status, text):
    """Update the model status indicator in the status bar.

    Args:
        status: CSS class for the dot ("ready", "loading", or "")
        text: Status text to display
    """
    dot = document.getElementById("local-status")
    label = document.getElementById("local-status-text")
    dot.className = f"status-dot {status}"
    label.textContent = text
