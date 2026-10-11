#!/usr/bin/env python3
"""Deterministically add figure semantics to a paper2assets package.

The legacy ``figures.json`` shape is a list and remains a list.  Each item is
enriched in place with a stable id, semantic roles, and per-section relevance.
``sections.json`` keeps its object-style ``figures`` entries, but every entry
now carries ``figure_id`` and each section also exposes ``figure_ids`` as a
simple join key.

This module deliberately uses conservative caption/spec evidence.  In
particular, a Method or Result figure is never inferred as Motivation merely
because every poster section is expected to contain artwork.  No suitable
Motivation figure is a valid and preferable result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


SEMANTIC_SCHEMA_VERSION = "figure_semantics.v2"
PDF_CAPTION_MAX_CHARS = 1000
PDF_CAPTION_MAX_WORDS = 180

ROLE_RULES: dict[str, tuple[tuple[str, float], ...]] = {
    "motivation": (
        ("motivating example", 0.78),
        ("motivation", 0.72),
        ("failure mode", 0.72),
        ("failure case", 0.68),
        ("limitations of existing", 0.72),
        ("limitation of existing", 0.72),
        ("limitations of prior", 0.72),
        ("why existing", 0.64),
        ("teaser", 0.64),
        ("key challenge", 0.48),
        ("bottleneck", 0.42),
        ("challenge", 0.30),
    ),
    "method": (
        ("model architecture", 0.78),
        ("system architecture", 0.78),
        ("method overview", 0.78),
        ("model overview", 0.76),
        ("system overview", 0.74),
        ("overall framework", 0.76),
        ("proposed framework", 0.76),
        ("proposed method", 0.76),
        ("our framework", 0.72),
        ("our method", 0.72),
        ("our model", 0.68),
        ("architecture", 0.62),
        ("pipeline", 0.66),
        ("workflow", 0.64),
        ("algorithm", 0.48),
        ("training procedure", 0.48),
        ("inference procedure", 0.48),
    ),
    "dataset": (
        ("dataset overview", 0.76),
        ("benchmark overview", 0.74),
        ("data collection", 0.68),
        ("dataset construction", 0.72),
        ("dataset statistics", 0.72),
        ("data distribution", 0.68),
        ("dataset", 0.48),
        ("benchmark", 0.42),
        ("distribution of", 0.38),
    ),
    "result": (
        ("quantitative results", 0.78),
        ("experimental results", 0.76),
        ("main results", 0.74),
        ("performance comparison", 0.72),
        ("comparison with state of the art", 0.76),
        ("outperforms", 0.62),
        ("performance", 0.54),
        ("accuracy", 0.46),
        ("evaluation", 0.42),
        ("results", 0.44),
        ("versus", 0.34),
    ),
    "ablation": (
        ("ablation study", 0.88),
        ("ablation", 0.84),
        ("component analysis", 0.72),
        ("effect of each", 0.68),
        ("effect of different", 0.58),
        ("sensitivity analysis", 0.70),
        ("hyperparameter analysis", 0.66),
    ),
    "qualitative": (
        ("qualitative comparison", 0.76),
        ("qualitative results", 0.76),
        ("visual comparison", 0.66),
        ("visualization", 0.56),
        ("generated examples", 0.64),
        ("example outputs", 0.62),
        ("examples of", 0.46),
        ("case study", 0.52),
    ),
    "context": (
        ("problem setup", 0.68),
        ("task overview", 0.62),
        ("illustration of the problem", 0.70),
        ("existing approaches", 0.58),
        ("prior methods", 0.48),
    ),
}

SECTION_ROLE = {
    "problem": "context",
    "motivation": "motivation",
    "contribution": "method",
    "method": "method",
    "dataset-benchmark": "dataset",
    "dataset": "dataset",
    "benchmark": "dataset",
    "key-result": "result",
    "key-results": "result",
    "result": "result",
    "results": "result",
    "ablation-study": "ablation",
    "ablation": "ablation",
    "headline-numbers": "result",
}

# Some downstream sections intentionally accept more than one visual role.
# A qualitative comparison is empirical evidence, so it is a valid Key Result
# even when its caption never uses the generic word "result".  Keep the
# broader mapping narrow: Headline Numbers still expects quantitative Result
# evidence, and Motivation remains Motivation-only with its separate vetoes.
SECTION_ROLE_ALTERNATIVES = {
    "key-result": ("result", "qualitative"),
    "key-results": ("result", "qualitative"),
    "result": ("result", "qualitative"),
    "results": ("result", "qualitative"),
}

SECTION_THRESHOLDS = {
    "problem": 0.62,
    "motivation": 0.62,
    "contribution": 0.68,
    "method": 0.55,
    "dataset-benchmark": 0.58,
    "dataset": 0.58,
    "benchmark": 0.58,
    "key-result": 0.55,
    "key-results": 0.55,
    "result": 0.55,
    "results": 0.55,
    "ablation-study": 0.62,
    "ablation": 0.62,
    "headline-numbers": 0.68,
}

ROLE_THRESHOLDS = {
    "context": 0.58,
    "motivation": 0.62,
    "method": 0.55,
    "dataset": 0.42,
    "result": 0.50,
    "ablation": 0.62,
}

STOPWORDS = {
    "about", "after", "again", "against", "also", "among", "and", "are",
    "because", "been", "before", "being", "between", "both", "but", "can",
    "each", "figure", "for", "from", "has", "have", "into", "its", "more",
    "most", "not", "our", "paper", "proposed", "results", "show", "shows",
    "that", "the", "their", "these", "this", "those", "through", "using",
    "versus", "was", "were", "which", "while", "with", "without",
}


def _round_confidence(value: float) -> float:
    return round(max(0.0, min(0.99, value)), 2)


def _normal_text(value: Any) -> str:
    value = str(value or "").lower().replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", value).strip()


def _tokens(value: Any) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z][a-z0-9-]{2,}", _normal_text(value))
        if token not in STOPWORDS
    }


def _slug(value: Any) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", _normal_text(value)).strip("-")
    return slug


def _caption_map(captions: Any) -> dict[str, str]:
    mapped: dict[str, str] = {}
    if isinstance(captions, dict):
        for label, text in captions.items():
            if str(label).lower().startswith("figure"):
                mapped[_normal_text(label)] = str(text or "")
    elif isinstance(captions, list):
        for item in captions:
            if not isinstance(item, dict):
                continue
            label = item.get("label", "")
            if str(label).lower().startswith("figure"):
                mapped[_normal_text(label)] = str(item.get("text", "") or "")
    return mapped


def _caption_quality(caption: str, source: str) -> dict[str, Any]:
    """Assess whether caption text is safe to use as semantic evidence."""
    reasons: list[str] = []
    text = re.sub(r"\s+", " ", str(caption or "")).strip()
    words = re.findall(r"\b\w+\b", text)
    if not text:
        reasons.append("empty caption")
    if source == "source-manifest-legacy":
        reasons.append(
            "source raster lacks explicit TeX caption provenance; re-extract assets"
        )
    if source == "pdf-text":
        if len(text) > PDF_CAPTION_MAX_CHARS:
            reasons.append(
                f"PDF caption exceeds {PDF_CAPTION_MAX_CHARS} characters"
            )
        if len(words) > PDF_CAPTION_MAX_WORDS:
            reasons.append(f"PDF caption exceeds {PDF_CAPTION_MAX_WORDS} words")
        if "\f" in caption:
            reasons.append("PDF caption crosses a page boundary")
        if re.search(
            r"\b(?:figure|fig\.?|table)\s+\d+\s*[:.]",
            text[1:],
            re.IGNORECASE,
        ):
            reasons.append("PDF caption contains another caption header")
    return {
        "status": "trusted" if not reasons else "quarantined",
        "source": source,
        "character_count": len(text),
        "word_count": len(words),
        "reasons": reasons,
    }


def _semantic_caption_text(caption: str, source: str) -> str:
    """Return only caption text safe enough to drive semantic role scoring.

    ``pdftotext -layout`` cannot reliably distinguish a wrapped caption from
    the next paragraph in the same column.  Keep the full PDF text for display
    and provenance, but restrict semantic evidence to its lead sentence.  TeX
    captions have exact figure-environment provenance and may use the full
    text.
    """
    text = re.sub(r"\s+", " ", str(caption or "")).strip()
    if source != "pdf-text":
        return text
    match = re.match(r"^(.+?[.!?])(?:\s|$)", text)
    return match.group(1).strip() if match else text


def _select_caption(
    figure: dict[str, Any], *, original_label: str, mapped_caption: str,
) -> tuple[str, str, list[dict[str, Any]]]:
    """Select caption text with TeX/source provenance taking precedence."""
    raw_candidates = figure.get("caption_candidates")
    candidates = [
        dict(item) for item in raw_candidates
        if isinstance(item, dict) and str(item.get("text") or "").strip()
    ] if isinstance(raw_candidates, list) else []

    source_caption = str(figure.get("source_caption") or "").strip()
    if not source_caption:
        for item in candidates:
            if str(item.get("source") or "").lower() in {
                "tex", "latex", "arxiv-source", "source-manifest",
            }:
                source_caption = str(item.get("text") or "").strip()
                if source_caption:
                    break

    current_caption = str(figure.get("caption") or "").strip()
    alignment = figure.get("caption_alignment")
    alignment_status = (
        str(alignment.get("status") or "").lower()
        if isinstance(alignment, dict) else ""
    )
    # Source-first rasters are initially assigned generated ``Figure i``
    # labels.  Only caption alignment can prove that such a label denotes the
    # same PDF figure.  Without that proof, an ordinal lookup would silently
    # shift captions after any skipped/unresolved source graphic.
    mapped_is_aligned = not (
        figure.get("source") == "original"
        and not source_caption
        and alignment_status != "aligned"
    )
    if not mapped_is_aligned:
        mapped_caption = ""
    if source_caption:
        selected, selected_source = source_caption, "tex"
    elif current_caption:
        selected = current_caption
        if figure.get("source") == "original":
            selected_source = "source-manifest-legacy"
        elif figure.get("source") == "pdf-crop":
            selected_source = "pdf-text"
        else:
            selected_source = (
                "pdf-text"
                if not mapped_caption
                or _normal_text(current_caption) == _normal_text(mapped_caption)
                else "figure-manifest"
            )
    else:
        selected, selected_source = mapped_caption, "pdf-text"

    additions = [
        (source_caption, "tex"),
        (mapped_caption, "pdf-text"),
    ]
    for text, source in additions:
        if not text or any(
            _normal_text(item.get("text")) == _normal_text(text)
            for item in candidates
        ):
            continue
        candidates.append({
            "label": original_label,
            "text": text,
            "source": source,
        })
    return selected, selected_source, candidates


def _figure_id(figure: dict[str, Any], used: set[str]) -> str:
    existing = _slug(figure.get("figure_id"))
    if existing and existing not in used:
        used.add(existing)
        return existing

    label = figure.get("original_label") or figure.get("caption_label")
    label_slug = _slug(label)
    if label_slug:
        candidate = label_slug if label_slug.startswith("figure-") else f"figure-{label_slug}"
    else:
        stem = Path(str(figure.get("file", "figure"))).stem
        candidate = f"figure-{_slug(stem) or 'asset'}"
    if candidate in used:
        fingerprint = hashlib.sha1(str(figure.get("file", "")).encode()).hexdigest()[:8]
        candidate = f"{candidate}-{fingerprint}"
    collision_base = candidate
    collision_index = 2
    while candidate in used:
        candidate = f"{collision_base}-{collision_index}"
        collision_index += 1
    used.add(candidate)
    return candidate


def _score_roles(caption: str, ordinal: int) -> list[dict[str, Any]]:
    text = _normal_text(caption)
    lead = text.split(".", 1)[0][:180]
    scored: list[dict[str, Any]] = []
    for role, rules in ROLE_RULES.items():
        hits = [(phrase, weight) for phrase, weight in rules if phrase in text]
        if not hits:
            continue
        hits.sort(key=lambda pair: pair[1], reverse=True)
        confidence = hits[0][1] + min(0.16, 0.05 * (len(hits) - 1))
        evidence = [f'caption phrase: "{phrase}"' for phrase, _ in hits[:4]]
        if role == "method" and ordinal <= 2:
            confidence += 0.04
            evidence.append(f"early-figure prior: ordinal {ordinal}")
        if role == "qualitative" and any(
            phrase in lead
            for phrase in (
                "qualitative comparison",
                "qualitative results",
                "visual comparison",
            )
        ):
            # An explicit caption lead describes what the figure is.  Do not
            # let generic prose later in the caption (for example "our method"
            # or "pipeline") turn an evaluation showcase into an architecture
            # figure merely because two broad Method phrases happen to occur.
            confidence += 0.12
            evidence.append("explicit qualitative role in caption lead")
        scored.append(
            {
                "role": role,
                "confidence": _round_confidence(confidence),
                "evidence": evidence,
            }
        )
    scored.sort(key=lambda item: (-item["confidence"], item["role"]))
    return scored


def _section_text(section: dict[str, Any]) -> str:
    return " ".join(
        str(section.get(key, "") or "")
        for key in ("heading", "necessary", "additional", "audio_script")
    )


def _expected_roles(section_id: str) -> tuple[str, ...]:
    alternatives = SECTION_ROLE_ALTERNATIVES.get(section_id)
    if alternatives:
        return alternatives
    primary = SECTION_ROLE.get(section_id)
    return (primary,) if primary else ()


def _score_section_relevance(
    *,
    caption: str,
    roles: list[dict[str, Any]],
    sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    role_by_name = {item["role"]: item for item in roles}
    caption_tokens = _tokens(caption)
    relevance: list[dict[str, Any]] = []
    for section in sections:
        section_id = _slug(section.get("id") or section.get("heading"))
        expected_roles = _expected_roles(section_id)
        role_item = max(
            (role_by_name[role] for role in expected_roles if role in role_by_name),
            key=lambda item: float(item["confidence"]),
            default=None,
        )
        evidence: list[str] = []
        score = 0.0
        if role_item:
            score = float(role_item["confidence"])
            evidence.append(
                f"semantic role {role_item['role']}: {role_item['confidence']:.2f}"
            )

        section_tokens = _tokens(_section_text(section))
        shared = sorted(caption_tokens & section_tokens)
        if len(shared) >= 2:
            denom = max(4, min(12, len(section_tokens), len(caption_tokens)))
            lexical = min(0.74, 0.20 + 1.15 * len(shared) / denom)
            # Lexical overlap explains/refines an already-supported semantic
            # role.  By itself it is weak evidence: paper summaries naturally
            # repeat the title, method name, and words such as "poster" across
            # many sections.  Capping lexical-only relevance below every auto
            # assignment threshold prevents that repetition from manufacturing
            # a Motivation figure.
            if role_item:
                score = max(score, lexical)
                evidence.append("caption/spec overlap: " + ", ".join(shared[:8]))
            else:
                score = max(score, min(0.54, lexical))
                evidence.append(
                    "lexical-only caption/spec overlap (no semantic role support): "
                    + ", ".join(shared[:8])
                )

        if score >= 0.28:
            relevance.append(
                {
                    "section_id": section_id,
                    "confidence": _round_confidence(score),
                    "evidence": evidence,
                }
            )
    relevance.sort(key=lambda item: (-item["confidence"], item["section_id"]))
    return relevance


def enrich_figures(
    figures: Any,
    captions: Any,
    sections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return a legacy-compatible enriched figures list."""
    if not isinstance(figures, list):
        return []
    cap_map = _caption_map(captions)
    used_ids: set[str] = set()
    enriched: list[dict[str, Any]] = []
    for ordinal, raw in enumerate(figures, 1):
        if not isinstance(raw, dict):
            continue
        figure = dict(raw)
        original_label = str(
            figure.get("original_label") or figure.get("caption_label") or ""
        ).strip()
        mapped_caption = cap_map.get(_normal_text(original_label), "")
        caption, caption_source, candidates = _select_caption(
            figure,
            original_label=original_label,
            mapped_caption=mapped_caption,
        )
        quality = _caption_quality(caption, caption_source)
        semantic_eligible = quality["status"] == "trusted"
        semantic_caption = _semantic_caption_text(caption, caption_source)
        figure_id = _figure_id(figure, used_ids)
        roles = _score_roles(semantic_caption, ordinal) if semantic_eligible else []
        primary = roles[0] if roles and roles[0]["confidence"] >= 0.35 else None

        figure["caption"] = caption
        figure["caption_candidates"] = candidates
        figure["caption_provenance"] = {
            "selected_source": caption_source,
            "quality": quality,
            "semantic_evidence_text": semantic_caption,
        }
        figure["figure_id"] = figure_id
        figure["original_label"] = original_label
        figure["semantic_schema_version"] = SEMANTIC_SCHEMA_VERSION
        figure["semantic_eligible"] = semantic_eligible
        figure["semantic_status"] = (
            "classified" if primary
            else "unclassified" if semantic_eligible
            else "quarantined"
        )
        figure["semantic_role"] = primary["role"] if primary else "unclassified"
        figure["semantic_confidence"] = primary["confidence"] if primary else 0.0
        figure["semantic_roles"] = roles
        figure["section_exclusions"] = [
            {
                "section_id": "motivation",
                "role": item["role"],
                "confidence": item["confidence"],
                "evidence": list(item.get("evidence", [])),
            }
            for item in roles
            if item["role"] in {"method", "result", "ablation"}
            and float(item["confidence"]) >= 0.55
        ]
        figure["section_relevance"] = _score_section_relevance(
            caption=semantic_caption,
            roles=roles,
            sections=sections,
        )
        enriched.append(figure)
    return enriched


