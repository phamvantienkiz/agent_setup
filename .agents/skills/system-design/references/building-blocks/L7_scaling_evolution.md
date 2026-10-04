---
name: scaling-evolution
description: This skill should be used when the user asks "how does this scale", "scale to millions", "scaling roadmap", "where is the bottleneck", "what breaks first", "10x growth", "vertical vs horizontal scaling", "scale from zero", or "what's the next scale curve". It gives the order-of-magnitude evolution path (single server â†’ tiers â†’ replicas â†’ cache â†’ CDN â†’ stateless tier â†’ multi-region â†’ sharding) and a way to diagnose the *next* bottleneck instead of memorizing one big diagram. Use it whenever a design must grow by orders of magnitude or a load increase is on the table, even if the user doesn't say "scaling".
---

# Scaling Evolution

Grow a design one bottleneck at a time. A system that serves 1k users and one
that serves 10M users are different architectures, but you do not jump between
them â€” you walk a path where each step removes the *current* ceiling and exposes
the next. Getting this wrong means either over-building day one (paying multi-
region complexity for 1k users) or freezing when load doubles because the design
was a memorized end-state, not a sequence of justified moves (GUIDE #7).

## When to reach for this
A load increase is on the table ("what if traffic 10Ã—?", "scale to millions"),
the user asks where the bottleneck is or what breaks first, or a single-box
design has outgrown one machine. Reach here to sequence the next two or three
moves â€” never the whole roadmap at once.

## When NOT to
Do not pre-build steps the numbers do not yet demand (YAGNI). Sharding,
multi-region, and a message queue are *late* moves; proposing them for a system
that fits on two boxes is the over-indexing this skill defends against. If the
current load fits comfortably on a vertically-scaled box with a replica, stop â€”
that is the cheapest design that meets the constraint, and it wins. Naming the
next five tiers when only one is needed is a red flag, not foresight.

## Clarify first
The path is driven entirely by numbers and constraints, so pin these down before
moving (most come from `requirements-scoping` and `back-of-the-envelope`):
- **Current and target scale** â€” today's QPS/data and the multiple you must hit
  (2Ã—? 100Ã—?). The multiple decides how many steps you take now.
- **Read:write ratio** â€” read-heavy systems scale with replicas + cache; write-
  heavy systems hit the master/storage ceiling and need sharding far sooner.
- **Where it hurts now** â€” is the *symptom* compute (CPU saturated), storage
  (DB/disk saturated), or network (bandwidth/connections)? Diagnose before adding.
- **Consistency and staleness budget** â€” replicas and multi-region trade freshness
  for scale; if reads must be current, that constrains the path (â†’ `consistency-coordination`).
- **State** â€” is anything pinned to a server (sessions, local files)? Stateful
  tiers block horizontal scaling.

## The method: walk the bottleneck ladder
Each rung removes one ceiling. Apply the **next** rung the numbers justify, not
the whole ladder. Full triggers and worked thresholds are in
`references/scaling-ladder.md`.

1. **Single server.** Web, app, DB, cache on one box. Correct for low traffic and
   early validation. *Breaks when* one machine can't hold the load or the data.
2. **Split the tiers.** Move the database (and later cache) onto its own host so
   web and data scale independently. *Breaks when* the single web box or single DB
   saturates, or either becomes a single point of failure.
3. **Vertical scale + replicate for reads.** First scale *up* (bigger box â€” simple,
   no app changes) until the hard limit or cost knee. Add read replicas to spread
   reads off the primary (â†’ `data-storage` owns replication). *Breaks when* writes
   saturate the primary, or replica lag breaks freshness.
4. **Add a cache.** Put hot reads in front of the DB once a number shows reads
   dominate (â†’ `caching`). Highest-leverage move for read-heavy systems. *Breaks
   when* writes are the bottleneck, or the working set no longer fits.
5. **Push static/edge to a CDN.** Offload images/JS/CSS/video to edge servers
   close to users (â†’ `content-delivery`). *Breaks when* the bottleneck is dynamic
   requests, not static assets.
6. **Make the web tier stateless + load-balance.** Move session/state to a shared
   store so any request hits any server; put a load balancer in front and
   autoscale the fleet (â†’ `load-balancing`). This is the unlock for cheap
   horizontal scale. *Breaks when* the data tier (now the bottleneck) can't keep up.
7. **Decouple with async.** Move slow/bursty work (uploads, encoding, fan-out)
   behind a queue so producers and consumers scale independently and spikes are
   absorbed (â†’ `messaging-streaming`). *Breaks when* even the sync path or storage
   is the limit.
8. **Multi-DC / multi-region.** Geo-route users to the nearest healthy data center
   for latency and disaster survival; replicate across regions. *Breaks when*
   cross-region data sync, conflict resolution, or a single dataset too big for one
   region forces the last rung.
9. **Shard the data tier.** Partition data across nodes when one primary can no
   longer hold the writes/data (â†’ `data-storage` owns sharding/partitioning;
   `consistency-coordination` owns consistent hashing). The most complex move â€”
   last, not first.

Vertical scaling (scale *up*: more CPU/RAM) is the cheap early move with no app
changes but a hard ceiling and no redundancy. Horizontal scaling (scale *out*:
more boxes) is the durable answer â€” better availability, near-unlimited headroom â€”
but demands statelessness and adds coordination cost. Climb vertically until the
knee, then go horizontal.

## Diagnose the bottleneck before adding anything
"Add more servers" without a diagnosis is guessing (GUIDE #3, #7). Classify the
pressure first, then act on *that* resource:
- **Compute-bound** (CPU/threads pegged, latency rises with request rate): add app
  servers / autoscale; check for an O(n) hot path before buying hardware.
- **Storage-bound** (DB CPU/IO pegged, slow queries, replica lag growing): add
  read replicas, cache, then shard. Adding web servers here makes it *worse* â€”
  more connections onto an already-saturated DB.
- **Network-bound** (bandwidth saturated, connection limits, cross-region RTT):
  CDN for egress, compression, connection pooling, keep chatty traffic in one DC.
The classic failure is sharding the database when the bottleneck is compute â€” a
new failure mode added to fix the wrong layer. Read the symptom, name the
resource, then pick the rung.

Treat each rung as a *hypothesis*, not a destination: "this design holds until
writes exceed X / a region is lost / the working set outgrows RAM." Saying the
breaking point out loud is the move that distinguishes reasoning from defending a
diagram. When a constraint changes (load doubles, latency target tightens, a DC
is lost), revisit the assumption and climb â€” calmly, not by patching the old
shape onto a problem it no longer fits.

## Dos and don'ts
Distilled from the ladder, the diagnosis step, and where the technique misleads.

**Do**
- **Diagnose the resource before adding capacity** â€” name compute vs storage vs
  network, then act on *that* tier. "Add servers" without a symptom is guessing.
- **Apply only the next rung the numbers justify**, and state its breaking point
  out loud ("holds until writes exceed X / a region is lost").
- **Climb vertically until the knee, then go horizontal** â€” bigger box first
  (no app changes), scale-out once the ceiling or cost knee is hit.
- **Make the web tier stateless before scaling it out** â€” move sessions to a
  shared store so autoscaling can't drop them.
- **Pair every rung with the failure mode it adds** (cache stampede, replica
  promotion, region failover, hot shard) â†’ `resilience-failure`.

**Don't**
- **Don't treat the ladder as a checklist** â€” it is a menu; most systems live
  happily at rung 4â€“6 forever and never shard.
- **Don't skip rungs to the "impressive" answer** â€” jumping to sharding or
  multi-region signals a memorized diagram, not a crossed ceiling.
- **Don't scale the layer that isn't the bottleneck** â€” more web servers onto a
  saturated DB just adds connections and amplifies the load downstream.
- **Don't route read-your-writes to a lagging replica** â€” replica lag reads like
  data loss; pin those reads to the primary (â†’ `consistency-coordination`).
- **Don't build the end-state on day one** â€” multi-region for 1k users is cost
  and complexity with no payoff. Match the rung to today's number.

## Numbers that matter
Numbers decide *which* rung is next; don't restate the tables â€” read
`back-of-the-envelope`. The ceilings that trigger a climb: a single RDBMS node
handles roughly **1k QPS**, a key-value node ~**10k**, a cache node
~**100kâ€“1M**; one ~64-core box is ~**64k** req/s of pure compute before IO. When
an estimate crosses one of these, that crossing *is* the next bottleneck. Peak is
typically ~2Ã— average, so size to peak. A useful framing: the rung you need is
roughly set by the *order of magnitude* of target QPS and dataset size â€” 1k QPS
fits one box, ~10k wants replicas and a cache, ~100k+ forces a stateless
horizontal tier, and a dataset past one node's RAM forces sharding. Each extra
"nine" of availability costs a disproportionate jump in redundancy (replicas â†’
multi-AZ â†’ multi-region) â€” tie the target to the requirement, not ambition
(â†’ `back-of-the-envelope`, `resilience-failure`).

## Diagram
To visualize the current architecture and the one-rung-ahead version side by
side (so the breaking point and the next move are explicit), use the in-plugin
`architecture-diagram` skill. Sketch only the rung you're on plus the next one â€”
not the whole ladder.

## Related building blocks
- `back-of-the-envelope` â€” *depends on* it for the ceilings; a number crossing one names the next bottleneck.
- `data-storage` â€” *owned-concept lives there*: replication and sharding/partitioning, the heaviest rungs.
- `caching` â€” *pairs with* this as the cache rung; owns what to cache and how it fails under load.
- `load-balancing` â€” *feeds into* the stateless horizontal tier; sits at its front.
- `content-delivery` â€” *pairs with* this as the CDN/edge rung for static and geo-distributed content.
- `resilience-failure` â€” *pairs with* every rung; each one adds a failure mode to degrade gracefully.
- `consistency-coordination` â€” *owned-concept lives there*: the freshness/coordination cost of replicas, multi-region, and shards.
- `system-design` â€” *orchestrated by* it; this skill runs at its "scale the design" step.

## References
- **`references/scaling-ladder.md`** â€” the full rung-by-rung ladder with concrete
  trigger thresholds, the compute/storage/network diagnosis checklist, the
  vertical-vs-horizontal decision, and the multi-region sync gotchas. Read when
  sequencing the next moves or diagnosing what breaks first.


---

# The Scaling Ladder

# Scaling ladder (rung-by-rung)

The detail that would bloat SKILL.md: concrete trigger thresholds per rung, the
bottleneck-diagnosis checklist, the vertical-vs-horizontal decision, and the
multi-region sync gotchas. Read when sequencing the next moves or arguing about
what breaks first.

> Climb to the **next** rung the numbers force â€” never the whole ladder. Each
> rung removes one ceiling and adds one failure mode. State the breaking point
> before you move; that is what separates reasoning from a memorized diagram.

## The rungs and their triggers

| # | Move | Climb when (trigger) | New failure mode it adds |
|---|---|---|---|
| 1 | Single server (all-in-one) | â€” (starting point) | Total SPOF; loses everything on one crash |
| 2 | Split web tier from data tier | One box can't hold both load and data; you want to scale them independently | Network hop between tiers; DB is now a separate SPOF |
| 3 | Vertical scale + read replicas | DB CPU/IO climbing; reads dominate; need read redundancy | Replica lag â†’ stale reads; promotion logic on primary failure |
| 4 | Cache hot reads | A number shows reads dominate and the DB is the read bottleneck | Stampede, stale-after-write, hot key, cold cache (â†’ `caching`) |
| 5 | CDN for static/edge | Static assets (img/JS/CSS/video) or geo-distance dominate latency/egress | CDN outage path; cache-expiry/invalidation drift (â†’ `content-delivery`) |
| 6 | Stateless web tier + LB + autoscale | Single web box saturates; you need elastic horizontal scale | Health-check stampede; scale-down drops in-flight state if not stateless |
| 7 | Async / queue for slow work | Bursty or slow tasks (encode, fan-out) block the sync path | Backpressure, duplicate delivery, DLQ growth (â†’ `messaging-streaming`) |
| 8 | Multi-DC / multi-region | Latency for distant users, or need to survive a region loss | Cross-region replication lag, conflict resolution, failover complexity |
| 9 | Shard the data tier | One primary can't hold the writes or the dataset | Resharding, hotspot/celebrity shard, cross-shard joins (â†’ `data-storage`) |

Most production systems settle somewhere around rungs 4â€“6 and never need 8â€“9.
Rungs are not strictly ordered â€” a write-heavy system may reach sharding (9)
before it ever needs a CDN (5). The order above is the *typical* read-heavy path;
let the numbers reorder it.

## Diagnose the bottleneck first (compute vs storage vs network)

Adding capacity without a diagnosis is the GUIDE's "add more servers" reflex.
Classify the pressure, then act on *that* resource.

| Symptom | Likely bound | Right move | Wrong move that amplifies it |
|---|---|---|---|
| CPU pegged, latency rises with request rate, threads queued | **Compute** | Profile the hot path; add app servers / autoscale | Sharding the DB (DB wasn't the problem) |
| DB CPU/IO pegged, slow queries, replica lag growing, connection pool exhausted | **Storage** | Add read replicas â†’ cache â†’ shard; add indexes; pool connections | Adding web servers â†’ more connections onto a saturated DB |
| Bandwidth saturated, connection caps hit, high cross-region RTT | **Network** | CDN/edge, compress payloads, pool/multiplex connections, keep chatty calls in one DC | Bigger DB or more app servers (neither is the limit) |

Diagnostic questions to ask before touching anything (the "production incident"
conversation, GUIDE #3): Did user count actually increase, or did per-user work?
Are DB latencies rising? Is the cache hit rate dropping? Is one shard/key hot?
Is a downstream dependency slow and causing retries upstream? The answer points
at one resource â€” fix that one.

## Vertical vs horizontal (the recurring fork)

| | Vertical (scale up) | Horizontal (scale out) |
|---|---|---|
| What | Bigger box: more CPU/RAM/disk | More boxes behind a balancer |
| Pro | Zero app changes; simplest; instant | Near-unlimited headroom; redundancy/failover |
| Con | Hard hardware ceiling; no failover; price climbs steeply near the top; reboot = full downtime | Requires statelessness; coordination, data distribution, more ops |
| Use first when | Traffic is low/moderate; quick relief; buying time | Large scale; high-availability requirement; elastic/bursty load |

Practical rule: scale **up** until the cost-per-unit knee or the hardware limit,
then scale **out**. Going horizontal requires removing state from the tier first
(see below) â€” do that before, not during, a scaling emergency. A DB can scale up
a long way (single powerful nodes hold many TB of RAM), which is why sharding is
often deferred far past the web tier going horizontal.

## Making a tier stateless (the unlock for rung 6)

Horizontal scale of the web/app tier only works if any request can hit any
server. Move state out:
- **Sessions / auth tokens** â†’ shared store (Redis/Memcached or a DB), or
  stateless signed tokens (JWT) so no server-side lookup is needed.
- **Uploaded files / user media** â†’ object storage or CDN, never local disk.
- **In-memory work state** â†’ externalize or make the request self-contained.

Sticky sessions (pin a user to one server) are a stopgap, not a fix: they make
add/remove of servers and failure handling harder and unbalance load
(â†’ `load-balancing`). Prefer true statelessness. Once stateless, autoscaling
(add/remove servers on load) is safe â€” scale-down won't strand a user's data.

## Multi-region / multi-DC gotchas (rung 8)

Going multi-region buys latency (geo-route users to the nearest DC) and disaster
survival (lose a region, route 100% to the survivor). The hard parts are data,
not traffic:
- **Traffic redirection** â€” GeoDNS routes users to the nearest healthy DC; failover
  re-points all traffic to the survivor. Test the failover path; an untested
  failover is a hope, not a plan.
- **Data synchronization** â€” replicate datasets across regions so a failover DC
  actually has the data. Async cross-region replication means a lag window where
  the far region is behind; a failover can lose the un-replicated tail.
- **Conflict resolution** â€” active-active (writes in both regions) needs conflict
  handling or single-writer-per-key guarantees; the consistency/availability fork
  under partition lives in `consistency-coordination` (CAP/PACELC). Active-passive
  (one region writes, others read/standby) is simpler and often enough.
- **Test & deploy** â€” keep config and code consistent across DCs; deploy and load-
  test in each region. Drift between regions surfaces only during a failover, the
  worst possible time.

## Sharding triggers and traps (rung 9)

Shard only when one primary genuinely can't hold the writes or the data â€” it is
the most complex rung. Mechanics (partition keys, consistent hashing,
rebalancing) are owned by `data-storage` and `consistency-coordination`; here are
the scaling-decision points:
- **Pick a shard key that spreads load evenly.** A poor key creates a
  hotspot/celebrity shard that re-centralizes the bottleneck you sharded to remove.
- **Resharding is expensive.** When a shard fills or load skews, the key/function
  changes and data moves; consistent hashing limits how much moves. Plan headroom.
- **Cross-shard joins/transactions get hard.** Denormalize or fan out queries;
  spanning a transaction across shards is a distributed-transaction problem
  (â†’ `consistency-coordination`).
- **Cheaper alternatives first.** Functional partitioning (split DBs by feature â€”
  users / posts / billing) and read replicas + cache often defer sharding for a
  long time. Try those before key-based sharding.

## Operational maturity that grows with the rungs

As the system climbs, the ability to *see* the next bottleneck matters as much as
the architecture. Centralized logging, host- and tier-level metrics (CPU, IO,
replica lag, cache hit rate, queue depth), and automated deploy/rollback are what
let you diagnose "what's breaking now" instead of guessing. Without them, every
scaling decision regresses to the "add more servers" reflex. These are not a rung
themselves â€” they are the instrument panel for climbing the ladder safely.

