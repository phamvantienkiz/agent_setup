"""Static HTML lint — runs before any rendering.

Catches the classes of errors that would otherwise burn a render cycle:

- LaTeX residue (``\\ref{`` / ``\\cite{`` / ``\\textbf{`` / lone ``\\ ``).
- Raw ``<`` inside ``$…$`` / ``$$…$$`` / ``\\(…\\)`` / ``\\[…\\]`` —
  MathJax may HTML-parse it as a tag start depending on its loader mode.
- Local ``src="..."`` images that don't exist on disk.
- Missing or unknown ``data-measure-role`` values.

The line numbers reported by preflight refer to **the original HTML file**.
Earlier versions stripped ``<style>`` / ``<script>`` / ``<!-- … -->``
blocks with ``re.sub(... , "")``, which collapsed newlines and shifted
every subsequent line number by N. We now replace each stripped block
with the SAME NUMBER OF NEWLINES, so character offsets after the strip
still map to the same line in the original file.
"""
from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .cli_common import eprint as _eprint
from .figure_semantics import (
    build_selection_manifest,
    eligible_for_role,
    figure_id,
    load_figure_records,
    normalize_asset_path,
    record_for_file,
    role_scores,
    semantic_contract_present,
    semantic_commit_error,
    semantics_available,
)
from .textutil import ascii_safe


# Roles understood by ``slack`` / ``polish``. Anything outside this
# set in a ``data-measure-role`` attribute is almost certainly a typo
# and would silently be ignored by the geometry pass.
KNOWN_ROLES: set[str] = {
    "poster", "header", "banner", "body",
    "column", "card", "hero", "footer-strip", "footer",
}


# (regex, human description) pairs for LaTeX residue. The patterns are
# scanned over the body with style/script/comments stripped (newline-
# preserved), so each match's character offset still maps to the right
# line in the original file.
LATEX_PATTERNS: list[tuple[str, str]] = [
    (r"\\ref\{",        r"\\ref{...} residue"),
    (r"\\cite\{",       r"\\cite{...} residue"),
    (r"\\textbf\{",     r"\\textbf{...} residue (use <b> or **bold**)"),
    (r"\\textit\{",     r"\\textit{...} residue (use <i> or *italic*)"),
    (r"\\emph\{",       r"\\emph{...} residue"),
    (r"\\section\{",    r"\\section{...} residue"),
    (r"\\label\{",      r"\\label{...} residue"),
    (r"\\begin\{",      r"\\begin{...} residue (use HTML structures)"),
    (r"\\end\{",        r"\\end{...} residue"),
    (r"(?<![\\a-zA-Z])\\\s",
        r"backslash-space '\\ ' (will render literally)"),
]


_VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})


class _FigureUsageParser(HTMLParser):
    """Collect ``<figure><img>`` sources with their nearest section id."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str, bool]] = []
        self.usages: list[tuple[str, str, int]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]],
    ) -> None:
        tag_l = tag.lower()
        attr_map = {str(key).lower(): value or "" for key, value in attrs}
        parent_section = self.stack[-1][1] if self.stack else ""
        parent_figure = self.stack[-1][2] if self.stack else False
        section_id = attr_map.get("data-section", "").strip() or parent_section
        in_figure = parent_figure or tag_l == "figure"
        if tag_l == "img" and section_id:
            src = attr_map.get("src", "").strip()
            if src and not src.startswith("{{"):
                self.usages.append((section_id, src, self.getpos()[0]))
        if tag_l not in _VOID_ELEMENTS:
            self.stack.append((tag_l, section_id, in_figure))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]],
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in _VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        wanted = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == wanted:
                del self.stack[index:]
                return


class _BrandingFreeHeaderParser(HTMLParser):
    """Reject branding accidentally restored to an explicitly unbranded header."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.problems: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        in_header = self.stack[-1][1] if self.stack else False
        in_authors = self.stack[-1][2] if self.stack else False
        if tag == "header":
            in_header = (
                attributes.get("data-institution-branding") == "none"
                or attributes.get("data-header") in {"v6", "v7", "pv6", "pv7"}
            )
        in_authors = in_authors or "authors" in classes
        if in_header:
            forbidden_classes = classes.intersection({
                "author-legend", "institutes-line", "institution-rail",
                "logo", "logo-block", "logo-grid", "venue-mark", "affiliations",
            })
            logo_image = tag == "img" and (
                "qr-img" not in classes
                or "/logos/" in (attributes.get("src") or "").replace("\\", "/")
            )
            if forbidden_classes or logo_image or (in_authors and tag == "sup"):
                self.problems.append(
                    f"L{self.getpos()[0]}: branding-free header contains institution "
                    "markup, a logo, or author markers; keep only plain author "
                    "names, venue text and optional QR tiles"
                )
        if tag not in _VOID_ELEMENTS:
            self.stack.append((tag, in_header, in_authors))

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]],
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def _branding_free_header_lint(raw: str) -> list[str]:
    parser = _BrandingFreeHeaderParser()
    parser.feed(raw)
    return parser.problems


