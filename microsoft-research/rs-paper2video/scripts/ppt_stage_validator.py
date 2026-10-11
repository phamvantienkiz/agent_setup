"""Structured validation for Paper2Video's PPT-Master and pptx2video handoff.

PPT-Master may phrase an automatically resolved direction differently in its
receipt, design specification, and execution lock. The validator therefore
checks concrete locked fields and semantic agreement instead of requiring one
generated sentence to be copied verbatim between artifacts.

It also audits the final rendered PPTX's native `p:timing` tree directly, so
the resolved `ppt_trigger` handoff (`on-click` or `after-previous`) is
verified against the delivered file instead of trusting either child skill's
own default.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Sequence
from pathlib import Path

from ppt_options_contract import PPT_TRIGGER_HANDOFF_VALUES


_AUDIENCE_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "for",
        "following",
        "of",
        "the",
        "to",
        "work",
    }
)
_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
_SPEC_LOCK_COLOR_KEYS = {
    # PPT-Master spec-lock/v1 uses bg/text. The longer names are accepted for
    # historical Paper2Video projects and older confirmation-UI receipts. A
    # few generated locks used ``body`` in the colors section (mirroring the
    # typography size key); it is unambiguous there, so retain it as a narrow
    # compatibility alias while requiring new locks to emit ``body_text``.
    "background": ("bg", "background"),
    "primary": ("primary",),
    "accent": ("accent",),
    "body_text": ("text", "body_text", "body"),
}


def spec_lock_value(lock_text: str, section: str, key: str) -> str:
    """Read one scalar from PPT-Master's markdown execution lock."""
    section_match = re.search(
        rf"(?ms)^##\s+{re.escape(section)}\s*$\n(.*?)(?=^##\s+|\Z)",
        lock_text,
    )
    if not section_match:
        return ""
    row = re.search(
        rf"(?m)^-\s+{re.escape(key)}:\s*(.+?)\s*$",
        section_match.group(1),
    )
    return row.group(1).strip().strip("\"'") if row else ""


def design_table_value(design_text: str, item: str) -> str:
    """Read a two-column value from a markdown table in design_spec.md."""
    wanted = _normalize_text(item)
    for line in design_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [
            cell.strip().strip("*`")
            for cell in line.strip().strip("|").split("|")
        ]
        if len(cells) >= 2 and _normalize_text(cells[0]) == wanted:
            return cells[1].strip()
    return ""


def _spec_lock_alias_value(
    lock_text: str,
    section: str,
    semantic_role: str,
    keys: Sequence[str],
) -> str:
    """Resolve one schema role without silently accepting conflicting aliases."""
    found = [
        (key, spec_lock_value(lock_text, section, key))
        for key in keys
    ]
    found = [(key, value) for key, value in found if value]
    if not found:
        return ""
    distinct = {value.casefold() for _, value in found}
    if len(distinct) != 1:
        detail = ", ".join(f"{key}={value}" for key, value in found)
        raise RuntimeError(
            "PPT-Master spec_lock.md has conflicting aliases for "
            f"{semantic_role}: {detail}"
        )
    return found[0][1]


def _normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.findall(r"[^\W_]+", text, flags=re.UNICODE))


def _audience_tokens(value: str) -> set[str]:
    tokens = set(_normalize_text(value).split()) - _AUDIENCE_STOP_WORDS
    if "ml" in tokens:
        tokens.update({"machine", "learning"})
    if "ai" in tokens:
        tokens.update({"artificial", "intelligence"})
    return tokens


def _material_audience_overlap(left: str, right: str) -> bool:
    left_tokens = _audience_tokens(left)
    right_tokens = _audience_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    overlap = left_tokens & right_tokens
    return len(overlap) >= min(2, len(left_tokens), len(right_tokens))


def _contains_normalized(haystack: str, needle: str) -> bool:
    normalized_needle = _normalize_text(needle)
    return bool(normalized_needle) and normalized_needle in _normalize_text(haystack)


