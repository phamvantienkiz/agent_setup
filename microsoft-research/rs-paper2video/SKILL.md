---
name: rs-paper2video
description: Turn a research paper, paper2assets package, or PPT deck into a narrated 1080p walkthrough MP4 video with synced bottom-bar subtitles, laser spotlight cues, and editable PPTX. Uses ppt-master and pptx2video with imageio-ffmpeg. STOPS to present video deliverable for review.
allowed-tools: Bash, Read, Write, Edit, Grep, Glob
metadata:
  framework: Microsoft Research Studio (HITL Edition)
  phase: "Post-Paper Dissemination (Walkthrough Video)"
---

# paper2video - paper/assets -> ppt-master deck -> pptx2video render -> narrated MP4

`paper2video` is a thin orchestrator with exactly one supported path. It does
not author slides itself, does not synthesize audio itself, does not
composite video itself, and does not gate QA itself. It resolves inputs and
one shared trigger decision, then fully delegates:

```text
paper.pdf
  -> .agents/skills/rs-paper2assets/scripts/build_package.py       (shared package)
  -> assets/meta/paper_spec.md + assets/meta/narration.json
  -> ppt_options_contract.py resolve-ppt-trigger          (ONE trigger decision)
  -> installed ppt-master skill                          (full workflow, receives the trigger)
  -> installed pptx2video skill / CLI `bootstrap` then `render` (full workflow, receives the trigger)
  -> ppt_stage_validator.py audit-final-pptx-trigger      (proves the handoff held)
  -> video.mp4, video_no_subtitles.mp4, video.pptx
```

**There is only one route.** An earlier version of this skill had a second,
self-implemented "Route A" that called private narration, duration, and
visual-cue scripts and invoked `python -m pptx2video.render_video` /
`pptx2video.build_timeline` / `pptx2video.check_video_package` as if they were
importable submodules of the installed public package. Those modules do not
exist at that import path in the public `pptx2video` CLI; the entry
points are the `pptx2video render`, `pptx2video doctor`, and `pptx2video
bootstrap` subcommands. Do not recreate that shortcut. Do not hand-assemble a
narration script, a visual-cue file, or a "simplified" render pipeline that
skips the installed `pptx2video` skill. Do not invoke any private submodule
path under `pptx2video.*`. Every render goes through `/pptx2video` (the
installed skill) or the exact `pptx2video render` CLI invocation in Step 5;
there is no lower-effort fallback for a rushed or low-context session.

## Why full delegation is mandatory

`pptx2video render` is not a smoke-test wrapper. Its own CLI (`cli.py`
`_render()`) always runs the QA pass and always writes
`assets/meta/reports/video_qa_report.json`; there is no `--no-qa` flag and no
way to skip the check itself. A hand-rolled call into an internal module could
skip that gate entirely, which is why every render goes through the Step 5
command.

**The strict gate is opt-in, and Step 5 opts in.** Upstream `pptx2video`
defaults `--qa-mode` to `warn-only`, which delivers a bundle despite blocking
warnings — the right default for previews and demos, the wrong one for a
Paper2Video deliverable. Step 5 therefore passes `--qa-mode strict`
explicitly. Never drop that flag to make a failing render succeed: a blocking
warning means the deck is not deliverable, and the repair belongs in
ppt-master (Step 3) or the narration, not in the gate. Treat a non-zero exit
as a blocking failure to fix, never as a reason to relax the mode or fall back
to a simpler local script.

## Two child skills, one shared trigger decision

This skill's own job is narrow: resolve inputs, resolve one `ppt_trigger`
value, pass it identically to both child skills, and verify the delivered
PPTX actually carries it. Everything else belongs to the child skills:

- **`ppt-master`** authors the deck: SVG pages, the Strategist confirmation
  stage, speaker notes, and PPTX export including native entrance-animation
  triggers (`--animation-trigger`).
- **`pptx2video`** renders the deck: TTS, word-boundary timing, animation
  scheduling, subtitles, timeline, and strict media QA
  (`assets/meta/reports/video_qa_report.json`).

Both read PowerPoint's native `p:timing` tree, but for different purposes:
ppt-master writes it, and pptx2video's video scheduler reads native row order
and narration timing from it, never the click-group number. If each of these
two skills is allowed to pick its own default trigger, they can produce a
PPTX/MP4 pair whose native badges and playback pacing quietly disagree. This
skill's Step 2 exists specifically to prevent that.

