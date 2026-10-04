---
name: sharded-counters
description: This skill should be used when the user needs a "sharded counter", "distributed counter", to "count likes / views at scale", handles a "high-write counter" or "hot counter contention", asks about "approximate counting", "real-time counts", or "HyperLogLog". It gives the recipe for absorbing write-heavy counting without a single hot row. Use it whenever one row/key takes concurrent increments faster than it can serialize them, even if the user doesn't say "sharded counter".
---

# Sharded counters

Count a thing that is incremented far faster than a single row, key, or
partition can serialize writes â€” likes, views, votes, rate tallies, inventory
decrements. The trap is the **hot counter**: every writer contends on one
record, so latency climbs and throughput plateaus no matter how big the box is.
Getting it wrong turns a trivial `+1` into the bottleneck of the whole feature.

## When to reach for this
Concurrent increments to a single logical count exceed what one row/key can
absorb â€” a viral post's like count, a live-event view counter, a global
rate tally. The symptom is write contention (lock waits, CAS retries, partition
hot-spotting) on one record while the rest of the store is idle. Reaching for
this means the *write* side is the problem, and an exact-to-the-millisecond
total is not required.

## When NOT to
Low write rate (a single atomic `INCR` handles thousands/sec â€” don't shard a
counter nobody is hammering; YAGNI). Counts that must be transactionally exact
and read-after-write consistent at every instant (bank balances, seat
inventory at sell-out) â€” that's a transactional decrement, see
`consistency-coordination`, not a fan-out tally. Counting *distinct* items
exactly (unique visitors) where you also need the member list â€” that's a set in
the store, not a counter. If reads dominate and writes are cheap, you need a
cached aggregate, not sharding.

## Clarify first
- **Write rate to the hottest single count** â€” peak increments/sec on *one*
  logical counter, not the aggregate (â†’ `back-of-the-envelope`).
- **Exact or approximate** â€” is an off-by-a-few total acceptable, and for how
  long may shards disagree (eventual)? Drives shard count and read path.
- **Counting occurrences or distinct items** â€” a running total vs. unique-count
  (likes vs. unique viewers) decides plain shards vs. HyperLogLog.
- **Read rate and freshness** â€” how often is the total read, and how stale may
  the served number be (sub-second? minutes?).
- **Time-windowed or lifetime** â€” "views in the last hour" needs bucketed keys
  and expiry; a lifetime total does not.

## The options
- **Single atomic counter** â€” one row/key with atomic `INCR`/`UPDATE +1`. Use
  when peak write rate on the hottest count is well within one node's serialized
  write throughput. The default; don't outgrow it prematurely.
- **Write-sharded (striped) counter** â€” split one logical count into N physical
  shards (`counter:{id}:shard:{0..N-1}`); each write increments a random/hashed
  shard, reads **sum all N**. Use when single-key contention is the bottleneck
  and the total may be eventually consistent.
- **Approximate distinct count (HyperLogLog)** â€” a fixed-size probabilistic
  sketch (~12 KB) that counts *unique* items with ~2% error. Use for uniques at
  scale where exact membership isn't needed (unique visitors, distinct search
  terms).
- **Time-windowed (bucketed) counters** â€” key the counter by time bucket
  (`views:{id}:2026-06-01T14`), increment the current bucket, sum recent buckets
  on read, expire old ones. Use for "last N minutes/hours" rate-style counts.
