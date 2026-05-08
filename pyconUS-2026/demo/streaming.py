"""SSE stream reader and Delta normalization.

Reads response.body via JS getReader(), decodes tokens, and yields
normalized Delta objects for any OpenAI-compatible SSE endpoint.
"""

import json
from dataclasses import dataclass, field
from pyscript import window


@dataclass
class ToolCall:
    id: str
    name: str
    args: dict = field(default_factory=dict)


@dataclass
class Delta:
    text: str | None = None
    tool_call: ToolCall | None = None
    finish_reason: str | None = None


async def read_sse_stream(response):
    """Read an SSE response stream and yield raw line strings."""
    decoder = window.TextDecoder.new()
    reader = response.body.getReader()
    buffer = ""

    while True:
        result = await reader.read()
        if result.done:
            break
        try:
            text = decoder.decode(result.value)
            buffer += text
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if line:
                    yield line
        except Exception:
            pass

    if buffer.strip():
        yield buffer.strip()


async def parse_openai_sse(response):
    """Parse an OpenAI-compatible SSE stream into Delta objects.

    Handles both text tokens and tool_calls (accumulated across chunks).
    """
    # Accumulate tool call fragments keyed by index
    pending_tool_calls: dict[int, dict] = {}

    async for line in read_sse_stream(response):
        if not line.startswith("data:"):
            continue

        data = line[5:].strip()
        if data == "[DONE]":
            break

        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            continue

        choice = chunk.get("choices", [{}])[0]
        finish_reason = choice.get("finish_reason")
        delta = choice.get("delta", {})

        # Text token
        content = delta.get("content")
        if content:
            yield Delta(text=content)

        # Tool call fragments
        for tc_chunk in delta.get("tool_calls", []):
            idx = tc_chunk.get("index", 0)
            if idx not in pending_tool_calls:
                pending_tool_calls[idx] = {
                    "id": tc_chunk.get("id", f"call_{idx}"),
                    "name": "",
                    "arguments": "",
                }
            fn = tc_chunk.get("function", {})
            if fn.get("name"):
                pending_tool_calls[idx]["name"] += fn["name"]
            if fn.get("arguments"):
                pending_tool_calls[idx]["arguments"] += fn["arguments"]

        if finish_reason == "tool_calls":
            for tc in pending_tool_calls.values():
                try:
                    args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    args = {"raw": tc["arguments"]}
                yield Delta(tool_call=ToolCall(id=tc["id"], name=tc["name"], args=args))
            yield Delta(finish_reason="tool_calls")
            return

        if finish_reason == "stop":
            yield Delta(finish_reason="stop")
            return
