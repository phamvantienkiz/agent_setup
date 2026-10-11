"""Count the KaTeX-breaking patterns in a run's rendered output.

The failure is one causal chain, not four independent bugs:

  1. the RENDERER classifies a code token as math because it contains `_`
  2. wrapping the whole parenthetical, it closes the `$` after a comma
  3. that leaves an unmatched `$`, which pairs with the next `$` in the
     paragraph and swallows the prose between them into math
  4. KaTeX then renders a paragraph of italic garbage, or errors outright

So `snake_in_math` is the leading indicator; `prose_swallowed` is the symptom
the reader actually sees. A prompt change that fixes (1) should drop all four.

Usage:
  python3 scripts/lint_markdown_safety.py <file-or-run-dir> [...]
  python3 scripts/lint_markdown_safety.py --baseline old.json <dir>   # regression
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

# A CODE identifier that got dragged into math. `$E_{fit}$` and `$s_{t}$` are correct
# math and must not be counted — the tell that a token is code, not a variable, is
# structural punctuation a formula never carries: a colon, a dot between letters, or
# two or more underscore-joined segments.
SNAKE = re.compile(
    r"\$[^$\n]*?(?:"
    r"[A-Za-z0-9]+_\{[A-Za-z0-9]+\}\s*[:.]\s*[A-Za-z0-9]"      # user_{ref}:arxiv...
    r"|[A-Za-z0-9]+\s*[:.]\s*[A-Za-z0-9]+_\{"                   # torch.no_{grad}
    r"|[A-Za-z0-9]+_\{[A-Za-z0-9]+\}_\{"                        # a_{b}_{c}
    r"|\\mathit\{[A-Za-z0-9\\_]*\\_"                          # \mathit{multi\_word}
    r")[^$\n]*?\$")
# inline math closed right after a sentence comma -> guarantees an unmatched $
COMMA_CLOSE = re.compile(r"\$[^$\n]{0,200}?,\$")
# display math opened with $$ but closed by a single $
DISPLAY_HALF = re.compile(r"\$\$[^$\n]{0,200}?\$(?!\$)")
# Currency only: `$1500 vs` / `$10k`. A math span that merely starts with a digit
# (`$2\cdot K$`) is not currency, so require the digits to be followed by prose or a
# unit rather than by a math operator or macro.
CURRENCY = re.compile(r"(?<![\\$])\$\d[\d,]*(?:\.\d+)?\s*(?:[kKmM]\b|(?=\s*(?:vs\b|per\b|[A-Za-z]{3,}\b)))")
# A line whose unescaped `$` count is odd genuinely leaves math open and swallows the
# rest of the paragraph. Matching "prose between two $" does NOT detect this — the text
# between two balanced spans is ordinary prose and flagging it is a false positive.
ODD_DOLLARS = re.compile(r"^(?:[^$`\n]|`[^`\n]*`|\\\$)*\$(?:[^$`\n]|`[^`\n]*`|\\\$)*$")

CHECKS = [
    ("snake_in_math", SNAKE, "identifier subscripted inside math (root cause)"),
    ("comma_close", COMMA_CLOSE, "math closed after a sentence comma"),
    ("display_half", DISPLAY_HALF, "$$ closed by a single $"),
    ("currency_dollar", CURRENCY, "unescaped currency $ opens math"),
    ("unbalanced_line", ODD_DOLLARS, "odd number of $ on the line — math left open"),
]


def collect(target: str) -> list[str]:
    if os.path.isfile(target):
        return [target]
    # Only OUR rendered cards and phase4 artifacts. `**/*.md` also swept in the
    # Phase 0 fulltext cache of third-party papers, whose `$12/hour` and `$45 B`
    # are their authors' prose and nothing this pipeline can or should fix.
    pats = ("**/phase4/idea.*.md", "**/phase4/*.json")
    out = []
    for p in pats:
        out += glob.glob(os.path.join(target, p), recursive=True)
    return sorted(set(out))


def scan(files):
    counts = {k: 0 for k, _, _ in CHECKS}
    hits = {k: [] for k, _, _ in CHECKS}
    for f in files:
        try:
            text = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for lineno, line in enumerate(text.split("\n"), 1):
            for key, pat, _ in CHECKS:
                for m in pat.finditer(line):
                    counts[key] += 1
                    if len(hits[key]) < 5:
                        hits[key].append(f"{os.path.basename(f)}:{lineno}  {m.group(0)[:72]}")
    return counts, hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--baseline", help="JSON from a previous run, to diff against")
    ap.add_argument("--json", dest="json_out", help="write counts here")
    ap.add_argument("--quiet", action="store_true", help="counts only, no examples")
    args = ap.parse_args()

    files = []
    for t in args.targets:
        files += collect(t)
    if not files:
        print("no files matched", file=sys.stderr)
        return 2
    counts, hits = scan(files)

    base = json.load(open(args.baseline)) if args.baseline else None
    print(f"scanned {len(files)} files")
    total = 0
    for key, _, desc in CHECKS:
        n = counts[key]
        total += n
        delta = ""
        if base is not None and key in base:
            d = n - base[key]
            delta = f"   ({d:+d} vs baseline {base[key]})"
        print(f"  {key:18} {n:5}  {desc}{delta}")
        if not args.quiet:
            for h in hits[key]:
                print(f"       {h}")
    print(f"  {'TOTAL':18} {total:5}")

    if args.json_out:
        json.dump(counts, open(args.json_out, "w"), indent=1)
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
