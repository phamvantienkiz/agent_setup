---
name: load-balancing
description: This skill should be used when the user adds a "load balancer", asks about "L4 vs L7" (transport vs application layer), picks a balancing algorithm ("round robin", "least connections", "weighted", "IP hash"), configures "health checks", needs "sticky sessions" / "session affinity", adds a "reverse proxy", does "SSL/TLS termination", spreads "traffic distribution" across an "autoscaling group", or wants a stateless web tier behind a single entry point. Use it whenever a design has more than one server behind one address, or a single box is the entry-point bottleneck or SPOF, even if the user doesn't say "load balancer".
---

# Load Balancing

Spread incoming requests across a pool of identical backends so no single server
is the bottleneck or the single point of failure. Get it wrong and the balancer
becomes the SPOF it was meant to remove, routes traffic to dead servers, or
*amplifies* an outage by hammering a backend that is already on its knees.

## When to reach for this
Reach for a balancer when more than one backend serves the same role and traffic
must be split across them; when a single entry point is a SPOF to eliminate; to
add or remove servers without clients noticing (the enabler for the stateless tier
and autoscaling); or to put one public address in front of a private fleet, with
TLS termination, health-gating, and routing in one place.

## When NOT to
One backend that comfortably handles peak load needs no balancer yet â€” adding one
is a new component, a new failure mode, and a new thing to operate (YAGNI). If the
real bottleneck is the database or a single hot shard, a balancer in front of the
web tier solves nothing; diagnose the actual constraint first (â†’ `back-of-the-envelope`).
Cross-region traffic steering is usually DNS/anycast at the edge, not an L4/L7
balancer (â†’ `content-delivery`). Per-client request limiting is a policy concern
owned by `resilience-failure`, not the balancing algorithm.

## Clarify first
- **Protocol & layer need** â€” raw TCP/UDP throughput (L4) or HTTP-aware routing by
  path/host/header/cookie (L7)? This picks the balancer type.
- **State** â€” is the backend stateless, or does a session live on one server
  (forcing affinity)? Moving state out is almost always the better answer.
- **Peak QPS & connection count** â€” one fat connection stream or many short
  requests? Drives algorithm and balancer sizing (â†’ `back-of-the-envelope`).
- **Health signal** â€” what does "healthy" mean (TCP accept? a `/healthz` 200? a
  deep dependency check?) and how fast must a dead node leave the pool?
- **TLS** â€” terminate at the balancer (offload backends, inspect L7) or pass
  through end-to-end (compliance/mTLS)?

## The options

**Layer of inspection**
- **L4 (transport):** route by IP/port; forward packets via NAT or DSR without
  reading payload. Use when you need raw throughput, non-HTTP protocols, or the
  lowest added latency.
- **L7 (application):** terminate the connection, read HTTP (host, path, headers,
  cookies), then route. Use when you need content-based routing, per-route pools,
  TLS termination, or request rewriting.

**Distribution algorithm**
- **Round robin / weighted round robin:** even rotation, weighted by capacity.
  Use for uniform, stateless backends.
- **Least connections / least response time:** send to the least-busy node. Use
  when request cost varies widely (long-lived connections, mixed workloads).
- **IP hash / consistent hash:** map a client (or key) to a stable backend. Use
  for affinity without server-side session storage, or to keep cache locality.
- **Random (two-choices):** pick two at random, take the lighter â€” cheap and
  surprisingly even at scale.

**Topology**
- **Active-passive:** one balancer serves, a standby takes the VIP on failure.
  Simple HA.
- **Active-active:** multiple balancers share load (via DNS or anycast). Removes
  the balancer's own SPOF and adds headroom.

**Reverse proxy role:** an L7 balancer is also a reverse proxy â€” one public face
that hides backends, terminates TLS, compresses, caches, and centralizes routing.
A reverse proxy is worth it even with a single backend for those benefits;
load balancing is the multi-backend case of the same component.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| L4 balancing | Max throughput, low latency, any protocol | Blind to content; no path/header routing, no TLS inspection | You need content-based routing or TLS termination â†’ L7 |
| L7 balancing | Content routing, TLS offload, rewrites, observability | Higher latency/CPU; terminates connections (more state) | Raw throughput dominates and routing is trivial â†’ L4 |
| Round robin | Dead simple, even for uniform work | Ignores actual load; a slow node still gets its share | Request costs vary a lot â†’ least-connections |
| Least connections | Adapts to uneven request cost | Needs live connection state; can herd onto a just-recovered node | Backends are uniform â†’ round robin is enough |
| IP/consistent hash | Affinity & cache locality without session store | Uneven spread; rebalances on pool change | You can externalize state â†’ round robin + shared store |
| Sticky sessions | Works with stateful backends today | Breaks even spread, complicates scale-in, loses session on node death | State can move to Redis/DB â†’ drop affinity |
| Active-passive | Simple HA for the balancer | Idle standby; failover gap (seconds) | You need zero-gap headroom â†’ active-active |

