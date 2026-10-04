---
name: api-design
description: This skill should be used when the user needs to "design the API", do "endpoint design", pin down a "request/response shape", choose a "pagination" strategy (cursor vs offset), add an "idempotency key" to a write, plan "API versioning", an "error contract", or pick between "REST vs gRPC vs GraphQL" or "WebSocket vs polling". Use it whenever a design has reached the interface â€” the concrete request, response, primary access path, and how clients page, retry, and version â€” even if the user only said "the boxes talk to each other".
---

# API Design

Define the contract between clients and a service: the exact request and response
shapes, how callers page through data, how retried writes stay safe, how errors
are reported, and how the contract evolves. Get this vague and the rest of the
diagram is guesswork (GUIDE #8) â€” a "NoSQL box" or "user service" solves nothing
until you can write the request, the response, and the key it hits.

## When to reach for this
The design has named services and a datastore, and you now need the *interface*:
what a client sends, what it gets back, how it fetches the next page, how it
retries a payment without double-charging, and how a v1 client survives a v2
deploy. Reach here the moment someone says "fetch the feed" or "store the post"
without a shape.

## When NOT to
Before requirements and scale are pinned â€” the protocol choice depends on
read/write ratio and latency target, not taste (â†’ `requirements-scoping`,
`back-of-the-envelope`). Don't reach for gRPC, GraphQL, or streaming because they
sound modern; a plain REST/JSON endpoint is the cheapest contract that meets most
constraints, and naming a fancier protocol you don't need is a YAGNI red flag.
Internal data-access keys and partition design live in `data-storage`; this skill
designs the *external* contract that mirrors them.

## Clarify first
- **Call shape** â€” request/response (CRUD), bidirectional/real-time, or one
  request â†’ many results (streaming)? This picks the protocol.
- **Read/write ratio and result-set size** â€” drives pagination and whether reads
  need their own optimized path (â†’ `back-of-the-envelope`).
- **Retry safety** â€” can a write be safely repeated? Which operations are
  naturally idempotent (PUT/DELETE) vs not (POST that creates/charges)?
- **Client diversity & churn** â€” public third parties (slow to upgrade, need
  strict versioning) vs your own apps (ship together)?
- **Latency & payload budget** â€” mobile/high-latency links favor compact binary
  and fewer round trips; browsers favor cacheable HTTP.

## The options

**Protocol / style** (pick per call shape)
- **REST over HTTP/JSON** â€” resource CRUD over standard verbs. Use as the default
  for public, cacheable, browser-friendly APIs.
- **RPC / gRPC (HTTP/2, protobuf)** â€” typed method calls, compact binary,
  streaming. Use for internal service-to-service traffic where latency and schema
  contracts matter.
- **GraphQL** â€” client specifies exactly the fields it wants in one query. Use
  when many clients need different shapes of the same graph and over/under-fetching
  on REST hurts.
- **WebSocket / SSE (streaming)** â€” persistent serverâ†’client push. Use when the
  server must push updates (chat, presence, live feeds) â€” see the polling tier below.
- **Webhooks** â€” server calls *the client's* URL on an event. Use for async,
  third-party event delivery.

**Server-push tier** (when clients need fresh data)
- **Polling** â†’ **long-polling** â†’ **SSE** â†’ **WebSocket**, in increasing
  efficiency for push and increasing connection cost. Start at polling; escalate
  only when a number (update frequency, fanout) forces it.

**Pagination**
- **Cursor (keyset)** â€” opaque token over a stable sort key. Default for large or
  changing datasets.
- **Offset/limit** â€” `?offset=40&limit=20`. Use only for small, mostly-static,
  jump-to-page lists.

**Idempotency** â€” client sends an `Idempotency-Key` on unsafe writes; the server
dedupes retries. This skill owns the key contract (see Interface sketch).

**Versioning** â€” URI (`/v2/...`), header (`Accept: application/vnd.x.v2+json`), or
additive/never-break. Prefer additive; reserve a new version for breaking changes.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| REST/JSON | Universal, cacheable, simple, tooling everywhere | Over/under-fetch; chatty for graphs; weak typing | Field-shaping pain â†’ GraphQL; internal latency â†’ gRPC |
| gRPC/RPC | Compact, typed, fast, native streaming | Not browser-native; needs proxy; opaque to HTTP caches | Public/browser clients need it â†’ REST gateway |
| GraphQL | One round trip, client picks fields | Caching/rate-limiting hard; expensive queries (N+1); server complexity | Few fixed shapes (REST simpler) or query cost unbounded |
| WebSocket/SSE | True server push, low-latency updates | Stateful connections, harder to scale/LB, reconnection logic | Updates are infrequent â†’ long-poll; one-way only â†’ SSE |
| Cursor pagination | Stable under inserts; O(1) per page at any depth | Opaque token; no random page jump; needs sort key | Users must jump to page N of a static set â†’ offset |
| Offset pagination | Trivial; arbitrary page jumps | Drift/dupes on insert; deep offsets scan & slow | Set grows or mutates â†’ cursor |
| Idempotency keys | Safe retries; no double-charge | Server must store keys + dedupe; key TTL/scope to define | Op is naturally idempotent (PUT/DELETE) â†’ may skip |
| URI versioning | Explicit, cache/log-visible, easy to route | Version sprawl; clients pinned forever | Changes are additive â†’ no new version needed |

## Behavior under stress
The contract decides how badly a client *amplifies* an incident.

- **Retry storms.** A timed-out write that isn't idempotent gets retried and may
  double-execute; clients retrying in lockstep stampede a recovering service.
  Idempotency keys make retries safe; the backoff/jitter that *paces* them is owned
  by `resilience-failure`. Surface `429` + `Retry-After` so well-behaved clients slow down.
- **Deep pagination.** Offset pagination at large offsets forces the store to scan
  and discard rows â€” a cheap-looking endpoint becomes a full-table scan under a
  crawler. Cursor pagination keeps every page O(page-size).
- **Unbounded responses.** No default page size, no max payload, or a GraphQL query
  that fans out â†’ one request exhausts memory/CPU. Cap page size, depth, and
  complexity at the contract.
- **Connection exhaustion.** WebSocket/SSE hold a connection per client; a
  reconnect storm after a deploy can exhaust file descriptors and load-balancer
  slots. Plan reconnect with jitter and connection limits.
- **Versioning breakage.** A non-additive change to a shared shape breaks every
  client at once â€” the loudest self-inflicted outage. Make changes additive;
  deprecate behind a version.

**Monitor:** error-rate by status class (4xx vs 5xx), p99 latency per endpoint,
retry/idempotency-replay rate, page-depth distribution, open connection count, and
per-version traffic (to know when an old version can be retired).

## How to apply
1. **Clarify the inputs.** Pin call shape, read/write ratio, result-set size,
   retry safety, client diversity, and latency/payload budget (see *Clarify
   first*). No contract before these are known.
2. **Pick the protocol and pagination from the trade-off table.** Default to
   REST/JSON; escalate to gRPC (internal latency/typing), GraphQL (many field
   shapes), or a push tier (server must push) only when an input forces it.
   Default pagination to cursor; reserve offset for small, static, jump-to-page sets.
3. **Set the key knobs.** Choose idempotent verbs by safety (GET/PUT/DELETE safe
   to retry, POST not), define the `Idempotency-Key` contract and its TTL, fix a
   stable error envelope, and pick a versioning policy (additive by default).
4. **Stress-test the contract.** Cap default and max page size, GraphQL
   depth/complexity, and payload size; plan reconnect-with-jitter and connection
   limits for push; surface `429` + `Retry-After`. Confirm a v1 client survives a
   v2 deploy.
5. **Size it with numbers.** Estimate requests/s per endpoint, response size,
   pages-per-session, and update-frequency Ã— fanout; use these to confirm the
   protocol and poll-vs-push choice (â†’ `back-of-the-envelope`).
6. **Pick a provider.** Keep the generic recipe unless the user names a cloud,
   then map to its managed gateway (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Default to REST/JSON and cursor pagination; escalate only when a number forces it.
- Choose verbs by retry safety so retries are correct by construction.
- Require an `Idempotency-Key` on every non-idempotent write and bound its TTL.
- Cap page size, query depth/complexity, and payload so worst-case cost is bounded.
- Keep one stable error envelope (code, message, request_id, retryable) across every endpoint.

**Don't**
- Reach for gRPC, GraphQL, or streaming because they sound modern (YAGNI red flag).
- Use offset pagination on growing or mutating sets â€” deep offsets scan the store.
- Ship a non-additive change to a shared shape without a new version.
- Leave responses unbounded (no default page size, no max payload).
- Re-teach retries/backoff or sharding here â€” link to `resilience-failure` / `data-storage`.

## Numbers that matter
Estimate before choosing: requests/s per endpoint, average and max response size,
page size Ã— pages-per-session (drives read load), and update frequency Ã— fanout
(decides poll vs push). A few rules of thumb that flip a decision: a binary
protocol (protobuf) commonly cuts payload several-fold over JSON, and compression
helps again before the wire â€” both matter most on mobile/high-latency links where
round trips dominate. Polling at interval `T` for `N` clients is `N/T` requests/s
of mostly-empty answers; once that approaches the push tier's connection budget,
switch to SSE/WebSocket. Cap page size (and GraphQL depth/complexity) so worst-case
response cost is bounded, and keep an idempotency key's stored window bounded
(e.g. 24h) so the dedupe table doesn't grow without limit. For the canonical
latency/QPS/payload reference figures, go to `back-of-the-envelope` â€” don't restate
its tables here.

## Interface sketch
Make the contract concrete. A read with cursor pagination and an error envelope:

```
GET /v1/users/{id}/posts?limit=20&cursor=eyJ0cyI6MTciLCJpZCI6Ijk5In0
200 OK
{ "data": [ { "id": "p_881", "created_at": "...", "text": "..." } ],
  "next_cursor": "eyJ0cyI6...",          // null when no more pages
  "has_more": true }

# error envelope â€” stable shape across every endpoint
4xx/5xx
{ "error": { "code": "rate_limited", "message": "â€¦", "request_id": "req_â€¦",
             "retryable": true } }
```

An idempotent write (this skill's owned contract):

```
POST /v1/payments
Idempotency-Key: 9f1c-â€¦ (client-generated UUID, unique per logical operation)
{ "amount": 4200, "currency": "usd", "source": "card_â€¦" }

# Server: first request with a key â†’ execute, store (key â†’ response) for a TTL.
# Retry with same key â†’ return the stored response, do NOT re-execute.
# Same key + different body â†’ 422 (key reuse conflict).
```

Mirror the response shape to the access pattern: cursor encodes the partition/sort
key the store pages on (PK/SK design is owned by `data-storage`). Pick verbs by
safety â€” GET (safe), PUT/DELETE (idempotent), POST (not), so retries are correct
by construction.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the request/response path, the cursor-paging loop, or an
idempotent-retry sequence (client â†’ gateway â†’ service â†’ store, with the replay
branch), use the in-plugin `architecture-diagram` skill â€” do not embed Mermaid
here. A one-line ASCII sketch inline is fine for quick reasoning.

## Related building blocks
- `data-storage` â€” *depends on* it: the request/response and cursor shapes mirror its primary key and access patterns (sharding/partitioning lives there); design them together.
- `resilience-failure` â€” *pairs with* it: it owns retries/backoff/jitter, timeouts, and rate limiting, while idempotency keys (owned here) are what make those retries safe.
- `consistency-coordination` â€” *pairs with* it when a retried or concurrent write must not violate an invariant; CAP/quorum theory lives there.
- `messaging-streaming` â€” *alternative to* synchronous request/response when the contract is async events or webhooks.
- `system-design` â€” *feeds into* this: the orchestrator routes here at the interface step.

## References
- **`references/deep-dive.md`** â€” protocol mechanics (HTTP verbs/status discipline, gRPC streaming modes, GraphQL query-cost limits), cursor-token construction, the full idempotency-key state machine, versioning/deprecation strategy, and error-contract design. Read when designing the contract in detail.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” API-gateway / managed-endpoint mappings, limits that change a decision, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# API design deep-dive

Mechanics that would bloat SKILL.md. Read when designing the contract in detail.

## HTTP verb & status discipline (the REST contract)

The verb encodes retry safety; the status encodes the outcome. Get these wrong
and clients can't retry correctly.

- **GET** â€” safe, idempotent, cacheable. Never mutate state in a GET.
- **PUT** â€” idempotent replace; repeating it lands the same final state.
- **PATCH** â€” partial update; *not* guaranteed idempotent (depends on the patch).
- **DELETE** â€” idempotent (deleting twice = still deleted).
- **POST** â€” neither safe nor idempotent; this is the verb that *needs* an
  idempotency key (creates, charges, sends).

Status classes clients branch on: **2xx** success; **4xx** client error (don't
retry as-is â€” fix the request); **409** conflict; **422** validation;
**429** rate-limited (retry after backoff); **5xx** server error (retryable with
backoff). The split between "retryable" (5xx, 429) and "don't bother" (most 4xx)
is what lets a client retry without making things worse.

## Cursor (keyset) pagination mechanics

A cursor is an **opaque, encoded position** in a stable sort order â€” not a page
number. Construct it from the columns the query sorts on so the next page is a
range scan, not an offset scan:

```
-- page 1
SELECT ... WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT 20;
-- cursor encodes the last row's (created_at, id)
-- page 2
SELECT ... WHERE user_id = ?
  AND (created_at, id) < (:cursor_ts, :cursor_id)
  ORDER BY created_at DESC, id DESC LIMIT 20;
```

Rules: include a **tiebreaker** (a unique id) in the sort so rows with equal
timestamps don't get skipped or duplicated; **base64url-encode** the cursor and
treat it as opaque so you can change its internals later; sign or version it if
clients shouldn't forge positions. Cursor pagination is stable under inserts
(new rows appear at the head, not shifting your window) and stays O(page-size) at
any depth â€” the reason it beats offset for feeds and logs. Its cost: no "jump to
page N" and no total count without a separate query.

Offset pagination (`LIMIT n OFFSET m`) is fine for small static lists, but at
large `m` the store scans and discards `m` rows per page, and concurrent inserts
shift every row so pages drift (duplicates/skips). Don't expose deep offsets on a
mutable, growing dataset.

## Idempotency-key state machine (owned contract)

The key turns "did my retried POST run twice?" into a guarantee. The server keeps
a table keyed by `(idempotency_key, scope)`:

1. **Request arrives with key.** Atomically insert the key in a `pending` state.
   - Insert succeeds â†’ this is the first attempt; proceed to execute.
   - Insert fails (key exists) â†’ a retry. If the stored entry is `complete`,
     return the **stored response** verbatim; if still `pending`, the original is
     in-flight â†’ return `409` (or block/poll briefly).
2. **On completion**, store the response (status + body) against the key, mark
   `complete`, set a TTL (e.g. 24h â€” long enough to cover client retry windows,
   short enough to bound the table).
3. **Same key, different request body** â†’ reject `422`: a key identifies one
   logical operation; reusing it for a different payload is a client bug.

Scope the key to the authenticated caller (and often the endpoint) so two clients
can't collide. Persist the key+response in a store that survives the write
(transactional with the side effect where possible) â€” otherwise a crash between
"did the work" and "saved the key" reopens the double-execution window. This is
why naturally idempotent verbs (PUT/DELETE) often don't need a key at all. For the
*retry/backoff/jitter* that drives clients to resend, and for distributed locks
guarding the critical section, see `resilience-failure` and
`consistency-coordination`.

## Versioning & deprecation

- **Additive, non-breaking changes** (new optional fields, new endpoints) need no
  version bump â€” clients ignore unknown fields. Make this the norm.
- **Breaking changes** (remove/rename a field, change a type, tighten validation)
  require a new version. Carriers: **URI** (`/v2/â€¦`, explicit and cache/log
  visible, most common), **header/media-type** (`Accept: â€¦v2+json`, cleaner URLs,
  harder to debug), or **query param** (`?version=2`, easy but easy to forget).
- **Deprecation lifecycle:** announce â†’ emit a `Deprecation`/`Sunset` header and
  log usage â†’ monitor per-version traffic â†’ retire only when the old version's
  traffic is near zero. Never delete a version while clients still call it.

Tolerant readers (ignore unknown fields, don't depend on field order) extend the
life of a single version and are the cheapest forward-compat insurance.

## Protocol mechanics

- **gRPC streaming modes:** unary (1â†”1), server-streaming (1 req â†’ many resp),
  client-streaming (many req â†’ 1 resp), bidirectional. Built on HTTP/2 multiplexed
  streams; protobuf gives a typed, compact, versioned schema (add fields with new
  tag numbers; never reuse a tag). Needs a proxy (e.g. grpc-web/gateway) to reach
  browsers.
- **GraphQL query cost:** a single query can fan out (N+1 resolvers, deep nesting).
  Defend with **depth limits**, **complexity/cost scoring**, **persisted queries**
  (allowlist), and per-resolver batching (dataloader). Caching is harder than REST
  because every query URL is unique â€” cache at the resolver/entity level.
- **Server-push ladder:** polling (simple, wasteful), long-polling (hold the
  request until data or timeout), SSE (one-way serverâ†’client over a single HTTP
  stream, auto-reconnect), WebSocket (full-duplex, stateful). Escalate only when
  update frequency/fanout justify the connection cost; the push-vs-poll line is in
  SKILL.md's stress section.

## Error contract design

Return **one error envelope shape across every endpoint** so clients write one
parser: a machine-readable `code` (stable string, not a sentence), a human
`message`, a `request_id` for support/correlation, and an explicit `retryable`
flag. Keep `code` stable across versions â€” clients branch on it. Don't leak stack
traces or internal identifiers. Map domain errors to the right status class so the
retry behavior above is correct.

## Common mistakes

- Mutating state in a GET (breaks caches and safe-retry assumptions).
- Offset pagination on a growing/mutable set (drift, deep-scan slowdowns).
- POST that creates/charges with no idempotency key (double-execution on retry).
- Breaking a shared response shape in place instead of versioning additively.
- No default/max page size, depth, or complexity limit (one request OOMs the box).
- Inconsistent error shapes per endpoint (every client needs a special case).
- Treating WebSocket like stateless HTTP (forgetting reconnect storms and per-
  connection memory).

