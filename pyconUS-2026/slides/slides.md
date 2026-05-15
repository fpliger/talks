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
title: Anatomy — one loop
---

<div style="display: flex; flex-direction: column; height: 100%;">
<div class="section-eyebrow">Anatomy of an agent</div>
<h2 style="font-size: 2.4rem; margin-bottom: 0.5rem;">One loop.</h2>
<div style="flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center;">
<LoopDiagram />
</div>
</div>

<div class="timing">01:30 · t+05:15</div>

<!--
SLIDE 6 — THE LOOP.  03:45–05:15.  ~1m30s.

Walk the four boxes once, slowly:

  ① "Ask the model — what should I do?"
  ② "Run the tool — call a function, hit an HTTP endpoint, run pandas."
  ③ "Feed the result back — append to messages[], hand it back to the model."
  ④ "Done? If yes, return. If not, loop."

Land on: "That's it. That's the entire architecture of every agent
you've ever used. Claude Code. Cursor. The thing your colleague is
building on a Hugging Face Space. Same four boxes."

Then bridge to demo: "Let me show it running."
-->

---
title: Anatomy (Continued) — four parts
---

<div class="section-eyebrow">Anatomy of an agent (continueed)</div>
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
<div class="desc">MCP servers (HTTP), Python tools (code), plus the DOM.</div>
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
title: Demo 3 — agent + tools
layout: full
---

<div style="display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.5rem; height: 100%; padding: 0;">
<div style="display: flex; flex-direction: column; justify-content: center; padding: 1.5rem 1rem 1.5rem 2.5rem;">
<div class="section-eyebrow">What to watch</div>
<h2 style="font-size: 1.5rem; margin-bottom: 0.75rem; line-height: 1.2;">
Demo 3 — agent + tools<br/>
<span style="color: var(--muted); font-weight: 400; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace;">step mode &middot; remote tier</span>
</h2>
<ol style="font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; list-style: none; padding: 0; line-height: 1.35;">
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">①</span><span><span style="color: var(--browser);">User</span> prompt → orchestrator</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">②</span><span>Orchestrator asks <span style="color: var(--remote);">LLM</span> with tools</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">③</span><span>LLM returns <span style="color: var(--tool);">tool call</span> — web_search, analyze_csv, ...</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">④</span><span>Orchestrator runs <span style="color: var(--tool);">MCP tool</span>, appends result</span></li>
<li style="padding: 0.3rem 0; border-bottom: 1px solid var(--border); display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">⑤</span><span>LLM calls next <span style="color: var(--tool);">tool</span> — analyze_csv, save_to_file, ...</span></li>
<li style="padding: 0.3rem 0; display: flex; gap: 0.5rem;"><span style="color: var(--muted); flex-shrink: 0;">⑥</span><span>File on <em>your real disk</em>. No backend.</span></li>
</ol>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; margin-top: 0.85rem; line-height: 1.5;">
→ Watch the arch panel light up.<br/>
→ Watch <code>messages[]</code> grow in Context tab.
</p>
</div>
<div style="display: flex; align-items: center; justify-content: center; padding: 2rem;">
<ArchDiagram lit-node="orchestrator" />
</div>
</div>

<div class="timing">06:00 · t+11:30</div>

<!--
SLIDE 9 — THE LIVE DEMO.  05:30–11:30.  ~6 min.

This is the centerpiece. The slide is a stage prop — the real show is
the browser tab. Cut to the demo when ready.

DEMO SCRIPT (step mode, remote tier):

  1. "Find me 3 climate stories from this week and save them to a file."
  2. Click "Demo 3" with step mode ON.
  3. Pause #1: orchestrator activated. Point: "Python in the tab."
  4. Pause #2: → LLM call. Point at calls panel: "this is the request."
  5. Token stream begins. Point: "messages[] is growing."
  6. Pause #3: tool call returned. "The model said: 'call web_search'.
     I am not running anything yet — just orchestrating."
  7. Tool runs (MCP). Point at tool pill in chat. Point at calls panel.
  8. Pause #4: results appended. "Now another LLM turn — same loop, again."
  9. Second tool call: save_to_file. The OS file picker opens.
  10. Pick a folder. File written. Open Finder. Show the .md file.

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
<div class="meta"><strong>QwenQwen2.5 1.5B</strong>, ~850 MB, downloads once<br/>Runs on the user's GPU. Offline (cached) after first load.<br/><em>No data leaves the device.</em></div>
</div>
<div class="tier local">
<div class="tier-head"><span class="dot"></span>Local</div>
<h3>Ollama / Anaconda Desktop / Agent Studio</h3>
<!-- <div class="ttft">85<small>ms TTFT</small></div> -->
<div class="meta"><strong>Llama 3.2 8B</strong> via localhost<br/>Same machine, capable model, real tool calling.<br/><em>No data leaves the device.</em></div>
</div>
<div class="tier remote">
<div class="tier-head"><span class="dot"></span>Remote</div>
<h3>Remote API</h3>
<!-- <div class="ttft">11<small>ms TTFT</small></div> -->
<div class="meta"><strong>Claude / GPT</strong> via fetch<br/>Best quality. Lowest latency. Costs per token.<br/><em>Data crosses the network.</em></div>
</div>
</div>