## Behavior under stress
The balancer sits in the request path of *everything*, so its failure modes are
the whole system's failure modes.

- **Health-check stampede (the classic foot-gun):** a backend recovers, the
  balancer marks it healthy, and the full firehose hits a single cold node â€” empty
  caches, cold JIT, full connection backlog â€” so it fails its next health check
  and drops out, oscillating (flapping). Aggressive checks can effectively *DDoS a
  recovering service*. Mitigate with **slow-start / connection ramping**, generous
  failure thresholds (N strikes before eviction, M before re-admission), check
  jitter, and a circuit breaker on the dependency path (â†’ `resilience-failure`).
- **Retry amplification:** the balancer (or clients) retries failed requests onto
  the *remaining* healthy nodes, so losing one node can cascade as the survivors
  absorb its load plus the retries. Cap retries; use backoff with jitter (owned by
  `resilience-failure`).
- **Uneven load / hot backend:** long-lived connections or sticky sessions pin
  load to a few nodes; round robin can't see it. Watch per-backend utilization,
  not just the aggregate.
- **Balancer as SPOF:** a single balancer failing takes everything down. Run it
  active-active or active-passive with a fast VIP/anycast failover.
- **Thundering reconnect:** if the balancer restarts, every client reconnects at
  once. Stagger draining and connection limits.

**Monitor:** per-backend request rate and latency (p99), healthy-host count,
health-check pass/fail and flap rate, connection counts, 5xx rate at the balancer
vs. at backends (divergence localizes the fault), and active connection
distribution.

## How to apply
1. **Clarify the inputs** â€” answer the *Clarify first* questions: protocol/layer,
   whether the backend is stateless, peak QPS and connection count, what "healthy"
   means, and the TLS posture. These pin every later choice.
2. **Pick the layer and algorithm from the trade-off table** â€” choose L4 for raw
   throughput/non-HTTP, L7 for content routing or TLS offload. Default to round
   robin for uniform stateless backends; reach for least-connections only when
   request cost varies, and hash-based affinity only when state can't move yet.
3. **Set the key knobs** â€” write the health check concretely (method, path,
   expected code, interval, fail/recover thresholds) and the pool's drain delay;
   enable slow-start so a recovering node ramps instead of taking the firehose.
4. **Stress-test the choice** â€” walk the failure modes: health-check stampede,
   retry amplification, hot backend, and the balancer as SPOF. Add active-active
   (or active-passive with fast VIP/anycast failover) so the balancer is not the
   new single point of failure.
5. **Size with numbers** â€” confirm the balancer handles peak QPS and concurrent
   connections, and verify the *backend* fleet (not the balancer) is the binding
   constraint. Pull per-server QPS and connection-memory figures from
   `back-of-the-envelope`.
6. **Pick a provider** â€” default to the generic recipe; if a cloud is named, read
   its provider file for the managed-service mapping and limits.

## Dos and don'ts
**Do**
- Push session state into a shared store so plain round robin and autoscaling work.
- Define health checks explicitly and choose shallow-vs-deep on purpose.
- Run the balancer active-active or active-passive so it is not a SPOF.
- Enable slow-start and generous fail/recover thresholds to stop flapping.
- Watch per-backend utilization, not just the aggregate, to catch hot nodes.

**Don't**
- Don't add a balancer for a single backend that handles peak (YAGNI) â€” a reverse
  proxy may still be worth it, but multi-backend balancing is not.
- Don't let a deep health check on a slow dependency evict the whole fleet at once.
- Don't reach for sticky sessions when the state can move out of the box.
- Don't retry blindly into the surviving nodes; cap retries and use backoff/jitter.
- Don't assume the balancer is the bottleneck before confirming the backend fleet is.

