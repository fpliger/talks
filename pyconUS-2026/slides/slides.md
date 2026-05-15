---
# ─────────────────────────────────────────────────────────────
# PyCon US 2026 — Distributing AI with Python in the Browser
# Talk format: 25 + 5 (Q&A)  ·  AI track  ·  Long Beach
# Built with Slidev (https://sli.dev)
#
# Run:    npm install && npm run dev
# Export: npm run export-pdf
# ─────────────────────────────────────────────────────────────
theme: default
title: Distributing AI with Python in the Browser
info: |
  PyCon US 2026 — AI track.
  Edge inference and flexibility without infrastructure.
class: text-center
highlighter: shiki
lineNumbers: false
drawings:
  persist: false
mdc: true
fonts:
  sans: 'Inter'
  mono: 'JetBrains Mono'
colorSchema: dark
download: true
exportFilename: pyconus-2026-distributing-ai
---

<style>
@import './style.css';
</style>

<div class="absolute inset-0 flex flex-col items-center justify-center" style="background: var(--bg);">
<div class="section-eyebrow" style="margin-bottom: 2rem;">PyCon US 2026</div>
<h1 style="font-size: 3.4rem; line-height: 1.1; max-width: 22ch; letter-spacing: -0.03em; font-weight: 700;">
Distributing AI<br/>
with <span style="background: linear-gradient(90deg, var(--browser), var(--local)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Python in the Browser</span>
</h1>
<p style="color: var(--muted); font-size: 1.15rem; margin-top: 1.5rem; max-width: 36rem; text-align: center;"><s>inference</s> agents &amp; flexibility, everywhere.</p>
<p class="mono" style="color: var(--muted); margin-top: 4rem; font-size: 0.85rem; letter-spacing: 0.1em;">Fabio Pliger · Anaconda · @b_smoke</p>
</div>

<!--
SLIDE 1 — TITLE.   00:00–00:10.

Don't read the slide. The demo is already streaming on the projector
behind you (Demo 1, in-browser tier). Let the audience clock the green
WebGPU dot. Speak after the room settles.

You may have already opened Demo 3 in step mode behind the deck, with
WebLLM pre-warmed on tab #2 and the SSE/MCP servers green.
-->

---
title: Thesis
layout: center
class: text-center
---

<div class="big-thesis">
Sorry in advance...<br/>
We'll talk about<br/>
<span class="accent">agents</span>
not models
</div>

<div style="margin-top: 3rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; letter-spacing: 0.04em;">
It's 2026, agents are the new cool :)
</div>

<div class="timing">00:30 · t+00:30</div>

<!--
SLIDE 2 — THESIS.  00:10–01:00.  ~50s.

