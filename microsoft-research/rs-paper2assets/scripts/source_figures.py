#!/usr/bin/env python3
"""source_figures.py — use the paper's ORIGINAL figure files instead of
cropping them out of the rendered PDF.

The rendered-PDF path (extract_pdf.py + crop_figure.py's LLM bbox-refinement
loop) is the single most expensive stage of paper2assets (~6 min wall + heavy
tokens). When the paper's real, already-clean figure graphics are available we
skip all of that:

  --arxiv <id|url>   download the arXiv source tarball (arxiv.org/e-print/<id>),
                     parse the main .tex for figures in document order, and
                     rasterise each graphic to assets/figures/*.png.
  --images <p|url>…  use figures the user attached / linked directly.

Writes assets/figures/*.png + assets/meta/figures.json in the SAME schema as
extract_pdf.py.  If only some TeX figures can be used directly, unresolved or
multi-file figures are left as explicit ``pdf-crop-pending`` records for
extract_pdf.py to fill by caption label. Exits 0 if >=1 source figure was
produced, non-zero otherwise (the caller then falls back to the full crop
pipeline). Never raises on a bad source.

Text / metadata are unaffected.  TeX captions stay authoritative for source
figures; PDF-text captions are retained only as alignment candidates.
"""
from __future__ import annotations

import argparse
import difflib
import gzip
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import layout  # noqa: E402

_UA = {"User-Agent": "Mozilla/5.0 (paper2assets source_figures)"}
_RASTER_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
_VECTOR_EXT = {".pdf", ".eps", ".ps"}
_GRAPHIC_EXT = _RASTER_EXT | _VECTOR_EXT


def _eprint(*a):
    print(*a, file=sys.stderr)


def _arxiv_id(s: str) -> str:
    """Bare arXiv id from an id or a URL (abs/pdf/e-print)."""
    m = re.search(r"(\d{4}\.\d{4,5}(v\d+)?)", s) or re.search(r"([a-z\-]+/\d{7})", s)
    return m.group(1) if m else s.strip()


# ── download + unpack the arXiv source tarball ──────────────────────────────
def download_arxiv_source(aid: str, dest: Path) -> bool:
    url = f"https://arxiv.org/e-print/{aid}"
    tarball = dest / "source.tar.gz"
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=60) as r, open(tarball, "wb") as f:
            shutil.copyfileobj(r, f)
    except Exception as e:
        _eprint(f"[source_figures] arXiv e-print download failed: {e}")
        return False
    srcdir = dest / "source"
    srcdir.mkdir(exist_ok=True)
    try:                                      # e-print is usually a gzipped tar
        with tarfile.open(tarball, "r:*") as t:
            t.extractall(srcdir, filter="data")
        return True
    except Exception:
        pass
    try:                                      # …sometimes a single gzipped .tex
        with gzip.open(tarball, "rb") as g:
            (srcdir / "main.tex").write_bytes(g.read())
        return True
    except Exception as e:
        _eprint(f"[source_figures] could not unpack e-print: {e}")
        return False


# ── parse .tex figure order (best-effort) ───────────────────────────────────
_FIG_ENV = re.compile(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.S)
_INCL = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
_CAP = re.compile(r"\\caption\s*\{", re.S)
_LABEL = re.compile(r"\\label\s*\{([^}]+)\}")
_GPATH = re.compile(r"\\graphicspath\s*\{\s*((?:\{[^}]*\}\s*)+)\}")


def _balanced(s: str, start: int) -> str:
    """Text inside the {...} that begins at s[start] (a '{'), brace-balanced."""
    depth, out = 0, []
    for ch in s[start:]:
        if ch == "{":
            depth += 1
            if depth == 1:
                continue
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        out.append(ch)
    return "".join(out)


