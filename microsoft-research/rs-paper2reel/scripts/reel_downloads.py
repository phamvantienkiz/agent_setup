#!/usr/bin/env python3
"""Shared Paper2Reel download-manifest contract.

The manifest describes the files in each user-facing archive without requiring
an archive to be persisted in the Reel bundle.  Both the standalone server and
the final-package checker use this module so path validation cannot drift.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


DOWNLOAD_SCHEMA_VERSION = "paper2reel.downloads.v1"
DOWNLOAD_ALL_PACKAGE_VERSION = "paper2reel.all.v2"
DOWNLOAD_VIDEO_PACKAGE_VERSION = "paper2reel.video.v2"
DOWNLOAD_MANIFEST_PATH = Path("assets/meta/reel_downloads.json")
DOWNLOAD_DELIVERIES = {"materialized", "on_demand"}
VIDEO_README_NAME = "README.txt"
VIDEO_README_TEXT = (
    "Convert edited PPTX file into video using the PPTX2Video project. "
    "Project link: https://github.com/ai-nuts/pptx2video"
)
VIDEO_README_BYTES = (VIDEO_README_TEXT + "\n").encode("utf-8")
ARCHIVE_ORDER = ("all", "poster", "video", "blog")
ARCHIVE_META = {
    "all": {"label": "All", "filename": "all_final.zip"},
    "poster": {"label": "Poster", "filename": "poster_final.zip"},
    "video": {"label": "Video", "filename": "video_final.zip"},
    "blog": {"label": "Blog", "filename": "blog_final.zip"},
}
MODULE_FILES: dict[str, dict[str, set[str]]] = {
    "poster": {
        "files": {"poster.html", "poster.png", "poster.pdf", "poster.pptx"},
        "directories": {
            "assets/_pptx_build",
            "assets/figures",
            "assets/fonts",
            "assets/logos",
            "assets/qr",
        },
    },
    "video": {
        "files": {"video.mp4", "video.pptx", VIDEO_README_NAME},
        "directories": {"assets/captions"},
    },
    "blog": {
        "files": {"blog_en.docx", "blog_zh.docx"},
        "directories": set(),
    },
}
ALL_PACKAGE_ROOT_FILES = {
    "reel.html",
    "content_alignment.json",
    "poster.pdf",
    "poster.pptx",
    "video.mp4",
    "video.pptx",
    VIDEO_README_NAME,
    "blog_en.docx",
    "blog_zh.docx",
}
# README.txt was added after the v2 All-package contract shipped. Keep it
# optional at this layer so historical v2 manifests remain downloadable; new
# video-package manifests require and validate it separately below.
ALL_PACKAGE_REQUIRED_FILES = {
    "reel.html",
    "content_alignment.json",
    "poster.pdf",
    "poster.pptx",
    "video.mp4",
    "video.pptx",
    "blog_en.docx",
    "blog_zh.docx",
}
ALL_PACKAGE_RUNTIME_DIRECTORIES = {
    "assets/poster",
    "assets/media",
    "assets/slides",
    "assets/blog",
    "assets/ui",
    "assets/fonts",
}
ALL_PACKAGE_EXCLUDED_PARTS = {
    "_pptx_build",
    "build",
    "cache",
    "caches",
    "meta",
    "previews",
    "reports",
    "temp",
    "tmp",
}
ALL_PACKAGE_MODULE_FILES = {
    "poster": {"poster.pdf", "poster.pptx"},
    "video": {"video.mp4", "video.pptx", VIDEO_README_NAME},
    "blog": {"blog_en.docx", "blog_zh.docx"},
}
PROHIBITED_PARTS = {
    ".claude",
    ".codex",
    ".git",
    "__pycache__",
    "_debug",
    "backup",
    "backups",
    "downloads",
    "internal",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_video_readme(video_source: Path) -> Path:
    """Write the deterministic PPTX2Video handoff note into a video bundle."""
    source = Path(video_source).resolve()
    if not source.is_dir():
        raise ValueError(f"video download source is not a directory: {source}")
    destination = source / VIDEO_README_NAME
    if destination.is_symlink():
        raise ValueError(f"video README may not be a symlink: {destination}")
    if destination.exists() and not destination.is_file():
        raise ValueError(f"video README must be a regular file: {destination}")
    try:
        if destination.is_file() and destination.read_bytes() == VIDEO_README_BYTES:
            return destination
        destination.write_bytes(VIDEO_README_BYTES)
    except OSError as exc:
        raise ValueError(f"could not write video README: {destination}") from exc
    return destination


def is_backup_name(name: str) -> bool:
    lowered = name.lower()
    return (
        lowered.endswith((".bak", ".backup", ".old", ".orig", "~"))
        or ".bak." in lowered
        or ".backup." in lowered
    )


def is_safe_relative_posix(value: str) -> bool:
    """Return whether *value* is a normalized, non-internal POSIX path."""
    if (
        not value
        or value != value.strip()
        or "\\" in value
        or value.startswith("/")
        or any(ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        return False
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        return False
    if path.as_posix() != value:
        return False
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & PROHIBITED_PARTS:
        return False
    return not any(is_backup_name(part) for part in path.parts)


def is_internal_path(relative: Path) -> bool:
    value = relative.as_posix()
    return not is_safe_relative_posix(value)


def matches_module(relative: Path | PurePosixPath, module: str) -> bool:
    spec = MODULE_FILES[module]
    relative_posix = relative.as_posix()
    return (
        relative_posix in spec["files"]
        or any(
            relative_posix.startswith(f"{directory}/")
            for directory in spec["directories"]
        )
    )


def matches_all_package(relative: Path | PurePosixPath) -> bool:
    """Return whether a path belongs in the self-contained Download All ZIP."""
    relative_posix = relative.as_posix()
    if not is_safe_relative_posix(relative_posix):
        return False
    if relative.suffix.lower() == ".zip":
        return False
    lowered_parts = tuple(part.lower() for part in relative.parts)
    if any(part.startswith(".") for part in lowered_parts):
        return False
    if set(lowered_parts) & ALL_PACKAGE_EXCLUDED_PARTS:
        return False
    if len(relative.parts) == 1:
        return relative_posix in ALL_PACKAGE_ROOT_FILES
    return any(
        relative_posix.startswith(f"{directory}/")
        for directory in ALL_PACKAGE_RUNTIME_DIRECTORIES
    )


def selected_files(
    source: Path,
    *,
    module: str | None,
) -> list[tuple[Path, Path]]:
    """Return safe files below *source*, optionally restricted by module."""
    selected: list[tuple[Path, Path]] = []
    source = source.resolve()
    if not source.is_dir():
        return selected
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if is_internal_path(relative):
            continue
        if module is not None and not matches_module(relative, module):
            continue
        selected.append((path, relative))
    return selected


def selected_all_package_files(
    bundle_root: Path,
    *,
    poster_source: Path | None,
    video_source: Path | None,
    blog_source: Path | None,
) -> list[tuple[Path, Path, Path]]:
    """Select one offline Reel plus the final user-facing module outputs.

    Runtime files always come from ``bundle_root``. Final Poster, Video, and
    Blog deliverables may come from separate source directories while a
    materialized Reel is being staged. Archive names stay rooted at the Reel
    package, and collisions prefer the already-published bundle copy.
    """
    bundle_root = bundle_root.resolve()
    selected: dict[str, tuple[Path, Path, Path]] = {}

    if bundle_root.is_dir():
        for path in sorted(bundle_root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(bundle_root)
            if matches_all_package(relative):
                selected.setdefault(
                    relative.as_posix().casefold(),
                    (path, relative, bundle_root),
                )

    sources = {
        "poster": poster_source,
        "video": video_source,
        "blog": blog_source,
    }
    for module in ("poster", "video", "blog"):
        raw_source = sources[module]
        if raw_source is None:
            continue
        source = Path(raw_source).resolve()
        if not source.is_dir():
            continue
        for name in sorted(ALL_PACKAGE_MODULE_FILES[module]):
            path = source / name
            relative = Path(name)
            if path.is_file():
                selected.setdefault(
                    relative.as_posix().casefold(),
                    (path, relative, source),
                )

    return [selected[key] for key in sorted(selected)]


def _bundle_path(path: Path, source: Path, bundle_root: Path, *, strict: bool) -> str:
    try:
        return path.resolve().relative_to(bundle_root.resolve()).as_posix()
    except ValueError:
        if strict:
            raise ValueError(
                f"on-demand download source is outside the final bundle: {path}"
            )
        return path.resolve().relative_to(source.resolve()).as_posix()


def _entry(path: Path, relative: Path, source: Path, bundle_root: Path, *, strict: bool) -> dict[str, Any]:
    return {
        "path": _bundle_path(path, source, bundle_root, strict=strict),
        "arcname": relative.as_posix(),
        "size": path.stat().st_size,
    }


def build_download_manifest(
    *,
    bundle_root: Path,
    poster_source: Path | None,
    video_source: Path | None,
    blog_source: Path | None,
    delivery: str,
) -> dict[str, Any]:
    """Build a deterministic download manifest from final-deliverable sources.

    ``on_demand`` is intentionally strict: every selected source must live
    below ``bundle_root`` and every module uses the explicit deliverable
    whitelist.  ``materialized`` preserves the legacy behavior for separate
    per-module source directories, where the whole safe source directory was
    archived.
    """
    if delivery not in DOWNLOAD_DELIVERIES:
        raise ValueError(f"unsupported download delivery mode: {delivery}")

    bundle_root = bundle_root.resolve()
    raw_sources = {
        "poster": poster_source,
        "video": video_source,
        "blog": blog_source,
    }
    sources = {
        module: Path(source).resolve()
        for module, source in raw_sources.items()
        if source is not None and Path(source).is_dir()
    }
    source_counts: dict[Path, int] = {}
    for source in sources.values():
        source_counts[source] = source_counts.get(source, 0) + 1

    module_entries: dict[str, list[dict[str, Any]]] = {
        "poster": [],
        "video": [],
        "blog": [],
    }
    strict = delivery == "on_demand"
    for module in ("poster", "video", "blog"):
        source = sources.get(module)
        if source is None:
            continue
        shared_source = source_counts[source] > 1
        module_filter = module if strict or shared_source else None
        module_entries[module] = [
            _entry(path, relative, source, bundle_root, strict=strict)
            for path, relative in selected_files(source, module=module_filter)
        ]

    all_entries: dict[str, dict[str, Any]] = {}
    all_package_files = selected_all_package_files(
        bundle_root,
        poster_source=sources.get("poster"),
        video_source=sources.get("video"),
        blog_source=sources.get("blog"),
    )
    has_reel_runtime = {
        relative.as_posix()
        for _path, relative, _source in all_package_files
    }.issuperset({"reel.html", "content_alignment.json"})
    if has_reel_runtime:
        for path, relative, source in all_package_files:
            item = _entry(path, relative, source, bundle_root, strict=strict)
            all_entries.setdefault(str(item["arcname"]), item)
    elif len(set(sources.values())) <= 1:
        # A temporary viewer staging directory may be created before reel.html
        # exists. Preserve the historical union format until the final bundle
        # is published and the manifest can be rebuilt as an offline Reel.
        for module in ("poster", "video", "blog"):
            for item in module_entries[module]:
                all_entries.setdefault(str(item["arcname"]), dict(item))
    else:
        for module in ("poster", "video", "blog"):
            for item in module_entries[module]:
                combined = dict(item)
                combined["arcname"] = f"{module}/{item['arcname']}"
                all_entries.setdefault(str(combined["arcname"]), combined)

    archives: dict[str, dict[str, Any]] = {}
    entries_by_archive = {
        "all": sorted(all_entries.values(), key=lambda item: str(item["arcname"])),
        **{
            module: sorted(module_entries[module], key=lambda item: str(item["arcname"]))
            for module in ("poster", "video", "blog")
        },
    }
    for kind in ARCHIVE_ORDER:
        archives[kind] = {
            **ARCHIVE_META[kind],
            "files": entries_by_archive[kind],
        }
    payload = {
        "schema_version": DOWNLOAD_SCHEMA_VERSION,
        "delivery": delivery,
        "created_at": utc_now(),
        "archives": archives,
    }
    video_source = sources.get("video")
    if (
        video_source is not None
        and (video_source / VIDEO_README_NAME).is_file()
        and (video_source / VIDEO_README_NAME).read_bytes() == VIDEO_README_BYTES
    ):
        payload["video_package_version"] = DOWNLOAD_VIDEO_PACKAGE_VERSION
    if has_reel_runtime:
        payload["all_package_version"] = DOWNLOAD_ALL_PACKAGE_VERSION
    return payload


def write_download_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _issue(
    code: str,
    message: str,
    *,
    path: str | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "path": path,
        "data": data or {},
    }


def validate_download_manifest(
    payload: Any,
    *,
    bundle_root: Path,
    require_sources: bool | None = None,
) -> list[dict[str, Any]]:
    """Validate manifest schema, classification, path safety, and sources."""
    issues: list[dict[str, Any]] = []
    bundle_root = bundle_root.resolve()
    if not isinstance(payload, dict):
        return [_issue("DOWNLOAD_MANIFEST_SCHEMA_INVALID", "Download manifest must be a JSON object.")]
    if payload.get("schema_version") != DOWNLOAD_SCHEMA_VERSION:
        issues.append(
            _issue(
                "DOWNLOAD_MANIFEST_SCHEMA_INVALID",
                f"schema_version must be {DOWNLOAD_SCHEMA_VERSION}.",
                data={"actual": payload.get("schema_version")},
            )
        )
    all_package_version = payload.get("all_package_version")
    if all_package_version not in {None, DOWNLOAD_ALL_PACKAGE_VERSION}:
        issues.append(
            _issue(
                "DOWNLOAD_ALL_PACKAGE_VERSION_INVALID",
                f"all_package_version must be {DOWNLOAD_ALL_PACKAGE_VERSION} when present.",
                path="all_package_version",
                data={"actual": all_package_version},
            )
        )
    video_package_version = payload.get("video_package_version")
    if video_package_version not in {None, DOWNLOAD_VIDEO_PACKAGE_VERSION}:
        issues.append(
            _issue(
                "DOWNLOAD_VIDEO_PACKAGE_VERSION_INVALID",
                f"video_package_version must be {DOWNLOAD_VIDEO_PACKAGE_VERSION} when present.",
                path="video_package_version",
                data={"actual": video_package_version},
            )
        )
    delivery = payload.get("delivery")
    if delivery not in DOWNLOAD_DELIVERIES:
        issues.append(
            _issue(
                "DOWNLOAD_DELIVERY_INVALID",
                "Download manifest delivery must be materialized or on_demand.",
                data={"actual": delivery},
            )
        )
    if require_sources is None:
        require_sources = delivery == "on_demand"

    archives = payload.get("archives")
    if not isinstance(archives, dict):
        issues.append(_issue("DOWNLOAD_ARCHIVES_SCHEMA_INVALID", "archives must be an object."))
        return issues
    actual_kinds = set(archives)
    expected_kinds = set(ARCHIVE_ORDER)
    if actual_kinds != expected_kinds:
        issues.append(
            _issue(
                "DOWNLOAD_ARCHIVE_SET_INVALID",
                "archives must contain exactly all, poster, video, and blog.",
                data={"actual": sorted(actual_kinds), "expected": list(ARCHIVE_ORDER)},
            )
        )

    normalized: dict[str, list[tuple[str, str, int]]] = {}
    for kind in ARCHIVE_ORDER:
        archive = archives.get(kind)
        if not isinstance(archive, dict):
            issues.append(
                _issue(
                    "DOWNLOAD_ARCHIVE_SCHEMA_INVALID",
                    "Archive entry must be an object.",
                    path=f"archives.{kind}",
                )
            )
            continue
        expected = ARCHIVE_META[kind]
        for field in ("label", "filename"):
            if archive.get(field) != expected[field]:
                issues.append(
                    _issue(
                        "DOWNLOAD_ARCHIVE_METADATA_INVALID",
                        f"Archive {kind} has an invalid {field}.",
                        path=f"archives.{kind}.{field}",
                        data={"actual": archive.get(field), "expected": expected[field]},
                    )
                )
        files = archive.get("files")
        if not isinstance(files, list):
            issues.append(
                _issue(
                    "DOWNLOAD_FILES_SCHEMA_INVALID",
                    "Archive files must be a list.",
                    path=f"archives.{kind}.files",
                )
            )
            continue
        if delivery == "on_demand" and not files:
            issues.append(
                _issue(
                    "DOWNLOAD_ARCHIVE_EMPTY",
                    "Every on-demand archive must contain at least one whitelisted source file.",
                    path=f"archives.{kind}.files",
                )
            )
        seen_paths: set[str] = set()
        seen_arcnames: set[str] = set()
        valid_entries: list[tuple[str, str, int]] = []
        for index, item in enumerate(files):
            item_path = f"archives.{kind}.files[{index}]"
            if not isinstance(item, dict):
                issues.append(
                    _issue("DOWNLOAD_FILE_SCHEMA_INVALID", "Download file entry must be an object.", path=item_path)
                )
                continue
            source_path = item.get("path")
            arcname = item.get("arcname")
            size = item.get("size")
            if not isinstance(source_path, str) or not is_safe_relative_posix(source_path):
                issues.append(
                    _issue(
                        "DOWNLOAD_SOURCE_PATH_UNSAFE",
                        "Download source path must be a safe bundle-relative POSIX path.",
                        path=f"{item_path}.path",
                        data={"value": source_path},
                    )
                )
                continue
            if not isinstance(arcname, str) or not is_safe_relative_posix(arcname):
                issues.append(
                    _issue(
                        "DOWNLOAD_ARCHIVE_PATH_UNSAFE",
                        "Download archive name must be a safe relative POSIX path.",
                        path=f"{item_path}.arcname",
                        data={"value": arcname},
                    )
                )
                continue
            if isinstance(size, bool) or not isinstance(size, int) or size < 0:
                issues.append(
                    _issue(
                        "DOWNLOAD_SOURCE_SIZE_INVALID",
                        "Download source size must be a non-negative integer.",
                        path=f"{item_path}.size",
                        data={"value": size},
                    )
                )
                continue
            arcname_key = arcname.casefold()
            duplicate_source = (
                delivery == "on_demand"
                and source_path in seen_paths
            )
            if duplicate_source or arcname_key in seen_arcnames:
                issues.append(
                    _issue(
                        "DOWNLOAD_FILE_DUPLICATE",
                        "Archive files must not repeat a source path or archive name.",
                        path=item_path,
                        data={"path": source_path, "arcname": arcname},
                    )
                )
                continue
            seen_paths.add(source_path)
            seen_arcnames.add(arcname_key)

            if delivery == "on_demand" and kind in MODULE_FILES:
                if not matches_module(PurePosixPath(source_path), kind) or not matches_module(
                    PurePosixPath(arcname), kind
                ):
                    issues.append(
                        _issue(
                            "DOWNLOAD_FILE_CLASSIFICATION_INVALID",
                            "On-demand module archives may contain only their whitelisted final deliverables.",
                            path=item_path,
                            data={"archive": kind, "path": source_path, "arcname": arcname},
                        )
                    )
            if kind == "all" and all_package_version == DOWNLOAD_ALL_PACKAGE_VERSION:
                if not matches_all_package(PurePosixPath(source_path)) or not matches_all_package(
                    PurePosixPath(arcname)
                ):
                    issues.append(
                        _issue(
                            "DOWNLOAD_ALL_FILE_CLASSIFICATION_INVALID",
                            "Download All may contain only the offline Reel runtime and final module deliverables.",
                            path=item_path,
                            data={"path": source_path, "arcname": arcname},
                        )
                    )

            if require_sources:
                candidate = bundle_root / source_path
                try:
                    resolved = candidate.resolve()
                    resolved.relative_to(bundle_root)
                except (OSError, ValueError):
                    issues.append(
                        _issue(
                            "DOWNLOAD_SOURCE_PATH_ESCAPE",
                            "Download source resolves outside the Reel bundle.",
                            path=source_path,
                        )
                    )
                else:
                    if not resolved.is_file():
                        issues.append(
                            _issue(
                                "DOWNLOAD_SOURCE_MISSING",
                                "Download source listed in the manifest is missing.",
                                path=source_path,
                                data={"archive": kind},
                            )
                        )
                    elif resolved.stat().st_size != size:
                        issues.append(
                            _issue(
                                "DOWNLOAD_SOURCE_SIZE_MISMATCH",
                                "Download source size no longer matches the manifest.",
                                path=source_path,
                                data={
                                    "archive": kind,
                                    "actual": resolved.stat().st_size,
                                    "expected": size,
                                },
                            )
                        )
            valid_entries.append((source_path, arcname, size))
        normalized[kind] = valid_entries

    if all(kind in normalized for kind in ARCHIVE_ORDER):
        actual_all = {
            entry[1].casefold(): entry
            for entry in normalized["all"]
        }
        if all_package_version is None:
            if delivery == "on_demand":
                expected_all: dict[str, tuple[str, str, int]] = {}
                for kind in ("poster", "video", "blog"):
                    for entry in normalized[kind]:
                        expected_all.setdefault(entry[1].casefold(), entry)
                if actual_all != expected_all:
                    issues.append(
                        _issue(
                            "DOWNLOAD_ALL_UNION_INVALID",
                            "A historical All archive must be the deduplicated union of Poster, Video, and Blog.",
                            path="archives.all.files",
                        )
                    )
        elif all_package_version == DOWNLOAD_ALL_PACKAGE_VERSION:
            missing = sorted(
                name
                for name in ALL_PACKAGE_REQUIRED_FILES
                if name.casefold() not in actual_all
            )
            if missing:
                issues.append(
                    _issue(
                        "DOWNLOAD_ALL_REQUIRED_FILE_MISSING",
                        "The self-contained Download All package is missing required Reel or module deliverables.",
                        path="archives.all.files",
                        data={"files": missing},
                    )
                )
            if require_sources:
                expected_all: dict[str, tuple[str, str, int]] = {}
                for path, relative, source in selected_all_package_files(
                    bundle_root,
                    poster_source=bundle_root,
                    video_source=bundle_root,
                    blog_source=bundle_root,
                ):
                    item = _entry(
                        path,
                        relative,
                        source,
                        bundle_root,
                        strict=True,
                    )
                    entry = (
                        str(item["path"]),
                        str(item["arcname"]),
                        int(item["size"]),
                    )
                    expected_all.setdefault(entry[1].casefold(), entry)
                if actual_all != expected_all:
                    issues.append(
                        _issue(
                            "DOWNLOAD_ALL_PACKAGE_INVALID",
                            "Download All must exactly match the self-contained Reel package selected from the final bundle.",
                            path="archives.all.files",
                        )
                    )
        if video_package_version == DOWNLOAD_VIDEO_PACKAGE_VERSION:
            expected_readme = (
                VIDEO_README_NAME,
                VIDEO_README_NAME,
                len(VIDEO_README_BYTES),
            )
            if expected_readme not in normalized["video"]:
                issues.append(
                    _issue(
                        "DOWNLOAD_VIDEO_README_MISSING",
                        "The Video archive must contain the canonical root README.txt.",
                        path="archives.video.files",
                    )
                )
            if (
                all_package_version == DOWNLOAD_ALL_PACKAGE_VERSION
                and expected_readme not in normalized["all"]
            ):
                issues.append(
                    _issue(
                        "DOWNLOAD_ALL_VIDEO_README_MISSING",
                        "Download All must contain the canonical root README.txt for the Video source.",
                        path="archives.all.files",
                    )
                )
            if require_sources:
                readme_path = bundle_root / VIDEO_README_NAME
                try:
                    readme_bytes = readme_path.read_bytes()
                except OSError:
                    readme_bytes = None
                if readme_bytes is not None and readme_bytes != VIDEO_README_BYTES:
                    issues.append(
                        _issue(
                            "DOWNLOAD_VIDEO_README_CONTENT_INVALID",
                            "README.txt must contain the canonical PPTX2Video handoff text.",
                            path=VIDEO_README_NAME,
                        )
                    )
    return issues


def materialize_download_archives(
    payload: dict[str, Any],
    *,
    bundle_root: Path,
    downloads_dir: Path | None = None,
    kinds: Iterable[str] = ARCHIVE_ORDER,
    clear_destination: bool = True,
) -> dict[str, Path]:
    """Write selected manifest archives for standalone/materialized delivery."""
    bundle_root = bundle_root.resolve()
    if payload.get("delivery") != "materialized":
        raise ValueError("materialized archives require delivery=materialized")
    issues = validate_download_manifest(
        payload,
        bundle_root=bundle_root,
        require_sources=True,
    )
    if issues:
        first = issues[0]
        raise ValueError(f"{first['code']}: {first['message']}")

    selected_kinds = tuple(kinds)
    unknown_kinds = sorted(set(selected_kinds) - set(ARCHIVE_ORDER))
    if unknown_kinds:
        raise ValueError(f"unknown download archives: {', '.join(unknown_kinds)}")

    destination = (
        Path(downloads_dir).resolve()
        if downloads_dir is not None
        else bundle_root / "assets" / "downloads"
    )
    if clear_destination and destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)

    written: dict[str, Path] = {}
    for kind in selected_kinds:
        archive_spec = payload["archives"][kind]
        archive_path = destination / str(archive_spec["filename"])
        with zipfile.ZipFile(
            archive_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as archive:
            for item in archive_spec["files"]:
                archive.write(
                    bundle_root / str(item["path"]),
                    str(item["arcname"]),
                )
        written[kind] = archive_path
    return written


def read_download_manifest(bundle_root: Path) -> dict[str, Any]:
    manifest_path = bundle_root.resolve() / DOWNLOAD_MANIFEST_PATH
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"download manifest missing: {manifest_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"download manifest is invalid JSON: {exc}") from exc
    issues = validate_download_manifest(payload, bundle_root=bundle_root)
    if issues:
        first = issues[0]
        raise ValueError(f"{first['code']}: {first['message']}")
    return payload


def archive_files(
    payload: dict[str, Any],
    kind: str,
    *,
    bundle_root: Path,
) -> tuple[str, list[tuple[Path, str]]]:
    """Resolve one validated on-demand archive to concrete source paths."""
    if kind not in ARCHIVE_ORDER:
        raise ValueError(f"unknown download archive: {kind}")
    if payload.get("delivery") != "on_demand":
        raise ValueError("dynamic downloads require delivery=on_demand")
    issues = validate_download_manifest(payload, bundle_root=bundle_root, require_sources=True)
    if issues:
        first = issues[0]
        raise ValueError(f"{first['code']}: {first['message']}")
    archive = payload["archives"][kind]
    files = [
        (bundle_root.resolve() / item["path"], item["arcname"])
        for item in archive["files"]
    ]
    return str(archive["filename"]), files


def archive_links(delivery: str) -> list[dict[str, str]]:
    """Return fixed-order viewer links for one delivery mode."""
    if delivery not in DOWNLOAD_DELIVERIES:
        raise ValueError(f"unsupported download delivery mode: {delivery}")
    return [
        {
            "label": ARCHIVE_META[kind]["label"],
            "href": (
                f"assets/downloads/{ARCHIVE_META[kind]['filename']}"
                if delivery == "materialized"
                else f"__download__/{kind}"
            ),
        }
        for kind in ARCHIVE_ORDER
    ]