The single sentence the audience should be able to repeat. Say it out
loud, slowly. Let the second line land separately ("…and in 2026 —
this is new — that loop can live in a browser tab.")

Anchor: this slide is a callback you'll return to in the closing CTA.
Don't elaborate. Move on.
-->

---
title: Speaker intro
layout: center
---

<div style="display: grid; grid-template-columns: 1.2fr 1fr; gap: 4rem; align-items: center;">
<div>
<div class="section-eyebrow">Who am I</div>
<h2 style="font-size: 2.2rem; margin-bottom: 1rem;">Fabio Pliger</h2>
<p style="font-size: 1.05rem; color: var(--text); line-height: 1.6; max-width: 32ch;">Engineer <strong style="color: #fff;">Anaconda</strong> - R&D Team. Creator of <strong style="color: var(--browser);">PyScript</strong> and long time Pythonista.</p>
<p style="font-size: 0.95rem; color: var(--muted); margin-top: 1.2rem; line-height: 1.5; max-width: 36ch;"></p>
</div>
<div style="display: flex; flex-direction: column; gap: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--muted);">
<div>github.com/fpliger</div>
<div>x &middot; @b_smoke</div>
<div>anaconda.com</div>
<div>pyscript.net</div>
</div>
</div>

<div class="timing">00:45 · t+01:15</div>

<!--
SLIDE 3 — SPEAKER INTRO.  01:00–01:45.  ~45s.

Affiliation goes here, not on slide 1. Why: the demo will earn the
credibility before you cash it in. Disclose, don't sell.

Last sentence is the disarmer — you're showing patterns, not pitching
products. People relax. Move on briskly.
-->

---
title: M1 — What is an agent?
layout: center
class: text-center
---

<!-- <div style="font-family: 'JetBrains Mono', monospace; color: var(--muted); font-size: 0.85rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 2rem;">Movement 1 of 4</div> -->

<div style="font-size: 2.8rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; max-width: 22ch; margin: 0 auto;">
What <em style="color: var(--browser); font-style: normal;">is</em><br/>
an agent?
</div>

<div style="margin-top: 2.5rem; color: var(--muted); font-size: 1rem;">4 parts &middot; 1 loop</div>

<div class="timing">00:15 · t+02:00</div>

<!--
SLIDE 4 — SECTION HEADER: ANATOMY.  01:45–02:00.  ~15s.

Quick beat. Set up the section. Skip if running long; it's a breath.
-->

---
title: Anatomy — four parts
---

<div class="section-eyebrow">Anatomy of an agent</div>
<h2 style="font-size: 2.4rem; margin-bottom: 1.5rem;">Four parts.</h2>

<div class="anatomy">
<div></div>
<div class="col-head">Model</div>
<div class="col-head">Tools</div>
<div class="col-head">Context</div>
<div class="col-head">Loop</div>
<div class="row-label">In general</div>
<div class="cell model">
<div class="label">decides</div>
<div class="desc">The "brain" thing that picks <em>what to do next</em>. An LLM, mostly.</div>
</div>
<div class="cell tools">
<div class="label">acts</div>
<div class="desc">Added functionality the model is allowed to call. APIs (MCPs), scripts, services.</div>
</div>
<div class="cell context">
<div class="label">remembers</div>
<div class="desc">What (custom information) the model sees on each turn. Instructions, history, results.</div>
</div>
<div class="cell loop">
<div class="label">drives</div>
<div class="desc">Ask &middot; act &middot; observe &middot; repeat. The runtime.</div>
</div>
</div>

<div class="timing">01:45 · t+03:45</div>

<!--
SLIDE 5 — ANATOMY.  02:00–03:45.  ~1m45s.

The teaching beat of the talk. Spend time here. Walk it left to right,
top to bottom.

  "Every agent is four things. A model that decides. Tools that act.
   A loop that drives. And context — what the model sees.
   That's it. Now look at row two — same four things. Different details.
   The model is wherever it runs fastest. The tools are HTTP and the DOM.
   The loop is Python, in the user's tab. The context is messages[].
   The architecture doesn't change in the browser. Only where the parts
   live."

Watch the time. This is the slide that wants to eat 30 extra seconds
because you love it. Don't.
-->

---
title: Anatomy (Continued) — four parts
---

<div class="section-eyebrow">Anatomy of an agent (continued)</div>
<h2 style="font-size: 2.4rem; margin-bottom: 1.5rem;">Four parts.</h2>

<div class="anatomy">
<div></div>
<div class="col-head">Model</div>
<div class="col-head">Tools</div>
<div class="col-head">Context</div>
<div class="col-head">Loop</div>
<div class="row-label">In general</div>
<div class="cell model">
<div class="label">decides</div>
<div class="desc">The "brain" thing that picks <em>what to do next</em>. An LLM, mostly.</div>
</div>
<div class="cell tools">
<div class="label">acts</div>
<div class="desc">Added functionality the model is allowed to call. APIs, scripts, services.</div>
</div>
<div class="cell context">
<div class="label">remembers</div>
<div class="desc">What (custom information) the model sees on each turn. Instructions, history, results.</div>
</div>
<div class="cell loop">
<div class="label">drives</div>
<div class="desc">Ask &middot; act &middot; observe &middot; repeat. The runtime.</div>
</div>
<div class="row-label">In the browser</div>
<div class="cell model">
<div class="label">decides</div>
<div class="desc">In-browser SLM (WebGPU), local server, or remote API.</div>
</div>
<div class="cell tools">
<div class="label">acts</div>
<div class="desc">MCP servers (HTTP), Python (JS, WASM, ...) tools (code), plus the DOM.</div>
</div>
<div class="cell context">
<div class="label">remembers</div>
<div class="desc"><code>messages[]</code>, plus DOM, sandboxed files, browser memory.</div>
</div>
<div class="cell loop">
<div class="label">drives</div>
<div class="desc">PyScript  (WASM|JS|...)  &mdash; Python running in the user's tab.</div>
</div>
<div class="invariant"><strong>Same architecture.</strong> Different implementation details.</div>
</div>

<div class="timing">01:45 · t+03:45</div>

<!--
SLIDE 7 — ANATOMY.  02:00–03:45.  ~1m45s.

The teaching beat of the talk. Spend time here. Walk it left to right,
top to bottom.

  "Every agent is four things. A model that decides. Tools that act.
   A loop that drives. And context — what the model sees.
   That's it. Now look at row two — same four things. Different details.
   The model is wherever it runs fastest. The tools are HTTP and the DOM.
   The loop is Python, in the user's tab. The context is messages[].
   The architecture doesn't change in the browser. Only where the parts
   live."

Watch the time. This is the slide that wants to eat 30 extra seconds
because you love it. Don't.
-->


---
title: Anatomy — LLM
---

<div style="display: flex; flex-direction: column; height: 100%;">
<div class="section-eyebrow">Anatomy of an agent</div>
<h2 style="font-size: 2.4rem; margin-bottom: 0.5rem;">Start with an LLM.</h2>
<div style="flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center;">
<LLMDiagram />
</div>
</div>

<div class="timing">01:00 · t+03:45</div>

<!--
SLIDE 6 — LLM DIAGRAM.

Frame it as: "before we talk about agents, let's agree on what an LLM is.
User sends messages. The LLM does its thing — call it magic — and
generates a response. That's it. A stateless function. Messages in,
response out. Now — what if we made it smarter?"
Then advance to the agent diagram slide.
-->

---
title: Anatomy — Agent
---

<div style="display: flex; flex-direction: column; height: 100%;">
<div class="section-eyebrow">Anatomy of an agent</div>
<h2 style="font-size: 2.4rem; margin-bottom: 0.5rem;">Add the loop.</h2>
<div style="flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center;">
<AgentDiagram />
</div>
</div>

<div class="timing">01:00 · t+04:45</div>

<!--
SLIDE 7 — AGENT DIAGRAM.

Frame it as: "Now let's add the loop. The agent wraps the LLM in a
control flow: prepare context, call the LLM, check if it wants to
call a tool — if yes, run it and feed the result back, then loop.
If no, we're done: output goes to the user. The LLM is still the
same stateless function — the agent is just the loop around it."
Then advance to the loop overview.
-->

---
title: M2 — The loop, made visible
layout: center
class: text-center
---

<!-- <div style="font-family: 'JetBrains Mono', monospace; color: var(--muted); font-size: 0.85rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 2rem;">Movement 2 of 4</div> -->

<div style="font-size: 2.8rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; max-width: 24ch; margin: 0 auto;">
The <br/>
<span style="color: var(--browser);">loop</span>
</div>

<div style="margin-top: 2.5rem; color: var(--muted); font-size: 1rem;">Live demo &middot; step-through</div>

<div class="timing">00:15 · t+05:30</div>

<!--
SLIDE 8 — DEMO BRIDGE.  05:15–05:30.  ~15s.

Walk to the laptop. Switch windows to demo (already open).
Step mode toggle is ON. Architecture panel visible on the right.
-->

---
title: Demo 2 — agent + tools
layout: full
---

<div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.5rem; height: 100%; padding: 0;">
<div style="display: flex; flex-direction: column; justify-content: center; padding: 1.5rem 1rem 1.5rem 2.5rem;">
<div class="section-eyebrow">What to watch</div>
<h2 style="font-size: 1.5rem; margin-bottom: 0.75rem; line-height: 1.2;">
Demo 2 — agent + tools<br/>
<span style="color: var(--muted); font-weight: 400; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;">step mode &middot; remote tier</span>
</h2>
<ol style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; list-style: none; padding: 0; line-height: 1.35;">
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">①</span><span><span style="color: var(--browser);">User</span> prompt → agent</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">②</span><span>agent asks <span style="color: var(--remote);">LLM</span> with tools</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">③</span><span>LLM returns <span style="color: var(--tool);">tool call</span> — web_search, analyze_csv, ...</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">④</span><span>agent runs <span style="color: var(--tool);">MCP tool</span>, appends result</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">⑤</span><span>LLM calls next <span style="color: var(--tool);">tool</span> — save_to_file</span></li>
<li style="padding: 0.3rem 0; display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">⑥</span><span>File on <em>your real disk</em>. No backend.</span></li>
</ol>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; margin-top: 0.85rem; line-height: 1.5;">
→ Watch the arch panel light up.<br/>
→ Watch <code>messages[]</code> grow in Context tab.
</p>
</div>
<div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
<ArchDiagram lit-node="agent" />
</div>
</div>

<div class="timing">06:00 · t+11:30</div>

<!--
SLIDE 9 — DEMO 2 AGENT.  05:30–11:30.  ~6 min.

DEMO SCRIPT (step mode, remote tier):
  1. "Find me 3 climate stories from this week and save them to a file."
  2. Click "Demo 2" with step mode ON.
  3. Pause at each checkpoint — narrate what's happening.
  4. When save_to_file fires, mount a local folder via the picker.
  5. Open Finder — show the written file.

LAND ON: "What you saw is the loop. ① ask ② act ③ observe ④ repeat.
And every byte of that loop ran in this browser tab."

If wifi flakes: switch tier to in-browser, run a smaller version.
If wifi dies: play the recorded fallback (phone or second device).
-->

---
title: M3 — Where does the model run?
layout: center
class: text-center
---

<!-- <div style="font-family: 'JetBrains Mono', monospace; color: var(--muted); font-size: 0.85rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 2rem;">Movement 3 of 4</div> -->

<div style="font-size: 2.8rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; max-width: 24ch; margin: 0 auto;">
Where does<br/>
<span style="color: var(--browser);">the model</span> run?
</div>

<div style="margin-top: 2.5rem; color: var(--muted); font-size: 1rem;">Three tiers &middot; one architecture</div>

<div class="timing">00:15 · t+11:45</div>

<!--
SLIDE 10 — SECTION HEADER.  11:30–11:45.  ~15s.
-->

---
title: Three tiers
---

<div class="section-eyebrow">Three places the model can run</div>
<h2 style="font-size: 2rem; margin-bottom: 2rem;">Same loop. Different Scenarios.</h2>

<div class="tiers">
<div class="tier browser">
<div class="tier-head"><span class="dot"></span>In-browser</div>
<h3>WebGPU + WebLLM</h3>
<!-- <div class="ttft">210<small>ms TTFT</small></div> -->
<div class="meta"><strong>Qwen2.5 1.5B</strong>, ~850 MB, downloads once<br/>Runs on the user's GPU. Offline (cached) after first load.<br/><em>No data leaves the device.</em></div>
</div>
<div class="tier local">
<div class="tier-head"><span class="dot"></span>Local</div>
<h3>Ollama / Anaconda Desktop / Agent Studio</h3>
<!-- <div class="ttft">85<small>ms TTFT</small></div> -->
<div class="meta"><strong>Qwen3 8B</strong> via localhost<br/>Same machine, capable model, real tool calling.<br/><em>No data leaves the device.</em></div>
</div>
<div class="tier remote">
<div class="tier-head"><span class="dot"></span>Remote</div>
<h3>Remote API</h3>
<!-- <div class="ttft">11<small>ms TTFT</small></div> -->
<div class="meta"><strong>Claude / GPT</strong> via fetch<br/>Best quality. Lowest latency. Costs per token.<br/><em>Data crosses the network.</em></div>
</div>
</div>

<p style="text-align: center; margin-top: 2rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">Same Python agent. Same <code>stream_chat(messages, tools)</code>. Three implementations behind it.</p>

<div class="timing">02:00 · t+13:45</div>

<!--
SLIDE 11 — THREE TIERS.  11:45–13:45.  ~2 min.

Numbers are real (metrics_snapshot.json from the spike).

  "Same loop, three places. The numbers come from this morning.
   In-browser is private and offline-friendly, model is small.
   Local — Ollama on your laptop — gets you 8B, still private.
   Remote — frontier model, fastest first token, highest quality,
   data leaves the device. Pick the tier per task."

Bridge to next slide: "Same demo, three tiers. Watch."
-->

---
title: Demo 1 — CSV analysis
layout: full
---

<div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.5rem; height: 100%; padding: 0;">
<div style="display: flex; flex-direction: column; justify-content: center; padding: 1.5rem 1rem 1.5rem 2.5rem;">
<div class="section-eyebrow">What to watch</div>
<h2 style="font-size: 1.5rem; margin-bottom: 0.75rem; line-height: 1.2;">
Demo 1 — CSV analysis<br/>
<span style="color: var(--muted); font-weight: 400; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;">Pyodide Pandas · any tier</span>
</h2>
<ol style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; list-style: none; padding: 0; line-height: 1.35;">
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">①</span><span><span style="color: var(--browser);">Pandas</span> runs <em>in the browser</em> — no data leaves the tab</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">②</span><span>LLM receives the numeric summary as a <span style="color: var(--tool);">tool result</span></span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">③</span><span>LLM streams an executive summary</span></li>
<li style="padding: 0.3rem 0; display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">④</span><span>Switch tiers — same result, different latency</span></li>
</ol>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; margin-top: 0.85rem; line-height: 1.5;">
→ Watch Pyodide light up in the arch panel.<br/>
→ Watch the context tab grow step by step.
</p>
</div>
<div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
<ArchDiagram lit-node="pyodide" />
</div>
</div>

<div class="timing">03:00 · t+14:45</div>

<!--
SLIDE 12 — DEMO 1 CSV.   13:45–14:45.   ~3 min.

DEMO SCRIPT:
  1. Remote tier active. Click Demo 1.
  2. Watch Pyodide node light up — "that's Pandas running in the tab."
  3. Watch tool result arrive in context panel — "no backend call."
  4. LLM streams narrative. Point at calls panel: "one LLM call."
  5. Ask a follow-up question in the input box.

LAND ON: "Pandas ran here. Zero round trips to a data server.
The model only saw the summary — private by construction."
-->

---
title: Demo 3 — folder agent
layout: full
---

<div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.5rem; height: 100%; padding: 0;">
<div style="display: flex; flex-direction: column; justify-content: center; padding: 1.5rem 1rem 1.5rem 2.5rem;">
<div class="section-eyebrow">What to watch</div>
<h2 style="font-size: 1.5rem; margin-bottom: 0.75rem; line-height: 1.2;">
Demo 3 — folder agent<br/>
<span style="color: var(--muted); font-weight: 400; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;">load agent.yaml from disk · remote tier</span>
</h2>
<ol style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; list-style: none; padding: 0; line-height: 1.35;">
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">①</span><span>Click Demo 3 → browser opens a <span style="color: var(--browser);">folder picker</span></span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">②</span><span>Select <code>fred-example-agent/</code> from disk</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">③</span><span>Python reads <code>agent.yaml</code> + <code>documents/</code> in the browser</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">④</span><span>System prompt &amp; docs injected into <code>messages[]</code></span></li>
<li style="padding: 0.3rem 0; display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">⑤</span><span>Agent introduces itself — then <em>chat with Fred</em></span></li>
</ol>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; margin-top: 0.85rem; line-height: 1.5;">
→ No server. No upload. No account.<br/>
→ The folder never leaves your machine.
</p>
</div>
<div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; padding: 2rem; gap: 0.8rem; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem;">
<div style="color: var(--muted); font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase;">fred-example-agent/</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; width: 100%;">
<div style="color: var(--tool);">agent.yaml</div>
<div style="color: var(--muted); margin-top: 0.4rem; font-size: 0.7rem;">name · description · system_prompt</div>
<div style="color: var(--muted); margin-top: 0.15rem; font-size: 0.7rem;">ai: provider · model · temperature</div>
</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; width: 100%;">
<div style="color: var(--browser);">documents/</div>
<div style="color: var(--muted); margin-top: 0.4rem; font-size: 0.7rem;">reference docs injected into context</div>
</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 1rem 1.25rem; width: 100%;">
<div style="color: var(--muted);">tools/mcp.json</div>
<div style="color: var(--muted); margin-top: 0.4rem; font-size: 0.7rem;">MCP server config (future)</div>
</div>
</div>
</div>

<div class="timing">03:00 · t+17:45</div>

<!--
SLIDE — DEMO 3 FOLDER AGENT.

DEMO SCRIPT (remote tier):
  1. Click Demo 3 — folder picker opens.
  2. Navigate to demo/fred-example-agent/ and confirm.
  3. Watch agent card appear: name, description, model, docs.
  4. Agent auto-greets: "Yabba Dabba Doo!"
  5. Type a question: "What do you do for work, Fred?"
  6. Chat for 1-2 turns.

LAND ON: "That folder is a portable agent definition. No server.
The system prompt, documents, and config live on your disk.
Python in the browser picked it up and ran it."
-->

---
title: M4 — Why now?
layout: center
class: text-center
---

<!-- <div style="font-family: 'JetBrains Mono', monospace; color: var(--muted); font-size: 0.85rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 2rem;">Movement 4 of 4</div> -->

<div style="font-size: 2.8rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; max-width: 24ch; margin: 0 auto;">
Why now?<br/>
<!-- <span style="color: var(--browser);">And what does it cost?</span> -->
</div>

<div class="timing">00:15 · t+17:45</div>

<!--
SLIDE 13 — SECTION HEADER.  17:30–17:45.  ~15s.
-->

---
title: Why now — three numbers
---

<div class="section-eyebrow">Why this works in 2026</div>
<h2 style="font-size: 2.4rem; margin-bottom: 1rem;">Three things shifted.</h2>

<div class="why-now">
<div class="row r1">
<div class="num">4 / 4</div>
<div class="label"><strong style="color: var(--browser);">WebGPU shipped</strong> in every major browser<small>Chrome &middot; Edge &middot; Firefox &middot; Safari &mdash; first time, November 2025.</small></div>
</div>
<div class="row r2">
<div class="num">8B</div>
<div class="label"><strong style="color: var(--local);">Small models do tool calling</strong><small>Phi-4-mini, Gemma 4, Qwen 3.5 &mdash; runs on a laptop, calls tools.</small></div>
</div>
<div class="row r3">
<div class="num">97M<span style="font-size: 1.4rem; color: var(--muted);">/mo</span></div>
<div class="label"><strong style="color: var(--tool);">MCP became a standard</strong><small>Anthropic SDK downloads. 9,400+ public MCP servers, +18% MoM.</small></div>
</div>
<div class="punch">Each one alone wouldn't move the needle. <strong>Together, they unlock this.</strong></div>
</div>

<div class="timing">01:30 · t+19:15</div>

<!--
SLIDE 13 — WHY NOW.   17:45–19:15.   ~1m30s.

Three numbers. Don't read them — frame them.

  4/4: "Last November, WebGPU shipped in every major browser. First
       time. That means a Python program can ask the user's GPU to
       run a model — no driver install, no native binary."

  8B:  "Two years ago small models couldn't call tools reliably.
       That's gone. Phi-4-mini, Gemma 4 — runs on a laptop, calls
       tools, drives an agent loop."

  97M: "MCP wasn't even a thing when this talk's abstract was
       written. Now Anthropic is shipping ~100 million SDK downloads
       a month. Tools are universal."

Punch: "Each on its own — meh. Together — new platform."
-->

---
title: Trade-offs — measured
---

<div class="section-eyebrow">Honest trade-offs &middot; measured today</div>
<h2 style="font-size: 2.2rem; margin-bottom: 1.5rem;">When to use each.</h2>

<table class="tradeoffs">
<thead>
<tr><th>Dimension</th><th>In-browser</th><th>Local</th><th>Remote</th></tr>
</thead>
<tbody>
<tr><td>Latency (TTFT)</td><td><span class="pill yellow">~210 ms</span></td><td><span class="pill green">~85 ms</span></td><td><span class="pill blue">~11 ms</span></td></tr>
<tr><td>Model ceiling</td><td><span class="pill yellow">1–3 B</span></td><td><span class="pill yellow">7–70 B</span></td><td><span class="pill green">frontier</span></td></tr>
<tr><td>Tool-call quality</td><td><span class="pill red">poor at 1B</span></td><td><span class="pill yellow">good at 8B+</span></td><td><span class="pill green">excellent</span></td></tr>
<tr><td>Privacy</td><td><span class="pill teal">on-device</span></td><td><span class="pill teal">on-device</span></td><td><span class="pill red">data leaves</span></td></tr>
<tr><td>Cost / 1k tokens</td><td><span class="pill teal">$0</span></td><td><span class="pill teal">$0</span></td><td><span class="pill yellow">$0.001–0.03</span></td></tr>
<tr><td>First-load weight</td><td><span class="pill red">~700 MB model</span></td><td><span class="pill yellow">pre-installed</span></td><td><span class="pill green">none</span></td></tr>
<tr><td>Offline capable</td><td><span class="pill green">after 1st load</span></td><td><span class="pill green">always</span></td><td><span class="pill red">needs net</span></td></tr>
</tbody>
</table>

<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; margin-top: 1.25rem; text-align: center;">Bundle: 11.4 MB · Cold start: 8.2 s · Warm: 1.1 s &nbsp;&middot;&nbsp; measured on M2 MacBook Pro, Chrome 124</p>

<div class="timing">02:30 · t+21:45</div>

<!--
SLIDE 14 — TRADE-OFFS.  19:15–21:45.  ~2m30s.

Be the speaker who tells the audience when NOT to use the thing.

  - "If you need frontier-quality reasoning on every turn, go remote."
  - "If you need <100ms TTFT and frontier quality, you can't have both
     without remote."
  - "If your users won't tolerate a 700 MB first download, in-browser
     is wrong."
  - "If your data MUST stay on the device — privacy, regulatory —
     in-browser or local. Remote isn't an option."

Numbers come from metrics_snapshot.json + the live drawer the audience
already saw. They're real. Refresh before the talk.

Don't apologize for the trade-offs. The point of the slide is that
this architecture is honest about them.
-->

---
title: Don't use this for
---

<div class="section-eyebrow">Don't use this for</div>
<h2 style="font-size: 2.4rem; margin-bottom: 1.5rem;">Where this is the wrong tool.</h2>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; font-size: 1rem; line-height: 1.55;">
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem 1.5rem;">
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ef5350; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.6rem;">DON'T</div>
<strong style="color: #fff;">Multi-tenant high-throughput backends.</strong>
<p style="color: var(--muted); margin-top: 0.4rem; font-size: 0.92rem;">Each tab pays the bundle cost. Servers exist for a reason.</p>
</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem 1.5rem;">
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ef5350; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.6rem;">DON'T</div>
<strong style="color: #fff;">Multi-GB frontier models locally.</strong>
<p style="color: var(--muted); margin-top: 0.4rem; font-size: 0.92rem;">The browser isn't going to run a 70B model well. Don't pretend it will.</p>
</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem 1.5rem;">
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ef5350; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.6rem;">DON'T</div>
<strong style="color: #fff;">Hard SLA on cold-start latency.</strong>
<p style="color: var(--muted); margin-top: 0.4rem; font-size: 0.92rem;">First load is 8 seconds and a 700 MB download. Tell users that.</p>
</div>
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.25rem 1.5rem;">
<div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #ef5350; letter-spacing: 0.15em; text-transform: uppercase; margin-bottom: 0.6rem;">DON'T</div>
<strong style="color: #fff;">A constrained device.</strong>
<p style="color: var(--muted); margin-top: 0.4rem; font-size: 0.92rem;">Old phones. Low-RAM laptops. The user's device <em>is</em> the infra.</p>
</div>
</div>

<div class="timing">01:00 · t+22:45</div>

<!--
SLIDE 15 — DON'T USE THIS FOR.   21:45–22:45.   ~1 min.

Tight. Read the headlines, one breath each. Move on.
You earn trust by being clear about the boundary.
-->

---
title: CTA — try it
layout: center
---

<div class="cta">
<div>
<div class="section-eyebrow">Take it home</div>
<h2>Try it.</h2>
<p style="color: var(--muted); font-size: 1.05rem; line-height: 1.55; max-width: 32ch;">The whole demo &mdash; routing, agent loop, MCP, three tiers &mdash; is open source. Clone it, run it, change it.</p>
<ol>
<li><span style="color: var(--browser);">git clone</span> the repo</li>
<li><span style="color: var(--local);">./run.sh</span> &mdash; servers + static</li>
<li><span style="color: var(--remote);">open</span> http://localhost:8000</li>
</ol>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; margin-top: 1.25rem;">Five minutes. No accounts. No GPUs. No bill.</p>
</div>
<div class="qr-card">
<div class="qr">[ QR &rarr; repo ]<br/><span style="margin-top: 0.4rem; display: block;">replace before talk</span></div>
<div class="url">github.com/fpliger/<br/>pyconus-2026-agent</div>
</div>
</div>

<div class="timing">01:30 · t+24:15</div>

<!--
SLIDE 16 — CTA.   22:45–24:15.   ~1m30s.

Last technical slide. Give the audience the actionable moment:
"Three steps. Five minutes. Try it on the flight home."

REPLACE BEFORE TALK:
  - QR code SVG (run a generator against the final repo URL)
  - Repo URL once it's published

If running long: cut to the next slide immediately. The CTA can be
30 seconds if needed.
-->

---
title: Closing — Q&A
layout: center
class: text-center
---

<div class="big-thesis" style="font-size: 3.2rem; max-width: 28ch;">
An agent is a loop.<br/>
<span class="accent">Python writes loops.</span><br/>
The browser ships them.
</div>

<div style="margin-top: 3rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; letter-spacing: 0.05em;">Questions?</div>

<div style="margin-top: 4rem; display: flex; justify-content: center; gap: 2.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--muted);">
<span>@bugzpodder</span>
<span>github.com/fpliger</span>
<span>pyscript.net</span>
</div>

<div class="timing">00:45 · t+25:00 &middot; Q&A starts</div>

<!--
SLIDE 17 — CLOSING + Q&A.   24:15–25:00.   ~45s.

Callback to the thesis. Three short lines: agent / Python / browser.

Then "Questions?" — and you're into Q&A. Leave this slide up the
whole time so the contact info is visible.

If Q&A drags, you have these in your back pocket:
  - "What about WebNN?" → Candidate Recommendation Jan 2026, Chrome
    + Edge shipping, Safari/Firefox not yet. ~2027 default.
  - "Why not just JavaScript?" → JS is fine. The talk is about giving
    Python developers an on-ramp; the architecture works in either.
  - "What about security?" → Browser sandbox is the strongest privacy
    guarantee you can ship. Tools are explicit. Tabs can't see other
    tabs.
  - "What about training?" → Out of scope. This is inference + agent
    orchestration, not training pipelines.
  - "Bundle size won't get smaller, will it?" → Pyodide team is
    actively trimming. MicroPython variant is 303 KB if you can live
    without the stdlib. Real answer: cache aggressively.
-->
