"""Load an agent definition from a local folder via File System Access API.

Expected folder structure:
  agent.yaml          — name, description, system_prompt, ai config, documents list
  documents/          — optional reference documents (text files)
  tools/mcp.json      — optional MCP server config (informational)

Returns a parsed config dict ready for use in run_demo_3.
"""

import json
import yaml
from pyscript import window
from ui import agent_log, add_message


async def load_agent_from_folder() -> dict | None:
    """Prompt the user to pick an agent folder, parse agent.yaml, return config.

    Returns a dict with keys:
      name, description, system_prompt, ai (dict), documents (dict filename→text),
      _mcp_config (dict, informational only)
    Returns None if the user cancelled or the folder is invalid.
    """
    if not hasattr(window, "showDirectoryPicker"):
        add_message(
            "⚠️ File System Access API is not available in this browser. "
            "Use Chrome or Edge to load agent folders.",
            role="system",
        )
        return None

    try:
        dir_handle = await window.showDirectoryPicker()
    except Exception:
        # User cancelled the picker — not an error
        return None

    agent_log("info", "agent folder selected — reading contents…")

    try:
        result = await window.readAgentFolder(dir_handle)
    except Exception as e:
        agent_log("error", f"readAgentFolder failed: {e}")
        add_message(f"⚠️ Could not read agent folder: {e}", role="system")
        return None

    yaml_text = result.yaml
    if not yaml_text:
        err = getattr(result, "error", "agent.yaml not found in selected folder")
        agent_log("error", f"no agent.yaml: {err}")
        add_message(f"⚠️ {err}", role="system")
        return None

    try:
        config = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        agent_log("error", f"YAML parse error: {e}")
        add_message(f"⚠️ Invalid agent.yaml: {e}", role="system")
        return None

    # documents comes back as JSON string (serialized on the JS side)
    try:
        docs_json = result.documentsJson
        config["documents"] = json.loads(docs_json) if docs_json else {}
    except Exception:
        config["documents"] = {}

    # mcp config — informational only
    try:
        mcp_json = result.mcpJson
        config["_mcp_config"] = json.loads(mcp_json) if mcp_json else {}
    except Exception:
        config["_mcp_config"] = {}

    name   = config.get("name", "Agent")
    n_docs = len(config["documents"])
    agent_log("info", f"loaded agent '{name}' — {n_docs} document(s) found")

    return config