def _path_key(value: Any) -> str:
    return str(value or "").replace("\\", "/").lstrip("./")


def attach_figures_to_sections(
    sections: list[dict[str, Any]],
    figures: list[dict[str, Any]],
) -> None:
    """Populate section figure refs, preserving explicit Markdown choices."""
    by_path = {_path_key(fig.get("file")): fig for fig in figures}
    by_name = {Path(key).name: fig for key, fig in by_path.items()}
    by_id = {fig.get("figure_id"): fig for fig in figures}

    for section in sections:
        section_id = _slug(section.get("id") or section.get("heading"))
        refs: list[dict[str, Any]] = []
        seen: set[str] = set()

        for explicit in section.get("figures", []):
            # Recomputed semantic refs from a previous idempotent package
            # refresh are candidates, not author-explicit Markdown choices.
            if explicit.get("source") == "figure_semantics":
                continue
            path = _path_key(explicit.get("path"))
            explicit_id = str(explicit.get("figure_id") or "").strip()
            id_figure = by_id.get(explicit_id) if explicit_id else None
            path_figure = by_path.get(path) if path else None
            if path_figure is None and path:
                path_figure = by_name.get(Path(path).name)
            if explicit_id and id_figure is None:
                raise ValueError(
                    f"section {section_id!r} references unknown figure_id "
                    f"{explicit_id!r}"
                )
            if path and path_figure is None:
                raise ValueError(
                    f"section {section_id!r} references unknown figure path {path!r}"
                )
            if id_figure is not None and path_figure is not None and id_figure is not path_figure:
                raise ValueError(
                    f"section {section_id!r} has conflicting figure_id/path "
                    f"references ({explicit_id!r}, {path!r})"
                )
            figure = id_figure or path_figure
            if figure is None:
                raise ValueError(
                    f"section {section_id!r} has an explicit figure without "
                    "figure_id or path"
                )
            if not figure.get("semantic_eligible", False):
                continue
            if section_id == "motivation":
                explicit_role_conf = {
                    item.get("role"): float(item.get("confidence", 0))
                    for item in figure.get("semantic_roles", [])
                }
                if explicit_role_conf.get("motivation", 0) < 0.62 or any(
                    explicit_role_conf.get(role, 0) >= 0.55
                    for role in ("method", "result", "ablation")
                ):
                    # Explicit placement is strong positive evidence, but it
                    # must not override a direct contradictory semantic role.
                    # A text-only Motivation remains safer than a Method or
                    # Result diagram in the wrong section.
                    continue
            figure_id = str(figure["figure_id"])
            if figure_id in seen:
                continue
            ref = dict(explicit)
            ref.update(
                {
                    "figure_id": figure_id,
                    "path": _path_key(figure.get("file")),
                    "confidence": 1.0,
                    "evidence": ["explicit Markdown image in paper_spec.md"],
                    "source": "paper_spec_explicit",
                }
            )
            refs.append(ref)
            seen.add(figure_id)

        threshold = SECTION_THRESHOLDS.get(section_id)
        if threshold is not None:
            expected_roles = _expected_roles(section_id)
            candidates: list[tuple[float, dict[str, Any], dict[str, Any]]] = []
            for figure in figures:
                if not figure.get("semantic_eligible", False):
                    continue
                relevance = next(
                    (
                        item
                        for item in figure.get("section_relevance", [])
                        if item.get("section_id") == section_id
                    ),
                    None,
                )
                if relevance is None or float(relevance.get("confidence", 0)) < threshold:
                    continue
                role_conf = {
                    item.get("role"): float(item.get("confidence", 0))
                    for item in figure.get("semantic_roles", [])
                }
                # Automatic references require direct role evidence.  Lexical
                # overlap only ranks candidates that already have the expected
                # role; it never creates a section assignment on its own.
                expected_role = max(
                    expected_roles,
                    key=lambda role: role_conf.get(role, 0),
                    default="",
                )
                expected_conf = role_conf.get(expected_role, 0)
                expected_threshold = ROLE_THRESHOLDS.get(expected_role, 0.55)
                if expected_roles and expected_conf < expected_threshold:
                    continue
                if section_id == "motivation" and any(
                    role_conf.get(role, 0) >= 0.55
                    for role in ("method", "result", "ablation")
                ):
                    continue
                if expected_role == "method" and any(
                    role_conf.get(role, 0) > expected_conf + 0.08
                    for role in ("result", "ablation", "qualitative")
                ):
                    continue
                candidates.append((float(relevance["confidence"]), figure, relevance))

            candidates.sort(
                key=lambda row: (
                    -row[0],
                    str(row[1].get("figure_id", "")),
                )
            )
            # One high-confidence figure is enough for Motivation/Problem;
            # Method/Result/Dataset/Ablation may expose two downstream choices.
            limit = 1 if section_id in {"problem", "motivation"} else 2
            for confidence, figure, relevance in candidates[:limit]:
                figure_id = str(figure["figure_id"])
                if figure_id in seen:
                    continue
                refs.append(
                    {
                        "figure_id": figure_id,
                        "confidence": _round_confidence(confidence),
                        "evidence": list(relevance.get("evidence", [])),
                        "source": "figure_semantics",
                    }
                )
                seen.add(figure_id)

        section["figures"] = refs
        section["figure_ids"] = [
            ref["figure_id"]
            for ref in refs
            if isinstance(ref, dict) and ref.get("figure_id")
        ]