- **Aggregate-on-read + cached total** â€” sum shards (or roll up) periodically and
  serve the cached number. Use when reads vastly outnumber writes and a slightly
  stale total is fine (pairs with `caching`).

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Single atomic counter | Simplest; exact; read-after-write trivial | One hot record caps write throughput; contention under spikes | Increments on one count exceed one node â†’ shard the writes |
| Write-sharded counter | Spreads write load N-way; removes the hot spot | Reads cost N lookups + sum; total is eventually consistent; pick N up front | Read cost of summing N grows painful â†’ cache the aggregate / roll up |
| HyperLogLog | Counts uniques in fixed tiny memory at huge scale | ~2% error; can't list members or do exact counts | Exact uniques or the member set is required â†’ use a stored set |
| Time-windowed buckets | Cheap rolling/rate counts; old data self-expires | More keys; window boundaries need care; cross-bucket reads sum many keys | You need an exact lifetime total â†’ keep a separate lifetime counter |
| Aggregate-on-read + cache | Cheap reads of a heavy-write count | Served total lags writes by the refresh interval | Reads must be fresh-to-the-write â†’ read shards live (eat the N-sum) |

## Behavior under stress
A counter is a tiny thing that punches above its weight in an outage.

- **Hot-shard skew:** if writes pick shards by `hash(userId)` instead of random,
  one viral actor or a bad hash can still pile onto one shard. *Mitigate:* pick
  the shard at random per write; size N to peak contention, not average.
- **Read amplification on spikes:** when a count goes viral, reads of the total
  multiply the N-shard sum across the read fan-out and can overload the store.
  *Mitigate:* cache the aggregate and refresh on an interval, not per read
  (â†’ `caching`).
- **Lost increments:** fire-and-forget increments (or a crash before flush in a
  buffered/write-back path) silently undercount. *Mitigate:* use the store's
  atomic increment, accept the eventual-consistency window explicitly, and
  reconcile from a source of truth if exactness later matters.
- **Window-boundary stampede:** time-bucketed counters all roll to a new key at
  the top of the hour â€” a synchronized cold bucket plus a flood of reads. *Mitigate:*
  pre-create buckets and jitter rollups.
- **Mass expiry:** bucketed counters expiring together can spike the store.
  *Mitigate:* stagger TTLs.

**Monitor:** per-shard write distribution (skew), increments/sec vs. node
ceiling, read-path latency for the N-sum, sketch error budget (HLL), and
under/over-count drift against any source of truth.

## How to apply
1. **Clarify the inputs** â€” peak increments/sec on the *hottest single count*,
   exact-vs-approximate tolerance, occurrence-vs-distinct, read rate, and
   freshness budget (see *Clarify first*). If no number shows one count is too
   hot, stay on a single atomic counter (YAGNI).
2. **Pick from the trade-off table** â€” single atomic if it fits one node;
   write-sharded if single-key contention is the wall; HyperLogLog for uniques;
   time-buckets for rolling windows. Combine (e.g. sharded + cached aggregate).
3. **Set the key knobs** â€” choose N (shard count) from peak contention, the
   shard-selection rule (random, not user-hashed), the read aggregation method,
   bucket granularity + TTL for windows, and the cache refresh interval.
4. **Stress-test the choice** â€” walk *Behavior under stress*: confirm shard
   skew, read amplification, lost increments, and window boundaries each have a
   mitigation the traffic profile actually needs.
5. **Size it with numbers** â€” N â‰¥ peak increments/sec Ã· per-shard write ceiling;
   confirm the N-sum read cost and any HLL error fit the budget
   (â†’ `back-of-the-envelope`).
6. **Pick a provider** â€” default to the generic recipe; open a provider file
   only if the user named a cloud (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Start with a single atomic counter; shard only when a number shows one count
  is the bottleneck.
- Pick the write shard at **random** so load spreads evenly regardless of the
  actor.
- Cache the summed aggregate and refresh on an interval when reads dominate.
- Use HyperLogLog for uniques-at-scale and state the ~2% error as a known cost.
- Expire time-bucket keys with staggered TTLs and pre-create the next bucket.
- State the eventual-consistency window out loud â€” sharding trades exact-now for
  throughput.

**Don't**
- Don't shard a counter that a single `INCR` already handles (premature
  sharding adds read cost for nothing).
