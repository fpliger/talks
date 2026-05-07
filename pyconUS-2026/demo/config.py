"""
Configuration for the Router Demo.

Toggle USE_MOCK_* to switch between mock and real backends.
"""

# =============================================================================
# MODEL BACKENDS
# =============================================================================

# In-browser model (WebLLM via WebGPU)
USE_MOCK_BROWSER = True
BROWSER_MODEL_ID = "Llama-3.2-1B-Instruct-q4f32_1-MLC"

# Local server model (Ollama, LM Studio, llama.cpp, etc.)
USE_MOCK_LOCAL = True
LOCAL_API_URL = "http://localhost:11434"
LOCAL_API_MODEL = "llama3.2"

# Remote API model (OpenAI, Anthropic, etc.)
USE_MOCK_REMOTE = True
REMOTE_API_URL = "http://localhost:8766"  # Mock server for demo
REMOTE_API_KEY = ""  # Set for real APIs (e.g., "sk-...")

# =============================================================================
# MCP TOOLS
# =============================================================================

MCP_SERVER_URL = "http://localhost:8765"

# =============================================================================
# For the talk: Show this file first to explain the architecture
# =============================================================================