### The four concepts the old protocol conflated

The single native `p:timing` tree has to answer four different questions, and
the previous version of this skill's protocol used only one field
(click-group number) to try to answer all of them, which fails whenever a
deck uses `after-previous`:

| Concept | What it means | Where it lives | Whose default wins |
|---|---|---|---|
| `effect_order` | Real entrance-animation sequence, 1..N, independent of trigger type | Native Animation Pane row order (`p:cTn` order inside `mainSeq`) | Fixed by authoring order; never inferred from click-group number |
| `ppt_trigger` | The one user-facing intent: `on-click` or `after-previous` | Resolved once by this skill's `resolve-ppt-trigger` command | This skill, not ppt-master's own CLI default, not pptx2video's own CLI default |
| `click_group` | PowerPoint's own derived click-group badge, shown in the Animation Pane UI | Computed by PowerPoint/pptx2video's `--click-group-policy` from trigger topology | A side effect, never a source of truth |
| `video_start` | When a phase plays in the rendered MP4 | pptx2video's narration/timeline scheduler, keyed to `effect_order` plus word-boundary timing | pptx2video's renderer; click-group number is never consulted |

The failure this fixes: a deck with 38 `after-previous` effects is fully
valid OOXML, but PowerPoint places every `after-previous` (automatic) effect
in the same native click group, commonly all showing `0` in the Animation
Pane's click-group column. That is expected PowerPoint behavior for automatic
effects, not data loss and not a rendering bug; `effect_order` (Pane row
order) still exists and is exactly what pptx2video's scheduler uses to place
each phase in the video's timeline, together with narration/word timing. The
problem in the old protocol was documentation and verification, not the
underlying render: nothing told the agent to pick `ppt_trigger` on purpose
before authoring, hand it to both children identically, and check the
delivered file. This skill's Step 2 and Step 6 close exactly that gap.

## Paths

Run Paper2Video workflow commands from `ResearchStudio-Reel/` unless noted.

```bash
PAPER2VIDEO=.agents/skills/rs-paper2video
PAPER2ASSETS=.agents/skills/rs-paper2assets
```

Install both external skills before starting. Do not clone or vendor either
dependency inside ResearchStudio:

```bash
npx skills add hugohe3/ppt-master --skill ppt-master
npx skills add ai-nuts/pptx2video --skill pptx2video
```

Install and verify the public `pptx2video` CLI runtime. Use a Python 3.11 or
newer environment, and track the upstream default branch — this is the install
form `pptx2video`'s own SKILL.md documents:

```bash
python -m pip install \
  'pptx2video[svg] @ git+https://github.com/ai-nuts/pptx2video.git'
python -m playwright install chromium
python3 -m pptx2video --version
python3 -m pptx2video doctor --svg
```

**Always invoke the runtime as `python3 -m pptx2video ...`, never as the bare
`pptx2video` command.** A host may have an older `pptx2video` (for example
`0.3.0`) earlier on `PATH` than the intended install; the bare command then
silently resolves to the wrong version with no error. Compare `python3 -m
pptx2video --version` against `pip show pptx2video`; when they disagree, fix
the environment (`pip install` target, `PATH`, virtualenv) before continuing,
rather than proceeding and hoping the CLI surface still matches this
document.

**Track the upstream default branch; do not pin a release tag.** `pptx2video`
ships features between tags, so a tag pin silently withholds them from every
paper2video user. Reinstall from the default branch to pick up upstream
fixes.

Do not hard-code a host-specific skill directory. Users may run this
repository from Codex, Claude Code, a shell, or another agent. This skill
itself never calls a private path under `pptx2video.*`; it always calls the
installed skill (`/pptx2video`) or the public `pptx2video render` /
`pptx2video doctor` / `pptx2video bootstrap` CLI subcommands.

## Output Contract

Follow the shared paper2assets v2 layout. The bundle top level holds only
deliverable files plus `manifest.json`; everything else lives under `assets/`:

```text
<video_outdir>/
  video.mp4                  # required, burned-in subtitles in an appended black bottom band
  video_no_subtitles.mp4     # required, raw/pre-subtitle playback copy for paper2reel
  video.pptx                 # required, the same delivered deck pptx2video rendered from
  manifest.json              # schema_version "paper2video.v1", layout "v2-assets"
  assets/
    audio/                          # script.json, per-block TTS, word timings
    captions/                       # video.srt, video.vtt
    slides/                         # rendered slide frames used by the MP4
    clips/                          # raw render intermediate
    meta/                           # timeline.json, QA and authority reports
```

