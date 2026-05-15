<!--
  Simple LLM flow diagram: User → LLM → Output.
  All font sizes in CSS px so they don't scale with the SVG.
  Style mirrors the dark palette used in LoopDiagram.vue.
-->
<template>
  <svg viewBox="0 0 360 420" class="llm-diagram" preserveAspectRatio="xMidYMid meet">
    <defs>
      <marker id="llm-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#6b7280"/>
      </marker>
    </defs>

    <!-- User pill -->
    <g class="node user">
      <rect x="90" y="16" width="180" height="48" rx="24"/>
      <text x="180" y="40" text-anchor="middle" dominant-baseline="middle" class="pill-label">User</text>
    </g>

    <!-- Arrow: User → LLM, with "Messages" edge label -->
    <line class="edge" x1="180" y1="64" x2="180" y2="112" marker-end="url(#llm-arrow)"/>
    <text x="196" y="91" class="edge-label">Messages</text>

    <!-- LLM outer box -->
    <g class="node llm-outer">
      <rect x="24" y="118" width="312" height="172" rx="14"/>
      <text x="44" y="142" class="box-title">LLM</text>

      <!-- Inner box 1: Do Magic! -->
      <g class="node llm-inner">
        <rect x="48" y="150" width="264" height="50" rx="10"/>
        <text x="180" y="175" text-anchor="middle" dominant-baseline="middle" class="inner-label">Do Magic!</text>
      </g>

      <!-- Inner box 2: Generate Response -->
      <g class="node llm-inner">
        <rect x="48" y="212" width="264" height="50" rx="10"/>
        <text x="180" y="237" text-anchor="middle" dominant-baseline="middle" class="inner-label">Generate Response</text>
      </g>
    </g>

    <!-- Arrow: LLM → Output, with "Response" edge label -->
    <line class="edge" x1="180" y1="290" x2="180" y2="342" marker-end="url(#llm-arrow)"/>
    <text x="196" y="319" class="edge-label">Response</text>

    <!-- Output pill -->
    <g class="node output">
      <rect x="90" y="348" width="180" height="48" rx="24"/>
      <text x="180" y="372" text-anchor="middle" dominant-baseline="middle" class="pill-label">Output</text>
    </g>
  </svg>
</template>

<style scoped>
.llm-diagram { width: 100%; height: 100%; max-height: 100%; }

/* User / Output pills — blue */
.node.user rect,
.node.output rect {
  fill: color-mix(in srgb, #448aff 14%, #11131a);
  stroke: #448aff;
  stroke-width: 2;
}
.pill-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 18px;
  font-weight: 700;
  fill: #448aff;
}

/* LLM outer box — green */
.node.llm-outer rect {
  fill: color-mix(in srgb, #69f0ae 10%, #11131a);
  stroke: #69f0ae;
  stroke-width: 2;
}
.box-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 700;
  fill: #69f0ae;
}

/* LLM inner boxes — slightly lighter green */
.node.llm-inner rect {
  fill: color-mix(in srgb, #69f0ae 18%, #11131a);
  stroke: #69f0ae;
  stroke-width: 1.5;
}
.inner-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  font-weight: 600;
  fill: #69f0ae;
}

/* Arrows and edge labels */
.edge {
  stroke: #6b7280;
  stroke-width: 2;
}
.edge-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  fill: #6b7280;
}
</style>
