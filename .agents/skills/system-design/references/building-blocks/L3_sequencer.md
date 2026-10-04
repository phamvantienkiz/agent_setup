---
name: sequencer
description: This skill should be used when the user needs a "unique ID generator", "distributed IDs", a "Snowflake ID", asks "UUID vs auto-increment", wants a "time-sortable ID", a "monotonic sequence", a "ticket server", or "ID generation at scale". It gives a menu of ID schemes (UUID/ULID, Snowflake-style, DB ticket/range) with their causality, ordering, and clock-skew trade-offs. Use it whenever a design needs collision-free identifiers across many nodes, even if the user doesn't say "sequencer".
---

# Sequencer

Hand out identifiers that are unique across every node without a central
bottleneck â€” and decide whether those IDs must also be *sortable* or *monotonic*.
Getting this wrong shows up late and hard: collisions corrupt data, a single
allocator caps write throughput, and IDs that leak a creation time or a sequential
count expose business secrets and enable enumeration attacks.

## When to reach for this
A system writes new records across multiple nodes and each needs a primary key
(orders, messages, uploads, events). Reach for this when a single auto-increment
column would serialize all writes, when IDs must be generated before a DB round
trip (client-side, offline), or when records must be roughly time-ordered without
a separate sort field.

## When NOT to
A single relational node still comfortably serves the write load (â†’
`back-of-the-envelope`) â€” then a plain `BIGINT AUTO_INCREMENT`/`SERIAL` is the
cheapest correct answer; do not build a distributed ID service for it (YAGNI).
If a natural unique key already exists (email, ISBN, content hash), use it. Don't
demand global monotonicity unless an invariant truly needs it â€” it is the most
expensive property here and usually only *per-entity* ordering is required.

## Clarify first
- **Generation point** â€” client/edge, app server, or database? (Decides whether a
  DB round trip per ID is acceptable.)
- **Ordering need** â€” none, *time-sortable* (k-sorted is fine), or *strictly
  monotonic*? Per-entity or global? This is the single biggest fork.
- **Write rate & node count** â€” IDs/sec at peak and how many generators (â†’
  `back-of-the-envelope`). Sets the bits needed for a sequence counter.
- **Size & encoding budget** â€” 64-bit int (fits an indexed key cheaply) vs 128-bit
  (no coordination ever) vs short URL-safe string?
- **Leakage tolerance** â€” may the ID reveal creation time or a guessable count
  (enumeration / competitor signal)?

## The options
- **Auto-increment / SQL sequence** â€” one DB column hands out IDs. Use when a
  single node owns the writes and you want zero new infrastructure.
- **UUIDv4 (random 128-bit)** â€” generate anywhere, no coordination, effectively
  zero collision risk. Use when you only need uniqueness and never sort by ID.
- **ULID / UUIDv7 (time-prefixed 128-bit)** â€” random but with a millisecond
  timestamp prefix, so IDs sort by creation time. Use when you want UUIDv4's
  zero-coordination *and* time-ordering (the modern default for new keys).
- **Snowflake-style (timestamp + node + sequence, 64-bit)** â€” pack a timestamp,
  a node ID, and a per-ms counter into a sortable 64-bit int. Use at high write
  rates where a compact, k-sorted integer key matters.
- **DB ticket / range allocation (Flickr-style)** â€” a central table hands out
  *blocks* of IDs (e.g. 1000 at a time); each node serves from its block in
  memory. Use when you want simple monotonic-ish integers without per-ID
  coordination.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Auto-increment / sequence | Trivial, monotonic, compact int | Serializes writes; single node caps throughput; leaks count | Writes outgrow one node, or you need client-side IDs â†’ ticket/Snowflake |
| UUIDv4 (random) | Generate anywhere, no coordination, no leakage | 128-bit; random order kills index locality (page splits); not sortable | You need time-ordering â†’ ULID/UUIDv7 |
| ULID / UUIDv7 | Zero coordination + time-sortable + index-friendly | Still 128-bit; only ms-sortable (not strict); leaks creation time | You need a 64-bit key or strict order â†’ Snowflake / sequence |
| Snowflake-style (64-bit) | Compact, k-sorted, ~4M IDs/node/sec | Needs node-ID assignment + clock-skew handling; epoch/bit budget caps lifespan | Clock sync is unreliable, or you can't assign node IDs â†’ ULID |
| DB ticket / range | Monotonic-ish ints, low coordination, simple | Allocator table is a SPOF; gaps on restart; only loosely ordered across nodes | Allocator becomes a bottleneck or SPOF â†’ Snowflake/ULID |

