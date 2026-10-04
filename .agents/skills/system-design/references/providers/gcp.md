# GCP Cloud Architecture & Service Mapping

Comprehensive mapping of system design building blocks to GCP managed services and architecture patterns.

---

## Building Block: api-design

# API design â€” GCP

## Service mapping
- **API Gateway** â€” managed gateway for REST/HTTP backends (Cloud Run, Functions,
  App Engine) configured from an OpenAPI spec; API keys, auth, basic quotas. The
  simple default for a public REST contract on serverless backends.
- **Apigee** â€” full enterprise API management: versioning, quotas/spike-arrest,
  transformation, monetization, analytics. Use when you need rich policy,
  developer portals, and product packaging.
- **Cloud Endpoints** â€” gateway/ESP proxy for REST *and gRPC* (OpenAPI or protobuf
  config), with auth and monitoring; sits in front of GKE/Compute/Cloud Run.
- **Global External HTTP(S) Load Balancer** â€” L7 routing with gRPC and WebSocket
  support for service traffic (pairs with `load-balancing`).

## When to pick which
API Gateway for a lightweight managed front on serverless; Endpoints when you need
gRPC or an ESP sidecar in front of GKE; Apigee for enterprise policy/quotas/portal;
the HTTP(S) LB for plain global routing of gRPC/WebSocket.

## Limits / things that bite (verify against current docs)
- API Gateway / serverless backends (Cloud Run, Functions) have **request timeout
  and payload caps** â€” long calls must go async; tune the backend timeout too.
- Quota/spike-arrest semantics differ: Apigee's spike-arrest smooths bursts,
  API Gateway's quotas are coarser â€” know which you're getting.
- Apigee is a heavyweight, higher-cost platform; API Gateway is far lighter â€”
  don't reach for Apigee unless its policy/portal features are needed.
- WebSocket via the HTTP(S) LB has connection-duration and timeout caps; long-lived
  clients reconnect.

## Pitfalls
- Reaching for Apigee (cost, complexity) when API Gateway or Endpoints suffices.
- Assuming the gateway provides idempotency â€” it doesn't; build the idempotency-key
  store (Firestore/Memorystore with TTL).
- Forgetting Cloud Run/Functions backend timeouts compound with the gateway's.
- Lock-in via Apigee policies and Endpoints ESP config that don't port out.


---

## Building Block: blob-store

# Blob store â€” GCP

## Service mapping
- **Cloud Storage (GCS)** â€” the object store. Buckets + objects, strong global read-after-write,
  object versioning, resumable + multipart uploads, signed URLs, lifecycle (Object Lifecycle
  Management). The default.
- **Storage classes** (the tiering knob, set per-bucket default or per-object) â€” *Standard* (hot),
  *Nearline* (â‰ˆ once-a-month access), *Coldline* (â‰ˆ once-a-quarter), *Archive* (cheapest at rest,
  for rarely-read retention). **All classes have millisecond first-byte latency** â€” the colder
  classes differ by price, minimum storage duration, and retrieval cost, *not* by a rehydration
  wait. *Autoclass* moves objects between classes automatically by access.
- **Location type** (the durability/geo knob) â€” *regional* (single region), *dual-region*, or
  *multi-region* (geo-redundant); GCS handles intra-location durability internally.
- **Cloud CDN / Media CDN** â€” CDN in front of a GCS origin (â†’ `content-delivery`).

## When to pick which
Standard for served objects; Nearline/Coldline for backups by access frequency; Archive for
long-term retention. Regional for lowest cost/latency; multi-region for geo-redundancy and
availability across a region loss. Autoclass when access patterns are unpredictable.

## Limits / things that bite (verify against current docs)
- Resumable upload is the recommended path for large objects and flaky links (session-URI based,
  query-and-resume); multipart (XML API) also exists for S3-compatibility.
- Colder classes carry **minimum storage durations** and per-GB **retrieval fees** â€” early deletes
  and tiny churny objects can cost more than Standard despite the lower storage rate.
- **Egress to the internet is billed** (and inter-region transfer); Cloud CDN cuts egress + origin load.
- Request rate auto-scales but ramps; very spiky write bursts to a fresh bucket can need a warm-up.
- Unlike most stores, even Archive is instant-access â€” do not assume an archive "thaw" step.

## Provider-specific trade-offs
- Integrates with IAM, Pub/Sub notifications (object events â†’ `messaging-streaming`), and
  BigQuery/Dataflow for data-lake reads; convenient but GCP-specific.
- Multi-region buckets simplify geo-redundancy without app-managed replication, at higher $/GB.

