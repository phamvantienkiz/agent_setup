---
name: consistency-coordination
description: This skill should be used when the user asks about the "CAP theorem", "PACELC", a "consistency model", "eventual vs strong consistency", "read-your-writes", "causal consistency", "quorum" or "R+W>N", "consensus", "Raft / Paxos", "leader election", "consistent hashing", a "distributed transaction", "2PC", or "saga". Use it whenever a design has multiple copies of data or coordinating nodes and a decision hinges on what a reader is guaranteed to see during replication lag, a network partition, or a node failure â€” even if the user doesn't say "consistency".
---

# Consistency & Coordination

Decide what a reader is guaranteed to see when data lives on more than one node,
and how independent nodes agree on a single answer. Get this wrong and the system
either serves stale or conflicting data silently, or stalls the moment a network
link drops â€” the most common and most punishing distributed-systems failure.

## When to reach for this
Any time state is replicated, sharded, or coordinated across nodes: choosing a
replication or quorum scheme, picking a consistency level, electing a leader,
spreading keys across an elastic fleet (consistent hashing), or committing a
change that spans services. Reach here the instant someone asks "what does a read
see right after a write?" or "what happens during a partition?"

## When NOT to
A single node with no replicas has nothing to coordinate â€” don't invoke quorums or
consensus for it (YAGNI). Most apps tolerate seconds of staleness; reaching for
strong consistency or distributed transactions when eventual consistency would do
buys latency and operational pain for a guarantee no requirement asked for. The
cheapest model that satisfies the invariant wins. Naming Raft or 2PC before a
correctness requirement forces it is a red flag.

## Clarify first
- **What breaks if a read is stale?** A wrong balance vs a slightly old like count
  are different systems. (â†’ `requirements-scoping`.)
- **Must a user see their own writes immediately?** Read-your-writes is far cheaper
  than global strong consistency.
