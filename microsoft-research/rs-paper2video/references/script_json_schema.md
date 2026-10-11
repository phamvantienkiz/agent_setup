# script.json - schema, authority, and gotchas

`script.json` is the narration authority Step 4 of `SKILL.md` builds from the
shared `assets/meta/narration.json`. Step 4 passes it to `pptx2video
bootstrap`; Step 5 passes it to `pptx2video render` only as
`--ids-from-script`. This preserves the handle-addressed narration embedded by
bootstrap instead of applying a second page-level override.

## Minimal shape (section-level narration)

```json
{
  "sections": [
    {"id": "problem", "heading": "Problem", "text": "Prior work assumes..."},
    {"id": "method",  "heading": "Method",  "text": "We propose a two-stage..."}
  ]
}
```

`assets/meta/narration.json` produced by `paper2assets` already has this
exact `{"id", "heading", "text"}` shape per section, so it can be used
directly as this file, provided its section count matches the deck's slide
count (see "Section count and order must match the PPTX" below).

## What pptx2video actually reads from this file

- **`sections` (required, top-level, must be a non-empty list).** Every other
  top-level key is ignored by `apply_user_script()`. A stray `voice`, `model`,
  or `edge_voice` key at the top level does nothing; TTS voice selection is a
  `pptx2video render --voice` CLI flag, not a `script.json` field. Do not
  carry over legacy OpenAI-TTS-style `voice: "alloy"` fields from an older
  version of this document; they have no effect on the render.
- **`sections[*].id` (required, string, one per PPTX slide, in slide order).**
  Must equal that slide's `section_id` exactly, or pptx2video raises. Pass this
  file as `--ids-from-script` during render so pptx2video assigns each slide's
  `section_id` from the same list bootstrap consumed. Do not build a separate
  id-mapping file for this.
- **`sections[*].heading`.** Cosmetic; used only in the assembled report
  metadata. Not spoken.
- **`sections[*].text`.** The spoken narration for the whole slide. Plain
  text; do not include markdown syntax (`**bold**`, `` `code` ``, list
  bullets) or literal code, since Edge TTS reads that syntax literally rather
  than rendering it, and speaking a code block aloud is rarely useful.
  Ending a section with sentence-final punctuation gives the TTS engine a
  natural prosodic drop instead of a flat trail-off. Bootstrap distributes
  this text across native animation targets. Never pass this page-level shape
  to `render --script-json` after bootstrap: that override assigns all text to
  the first block and clears the remaining blocks.
- **`sections[*].elements` (optional, replaces `text` for that section when
  present).** For precise per-shape timing, address individual top-level
  shapes by their stable handle instead of narrating the whole slide as one
  block:

  ```json
  {
    "sections": [
      {
        "id": "results",
        "elements": [
          {
            "handle": "latency-card",
            "script": "The card appears. [[Spotlight] Notice the lower latency.]"
          }
        ]
      }
    ]
  }
  ```

  `handle` must match a handle pptx2video's protocol extraction already
  assigned to a top-level shape or group on that slide (inspect the deck's
  Notes/Alt Text or a prior render's `timeline.json` to find valid handles).
  `script` is spoken text that may contain at most the `Spotlight` marker;
  `[[Spotlight]]` places a supplemental emphasis cue at that point in the
  narration, and `[[Spotlight] scope text]` additionally marks which spoken
  span the spotlight covers. No other marker name is accepted in a
  user-supplied script; native entrance/exit animation timing comes from the
  PPTX's own `p:timing` tree (see `references/ppt_trigger_handoff.md`), not
  from a script marker.

  This handle-level form is the only safe form for an intentional later
  `render --script-json` override on an animated deck. The normal animated
  Paper2Video path does not need that override because bootstrap already
  persisted the per-element text.

## Section count and order must match the PPTX

The number of `sections` entries must equal the number of slides in the PPTX
Step 3 (ppt-master) exported, in the same order; pptx2video rejects a
mismatch outright. When ppt-master's page-count resolution produced a
different slide count than `narration.json` has sections, reconcile before
rendering: either regenerate the deck at the corrected page count, or edit
the `script.json` copy so its section count and order match the delivered
PPTX exactly. Do not truncate or duplicate sections to force a match.

## Where the audio actually comes from

`pptx2video render` synthesizes every narration MP3 itself, automatically,
using Edge TTS (free, no API key). It does not read pre-rendered audio from
`script.json`, and this skill does not call any separate audio-generation
script before Step 5. See `references/pptx2video.md` for the `--voice` and
`--rate` flags that control that synthesis.

## Divergence from paper2poster's `generate_audio.py` contract

An earlier version of this file described paper2poster's OpenAI-TTS
`generate_audio.py` script JSON (`voice: alloy/echo/fable/onyx/nova/shimmer`,
one MP3 per section written by hand). That is a different tool with a
different contract; `paper2video` does not call `generate_audio.py` and does
not pre-synthesize audio at all. If a user wants poster-style OpenAI TTS
audio for some other purpose, that is `paper2poster`'s own
`scripts/generate_audio.py`, documented in that skill, not this one.