def _usage_role(section_id: str) -> str | None:
    section = section_id.strip().lower().replace("_", "-")
    if section == "motivation":
        return "motivation"
    if section == "method" or section.startswith("method-"):
        return "method"
    if section in {
        "key-result", "key-results", "result", "results",
        "qualitative-result", "qualitative-results",
    }:
        return "result"
    return None


def _semantic_figure_lint(
    html_path: Path, raw: str,
) -> tuple[list[str], list[str]]:
    """Validate section figure choices against the upstream semantic contract.

    New semantic bundles are a hard contract.  Legacy or partial bundles must
    be upgraded rather than falling back to raw-model figure guessing.
    """
    figures_path = html_path.parent / "assets" / "meta" / "figures.json"
    if not figures_path.is_file():
        return [], []

    problems: list[str] = []
    warnings: list[str] = []
    try:
        records = load_figure_records(figures_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return [f"cannot read figure metadata '{figures_path}': {exc}"], []

    if not semantics_available(records):
        state = (
            "invalid/partial figure_semantics.v2 contract"
            if semantic_contract_present(records)
            else "legacy figures.json without figure_semantics.v2"
        )
        problems.append(
            f"{state}; upgrade the paper2assets bundle with build_package.py "
            "--skip-extract --paper-spec before rendering. Manual/raw-model "
            "figure attribution is disabled"
        )
        return problems, warnings

    commit_error = semantic_commit_error(figures_path, records)
    if commit_error:
        problems.append(commit_error)
        return problems, warnings

    expected = build_selection_manifest(records, figures_path=figures_path)
    selection_path = figures_path.with_name("figure_selection.json")
    if not selection_path.is_file():
        problems.append(
            "semantic figures.json is present but figure_selection.json is "
            "missing; run scripts/select_figures.py on this bundle before "
            "substituting poster figures"
        )
        manifest = expected
    else:
        try:
            manifest = json.loads(selection_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(
                f"cannot read semantic selection manifest '{selection_path}': {exc}"
            )
            manifest = expected

    if not isinstance(manifest, dict):
        problems.append("figure_selection.json must contain a JSON object")
        manifest = expected

    # Compare every field that the selector deterministically recomputes.  A
    # file-only comparison misses stale confidence/evidence/captions and old
    # thresholds even when the winning path happens to remain unchanged.
    for field in (
        "schema_version", "source", "mode", "semantics_available",
        "thresholds", "selections", "warnings",
    ):
        if manifest.get(field) != expected.get(field):
            problems.append(
                f"stale/non-deterministic figure_selection.json field "
                f"'{field}'; rerun scripts/select_figures.py"
            )

    actual_selections = manifest.get("selections", {})
    if not isinstance(actual_selections, dict):
        problems.append("figure_selection.json has no selections object")
        actual_selections = {}

    parser = _FigureUsageParser()
    parser.feed(raw)
    tracked: list[tuple[str, str, str, int]] = []
    for section_id, src, line in parser.usages:
        role = _usage_role(section_id)
        if role is not None:
            tracked.append((role, section_id, src, line))

    used_by_role: dict[str, set[str]] = {
        "method": set(), "motivation": set(), "result": set(),
    }
    first_by_role: set[str] = set()
    for role, section_id, src, line in tracked:
        normalized = normalize_asset_path(src)
        record = record_for_file(records, normalized)
        if record is None and not (
            normalized.startswith("assets/figures/")
            or normalized.startswith("figures/")
        ):
            # Local logos, QR codes, and decorative assets may live inside a
            # section.  Only sources that resolve to a figure record, or claim
            # the canonical figure directory, participate in semantic lint.
            continue
        used_by_role[role].add(normalized)
        if record is None:
            problems.append(
                f"L{line}: {section_id} figure '{src}' is absent or ambiguous "
                "in assets/meta/figures.json"
            )
            continue
        if not eligible_for_role(record, role):
            scores = role_scores(record)
            score_text = ", ".join(
                f"{name}={score:.2f}" for name, score in sorted(scores.items())
            ) or "no semantic roles"
            problems.append(
                f"L{line}: {section_id} uses {figure_id(record)} but it is not "
                f"eligible for {role} ({score_text})"
            )

        # The first canonical figure in each primary section must be the
        # deterministic selector's choice.  Further result figures remain
        # allowed when each independently passes the role gate.
        if role not in first_by_role:
            first_by_role.add(role)
            selected = actual_selections.get(role)
            selected_file = (
                normalize_asset_path(selected.get("file"))
                if isinstance(selected, dict) else ""
            )
            if not selected_file:
                problems.append(
                    f"L{line}: {section_id} contains {figure_id(record)}, but "
                    f"the deterministic selector returned no {role} figure"
                )
            elif normalized != selected_file:
                problems.append(
                    f"L{line}: {section_id} uses '{normalized}', but the "
                    f"deterministic {role} selection is '{selected_file}'"
                )

    overlap = used_by_role["method"].intersection(used_by_role["motivation"])
    for src in sorted(overlap):
        problems.append(
            f"Method and Motivation reuse the same figure '{src}'; the roles "
            "must be disjoint"
        )

    return problems, warnings


def _newline_preserving_sub(pattern: str, html: str, *,
                            flags: int = 0) -> str:
    """Replace each match with ``\\n`` * <newline-count-in-match>.

    This preserves line numbers across ``<style>`` / ``<script>`` /
    ``<!-- … -->`` blocks so a regex match's character offset in the
    stripped output still maps to the same line in the original file.
    """
    def keep_newlines(m: re.Match) -> str:
        return "\n" * m.group(0).count("\n")
    return re.sub(pattern, keep_newlines, html, flags=flags)


def strip_for_lint(html: str) -> str:
    """Remove ``<style>``, ``<script>``, and HTML comments while
    preserving newline counts. The output is what every preflight rule
    scans against.

    ONE document-order pass over all three so a construct nested inside
    another is consumed as a single unit by whichever delimiter opens
    FIRST. Stripping them in separate passes was a bug: a comment that
    contained ``<script>`` (e.g. ``<!-- ... change the <script> src -->``)
    had its closing ``-->`` eaten by the script pass, after which the
    comment pass ran past it and deleted real body markup downstream --
    the root ``<div data-measure-role="poster">`` went missing, so
    preflight false-failed "missing poster". The combined alternation
    also handles the reverse (a ``<style>``/``<script>`` body containing
    ``-->`` or ``<!--``): the tag opens first, so its whole body is taken
    before the comment rule can match inside it.
    """
    return _newline_preserving_sub(
        r"<!--.*?-->"
        r"|<style[^>]*>.*?</style>"
        r"|<script[^>]*>.*?</script>",
        html, flags=re.DOTALL | re.IGNORECASE,
    )


def find_math_segments(text: str) -> list[tuple[int, int, str]]:
    """Find inline + display math segments. Returns ``[(start, end, body)]``.

    Supports the four delimiter pairs every Claude-poster template
    configures MathJax for:

      - ``$$ … $$`` (display)
      - ``$ … $`` (inline; excludes already-covered ``$$`` regions)
      - ``\\[ … \\]`` (display)
      - ``\\( … \\)`` (inline)
    """
    out: list[tuple[int, int, str]] = []

    def add(s: int, e: int, body: str) -> None:
        out.append((s, e, body))

    # $$...$$
    for m in re.finditer(r"\$\$(.+?)\$\$", text, re.DOTALL):
        add(m.start(), m.end(), m.group(1))
    # \[...\]
    for m in re.finditer(r"\\\[(.+?)\\\]", text, re.DOTALL):
        add(m.start(), m.end(), m.group(1))

    covered = [(s, e) for s, e, _ in out]

    # $...$ — single-line only, not already inside a $$...$$
    for m in re.finditer(r"(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)", text):
        s, e = m.start(), m.end()
        if any(cs <= s < ce or cs < e <= ce for cs, ce in covered):
            continue
        add(s, e, m.group(1))
    # \(...\) — single-line only, not already inside a \[...\]
    for m in re.finditer(r"\\\(([^\n]+?)\\\)", text):
        s, e = m.start(), m.end()
        if any(cs <= s < ce or cs < e <= ce for cs, ce in covered):
            continue
        add(s, e, m.group(1))

    return out


def _delim_label(body: str, segment: str) -> str:
    """Try to label a math segment by its delimiter style in error
    output. ``segment`` is the raw matched text; we look at its first
    char(s)."""
    if segment.startswith("$$") and segment.endswith("$$"):
        return "$$...$$"
    if segment.startswith("$") and segment.endswith("$"):
        return "$...$"
    if segment.startswith("\\["):
        return "\\[...\\]"
    if segment.startswith("\\("):
        return "\\(...\\)"
    return "math"


def cmd_preflight(args: argparse.Namespace) -> int:
    html_path = Path(args.html).resolve()
    if not html_path.exists():
        _eprint(f"ERROR: HTML not found: {ascii_safe(html_path)}")
        return 2
    raw = html_path.read_text(encoding="utf-8", errors="ignore")
    body = strip_for_lint(raw)

    problems: list[str] = _branding_free_header_lint(raw)
    warnings: list[str] = []

    # 0) Figure-to-section semantics.  New paper2assets bundles carry an
    #    auditable contract and fail on a mismatched Motivation/Method/Result
    #    image. Legacy/partial bundles fail until Paper2Assets upgrades them.
    semantic_problems, semantic_warnings = _semantic_figure_lint(html_path, raw)
    problems.extend(semantic_problems)
    warnings.extend(semantic_warnings)

    # 1) Unclosed <style>/<script>/<!-- --> . strip_for_lint needs the
    #    closer to remove the block, so an unclosed opener SURVIVES in
    #    `body`. A real browser swallows the rest of the document into that
    #    construct -- which makes every post-strip check below (LaTeX scan,
    #    raw-'<' scan, role-presence) untrustworthy: the linter "sees" a
    #    poster div the browser will never render. Fail loudly instead of
    #    silently PASSing on markup we can't actually see past.
    m_open = re.search(r"<!--|<style\b|<script\b", body, re.IGNORECASE)
    if m_open:
        ln = body[: m_open.start()].count("\n") + 1
        problems.append(
            f"L{ln}: unclosed '{ascii_safe(m_open.group(0))}' block -- add "
            "the matching '-->', '</style>', or '</script>'. The browser "
            "would otherwise swallow the rest of the poster into it."
        )

    # 2) LaTeX residue.
    for pat, desc in LATEX_PATTERNS:
        for m in re.finditer(pat, body):
            ln = body[: m.start()].count("\n") + 1
            problems.append(f"L{ln}: {desc} -> '{ascii_safe(m.group(0))}'")

    # 3) Raw '<' inside math segments. The common HTML-parse failure
    #    case is `a<b` / `x<y`. We catch '<' even after a letter/digit.
    #    Suppressed only when it's an escape `\<` or part of `</` / `<!`
    #    (HTML constructs MathJax never sees) or `<=` (a single MathJax
    #    token that is parsed atomically and does NOT trip the HTML
    #    tokenizer's tag-start lookahead).
    for s, e, mbody in find_math_segments(body):
        # Compute the math body's offset inside the original segment so
        # multi-line `$$ … \n a < b \n … $$` reports the `<`'s line,
        # not the segment-start line. find_math_segments hands back the
        # full `(start, end, body)` of the segment; the body's first
        # char is at `body[s + (segment_text_len - body_len)]` — easier
        # to recompute via `body.find(mbody, s)`.
        body_offset_in_body = body.find(mbody, s)
        if body_offset_in_body == -1:
            body_offset_in_body = s  # fallback shouldn't happen
        for m in re.finditer(r"(?<!\\)<(?![=/!])", mbody):
            abs_offset = body_offset_in_body + m.start()
            ln = body[: abs_offset].count("\n") + 1
            label = _delim_label(body[s:e], body[s:e])
            problems.append(
                f"L{ln}: raw '<' inside {label} "
                f"'{ascii_safe(mbody.strip()[:60])}' -- use \\lt"
            )

    # 4) Image src: local must exist; remote http(s) warns. A print
    #    poster should be self-contained -- a CDN image that 404s or is
    #    slow at render time silently breaks the figure, and the render
    #    gates can't see a missing remote image. data: URIs are inline.
    for m in re.finditer(r'src\s*=\s*["\']([^"\']+)["\']', body,
                         re.IGNORECASE):
        src = m.group(1)
        # Scheme matching is case-insensitive (browsers treat `HTTPS:` /
        # `DATA:` like `https:` / `data:`); lower-case only for the scheme
        # test, keep `src` raw for display and local-path resolution.
        src_l = src.lower()
        if src_l.startswith("data:"):
            continue
        if src_l.startswith(("http://", "https://", "//")):
            ln = body[: m.start()].count("\n") + 1
            warnings.append(
                f"L{ln}: remote image '{ascii_safe(src[:60])}' -- inline or "
                "localize "
                "it; a print poster should not depend on a CDN at render "
                "time"
            )
            continue
        # Strip ?query / #fragment and percent-decode before resolving a
        # LOCAL path -- a legit `fig.png?v=2` or `my%20fig.png` otherwise
        # reads as a missing file.
        local = unquote(urlsplit(src).path)
        candidate = (html_path.parent / local).resolve()
        if not candidate.exists():
            ln = body[: m.start()].count("\n") + 1
            problems.append(f"L{ln}: missing local image '{ascii_safe(src)}'")

    # 5) data-measure-role="poster" required on the root. Paper2poster
    #    templates carry no `data-measure-role` attributes and use
    #    `class="poster"` instead; accept that as a valid substitute so
    #    the runtime class-fallback shim in render.py can map it.
    has_attr_poster = bool(
        re.search(r'data-measure-role\s*=\s*["\']poster["\']', body)
    )
    has_class_poster = bool(
        re.search(
            r'class\s*=\s*["\'][^"\']*\bposter\b[^"\']*["\']', body,
        )
    )
    if not (has_attr_poster or has_class_poster):
        problems.append(
            'missing root marker: add data-measure-role="poster" '
            '(or class="poster") to the outer container'
        )

    # 6) Unknown role values flag silent measure misses.
    for m in re.finditer(
        r'data-measure-role\s*=\s*["\']([^"\']+)["\']', body
    ):
        role = m.group(1).strip()
        if role not in KNOWN_ROLES:
            ln = body[: m.start()].count("\n") + 1
            problems.append(
                f"L{ln}: unknown data-measure-role='{ascii_safe(role)}' "
                f"(allowed: {sorted(KNOWN_ROLES)})"
            )

    # 7) Soft sanity: no <title> / no <h1>. Warns, doesn't fail.
    if not re.search(r"<title[^>]*>.+?</title>", raw, re.DOTALL):
        warnings.append("no <title> set")
    if not re.search(r"<h1\b", raw):
        warnings.append(
            "no <h1> -- poster title block usually carries one"
        )

    # 8) Every kept <figure> must carry a non-empty one-line <figcaption>.
    #    A figure whose caption is missing or blank renders as an unlabeled
    #    image -- a recurring defect on method / architecture figures. Warn
    #    (not fail: a purely decorative figure is a rare valid exception) but
    #    surface it every preflight so the caption gets filled from
    #    captions.json instead of shipping a bare figure.
    for m in re.finditer(r"<figure\b[^>]*>(.*?)</figure>", body,
                         re.DOTALL | re.IGNORECASE):
        inner = m.group(1)
        cap = re.search(r"<figcaption\b[^>]*>(.*?)</figcaption>", inner,
                        re.DOTALL | re.IGNORECASE)
        cap_txt = re.sub(r"<[^>]+>", "", cap.group(1)).strip() if cap else ""
        if not cap_txt:
            ln = body[: m.start()].count("\n") + 1
            warnings.append(
                f"L{ln}: <figure> has no non-empty <figcaption> -- every kept "
                "figure needs a one-line caption (from captions.json); an "
                "unlabeled figure is a defect"
            )

    print(f"[preflight] {ascii_safe(html_path)}")
    print(f"  problems: {len(problems)}   warnings: {len(warnings)}")
    for w in warnings:
        print(f"  WARN: {w}")
    for p in problems:
        _eprint(f"  FAIL: {p}")

    if problems:
        return 1
    print("[preflight] PASS")
    return 0


def has_required_roles_in_html(html_path: Path) -> dict[str, int]:
    """Cheap static count of each known role on disk. Used by ``polish``
    so it can hard-fail on a poster lacking ALL measurement markup,
    instead of silently PASSing on "0 figures, 0 columns, 0 stat
    elements".

    Compat fallback for paper2poster-style templates: add the conventional
    CSS classes that the runtime shim (``inject_class_fallback_roles``)
    maps to each role. Without this, polish hard-fails on disk before the
    browser ever opens, even though the runtime would have populated the
    roles fine.

    The fallback is ADDITIVE per role, mirroring the runtime shim: an
    explicit role does not turn the shim off for that role (in
    ``assets/layouts_portrait/full.html`` the single declared
    ``column`` on ``.method-hero`` sits alongside ordinary ``.col``
    columns, and both are measured). Bailing out on the FIRST attribute
    seen reported ``poster=0, card=0`` for that template, which tripped
    ``cmd_polish``'s "missing markup" hard-fail on a poster the runtime
    would have measured fine.

    This is a coarse ESTIMATE, not a prediction of the runtime. Against the
    lowercase, quoted markup this skill's templates emit it over-counts (a
    regex cannot tell which class-matched element already carries a role, so
    an element with both is counted twice), which is the harmless direction
    for its consumer: ``cmd_polish``'s pre-browser "is this file measurable
    at all?" check tests for zero, so erring high keeps it from refusing a
    poster it could measure. It is NOT an upper bound for arbitrary HTML --
    a browser accepts markup this regex does not match (``CLASS=section``,
    unquoted attribute values), where it would under-count instead.

    Either way it is only a fail-fast. Anything needing to know what the
    poster ACTUALLY renders must ask the live page (``render.count_roles``),
    which both ``cmd_polish`` and ``slack --with-polish`` now do before
    trusting a PASS.
    """
    raw = html_path.read_text(encoding="utf-8", errors="ignore")
    body = strip_for_lint(raw)
    counts: dict[str, int] = {role: 0 for role in KNOWN_ROLES}
    for m in re.finditer(
        r'data-measure-role\s*=\s*["\']([^"\']+)["\']', body
    ):
        role = m.group(1).strip()
        if role in counts:
            counts[role] += 1

    # Class-based fallback (paper2poster templates). Keep the selectors in
    # step with `render._COMPAT_ROLES_JS` -- if the two disagree, this
    # static pre-check and the runtime shim disagree about the same file.
    def _count_class(name: str) -> int:
        return len(re.findall(
            r'class\s*=\s*["\'][^"\']*\b' + re.escape(name) + r'\b[^"\']*["\']',
            body,
        ))
    fallbacks: dict[str, Callable[[], int]] = {
        "poster": lambda: _count_class("poster"),
        "column": lambda: _count_class("col"),
        "card": lambda: _count_class("section"),
        "banner": lambda: _count_class("titlebar") + _count_class("banner"),
        "footer-strip": lambda: _count_class("footer-strip"),
        "footer": lambda: _count_class("footer"),
    }
    for role, count_fn in fallbacks.items():
        counts[role] += count_fn()
    return counts
