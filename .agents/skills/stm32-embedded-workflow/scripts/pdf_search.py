#!/usr/bin/env python3
"""Keyword-search a folder of PDFs and report only page numbers plus short snippets.

This is the cheap step. It never returns page bodies, so it is safe to run against a
1750-page reference manual. Use the page numbers it reports with pdf_pages.py.

Usage:
    python pdf_search.py docs/boards/STM32F429I-DISC1/ --query "alternate function mapping"
    python pdf_search.py docs/boards/ -q "EXTI" -q "SYSCFG_EXTICR" --max-hits 15
    python pdf_search.py <folder> -q "USART1_TX" --file datasheet      # restrict by filename
    python pdf_search.py <folder> -q "TIMx_PSC" --context 160 --regex

Notes:
  - Matching is case-insensitive substring by default; --regex switches to regular
    expressions.
  - Multiple --query terms are OR-ed; --all requires every term on the same page, which
    is a good way to pin down a specific table.
  - Extracted text is cached per PDF under ".index/<stem>.pages.jsonl" so the second
    search on the same document is fast.

Dependencies:
    pip install pypdf     (or PyPDF2)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def _load_reader(path: Path):
    try:
        from pypdf import PdfReader  # type: ignore

        return PdfReader(str(path))
    except ImportError:
        pass
    try:
        from PyPDF2 import PdfReader  # type: ignore

        return PdfReader(str(path))
    except ImportError:
        pass
    sys.exit("No PDF backend found. Install one of:\n    pip install pypdf\n    pip install PyPDF2")


def _cache_path(pdf: Path) -> Path:
    return pdf.parent / ".index" / f"{pdf.stem}.pages.jsonl"


def _page_texts(pdf: Path, rebuild: bool = False):
    """Yield (page_number, text). Uses a jsonl cache so repeated searches are cheap."""
    cache = _cache_path(pdf)
    if cache.exists() and not rebuild:
        with cache.open(encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                yield rec["p"], rec["t"]
        return

    reader = _load_reader(pdf)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with cache.open("w", encoding="utf-8") as fh:
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            text = re.sub(r"[ \t]+", " ", text)
            fh.write(json.dumps({"p": i, "t": text}, ensure_ascii=False) + "\n")
            yield i, text


def _compile(queries, use_regex: bool):
    flags = re.IGNORECASE
    if use_regex:
        return [re.compile(q, flags) for q in queries]
    return [re.compile(re.escape(q), flags) for q in queries]


def _snippet(text: str, match: re.Match, context: int) -> str:
    start = max(0, match.start() - context // 2)
    end = min(len(text), match.end() + context // 2)
    frag = text[start:end].replace("\n", " ")
    frag = re.sub(r"\s+", " ", frag).strip()
    return ("…" if start > 0 else "") + frag + ("…" if end < len(text) else "")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="a PDF file, or a folder of PDFs")
    ap.add_argument("-q", "--query", action="append", required=True, help="search term (repeatable)")
    ap.add_argument("--all", action="store_true", help="require every term on the same page")
    ap.add_argument("--regex", action="store_true", help="treat queries as regular expressions")
    ap.add_argument("--file", help="only search PDFs whose filename contains this string")
    ap.add_argument("--max-hits", type=int, default=20, help="stop after this many hits per PDF (default 20)")
    ap.add_argument("--context", type=int, default=120, help="snippet width in characters (default 120)")
    ap.add_argument("--rebuild-cache", action="store_true")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Not found: {target}", file=sys.stderr)
        return 1

    pdfs = [target] if target.is_file() else sorted(target.rglob("*.pdf"))
    if args.file:
        pdfs = [p for p in pdfs if args.file.lower() in p.name.lower()]
    if not pdfs:
        print("No matching PDFs.", file=sys.stderr)
        return 1

    patterns = _compile(args.query, args.regex)
    grand_total = 0

    for pdf in pdfs:
        hits = []
        for page_no, text in _page_texts(pdf, rebuild=args.rebuild_cache):
            if not text:
                continue
            matches = [(pat, pat.search(text)) for pat in patterns]
            found = [(pat, m) for pat, m in matches if m]
            if not found:
                continue
            if args.all and len(found) != len(patterns):
                continue
            pat, m = found[0]
            hits.append((page_no, _snippet(text, m, args.context)))
            if len(hits) >= args.max_hits:
                break

        if not hits:
            continue
        grand_total += len(hits)
        print(f"\n## {pdf.name}")
        for page_no, snip in hits:
            print(f"  p.{page_no:<5} {snip}")

    if grand_total == 0:
        print("No hits. Try different terms — ST documents phrase things formally, e.g.\n"
              "  'alternate function mapping' not 'pin functions'\n"
              "  'external interrupt/event controller' not 'pin interrupt'\n"
              "  'peripheral clock enable register' not 'turn on clock'")
        return 2

    print(f"\n{grand_total} hit(s). Extract only what you need:")
    print("  python scripts/pdf_pages.py <pdf> --pages <start>-<end> --out .cache/<name>.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
