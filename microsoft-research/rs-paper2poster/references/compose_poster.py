#!/usr/bin/env python3
"""compose_poster.py — assemble a self-contained poster template from independent axes.

The poster source is decoupled into orientation-aware pieces under <skill>/assets/:

    layouts/<layout>.html   STRUCTURE  — column grid + .section cards + base CSS,
                            with a {{HEADER}} hook in <body> and a {{STYLE_CSS}}
                            hook in <head>.
    styles/<style>.css      VISUAL     — one of the installed card treatments.
    headers*/<header>.html  TITLEBAR   — landscape v1..v7 or Portrait pv1..pv7.

compose(layout, style, header, outpath) reads the layout, injects the style CSS at
{{STYLE_CSS}} and the header HTML at {{HEADER}}, and writes ONE self-contained
poster.html — structurally identical to the old monolithic poster_<layout>_<style>
.html, so check_poster.py / render_poster.py and the staged-fill loop work unchanged.

WHY COMPOSE (not ship runtime CSS): the rendered poster.html must stay
self-contained (inline CSS, local fonts, MathJax) AND the full ~100 KB HTML must
never pass through a tool-call's output channel (token-cap abort). So we decouple
the SOURCE on disk and compose at build time — this script reads the pieces and
writes the file; the model only ever emits the small per-paper SUBS later
(see references/build_poster.py).

CONTENT placeholders ({{TITLE}}, {{LOGO_1}}, {{VENUE_LOGO}}, {{PROBLEM}}, …) are
INTENTIONALLY left intact for the downstream build_poster.py SUBS fill — compose
only resolves the two STRUCTURAL hooks ({{STYLE_CSS}}, {{HEADER}}).

Usage:
    python compose_poster.py --layout full --style solid --header v3 --out poster.html
    # then fill content with build_poster.py (cp <chosen pieces> already done here)
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import itertools
import json
import os
import random
import re
import sys
import threading
from collections import OrderedDict
from pathlib import Path

# references/ lives directly under the skill root; assets/ is its sibling.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_theme  # noqa: E402  (sibling module; the COLOR axis injector)

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ASSETS = SKILL_DIR / "assets"

# The structural hooks compose resolves. Everything else ({{TITLE}} …) is a
# CONTENT placeholder and must SURVIVE compose for the later SUBS fill.
STRUCT_HOOKS = ("{{STYLE_CSS}}", "{{HEADER}}", "{{SCAN_SECTION}}", "{{MATH_HEAD}}")

# Math-typesetting engine axis (ONE place to switch the default). "katex" renders
# thinner glyphs matching the posterskill look; "mathjax" is the classic MathJax
# tex-svg. Both are bundled offline (assets/{katex,mathjax}/) and intercepted by
# the renderer + html2pptx, and the html2pptx math pass is engine-agnostic, so
# flipping this default (or passing --math / POSTER_MATH) needs no other change.
MATH_ENGINE_DEFAULT = "katex"
MATH_ENGINES = ("katex", "mathjax")

# These heading treatments create misleading horizontal divisions in Portrait's
# narrow columns. Keep their source CSS installed for Landscape, but remove them
# from Portrait's catalog so neither random nor explicit selection can use them.
PORTRAIT_EXCLUDED_STYLES = frozenset({"underline", "double-rule"})
BRANDING_FREE_HEADERS = frozenset({"v6", "v7", "pv6", "pv7"})

# Batch sampler v4 resolves every requested random axis JOINTLY.  The previous
# sampler balanced each axis in isolation, which made every marginal look good
# but could repeat a complete style/header/theme tuple before the Cartesian
# combination space was exhausted.  Keep a small process-local cache because a
# batch commonly asks for consecutive indices through repeated ``compose()``
# calls.  The cache is an optimisation only; every state is reconstructed from
# the seed/catalog and remains byte-stable across fresh processes.
SAMPLER_VERSION = 4
_JOINT_CACHE_MAX = 32
_JOINT_CACHE: OrderedDict[tuple, dict] = OrderedDict()
_JOINT_CACHE_LOCK = threading.RLock()


def _options(directory: Path, suffix: str) -> list[str]:
    """Sorted stems of the choosable pieces in a directory (for error messages)."""
    if not directory.is_dir():
        return []
    return sorted(p.name[: -len(suffix)] for p in directory.glob(f"*{suffix}"))


def _rand_pick_list(opts: list[str], seed: str) -> str:
    """Deterministically pick one of an explicit ``opts`` list keyed by ``seed`` (SHA-256)."""
    if not opts:
        sys.exit(f"_rand_pick_list: empty option list for seed {seed!r}")
    h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)
    return opts[h % len(opts)]


def _rand_pick(directory: Path, suffix: str, seed: str, exclude: tuple = ()) -> str:
    """Deterministically pick one option from ``directory`` keyed by ``seed`` (SHA-256).
    Reproducible — a wave of posters seeded by their output paths gets a stable SPREAD
    across the options, with no flaky model 'pick random' step. ``exclude`` drops names."""
    opts = [o for o in _options(directory, suffix) if o not in exclude]
    if not opts:
        sys.exit(f"_rand_pick: no options in {directory} (excluding {exclude})")
    return _rand_pick_list(opts, seed)


def _balanced_pick_list(opts: list[str], *, seed: str, axis: str, index: int) -> str:
    """Pick from a deterministic shuffled cycle for a batch variant.

    Every aligned block of ``len(opts)`` indices covers the whole axis exactly once.
    The permutation changes deterministically for each block. This matters when two
    axes have equal pool sizes, such as Portrait's 9 styles and 9 themes: a fixed
    permutation would otherwise lock every style to the same theme across the batch.
    """
    if not opts:
        sys.exit(f"_balanced_pick_list: empty option list for axis {axis!r}")
    cycle, position = divmod(index, len(opts))
    ordered = sorted(opts)
    digest = hashlib.sha256(
        f"{seed}|{axis}|balanced-v2|cycle:{cycle}".encode("utf-8")
    ).digest()
    random.Random(int.from_bytes(digest, "big")).shuffle(ordered)
    return ordered[position]


def _joint_balanced_pick(
    axis_options: dict[str, list[str]], *, seed: str, index: int,
    forbidden: tuple[tuple[tuple[str, str], ...], ...] = (),
) -> dict[str, str]:
    """Return one deterministic, unused joint batch combination.

    ``axis_options`` contains only axes whose request was ``random``.  Until the
    valid Cartesian space is exhausted, index ``0..space-1`` is a permutation
    of that space, so complete resolved tuples cannot repeat.  At each step the
    sampler first looks for an unused tuple whose value is currently
    least-used on *every* axis.  This retains the old per-axis shuffled-cycle
    property (prefix marginal spread normally stays <= 1) while removing joint
    collisions.  If a constrained/irregular catalog has no such tuple, the
    deterministic fallback chooses the unused tuple with the smallest resulting
    marginal spread; uniqueness is never relaxed.

    ``forbidden`` is a tuple of conjunctions.  For example
    ``((('layout', '3col'), ('header', 'v5')),)`` removes the Landscape-only
    invalid pairing before sampling instead of repairing it after selection.
    """
    if index < 0:
        sys.exit("_joint_balanced_pick: index must be >= 0")
    if not axis_options:
        return {}

    normalized = tuple(
        (axis, tuple(sorted(dict.fromkeys(options))))
        for axis, options in axis_options.items()
    )
    for axis, options in normalized:
        if not options:
            sys.exit(f"_joint_balanced_pick: empty option list for axis {axis!r}")
    forbidden_norm = tuple(
        tuple(sorted((str(axis), str(value)) for axis, value in rule))
        for rule in forbidden
    )
    axis_names = tuple(axis for axis, _ in normalized)
    pools = tuple(options for _, options in normalized)
    axis_pos = {axis: pos for pos, axis in enumerate(axis_names)}

    def allowed(combo: tuple[str, ...]) -> bool:
        for rule in forbidden_norm:
            if all(axis in axis_pos and combo[axis_pos[axis]] == value
                   for axis, value in rule):
                return False
        return True

    candidates = tuple(
        combo for combo in itertools.product(*pools) if allowed(combo)
    )
    if not candidates:
        sys.exit("_joint_balanced_pick: constraints removed every combination")

    cycle, position = divmod(index, len(candidates))
    cache_key = (seed, normalized, forbidden_norm, cycle)
    with _JOINT_CACHE_LOCK:
        state = _JOINT_CACHE.get(cache_key)
        if state is None:
            order = list(range(len(candidates)))
            catalog_token = json.dumps(
                {axis: list(options) for axis, options in normalized},
                sort_keys=True, separators=(",", ":"),
            )
            digest = hashlib.sha256(
                f"{seed}|joint-balanced-v1|cycle:{cycle}|{catalog_token}|"
                f"{forbidden_norm!r}".encode("utf-8")
            ).digest()
            random.Random(int.from_bytes(digest, "big")).shuffle(order)
            state = {
                "candidates": candidates,
                "order": order,
                "used": bytearray(len(candidates)),
                "counts": [[0] * len(options) for options in pools],
                "value_pos": [
                    {value: pos for pos, value in enumerate(options)}
                    for options in pools
                ],
                "sequence": [],
            }
            _JOINT_CACHE[cache_key] = state
            while len(_JOINT_CACHE) > _JOINT_CACHE_MAX:
                _JOINT_CACHE.popitem(last=False)
        else:
            _JOINT_CACHE.move_to_end(cache_key)

        while len(state["sequence"]) <= position:
            counts = state["counts"]
            minima = [min(row) for row in counts]
            chosen = None
            for candidate_index in state["order"]:
                if state["used"][candidate_index]:
                    continue
                combo = candidates[candidate_index]
                if all(
                    counts[axis_index][state["value_pos"][axis_index][value]]
                    == minima[axis_index]
                    for axis_index, value in enumerate(combo)
                ):
                    chosen = candidate_index
                    break

            if chosen is None:
                best_score = None
                for candidate_index in state["order"]:
                    if state["used"][candidate_index]:
                        continue
                    combo = candidates[candidate_index]
                    spreads = []
                    for axis_index, value in enumerate(combo):
                        trial = counts[axis_index].copy()
                        trial[state["value_pos"][axis_index][value]] += 1
                        spreads.append(max(trial) - min(trial))
                    score = (max(spreads), sum(spreads))
                    if best_score is None or score < best_score:
                        best_score = score
                        chosen = candidate_index

            if chosen is None:  # defensive; divmod above keeps us inside the space
                sys.exit("_joint_balanced_pick: no unused combination remains")
            state["used"][chosen] = 1
            combo = candidates[chosen]
            state["sequence"].append(combo)
            for axis_index, value in enumerate(combo):
                value_index = state["value_pos"][axis_index][value]
                counts[axis_index][value_index] += 1

        selected = state["sequence"][position]
        return dict(zip(axis_names, selected))


def _joint_combination_space(
    axis_options: dict[str, list[str]],
    forbidden: tuple[tuple[tuple[str, str], ...], ...] = (),
) -> int:
    """Count valid joint combinations for auditable sampler metadata."""
    if not axis_options:
        return 1
    axis_names = tuple(axis_options)
    pools = tuple(tuple(dict.fromkeys(axis_options[axis])) for axis in axis_names)
    axis_pos = {axis: pos for pos, axis in enumerate(axis_names)}
    total = 0
    for combo in itertools.product(*pools):
        rejected = any(
            all(axis in axis_pos and combo[axis_pos[axis]] == value
                for axis, value in rule)
            for rule in forbidden
        )
        if not rejected:
            total += 1
    return total


def _catalog_digest(catalog: dict[str, list[str]]) -> str:
    payload = json.dumps(catalog, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# Scan-to-Read variant groups. The build passes --scan single|dual based ONLY on whether a
# code QR exists (single = paper-only, dual = paper+code); compose then picks a concrete
# variant WITHIN the group, keyed by the output path — a reproducible spread that still
# guarantees a 2-QR layout never lands on a 1-QR paper. "directory" works in either group.
SCAN_GROUPS = {
    "single": ["hero", "contact", "directory", "banner"],
    "dual": ["twin", "chips", "directory"],
}

# Variants that render exactly ONE QR tile (paper only). "directory" and the whole
# "dual" group render two, so they are NOT here. Used by the QR-count guard below.
SCAN_SINGLE_ONLY = {"hero", "contact", "banner"}


def _count_qrs(outpath: Path) -> int:
    """Count QR images that exist on disk for this poster, read from
    <outdir>/assets/meta/metadata.json (written by paper2assets make_qr.py).
    Returns 0 on ANY failure so the caller safely falls back to the passed --scan."""
    try:
        base = outpath.resolve().parent
        data = json.loads((base / "assets" / "meta" / "metadata.json")
                          .read_text(encoding="utf-8"))
        n = 0
        for q in (data.get("qr") or []):
            p = q.get("path") or ""
            if p and (base / p).exists():
                n += 1
        return n
    except Exception:
        return 0


def compose(layout: str, style: str, header: str, outpath, *,
            scan: str = "aside", theme: str = "random",
            orientation: str = "landscape", math: str | None = None,
            assets: Path = DEFAULT_ASSETS, seed: str | None = None,
            variant_index: int | None = None, variant_seed: str | None = None,
            selection_out: Path | str | None = None) -> Path:
    """Read the layout, inject styles/<style>.css at {{STYLE_CSS}} (+ landscape:
    headers/<header>.html at {{HEADER}} and scan/<scan>.html at {{SCAN_SECTION}}),
    write a self-contained poster template to ``outpath``, then apply the COLOR
    axis: resolve ``theme`` (``random`` = deterministic pick keyed by the seed) and
    rewrite the :root accent vars in place. Returns the output Path.

    ``orientation`` = ``landscape`` (default) reads assets/layouts/ and composes
    all axes. ``portrait`` reads assets/layouts_portrait/, uses pv1-pv7 headers,
    and omits only the Scan-to-Read body section. Exits non-zero on any error.

    v6/v7 and pv6/pv7 omit institution names and logos. They are explicit-only;
    random selection retains the existing branded header catalog.

    Random selection is deterministic. The seed precedence is explicit ``seed``,
    ``POSTER_SEED``, then the resolved absolute output path. For a 30+ paper batch,
    pass the same ``variant_seed`` and consecutive ``variant_index`` values: the
    random axes are sampled jointly without replacement while preserving balanced
    marginal coverage.
    """
    if orientation not in ("landscape", "portrait"):
        sys.exit(
            f"compose: unknown orientation '{orientation}'; "
            "choose from landscape, portrait"
        )
    is_portrait = orientation == "portrait"
    layouts = assets / ("layouts_portrait" if is_portrait else "layouts")
    styles = assets / "styles"
    headers = assets / ("headers_portrait" if is_portrait else "headers")
    scans = assets / "scan"
    math_dir = assets / "math"
    out = Path(outpath)
    explicit_seed = seed if seed is not None else os.environ.get("POSTER_SEED")
    base_seed = explicit_seed if explicit_seed is not None else str(out.resolve())
    batch_seed = (variant_seed if variant_seed is not None
                  else os.environ.get("POSTER_VARIANT_SEED"))
    if variant_index is not None and variant_index < 0:
        sys.exit("compose: --variant-index must be >= 0")
    if variant_index is not None and batch_seed is None:
        batch_seed = base_seed

    requested = {
        "orientation": orientation,
        "layout": layout,
        "style": style,
        "header": header,
        "scan": scan,
        "theme": theme,
        "math": math,
    }
    installed_styles = _options(styles, ".css")
    orientation_styles = [
        name for name in installed_styles
        if not (is_portrait and name in PORTRAIT_EXCLUDED_STYLES)
    ]
    catalog = {
        "layouts": [o for o in _options(layouts, ".html")
                    if o not in ("methoddriven", "methoddriven4")],
        "styles": orientation_styles,
        "headers": [name for name in _options(headers, ".html")
                    if name not in BRANDING_FREE_HEADERS],
        "themes": sorted(apply_theme.THEMES),
    }

    if style != "random" and style not in catalog["styles"]:
        detail = ""
        if is_portrait and style in PORTRAIT_EXCLUDED_STYLES:
            detail = (
                f"; '{style}' is Landscape-only because it is excluded from Portrait"
            )
        sys.exit(
            f"compose: style '{style}' is not available for {orientation}{detail}\n"
            f"  available styles: {', '.join(catalog['styles']) or '(none)'}"
        )

    # Resolve the QR guard before constructing the joint random-axis catalog so
    # ``scan`` participates in the same collision-free batch tuple as the other
    # axes.  ``requested`` above intentionally retains the caller's raw choice.
    if (not is_portrait
            and (scan == "single" or scan in SCAN_SINGLE_ONLY)
            and _count_qrs(Path(outpath)) >= 2):
        print(f"[compose] metadata has >=2 QRs but --scan={scan} is single-QR "
              f"-> upgrading to the dual group so both codes render", file=sys.stderr)
        scan = "dual"

    joint_axis_options: dict[str, list[str]] = {}
    joint_forbidden: tuple[tuple[tuple[str, str], ...], ...] = ()
    if variant_index is not None:
        # Stable insertion order is part of sampler v4's replay contract.
        if layout == "random":
            joint_axis_options["layout"] = catalog["layouts"]
        if style == "random":
            joint_axis_options["style"] = catalog["styles"]
        if header == "random":
            header_options = catalog["headers"]
            if not is_portrait and layout == "3col":
                header_options = [name for name in header_options if name != "v5"]
            joint_axis_options["header"] = header_options
        if not is_portrait:
            if scan in SCAN_GROUPS:
                joint_axis_options["scan"] = [
                    name for name in SCAN_GROUPS[scan]
                    if (scans / f"{name}.html").exists()
                ] or SCAN_GROUPS[scan]
            elif scan == "random":
                joint_axis_options["scan"] = _options(scans, ".html")
        if theme == "random":
            joint_axis_options["theme"] = catalog["themes"]
        if (not is_portrait and layout == "random" and header == "random"):
            joint_forbidden = ((('layout', '3col'), ('header', 'v5')),)

    joint_pick = (
        _joint_balanced_pick(
            joint_axis_options, seed=batch_seed or base_seed,
            index=variant_index, forbidden=joint_forbidden,
        )
        if variant_index is not None else {}
    )

    def pick(opts: list[str], axis: str) -> str:
        if axis in joint_pick:
            selected = joint_pick[axis]
            if selected not in opts:
                sys.exit(
                    f"compose: joint sampler selected unavailable {axis} "
                    f"value {selected!r}"
                )
            return selected
        if variant_index is not None:
            return _balanced_pick_list(opts, seed=batch_seed or base_seed,
                                       axis=axis, index=variant_index)
        return _rand_pick_list(opts, f"{base_seed}|{axis}")
    # Math engine: --math wins, then POSTER_MATH env, then the module default.
    # Applies to BOTH orientations ({{MATH_HEAD}} lives in every template).
    engine = (math or os.environ.get("POSTER_MATH") or MATH_ENGINE_DEFAULT).strip().lower()
    if engine not in MATH_ENGINES:
        sys.exit(f"compose: unknown --math '{engine}'; "
                 f"choose from {', '.join(MATH_ENGINES)}")
    # Resolve "random" deterministically. Batch mode uses balanced shuffled cycles;
    # single-poster mode hashes the stable base seed independently for every axis.
    if style == "random":
        style = pick(catalog["styles"], "style")
    if layout == "random":
        # methoddriven is OPT-IN (only when the user explicitly asks for a
        # method-driven poster) — never let --layout random select it.
        layout = pick(catalog["layouts"], "layout")
    if header == "random":
        header = pick(catalog["headers"], "header")
    if not is_portrait:
        # 3col carries NO QR (the wide-column scan-to-read is suppressed, and v5 would add a
        # titlebar QR), so a 3col poster never uses the v5 header — re-pick from v1-v4.
        if layout == "3col" and header == "v5":
            header = pick([h for h in catalog["headers"] if h != "v5"], "header3col")
        # scan: a GROUP keyword (single|dual) picks a variant WITHIN that group; "random"
        # picks any installed variant; an explicit name is used as-is. Random picks use the seed.
        if scan in SCAN_GROUPS:
            avail = [s for s in SCAN_GROUPS[scan] if (scans / f"{s}.html").exists()]
            scan = pick(avail or SCAN_GROUPS[scan], "scan")
        elif scan == "random":
            scan = pick(_options(scans, ".html"), "scan")
    # color: resolve the theme up front (deterministic per seed) so the echo
    # reports the REAL color; the swap itself happens after the file is written.
    theme = (pick(catalog["themes"], "theme") if theme == "random"
             else apply_theme.resolve_theme(theme, f"{base_seed}|theme"))
    lp = layouts / f"{layout}.html"
    sp = styles / f"{style}.css"
    hp = headers / f"{header}.html"
    mp = math_dir / f"{engine}.html"
    # Echo the RESOLVED axes (after random/group/3col-v5 resolution) so the caller can
    # branch on the real layout. main()'s summary below echoes the raw CLI args.
    tail = (f"scan={scan} " if not is_portrait else "")
    print(f"compose: orientation={orientation} layout={layout} style={style} "
          f"header={header} {tail}math={engine} theme={theme}", flush=True)

    checks = [(lp, "layout", _options(layouts, ".html")),
              (sp, "style", _options(styles, ".css")),
              (hp, "header", _options(headers, ".html")),
              (mp, "math", _options(math_dir, ".html"))]
    if not is_portrait:
        scp = scans / f"{scan}.html"
        checks += [(scp, "scan", _options(scans, ".html"))]
    for path, kind, opts in checks:
        if not path.exists():
            sys.exit(f"compose: {kind} '{path.stem}' not found at {path}\n"
                     f"  available {kind}s: {', '.join(opts) or '(none)'}")

    html = lp.read_text(encoding="utf-8")
    pieces = {"{{STYLE_CSS}}": (sp.read_text(encoding="utf-8"), sp.name),
              "{{HEADER}}": (hp.read_text(encoding="utf-8"), hp.name),
              "{{MATH_HEAD}}": (mp.read_text(encoding="utf-8"), mp.name)}
    if not is_portrait:
        pieces["{{SCAN_SECTION}}"] = (scp.read_text(encoding="utf-8"), scp.name)

    # A style/header piece must never itself carry a STRUCTURAL hook (would recurse
    # / leave a dangling hook). Content placeholders inside the header are fine.
    for hook, (value, src) in pieces.items():
        for other in STRUCT_HOOKS:
            if other in value:
                sys.exit(f"compose: piece {src} unexpectedly contains {other}")

    # Inject each structural hook EXACTLY once.
    for hook, (value, src) in pieces.items():
        n = html.count(hook)
        if n != 1:
            sys.exit(f"compose: layout {lp.name} must contain exactly one {hook}, "
                     f"found {n}")
        html = html.replace(hook, value, 1)

    # Figure-fill floor for the client-side fit() script, kept in sync with the
    # POSTER_FIG_MIN_RATIO gate (default 0.90). Plain replace-all (NOT a structural
    # hook) so templates without the token are a no-op.
    html = html.replace("{{FIG_MIN_RATIO}}",
                        os.environ.get("POSTER_FIG_MIN_RATIO", "0.90"))

    # No structural hook may survive; content {{...}} placeholders are expected to.
    leftover_struct = [h for h in STRUCT_HOOKS if h in html]
    if leftover_struct:
        sys.exit(f"compose: structural hook(s) still present after inject: "
                 f"{leftover_struct}")

    resolved = {
        "orientation": orientation,
        "layout": layout,
        "style": style,
        "header": header,
        "scan": None if is_portrait else scan,
        "theme": theme,
        "math": engine,
    }
    selection = {
        "schema_version": "paper2poster.composition.v1",
        "sampler_version": SAMPLER_VERSION,
        "seed_source": ("argument" if seed is not None else
                        "environment" if explicit_seed is not None else
                        "resolved_output_path"),
        "seed_sha256": hashlib.sha256(base_seed.encode("utf-8")).hexdigest(),
        "variant_index": variant_index,
        "variant_seed_sha256": (hashlib.sha256((batch_seed or "").encode("utf-8")).hexdigest()
                                if variant_index is not None else None),
        "variant_joint_axes": (list(joint_axis_options)
                               if variant_index is not None else []),
        "variant_combination_space": (
            _joint_combination_space(joint_axis_options, joint_forbidden)
            if variant_index is not None else None
        ),
        "requested": requested,
        "resolved": resolved,
        "catalog": catalog,
        "catalog_digest": _catalog_digest(catalog),
    }
    selection_json = json.dumps(selection, sort_keys=True, ensure_ascii=False,
                                separators=(",", ":"))
    safe_selection_json = selection_json.replace("</", "<\\/")
    metadata = (f'<script id="paper2poster-composition" type="application/json">'
                f'{safe_selection_json}</script>')
    if "</head>" not in html:
        sys.exit(f"compose: layout {lp.name} has no </head> for composition metadata")
    html = html.replace("</head>", metadata + "\n</head>", 1)
    body_attrs = (f'data-poster-orientation="{html_lib.escape(orientation, quote=True)}" '
                  f'data-poster-layout="{html_lib.escape(layout, quote=True)}" '
                  f'data-poster-style="{html_lib.escape(style, quote=True)}" '
                  f'data-poster-header="{html_lib.escape(header, quote=True)}" '
                  f'data-poster-theme="{html_lib.escape(theme, quote=True)}"')
    html, body_count = re.subn(r"(?m)^<body(?=[\s>])", f"<body {body_attrs}", html, count=1)
    if body_count != 1:
        sys.exit(f"compose: layout {lp.name} must contain one <body> tag")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    # COLOR axis: rewrite the :root accent vars to the resolved theme in place.
    themed, _ = apply_theme.recolor(out.read_text(encoding="utf-8"),
                                    apply_theme.THEMES[theme])
    out.write_text(themed, encoding="utf-8")
    if selection_out is not None:
        selection_path = Path(selection_out)
        selection_path.parent.mkdir(parents=True, exist_ok=True)
        selection_path.write_text(json.dumps(selection, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
    return out


def _self_containment_warnings(html: str) -> list[str]:
    """Best-effort: flag external CSS that would break the self-contained invariant.
    External <link rel=stylesheet> or @import is a hard violation; the MathJax CDN
    <script src> AND the KaTeX CDN css/js are the allowed externals (both mirrored
    offline by the skill + intercepted by the renderer), so they are NOT flagged."""
    warns = []
    # Strip the KaTeX CDN stylesheet link before the generic check — it is an
    # allowed, offline-mirrored external (assets/katex/), like the MathJax script.
    scrubbed = re.sub(
        r'<link\b[^>]*href\s*=\s*["\']?[^"\'>]*katex[^"\'>]*\.css[^>]*>', '', html, flags=re.I)
    if re.search(r'<link\b[^>]*\brel\s*=\s*["\']?stylesheet', scrubbed, re.I):
        warns.append("external stylesheet <link rel=stylesheet> present")
    if re.search(r'@import\b', html):
        warns.append("CSS @import present")
    return warns


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="compose_poster",
        description="Compose a self-contained poster template from "
                    "layout × style × header.",
    )
    ap.add_argument("--layout", required=True,
                    help="structure: full | half | 3col | random")
    ap.add_argument("--style", default=os.environ.get("POSTER_STYLE", "random"),
                    help="visual style name or random (default POSTER_STYLE or random)")
    ap.add_argument("--header", default=os.environ.get("POSTER_HEADER", "random"),
                    help="titlebar variant (default POSTER_HEADER or random): landscape v1-v5, "
                         "portrait pv1-pv5; opt-in no institutions/logos: "
                         "v6/v7 (landscape), pv6/pv7 (portrait)")
    ap.add_argument("--scan", default="aside",
                    help="Scan-to-Read variant: single | dual (group keyword — "
                         "recommended; compose picks within the group) | random | "
                         "aside | hero | contact | directory | banner | twin | chips "
                         "(default aside)")
    ap.add_argument("--out", default="poster.html",
                    help="output path (default ./poster.html)")
    ap.add_argument("--theme", default=os.environ.get("POSTER_THEME", "random"),
                    help="COLOR axis: random (default POSTER_THEME or random; "
                         "deterministic per seed) | "
                         + " | ".join(sorted(apply_theme.THEMES)))
    ap.add_argument("--orientation",
                    default=os.environ.get("POSTER_ORIENTATION", "landscape"),
                    choices=("landscape", "portrait"),
                    help="landscape (default POSTER_ORIENTATION; 4 axes) | "
                         "portrait (layouts_portrait/, "
                         "pv1-pv7 titlebar, no scan section)")
    ap.add_argument("--seed", default=None,
                    help="stable seed for random axes (default: POSTER_SEED or the "
                         "resolved absolute --out path)")
    ap.add_argument("--variant-index", type=int, default=None,
                    help="zero-based batch index; random axes use balanced cycles")
    ap.add_argument("--variant-seed", default=None,
                    help="shared batch seed for --variant-index (also "
                         "POSTER_VARIANT_SEED)")
    ap.add_argument("--selection-out", default=None,
                    help="optional JSON path for the resolved composition manifest")
    ap.add_argument("--math", default=None, choices=MATH_ENGINES,
                    help=f"math engine (default {MATH_ENGINE_DEFAULT}; also "
                         f"POSTER_MATH env): katex (thin, posterskill-like) | mathjax")
    ap.add_argument("--assets", default=None,
                    help="override the assets/ dir (default: the skill's assets/)")
    a = ap.parse_args(argv)

    assets = Path(a.assets).resolve() if a.assets else DEFAULT_ASSETS
    out = compose(a.layout, a.style, a.header, a.out, scan=a.scan, theme=a.theme,
                  orientation=a.orientation, math=a.math, assets=assets,
                  seed=a.seed, variant_index=a.variant_index,
                  variant_seed=a.variant_seed, selection_out=a.selection_out)

    txt = out.read_text(encoding="utf-8")
    leftover = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", txt)))
    _eng = (a.math or os.environ.get("POSTER_MATH") or MATH_ENGINE_DEFAULT)
    print(f"composed {a.layout}+{a.style}+{a.header}+scan:{a.scan}+math:{_eng} -> {out} "
          f"({out.stat().st_size} bytes)")
    if leftover:
        print(f"  content placeholders awaiting SUBS fill: {', '.join(leftover)}")
    for w in _self_containment_warnings(txt):
        print(f"  WARN: {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
