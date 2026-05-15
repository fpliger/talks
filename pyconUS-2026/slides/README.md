# PyCon US 2026 — Slide deck

Talk: **Distributing AI with Python in the Browser: Edge Inference and Flexibility Without Infrastructure**
30 minutes (25 + 5 Q&A) · AI track · Long Beach Convention Center

Built with [Slidev](https://sli.dev). Slide source is `slides.md`; theming is in `style.css`; reusable diagrams are Vue components in `components/`.

---

## Run

```bash
cd slides
npm install
npm run dev          # opens at http://localhost:3030
```

Press `o` for overview, `f` for full-screen, `space` to advance.
Press `p` to open presenter mode (notes + timer on second screen).

## Export PDF

```bash
npm run export-pdf   # → dist/pyconus-2026.pdf
```

(Slidev runs Playwright under the hood for export. First run will install Chromium.)

---

## Structure (24 min content + 1 min slack)

| # | Slide | Movement | Min | Cumulative |
|---|---|---|---|---|
| 1 | Title | Open | 0:30 | 0:30 |
| 2 | "An agent is not a chatbot. It's a loop." | Open | 0:50 | 1:20 |
| 3 | Speaker intro | Open | 0:25 | 1:45 |
| 4 | Section: What is an agent? | M1 | 0:15 | 2:00 |
| 5 | **Anatomy** — 4 parts × 2 rows | M1 | 1:45 | 3:45 |
| 6 | **The loop** — 4 boxes | M1 | 1:30 | 5:15 |
| 7 | Section: The loop, made visible | M2 | 0:15 | 5:30 |
| 8 | **Live Demo 3** — agent + tools (step mode) | M2 | 6:00 | 11:30 |
| 9 | Section: Where does the model run? | M3 | 0:15 | 11:45 |
| 10 | **Three tiers** | M3 | 2:00 | 13:45 |
| 11 | **Live Demo 1 ×3** — tier switching | M3 | 3:45 | 17:30 |
| 12 | Section: Why now & what does it cost | M4 | 0:15 | 17:45 |
| 13 | **Why now** — three numbers | M4 | 1:30 | 19:15 |
| 14 | **Trade-offs** — measured today | M4 | 2:30 | 21:45 |
| 15 | Don't use this for | M4 | 1:00 | 22:45 |
| 16 | **CTA** — clone, run, open | Close | 1:30 | 24:15 |
| 17 | Closing + Q&A | Close | 0:45 | 25:00 |

**Anchor slides** (the ones to nail):
- 5 (anatomy), 6 (loop), 10 (three tiers), 13 (why now), 14 (trade-offs), 16 (CTA).
- Slides 8 and 11 are demo handoffs — the slide is a prop, the live tab is the show.

---

## Pre-talk checklist (the morning of)

1. **Refresh the numbers.** Run `python spike/measure_metrics.py`; copy fresh values into `metrics_snapshot.json` and into slide 10 / slide 14 (search for `~210`, `~85`, `~11`, `8.2 s`, `11.4 MB`).
2. **Pre-warm the demo.** Open `http://localhost:8000` in a hidden tab. Click Demo 1 once on the in-browser tier so WebLLM is cached. Open Demo 3 in step mode, ready to go.
3. **Verify all three tier dots are green.** Health probe in the demo footer.
4. **Drop the QR code.** Replace the placeholder in slide 16 with a real QR PNG/SVG pointing at the public repo URL (use `qrencode` or any generator).
5. **Speaker links.** Update `@bugzpodder` and the GitHub URL on slides 3 and 17 if the handles changed.
6. **Backup recording.** Have the Demo 3 fallback video on a phone or second device, queued.

---

## Customization notes

- **Colors:** all six tier/role colors are CSS vars in `style.css` (`--browser`, `--local`, `--remote`, `--tool`, `--pyodide`, `--hybrid`). They mirror `demo/index.html` exactly so the deck → demo cut is seamless.
- **Diagrams:** `components/LoopDiagram.vue` accepts a `:step="1..4"` prop to highlight one node — useful if you want to walk through it click-by-click. `components/ArchDiagram.vue` accepts `lit-node` and `lit-edge` props.
- **Section headers** (slides 4, 7, 9, 12) are intentionally minimal — they're a breath, not content. Cut them ruthlessly if you're running long.

---

## Out of scope

- Training pipelines, fine-tuning, RAG, embeddings — none of it appears in the deck. If asked, defer to Q&A.
- Multi-agent / planner-executor / ReAct frameworks — same.
- WebNN — single Q&A note in slide 17 speaker notes; otherwise ignored.
