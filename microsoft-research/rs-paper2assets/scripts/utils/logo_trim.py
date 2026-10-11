#!/usr/bin/env python3
"""logo_trim — best-effort logo autotrim for the poster header chips.

After a logo is downloaded, this rasterizes any vector source (SVG -> PNG via
cairosvg, falling back to chromium/playwright) and crops the transparent /
near-white border so the logo chip hugs the mark tightly instead of floating in a
sea of padding. EVERY failure is swallowed and the ORIGINAL file is kept — all
optional deps (Pillow, cairosvg, playwright) degrade to a no-op if absent.

Public API:
    autotrim(path) -> Path
        Returns the path to the tight version. For a raster (PNG/JPG/GIF) it
        crops IN PLACE and returns the same path. For an SVG it writes a tight
        <stem>.png beside it and returns THAT path (callers should record it);
        if rasterization isn't possible it returns the original SVG path
        unchanged.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

# A pixel counts as background if it is (near-)transparent OR opaque near-white.
_NEAR_WHITE = 245   # all RGB channels >= this == white-ish
_ALPHA_MIN = 16     # alpha <= this == transparent
_PAD = 2            # keep a 2px breathing margin around the cropped mark
_RASTER_W = 600     # SVG rasterization width (height auto from aspect)


def _content_bbox(im):
    """(l, t, r, b) of the non-background region, or None. numpy fast path with a
    Pillow-only fallback."""
    try:
        import numpy as np
        arr = np.asarray(im)  # H x W x 4 (RGBA)
        if arr.ndim != 3 or arr.shape[2] < 4:
            return None
        rgb, alpha = arr[..., :3], arr[..., 3]
        # When the source has meaningful transparency, alpha defines artwork.
        # Intersecting alpha with "non-white" erased white wordmarks and made
        # their bbox look empty. Fully opaque rasters still use near-white as
        # the removable canvas background.
        has_transparency = bool((alpha < 250).mean() >= 0.005)
        content = (
            alpha > _ALPHA_MIN
            if has_transparency
            else rgb.min(axis=2) < _NEAR_WHITE
        )
        if not content.any():
            return None
        ys, xs = content.nonzero()
        return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    except Exception:
        pass
    # Pillow-only fallback: intersect the opaque bbox with the non-white bbox.
    try:
        from PIL import Image, ImageChops
        alpha = im.split()[3]
        alpha_bbox = alpha.getbbox()
        alpha_min, _ = alpha.getextrema()
        rgb = im.convert("RGB")
        diff = ImageChops.difference(rgb, Image.new("RGB", im.size, (255, 255, 255)))
        nonwhite = diff.convert("L").point(lambda p: 255 if p > (255 - _NEAR_WHITE) else 0)
        white_bbox = nonwhite.getbbox()
        if alpha_min < 250:
            return alpha_bbox
        return white_bbox
    except Exception:
        return None


def _trim_png_in_place(path: Path) -> bool:
    """Crop the transparent/near-white border of a raster IN PLACE. True if cropped."""
    try:
        from PIL import Image
    except Exception:
        return False
    try:
        im = Image.open(path).convert("RGBA")
    except Exception:
        return False
    w, h = im.size
    bbox = _content_bbox(im)
    if not bbox:
        return False
    l, t, r, b = bbox
    l = max(0, l - _PAD); t = max(0, t - _PAD)
    r = min(w, r + _PAD); b = min(h, b + _PAD)
    if (l, t, r, b) == (0, 0, w, h):
        return False  # already tight
    # Never save back through the same path that Pillow opened.  Apart from
    # making a partially-written file observable, RGBA -> JPEG raises only
    # after Pillow has opened and truncated the destination.  Write beside the
    # source and atomically replace it after a complete, non-empty encode.
    source_mode = path.stat().st_mode & 0o7777
    temporary: Path | None = None
    try:
        cropped = im.crop((l, t, r, b))
        suffix = path.suffix.lower()
        image_format = {
            ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
            ".gif": "GIF", ".webp": "WEBP", ".bmp": "BMP",
        }.get(suffix)
        if image_format == "JPEG":
            cropped = cropped.convert("RGB")
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.stem}-trim-",
            suffix=path.suffix, delete=False,
        ) as handle:
            temporary = Path(handle.name)
        cropped.save(temporary, format=image_format)
        if temporary.stat().st_size <= 0:
            return False
        temporary.chmod(source_mode)
        temporary.replace(path)
        temporary = None
        return True
    except Exception:
        return False
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _rasterize_svg(svg: Path, png: Path) -> bool:
    """SVG -> PNG. cairosvg first (fast), then chromium/playwright. True on success."""
    try:
        import cairosvg
        cairosvg.svg2png(url=str(svg), write_to=str(png), output_width=_RASTER_W)
        return png.exists() and png.stat().st_size > 0
    except Exception:
        pass
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(device_scale_factor=2)
                page.goto(svg.resolve().as_uri())
                el = page.query_selector("svg") or page.query_selector("img")
                (el or page).screenshot(path=str(png), omit_background=True)
            finally:
                browser.close()
        return png.exists() and png.stat().st_size > 0
    except Exception:
        return False


def autotrim(path) -> Path:
    """Rasterize (if SVG) + trim the transparent/near-white border. Best-effort:
    on any failure the ORIGINAL path is returned unchanged."""
    try:
        path = Path(path)
        if not path.exists():
            return path
        if path.suffix.lower() in (".svg", ".svgz"):
            png = path.with_suffix(".png")
            if _rasterize_svg(path, png):
                _trim_png_in_place(png)
                return png            # caller should record the tight PNG
            return path               # couldn't rasterize -> keep the SVG
        _trim_png_in_place(path)
        return path
    except Exception:
        return Path(path)


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        out = autotrim(arg)
        print(f"{arg} -> {out}")