## Pitfalls
- Deleting Nearline/Coldline/Archive objects before the minimum duration â†’ early-deletion charges.
- No lifecycle rule to expire noncurrent versions or tier down â†’ silent storage growth.
- Serving popular objects from origin without Cloud CDN â†’ egress blowup.
- Over-broad or long-lived signed URLs â€” scope to object + method, keep expiry short.


---

## Building Block: caching

# Caching â€” GCP

## Service mapping
- **Memorystore for Redis / Valkey** â€” managed Redis; Basic tier (single node) and
  Standard tier (replicated with automatic failover); read replicas for read
  scaling; Cluster mode for sharded horizontal scale.
- **Memorystore for Memcached** â€” managed Memcached; auto-scaled nodes for a
  simple distributed object cache.
- **Cloud CDN** â€” edge caching for static/media (â†’ `content-delivery`).

## When to pick which
Redis Standard for HA + failover and data structures; Redis Cluster when one node
isn't enough; Memcached for a plain horizontally-scaled object cache; read
replicas when reads dominate but the dataset fits one shard.

## Limits / things that bite (verify against current docs)
- Basic tier has **no failover and no SLA** â€” a node restart loses the cache.
- Instances are regional and VPC-attached; cross-region access adds latency.
- Per-instance memory and network throughput caps; a hot key saturates one shard.
- Maintenance windows can cause brief failovers â€” design for transient
  unavailability.