This layout, and every file inside it, is produced by `pptx2video render`
itself; Step 5 below is the only place this skill writes into
`<video_outdir>`. Do not hand-assemble any part of this tree before that step.

**Pick `<video_outdir>` before any file writes.** Resolve deterministically:

1. **An explicit `<video_outdir>` argument from the caller wins.** Honor it
   verbatim; the defaults below only fire when no path was passed.
2. **A `paper2assets` package already exists** -> reuse its folder verbatim as
   `<video_outdir>`. The canonical detection signal is
   `<dir>/assets/meta/paper_spec.md`; `<dir>/manifest.json` with
   `"layout": "v2-assets"` is a confirming hint when present.
3. **Otherwise (a bare PDF is the only input)** -> default to
   `<input_pdf_dir>/<pdf_stem>/`, matching the `paper2assets` default
   convention so a later `paper2assets` run lands in the same bundle.

`pptx2video render` refuses to write into a path that already exists, so Step
5 renders into a fresh temporary bundle for exactly this reason and then this
skill promotes the result into `<video_outdir>` (see Step 5).

## Step 1: Build or reuse the shared paper2assets package

```bash
python .agents/skills/rs-paper2assets/scripts/build_package.py <paper.pdf> --outdir "$VIDEO_OUT"
```

If `paper_spec.md` already exists, sync structured claims and narration
instead of re-extracting:

```bash
python .agents/skills/rs-paper2assets/scripts/build_package.py <paper.pdf> \
  --outdir "$VIDEO_OUT" \
  --skip-extract \
  --paper-spec "$VIDEO_OUT/assets/meta/paper_spec.md"
```

`assets/meta/narration.json` is the canonical narration order for this run:
one `{"id", "heading", "text"}` entry per section, in the same order poster,
blog, and video all use. Do not reorder or rewrite it here; ppt-master reads
the paper2assets package to author slides in this order, and Step 4 passes
narration to pptx2video from the same source.

## Step 2: Resolve the one shared `ppt_trigger` decision

This is the single most important step in this skill. Resolve `ppt_trigger`
**before** invoking ppt-master, and pass the exact same resolved value to both
ppt-master and pptx2video. Never let either child skill fall back to its own
independent default.

```bash
python3 .agents/skills/rs-paper2video/scripts/ppt_options_contract.py resolve-ppt-trigger \
  --ppt-trigger {auto,on-click,after-previous}
```

- Omit `--ppt-trigger`, or pass `auto`, when the user has not stated a
  preference. This resolves to `on-click`, because a downloaded PPTX with a
  continuous `1..N` Animation Pane badge sequence is the more broadly useful
  default deliverable, and the rendered MP4 still auto-plays with no manual
  click either way (see below).
- Pass `on-click` explicitly when the user wants a presenter-controllable,
  numbered PPTX.
- Pass `after-previous` only when the user explicitly asks for a PPTX that
  also auto-plays natively in PowerPoint (not merely "a video that plays
  itself" -- the rendered MP4 always plays itself regardless of this choice).

The command prints one JSON object; treat every field as a literal value to
carry into the next two steps, not as a suggestion:

```json
{
  "ppt_trigger": "on-click",
  "ppt_master_animation_trigger": "on-click",
  "pptx2video_click_group_policy": "normalize"
}
```

```json
{
  "ppt_trigger": "after-previous",
  "ppt_master_animation_trigger": "after-previous",
  "pptx2video_click_group_policy": "preserve"
}
```

`ppt_master_animation_trigger` is the exact value for ppt-master's
`--animation-trigger` flag in Step 3. `pptx2video_click_group_policy` is the
exact value for pptx2video's `--click-group-policy` flag in Step 5. Both come
from this one command so the two child skills can never disagree about the
user's trigger intent. Record the printed JSON (for example into
`$VIDEO_OUT/assets/meta/ppt_trigger_handoff.json`) so Step 6's audit and any
retry use the same resolved value.

**Why the rendered MP4 auto-plays either way.** pptx2video's video scheduler
places every entrance phase in the timeline using native Animation Pane row
order (`effect_order`) plus narration/word-boundary timing; it never consults
PowerPoint's click-group number. Choosing `on-click` changes only what the
downloaded PPTX looks like when a human opens it in PowerPoint. It does not
make the MP4 wait for a click.

