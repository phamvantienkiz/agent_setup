#!/usr/bin/env python3
"""Trích xuất văn bản bài báo PDF theo trang và lập chỉ mục để AI định vị nhanh.

Dùng:  python extract_paper.py paper.pdf --out ./paper_out

Tạo trong thư mục --out:
  pages/page_001.txt ...   văn bản từng trang
  full.txt                 toàn văn, có dấu mốc "=== TRANG n ==="
  index.md                 chỉ mục: metadata, nơi công bố/phiên bản, các mục, caption Bảng/Hình, định lý

Lưu ý: bảng gộp ô, công thức, chỉ số trên/dưới có thể bị trích xuất sai. Hãy mở PDF để đối chiếu.
"""
import argparse
import re
import sys
from pathlib import Path


def extract_pages(path):
    pages = []
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                pages.append(p.extract_text() or "")
        if sum(len(t) for t in pages) > 200:
            return pages, "pdfplumber"
    except Exception:
        pass
    try:
        import pypdf
        r = pypdf.PdfReader(path)
        pages = [(p.extract_text() or "") for p in r.pages]
        if sum(len(t) for t in pages) > 200:
            return pages, "pypdf"
    except Exception:
        pass
    return pages, "none"


SECTION_RE = re.compile(
    r"^\s*((?:[0-9]{1,2}(?:\.[0-9]{1,2}){0,2}\.?)|(?:[IVX]{1,5}\.)|(?:[A-Z]\.))\s+([A-Z][^\n]{2,90})$")
NAMED = {"abstract", "introduction", "related work", "background", "preliminaries", "method",
         "methods", "methodology", "approach", "model", "experiments", "experimental results",
         "results", "evaluation", "discussion", "limitations", "conclusion", "conclusions",
         "references", "appendix", "acknowledgments", "acknowledgements"}
CAPTION_RE = re.compile(
    r"^\s*(Table|Figure|Fig\.|Algorithm|Bảng|Hình)\s*([0-9]+[a-z]?)\s*[:.\-–]?\s*(.{0,140})", re.I)
THEOREM_RE = re.compile(
    r"^\s*(Theorem|Lemma|Proposition|Corollary|Definition|Assumption|Định lý|Bổ đề|Mệnh đề|Định nghĩa)\s*([0-9.]*)",
    re.I)
VENUE_RE = re.compile(
    r"(Accepted|Proceedings|Conference|Workshop|Journal|Transactions|arXiv|preprint|Technical Report|TR[0-9\-]+|"
    r"under review|submitted|ICML|NeurIPS|ICLR|CVPR|ICCV|ECCV|ACL|EMNLP|AAAI|IJCAI|SIGMOD|VLDB|SOSP|OSDI|"
    r"©|Copyright|IEEE|ACM|Springer|Elsevier)", re.I)
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)")
ARXIV_RE = re.compile(r"arXiv:\s*([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)", re.I)


def build_index(pages, engine, src):
    out = [f"# Chỉ mục: {src.name}", "",
           f"- Số trang: {len(pages)} · Công cụ trích xuất: {engine}"]
    chars = sum(len(t) for t in pages)
    if engine == "none" or chars < 200:
        out += ["", "> CẢNH BÁO: gần như không trích được văn bản (có thể là PDF dạng ảnh/scan). "
                "Cần OCR hoặc xin người dùng dán văn bản.", ""]
        return "\n".join(out)

    full = "\n".join(pages)
    head = "\n".join(pages[:2])
    doi = sorted(set(DOI_RE.findall(full)))[:5]
    arx = sorted(set(ARXIV_RE.findall(full)))[:3]
    out.append(f"- DOI phát hiện: {', '.join(doi) if doi else '(không thấy)'}")
    out.append(f"- arXiv ID phát hiện: {', '.join(arx) if arx else '(không thấy)'}")

    out += ["", "## Dòng liên quan đến nơi công bố / phiên bản (từ 2 trang đầu)",
            "_Đối chiếu để phát hiện: tech report vs bản hội nghị, preprint vs đã bình duyệt._", ""]
    seen = set()
    for i, t in enumerate(pages[:2], 1):
        for line in t.splitlines():
            s = line.strip()
            if 6 < len(s) < 200 and VENUE_RE.search(s) and s not in seen:
                seen.add(s)
                out.append(f"- (tr.{i}) {s}")
    if not seen:
        out.append("- (không thấy dòng nào)")
    if re.search(r"arxiv|preprint|under review", head, re.I):
        out += ["", "> LƯU Ý: có dấu hiệu preprint. Tìm thấy ≠ đã được thẩm định; "
                "cần đối chiếu phiên bản chính thức."]

    out += ["", "## Các mục (suy đoán từ định dạng dòng)", ""]
    for i, t in enumerate(pages, 1):
        for line in t.splitlines():
            s = line.strip()
            m = SECTION_RE.match(s)
            if (m and not re.search(r"[.,;]\s*$", s) and len(s) < 100) or s.lower().rstrip(".:") in NAMED:
                out.append(f"- tr.{i}: {s}")

    caps = []
    for i, t in enumerate(pages, 1):
        for line in t.splitlines():
            m = CAPTION_RE.match(line)
            if m:
                caps.append(f"- tr.{i}: {m.group(1).capitalize()} {m.group(2)} - {m.group(3).strip()}")
    out += ["", "## Bảng / Hình / Thuật toán (caption)", ""] + (caps or ["- (không thấy)"])

    thms = []
    for i, t in enumerate(pages, 1):
        for line in t.splitlines():
            if THEOREM_RE.match(line):
                thms.append(f"- tr.{i}: {line.strip()[:120]}")
    out += ["", "## Định nghĩa / Bổ đề / Định lý / Giả định", ""] + (thms or ["- (không thấy)"])

    refs = [i for i, t in enumerate(pages, 1)
            if re.search(r"^\s*(references|tài liệu tham khảo)\s*$", t, re.I | re.M)]
    if refs:
        out += ["", f"- Danh mục tham khảo bắt đầu khoảng trang {refs[0]}."]
    out += ["", "## Gợi ý dùng",
            "- Dùng số trang ở trên để mở đúng đoạn trong `pages/`; trích dẫn vị trí (Mục/Bảng/Trang) trong câu trả lời.",
            "- Với bảng và công thức, đọc cả caption lẫn đoạn văn nhắc đến chúng; xác nhận lại trên PDF gốc."]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    src = Path(a.pdf)
    if not src.exists():
        sys.exit(f"Không thấy tệp: {src}")
    out = Path(a.out or (src.stem + "_extracted"))
    (out / "pages").mkdir(parents=True, exist_ok=True)
    pages, engine = extract_pages(str(src))
    for i, t in enumerate(pages, 1):
        (out / "pages" / f"page_{i:03d}.txt").write_text(t, encoding="utf-8")
    (out / "full.txt").write_text(
        "\n".join(f"\n=== TRANG {i} ===\n{t}" for i, t in enumerate(pages, 1)), encoding="utf-8")
    (out / "index.md").write_text(build_index(pages, engine, src), encoding="utf-8")
    print(f"Đã trích {len(pages)} trang bằng {engine} → {out}/index.md")


if __name__ == "__main__":
    main()