- **What is the blast radius of a partition or lost region?** Drives the CAP/PACELC
  choice. (GUIDE failure mode #1.)
- **Write contention and conflict shape** â€” single-writer per key, or concurrent
  writers needing conflict resolution?
- **Latency budget** â€” synchronous coordination adds a round trip (or a
  cross-region one); confirm the budget allows it. (â†’ `back-of-the-envelope`.)

## The options

**Pick a consistency model** (the guarantee a read gets):
- **Strong / linearizable** â€” every read sees the latest committed write. Use when
  an invariant must hold globally (balances, inventory, uniqueness).
- **Read-your-writes / monotonic** â€” a session sees its own writes and never goes
  backward. Use for profile edits, "post then see your post".
- **Causal** â€” reads respect causeâ†’effect order (a reply never precedes its
  parent). Use for comments, chat, collaborative edits.
- **Eventual** â€” replicas converge "soon"; reads may lag. Use for like counts,
  feeds, caches â€” anything where staleness is cheap.

**Pick how copies agree:**
- **Single-leader (primary)** â€” one node orders all writes; followers replicate.
  Use when a clear write owner is acceptable; the common default.
- **Quorum (R + W > N)** â€” read/write to a majority; tune R and W per workload.
  Use for leaderless stores needing tunable consistency and availability.
- **Consensus (Raft / Paxos)** â€” a majority agrees on a replicated log, even across
  failures. Use for the control plane: leader election, config, metadata, locks.

**Coordinate a multi-key / multi-service change:**
- **Saga** â€” a sequence of local transactions with compensating undos. Use across
  services where a global lock is impossible; accepts eventual consistency.
- **2PC / distributed transaction** â€” atomic all-or-nothing across nodes via a
  coordinator. Use only when atomicity is mandatory and the cost is accepted.

**Spread keys across nodes â€” consistent hashing** (this skill owns it): map keys
and nodes onto a hash ring; a key belongs to the next node clockwise. Adding or
removing a node remaps only ~K/N keys instead of nearly all (as plain
`hash(key) % N` does), avoiding a remap storm. Virtual nodes even out load and tame
hotspots. It is the standard partitioning scheme for caches, leaderless stores, and
LB backends. Mechanics in `references/deep-dive.md`.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Strong/linearizable | Correctness; no stale reads | Latency (a round trip / quorum); unavailable under partition (CP) | Staleness becomes tolerable â†’ relax to read-your-writes/eventual |
| Read-your-writes | "See my own change" without global cost | Other users still see stale; needs session/sticky routing | A global invariant appears â†’ go strong |
| Eventual | Highest availability + lowest latency (AP) | Stale and conflicting reads; needs conflict resolution | An invariant can't tolerate divergence â†’ stronger model |
| Single-leader | Simple ordering; no write conflicts | Leader is a write SPOF; failover gap; reads from followers lag | Write throughput exceeds one node, or leader region lost â†’ multi-leader/quorum |
| Quorum (R+W>N) | Tunable consistency vs availability per call | Higher read+write cost; still needs conflict handling on concurrent writes | Even one quorum slow path is too costly â†’ leader or local reads |
| Consensus (Raft/Paxos) | Agreement that survives node loss | Majority required (loses availability below quorum); write latency; complex | The data plane needs it at scale â†’ push coordination to a service |
| Saga | Cross-service change without a global lock | No isolation; partial states visible; must design compensations | True atomicity is required â†’ 2PC (and accept its cost) |
| 2PC | Atomic multi-node commit | Coordinator is a SPOF; locks held across the vote; blocks on failure | Availability/throughput matter more than strict atomicity â†’ saga |

## Behavior under stress
This block's whole purpose is the failure case â€” what happens when the network or a
node breaks (GUIDE #1, #6).

- **Network partition** is the forcing function (the C-vs-A choice in CAP). A
  CP/strong system *rejects writes* on the minority side to protect invariants â€” it
  trades availability for correctness. An AP/eventual system *accepts writes
  everywhere* and reconciles later â€” it trades correctness for availability. State
  which one you chose and why; there is no third option that keeps both.
- **Leader loss** triggers an election. During the gap, writes pause (single-leader)
  or proceed risky (if you let a stale leader keep writing â†’ **split-brain** and
  divergent histories). Fencing tokens and a majority quorum prevent two leaders.
- **Quorum below majority** (too many nodes down) means a strict quorum store stops
  accepting writes â€” by design. More nodes down than `N âˆ’ W` blocks writes; more
  than `N âˆ’ R` blocks reads.
- **Coordination amplifies outages:** a 2PC coordinator crash leaves participants
  holding locks (blocking); a consensus cluster that loses quorum freezes the
  control plane and everything depending on it. Aggressive leader-election timeouts
  can cause election storms (repeated re-elections under load).
- **Monitor:** replication lag (the staleness window), leader-election rate and
  duration, quorum health (reachable nodes vs N), conflict/repair rate, andâ€”for
  consistent hashingâ€”per-node key distribution and rebalance volume.

Failover trade-offs (active-passive vs active-active, data-loss windows) are
covered by `resilience-failure`; this block supplies the consistency cost of each.

## How to apply
1. **Clarify the invariant.** Pin down what breaks on a stale or conflicting read,
   whether a user must see their own writes, and the partition blast radius (use the
   Clarify-first questions). No invariant â†’ default to eventual and stop.
2. **Pick the model and the agreement scheme** from the Trade-offs table: match the
   guarantee to the weakest invariant the data can tolerate, then choose
   single-leader / quorum / consensus by who owns writes and what must survive node
   loss. Add a saga or 2PC only when a change spans services and atomicity is forced.
3. **Set the knobs.** Pin the consistency level per *operation* (not per datastore),
   set `N`, `R`, `W` so `R + W > N` where overlap is required, choose a conflict
   policy (LWW / version-vector / app resolver), and pick consistent hashing for key
   placement when the fleet is elastic.
4. **Stress-test the choice.** State the CAP stance explicitly: what happens on a
   partition, on leader loss, and below quorum. Confirm split-brain is fenced and
   coordination can't amplify an outage into a cluster-wide freeze.
5. **Size it with numbers.** Price the coordination round trips (same-DC vs
   cross-region) against the latency budget and size `N` for the failure target, via
   `back-of-the-envelope`. If strong consistency blows the budget, relax the model.
6. **Map to a provider.** Default to the generic recipe; if a cloud is named, read its
   provider file for the managed consistency knobs and quorum-store limits.

## Dos and don'ts
**Do**
- Pin the guarantee on the *operation* â€” most reads eventual, only invariant-bearing
  ones strong â€” so coordination cost is paid only where it earns correctness.
- State the CAP stance out loud: on a partition, name which side rejects writes (CP)
  or accepts and reconciles (AP). There is no option that keeps both.
- Size `R`, `W`, `N` for overlap and a failure target, and fence leaders with a
  majority quorum plus fencing tokens.
- Return a version (or vector clock) so callers can detect and resolve conflicts.

**Don't**
- Don't reach for strong consistency, consensus, or 2PC before an invariant forces
  it â€” staleness is usually cheap, and global coordination buys latency and pain.
- Don't run synchronous strong consistency or 2PC across regions on a tight write
  budget; a cross-region round trip can add 100 ms+.
- Don't let a stale leader keep writing during an election gap â€” that is split-brain.
- Don't shard keys with `hash(key) % N`; a membership change then remaps nearly all
  keys instead of ~`K/N`.

## Numbers that matter
Coordination cost is dominated by round trips, not CPU. A same-datacenter round
trip is sub-millisecond; a cross-region one is tens to ~100+ ms â€” so synchronous
strong consistency or 2PC across regions can add 100 ms+ per write. Quorum size is
`âŒŠN/2âŒ‹ + 1`; with `N=3`, two nodes must agree, so the cluster survives one failure.
Consistent hashing remaps only ~`K/N` keys on a membership change (vs ~all for
modulo). Use the latency table and the availability-nines math in
`back-of-the-envelope` to price the round trips and to size N for a failure target.

## Interface sketch
The contract is the **guarantee**, stated explicitly per operation, plus the knobs
that produce it:

```
ConsistencyLevel: STRONG | READ_YOUR_WRITES | CAUSAL | EVENTUAL
Quorum:           N (replicas), W (write acks), R (read acks)  // R + W > N â‡’ overlap
Write API:        write(key, value, level=STRONG) -> {version|vector_clock}
Read API:         read(key, level=EVENTUAL)       -> {value, version, stale?: bool}
Conflict policy:  last-write-wins(ts) | version-vector-merge | app-resolver
```

Pin the level on the *operation*, not the datastore â€” most reads can be eventual
while a few (the invariant-bearing ones) demand strong. Return a version so callers
can detect and resolve conflicts.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize a leader-follower-under-partition scenario, a quorum read/write, or a
consistent-hashing ring, use the in-plugin `architecture-diagram` skill. An inline
sketch (`client â†’ leader â†’ [replication stream] â†’ followers`, with the partition as
a dashed/broken arrow) is fine for quick reasoning; do not embed Mermaid.

## Related building blocks
- `data-storage` â€” *pairs with* this: it owns replication and sharding/partitioning (the mechanics), this block supplies the consistency guarantee they enforce.
- `messaging-streaming` â€” *alternative to* coordinating in the data plane: message ordering and exactly-once delivery are the same problem at the transport layer; pair when events must be ordered or deduplicated.
- `resilience-failure` â€” *feeds into* this: it owns failover, retries, and graceful degradation; this block prices the consistency cost of the availability mechanics it provides.
- `caching` â€” *depends on* consistent hashing (the owned-concept lives here) to shard a distributed cache, and trades freshness for speed.
- `back-of-the-envelope` â€” *owned-concept lives in* it: the latency table and availability-nines math used to price round trips and size `N`.
- `service-decomposition` â€” *depends on* this for cross-service consistency (saga/2PC) and for the coordination behind **service discovery** (leader election, etcd/Consul/ZooKeeper).
- `system-design` â€” the orchestrator that *routes here* when a design replicates or coordinates state.

## References
- **`references/deep-dive.md`** â€” CAP vs PACELC in full, consistency-model mechanics, the quorum math, Raft/Paxos at a high level, leader election & split-brain (fencing), consistent-hashing ring + virtual nodes, and 2PC vs saga internals. Read when designing the coordination layer in detail.
- **`references/providers/{generic,aws,gcp}.md`** â€” coordination services (ZooKeeper/etcd/Consul), quorum stores, and the managed consistency knobs (e.g. Spanner external consistency, DynamoDB consistent-read flag) per environment.


---

# Deep Dive & Technical Mechanics

# Consistency & coordination deep-dive

The mechanics that would bloat SKILL.md: the theorems in full, the model
definitions, the quorum math, the consensus and election protocols, the hash ring,
and the commit protocols. Read when designing the coordination layer in detail.

## CAP, then PACELC (the real rule)

**CAP:** when a network **P**artition splits the nodes, a distributed store can keep
either **C**onsistency (every read sees the latest write or errors) or
**A**vailability (every request gets a non-error response), not both. Partitions are
not optional â€” networks drop â€” so the genuine choice is **CP vs AP** *during a
partition*:

- **CP** (e.g. a quorum/consensus store, a single-leader DB): the minority side
  refuses writes (and possibly reads) rather than diverge. Correct, but unavailable
  for some clients until the partition heals.
- **AP** (e.g. Dynamo-style, multi-leader): every replica keeps serving and accepts
  writes locally; divergence is reconciled later via conflict resolution.

CAP only describes the partition case, which misleads people into thinking
consistency is free the rest of the time. **PACELC** fixes that: *if Partition, then
A or C; Else (normal operation), then Latency or Consistency.* The everyday cost of
strong consistency is **latency** â€” the coordination round trip on every write (and
strong read), even when nothing is broken. Most "is it CP or AP" debates are really
the **E**LC half: how much latency you'll pay for fresher reads.

## Consistency models, precisely

Ordered strongest â†’ weakest:

- **Linearizable (strong):** operations appear to take effect instantly at a single
  global point in time, in real-time order. A read returns the most recent committed
  write, full stop. Requires coordination on every write (and often reads).
- **Sequential:** all nodes see operations in the *same* order, but not necessarily
  real-time order. Weaker than linearizable; rarely the explicit target in practice.
- **Causal:** operations with a causeâ†’effect (happens-before) relationship are seen
  in that order by everyone; concurrent (unrelated) operations may be seen in
  different orders. Implemented with version/vector clocks. Good for chat, comments,
  collaborative editing â€” a reply never appears before the message it answers.
- **Read-your-writes (session):** within one client session, reads always reflect
  that session's prior writes. Cheap to provide â€” route the session to the primary
  (or to a replica known to be caught up) for a short window after a write, or carry
  the write's version and read against a replica that has it.
- **Monotonic reads:** a session never sees data move *backward* in time (no reading
  a newer value then an older one). Often bundled with read-your-writes as "session
  guarantees".
- **Eventual:** if writes stop, all replicas converge. Says nothing about *when* or
  about intermediate reads. Highest availability; needs conflict resolution.

A system rarely needs one global model. Pin the level per operation: most reads
eventual, the few invariant-bearing ones strong.

## Quorum math (R + W > N)

With `N` replicas, require `W` acks to commit a write and `R` acks to serve a read.
If `R + W > N`, the read set and write set must **overlap** by at least one replica,
so a read is guaranteed to touch a node holding the latest write â€” giving strong
consistency without a single leader.

- `W = N, R = 1`: fast reads, slow/fragile writes (every replica must ack).
- `R = N, W = 1`: fast writes, slow reads.
- `R = W = âŒŠN/2âŒ‹ + 1` (majority): balanced; tolerates `âŒŠ(Nâˆ’1)/2âŒ‹` node failures.
  With `N=3`, `R=W=2` survives one node down.

Caveats: quorum overlap guarantees you *read* a current copy, but with concurrent
writers you can still get **conflicting versions** at the overlap node â€” resolve via
version vectors or last-write-wins. **Sloppy quorum + hinted handoff** (Dynamo)
keeps accepting writes on substitute nodes during failures, trading the strict
overlap guarantee for availability.

## Consensus: Raft / Paxos at altitude

Consensus protocols get a cluster to agree on an ordered **replicated log** of
operations even though nodes crash and messages are lost â€” the foundation under
strongly-consistent stores, leader election, locks, and config.

- **Raft** (the one to be able to explain): elects a single **leader** for a *term*.
  Clients send writes to the leader; it appends to its log and replicates to
  followers; once a **majority** persist an entry it is *committed* and applied.
  Followers that miss the leader's heartbeat start an election by incrementing the
  term and requesting votes; a candidate wins with a majority. A randomized election
  timeout makes split votes rare.
- **Paxos** solves the same agreement problem (prepare/promise â†’ accept/accepted
  phases) and is famously harder to reason about; Multi-Paxos amortizes it for a log.
  Raft was designed to be the understandable equivalent.

The universal constraint: progress needs a **majority**. A cluster of `2f+1` nodes
tolerates `f` failures; below quorum it **stops** (CP) rather than risk divergence.
This is why control-plane clusters are sized 3 or 5, not 2 or 4 (an even number buys
no extra fault tolerance and worsens split-vote odds).

## Leader election & split-brain

A leader (primary) gives a clean single writer, so failover correctness is the whole
game. The danger is **split-brain**: a partition (or a paused-then-resumed old
leader) leaves *two* nodes each believing they lead, accepting divergent writes.

Defenses:
- **Majority-based election** (Raft/ZooKeeper/etcd): a node can lead only with votes
  from a majority, so two leaders in the same term are impossible.
- **Fencing tokens:** the election hands the new leader a monotonically increasing
  token; downstream stores reject any write carrying a stale token, so a zombie old
  leader cannot commit even if it still thinks it's in charge.
- **Lease/TTL:** a leader holds a time-bounded lease it must renew; if it can't reach
  the coordinator to renew, it must step down before the lease expires.

Tune election timeouts carefully â€” too aggressive and transient latency triggers
**election storms** (constant re-elections that stall the cluster).

## Consistent hashing (owned here)

Plain `serverIndex = hash(key) % N` remaps *nearly every* key when `N` changes (a
node joins/leaves), causing a mass cache-miss / data-shuffle storm. Consistent
hashing fixes this:

1. Hash the output space into a **ring** (e.g. 0 â€¦ 2^160âˆ’1, ends joined).
2. Hash each **node** (by IP/name) onto a point on the ring.
3. Hash each **key** onto the ring; it belongs to the **first node clockwise**.
4. Adding a node steals only the keys between it and its anticlockwise neighbor;
   removing a node hands its keys to the next node clockwise. Only ~`K/N` keys move.

**Virtual nodes (replicas):** one physical node is placed at *many* ring points
(e.g. 100â€“200). This fixes the two weaknesses of the naive ring â€” uneven partition
sizes and lumpy key distribution â€” by smoothing the load (standard deviation drops as
virtual-node count rises). More virtual nodes â‡’ more even distribution but more
metadata; tune to taste. Virtual nodes also **mitigate hotspots**: a celebrity key's
neighbors are spread across different physical nodes instead of piling onto one.

Used in: Dynamo/Cassandra partitioning, Discord, Akamai's CDN, and Maglev network
load balancers. It is why `caching`, `data-storage`, and `load-balancing` can scale
their fleets elastically â€” they all link here for the mechanism.

## 2PC vs saga (multi-node atomicity)

When one logical change spans nodes/services, two shapes exist:

- **Two-phase commit (2PC):** a **coordinator** runs *prepare* (each participant
  locks and votes yes/no), then *commit* or *abort* based on the votes â€” atomic
  all-or-nothing. Cost: participants **hold locks** between phases (reduced
  concurrency), and a coordinator crash after prepare leaves them **blocked**
  (in-doubt) until it recovers â€” a liveness and SPOF hazard. 3PC reduces blocking at
  more message cost but is rarely used. Use 2PC only when atomicity is mandatory and
  the coordination cost is acceptable; it does not scale across regions or services
  well.
- **Saga:** model the change as a sequence of **local** transactions, each with a
  **compensating** transaction that semantically undoes it (refund, cancel, release).
  On failure partway, run the compensations for the steps already done. No global
  lock, no coordinator SPOF â€” but **no isolation**: intermediate states are visible
  (an order can briefly exist "paid but not shipped"), and compensations must be
  idempotent and always eventually succeed. Orchestrated (central coordinator) or
  choreographed (events) â€” see `messaging-streaming` for the event plumbing and
  exactly-once/idempotency that make sagas safe.

Rule of thumb: prefer a saga across service boundaries; reach for 2PC only inside a
tight, low-latency boundary where true atomicity is non-negotiable.

## Common mistakes

- Claiming "CA" â€” there is no CA system once you admit partitions happen.
- Treating CAP as the whole story and ignoring the latency cost of consistency in
  normal operation (PACELC's ELC half).
- Running an even-sized consensus/quorum cluster (no extra fault tolerance).
- Letting an old leader keep writing after a partition (no fencing) â†’ split-brain.
- Using `hash % N` for an elastic fleet â†’ remap storm on every scale event.
- Choosing 2PC for cross-service workflows where a saga would avoid the blocking SPOF.
- Picking strong consistency globally when only a handful of operations need it.

