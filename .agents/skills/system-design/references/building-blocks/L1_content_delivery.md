---
name: content-delivery
description: This skill should be used when the user asks about a "CDN", "edge caching", "static asset delivery", "media / video delivery", "geo distribution of content" or "edge POP selection", "push vs pull CDN", "cache-control headers" / "TTL for static assets", "origin offload", or "origin shield". It gives the recipe for serving bytes from the edge close to users. Use it whenever a design serves images, video, JS/CSS, or downloads to a wide geography, or the origin is saturated by repeat reads of the same files, even if the user doesn't say "CDN".
---

# Content Delivery

Push bytes to the network edge so requests terminate close to the user and never
reach the origin. A CDN is the outermost cache layer of a system: get it right and
most static/media traffic and a chunk of latency vanish before they hit your
servers; get it wrong and you serve stale assets, leak origin load, or pay egress
twice.

## When to reach for this
The same files (images, video, JS/CSS bundles, downloads, fonts) are read
repeatedly by a geographically spread audience; the origin or its bandwidth is the
bottleneck for static reads; or cross-region latency on first byte hurts (a
cross-continent round trip is ~100 ms â€” see `back-of-the-envelope`). A CDN buys
latency *and* origin offload at once.

## When NOT to
Highly personalized, per-request dynamic responses with no cacheable shape (a CDN
adds a hop and caches nothing). Tiny single-region audiences where the origin
already serves reads comfortably (YAGNI â€” a CDN is another vendor, another bill,
another invalidation problem). Strictly fresh data that cannot tolerate any
staleness window â€” that belongs at the origin or behind `consistency-coordination`,
not a TTL-based edge. Naming a CDN before a number shows static reads or geography
is the problem is a red flag.

## Clarify first
- **Content mix** â€” what fraction is cacheable static/media vs uncacheable
  dynamic/personalized? (Only the cacheable part benefits.)
- **Update cadence & staleness budget** â€” how often do assets change, and how
  stale may an edge copy be? (Drives TTL and invalidation strategy.)
- **Geography** â€” where are users, and how concentrated? (Decides whether edge PoPs
  and geo-routing matter at all.)
- **Object size & egress volume** â€” average asset size Ã— requests = egress; this
  sizes the bill and the offload (â†’ `back-of-the-envelope`).
- **Origin shape** â€” object store (S3/GCS/blob) or dynamic app server? Can it
  survive a cold-cache stampede if the edge flushes?

## The options

**Distribution model â€” how content reaches the edge**
- **Pull (origin-pull):** the edge fetches on first miss, caches per TTL, serves
  the rest. *Use when* traffic is high and content is large or churny â€” the edge
  holds only what's actually requested. The default for most systems.
- **Push:** you upload assets to the CDN ahead of demand and rewrite URLs.
  *Use when* the catalog is small/static or launch spikes can't tolerate a cold
  first-miss (you pre-warm); you accept managing storage and uploads yourself.

**Caching key & TTL â€” what the edge keys on and for how long**
- **Long TTL + fingerprinted URLs** (`app.4f9a.js`, `image.png?v=2`): immutable
  assets cached for months; a content change is a *new URL*, not an invalidation.
  *Use when* you control asset URLs â€” the cleanest model.
- **Short TTL / `stale-while-revalidate`:** bound staleness for content that
  changes on a schedule. *Use when* URLs are stable but content updates.

**Edge proximity & routing â€” how a user reaches the nearest PoP**
- **Anycast / DNS geo-routing:** route each user to the closest healthy edge.
  *Use when* the audience is multi-region (almost always, for a CDN). Shared with
  `load-balancing` â€” see there for the routing mechanics.

**Origin protection â€” shrinking the origin's exposed surface**
- **Origin shield / mid-tier cache:** a single regional cache layer in front of the
  origin that all edges pull through, collapsing N edge misses into one origin
  fetch. *Use when* origin offload or stampede protection matters more than a
  little extra latency on cold misses.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Pull CDN | Edge holds only requested content; no upload pipeline | First request per object is a slow miss; redundant re-pulls when TTL expires before content changes | Cold-miss latency or launch spikes hurt â†’ push / pre-warm |
