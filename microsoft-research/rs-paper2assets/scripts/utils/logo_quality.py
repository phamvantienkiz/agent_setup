#!/usr/bin/env python3
"""Deterministic visual quality checks for downloaded institution logos.

The fetcher receives both curated Wikimedia files and arbitrary URLs selected by
the web-search fallback.  A valid image response is not enough: the URL can be a
campus photo, a publication cover, a social-card image, or a white-only mark that
disappears on the poster's light header.  This module rasterizes each candidate,
measures its visible shape, and rejects those failure modes before the file enters
``assets/logos/`` or ``logos.json``.

The classifier intentionally uses conservative image geometry rather than a
network model.  It is deterministic, offline, auditable, and cheap enough to run
again in tests and downstream defensive checks.
"""
from __future__ import annotations

import io
from dataclasses import asdict, dataclass


BAD_RESOURCE_HINTS = (
    "aerial", "background", "brochure", "building", "campus", "cover",
    "hero-image", "og-image", "photo", "photograph", "social-card",
)


@dataclass(frozen=True)
class LogoInspection:
    accepted: bool
    reason: str
    width: int = 0
    height: int = 0
    has_transparency: bool = False
    foreground_fraction: float = 0.0
    contrast_mean: float = 0.0
    unique_colors: int = 0
    color_entropy: float = 0.0
    edge_density: float = 0.0
    palette_concentration: float = 0.0
    flat_fraction: float = 0.0
    fingerprint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _looks_svg(data: bytes) -> bool:
    head = data[:512].lstrip().lower()
    return head.startswith(b"<svg") or head.startswith(b"<?xml")


def _load_rgba(data: bytes):
    """Return a bounded RGBA Pillow image, rasterizing SVG when necessary."""
    from PIL import Image

    payload = data
    if _looks_svg(data):
        import cairosvg

        payload = cairosvg.svg2png(bytestring=data, output_width=640)
    image = Image.open(io.BytesIO(payload))
    try:
        image.seek(0)
    except Exception:
        pass
    image = image.convert("RGBA")
    image.thumbnail((640, 640), Image.Resampling.LANCZOS)
    return image


def _entropy(values, bins: int = 32) -> float:
    import numpy as np

    hist, _ = np.histogram(values, bins=bins, range=(0, 256))
    hist = hist[hist > 0].astype(float)
    if not len(hist):
        return 0.0
    probs = hist / hist.sum()
    return float(-(probs * np.log2(probs)).sum())


def _reject(reason: str, **metrics) -> LogoInspection:
    return LogoInspection(False, reason, **metrics)


