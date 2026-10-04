# AZURE Cloud Architecture & Service Mapping

Comprehensive mapping of system design building blocks to AZURE managed services and architecture patterns.

---

## Building Block: api-design

# API design â€” Azure

## Service mapping
- **API Management (APIM)** â€” managed API gateway: versioning/revisions, products
  + subscription keys, rate-limit/quota policies, request/response transformation,
  validation. The default front for public REST/gRPC/GraphQL contracts.
- **Application Gateway** â€” L7 load balancer with WAF and path/host routing;
  supports WebSocket and gRPC pass-through. Use for service traffic when you don't
  need APIM's full policy layer (pairs with `load-balancing`).
- **Web PubSub / SignalR Service** â€” managed WebSocket/real-time push; Azure holds
  the connections so you don't run a stateful fleet.
- **APIM** also fronts GraphQL (pass-through or synthetic) with the same policy
  engine.

## When to pick which
APIM when you need versioning, keys/quotas, and policy transforms on a public API;
Application Gateway for WAF + L7 routing of plain HTTP/gRPC/WebSocket; Web
PubSub/SignalR for managed push without operating connection servers.

## Limits / things that bite (verify against current docs)
- APIM throughput, policy complexity, and features are **tier-bound** (Consumption
  vs Developer vs Standard/Premium); Consumption is serverless but has cold-start
  and feature gaps, Premium adds VNet + multi-region.
- Rate-limit/quota policies are enforced **per APIM instance/scope** â€” multi-region
  or scaled-out APIM needs care to enforce a single global limit.
- APIM request timeout and body-size caps apply; long calls must go async.
- Web PubSub/SignalR bill per connection + message and cap concurrent connections
  per tier.

## Pitfalls
- Choosing a low APIM tier then needing VNet/multi-region (a tier migration).
- Assuming APIM provides idempotency â€” it doesn't; build the idempotency-key store
  yourself (Cosmos DB / Redis with TTL).
- Treating per-instance rate limits as global across a scaled-out deployment.
- Lock-in via APIM policy expressions and named-value config that don't port out.


---

## Building Block: blob-store

# Blob store â€” Azure

## Service mapping
- **Azure Blob Storage** â€” the object store, inside a *storage account* â†’ *containers* â†’ blobs.
  **Block blobs** are the object-storage workhorse (uploaded as blocks then committed â€” Azure's
  multipart); append blobs suit log appends; page blobs back disks (not general object storage).
- **Access tiers** (the tiering knob) â€” *Hot*, *Cool*, *Cold*, and *Archive* (offline; rehydrate
  to an online tier over hours before reading). Set per-blob or as an account default.
- **Redundancy** (the durability knob, set on the account) â€” *LRS* (replicas in one datacenter),
  *ZRS* (across availability zones), *GRS/GZRS* (asynchronous copy to a second region),
  *RA-GRS* (read access to the secondary). Pick by failure domain you must survive.
- **Azure CDN / Front Door** â€” CDN in front of the blob origin (â†’ `content-delivery`).
- **SAS (Shared Access Signature)** â€” Azure's signed-URL equivalent: scoped, time-limited,
  per-blob or per-container grants.

## When to pick which
Hot for actively served blobs; Cool/Cold for backups and infrequently read data (cheaper
storage, higher access cost, minimum retention periods); Archive for compliance retention off
the request path. LRS for cheapest single-region; ZRS for AZ resilience; GRS/GZRS for region loss.

## Limits / things that bite (verify against current docs)
- Block-blob max size is a function of max block size Ã— max block count; large blobs require the
  block (multipart) path.
- **Archive is offline** â€” you must *rehydrate* (hours) to Hot/Cool before a read; plan it as async.
- Cool/Cold/Archive have minimum storage-duration charges and per-GB retrieval costs; churny or
  tiny blobs can cost more in a cool tier.
- Redundancy is largely an *account-level* setting â€” mixing requirements may mean multiple accounts.
- GRS replication to the secondary region is asynchronous â†’ possible data loss window on failover.

## Provider-specific trade-offs
- Tight integration with Entra ID, Event Grid (blob events), and lifecycle management policies;
  convenient but Azure-specific.
- Account-scoped redundancy/throughput limits make the storage-account boundary a real design unit,
  unlike S3's flatter bucket model.

