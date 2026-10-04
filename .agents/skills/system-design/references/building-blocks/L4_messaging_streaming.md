---
name: messaging-streaming
description: This skill should be used when the user designs a "message queue", reaches for "Kafka", "RabbitMQ", "SQS", "Kinesis", "pub/sub", or "event-driven" architecture, asks about "async processing", "background jobs", "stream processing", or wrestles with "exactly-once vs at-least-once", "delivery guarantees", "message ordering", "duplicate handling / dedup", "dead letter queue", "backpressure", "saga orchestration", or "durable workflow". Use it whenever a slow or spiky operation should move off the request path, or two services must be decoupled, even if the user doesn't say "queue".
---

# Messaging & Streaming

Move work off the synchronous request path and decouple producers from
consumers, so a slow, spiky, or failure-prone operation doesn't block the
caller. Getting this wrong is subtle: a queue silently changes the delivery and
ordering guarantees, and under load it can absorb a spike gracefully *or* become
the thing that hides a meltdown until the backlog is unrecoverable.

## When to reach for this
A step is too slow to do inline (image transcode, fan-out, third-party call); the
write path is spiky and needs a buffer to smooth bursts (â†’ `back-of-the-envelope`
for the spike factor); two services must be decoupled so one can fail or deploy
independently; or many consumers need the same event stream. The async hand-off
buys responsiveness, isolation, and elasticity (scale producers and consumers
separately).

## When NOT to
The caller needs the result *now* to proceed (a synchronous read, a balance check
before confirming) â€” a queue only adds latency and a place for work to get lost.
Strong read-after-write within one request. Trivial in-process work that a
function call handles. Don't add a broker before a number or a coupling problem
justifies it (YAGNI): it's a new stateful system to operate, monitor, and reason
about under failure. "We'll need Kafka eventually" is name-dropping, not a
requirement.

## Clarify first
- **Sync or async?** Does the caller need the result inline, or is fire-and-react
  acceptable? This decides whether a queue belongs here at all.
- **Delivery guarantee needed** â€” is a dropped message acceptable (at-most-once),
  or must every message be processed (at-least-once + idempotent consumers)?
- **Ordering** â€” must messages be processed in order, globally or per-key (per
  user, per account)? Global ordering is expensive; per-key usually suffices.
- **Throughput and retention** â€” messages/sec at peak, and how long must they be
  replayable? (â†’ `back-of-the-envelope`.) One-shot work vs. a replayable log.
- **Consumer count and pattern** â€” one worker pool draining a job, or many
  independent subscribers each reading every event?
- **Failure handling** â€” what happens to a message that keeps failing? Where does
  it go, and who looks at it?

## The options

**Sync vs. async â€” settle this before picking a tool.** Stay synchronous when the
caller needs the result to continue and the call is fast and reliable; a direct
request is simpler to build, trace, and reason about. Go async when the work is
slow, spiky, fan-out-heavy, or the caller can react to the result later â€” this
trades immediate consistency and an easy stack trace for responsiveness and
isolation. Only after choosing async do the options below apply. Building
request/reply *over* a queue to fake a synchronous answer is a smell â€” a direct
call is the better design.

**Queue (work/task queue)** â€” one logical consumer group competes to drain
messages; a message is delivered to one worker and removed when acked. *Use when*
there are background jobs or commands to process exactly once-ish, and workers
should scale to drain a backlog.

**Pub/sub (fan-out)** â€” each subscriber gets its own copy of every message;
producers don't know subscribers. *Use when* multiple independent consumers react
to the same event (notify, index, audit) and loose coupling matters.

**Stream (durable, replayable log)** â€” an append-only, partitioned, retained log;
consumers track their own offset and can replay history. *Use when* the design
needs ordering per partition, multiple consumers at different positions, event
sourcing, or reprocessing (â†’ `data-storage` for event sourcing/outbox).

**Durable workflow (orchestration engine)** â€” code that survives process crashes;
the engine persists each step and resumes where it left off, with built-in
retries, timers, and compensation. *Use when* a multi-step process with retries,
human delays, and rollback (a saga) would otherwise become a fragile hand-rolled
mesh of queues, state flags, and cron jobs.

