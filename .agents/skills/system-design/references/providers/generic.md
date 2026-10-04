# GENERIC Cloud Architecture & Service Mapping

Comprehensive mapping of system design building blocks to GENERIC managed services and architecture patterns.

---

## Building Block: api-design

# API design â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **REST/JSON** over an HTTP framework + a reverse proxy / API gateway you run
  (NGINX, Envoy, Kong, Traefik) for routing, TLS termination, auth, and rate
  limiting at the edge.
- **gRPC** with protobuf for internal service-to-service calls; add Envoy or
  grpc-web as a gateway when browsers must reach it.
- **GraphQL** via a server library (Apollo, graphql-js, gqlgen) â€” put depth/cost
  limits and persisted-query allowlists in front of it.
- **WebSocket/SSE** terminated at the app or a connection-aware proxy; SSE rides
  plain HTTP, WebSocket needs proxy support for the `Upgrade` handshake.
- **OpenAPI** (REST) / **protobuf** (gRPC) as the schema source of truth â€”
  generate clients, server stubs, and docs from it so the contract can't drift.

## Topology
- Edge gateway/proxy â†’ service. The gateway owns cross-cutting concerns (auth, rate
  limiting, TLS, request size caps) so each service doesn't re-implement them.
- Idempotency-key store: a fast, durable KV (e.g. Redis with persistence, or a DB
  table) holding `key â†’ response` with a TTL; co-locate with or transact alongside
  the write it protects.

## Limits / things that bite
- A stateless HTTP gateway scales horizontally; a **WebSocket/SSE** tier does not â€”
  it holds a connection (and memory) per client, so sizing is connections, not QPS,
  and load balancing must be connection-aware (sticky or a shared session store).
- Default request body and header size caps in the proxy will silently reject large
  payloads â€” set them deliberately.
