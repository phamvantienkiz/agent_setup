# The ppt_trigger handoff: four concepts, one native XML tree

This is the deep dive behind `SKILL.md` Step 2 (resolve) and Step 6 (audit).
Read this file when you need to understand *why* the handoff protocol looks
the way it does, not just which commands to run.

## The original symptom this protocol was built to fix

A real run authored a deck with ppt-master's `--animation-trigger
after-previous` and produced 38 native entrance effects, all correctly typed
`afterEffect` in the PPTX's own `p:timing` tree. Opening that deck in
PowerPoint's Animation Pane showed every one of those 38 effects in click
group `0`. The previous version of this skill's protocol treated that `0` as
a bug (data loss, or a broken render) and tried to work around it. It is not
a bug. It is the correct, expected native OOXML representation of "every one
of these effects fires automatically, none of them wait for a mouse click."
The real defect was that the protocol had no vocabulary to say "this deck
intentionally has no click groups" versus "this deck's click groups were
supposed to be numbered and got lost."

## Four concepts, one native XML tree

A slide's `p:timing` tree has to answer four genuinely different questions.
The old protocol used one field, PowerPoint's click-group number, to try to
answer all four, which only works for `on-click` decks and silently breaks
for `after-previous` decks.

| Concept | Question it answers | Where it lives | Who decides it |
|---|---|---|---|
| `effect_order` | In what order do effects fire, 1..N, regardless of trigger type? | XML document order of `p:cTn` nodes inside `mainSeq`; pptx2video's own internal `native_order` field | Author (ppt-master), preserved verbatim by pptx2video |
| `ppt_trigger` | Should a human presenter click to advance each effect, or should PowerPoint auto-advance it? | `p:cTn/@nodeType` on the effect node itself (`clickEffect` vs `afterEffect`) | This skill's Step 2, handed to both children |
| `click_group` | What number does PowerPoint's Animation Pane display next to this effect? | A derived property of how many `par` children sit directly under `mainSeq`'s `childTnLst`; not stored as a number anywhere, PowerPoint computes it from tree shape | A side effect of `ppt_trigger`, never authored directly |
| `video_start` | When does this effect actually play in the rendered MP4? | pptx2video's internal schedule, computed from `effect_order` plus narration/word-boundary timing | pptx2video's scheduler, ignores `click_group` entirely |

## The native XML mechanics

Every native entrance/emphasis effect lives in `mainSeq/childTnLst`, one
`p:par` per top-level click group, each `p:par` holding its own
`childTnLst` of one or more effect rows (`_native_effects()` and
`_main_sequence_row_groups()` in the installed `pptx2video` package's
`editable_pptx.py`). The two facts that matter:

1. **`effect_order` is pure XML document order**, independent of trigger
   type. pptx2video's extractor assigns `native_order = len(effects) + 1` as
   it walks every `p:cTn[@presetClass="entr" or @presetClass="emph"]` node in
   the document, one increment per effect encountered, whether that effect's
   `nodeType` is `clickEffect`, `afterEffect`, or `withEffect`. This is
   exactly the row order PowerPoint's Animation Pane displays top to bottom,
   and it survives regardless of which trigger the deck uses.
2. **`click_group` is a derived count of top-level `par` children**, not an
   attribute stored anywhere. Every `clickEffect` row starts a new top-level
   `par` (a new click group). An `afterEffect` row also starts a new
   sequential phase, but PowerPoint's Animation Pane numbers `afterEffect`
   phases as click group `0` because none of them are gated on an actual
   click; they are all "automatic" from the presenter's point of view, even
   though they still fire in strict `effect_order` one after another. A
   `withEffect` row rides on its own group's leader and never gets an
   independent badge at all. This is why a deck with 38 `afterEffect` rows
   correctly shows 38 rows, all under click group `0`, each still occupying
   its own distinct position in Animation-Pane top-to-bottom order
   (`effect_order`).

## `normalize` versus `preserve`

pptx2video's `--click-group-policy` flag controls
`normalize_animation_click_groups()`, which can rewrite `mainSeq` after
ppt-master has already authored it:

- **`preserve`** leaves the slide's `mainSeq` completely untouched. Whatever
  trigger ppt-master wrote (`clickEffect` or `afterEffect`) survives exactly
  as authored. This is what `after-previous` needs: rewriting nothing is the
  only way to keep a deck that "auto-plays natively in PowerPoint."
- **`normalize`** rewrites every slide so each sequential phase becomes its
  own numbered top-level click group. Concretely, for each phase it builds a
  fresh `p:par` (`_new_numbered_click_group()`), and the first row in this
  phase has its `nodeType` **force-set to `clickEffect`**
  (`effect.set("nodeType", "clickEffect")`), regardless of whatever trigger
  that row originally had. This is the one line of code that makes
  `normalize` dangerous if applied to a deck the user asked to keep
  `after-previous`: it silently converts `afterEffect` rows into
  `clickEffect` rows so that PowerPoint can award them sequential badges.
  That is exactly why `SKILL.md` forbids relying on this flag's own CLI
  default (`normalize`) and instead requires the exact value
  `ppt_options_contract.py resolve-ppt-trigger` printed in Step 2.

This is the direct causal chain: ppt-master's `--animation-trigger` decides
what gets written first; pptx2video's `--click-group-policy` decides whether
that writing survives or gets overwritten. If the two flags disagree, the
one that runs last (pptx2video, since it renders after ppt-master exports)
wins, silently. Passing both from one single resolved decision is the only
way to guarantee they never disagree.

## Why the MP4 auto-plays regardless of `ppt_trigger`

pptx2video's video scheduler (`_schedule_slide_effects()` in
`editable_pptx.py`) sorts every native effect for a slide by
`int(pair[2]["native_order"])`, i.e. by `effect_order`, then places each one
in the timeline using narration/word-boundary timing from the synthesized
Edge TTS audio. It never reads `nodeType`, never reads click-group number,
and never waits for an actual mouse click; "click" triggers in a PPTX have no
meaning inside a rendered video file. This is why the MP4 always auto-plays
in the correct order no matter which `ppt_trigger` was chosen: the video
scheduler's only inputs are `effect_order` and narration timing, both of
which exist and are correct under either trigger choice. Choosing
`ppt_trigger` only changes what a human sees when they later open the
delivered PPTX itself in PowerPoint.

## `resolve_ppt_trigger_handoff()`

`skills/paper2video/scripts/ppt_options_contract.py` owns the single mapping
from user intent to both children's flags:

```python
PPT_TRIGGER_HANDOFF_VALUES = ("on-click", "after-previous")
PPT_TRIGGER_DEFAULT = "on-click"
PPT_TRIGGER_TO_CLICK_GROUP_POLICY = {
    "on-click": "normalize",
    "after-previous": "preserve",
}
```

`resolve_ppt_trigger_handoff({"ppt_trigger": "..."})` accepts `on-click`,
`after-previous`, `auto`, or omitted (the last two both resolve to the
default `on-click`), and returns:

```json
{
  "ppt_trigger": "on-click",
  "ppt_master_animation_trigger": "on-click",
  "pptx2video_click_group_policy": "normalize"
}
```

`ppt_master_animation_trigger` feeds ppt-master's `--animation-trigger`
flag (Step 3). `pptx2video_click_group_policy` feeds pptx2video's
`--click-group-policy` flag (Step 5). ppt-master's own third trigger value,
`with-previous` (simultaneous reveal, no click-group or narration-order
ambiguity to resolve), stays outside this handoff entirely; it is a
lower-level per-element choice ppt-master's own confirmation stage handles
directly, not something paper2video resolves.

## `audit_final_pptx_trigger()`

`skills/paper2video/scripts/ppt_stage_validator.py`'s
`audit-final-pptx-trigger` CLI parses the delivered `video.pptx`'s actual
`p:timing` tree, per slide, and checks every non-With-Previous row's native
`nodeType` against `_EXPECTED_NATIVE_TRIGGER`:

```python
_EXPECTED_NATIVE_TRIGGER = {
    "on-click": "clickeffect",
    "after-previous": "aftereffect",
}
```

`_non_with_previous_triggers()` deliberately includes every row in a
preserved multi-row `after-previous` click group, not only the group's
leader; each row is still an independent trigger decision that must match.
If the whole delivered deck has zero slides with any native `p:timing`
animation at all, the audit raises rather than passing vacuously; a deck
that requested animated entrances and silently got none is a failure, not a
trivial pass. This is why the audit is mandatory (Step 6) even after
pptx2video's own QA report (Step 5) already passed: the QA report proves the
render pipeline ran cleanly, but it says nothing about whether ppt-master's
`--animation-trigger` and pptx2video's `--click-group-policy` actually agreed
about the trigger the user asked for. Only parsing the delivered file's own
native tree proves that.