Delivery semantics cut across all of these: **at-most-once** (fire and forget,
may drop), **at-least-once** (retries until acked, may duplicate â€” the practical
default), **exactly-once** (no loss, no dup). True end-to-end exactly-once is
impractical: a broker's "EOS" (e.g. Kafka) is **intra-cluster only**, so across
systems you always implement it as **at-least-once + idempotent/deduped
consumers** (â†’ `api-design` idempotency keys). See
`references/deep-dive.md` for the mechanics.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Queue (work queue) | Decouples + buffers; scale workers to drain backlog | At-least-once means duplicates; ordering not guaranteed across workers | Replay or many independent consumers are needed â†’ stream/pub-sub |
| Pub/sub (fan-out) | One event, N decoupled reactions; add consumers freely | No replay (transient); slow subscriber can lag or drop; fan-out amplifies load | History/replay or per-key ordering is needed â†’ stream |
| Stream (log) | Ordering per partition, replay, multi-consumer, event sourcing | Operationally heavier; partition key is a hot-shard risk; consumers must manage offsets | Simple one-shot jobs don't need a log â†’ queue |
| Durable workflow | Crash-safe long-running sagas; retries/compensation built in | New runtime + programming model; latency overhead; lock-in to engine semantics | A single async step with no orchestration â†’ plain queue |
| At-least-once delivery | No message loss under retry/crash | Duplicates â€” consumers must be idempotent (â†’ `api-design` idempotency keys) | Loss is acceptable and dedup cost isn't worth it â†’ at-most-once |
| Exactly-once (effective) | No loss and no duplicate side effects | Cost/complexity; often narrow (within one broker, not across systems) | Idempotent at-least-once is good enough (it usually is) |

## Behavior under stress
A broker's whole job is to absorb a spike â€” but it can also *hide* a meltdown.

- **Backlog growth / unbounded queues:** producers outpace consumers; the queue
  grows past memory, spilling to disk and slowing further. End-to-end latency
  climbs invisibly while throughput looks fine. *Mitigate:* **backpressure** â€”
  bound the queue and shed or 503 producers (with backoff) once full, rather than
  buffering forever. Alarm on queue depth and message age, not just rate.
- **Retry storms / poison messages:** a message that always fails is redelivered
  forever (at-least-once), burning consumer capacity and re-amplifying load on a
  downstream that's already struggling. *Mitigate:* capped retries with
  backoff+jitter, then route to a **dead-letter queue (DLQ)** so the poison
  message stops blocking the line and a human can inspect it. (Retries, backoff,
  DLQ-as-containment, and backpressure are owned by `resilience-failure`.)
- **Duplicate amplification:** under retry, the same side effect (charge, email)
  fires twice unless consumers dedup. *Mitigate:* idempotency keys / dedup table.
- **Hot partition:** in a stream, a skewed partition key (one celebrity, one
  tenant) overloads a single partition while others idle â€” the same hot-key shape
  as `data-storage` sharding. *Mitigate:* better key, sub-partitioning, or batching.
- **Slow consumer in fan-out:** one lagging subscriber backs up or drops; isolate
  consumers so one can't stall the others.

**Monitor:** queue depth, **oldest-message age / consumer lag** (the single best
signal), redelivery/DLQ rate, consumer throughput vs. producer rate, and
end-to-end latency.

## How to apply
1. **Clarify the inputs.** Settle sync vs. async first; if the caller needs the
   result inline, stop â€” no broker. Then answer delivery guarantee, ordering
   scope, throughput/retention, consumer pattern, and failure handling (see
   *Clarify first*).
2. **Pick the shape from the trade-off table.** One worker pool draining jobs â†’
   **queue**; many independent reactions to one event â†’ **pub/sub**; ordering,
   replay, or multiple offsets â†’ **stream**; multi-step retry/compensation saga â†’
   **durable workflow**. Pick the cheapest shape that meets the constraint.
3. **Set the key knobs.** Choose the delivery semantic (at-least-once + idempotent
   consumers is the default), the ack point (after-process vs. before), the
   partition/ordering key, retention window, and retry cap before the DLQ.
4. **Stress-test the choice.** Walk backlog growth, retry storms / poison
   messages, duplicate amplification, hot partition, and slow fan-out consumer.
   Add backpressure, a DLQ, and dedup where each applies.
5. **Size it with numbers.** Compute peak produce vs. sustained consume rate,
   `consume_rate âˆ’ produce_rate` drain, partition count vs. consumer parallelism,
   and storage = rate Ã— message size Ã— retention (â†’ `back-of-the-envelope`).
6. **Pick a provider.** Default to the generic recipe; only read a provider file
   if the user names a cloud and a managed limit changes the choice.

## Dos and don'ts
**Do**
- Settle sync vs. async before naming any broker; keep synchronous work synchronous.
- Default to at-least-once and make consumers idempotent (â†’ `api-design` keys).
- Bound queues and apply backpressure; alarm on oldest-message age / consumer lag.
- Cap retries with backoff+jitter, then route poison messages to a DLQ.
- Define the message envelope (`message_id`, schema version, key, `trace_id`) up front.

