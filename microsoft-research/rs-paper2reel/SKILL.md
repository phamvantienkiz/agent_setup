---
name: rs-paper2reel
description: Build an interactive HTML viewer (reel.html) that aligns paper2poster output with slide frames, video clips, and bilingual blog text via content_alignment.json without mutating original deliverables. STOPS to present interactive web preview.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  framework: Microsoft Research Studio (HITL Edition)
  phase: "Post-Paper Dissemination (Interactive Web Reel)"
---

# paper2reel - aligned artifact viewer

`paper2reel` builds a browsing layer over existing artifacts. It does
not replace or mutate `paper2poster`, `ppt-master`, `paper2blog`, or
`paper2video` outputs.

The key artifact is:

```text
content_alignment.json
```

It maps the canonical section ids from `paper2assets`'s `assets/meta/sections.json` to:

- poster DOM targets, usually `[data-section="<id>"]`;
- slide frame targets, usually one or more slide indexes;
- blog blocks rendered from the same paper2blog content used for final DOCX;
- video clips cut from the same final, Bottom-Bar-subtitled MP4 and timeline
  used for paper2video delivery.

This sidecar lets a wrapper UI switch between Poster / Slides / Blog and jump to
the corresponding location without adding visible engineering tags to the
deliverables themselves.

## Viewer UX Contract

The user-facing viewer must preserve the original poster as the default screen.
When `reel.html` first opens, it should show only the poster itself:
no permanent wrapper bar, no tab strip, and no visible instructions outside the
poster. The wrapper controls are discoverable through keyboard shortcuts and
section interactions:

- `v` toggles the top section menu.
- `h` toggles keyboard shortcut help.
- `a` toggles the poster's existing audio controls.
- `s` toggles fullscreen.
- `d` toggles the poster debug/hover controls.
- double-clicking a poster section opens a large modal.
- clicking or double-clicking the poster title opens the full-paper modal.

Method focus cards keep their `data-section="method-1"…"method-N"` identities.
Use a card's own alignment entry when present; otherwise its hover/double-click
interaction opens the canonical `method` video, blog, and slides. Highlight the
actual clicked card, including under poster scaling and historical raster
overlays. Do not rename cards or invent subsection clips to make them clickable.

The modal must use the section-media layout: video with baked Bottom Bar
subtitles on the left, blog on the right, EN/中文 switching, slide thumbnails
below the video, and a draggable splitter. Do not replace this with a Poster / Slides / Video /
Blog tabbed viewer. A tabbed viewer is a regression because it drops the
section-level interaction contract.

Video seekability is part of the contract, not a hosting detail. The modal's
video progress bar and slide thumbnails must actually seek playback. Serve and
test reels with the Range-capable paper2reel server below; do not use
`python -m http.server` as a passing preview or QA environment because it may
answer MP4 Range requests with `200 OK` instead of `206 Partial Content`.

The viewer is intentionally template-locked. Treat
`assets/section_modal_contract.json` as the golden UI contract distilled from
the hand-tuned Attention reel: fixed section-modal template, hidden
topbar by default, `v/h/a/s/d` shortcuts, debug opacity slider, baked subtitle
playback, download menu, draggable splitter, slide thumbnails, EN/CN blog
panes, and timeline-backed section clips. Do not ask an agent to redesign this HTML. The
builder may only fill data into the fixed template and copy self-contained
assets.

## Inputs And Outputs

For a full bundle, paper2reel must read the same v2 outputs that are delivered
to the user:

```text
<poster_outdir>/                       # poster.html, poster.pdf/png/pptx, manifest.json, assets/
<blog_outdir>/                         # blog_zh.docx, blog_en.docx, manifest.json, assets/
<video_outdir>/                        # video*.mp4, manifest.json, assets/
```

Do not build a reel from stale example files or old `exports/` folders. The
viewer and all timeline-backed clips must use the final
`<video_outdir>/video.mp4`, whose subtitles are baked into the appended black
Bottom Bar. Do not attach the VTT sidecar in the Reel viewer; doing so would
duplicate text already present in every video frame.

Build the user-facing viewer directly in a v2 reel bundle:

```text
<reel_outdir>/
  reel.html
  content_alignment.json
  manifest.json
  assets/
    poster/
    media/
    slides/
    blog/
    meta/
      reel_downloads.json
    downloads/                           # materialized mode only
```