def annotate_documents(
    figures: Any,
    captions: Any,
    sections_doc: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not isinstance(figures, list) or any(
        not isinstance(item, dict) for item in figures
    ):
        raise ValueError("figures.json must be a list of objects")
    figure_paths = [_path_key(item.get("file")) for item in figures]
    if any(not path for path in figure_paths) or len(set(figure_paths)) != len(figure_paths):
        raise ValueError("figures.json file paths must be non-empty and unique")
    if isinstance(captions, list):
        if any(not isinstance(item, dict) for item in captions):
            raise ValueError("captions.json list entries must be objects")
    elif isinstance(captions, dict):
        if any(not isinstance(value, str) for value in captions.values()):
            raise ValueError("captions.json object values must be strings")
    else:
        raise ValueError("captions.json must be an object or list")
    if not isinstance(sections_doc, dict):
        raise ValueError("sections.json must be an object")
    required_section_fields = {
        "schema_version": str,
        "created_at": str,
        "title": str,
        "authors": str,
        "institutes": list,
        "title_audio_script": str,
        "sections": list,
        "status": str,
    }
    if "source_spec" not in sections_doc or not isinstance(
        sections_doc["source_spec"], (str, type(None))
    ):
        raise ValueError("sections.json field 'source_spec' must be a string or null")
    missing = sorted(set(required_section_fields).difference(sections_doc))
    if missing:
        raise ValueError(
            "sections.json is missing required field(s): " + ", ".join(missing)
        )
    for key, expected in required_section_fields.items():
        if not isinstance(sections_doc[key], expected):
            raise ValueError(
                f"sections.json field {key!r} must be {expected.__name__}"
            )
    if any(not isinstance(value, str) for value in sections_doc["institutes"]):
        raise ValueError("sections.json institutes entries must be strings")
    if sections_doc["schema_version"] not in {
        "paper_sections.v1", "paper_sections.v2",
    }:
        raise ValueError("sections.json has an unsupported schema_version")
    if sections_doc["status"] not in {"synced", "empty_until_spec_sync"}:
        raise ValueError("sections.json has an unsupported status")
    sections = sections_doc["sections"]
    if not isinstance(sections, list) or any(
        not isinstance(section, dict) for section in sections
    ):
        raise ValueError("sections.json sections must be a list of objects")
    section_ids: set[str] = set()
    for section in sections:
        required = {
            "id": str,
            "heading": str,
            "necessary": str,
            "additional": str,
            "audio_script": str,
            "figures": list,
            "tables": list,
            "source": dict,
        }
        missing = sorted(set(required).difference(section))
        if missing:
            raise ValueError(
                "sections.json section is missing required field(s): "
                + ", ".join(missing)
            )
        for key, expected in required.items():
            if not isinstance(section[key], expected):
                raise ValueError(
                    f"sections.json section field {key!r} must be "
                    f"{expected.__name__}"
                )
        section_id = str(section["id"]).strip()
        if not section_id or section_id in section_ids:
            raise ValueError("sections.json section ids must be non-empty and unique")
        section_ids.add(section_id)
        refs = section.get("figures", [])
        if not isinstance(refs, list) or any(
            not isinstance(ref, dict) for ref in refs
        ):
            raise ValueError("every section figures field must be a list of objects")
    enriched = enrich_figures(figures, captions, sections)
    attach_figures_to_sections(sections, enriched)
    sections_doc["figure_semantics_schema_version"] = SEMANTIC_SCHEMA_VERSION
    return enriched, sections_doc


def _load_required_json(path: Path, expected: type | tuple[type, ...]) -> Any:
    if not path.is_file():
        raise SystemExit(f"required JSON file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read required JSON file {path}: {exc}") from exc
    if not isinstance(payload, expected):
        names = (
            ", ".join(item.__name__ for item in expected)
            if isinstance(expected, tuple) else expected.__name__
        )
        raise SystemExit(f"invalid JSON shape in {path}: expected {names}")
    return payload


def _write_json_atomic(path: Path, payload: Any) -> None:
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        temp.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures", required=True, help="Path to figures.json")
    parser.add_argument("--captions", required=True, help="Path to captions.json")
    parser.add_argument("--sections", required=True, help="Path to sections.json")
    args = parser.parse_args()
    figure_path = Path(args.figures)
    caption_path = Path(args.captions)
    section_path = Path(args.sections)
    sections_doc = _load_required_json(section_path, dict)
    figures, sections_doc = annotate_documents(
        _load_required_json(figure_path, list),
        _load_required_json(caption_path, (list, dict)),
        sections_doc,
    )
    _write_json_atomic(figure_path, figures)
    _write_json_atomic(section_path, sections_doc)
    print(
        f"[paper2assets/semantics] annotated {len(figures)} figures and "
        f"{len(sections_doc.get('sections', []))} sections"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