**Don't**
- Don't add a broker "for scale later" before a number or coupling problem justifies it.
- Don't build request/reply over a queue to fake a synchronous answer.
- Don't reach for exactly-once when idempotent at-least-once already suffices.
- Don't buffer an unbounded backlog â€” it hides a meltdown until it's unrecoverable.
- Don't pick a global ordering guarantee when per-key ordering is enough.

## Numbers that matter
Quantify before choosing: peak produce rate vs. sustained consume rate (if
producers can outrun consumers for long, backpressure and a depth alarm are
required), retention window (drives storage = rate Ã— message size Ã— retention), and
partition count (caps consumer parallelism â€” one consumer per partition per
group). A backlog drains at `(consume_rate âˆ’ produce_rate)`; if that's negative,
it never drains. Use `back-of-the-envelope` for the spike factor, message sizes,
and storage; don't restate its tables here.

## Interface sketch
A message is a contract. Define it explicitly, not as "an event":
- **Envelope:** stable `message_id` (for dedup), `type`/`schema_version`, a
  `partition_key`/ordering key, `timestamp`, and a `trace_id` for correlation.
- **Payload:** a versioned schema. Prefer event facts (`OrderPlaced{order_id,
  total}`) over commands when fanning out; keep it small and forward-compatible.
- **Ack contract:** when does the consumer ack â€” before or after the side effect?
  Ack-after-process gives at-least-once; ack-before gives at-most-once.
- **DLQ shape:** failed messages keep the original envelope plus failure reason
  and attempt count, so they can be inspected and replayed.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the producer â†’ broker â†’ consumer path, fan-out to multiple
subscribers, or the retry â†’ DLQ flow, use the in-plugin `architecture-diagram`
skill. Quick inline sketch: `producer â†’ [queue] â†’ workers â”€failâ†’ [DLQ]`; the main
path solid, the DLQ branch dashed.

## Related building blocks
- `resilience-failure` â€” *owned-concept lives in*: retries/backoff/jitter,
  dead-letter queues, and backpressure as outage containment. This skill names
  them; that one tunes them.
- `api-design` â€” *depends on* its idempotency keys, the mechanism that makes
  at-least-once delivery safe.
- `data-storage` â€” *pairs with* this for event sourcing and the transactional
  outbox; *owned-concept lives in*: the hot-shard/partition-key problem streams inherit.
- `consistency-coordination` â€” *owned-concept lives in*: ordering guarantees,
  exactly-once vs. idempotency, and saga/distributed-transaction theory behind
  durable workflows.
- `back-of-the-envelope` â€” *feeds into* sizing: the produce/consume rates,
  retention, and storage that size the broker.
- `system-design` â€” *the orchestrator* that routes here when work goes async.

## References
- **`references/deep-dive.md`** â€” delivery-guarantee mechanics (acks, visibility
  timeouts, offsets, idempotent/dedup consumers, transactional outbox), ordering
  internals, partitioning, DLQ design, and when durable-workflow engines beat
  hand-rolled queue+retry+saga. Read when designing the messaging layer in detail.
- **`references/providers/{generic,aws,azure,gcp,temporal}.md`** â€” service
  mappings, decision-changing limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Messaging & streaming deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
messaging layer in detail.

## Delivery guarantees â€” what actually happens

The guarantee is a property of the *whole loop* (deliver â†’ process â†’ ack), not
just the broker.

- **At-most-once:** consumer acks *before* processing (or broker fire-and-forgets).
  A crash after ack but before the side effect loses the message. Cheapest, no
  duplicates, drops under failure. Fine for metrics samples, best-effort notifies.
- **At-least-once:** consumer acks *after* the side effect commits. If it crashes
  before acking, the broker redelivers â€” so the side effect can run twice. This is
  the practical default: no loss, but **duplicates are guaranteed eventually**.
- **Exactly-once:** no loss and no duplicate *effects*. True end-to-end
  exactly-once across independent systems is impossible in general; what vendors
  ship is narrow (exactly-once *within one broker/stream*, e.g. Kafka
  transactions writing back to Kafka). The portable answer is **at-least-once
  delivery + idempotent consumers** = "effectively once."

### Making at-least-once safe (idempotency / dedup)
- **Idempotency key:** carry a stable `message_id`; the consumer records processed
  IDs (a dedup table / set with TTL) and skips repeats. Owned mechanism:
  `api-design` idempotency keys.
- **Natural idempotency:** design the side effect so re-applying is a no-op
  (`SET balance = 100` not `balance += 10`; upsert by key not insert).
- **Dedup window:** brokers that offer dedup do it within a time window (e.g.
  minutes) â€” beyond that, duplicates slip through, so the consumer still needs to
  be idempotent for correctness over long retries.