## Pitfalls
- Reading from Archive without budgeting rehydration latency â†’ timeouts.
- No lifecycle policy to delete old versions/snapshots or tier down cold data â†’ silent growth.
- Over-broad or long-lived SAS tokens (especially account-level SAS) â€” scope to blob + short expiry.
- Serving hot blobs from origin without Front Door/CDN â†’ egress and throughput pressure.


---

## Building Block: caching

# Caching â€” Azure

## Service mapping
- **Azure Cache for Redis** â€” managed Redis; tiers: Basic (single node, no SLA),
  Standard (two-node replicated), Premium (clustering, persistence, VNet,
  zone redundancy), Enterprise / Enterprise Flash (Redis Enterprise: active
  geo-replication, RediSearch/modules, NVMe flash for larger-than-RAM sets).
- **Azure Front Door / CDN** â€” edge caching for static/media (â†’ `content-delivery`).

## When to pick which
Standard for basic HA; Premium for clustering + persistence + VNet isolation;
Enterprise for active-active geo-replication or Redis modules; Enterprise Flash
when the dataset is large and cost/GB matters more than pure RAM speed.

## Limits / things that bite (verify against current docs)
- Clustering and persistence are **Premium+ only** â€” the cheaper tiers are a
  single logical node.
- Scaling tiers/clusters can require a failover or a brief data flush; plan for it.
- Per-tier caps on connections, bandwidth, and memory â€” a hot key still saturates
  one shard.
- Geo-replication semantics differ between Premium (passive) and Enterprise
  (active) â€” know which consistency you're getting.

## Pitfalls
- Choosing Basic/Standard then discovering clustering needs a tier jump (migration).
- Assuming persistence exists below Premium.
- Lock-in via Enterprise modules (RediSearch etc.) that aren't in open-source Redis.


---

## Building Block: content-delivery

# Content delivery â€” Azure

## Service mapping
- **Azure Front Door** â€” the strategic choice: global anycast edge that combines
  CDN caching, TLS termination, path-based routing, and L7 load balancing /
  failover across origins in one product. Prefer it for new designs.
- **Azure CDN** â€” classic pull CDN (Microsoft/edge network); simpler, caching-only.
  Note the older third-party (Verizon/Akamai) tiers are being retired â€” **verify
  the current product against docs** before designing around them.
- **Blob Storage / Static Website hosting** â€” the usual static/media origin behind
  Front Door or CDN.
- **Traffic Manager** â€” DNS-based geo/priority routing when you need pure DNS
  steering rather than an anycast edge (â†’ `load-balancing`).

## When to pick which
Front Door when you want edge caching *and* global routing/failover/WAF together
(most cases); plain Azure CDN only for caching with no routing needs; Blob Static
Website + Front Door for a simple static site.

## Limits / things that bite (verify against current docs)
- Front Door **caching rules** decide query-string and header handling â€” default
  behavior may not cache as you expect; configure the cache key explicitly.
- Purge propagation is not instant; prefer versioned URLs.
- Front Door and classic CDN have different feature sets and pricing models â€” don't
  assume parity; rules engines differ.
- Egress / routing costs are the dominant line; tiers vary by region.

## Pitfalls
- Designing around a retiring CDN tier â€” confirm the SKU is current.
- Expecting Front Door's routing features from plain Azure CDN (it's caching-only).
- Misconfigured cache key (forwarding all query strings) â†’ low hit rate.
- Lock-in via Front Door rules engine / WAF policies that don't port elsewhere.


---

## Building Block: data-storage

# Data Storage â€” Azure

## Service mapping â†’ options
- **Azure SQL Database** â€” managed relational (SQL Server engine); auto-backups,
  read replicas, geo-replication, elastic pools. The default managed SQL.
  **Azure Database for PostgreSQL/MySQL** when you need those engines.
- **Cosmos DB** â€” globally distributed multi-model: key-value, document
  (Mongo API), wide-column (Cassandra API), graph (Gremlin). Maps to all the
  NoSQL options; auto-sharded by a **partition key**, single-digit-ms reads.
- **Azure Cache for Redis** â€” managed Redis (see `caching`), not a system of
  record.

## Limits / things that bite (verify against current docs)
- **Cosmos DB:** throughput is provisioned in **RUs** (request units); a single
  **logical partition** has a size cap (~20 GB) and a per-partition RU ceiling, so
  a bad partition key creates hot partitions that throttle. Choose a
  high-cardinality, evenly-accessed partition key â€” it can't be changed later
  without a data migration.
