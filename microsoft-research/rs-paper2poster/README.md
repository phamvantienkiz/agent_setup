# paper2poster

> Turn a paper's extracted assets into a print-ready, single-page academic poster — HTML + PDF + PNG + an editable PowerPoint — fitted to the page exactly.

`paper2poster` is the **rendering stage** of the ResearchStudio pipeline. It takes the `<outdir>/` bundle produced by [`paper2assets`](../paper2assets/), picks the figures, fills a fixed-canvas HTML template with the paper's 9-section spec, runs a measured loop until every section sits at the right density, narrates each section for the in-poster Listen buttons, and exports the result to PDF/PNG plus a natively-editable `.pptx` (via the bundled [`html2pptx`](html2pptx/) sub-skill).

```
paper2assets  ──▶  paper2poster  ──▶  html2pptx
  <outdir>/         poster.html        poster.pptx
                    poster.pdf / .png  (built in — same run)
```

## Input

A `paper2assets` `<outdir>/` containing (at minimum):

- `manifest.json`
- `assets/meta/paper_spec.md` — the 9-section structured summary
- `assets/meta/{text.txt, figures.json, metadata.json}`
- `assets/figures/*.png` — cleaned figure rasters
- `assets/logos/`, `assets/qr/` — optional, best-effort

Run `paper2assets` first if these are missing.

## Output

Written back into the same `<outdir>/`, next to `manifest.json` and `assets/`:

| File | What it is |
|---|---|
| `poster.html` | Self-fitting single-page poster (references `assets/` for figures + fonts). Press `s` for fullscreen, `a` to toggle Listen buttons, `d` for a debug overlay |
| `poster.pdf` | Print-ready PDF at the exact canvas size (Chromium print emulation) |
| `poster.png` | Thumbnail preview |
| `poster.pptx` | Editable PowerPoint — native text + shapes, not a PNG-in-slide (via html2pptx) |
| `assets/audio/*.mp3` | Per-section narration for the Listen buttons (free Edge TTS; skipped if unavailable) |

## Usage

From a Claude Code session:

```text
# point it at a paper2assets <outdir>/
> /paper2poster ./my_paper/

# …or describe what you want in natural language
> /paper2poster Render a portrait poster for arxiv 2502.06434 in teal
```

One run yields all four artifacts — you never call `html2pptx` separately.

## How it works

The lean first render holds only each section's essential text. A **measured fill loop** (`check_poster.py slack` + `polish`) then grows or shrinks content section-by-section until every card reads `FULL` (90–100% of its height) and every figure fills ≥90% of its card on at least one axis. At render time a final **expand** pass lifts under-filled cards toward ~98% and bakes the result back into `poster.html`, so the PDF, PNG, and PPTX all match.

## Two canvas presets

| Orientation | Size | Venues |
|---|---|---|
| **Landscape** (default) | 60 × 36 in (5:3) | NeurIPS · ICML · CVPR |
| **Portrait** (`POSTER_ORIENTATION=portrait`) | A0, 33.1 × 46.8 in | ACL · NAACL · AAAI |

Both orientations are **composed at build time** instead of selecting a monolithic template. Landscape uses `assets/layouts/{full,half,3col}.html`; Portrait uses `assets/layouts_portrait/{full,half}.html`. They share 9 themes and the same style sources, while each orientation has its own five-header family. Landscape enables all 11 styles; Portrait enables 9. The renderer routes by orientation, then by the Method figure's aspect ratio.

## Header, logos & QR

`references/compose_poster.py` combines independent axes into one self-contained file. Layout, style, header, and theme apply to both orientations; Scan-to-Read is Landscape-only:

- **Layout** — Landscape `assets/layouts/{full,half,3col}.html`; Portrait `assets/layouts_portrait/{full,half}.html`. Portrait Half has two columns with exactly one bottom `.grow` per column. Portrait Full has four content bands, including a `1.5fr 1fr 1fr` Results band and full-width Takeaway.
- **Style:** `assets/styles/*.css`. Landscape randomizes across all 11 visual treatments. Portrait excludes `underline` and `double-rule`, leaving 9 eligible styles, because those horizontal rules create misleading section divisions in narrow columns.
- **Header** — Landscape `assets/headers/{v1…v5}.html`; Portrait `assets/headers_portrait/{pv1…pv5}.html`. Each orientation randomizes across its own five-header pool. Portrait uses five structural arrangements: balanced triptych (`pv1`), full-width masthead over a navigation strip (`pv2`), left editorial copy followed by institution marks and an outer-right Venue/QR rail (`pv3`), the center-aligned reverse triptych of pv1 (`pv4`), and the mirrored outer-left Venue/QR plus institution marks beside right editorial copy (`pv5`). In the navigation variants, one vertical divider separates Venue/QR from institution marks while the marks remain adjacent to the paper information and retain an independent `fit_logos.py` zone.
- **Theme** — 9 shared academic palettes: blue · teal · green · burgundy · purple · rust · slate · plum · mono.
- **Scan** — Landscape only, from `assets/scan/{aside,hero,contact,directory,banner,twin,chips}.html`. The build picks `--scan single` (paper only) or `dual` (paper + code), then samples a fitting variant. Portrait has no standalone scan section or scan axis; its headers own the QR slots.

**Venue logo** — `paper2assets` best-effort fetches the conference mark (Wikipedia / Wikidata) into `assets/logos/_venue.png`; the header shows that logo and hides the venue-year text so the two never duplicate. The venue is always the **real conference / journal** — never "arXiv" (a preprint host is not a publication venue).