This directory must be self-contained enough to serve locally: `reel.html`
and `content_alignment.json` sit at the bundle root; poster/video/slides/blog
assets sit under `assets/`. Do not copy only `reel.html`.

## Poster + Slides Base Viewer

From the repo root:

```bash
python .agents/skills/rs-paper2reel/scripts/build_poster_slides_view.py \
  --poster-dir <poster_outdir> \
  --slides-dir <slide_png_or_svg_dir> \
  --script-json <optional_audio_script_json> \
  --section-slide-map <optional_section_slide_map.json> \
  --blog-outline-en <blog_outdir>/assets/meta/outline_en.json \
  --blog-outline-zh <blog_outdir>/assets/meta/outline_zh.json \
  --blog-figures-dir <blog_outdir>/assets/figures \
  --download-poster-dir <poster_outdir> \
  --download-blog-dir <blog_outdir> \
  --download-video-dir <video_outdir> \
  --download-mode materialized \
  --outdir <reel_outdir>
```

The script writes:

```text
<viewer_outdir>/
  reel.html
  content_alignment.json
  manifest.json
  assets/
    poster/
    poster.html
      assets/
        figures/
        fonts/
        logos/
        qr/
        audio/
    slides/
      slide_01.png
      ...
    blog/
      figures/
        ...
    meta/
      reel_downloads.json
    downloads/                       # materialized mode only
      all_final.zip
      poster_final.zip
      blog_final.zip
      video_final.zip
```

`reel.html` keeps the poster in an iframe so its own interactions
remain intact. The wrapper only observes section clicks and applies transient
highlighting. Slides are copied as image frames for stable scrolling and
highlighting.

When paper2blog outlines are available, pass both language outlines and the
figure directory. The builder will copy blog figures into `blog/figures/` and
store section-level EN/CN blocks in `content_alignment.json`; the browser gate
requires those blocks.

When download directories are provided, the builder always writes
`assets/meta/reel_downloads.json` with schema
`paper2reel.downloads.v1`. Its `archives` object contains exactly `all`,
`poster`, `video`, and `blog`; every archive declares `label`, `filename`, and
deduplicated `files` entries with bundle-relative POSIX `path`, ZIP `arcname`,
and exact byte `size`.

Download delivery has two explicit modes:

- `materialized` is the standalone default. It preserves
  `assets/downloads/{all,poster,video,blog}_final.zip` and full `file://`
  download behavior.
- `on_demand` writes no persistent ZIP. It uses relative
  `__download__/{all,poster,video,blog}` links, which `serve_reel.py` resolves
  from the manifest and streams as temporary ZIP responses. Direct `file://`
  opening hides these online-only links.

Both modes exclude `.claude/`, nested download directories, backups, and
internal files. The Video archive contains `video.pptx`, `video.mp4`, optional
caption sidecars, and a root `README.txt` pointing editors to PPTX2Video.
Historical manifests without that README remain valid; download servers inject
the canonical note into `video_final.zip` without rewriting the old bundle.
New manifests mark `all_package_version: paper2reel.all.v2`; their
All archive is instead a self-contained offline Reel containing `reel.html`,
`content_alignment.json`, the Reel runtime under `assets/poster`,
`assets/media`, `assets/slides`, `assets/blog`, `assets/ui`, and `assets/fonts`,
plus the final Poster PDF/PPTX, Video MP4/PPTX, and EN/CN Blog DOCX files. It
does not duplicate the root `poster.html` or `poster.png`, and it excludes
build/cache trees and nested ZIPs. Historical manifests without
`all_package_version` retain the original deduplicated-union behavior and
remain downloadable. Use `on_demand` for Portal jobs and `materialized` for
standalone offline bundles unless the caller explicitly chooses otherwise.

## Timeline-Backed Section Media

When paper2video has produced `timeline.json`, use it as the source of truth
for modal video clips, slide clips, and section timing. Do not cut
section videos from guessed MP4 timestamps. The section clips should be composed
from complete timeline slide clips and end with a short silent freeze tail, so
the modal does not stop mid-motion or mid-thought.

```bash
python .agents/skills/rs-paper2reel/scripts/build_section_media_from_timeline.py \
  --viewer-dir <reel_outdir> \
  --timeline <video_outdir>/assets/meta/timeline.json \
  --video <video_outdir>/video.mp4 \
  --allow-burned-subtitle-video \
  --section-tail-seconds 0.9
```