## Step 3: Author the deck with ppt-master, passing the resolved trigger

Invoke the installed `ppt-master` skill and follow its full workflow: source
conversion, project init/import, the Strategist confirmation stage (fields a
through h, MANDATORY, cannot be skipped), optional image acquisition,
sequential page-by-page SVG authoring, `svg_quality_checker.py`, then the
three-command export pipeline run one command at a time
(`total_md_split.py`, `finalize_svg.py`, `svg_to_pptx.py`).

- Do not replace ppt-master with handwritten SVG, a local simplified
  generator, or a copied example deck whose content does not come from the
  paper.
- If ppt-master reaches a blocking confirmation gate and the user has not
  already approved defaults, stop and ask the user.
- If a machine dependency is missing, record the concrete missing dependency
  and stop. Do not silently degrade to a different slide-generation method.
- Pass `$PAPER_ASSETS/assets/meta/narration.json` sections (or the paper/PDF
  content directly) as the source content; do not invent claims absent from
  the paper.

Pass ppt-master's `--animation-trigger` flag exactly as
`resolve_ppt_trigger_handoff` returned in Step 2:

```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path> \
  --animation-trigger <ppt_master_animation_trigger from Step 2>
```

If the deck should carry no entrance animation at all (`-a none`, ppt-master's
own default), the `--animation-trigger` flag is irrelevant and may be omitted;
the resolved value only matters once `-a` requests an actual entrance effect.
Leave speaker notes enabled (ppt-master's default; do not pass `--no-notes`)
so Step 4 can replace its raw Notes with pptx2video's canonical per-element
protocol -- see the note on notes format below.

**ppt-master Notes are not pptx2video's Notes protocol.** ppt-master's
`markdown_to_plain_text()` writes plain presenter-note paragraphs, not
pptx2video's canonical `## [handle] semantic` block grammar. pptx2video treats
ordinary presenter notes as absent narration and falls back to a generic
per-shape handle. Do not render an animated raw ppt-master PPTX directly.
Step 4 first bootstraps the page-level narration into handle-addressed Notes
and Alt Text.

Before invoking ppt-master, prepare title-slide utility assets when a
`paper2assets` package exists:

```bash
python .agents/skills/rs-paper2assets/scripts/fetch_logos.py \
  --outdir "$PAPER_ASSETS" --from-spec "$PAPER_ASSETS/assets/meta/paper_spec.md" || true
python .agents/skills/rs-paper2assets/scripts/make_qr.py \
  --outdir "$PAPER_ASSETS" --from-metadata "$PAPER_ASSETS/assets/meta/metadata.json" || true
```

Skip `fetch_logos.py` when `paper_spec.md` is not available; do not invent
logos. `make_qr.py` is best-effort and only uses `paper_url`, `code_url`, or
the documented `arxiv_id` fallback from `metadata.json`. Add a requirement
block to the ppt-master prompt covering restrained placement of these assets
on slide 1 (right-side title area or lower-right safe zone), and instruct
ppt-master to omit unavailable assets cleanly rather than leaving broken
placeholders.

Confirm the export produced a PPTX at `<project_path>/exports/<name>.pptx`
before continuing to Step 4.

## Step 4: Prepare narration and bootstrap the editable protocol

Build a `script.json` from the shared `narration.json` so pptx2video's
narration authority is explicit and does not depend on ppt-master's raw Notes
text:

```json
{
  "sections": [
    {"id": "problem", "heading": "Problem", "text": "..."},
    {"id": "method", "heading": "Method", "text": "..."}
  ]
}
```

`assets/meta/narration.json` from paper2assets already has this
`{"id", "heading", "text"}` shape; it can be used directly as the
`bootstrap --script-json` input provided its section count matches the PPTX
slide count. The number of sections in this file must equal the number of
slides in the deck exported in Step 3, in the same order; pptx2video rejects a
section-count mismatch. When ppt-master's page-count resolution produced a
different number of slides than `narration.json` has sections, reconcile the
two before rendering: either regenerate the deck at the corrected page count,
or edit the `script.json` copy so its section count and order match the
delivered PPTX exactly. Do not truncate or duplicate sections to force a
match.

Bootstrap the ordinary animated deck once. This divides each slide's
page-level narration across its animation targets and writes canonical
handle-addressed Notes and Alt Text:

```bash
PPTX2VIDEO_WORK=$(mktemp -d)
PPTX2VIDEO_SOURCE="$PPTX2VIDEO_WORK/video-protocol-source.pptx"
PPTX2VIDEO_TMP="$PPTX2VIDEO_WORK/video-bundle"
python3 -m pptx2video bootstrap \
  "<project_path>/exports/<name>.pptx" \
  --script-json "$VIDEO_AUDIO/script.json" \
  --output "$PPTX2VIDEO_SOURCE"
```

Treat a non-zero bootstrap exit as blocking. Do not replace
`$PPTX2VIDEO_SOURCE` with the raw ppt-master export in Step 5.

## Step 5: Render through pptx2video, passing the same resolved trigger

Render the bootstrapped PPTX into the fresh output directory. Pass the
page-level script only as `--ids-from-script`: this preserves the per-element
narration written in Step 4 while fixing each slide's internal `section_id`.
Do not use `--script-json` for this render; it would put the entire slide
transcript on the first animation element while clearing the others.

```bash
python3 -m pptx2video render \
  "$PPTX2VIDEO_SOURCE" \
  "$PPTX2VIDEO_TMP" \
  --resolution 1080p \
  --ids-from-script "$VIDEO_AUDIO/script.json" \
  --animation-order-policy animation-pane \
  --click-group-policy <pptx2video_click_group_policy from Step 2> \
  --qa-mode strict
```

- `--click-group-policy` must be the exact value Step 2 resolved
  (`normalize` for `on-click`, `preserve` for `after-previous`). Never omit
  this flag and rely on pptx2video's own CLI default; the CLI default
  (`normalize`) silently overwrites a deliberately authored `after-previous`
  cascade into a click-driven deck, which is the opposite of what an explicit
  `after-previous` request means.
- `--animation-order-policy animation-pane` makes the run fully
  non-interactive and deterministic. pptx2video's own `auto` default only
  prompts when `stdin` is a TTY; in a non-interactive agent session with an
  actual ordering conflict it exits 3 without rendering. Passing
  `animation-pane` explicitly confirms "trust the deck's own Animation Pane
  order" up front so a real conflict never stalls the run silently.
- Do not pass `--no-subtitles` unless the user explicitly disabled captions;
  the default burns captions into `video.mp4` while leaving
  `video_no_subtitles.mp4` and the VTT/SRT sidecars intact.
- Do not pass `--baseline-pptx` / `--narration-mode regenerate` for a first
  render; those are for an explicit re-render of a previously delivered deck.

**Do not add `--no-qa`.** It does not exist on the top-level `pptx2video
render` CLI. QA always runs and always writes
`assets/meta/reports/video_qa_report.json`; `--qa-mode` only decides which
findings fail the render. Under the `strict` mode this step passes,
`cli.py`'s own `_render()` raises `SystemExit` unless the checker reported
`passed`, which blocks on every error and every non-exempt warning. Codes the
checker exempts (currently `audio_extra_files`, an unreferenced MP3 left over
from a previous run) stay visible in the report without blocking. A non-zero
exit here is a blocking failure: fix the deck, script, or flags and rerun this
exact command; do not relax `--qa-mode` and do not fall back to a private
render path to force a result through.

On success, promote the fresh bundle into `<video_outdir>` without clobbering
an existing `manifest.json` from a different paper2* skill sharing the same
bundle root:

```bash
rsync -a --exclude=manifest.json "$PPTX2VIDEO_TMP"/ "$VIDEO_OUT"/
```

If `$VIDEO_OUT/manifest.json` already exists (written by `paper2assets`,
`paper2poster`, or `paper2blog` sharing the same bundle root), merge
`$PPTX2VIDEO_TMP/manifest.json`'s video-specific fields into it by hand
instead of overwriting; do not let a blind copy erase fields another
paper2* skill wrote to the same `manifest.json`. Otherwise, copy pptx2video's
`manifest.json` in as-is.

## Step 6: Audit the final PPTX against the resolved trigger (MANDATORY gate)

This closes the loop the old protocol never checked: prove the delivered
`video.pptx`'s native `p:timing` tree actually carries the trigger this skill
resolved in Step 2, rather than trusting that ppt-master's flag and
pptx2video's flag each did the right thing.

```bash
python3 .agents/skills/rs-paper2video/scripts/ppt_stage_validator.py audit-final-pptx-trigger \
  "$VIDEO_OUT/video.pptx" \
  --ppt-trigger <ppt_trigger from Step 2>
```

- `on-click` requires every non-With-Previous native row to be `clickEffect`;
  this is what gives a downloaded PPTX a continuous `1..N` Animation Pane
  badge sequence.
- `after-previous` requires every non-With-Previous native row, including
  every row inside a preserved cascade, to be `afterEffect`; this is what
  makes the PPTX auto-play natively in PowerPoint. No numbered Pane is
  claimed or required for this choice.
- The audit raises if the delivered deck has no native `p:timing` animation
  on any slide at all, so a silently-dropped animation request fails loudly
  instead of passing by vacuity.

A non-zero exit here is a blocking failure, exactly like a failed
`video_qa_report.json` in Step 5: it means ppt-master's `--animation-trigger`
and pptx2video's `--click-group-policy` disagreed about the trigger, or one
of them fell back to its own default instead of the value resolved in Step 2.
Re-check the flags actually passed in Step 3 and Step 5 against Step 2's
printed JSON, fix whichever command diverged, and re-render before reporting
the video as done.

## Step 7: Report

Tell the user the absolute paths of the deliverables:

- `<video_outdir>/video.mp4` (burned-in subtitles)
- `<video_outdir>/video_no_subtitles.mp4` (paper2reel source)
- `<video_outdir>/video.pptx` (editable deck, the same file the Step 6 audit
  verified)
- `<video_outdir>/assets/meta/timeline.json` and
  `<video_outdir>/assets/meta/reports/video_qa_report.json`

State explicitly which `ppt_trigger` was used and confirm Step 6's audit
passed. Do not report the task done without having run and passed both
Step 5's QA gate and Step 6's trigger audit.

## Acceptance criteria

- Downloaded PPTX Animation Pane shows a continuous `1..N` badge sequence
  when `ppt_trigger=on-click` was resolved and used.
- The rendered video auto-plays every phase in an order that matches the
  spoken narration, regardless of which `ppt_trigger` was used.
- When the user explicitly requested `after-previous`, the delivered PPTX
  still auto-plays natively in PowerPoint, without a claim of continuous
  native numbering.
- `ppt_stage_validator.py audit-final-pptx-trigger` exits 0 against the exact
  `ppt_trigger` resolved in Step 2.
- `pptx2video render`'s own QA gate (`video_qa_report.json`) reported
  `passed` under `--qa-mode strict`: no errors, and no warnings outside the
  checker's own exempt list.

## Key rules

- One route only. Every render goes through `/pptx2video` or the exact
  `pptx2video render` CLI command in Step 5; never a private
  `pptx2video.<module>` import, never a hand-rolled narration/timeline/QA
  substitute.
- One trigger decision. Step 2 resolves `ppt_trigger` exactly once per run;
  Step 3 and Step 5 both consume that same resolved JSON, never their own
  child-skill default.
- QA gate passing is not the finish line by itself. A passing
  `video_qa_report.json` proves pptx2video's own render was clean; it does
  not prove the trigger handoff held. Step 6's audit is the check that
  proves that, and it is mandatory before reporting completion.
- Do not degrade silently. A missing dependency, a blocked ppt-master
  confirmation gate, a failed QA report, or a failed trigger audit are all
  stop-and-fix conditions, never a reason to ship a simplified or unverified
  video.

## Tools

```
scripts/
├── ppt_options_contract.py   # resolve-ppt-trigger CLI; also the shared PPT option/appearance contract
└── ppt_stage_validator.py    # audit-final-pptx-trigger CLI; also descriptive-option/export-flag audits
```

The generic render runtime is not owned or vendored by this skill. Install
`pptx2video` and invoke it only through `/pptx2video` or
`python3 -m pptx2video {doctor,render,bootstrap}`.

## References

- `references/pptx2video.md` - the standalone renderer's install steps, the
  exact CLI flags this skill's Step 5 command relies on, and the pitfalls
  (PATH, `--no-qa` not existing, click-group-policy defaults) that make an
  almost-right invocation silently diverge from the protocol.
- `references/script_json_schema.md` - the `script.json` schema Step 4
  passes to `bootstrap` and Step 5 passes only as `--ids-from-script`,
  including the handle-level `elements` form and TTS text gotchas.
- `references/ppt_trigger_handoff.md` - deep dive on the four-concept model,
  the native OOXML mechanics behind it, and the failure modes this skill's
  Step 2/Step 6 close.


