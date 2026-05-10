"""Configuration for the Router Demo.

DEMO_DEFAULTS sets the pre-selected tier for each demo button.
Switch tiers live using the selector in the UI.
Set REMOTE_API_KEY (or env var REMOTE_API_KEY) to use a real frontier API;
otherwise the demo falls back to the local mock SSE server.
"""

import os

# =============================================================================
# DEMO DEFAULTS — which tier each demo button pre-selects
# =============================================================================
# "in-browser" | "local" | "remote"
DEMO_DEFAULTS = {1: "in-browser", 2: "remote", 3: "remote"}

# =============================================================================
# IN-BROWSER MODEL (WebLLM via WebGPU)
# =============================================================================
BROWSER_MODEL_ID = "Llama-3.2-1B-Instruct-q4f32_1-MLC"

# =============================================================================
# LOCAL SERVER (Ollama / LM Studio / llama.cpp — OpenAI-compatible)
# =============================================================================
LOCAL_API_URL = os.environ.get("LOCAL_API_URL", "http://localhost:11434")
LOCAL_API_MODEL = os.environ.get("LOCAL_API_MODEL", "llama3.2")

# =============================================================================
# REMOTE API (real frontier model, or mock SSE server on :8766)
# =============================================================================
REMOTE_API_URL   = os.environ.get("REMOTE_API_URL",   "http://localhost:8766")
REMOTE_API_KEY   = os.environ.get("REMOTE_API_KEY",   "")
REMOTE_API_MODEL = os.environ.get("REMOTE_API_MODEL", "claude-sonnet-4-6")

# =============================================================================
# MCP TOOLS SERVER
# =============================================================================
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8765")