def _clean_caption(t: str) -> str:
    t = re.sub(r"\\label\s*\{[^}]*\}", "", t)
    t = re.sub(r"\\[a-zA-Z]+\*?\s*(\[[^\]]*\])?", " ", t)   # strip macros
    t = re.sub(r"[{}]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _strip_tex_comments(text: str) -> str:
    r"""Remove unescaped TeX comments while preserving escaped ``\%``."""
    cleaned: list[str] = []
    for line in text.splitlines(keepends=True):
        cut = len(line)
        for index, char in enumerate(line):
            if char != "%":
                continue
            slashes = 0
            cursor = index - 1
            while cursor >= 0 and line[cursor] == "\\":
                slashes += 1
                cursor -= 1
            if slashes % 2 == 0:
                cut = index
                break
        if cut == len(line):
            cleaned.append(line)
            continue
        suffix = "\r\n" if line.endswith("\r\n") else "\n" if line.endswith("\n") else ""
        cleaned.append(line[:cut] + suffix)
    return "".join(cleaned)


def find_main_tex(srcdir: Path) -> Path | None:
    texs = list(srcdir.rglob("*.tex"))
    if not texs:
        return None
    for t in texs:                            # prefer the one with \documentclass
        try:
            if "\\documentclass" in t.read_text(errors="ignore"):
                return t
        except Exception:
            continue
    return max(texs, key=lambda p: p.stat().st_size)


def parse_tex_figures(main_tex: Path) -> list[dict]:
    """Ordered [{graphic, caption, label}] from the main .tex (+ its \\inputs)."""
    root = main_tex.parent
    try:
        text = main_tex.read_text(errors="ignore")
    except Exception:
        return []
    # inline simple \input/\include so figure order across files is preserved
    def _inline(txt, depth=0):
        txt = _strip_tex_comments(txt)
        if depth > 3:
            return txt
        def repl(m):
            name = m.group(1).strip()
            for cand in (root / name, root / f"{name}.tex"):
                if cand.exists():
                    return _inline(cand.read_text(errors="ignore"), depth + 1)
            return ""
        return re.sub(r"\\(?:input|include)\s*\{([^}]+)\}", repl, txt)
    text = _inline(text)
    text = text.split("\\appendix")[0]        # main-body only
    gpaths = [""]
    gm = _GPATH.search(text)
    if gm:
        gpaths += re.findall(r"\{([^}]*)\}", gm.group(1))
    out = []
    for env in _FIG_ENV.finditer(text):
        body = env.group(1)
        incls = _INCL.findall(body)
        if not incls:
            continue
        cap = ""
        # Composite figures commonly contain child ``subfigure`` captions
        # before the outer Figure caption.  The outer caption/label is the
        # final pair in normal LaTeX figure structure; using the first pair
        # misidentifies the whole composite as its first panel.
        captions = list(_CAP.finditer(body))
        if captions:
            cm = captions[-1]
            cap = _clean_caption(_balanced(body, cm.end() - 1))
        labels = _LABEL.findall(body)
        out.append({"graphics": incls, "caption": cap,
                    "label": labels[-1] if labels else "", "gpaths": gpaths})
    return out


def _resolve(root: Path, ref: str, gpaths: list[str]) -> Path | None:
    ref = ref.strip().strip('"')
    cands = []
    for gp in gpaths:
        base = (root / gp / ref) if gp else (root / ref)
        cands.append(base)
        if not base.suffix:
            for ext in (".pdf", ".png", ".jpg", ".jpeg", ".eps", ".ps"):
                cands.append(base.with_suffix(ext))
    for c in cands:
        if c.exists() and c.suffix.lower() in _GRAPHIC_EXT:
            return c
    # Last resort: match by stem anywhere in the tree, but only when the match
    # is unique.  arXiv bundles often contain poster/deck assets with generic
    # names such as ``overview.pdf``; returning the first rglob hit can attach
    # an unrelated raster to an otherwise valid figure caption.
    stem = Path(ref).stem
    matches = sorted(
        f for f in root.rglob("*")
        if f.stem == stem and f.suffix.lower() in _GRAPHIC_EXT
    )
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        _eprint(
            f"[source_figures] ambiguous graphic '{ref}': "
            f"{len(matches)} same-stem matches; skipping"
        )
    return None


# ── rasterise any graphic to PNG ────────────────────────────────────────────
def rasterize(src: Path, dst: Path, dpi: int = 432) -> tuple[int, int] | None:
    try:
        from PIL import Image
    except Exception:
        Image = None
    ext = src.suffix.lower()
    try:
        if ext in _RASTER_EXT and Image is not None:
            im = Image.open(src).convert("RGBA")
            im.save(dst)
            return im.size
        pdf = src
        if ext in (".eps", ".ps"):            # convert to pdf first (ghostscript)
            if not shutil.which("ps2pdf") and not shutil.which("gs"):
                return None
            pdf = dst.with_suffix(".src.pdf")
            tool = (["ps2pdf", str(src), str(pdf)] if shutil.which("ps2pdf")
                    else ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pdfwrite",
                          f"-sOutputFile={pdf}", str(src)])
            subprocess.run(tool, capture_output=True, timeout=120)
        # vector pdf -> png via pdftoppm (first page).
        # -cropbox: rasterize the CropBox (what \includegraphics shows in the paper),
        # NOT the full MediaBox. Figure PDFs whose CropBox < MediaBox carry leftover /
        # off-canvas content outside the visible crop (e.g. an unused panel parked in
        # the page margin); without -cropbox that junk leaks into the extracted figure.
        prefix = dst.with_suffix("")
        subprocess.run(["pdftoppm", "-cropbox", "-png", "-r", str(dpi), "-singlefile",
                        str(pdf), str(prefix)], capture_output=True, timeout=120, check=True)
        if pdf != src:
            pdf.unlink(missing_ok=True)
        if not dst.exists() and prefix.with_suffix(".png").exists():
            prefix.with_suffix(".png").rename(dst)
        if Image is not None and dst.exists():
            return Image.open(dst).size
        return (0, 0) if dst.exists() else None
    except Exception as e:
        _eprint(f"[source_figures] rasterize failed for {src.name}: {e}")
        return None