def inspect_logo_bytes(data: bytes, source: str = "") -> LogoInspection:
    """Classify one candidate image for use on a light academic-poster header.

    Accepted candidates must have a real visible mark, enough contrast on white,
    and logo-like visual complexity.  Transparent pixels define the foreground
    for alpha images, so a white mark is measured correctly instead of being
    mistaken for crop background.  It is then rejected explicitly as invisible
    on the light header rather than silently turning into a giant white tile.
    """
    try:
        import numpy as np

        image = _load_rgba(data)
        arr = np.asarray(image, dtype=np.uint8)
    except Exception as exc:
        return _reject(f"decode_failed:{type(exc).__name__}")

    height, width = arr.shape[:2]
    base = {"width": width, "height": height}
    if width < 12 or height < 12:
        return _reject("too_small", **base)
    aspect = width / float(height)
    if aspect > 16.0 or aspect < (1.0 / 16.0):
        return _reject("extreme_aspect_ratio", **base)

    rgb = arr[..., :3].astype(np.float32)
    alpha = arr[..., 3].astype(np.float32)
    has_transparency = bool((alpha < 250).mean() >= 0.005)

    if has_transparency:
        # Alpha is authoritative.  In particular, opaque WHITE pixels can be
        # intentional artwork and must survive bbox calculation.
        foreground = alpha > 16
    else:
        border = np.concatenate((
            rgb[:2].reshape(-1, 3), rgb[-2:].reshape(-1, 3),
            rgb[:, :2].reshape(-1, 3), rgb[:, -2:].reshape(-1, 3),
        ))
        background = np.median(border, axis=0)
        foreground = np.linalg.norm(rgb - background, axis=2) > 18.0
        if not foreground.any():
            foreground = rgb.min(axis=2) < 245

    if not foreground.any() or int(foreground.sum()) < 32:
        return _reject(
            "blank_or_empty", has_transparency=has_transparency, **base,
        )

    ys, xs = foreground.nonzero()
    left, right = int(xs.min()), int(xs.max()) + 1
    top, bottom = int(ys.min()), int(ys.max()) + 1
    if right - left < 6 or bottom - top < 6:
        return _reject(
            "negligible_visible_shape", has_transparency=has_transparency, **base,
        )

    tight_rgb = rgb[top:bottom, left:right]
    tight_alpha = alpha[top:bottom, left:right] / 255.0
    tight_fg = foreground[top:bottom, left:right]
    composite = tight_rgb * tight_alpha[..., None] + 255.0 * (1.0 - tight_alpha[..., None])
    luminance = (
        composite[..., 0] * 0.2126 + composite[..., 1] * 0.7152
        + composite[..., 2] * 0.0722
    )
    saturation = composite.max(axis=2) - composite.min(axis=2)
    visible_contrast = (255.0 - luminance) + 0.30 * saturation
    contrast_mean = float(visible_contrast[tight_fg].mean())
    foreground_fraction = float(tight_fg.mean())

    # A white-only transparent wordmark is technically non-empty but is
    # invisible on the light header.  Reject it and let the fetcher try the next
    # official candidate or report the institute as missing.
    if contrast_mean < 12.0 and float(np.percentile(
        visible_contrast[tight_fg], 90
    )) < 24.0:
        return _reject(
            "low_contrast_on_light_header",
            has_transparency=has_transparency,
            foreground_fraction=foreground_fraction,
            contrast_mean=round(contrast_mean, 3),
            **base,
        )

    # Normalize to a small white-composited raster for complexity metrics and
    # a stable visual fingerprint across source resolutions.
    from PIL import Image

    normalized = Image.fromarray(
        np.clip(composite, 0, 255).astype(np.uint8), "RGB"
    ).resize((96, 96), Image.Resampling.LANCZOS)
    norm = np.asarray(normalized, dtype=np.uint8)
    quantized = (norm // 16).reshape(-1, 3)
    _, color_counts = np.unique(quantized, axis=0, return_counts=True)
    unique_colors = int(len(color_counts))
    palette_concentration = float(
        np.sort(color_counts)[-8:].sum() / len(quantized)
    )
    gray = (
        norm[..., 0].astype(float) * 0.2126
        + norm[..., 1].astype(float) * 0.7152
        + norm[..., 2].astype(float) * 0.0722
    )
    color_entropy = _entropy(gray)
    gx = np.abs(np.diff(gray, axis=1))
    gy = np.abs(np.diff(gray, axis=0))
    edge_density = float(
        ((gx[:-1, :] + gy[:, :-1]) > 28.0).mean()
    ) if gray.shape[0] > 2 and gray.shape[1] > 2 else 0.0
    rgb_gx = np.max(np.abs(np.diff(norm.astype(float), axis=1)), axis=2)
    rgb_gy = np.max(np.abs(np.diff(norm.astype(float), axis=0)), axis=2)
    flat_fraction = float(
        ((rgb_gx < 4.0).mean() + (rgb_gy < 4.0).mean()) / 2.0
    )

    source_low = urllib_unquote(source).lower()
    bad_hint = any(token in source_low for token in BAD_RESOURCE_HINTS)
    tight_aspect = (right - left) / float(bottom - top)
    # Opaque JPEG crests are a difficult but legitimate logo class. Their
    # antialiased linework creates hundreds of colors and high edge entropy,
    # which superficially resembles a photograph. Unlike a campus photo, a
    # crest is non-rectangular inside its tight bbox and is built from a small
    # set of large, locally flat color regions. Preserve that explainable shape
    # before applying the broad photo/cover rejection below.
    graphic_crest_like = (
        not has_transparency
        and 0.55 <= foreground_fraction <= 0.88
        and edge_density > 0.30
        and palette_concentration > 0.38
        and flat_fraction > 0.28
    )
    photo_like = (
        not has_transparency
        and not graphic_crest_like
        and foreground_fraction > 0.75
        and unique_colors > 80
        and (color_entropy > 3.30 or edge_density > 0.30)
    )
    cover_like = (
        not has_transparency
        and not graphic_crest_like
        and (
            (
                tight_aspect < 0.84
                and foreground_fraction > 0.48
                and unique_colors > 180
                and (color_entropy > 4.0 or edge_density > 0.15)
            )
            or (
                # Portrait brand cards and social covers can be mostly pale
                # background around a centered mark, so their foreground
                # fraction is much lower than a photograph.  Their opaque,
                # high-colour, page-like canvas still distinguishes them from
                # transparent seals and crests.
                aspect < 0.90
                and foreground_fraction > 0.20
                and unique_colors > 80
                and color_entropy > 2.10
                and edge_density < 0.20
            )
        )
    )
    metrics = {
        **base,
        "has_transparency": has_transparency,
        "foreground_fraction": round(foreground_fraction, 5),
        "contrast_mean": round(contrast_mean, 3),
        "unique_colors": unique_colors,
        "color_entropy": round(color_entropy, 4),
        "edge_density": round(edge_density, 5),
        "palette_concentration": round(palette_concentration, 5),
        "flat_fraction": round(flat_fraction, 5),
    }
    if photo_like:
        return _reject("photographic_image", **metrics)
    if cover_like:
        return _reject("cover_or_page_image", **metrics)
    if bad_hint and (unique_colors > 140 or foreground_fraction > 0.72):
        return _reject("resource_url_suggests_non_logo", **metrics)

    # 256-bit difference hash.  Unlike a byte hash, this remains stable across
    # PNG/JPEG encoding, source resolution, and small antialiasing changes, so
    # visually identical marks fetched from different URLs can be collapsed.
    fingerprint_image = Image.fromarray(norm, "RGB").convert("L").resize(
        (17, 16), Image.Resampling.BILINEAR
    )
    fp_arr = np.asarray(fingerprint_image, dtype=np.int16)
    bits = (fp_arr[:, 1:] >= fp_arr[:, :-1]).reshape(-1)
    fingerprint = "".join(
        f"{sum(int(bit) << (3 - offset) for offset, bit in enumerate(bits[i:i + 4])):x}"
        for i in range(0, len(bits), 4)
    )
    return LogoInspection(True, "accepted", fingerprint=fingerprint, **metrics)


def fingerprint_distance(left: str, right: str) -> int | None:
    """Return perceptual-hash Hamming distance, or ``None`` if incomparable."""
    if not left or not right or len(left) != len(right):
        return None
    try:
        return (int(left, 16) ^ int(right, 16)).bit_count()
    except (TypeError, ValueError):
        return None


def fingerprints_match(left: str, right: str, max_distance: int = 16) -> bool:
    """Whether two 256-bit visual fingerprints represent the same mark."""
    distance = fingerprint_distance(left, right)
    return distance is not None and distance <= max_distance


def inspect_logo_path(path, source: str = "") -> LogoInspection:
    try:
        with open(path, "rb") as handle:
            return inspect_logo_bytes(handle.read(), source=source or str(path))
    except Exception as exc:
        return _reject(f"read_failed:{type(exc).__name__}")


def urllib_unquote(value: str) -> str:
    """Decode URL hints without importing a large parser in the hot path."""
    try:
        from urllib.parse import unquote

        return unquote(value or "")
    except Exception:
        return value or ""