## Behavior under stress
The whole point of distributed ID schemes is to avoid a single allocator, so the
failure modes cluster around *coordination shortcuts*.

- **Allocator as SPOF/bottleneck (ticket, single sequence):** every write blocks on
  one row/node. A spike or its failure stalls all inserts. *Mitigate:* hand out
  larger ranges, replicate the allocator, or move to Snowflake/ULID (no central
  hop). Larger ranges trade away monotonicity and waste IDs on restart.
- **Clock skew & rewind (Snowflake/time-prefixed):** if a node's clock jumps
  backward (NTP correction, VM pause), it can re-emit a timestamp it already used
  and collide within its node+sequence space. *Mitigate:* refuse to emit while
  `now < last_timestamp` (block or error), use a monotonic clock source, and alarm
  on skew. Never silently trust wall-clock time.
- **Sequence-bits exhaustion:** more than `2^seq_bits` IDs in one millisecond on
  one node overflows the counter. *Mitigate:* spin-wait to the next ms, or size
  the bit budget to peak rate up front.
- **Node-ID collision:** two generators boot with the same node ID (bad config,
  autoscaling reuse) and silently mint duplicates. *Mitigate:* lease node IDs from
  a coordinator (â†’ `consistency-coordination`) instead of static config.
- **Hot shard from sequential keys:** monotonic IDs as a shard/partition key send
  all new writes to one shard. *Mitigate:* hash the key or prefix-shard â€” the
  partitioning fix lives in `data-storage`.

**Monitor:** ID issuance rate per node, clock-skew/rewind events, allocator
latency and range-exhaustion rate, and duplicate-key errors (should be zero).

## How to apply
1. **Clarify the inputs** â€” pin down the generation point, the ordering need
   (none / time-sortable / strict; per-entity vs global), peak IDs/sec, the size
   budget, and leakage tolerance (see *Clarify first*). If one DB node serves the
   writes, stop â€” use auto-increment (â†’ `back-of-the-envelope`).
2. **Pick from the trade-off table** â€” no ordering and 128-bit is fine â†’ UUIDv4;
   want time-sortable with zero coordination â†’ ULID/UUIDv7; need a compact 64-bit
   k-sorted int at high rate â†’ Snowflake; want simple monotonic ints â†’ ticket/range.
3. **Set the key knobs** â€” for Snowflake fix the epoch and the timestamp/node/seq
   bit split against your node count and peak rate; for ticket pick the block size;
   decide the node-ID assignment method (lease vs static); choose the encoding
   (raw int, Base62, Crockford Base32).
4. **Stress-test the choice** â€” walk *Behavior under stress*: clock rewind,
   sequence exhaustion, node-ID collision, allocator failure, and the hot-shard
   effect of sequential keys. Confirm a mitigation for each one your profile hits.
5. **Size it with numbers** â€” confirm the bit budget covers peak IDs/sec/node and
   the epoch gives enough years; confirm the encoded length fits the key/URL
   constraint (â†’ *Numbers that matter*).
6. **Pick a provider** â€” default to the generic recipe (a Snowflake library, a
   ticket row, or ULID/UUIDv7); only open a provider file if the user named a
   cloud (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Default to ULID/UUIDv7 for new keys when you want zero coordination plus rough
  time-ordering â€” it dodges UUIDv4's random-index pain.
- Size the Snowflake bit budget (timestamp/node/sequence) against peak rate and
  required lifespan *before* picking it; write the epoch down.
- Lease node IDs from a coordinator instead of static config when nodes autoscale.
- Refuse to emit on clock rewind and alarm on skew; treat duplicate-key errors as
  a P1.
- Separate the *internal* key (sortable, may leak time) from any *external* opaque
  ID when enumeration or leakage matters.

**Don't**
- Don't build a distributed ID service before a number shows one DB node can't
  keep up (YAGNI).
- Don't use a random UUIDv4 as a clustered/primary index on a hot table â€” random
  order causes page splits and write amplification.
- Don't make a single sequence or ticket row the allocator for the whole fleet
  without replication â€” it's a SPOF and a write bottleneck.
- Don't use a globally monotonic ID as a shard key â€” it creates a hot shard (fix
  in `data-storage`).
- Don't trust wall-clock time for ordering; ms-sortable is k-sorted, not strict.

