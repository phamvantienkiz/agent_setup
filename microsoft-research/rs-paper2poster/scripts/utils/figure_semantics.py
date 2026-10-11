"""Deterministic figure selection from paper2assets semantic metadata.

The upstream ``figures.json`` contract is deliberately additive: legacy
bundles are still a bare list of physical figure records, while newer bundles
add ``semantic_roles`` and ``section_relevance`` to each record.  This module
keeps all normalization and selection rules in one place so the standalone
selector and poster preflight cannot disagree.
"""
from __future__ import annotations

import json
import hashlib
import math
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit


MOTIVATION_MIN_CONFIDENCE = 0.62
ROLE_MIN_CONFIDENCE = 0.55
MOTIVATION_VETO_CONFIDENCE = 0.55
MOTIVATION_VETO_ROLES = frozenset({"method", "result", "ablation"})
SEMANTIC_SCHEMA_VERSION = "figure_semantics.v2"
SELECTION_SCHEMA_VERSION = "paper2poster.figure-selection.v2"
CANONICAL_ROLES = frozenset({
    "motivation", "method", "dataset", "result", "ablation",
    "qualitative", "context", "unclassified",
})
SEMANTIC_COMMIT_FIELDS = (
    "file", "page", "caption", "caption_provenance", "figure_id",
    "semantic_schema_version", "semantic_eligible", "semantic_status",
    "semantic_role", "semantic_confidence", "semantic_roles",
    "section_exclusions", "section_relevance",
)


def _confidence(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, score))


def _role(value: Any) -> str:
    role = str(value or "").strip().lower().replace("_", "-")
    aliases = {
        "methods": "method", "architecture": "method", "pipeline": "method",
        "results": "result", "key-result": "result", "key-results": "result",
        "qualitative-result": "qualitative", "qualitative-results": "qualitative",
        "motivational": "motivation", "teaser": "motivation",
        "ablations": "ablation", "benchmark": "dataset",
    }
    return aliases.get(role, role)


def _section(value: Any) -> str:
    return str(value or "").strip().lower().replace("_", "-")


def normalize_asset_path(value: Any) -> str:
    """Normalize an HTML/manifest asset path without touching the filesystem."""
    raw = str(value or "").strip().replace("\\", "/")
    path = unquote(urlsplit(raw).path)
    while path.startswith("./"):
        path = path[2:]
    try:
        return str(PurePosixPath(path))
    except (TypeError, ValueError):
        return path


def load_figure_records(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict) and isinstance(payload.get("figures"), list):
        records = payload["figures"]
    else:
        raise ValueError("figures.json must be a list or an object with figures[]")
    if any(not isinstance(item, dict) for item in records):
        raise ValueError("every figures.json entry must be an object")
    return [dict(item) for item in records]


def semantic_contract_present(records: list[dict[str, Any]]) -> bool:
    """Whether records claim any part of the v2 semantic producer contract."""
    markers = {
        "semantic_schema_version", "semantic_status", "semantic_role",
        "semantic_roles", "section_relevance", "caption_provenance",
        "semantic_eligible", "section_exclusions",
    }
    return any(markers.intersection(record) for record in records)