- Cosmos offers **five consistency levels** (strong â†’ eventual); stronger levels
  cost more RUs and add cross-region latency. This is a knob the generic model
  doesn't have â€” pick deliberately (consistency theory â†’ `consistency-coordination`).
- **Azure SQL** has DTU/vCore service tiers that cap CPU/IO/connections; hitting
  the tier ceiling throttles. Connection limits scale with tier.

## Provider-specific trade-offs
- Cosmos DB's turnkey multi-region writes are powerful but expensive and
  Azure-specific (lock-in); the multi-region consistency choice is yours to own.
- Azure SQL hides patching/HA but the API-compatibility layer (e.g. Mongo/Cassandra
  on Cosmos) is not 100% â€” verify the features you depend on.

## Pitfalls
- Under-provisioning RUs â†’ throttling (429s) under load; or over-provisioning â†’
  large bills.
- Choosing a low-cardinality Cosmos partition key and hitting the 20 GB / hot-
  partition wall.
- Defaulting Cosmos to **strong** consistency everywhere and paying latency/RU
  cost where eventual would do.


---

## Building Block: distributed-logging

# Distributed logging â€” Azure

## Service mapping (generic stage â†’ Azure)
- **Collect:** Azure Monitor Agent (AMA) on VMs/VMSS; for AKS, Container Insights or a
  Fluent Bit DaemonSet. Apps/services emit diagnostic logs to **Azure Monitor**.
- **Buffer / transport:** **Event Hubs** as the durable log bus (Kafka-protocol
  compatible). Diagnostic settings can stream resource logs to Event Hubs for fan-out.
- **Index / search:** **Azure Monitor Logs / Log Analytics workspace**, queried with
  **KQL** (Kusto Query Language) â€” the managed hot search/index tier.
- **Cold archive:** **Azure Blob Storage** via diagnostic settings or Event Hubs
  capture, with lifecycle tiering to Cool/Archive (â†’ `blob-store`).

Common recipe: agents/resources â†’ diagnostic settings â†’ Log Analytics (hot, KQL) and/or
Event Hubs â†’ Blob Storage (cold) for cheap long retention.

## Limits / things that bite (verify against current docs)
- **Log Analytics ingestion** is billed per GB ingested and per GB retained; the
  default retention window is limited and longer retention costs more â€” set it per
  table.
- **Table plans:** an Analytics tier for interactive KQL vs. a cheaper Basic/Auxiliary
  tier for high-volume logs you rarely query interactively â€” choosing wrong is a
  cost/queryability trap.
- **Event Hubs** throughput is sized in throughput units / processing units; partition
  count is fixed at creation and caps consumer parallelism; ordering is per-partition.
- Ingestion has per-workspace rate caps that throttle during spikes.

## Provider trade-offs
- Log Analytics + KQL is powerful and tightly integrated with Azure Monitor metrics
  and alerts (the *alerting/SLO* side is `observability`), but ingest cost scales with
  volume â€” sample and tier.
- Basic/Auxiliary tables are far cheaper for verbose logs but restrict query features
  and retention; route high-value logs to Analytics, bulk logs to the cheap tier or
  straight to Blob.
- Lock-in: KQL queries, diagnostic-setting routing, and workspace structure don't port.

## Pitfalls
- Sending all verbose logs to the Analytics tier (expensive) instead of the Basic tier
  or Blob archive.
- Leaving default retention and ingesting unsampled debug floods â†’ bill shock.
- Assuming Event Hubs preserves global order â€” it's per-partition only.


---

## Building Block: distributed-search

# Distributed search â€” Azure

## Service mapping
- **Azure AI Search** (formerly Cognitive Search) â€” managed search service:
  inverted-index full-text (BM25), facets, suggesters/autocomplete, indexers that
  pull from data sources (Blob, Cosmos DB, SQL), and optional vector/semantic
  ranking. The default managed search on Azure; it abstracts shards behind
  *replicas* (query throughput/HA) and *partitions* (index size/capacity).
- **Self-managed OpenSearch/Elasticsearch on VMs/AKS** â€” when you need full
  engine control or portability; then the generic recipe applies.

## When to pick which
AI Search when you want a managed, batteries-included search with built-in
indexers and suggesters and don't want to operate a cluster; self-managed
OpenSearch when you need low-level shard/analyzer control or cross-cloud
portability.

