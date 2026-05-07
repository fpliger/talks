# Handoff prompt — PyCon US 2026 talk: slide design session

Paste this into a new chat. The folder being shared is `pyconUS_2026/`.

---

You're picking up a PyCon US 2026 talk prep project for the slide design session. The talk is **"Distributing AI with Python in the Browser: Edge Inference and Flexibility Without Infrastructure"** — 30 minutes (25+5) on the AI track, accepted.

This folder (`pyconUS_2026/`) contains:
- `talk_brainstorm.ipynb` — the full brainstorm. The talk's source of truth.
- `spike_log.ipynb` — outcome of the demo prototyping session. Has real measurements and learnings that should land in the trade-offs slide.
- Subfolders / files: previous PyScript agents and the router demo built during the spike.

**Your job this session: turn §7 (outline) and §9 (slide concepts) into an actual deck.**

1. Read `talk_brainstorm.ipynb` — especially **§3** (narrative through-line), **§7** (outline + minute budget), **§9** (slide concepts), **§10** (status). Then read `spike_log.ipynb`.

2. Confirm a few things with the speaker before designing:
   - Which demo became the headline? (§8 has a starting candidate, but the spike may have changed it.)
   - Deck format — `.pptx`? HTML? Reveal.js? Something else?
   - Any Anaconda or PyScript brand template to honor?

3. Produce slides for every section in §7. The anchor slides to nail:
   - **Architecture diagram** (§9) — readable from the back of a conference room.
   - **Anatomy slide** (§9) — two-row layout, *in general* over *in the browser*.
   - **"Why now"** (§9) — three numbers, one per row.
   - **Trade-offs** (§9) — refresh rows with real numbers from the spike.
   - **CTA** — QR code to repo, three steps, "Questions?".

4. Stay strict to the **24-minute content budget** in §7. If a slide tempts a 90-second tangent, it's the wrong slide.

**Done =** complete deck matching §7, an architecture diagram readable from the back row, trade-offs slide updated with spike numbers, speaker notes for each slide, timing markers consistent with 24 minutes.

**Out of scope:** changing the talk's narrative or scope (locked in the brainstorm); writing new code unless a slide embed needs it.