**Institution logos** — `references/fit_logos.py` packs the institution marks to fill the header zone at a single **uniform height** (every logo enlarges together, sized by the browser's true aspect ratio so even wide SVG wordmarks fit without overflowing the band). Its automatic completion is an allowlist operation: only accepted `logos[]` entries in `assets/logos/logos.json` may be injected, so orphan cover images and rejected or stale marks are not rendered merely because they remain in the directory. Historical `logos[]` entries without approval fields remain compatible. If the manifest is missing, the fitter adds nothing from disk and only preserves explicit HTML sources. `assets/logos/_venue.png` remains a separate conference resource. Branded Landscape headers expose six logo slots; branded Portrait headers expose four. The explicit `v6`/`v7` and `pv6`/`pv7` headers expose none.

**QR codes** — in Landscape, the Paper / Code QRs live in the **Scan to Read** section for headers v1–v4 and v6–v7; the v5 classic header carries a QR in the title band itself. The **3col layout suppresses Scan-to-Read** and is kept off v5, so a 3col poster carries no QR. Portrait has no standalone Scan-to-Read section and uses only its selected `pv1`–`pv7` header's QR slots.

## No institution names or logos

Choose an explicit **Title banner** template rather than relying on a prompt:

| Layout direction | Centered | Left-aligned |
|---|---|---|
| Landscape | `--header v6` | `--header v7` |
| Portrait | `--header pv6` | `--header pv7` |

The Web selector labels these **Clean centered / Clean left · no institutions/logos**.
They work with every body layout in the chosen orientation. They keep the title,
plain author names, venue text and normal QR placement, but have no institution
legend or logo containers. Existing branded templates and random pools are unchanged.
Fill `{{AUTHORS_PLAIN}}` and follow `references/branding_free_headers.md`; the
logo fitter respects the explicit opt-out and preflight rejects restored branding.
This does not anonymize authors or remove text embedded in scientific figures.

## Deterministic diversity for batches

The default `random` values are reproducible. Seed precedence is explicit `--seed`, then `POSTER_SEED`, then the resolved absolute `--out` path, so separate paper directories naturally receive different combinations.

For a 30+ paper gallery, pass consecutive zero-based `--variant-index` values with one shared `--variant-seed` (or `POSTER_VARIANT_SEED`). The sampler deterministically orders the joint random-axis combination space without replacement, so complete style/header/theme tuples do not repeat while unused combinations remain; it simultaneously keeps each axis marginally balanced. Landscape covers 11 styles in 11 posters; Portrait covers its 9 eligible styles in 9 posters; 5 posters cover all 5 Portrait headers; and 9 cover all 9 themes. Keep `--layout` driven by the Method figure unless layout itself should be sampled.

```bash
python references/compose_poster.py --orientation portrait \
  --layout full --style random --header random --theme random \
  --variant-index 17 --variant-seed portrait-wave-20260810 \
  --selection-out <outdir>/selection.json \
  --out <outdir>/poster.html
```

Every composed HTML embeds the resolved manifest in `#paper2poster-composition` and stamps the main axes on `<body data-poster-...>`. `--selection-out` writes the same metadata as external JSON for gallery audits and tests.

## Tuning knobs (env vars)

| Var | Default | Controls |
|---|---|---|
| `POSTER_ORIENTATION` | `landscape` | `landscape` or `portrait` |
| `POSTER_STYLE` | `random` | Landscape: 1 of 11; Portrait: 1 of 9, excluding `underline` and `double-rule` |
| `POSTER_HEADER` | `random` | Branded pool: Landscape `v1`–`v5`, Portrait `pv1`–`pv5`; explicit no institutions/logos: `v6`/`v7`, `pv6`/`pv7` |
| `POSTER_THEME` | `random` | shared theme: 1 of 9 (`blue` … `mono`) |
| `POSTER_SEED` | resolved absolute output path | stable seed for ordinary random-axis selection; explicit `--seed` wins |
| `POSTER_VARIANT_SEED` | ordinary seed | shared batch seed used with `--variant-index` for balanced cycles |
| `POSTER_FONT` | `Arial` | any of 8 PPT-safe families (Arial round-trips with no font embedding) |
| `POSTER_FULL_THRESHOLD` | `0.90` | the fill-loop's FULL gate (raise for a tighter pack, ~2× loop time) |
| `POSTER_EXPAND_THRESHOLD` | `0.98` | render-time expand target (`0` disables) |

## Scripts

```
scripts/
├── check_poster.py     # slack / preflight / polish / verify-final / deliverables gates
├── render_poster.py    # print-emulated PDF + PNG; applies & bakes the expand
└── generate_audio.py   # narration.json → assets/audio/<id>.mp3 (free Edge TTS)
```

Figure-cropping tools live in `paper2assets`; the PPTX converter is bundled at [`html2pptx/`](html2pptx/).

## Requirements

- Python ≥ 3.10, `playwright` + Chromium (`python -m playwright install chromium`)
- `edge-tts` — optional, for the narration audio
- LibreOffice — for the html2pptx PPTX export

## More detail

[`SKILL.md`](SKILL.md) is the authoritative, agent-facing spec: the full step-by-step workflow, the template-routing rules, the staged-fill convergence protocol, and every edge case. The [`references/`](references/) folder holds the deep guides (template substitution, content patterns, visual polish, staged fill, audio narration).
