<!--
  The agentic loop diagram.
  All font sizes use CSS px (fixed screen pixels) so text never
  scales as the SVG stretches to fill the slide.
-->
<script setup lang="ts">
const props = defineProps<{ step?: number }>();
const active = (n: number) => (props.step ?? -1) === n;
</script>

<template>
  <svg viewBox="0 0 720 320" class="loop" preserveAspectRatio="xMidYMid meet">
    <defs>
      <marker id="arrow-mute" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#2a2d36"/>
      </marker>
      <marker id="arrow-lit" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
        <path d="M0,0 L0,6 L8,3 z" fill="#69f0ae"/>
      </marker>
    </defs>

    <!-- Center label -->
    <text x="360" y="152" text-anchor="middle" class="center-label">while not done:</text>
    <text x="360" y="168" text-anchor="middle" class="center-sub">the agent loop</text>

    <!-- Node 1 — Ask the model (top-left) -->
    <g :class="{ node: true, active: active(1) }">
      <rect x="20" y="80" width="180" height="80" rx="10"/>
      <text x="110" y="113" text-anchor="middle" dominant-baseline="middle" class="t-num">①</text>
      <text x="110" y="143" text-anchor="middle" class="t-label">Ask the model</text>
    </g>

    <!-- Node 2 — Run the tool (top-right) -->
    <g :class="{ node: true, active: active(2) }">
      <rect x="520" y="80" width="180" height="80" rx="10"/>
      <text x="610" y="113" text-anchor="middle" dominant-baseline="middle" class="t-num">②</text>
      <text x="610" y="143" text-anchor="middle" class="t-label">Run the tool</text>
    </g>

    <!-- Node 3 — Feed result back (bottom-right) -->
    <g :class="{ node: true, active: active(3) }">
      <rect x="520" y="200" width="180" height="80" rx="10"/>
      <text x="610" y="233" text-anchor="middle" dominant-baseline="middle" class="t-num">③</text>
      <text x="610" y="263" text-anchor="middle" class="t-label">Feed result back</text>
    </g>

    <!-- Node 4 — Done? loop (bottom-left) -->
    <g :class="{ node: true, active: active(4) }">
      <rect x="20" y="200" width="180" height="80" rx="10"/>
      <text x="110" y="233" text-anchor="middle" dominant-baseline="middle" class="t-num">④</text>
      <text x="110" y="263" text-anchor="middle" class="t-label">Done? if not, loop</text>
    </g>

    <!-- Arrows: full loop -->
    <path :class="{ edge: true, lit: active(2) }"
          d="M 200,120 L 520,120" marker-end="url(#arrow-mute)"/>
    <path :class="{ edge: true, lit: active(3) }"
          d="M 610,160 L 610,200" marker-end="url(#arrow-mute)"/>
    <path :class="{ edge: true, lit: active(4) }"
          d="M 520,240 L 200,240" marker-end="url(#arrow-mute)"/>
    <path :class="{ edge: true, lit: active(1) }"
          d="M 120,200 L 120,160" marker-end="url(#arrow-mute)"/>

    <!-- Shortcut: 1 → 4 directly (no tool call) -->
    <path class="edge edge-skip"
          d="M 100,160 Q 55,180 100,200" marker-end="url(#arrow-mute)"/>
    <text x="44" y="183" text-anchor="middle" class="skip-label">no tool</text>
    <text x="44" y="194" text-anchor="middle" class="skip-label">call</text>
  </svg>
</template>

<style scoped>
.loop { width: 100%; height: 100%; max-height: 100%; }

/* CSS px = fixed screen pixels, independent of SVG scale */
.t-num        { font-family: 'JetBrains Mono', monospace; font-size: 28px; font-weight: 700; fill: #6b7280; transition: fill 0.3s; }
.t-label      { font-family: 'JetBrains Mono', monospace; font-size: 13px; fill: #6b7280; transition: fill 0.3s; }
.center-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; fill: #6b7280; letter-spacing: 0.15em; }
.center-sub   { font-family: 'JetBrains Mono', monospace; font-size: 10px; fill: #3a3f52; }

.node rect {
  fill: #161920;
  stroke: #2a2d36;
  stroke-width: 1.5;
  transition: stroke 0.3s, fill 0.3s, filter 0.3s;
}

.node.active rect {
  fill: color-mix(in srgb, #69f0ae 16%, #11131a);
  stroke: #69f0ae;
  filter: drop-shadow(0 0 12px #69f0ae);
}
.node.active .t-num   { fill: #69f0ae; }
.node.active .t-label { fill: #69f0ae; }

.edge {
  fill: none;
  stroke: #2a2d36;
  stroke-width: 2;
  transition: stroke 0.3s;
}
.edge-skip {
  stroke-dasharray: 4 3;
  stroke-width: 1.5;
}
.skip-label { font-family: 'JetBrains Mono', monospace; font-size: 9px; fill: #4a5060; }
.edge.lit {
  stroke: #69f0ae;
  marker-end: url(#arrow-lit);
}
</style>
