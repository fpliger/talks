"""
Model Backends for the Router Demo.

Three tiers:
- browser_generate(): In-browser model via WebLLM (WebGPU)
- local_generate(): Local server model via Ollama/LM Studio
- remote_generate(): Remote API model via OpenAI/Anthropic
"""

import json
import asyncio
from pyscript import fetch, window

from config import (
    USE_MOCK_BROWSER, BROWSER_MODEL_ID,
    USE_MOCK_LOCAL, LOCAL_API_URL, LOCAL_API_MODEL,
    USE_MOCK_REMOTE, REMOTE_API_URL, REMOTE_API_KEY,
)
from ui import update_status


# Global: WebLLM engine instance
_browser_engine = None


# =============================================================================
# IN-BROWSER MODEL (WebLLM via WebGPU)
# =============================================================================

async def init_browser_model():
    """Initialize WebLLM in-browser model.

    Call this once before using browser_generate().
    Downloads model on first use (~700MB for Llama-3.2-1B).
    """
    global _browser_engine

    if USE_MOCK_BROWSER:
        update_status("ready", "Browser: Mock")
        return True

    update_status("loading", "Browser: Loading...")

    try:
        webllm = window.webllm

        def progress_callback(progress):
            pct = int(progress.progress * 100) if hasattr(progress, 'progress') else 0
            update_status("loading", f"Browser: {pct}%")

        _browser_engine = await webllm.CreateMLCEngine(
            BROWSER_MODEL_ID,
            {"initProgressCallback": progress_callback}
        )

        update_status("ready", f"Browser: Ready")
        return True

    except Exception as e:
        print(f"Browser model init failed: {e}")
        update_status("", f"Browser: Failed")
        return False


async def browser_generate(prompt: str) -> str:
    """Generate response using in-browser WebLLM model.

    Args:
        prompt: User prompt string

    Returns:
        Generated response string
    """
    if USE_MOCK_BROWSER:
        await asyncio.sleep(0.3)  # Simulate processing

        # Mock responses for demo
        if "date" in prompt.lower() and "iso" in prompt.lower():
            return "2026-05-05"
        elif "2+2" in prompt or "2 + 2" in prompt:
            return "4"
        else:
            return f"[Browser model response to: {prompt[:50]}...]"

    if _browser_engine is None:
        raise Exception("Browser model not initialized. Call init_browser_model() first.")

    response = await _browser_engine.chat.completions.create({
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.1
    })

    return response.choices[0].message.content


# =============================================================================
# LOCAL SERVER MODEL (Ollama, LM Studio, llama.cpp, etc.)
# =============================================================================

async def local_generate(messages: list, model: str = None) -> tuple:
    """Generate response using local model server.

    Supports OpenAI-compatible APIs (Ollama, LM Studio, vLLM, etc.)

    Args:
        messages: List of message dicts [{"role": "user", "content": "..."}]
        model: Model name (defaults to LOCAL_API_MODEL from config)

    Returns:
        Tuple of (content, tool_calls)
    """
    if USE_MOCK_LOCAL:
        await asyncio.sleep(0.4)
        return "[Local server model response - mock]", []

    model = model or LOCAL_API_MODEL

    try:
        # Try OpenAI-compatible endpoint (works with most local servers)
        response = await fetch(
            f"{LOCAL_API_URL}/v1/chat/completions",
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({
                "model": model,
                "messages": messages,
                "stream": False
            })
        )

        if response.status != 200:
            # Fallback to Ollama-native endpoint
            response = await fetch(
                f"{LOCAL_API_URL}/api/chat",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({
                    "model": model,
                    "messages": messages,
                    "stream": False
                })
            )

        if response.status != 200:
            raise Exception(f"HTTP {response.status}")

        data = await response.json()

        # Handle both OpenAI and Ollama response formats
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
        else:
            content = data["message"]["content"]

        return content, []

    except Exception as e:
        print(f"Local server error: {e}")
        return f"Error connecting to local server: {e}", []


# =============================================================================
# REMOTE API MODEL (OpenAI, Anthropic, etc.)
# =============================================================================

async def remote_generate(messages: list, tools=None) -> tuple:
    """Generate response using remote API.

    Args:
        messages: List of message dicts
        tools: Optional list of tool definitions

    Returns:
        Tuple of (content, tool_calls)
    """
    if USE_MOCK_REMOTE:
        await asyncio.sleep(0.5)
        return "Hello! I'm an AI assistant. This response is from the mock remote server.", []

    post_data = {
        "messages": messages,
        "stream": False
    }

    if tools:
        post_data["tools"] = tools

    headers = {"Content-Type": "application/json"}
    if REMOTE_API_KEY:
        headers["Authorization"] = f"Bearer {REMOTE_API_KEY}"

    try:
        response = await fetch(
            f"{REMOTE_API_URL}/v1/chat/completions",
            method="POST",
            headers=headers,
            body=json.dumps(post_data)
        )

        if response.status != 200:
            raise Exception(f"HTTP {response.status}")

        data = await response.json()
        content = data["choices"][0]["message"]["content"]
        tool_calls = data["choices"][0]["message"].get("tool_calls", [])

        return content, tool_calls

    except Exception as e:
        print(f"Remote API error: {e}")
        return f"Error connecting to remote API: {e}", []
