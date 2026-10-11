#!/usr/bin/env python3
"""Fetch institute logos from Wikimedia Commons for the poster titlebar.

Given a list of institute names (one per line, or `;`-separated on a single
line — same shape as the `**Institutes:**` line in `paper_spec.md`), this
script tries to download an official-looking logo for each into
`<outdir>/assets/logos/<slug>.png` and prints the mapping used.

Sourcing strategy (best-effort, never fabricates):

  1. Open the institute's English Wikipedia page (`en.wikipedia.org/wiki/<Name>`,
     with spaces → underscores) and read its Wikidata entity id.
  2. Prefer the entity's `logo image` (P154) on Wikidata, except when it is an
     explicitly localized text mark and the English infobox has a logo.
  3. Scrape the infobox `<img>` as that fallback: pick the filename matching
     `logo`/`wordmark`/`seal`/`crest`, scored so the wordmark/logo beats the
     seal and Commons beats non-free en.wikipedia uploads. Skip flags/photos/maps.
  4. Resolve to a full-resolution image URL, download to
     `<outdir>/assets/logos/<slug>.png`, decode it, and reject photos, covers,
     blank/low-contrast marks, corrupt responses, and duplicate visuals before
     keeping it. If anything fails for one institute, skip it (the
     `.logo-block:has(no logos)` CSS rule hides the slot gracefully).

Usage:
    python fetch_logos.py --outdir <outdir> --names "Microsoft Research Asia;UCSD;Tsinghua University"
    # or
    python fetch_logos.py --outdir <outdir> --from-spec <outdir>/paper_spec.md
    # WEB-SEARCH FALLBACK for an institute this Wikimedia pass missed:
    python fetch_logos.py --outdir <outdir> --add-logo "Westlake University=https://.../westlake-logo.png"

Prints a JSON summary on stdout AND a ✓/✗ CHECKLIST on stderr. The JSON carries
the resolved logos plus the institutes that produced NONE — run the Step-6 web
search on each of those, then `--add-logo "Name=URL"` to fetch it:
    {"logos":   [{"name": "...", "slug": "...", "path": "assets/logos/<slug>.png", "source": "<url>"}, ...],
     "missing": ["Westlake University", ...]}    # institutes with no Wikimedia logo -> web-search fallback
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

# Share the canonical bundle layout (utils/layout.py) when run directly.
_THIS_DIR = str(Path(__file__).resolve().parent)
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)
from utils import layout  # noqa: E402
from utils.logo_quality import (  # noqa: E402
    fingerprints_match,
    inspect_logo_bytes,
    inspect_logo_path,
)
try:
    from utils.logo_trim import autotrim  # noqa: E402
except Exception:  # best-effort: a missing trim util / dep degrades to a no-op
    def autotrim(p):
        return p

UA = "Mozilla/5.0 (paper2poster fetch_logos)"
LOGO_KEYWORDS = ("logo", "seal", "wordmark", "crest", "coat_of_arms", "emblem")
# Scored preference for the infobox fallback: the modern wordmark/logo beats the
# legacy seal/crest/coat-of-arms. Many university infoboxes carry BOTH, and
# viewers now expect the wordmark (e.g. MIT's 3 red letters, not the round seal).
# Seals stay eligible (still positive) as a last resort for institutions that
# publish only a seal. The Wikidata P154 lookup runs first and usually wins.
LOGO_WEIGHTS = {"wordmark": 30, "logo": 20, "emblem": 6,
                "seal": 4, "crest": 4, "coat_of_arms": 4}
SKIP_KEYWORDS = ("flag", "map", "campus", "photo", "building", "aerial")

# Some common institute aliases → the Wikipedia article title that actually
# carries an official mark in its infobox. Keeps the lookup robust against
# short forms (UCSD, MIT CSAIL, MSRA, etc.) that don't resolve directly.
ALIASES = {
    # Microsoft Research / MSRA map to the PARENT company Microsoft so the
    # titlebar shows Microsoft's four-square corporate logo (team convention),
    # NOT Microsoft Research's own wordmark. Mirrors google research -> Google.
    "msr": "Microsoft",
    "msra": "Microsoft",
    "microsoft research": "Microsoft",
    "microsoft research asia": "Microsoft",
    "microsoft research lab": "Microsoft",
    "microsoft research lab asia": "Microsoft",
    "ucsd": "University of California, San Diego",
    "uc san diego": "University of California, San Diego",
    "uc berkeley": "University of California, Berkeley",
    "ucb": "University of California, Berkeley",
    "ucla": "University of California, Los Angeles",
    "mit": "Massachusetts Institute of Technology",
    "cmu": "Carnegie Mellon University",
    "nyu": "New York University",
    "ust": "Hong Kong University of Science and Technology",
    "hkust": "Hong Kong University of Science and Technology",
    "cuhk": "Chinese University of Hong Kong",
    "pku": "Peking University",
    "thu": "Tsinghua University",
    "sjtu": "Shanghai Jiao Tong University",
    "ethz": "ETH Zurich",
    "eth zurich": "ETH Zurich",
    "epfl": "EPFL",
    "kaist": "KAIST",
    "nvidia": "Nvidia",
    "google research": "Google",
    "google deepmind": "Google DeepMind",
    "deepmind": "Google DeepMind",
    "facebook ai research": "Meta Platforms",
    "facebook ai": "Meta Platforms",
    "facebook": "Meta Platforms",
    "fair": "Meta Platforms",
    "meta ai": "Meta Platforms",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
    "ibm research": "IBM",
}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    return s or "logo"


_LEGAL_SUFFIX_RE = re.compile(
    r"\b(?:corporation|corp\.?|incorporated|inc\.?|llc|ltd\.?|limited|gmbh)\b",
    re.IGNORECASE,
)


def canonical_institution_key(name: str, resolved_title: str | None = None) -> str:
    """Stable identity key shared by deterministic and web-fallback fetches.

    Prefer the Wikipedia title that actually resolved.  Without one, walk the
    same parent/alias candidates as ``fetch_logo_for`` so spelling variants,
    departments, and aliases such as MSRA converge on the parent institution.
    Legal company suffixes are presentation details and do not create a second
    institution identity.
    """
    if resolved_title:
        canonical = resolve_wikipedia_title(resolved_title)
    else:
        candidates = parent_candidates(name) if "parent_candidates" in globals() else [name]
        canonical = ""
        for candidate in candidates:
            alias = ALIASES.get(candidate.strip().lower())
            if alias:
                canonical = alias
                break
        canonical = canonical or resolve_wikipedia_title(name)
    canonical = _LEGAL_SUFFIX_RE.sub(" ", canonical)
    canonical = re.sub(r"\s+", " ", canonical).strip(" ,.-")
    return slugify(canonical)


def fetch(url: str, timeout: float = 15.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def resolve_wikipedia_title(name: str) -> str:
    key = name.strip().lower()
    return ALIASES.get(key, name.strip())


def search_wikipedia_titles(query: str, limit: int = 3) -> list[str]:
    """Resolve an institution name to its best-matching English-Wikipedia
    article title(s) via the opensearch API. This is what makes the lookup
    robust WITHOUT a hand-maintained alias table: it handles abbreviations,
    rebrands (e.g. "Facebook AI" -> "Meta Platforms"), and minor spelling
    differences an exact wiki/<Name> URL guess can't. Returns [] on failure
    so the caller still falls back to the alias/exact candidates."""
    api = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "opensearch", "search": query, "limit": str(limit),
        "namespace": "0", "format": "json", "redirects": "resolve"})
    try:
        data = json.loads(fetch(api).decode("utf-8", errors="ignore"))
        return [t for t in (data[1] if len(data) > 1 else []) if t]
    except Exception:
        return []


_TITLE_TOKEN_STOPWORDS = {
    "a", "an", "and", "ai", "for", "inc", "lab", "labs", "llc", "ltd", "ml",
    "of", "research", "school", "the", "university",
}


def _title_tokens(text: str) -> set[str]:
    return {
        tok
        for tok in re.findall(r"[a-z0-9]+", text.lower())
        if len(tok) > 1 and tok not in _TITLE_TOKEN_STOPWORDS
    }


def search_title_relevant(query: str, title: str) -> bool:
    """Keep opensearch fallback titles tied to the requested institute.

    Wikipedia opensearch can return pages from the same broad parent brand
    (for example "Google Translate" for "Google Brain"). Exact aliases and
    explicit "(company)" / "(organization)" candidates are tried before this
    fallback, so search results should preserve the distinctive query token
    rather than accepting a merely adjacent brand page.
    """
    query_tokens = _title_tokens(query)
    if not query_tokens:
        return True
    title_tokens = _title_tokens(title)
    if len(query_tokens) == 1:
        return bool(query_tokens & title_tokens)
    # For multi-token institute names, require at least two shared tokens.
    # This rejects adjacent brand pages like "Google Translate" for
    # "Google Brain", while still allowing small article-title variants.
    return len(query_tokens & title_tokens) >= min(2, len(query_tokens))


# Tails we strip when generating parent-candidate fallbacks for an institute
# name. Order: most specific first. Match is case-insensitive.
# Note: "Institute of X" intentionally NOT stripped here — bare "Institute" is
# usually part of the institution's name (Massachusetts Institute of Tech,
# Indian Institute of Tech, ...). The alias dict handles those.
_DEPARTMENTAL_TAIL_PATTERNS = [
    r"\s*[,/;]\s*Department\s+of\s+.*$",
    r"\s+Department\s+of\s+.*$",
    r"\s*[,/;]\s*School\s+of\s+.*$",
    r"\s+School\s+of\s+.*$",
    r"\s*[,/;]\s*College\s+of\s+.*$",
    r"\s+College\s+of\s+.*$",
    r"\s*[,/;]\s*Faculty\s+of\s+.*$",
    r"\s+Faculty\s+of\s+.*$",
    r"\s*[,/;]\s*Division\s+of\s+.*$",
    r"\s+Division\s+of\s+.*$",
    r"\s*[,/;]\s*Center\s+for\s+.*$",
    r"\s+Center\s+for\s+.*$",
    r"\s*[,/;]\s*Centre\s+for\s+.*$",
    r"\s+Centre\s+for\s+.*$",
    r"\s*[,/;]\s*(?:AI\s+|ML\s+|Robotics\s+|Computer\s+Vision\s+)?Lab(?:oratory)?s?\s*$",
    r"\s+(?:AI\s+|ML\s+|Robotics\s+|Computer\s+Vision\s+)?Lab(?:oratory)?s?\s*$",
    r"\s*[,/;]\s*(?:Research\s+)?Group\s*$",
    r"\s+(?:Research\s+)?Group\s*$",
    r"\s*[,/;]\s*Center\s*$",
    r"\s+Center\s*$",
    r"\s*[,/;]\s*Centre\s*$",
    r"\s+Centre\s*$",
    r"\s*[,/;]\s*Division\s*$",
    r"\s+Division\s*$",
]

# Tokens that mark a segment as "looks like an institution proper".
# Used to rank segments when generating parent-institution candidates
# from a comma-separated input like "School of Pharmacy, Microsoft
# Research Asia, Shanghai, China".
#
# Tiered by confidence — when an input contains MULTIPLE
# institution-tokens across segments, the HIGHER-tier token's segment
# wins as the primary parent candidate:
#
#   HIGH = the segment almost certainly IS the institution.
#          Big-tech / lab names (microsoft, google, ...), "university",
#          "polytechnic", and the international variants. Promoting
#          these first fixes the previous-version bug where
#          "School of Pharmacy, Microsoft Research Asia" ranked
#          "School of Pharmacy" first (because both segments matched
#          the unweighted token list) and ended up grabbing a random
#          Wikipedia disambiguation icon instead of MSRA's logo.
#
#   MID  = the segment COULD be the institution (MIT / KAIST / IIT
#          all end in "Institute") OR could be a research-group label.
#          Used as fallback below HIGH.
#
#   LOW  = the segment is typically a SUB-UNIT but occasionally
#          could be the actual institution (some standalone "Schools"
#          and "Colleges" do exist as standalone Wikipedia entries).
#          Always ranked below MID.
_INSTITUTION_TOKENS_HIGH = (
    "university", "universidad", "université", "universität", "academia",
    "polytechnic",
    "microsoft", "google", "meta", "apple", "nvidia", "amazon", "openai",
    "anthropic", "deepmind", "ibm", "intel", "samsung", "tencent", "alibaba",
    "baidu", "huawei", "bytedance",
)
_INSTITUTION_TOKENS_MID = (
    "institute", "research", "labs", "laboratory",
)
_INSTITUTION_TOKENS_LOW = (
    "school", "college", "faculty", "division",
)


def _institution_tier(segment: str) -> int:
    """Return 0/1/2/3 ranking for a segment (lower = higher priority).
       0=HIGH, 1=MID, 2=LOW, 3=other (no institution token at all)."""
    s = segment.lower()
    if any(tok in s for tok in _INSTITUTION_TOKENS_HIGH):
        return 0
    if any(tok in s for tok in _INSTITUTION_TOKENS_MID):
        return 1
    if any(tok in s for tok in _INSTITUTION_TOKENS_LOW):
        return 2
    return 3


def _looks_like_institution_fallback(segment: str) -> bool:
    """Keep named institutions and acronym-like brands, not bare locations."""
    letters = re.sub(r"[^A-Za-z]", "", segment)
    return (
        _institution_tier(segment) < 3
        or segment.strip().lower() in ALIASES
        or (len(letters) >= 4 and letters.isupper())
    )


def parent_candidates(name: str) -> list[str]:
    """Generate parent-institution candidates for `name`, most specific first.

    The goal: when the input is a second-level institution like
    "Microsoft Research Asia, GenAI Group" or "Tsinghua University,
    Department of Computer Science", we may not find an infobox at the
    specific name's Wikipedia page — but the parent does have one. So we
    fall back: try the input as-is, then try progressively-more-generic
    variants until something resolves.

    Rules applied in order:
      1. The input as-is.
      2. Same with parenthesized phrases stripped: "Tsinghua University (China)"
         -> "Tsinghua University".
      3. Same with departmental tails stripped: "X University Lab" -> "X University".
      4. Each institution-like comma/dash/slash/semicolon-separated segment,
         ordered by
         institution-token TIER (see _institution_tier): HIGH segments
         (containing 'microsoft', 'university', 'polytechnic', ...) first,
         then MID ('institute', 'research', 'labs'), then LOW ('school',
         'college', 'faculty'). Trailing location-like segments are skipped;
         acronym-like institution names such as A*STAR remain eligible.
         Within the same tier, segments preserve input order.
         Example: "School of Pharmacy, Microsoft Research Asia, Shanghai"
         yields "Microsoft Research Asia" (HIGH via 'microsoft') BEFORE
         "School of Pharmacy" (LOW via 'school') — the previous version
         treated both as same-priority and randomly picked the first.
      5. Each segment with its own departmental-tail stripping.

    Duplicates are removed while preserving order. The caller (fetch_logo_for)
    tries each candidate via resolve_wikipedia_title -> Wikipedia infobox.
    The first one that yields a real logo wins; misses cascade to the next.
    """
    seen: set[str] = set()
    out: list[str] = []

    def push(s: str) -> None:
        s = s.strip(" ,;-—.").strip()
        if len(s) < 3:
            return
        key = s.lower()
        if key in seen:
            return
        seen.add(key)
        out.append(s)

    raw = name.strip()
    push(raw)

    # Strip parenthesized phrases.
    push(re.sub(r"\s*\([^)]*\)", "", raw).strip())

    # Strip departmental tails from the whole string.
    for pat in _DEPARTMENTAL_TAIL_PATTERNS:
        stripped = re.sub(pat, "", raw, flags=re.IGNORECASE).strip()
        if stripped != raw and _looks_like_institution_fallback(stripped):
            push(stripped)

    # Split into segments and rank by institution-token tier (HIGH=0 first).
    # Stable sort preserves input order within the same tier.
    segments = [s.strip() for s in re.split(r"\s*[,;/]\s*|\s+[-—]\s+", raw) if s.strip()]
    segments_ranked = sorted(
        enumerate(segments), key=lambda item: _institution_tier(item[1])
    )
    for original_index, seg in segments_ranked:
        if (
            not _looks_like_institution_fallback(seg)
            and original_index != 0
        ):
            continue
        push(seg)
        # Also strip tails on the segment itself.
        for pat in _DEPARTMENTAL_TAIL_PATTERNS:
            stripped = re.sub(pat, "", seg, flags=re.IGNORECASE).strip()
            if (
                stripped
                and stripped != seg
                and _looks_like_institution_fallback(stripped)
            ):
                push(stripped)
        # And strip parentheses on the segment.
        push(re.sub(r"\s*\([^)]*\)", "", seg).strip())

    return out


def find_logo_url(html: str) -> str | None:
    """Locate the first plausible logo <img> in the page's infobox.

    Restrict search to the infobox table — Wikipedia footers contain a
    Commons-logo.svg and other decorations that would otherwise score high
    on the "logo" keyword.
    """
    # Carve out the infobox HTML, if present. Wikipedia uses
    # <table class="infobox ..."> ... </table>; we grab the first one.
    m_box = re.search(r'<table[^>]*\bclass="[^"]*infobox[^"]*"[^>]*>(.*?)</table>', html, re.IGNORECASE | re.DOTALL)
    scope = m_box.group(1) if m_box else html
    img_pat = re.compile(r"<img\b[^>]*\bsrc=\"([^\"]+)\"", re.IGNORECASE)
    candidates: list[tuple[int, str]] = []
    for m in img_pat.finditer(scope):
        src = m.group(1)
        if "upload.wikimedia.org" not in src:
            continue
        low = src.lower()
        if any(k in low for k in SKIP_KEYWORDS):
            continue
        # Skip Wikipedia chrome (Commons-logo, edit-pencil, etc.) AND
        # generic icons that show up on disambiguation / stub pages
        # (Disambig_gray.svg is the grey wrench that appears on every
        # disambig page — picking it up made e.g. 'CFAR' (the disambig
        # page for Center for Frontier AI Research) produce a wrench
        # icon instead of cascading to A*STAR's real logo).
        if ("commons-logo" in low or "wikimedia-button" in low
                or "edit-ltr" in low or "disambig" in low
                or "question_book" in low or "stub_icon" in low
                or "cscr-featured" in low
                # Sister-project / chrome marks that decorate disambiguation and
                # general (non-company) articles -- a bare ambiguous name like
                # "Runway" lands on such a page and would otherwise pick up the
                # Wiktionary logo. Rejecting these makes the candidate cascade
                # fall through to the real company/org article. GENERAL, not
                # keyed to any one institute.
                or "wiktionary" in low or "wikinews" in low or "wikiquote" in low
                or "wikibooks" in low or "wikisource" in low or "wikiversity" in low
                or "wikivoyage" in low or "wikispecies" in low or "wikidata" in low
                or "wikipedia-logo" in low or "mediawiki" in low or "ambox" in low
                or "_padlock" in low
                or low.endswith("/increase2.svg") or low.endswith("/decrease2.svg")):
            continue
        score = 1  # infobox imgs get a base score so the first <img> wins absent keywords
        # Prefer the modern wordmark/logo over the legacy seal/crest (see LOGO_WEIGHTS).
        for kw, w in LOGO_WEIGHTS.items():
            if kw in low:
                score += w
        if ".svg" in low:
            score += 3
        # Commons files are freely licensed by policy; local en.wikipedia uploads
        # are frequently non-free fair-use marks -- prefer the reusable Commons one.
        if "/commons/" in low:
            score += 2
        candidates.append((score, src))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def _qid_from_html(html: str) -> str | None:
    """Pull the Wikidata entity id (Q…) embedded in a Wikipedia page."""
    m = re.search(r'"wgWikibaseItemId"\s*:\s*"(Q\d+)"', html)
    if m:
        return m.group(1)
    m = re.search(r"/Special:EntityData/(Q\d+)", html)
    return m.group(1) if m else None


def wikidata_logo_urls(qid: str | None) -> list[str]:
    """Commons file URLs from the entity's `logo image` (P154), NEWEST first.

    P154 is the institution's OFFICIAL logo(s), curated on Wikidata -- more up
    to date than the legacy seal a Wikipedia infobox may list first (e.g. MIT's
    2023 red wordmark vs. the round seal). Commons hosts only freely-licensed /
    public-domain files, so a P154 hit is also safe for others to reuse.

    An entity often lists MANY versions (Microsoft has 4, Google 6). Pick the
    CURRENT one by ranking each value on:
      1. Wikidata rank -- editors flag the live logo `preferred`.
      2. no P582 end-time -- a value with an end date is a retired logo.
      3. latest P580 start-time -- the most recently adopted mark.
      4. latest P582 end-time -- tiebreak when every value is retired.
    Older versions stay in the list (after the newest) as download fallbacks.
    """
    if not qid:
        return []
    try:
        raw = fetch(
            f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
        ).decode("utf-8", errors="ignore")
        claims = json.loads(raw).get("entities", {}).get(qid, {}).get("claims", {})
    except Exception:
        return []
    RANK = {"preferred": 2, "normal": 1, "deprecated": 0}

    def _qtime(quals: dict, pid: str) -> str:
        # Wikidata times look like "+2012-08-24T00:00:00Z"; the leading-year ISO
        # shape sorts chronologically as a plain string. Missing -> "".
        try:
            return quals[pid][0]["datavalue"]["value"]["time"].lstrip("+")
        except Exception:
            return ""

    rows = []
    for c in claims.get("P154", []):
        fn = c.get("mainsnak", {}).get("datavalue", {}).get("value")
        if not isinstance(fn, str):
            continue
        quals = c.get("qualifiers", {})
        end = _qtime(quals, "P582")
        rows.append((
            RANK.get(c.get("rank"), 1),      # preferred (live) logo wins
            0 if end else 1,                 # still-current beats retired
            _qtime(quals, "P580"),           # newest adoption date first
            end,                             # newest retirement date (tiebreak)
            fn,
        ))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[3]), reverse=True)
    return ["https://commons.wikimedia.org/wiki/Special:FilePath/"
            + urllib.parse.quote(fn.replace(" ", "_")) for *_, fn in rows]


def thumb_to_full(url: str) -> list[str]:
    """Return candidate URLs in priority order: original first, then safe thumbs.

    Wikimedia rejects arbitrary thumb widths with HTTP 400 ("Use thumbnail
    sizes listed on https://w.wiki/GHai"). For raster originals we strip
    `/thumb/.../NNNpx-...` to get the source file; for SVG-derived PNGs we
    fall back to a list of commonly-allowed widths (500, 330, 250).
    """
    if url.startswith("//"):
        url = "https:" + url
    cands: list[str] = []
    if "/thumb/" in url:
        # Strip the /thumb/ middle: .../commons/thumb/a/ab/Foo.png/NNNpx-Foo.png
        # → .../commons/a/ab/Foo.png
        m = re.match(r"(.*?)/thumb/([^/]+/[^/]+/[^/]+)/\d+px-[^/]+$", url)
        if m:
            cands.append(m.group(1) + "/" + m.group(2))
        # Also try a few documented thumb widths for SVG sources (the
        # original .svg cannot be rendered server-side at arbitrary px).
        for w in (500, 330, 250, 1024):
            cands.append(re.sub(r"/\d+px-", f"/{w}px-", url))
    else:
        cands.append(url)
    # De-dup while preserving order.
    seen, out = set(), []
    for u in cands:
        if u not in seen:
            seen.add(u); out.append(u)
    return out


def is_image(data: bytes) -> bool:
    if not data or len(data) < 32:
        return False
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return True
    if data[:3] == b"\xff\xd8\xff":
        return True  # jpeg
    if data[:4] == b"<svg" or data[:5] == b"<?xml":
        return True
    return False


def detect_ext(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    if data[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if data[:4] == b"<svg" or data[:5] == b"<?xml":
        return ".svg"
    return ".png"  # fallback


MANIFEST_VERSION = 2


def _manifest_path(logos_dir: Path) -> Path:
    return logos_dir / "logos.json"


def _load_manifest(logos_dir: Path) -> dict:
    path = _manifest_path(logos_dir)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
        manifest = loaded if isinstance(loaded, dict) else {}
    except (OSError, ValueError, TypeError):
        manifest = {}
    manifest.setdefault("version", MANIFEST_VERSION)
    for key in ("logos", "missing", "rejected"):
        if not isinstance(manifest.get(key), list):
            manifest[key] = []
    return manifest


def _write_manifest(logos_dir: Path, manifest: dict) -> None:
    """Atomically persist the authoritative accepted/rejected selection."""
    manifest = dict(manifest)
    manifest["version"] = MANIFEST_VERSION
    destination = _manifest_path(logos_dir)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=logos_dir,
            prefix=".logos-", suffix=".json.tmp", delete=False,
        ) as handle:
            json.dump(manifest, handle, indent=2)
            handle.write("\n")
            temporary = Path(handle.name)
        temporary.replace(destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink(missing_ok=True)


def _entry_keys(entry: dict) -> set[str]:
    keys = {
        str(key).strip()
        for key in (entry.get("institution_keys") or [])
        if str(key).strip()
    }
    if entry.get("institution_key"):
        keys.add(str(entry["institution_key"]).strip())
    if not keys:
        for name in str(entry.get("name") or "").split(";"):
            if name.strip():
                keys.add(canonical_institution_key(name.strip()))
    return keys


def _entry_file(entry: dict, logos_dir: Path) -> Path | None:
    """Resolve a manifest logo path without allowing traversal.

    Manifest paths are bundle-relative (``assets/logos/foo.png``).  Resolving
    them against ``logos_dir.parent`` produced ``assets/assets/logos`` and was
    the reason duplicate files were never removed.  The filename is sufficient
    because accepted institution marks are contractually direct children of
    ``assets/logos``.
    """
    raw = str(entry.get("path") or "")
    name = Path(raw).name
    if not name or name in {".", "..", "logos.json", "_venue.png"}:
        return None
    candidate = (logos_dir / name).resolve()
    try:
        candidate.relative_to(logos_dir.resolve())
    except ValueError:
        return None
    return candidate


def _delete_manifest_file(
    entry: dict, logos_dir: Path, protected: set[Path] | None = None,
) -> bool:
    """Delete only a superseded manifest-owned file, never an orphan asset."""
    path = _entry_file(entry, logos_dir)
    protected = {p.resolve() for p in (protected or set())}
    if path is None or path.resolve() in protected or not path.exists():
        return False
    path.unlink(missing_ok=True)
    return True


def _quality_payload(inspection) -> dict:
    return inspection.to_dict()


def _approved_entry(
    name: str,
    slug: str,
    path: Path,
    source: str,
    inspection,
    *,
    resolved_title: str | None = None,
) -> dict:
    requested_key = canonical_institution_key(name)
    institution_key = canonical_institution_key(name, resolved_title)
    institution_keys = list(dict.fromkeys((institution_key, requested_key)))
    return {
        "name": name,
        "institution_key": institution_key,
        "institution_keys": institution_keys,
        "slug": slug,
        "path": f"{layout.LOGOS}/{path.name}",
        "source": source,
        "approved": True,
        "decision": "approved",
        "fingerprint": inspection.fingerprint,
        "quality": _quality_payload(inspection),
    }


def _rejected_entry(
    name: str, source: str, inspection, *, stage: str,
    resolved_title: str | None = None,
) -> dict:
    return {
        "name": name,
        "institution_key": canonical_institution_key(name, resolved_title),
        "source": source,
        "stage": stage,
        "approved": False,
        "decision": "rejected",
        "reason": inspection.reason,
        "quality": _quality_payload(inspection),
    }


def _merge_rejected(previous: list[dict], new: list[dict]) -> list[dict]:
    merged: dict[tuple[str, str, str], dict] = {}
    for entry in [*previous, *new]:
        if not isinstance(entry, dict):
            continue
        key = (
            str(entry.get("institution_key") or ""),
            str(entry.get("source") or ""),
            str(entry.get("reason") or ""),
        )
        merged[key] = entry
    return list(merged.values())


def _entry_is_approved(entry: dict) -> bool:
    """Keep historical accepted entries while honoring explicit rejections."""
    if not isinstance(entry, dict):
        return False
    if "approved" in entry and entry.get("approved") is not True:
        return False
    if "decision" in entry and str(entry.get("decision", "")).lower() != "approved":
        return False
    quality = entry.get("quality")
    if isinstance(quality, dict) and quality.get("accepted") is False:
        return False
    return True


def _merge_entry_identity(keeper: dict, duplicate: dict) -> None:
    """Fold display names and canonical institution identities into a keeper."""
    names: list[str] = []
    for entry in (keeper, duplicate):
        for name in str(entry.get("name") or "").split(";"):
            name = name.strip()
            if name and name not in names:
                names.append(name)
    if names:
        keeper["name"] = "; ".join(names)

    keys: list[str] = []
    for entry in (keeper, duplicate):
        for key in _entry_keys(entry):
            if key and key not in keys:
                keys.append(key)
    if keys:
        keeper["institution_key"] = str(
            keeper.get("institution_key") or keys[0]
        )
        keeper["institution_keys"] = keys


def download_named_logo(
    name: str, url: str, logos_dir: Path, rejected: list[dict] | None = None,
) -> dict | None:
    """Download ONE logo from an explicit URL for the web-search fallback.

    Reuses the same pipeline as the Wikimedia path (detect ext → slug from the
    institute name → autotrim the border) so a fallback logo looks identical in
    the header to the deterministically-fetched ones. Returns a manifest entry
    (or None on failure). Used by `--add-logo "Name=URL"`.
    """
    try:
        data = fetch(url)
    except Exception as e:
        print(f"[fetch_logos] add-logo {name!r}: download failed ({url}): {e}", file=sys.stderr)
        return None
    inspection = inspect_logo_bytes(data, source=url)
    if not inspection.accepted:
        failure = _rejected_entry(name, url, inspection, stage="web-fallback")
        if rejected is not None:
            rejected.append(failure)
        print(
            f"[fetch_logos] add-logo {name!r}: rejected {inspection.reason} ({url})",
            file=sys.stderr,
        )
        return None
    ext = detect_ext(data)
    slug = slugify(name)
    out = logos_dir / f"{slug}{ext}"
    out.write_bytes(data)
    tight = autotrim(out)
    if tight != out:
        try:
            out.unlink()
        except Exception:
            pass
        out = tight
    info = _approved_entry(name, slug, out, url, inspection)
    print(
        f"[fetch_logos] add-logo {name!r} -> {info['path']}  "
        f"({out.stat().st_size} bytes, source={url})",
        file=sys.stderr,
    )
    return info


def fetch_logo_for(
    name: str, rejected: list[dict] | None = None,
) -> dict | None:
    """Fetch (don't yet write) the best logo for `name`.

    Tries a fallback chain of parent-institution candidates (see
    `parent_candidates`): the input as-is first, then progressively-more-
    generic variants. First candidate that resolves to a real infobox
    logo wins. This handles the second-level-institution case where the
    specific sub-org doesn't have its own Wikipedia article — e.g.
    "Microsoft Research Asia, GenAI Group" cascades to "Microsoft Research
    Asia" -> alias to "Microsoft" (parent company, four-square logo) -> hit.
    Same for
    "Tsinghua University, Department of CS" cascading to "Tsinghua
    University". The returned dict's `name` keeps the ORIGINAL input
    string so the spec's display name is preserved; `title` records
    which parent candidate actually resolved.

    Returns {"name", "title", "source", "data"} on success — caller is
    responsible for writing the bytes to disk after dedup. Splitting fetch
    from write lets `main()` skip duplicates (two institutes resolving to
    the same Wikipedia title, the same source URL, or the same image bytes)
    so the titlebar doesn't render two identical tiles.
    """
    candidates = parent_candidates(name) or [name.strip()]
    # Ordered, de-duped Wikipedia article titles to try:
    #   1. alias hit (or raw text) for each parent candidate — fast, no API.
    #   2. opensearch matches for the raw name + the top-ranked candidate —
    #      robust to abbreviations / rebrands / NEW orgs with no hardcoded
    #      alias (e.g. "Facebook AI" -> search -> "Meta Platforms").
    titles: list[str] = []
    seen: set[str] = set()
    def _add(t: str) -> None:
        t = (t or "").strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            titles.append(t)
    for cand in candidates:
        _add(resolve_wikipedia_title(cand))
    # If ANY candidate has an explicit ALIAS mapping, that alias IS the answer --
    # a curated brand->parent decision (e.g. "microsoft research asia" -> "Microsoft"
    # for the four-square corporate mark, NOT the Microsoft Research wordmark).
    # Trust it and SKIP the opensearch fallback below, which otherwise searches
    # the raw name and drags in the sibling-brand page ("Microsoft Research"),
    # winning nondeterministically whenever the aliased page fetch flakes.
    aliased = any(c.strip().lower() in ALIASES for c in candidates)
    if not aliased:
        # Disambiguation-aware company/org variants (GENERAL -- no per-company alias):
        # an ambiguous short name ("Runway", "Cohere") often has its company article
        # under a "(company)" / "(organization)" title while the BARE article is a
        # dictionary word or disambiguation page. Strip a trailing "ML/AI/Inc/Labs/..."
        # so "Runway ML" -> "Runway (company)". Tried BEFORE the noisy opensearch
        # results so e.g. "Runway (company)" beats "Runway (song)".
        core = re.sub(r"\s+(ml|ai|inc\.?|llc|ltd\.?|gmbh|labs?|research|technologies)$",
                      "", name.strip(), flags=re.I).strip()
        for base in dict.fromkeys([name.strip(), core]):
            if base and 1 <= len(base.split()) <= 3:
                for suf in ("(company)", "(organization)", "(software)"):
                    _add(f"{base} {suf}")
        for q in dict.fromkeys([name.strip(), candidates[0]]):
            for t in search_wikipedia_titles(q):
                if search_title_relevant(q, t):
                    _add(t)
    else:
        # Aliased: only allow the disambiguation variants of the alias TARGET.
        for cand in candidates:
            tgt = ALIASES.get(cand.strip().lower())
            if tgt and 1 <= len(tgt.split()) <= 3:
                for suf in ("(company)", "(organization)"):
                    _add(f"{tgt} {suf}")

    for title in titles:
        page = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
        try:
            html = fetch(page).decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[fetch_logos] {name!r} via {title!r}: wiki fetch failed: {e}", file=sys.stderr)
            continue
        # Wikidata `logo image` (P154) is normally the best source.  When it is
        # explicitly a localized text mark, prefer the English infobox logo so
        # a Korean/Chinese wordmark does not replace a recognizable mark.
        wd_urls = wikidata_logo_urls(_qid_from_html(html))
        src = find_logo_url(html)
        if not wd_urls and not src:
            print(f"[fetch_logos] {name!r} via {title!r}: no logo at {page}", file=sys.stderr)
            continue
        infobox_urls = thumb_to_full(src) if src else []
        p154_name = (
            urllib.parse.unquote(wd_urls[0]).lower().replace("_", " ")
            if wd_urls else ""
        )
        localized_text_mark = (
            "characters" in p154_name
            or bool(re.search(r"logotype\s*\((?!en\))[^)]+\)", p154_name))
        )
        full_candidates = (
            infobox_urls + wd_urls if localized_text_mark and infobox_urls
            else wd_urls + infobox_urls
        )
        data = None
        chosen_url = None
        chosen_inspection = None
        for full in full_candidates:
            try:
                blob = fetch(full)
            except Exception:
                continue
            inspection = inspect_logo_bytes(blob, source=full)
            if not inspection.accepted:
                if rejected is not None:
                    rejected.append(_rejected_entry(
                        name, full, inspection, stage="wikimedia",
                        resolved_title=title,
                    ))
                print(
                    f"[fetch_logos] {name!r} via {title!r}: rejected "
                    f"{inspection.reason} ({full})",
                    file=sys.stderr,
                )
                continue
            data = blob
            chosen_url = full
            chosen_inspection = inspection
            break
        if not data:
            print(f"[fetch_logos] {name!r} via {title!r}: all download candidates failed", file=sys.stderr)
            continue
        if title.strip().lower() != name.strip().lower():
            print(f"[fetch_logos] {name!r}: resolved via {title!r}", file=sys.stderr)
        return {
            "name": name,
            "title": title,
            "source": chosen_url,
            "data": data,
            "inspection": chosen_inspection,
            "institution_key": canonical_institution_key(name, title),
        }
    print(f"[fetch_logos] {name!r}: no candidate produced a logo (tried {len(titles)})", file=sys.stderr)
    return None


def parse_names(arg: str | None, spec: Path | None) -> list[str]:
    if arg:
        # Accept either ; or newline separation.
        parts = re.split(r"[;\n]", arg)
        return [p.strip() for p in parts if p.strip()]
    if spec and spec.exists():
        # Two accepted formats:
        #   - YAML frontmatter (current paper_spec.md):
        #       institutes: ¹CFAR, A*STAR; ²IHPC, A*STAR; …
        #   - legacy markdown (older spec files):
        #       **Institutes:** CFAR, A*STAR; IHPC, A*STAR; …
        # The institutes are `;`-separated (per SKILL.md Step 3).
        # Don't split on commas — names like 'University of California,
        # San Diego' contain commas. Strip leading superscript markers
        # (¹²³⁴⁵⁶⁷⁸⁹⁰ plus *†‡§¶ commonly used) from each name so the
        # Wikipedia lookup sees 'CFAR, A*STAR' not '¹CFAR, A*STAR'.
        line_pat = re.compile(
            r"^\s*(?:\*\*Institutes:\*\*|institutes\s*:)\s*(.+?)\s*$",
            re.IGNORECASE,
        )
        marker_pat = re.compile(r"^[²³¹⁰-⁹*†‡§¶0-9\s.,\-]+")
        for line in spec.read_text(encoding="utf-8").splitlines():
            m = line_pat.match(line)
            if not m:
                continue
            out: list[str] = []
            for raw in m.group(1).split(";"):
                cleaned = marker_pat.sub("", raw).strip()
                if cleaned:
                    out.append(cleaned)
            if out:
                return out
    return []


def _dedupe_by_source(
    results: list[dict], logos_dir: Path, *, delete_duplicates: bool = True,
) -> list[dict]:
    """Collapse manifest entries that resolved to the SAME logo so the poster
    titlebar renders one tile per visually-distinct mark.

    Three-level dedup:
      1. by `source` URL (cheapest; catches MSR + MSRA + Microsoft Research
         all hitting the same Wikipedia file).
      2. by perceptual fingerprint (catches the same mark encoded as PNG/JPEG
         or downloaded at a different resolution).
      3. by exact file hash when a legacy entry has no usable fingerprint.

    First-seen entry wins; later duplicates have their local file removed
    (the survivor's file stays). The survivor's `name` becomes a `;`-joined
    list of all institute names that shared the file, so downstream
    substitution can show 'A*STAR (CFAR / IHPC)' in alt-text or tooltips."""
    seen_src: dict[str, dict] = {}
    seen_hash: dict[str, dict] = {}
    fingerprinted: list[dict] = []
    kept: list[dict] = []

    for entry in results:
        if not isinstance(entry, dict):
            continue
        file_path = _entry_file(entry, logos_dir)
        fingerprint = str(entry.get("fingerprint") or "")
        if not fingerprint and file_path is not None and file_path.is_file():
            inspection = inspect_logo_path(
                file_path, source=str(entry.get("source") or file_path),
            )
            if inspection.accepted:
                fingerprint = inspection.fingerprint
                entry["fingerprint"] = fingerprint
                entry.setdefault("quality", _quality_payload(inspection))

        src = entry.get("source", "")
        duplicate = seen_src.get(str(src)) if src else None
        reason = "same source"
        if duplicate is None and fingerprint:
            duplicate = next(
                (
                    prior for prior in fingerprinted
                    if fingerprints_match(
                        fingerprint, str(prior.get("fingerprint") or "")
                    )
                ),
                None,
            )
            reason = "same visual fingerprint"

        file_hash = ""
        if duplicate is None and file_path is not None and file_path.is_file():
            try:
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            except OSError:
                file_hash = ""
            if file_hash:
                duplicate = seen_hash.get(file_hash)
                reason = "same bytes"

        if duplicate is not None:
            original_name = entry.get("name", "")
            _merge_entry_identity(duplicate, entry)
            if delete_duplicates:
                keeper_path = _entry_file(duplicate, logos_dir)
                protected = {keeper_path} if keeper_path is not None else set()
                _delete_manifest_file(entry, logos_dir, protected=protected)
            print(
                f"[fetch_logos] dedup ({reason}): {original_name!r} "
                f"→ folded into {str(duplicate.get('name', '')).split(';')[0]!r}",
                file=sys.stderr,
            )
            continue

        if src:
            seen_src[str(src)] = entry
        if fingerprint:
            fingerprinted.append(entry)
        if file_hash:
            seen_hash[file_hash] = entry
        kept.append(entry)
    return kept


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--outdir", required=True, type=Path, help="Poster outdir; logos/ is created inside it. (If you pass <outdir>/logos by mistake, the trailing /logos is auto-stripped with a warning — see Step 6 of paper2assets/SKILL.md.)")
    ap.add_argument("--names", help='Semicolon-separated institute names, e.g. "Microsoft Research Asia;UCSD;Tsinghua University"')
    ap.add_argument("--from-spec", "--spec", dest="from_spec", type=Path,
                    help="Read names from the **Institutes:** line of paper_spec.md. "
                         "(`--spec` is a backward-compat alias; the canonical flag is "
                         "`--from-spec` because that's what SKILL.md/help-output says.)")
    ap.add_argument("--add-logo", action="append", default=[], metavar='"Name=URL"',
                    help="Web-search FALLBACK: download ONE logo for an institute the "
                         "deterministic pass reported as missing. Format 'Name=URL'. "
                         "Repeatable. Skips the Wikimedia pass, applies the same quality "
                         "gate, and atomically merges accepted selections into logos.json.")
    args = ap.parse_args(argv)

    # Defensive: if caller passed `<outdir>/logos` (a common SKILL.md
    # misreading — script appends /logos itself, so passing it ends up
    # at <outdir>/logos/logos/<slug>.png and downstream paper2poster
    # finds nothing). Strip it once with a loud warning so the bug is
    # visible in batch logs.
    # Defensive: if caller passed `<outdir>/logos` or `<outdir>/assets/logos`
    # (a common SKILL.md misreading — the script appends the canonical
    # `assets/logos/` itself, so passing it ends up nested and downstream
    # paper2poster finds nothing). Strip it once with a loud warning so the
    # bug is visible in batch logs.
    if args.outdir.name == "logos":
        stripped = args.outdir.parent
        if stripped.name == "assets":
            stripped = stripped.parent
        print(f"[fetch_logos] WARNING: --outdir ends in '/logos' "
              f"({args.outdir!s}); auto-stripping to {stripped!s}. "
              f"Pass the POSTER OUTDIR (assets/logos/ is created inside it).",
              file=sys.stderr)
        args.outdir = stripped

    logos_dir = layout.logos_dir(args.outdir, create=True)
    previous = _load_manifest(logos_dir)

    # FALLBACK MODE: merge explicit web-search results into the authoritative
    # manifest. Replacing one institution never discards unrelated entries or
    # user-owned orphan files that merely happen to live beside the manifest.
    if args.add_logo:
        added: list[dict] = []
        new_rejected: list[dict] = []
        for spec in args.add_logo:
            if "=" not in spec:
                print(f"[fetch_logos] --add-logo needs 'Name=URL', got {spec!r}", file=sys.stderr)
                continue
            nm, url = spec.split("=", 1)
            info = download_named_logo(
                nm.strip(), url.strip(), logos_dir, rejected=new_rejected,
            )
            if info:
                added.append(info)
        added = _dedupe_by_source(added, logos_dir)

        previous_accepted = [
            dict(entry) for entry in previous["logos"]
            if _entry_is_approved(entry)
        ]
        added_keys = (
            set().union(*(_entry_keys(entry) for entry in added))
            if added else set()
        )
        retained: list[dict] = []
        superseded: list[dict] = []
        for entry in previous_accepted:
            if added_keys & _entry_keys(entry):
                superseded.append(entry)
            else:
                retained.append(entry)

        candidates = [*retained, *added]
        merged = _dedupe_by_source(
            candidates, logos_dir, delete_duplicates=False,
        )
        merged_paths = {
            path.resolve()
            for entry in merged
            if (path := _entry_file(entry, logos_dir)) is not None
        }
        discarded = [
            entry for entry in candidates
            if (path := _entry_file(entry, logos_dir)) is not None
            and path.resolve() not in merged_paths
        ]
        missing = [
            name for name in previous["missing"]
            if canonical_institution_key(str(name)) not in added_keys
        ]
        manifest = {
            "version": MANIFEST_VERSION,
            "logos": merged,
            "missing": missing,
            "rejected": _merge_rejected(previous["rejected"], new_rejected),
        }
        try:
            _write_manifest(logos_dir, manifest)
        except Exception as exc:  # noqa: BLE001
            print(f"[fetch_logos] ERROR: could not write logos.json: {exc}", file=sys.stderr)
            print(json.dumps(manifest, indent=2))
            return 1

        for entry in [*superseded, *discarded]:
            _delete_manifest_file(entry, logos_dir, protected=merged_paths)
        print(
            f"[fetch_logos] manifest -> {layout.LOGOS}/logos.json "
            f"({len(merged)} logo(s))",
            file=sys.stderr,
        )
        print(json.dumps(manifest, indent=2))
        return 0 if added else 1

    names = parse_names(args.names, args.from_spec)
    if not names:
        print("[fetch_logos] no institute names provided (use --names or --from-spec)", file=sys.stderr)
        return 2

    results: list[dict] = []
    new_rejected: list[dict] = []
    requested_keys = {canonical_institution_key(name) for name in names}
    seen_requested: set[str] = set()
    for name in names:
        request_key = canonical_institution_key(name)
        if request_key in seen_requested:
            print(
                f"[fetch_logos] {name!r}: deduped -- same canonical "
                f"institution key {request_key!r}; skipping",
                file=sys.stderr,
            )
            continue
        seen_requested.add(request_key)
        fetched = fetch_logo_for(name, rejected=new_rejected)
        if not fetched:
            continue

        slug = slugify(fetched["title"])
        ext = detect_ext(fetched["data"])
        out = logos_dir / f"{slug}{ext}"
        out.write_bytes(fetched["data"])
        tight = autotrim(out)
        if tight != out:
            try:
                out.unlink()
            except Exception:
                pass
            out = tight
        info = _approved_entry(
            name, slug, out, fetched["source"], fetched["inspection"],
            resolved_title=fetched["title"],
        )
        print(
            f"[fetch_logos] {name!r} -> {info['path']}  "
            f"({out.stat().st_size} bytes, source={fetched['source']})",
            file=sys.stderr,
        )
        results.append(info)

    results = _dedupe_by_source(results, logos_dir)

    # A deterministic result replaces a prior fallback for the same canonical
    # institution. If Wikimedia still misses, preserve a valid existing fallback
    # selected for one of the current spec's institutes.
    resolved_keys = (
        set().union(*(_entry_keys(entry) for entry in results))
        if results else set()
    )
    preserved: list[dict] = []
    old_selected: list[dict] = []
    for raw_entry in previous["logos"]:
        if not _entry_is_approved(raw_entry):
            continue
        entry = dict(raw_entry)
        keys = _entry_keys(entry)
        if not keys & requested_keys:
            continue
        old_selected.append(entry)
        if keys & resolved_keys:
            continue
        path = _entry_file(entry, logos_dir)
        inspection = (
            inspect_logo_path(
                path, source=str(entry.get("source") or path),
            )
            if path is not None and path.is_file() else None
        )
        if inspection is None or not inspection.accepted:
            if inspection is not None:
                for display_name in str(entry.get("name") or "").split(";"):
                    new_rejected.append(_rejected_entry(
                        display_name.strip() or "unknown",
                        str(entry.get("source") or entry.get("path") or ""),
                        inspection,
                        stage="existing-manifest",
                    ))
            continue
        entry["approved"] = True
        entry["decision"] = "approved"
        entry["fingerprint"] = inspection.fingerprint
        entry["quality"] = _quality_payload(inspection)
        entry_keys = list(keys)
        if entry_keys:
            entry["institution_key"] = str(
                entry.get("institution_key") or entry_keys[0]
            )
            entry["institution_keys"] = entry_keys
        preserved.append(entry)

    candidates = [*results, *preserved]
    final_results = _dedupe_by_source(
        candidates, logos_dir, delete_duplicates=False,
    )
    final_keys = (
        set().union(*(_entry_keys(entry) for entry in final_results))
        if final_results else set()
    )
    missing = [
        name for name in names
        if canonical_institution_key(name) not in final_keys
    ]

    resolved_count = len(names) - len(missing)
    print(f"[fetch_logos] CHECKLIST: {resolved_count}/{len(names)} institute(s) resolved", file=sys.stderr)
    for name in names:
        mark = "✓" if canonical_institution_key(name) in final_keys else "✗"
        print(f"[fetch_logos]   {mark} {name}", file=sys.stderr)
    if missing:
        print(f"[fetch_logos]   ✗ MISSING — WEB-SEARCH FALLBACK REQUIRED (Step 6): {', '.join(missing)}", file=sys.stderr)

    manifest = {
        "version": MANIFEST_VERSION,
        "logos": final_results,
        "missing": missing,
        "rejected": _merge_rejected(previous["rejected"], new_rejected),
    }
    try:
        _write_manifest(logos_dir, manifest)
        print(f"[fetch_logos] manifest -> {layout.LOGOS}/logos.json "
              f"({len(final_results)} logo(s))", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"[fetch_logos] ERROR: could not write logos.json: {exc}", file=sys.stderr)
        print(json.dumps(manifest, indent=2))
        return 1

    final_paths = {
        path.resolve()
        for entry in final_results
        if (path := _entry_file(entry, logos_dir)) is not None
    }
    for entry in [*old_selected, *candidates]:
        path = _entry_file(entry, logos_dir)
        if path is not None and path.resolve() not in final_paths:
            _delete_manifest_file(entry, logos_dir, protected=final_paths)

    print(json.dumps(manifest, indent=2))
    return 0 if final_results else 1


if __name__ == "__main__":
    raise SystemExit(main())
