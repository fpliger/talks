<!--
  Agent flow diagram.
  Shows: User → AGENT box (Prepare Context, Call LLM, Tool Call Requests? diamond,
  Call Tool(s), Add Tool Results loop) → LLM box (outside right) → Output.
  All font sizes in CSS px so they scale-independent of the SVG viewport.
-->
<template>
  <svg viewBox="0 0 660 596" class="agent-diagram" preserveAspectRatio="xMidYMid meet">
    <defs>
      <marker id="ag-arrow-muted" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#6b7280"/>
      </marker>
      <marker id="ag-arrow-orange" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#ffab40"/>
      </marker>
    </defs>

    <!-- ── AGENT dashed box ───────────────────────────────── -->
    <rect x="14" y="98" width="412" height="436" rx="14"
          fill="color-mix(in srgb, #ffab40 6%, #11131a)"
          stroke="#ffab40" stroke-width="1.8" stroke-dasharray="7 4"/>
    <text x="28" y="118" class="agent-title">AGENT</text>

    <!-- ── LLM outer box (green, outside right) ──────────── -->
    <rect x="462" y="188" width="174" height="128" rx="12"
          fill="color-mix(in srgb, #69f0ae 10%, #11131a)"
          stroke="#69f0ae" stroke-width="2"/>
    <text x="476" y="208" class="llm-title">LLM</text>

    <!-- LLM inner: Do Magic! -->
    <rect x="476" y="212" width="146" height="38" rx="8"
          fill="color-mix(in srgb, #69f0ae 18%, #11131a)"
          stroke="#69f0ae" stroke-width="1.5"/>
    <text x="549" y="231" text-anchor="middle" dominant-baseline="middle" class="inner-label">Do Magic!</text>

    <!-- LLM inner: Generate Response -->
    <rect x="476" y="258" width="146" height="52" rx="8"
          fill="color-mix(in srgb, #69f0ae 18%, #11131a)"
          stroke="#69f0ae" stroke-width="1.5"/>
    <text x="549" y="276" text-anchor="middle" dominant-baseline="middle" class="inner-label">Generate Response</text>
    <text x="549" y="292" text-anchor="middle" dominant-baseline="middle" class="inner-sublabel">0 or more Tool Call Requests</text>

    <!-- ── User pill (blue) ───────────────────────────────── -->
    <rect x="170" y="8" width="140" height="44" rx="22"
          fill="color-mix(in srgb, #448aff 14%, #11131a)"
          stroke="#448aff" stroke-width="2"/>
    <text x="240" y="30" text-anchor="middle" dominant-baseline="middle" class="pill-label">User</text>

    <!-- ── Prepare Context (orange) ──────────────────────── -->
    <rect x="150" y="110" width="180" height="44" rx="10"
          fill="color-mix(in srgb, #ffab40 16%, #11131a)"
          stroke="#ffab40" stroke-width="2"/>
    <text x="240" y="132" text-anchor="middle" dominant-baseline="middle" class="node-label-orange">Prepare Context</text>

    <!-- ── Call LLM (orange) ──────────────────────────────── -->
    <rect x="162" y="192" width="156" height="44" rx="10"
          fill="color-mix(in srgb, #ffab40 16%, #11131a)"
          stroke="#ffab40" stroke-width="2"/>
    <text x="240" y="214" text-anchor="middle" dominant-baseline="middle" class="node-label-orange">Call LLM</text>

    <!-- ── Diamond: Tool Call Requests? ──────────────────── -->
    <polygon points="240,278 304,314 240,350 176,314"
             fill="color-mix(in srgb, #ffab40 12%, #11131a)"
             stroke="#ffab40" stroke-width="2"/>
    <text x="240" y="308" text-anchor="middle" dominant-baseline="middle" class="diamond-label">Tool Call</text>
    <text x="240" y="324" text-anchor="middle" dominant-baseline="middle" class="diamond-label">Requests?</text>

    <!-- ── Call Tool(s) (orange) ─────────────────────────── -->
    <rect x="162" y="376" width="156" height="44" rx="10"
          fill="color-mix(in srgb, #ffab40 16%, #11131a)"
          stroke="#ffab40" stroke-width="2"/>
    <text x="240" y="398" text-anchor="middle" dominant-baseline="middle" class="node-label-orange">Call Tool(s)</text>

    <!-- ── Add Tool Result(s) to Context (orange) ────────── -->
    <rect x="128" y="448" width="224" height="44" rx="10"
          fill="color-mix(in srgb, #ffab40 16%, #11131a)"
          stroke="#ffab40" stroke-width="2"/>
    <text x="240" y="470" text-anchor="middle" dominant-baseline="middle" class="node-label-orange">Add Tool Result(s) to Context</text>

    <!-- ── Output pill (blue) ────────────────────────────── -->
    <rect x="170" y="546" width="140" height="44" rx="22"
          fill="color-mix(in srgb, #448aff 14%, #11131a)"
          stroke="#448aff" stroke-width="2"/>
    <text x="240" y="568" text-anchor="middle" dominant-baseline="middle" class="pill-label">Output</text>

    <!-- ── ARROWS ─────────────────────────────────────────── -->

    <!-- User → Prepare Context -->
    <line x1="240" y1="52" x2="240" y2="110" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="256" y="84" class="edge-label">Messages</text>

    <!-- System Prompt → Prepare Context -->
    <line x1="14" y1="132" x2="150" y2="132" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="80" y="125" text-anchor="middle" class="edge-label">System Prompt</text>

    <!-- Tools → Prepare Context -->
    <line x1="426" y1="132" x2="330" y2="132" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="428" y="125" class="edge-label">Tools</text>

    <!-- Prepare Context → Call LLM -->
    <line x1="240" y1="154" x2="240" y2="192" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>

    <!-- Call LLM → LLM (Context) -->
    <line x1="318" y1="214" x2="462" y2="214" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="390" y="207" text-anchor="middle" class="edge-label">Context</text>

    <!-- LLM → merge point below Call LLM (Response) -->
    <line x1="462" y1="264" x2="240" y2="264" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="351" y="257" text-anchor="middle" class="edge-label">Response</text>

    <!-- Merge point → Diamond top -->
    <line x1="240" y1="264" x2="240" y2="278" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>

    <!-- Diamond Yes → Call Tool(s) -->
    <line x1="240" y1="350" x2="240" y2="376" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="248" y="367" class="edge-label edge-label-green">Yes</text>

    <!-- Call Tool(s) → Add Tool Results -->
    <line x1="240" y1="420" x2="240" y2="448" class="edge-muted" marker-end="url(#ag-arrow-muted)"/>

    <!-- Loop back: Add Tool Results → Call LLM (orange) -->
    <path d="M 128,470 L 56,470 L 56,214 L 162,214"
          class="edge-orange" marker-end="url(#ag-arrow-orange)"/>

    <!-- Diamond No → Output (exits AGENT box right side) -->
    <path d="M 304,314 L 448,314 L 448,568 L 310,568"
          class="edge-muted" marker-end="url(#ag-arrow-muted)"/>
    <text x="320" y="307" class="edge-label edge-label-green">No</text>

  </svg>
</template>

<style scoped>
.agent-diagram { width: 100%; height: 100%; max-height: 100%; }

/* Text styles — all CSS px, never SVG user units */
.agent-title       { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; fill: #ffab40; letter-spacing: 0.12em; }
.llm-title         { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 700; fill: #69f0ae; }
.pill-label        { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; fill: #448aff; }
.node-label-orange { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; fill: #ffab40; }
.inner-label       { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; fill: #69f0ae; }
.inner-sublabel    { font-family: 'JetBrains Mono', monospace; font-size: 9px;  fill: color-mix(in srgb, #69f0ae 60%, #6b7280); }
.diamond-label     { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; fill: #ffab40; }
.edge-label        { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #6b7280; }
.edge-label-green  { fill: #69f0ae; }

/* Edges */
.edge-muted  { fill: none; stroke: #6b7280; stroke-width: 1.8; }
.edge-orange { fill: none; stroke: #ffab40; stroke-width: 2; }
</style>