- Don't hash the shard by user/entity ID â€” a hot actor reconcentrates the load.
- Don't sum N shards on every read of a viral count â€” cache the aggregate.
- Don't use a sharded/eventual counter where the number must be transactionally
  exact (money, sell-out inventory) â†’ `consistency-coordination`.
- Don't reach for HyperLogLog when you also need the member list or an exact
  count.

## Numbers that matter
The deciding figure is **peak increments/sec on the single hottest count** vs. a
node's serialized write ceiling â€” that ratio sets N. A HyperLogLog sketch is
~12 KB for billions of uniques at ~2% standard error, regardless of cardinality
â€” the reason it beats a stored set at scale. Reading a sharded total costs N
lookups, so N trades write headroom for read cost. For QPS rates, per-node write
ceilings, and storage sizing, don't restate them here â€” see `back-of-the-envelope`.

## Interface sketch
A sharded counter is a key contract, not one value:

- **Write:** `INCR counter:{id}:shard:{rand(0..N-1)}` (atomic, fire to one shard).
- **Read:** `sum(GET counter:{id}:shard:{0..N-1})` â€” or read the cached aggregate
  `count:{id}` refreshed every T seconds.
- **Distinct:** `PFADD uniq:{id} {member}` then `PFCOUNT uniq:{id}` (HLL sketch).
- **Windowed:** `INCR views:{id}:{bucket}` with a TTL; read sums the recent
  buckets.

Decide N, the shard-selection rule, the aggregation/refresh policy, and the
window granularity up front â€” they are the contract, not implementation details.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the fan-out write path (writer â†’ random shard) and the
aggregate-on-read sum (read â†’ N shards â†’ cached total), use the in-plugin
`architecture-diagram` skill â€” shards share the store color, the read fan-out is
a dashed sum arrow, and the cached aggregate sits in the cache color.

## Related building blocks
- `data-storage` â€” *depends on* this for where the shards physically live;
  sharding/partitioning theory and key design are *owned* there.
- `caching` â€” *pairs with* this to serve the cached aggregate so a viral count's
  reads don't re-sum N shards every time.
- `consistency-coordination` â€” *depends on* this for the exact-vs-eventual count
  decision; transactional/atomic semantics and quorum are *owned* there.
- `back-of-the-envelope` â€” *feeds into* this: it supplies the per-count write
  rate and per-node ceiling that justify sharding and set N.
- `system-design` â€” *owned-concept lives in* the orchestrator: the reasoning
  loop, the trade-off method, and the ten failure modes.

## References
- **`references/deep-dive.md`** â€” shard-count math, random vs. hashed selection,
  HyperLogLog mechanics and error, time-bucket layout, roll-up/aggregation
  patterns, and reconciliation. Read when designing the counter in detail.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” service mappings,
  atomicity/contention limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Sharded counters deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
counter in detail.

## Why one counter goes hot

A single logical count is one row/key. Every increment must serialize against
every other â€” a row lock (SQL `UPDATE â€¦ SET c = c + 1`), a compare-and-swap
retry loop, or a single-threaded shard handling one atomic op at a time. Under
contention, writers queue: throughput plateaus at the *serialization* rate of
that one record, and added concurrency only deepens the queue (latency climbs,
CAS retries multiply). Scaling the box up doesn't help â€” the limit is one
record's write path, not the machine.

## Write-sharded (striped) counter

Split the logical count into N physical sub-counters and **sum on read**:

```
write:  shard = rand(0, N-1);  INCR counter:{id}:shard:{shard}
read:   total = sum(GET counter:{id}:shard:{i} for i in 0..N-1)
```

- **Pick the shard at random per write**, not by `hash(actorId)`. Hashing by the
  actor reconcentrates load when one actor (a celebrity, a bot, a retry storm) is
  responsible for the spike â€” the exact case sharding exists to fix. Random
  spreads evenly regardless of who writes.