- Self-managed rate limiting and idempotency dedupe need a shared store to work
  across instances (an in-process counter doesn't; â†’ `resilience-failure`).

## Pitfalls
- No managed quota/throttle layer â€” you build and operate it (the gateway helps but
  you configure the limits and the storage behind them).
- Forgetting connection draining on deploy â†’ WebSocket clients all reconnect at
  once (reconnect storm; add jitter).
- Hand-written clients drift from the server shape â€” generate from OpenAPI/protobuf
  instead.

Operationally heavier than a managed gateway, but zero lock-in and full control of
versioning, auth, and limits. Use when running your own infra or for portability
across clouds.


---

## Building Block: blob-store

# Blob store â€” generic / self-hosted

The vendor-neutral default. If no cloud is named, this is the answer.

## Service mapping (generic recipe â†’ open source)
- **S3-compatible object store** â†’ **MinIO** (simplest, S3 API, erasure coding within a node
  set; the on-prem S3 default), **Ceph + RGW** (RADOS data plane, replication *or* EC pools,
  S3/Swift gateways; scales to exabytes, heavier to operate), **SeaweedFS** (optimized for
  *many small files* â€” packs them into volume files to keep the metadata index tiny).
- **Durability scheme** â†’ replication or erasure-coded pools, configured per bucket/pool.
- **Tiering** â†’ hot pool on SSD/NVMe, cold pool on HDD; lifecycle/transition policies move
  objects between pools.
- **CDN fronting** â†’ any CDN or reverse-proxy cache in front (â†’ `content-delivery`).

## Decision-changing limits (verify against current docs)
- The **metadata/index node** is the scaling ceiling and the SPOF â€” replicate and shard it.
  Billions of tiny objects stress it long before disk capacity does; pick SeaweedFS or pack
  small objects if the count is huge.
- Erasure-coded reads gather *k* shards across nodes â€” sensitive to network and per-node
  count; keep EC for large/cold pools.
- Multipart part-size minimums and max-parts-per-upload exist (S3-compatible APIs commonly
  use a ~5 MB minimum part and a max part count); confirm for the chosen implementation.

## Trade-offs (self-host vs managed)
- You own placement, rebalancing, failure-domain layout, capacity planning, and upgrades â€”
  real operational weight, but no egress markup and no lock-in.
- S3-compatible APIs make migration to/from a cloud feasible, *if* you avoid provider-only
  features (lifecycle quirks, server-side encryption modes, event hooks).
- Capacity is provisioned, not elastic â€” you must plan headroom; a cloud absorbs spikes.

## Pitfalls
- Treating the index node as an afterthought â€” it is the first thing to fall over.
- Erasure-coding a hot small-object pool, then chasing tail latency.
- Skipping lifecycle/abort-incomplete rules â€” orphaned parts and old versions grow forever.
- Assuming "S3-compatible" means feature-complete; verify the specific API surface you rely on.


---

## Building Block: caching

# Caching â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **Memcached** â€” multithreaded LRU object cache; simplest, highest raw
  throughput for get/set. No persistence, no replication, no rich types.
- **Redis** (open source / Valkey) â€” single-threaded core, rich data structures,
  optional persistence (RDB/AOF), replication, and **Redis Cluster** for
  horizontal sharding via hash slots (16,384 slots, consistent-hash-like).

## Topology
- Single node for small hot sets.
- Primary + replicas for read scaling and failover (replica promotion on primary
  loss; expect a brief unavailability + possible loss of un-replicated writes).
- Cluster mode (sharded) when the hot set or QPS exceeds one node. Client or proxy
  routes keys to shards by hash slot.

## Limits / things that bite
- A node is bounded by RAM (the hot set must fit) and by a single core for
  Redis command execution â€” a hot key can saturate one shard regardless of total
  cluster size. Mitigate with an L1 tier or key replication (see deep-dive).
- Persistence (AOF fsync) trades durability for write latency; RDB snapshots can
  cause fork/latency spikes on large datasets.
- Eviction is configured per instance (`maxmemory-policy`: `allkeys-lru`,
  `volatile-ttl`, etc.) â€” set it deliberately; the default may reject writes when
  full.

## Pitfalls
- No managed failover â€” you operate Sentinel/Cluster yourself.
- Cluster mode restricts multi-key ops to a single slot (hash tags needed).
- Backups/persistence and security (TLS, auth) are on you.

Operationally heavier than a managed service, but zero lock-in and full control.
Use when running your own infra or for portability across clouds.


---

## Building Block: consistency-coordination

# Consistency & coordination â€” generic (vendor-neutral / self-hosted)

The default answer. These open-source/self-host tools implement the SKILL.md
options. If the user names a cloud with no provider file here, this is still the
answer â€” describe the generic tool and note the managed equivalent exists.

## Service mapping (option â†’ tool)

- **Consensus / leader election / locks / config** â†’ **etcd**, **ZooKeeper**, or
  **Consul**. All run a Raft (etcd, Consul) or ZAB (ZooKeeper) majority-quorum
  cluster and expose: strongly-consistent key/value, watches, ephemeral nodes /
  leases (the primitive for **leader election** and **distributed locks**), and
  membership/service discovery. Reach for these for the **control plane**, not the
  bulk data plane.
- **Single-leader replication** â†’ **PostgreSQL / MySQL** with one primary + sync or
  async replicas. Synchronous replica = no data-loss window but higher write
  latency; async = a small loss window on failover. (Storage engine details â†’
  `data-storage`.)
- **Quorum / leaderless (R+W>N)** â†’ **Apache Cassandra** or **Riak**: per-query
  tunable consistency (`ONE`, `QUORUM`, `ALL`), consistent-hashing partitioning,
  hinted handoff, read repair. The textbook tunable-consistency store.
- **Consistent-hashing partitioning** â†’ built into Cassandra/Riak/Dynamo-style
  stores and into client libraries for **Redis**/**Memcached** sharding; or roll
  your own ring with virtual nodes.
- **Distributed transaction (2PC)** â†’ an **XA**-capable transaction manager across
  XA resources; rarely worth it cross-service.
- **Saga** â†’ orchestrate with a workflow engine (e.g. **Temporal**) or choreograph
  over a broker (see `messaging-streaming`); the engine handles retries,
  compensations, and idempotency.

## Key limits / things that bite (verify against current docs)

- **Quorum cluster sizing:** use an **odd** count (3 or 5). `2f+1` nodes tolerate `f`
  failures; below majority the cluster **stops accepting writes** by design. A 2- or
  4-node cluster buys no extra tolerance and worsens split-vote odds.
- **etcd/ZooKeeper are control-plane stores**, not databases: bounded total
  dataset, request-size caps, and watch/connection limits. Putting bulk data or
  high-write-rate state in them will tip them over.
- **Write latency is a round trip to a majority** â€” co-locate consensus members in
  one region (or accept tens-to-100+ ms per write across regions).
- **Synchronous replication** stalls writes if a required replica is slow/down;
  decide whether a slow replica should block or be dropped from the sync set.

## Provider-neutral trade-offs

- Strong consistency = a coordination round trip on the write path *and* a quorum
  that can refuse service under partition (CP). Price both before choosing it.
- Tunable stores (Cassandra) let you mix per query, but `QUORUM` reads+writes cost
  more nodes per op and still need conflict handling for concurrent writers.
- Leader-based systems are simplest but the leader is a write SPOF with a failover
  gap; quantify the gap against the availability target (â†’ `back-of-the-envelope`).

## Pitfalls

- Reaching for ZooKeeper/etcd as a general database (it's a coordination kernel).
- Running an even-sized quorum cluster.
- Cross-region synchronous consensus without budgeting the round-trip latency.
- Building leader election by hand (timeouts, fencing) instead of using a lease/
  ephemeral-node primitive â€” easy to create split-brain.
- Hand-rolling 2PC for cross-service workflows where a saga avoids the blocking
  coordinator.


---

## Building Block: content-delivery

# Content delivery â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **A commercial CDN** (Cloudflare, Akamai, Fastly) â€” the usual choice; a global
  PoP network you configure, not operate. Pull by default; most support push,
  shields, signed URLs, edge compute, and `stale-while-revalidate`.
- **Self-hosted edge cache** (Varnish, NGINX `proxy_cache`, Apache Traffic Server)
  â€” reverse-proxy caches you run in a few regions yourself. *Use when* you need
  full control, on-prem, or a private edge â€” but you own PoP placement, scaling,
  TLS, and routing. This is a regional reverse-proxy cache, not a global CDN.

## Topology
- **Pull:** edge â† (optional shield) â† origin (object store or app server). Set
  `Cache-Control`/`s-maxage` at the origin; edges obey it.
- **Push:** build pipeline uploads to CDN storage; URLs rewritten to the CDN domain.
- **Routing:** anycast or DNS geo-routing sends each user to the nearest healthy
  edge (mechanics in `load-balancing`).
- **Shield:** one regional mid-tier cache in front of the origin collapses edge
  misses into a single origin fetch.

## Limits / things that bite
- **Cache key** is the lever: unbounded query params or cookies in the key drop hit
  rate toward zero â€” whitelist params, strip cookies on static paths, mind `Vary`.
- **Purge propagation** is not instant across global PoPs (seconds to minutes);
  prefer versioned/fingerprinted URLs over purge for freshness.
- **Self-hosted Varnish/NGINX** caches in RAM/disk per node â€” sized per box, no
  global anycast unless you build it; an eviction loses that node's working set.
- **Egress** is the cost line that dominates; a hot uncacheable path bleeds it.

## Pitfalls
- Treating a single-region Varnish box as a CDN â€” it has no global proximity.
- No origin fallback when the edge/CDN is down (the edge is now a dependency).
- One giant TTL â†’ synchronized expiry stampede; add jitter / `stale-while-revalidate`.
- Forgetting the origin must survive a global cold-cache pull (use a shield).

Operationally lightest with a commercial CDN (zero PoP ops, pay per egress);
self-hosted edge gives control and no per-egress vendor bill but you build the
global footprint, routing, and resilience yourself.


---

## Building Block: data-storage

# Data Storage â€” Generic (self-hosted / open-source)

The default answer when no cloud is named. These are the engines the SKILL.md
options map to, self-hosted or run anywhere.

## Engine mapping â†’ options
- **Relational/SQL** â†’ **PostgreSQL** (rich types, JSONB, materialized views,
  strong default) or **MySQL/MariaDB** (huge ecosystem, simple replication).
- **Document** â†’ **MongoDB** (flexible schema, secondary indexes, multi-doc
  transactions in recent versions).
- **Key-value** â†’ **Redis** (in-memory, rich structures; also a cache â€” see
  `caching`) or **Riak** (durable, distributed).
- **Wide-column** â†’ **Cassandra** (leaderless, write-heavy, tunable consistency)
  or **HBase** (Hadoop ecosystem).
- **Graph** â†’ **Neo4j**.
- **Connection pooler** â†’ **PgBouncer** (Postgres), **ProxySQL** (MySQL).

## Limits / things that bite (verify against current docs)
- A single relational node's practical ceiling is roughly **~1k QPS** and low-TB
  datasets before replicas/sharding (â†’ `back-of-the-envelope`); exact numbers
  depend on schema, indexes, and query mix.
- Postgres connections are processes â€” the default `max_connections` is low
  (often ~100); exceed it and new connections error. Pool with PgBouncer.
- MySQL async replication can lag and lose the un-replicated tail on failover;
  enable semi-sync if you can't afford that loss.
- Cassandra: consistency is tunable per query (`ONE`/`QUORUM`/`ALL`) â€” picking
  `ONE` for both read and write gives no read-your-writes guarantee.

## Trade-offs specific to self-hosting
- You own failover, backups, replica promotion, and resharding â€” no managed
  automation. Cheaper and portable (no lock-in), but operationally heavy.
- Sharding is mostly manual (app-level routing or a layer like Vitess/Citus);
  managed clouds hide more of this.

## Pitfalls
- Defaulting to NoSQL for "scale" when one Postgres node would serve the load.
- Running without a connection pooler and hitting `max_connections` under spike.
- Treating self-managed async replicas as strongly consistent.
- No tested failover/restore runbook â€” replication is not a backup.


---

## Building Block: distributed-logging

# Distributed logging â€” generic (self-host / open source)

The default answer when no cloud is named. Vendor-neutral mechanics and the
open-source building blocks for each pipeline stage.

## Stage â†’ tool mapping
- **Collect:** Fluent Bit or Vector (lightweight node agents), Fluentd (heavier,
  plugin-rich), Filebeat (Elastic's shipper). Read files/stdout, parse, enrich, route.
- **Transport / buffer:** the agent's own disk buffer for simple cases; **Kafka** (or
  Redpanda/Pulsar) as a durable, partitioned **log bus** for high volume / fan-out.
  Treat delivery, ordering, and backpressure as owned by `messaging-streaming`.
- **Index / search:** **Elasticsearch / OpenSearch** for full-text field search (the
  "E" in ELK/EFK); **Loki** for cheap label-indexed storage with grep-style queries.
- **Visualize / query:** Kibana (ES/OpenSearch) or Grafana (Loki).
- **Cold archive:** object storage (MinIO self-host, or any S3-compatible bucket) via
  `blob-store`; query cold data with an in-place engine if needed.

Common assemblies: **ELK** = Elasticsearch + Logstash + Kibana; **EFK** swaps
Logstash for Fluentd/Fluent Bit; **PLG** = Promtail/Loki/Grafana.

## When to pick which
- Need rich, ad-hoc full-text search across fields â†’ Elasticsearch/OpenSearch.
- Volume is large and you mostly filter by label then scan â†’ Loki (far cheaper).
- One sink, moderate volume â†’ agent disk buffer straight to the indexer (skip Kafka).
- Spiky volume or multiple sinks (search + archive + analytics) â†’ put Kafka in front.

## Limits / things that bite (verify against current docs)
- **Elasticsearch shard pressure:** too many shards exhausts heap; keep shards moderate
  and even, use rollover. High-cardinality index fields cause mapping explosions.
- **Heap/JVM:** ES nodes are RAM-bound; under-provisioned heap â†’ GC pauses â†’ ingest
  rejection (HTTP 429). Watch the bulk/index queue.
- **Kafka:** ordering is per-partition only; partition count caps consumer parallelism;
  retention is bytes/time per topic â€” size it for the longest sink outage.
- **Loki:** weak at high-cardinality and arbitrary full-text; label cardinality is the
  cost driver.

## Pitfalls
- Synchronous ship from the app/agent that blocks the request path on a slow indexer.
- Unbounded buffers (memory or disk) that OOM/fill during the spike they should absorb.
- One ever-growing index with no time-based rollover â†’ retention becomes a crisis.
- Regex-parsing free text at the agent at high volume (CPU sink) instead of emitting
  structured logs at the source.
- Running ES "because it's standard" when label-indexed Loki would cost a fraction.


---

## Building Block: distributed-search

# Distributed search â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **Elasticsearch / OpenSearch** â€” distributed search engines over Lucene; REST
  API, JSON docs, sharding + replication, near-real-time refresh, aggregations
  (facets), BM25 by default. The default full-text choice. OpenSearch is the
  Apache-2.0 fork; pick on licensing/feature needs.
- **Apache Lucene** â€” the underlying library (inverted index, segments, BM25).
  Embed it directly only when you want a single-node, in-process index and no
  cluster operations.
- **Apache Solr** â€” also Lucene-based; mature faceting and config-driven schemas.
  A reasonable alternative to Elasticsearch for classic enterprise search.

Map the SKILL's options: build mode = refresh interval + bulk vs streaming
indexing; ranking = default BM25, add function-score/boosts for hybrid;
autocomplete = completion suggester (FST) or edge-n-gram field; distribution =
shard count at index creation + replica count per shard.

## Topology
- Single node for small corpora / dev.
- Multi-node cluster with dedicated roles for scale: master-eligible (cluster
  state), data nodes (shards), and coordinating nodes (fan-out/merge). Isolate
  indexing-heavy and query-heavy load onto separate node pools when they contend.
- Shards per index fixed at creation; replicas adjustable. Size shards from
  corpus bytes up front (reindex to change shard count).

## Limits / things that bite (verify against current docs)
- Shard count is effectively immutable post-creation â€” under/over-sharding both
  hurt; plan from index bytes Ã· target shard size.
- JVM heap pressure and large GC pauses on a data node spike query tail latency
  across every fan-out query.
- Deep `from`/`size` pagination is expensive cluster-wide; use `search_after` /
  scroll / point-in-time cursors.
- Refresh interval trades freshness for write cost; merges contend with queries.

## Pitfalls
- Treating it as a primary store â€” no transactions; it's a derived, rebuildable
  index. Keep the source of truth elsewhere and own a full-reindex path.
- Mismatched index-time vs query-time analyzers â†’ silent zero-result queries.
- Running unthrottled bulk reindex against a live cluster (merge storm).
- No durable buffer in front of the indexer, so a write surge stalls or drops.
- You operate it: capacity, upgrades, snapshots, security (TLS/auth) are on you.


---

## Building Block: dns

# DNS â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **BIND** â€” the reference authoritative + recursive server; ubiquitous, flexible,
  zone-file driven. Heaviest to operate; large attack surface if misconfigured.
- **PowerDNS** â€” authoritative server with pluggable backends (SQL, etc.) plus a
  separate recursor; good when zones live in a database. Some geo/load features via
  backends (e.g. geoip).
- **Knot DNS / NSD** â€” modern, fast authoritative-only servers; pair with Unbound
  as the recursive resolver. Common for high-performance authoritative tiers.
- **CoreDNS** â€” plugin-based, common inside Kubernetes for service discovery.

## Topology
- **Authoritative tier** holds your zones; run **at least two** name servers, on
  separate networks/sites. Standard DNS supports primaryâ†’secondary **zone transfer**
  (AXFR/IXFR) so secondaries stay in sync â€” use it for redundancy.
- **Anycast** the authoritative IPs across sites via BGP for proximity and DDoS
  resilience (you operate the routing).
- **Recursive resolvers** are usually the client's/ISP's; you run recursors only
  for internal resolution.

## Routing policies without a managed service
Plain BIND/NSD give you simple and round-robin (multiple `A` records) out of the
box. **Weighted, latency, geo, and failover** policies are *features layered on
top* â€” PowerDNS geoip/lua backends, dnsdist, or a GSLB appliance â€” and **health-
checked failover** means running your own prober that rewrites zone records on
failure. This operational burden is exactly why most teams use a managed provider
for traffic steering.

## Limits / things that bite
- Self-run health-check failover is DIY: you build the prober, the thresholds, and
  the record-rewrite path â€” and it's still TTL-bound for recovery.
- Zone transfers must be secured (TSIG) or you leak/expose your zone.
- A misconfigured open recursive resolver becomes a DDoS amplifier â€” lock it down.
- Geo/latency steering needs an IP-geolocation database you keep current.

## Pitfalls
- One physical site for all authoritative servers â†’ SPOF; spread them.
- Forgetting DNSSEC key rollover if signing zones (broken validation = outage).
- Treating round-robin `A` records as load balancing â€” clients cache one answer and
  there's no health awareness.

Maximum control and zero lock-in, but you own anycast/BGP, health checking, and
geo data. Use when running your own infra or when a managed provider can't meet a
constraint; otherwise a managed zone removes most of this toil.


---

## Building Block: load-balancing

# Load balancing â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **HAProxy** â€” battle-tested L4 and L7 proxy/balancer. Rich algorithms
  (round robin, least-conn, source hash), fine-grained health checks, slow-start,
  connection draining, TLS termination. The default for a dedicated software LB.
- **Nginx** â€” web server + L7 reverse proxy + balancer; also does static serving,
  caching, compression, TLS termination. Great when the balancer and reverse-proxy
  roles are the same box. L4 (stream) module exists but is less full-featured.
- **Envoy** â€” modern L4/L7 proxy built for dynamic service discovery, gRPC/HTTP2,
  observability, and outlier detection (passive ejection). The data plane behind
  most service meshes; pick it for dynamic fleets and rich telemetry.
- **Keepalived / VRRP** â€” floats a virtual IP between two balancers for
  active-passive HA. **IPVS/LVS** â€” kernel-level L4 for very high throughput.

## Topology
- Single balancer only for non-critical/dev â€” it's a SPOF.
- **Active-passive:** two balancers, a VIP moved by Keepalived/VRRP on failure
  (failover gap of seconds).
- **Active-active:** multiple balancers behind DNS round robin or anycast/ECMP, or
  a small L4 tier (LVS) fronting an L7 tier (HAProxy/Envoy) for scale.

## Limits / things that bite
- A single instance is bounded by CPU (TLS + L7 parsing), open file descriptors /
  ephemeral ports, and NIC bandwidth â€” L7 termination is far heavier than L4
  forwarding. Size against peak concurrent connections, not just QPS.
- Health-check config is yours to get right: set failure/success thresholds,
  intervals, jitter, and slow-start explicitly or you'll flap or stampede
  recovering nodes (see deep-dive).
- Connection draining/deregistration delay must be configured for graceful
  deploys/scale-in, or in-flight requests drop.
- Backend discovery is on you: static config, DNS, or a registry (Consul/etcd) +
  reload. Stale targets get traffic until removed.

## Pitfalls
- One balancer with no standby â€” you reintroduced the SPOF.
- TLS terminated at the LB but the internal hop left in plaintext when compliance
  requires encryption end-to-end (use re-encrypt/passthrough).
- Default round robin on long-lived connections â†’ uneven load (use least-conn).
- Operating HA, certs, and observability yourself â€” heavier than a managed LB, but
  zero lock-in and full control. Use when self-hosting or for cloud portability.


---

## Building Block: messaging-streaming

# Messaging & streaming â€” generic (self-host / open source)

The vendor-neutral default. If no cloud is named, this is the answer.

## Service mapping â†’ the generic options
- **Queue (work queue):** **RabbitMQ** (AMQP, rich routing, acks, per-message TTL,
  built-in DLX/dead-lettering) or **Redis Streams / Lists** (simple, fast, fewer
  guarantees). RabbitMQ for real delivery guarantees and routing; Redis for a
  light, fast broker when occasional loss is tolerable.
- **Pub/sub (fan-out):** **NATS** (lightweight, low-latency; core NATS is
  at-most-once, **JetStream** adds persistence + at-least-once) or RabbitMQ
  fanout/topic exchanges. NATS when you want simple, fast fan-out at the edge.
- **Stream (durable log):** **Apache Kafka** (partitioned, retained, replayable,
  consumer groups, transactions for effective-once *within* Kafka) â€” the default
  log. **Redis Streams** for a smaller-scale replayable log. **Pulsar** as a
  Kafka alternative with built-in tiered storage and multi-tenancy.
- **Durable workflow:** **Temporal** (open-source, self-hostable) â€” see
  `temporal.md` for when to choose it over hand-rolled orchestration.

## Decision-changing limits (verify against current docs)
- **Kafka:** ordering is per-partition only; consumer parallelism is capped at
  partition count per group; increasing partitions rehashes keys and breaks
  in-flight per-key order. Replication factor + `min.insync.replicas` set the
  durability/availability trade-off. Throughput is high (sequential disk writes).
- **RabbitMQ:** strong routing and per-message acks, but throughput is lower than
  a log and a deep queue in memory pressures the node. Quorum queues for
  durability; classic mirrored queues are deprecated.
- **Redis Streams:** in-memory first â€” durability depends on AOF/RDB; sizing must
  fit the retained stream in RAM or it evicts.
- **NATS core:** at-most-once (no persistence); use JetStream for retention/acks.

## Provider-specific trade-offs
- Self-hosting means *you* run replication, failover, upgrades, partition
  rebalancing, and capacity â€” real operational load. The payoff is no lock-in and
  full control of guarantees.
- Kafka's strength (a retained, replayable log) is also its cost: cluster +
  ZooKeeper/KRaft, partition planning, and consumer-offset management.

## Pitfalls
- Picking Kafka for a simple background-job queue â€” partitions, offsets, and
  cluster ops are overkill when RabbitMQ/SQS-style work queues fit.
- Using Redis as a broker and assuming durability â€” un-persisted messages vanish
  on restart (the classic "Redis loses messages" trap).
- Forgetting RabbitMQ needs explicit DLX config and publisher confirms; without
  them you get neither dead-lettering nor at-least-once publication.
- Setting Kafka partitions too low (caps consumer scaling) or too high (rebalance
  and metadata overhead).


---

## Building Block: observability

# Observability â€” generic (vendor-neutral / self-hosted)

The default answer. Instrument with **OpenTelemetry**, then route to open-source
backends. This stack is portable and the baseline every provider file maps against.

## Service mapping (recipe â†’ open source)
- **Instrumentation seam** â€” **OpenTelemetry** SDK + Collector. One instrumentation,
  any backend; the thing that keeps you off lock-in.
- **Metrics + alerting** â€” **Prometheus** (pull/scrape, PromQL) with
  **Alertmanager** for grouping/inhibition/routing. Long-term storage via Thanos or
  Mimir when a single Prometheus won't hold retention.
- **Dashboards** â€” **Grafana** (queries Prometheus, Loki, and Jaeger in one pane).
- **Logs** â€” **Loki** for log aggregation/query (label-indexed, cheap), or the
  Elasticsearch/ELK route. The full high-volume pipeline is `distributed-logging`.
- **Traces** â€” **Jaeger** (or Tempo / Zipkin); receives OTLP spans, supports tail
  sampling via the Collector.

## When to pick which
- Prometheus + Grafana + Alertmanager is the near-universal metrics/alerting core.
- Add Jaeger/Tempo only once requests cross services and you need per-hop timing.
- Loki when you want logs in Grafana cheaply by labels; ELK when you need full-text
  search and rich indexing (heavier to run).

## Limits / things that bite (verify against current docs)
- **Prometheus is single-node and not long-term storage by default** â€” retention
  and HA need Thanos/Mimir/Cortex; plan this before cardinality grows.
- **Cardinality is the hard ceiling** â€” series â‰ˆ product of label values; one
  unbounded label OOMs the server. Govern labels, not just scrape rate.
- **Pull model** needs network reachability to every `/metrics` target; short-lived
  jobs need the push-gateway.
- Self-hosting means *you* run the HA, retention, and upgrades â€” real operational
  cost.

## Pitfalls
- Treating Prometheus as durable/long-term storage without Thanos/Mimir.
- High-cardinality labels (user/request IDs) in metrics â€” push those to traces/logs.
- Synchronous OTLP export blocking the app; use the Collector with a queue + drop.
- Running ELK "because it's standard" when Loki + metrics would cover the need at a
  fraction of the operational load (borrowed context, not reasoning).


---

## Building Block: resilience-failure

# Resilience & failure â€” generic (vendor-neutral / self-host)

The default answer when no cloud is named. Maps the SKILL.md options to
open-source / library implementations you run yourself.

## Service mapping
- **Timeouts, retries, circuit breakers, bulkheads** â€” a resilience library in
  the app: Resilience4j (JVM), Polly (.NET), Hystrix-style wrappers, `tenacity`
  (Python), `failsafe`. Or a service mesh (Envoy/Istio, Linkerd) that applies
  timeouts, retries-with-budget, circuit breaking, and outlier ejection at the
  proxy â€” no app code, language-agnostic.
- **Rate limiting** â€” counters in **Redis** (`INCR`/`EXPIRE`, or a Lua script /
  sorted set for atomic sliding windows). At the edge: Nginx `limit_req` (leaky
  bucket), HAProxy stick-tables, Envoy global rate limiting, or an API gateway
  (Kong, APISIX) with a token-bucket plugin.
- **Health checks & failover routing** â€” owned by `load-balancing` (HAProxy/Nginx
  health checks, Keepalived/VRRP for a floating IP). Pair with N+1 redundancy here.
- **Redundancy** â€” run â‰¥2 of every stateless instance behind the LB; for stateful
  tiers use replication + a promotion mechanism (â†’ `data-storage`,
  `consistency-coordination`).
- **Queue-based containment** â€” a broker (Kafka/RabbitMQ) to absorb spikes and a
  DLQ for poison messages â†’ `messaging-streaming`.

## Limits / things that bite (verify against current docs)
- A **single Redis** holding rate-limit counters is itself a SPOF and a hot key;
  replicate it, and decide fail-open vs fail-closed if it's unreachable.
- Nginx `limit_req` is per-worker/per-instance unless backed by shared state â€”
  N instances multiply the effective limit by N.
- Service-mesh retries can **stack** with app-level retries (retries-of-retries);
  enable retries in exactly one layer, with a budget.
- Library defaults are often "infinite timeout / unlimited retries" â€” the unsafe
  default; set them explicitly.

## Provider-specific trade-offs
- A **service mesh** centralizes resilience config (one policy, all services) at
  the cost of sidecar latency/ops overhead; a **library** is leaner but
  per-language and per-service to wire up.
- Self-hosting means you own failover testing, counter-store HA, and capacity â€”
  no managed safety net.

## Pitfalls
- Configuring retries in both the mesh and the app (multiplicative load).
- Per-instance rate limits that don't add up to the intended global limit.
- A breaker with no fallback wired in â€” fail-fast into an error, not a degraded
  answer.
- One shared connection/thread pool across dependencies (no bulkhead).


---

## Building Block: sequencer

# Sequencer â€” Generic (self-hosted / open-source / library)

The default answer when no cloud is named. There is no "ID service" to buy in the
common case â€” you pick a library or a tiny piece of infrastructure you already run.

## Recipe mapping â†’ options
- **UUIDv4 / UUIDv7** â†’ standard-library or first-party uuid packages in every
  language (e.g. Python `uuid`, Java `java.util.UUID` + a v7 lib, Go `google/uuid`).
  No infrastructure.
- **ULID** â†’ small libraries in every ecosystem (e.g. `ulid` packages). No
  infrastructure; pick the *monotonic* variant if you generate many per ms.
- **Snowflake-style** â†’ embed a library (Twitter's original, Sony's `sonyflake`,
  Baidu `uid-generator`, or a ~50-line homegrown generator). Node id from config
  or a lease (see below).
- **Ticket / range allocator** â†’ a single SQL row. MySQL: `REPLACE INTO Tickets ...
  ; SELECT LAST_INSERT_ID()`. Postgres: a `SEQUENCE` with `CACHE`/range claims, or
  `UPDATE counters SET v = v + :block RETURNING v - :block`.
- **Plain sequence** â†’ Postgres `SERIAL`/`IDENTITY`, MySQL `AUTO_INCREMENT` â€” the
  default when one DB node owns the writes.
- **Node-ID leasing** â†’ ZooKeeper/etcd ephemeral node, Consul session, or a DB row
  with a TTL (coordination theory: `consistency-coordination`).

## Limits / things that bite (verify against current docs)
- A single ticket/sequence row tops out near a single relational node's write
  ceiling (~**1k QPS** order of magnitude; â†’ `back-of-the-envelope`). Range
  allocation with block size N multiplies that headroom by ~N.
- A 64-bit Snowflake's lifespan and node count are fixed by its bit split (e.g.
  ~69 years / 1024 nodes / 4M IDs/node/sec for 41/10/12) â€” chosen once, hard to
  change after IDs are issued.
- Postgres sequences are not gap-free and may skip on rollback/crash â€” fine for
  IDs, not for "count of rows."

## Trade-offs specific to self-hosting
- You own node-ID assignment, clock-skew monitoring (NTP/chrony), and allocator
  failover â€” no managed automation, but full portability and no lock-in.
- Embedding a Snowflake library means *no* network hop per ID (best latency) but
  pushes clock-sync and node-ID discipline onto every host.
- A ticket server is one more stateful thing to make highly available (run
  odd/even pair, or replicate).

## Pitfalls
- Reaching for a distributed scheme when one `SERIAL` column would serve the load.
- Static node ids on an autoscaling fleet â†’ silent duplicate IDs.
- Using the Unix epoch (not a recent custom epoch) and wasting decades of the
  timestamp range.
- UUIDv4 as a clustered primary key on a write-hot table â€” random order causes
  index page splits; prefer ULID/UUIDv7.
- No clock-rewind guard in a homegrown Snowflake generator.


---

## Building Block: service-decomposition

# Service decomposition â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer.

## What to run
- **Monolith / modular monolith** â€” any framework; enforce module boundaries with
  package/build structure (e.g. separate modules, no cross-module DB access).
- **Comms** â€” REST/JSON for breadth; **gRPC** for internal high-throughput typed
  calls; events via Kafka/RabbitMQ for async (â†’ `messaging-streaming`).
- **API gateway** â€” Nginx, Kong, Envoy, or Traefik (auth, routing, rate limiting).
- **Service discovery** â€” Consul, etcd, or ZooKeeper as a registry; or DNS-based
  (e.g. Kubernetes Services).
- **Service mesh** â€” Istio or Linkerd (Envoy sidecars: mTLS, retries, traffic
  shaping, telemetry).

## Topology
Clients â†’ gateway â†’ services (each owning its data store) â†’ async via a broker.
On Kubernetes, Services + DNS give discovery for free; add a mesh only when
uniform mTLS/retries/observability across many services justify the overhead.

## Limits / things that bite
- Each sync hop â‰ˆ a same-DC round trip plus the callee's work; deep call graphs
  blow latency budgets.
- A registry or gateway is a SPOF unless replicated; cache discovery client-side.
- Mesh sidecars add per-call latency and a real ops burden â€” not free.

## Pitfalls
- Sharing one database across services (distributed monolith).
- Splitting before a real driver (deploy/scale/ownership) exists.
- No distributed tracing â†’ undebuggable cross-service failures.


---

## Building Block: sharded-counters

# Sharded counters â€” generic (vendor-neutral)

The default answer when no cloud is named. Self-hosted / open-source primitives.

## Service mapping (generic recipe â†’ tools)
- **Single atomic counter** â†’ Redis `INCR`/`INCRBY`; SQL `UPDATE â€¦ SET c = c + 1`
  (one row); any store with an atomic increment.
- **Write-sharded counter** â†’ N Redis keys `counter:{id}:shard:{i}`, increment a
  random shard, sum on read (`MGET` the N shards). In SQL, N rows keyed by
  `(id, shard)` with `SELECT SUM(c) â€¦ GROUP BY id`.
- **Approximate distinct (uniques)** â†’ Redis HyperLogLog (`PFADD` / `PFCOUNT` /
  `PFMERGE`) â€” ~12 KB per sketch, ~2% error, mergeable across shards/windows.
- **Time-windowed** â†’ Redis keys per time bucket with `EXPIRE`, or a wide-column
  store (Cassandra) with a counter column per `(id, bucket)`.
- **Eventual aggregate at very high write scale** â†’ Cassandra **counter columns**
  (the cluster handles distribution; counters are eventually consistent and
  non-idempotent on retry â€” see pitfalls).

## When to pick which
- Redis for the hot path: atomic ops, HLL built in, microsecond increments,
  trivial key sharding. The common choice for likes/views/rate tallies.
- SQL single-row counter only at low write rates; shard to N rows when the row
  lock is the wall.
- Cassandra counters when writes are distributed-scale and eventual consistency
  is acceptable; avoid where retries must not double-count.

## Limits / things that bite (verify against current docs)
- A single Redis instance is **single-threaded** for command execution â€” one hot
  key is capped by one core's op rate; sharding the *key* (not just the cluster)
  is what removes the hot spot.
- Redis Cluster shards by hash slot: `counter:{id}:shard:{i}` keys spread across
  the cluster only if the slots differ â€” don't wrap the whole key in a hash tag.
- Redis HLL: ~12 KB max per key, ~0.81%/âˆšm (~2%) standard error; `PFCOUNT` on a
  union of large sketches is comparatively expensive â€” cache it.
- Cassandra counter columns are **not idempotent**: a timed-out write that is
  retried may apply twice (over-count). They can't be part of a row with
  non-counter columns, and deletes-then-reuse is unsafe.
- SQL single-row counters serialize on a row lock; contention shows as lock waits
  and deadlocks long before the box is CPU-bound.

## Pitfalls
- Treating a Redis counter as durable without AOF/replication â€” a crash drops
  recent increments.
- Choosing N once for the average and getting crushed when one count goes viral
  â€” size N to peak on the hottest count.
- Summing shards on every read instead of caching the aggregate.
- Using Cassandra counters where exactness matters (retry double-count).


---

## Building Block: task-scheduling

# Task scheduling â€” generic / self-hosted

The vendor-neutral default. When no cloud is named, this is the answer. The queue
transport underneath is `messaging-streaming`; this layer adds scheduling and
leasing.

## What to run
- **Celery (Python) / Sidekiq (Ruby) / BullMQ (Node)** â€” task-queue frameworks
  over Redis or RabbitMQ. Worker pools, retries+backoff, priority queues,
  scheduled/delayed tasks. Maps the **pull leasing** + **priority** options. The
  default for app-level background jobs.
- **Quartz (JVM)** â€” scheduler library; **clustered mode** (DB-backed) gives HA
  cron with misfire handling. Maps the **distributed scheduler** option.
- **Airflow / Dagster / Prefect** â€” DAG orchestrators; dependencies, backfill, run
  history. Maps the **workflow DAG** option for batch pipelines.
- **Redis sorted set** (`ZADD score=run_at` + poller) or **RabbitMQ delayed
  exchange** â€” maps the **delay-queue / timer** option.
- **Leader lock** in etcd / ZooKeeper / Consul / a DB row â€” makes a single-instance
  scheduler (Celery beat, Sidekiq-cron) HA without double-firing.

## Topology
- One scheduler/beat process (leader-elected if HA) enqueues due jobs.
- A queue (Redis/RabbitMQ) holds ready and delayed jobs.
- A horizontally-scaled worker pool leases and drains; scale workers on backlog.
- A DLQ (or failed-set) holds poison tasks after the retry cap.

## Limits / things that bite
- **Beat/cron is usually single-instance** â€” running two without a leader lock
  double-fires every recurring job. Make it HA yourself.
- **Visibility-timeout semantics differ by broker:** Redis-backed task queues
  often re-deliver on worker loss only if configured (`acks_late`, visibility
  timeout); the default may ack-on-receive and *lose* a job on crash. Set it
  deliberately.
- **Redis as broker can lose messages** (no fsync per message) â€” fine for
  recompute, risky for must-run jobs; RabbitMQ persists but you operate the nodes.
- **Priority queues** in some brokers are coarse (a fixed set of levels), not
  arbitrary integer priority.

## Pitfalls
- Using `acks_early`/ack-on-receive for jobs that must survive a crash.
- No leader lock on the scheduler â†’ split-brain double-fire.
- Reaching for Airflow for low-latency or high-rate tiny jobs (scheduler tick
  latency makes it the wrong tool).
- Treating Redis-broker durability as guaranteed for money/must-run work.

Operationally heavier than a managed service, but zero lock-in and full control.
Use when running your own infra or for portability across clouds.


---