## Numbers that matter
A modern software balancer (HAProxy/Nginx/Envoy) handles tens of thousands of
requests/sec and many thousands of concurrent connections per instance â€” usually
well above a single web/app node, so it is rarely the first bottleneck. Size it
against peak QPS and concurrent connections, and confirm the *backend* fleet (not
the balancer) is the binding constraint. Per-server QPS rates, connection-memory
cost, and peak-factor math live in `back-of-the-envelope` â€” don't restate them
here; pull the figures from there to size the pool and the balancer.

## Interface sketch
Load balancing has no request/response contract of its own, but two configs are
load-bearing and worth writing down concretely:
- **Health check:** method + path + expected code + interval + thresholds, e.g.
  `GET /healthz â†’ 200, every 5s, unhealthy after 3 fails, healthy after 2 passes`.
  Make `/healthz` shallow (process alive) vs. deep (checks DB) deliberately â€” a
  deep check that fails on a slow dependency can evict the whole fleet at once.
- **Backend pool / target group:** the set of `host:port` targets, weights, and
  the drain/deregistration delay used on scale-in so in-flight requests finish.

## How load balancing enables the stateless tier
Spreading requests freely across interchangeable servers only works if any server
can serve any request â€” i.e. no session state lives on the box. Push session/state
into a shared store (Redis/DB) so the balancer can use plain round robin, add or
remove nodes at will, and let an autoscaling group grow/shrink the pool. Sticky
sessions are the fallback when state *can't* move yet, at the cost of even spread
and easy scale-in. The horizontal-scale and stateless-tier story is owned by
`scaling-evolution`; this skill is the mechanism that makes it routable.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the request path (client â†’ balancer â†’ backend pool) or the
health-check/failover flow, use the in-plugin `architecture-diagram` skill. A
quick inline sketch â€” `client â†’ [LB] â†’ {web1, web2, web3} â†’ shared state` â€” is
fine for reasoning; do not embed Mermaid.

## Related building blocks
- `scaling-evolution` â€” *feeds into* this: it owns the stateless tier and
  horizontal vs. vertical scaling, and this skill is the routing mechanism that
  makes that fleet addressable.
- `resilience-failure` â€” *pairs with* this whenever the balancer can amplify an
  outage; *owned-concept lives in* it â€” retries/backoff/jitter, circuit breakers,
  failover, and rate limiting are the cure for health-check stampedes and retry storms.
- `content-delivery` â€” *alternative to* this for cross-region traffic: when
  "balancing" is really steering users to the nearest region, geo/DNS/anycast at
  the edge (owned there) is the right tool, not an L4/L7 balancer.
- `back-of-the-envelope` â€” *depends on* it for the QPS, connection, and
  peak-factor numbers that size the pool and the balancer.
- `system-design` â€” the orchestrator that routes here when a design grows past one
  server.

## References
- **`references/deep-dive.md`** â€” L4 NAT vs. DSR, how L7 termination works, the
  algorithm internals (incl. consistent hashing for affinity), health-check tuning
  and slow-start, connection draining, TLS termination vs. passthrough. Read when
  configuring a balancer in detail.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” service mappings, limits,
  and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Load balancing deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when configuring a
balancer in detail.

## L4 forwarding: NAT vs. DSR

An L4 balancer never reads the payload; it forwards packets by IP/port.

- **NAT (network address translation):** the balancer rewrites the destination
  (and on the way back, the source) so both directions traverse it. Simple, but
  the balancer is in the return path too â€” return traffic (often the larger half)
  flows back through it, capping throughput.
- **DSR (direct server return):** the backend replies straight to the client,
  bypassing the balancer on egress. The balancer only handles inbound, so it
  scales much further for response-heavy workloads (video, downloads). Costs more
  setup (loopback VIP on backends, L2 adjacency or tunneling) and loses
  return-path visibility.

L4 keeps the client's TCP connection essentially end-to-end, so it adds minimal
latency and works for any protocol (gRPC streams, databases, custom TCP/UDP).

## L7 termination: how it actually routes

An L7 balancer is a **full proxy**: it terminates the client's TCP/TLS
connection, parses the HTTP request, makes a routing decision, then opens (or
reuses, via a connection pool) a *separate* connection to the chosen backend.
Two connections, two congestion windows. This is what enables:

- **Content routing:** by `Host`, path prefix, header, method, or cookie â€” e.g.
  `/api/*` to the API pool, `/static/*` to a cache tier, video hosts to media
  servers, billing to hardened nodes.