This updates:

```text
<viewer_outdir>/content_alignment.json
<viewer_outdir>/reel.html   # inline ALIGNMENT refreshed when present
<viewer_outdir>/assets/media/video.mp4   # final playback copy with baked Bottom Bar
<viewer_outdir>/assets/media/clips/<section>.mp4
<viewer_outdir>/assets/media/slide_clips/slide-XX.mp4
```

The deterministic Reel bootstrap passes `--allow-burned-subtitle-video` to
declare that the selected source is the final Bottom Bar render. In this mode
the builder records `burned_bottom_bar` for both video source and caption
delivery and does not expose a sidecar CC track.

`timeline.json` must already contain the explicit section mapping. If the deck
uses slide ids instead of canonical poster ids, build the timeline with
`python -m pptx2video.build_timeline --section-map ...` first.

## Required Hard Gate

After building the base viewer and timeline-backed media, run the reel
package checker. This is a required gate, not an optional smoke test:

```bash
python .agents/skills/rs-paper2reel/scripts/check_reel_package.py \
  <reel_outdir> \
  --browser \
  --file-browser \
  --screenshot <reel_outdir>/assets/meta/previews/reel_browser_gate.png \
  --report <reel_outdir>/assets/meta/reports/reel_qa_report.json
```

The checker must pass before marking paper2reel complete. It validates
that the delivered viewer is the section-modal UI, not the stale tabbed viewer,
and confirms in a real browser that default poster-only view, shortcuts,
double-click section modal, baked-subtitle video clip, slide thumbnails, and
blog text work. It also verifies MP4 byte-range support and exercises real
video seeking: clicking a later slide thumbnail must move `sectionVideo` to the
thumbnail timestamp, and direct progress-bar style seeking must succeed for
both full-video and section-clip playback.

The same final `reel.html` must also support direct local opening with
`file://` or a double-click. In direct-open mode the viewer embeds the copied
poster HTML through `iframe.srcdoc`, sets the poster base URL to
`assets/poster/`, localizes poster render resources such as MathJax under
`assets/poster/`, and preserves the baked Bottom Bar while the section modal,
poster hover, shortcuts, blog pane, slide-thumbnail seeking, and direct video
seeking remain usable without starting a server. This is a user-facing feature
parity path, not an HTTP protocol replacement: `file://` has no HTTP 206 Range
headers, so `--browser` remains required for Range/seek validation and
`--file-browser` separately validates the direct-open runtime.

The checker reads `assets/section_modal_contract.json`. Missing any required
golden-contract feature is a blocking ERROR: shortcut handlers, debug slider,
paper2poster's native debug bbox/size overlay, the golden download pill with
icon and `All | Poster | Video | Blog` links, section-rail hover styling,
section clips with baked Bottom Bar subtitles, absence of duplicate sidecar
tracks, blog images, or the fixed template/version markers.

Download QA follows the manifest's explicit `delivery` field. In
`materialized` mode it validates the four ZIPs using the existing archive
boundaries. In `on_demand` mode it rejects persisted ZIPs, validates every
manifest path, classification, source file, and byte size, checks the
deduplicated All union, and probes each dynamic endpoint with HTTP HEAD.

If the checker fails, treat it as an agent repair task first: fix the viewer and
rerun the gate. Do not mark the stage `PASS` and do not ask the user to catch it
by visually inspecting the page.

For human preview, start the same Range-capable server used by the browser gate:

```bash
python .agents/skills/rs-paper2reel/scripts/serve_reel.py <reel_outdir> --port 8900
```

Open `http://127.0.0.1:8900/reel.html`. The preview is not considered faithful
unless video requests return `206 Partial Content` for Range requests.
For `on_demand` bundles this server also implements
`/__download__/{all,poster,video,blog}` and creates each ZIP only for the
request; it does not write archives into the bundle.

For quick local sharing, users may also double-click `<reel_outdir>/reel.html`.
Do not remove the `assets/` folder or copy only the HTML file; direct-open mode
still depends on the v2 bundle folder structure.

## Output Manifest

