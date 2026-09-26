#!/usr/bin/env python3
"""Build a compact page index for every PDF in a board documentation folder.

Why this exists: ST reference manuals run to ~1750 pages. Loading one into an agent's
context destroys the session. This script reads the PDF bookmarks (outline) and, when
there are none, the first line of each page, and writes a small index that maps
sections to page ranges. The index is what the agent reads; the PDF never is.

Usage:
    python pdf_index.py docs/boards/STM32F429I-DISC1/
    python pdf_index.py docs/boards/STM32F429I-DISC1/reference-manual-RM0090.pdf
    python pdf_index.py <path> --max-depth 2     # shallower outline, smaller index

Outputs, next to the PDFs, in a ".index/" subfolder:
    <stem>.index.json   machine-readable: title, page, level, page_count
    <stem>.index.md     human/agent-readable table of contents with page ranges

Dependencies (pick whichever is installed):
    pip install pypdf          # preferred
    pip install PyPDF2         # fallback
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ---------------------------------------------------------------- pdf backend


def _load_reader(path: Path):
    """Return (reader, module_name). Tries pypdf, then PyPDF2, then pdfplumber."""
    try:
        from pypdf import PdfReader  # type: ignore

        return PdfReader(str(path)), "pypdf"
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore

        return PdfReader(str(path)), "PyPDF2"
    except ImportError:
        pass
    sys.exit(
        "No PDF backend found. Install one of:\n"
        "    pip install pypdf\n"
        "    pip install PyPDF2"
    )


# ---------------------------------------------------------------- outline walk


def _walk_outline(reader, items, level=0, out=None, max_depth=3):
    """Flatten a nested PDF outline into [{title, page, level}, ...]."""
    if out is None:
        out = []
    if level > max_depth:
        return out
    for item in items:
        if isinstance(item, list):
            _walk_outline(reader, item, level + 1, out, max_depth)
            continue
        title = getattr(item, "title", None)
        if title is None:
            continue
        try:
            page = reader.get_destination_page_number(item) + 1  # 1-based
        except Exception:
            continue
        out.append({"title": str(title).strip(), "page": page, "level": level})
    return out


def _first_lines_index(reader, sample_every=1, max_pages=None):
    """Fallback when a PDF has no bookmarks: take the first non-empty line per page."""
    entries = []
    total = len(reader.pages)
    limit = min(total, max_pages) if max_pages else total
    for i in range(0, limit, sample_every):
        try:
            text = reader.pages[i].extract_text() or ""
        except Exception:
            text = ""
        line = ""
        for candidate in text.splitlines():
            candidate = candidate.strip()
            if len(candidate) > 3:
                line = candidate
                break
        entries.append({"title": line[:120], "page": i + 1, "level": 0})
    return entries


# ---------------------------------------------------------------- index build


def build_index(pdf_path: Path, max_depth: int = 3, fallback_sample: int = 1) -> dict:
    reader, backend = _load_reader(pdf_path)
    page_count = len(reader.pages)

    entries = []
    try:
        outline = reader.outline  # pypdf >= 3
    except AttributeError:
        outline = getattr(reader, "outlines", None)
    except Exception:
        outline = None

    if outline:
        try:
            entries = _walk_outline(reader, outline, max_depth=max_depth)
        except Exception as exc:  # noqa: BLE001
            print(f"  ! outline walk failed ({exc}); falling back to page scan")

    source = "outline"
    if not entries:
        source = "page-scan"
        print(f"  ! no usable bookmarks in {pdf_path.name}; scanning page headers "
              f"({page_count} pages, this takes a moment)")
        entries = _first_lines_index(reader, sample_every=fallback_sample)

    # derive an end page for each entry so the agent can request a bounded range
    for i, entry in enumerate(entries):
        next_start = entries[i + 1]["page"] if i + 1 < len(entries) else page_count + 1
        entry["end_page"] = max(entry["page"], next_start - 1)

    return {
        "file": pdf_path.name,
        "backend": backend,
        "page_count": page_count,
        "index_source": source,
        "entries": entries,
    }


def write_index(index: dict, out_dir: Path, stem: str) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}.index.json"
    md_path = out_dir / f"{stem}.index.md"

    json_path.write_text(json.dumps(index, indent=1, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Index — {index['file']}",
        "",
        f"- pages: {index['page_count']}",
        f"- index source: {index['index_source']}",
        "",
        "Request pages with:",
        "",
        "```bash",
        f"python scripts/pdf_pages.py <path>/{index['file']} --pages <start>-<end> --out .cache/<name>.md",
        "```",
        "",
        "| Pages | Section |",
        "|---|---|",
    ]
    for e in index["entries"]:
        span = f"{e['page']}" if e["page"] == e["end_page"] else f"{e['page']}-{e['end_page']}"
        title = e["title"].replace("|", "\\|")
        lines.append(f"| {span} | {'&nbsp;' * 4 * e['level']}{title} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


# ---------------------------------------------------------------- entry point


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="a PDF file, or a folder containing PDFs")
    ap.add_argument("--max-depth", type=int, default=3, help="outline nesting depth to keep (default 3)")
    ap.add_argument("--fallback-sample", type=int, default=1,
                    help="when a PDF has no bookmarks, scan every Nth page (default 1)")
    ap.add_argument("--force", action="store_true", help="rebuild even if an index already exists")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Not found: {target}", file=sys.stderr)
        return 1

    pdfs = [target] if target.is_file() else sorted(target.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {target}", file=sys.stderr)
        return 1

    out_dir = (target.parent if target.is_file() else target) / ".index"

    for pdf in pdfs:
        stem = pdf.stem
        if not args.force and (out_dir / f"{stem}.index.md").exists():
            print(f"= {pdf.name}: index already present (use --force to rebuild)")
            continue
        print(f"+ indexing {pdf.name} ...")
        index = build_index(pdf, max_depth=args.max_depth, fallback_sample=args.fallback_sample)
        json_path, md_path = write_index(index, out_dir, stem)
        print(f"  -> {md_path}  ({len(index['entries'])} entries, {index['page_count']} pages)")

    print(f"\nRead the .index.md files in {out_dir} — never the PDFs themselves.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