## Limits / things that bite (verify against current docs)
- Capacity is set by **replicas Ã— partitions** (search units); both are bounded
  per tier and the tier caps total index size and doc count â€” pick the tier from
  your corpus bytes, and re-tiering can mean a rebuild.
- Indexers (the pull pipeline) have batch-size and run-frequency limits; large or
  fast-changing corpora can lag â€” monitor indexer freshness.
- Per-tier caps on indexes, fields, and queries-per-second.

## Pitfalls
- Under-provisioning partitions for a growing corpus, then hitting a tier change.
- Relying solely on built-in indexers for near-real-time freshness without a
  push path / durable buffer in front (â†’ `messaging-streaming`).
- Treating it as a primary store rather than a reindexable derived copy.
- Lock-in: skillsets, indexers, and semantic ranking configs are Azure-specific.


---

## Building Block: dns

# DNS â€” Azure

## Service mapping
Azure splits "host the zone" from "steer the traffic" across two services â€” know
which one a routing policy lives in.

- **Azure DNS** â€” managed authoritative hosting on anycast. Public and private
  zones, `A`/`AAAA`/`CNAME`/`MX`/`TXT`, and **alias records** (the generic `ALIAS`,
  including apex) pointing at Azure resources (Public IP, Front Door, Traffic
  Manager). This is record hosting â€” it does **not** do latency/geo/failover steering.
- **Traffic Manager** â€” DNS-*based* global traffic routing. This is where the
  routing policies live: **Priority** (= failover), **Weighted**, **Performance**
  (= latency-based), **Geographic** (= geolocation), **Multivalue**, and **Subnet**.
  Health-checked endpoint monitoring gates them. It returns a `CNAME`/answer per
  policy, so it is still TTL-bound.
- **Azure Front Door** â€” anycast L7 edge with health-based, near-instant failover
  *without* DNS TTL waits; pair with it (or use instead of Traffic Manager) when
  TTL-bound failover is too slow. Edge caching is `content-delivery`.

## When to pick which
Host the zone in Azure DNS; alias the apex onto Front Door or Traffic Manager. Use
Traffic Manager for DNS-level global routing across regions/clouds/on-prem; use
Front Door when you need fast failover plus edge termination/caching.

## Limits / things that bite (verify against current docs)
- Traffic Manager is DNS-level â†’ **TTL-bound failover**; Front Door is not.
- Traffic Manager Performance routing uses an internet-latency table to Azure
  regions, keyed to the resolver â€” not the exact user.
- Probe interval/timeout/tolerated-failures set detection speed; tighter = flap risk.
- Per-profile endpoint counts and per-zone record-set quotas apply.

## Pitfalls
- Expecting Azure DNS alone to do failover/geo â€” that requires Traffic Manager or Front Door.
- Confusing Traffic Manager (DNS, TTL-bound) with Front Door (anycast, fast) failover.
- Nesting Traffic Manager profiles and losing track of effective TTL.


---

## Building Block: load-balancing

# Load balancing â€” Azure

## Service mapping
- **Azure Load Balancer** â€” managed **L4** (TCP/UDP); high throughput, low latency,
  source-IP preservation, public or internal. The L4 default within a region.
- **Application Gateway** â€” managed **L7**; path/host routing, TLS termination,
  cookie-based affinity, autoscaling, with an optional **WAF** tier. The HTTP(S)
  default when you need content routing in-region.
- **Azure Front Door** â€” global **L7** edge: anycast entry, TLS offload, path/host
  routing, caching, and WAF at the edge (cross-region steering + CDN, â†’
  `content-delivery`). Use for global apps, not single-region balancing.
- **Traffic Manager** â€” DNS-based global routing (priority/weighted/geo/perf); like
  Route 53, it steers between endpoints, it is not an L4/L7 data-path LB.
- **VM Scale Set** â€” the autoscaling fleet the LB/App Gateway balances over.

## When to pick which
Azure Load Balancer for L4 TCP/UDP throughput within a region; Application Gateway
for in-region L7 HTTP routing + WAF; Front Door for global edge routing/caching;
Traffic Manager when DNS-level endpoint selection is enough.

## Limits / things that bite (verify against current docs)
- Application Gateway v1 had manual sizing; v2 autoscales â€” confirm you're on v2
  for elastic load, and note warm-up time on sudden spikes.