`<reel_outdir>/manifest.json` must include `"layout": "v2-assets"` and
root-relative paths for `reel.html`, `content_alignment.json`,
`assets/poster/`, `assets/media/`, `assets/slides/`, `assets/blog/`, and
`assets/meta/reel_downloads.json`. Materialized bundles also index
`assets/downloads/`. Keep QA screenshots and reports under
`assets/meta/previews/` and `assets/meta/reports/`.

If required inputs are missing or the viewer cannot load a needed artifact,
record an `ERROR` in the QA report/manifest and stop. Do not silently build a
partial viewer that hides missing poster, video, slides, or blog content.

## Bootstrap From PDF Or Incomplete Bundle

When the user invokes `paper2reel` with a PDF, arXiv/link input, or an
incomplete v2 bundle, first inspect the shared bundle and decide which upstream
stages are already complete. Missing stages must be completed by their full
skills before the reel is assembled:

```text
paper2assets -> paper2poster -> paper2blog -> paper2video -> paper2reel
```

Use the bootstrap helper for the inspection and for the deterministic final
assembly:

```bash
python .agents/skills/rs-paper2reel/scripts/build_reel_from_paper.py <paper.pdf-or-bundle> --dry-run
```

Then follow its stage report:

- If `paper2assets` is missing `paper_spec.md`, run the complete
  `paper2assets` skill. Do not treat `extract_pdf.py` output alone as a
  paper2assets package, because Step 4 is model-driven.
- If only `manifest.json`, `assets/meta/sections.json`, or
  `assets/meta/narration.json` is missing while `paper_spec.md`, `text.txt`,
  `figures.json`, and `metadata.json` already exist, the helper may refresh
  those deterministic package files with `--run-missing`.
- If `paper2poster` is missing, run the complete `paper2poster` skill,
  including the measured fill loop, render/export, html2pptx handoff, and
  deliverable gate.
- If `paper2blog` is missing, run the complete bilingual `paper2blog` skill,
  including real EN/CN outlines, DOCX generation, figure embedding, and the
  blog QA gate.
- If `paper2video` is missing, run the complete `paper2video` skill, including
  ppt-master, audio, timeline, captions, visual highlights, `video.mp4`,
  `video_no_subtitles.mp4`, `video.pptx`, and the video QA gate.
- When all upstream stages pass, let the helper assemble the reel:

  ```bash
  python .agents/skills/rs-paper2reel/scripts/build_reel_from_paper.py \
    <paper.pdf-or-bundle> \
    --run-missing \
    --download-mode materialized
  ```

  Portal callers must pass `--download-mode on_demand`. After the staged Reel
  is synchronized into the final shared bundle, the helper rebuilds the
  manifest against that final bundle and removes any historical
  `assets/downloads/` directory.

The helper builds the viewer in a temporary staging directory and then copies
only the reel deliverables back into the v2 bundle. This avoids the
`build_poster_slides_view.py --outdir` clean step from deleting existing
poster, blog, video, or paper2assets outputs. It preserves the v2 contract:
`reel.html` and `content_alignment.json` at the bundle root, with reel support
assets under `assets/poster/`, `assets/media/`, `assets/slides/`,
`assets/blog/`, plus `assets/meta/reel_downloads.json`; only materialized mode
adds `assets/downloads/`.

If the helper reports a blocked stage, stop and complete that named full skill
stage. Do not write a simplified poster, video, blog outline, slide image, or
HTML page to make the reel checker pass.

## Alignment Rules

Prefer explicit section ids from `paper2assets`:

- `title`
- `problem`
- `motivation`
- `contribution`
- `method`
- `dataset-benchmark`
- `key-result`
- `ablation-study`
- `headline-numbers`
- `takeaway`
- paper-specific custom ids such as `failure-modes-limitations`

For slides, pass a `script.json` when available. The script's `sections[*].id`
and order provide slide identity without embedding metadata in the PPTX.

If automatic slide matching is weak, pass an override JSON:

```json
{
  "method": [4, 5],
  "key-result": [7, 9],
  "takeaway": [10]
}
```

Use the override with:

```bash
python .agents/skills/rs-paper2reel/scripts/build_poster_slides_view.py \
  --poster-dir <paper2poster_outdir> \
  --slides-dir <slide_png_or_svg_dir> \
  --script-json <script.json> \
  --section-slide-map <map.json> \
  --outdir <viewer_outdir>
```

