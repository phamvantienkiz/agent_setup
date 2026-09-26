#!/usr/bin/env python3
"""Extract a bounded range of PDF pages to a markdown file, for the agent to read.

This is the only sanctioned way to get PDF content into context. It refuses to extract
more than --max-pages (default 20) in one call, because a wider extraction is what
exhausts a session's context.

Usage:
    python pdf_pages.py datasheet.pdf --pages 76-80 --out .cache/ds-af-map.md
    python pdf_pages.py rm.pdf --pages 382,383,390-392 --out .cache/rm-exti.md
    python pdf_pages.py um.pdf --pages 22-24 --out .cache/um-leds.md --keep-layout

Options worth knowing:
    --keep-layout   preserve line breaks as extracted; helps with tables, hurts prose
    --max-pages N   raise the guard rail deliberately (say why in the dossier)
    --stdout        print instead of writing (only for ranges of 1-3 pages)

If a table comes out mangled — columns collapsed into one run of text — say so rather
than guessing its contents. Options then: render that single page as an image and look
at it, or ask the user to read that one page.

Dependencies:
    pip install pypdf         # baseline text extraction
    pip install pdfplumber    # optional, better table handling; used when available
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MAX_PAGES_DEFAULT = 20


def parse_pages(spec: str) -> list[int]:
    """'3,5,10-14' -> [3,5,10,11,12,13,14] (1-based, deduplicated, sorted)."""
    pages: set[int] = set()
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, _, b = chunk.partition("-")
            try:
                start, end = int(a), int(b)
            except ValueError:
                sys.exit(f"Bad page range: {chunk!r}")
            if end < start:
                start, end = end, start
            pages.update(range(start, end + 1))
        else:
            try:
                pages.add(int(chunk))
            except ValueError:
                sys.exit(f"Bad page number: {chunk!r}")
    return sorted(pages)


def extract_pypdf(pdf: Path, pages: list[int]) -> dict[int, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError:
        try:
            from PyPDF2 import PdfReader  # type: ignore
        except ImportError:
            sys.exit("Install a PDF backend: pip install pypdf")
    reader = PdfReader(str(pdf))
    total = len(reader.pages)
    out = {}
    for p in pages:
        if p < 1 or p > total:
            out[p] = f"[page {p} out of range; document has {total} pages]"
            continue
        try:
            out[p] = reader.pages[p - 1].extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            out[p] = f"[extraction failed: {exc}]"
    return out


def extract_plumber(pdf: Path, pages: list[int]) -> dict[int, str] | None:
    """Better for tables. Returns None if pdfplumber is unavailable."""
    try:
        import pdfplumber  # type: ignore
    except ImportError:
        return None
    out = {}
    with pdfplumber.open(str(pdf)) as doc:
        total = len(doc.pages)
        for p in pages:
            if p < 1 or p > total:
                out[p] = f"[page {p} out of range; document has {total} pages]"
                continue
            page = doc.pages[p - 1]
            body = page.extract_text() or ""
            tables = page.extract_tables() or []
            if tables:
                parts = [body, ""]
                for ti, table in enumerate(tables, start=1):
                    parts.append(f"<!-- table {ti} on page {p} -->")
                    for row in table:
                        cells = ["" if c is None else str(c).replace("\n", " ").strip() for c in row]
                        parts.append("| " + " | ".join(cells) + " |")
                    parts.append("")
                body = "\n".join(parts)
            out[p] = body
    return out


def tidy(text: str, keep_layout: bool) -> str:
    if keep_layout:
        return text
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--pages", required=True, help="e.g. 76-80 or 382,390-392")
    ap.add_argument("--out", help="output markdown path (omit with --stdout)")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--keep-layout", action="store_true", help="preserve line breaks (better for tables)")
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES_DEFAULT)
    ap.add_argument("--no-tables", action="store_true", help="skip pdfplumber table reconstruction")
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        print(f"Not found: {pdf}", file=sys.stderr)
        return 1

    pages = parse_pages(args.pages)
    if not pages:
        print("No pages requested.", file=sys.stderr)
        return 1
    if len(pages) > args.max_pages:
        print(
            f"Refusing to extract {len(pages)} pages (limit {args.max_pages}).\n"
            "Narrow the range with pdf_search.py first, or raise --max-pages on purpose.",
            file=sys.stderr,
        )
        return 2
    if args.stdout and len(pages) > 3:
        print("--stdout is limited to 3 pages; use --out for larger extracts.", file=sys.stderr)
        return 2
    if not args.stdout and not args.out:
        print("Provide --out <path.md> or --stdout.", file=sys.stderr)
        return 1

    texts = None if args.no_tables else extract_plumber(pdf, pages)
    backend = "pdfplumber"
    if texts is None:
        texts = extract_pypdf(pdf, pages)
        backend = "pypdf"

    parts = [
        f"# Extract — {pdf.name}",
        "",
        f"- pages: {args.pages}",
        f"- extractor: {backend}",
        "- cite facts from this file as `[{doc} p.N]`".replace("{doc}", pdf.stem),
        "",
    ]
    for p in pages:
        parts.append(f"\n---\n\n## page {p}\n")
        parts.append(tidy(texts.get(p, ""), args.keep_layout))
    content = "\n".join(parts) + "\n"

    if args.stdout:
        print(content)
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    chars = len(content)
    print(f"Wrote {out_path}  ({len(pages)} pages, ~{chars} chars, ~{chars // 4} tokens)")
    if chars > 60000:
        print("! That is a large extract. Consider narrowing the page range before reading it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
