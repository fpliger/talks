"""Tier implementations: InBrowserTier, LocalTier, RemoteTier.

Each tier implements:
    async def stream_chat(messages, tools=None) -> AsyncIterator[Delta]

Callers (main.py, agent.py) are tier-agnostic; they only see Delta objects.
"""

import json
import asyncio
from pyscript import fetch, window
from pyodide.ffi import create_proxy, to_js
import js

from config import (
    BROWSER_MODEL_ID,
    LOCAL_API_URL, LOCAL_API_MODEL,
    REMOTE_API_URL, REMOTE_API_KEY,
)
from streaming import Delta, ToolCall, parse_openai_sse
from ui import update_status, update_progress


# =============================================================================
# IN-BROWSER TIER (WebLLM via WebGPU)
# =============================================================================

_browser_engine = None


async def _init_browser_engine():
    global _browser_engine
    if _browser_engine is not None:
        return True

    update_status("loading", "In-browser: Checking prerequisites…")
    try:
        # 1. Must be served over HTTP (not file://) for Cache Storage API to work
        protocol = str(window.location.protocol)
        if protocol == "file:":
            raise Exception("Must be served over http:// — run: python -m http.server 8000")

        # 2. Cache Storage API must be available (secure context check)
        if not getattr(window, "caches", None):
            raise Exception("Cache Storage API unavailable — try Chrome with hardware acceleration enabled (chrome://settings/system)")

        # 3. WebGPU must be available for local inference
        gpu = getattr(window.navigator, "gpu", None)
        if not gpu:
            raise Exception("WebGPU unavailable — enable GPU acceleration in Chrome settings (chrome://settings/system)")

        # 4. Wait for the WebLLM ES module to finish loading
        update_status("loading", "In-browser: Loading model…")
        for _ in range(20):
            if getattr(window, "webllmLoaded", False):
                break
            await asyncio.sleep(0.25)
        else:
            raise Exception("WebLLM module did not load — check browser console")

        webllm = window.webllm

        def on_progress(progress):
            # Extract immediately — progress is a borrowed JS proxy
            try:
                pct = int(float(str(progress.progress)) * 100)
            except Exception:
                pct = 0
            try:
                text = str(progress.text)
            except Exception:
                text = ""
            update_status("loading", f"In-browser: {pct}%")
            update_progress(pct, text)

        on_progress_proxy = create_proxy(on_progress)
        _browser_engine = await webllm.CreateMLCEngine(
            BROWSER_MODEL_ID,
            {"initProgressCallback": on_progress_proxy},
        )
        on_progress_proxy.destroy()
        update_status("ready", "In-browser: Ready")
        update_progress(100, "Model ready")
        return True
    except Exception as e:
        update_status("", f"In-browser: Failed ({e})")
        return False


class InBrowserTier:
    name = "in-browser"

    async def stream_chat(self, messages, tools=None):
        ok = await _init_browser_engine()
        if not ok:
            yield Delta(text="[In-browser model unavailable]", finish_reason="stop")
            return

        try:
            # Pass options as a JS object — Python dict kwargs don't survive
            # the async boundary correctly with some WebLLM builds
            options = to_js({
                "messages": messages,
                "max_tokens": 512,
                "temperature": 0.1,
                "stream": True,
            }, dict_converter=js.Object.fromEntries)

            stream = await _browser_engine.chat.completions.create(options)

            async for chunk in stream:
                # Extract values immediately before yielding — proxies are
                # destroyed by Pyodide at yield/await boundaries
                try:
                    content = str(chunk.choices[0].delta.content or "")
                    finish = str(chunk.choices[0].finish_reason or "")
                except Exception:
                    content = ""
                    finish = ""

                if content:
                    yield Delta(text=content)
                if finish == "stop":
                    yield Delta(finish_reason="stop")
                    return
        except Exception as e:
            yield Delta(text=f"\n[Error: {e}]", finish_reason="stop")


# =============================================================================
# LOCAL TIER (Ollama / LM Studio / llama.cpp — OpenAI-compatible)
# =============================================================================

class LocalTier:
    name = "local"

    async def stream_chat(self, messages, tools=None):
        payload = {
            "model": LOCAL_API_MODEL,
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        try:
            response = await fetch(
                f"{LOCAL_API_URL}/v1/chat/completions",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps(payload),
            )
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            async for delta in parse_openai_sse(response):
                yield delta
        except Exception as e:
            yield Delta(text=f"[Local server error: {e}]", finish_reason="stop")


# =============================================================================
# REMOTE TIER (OpenAI-compatible — real API or mock SSE server)
# =============================================================================

class RemoteTier:
    name = "remote"

    async def stream_chat(self, messages, tools=None):
        payload = {
            "messages": messages,
            "stream": True,
        }
        if tools:
            payload["tools"] = tools

        headers = {"Content-Type": "application/json"}
        if REMOTE_API_KEY:
            headers["Authorization"] = f"Bearer {REMOTE_API_KEY}"

        try:
            response = await fetch(
                f"{REMOTE_API_URL}/v1/chat/completions",
                method="POST",
                headers=headers,
                body=json.dumps(payload),
            )
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            async for delta in parse_openai_sse(response):
                yield delta
        except Exception as e:
            yield Delta(text=f"[Remote API error: {e}]", finish_reason="stop")


# =============================================================================
# FACTORY
# =============================================================================

def get_tier(name: str):
    """Return a tier instance by name: 'in-browser', 'local', 'remote'."""
    return {
        "in-browser": InBrowserTier,
        "local": LocalTier,
        "remote": RemoteTier,
    }[name]()