def _positive_number(value: str) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def audit_descriptive_options(
    applied: dict,
    opts: dict,
    lock_text: str,
    design_text: str,
) -> None:
    """Verify audience, typography, and color against executable PPT locks.

    Explicit choices must be copied exactly into the applied-options receipt
    and be recorded in the generated design/lock. Auto choices may be worded
    differently, but must resolve to mutually consistent structured values in
    both design_spec.md and spec_lock.md.
    """
    requested_audience = str(opts.get("ppt_audience") or "").strip()
    applied_audience = str(applied.get("target_audience") or "").strip()
    locked_audience = spec_lock_value(lock_text, "communication", "audience")
    designed_audience = design_table_value(design_text, "Target Audience")
    if not applied_audience:
        raise RuntimeError("PPT-Master did not resolve a target audience")
    if not locked_audience or not designed_audience:
        raise RuntimeError(
            "PPT-Master audience is missing from spec_lock.md or design_spec.md"
        )
    if requested_audience:
        if applied_audience != requested_audience:
            raise RuntimeError("PPT-Master target audience does not match the request")
        if not (
            _contains_normalized(locked_audience, requested_audience)
            or _contains_normalized(designed_audience, requested_audience)
        ):
            raise RuntimeError(
                "PPT-Master did not record the requested target audience in its design lock"
            )
    elif not (
        _material_audience_overlap(applied_audience, locked_audience)
        and _material_audience_overlap(locked_audience, designed_audience)
    ):
        raise RuntimeError(
            "PPT-Master Auto target audience is inconsistent across its receipt and design lock"
        )

    requested_typography = str(opts.get("ppt_typography") or "").strip()
    applied_typography = str(applied.get("typography_direction") or "").strip()
    font_family = spec_lock_value(lock_text, "typography", "font_family")
    body_size = spec_lock_value(lock_text, "typography", "body")
    title_size = spec_lock_value(lock_text, "typography", "title")
    if not applied_typography:
        raise RuntimeError("PPT-Master did not resolve a typography direction")
    if not font_family or not _positive_number(body_size) or not _positive_number(title_size):
        raise RuntimeError(
            "PPT-Master spec_lock.md is missing executable typography values"
        )
    primary_font = font_family.split(",", 1)[0].strip().strip("\"'")
    if not _contains_normalized(design_text, primary_font):
        raise RuntimeError(
            "PPT-Master design_spec.md does not match the font in spec_lock.md"
        )
    if requested_typography:
        if applied_typography != requested_typography:
            raise RuntimeError(
                "PPT-Master typography direction does not match the request"
            )
        if not _contains_normalized(design_text, requested_typography):
            raise RuntimeError(
                "PPT-Master did not record the requested typography direction in design_spec.md"
            )
    elif not _contains_normalized(applied_typography, primary_font):
        raise RuntimeError(
            "PPT-Master Auto typography receipt does not match the font locked in its design"
        )

    requested_color = str(opts.get("ppt_color") or "").strip()
    applied_color = str(applied.get("color_direction") or "").strip()
    locked_colors = {
        role: _spec_lock_alias_value(
            lock_text,
            "colors",
            role,
            keys,
        )
        for role, keys in _SPEC_LOCK_COLOR_KEYS.items()
    }
    if not applied_color:
        raise RuntimeError("PPT-Master did not resolve a color direction")
    invalid_color_roles = [
        role
        for role, value in locked_colors.items()
        if not _HEX_COLOR.fullmatch(value)
    ]
    if invalid_color_roles:
        raise RuntimeError(
            "PPT-Master spec_lock.md is missing or has invalid executable HEX "
            "color roles: " + ", ".join(invalid_color_roles)
        )
    missing_design_colors = [
        value
        for value in locked_colors.values()
        if value.casefold() not in design_text.casefold()
    ]
    if missing_design_colors:
        raise RuntimeError(
            "PPT-Master design_spec.md does not match the colors in spec_lock.md"
        )
    if requested_color:
        if applied_color != requested_color:
            raise RuntimeError("PPT-Master color direction does not match the request")
        if not _contains_normalized(design_text, requested_color):
            raise RuntimeError(
                "PPT-Master did not record the requested color direction in design_spec.md"
            )
    else:
        receipt_color_count = sum(
            value.casefold() in applied_color.casefold()
            for value in locked_colors.values()
        )
        if receipt_color_count < 2:
            raise RuntimeError(
                "PPT-Master Auto color receipt does not describe the palette locked in its design"
            )


def normalize_export_flag_tokens(
    raw: str | Sequence[object] | None,
) -> list[str]:
    """Normalize either grouped or tokenized JSON export flags."""
    if isinstance(raw, str):
        chunks = [raw]
    elif isinstance(raw, Sequence):
        chunks = [str(item).strip() for item in raw if str(item).strip()]
    else:
        return []

    tokens: list[str] = []
    try:
        for chunk in chunks:
            tokens.extend(shlex.split(chunk))
    except ValueError:
        return []
    return tokens


