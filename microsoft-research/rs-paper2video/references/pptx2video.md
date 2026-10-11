# Standalone pptx2video CLI reference

Paper2Video delegates every render to the independently maintained
[`ai-nuts/pptx2video`](https://github.com/ai-nuts/pptx2video) skill and its
public CLI. This skill does not copy or vendor that package's runtime,
and it never imports a private `pptx2video.<module>` path. This file lists the
exact flags Step 5 of `SKILL.md` relies on and the pitfalls that make an
almost-right invocation silently diverge from the protocol.

## Install once per environment

```bash
npx skills add hugohe3/ppt-master --skill ppt-master
npx skills add ai-nuts/pptx2video --skill pptx2video
python -m pip install \
  'pptx2video[svg] @ git+https://github.com/ai-nuts/pptx2video.git'
python -m playwright install chromium
python3 -m pptx2video --version
python3 -m pptx2video doctor --svg
```

## The PATH trap: always use `python3 -m pptx2video`

A host can have an older `pptx2video` earlier on `PATH` than the intended
install. The bare `pptx2video` command then silently resolves to that
older version with no error; it does not fail, it just renders with a
different, incompatible flag surface. Compare `python3 -m pptx2video
--version` against `pip show pptx2video` when they might disagree. Every
command in this file and in `SKILL.md` uses
`python3 -m pptx2video`, never the bare `pptx2video` binary, for exactly this
reason.

## The bootstrap and render commands Steps 4-5 use

```bash
PPTX2VIDEO_WORK=$(mktemp -d)
PPTX2VIDEO_SOURCE="$PPTX2VIDEO_WORK/video-protocol-source.pptx"
PPTX2VIDEO_TMP="$PPTX2VIDEO_WORK/video-bundle"
python3 -m pptx2video bootstrap \
  "<project_path>/exports/<name>.pptx" \
  --script-json "$VIDEO_AUDIO/script.json" \
  --output "$PPTX2VIDEO_SOURCE"

python3 -m pptx2video render \
  "$PPTX2VIDEO_SOURCE" \
  "$PPTX2VIDEO_TMP" \
  --resolution 1080p \
  --ids-from-script "$VIDEO_AUDIO/script.json" \
  --animation-order-policy animation-pane \
  --click-group-policy <pptx2video_click_group_policy from Step 2>
```

`<PPTX2VIDEO_TMP>` (the `output` positional argument) must not already exist;
the CLI refuses to write into an existing path.

## Flags this skill's protocol depends on, and why

- **`--click-group-policy {normalize,preserve}` (no default assumed here).**
  The CLI's own default is `normalize`. This skill never relies on that
  default: it always passes the exact value
  `ppt_options_contract.py resolve-ppt-trigger` printed in Step 2
  (`normalize` for `on-click`, `preserve` for `after-previous`). Passing
  `normalize` when the user asked for `after-previous` silently rewrites a
  deliberately authored click-free cascade into a numbered click-driven deck,
  which is the opposite of the request. This is the single most important
  flag in the whole handoff; never omit it and never let it fall back to the
  CLI default.
- **`--animation-order-policy {auto,animation-pane,reading-order}`, default
  `auto`.** Pass `animation-pane` explicitly. The CLI's own `auto` default
  only prompts interactively when `stdin` is a TTY; in a non-interactive
  agent session with an actual Animation-Pane-versus-narration-order conflict,
  `auto` (and `reading-order`) exit `3` without producing a bundle at all,
  and print a decision report path instead of rendering. `animation-pane`
  confirms up front "trust the deck's own Animation Pane order," so a real
  conflict is resolved deterministically instead of stalling the run.
- **`bootstrap --script-json PATH`.** Supplies page-level narration while
  converting ppt-master's ordinary animated deck into canonical per-element
  Notes and Alt Text. Run this once before rendering.
- **`render --script-json PATH`.** Replaces the PPTX's narration authority.
  Do not pass a page-level script after bootstrap: `apply_user_script()` puts
  the whole slide transcript on the first block and clears the other blocks.
  Use this render flag only for an explicitly handle-addressed
  `sections[*].elements` override.
- **`--ids-from-script PATH`.** Fixes each slide's `section_id` to this file's
  `sections[*].id`, in order without replacing block narration. Pass the same
  file used by bootstrap. This makes pptx2video's own
  section-count/section-id validation pass automatically; do not hand-build a
  separate id-mapping file.
- **`--resolution {720p,1080p,1440p,4k}`, default `1080p`.** Pass `1080p`
  explicitly for a predictable, documented default; do not silently rely on
  whatever the installed CLI version happens to default to.
- **`--qa-mode {strict,warn-only}`, upstream default `warn-only`. Always pass
  `strict` explicitly for Paper2Video delivery.** QA always runs and always
  writes `assets/meta/reports/video_qa_report.json`; this flag only decides
  which findings fail the render. `warn-only` fails on `error` findings but
  delivers the bundle despite blocking warnings — correct for previews and
  demos, wrong for a Paper2Video deliverable. `strict` additionally fails on
  any non-exempt warning, which is the gate this skill's Step 5 depends on.
  There is still no `--no-qa` flag and no way to skip the QA pass itself; a
  hand-rolled call into an internal module remains the only way to bypass it,
  which is exactly why this skill forbids calling any internal module directly
  (see `SKILL.md`'s "Why full delegation is mandatory").
- **Do not pass `--baseline-pptx` / `--narration-mode regenerate` for a first
  render.** Those flags exist for an explicit later re-render of a previously
  delivered deck against a new edited PPTX; they are irrelevant to Step 5's
  first pass.
- **`--no-subtitles`.** Omit it unless the user explicitly disabled captions.
  The default burns captions into `video.mp4` in an appended black bottom
  band while leaving `video_no_subtitles.mp4` and the `.srt`/`.vtt` sidecars
  untouched, which is what `paper2reel` expects downstream.

## Full flag surface (from `pptx2video render --help`)

```
pptx2video render <pptx> <output>
  --resolution {720p,1080p,1440p,4k}      default 1080p
  --fps FPS                               default 30
  --voice VOICE                           Edge TTS voice, default en-US-AriaNeural
  --rate RATE                             Edge TTS rate, default +0%
  --tts-cache-dir DIR | --no-tts-cache
  --ids-from-script PATH
  --script-json PATH
  --baseline-pptx PATH
  --narration-mode {keep,regenerate}      default keep
  --narration-order-policy {geometry,author-notes}   default geometry
  --regeneration-model MODEL              default gpt-5.6-sol
  --highlight-style {box,spotlight,cursor,box_cursor,spotlight_cursor,
                      laser,box_laser,spotlight_laser}  default spotlight_laser
  --animation-order-policy {auto,animation-pane,reading-order}  default auto
  --animation-order-sequence [SLIDE=]ORDER  (repeatable)
  --animation-order-report PATH
  --semantic-profile {concise,detailed}   default concise
  --click-group-policy {normalize,preserve}  default normalize
  --no-subtitles
  --keep-temp
  --qa-mode {strict,warn-only}            default warn-only
```

There is no `--no-qa` flag on this list; see above. `--qa-mode` changes which
findings block, never whether QA runs.

## Verify dependencies before rendering

```bash
python3 -m pptx2video doctor --svg
```

Checks Python, native rendering (LibreOffice, Poppler, FFmpeg/FFprobe), and
SVG dependencies (Playwright plus a system or bundled Chromium). Fix whatever
`doctor` reports before running Step 5; do not proceed past a failing
`doctor` check by assuming the render will still work.

## Where narration audio actually comes from

`pptx2video render` synthesizes all narration audio itself, automatically,
using Edge TTS (`generate_edge_audio.py`, default voice
`en-US-AriaNeural`). Paper2Video does not pre-synthesize any MP3 and does not
pass a `--voice` flag by default. Bootstrap distributes the page-level
`script.json` text into the PPTX protocol; render then speaks that preserved
per-element protocol. See `references/script_json_schema.md` for the exact
schema.

## Advanced authoring surface

For direct manual edits to an already-rendered deck (handle-level Notes/Alt
Text markers or `--baseline-pptx` re-renders), use the installed
`/pptx2video` skill directly and read its own
`references/cli.md` and `references/editable_pptx.md`. Those flows are
outside this skill's one supported route (paper -> ppt-master -> `bootstrap`
-> `render`); this skill's Step 5 command above is the only render invocation
this skill's protocol issues.