## Numbers that matter
A 64-bit Snowflake layout (â‰ˆ41 timestamp bits + 10 node + 12 sequence) gives ~69
years from its epoch, 1024 nodes, and 4096 IDs/node/ms â‰ˆ **4M IDs/node/sec** â€”
ample for almost any single service. UUID/ULID are 128 bits = 16 bytes (vs 8 for
a 64-bit int), doubling index key size. A ticket block of N IDs cuts allocator
hits by NÃ— but risks losing up to N IDs on a node restart. For peak-rate and
storage sizing, see `back-of-the-envelope`; restate only the figure a decision
turns on.

## Interface sketch
An issued ID is a contract. State its **width** (64 vs 128 bit), its **layout**
(e.g. Snowflake `[timestamp:41 | node:10 | seq:12]`), its **ordering guarantee**
(unordered / k-sorted by ms / strict), and its **encoding** (raw int, Base62,
Crockford Base32 â€” case-insensitive, URL-safe). A generator endpoint, if any, is
minimal: `next(entity) -> {id, issued_at}`. Document whether the ID is the storage
key, the sort key, or both â€” that choice is consumed by `data-storage`.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer (most clouds have **no** dedicated ID
service â€” you run a library or a sequence yourself).

## Diagram
To visualize the issuance path (generator nodes â†’ 64-bit layout â†’ record key) or
the ticket-server block-allocation flow, use the in-plugin `architecture-diagram`
skill; an inline `[ts | node | seq]` sketch is enough for quick bit-budget
reasoning. Do not embed Mermaid.

## Related building blocks
- `data-storage` â€” *feeds into* it: the ID becomes the primary/sort key, and the
  sharding/partitioning that a sequential key can hot-spot is owned there.
- `consistency-coordination` â€” *depends on* it for the causality, ordering, and
  leader-election theory behind monotonic guarantees and node-ID leasing; link,
  don't re-teach.
- `messaging-streaming` â€” *pairs with* it for message ordering and dedup, where
  time-sortable IDs give a natural sequence and idempotency anchor.
- `api-design` â€” *pairs with* it: ID generation underpins idempotency keys (owned
  there) for safe retries.
- `system-design` â€” *owned-concept lives in* the orchestrator: the reasoning loop,
  the trade-off method, and the ten failure modes.

## References
- **`references/deep-dive.md`** â€” Snowflake bit-layout math and epoch choice,
  clock-skew/monotonic-clock handling, ticket-server range allocation, ULID vs
  UUIDv7 byte layout, encoding (Base62/Crockford), and node-ID leasing. Read when
  designing the generator in detail.
- **`references/providers/{generic,aws,gcp}.md`** â€” library/service mappings,
  limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Sequencer deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
generator in detail.

## Snowflake bit layout and the epoch

The classic Twitter Snowflake packs a 64-bit signed integer (top sign bit unused
so values stay positive):

```
[ 1 unused | 41 timestamp ms | 10 node id | 12 sequence ]
```