## Acks, visibility timeouts, and offsets (the three models)

- **Ack + redelivery (RabbitMQ, SQS):** broker holds the message "in flight" after
  delivery; if not acked within a **visibility timeout**, it's redelivered. Too
  short â†’ duplicate processing of slow jobs; too long â†’ slow recovery from a dead
  consumer. Tune to p99 processing time.
- **Offset commit (Kafka, Kinesis):** the log is immutable; each consumer group
  stores an **offset** (position). "Ack" = commit the offset. Commit *after*
  processing for at-least-once; the gap between process and commit is the
  duplicate window on crash.
- **Lease/extend:** long jobs extend the lease/visibility periodically (heartbeat)
  so they aren't redelivered mid-flight.

## Ordering

- **No global order for free.** A queue with N competing workers processes
  out of order by construction.
- **Per-key ordering** is the usual real requirement: all events for one user/
  account in order. Achieve it by routing a key to a single partition/FIFO group
  (`partition = hash(key) % partitions`); order holds *within* a partition only.
- **Cost:** ordering serializes a key â€” it caps parallelism and creates the
  **hot-partition** risk (a heavy key can't be spread). FIFO modes also cap
  throughput. Full ordering/consensus theory: `consistency-coordination`.
- A failed message in a strict-order partition blocks everything behind it ("head
  of line blocking") â€” decide whether to halt, skip-to-DLQ, or pause the key.

## Partitioning a stream

- Partition count caps consumer parallelism: at most one consumer per partition
  per group. Over-provision partitions early â€” increasing them later rehashes keys
  and breaks ordering for in-flight keys.
- Choose a partition key that spreads load *and* keeps related events together;
  these pull in opposite directions. Same hot-key/sharding shape as `data-storage`.

## Dead-letter queues (DLQ)

- After a capped number of failed deliveries (backoff + jitter between tries), the
  broker routes the message to a separate DLQ instead of redelivering forever. This
  stops a **poison message** from blocking the line and burning capacity. (Retry
  policy, backoff/jitter, and DLQ-as-containment are owned by `resilience-failure`.)
- Preserve the original envelope + failure reason + attempt count. Build a
  **replay path** (DLQ â†’ fix â†’ re-enqueue) and alarm on DLQ arrival rate â€” a silent
  DLQ is lost data.
- Distinguish **transient** (downstream blip â†’ retry) from **permanent** (bad
  schema â†’ straight to DLQ, don't waste retries) failures.

## Transactional outbox (avoiding the dual-write problem)

Writing to the DB *and* publishing to a broker in one step isn't atomic â€” a crash
between them loses or phantoms an event. The **outbox** pattern: write the event
to an `outbox` table in the *same DB transaction* as the state change; a separate
relay (poller or CDC tail of the log) publishes outbox rows to the broker. This
gives at-least-once publication with no dual-write race. Owned in depth by
`data-storage`; named here because it's how producers safely emit events.

## Sync vs. async decision

Go async only when the caller doesn't need the result to proceed. Async buys
responsiveness and isolation but costs: eventual consistency (the result lands
later), harder debugging (no single stack trace â€” use a `trace_id`), and a new
failure surface. If you find yourself building request/reply *over* a queue to get
a synchronous answer, a direct call is probably simpler.

## Durable workflows vs. hand-rolled queue+retry+saga

A multi-step process â€” reserve inventory, charge card, ship, on failure refund and
release â€” can be built from queues + state flags + retry logic + compensation
handlers. That works until the orchestration logic (timeouts, partial failure,
"which step are we on after a crash?") becomes the bulk of the code and the bugs.

A **durable execution engine** (e.g. Temporal) persists each step's result and
the workflow's position, so a worker crash resumes exactly where it left off;
retries, timers (sleep for days), and compensation are first-class. Reach for it
when: the process is long-running or spans human delays; correctness under partial
failure is critical; you need visibility into in-flight workflows. Skip it when a
single async step suffices â€” the engine is a new runtime, programming model, and
lock-in. Saga/compensation *theory* lives in `consistency-coordination`; this is
the build-vs-buy call for *running* one.

## Common mistakes

- Treating at-least-once as exactly-once â†’ duplicate charges/emails (no idempotency).
- No DLQ â†’ one poison message redelivers forever and stalls the consumer group.
- Unbounded queue, no depth/age alarm â†’ backlog hides a meltdown until it's
  unrecoverable.
- Visibility timeout shorter than processing time â†’ silent duplicate processing.
- Choosing global ordering when per-key would do â†’ throughput ceiling + hot partition.
- Dual-write to DB and broker without an outbox â†’ lost or phantom events.
- Building synchronous request/reply over a queue instead of just calling the service.