def _fetch(ref: str, dest: Path) -> Path | None:
    if re.match(r"https?://", ref):
        try:
            req = urllib.request.Request(ref, headers=_UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            p = dest / (Path(ref.split("?")[0]).name or "image")
            p.write_bytes(data)
            return p
        except Exception as e:
            _eprint(f"[source_figures] download failed {ref}: {e}")
            return None
    p = Path(ref)
    return p if p.exists() else None


# ── figures.json (extract_pdf schema) ───────────────────────────────────────
def _caption_entries(outdir: Path) -> list[dict]:
    try:
        caps = json.loads(layout.meta_file(outdir, "captions").read_text())
    except Exception:
        return []
    entries: list[dict] = []
    # extract_pdf may emit either a list of {label,text,page} dicts or a
    # {"Figure N": "text"} mapping. Handle both.
    if isinstance(caps, dict):
        for label, text in caps.items():
            if str(label).lower().startswith("figure"):
                entries.append({"label": str(label), "text": str(text or ""), "page": 0})
        return entries
    for c in caps:
        if not isinstance(c, dict):
            continue
        if str(c.get("label", "")).lower().startswith("figure"):
            entries.append(
                {
                    "label": str(c.get("label", "")),
                    "text": str(c.get("text", "") or ""),
                    "page": c.get("page", 0),
                }
            )
    return entries


def _caption_similarity(left: str, right: str) -> float:
    def norm(value: str) -> str:
        value = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^]]*\])?", " ", value.lower())
        return re.sub(r"[^a-z0-9]+", " ", value).strip()

    a, b = norm(left), norm(right)
    if not a or not b:
        return 0.0
    seq = difflib.SequenceMatcher(None, a, b).ratio()
    at, bt = set(a.split()), set(b.split())
    common = len(at & bt)
    token = common / max(1, len(at | bt))
    containment = common / max(1, min(len(at), len(bt)))
    prefix = 1.0 if a.startswith(b) or b.startswith(a) else 0.0
    return max(0.55 * seq + 0.25 * token + 0.20 * containment,
               0.82 * containment + 0.18 * prefix)