def audit_export_flags(applied_raw: object, expected_flags: Sequence[str]) -> None:
    """Require the exact svg_to_pptx options, independent of JSON grouping."""
    applied_tokens = normalize_export_flag_tokens(applied_raw)  # type: ignore[arg-type]
    expected_tokens = normalize_export_flag_tokens(expected_flags)
    if applied_tokens != expected_tokens:
        raise RuntimeError(
            f"PPT-Master export flags mismatch: expected {list(expected_flags)}, "
            f"got {applied_tokens}"
        )


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
_SLIDE_XML_RE = re.compile(r"ppt/slides/slide(\d+)\.xml")

# Maps the resolved `ppt_trigger` handoff value (see
# `ppt_options_contract.resolve_ppt_trigger_handoff`) to the lowercase native
# `p:cTn/@nodeType` every non-With-Previous Animation Pane row must carry in
# the final rendered PPTX.
_EXPECTED_NATIVE_TRIGGER = {
    "on-click": "clickeffect",
    "after-previous": "aftereffect",
}


def _slide_xml_parts(pptx_path: Path) -> list[tuple[str, bytes]]:
    """Return every slide XML part, ordered by its numeric slide filename."""
    with zipfile.ZipFile(pptx_path) as archive:
        numbered = [
            (int(match.group(1)), name)
            for name in archive.namelist()
            for match in (_SLIDE_XML_RE.fullmatch(name),)
            if match
        ]
        numbered.sort(key=lambda item: item[0])
        return [(name, archive.read(name)) for _, name in numbered]


def _row_native_trigger(row: ET.Element) -> str:
    """Return the lowercase native trigger of one Animation Pane row.

    A row's trigger lives on the inner ``p:cTn`` whose ``presetClass`` is the
    entrance or emphasis effect itself (``entr``/``emph``), not on the row's
    own outer wrapper node.
    """
    for node in row.iter(f"{{{P_NS}}}cTn"):
        if node.get("presetClass") in ("entr", "emph"):
            return str(node.get("nodeType") or "").lower()
    return ""


def _slide_click_groups(slide_xml: bytes) -> list[list[str]] | None:
    """Return one slide's top-level click groups as lists of row triggers.

    Returns ``None`` when the slide has no ``p:timing`` main sequence at all
    (no entrance/emphasis animation authored on that slide).
    """
    root = ET.fromstring(slide_xml)
    main_sequence = root.find(f".//{{{P_NS}}}cTn[@nodeType='mainSeq']")
    if main_sequence is None:
        return None
    child_list = main_sequence.find(f"{{{P_NS}}}childTnLst")
    if child_list is None:
        return []
    groups: list[list[str]] = []
    for group in child_list.findall(f"{{{P_NS}}}par"):
        outer_ctn = group.find(f"{{{P_NS}}}cTn")
        row_list = (
            outer_ctn.find(f"{{{P_NS}}}childTnLst")
            if outer_ctn is not None
            else None
        )
        row_pars = row_list.findall(f"{{{P_NS}}}par") if row_list is not None else []
        groups.append([_row_native_trigger(row) for row in row_pars])
    return groups


def _non_with_previous_triggers(groups: list[list[str]]) -> list[str]:
    """Return every ``clickEffect``/``afterEffect`` native trigger on a slide.

    A ``witheffect`` row rides on its group leader's start time and never
    gets its own Animation Pane badge, so it carries no independent trigger
    decision to audit. This intentionally includes every such row in a
    group, not only the first: a preserved (non-normalized) ``after-previous``
    cascade can hold several ``afterEffect`` rows in one native click group,
    and each one is still a trigger decision that must match the resolved
    handoff.
    """
    return [
        trigger
        for group in groups
        for trigger in group
        if trigger != "witheffect"
    ]