| Push CDN | No cold miss; full control of what's cached and when | You own upload + storage + URL rewriting; pay to store rarely-read assets | Catalog grows or churns â†’ pull |
| Long TTL + fingerprinted URLs | Near-permanent caching; updates are new URLs (no invalidation race) | Requires build/URL control; old versions linger at edge until aged out | URLs are not under your control â†’ short TTL |
| Short TTL / stale-while-revalidate | Bounded staleness on stable URLs | More origin revalidation traffic; synchronized expiry can stampede | Content is truly immutable â†’ fingerprint + long TTL |
| Geo-routing / anycast | Users hit the nearest edge; lower latency | More PoPs to reason about; routing can send users to a degraded PoP | Single-region audience â†’ skip it |
| Origin shield | Collapses edge misses into one origin fetch; protects origin | Extra hop on cold path; the shield is a new chokepoint/SPOF if single-region | Origin is robust and offload is already enough â†’ drop it |

## Behavior under stress
A CDN usually *absorbs* load spikes â€” that's its job â€” but it has its own failure
shapes, and they tend to dump straight onto the origin.

- **Cold cache / mass eviction:** after a purge, config push, or TTL synchronized
  expiry, edge hit rate craters and every PoP pulls from the origin at once. This
  is a `caching` thundering herd at global scale. *Mitigate:* origin shield to
  collapse misses, TTL jitter, `stale-while-revalidate` so the edge serves stale
  while it refetches, staged purges.
- **Cache busting / low hit rate:** unbounded query-string variation or cookies in
  the cache key explode the keyspace so nothing stays cached â€” the origin sees full
  traffic while you still pay the CDN. *Mitigate:* normalize/whitelist cache-key
  params; strip cookies on static paths.
- **Hot object:** one viral file can exceed a single PoP's capacity, but CDNs scale
  this far better than an origin â€” the real risk is a hot *uncacheable* path
  punching through to the origin.
- **CDN outage / partial PoP failure:** the edge is now a dependency in front of
  everything. Plan origin fallback (clients or DNS failover to origin) and accept
  the origin must briefly take full load, or use a second CDN (multi-CDN).
- **Egress surprise:** a misconfigured `no-cache` or a hot uncacheable asset can
  10Ã— the origin egress bill silently.

**Monitor:** edge hit ratio (cache hit rate), origin offload %, origin request rate
(the number that spikes when the edge fails), p95 edge latency by region, egress
bytes, and 4xx/5xx at the edge vs origin.

## How to apply
1. **Clarify the inputs** â€” content mix (cacheable fraction), staleness budget,
   geography, object size Ã— volume, and origin shape (see `Clarify first`). If the
   cacheable fraction is near zero or the audience is single-region, stop here.
2. **Pick the distribution model and cache key** from the trade-off table: default
   to **pull**; switch to **push/pre-warm** only when cold-miss latency or launch
   spikes hurt. Prefer **long TTL + fingerprinted URLs** when you control URLs,
   else **short TTL / `stale-while-revalidate`**.
3. **Set the knobs** â€” `Cache-Control` (max-age, immutable, stale-while-revalidate),
   the cache key (URL path + whitelisted params; strip cookies on static paths),
   `Vary` only where you truly differ, and add an **origin shield** if offload or
   stampede protection matters.
4. **Stress-test the design** â€” walk a global purge, a config push, and a CDN/PoP
   outage. Confirm TTL jitter + `stale-while-revalidate` + shield keep the origin
   survivable, and that a client/DNS fallback to origin exists.
5. **Size it with numbers** â€” estimate hit ratio (target 90%+), origin offload %,
   and egress (`requests Ã— avg object size`) via `back-of-the-envelope`. If egress
   or origin request rate is alarming, revisit the cache key and TTL.
6. **Pick a provider** â€” default to the generic recipe; if a cloud is named, read
   its provider file for the service mapping and limits (see `Choosing a provider`).

## Dos and don'ts
**Do**
- Fingerprint immutable assets and cache them for months â€” turn updates into new
  URLs, not invalidations.
- Whitelist cache-key params and strip cookies on static paths to keep hit ratio high.
- Add `stale-while-revalidate` and TTL jitter so synchronized expiry can't stampede
  the origin.