def sync_figure_captions(outdir: Path) -> int:
    """Backfill source-first manifests after PDF captions become available.

    Source graphics are normally extracted before ``extract_pdf --no-figures``.
    The old flow therefore froze sequential ``Figure i`` labels.  Align TeX
    captions to PDF captions only when the text match is strong and unique.
    Never use generated ordinals or document order as a fallback: one skipped
    or unresolved source graphic would shift every later caption.  TeX
    ``\\label{...}`` values remain available as ``source_label`` and the TeX
    caption remains the selected semantic text.
    """
    manifest_path = layout.meta_file(outdir, "figures")
    try:
        figures = json.loads(manifest_path.read_text())
    except Exception:
        return 0
    captions = _caption_entries(outdir)
    if not isinstance(figures, list) or not captions:
        return 0

    source_captions: dict[int, str] = {}
    for index, figure in enumerate(figures):
        if not isinstance(figure, dict):
            continue
        source_caption = str(
            figure.get("source_caption")
            or (figure.get("caption", "") if figure.get("source") == "original" else "")
            or ""
        )
        if source_caption:
            source_captions[index] = source_caption

    # Score the complete matrix before assigning anything.  A greedy
    # "unused captions" pass can let a later figure inherit its second-best
    # label after an earlier row consumed the true match.  Require the match
    # to be uniquely best in both directions instead.
    row_matches: dict[int, tuple[int, float, float]] = {}
    for figure_index, source_caption in source_captions.items():
        ranked = sorted(
            (
                (_caption_similarity(source_caption, caption["text"]), caption_index)
                for caption_index, caption in enumerate(captions)
            ),
            key=lambda item: (-item[0], item[1]),
        )
        if ranked:
            score, chosen = ranked[0]
            second = ranked[1][0] if len(ranked) > 1 else 0.0
            row_matches[figure_index] = (chosen, score, score - second)

    column_matches: dict[int, tuple[int, float, float]] = {}
    for caption_index, caption in enumerate(captions):
        ranked = sorted(
            (
                (_caption_similarity(source_caption, caption["text"]), figure_index)
                for figure_index, source_caption in source_captions.items()
            ),
            key=lambda item: (-item[0], item[1]),
        )
        if ranked:
            score, chosen = ranked[0]
            second = ranked[1][0] if len(ranked) > 1 else 0.0
            column_matches[caption_index] = (chosen, score, score - second)

    aligned = 0
    for figure_index, figure in enumerate(figures):
        if not isinstance(figure, dict):
            continue
        source_caption = source_captions.get(figure_index, "")
        chosen: int | None = None
        score = 0.0
        margin = 0.0
        reverse_margin = 0.0
        if figure_index in row_matches:
            candidate, score, margin = row_matches[figure_index]
            reverse = column_matches.get(candidate)
            if reverse:
                reverse_figure, _, reverse_margin = reverse
                if (
                    score >= 0.72
                    and margin >= 0.08
                    and reverse_figure == figure_index
                    and reverse_margin >= 0.08
                ):
                    chosen = candidate
        if chosen is None:
            figure["caption_alignment"] = {
                "method": "mutual-source-caption-similarity",
                "status": "unresolved",
                "confidence": round(score, 3),
                "margin": round(margin, 3),
                "reverse_margin": round(reverse_margin, 3),
            }
            continue

        caption = captions[chosen]
        figure["source_caption"] = source_caption
        figure["original_label"] = caption["label"]
        figure["caption_label"] = caption["label"]
        # The TeX caption belongs to the exact figure environment that yielded
        # this raster.  Keep it authoritative; the layout-extracted PDF text is
        # often polluted by the neighbouring column.
        figure["caption"] = source_caption
        if caption.get("page"):
            figure["page"] = caption["page"]
        candidates = []
        if source_caption:
            candidates.append(
                {
                    "label": figure.get("source_label") or caption["label"],
                    "text": source_caption,
                    "source": "tex",
                }
            )
        candidates.append(
            {"label": caption["label"], "text": caption["text"], "source": "pdf-text"}
        )
        figure["caption_candidates"] = candidates
        figure["caption_alignment"] = {
            "method": "mutual-source-caption-similarity",
            "status": "aligned",
            "confidence": round(score, 3),
            "margin": round(margin, 3),
            "reverse_margin": round(reverse_margin, 3),
        }
        aligned += 1

    manifest_path.write_text(json.dumps(figures, indent=2, ensure_ascii=False) + "\n")
    return aligned