- Basic Load Balancer lacks features/SLA of Standard and is being retired â€” use
  Standard.
- L4 Load Balancer does **no** TLS termination or content routing (that's App
  Gateway/Front Door); don't expect L7 behavior from it.
- Probe (health-check) interval/threshold config drives eviction speed and flap â€”
  set deliberately; an unhealthy probe drops the backend from rotation.

## Pitfalls
- Reaching for Front Door for a single-region app (over-engineering + cost) â€” App
  Gateway or Load Balancer suffices.
- Using cookie affinity on App Gateway instead of externalizing session state,
  then losing sessions on scale-in.
- Confusing Traffic Manager (DNS steering) with an actual data-path balancer.
- Lock-in: App Gateway/Front Door rules and WAF policies don't port to other clouds.


---

## Building Block: messaging-streaming

# Messaging & streaming â€” Azure

## Service mapping â†’ the generic options
- **Service Bus (Queues)** â€” managed work queue; at-least-once, sessions for
  per-key ordering, built-in dead-lettering, scheduled/deferred messages,
  duplicate detection within a window. The default enterprise queue.
- **Service Bus (Topics/Subscriptions)** â€” pub/sub fan-out with per-subscription
  filters. Use when multiple consumers need filtered copies of events.
- **Event Grid** â€” lightweight event routing/pub-sub for reactive,
  event-driven integration (resource events, custom topics). Push-based, at-least-once.
- **Event Hubs** â€” partitioned, replayable log (the Kafka/Kinesis analog); ordering
  per partition, consumers track offsets; exposes a **Kafka-compatible endpoint**.
  Use for high-throughput streaming/telemetry and replay.

## Decision-changing limits (verify against current docs)
- **Service Bus message size** depends on tier (Standard ~256 KB; Premium larger);
  big payloads â†’ blob + claim-check.
- **Sessions** are how you get FIFO/per-key ordering on Service Bus â€” without a
  session the queue is competing-consumer (no order). One session = one consumer.
- **Service Bus duplicate detection** works within a configured time window only;
  beyond it, consumers must still be idempotent.
- **Event Hubs** throughput is bought in **throughput units / processing units**;
  parallelism = partition count, fixed at creation (plan ahead). Ordering per
  partition only; a hot partition key throttles one partition.

## Provider-specific trade-offs
- Service Bus (queues/topics) vs. Event Hubs/Event Grid is the queue-vs-stream-vs-
  event-routing split: Service Bus for command/job processing with rich delivery
  semantics; Event Hubs for high-volume replayable streams; Event Grid for
  reactive routing.
- Premium tier buys predictable performance and larger messages at higher cost.
- For durable workflows Azure offers **Durable Functions** (orchestration as code
  on Functions) â€” compare with Temporal in `temporal.md`.

## Pitfalls
- Expecting FIFO from a plain Service Bus queue â€” you must use **sessions**.
- Treating duplicate detection as exactly-once beyond its window â†’ double effects.
- Fixing Event Hubs partition count too low and discovering it can't be raised
  without recreating â€” over-provision early.
- Ignoring the dead-letter sub-queue Service Bus auto-populates (max-delivery,
  expiry, filter failures) â€” monitor and drain it.


---

## Building Block: observability

# Observability â€” Azure

## Service mapping
- **Azure Monitor** â€” the umbrella: metrics, **Metric Alerts**, dashboards, and
  autoscale signals.
- **Application Insights** â€” APM: request RED metrics, **distributed tracing**,
  dependency maps, and live metrics. Native OpenTelemetry export is supported.
- **Log Analytics (Kusto/KQL)** â€” the log + query store behind Azure Monitor; the
  high-volume pipeline concern is `distributed-logging`.
- **Azure Managed Grafana** + **Azure Monitor managed service for Prometheus** â€”
  run the generic PromQL/Grafana stack managed, for portability.
- **Health probes** â€” App Service / AKS liveness+readiness; gating is `load-balancing`.

## When to pick which
- Application Insights when the app is .NET/Azure-centric â€” richest auto-instrumentation
  and dependency tracing with least effort.
- Azure Monitor managed Prometheus + Managed Grafana to keep the generic recipe and
  PromQL portability.
- Log Analytics/KQL when you need powerful ad-hoc log querying.

