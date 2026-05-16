"""MCP HTTP server for the router demo.

Tools exposed:
  web_search(query, k=3)         — returns k climate news story objects
  save_to_file(filename, content) — writes to ./notes/ (server-side fallback;
                                    browser uses File System Access API first)

Run with: python server.py
Endpoints: GET /tools, POST /call-tool, GET /health
"""

import json
import os
from datetime import date
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

NOTES_DIR = Path(__file__).parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)

# Plausible climate stories used by web_search mock
_CLIMATE_STORIES = [
    {
        "title": "Global Carbon Emissions Decline for First Time in a Decade",
        "url": "https://example-news.org/climate/carbon-decline-2026",
        "summary": (
            "A new IEA report shows global CO₂ emissions fell 0.4% in 2025, "
            "driven by record renewable capacity additions and EV adoption."
        ),
    },
    {
        "title": "EU Green Deal Reaches 50% Renewable Energy Milestone",
        "url": "https://example-news.org/climate/eu-renewables-milestone",
        "summary": (
            "The European Union announced that 50.2% of its electricity came "
            "from renewable sources in Q1 2026 — three years ahead of schedule."
        ),
    },
    {
        "title": "Ocean Cleanup Project Reports 30% Reduction in Pacific Plastic Patch",
        "url": "https://example-news.org/climate/ocean-cleanup-2026",
        "summary": (
            "The Ocean Cleanup nonprofit confirmed its System 03 has removed "
            "over 400,000 kg of plastic, shrinking the Great Pacific Garbage Patch "
            "by an estimated 30% since 2021."
        ),
    },
    {
        "title": "Arctic Sea Ice Extent Records Largest Recovery in 15 Years",
        "url": "https://example-news.org/climate/arctic-ice-recovery",
        "summary": (
            "NSIDC data shows Arctic summer sea ice extent in 2025 was 6% larger "
            "than the previous year — the biggest single-year recovery since 2010."
        ),
    },
    {
        "title": "India Surpasses 500 GW Renewable Capacity Target Two Years Early",
        "url": "https://example-news.org/climate/india-renewables-500gw",
        "summary": (
            "India reached 502 GW of installed renewable energy capacity in March 2026, "
            "making it the third-largest renewable producer globally."
        ),
    },
]


TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for recent news stories on a topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string",
                },
                "k": {
                    "type": "integer",
                    "description": "Number of results to return (default 3)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_to_file",
        "description": "Save text content to a file.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "Name of the file to create or overwrite",
                },
                "content": {
                    "type": "string",
                    "description": "Text content to write",
                },
            },
            "required": ["filename", "content"],
        },
    },
]


def _call_web_search(arguments: dict) -> dict:
    k = min(int(arguments.get("k", 3)), len(_CLIMATE_STORIES))
    stories = _CLIMATE_STORIES[:k]
    lines = []
    for i, s in enumerate(stories, 1):
        lines.append(f"{i}. **{s['title']}**\n   {s['url']}\n   {s['summary']}")
    text = "\n\n".join(lines)
    return {"content": [{"type": "text", "text": text}]}


def _call_save_to_file(arguments: dict) -> dict:
    filename = arguments.get("filename", f"notes_{date.today()}.md")
    content = arguments.get("content", "")
    # Sanitize filename
    safe_name = Path(filename).name
    path = NOTES_DIR / safe_name
    path.write_text(content, encoding="utf-8")
    return {"content": [{"type": "text", "text": f"Saved to {path}"}]}


def call_tool(name: str, arguments: dict) -> dict:
    if name == "web_search":
        return _call_web_search(arguments)
    if name == "save_to_file":
        return _call_save_to_file(arguments)
    return {
        "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        "isError": True,
    }


class MCPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

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
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                result = call_tool(data.get("name"), data.get("arguments", {}))
                self._send_json(result)
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON"}, 400)
        else:
            self._send_json({"error": "Not found"}, 404)

    def log_message(self, fmt, *args):
        print(f"[MCP] {args[0]}")


if __name__ == "__main__":
    port = 8765
    server = HTTPServer(("localhost", port), MCPHandler)
    print(f"MCP server on http://localhost:{port}")
    print(f"Notes directory: {NOTES_DIR}")
    print("Endpoints: GET /tools  POST /call-tool  GET /health")
    server.serve_forever()