- **Timestamp (41 bits):** milliseconds since a *custom epoch* (not the Unix
  epoch). 2^41 ms â‰ˆ **69.7 years** of lifespan. Picking a recent custom epoch
  (e.g. the project's launch date) buys the full 69 years from *now* instead of
  burning ~55 of them on time already elapsed since 1970.
- **Node id (10 bits):** 1024 distinct generators. Split as datacenter+worker
  (e.g. 5+5) if you need region awareness.
- **Sequence (12 bits):** 4096 IDs per node per millisecond â†’ ~4.0M IDs/node/sec.

The split is a budget you re-allocate to fit the problem: fewer node bits if you
have few generators, more sequence bits if one node must burst harder, more
timestamp bits (e.g. shift to a coarser tick) for a longer lifespan. Decide it
once; changing it later breaks sortability and risks collisions with already-
issued IDs.

**Why it's only k-sorted, not strictly sorted:** IDs are globally sortable *by
millisecond*, but within the same ms two different nodes' IDs interleave by node
id, not by true issue time. So Snowflake (and ULID/UUIDv7) give *k-sortedness*:
roughly time-ordered, good enough for range scans and pagination, not a strict
total order. A strict global monotonic counter needs single-writer serialization
(a sequence, or consensus) â€” that theory lives in `consistency-coordination`.

## Clock skew, rewind, and monotonic clocks

Time-based IDs assume the wall clock only moves forward. It doesn't: NTP steps it,
VMs pause and resume, leap seconds happen. The generator algorithm must defend:

```
on next_id():
  ts = now_ms()
  if ts < last_ts:            # clock moved backward
      # either block until ts >= last_ts, or reject with an error,
      # or (Snowflake variant) reuse last_ts and bump sequence
      handle_rewind()
  if ts == last_ts:
      seq = (seq + 1) & seq_mask
      if seq == 0:            # sequence exhausted this ms
          ts = wait_next_ms(last_ts)
  else:
      seq = 0
  last_ts = ts
  return (ts << shift) | (node << node_shift) | seq
```

- Read time from a **monotonic source** for the comparison where possible; use
  wall-clock only to fill the timestamp field.
- A small backward jump (a few ms) is best handled by *blocking* until the clock
  catches up. A large jump should *error* and alarm â€” silently emitting risks
  duplicates across the node+sequence space.
- Keep clocks tight with NTP/chrony; alarm when measured skew exceeds a threshold
  (e.g. tens of ms). Skew also corrupts ordering even when it doesn't collide.

## Node-ID assignment

Static config (node id baked into a deploy) is simple but fragile: autoscaling,
re-imaging, or a copy-paste error can boot two generators with the same id, and
they will mint *duplicates* silently. For elastic fleets, **lease** a node id:

- Register on startup against a coordinator (ZooKeeper/etcd ephemeral node, or a
  DB row with a TTL) and release on shutdown.
- Renew the lease; if it can't be renewed, stop issuing IDs.

Leader election and lease semantics are owned by `consistency-coordination` â€”
reference it; this skill only decides *that* node ids must be unique and how
collisions manifest.

## DB ticket / range allocation (Flickr-style)

A central table issues IDs without a per-ID network hop per generator:

- **Single-row ticket server:** a row holds the last-issued value; `REPLACE
  INTO ... ; SELECT LAST_INSERT_ID()` (MySQL) atomically bumps and returns it.
  To remove the SPOF, run two servers â€” one issuing **odd** numbers, one **even**
  (`auto_increment_increment=2`, different offsets). Loosely ordered, highly
  available.
- **Range/block allocation:** instead of one ID per call, a node claims a *block*
  (e.g. `UPDATE counters SET val = val + 1000 ... RETURNING old_val`) and serves
  IDs 0â€“999 from memory. Allocator load drops by the block size. The cost: a
  restart abandons the unused tail of the block (gaps), and IDs are only ordered
  *within* a block, not across nodes drawing concurrent blocks.

Block size is the knob: bigger blocks = fewer allocator hits and lower coupling,
but more wasted IDs on restart and weaker ordering. Size it to amortize allocator
latency over expected uptime, not to zero.

## ULID vs UUIDv7 byte layout

Both are 128-bit, time-prefixed, and lexicographically sortable by creation time â€”
fixing UUIDv4's random-index problem while keeping zero coordination.

- **ULID:** 48-bit ms timestamp + 80 bits randomness. Canonical text form is 26
  chars of **Crockford Base32** (case-insensitive, no `I/L/O/U` to avoid
  ambiguity), URL-safe. Monotonic variant increments the random field within the
  same ms.
- **UUIDv7:** 48-bit ms timestamp + version/variant bits + ~74 bits randomness, in
  the standard 36-char hyphenated UUID text form. Prefer it when you need RFC-UUID
  tooling/column-type compatibility.

Both still **leak creation time** in the prefix. If that's sensitive, keep them
internal and expose a separate opaque external id.

## Encoding and size

- **Raw 64-bit int:** smallest index key (8 bytes), but a long decimal string and
  trivially enumerable.
- **Base62 / Crockford Base32:** compact URL-safe strings; Base62 (`0-9A-Za-z`)
  packs a 64-bit int into ~11 chars, Base32 into ~13 but is case-insensitive and
  human-friendlier (good for codes read aloud).
- **128-bit (UUID/ULID):** 16-byte key, 26â€“36 char text. The index-size and
  cache-footprint cost is real on hot, heavily-indexed tables â€” a reason to prefer
  a 64-bit Snowflake when key size dominates.

## Common mistakes

- Burning the timestamp range on the Unix epoch instead of a recent custom epoch.
- Static node ids on an autoscaling fleet â†’ silent duplicates.
- Treating ms-sortable IDs as a strict total order.
- UUIDv4 as a clustered primary key on a write-hot table (page splits, bloat).
- Sequential IDs as a shard key â†’ hot shard (partition fix is in `data-storage`).
- No clock-rewind guard; trusting NTP to never step backward.

