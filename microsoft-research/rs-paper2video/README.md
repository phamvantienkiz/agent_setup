# paper2video

> Turn a paper's shared assets into a narrated research walkthrough video: editable PPTX, subtitle-ready MP4, no-subtitle MP4 for reels, and timeline metadata, without breaking alignment between slides, audio, captions, and sections.

`paper2video` is the **video rendering stage** of the ResearchStudio pipeline. It reuses the `<outdir>/` bundle produced by [`paper2assets`](../paper2assets/) so the video uses the same section claims, figures, numbers, logos, QR codes, and narration source as `paper2poster` and `paper2blog`. It fully delegates deck authoring to the installed `ppt-master` skill and fully delegates rendering, subtitles, timeline assembly, and strict media QA to the installed `pptx2video` skill and its public CLI.

```
paper2assets  --->  ppt-master  --->  pptx2video render  --->  paper2reel
  <outdir>/          deck + notes     video.mp4                no-subtitle video + timeline
                                      video.pptx
```

## Why one route, not two

There is exactly one supported path: `paper2assets` for narration, `ppt-master` for the deck, `pptx2video render` for everything else. This skill never calls a private `pptx2video.<module>` import and never hand-assembles a narration, visual-cue, or QA substitute. `pptx2video render`'s own CLI reads `assets/meta/reports/video_qa_report.json` after every render and exits non-zero unless it passed with zero errors and zero warnings, and the CLI does not even expose a flag to skip that check. Routing every render through the real `pptx2video render` command (or `/pptx2video`) is what keeps an agent from quietly cutting corners under time pressure.

## Input

Either:

- a `paper2assets` `<outdir>/` containing `manifest.json` and `assets/meta/paper_spec.md`;
- a raw paper PDF, which is resolved to the same `<pdf_stem>/` bundle convention and completed through `paper2assets` first.

## Output

The bundle root holds only deliverables plus `manifest.json`, next to `assets/`:

| File | What it is |
|---|---|
| `video.mp4` | Final H.264/AAC video with burned-in subtitles in an appended black bottom band |
| `video_no_subtitles.mp4` | Required raw playback copy for `paper2reel`, so the reel CC toggle does not double-subtitle the video |
| `video.pptx` | The exact deck `pptx2video` rendered from, verified against the resolved trigger handoff |
| `assets/audio/*.{mp3,json}` | Per-block narration, script JSON, and word timings |
| `assets/captions/{video.srt,video.vtt}` | Subtitle sidecars used for burn-in and reel captions |
| `assets/slides/` | Rendered slide frames used by the MP4 |
| `assets/clips/` | Raw render intermediate |
| `assets/meta/` | Timeline, QA report, and authority reports |

This entire tree is produced by `pptx2video render` itself and then promoted into `<outdir>/`; this skill never writes it by hand.

## The ppt-master to pptx2video trigger handoff

The most important contract this skill owns is a single `ppt_trigger` decision (`on-click` or `after-previous`), resolved once and handed identically to both child skills:

- `effect_order` (the real 1..N animation sequence) always comes from native Animation Pane row order, independent of trigger type.
- `ppt_trigger` is the one user-facing choice this skill resolves with `ppt_options_contract.py resolve-ppt-trigger`.
- `click_group` is PowerPoint's own derived badge number; it is a side effect of `ppt_trigger`, never a source of truth. An `after-previous` deck commonly shows every automatic effect in click group `0` in PowerPoint's native panel; that is expected OOXML behavior, not data loss.
- `video_start` (when a phase plays in the MP4) comes from pptx2video's narration/timeline scheduler, keyed to `effect_order` and word-boundary timing. It never consults the click-group number, so the rendered video auto-plays in the correct order regardless of which `ppt_trigger` was chosen.

`ppt_stage_validator.py audit-final-pptx-trigger` parses the delivered `video.pptx`'s native `p:timing` tree and fails unless every row matches the resolved trigger, so the handoff is verified against the actual file, not assumed from either child skill's own default.

## Usage

Install the two external skills in order, then install and verify the public `pptx2video` CLI runtime. The runtime requires Python 3.11 or newer:

```bash
npx skills add hugohe3/ppt-master --skill ppt-master
npx skills add ai-nuts/pptx2video --skill pptx2video
python -m pip install \
  'pptx2video[svg] @ git+https://github.com/ai-nuts/pptx2video.git'
python -m playwright install chromium
python3 -m pptx2video --version
python3 -m pptx2video doctor --svg
```

Install from the upstream default branch rather than a release tag: `pptx2video` ships features between tags, and a tag pin silently withholds them. Always invoke the runtime as `python3 -m pptx2video ...`, never the bare `pptx2video` command; a stale `pptx2video` earlier on `PATH` silently resolves to the wrong version otherwise. Compare `python3 -m pptx2video --version` against `pip show pptx2video` when they might disagree.

From a Claude Code session:

```text
# point at the shared paper2assets bundle
> /paper2video ./my_paper/

# or start from a raw PDF; the skill resolves the same bundle root first
> /paper2video ./my_paper.pdf

# render an existing or edited deck through the installed standalone skill directly
> /pptx2video ./edited.pptx
```

The package is not complete until `video.mp4`, `video_no_subtitles.mp4`, `video.pptx`, `assets/meta/timeline.json`, a passing `video_qa_report.json`, and a passing `audit-final-pptx-trigger` check are all present.

## How it works

1. **Resolve one bundle root**, the same `<outdir>/` used by `paper2assets`, `paper2poster`, and `paper2blog`.
2. **Resolve one `ppt_trigger` decision** with `ppt_options_contract.py resolve-ppt-trigger`, before ppt-master runs.
3. **Delegate deck authoring to ppt-master**, passing the resolved trigger to its `--animation-trigger` flag. The skill must run the full ppt-master workflow, not a hand-written shortcut deck.
4. **Prepare narration** as a `script.json` built from the shared `assets/meta/narration.json`, with a section count matching the deck's slide count.
5. **Delegate rendering to `pptx2video render`**, passing the same resolved trigger to its `--click-group-policy` flag, then promote the fresh bundle into `<outdir>/`.
6. **Audit the delivered PPTX** with `ppt_stage_validator.py audit-final-pptx-trigger` to prove the handoff held end to end.
7. **Report** absolute paths for every deliverable, the resolved trigger used, and confirmation that both the QA gate and the trigger audit passed.

## Requirements

- Python >= 3.11
- Installed `ppt-master` and `pptx2video` skills
- `pptx2video` CLI runtime from `ai-nuts/pptx2video` default branch, installed with the `svg` extra
- Playwright Chromium installed with `python -m playwright install chromium`
- A passing `python3 -m pptx2video doctor --svg` check
- LibreOffice, Poppler, FFmpeg / FFprobe
- Edge TTS by default, synthesized automatically by `pptx2video render`

## More detail

[`SKILL.md`](SKILL.md) is the authoritative, agent-facing spec: the single supported route, the trigger-handoff protocol, and the mandatory QA and audit gates. The [`references/`](references/) folder documents the `script.json` schema, the trigger handoff deep dive, and the standalone `pptx2video` CLI flag reference.
