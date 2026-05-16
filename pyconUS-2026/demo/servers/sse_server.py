"""Mock SSE server that simulates LLM token streaming.

Run with: python sse_server.py
Exposes: POST /v1/chat/completions (OpenAI-compatible streaming)

Prompt-aware: matches the last user message against known demo prompts and
returns a contextually correct streamed response.  Falls back to a generic
reply for free-form input.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time


def _has_tool_result(messages: list) -> bool:
    """Return True if the history already contains a tool result message."""
    return any(m.get("role") == "tool" for m in messages)


def _wants_tools(messages: list, tools: list) -> bool:
    """Return True if this is the first turn of a tool-calling demo."""
    if not tools:
        return False
    last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last = m.get("content", "").lower()
            break
    return (
        "climate" in last or "stories" in last or "notes" in last or "search" in last
        or "csv" in last or "analyze" in last or "sales" in last
    )


def _pick_tool_calls(messages: list) -> list[dict]:
    """Return the tool_calls to emit on the first agent turn."""
    last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last = m.get("content", "").lower()
            break
    # Demo 2 — CSV analysis via Pyodide tool
    if "csv" in last or "analyze" in last or "sales" in last:
        return [{"name": "analyze_csv", "args": {"path": "./data/sales.csv"}}]
    # Demo 3 — climate search + save
    calls = [{"name": "web_search", "args": {"query": "top climate stories this week", "k": 3}}]
    if "save" in last or "notes" in last:
        calls.append({"name": "save_to_file", "args": {"filename": "climate_notes.md", "content": "placeholder"}})
    return calls


def _pick_response(messages: list) -> list[str]:
    """Return token list for the final (after tool results) assistant turn."""
    last = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last = m.get("content", "").lower()
            break

    # Demo 1 — ISO date conversion
    if "iso" in last or "may 5" in last or "2026" in last:
        return list("2026-05-05")

    # Demo 2 — narrative after analyze_csv tool result
    if "csv" in last or "analyze" in last or "sales" in last or "board slide" in last or "executive summary" in last:
        return (
            "Revenue reached $2.4 M in the first half of 2026, driven by strong "
            "Analytics Suite performance at 43 % of total sales. "
            "Quarter-over-quarter growth of +11.2 % signals healthy demand momentum heading into Q3. "
            "Management recommends accelerating Analytics Suite inventory ahead of the summer peak season."
        ).split(" ")

    # Demo 3 — final summary after tool results arrive
    if "climate" in last or "stories" in last or "notes" in last:
        return (
            "I've searched for the top climate stories this week and saved them "
            "to your notes. The headlines cover record renewable capacity, ocean "
            "cleanup milestones, and Arctic ice recovery — all strong signals of "
            "progress on the climate agenda."
        ).split(" ")

    # Generic fallback
    return (
        "I'm a mock remote LLM. Your message was received and processed "
        "server-side. Switch to a real API endpoint by setting REMOTE_API_KEY."
    ).split(" ")


class SSEHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

    def do_POST(self):
        if self.path == "/v1/chat/completions":
            self._handle_completions()
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def _handle_completions(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
        except Exception:
            data = {}

        messages = data.get("messages", [])
        tools    = data.get("tools", [])
        stream   = data.get("stream", False)

        # Decide: emit tool_calls (first agent turn) or text (final/text turn)
        if _wants_tools(messages, tools) and not _has_tool_result(messages):
            self._tool_calls_to_emit = _pick_tool_calls(messages)
            if stream:
                self._stream_tool_calls()
            else:
                self._send_tool_calls()
        else:
            self._response_tokens = _pick_response(messages)
            if stream:
                self._stream_response()
            else:
                self._send_full_response()

    def _stream_tool_calls(self):
        """Emit an SSE stream that ends with finish_reason=tool_calls."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._send_cors_headers()
        self.end_headers()

        tool_calls = getattr(self, "_tool_calls_to_emit", [])
        for idx, tc in enumerate(tool_calls):
            # First chunk: id + name
            chunk = {
                "id": f"chatcmpl-tc-{idx}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-remote",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "tool_calls": [{
                            "index": idx,
                            "id": f"call_{idx}",
                            "type": "function",
                            "function": {"name": tc["name"], "arguments": ""},
                        }]
                    },
                    "finish_reason": None,
                }]
            }
            self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.03)

            # Second chunk: arguments
            args_str = json.dumps(tc["args"])
            chunk2 = {
                "id": f"chatcmpl-tc-{idx}-args",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-remote",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "tool_calls": [{
                            "index": idx,
                            "function": {"arguments": args_str},
                        }]
                    },
                    "finish_reason": None,
                }]
            }
            self.wfile.write(f"data: {json.dumps(chunk2)}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.03)

        # Final chunk with finish_reason=tool_calls
        final = {
            "id": "chatcmpl-tc-final",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "mock-remote",
            "choices": [{"index": 0, "delta": {}, "finish_reason": "tool_calls"}]
        }
        self.wfile.write(f"data: {json.dumps(final)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _send_tool_calls(self):
        """Non-streaming tool_calls response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()

        tool_calls = getattr(self, "_tool_calls_to_emit", [])
        response = {
            "id": "chatcmpl-tc",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "mock-remote",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": f"call_{i}",
                            "type": "function",
                            "function": {"name": tc["name"], "arguments": json.dumps(tc["args"])},
                        }
                        for i, tc in enumerate(tool_calls)
                    ],
                },
                "finish_reason": "tool_calls",
            }]
        }
        self.wfile.write(json.dumps(response).encode())

    def _stream_response(self):
        """Send SSE streaming response like OpenAI."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._send_cors_headers()
        self.end_headers()

        tokens = getattr(self, "_response_tokens", ["…"])
        for i, token in enumerate(tokens):
            # Add space prefix for word-split tokens (not for char-split like ISO date)
            tok = token if i == 0 else (" " + token if len(token) > 1 else token)
            event = {
                "id": f"chatcmpl-{i}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-remote",
                "choices": [{
                    "index": 0,
                    "delta": {"content": tok} if i > 0 else {"role": "assistant", "content": tok},
                    "finish_reason": None,
                }]
            }
            self.wfile.write(f"data: {json.dumps(event)}\n\n".encode())
            self.wfile.flush()
            time.sleep(0.04)

        # Send final event
        final_event = {
            "id": f"chatcmpl-final",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "mock-gpt-4",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        self.wfile.write(f"data: {json.dumps(final_event)}\n\n".encode())
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _send_full_response(self):
        """Send non-streaming response."""
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._send_cors_headers()
        self.end_headers()

        tokens = getattr(self, "_response_tokens", ["…"])
        content = " ".join(tokens) if len(tokens[0]) > 1 else "".join(tokens)
        response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "mock-remote",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }]
        }
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"[SSE Server] {args[0]}")


if __name__ == "__main__":
    port = 8766
    server = HTTPServer(("localhost", port), SSEHandler)
    print(f"SSE test server running on http://localhost:{port}")
    print("Endpoints: POST /v1/chat/completions (stream=true for SSE)")
    server.serve_forever()
