#!/usr/bin/env python3
"""Select poster figures deterministically from paper2assets semantics."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from utils.figure_semantics import (  # noqa: E402
    build_selection_manifest,
    load_figure_records,
    semantic_contract_present,
    semantic_commit_error,
    semantics_available,
)


def _resolve_figures_path(value: str) -> tuple[Path, Path]:
    supplied = Path(value).expanduser().resolve()
    if supplied.is_file():
        return supplied, supplied.parent.parent.parent
    figures_path = supplied / "assets" / "meta" / "figures.json"
    return figures_path, supplied


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read paper2assets figure semantics and write an auditable, "
            "disjoint Method / optional Motivation / Result selection."
        )
    )
    parser.add_argument(
        "bundle",
        help="paper2assets bundle root, or an explicit figures.json path",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "output manifest (default: "
            "<bundle>/assets/meta/figure_selection.json)"
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="also print the complete manifest as JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    figures_path, bundle_root = _resolve_figures_path(args.bundle)
    if not figures_path.is_file():
        print(f"ERROR: figures.json not found: {figures_path}", file=sys.stderr)
        return 2
    try:
        records = load_figure_records(figures_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {figures_path}: {exc}", file=sys.stderr)
        return 2
    if not semantics_available(records):
        state = (
            "invalid/partial figure_semantics.v2"
            if semantic_contract_present(records)
            else "legacy figures.json without figure_semantics.v2"
        )
        print(
            f"ERROR: {state}; upgrade the paper2assets bundle with "
            "build_package.py --skip-extract --paper-spec before selecting "
            "poster figures. Manual/raw-model fallback is disabled.",
            file=sys.stderr,
        )
        return 2
    commit_error = semantic_commit_error(figures_path, records)
    if commit_error:
        print(f"ERROR: {commit_error}", file=sys.stderr)
        return 2

    manifest = build_selection_manifest(records, figures_path=figures_path)
    out_path = (
        Path(args.out).expanduser().resolve()
        if args.out
        else bundle_root / "assets" / "meta" / "figure_selection.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"[select_figures] {manifest['mode']} -> {out_path}")
    for role, selection in manifest["selections"].items():
        if selection is None:
            suffix = " (optional; omit)" if role == "motivation" else ""
            print(f"  {role:10s} none{suffix}")
        else:
            print(
                f"  {role:10s} {selection['figure_id']}  "
                f"confidence={selection['confidence']:.2f}  "
                f"{selection['file']}"
            )
    for warning in manifest.get("warnings", []):
        print(f"  WARN: {warning}")
    if args.stdout:
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