## Limits / things that bite (verify against current docs)
- **Application Insights samples telemetry by default** (adaptive sampling) â€” great
  for cost, but verify errors/slow requests aren't being dropped.
- **Log Analytics ingestion + retention is the main cost driver**; data-cap and
  retention tiers change the bill sharply.
- **Metric Alerts evaluation frequency and granularity** bound how fast an SLO burn
  is detected.
- KQL has query limits/timeouts on large windows.

## Pitfalls
- Trusting default adaptive sampling for SLO-critical signals without checking it.
- High-cardinality custom dimensions inflating Log Analytics cost.
- Lock-in to App Insights SDKs/KQL dashboards â€” use the OpenTelemetry exporter and
  managed Prometheus/Grafana to stay portable.
- Conflating Log Analytics retention with metrics retention (different knobs/costs).


---

## Building Block: resilience-failure

# Resilience & failure â€” Azure

## Service mapping
- **Redundancy / failover** â€” **Availability Zones** within a region (default
  fault isolation); **Availability Sets** for rack/update-domain spread;
  paired-region replication for region loss. VM Scale Sets replace failed
  instances; Load Balancer / Application Gateway stop routing to unhealthy
  backends (health probes â†’ `load-balancing`).
- **Global failover routing** â€” **Azure Front Door** (and Traffic Manager) for
  health-probe-based failover and latency/priority routing across regions.
- **Rate limiting / load shedding** â€” **Front Door / Application Gateway WAF**
  rate-limit rules at the edge; **API Management** has throttling policies
  (`rate-limit` and `quota` by key/subscription).
- **Retries / circuit breaking** â€” Azure SDKs retry with backoff + jitter;
  app-level via Polly (the .NET standard); a mesh (Istio/Linkerd on AKS) adds
  proxy-level timeouts/retries/breaking.
- **Queue containment** â€” **Service Bus** (with dead-letter queues) â†’ `messaging-streaming`.
- **Shared limiter store** â€” **Azure Cache for Redis** for counters.

## Limits / things that bite (verify against current docs)
- Zone-redundant managed services failover in seconds; async geo-replication
  (e.g. SQL geo-replicas) can lose recent writes on region failover.
- API Management rate-limit policies are scoped (by key/product/subscription) and
  per-unit/region â€” limits don't automatically aggregate across regions.
- Front Door WAF rate limiting uses a rolling window with coarse granularity; not
  a precise per-second limiter.

## Provider-specific trade-offs
- Zone redundancy is the cheap default; **paired-region / active-active is a
  major cost and complexity jump** â€” tie it to the SLA, not ambition.
- Front Door centralizes edge protection + global routing but becomes a critical
  path component to design redundantly around.

## Pitfalls
- Confusing **Availability Sets** (fault/update domains in one datacenter) with
  **Zones** (separate datacenters) â€” only zones survive a datacenter loss.
- Stacking SDK retries with Polly retries with mesh retries (load multiplier).
- Treating geo-replication failover as lossless.


---

## Building Block: service-decomposition

# Service decomposition â€” Azure

## Service mapping
- **Compute for services** â€” AKS (Kubernetes), Container Apps (managed
  containers + built-in Dapr/KEDA), or Functions for event-driven services.
- **API gateway / front door** â€” API Management (full gateway: auth, throttling,
  versioning) or Application Gateway / Front Door for routing.
- **Service discovery** â€” Kubernetes DNS on AKS; Container Apps service discovery;
  Dapr name resolution.
- **Service mesh** â€” Istio-based add-on for AKS, or Open Service Mesh; **Dapr**
  as a sidecar for service invocation, pub/sub, and state.
- **Cross-service workflows / saga** â€” Durable Functions or Logic Apps
  (orchestration); transactional outbox via Service Bus + change feed.

## When to pick which
Container Apps + Dapr for a fast managed microservices start; AKS when you need
full Kubernetes/mesh control; API Management when you need a policy-rich gateway;
Durable Functions for orchestrated sagas.

## Limits / things that bite (verify against current docs)
- API Management tiers differ sharply (no VNet/SLA on Consumption; cost on Premium).
- Dapr adds a sidecar (latency/ops) though it simplifies invocation/pub-sub.
- Front Door / App Gateway routing + WAF add hops and config surface.

## Pitfalls
- Treating Logic Apps/Durable as a place for core business logic.
- Mixing Dapr and a separate mesh without a clear division of responsibility.
- Cross-service ACID expectations â€” use saga/outbox, not distributed transactions.


