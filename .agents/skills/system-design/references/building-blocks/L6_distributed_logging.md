---
name: distributed-logging
description: This skill should be used when the user designs "distributed logging", "log aggregation", "centralized logs", an "ELK" or "EFK" stack, "log shipping", "structured logging", a "correlation ID" or "trace ID" in logs, "log retention", or "high-volume log ingest". It gives the collect â†’ buffer â†’ ship â†’ index â†’ store â†’ retain pipeline, sampling, ordering, and cold-storage tiering. Use it whenever many services emit logs that must be searched in one place under load, even if the user doesn't say "logging pipeline".
---

# Distributed logging

Move logs from thousands of processes into one searchable place, fast enough to
debug a live incident and cheap enough to keep for months. Getting it wrong is a
classic "ignore failure" miss: the logging pipeline is itself a distributed system
that buckles under the exact traffic spike you most need it during, and a naive
design either drops the evidence or takes down the app it instruments.

## When to reach for this
More than one process emits logs and someone needs to search them together; an
incident requires correlating a request across services; log volume has outgrown
`grep` on a box; or compliance demands retention. The pipeline buys central search,
cross-service correlation, and a durable record decoupled from any single host.

## When NOT to
A single service on one host where `journald` + log rotation is enough â€” a full
pipeline is pure operational overhead (YAGNI). Numeric time-series questions ("what
is p99 latency", "is error rate up") belong to metrics, not log scans â€” that is
`observability`'s job; logs answer "what exactly happened to *this* request". Don't
ship every debug line at full volume before a number shows the volume justifies the
cost; sample first.

## Clarify first
- **Volume and peak** â€” lines/sec and bytes/sec, average and peak (â†’ `back-of-the-envelope`). This sizes every stage.
- **Structured or free-text** â€” can producers emit JSON now, or is there legacy text to parse?
- **Query latency need** â€” interactive search in seconds (hot index) vs. occasional forensic/audit reads (cold archive)?
- **Retention + compliance** â€” how long hot, how long cold, any legal hold or PII redaction requirement?
- **Loss tolerance** â€” may logs be dropped/sampled under overload, or is every line evidence (audit/financial)?

## The options

**Collection (agent on the host)**
- **Sidecar/node agent (Fluentd, Fluent Bit, Vector, Filebeat):** tails files or
  reads stdout, adds metadata, ships out. Use when apps log to files/stdout and you
  want app code untouched â€” the default.
- **Direct-to-bus SDK:** the app writes structured events straight to a transport.
  Use when you control the code and want exact structure, accepting tighter coupling.

**Transport / buffer (the shock absorber)**
- **Agent-side buffer + direct ship to indexer:** simplest; agent disk-buffers and
  retries. Use at low-to-moderate volume with one consumer.
- **Durable log bus (`messaging-streaming`, e.g. Kafka):** producers write to a
  partitioned bus; indexers consume at their own pace. Use at high volume or when
  multiple sinks (search, archive, analytics) read the same stream.

**Index / store (the search backend)**
- **Full-text index (Elasticsearch/OpenSearch â€” the "E" in ELK/EFK):** rich queries,
  expensive RAM/disk. Use when interactive field search matters.
- **Label-indexed store (Loki):** indexes only labels, stores log bodies compressed;
  much cheaper, grep-style queries. Use for high volume where you mostly filter by
  service/label then scan.

**Retention / tiering**
- **Hot index â†’ cold object store (`blob-store`):** keep days of searchable data
  hot, roll older data to compressed objects. Use whenever retention exceeds the
  hot window economically (almost always).

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Node agent (Fluent Bit/Vector) | No app changes; central metadata + routing | One more daemon per host; parsing CPU; agent can lag | You need exact structure â†’ emit structured events from the app |
| Direct-to-bus SDK | Clean structured events, no file parse | Couples app to transport; app blocks/loses logs if bus is down | Coupling/availability hurts â†’ go back to agent + local buffer |
| Agent buffer â†’ direct indexer | Fewest moving parts | Indexer backpressure hits producers; no replay; one sink | Volume spikes or you need >1 sink â†’ add a log bus |
| Durable log bus (Kafka) | Absorbs spikes, decouples, replay, fan-out | Extra system to run; ordering only per-partition; cost | Volume is low and single-sink â†’ drop the bus |
| Full-text index (ES/OpenSearch) | Fast rich field search | RAM/disk hungry; mapping explosions; costly at scale | Cost dominates and queries are label-filtered â†’ Loki |
| Label-indexed (Loki) | Cheap storage at high volume | Weak full-text; slow on high-cardinality scans | You truly need arbitrary field search â†’ full-text index |
| Hot index + cold archive | Cheap long retention | Cold reads are slow/manual to rehydrate | Forensic reads on old data must be fast â†’ widen hot window |

## Behavior under stress
The pipeline's failure mode is that incidents *generate* log spikes â€” an outage
emits floods of errors and stack traces exactly when the pipeline is busiest, so it
must degrade without amplifying the outage.

- **Producer backpressure:** if the indexer slows and agents ship synchronously,
  log calls can block the app. *Mitigate:* bounded local buffer with **drop-newest /
  sample on overflow**, never block the request path. A durable bus moves the
  backlog off the hosts (backpressure + DLQ semantics are owned by `messaging-streaming`).
- **Volume amplification:** one bad deploy logging at debug can 100Ã— volume and blow
  the index. *Mitigate:* per-service rate caps at the agent (rate limiting is owned by
  `resilience-failure`), dynamic sampling, alerts on ingest bytes/sec.
- **Index hot-shard / mapping explosion:** high-cardinality fields (raw user IDs as
  index fields) or one fat shard wrecks the cluster. *Mitigate:* time-based indices,
  bounded field mappings, label discipline.
- **Ordering:** the bus only orders *within a partition*; merged multi-host streams
  interleave. *Mitigate:* sort by event timestamp at query time; carry a monotonic
  sequence or trace span order, don't trust arrival order.
- **Losing the evidence:** dropping logs silently hides the very failure under
  investigation. *Mitigate:* meter and alert on drop/sample rate so loss is visible.

**Monitor:** ingest bytes/sec and lines/sec, end-to-end ship lag, bus consumer lag,
agent buffer fullness + drop rate, index queue/rejection rate, query latency.

## How to apply
1. **Clarify the inputs** â€” pin volume (avg + peak bytes/sec), structured-vs-text,
   query-latency need, retention, and loss tolerance (see *Clarify first*). If volume
   is tiny and single-host, stop â€” host-local logs suffice (YAGNI).
2. **Pick stages from the trade-off table** â€” choose a collector, decide whether a
   durable bus is warranted (volume/spike/multi-sink), pick the index backend by the
   query need, and choose the hot window + cold tier.
3. **Set the key knobs** â€” mandate a structured schema with a **correlation/trace ID**
   on every line, set agent buffer size + overflow policy, sampling rates, index
   rollover (time-based) and shard sizing, and the retention/tiering policy.
4. **Stress-test the choice** â€” walk each item in *Behavior under stress* (producer
   backpressure, a debug-flood deploy, hot shard, ordering, silent drops) and confirm
   the pipeline degrades by sampling/buffering, never by blocking the app.
5. **Size it with numbers** â€” multiply lines/sec Ã— bytes/line Ã— peak factor Ã— retention
   to get hot index GB and cold archive GB/month; confirm the bus partition count and
   indexer fleet cover peak ingest (â†’ *Numbers that matter*).
6. **Pick a provider** â€” default to the generic recipe; open a provider file only if
   the user named a cloud (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Emit **structured** logs (JSON) with a correlation/trace ID stamped at the edge and propagated, so a request is one query.
- Put a **bounded buffer** between producers and the indexer and drop/sample on overflow rather than block the app.
- Use a durable log bus once volume spikes or more than one sink reads the stream.
- Tier aggressively: short hot window for search, compressed cold archive for retention.
- Meter ingest rate, ship lag, and drop rate, and alert on them â€” invisible loss is the trap.

**Don't**
- Don't let a logging call block or crash the request path; logging is best-effort by default.
- Don't index high-cardinality free-form fields â€” it explodes the cluster; keep labels bounded.
- Don't trust arrival order for causality; sort by event time / sequence (â†’ `sequencer`).
- Don't re-teach metrics/alerting here or set SLOs in logs â€” that's `observability`.
- Don't keep everything hot forever to avoid cold reads; size the hot window to the debugging window.

## Numbers that matter
Size the pipeline from volume: lines/sec Ã— bytes/line gives ingest bytes/sec; a few
KB/line at tens of thousands of lines/sec is already 100s of MB/s and TBs/day. Hot
index storage â‰ˆ daily bytes Ã— hot-days Ã— (1 + replica + overhead); cold archive â‰ˆ
daily bytes Ã— retention-days, compressed ~5â€“10Ã—. Apply a peak multiplier for incident
floods. Don't restate latency/QPS/storage rules of thumb here â€” pull them from
`back-of-the-envelope`.

## Interface sketch
A log line is a contract: a **structured event**, not a string. Minimum fields:

```
{ "ts": "2026-05-29T12:00:00.123Z", "level": "ERROR", "service": "checkout",
  "host": "pod-7", "trace_id": "abc123", "span_id": "f9", "msg": "charge failed",
  "user_id": "u42", "err": "timeout", "latency_ms": 812 }
```

`ts` is the event time (sort key at query); `trace_id`/`span_id` correlate across
services; `level` and `service` are bounded **index labels**; high-cardinality values
(`user_id`) stay as searchable body fields, not index keys. The bus partition key is
usually `service` or `trace_id` to keep a request's lines ordered together.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping, quotas/limits,
and provider-specific trade-offs. If no file exists for that provider, the generic
recipe is the answer.

## Diagram
To visualize the pipeline (producers â†’ agents â†’ bus â†’ indexer/search + archive sink)
or the overflow/degradation path, use the in-plugin `architecture-diagram` skill â€”
draw the durable bus as the buffer between producers and sinks, the cold-archive sink
with a `blob-store` color, and the drop-on-overflow path as a dashed arrow.

## Related building blocks
- `observability` â€” *owned-concept lives in* the three-pillars view: metrics, traces, alerting, and SLO/SLIs are taught there; logs are one pillar, and *what* to alert on is its job, not this skill's.
- `messaging-streaming` â€” *depends on* it for the durable log bus: delivery guarantees, ordering, backpressure, and DLQ semantics are owned there; this skill just uses the bus as transport.
- `blob-store` â€” *feeds into* it for cold log archival: durability, tiering, and lifecycle of the compressed cold objects live there.
- `sequencer` â€” *pairs with* this when ordering across hosts matters; monotonic IDs and clock-skew handling are owned there.
- `system-design` â€” *owned-concept lives in* the orchestrator: the reasoning loop, the trade-off method, and the ten failure modes. *Feeds into* the wider design.

## References
- **`references/deep-dive.md`** â€” buffering and backpressure mechanics, sampling strategies, structured-logging + correlation-ID propagation, index lifecycle/rollover, ordering, and cold tiering. Read when designing the pipeline in detail.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” service mappings, limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Distributed logging deep-dive

Mechanics that would bloat SKILL.md. Read when designing the pipeline in detail.

## The pipeline stages

`collect â†’ buffer â†’ ship â†’ index â†’ store â†’ retain`. Each stage is a place a spike
can stall. The art is making every stage shed load gracefully so an incident's log
flood never feeds back into the application.

- **Collect** â€” an agent (Fluent Bit, Vector, Fluentd, Filebeat) tails files or reads
  the container stdout stream, parses/enriches (add `host`, `pod`, `region`, `service`),
  and forwards. Fluent Bit/Vector are lightweight (C/Rust) node agents; Fluentd is
  heavier with more plugins. Keep parsing cheap â€” regex parsing of free-text at the
  agent is a common CPU sink; prefer structured input.
- **Buffer** â€” a bounded queue between collect and ship. Local disk buffer on the
  agent survives short indexer outages; a durable bus survives long ones and fans out.
- **Ship** â€” push or pull to the indexer/sink. Batch and compress; one request per
  line melts the network and the indexer.
- **Index** â€” build the search structure (inverted index for full-text, or label
  index for Loki). Most expensive stage in RAM and disk.
- **Store + retain** â€” hot searchable tier, then roll to cold object storage.

## Buffering and backpressure

The cardinal rule: **logging is best-effort and must never block or crash the app.**
Concretely:

- Use an **async, bounded** in-process buffer (ring buffer / bounded channel). When
  full, choose an overflow policy explicitly: drop-newest, drop-oldest, or sample.
  Never an unbounded queue (it becomes an OOM) and never a synchronous blocking write
  to the network on the hot path.
- The agent's **disk buffer** rides out indexer hiccups and retries with backoff. Size
  it to cover the longest expected sink outage at peak volume â€” that is a real GB
  number, not "some".
- A **durable bus** (`messaging-streaming`) moves the backlog off the application
  hosts entirely: producers write and move on, consumers (indexer, archiver) read at
  their own pace and replay after an outage. Delivery guarantees, consumer-group
  backpressure, ordering, and DLQ behavior are owned by `messaging-streaming`; this
  pipeline just relies on them.

Backpressure must terminate at a *drop or sample*, never at the user request. If the
only thing throttling producers is the indexer being slow, an indexer incident
becomes an application incident.

## Sampling strategies

Sampling trades completeness for survivability and cost. Pick per log class:

- **Keep all errors/warns, sample info/debug.** The cheapest high-value policy â€” you
  almost always want every error but not every health-check line.
- **Head sampling** â€” decide at emit time (e.g. keep 10% of debug). Simple, cheap,
  but may drop the one line you needed.
- **Tail sampling** â€” buffer a trace's lines and keep the whole trace only if it
  errored or was slow. Far better signal, needs the trace's lines grouped (partition
  by `trace_id`) and short buffering.
- **Dynamic / rate-capped** â€” per-service ceiling (e.g. max N lines/sec/service); a
  runaway debug deploy gets clamped instead of blowing the cluster.

Always **meter the sample/drop rate and alert on it.** Silent dropping hides the
failure you are debugging â€” that is the "ignore failure" trap in disguise.

## Structured logging and correlation IDs

- **Structured (JSON or key/value)** logs are queryable as fields; free text forces
  fragile regex at index time. Standardize a schema across services: `ts`, `level`,
  `service`, `host`, `trace_id`, `span_id`, `msg`, plus typed fields.
- **Correlation / trace ID**: generate at the system edge (gateway/LB) if absent,
  propagate through every hop (HTTP header like `traceparent`, message metadata, RPC
  context), and stamp it on every log line. This is what turns "search 8 services by
  hand" into one query. The propagation convention and the metrics/traces side of this
  are owned by `observability`; here it is just a mandatory field on the log event.
- Keep **index labels bounded** (low cardinality: `service`, `level`, `region`).
  Put high-cardinality values (`user_id`, `request_id`) in the *body* as searchable
  fields, not as index keys â€” high-cardinality index fields cause mapping explosions
  and hot shards.

## Index lifecycle and rollover

- **Time-based indices** (e.g. one index per day/hour, or rollover at a size/age
  threshold) let retention be "delete old indices" â€” cheap and atomic â€” instead of
  per-document deletes.
- **Shard sizing**: too many tiny shards waste cluster memory; one giant shard becomes
  a hot spot. Aim for moderate, even shards; let rollover cap shard size.
- **Tiered nodes** (hot/warm/cold) move aging indices to cheaper, slower hardware
  before archival. ILM/lifecycle policies automate the hops.

## Ordering

A durable bus orders messages **only within a partition**. Logs merged from many
hosts/partitions interleave, and clocks across hosts skew. Therefore:

- Treat **arrival order as meaningless** for causality. Sort by the **event timestamp**
  carried in the line at query time.
- For strict per-request order, partition the bus by `trace_id` so one request's lines
  land on one partition in order, and/or carry a monotonic sequence/span order.
- For a globally monotonic ordering key, use `sequencer` (Snowflake-style IDs); clock
  skew and monotonicity are its domain.

## Cold tiering to object storage

- Roll data out of the hot index once it ages past the **debugging window** (often
  7â€“30 days) into compressed objects in `blob-store`. Logs compress well (~5â€“10Ã—).
- Cold reads are **slow and often manual** (rehydrate / re-index a day's archive, or
  query in place with a query engine). That is acceptable for audit/forensics; if old
  data needs fast search, widen the hot window instead â€” and pay for it.
- Object-store **lifecycle rules** (transition to colder classes, then expire) enforce
  retention automatically. Durability, tiering classes, and lifecycle are owned by
  `blob-store`.
- Encrypt and redact: PII often must be masked before archive, and legal holds may
  freeze deletion. Bake redaction into the pipeline (at the agent or a stream
  processor), not as an afterthought.

## Common mistakes

- A logging call that blocks the request thread on a slow sink (turns a sink outage
  into a user-facing outage).
- Unbounded in-memory buffer â†’ OOM during the exact spike it was meant to absorb.
- Indexing high-cardinality fields â†’ mapping explosion and hot shards.
- One huge "logs" index with no rollover â†’ cannot delete old data cheaply, retention
  becomes a crisis.
- Silent sampling/drop with no metric â†’ the incident's evidence vanishes invisibly.
- Trusting arrival order across hosts as causal order.
- Keeping everything hot "just in case" â†’ the cluster cost balloons; tier instead.

