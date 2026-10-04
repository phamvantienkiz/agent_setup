# AWS Cloud Architecture & Service Mapping

Comprehensive mapping of system design building blocks to AWS managed services and architecture patterns.

---

## Building Block: api-design

# API design â€” AWS

## Service mapping
- **API Gateway (REST API)** â€” full-featured managed REST front: per-method
  throttling, API keys + usage plans, request validation, WAF, caching. The
  default for a public REST contract.
- **API Gateway (HTTP API)** â€” leaner, cheaper, lower-latency HTTP front; fewer
  features (no built-in request validation/caching). Use when you don't need the
  REST API extras.
- **API Gateway (WebSocket API)** â€” managed WebSocket with `$connect`/`$disconnect`
  routes; AWS holds the connections so you don't size a stateful fleet.
- **AppSync** â€” managed GraphQL (resolvers, real-time subscriptions, auth). Use
  when the contract is GraphQL and you don't want to run your own server.
- **ALB** â€” L7 routing for gRPC/HTTP to containers/instances when you don't need
  gateway features; pairs with `load-balancing`.

## When to pick which
REST API for rich public APIs needing keys/throttling/validation; HTTP API for
simple low-latency proxies; WebSocket API for managed push; AppSync for GraphQL;
ALB for plain gRPC/HTTP service traffic.

## Limits / things that bite (verify against current docs)
- API Gateway has a **default ~29s integration timeout** â€” long requests must go
  async (return 202 + poll, or push). Payloads are capped (~10 MB REST).
- Account-level and per-method **throttle/burst quotas** apply; usage plans set
  per-key rate/burst â€” design your rate limits to these, not above them.
- WebSocket API bills per message + connection-minute and caps idle/total
  connection duration â€” long-lived clients reconnect.
- Pricing differs sharply: HTTP API is much cheaper per request than REST API at
  scale.

## Pitfalls
- Putting a slow synchronous call behind the 29s timeout instead of going async.
- Assuming API Gateway gives idempotency â€” it doesn't; you still build the
  idempotency-key store (DynamoDB with a TTL attribute is the common fit).
- Reaching for REST API features (and cost) when HTTP API would do.
- Lock-in: AppSync resolvers and API Gateway mapping templates don't port to other
  clouds.


---

## Building Block: blob-store

# Blob store â€” AWS

## Service mapping
- **S3** â€” the object store. Buckets + keys, strong read-after-write, versioning, multipart
  upload, presigned URLs, lifecycle rules, event notifications. The default.
- **Storage classes** (the tiering knob) â€” *Standard* (hot), *Standard-IA* / *One Zone-IA*
  (infrequent access, cheaper storage + retrieval fee), *Glacier Instant/Flexible Retrieval*
  and *Glacier Deep Archive* (archive; minutes-to-hours retrieval, cheapest at rest),
  *Intelligent-Tiering* (auto-moves objects between tiers by access pattern).
- **Durability/replication** â€” S3 handles intra-region durability internally; **Cross-Region
  Replication (CRR)** / Same-Region Replication for geo/compliance copies (asynchronous).
- **CloudFront** â€” CDN in front of S3 origin (â†’ `content-delivery`).

## When to pick which
Standard for actively served objects; IA for backups read a few times a month; Glacier/Deep
Archive for compliance retention off the request path; Intelligent-Tiering when access is
unpredictable and you don't want to manage lifecycle transitions yourself.

## Limits / things that bite (verify against current docs)
- Max single object size and the single-PUT vs multipart threshold â€” large objects *must* use
  multipart; multipart part-size minimum (~5 MB) and a max part count cap effective object size.
- Glacier/Deep Archive retrievals take minutes to hours and charge retrieval + request fees â€”
  never on a latency path.
- IA/One Zone-IA have a minimum billable object size and minimum storage duration; tiering
  many tiny objects can cost *more* than Standard.
- **Egress to the internet is billed**; CloudFront in front cuts both egress and origin load.
- Request rate scales per *prefix* â€” historically high-cardinality random prefixes spread load;
  monotonic/date prefixes can hotspot.

## Provider-specific trade-offs
- Deep S3 integration (IAM, KMS encryption, event â†’ Lambda, S3 Select) is convenient but is
  lock-in; the S3 API itself is the de-facto standard others emulate.
- Intelligent-Tiering removes lifecycle work but adds a per-object monitoring charge â€” wasteful
  for very small objects.

## Pitfalls
- Putting Glacier on a read path and timing out requests.
- No lifecycle rule to **abort incomplete multipart uploads** â†’ orphaned parts billed forever.
- Versioning on with no expiry of non-current versions â†’ silent storage growth.
- Serving popular objects straight from S3 without CloudFront â†’ egress blowup.
- Over-broad/long-lived presigned URLs and bucket policies â€” scope tight, expire short.