def semantic_commit_error(
    figures_path: Path, records: list[dict[str, Any]],
) -> str | None:
    """Validate the manifest-last commit marker for the canonical package."""
    manifest_path = figures_path.parent.parent.parent / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"cannot read semantic package commit marker {manifest_path}: {exc}"
    if not isinstance(manifest, dict):
        return f"semantic package commit marker must be an object: {manifest_path}"
    expected = str(manifest.get("figure_semantics_generation") or "").strip()
    if not expected:
        return (
            "manifest.json has no figure_semantics_generation; rerun "
            "Paper2Assets build_package.py before rendering"
        )
    projection = [
        {key: record.get(key) for key in SEMANTIC_COMMIT_FIELDS}
        for record in records
    ]
    encoded = json.dumps(
        projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    actual = hashlib.sha256(encoded).hexdigest()
    if actual != expected:
        return (
            "figures.json semantic generation does not match manifest.json; "
            "rerun Paper2Assets build_package.py before rendering"
        )

    expected_paths = {
        "figures": "assets/meta/figures.json",
        "sections": "assets/meta/sections.json",
        "narration": "assets/meta/narration.json",
    }
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        return (
            "manifest.json has no canonical artifact commit records; rerun "
            "Paper2Assets build_package.py before rendering"
        )
    actual_hashes: dict[str, str] = {}
    bundle_root = manifest_path.parent
    for name, relative in expected_paths.items():
        item = artifacts.get(name)
        if not isinstance(item, dict):
            return f"manifest.json has no committed {name} artifact"
        if str(item.get("path") or "") != relative:
            return f"manifest.json has an invalid committed {name} path"
        scope = str(item.get("hash_scope") or "")
        expected_scope = (
            "semantic-selection-fields" if name == "figures"
            else "normalized-json"
        )
        if scope != expected_scope:
            return f"manifest.json has an invalid committed {name} hash scope"
        if name == "figures":
            digest = actual
        else:
            artifact_path = bundle_root / relative
            try:
                payload = json.loads(artifact_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                return f"cannot read committed {name} artifact {artifact_path}: {exc}"
            if not isinstance(payload, dict):
                return f"committed {name} artifact must be an object: {artifact_path}"
            encoded_payload = (
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            ).encode("utf-8")
            digest = hashlib.sha256(encoded_payload).hexdigest()
        if digest != str(item.get("sha256") or ""):
            return (
                f"{name} artifact generation does not match manifest.json; "
                "rerun Paper2Assets build_package.py before rendering"
            )
        actual_hashes[name] = digest

    package_generation = hashlib.sha256(
        "\n".join(
            f"{name}:{digest}" for name, digest in sorted(actual_hashes.items())
        ).encode("utf-8")
    ).hexdigest()
    if package_generation != str(manifest.get("package_generation") or ""):
        return (
            "canonical package generation does not match manifest.json; rerun "
            "Paper2Assets build_package.py before rendering"
        )
    return None


def _valid_confidence(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and 0.0 <= float(value) <= 1.0
    )


def semantics_available(records: list[dict[str, Any]]) -> bool:
    """Return true only for a complete Paper2Assets v2 producer contract.

    Older/prototype bundles sometimes carry one or two similarly named fields.
    The v2 producer annotates every record, so a mixed, malformed, or partial
    list is not a valid semantic contract and downstream callers must fail
    closed until Paper2Assets upgrades it.
    """

    required = {
        "figure_id", "semantic_schema_version", "semantic_status",
        "semantic_role", "semantic_confidence", "semantic_roles",
        "section_relevance", "caption_provenance", "semantic_eligible",
        "section_exclusions",
    }
    # An empty figure list is a valid v2 package state.  With no records the
    # per-record contract is vacuously complete; semantic_commit_error()
    # separately requires the manifest-last generation marker, so a legacy
    # empty list cannot masquerade as an upgraded bundle.
    if not records:
        return True
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    for record in records:
        if not required.issubset(record):
            return False
        if record.get("semantic_schema_version") != SEMANTIC_SCHEMA_VERSION:
            return False
        record_id = str(record.get("figure_id") or "").strip()
        record_file = figure_file(record)
        if not record_id or record_id in seen_ids:
            return False
        if (
            not record_file.startswith("assets/figures/")
            or record_file in seen_files
        ):
            return False
        seen_ids.add(record_id)
        seen_files.add(record_file)
        if record.get("semantic_status") not in {
            "classified", "unclassified", "quarantined",
        }:
            return False
        if not isinstance(record.get("semantic_eligible"), bool):
            return False
        if record.get("semantic_status") == "quarantined" and record.get(
            "semantic_eligible"
        ):
            return False
        if not isinstance(record.get("semantic_role"), str):
            return False
        confidence = record.get("semantic_confidence")
        if not _valid_confidence(confidence):
            return False
        roles = record.get("semantic_roles")
        if not isinstance(roles, list):
            return False
        seen_roles: set[str] = set()
        for item in roles:
            if not isinstance(item, dict):
                return False
            item_role = _role(item.get("role"))
            if (
                item_role not in CANONICAL_ROLES - {"unclassified"}
                or item_role in seen_roles
            ):
                return False
            seen_roles.add(item_role)
            if not _valid_confidence(item.get("confidence")):
                return False
            if not isinstance(item.get("evidence"), list):
                return False
        relevance = record.get("section_relevance")
        if not isinstance(relevance, list):
            return False
        for item in relevance:
            if (
                not isinstance(item, dict)
                or not str(item.get("section_id") or "").strip()
                or not _valid_confidence(item.get("confidence"))
                or not isinstance(item.get("evidence"), list)
            ):
                return False
        provenance = record.get("caption_provenance")
        if not isinstance(provenance, dict):
            return False
        quality = provenance.get("quality")
        if (
            not str(provenance.get("selected_source") or "").strip()
            or not isinstance(quality, dict)
            or quality.get("status") not in {"trusted", "quarantined"}
            or not isinstance(quality.get("reasons"), list)
        ):
            return False
        exclusions = record.get("section_exclusions")
        if not isinstance(exclusions, list):
            return False
        for item in exclusions:
            if (
                not isinstance(item, dict)
                or not str(item.get("section_id") or "").strip()
                or _role(item.get("role")) not in MOTIVATION_VETO_ROLES
                or not _valid_confidence(item.get("confidence"))
                or not isinstance(item.get("evidence"), list)
            ):
                return False

        primary = _role(record.get("semantic_role"))
        status = record.get("semantic_status")
        eligible = record.get("semantic_eligible")
        role_map = {
            _role(item.get("role")): float(item.get("confidence"))
            for item in roles
        }
        expected_primary = (
            min(role_map, key=lambda role: (-role_map[role], role))
            if role_map else ""
        )
        if (quality.get("status") == "trusted") != eligible:
            return False
        if status == "classified":
            if (
                not eligible
                or float(confidence) < 0.35
                or primary not in role_map
                or primary == "unclassified"
                or primary != expected_primary
                or abs(role_map[primary] - float(confidence)) > 1e-9
            ):
                return False
        elif status == "unclassified":
            if (
                not eligible
                or primary != "unclassified"
                or float(confidence) != 0.0
                or any(score >= 0.35 for score in role_map.values())
            ):
                return False
        elif (
            eligible
            or primary != "unclassified"
            or float(confidence) != 0.0
            or roles
            or quality.get("status") != "quarantined"
        ):
            return False
        for item in exclusions:
            exclusion_role = _role(item.get("role"))
            if (
                role_map.get(exclusion_role) != float(item.get("confidence"))
                or float(item.get("confidence")) < MOTIVATION_VETO_CONFIDENCE
            ):
                return False
    return True


def role_scores(record: dict[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    entries = record.get("semantic_roles")
    if isinstance(entries, list):
        for item in entries:
            if isinstance(item, dict):
                role = _role(item.get("role"))
                score = _confidence(item.get("confidence"))
            else:
                role = _role(item)
                score = 1.0
            if role:
                scores[role] = max(scores.get(role, 0.0), score)

    primary = _role(record.get("semantic_role"))
    if primary:
        scores[primary] = max(
            scores.get(primary, 0.0),
            _confidence(record.get("semantic_confidence")),
        )
    return scores


def section_scores(record: dict[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    entries = record.get("section_relevance")
    if isinstance(entries, list):
        for item in entries:
            if not isinstance(item, dict):
                continue
            section_id = _section(item.get("section_id"))
            if section_id:
                scores[section_id] = max(
                    scores.get(section_id, 0.0),
                    _confidence(item.get("confidence")),
                )
    elif isinstance(entries, dict):
        # Accept early/prototype producers that represented relevance as a map.
        for key, value in entries.items():
            section_id = _section(key)
            if section_id:
                if isinstance(value, dict):
                    value = value.get("confidence")
                scores[section_id] = _confidence(value)
    return scores


def role_evidence(record: dict[str, Any], role: str) -> list[str]:
    wanted = _role(role)
    entries = record.get("semantic_roles")
    if not isinstance(entries, list):
        return []
    for item in entries:
        if not isinstance(item, dict) or _role(item.get("role")) != wanted:
            continue
        evidence = item.get("evidence")
        if isinstance(evidence, list):
            return [str(value) for value in evidence if str(value).strip()]
        if evidence:
            return [str(evidence)]
    return []


def figure_id(record: dict[str, Any]) -> str:
    explicit = str(record.get("figure_id") or "").strip()
    if explicit:
        return explicit
    label = str(record.get("original_label") or record.get("caption_label") or "").strip()
    if label:
        return label.lower().replace(" ", "-")
    return PurePosixPath(normalize_asset_path(record.get("file") or record.get("path"))).stem


def figure_file(record: dict[str, Any]) -> str:
    return normalize_asset_path(record.get("file") or record.get("path"))


def _asset_candidates(figures_path: Path, value: Any) -> list[Path]:
    """Resolve a manifest path against the bundle without requiring one shape."""
    raw = str(value or "").strip().replace("\\", "/")
    split = urlsplit(raw)
    if split.scheme and split.scheme.lower() != "file":
        return []
    decoded = unquote(split.path)
    if not decoded:
        return []
    supplied = Path(decoded)
    if supplied.is_absolute():
        return [supplied]

    normalized = normalize_asset_path(decoded)
    assets_root = figures_path.parent.parent
    bundle_root = assets_root.parent
    candidates: list[Path] = []
    if normalized == "assets" or normalized.startswith("assets/"):
        candidates.append(bundle_root / normalized)
    elif normalized == "figures" or normalized.startswith("figures/"):
        candidates.append(assets_root / normalized)
    else:
        # Accept old manifests that stored only a basename, while retaining
        # deterministic precedence for the current assets/figures contract.
        candidates.extend([
            assets_root / "figures" / normalized,
            assets_root / normalized,
            bundle_root / normalized,
        ])
    return candidates


def asset_exists(record: dict[str, Any], figures_path: Path) -> bool:
    """Whether the record resolves to a real local asset in this bundle."""
    return any(path.is_file() for path in _asset_candidates(
        figures_path, record.get("file") or record.get("path"),
    ))


def _page(record: dict[str, Any]) -> int:
    try:
        return int(record.get("page", 10**9))
    except (TypeError, ValueError):
        return 10**9


def _candidate_score(record: dict[str, Any], role: str) -> tuple[float, float]:
    roles = role_scores(record)
    relevance = section_scores(record)
    section_ids = {
        "motivation": ("motivation",),
        "method": ("method", "method-text"),
        "result": ("key-result", "key-results", "result", "results"),
    }[role]
    return roles.get(role, 0.0), max((relevance.get(s, 0.0) for s in section_ids), default=0.0)


def eligible_for_role(record: dict[str, Any], role: str) -> bool:
    if not record.get("semantic_eligible", False):
        return False
    roles = role_scores(record)
    if role == "motivation":
        if roles.get("motivation", 0.0) < MOTIVATION_MIN_CONFIDENCE:
            return False
        if any(
            roles.get(veto, 0.0) >= MOTIVATION_VETO_CONFIDENCE
            for veto in MOTIVATION_VETO_ROLES
        ):
            return False
        return not any(
            isinstance(item, dict)
            and _section(item.get("section_id")) == "motivation"
            and _role(item.get("role")) in MOTIVATION_VETO_ROLES
            and _confidence(item.get("confidence")) >= MOTIVATION_VETO_CONFIDENCE
            for item in record.get("section_exclusions", [])
        )
    if role == "result":
        result_score = max(
            roles.get("result", 0.0), roles.get("qualitative", 0.0),
        )
        if result_score < ROLE_MIN_CONFIDENCE:
            return False
        # Captions for comparison galleries often mention "our method" even
        # though the figure's visual purpose is empirical.  Keep them eligible
        # when Result/Qualitative is within 0.08 of Method, but reject a clearly
        # method-dominant diagram.
        return roles.get("method", 0.0) <= result_score + 0.08
    if role == "method":
        method_score = roles.get("method", 0.0)
        if method_score < ROLE_MIN_CONFIDENCE:
            return False
        # Prefer an unambiguous system overview for Method.  A qualitative
        # gallery with incidental "our method"/"pipeline" wording belongs in
        # Result when its empirical score is close to the Method score.
        empirical_score = max(
            roles.get("result", 0.0),
            roles.get("ablation", 0.0),
            roles.get("qualitative", 0.0),
        )
        return empirical_score < method_score - 0.08
    return roles.get(role, 0.0) >= ROLE_MIN_CONFIDENCE


def record_for_file(records: list[dict[str, Any]], value: str) -> dict[str, Any] | None:
    wanted = normalize_asset_path(value)
    exact = [record for record in records if figure_file(record) == wanted]
    if len(exact) == 1:
        return exact[0]
    basename = PurePosixPath(wanted).name
    by_name = [
        record for record in records
        if PurePosixPath(figure_file(record)).name == basename
    ]
    return by_name[0] if len(by_name) == 1 else None


@dataclass(frozen=True)
class FigureSelection:
    role: str
    record: dict[str, Any]
    confidence: float
    section_relevance: float

    def to_dict(self) -> dict[str, Any]:
        selected_role = self.role
        if self.role == "result" and role_scores(self.record).get("result", 0.0) < self.confidence:
            selected_role = "qualitative"
        return {
            "figure_id": figure_id(self.record),
            "file": figure_file(self.record),
            "role": selected_role,
            "confidence": round(self.confidence, 4),
            "section_relevance": round(self.section_relevance, 4),
            "evidence": role_evidence(self.record, selected_role),
            "caption": str(self.record.get("caption") or "").strip(),
            "caption_provenance": self.record.get("caption_provenance"),
        }


def select_figures(
    records: list[dict[str, Any]], *, figures_path: Path | None = None,
) -> dict[str, FigureSelection | None]:
    """Select disjoint Method, optional Motivation, and Result figures.

    Sorting is deterministic: semantic confidence, section relevance, earlier
    page, stable figure id, then file path.  Motivation is evaluated after
    Method and is omitted when no high-confidence, non-method/result candidate
    remains.  Result is evaluated last and is disjoint from both.
    """
    if not semantics_available(records):
        raise ValueError(
            "figures.json lacks a complete valid figure_semantics.v2 contract"
        )

    selected: dict[str, FigureSelection | None] = {
        "method": None, "motivation": None, "result": None,
    }
    used: set[str] = set()
    for role in ("method", "motivation", "result"):
        candidates: list[tuple[tuple[Any, ...], FigureSelection]] = []
        for record in records:
            path = figure_file(record)
            if (
                not path
                or path in used
                or (figures_path is not None and not asset_exists(record, figures_path))
                or not eligible_for_role(record, role)
            ):
                continue
            role_score, relevance_score = _candidate_score(record, role)
            if role == "result":
                role_score = max(
                    role_score,
                    role_scores(record).get("qualitative", 0.0),
                )
            choice = FigureSelection(role, record, role_score, relevance_score)
            key = (
                -role_score, -relevance_score, _page(record),
                figure_id(record), path,
            )
            candidates.append((key, choice))
        if candidates:
            candidates.sort(key=lambda item: item[0])
            selected[role] = candidates[0][1]
            used.add(figure_file(candidates[0][1].record))
    return selected


def build_selection_manifest(
    records: list[dict[str, Any]], *, figures_path: Path,
) -> dict[str, Any]:
    has_semantics = semantics_available(records)
    if not has_semantics:
        raise ValueError(
            "figures.json lacks a complete valid figure_semantics.v2 contract"
        )
    selected = select_figures(records, figures_path=figures_path)
    warnings: list[str] = []
    for record in records:
        path = figure_file(record)
        if path and not asset_exists(record, figures_path):
            warnings.append(
                f"Skipped {figure_id(record) or 'unnamed figure'} because its "
                f"asset is missing: {path}"
            )
    return {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "source": "assets/meta/figures.json",
        "mode": "semantic",
        "semantics_available": has_semantics,
        "thresholds": {
            "motivation_min_confidence": MOTIVATION_MIN_CONFIDENCE,
            "role_min_confidence": ROLE_MIN_CONFIDENCE,
            "motivation_veto_confidence": MOTIVATION_VETO_CONFIDENCE,
        },
        "selections": {
            role: choice.to_dict() if choice is not None else None
            for role, choice in selected.items()
        },
        "warnings": warnings,
    }
