# Router Demo Architecture

## Overview

A hybrid AI agent running entirely in the browser, orchestrated by Python (PyScript). The agent routes requests to local or remote models based on task complexity, and can call external tools via MCP.

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

### Demo 1: Local Only
```
User: "Convert this date to ISO format: May 5, 2026"
  │
  ▼
Router: "Simple task" → LOCAL path
  │
  ▼
Local Model (WebLLM/Mock): "2026-05-05"
  │
  ▼
Display with [LOCAL] badge
```

### Demo 2: Hybrid
```
User: "Summarize this CSV"
  │
  ▼
Router: "Data + reasoning" → HYBRID path
  │
  ├──▶ Local: Pandas analyzes data
  │         │
  │         ▼
  │    {rows: 1247, revenue: $2.4M, ...}
  │
  └──▶ Remote: Model frames the analysis
              │
              ▼
         "Executive summary: Revenue grew 12%..."
  │
  ▼
Display with [HYBRID] badge
```

### Demo 3: Remote + Tools
```
User: "Find climate stories and save to notes"
  │
  ▼
Router: "Needs tools" → REMOTE path
  │
  ▼
MCP: List available tools
  │
  ▼
Remote Model: Plans tool calls
  │
  ├──▶ Tool: web_search("climate news")
  │         │
  │         ▼
  │    [search results]
  │
  └──▶ Tool: save_to_file("notes.txt")
              │
              ▼
         [saved]
  │
  ▼
Remote Model: Summarizes results
  │
  ▼
Display with [REMOTE] + [TOOL] badges
```

---

## Component Details

### Router (`router.py`)
- **Purpose**: Decides which execution path based on prompt analysis
- **Implementation**: Pattern matching on keywords
- **Extensible**: Could use a classifier model for smarter routing

### Model Gateway
- **Local**: WebLLM running Llama-3.2-1B via WebGPU
- **Remote**: Any OpenAI-compatible API via fetch
- **Interface**: Both expose `.generate(messages)` → response

### MCP Client
- **Protocol**: HTTP-based MCP (not the SDK directly)
- **Operations**: `list_tools()`, `call_tool(name, args)`
- **Why HTTP**: MCP SDK uses httpx which doesn't work in Pyodide

### Tool Types
| Type | Example | Runs Where |
|------|---------|------------|
| MCP Tools | web_search, save_file | External server |
| Python-native | Pandas analysis | In browser (Pyodide) |
| DOM Tools | Read page content | Browser APIs |

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