<p style="text-align: center; margin-top: 2rem; color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem;">Same Python orchestrator. Same <code>stream_chat(messages, tools)</code>. Three implementations behind it.</p>

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
title: Demo 1 — three tiers
layout: full
---

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; height: 100%; padding: 2rem 3rem;">
<div style="display: flex; flex-direction: column; justify-content: center; gap: 1.25rem;">
<div class="section-eyebrow">What to watch</div>
<h2 style="font-size: 1.8rem; margin: 0; line-height: 1.15;">
Show me the code<br/>
<span style="color: var(--muted); font-weight: 400; font-size: 0.95rem; font-family: 'JetBrains Mono', monospace;">three tiers, in order</span>
</h2>
<div style="display: flex; flex-direction: column; gap: 0.8rem; margin-top: 1rem;">
<div style="display: grid; grid-template-columns: auto 1fr auto; gap: 1rem; align-items: center; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--browser); border-radius: 8px;"><span style="font-family: 'JetBrains Mono', monospace; color: var(--browser); font-weight: 600; font-size: 0.85rem;">IN-BROWSER</span><span style="color: var(--text); font-size: 0.92rem;">Tab does the inference.</span><span class="mono" style="color: var(--browser); font-weight: 700;">slow</span></div>
<div style="display: grid; grid-template-columns: auto 1fr auto; gap: 1rem; align-items: center; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--local); border-radius: 8px;"><span style="font-family: 'JetBrains Mono', monospace; color: var(--local); font-weight: 600; font-size: 0.85rem;">LOCAL</span><span style="color: var(--text); font-size: 0.92rem;">Ollama, a 30s away.</span><span class="mono" style="color: var(--local); font-weight: 700;">slow*</span></div>
<div style="display: grid; grid-template-columns: auto 1fr auto; gap: 1rem; align-items: center; padding: 0.75rem 1rem; background: var(--surface); border: 1px solid var(--border); border-left: 4px solid var(--remote); border-radius: 8px;"><span style="font-family: 'JetBrains Mono', monospace; color: var(--remote); font-weight: 600; font-size: 0.85rem;">REMOTE</span><span style="color: var(--text); font-size: 0.92rem;">Frontier API.</span><span class="mono" style="color: var(--remote); font-weight: 700;">~fast</span></div>
</div>
<p style="color: var(--muted); font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; margin-top: 0.5rem; line-height: 1.55;">
&rarr; Same prompt. Same Python.<br/>
&rarr; The dropdown is the only thing that changes.
</p>
</div>
<div style="display: flex; align-items: center; justify-content: center;">

```python
# tiers.py — same interface, three implementations
class InBrowserTier:
    async def stream_chat(self, messages, tools):
        engine = await webllm.CreateMLCEngine(...)
        async for d in engine.chat.completions.create(...):
            yield Delta(text=d.delta.content)

class LocalTier:
    async def stream_chat(self, messages, tools):
        r = await fetch("http://localhost:11434/v1/chat/completions", ...)
        async for evt in sse(r):
            yield Delta(text=evt["choices"][0]["delta"]["content"])

class RemoteTier:
    async def stream_chat(self, messages, tools):
        r = await fetch(REMOTE_API_URL, headers=AUTH, ...)
        async for evt in sse(r):
            yield Delta(text=evt["choices"][0]["delta"]["content"])
```

</div>
</div>

<div class="timing">03:45 · t+17:30</div>

<!--
SLIDE 12 — DEMO 1 ×3.   13:45–17:30.   ~3m45s.

This is your second live moment. Cut to the demo.

DEMO SCRIPT:
  - In-browser tier active. Click Demo 1. Watch ~210ms TTFT.
  - Switch tier dropdown to Local. Click Demo 1. Watch ~85ms.
  - Switch tier dropdown to Remote. Click Demo 1. Watch ~11ms.
  - Open trade-offs drawer briefly. The numbers are right there.

LAND ON: "Same Python. Three tiers. Same loop. The dropdown is the
only thing I changed. That's the headline of this whole talk: the
model is one box in the architecture; you can swap it without
rewriting the agent."

If you have time, drop the punchline early: "And here's the trick —
the orchestrator never moves. It always runs in the tab."
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