- **Request manipulation:** header injection (`X-Forwarded-For`, request IDs),
  rewrites, redirects, compression.
- **Backend connection pooling / multiplexing:** many short client connections
  reuse a small pool of warm backend connections (huge win for HTTP/2, gRPC).

Cost: per-request CPU (parsing, TLS), added latency, and the balancer now holds
connection state â€” making *it* more stateful and its memory a sizing concern.

## Distribution algorithms in detail

- **Round robin:** rotate through the pool. **Weighted** assigns more turns to
  bigger nodes. Blind to actual load â€” a node stuck on slow requests still gets
  its share.
- **Least connections:** route to the fewest active connections; **least response
  time** also factors latency. Best when request cost is uneven (mixed or
  long-lived connections). Requires the balancer to track live state; a
  just-added node looks idle and can get *flooded* â€” pair with slow-start.
- **Power of two choices:** sample two backends at random, pick the less loaded.
  Near-optimal balance with O(1) state and no global coordination â€” the default
  in many modern proxies.
- **Hash-based (IP hash / header hash):** deterministic clientâ†’backend mapping for
  affinity without a session store. Plain modulo hashing remaps almost everything
  when the pool changes; **consistent hashing** moves only ~K/N keys on a pool
  change, preserving most affinity and cache locality. The full consistent-hashing
  mechanics (rings, virtual nodes) are owned by `consistency-coordination` â€” use
  it here purely as the "affinity that survives scaling" tool.

## Health checks (the part people get wrong)

- **Active checks:** the balancer probes each backend (`GET /healthz`, a TCP
  connect, or gRPC health RPC) on an interval. **Passive checks** observe real
  traffic and eject a node after N consecutive errors.
- **Shallow vs. deep:** a shallow check (process accepts a connection / returns
  200 from a trivial handler) tests "is the box up." A deep check (verifies DB,
  cache, downstream) tests "can it serve" â€” but if the shared dependency hiccups,
  *every* backend fails the deep check simultaneously and the whole pool is
  evicted, turning a slow dependency into a total outage. Prefer shallow liveness
  for pool membership; handle dependency failure with degradation in the app
  (â†’ `resilience-failure`).
- **Thresholds & jitter:** require multiple consecutive fails before eviction and
  multiple passes before re-admission (anti-flap). Jitter the interval so checks
  don't synchronize into a probe storm.

## Slow-start / connection ramping (anti-stampede)

When a node (re)joins, ramp its share from near-zero up over a warm-up window
instead of handing it a full load instantly. This lets caches fill, JITs warm,
and connection pools build before peak traffic arrives â€” directly preventing the
recoverâ†’overloadâ†’dropâ†’recover oscillation. Combine with least-connections-aware
weighting so a "0 connections" fresh node isn't treated as the most attractive
target.

## Connection draining (graceful scale-in / deploy)

On deregistering a node (scale-in, deploy, scale to a smaller instance), stop
sending it *new* connections but let in-flight requests finish for a drain
timeout before terminating. Without draining, every deploy or scale event drops
live requests. Set the drain window to cover your slowest reasonable request.

## TLS termination vs. passthrough

- **Termination at the balancer:** decrypt once at the edge; backends speak plain
  HTTP. Offloads CPU, centralizes certs, and is *required* for L7 content routing
  (you can't route on a path you can't read). Re-encrypt to backends (mTLS in the
  mesh) if the internal hop must stay encrypted.
- **Passthrough (TCP/L4):** the balancer forwards encrypted bytes; the backend
  terminates TLS. Needed for end-to-end encryption or client-cert auth that must
  reach the app. Loses L7 routing and inspection.

## Common mistakes

- One balancer, no standby â€” the balancer is now the SPOF it was meant to remove.
- Deep health checks that evict the whole fleet when a shared dependency blips.
- No slow-start â†’ recovered nodes get firehosed and flap.
- No connection draining â†’ every deploy drops in-flight requests.
- Sticky sessions used as a crutch instead of externalizing state, then scale-in
  drops live sessions.
- Unbounded retries at the balancer amplifying load onto survivors (cap + backoff;
  â†’ `resilience-failure`).
- Treating cross-region steering as an L4/L7 problem instead of DNS/anycast/CDN
  (â†’ `content-delivery`).