---

## Building Block: caching

# Caching â€” AWS

## Service mapping
- **ElastiCache for Redis / Valkey** â€” managed Redis; replication, automatic
  failover (Multi-AZ), cluster mode (sharding), backups. The default managed cache.
- **ElastiCache for Memcached** â€” managed Memcached; multithreaded, simple,
  node-based scaling; no persistence/replication.
- **ElastiCache Serverless** â€” auto-scaling capacity, pay-per-use; removes node
  sizing at a price premium.
- **DAX** â€” DynamoDB Accelerator; an in-line write-through cache *specifically*
  for DynamoDB (microsecond reads) â€” use only when the origin is DynamoDB.
- **CloudFront** â€” edge caching for static/media (â†’ `content-delivery`).

## When to pick which
Redis for replication/persistence/data structures and Multi-AZ failover;
Memcached for a plain horizontally-scaled object cache; DAX only with DynamoDB;
Serverless when load is spiky and you don't want to size nodes.

## Limits / things that bite (verify against current docs)
- Multi-AZ failover takes seconds and can drop un-replicated writes.
- Cluster mode shards by hash slot; cross-slot multi-key ops need hash tags.
- Node memory and network bandwidth are per instance type â€” a hot key still
  saturates one shard.
- ElastiCache lives in your VPC; cross-AZ data transfer is billable.

## Pitfalls
- Reaching for DAX when the origin isn't DynamoDB (it isn't a general cache).
- Forgetting `maxmemory-policy` / eviction config carries over from Redis.
- Assuming Serverless is cheaper at steady high load â€” it usually isn't.
- Lock-in: DAX and ElastiCache configs don't port directly to other clouds.


---

## Building Block: consistency-coordination

# Consistency & coordination â€” AWS

Only the managed pieces that change the generic recipe. For anything not listed,
the generic recipe (self-hosted etcd/ZooKeeper, Cassandra, etc.) is the answer.

## Service mapping
- **DynamoDB** â€” leaderless, quorum-replicated store with a **per-read consistency
  knob**: default **eventually consistent** reads (cheaper, may lag); pass
  `ConsistentRead=true` for a **strongly consistent** read (latest committed, ~2Ã— the
  read cost, single-region only). This is the decision-changing detail: consistency
  is chosen *per request*, not per table.
- **DynamoDB global tables** â€” multi-region, **multi-leader / last-write-wins**
  (AP across regions): every region is writable and converges; cross-region reads
  are eventually consistent. Strong reads do **not** span regions.
- **DynamoDB transactions** (`TransactWriteItems`) â€” ACID across items in one region
  via an internal 2PC-like protocol; single-region, item-count and size limited.
- **Aurora / RDS** â€” single-leader (writer) + replicas; reads from replicas lag.
  Multi-AZ failover takes seconds (a write-availability gap).
- **No managed ZooKeeper/etcd as a primitive** â€” run them yourself, or use
  application-level coordination; **MSK** ships ZooKeeper/KRaft for Kafka's own use.

## Limits / things that bite (verify against current docs)
- Strong reads in DynamoDB are single-region and don't work on global secondary
  indexes; global tables are LWW, so concurrent cross-region writes silently lose.
- DynamoDB partition throughput is per-partition-key â€” a hot key throttles one
  partition regardless of table capacity (consistent hashing spreads keys, not a
  single hot key).
- Multi-AZ RDS/Aurora failover is seconds, and async replicas can lose the last
  un-replicated writes.