def write_figures(entries: list[dict], outdir: Path) -> tuple[int, int]:
    """Write source rasters and pending PDF-fallback records in figure order."""
    figdir = layout.figures_dir(outdir, create=True)
    manifest = []
    source_count = 0
    fallback_count = 0
    for entry in entries:
        order = int(entry["order"])
        png = entry.get("png")
        caption = str(entry.get("caption") or "")
        label = str(entry.get("label") or "")
        clabel = f"Figure {order}"
        common = {
            "page": 0,
            "original_label": clabel,
            "caption_label": clabel,
            "caption": caption,
            "caption_candidates": [
                {"label": label or clabel, "text": caption, "source": "tex"}
            ],
            "source_label": label,
            "source_caption": caption,
            "source_order": order,
        }
        if png is None:
            manifest.append({
                **common,
                "source": "pdf-crop-pending",
                "fallback_reason": str(entry.get("fallback_reason") or "unresolved-source"),
            })
            fallback_count += 1
            continue

        final = figdir / f"figure{order}.png"
        if png.resolve() != final.resolve():
            shutil.move(str(png), str(final))
        try:
            from PIL import Image
            w, h = Image.open(final).size
        except Exception:
            w = h = 0
        manifest.append({
            **common,
            "file": f"{layout.FIGURES}/{final.name}",
            "page": 0, "page_width": w, "page_height": h,
            "width": w, "height": h, "column": "full", "num_columns": 1,
            "source": "original",
        })
        source_count += 1
    layout.meta_file(outdir, "figures", create_parent=True).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    sync_figure_captions(outdir)
    return source_count, fallback_count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--arxiv", help="arXiv id or URL — download the source tarball")
    ap.add_argument("--images", nargs="+", help="figure paths/URLs to use directly")
    ap.add_argument("--dpi", type=int, default=432)
    a = ap.parse_args()
    outdir = Path(a.outdir)
    figdir = layout.figures_dir(outdir, create=True)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        entries: list[dict] = []

        if a.images:
            for j, ref in enumerate(a.images, 1):
                src = _fetch(ref, tmp)
                if not src:
                    continue
                png = rasterize(src, tmp / f"img{j}.png", a.dpi)
                if png is not None:
                    entries.append({
                        "png": tmp / f"img{j}.png", "caption": "", "label": "",
                        "order": len(entries) + 1,
                    })
        elif a.arxiv:
            aid = _arxiv_id(a.arxiv)
            print(f"[source_figures] arXiv {aid}: downloading source…")
            if not download_arxiv_source(aid, tmp):
                _eprint("[source_figures] no source bundle — fall back to crop.")
                return 3
            main_tex = find_main_tex(tmp / "source")
            figs = parse_tex_figures(main_tex) if main_tex else []
            if figs:
                print(f"[source_figures] parsed {len(figs)} figure env(s) from {main_tex.name}")
                for k, fig in enumerate(figs, 1):
                    if len(fig["graphics"]) != 1:
                        # Keep the figure's exact TeX identity in the manifest.
                        # extract_pdf.py will align that caption to a printed
                        # Figure label and replace only this record with the
                        # rendered composite crop.
                        _eprint(
                            f"[source_figures]   fig{k}: "
                            f"{len(fig['graphics'])} includegraphics entries; "
                            "defer this composite to PDF crop"
                        )
                        entries.append({
                            "png": None,
                            "caption": fig["caption"],
                            "label": fig["label"],
                            "order": k,
                            "fallback_reason": f"composite:{len(fig['graphics'])}-graphics",
                        })
                        continue
                    ref = fig["graphics"][0]
                    src = _resolve((tmp / "source"), ref, fig["gpaths"])
                    if not src:
                        _eprint(f"[source_figures]   fig{k}: could not resolve {ref}")
                        entries.append({
                            "png": None,
                            "caption": fig["caption"],
                            "label": fig["label"],
                            "order": k,
                            "fallback_reason": "unresolved-graphic",
                        })
                        continue
                    if rasterize(src, tmp / f"f{k}.png", a.dpi) is not None:
                        entries.append({
                            "png": tmp / f"f{k}.png",
                            "caption": fig["caption"],
                            "label": fig["label"],
                            "order": k,
                        })
                    else:
                        entries.append({
                            "png": None,
                            "caption": fig["caption"],
                            "label": fig["label"],
                            "order": k,
                            "fallback_reason": "rasterize-failed",
                        })
            else:                                    # no tex figures -> all graphics
                gfx = sorted(p for p in (tmp / "source").rglob("*")
                             if p.suffix.lower() in _GRAPHIC_EXT and p.stat().st_size > 2000)
                for k, src in enumerate(gfx, 1):
                    if rasterize(src, tmp / f"f{k}.png", a.dpi) is not None:
                        entries.append({
                            "png": tmp / f"f{k}.png", "caption": "", "label": "",
                            "order": len(entries) + 1,
                        })
        else:
            _eprint("[source_figures] need --arxiv or --images")
            return 2

        if not entries:
            _eprint("[source_figures] produced 0 figures — fall back to crop.")
            return 4
        if not any(entry.get("png") is not None for entry in entries):
            _eprint("[source_figures] produced 0 source figures — fall back to full PDF crop.")
            return 4
        source_count, fallback_count = write_figures(entries, outdir)

    print(f"[source_figures] wrote {source_count} original figure(s) -> {figdir}")
    if fallback_count:
        print(
            f"[source_figures] deferred {fallback_count} figure(s) to selective PDF crop; "
            "run extract_pdf.py --no-figures to fill them"
        )
    else:
        print("[source_figures] no PDF fallback needed (crop loop skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
