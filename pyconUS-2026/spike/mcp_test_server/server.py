"""Simple MCP-over-HTTP test server for spike validation.

Run with: python server.py
Exposes: GET /tools, POST /call-tool

This mimics what an MCP HTTP server would expose, enough to validate
the PyScript client can do list_tools + call_tool round-trips.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Simple tool definitions (MCP format)
TOOLS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g. 'San Francisco'"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculate",
        "description": "Perform a simple calculation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression to evaluate, e.g. '2 + 2'"
                }
            },
            "required": ["expression"]
        }
    }
]


def call_tool(name: str, arguments: dict) -> dict:
    """Execute a tool and return the result."""
    if name == "get_weather":
        location = arguments.get("location", "Unknown")
        return {
            "content": [
                {"type": "text", "text": f"Weather in {location}: 72°F, sunny"}
            ]
        }
    elif name == "calculate":
        expr = arguments.get("expression", "0")
        try:
            # Safe eval for simple math
            result = eval(expr, {"__builtins__": {}}, {})
            return {
                "content": [
                    {"type": "text", "text": f"Result: {result}"}
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {"type": "text", "text": f"Error: {e}"}
                ],
                "isError": True
            }
    else:
        return {
            "content": [
                {"type": "text", "text": f"Unknown tool: {name}"}
            ],
            "isError": True
        }


class MCPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/tools":
            self._send_json({"tools": TOOLS})
        elif self.path == "/health":
            self._send_json({"status": "ok"})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/call-tool":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                name = data.get("name")
                arguments = data.get("arguments", {})
                result = call_tool(name, arguments)
                self._send_json(result)
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[MCP Server] {args[0]}")


if __name__ == "__main__":
    port = 8765
    server = HTTPServer(("localhost", port), MCPHandler)
    print(f"MCP test server running on http://localhost:{port}")
    print("Endpoints: GET /tools, POST /call-tool, GET /health")
    server.serve_forever()
