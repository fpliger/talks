# Router Demo Architecture

## Overview

An AI agent loop running entirely in the browser, driven by Python (PyScript). The agent routes requests to in-browser, local, or remote models, and can call external tools via MCP.

---

## The Four Parts of an Agent

```
┌─────────────────────────────────────────────────────────────────┐
│                         AGENT LOOP                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│   │  MODEL  │───▶│  TOOLS  │───▶│  LOOP   │───▶│ CONTEXT │──┐  │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘  │  │
│        ▲                                                     │  │
│        └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

| Part | General | In This Demo |
|------|---------|--------------|
| **Model** | Decides what to do next | Local SLM (WebLLM) or Remote API |
| **Tools** | Functions the model can call | MCP servers + Python-native (Pandas) |
| **Loop** | Drives execution: ask → run → repeat | PyScript code in browser |
| **Context** | What the model sees each turn | Messages + tool results + DOM state |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 PyScript (Python Runtime)                  │  │
│  │                                                            │  │
│  │   ┌──────────┐     ┌──────────────────────────────────┐   │  │
│  │   │  ROUTER  │────▶│         MODEL GATEWAY            │   │  │
│  │   │ (Python) │     │  ┌────────────┐ ┌─────────────┐  │   │  │
│  │   └──────────┘     │  │   LOCAL    │ │   REMOTE    │  │   │  │
│  │        │           │  │  (WebLLM)  │ │ (API/fetch) │  │   │  │
│  │        │           │  └────────────┘ └─────────────┘  │   │  │
│  │        │           └──────────────────────────────────┘   │  │
│  │        │                                                   │  │
│  │        ▼                                                   │  │
│  │   ┌──────────────────────────────────────────────────┐    │  │
│  │   │                    TOOLS                          │    │  │
│  │   │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │    │  │
│  │   │  │ MCP Client  │  │ Python-Native│  │   DOM    │  │    │  │
│  │   │  │ (HTTP/fetch)│  │  (Pandas)    │  │  Access  │  │    │  │
│  │   │  └─────────────┘  └─────────────┘  └──────────┘  │    │  │
│  │   └──────────────────────────────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │  MCP Server │     │  LLM API    │     │  WebGPU     │
   │  (HTTP)     │     │  (Remote)   │     │  (Local)    │
   └─────────────┘     └─────────────┘     └─────────────┘
```

---

## Routing Flow

```
                    User Prompt
                         │
                         ▼
                  ┌─────────────┐
                  │   ROUTER    │
                  │  (Python)   │
                  └─────────────┘
                         │
           ┌─────────────┼─────────────┐
           │             │             │
           ▼             ▼             ▼
      ┌────────┐   ┌──────────┐   ┌────────┐
      │ LOCAL  │   │  HYBRID  │   │ REMOTE │
      │  Path  │   │   Path   │   │  Path  │
      └────────┘   └──────────┘   └────────┘
           │             │             │
           ▼             ▼             ▼
      Local SLM    Local Data +   Remote Model
      responds     Remote Model   + MCP Tools
                   frames it
```

### Routing Decision Logic

```python
def route_request(prompt: str) -> str:
    # LOCAL: Simple, quick, no external data
    #   "convert", "format", "calculate", "what is"

    # HYBRID: Local processing + remote reasoning
    #   "summarize", "analyze", "csv", "data"

    # REMOTE: Complex queries or tool needs
    #   "search", "find", "save", "look up"
```

---

## Three Demo Paths

### Demo 1: CSV Analysis (in-browser)
```
User: "Analyze sales.csv and write an executive summary"
  │
  ▼
LLM calls analyze_csv tool (Pandas, runs in Pyodide)
  │
  ▼
Tool result: {rows, revenue, top_product, QoQ growth}
  │
  ▼
LLM streams 3-sentence summary
```

### Demo 2: Agent + MCP Tools
```
User: "Find top climate stories and save to notes"
  │
  ▼
LLM calls web_search("climate news")
  │
  ▼
[search results injected into context]
  │
  ▼
LLM calls save_to_file("notes.md", content)
  │   (intercepted — File System Access API writes to user's disk)
  ▼
LLM streams final summary
```

### Demo 3: Folder Agent
```
User picks a local folder (agent.yaml + documents/)
  │
  ▼
JS reads folder via File System Access API
  │
  ▼
Python parses agent.yaml, injects documents into system prompt
  │
  ▼
Agent instantiated — greets user, ready for conversation
```

---

## Component Details

### Router (`router.py`)
- **Purpose**: Decides which execution path based on prompt analysis
- **Implementation**: Pattern matching on keywords
- **Extensible**: Could use a classifier model for smarter routing

### Tier Gateway (`tiers.py`)
- **In-browser**: WebLLM running Qwen2.5-1.5B via WebGPU
- **Local**: `fetch` to `localhost:11434/v1/chat/completions` (Ollama / any OpenAI-compatible)
- **Remote**: same SSE path; uses `REMOTE_API_KEY` if set, falls back to mock SSE server on `:8766`
- **Interface**: all three expose `async def stream_chat(messages, tools) → AsyncIterator[Delta]`

### MCP Client
- **Protocol**: HTTP-based MCP (not the SDK directly)
- **Operations**: `list_tools()`, `call_tool(name, args)`
- **Why HTTP**: MCP SDK uses httpx which doesn't work in Pyodide

### Tool Types
| Type | Example | Runs Where |
|------|---------|------------|
| MCP tools | web_search, save_to_file | External MCP server (HTTP) |
| PyScript-native | analyze_csv (Pandas) | In-browser (Pyodide) |
| FS bridge | save_to_file intercept | Browser File System Access API |

---

## Data Flow Summary

```
┌──────────┐   prompt   ┌──────────┐   route    ┌──────────┐
│   User   │──────────▶│  Router  │──────────▶│  Model   │
└──────────┘           └──────────┘           └──────────┘
                                                    │
                                              tool_call?
                                                    │
                            ┌───────────────────────┴──────┐
                            │ yes                          │ no
                            ▼                              ▼
                      ┌──────────┐                   ┌──────────┐
                      │  Tools   │                   │ Response │
                      └──────────┘                   └──────────┘
                            │                              │
                            │ result                       │
                            ▼                              │
                      ┌──────────┐                         │
                      │  Model   │◀────────────────────────┘
                      │ (again)  │
                      └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │   User   │
                      └──────────┘
```

---

## Key Insight

> **The architecture is the same whether running on a server or in a browser. Only the implementation details change: bundle size, cold start, what each part can talk to.**

This is what makes browser-based agents interesting — same patterns, different constraints, new capabilities (privacy, offline, no infrastructure).