## Pitfalls
- Assuming DynamoDB reads are strong by default â€” they are eventual unless you ask.
- Expecting global-table strong consistency across regions (it's LWW eventual).
- Treating LWW conflict resolution as safe for counters/accumulators (it isn't â€”
  use atomic counters or a CRDT-style model).


---

## Building Block: content-delivery

# Content delivery â€” AWS

## Service mapping
- **CloudFront** â€” the CDN; global PoPs, pull from origin (S3, ALB, or any HTTP
  origin), `Cache-Control`/policy-driven TTLs, signed URLs/cookies, and
  **CloudFront Functions / Lambda@Edge** for edge logic. The default.
- **Origin Shield** â€” an opt-in regional mid-tier cache for a CloudFront
  distribution; collapses PoP misses into one origin fetch (â†’ origin shield option).
- **S3** â€” the usual static/media origin behind CloudFront; pair via Origin Access
  Control so the bucket isn't publicly reachable.
- **Route 53** â€” DNS geo/latency routing to origins or for multi-region (â†’ `load-balancing`).
- No separate "push CDN" product â€” push is "upload to S3, serve via CloudFront."

## When to pick which
CloudFront + S3 for static/media; add Origin Shield when many PoPs hammer a single
origin or to blunt stampedes; Lambda@Edge only when you need real request/response
manipulation (CloudFront Functions for cheap lightweight header/URL rewrites).

## Limits / things that bite (verify against current docs)
- **Cache key** is set by *cache policies* â€” forwarding all query strings/cookies/
  headers tanks hit rate; forward only what varies the response.
- Invalidations are **eventually consistent** and the first chunk per month is free,
  then billed per path â€” prefer versioned URLs over mass invalidation.
- Egress (data transfer out) is the dominant cost; pricing tiers vary by region.
- Lambda@Edge has size/runtime limits and runs in the requesting region â€” adds
  latency and complexity vs CloudFront Functions.

## Pitfalls
- Public S3 bucket as origin (use Origin Access Control instead).
- Forwarding cookies/all query strings in the cache policy â†’ near-zero hit rate.
- Relying on invalidation for freshness and being surprised by propagation lag.
- Lock-in: cache policies, Lambda@Edge, and signed-URL formats don't port to other clouds.


---

## Building Block: data-storage

# Data Storage â€” AWS

## Service mapping â†’ options
- **RDS** (Postgres/MySQL/MariaDB) â€” managed relational; automated backups,
  read replicas, Multi-AZ failover. The default managed SQL.
- **Aurora** â€” RDS-compatible (Postgres/MySQL) with a distributed storage layer:
  up to 15 low-lag read replicas, fast failover, storage auto-grows. Pick over
  plain RDS when you need more read scale and quicker failover.
- **DynamoDB** â€” managed key-value + document; partition key (+ optional sort
  key), single-digit-ms reads, on-demand or provisioned capacity, auto-sharded.
  Maps to key-value / wide-column options.
- **ElastiCache** â€” managed Redis/Memcached (see `caching`), not a system of
  record.
- **Keyspaces** (managed Cassandra), **Neptune** (graph), **DocumentDB**
  (Mongo-compatible) â€” use when you specifically need those models.

## Limits / things that bite (verify against current docs)
- **DynamoDB:** item size capped (~400 KB); a single partition has a throughput
  ceiling, so a hot partition key throttles even when total capacity is spare â€”
  design the PK for even spread. Strongly-consistent reads cost more RCUs and
  only work on the base table, not global secondary indexes (GSIs are eventually
  consistent).
- **RDS/Aurora:** Multi-AZ failover takes seconds to ~a minute; an async read
  replica can lag and lose the tail if promoted. Connection limits scale with
  instance size â€” front with **RDS Proxy** to survive Lambda/spiky fan-out.
- Cross-AZ data transfer is billable.

## Provider-specific trade-offs
- DynamoDB is serverless and scales effortlessly but locks you into its data
  model and query style (no joins, access patterns must be designed up front);
  migrating off is real work.
- Aurora decouples compute from storage (cheap replicas) but is AWS-only.
- On-demand DynamoDB is convenient but pricier than well-sized provisioned
  capacity at steady high load.

## Pitfalls
- Choosing DynamoDB then fighting it with scan-heavy/ad-hoc queries it isn't built
  for â€” that's a relational workload.
- Hot partition key throttling while the table looks under-provisioned.
- Skipping RDS Proxy and exhausting connections under serverless fan-out.
- Assuming GSIs are strongly consistent.


---

## Building Block: distributed-logging

# Distributed logging â€” AWS

## Service mapping (generic stage â†’ AWS)
- **Collect:** CloudWatch agent / Fluent Bit (the `aws-for-fluent-bit` image is the
  standard ECS/EKS sidecar/daemon). Lambda and many services log to **CloudWatch Logs**
  natively.
- **Buffer / transport:** **Kinesis Data Streams** as the durable log bus, or
  **Kinesis Data Firehose** for buffered, no-ops delivery straight to a sink. (Kafka
  via **MSK** if you already run Kafka â€” owned by `messaging-streaming`.)
- **Index / search:** **OpenSearch Service** (managed Elasticsearch/OpenSearch) for
  full-text search; CloudWatch Logs Insights for query-in-place without a separate
  cluster.
- **Cold archive:** **S3** via Firehose, with lifecycle to Glacier classes; query in
  place with **Athena** (â†’ `blob-store`).

A very common AWS recipe: agents/services â†’ CloudWatch Logs â†’ **subscription filter** â†’
Firehose â†’ S3 (cold) and/or OpenSearch (hot search). Firehose does the buffering,
batching, compression, and retry so you don't run agents for that hop.

## Limits / things that bite (verify against current docs)
- **CloudWatch Logs `PutLogEvents`** has per-request batch size and per-stream
  throughput limits; bursts get throttled â€” batch and back off.
- **Firehose** buffers by size *or* time interval, whichever first â€” there is an
  inherent delivery delay (secondsâ€“minutes); not for interactive tailing.
- **Kinesis Data Streams** throughput is per-shard (fixed MB/s in, records/s); ordering
  is per-shard only; you must scale shards for peak ingest.
- **OpenSearch Service** is the same shard/heap pressure as self-hosted ES; instance
  type caps RAM and the index queue.
- CloudWatch Logs **retention is per-log-group**; default can be "never expire" â†’
  silent cost growth. Set it explicitly.

## Provider trade-offs
- CloudWatch Logs is the path of least resistance (most services emit there for free)
  but ingestion + storage + Insights scans are billed separately and add up fast.
- Firehose â†’ S3 is the cheap durable archive; OpenSearch is the expensive hot search â€”
  send everything to S3, a sampled/filtered subset to OpenSearch.
- Lock-in: subscription filters, Firehose transforms, and Insights queries don't port
  to other clouds.

## Pitfalls
- Leaving log groups on infinite retention (cost) â€” or expecting Firehose to be
  real-time (it isn't).
- Sending full-volume logs to OpenSearch when most queries are label filters that S3 +
  Athena would answer for far less.
- Forgetting Kinesis shard limits during an incident spike â†’ throttled, dropped logs
  exactly when you need them.


---

## Building Block: distributed-search

# Distributed search â€” AWS

## Service mapping
- **Amazon OpenSearch Service** â€” managed OpenSearch/Elasticsearch; provisioned
  domains (you size data/master nodes, shards, replicas) â€” the default managed
  full-text engine on AWS.
- **OpenSearch Serverless** â€” auto-scaling capacity in "collections" (search /
  time-series / vector); removes node sizing at a price premium and with less
  low-level tuning control.
- **OpenSearch Ingestion** â€” managed pipeline (collect/transform â†’ index); pairs
  with the indexing pipeline. A durable buffer (e.g. Kinesis/MSK) still belongs
  in front (â†’ `messaging-streaming`).
- **CloudSearch** â€” older managed search; prefer OpenSearch for new designs.

## When to pick which
Provisioned domains when you want control over shard/replica sizing and steady
cost; Serverless when load is spiky and you don't want to size nodes; Ingestion
when you want managed transform-and-load rather than running your own indexer.

## Limits / things that bite (verify against current docs)
- Provisioned domains need master nodes for stability at scale; under-sizing
  master/data nodes causes cluster instability under load.
- Storage, shard-per-node, and field-count limits per instance type â€” a hot or
  oversized shard still saturates one node and drags fan-out latency.
- Serverless OCU (compute unit) billing can surprise at steady high load; it
  isn't automatically cheaper than a right-sized provisioned domain.
- Version upgrades and blue/green domain changes can be disruptive â€” plan them.

## Pitfalls
- Assuming Serverless removes all tuning â€” you lose some shard/analyzer control.
- Skipping dedicated master nodes on a production provisioned domain.
- Treating the domain as a source of truth instead of a reindexable derived copy.
- Lock-in: OpenSearch APIs are portable, but Serverless collections and
  Ingestion configs don't port directly to other clouds.


---

## Building Block: dns

# DNS â€” AWS

## Service mapping
- **Route 53** â€” managed authoritative DNS on a global anycast network; the default.
  Hosted zones (public/private), health checks, and routing policies cover every
  generic option:
  - **Simple / Weighted / Latency / Geolocation / Geoproximity / Failover /
    Multivalue-answer** routing policies map 1:1 to the generic policies (geoproximity
    adds a bias knob to shift traffic between regions).
  - **Alias records** â€” Route 53's apex-alias (the generic `ALIAS`); point the zone
    apex at an ELB/CloudFront/S3/API Gateway target with no charge for alias queries.
  - **Health checks** â€” endpoint, calculated (combine checks), or CloudWatch-alarm
    based; gate any policy so unhealthy targets drop out.
- **Route 53 Resolver** â€” for hybrid/VPC DNS (inbound/outbound endpoints); not traffic steering.
- **Global Accelerator** â€” anycast IP + health-based failover that reacts *faster
  than DNS* (no TTL wait) by steering at the network layer; reach for it when DNS
  TTL-bound failover is too slow.

## When to pick which
Route 53 alias at the apex onto an ELB/CloudFront is the standard front door.
Latency routing for speed, geolocation for residency, failover for active-passive
DR, weighted for canary. Use Global Accelerator instead when you need sub-TTL
failover or a fixed entry IP.

## Limits / things that bite (verify against current docs)
- Health-check failover is still **TTL + propagation** bound â€” Global Accelerator
  exists precisely to beat that.
- Latency records route by the *resolver's* AWS-measured latency, not the user's.
- Alias targets are limited to specific AWS resource types.
- Per-hosted-zone record counts and health-check counts have soft quotas.

## Pitfalls
- Putting a `CNAME` at the apex instead of an alias record.
- Expecting Route 53 failover to be instant (it is not â€” consider Global Accelerator).
- Geoproximity bias misconfigured, silently overloading one region.
- Single hosted zone with no secondary-provider plan for a critical property.


---

## Building Block: load-balancing

# Load balancing â€” AWS

## Service mapping
- **ALB (Application Load Balancer)** â€” managed **L7**; routes by host/path/header/
  query, TLS termination, HTTP/2 + gRPC, WebSockets, target groups, sticky sessions
  via LB-issued cookie. The default for HTTP(S) services.
- **NLB (Network Load Balancer)** â€” managed **L4**; ultra-high throughput, very low
  latency, static IP / Elastic IP, TLS passthrough or termination, preserves source
  IP. Use for non-HTTP, extreme throughput, or static-IP needs.
- **CLB (Classic)** â€” legacy L4/L7; avoid for new designs (use ALB/NLB).
- **Auto Scaling Group + target group** â€” the fleet ALB/NLB balances over; ASG adds/
  removes instances and the LB health-gates them (the stateless-tier enabler).
- **Route 53** â€” DNS-level latency/geo/weighted routing (cross-region steering, â†’
  `content-delivery`), not an L4/L7 LB.
- **Global Accelerator** â€” anycast static IPs that steer to the nearest healthy
  regional LB.

## When to pick which
ALB for content-based HTTP routing and TLS offload; NLB for raw TCP/UDP
throughput, static IPs, source-IP preservation, or mTLS passthrough; pair an NLB
in front of an ALB only when you need both static IP and L7 routing.

## Limits / things that bite (verify against current docs)
- ALB scales by adding capacity units â€” it **pre-warms slowly**; a sudden traffic
  cliff can outrun scaling. Engage support for known spikes.
- ALB idle-connection timeout (default ~60s) silently drops long-lived/streaming
  connections; tune it and your backends' keep-alive.
- NLB to targets in the same subnet can break source-IP/health-check unless
  client-IP preservation is configured correctly.
- ASG health checks (EC2) and LB health checks are *separate* â€” an instance can be
  "EC2-healthy" but LB-unhealthy; wire ELB health checks into the ASG.
- Cross-AZ load balancing may incur data-transfer charges and is on/off per LB type.

## Pitfalls
- Relying on ALB stickiness instead of externalizing session state, then losing
  sessions on scale-in.
- Forgetting deregistration delay (connection draining) so deploys drop requests.
- Treating Route 53 latency routing as a substitute for in-region balancing (it
  isn't â€” it steers between regions).
- Lock-in: ALB routing rules, target groups, and Global Accelerator don't port to
  other clouds.


---

## Building Block: messaging-streaming

# Messaging & streaming â€” AWS

## Service mapping â†’ the generic options
- **SQS (Standard)** â€” managed work queue; at-least-once, best-effort ordering,
  near-infinite throughput. The default queue. Built-in DLQ via redrive policy.
- **SQS (FIFO)** â€” exactly-once *processing* (within a dedup window) and ordering
  per `MessageGroupId`; lower throughput than Standard. Use when order/dedup matter.
- **SNS** â€” pub/sub fan-out; push to SQS, Lambda, HTTP. SNSâ†’SQS fan-out is the
  canonical AWS decouple-and-fan-out pattern.
- **EventBridge** â€” event bus with content-based routing/filtering and SaaS
  integrations; pub/sub with rules. Use for cross-service event routing.
- **Kinesis Data Streams** â€” partitioned, replayable log (the Kafka analog);
  ordering per shard, consumers track position. Use for streams/replay.
- **MSK** â€” managed Apache Kafka; use when you specifically need Kafka APIs/ecosystem.

## Decision-changing limits (verify against current docs)
- **SQS message size** ~256 KB (larger â†’ S3 + claim-check pointer).
- **SQS visibility timeout** governs redelivery; shorter than job time â†’ duplicate
  processing. Max in-flight messages is bounded.
- **SQS FIFO throughput** is far lower than Standard (raised by batching /
  high-throughput mode, still a ceiling); ordering is per `MessageGroupId`.
- **Kinesis** ~1 MB/s or 1000 records/s write **per shard**, ~2 MB/s read;
  parallelism = shard count; resharding is an operation. A hot partition key
  saturates one shard.
- **SNS/EventBridge** are at-least-once â†’ subscribers must be idempotent.

## Provider-specific trade-offs
- SQS Standard can deliver duplicates and out of order â€” consumers must be
  idempotent (the AWS "delivered twice" gotcha). FIFO removes most of this at a
  throughput cost.
- Managed DLQ is first-class (redrive), but you must set max receives and *watch*
  the DLQ â€” it's silent by default.
- Kinesis vs. MSK: Kinesis is simpler/serverless-ish but AWS-specific (lock-in);
  MSK is portable Kafka but you manage more.
- For durable workflows AWS offers **Step Functions** (state-machine orchestration,
  AWS-native) â€” compare with Temporal in `temporal.md`.

## Pitfalls
- Using SQS Standard where order matters, then bolting on ordering logic â€” use FIFO.
- Forgetting SNS/SQS/Kinesis are at-least-once â†’ no idempotency â†’ double side effects.
- Under-sharding Kinesis (throttling) or ignoring a hot shard from a skewed key.
- No redrive/DLQ â†’ poison messages redeliver until retention expires, then vanish.


---

## Building Block: observability

# Observability â€” AWS

## Service mapping
- **CloudWatch Metrics** â€” managed metrics + dashboards + **CloudWatch Alarms** for
  alerting. The default; integrates with most AWS services out of the box.
- **CloudWatch Logs** â€” managed log ingestion/query (Logs Insights). The pipeline
  concern is `distributed-logging`; here it's the metrics/alarm + log-metric-filter
  side.
- **X-Ray** â€” managed distributed tracing; OTLP via the ADOT (AWS Distro for
  OpenTelemetry) Collector.
- **Amazon Managed Service for Prometheus (AMP)** + **Managed Grafana** â€” run the
  generic Prometheus/Grafana stack without self-hosting; pick this to stay
  PromQL-portable instead of CloudWatch-native.
- **CloudWatch Synthetics / Route 53 health checks** â€” synthetic + external
  liveness probing (health-check *gating* is `load-balancing`).

## When to pick which
- CloudWatch for native, low-setup metrics+alarms across AWS services.
- AMP + Managed Grafana when you want the generic recipe managed (portability,
  PromQL, existing dashboards).
- X-Ray for tracing if you're CloudWatch-native; ADOT keeps you OTel-portable.

## Limits / things that bite (verify against current docs)
- **CloudWatch custom-metric and high-cardinality dimension costs add up fast** â€”
  each unique dimension combination is a billable custom metric.
- **Standard CloudWatch metric granularity is 1-minute** (high-resolution down to
  1s costs more) â€” alerting reaction time is bounded by this.
- **PutMetricData / API throttling** under bursty custom-metric publishing.
- X-Ray sampling is configured separately; default rules may under-sample errors.

## Pitfalls
- Emitting high-cardinality CloudWatch dimensions (user/request IDs) â€” cost
  explosion; keep those in logs/traces.
- Assuming 1-minute metrics are fast enough for tight SLO burn alerts.
- CloudWatch-native lock-in: dashboards/alarms don't port; AMP+Grafana avoids this.
- Forgetting cross-account/cross-region aggregation cost when centralizing telemetry.


---

## Building Block: resilience-failure

# Resilience & failure â€” AWS

## Service mapping
- **Redundancy / failover** â€” span **multiple Availability Zones** (the default
  unit of fault isolation); go **multi-Region** only for whole-Region survival.
  Auto Scaling groups replace failed instances; ALB/NLB stop routing to unhealthy
  targets (health checks â†’ `load-balancing`).
- **DNS failover** â€” **Route 53 health checks** + failover/latency/weighted
  routing flip traffic to a healthy endpoint or Region.
- **Rate limiting / load shedding** â€” **API Gateway** usage plans + throttling
  (token-bucket: rate + burst); **AWS WAF rate-based rules** at CloudFront/ALB to
  shed abusive IPs before they reach the app.
- **Retries / timeouts / circuit breaking** â€” the **AWS SDK** retries with
  backoff + jitter and adaptive mode built in; **App Mesh** (Envoy) adds
  mesh-level timeouts/retries/circuit breaking.
- **Queue containment** â€” **SQS** (with a redrive policy â†’ DLQ) absorbs spikes and
  isolates poison messages â†’ `messaging-streaming`.
- **Shared limiter store** â€” **ElastiCache (Redis)** for counters.

## Limits / things that bite (verify against current docs)
- Multi-AZ failover for managed stores (RDS, ElastiCache) takes **seconds** and
  can drop un-replicated writes â†’ `consistency-coordination`.
- API Gateway throttling is **token bucket** (steady rate + burst); account- and
  stage-level limits stack â€” a low account limit caps everything.
- WAF rate-based rules evaluate over a rolling window with a **minimum** window
  and coarse granularity; not a precise per-second limiter.
- Cross-AZ data transfer is billable; chatty cross-AZ retries cost money.

## Provider-specific trade-offs
- Multi-AZ is cheap insurance and usually enough; **multi-Region is a large
  step-up** in cost and complexity (data replication, failover orchestration) â€”
  justify it against the availability target, don't default to it.
- Route 53 failover depends on health-check sensitivity: too aggressive flaps,
  too lax delays cutover.

## Pitfalls
- Assuming Multi-AZ = zero data loss (it's seconds of async-replicated risk).
- Double retries: SDK adaptive retries **plus** app-level retries â†’ load
  multiplier. Pick one layer.
- Relying on WAF rate rules for fine-grained per-user limits â€” use API Gateway /
  app-level for that.
- A single-AZ ElastiCache limiter store as an unnoticed SPOF.


---

## Building Block: sequencer

# Sequencer â€” AWS

## Service mapping
There is **no dedicated AWS ID-generation service** â€” the generic recipe (a
Snowflake library, ULID/UUIDv7, or a ticket row) is the answer. What AWS changes
is *where you store and shard* the ID and how you run the allocator:

- **DynamoDB** â€” IDs are your **partition key**. A monotonic/sequential key
  concentrates writes on one partition (hot partition); use a high-cardinality key
  (UUIDv7/ULID/Snowflake) or add a write-sharding prefix. DynamoDB has **no
  auto-increment**; an atomic-counter item (`UpdateItem ADD`) can act as a small
  ticket server but serializes on that one item.
- **Aurora / RDS (MySQL, Postgres)** â€” native `AUTO_INCREMENT`/`SEQUENCE` and the
  ticket-server pattern work as in generic. Aurora's single writer means a single
  sequence still serializes through it.
- **Lambda / ECS / EC2** â€” host the Snowflake/ULID library here. For Snowflake,
  the challenge is node-ID assignment under autoscaling (see below).
- **ElastiCache (Redis)** â€” `INCR`/`INCRBY` gives an atomic counter or a fast
  range allocator (claim a block with `INCRBY`), backed by Redis durability
  settings.

## Limits / things that bite (verify against current docs)
- **DynamoDB partition throughput** is capped per partition (order of a few
  thousand WCU); a sequential partition key funnels all new writes there. This is
  the most common ID-related AWS failure â€” partitioning fix lives in `data-storage`.
- **Lambda has no stable node identity** â€” concurrent executions scale elastically
  and reuse nothing, so a static Snowflake node id is unsafe. Lease a node id (e.g.
  from a DynamoDB item with a TTL) or prefer ULID/UUIDv7 which need no node id.
- **Clock:** EC2/Lambda clocks are NTP-synced but can still step; keep the
  rewind guard. (Verify current quotas against AWS docs â€” they drift.)

## Provider-specific trade-offs
- Choosing DynamoDB strongly nudges you toward UUIDv7/ULID/Snowflake (high
  cardinality) and away from sequential keys â€” a real design constraint, not a
  preference.
- An atomic-counter item or Redis `INCR` ties your ID rate to one item/key's
  throughput; range-allocate to relieve it.

## Pitfalls
- Sequential ID as a DynamoDB partition key â†’ hot partition and throttling.
- Static Snowflake node ids on Lambda/Fargate â†’ duplicates under scale-out.
- Assuming DynamoDB can auto-increment â€” it can't; you build the allocator.


---

## Building Block: service-decomposition

# Service decomposition â€” AWS

## Service mapping
- **Compute for services** â€” ECS/Fargate or EKS (containers), or Lambda (functions)
  for event-driven/spiky services.
- **API gateway / front door** â€” API Gateway (REST/HTTP/WebSocket, auth, throttling)
  or ALB (path/host routing) for simpler container fronting.
- **Service discovery** â€” AWS Cloud Map (+ ECS Service Connect); EKS uses
  Kubernetes DNS.
- **Service mesh** â€” App Mesh (Envoy-based) or self-managed Istio on EKS.
- **Cross-service workflows / saga** â€” Step Functions (orchestration) or
  EventBridge (choreography); transactional outbox via DynamoDB Streams.

## When to pick which
ALB for plain container routing; API Gateway when you need managed auth/throttle/
usage plans; Lambda + EventBridge for event-driven services; Step Functions when a
multi-service write needs orchestrated compensation (saga).

## Limits / things that bite (verify against current docs)
- API Gateway adds latency + per-request cost and has payload/timeout limits
  (e.g. ~29s integration timeout) â€” not for long-running calls.
- App Mesh/Envoy sidecars add latency and operational surface.
- Cloud Map / Service Connect health-check + DNS TTL lag affects failover speed.

## Pitfalls
- API Gateway accreting business logic (mappings/transforms) into a hidden monolith.
- Lambda for chatty synchronous chains â†’ cold starts + fan-out latency.
- Cross-service ACID expectations â€” use Step Functions/saga, not 2PC.


---

## Building Block: sharded-counters

# Sharded counters â€” AWS

Only the contention/atomicity differences that change the recipe. Default to the
generic recipe; this maps it to AWS services.

## Service mapping
- **DynamoDB atomic counter** â€” `UpdateItem` with an `ADD`/`SET c = c + :n`
  expression increments a number attribute atomically. The single-counter
  option.
- **DynamoDB + write sharding** â€” append a random suffix to the partition key
  (`pk = id#shard{rand(0..N-1)}`), increment the sharded item, and **sum the N
  items** (a `Query` or N `GetItem`s) on read. The striped-counter recipe â€” and
  the standard fix for a hot partition.
- **ElastiCache for Redis / Valkey** â€” managed Redis for the fast path: `INCR`,
  HyperLogLog (`PFADD`/`PFCOUNT`), key sharding. Use when you want
  microsecond increments and built-in HLL.
- **Amazon Keyspaces (Cassandra)** â€” managed counter columns for
  distributed-scale eventual counts (same non-idempotent caveat as generic).

## When to pick which
DynamoDB atomic counter when the item is durable system-of-record and write rate
fits one partition; DynamoDB write-sharding when a single partition key goes hot;
ElastiCache Redis when the count is a fast/ephemeral tally with HLL needs.

## Limits / things that bite (verify against current docs)
- A DynamoDB **partition** has a hard write ceiling (historically ~1,000 WCU/s);
  hammering one key is a **hot partition** that throttles regardless of table
  capacity â€” write-sharding the key is the fix.
- DynamoDB updates are atomic per item but the table is eventually consistent on
  reads unless you request a strongly-consistent read (which costs more and can't
  span the N sharded items as one transaction).
- Reading a write-sharded total is N reads + a client-side sum; size N against
  the per-partition ceiling, not the average.
- ElastiCache Multi-AZ failover takes seconds and can drop un-replicated
  increments.

## Pitfalls
- Leaving a viral counter on one partition key and blaming "DynamoDB throttling"
  â€” it's a hot partition; shard the key.
- Assuming a single `UpdateItem ADD` scales infinitely â€” it's capped by the
  partition.
- Forgetting the N-shard read can't be one strongly-consistent transaction â€” the
  summed total is eventually consistent.
- Lock-in: DynamoDB key-sharding layout and Keyspaces counters don't port
  directly to other clouds.


---

## Building Block: task-scheduling

# Task scheduling â€” AWS

## Service mapping
- **EventBridge Scheduler** â€” managed cron/at/rate triggers at scale; fires a
  target (Lambda, SQS, Step Functions). Maps the **distributed scheduler** option
  (HA, no leader to operate). Successor to CloudWatch Events scheduled rules.
- **SQS + Lambda (or ECS/EC2 workers)** â€” the queue holds ready/delayed jobs; the
  **visibility timeout** is the lease; Lambda/worker pool drains it. Maps **pull
  leasing**. SQS **redrive policy â†’ DLQ** after `maxReceiveCount`.
- **Step Functions** â€” managed workflow/DAG with retries, timers (`Wait`),
  and Map/parallel. Maps the **workflow DAG** option for orchestrated multi-step
  jobs (see also `temporal.md`).
- **SQS message timers / delay queues** â€” per-message or per-queue delivery delay.
  Maps the **delay queue** option.

## When to pick which
EventBridge Scheduler for cron/recurring triggers; SQS + Lambda for pull-based
worker draining with visibility-timeout leasing and a DLQ; Step Functions when
multi-step orchestration with retries/compensation is the hard part; FIFO SQS
when per-group ordering + content dedup is required.

## Limits / things that bite (verify against current docs)
- **SQS delivery delay caps at 15 min** â€” for longer delays, store the job and
  re-enqueue, or use EventBridge Scheduler with a one-time `at` schedule.
- **SQS visibility timeout max 12 h**; extend with `ChangeMessageVisibility`
  (the heartbeat equivalent). Default is 30 s â€” too short for most jobs.
- **Standard SQS is at-least-once + best-effort order** â†’ design idempotent
  consumers. **FIFO SQS** dedups within a 5-min window and is throughput-capped.
- **Lambda** has a max execution time (minutes, not hours) â€” long jobs need
  ECS/EC2 workers, not Lambda.
- EventBridge Scheduler / SQS have per-account throughput quotas â€” raise via
  Service Quotas before high-rate dispatch.

## Pitfalls
- Leaving the SQS visibility timeout at 30 s for a multi-minute job â†’ constant
  re-delivery and double-runs.
- Assuming FIFO SQS gives free exactly-once across systems â€” it dedups *delivery*
  in a window, not your side effects.
- Using Lambda for long-running jobs and hitting the timeout mid-task.
- Forgetting to set a redrive policy â†’ poison messages loop forever.
- Lock-in: EventBridge Scheduler / Step Functions definitions don't port to
  other clouds.


---


