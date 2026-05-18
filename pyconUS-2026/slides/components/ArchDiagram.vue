<!--
  Architecture diagram. Mirrors the demo's arch panel:
  PyScript orchestrator at center, three boxes below
  (LLM / Pyodide tool / MCP tools), context arc.

  Optional `litNode` prop: 'orchestrator' | 'llm' | 'pyodide' | 'mcp' | 'user'
-->
<script setup lang="ts">
const props = defineProps<{ litNode?: string; litEdge?: string }>();
const isLit = (n: string) => props.litNode === n;
const isLitEdge = (e: string) => props.litEdge === e;
</script>

<template>
  <svg viewBox="0 0 600 360" class="arch">
    <defs>
      <marker id="arch-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#2a2d36"/>
      </marker>
    </defs>

    <!-- User -->
    <g :class="{ node: true, user: true, lit: isLit('user') }">
      <rect x="240" y="10" width="120" height="44" rx="8"/>
      <text x="300" y="32" text-anchor="middle">User</text>
      <text x="300" y="46" text-anchor="middle" class="sub">prompt</text>
    </g>

    <!-- arrow user → orchestrator -->
    <line :class="{ edge: true, lit: isLitEdge('user-orch') }"
          x1="300" y1="54" x2="300" y2="100"
          marker-end="url(#arch-arrow)"/>

    <!-- Orchestrator -->
    <g :class="{ node: true, orch: true, lit: isLit('orchestrator') }">
      <rect x="160" y="100" width="280" height="64" rx="10"/>
      <text x="300" y="128" text-anchor="middle" class="big">Orchestrator</text>
      <text x="300" y="148" text-anchor="middle" class="sub">PyScript · agent loop · in your tab</text>
    </g>

    <!-- arrows out -->
    <line :class="{ edge: true, lit: isLitEdge('orch-llm') }"
          x1="220" y1="164" x2="100" y2="220" marker-end="url(#arch-arrow)"/>
    <line :class="{ edge: true, lit: isLitEdge('orch-pyodide') }"
          x1="300" y1="164" x2="300" y2="220" marker-end="url(#arch-arrow)"/>
    <line :class="{ edge: true, lit: isLitEdge('orch-mcp') }"
          x1="380" y1="164" x2="500" y2="220" marker-end="url(#arch-arrow)"/>

    <!-- LLM -->
    <g :class="{ node: true, llm: true, lit: isLit('llm') }">
      <rect x="20" y="220" width="170" height="68" rx="10"/>
      <text x="105" y="250" text-anchor="middle" class="big">LLM</text>
      <text x="105" y="270" text-anchor="middle" class="sub">in-browser · local · remote</text>
    </g>

    <!-- Pyodide tools -->
    <g :class="{ node: true, py: true, lit: isLit('pyodide') }">
      <rect x="215" y="220" width="170" height="68" rx="10"/>
      <text x="300" y="250" text-anchor="middle" class="big">Pyodide tools</text>
      <text x="300" y="270" text-anchor="middle" class="sub">analyze_csv · pandas</text>
    </g>

    <!-- MCP tools -->
    <g :class="{ node: true, mcp: true, lit: isLit('mcp') }">
      <rect x="410" y="220" width="170" height="68" rx="10"/>
      <text x="495" y="250" text-anchor="middle" class="big">MCP tools</text>
      <text x="495" y="270" text-anchor="middle" class="sub">web_search · save_to_file</text>
    </g>

    <!-- context arc -->
    <path d="M 105,288 Q 105,330 300,335 Q 495,330 495,288"
          fill="none" stroke="#2a2d36" stroke-dasharray="3,3" opacity="0.5"/>
    <rect x="200" y="328" width="200" height="22" rx="6"
          fill="#11131a" stroke="#2a2d36"/>
    <text x="300" y="343" text-anchor="middle" class="ctx">
      context window — messages[]
    </text>
  </svg>
</template>

<style scoped>
.arch { width: 100%; height: auto; max-height: 70vh; }

.node rect {
  fill: #11131a;
  stroke: #2a2d36;
  stroke-width: 1.5;
  transition: stroke 0.3s, fill 0.3s, filter 0.3s;
}
.node text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  fill: #6b7280;
  transition: fill 0.3s;
}
.node .big { font-size: 14px; font-weight: 600; }
.node .sub { font-size: 10px; fill: #4a5060; }

.node.user.lit rect    { stroke: #b3c8ff; filter: drop-shadow(0 0 8px #b3c8ff); fill: color-mix(in srgb, #b3c8ff 14%, #11131a); }
.node.user.lit text    { fill: #b3c8ff; }

.node.orch.lit rect    { stroke: #69f0ae; filter: drop-shadow(0 0 10px #69f0ae); fill: color-mix(in srgb, #69f0ae 14%, #11131a); }
.node.orch.lit text    { fill: #69f0ae; }

.node.llm.lit rect     { stroke: #448aff; filter: drop-shadow(0 0 10px #448aff); fill: color-mix(in srgb, #448aff 14%, #11131a); }
.node.llm.lit text     { fill: #448aff; }

.node.py.lit rect      { stroke: #a78bfa; filter: drop-shadow(0 0 10px #a78bfa); fill: color-mix(in srgb, #a78bfa 14%, #11131a); }
.node.py.lit text      { fill: #a78bfa; }

.node.mcp.lit rect     { stroke: #ffab40; filter: drop-shadow(0 0 10px #ffab40); fill: color-mix(in srgb, #ffab40 14%, #11131a); }
.node.mcp.lit text     { fill: #ffab40; }

.edge {
  stroke: #2a2d36;
  stroke-width: 1.5;
  fill: none;
  transition: stroke 0.3s;
}
.edge.lit {
  stroke: #69f0ae;
  stroke-width: 2;
}

.ctx {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  fill: #4a5060;
}
</style>