def audit_final_pptx_trigger(pptx_path: str | Path, expected_ppt_trigger: str) -> None:
    """Verify the delivered PPTX's native triggers match the resolved handoff.

    This parses the final rendered ``video.pptx``'s own ``p:timing`` tree --
    the exact structure PowerPoint's Animation Pane reads -- instead of
    trusting a JSON report or letting ppt-master and pptx2video each keep
    their own default. ``expected_ppt_trigger`` must be the value paper2video
    resolved once with ``ppt_options_contract.resolve_ppt_trigger_handoff``
    and handed to both ppt-master's ``--animation-trigger`` and pptx2video's
    ``--click-group-policy``; this function closes the loop by proving the
    delivered file actually carries that trigger end to end.

    - ``on-click`` requires every non-With-Previous row to be a native
      ``clickEffect``. That is what gives a downloaded PPTX a continuous
      ``1..N`` Animation Pane badge sequence.
    - ``after-previous`` requires every non-With-Previous row, including
      every row inside a preserved cascade, to be a native ``afterEffect``.
      That is what makes the PPTX auto-play in PowerPoint, with no numbered
      Pane guaranteed.

    Slides with no ``p:timing`` main sequence (no entrance/emphasis
    animation on that slide) are skipped; they carry no trigger to check. If
    the whole deck has no animated slide at all, this raises: paper2video
    only calls this audit for a project that requested animated entrances,
    so a fully static deliverable is itself a silent-degrade failure, not a
    pass-by-vacuity.
    """
    expected_ppt_trigger = str(expected_ppt_trigger or "").strip().lower()
    if expected_ppt_trigger not in PPT_TRIGGER_HANDOFF_VALUES:
        raise RuntimeError(
            "expected_ppt_trigger must be one of "
            f"{list(PPT_TRIGGER_HANDOFF_VALUES)}, got {expected_ppt_trigger!r}"
        )
    expected_trigger = _EXPECTED_NATIVE_TRIGGER[expected_ppt_trigger]

    pptx_path = Path(pptx_path)
    if not pptx_path.is_file():
        raise RuntimeError(f"final PPTX not found for trigger audit: {pptx_path}")

    mismatches: list[str] = []
    animated_slide_count = 0
    for name, slide_xml in _slide_xml_parts(pptx_path):
        groups = _slide_click_groups(slide_xml)
        if groups is None:
            continue
        slide_triggers = _non_with_previous_triggers(groups)
        if not slide_triggers:
            continue
        animated_slide_count += 1
        bad_triggers = sorted({t for t in slide_triggers if t != expected_trigger})
        if bad_triggers:
            mismatches.append(
                f"{name}: expected every non-With-Previous native trigger to be "
                f"{expected_trigger!r}, found {bad_triggers}"
            )

    if animated_slide_count == 0:
        raise RuntimeError(
            "Final PPTX has no native p:timing entrance/emphasis animation on "
            "any slide, so the resolved ppt_trigger handoff "
            f"({expected_ppt_trigger!r}) cannot be verified. If animation was "
            "not actually requested for this deck, do not call this audit; "
            "otherwise ppt-master silently dropped the requested animation."
        )
    if mismatches:
        raise RuntimeError(
            "Final PPTX native animation triggers do not match the resolved "
            f"ppt_trigger handoff ({expected_ppt_trigger!r} requires every "
            f"non-With-Previous row to be {expected_trigger!r}):\n"
            + "\n".join(mismatches)
        )


def _cli_audit_final_pptx_trigger(argv: list[str] | None = None) -> int:
    """CLI entry point: audit a delivered PPTX against the resolved ppt_trigger.

    This is the only sanctioned way to verify the final `video.pptx` the
    `/pptx2video` handoff returns. It exists so the check is one concrete,
    non-optional command in `SKILL.md` instead of a described-but-skippable
    Python call: a paper2video run is not complete until this command exits
    0 against the exact `--ppt-trigger` value that was sent to both
    ppt-master and pptx2video.
    """
    parser = argparse.ArgumentParser(
        prog="ppt_stage_validator.py audit-final-pptx-trigger",
        description=(
            "Parse the delivered video.pptx's native p:timing tree and fail "
            "unless every non-With-Previous Animation Pane row matches the "
            "resolved ppt_trigger handoff."
        ),
    )
    parser.add_argument("pptx_path", help="Path to the delivered video.pptx")
    parser.add_argument(
        "--ppt-trigger",
        required=True,
        choices=list(PPT_TRIGGER_HANDOFF_VALUES),
        help=(
            "The ppt_trigger value resolved earlier by "
            "ppt_options_contract.py resolve-ppt-trigger for this run."
        ),
    )
    args = parser.parse_args(argv)
    try:
        audit_final_pptx_trigger(args.pptx_path, args.ppt_trigger)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"OK: every non-With-Previous native trigger in {args.pptx_path} "
        f"matches ppt_trigger={args.ppt_trigger!r}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] != "audit-final-pptx-trigger":
        print(
            "usage: ppt_stage_validator.py audit-final-pptx-trigger "
            "<video.pptx> --ppt-trigger {on-click,after-previous}",
            file=sys.stderr,
        )
        return 2
    return _cli_audit_final_pptx_trigger(argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