## Pitfalls
- Using Basic tier in production and being surprised by data loss on maintenance.
- Forgetting Memorystore is regional â€” multi-region needs your own replication.
- Assuming Memcached tier offers persistence/replication (it doesn't).


---

## Building Block: consistency-coordination

# Consistency & coordination â€” GCP

Only the managed pieces that change the generic recipe. For anything not listed,
the generic recipe (self-hosted etcd/ZooKeeper, Cassandra, etc.) is the answer.

## Service mapping
- **Cloud Spanner** â€” the decision-changing service: a horizontally-sharded SQL
  database offering **external consistency** (the strongest practical guarantee â€”
  linearizable *and* globally serializable transactions) **across regions**. It
  achieves this with **TrueTime** (GPS + atomic-clock bounded clock uncertainty) plus
  Paxos per shard. Reach for Spanner when you genuinely need global strong
  consistency with SQL and are willing to pay for it; it removes the usual "you can't
  have strong consistency across regions cheaply" constraint â€” at a real cost.
- **Firestore / Datastore** â€” strongly consistent reads and queries within a region;
  multi-region modes add availability. Document model, not tunable-per-query like
  Cassandra.
- **Bigtable** â€” single-cluster strong consistency; replicated/multi-cluster routing
  becomes **eventually consistent** across clusters. Consistent-hashing-style
  range/row-key sharding (mind hot row-key ranges).
- **No managed ZooKeeper/etcd primitive** â€” GKE runs etcd for Kubernetes' own control
  plane; for app-level coordination, run etcd/ZooKeeper yourself or use Spanner/
  Firestore transactions as the coordination point.

## Limits / things that bite (verify against current docs)
- Spanner's external consistency is **not free**: writes incur a commit-wait tied to
  TrueTime uncertainty and cross-region Paxos round trips â€” budget the added write
  latency; price scales with node/processing units.
- Bigtable multi-cluster replication is eventually consistent; don't assume a write
  in cluster A is instantly visible in cluster B.
- Firestore has per-document and transaction contention limits (hot documents
  throttle).

## Pitfalls
- Reaching for Spanner when regional strong consistency (Firestore/Cloud SQL) or
  eventual consistency would meet the requirement â€” paying for global serializability
  no one asked for (YAGNI).
- Assuming Bigtable cross-cluster reads are strongly consistent.
- Ignoring Spanner commit-wait latency in a tight write-path budget.


---

## Building Block: content-delivery

# Content delivery â€” GCP

## Service mapping
- **Cloud CDN** â€” the general CDN; caches at Google's edge in front of an external
  HTTPS load balancer (the LB *is* the front door), pulling from a backend bucket
  or backend service. Use for static/media and cacheable dynamic responses.
- **Media CDN** â€” a separate product tuned for **large-scale video/media** delivery
  (built on YouTube's edge); choose it over Cloud CDN when streaming volume,
  segmented HLS/DASH, or huge file egress dominates.
- **Cloud Storage (GCS)** â€” the usual static/media origin (backend bucket).
- **Cloud Load Balancing** â€” Cloud CDN is enabled *on* the external HTTPS LB; global
  anycast routing comes from the LB (â†’ `load-balancing`).

## When to pick which
Cloud CDN for web static assets and general caching tied to your HTTPS LB; Media CDN
when the workload is video/large-file streaming at scale; GCS backend bucket as the
simplest static origin.

## Limits / things that bite (verify against current docs)
- Cloud CDN requires (and is configured through) an **external HTTPS load
  balancer** â€” you don't point it at a raw origin; the LB defines backends.
- **Cache mode** matters: `CACHE_ALL_STATIC` vs `USE_ORIGIN_HEADERS` vs
  `FORCE_CACHE_ALL` change what gets cached â€” pick deliberately.
- Cache-key policy (include/exclude query strings, host, protocol) drives hit rate;
  default may over- or under-cache.
- Invalidation propagation is not instant; prefer versioned URLs. Egress is the
  dominant cost and varies by region/tier.

## Pitfalls
- Expecting Cloud CDN without setting up the HTTPS LB + backend bucket/service.
- Using Cloud CDN for heavy video when Media CDN is the fit (or vice versa).
- Wrong cache mode â†’ caching nothing, or caching personalized responses.
- Lock-in via LB + CDN config and Media CDN-specific features.


---

## Building Block: data-storage

# Data Storage â€” GCP

## Service mapping â†’ options
- **Cloud SQL** (Postgres/MySQL/SQL Server) â€” managed relational; backups, read
  replicas, HA failover. The default managed SQL for single-region scale.
- **Spanner** â€” horizontally-scalable relational: SQL + ACID transactions
  *across shards* and regions, with strong (external) consistency. The rare store
  that scales writes without giving up joins/transactions â€” at premium cost.
- **Bigtable** â€” wide-column (the original Bigtable); huge write throughput,
  sorted row keys for range scans. Maps to the wide-column option.
- **Firestore** â€” managed document store with real-time sync; maps to the
  document option for app/mobile data.
- **Memorystore** â€” managed Redis/Memcached (see `caching`), not a system of
  record.

## Limits / things that bite (verify against current docs)
- **Bigtable:** performance hinges on **row-key design** â€” monotonically
  increasing keys (timestamps, sequential IDs) hot-spot one node ("hotspotting");
  use a salted/field-promoted key for even spread. No secondary indexes and no
  joins â€” design the row key around your queries.
- **Spanner:** avoid monotonic primary keys for the same hot-spotting reason;
  capacity is provisioned in **nodes/processing units** and strong cross-region
  consistency adds commit latency. Powerful but the most expensive option.
- **Cloud SQL:** vertical scale and connection limits are bounded by instance
  size; read replicas are async and can lag.

## Provider-specific trade-offs
- Spanner removes the classic "shard and lose transactions" trade-off but is
  GCP-only and priced for it â€” justify with a real cross-shard-transaction need.
- Bigtable/Firestore lock you into their data and query models; migrating off is
  real work.

## Pitfalls
- Monotonic row/primary keys in Bigtable or Spanner â†’ hotspotting one node while
  the cluster looks idle.
- Reaching for Spanner when a single Cloud SQL node (or replicas) would serve the
  load â€” paying for scale you don't need (YAGNI).
- Expecting Bigtable to do ad-hoc queries or joins â€” it's query-pattern-first.


---

## Building Block: distributed-logging

# Distributed logging â€” GCP

## Service mapping (generic stage â†’ GCP)
- **Collect:** the **Ops Agent** on GCE; on GKE, logging is built in (a Fluent Bit
  DaemonSet ships container logs to Cloud Logging automatically). Apps can also write
  structured entries directly via the Cloud Logging API/SDK.
- **Buffer / transport:** **Pub/Sub** as the durable log bus â€” Cloud Logging **sinks**
  route matching entries to Pub/Sub for fan-out / stream processing.
- **Index / search:** **Cloud Logging** (Logs Explorer) is the managed hot search tier
  with its own query language; for analytics, route to **BigQuery** via a log sink.
- **Cold archive:** **Cloud Storage** bucket via a log sink, with lifecycle rules to
  Nearline/Coldline/Archive classes (â†’ `blob-store`).

Common recipe: agents/resources â†’ Cloud Logging â†’ **log sinks** fan out to: a logging
bucket (hot, searchable for N days), BigQuery (analytics), Cloud Storage (cold), and/or
Pub/Sub (stream to anywhere).

## Limits / things that bite (verify against current docs)
- **Log buckets** have a configurable retention period; the default is a fixed window â€”
  extend it (and pay) or sink to GCS for long retention.
- **Ingestion** is billed per GB after a free allotment; verbose unsampled logging gets
  expensive fast.
- **Exclusion filters** drop matching entries *before* ingest billing â€” the primary
  cost lever (e.g. drop health-check and 200-OK access logs).
- **Pub/Sub** ordering is only guaranteed with an ordering key within a region; without
  it, messages may arrive out of order.
- BigQuery sink streaming has its own quotas and per-GB cost.

## Provider trade-offs
- Cloud Logging is deeply integrated (auto-collection on GKE, one query surface) but
  long retention and high volume push you to GCS/BigQuery sinks for cost.
- BigQuery is excellent for SQL analytics over logs but is not a low-latency
  tail/search tool â€” use Logs Explorer for that.
- Exclusion filters + sinks are the cost/queryability control plane; design them up
  front. Lock-in: sink config, the query language, and BigQuery schemas don't port.

## Pitfalls
- Not setting **exclusion filters** â†’ paying to ingest health checks and noise.
- Treating BigQuery as interactive log search (it's analytics, not tailing).
- Assuming Pub/Sub preserves order without an ordering key.
- Leaving default log-bucket retention and expecting cheap long-term storage there
  instead of GCS.


---

## Building Block: distributed-search

# Distributed search â€” GCP

## Service mapping
- **Vertex AI Search** (formerly Enterprise Search / Discovery Engine) â€” managed,
  Google-quality search and recommendations over your data; handles indexing,
  ranking, and semantic/keyword retrieval with little tuning. Use when you want a
  high-quality search experience without operating an engine.
- **Self-managed OpenSearch/Elasticsearch on GCE/GKE** â€” when you need full
  engine control, custom analyzers/shard tuning, or cross-cloud portability; the
  generic recipe applies. (GCP has no managed Elasticsearch-API service of its
  own; Elastic Cloud on GCP is a third-party option.)
- **AlloyDB / Cloud SQL full-text** â€” built-in DB full-text for small corpora
  where a separate search system isn't warranted (â†’ `data-storage`).

## When to pick which
Vertex AI Search for a managed, relevance-strong experience with minimal ops and
built-in semantic ranking; self-managed OpenSearch when you need explicit
shard/replica/analyzer control or portability; DB full-text when the corpus is
small enough not to need a cluster (YAGNI).

## Limits / things that bite (verify against current docs)
- Vertex AI Search abstracts the index â€” you trade low-level shard/analyzer
  control for managed quality; verify it supports your filter/facet/freshness
  needs before committing.
- Quotas on data stores, documents, and QPS per project apply.
- Self-managed clusters carry the generic operational burden (heap, merges,
  shard sizing) plus regional/VPC placement affecting latency.

## Pitfalls
- Assuming a drop-in Elasticsearch-API managed service exists natively â€” it
  doesn't; either use Vertex AI Search's model or self-manage / Elastic Cloud.
- Adopting Vertex AI Search then needing custom analyzers/scoring it doesn't expose.
- Treating any of these as a source of truth rather than a reindexable derived copy.
- Lock-in: Vertex AI Search data stores and config don't port to other clouds.


---

## Building Block: dns

# DNS â€” GCP

## Service mapping
GCP also splits zone hosting from global steering â€” most traffic steering happens
in the load balancer, not in Cloud DNS.

- **Cloud DNS** â€” managed authoritative hosting on Google's anycast network. Public
  and private zones, standard record types, DNSSEC, and **routing policies**:
  **Weighted round-robin** and **Geolocation** (answer by client region), plus
  health-checked **failover** for internal/private routing. Apex support is via the
  policy/record set rather than a separate alias type â€” point records at a global
  LB IP.
- **Cloud Load Balancing (global external)** â€” the primary "latency/geo" steerer.
  A single **anycast global IP** front-ends all regions; Google's edge routes users
  to the nearest healthy backend and fails over **without DNS TTL waits**. Prefer
  this over DNS-level geo for speed and fast failover. Edge caching (Cloud CDN) is
  `content-delivery`.
- **Cloud DNS routing policies** cover DNS-level weighted/geo when you specifically
  need answers to differ per client rather than a single anycast IP.

## When to pick which
Default: one global external Application LB on an anycast IP, with Cloud DNS holding
a simple record pointing at it â€” proximity and failover handled at the LB, no TTL
dependency. Reach for Cloud DNS geolocation/weighted policies when you need the
*answer itself* to differ (data residency, canary across distinct IPs).

## Limits / things that bite (verify against current docs)
- DNS-level geo/weighted policies are TTL-bound; the global LB's anycast steering is not.
- Cloud DNS geolocation maps by client region (resolver-influenced), not exact user.
- Per-zone record-set and per-policy item quotas apply.
- Health-checked DNS failover applies mainly to private/internal zones â€” public
  fast failover is the LB's job.

## Pitfalls
- Building DNS-level geo routing when a single global anycast LB IP would be simpler and faster.
- Forgetting DNSSEC key management once enabled (validation breaks = outage).
- Assuming Cloud DNS does latency routing like a managed competitor â€” favor the LB instead.


---

## Building Block: load-balancing

# Load balancing â€” GCP

## Service mapping
GCP unifies most options under **Cloud Load Balancing**, split by layer and scope:
- **Global external Application LB** â€” **L7**, anycast single global IP, host/path
  routing, TLS termination, integrates with Cloud CDN at the edge (cross-region
  steering + caching, â†’ `content-delivery`). The default for global HTTP(S).
- **Regional external Application LB** â€” **L7** scoped to one region when global/
  anycast isn't needed.
- **External passthrough Network LB** â€” **L4** (TCP/UDP); preserves client IP,
  passthrough (no termination), very high throughput.
- **Proxy Network LB** â€” **L4** that terminates TCP (optionally TLS) and proxies.
- **Internal LBs** â€” L4 and L7 variants for private VPC traffic between tiers.
- **Managed Instance Group (MIG)** â€” the autoscaling fleet the LB balances over,
  with health-gated membership (the stateless-tier enabler).

## When to pick which
Global external Application LB for global HTTP(S) with anycast + CDN; regional
Application LB for single-region L7; passthrough Network LB for L4 throughput and
source-IP preservation; internal LBs for tier-to-tier traffic inside the VPC.

## Limits / things that bite (verify against current docs)
- The global Application LB uses **anycast** with Google's edge â€” there's no single
  warm-up cliff like some per-region LBs, but backend MIG capacity and autoscaling
  still bound real throughput.
- **Health checks are central** to membership and to autoscaling/autohealing â€” a
  too-aggressive or too-deep check can evict or recreate healthy instances; tune
  interval, thresholds, and check depth.
- Backend service settings (connection draining timeout, balancing mode by
  RATE/UTILIZATION/CONNECTION, capacity scaler) directly shape distribution â€” set
  them deliberately.
- Network LB is **passthrough** (no TLS termination / no L7 routing) â€” use an
  Application LB or Proxy LB when you need those.

## Pitfalls
- Picking a passthrough Network LB then needing path-based routing or TLS
  termination (wrong layer â€” use Application LB).
- Leaving generated-cookie affinity on instead of externalizing session state.
- Misconfigured balancing mode causing hot backends (e.g. CONNECTION mode for
  uneven request cost â€” prefer RATE/UTILIZATION).
- Lock-in: backend-service config, URL maps, and global anycast IPs don't port to
  other clouds.


---

## Building Block: messaging-streaming

# Messaging & streaming â€” GCP

## Service mapping â†’ the generic options
- **Pub/Sub** â€” managed pub/sub *and* work queue in one; at-least-once by default,
  push or pull subscriptions, built-in dead-lettering and retry policy,
  auto-scaling throughput. The default for both fan-out and async jobs on GCP.
- **Pub/Sub (ordering keys)** â€” opt-in per-key ordering when you set an ordering
  key; off by default.
- **Pub/Sub Lite** â€” cheaper, lower-cost-per-message variant where you provision
  capacity (zonal); use for high-volume, cost-sensitive streaming where you accept
  managing capacity.
- **Dataflow** â€” managed stream/batch processing (Apache Beam) that *consumes*
  Pub/Sub for windowing, aggregation, exactly-once processing within the pipeline.
  Use when you need stream *processing*, not just transport.

## Decision-changing limits (verify against current docs)
- **At-least-once by default** â†’ duplicates happen; consumers must be idempotent.
  Pub/Sub offers an **exactly-once delivery** mode within a subscription (narrower
  scope; verify constraints).
- **Ordering** requires an ordering key and same-region publish; it caps
  per-key parallelism (the usual ordering cost).
- **Ack deadline** is the visibility-timeout analog; extend it for long jobs or
  get redelivery. Message **retention** window bounds replay/seek-to-timestamp.
- **Message size** limit (~10 MB) larger than SQS, but large payloads still favor
  a claim-check via Cloud Storage.

## Provider-specific trade-offs
- One service (Pub/Sub) covers queue + pub/sub, which simplifies the decision but
  means you tune subscriptions (push vs. pull, ack deadline, ordering) rather than
  pick a different product.
- Pub/Sub is not a long-retention replayable log like Kafka by default â€” for
  Kafka semantics use self-managed Kafka on GKE or a partner offering; for stream
  *processing* reach for Dataflow.
- For durable workflows GCP offers **Workflows** (YAML orchestration) and
  **Cloud Tasks** (HTTP task queue with scheduling) â€” compare with Temporal in
  `temporal.md`.

## Pitfalls
- Assuming exactly-once because GCP offers the mode â€” it's per-subscription and
  bounded; keep consumers idempotent.
- Forgetting ordering is off until you set an ordering key.
- Ack-deadline shorter than processing time â†’ silent duplicate processing.
- No dead-letter topic configured â†’ failed messages redeliver until retention ends.


---

## Building Block: observability

# Observability â€” GCP

## Service mapping
- **Cloud Monitoring** (formerly Stackdriver) â€” managed metrics, dashboards,
  **alerting policies**, and **SLO + error-budget objects as first-class features**
  (define an SLI/SLO and burn-rate alerts natively).
- **Cloud Trace** â€” managed distributed tracing; OTLP/OpenTelemetry export.
- **Cloud Logging** â€” managed log ingestion/query + **log-based metrics**; the
  high-volume pipeline concern is `distributed-logging`.
- **Managed Service for Prometheus + Managed Grafana** â€” run the generic PromQL
  stack managed (GMP auto-collects from GKE), for portability.
- **GKE/Cloud Run health checks** â€” liveness+readiness; gating is `load-balancing`.

## When to pick which
- Cloud Monitoring when you want native SLOs/error budgets and burn-rate alerts
  without building them â€” its standout feature.
- Managed Service for Prometheus on GKE for PromQL portability with managed scaling.
- Cloud Trace for low-effort tracing on GCP-hosted services via OTel.

## Limits / things that bite (verify against current docs)
- **Cardinality / active-time-series limits** per metric â€” unbounded labels hit
  ingestion limits and cost.
- **Cloud Logging ingestion + retention is the main cost driver**; log-based metrics
  add cost on top.
- **Alerting policy evaluation period** bounds detection latency for SLO burns.
- Trace sampling is configurable; defaults may under-sample errors.

## Pitfalls
- High-cardinality metric labels hitting per-metric time-series limits.
- Building custom SLO tooling when Cloud Monitoring's native SLOs already do it.
- Lock-in to Cloud Monitoring dashboards/alerting â€” OTel + managed Prometheus/Grafana
  keeps you portable.
- Forgetting log-based metric cost when deriving metrics from high-volume logs.


---

## Building Block: resilience-failure

# Resilience & failure â€” GCP

## Service mapping
- **Redundancy / failover** â€” **regional** (multi-zone) Managed Instance Groups
  are the default fault isolation; **multi-region** for region loss. MIG
  autohealing replaces failed instances; the global external HTTP(S) Load
  Balancer routes around unhealthy backends (health checks â†’ `load-balancing`).
- **Global failover routing** â€” the global LB + Cloud DNS route to the nearest
  healthy backend and fail over across regions automatically.
- **Rate limiting / load shedding** â€” **Cloud Armor** rate-based ban rules and
  WAF at the edge; **Apigee** / API Gateway for per-key quota and spike-arrest
  (token-bucket-style) throttling.
- **Retries / circuit breaking** â€” Cloud client libraries retry with backoff +
  jitter; **Traffic Director / Anthos Service Mesh** (Envoy) adds proxy-level
  timeouts, retries, circuit breaking, and outlier ejection.
- **Queue containment** â€” **Pub/Sub** (with dead-letter topics) â†’ `messaging-streaming`.
- **Shared limiter store** â€” **Memorystore (Redis)** for counters.

## Limits / things that bite (verify against current docs)
- Regional MIGs survive a zone loss transparently; multi-region failover depends
  on async cross-region replication and can lose recent writes.
- Cloud Armor rate-based rules use a rolling window with coarse granularity and a
  configurable ban duration â€” not a precise per-request limiter.
- Apigee spike-arrest smooths bursts (per-second/minute) and is enforced per
  message processor, so effective limits can differ from the nominal rate.

## Provider-specific trade-offs
- GCP's **global** anycast LB makes multi-region front-ends simpler than
  elsewhere â€” but the data tier's replication/consistency is still the hard part
  (â†’ `consistency-coordination`).
- Regional redundancy is the cheap default; multi-region is the cost/complexity
  step-up to justify against the SLA.

## Pitfalls
- Deploying a **zonal** (not regional) MIG and losing everything when that zone
  fails.
- Stacking client-library retries with mesh retries (load multiplier).
- Relying on Cloud Armor for fine-grained per-user limits â€” use Apigee/app-level.


---

## Building Block: sequencer

# Sequencer â€” GCP

## Service mapping
GCP has **no dedicated ID-generation service** â€” the generic recipe (Snowflake
library, ULID/UUIDv7, or a ticket row) applies. The notable GCP-specific twist is
**Cloud Spanner**, whose docs *actively warn against* monotonic primary keys:

- **Cloud Spanner** â€” a globally-distributed SQL DB. A timestamp-ordered or
  auto-incrementing primary key creates a **hotspot**: all new writes land on the
  same key range / split, defeating Spanner's horizontal scaling. Spanner's own
  guidance is to use a **UUID** (v4) primary key, **bit-reverse** a sequential
  key, or hash-prefix it. Spanner also offers a built-in `GENERATE_UUID()` and
  bit-reversed sequences for exactly this reason. (The hotspot/partition concept
  is owned by `data-storage`.)
- **Cloud SQL (MySQL/Postgres)** â€” native `AUTO_INCREMENT`/`SEQUENCE` and the
  ticket-server pattern work as in generic; single writer serializes a sequence.
- **Bigtable / Firestore** â€” like Spanner, sequential row keys/document IDs hotspot
  a single tablet; Firestore auto-generated IDs are random by design for this
  reason.
- **GKE / Cloud Run / Compute Engine** â€” host the Snowflake/ULID library; node-ID
  assignment under autoscaling is the open problem (lease it, or use ULID/UUIDv7).
- **Memorystore (Redis)** â€” `INCR`/`INCRBY` for an atomic counter or range
  allocator.

## Limits / things that bite (verify against current docs)
- **Spanner split hotspotting** is the headline constraint: monotonic keys cap
  throughput regardless of node count. Use UUID, bit-reversed, or hashed keys.
- **Cloud Run / GKE pods have no stable identity** under autoscaling â€” static
  Snowflake node ids are unsafe; lease them or avoid needing them.
- Clocks are NTP-synced but can step; keep the rewind guard.

## Provider-specific trade-offs
- Spanner/Bigtable/Firestore push you toward random or time-prefixed-but-
  high-cardinality IDs (UUIDv7/ULID, or bit-reversed sequences) â€” a hard design
  constraint, not a style choice.
- `GENERATE_UUID()` and bit-reversed sequences keep ID logic in the DB (no app
  library) at the cost of losing client-side generation.

## Pitfalls
- Monotonic / timestamp-leading primary key in Spanner or Bigtable â†’ split/tablet
  hotspot and throttling.
- Static Snowflake node ids on Cloud Run/GKE â†’ duplicates under scale-out.
- Expecting a managed "ID service" â€” there isn't one; you run a library or a
  DB-side function.


---

## Building Block: service-decomposition

# Service decomposition â€” GCP

## Service mapping
- **Compute for services** â€” GKE (Kubernetes), Cloud Run (managed containers,
  scale-to-zero), or Cloud Functions for event-driven services.
- **API gateway / front door** â€” API Gateway (managed) or Apigee (full API
  management); Cloud Load Balancing for routing.
- **Service discovery** â€” Kubernetes DNS on GKE; Cloud Run service URLs; Traffic
  Director for mesh-managed discovery.
- **Service mesh** â€” Anthos Service Mesh / Traffic Director (Envoy-based) or
  self-managed Istio on GKE.
- **Cross-service workflows / saga** â€” Workflows (orchestration) or Pub/Sub
  (choreography); transactional outbox via Pub/Sub + a DB change stream.

## When to pick which
Cloud Run for stateless services you want managed + scale-to-zero; GKE when you
need full Kubernetes/mesh; API Gateway for lightweight fronting, Apigee for rich
API management; Workflows for orchestrated sagas.

## Limits / things that bite (verify against current docs)
- Cloud Run request timeout cap and cold starts affect chatty synchronous chains.
- Apigee is powerful but heavy/costly; API Gateway is lighter but less featured.
- Traffic Director / Anthos Service Mesh add Envoy overhead and config surface.

## Pitfalls
- Cloud Functions for deep synchronous fan-out (cold-start + latency stacking).
- One Cloud SQL instance shared across services (distributed monolith).
- Expecting cross-service ACID â€” use saga/outbox via Workflows/Pub-Sub.


---

## Building Block: sharded-counters

# Sharded counters â€” GCP

Only the contention/atomicity differences that change the recipe. Default to the
generic recipe; this maps it to GCP services.

## Service mapping
- **Firestore distributed counter** â€” Google's documented pattern is *exactly*
  write-sharding: split a counter into N sub-documents, increment a random shard
  in a transaction, sum the shards on read. Firestore caps sustained writes to a
  single document (~1/sec), so sharding is mandatory above trivial rates.
- **Bigtable counter** â€” atomic increment on a cell (`ReadModifyWrite`). Distribute
  load by designing the **row key** to avoid hot-spotting (salt/field-promote the
  key); a sequential or single hot row key serializes on one tablet.
- **Spanner** â€” transactional `UPDATE â€¦ SET c = c + 1`; exact and strongly
  consistent, but a single hot row contends on locks â€” shard the row (N rows
  summed) for write-heavy counts.
- **Memorystore for Redis / Valkey** â€” managed Redis for the fast path: `INCR`,
  HyperLogLog, key sharding. Use for microsecond tallies and HLL uniques.

## When to pick which
Firestore distributed counter for app-level counts that must be durable (use the
built-in shard pattern); Bigtable when increments are huge-scale and you control
the row-key design; Spanner when the count must be transactionally exact (shard
the row only if writes are hot); Memorystore Redis for ephemeral fast tallies.

## Limits / things that bite (verify against current docs)
- Firestore: ~**1 write/sec sustained per document** â€” a single counter doc hits
  this fast; the N-shard read sums all sub-docs.
- Bigtable: a hot row key concentrates on one tablet; throughput is per-tablet, so
  row-key design (salting) is the real contention lever.
- Spanner: a single hot row serializes on locks; cross-row reads to sum shards add
  latency but stay strongly consistent.
- Memorystore Basic tier has no failover/SLA â€” a restart loses the cache;
  instances are regional and VPC-attached.

## Pitfalls
- Incrementing one Firestore document at high rate and hitting the per-document
  write limit â€” use the distributed-counter shard pattern.
- A monotonic/sequential Bigtable row key creating a tablet hot spot â€” salt or
  field-promote the key.
- Assuming Spanner's strong consistency removes contention â€” a hot row still
  serializes; shard it for write-heavy counts.
- Lock-in: Firestore's shard pattern and Bigtable row-key design don't port
  directly to other clouds.


---

## Building Block: task-scheduling

# Task scheduling â€” GCP

## Service mapping
- **Cloud Scheduler** â€” fully-managed cron; fires HTTP, Pub/Sub, or App Engine
  targets on a crontab. Maps the **distributed scheduler** option (HA, no leader
  to run).
- **Cloud Tasks** â€” managed task queue with explicit dispatch to an HTTP/App
  Engine target, **per-task scheduled time** (delay), **rate/concurrency limits**,
  and automatic **retries with backoff**. Maps **pull/push leasing** + the
  **delay queue** + per-queue **fairness/rate** options.
- **Workflows** â€” managed orchestration of steps/services with retries. Maps the
  **workflow DAG** option for multi-step jobs (see also `temporal.md`).
- **Pub/Sub** â€” the transport when fan-out delivery is needed (â†’ `messaging-streaming`).

## When to pick which
Cloud Scheduler for cron/recurring triggers; Cloud Tasks when you need
per-task delays, rate limiting, and built-in retries to a worker endpoint;
Workflows when multi-step orchestration is the hard part. Cloud Scheduler â†’
publishes a message; Cloud Tasks â†’ dispatches to your handler â€” combine them.

## Limits / things that bite (verify against current docs)
- **Cloud Tasks** has per-queue dispatch rate and max-concurrent-dispatch caps
  (your fairness/throttle knob) and a max task schedule time / retention window
  (far-future delays beyond it need storing and re-enqueue).
- Cloud Tasks dispatch is **at-least-once** with a per-task **dispatch deadline**
  (the lease/visibility equivalent) â€” exceed it and the task is retried â†’ make
  handlers idempotent.
- **Cloud Scheduler** fires at-least-once â€” a tick can double-fire on retry;
  make the target idempotent (key by scheduled time).
- Targets are HTTP/Pub/Sub endpoints, so worker scaling is your handler's
  concern (Cloud Run / GKE autoscaling).

## Pitfalls
- Setting the Cloud Tasks dispatch deadline shorter than the job â†’ retries and
  double-runs.
- Assuming Cloud Scheduler guarantees exactly-once firing (it doesn't).
- Using Cloud Tasks for far-future delays beyond its schedule horizon.
- Lock-in: Cloud Tasks/Scheduler/Workflows configs don't port to other clouds.


---