---

## Building Block: sharded-counters

# Sharded counters â€” Azure

Only the contention/atomicity differences that change the recipe. Default to the
generic recipe; this maps it to Azure services.

## Service mapping
- **Cosmos DB atomic increment** â€” a patch/partial-update `Increment` on a numeric
  property updates one item atomically within its logical partition. The
  single-counter option.
- **Cosmos DB + write sharding** â€” spread the count across N logical partition
  keys (`id#shard{rand(0..N-1)}`), increment a random shard, and sum the N items
  on read. The striped-counter recipe and the fix for a hot logical partition.
- **Azure Cache for Redis** â€” managed Redis for the fast path: `INCR`,
  HyperLogLog, key sharding. Use for microsecond tallies and built-in HLL.

## When to pick which
Cosmos DB atomic increment when the item is durable system-of-record and the
count fits one logical partition's throughput; Cosmos write-sharding when one
partition key goes hot; Azure Cache for Redis when the count is a fast/ephemeral
tally or needs HLL.

## Limits / things that bite (verify against current docs)
- A Cosmos DB **logical partition** has a throughput ceiling (provisioned RU/s per
  partition, plus a per-logical-partition cap) â€” concentrating increments on one
  partition key creates a hot partition that throttles (429s) regardless of total
  RU/s. Write-sharding the key is the fix.
- Every increment consumes RU/s; a high-write counter's cost scales with write
  rate, and the N-shard read consumes RU/s per item read.
- Cross-partition reads (summing N shards) fan out and cost more RU/s than a
  single-partition read.
- Multi-region writes use conflict resolution; concurrent increments across
  regions need last-writer-wins care or a custom merge â€” prefer per-region shards
  summed centrally.

## Pitfalls
- Leaving a viral counter on one partition key and hitting 429 throttling â€” shard
  the key across logical partitions.
- Under-provisioning RU/s for the write spike on the hottest counter.
- Assuming multi-region writes simply add increments â€” they can conflict; design
  per-region shards.
- Lock-in: Cosmos partition-key layout and RU model don't port directly to other
  clouds.


---

## Building Block: task-scheduling

# Task scheduling â€” Azure

## Service mapping
- **Logic Apps** â€” managed scheduled/recurring triggers and low-code workflow
  orchestration; recurrence trigger maps the **distributed scheduler** option,
  and the connector workflow maps the **workflow DAG** option.
- **Azure Functions Timer trigger** â€” cron-expression scheduled functions; HA
  managed cron for code-first jobs. Maps the **scheduler** option.
- **Storage Queues / Service Bus Queues + Functions or workers** â€” the queue
  holds jobs; the **lock/visibility (peek-lock) duration** is the lease; a worker
  pool drains it. Maps **pull leasing**. Service Bus has **dead-lettering**
  built in.
- **Service Bus scheduled messages / message TTL** â€” per-message scheduled
  enqueue time. Maps the **delay queue** option.
- **Durable Functions** â€” code-first orchestration with retries/timers (see
  `temporal.md`).

## When to pick which
Functions Timer trigger for code-first cron; Logic Apps for low-code scheduled
workflows and connector-heavy orchestration; Service Bus + workers for
priority/sessions and built-in DLQ; Storage Queues for a cheap, simple job queue.

## Limits / things that bite (verify against current docs)
- **Service Bus peek-lock** default lock is short (e.g. ~30â€“60 s); renew the lock
  (the heartbeat equivalent) for long jobs or set a longer lock duration; lock
  expiry re-delivers.
- **Storage Queues** give at-least-once with a visibility timeout but **no native
  DLQ** (you build it) and weaker ordering; **Service Bus** adds sessions
  (ordering), DLQ, and scheduled messages.
- **Functions Consumption plan** has an execution-time cap and cold starts â€” long
  or latency-sensitive jobs want Premium/Dedicated or container workers.
- Per-namespace/throughput quotas apply on Service Bus.

## Pitfalls
- Using Storage Queues and discovering there's no built-in dead-lettering.
- Leaving the Service Bus lock too short for long jobs â†’ re-delivery and double-runs.
- Running the Functions Timer trigger as if it guarantees exactly-once firing â€”
  make the handler idempotent.
- Lock-in: Logic Apps / Durable Functions definitions don't port to other clouds.


---