- Add an origin shield when many edges would otherwise miss to the origin at once.
- Plan an origin/DNS fallback (or multi-CDN) for a CDN or PoP outage.
- Monitor edge hit ratio and origin request rate â€” the number that spikes when the
  edge fails.

**Don't**
- Reach for a CDN before a number shows static reads or geography is the bottleneck.
- Let unbounded query strings or `Vary: Cookie` explode the keyspace and gut caching.
- Treat a single-region origin shield as free â€” it is a new chokepoint/SPOF.
- Cache strictly-fresh data on a TTL when zero staleness is required.
- Ship a careless `no-cache` on a hot asset â€” it can silently 10Ã— origin egress.

## Numbers that matter
The decisive quantities are **hit ratio** (90%+ is the goal; below ~80% question
whether content is cacheable), **origin offload %** (1 âˆ’ origin-requests/total),
and **egress** (`requests Ã— avg object size`). Edge-vs-origin latency is the
payoff: an edge hit is a same-region round trip (~ms to tens of ms) instead of a
cross-continent one (~100 ms). Do the egress and offload math with
`back-of-the-envelope` â€” don't restate its tables here; egress is the line item
that usually dominates a CDN bill.

## Interface sketch
The contract is mostly **HTTP cache headers** the origin sets and the edge obeys:
- `Cache-Control: public, max-age=31536000, immutable` for fingerprinted static.
- `Cache-Control: public, max-age=60, stale-while-revalidate=600` for stable URLs
  with periodic updates.
- `ETag` / `Last-Modified` to enable cheap revalidation (304 Not Modified).
- `Vary` only on headers you truly serve differently on (a careless `Vary: Cookie`
  destroys hit rate).
- The **cache key**: URL path + an explicit whitelist of query params; decide which
  cookies/headers (if any) are part of it.
Invalidation is a `PURGE`/invalidation API call *or* (preferably) a URL version
bump. Versioned URLs sidestep the purge-propagation race entirely.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the edge â†’ shield â†’ origin pull path (and the dashed cold-miss arrow,
plus geo-routing from clients to the nearest PoP), use the in-plugin
`architecture-diagram` skill. Sketch the edge nodes in the cache color and the
origin in its store color; do not embed Mermaid here.

## Related building blocks
- `caching` â€” *owned-concept lives in*: invalidation, eviction, TTL, and
  thundering-herd theory live there; the CDN is the edge tier *above* the
  app/distributed cache and *alternative to* origin reads for static/media.
- `load-balancing` â€” *owned-concept lives in*: the geo/anycast routing and origin
  health checks that send users to the nearest edge.
- `back-of-the-envelope` â€” *feeds into* this: supplies the egress, offload %, and
  latency-payoff numbers that justify a CDN.
- `data-storage` â€” *depends on*: the object store that is usually the CDN's origin.
- `consistency-coordination` â€” *alternative to* this for data that cannot tolerate
  any staleness window (serve from origin, not a TTL-based edge).
- `system-design` â€” *pairs with* (back-link): the orchestrator that routes here when
  a design serves static/media at geographic scale.

## References
- **`references/deep-dive.md`** â€” cache-key normalization, `Cache-Control` directive
  semantics, push vs pull mechanics, origin shield / tiered topology, invalidation
  vs versioning races, multi-CDN, and media-specific delivery (segmented HLS/DASH,
  range requests, signed URLs). Read when designing the edge layer in detail.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” service mappings, limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Content delivery deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the edge
layer in detail.

## The cache key (where hit rate is won or lost)

The edge caches one object per **cache key**. By default the key is the request
URL, but every extra dimension multiplies the keyspace and shreds hit rate:

- **Query strings:** an unbounded param (tracking IDs, cache-busters) means every
  request is a unique key â€” nothing caches. *Fix:* whitelist the params that truly
  change the response (`?w=400`), ignore the rest, and sort them so `?a=1&b=2` and
  `?b=2&a=1` collapse to one key.
- **Cookies:** including a session cookie in the key gives every user their own
  copy. Strip cookies on static paths; only key on a cookie when content genuinely
  varies by it.
- **`Vary` header:** the origin's `Vary` tells the edge which request headers fork
  the cache. `Vary: Accept-Encoding` (gzip/br) is fine and necessary;
  `Vary: User-Agent` forks the cache thousands of ways â€” avoid. `Vary: Cookie` is
  almost always a mistake on cacheable content.