- **Choosing N:** `N â‰¥ ceil(peak_increments_per_sec / per_shard_write_ceiling)`,
  then round up for headroom and skew. Bigger N spreads writes better but makes
  every read sum more keys. N is a knob between write headroom and read cost;
  pick it from the *peak on the hottest single count*, not the average across all
  counters.
- **Eventual consistency:** a read may catch some shards mid-increment, so the
  total can lag the true value by the in-flight writes. This is the core trade:
  throughput for exact-now. State the window; if it's unacceptable, you don't
  want a sharded counter (â†’ `consistency-coordination`).

## Aggregation on read and roll-up

Summing N shards per read is fine at low read rates. When reads dominate or the
count goes viral:

- **Cached aggregate:** a background job (or a periodic task) sums the shards and
  writes `count:{id}`; reads serve that. Refresh interval = freshness budget.
  Pairs with `caching`.
- **Two-tier roll-up:** shards â†’ periodic roll-up into a durable lifetime total
  (e.g. flush hourly buckets into a `total` column). Keeps the hot path in fast
  storage and the source-of-truth total in durable storage.
- **Read-time vs. write-time aggregation:** aggregate on read when writes are the
  hot path (most counters); aggregate on write (maintain a materialized total)
  only when reads are hotter than writes and you can afford the write coupling.

## HyperLogLog (approximate distinct count)

Counting *unique* items (unique visitors, distinct terms) exactly needs storing
every member â€” memory grows with cardinality. HyperLogLog is a probabilistic
sketch that estimates cardinality in **fixed** memory:

- Hash each member; use the leading bits to pick one of `m` registers, and record
  the position of the leftmost 1-bit in the rest. Cardinality is estimated from
  the harmonic mean of register values (a long run of leading zeros implies many
  distinct items were seen).
- **~12 KB** holds the standard `m = 16384` registers and estimates up to
  billions of uniques at **~0.81% / âˆšm â‰ˆ 2%** standard error â€” independent of how
  large the true count is.
- **Mergeable:** sketches union losslessly (take the max per register), so
  per-shard or per-window sketches combine into a global unique count. This is
  what makes HLL scale across nodes and time buckets.
- **Limits:** you cannot list members, remove a member, or get an exact count.
  If any of those is required, use a stored set (and accept the memory cost) or a
  different structure.

## Time-windowed (bucketed) counters

For "views in the last hour / 5 minutes":

```
write:  bucket = floor(now / granularity);  INCR views:{id}:{bucket}  (+ TTL)
read:   sum the buckets covering the window
```

- **Granularity** trades resolution for key count: 1-minute buckets give a tight
  sliding window but more keys to sum; 1-hour buckets are cheap but coarse.
- **TTL** each bucket to just beyond the longest window read, so old data
  self-expires â€” no cleanup job.
- **Stagger TTLs / pre-create buckets** so an entire counter's buckets don't
  expire or cold-start at the same instant (window-boundary stampede). HLL
  sketches can be bucketed the same way for windowed unique counts.

## Reconciliation and durability

Increments to an in-memory store (e.g. Redis) are fast but not durable by
default; a crash can lose recent increments. Options:

- Enable persistence (AOF) and/or replication for the counter store.
- Treat the fast counter as a *cache* of a durable source of truth (events in a
  log/DB) and reconcile periodically â€” exact when it matters, fast on the hot
  path. The event log is owned by `messaging-streaming` / `data-storage`.
- For money or inventory, do **not** use an eventual sharded counter â€” use a
  transactional decrement with the right isolation (â†’ `consistency-coordination`).

## Common mistakes

- Sharding a counter a single `INCR` already handled (read cost for no gain).
- Hashing the shard by actor ID, so a hot actor lands on one shard anyway.
- Summing N shards on every read of a viral count instead of caching the total.
- One TTL for all buckets â†’ synchronized mass expiry.
- Using HLL where the member list or an exact count is later required.
- Assuming the in-memory counter is durable without persistence/reconciliation.

