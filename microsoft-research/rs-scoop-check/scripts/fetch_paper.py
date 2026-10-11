#!/usr/bin/env python3
"""fetch_paper.py - Cross-platform paper downloader and Pure Python text extractor.

Implements Solution 1 (Phương án 1): Pure Python via PyMuPDF (fitz) within .venv.
Runs identically on Windows (PowerShell/CMD), macOS, and Linux without poppler-utils.

Usage:
    python fetch_paper.py <PDF_URL> <pdf_name> [--out-dir <papers_dir>]
"""
import argparse
import sys
from pathlib import Path
import urllib.request
import urllib.error

def download_pdf(url: str, dest_path: Path, timeout: int = 60) -> bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            if not content.startswith(b"%PDF"):
                sys.stderr.write(f"FAILED: {url} did not return a valid PDF (got HTML/error payload).\n")
                return False
            dest_path.write_bytes(content)
            return True
    except Exception as e:
        sys.stderr.write(f"FAILED: Error downloading {url}: {e}\n")
        return False

def extract_text_pymupdf(pdf_path: Path, txt_path: Path) -> bool:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages_text = []
        for page in doc:
            # Layout/text extraction preserving reading order
            t = page.get_text("text") or ""
            pages_text.append(t)
        full_text = "\f".join(pages_text)
        if not full_text.strip():
            return False
        txt_path.write_text(full_text, encoding="utf-8", errors="replace")
        return True
    except Exception as e:
        sys.stderr.write(f"Warning: PyMuPDF extraction failed: {e}\n")
        return False

def main():
    parser = argparse.ArgumentParser(description="Download PDF and extract text using PyMuPDF (Pure Python).")
    parser.add_argument("url", help="Direct URL to paper PDF")
    parser.add_argument("name", help="Identifier slug for the paper")
    parser.add_argument("--out-dir", default="./papers", help="Directory to store papers")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = out_dir / f"{args.name}.pdf"
    txt_path = out_dir / f"{args.name}.txt"

    if not download_pdf(args.url, pdf_path):
        sys.exit(1)

    if not extract_text_pymupdf(pdf_path, txt_path):
        sys.stderr.write(f"FAILED: Could not extract text from {pdf_path}\n")
        sys.exit(2)

    pdf_bytes = pdf_path.stat().st_size
    txt_bytes = txt_path.stat().st_size
    txt_lines = len(txt_path.read_text(encoding="utf-8", errors="replace").splitlines())

    print(f"ok: extractor=pymupdf_pure_python pdf_bytes={pdf_bytes} txt_bytes={txt_bytes} txt_lines={txt_lines}")
    print(str(txt_path))

if __name__ == "__main__":
    main()
