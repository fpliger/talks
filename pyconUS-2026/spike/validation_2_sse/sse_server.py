"""Mock SSE server that simulates LLM token streaming.

Run with: python sse_server.py
Exposes: POST /v1/chat/completions (OpenAI-compatible streaming)

This mimics what OpenAI/Anthropic APIs return for streaming completions.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time

# Simulated response tokens
RESPONSE_TOKENS = [
    "Hello", "!", " I", "'m", " an", " AI", " assistant",
    " running", " in", " your", " browser", ".",
    " This", " response", " is", " being", " streamed",
    " token", " by", " token", "."
]


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
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            stream = data.get("stream", False)
        except:
            stream = False

        if stream:
            self._stream_response()
        else:
            self._send_full_response()

    def _stream_response(self):
        """Send SSE streaming response like OpenAI."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._send_cors_headers()
        self.end_headers()

        # Send tokens one by one
        for i, token in enumerate(RESPONSE_TOKENS):
            event = {
                "id": f"chatcmpl-{i}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "mock-gpt-4",
                "choices": [{
                    "index": 0,
                    "delta": {"content": token} if i > 0 else {"role": "assistant", "content": token},
                    "finish_reason": None
                }]
            }

            line = f"data: {json.dumps(event)}\n\n"
            self.wfile.write(line.encode())
            self.wfile.flush()
            time.sleep(0.05)  # 50ms between tokens

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

        response = {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "mock-gpt-4",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "".join(RESPONSE_TOKENS)
                },
                "finish_reason": "stop"
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