## Cache-Control directives that matter

The origin controls edge behavior through response headers:

- `max-age=N` â€” fresh for N seconds (browser **and** edge unless overridden).
- `s-maxage=N` â€” edge-specific TTL; lets the edge cache longer than the browser.
- `public` / `private` â€” `private` forbids shared (edge) caching; use for
  per-user responses.
- `no-cache` â€” must revalidate before serving (still may store); `no-store` â€”
  never store. These two, set by accident on a hot asset, send full traffic to
  origin.
- `immutable` â€” the asset never changes for this URL; the browser won't even
  revalidate. Pair with fingerprinted filenames.
- `stale-while-revalidate=N` â€” serve the stale copy for up to N seconds while
  asynchronously refetching. Hides origin latency on refresh and blunts expiry
  stampedes.
- `stale-if-error=N` â€” serve stale on origin error. Cheap resilience.

## Push vs pull mechanics

- **Pull:** edge gets a miss â†’ fetches from origin (or shield) â†’ stores per
  `Cache-Control`/TTL â†’ serves. Redundant re-pulls happen when a TTL expires but
  the object didn't change; conditional requests (`If-None-Match` with `ETag`)
  turn that into a cheap 304 instead of a full transfer.
- **Push:** you upload via the CDN's API/storage and rewrite asset URLs to the CDN
  domain. No cold miss, but you own the upload pipeline, storage cost for cold
  objects, and consistency between your build and what's on the edge.

## Origin shield / tiered caching

Without a shield, a cold object is fetched independently by every edge PoP â€” N
misses, N origin fetches. An **origin shield** is a designated regional cache that
all PoPs pull *through*: the origin sees one fetch per object, not N. It also
absorbs purge/expiry stampedes. Cost: an extra hop on the cold path and a regional
chokepoint â€” make the shield itself redundant if the origin can't take direct load.

## Invalidation vs versioning (the race)

- **Explicit purge:** call the CDN to evict a path/tag. Propagation across global
  PoPs is *not* instant (seconds to minutes); during that window different users
  see different versions. Tag-based purges (evict everything tagged `product:123`)
  scale better than path-by-path.
- **Versioned / fingerprinted URLs:** change the URL when content changes
  (`app.4f9a.js`, `?v=2`). The new URL is a guaranteed miss â†’ always fresh; old
  URLs age out by TTL. No purge, no race. This is the preferred model and the same
  trick `caching` uses with versioned keys â€” see there for the eviction/invalidation
  theory shared with this layer.

## Media-specific delivery

Large media is delivered differently from small static files:

- **Segmented streaming (HLS/DASH):** video is chunked into short segments + a
  manifest. Each segment is a cacheable static object, so a CDN serves video
  without special support; only the manifest is small and short-lived.
- **Byte-range requests** (`Range:` / `206 Partial Content`): enable seeking and
  resumable downloads without refetching the whole file; the edge caches ranges.
- **Signed URLs / signed cookies:** time-limited, tamper-proof tokens authorize
  access to private media at the edge without a per-request origin auth call.
- **On-the-fly transforms** (image resize/format, e.g. AVIF/WebP via `Accept`):
  powerful but each variant is a distinct cache key â€” bound the variant set.

## Multi-CDN

Using two CDN providers behind smart DNS/steering removes the single-CDN SPOF and
lets you route by performance or cost per region. Cost: more operational surface,
split hit rates (each CDN warms independently), and config drift between vendors.
Reach for it only when CDN-level availability or per-region performance genuinely
justifies it.

## Common mistakes

- Cookies or unbounded query params in the cache key â†’ ~0% hit rate, full origin
  load while still paying the CDN.
- One global TTL â†’ synchronized mass expiry stampede (add jitter, use
  `stale-while-revalidate`).
- Relying on purge for freshness instead of versioned URLs (propagation race).
- No origin fallback plan â€” the CDN becomes a hard dependency in front of everything.
- `no-store`/`no-cache` left on a hot asset â†’ silent egress and origin blowup.
- Treating the edge as durable storage; it is a cache and can evict anything anytime.

