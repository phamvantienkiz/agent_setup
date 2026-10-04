---
name: system-design
description: Master skill for enterprise distributed system design and architecture. Use when designing system architecture, APIs, components, data models, or infrastructure scaling. Triggers on "system design", "scale this", "high availability", "design a URL shortener", "design Twitter", "design Uber", "design a news feed", "design a chat system", "rate limiter", "capacity planning", "distributed architecture", "sharding strategy", "caching strategy", "load balancing", "message queue", "consistency model", "CAP theorem", "SLA calculation", "latency numbers", "cloud architecture (AWS/GCP/Azure)", or any "how should I architect/design X" question.
license: MIT
metadata:
  version: "2.0.0"
  framework: "Hybrid Synthesis (proyecto26 22-block topology + wondelai/Alex Xu 8 case studies & 10/10 rubric)"
---

# System Design Framework (Enterprise Master Skill)

Drive any open-ended system design problem from a vague prompt to a production-ready, justified, and stress-tested architecture — **by active reasoning, not by recalling memorized diagrams.**

```
       [ 1. Clarify Requirements ]  ──►  [ 2. Estimate Scale (BOTEC) ]
                   │                                     │
                   ▼                                     ▼
       [ 3. High-Level Design ]     ◄──  (Numbers force component choices)
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
[ 4. Evaluate Trade-Offs ]  [ 5. Stress-Test Failure Modes ]
         │                   │
         └─────────┬─────────┘
                   ▼
       [ 6. Deep Dive & Scale Evolution (10x/100x) ]
```

---

## 1. Core Philosophy: Active Reasoning Over Static Diagrams

1. **Architecture is a Falsifiable Hypothesis**: Every architecture holds only under a stated set of constraints (QPS, read/write ratio, latency SLAs, data shape). If constraints change, the design must adapt calmly.
2. **Start with Requirements, Not Solutions**: Jumping to components (e.g. naming Kafka or Cassandra) before understanding scale produces brittle, over-engineered systems.
3. **Quantify Before Choosing**: Qualitative words like "high traffic" or "fast" are meaningless. Always convert scale into numbers (QPS, daily storage, peak bandwidth, server counts).
4. **Justify Every Choice**: For every technology introduced, answer three mandatory questions: **What does it solve? What does it worsen? What would make you change it?**

---

## 2. The 6-Step Reasoning Loop (45–60 min Timebox)

Follow this loop iteratively. Late steps routinely send you back to re-evaluate early assumptions:

### Step 1: Clarify Requirements & Scope (~5–10 min)
- **Functional Requirements**: Pick 2–4 core user flows; explicitly state what is **out of scope**.
- **Non-Functional Requirements**: DAU/MAU, read/write ratio, latency target (P50/P99), availability target, consistency model, durability (RPO/RTO).
- **Tooling & Guide**: See [references/framework/reasoning-loop.md](references/framework/reasoning-loop.md) and [references/building-blocks/L0_requirements_scoping.md](references/building-blocks/L0_requirements_scoping.md).
- **Template**: Capture scope in [assets/requirements-template.md](assets/requirements-template.md).

### Step 2: Estimate Scale (Back-of-the-Envelope) (~5 min)
- **Calculations**: Average QPS, Peak QPS (2–5×), Daily and yearly storage growth, Peak ingress/egress bandwidth, Approximate server count.
- **Numbers to Remember**: Memory (~100 ns) vs SSD (~150 µs) vs Intra-DC round-trip (~0.5 ms) vs Cross-continent (~150 ms).
- **Tooling & Guide**: See [references/estimation/latency-and-sla.md](references/estimation/latency-and-sla.md) and [references/estimation/numbers-to-remember.md](references/estimation/numbers-to-remember.md).
- **Automated Sizing Script**: Run [scripts/botec.py](scripts/botec.py) for deterministic sizing calculations.

### Step 3: Propose High-Level Design (~15 min)
- **Topology**: Clients $\rightarrow$ DNS $\rightarrow$ CDN/Edge $\rightarrow$ Load Balancers $\rightarrow$ API Gateway $\rightarrow$ Application Services $\rightarrow$ Data Stores & Caches $\rightarrow$ Message Queues & Workers.
- **API Contracts**: Define core endpoints with concrete HTTP methods, request/response JSON bodies, pagination cursors, and idempotency keys. See [references/building-blocks/L2_api_design.md](references/building-blocks/L2_api_design.md).
- **Data Model**: Storage technology choice (SQL vs NoSQL), primary keys, sort keys, and shard/partition keys. See [references/building-blocks/L3_data_storage.md](references/building-blocks/L3_data_storage.md).
- **System Diagram**: Represent system components and data flows using standard **Mermaid** blocks within the Markdown design document. For standalone interactive HTML visual views, delegate on-demand to dedicated visual skills (`diagram-design`, `html-diagram`) and save to `docs/views/{system}-view.html`.

### Step 4: Evaluate Trade-Offs (~10 min)
- Never name a tool without filling the mandatory 4-column rubric:
  ```markdown
  | Option | What it solves | What it worsens | Change it when |
  ```
- Balance: Latency $\leftrightarrow$ Throughput; Consistency $\leftrightarrow$ Availability (CAP/PACELC); Operational Simplicity $\leftrightarrow$ Theoretical Optimality.
- **Guide**: See [references/framework/tradeoff-framework.md](references/framework/tradeoff-framework.md).

### Step 5: Stress-Test Failure Modes (~10 min)
- Assume every single component will break:
  - **Single Points of Failure (SPOFs)**: What happens if this node/database fails?
  - **Degradation Path**: Fall back to stale cache, serve partial data, or disable non-critical features. Never rely purely on aggressive retries (prevents retry storms / thundering herd).
  - **Resilience Patterns**: Circuit Breakers, Bulkheads, Rate Limiting, Backpressure, Dead-Letter Queues.
- **Guide**: See [references/framework/failure-modes.md](references/framework/failure-modes.md) and [references/building-blocks/L6_resilience_failure.md](references/building-blocks/L6_resilience_failure.md).

### Step 6: Deep Dive & Scale Evolution (~5–10 min)
- Pick the 1–2 most complex subsystems (e.g. distributed sharding, real-time message fanout, or sharded counters).
- Walk the **Scaling Ladder**: Explain what architectural changes become necessary when the system grows 10× or 100×.
- **Guide**: See [references/building-blocks/L7_scaling_evolution.md](references/building-blocks/L7_scaling_evolution.md).

---

## 3. The 10 Failure Modes & Guardrails

Avoid the classic traps that cause architectures to fail in production:

| # | Failure Mode | Danger Signal | Required Reflex |
|---|---|---|---|
| **#1** | **Opaque Primitives** | Treating DB/Cache/Queue as black boxes. | Know their internal stress behavior (eviction storms, WAL contention, partition lag). |
| **#2** | **Fundamentals Gap** | Confusing CAP, PACELC, or Quorum consistency. | State explicitly: when network partitions, do you reject writes or diverge? |
| **#3** | **Rushing Without Clarifying** | Drawing boxes before defining scope. | Clarify: 2–4 features, explicit out-of-scope, and numeric SLAs first. |
| **#4** | **Weak Trade-Off Articulation** | Name-dropping tools as "industry standard". | Fill the 3 questions: Solves / Worsens / When to change. |
| **#5** | **No Sense of Scale** | Calling traffic "high" or "heavy". | Convert to numbers (QPS, daily bytes, peak bandwidth). |
| **#6** | **Ignoring Failure Modes** | Assuming 100% uptime; adding more retries. | Implement Circuit Breakers, Fallback caches, and Rate Limiting. |
| **#7** | **Over-Indexing on Sunk Design** | Clinging to a diagram when constraints change. | Treat design as a hypothesis; pivot gracefully when assumptions break. |
| **#8** | **Weak API / Data Models** | Vague "fetch feed" descriptions. | Write concrete JSON request/response shapes, primary keys, and partition keys. |
| **#9** | **Presentation Over Collaboration** | Defending slides defensively. | Invite feedback, think out loud, and collaborate like a team design review. |
| **#10**| **Inability to Course-Correct** | Patching broken assumptions. | Audit the broken assumption and redesign affected subsystems directly. |

*Detailed breakdowns and antidotes*: See [references/framework/failure-modes.md](references/framework/failure-modes.md).

---

## 4. Master Building-Blocks Routing Table

When a design question focuses on a specific tier, consult the owning building block:

| Layer | Concern / Problem Statement | Owning Reference File |
|:---|:---|:---|
| **L0 Frame** | Clarifying questions, scope boundary, out-of-scope | [references/building-blocks/L0_requirements_scoping.md](references/building-blocks/L0_requirements_scoping.md) |
| **L0 Frame** | QPS, storage, bandwidth, server sizing calculations | [references/estimation/numbers-to-remember.md](references/estimation/numbers-to-remember.md) & [scripts/botec.py](scripts/botec.py) |
| **L1 Edge** | Domain resolution, GeoDNS, latency routing, failover | [references/building-blocks/L1_dns.md](references/building-blocks/L1_dns.md) |
| **L1 Edge** | Traffic distribution, L4 vs L7, health checks, sticky sessions | [references/building-blocks/L1_load_balancing.md](references/building-blocks/L1_load_balancing.md) |
| **L1 Edge** | Static asset & media delivery, edge caching, CDN push/pull | [references/building-blocks/L1_content_delivery.md](references/building-blocks/L1_content_delivery.md) |
| **L2 Services** | REST/gRPC/GraphQL, pagination, idempotency keys, versioning | [references/building-blocks/L2_api_design.md](references/building-blocks/L2_api_design.md) |
| **L2 Services** | Monolith vs microservices, domain boundaries, API Gateway | [references/building-blocks/L2_service_decomposition.md](references/building-blocks/L2_service_decomposition.md) |
| **L3 State** | SQL vs NoSQL, sharding strategies, shard key selection, replication | [references/building-blocks/L3_data_storage.md](references/building-blocks/L3_data_storage.md) |
| **L3 State** | Cache-aside, write-through, LRU, stampede, hot key mitigation | [references/building-blocks/L3_caching.md](references/building-blocks/L3_caching.md) |
| **L3 State** | Unstructured large files (images, video), chunking, presigned URLs | [references/building-blocks/L3_blob_store.md](references/building-blocks/L3_blob_store.md) |
| **L3 State** | Unique ID generation at scale, Snowflake 64-bit, UUIDv7 | [references/building-blocks/L3_sequencer.md](references/building-blocks/L3_sequencer.md) |
| **L3 State** | High-write counters (likes, views), HyperLogLog, time buckets | [references/building-blocks/L3_sharded_counters.md](references/building-blocks/L3_sharded_counters.md) |
| **L3 State** | Full-text search, inverted index, prefix Trie autocomplete | [references/building-blocks/L3_distributed_search.md](references/building-blocks/L3_distributed_search.md) |
| **L4 Async** | Event queues vs streaming logs, Kafka/RabbitMQ/SQS, ordering | [references/building-blocks/L4_messaging_streaming.md](references/building-blocks/L4_messaging_streaming.md) |
| **L4 Async** | Scheduled jobs, worker leasing, distributed cron, retry dedup | [references/building-blocks/L4_task_scheduling.md](references/building-blocks/L4_task_scheduling.md) |
| **L5 Correct**| Strong vs Eventual consistency, Quorum W+R>N, Raft/Paxos consensus | [references/building-blocks/L5_consistency_coordination.md](references/building-blocks/L5_consistency_coordination.md) |
| **L6 Ops** | Circuit breakers, retries with backoff, bulkheads, rate limiters | [references/building-blocks/L6_resilience_failure.md](references/building-blocks/L6_resilience_failure.md) |
| **L6 Ops** | Four Golden Signals, RED/USE metrics, distributed tracing | [references/building-blocks/L6_observability.md](references/building-blocks/L6_observability.md) |
| **L6 Ops** | High-volume log collection, shipping, buffering, trace correlation | [references/building-blocks/L6_distributed_logging.md](references/building-blocks/L6_distributed_logging.md) |
| **L7 Growth** | Scaling ladder: what breaks at 10k, 100k, 1M, 10M DAU | [references/building-blocks/L7_scaling_evolution.md](references/building-blocks/L7_scaling_evolution.md) |

---

## 5. Cloud Provider Modularity

Default to **Vendor-Neutral Generic** components. When a target cloud is specified, reference the corresponding provider mapping:

- **AWS Ecosystem**: [references/providers/aws.md](references/providers/aws.md) (ALB, DynamoDB, S3, ElastiCache, SQS, Kinesis, CloudWatch, X-Ray)
- **GCP Ecosystem**: [references/providers/gcp.md](references/providers/gcp.md) (Cloud Load Balancing, Spanner, Firestore, Cloud Storage, Memorystore, Pub/Sub, Cloud Tasks)
- **Azure Ecosystem**: [references/providers/azure.md](references/providers/azure.md) (Front Door, Cosmos DB, Blob Storage, Azure Cache for Redis, Service Bus, Event Hubs)
- **Temporal (Durable Workflows)**: [references/providers/temporal.md](references/providers/temporal.md) (Long-running orchestrations, Distributed Sagas)
- **Generic / Open Source**: [references/providers/generic.md](references/providers/generic.md) (Nginx, HAProxy, PostgreSQL, Redis, Kafka, MinIO, RabbitMQ)

---

## 6. Reference Patterns Bank (8 Case Studies)

For end-to-end walkthroughs, review the dedicated pattern guides:

1. [URL Shortener (TinyURL)](references/patterns/url_shortener.md): Base62 encoding, 301 vs 302 redirect analytics, Key-Value cache.
2. [API Rate Limiter](references/patterns/rate_limiter.md): Token bucket, sliding window counter, Redis cluster atomic operations, HTTP 429 Retry-After.
3. [Notification System](references/patterns/notification_system.md): Per-channel worker queues (Push, SMS, Email), exponential backoff, idempotency deduplication.
4. [News Feed (Social Network)](references/patterns/news_feed.md): Fanout-on-write vs fanout-on-read, Redis sorted sets, Hybrid model for celebrity accounts.
5. [Real-Time Chat System](references/patterns/chat_system.md): WebSocket connection management, monotonic sequence IDs per conversation, heartbeat presence tracking.
6. [Search Autocomplete](references/patterns/search_autocomplete.md): Prefix Tree (Trie), offline batch precomputation, prefix cache sharding.
7. [Distributed Web Crawler](references/patterns/web_crawler.md): Priority URL Frontier (BFS), politeness (robots.txt delay), HTML content hashing dedup.
8. [Distributed Unique ID Generator](references/patterns/unique_id_generator.md): Twitter Snowflake 64-bit structure, NTP clock drift mitigation, 4M IDs/sec.
- **Pattern Overview**: [references/patterns/overview.md](references/patterns/overview.md).

---

## 7. Diagramming & Pure Markdown Standard

To maintain repository cleanliness, git diff reviewability, and alignment with the project's documentation architecture:

1. **Pure Markdown Invariant in Design Docs**:
   - All system design documentation (`docs/architecture/` and `docs/implementation/{release}/technical-design.md`) **MUST be written in pure Markdown (`.md`)**.
   - Internal diagrams, component layouts, sequences, data flows, and state machines MUST be expressed using standard **Mermaid syntax** (`flowchart TD`, `flowchart LR`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`).
   - **Prohibited**: Do NOT embed inline HTML (`<canvas>`, `<svg>`, `<script>`, style tags) or commit binary image dumps into core doc trees.

2. **Centralized Visual Views (`docs/views/`)**:
   - Standalone visual, styled, or interactive views (e.g. interactive system topologies, cloud infrastructure maps) are **never embedded directly into core documentation**.
   - Instead, they are saved exclusively into `docs/views/{system}-view.html`.
   - Core design documents can link to these views using clean markdown links: `[Interactive Topology View](../../views/{system}-view.html)`.

3. **On-Demand Generation & Specialist Visual Skills Delegation**:
   - `system-design` focuses strictly on engineering trade-offs, capacity calculations, failure mode resilience, and pure Markdown documentation. It does **NOT** maintain an internal HTML/SVG rendering engine.
   - Standalone HTML views are generated **ONLY upon explicit user request** (e.g. "vẽ HTML view", "tạo bản đồ tương tác").
   - When requested, the Agent reads the Markdown source and invokes dedicated visual specialist skills:
     - **`diagram-design`**: Branded architecture diagrams, cloud topology, sequence, and component diagrams.
     - **`html-diagram`**: Standalone interactive HTML diagrams with zoom, pan, and collapsible subsystem layers.
     - **`design-artifact` / `html`**: Interactive executive dashboards and high-level tech summaries.

---

## 8. Integration with Documentation & Downstream Skills

### 3-Layer Documentation Architecture Alignment
All artifacts produced by `system-design` MUST be placed in accordance with the project's documentation standard (see `documentation` skill at [.agents/skills/documentation/SKILL.md](../documentation/SKILL.md)):

1. **Global System Architecture (Single Source of Truth & Living Invariants)**:
   - When designing a new system or evolving global technical invariants, update the authoritative files in `docs/architecture/`:
     - **System Topology & Components** $\rightarrow$ `docs/architecture/02-high-level-architecture.md`
     - **Service Boundaries & Decomposition** $\rightarrow$ `docs/architecture/03-service-architecture.md`
     - **Cloud Infrastructure & Deployment** $\rightarrow$ `docs/architecture/04-deployment-architecture.md`
     - **Database Models, Sharding & Caching** $\rightarrow$ `docs/architecture/05-data-architecture.md`
     - **Global API Invariants & Integration** $\rightarrow$ `docs/architecture/08-integration-architecture.md`
     - **Key Architectural Decisions** $\rightarrow$ File an ADR at `docs/architecture/adr/ADR-XXX-{title}.md` (capturing the *Solves / Worsens / Change it when* analysis).
2. **Release-Scoped Feature Design (Delivery Layer)**:
   - When designing a specific subsystem or feature within a delivery sprint/milestone:
     - **Subsystem Technical Architecture** $\rightarrow$ `docs/implementation/{release}/technical-design.md`
     - **Feature Non-Functional Constraints & Scale** $\rightarrow$ `docs/implementation/{release}/srs.md`
3. **Visual Architecture Diagrams (On-Demand Only)**:
   - When requested by the user, invoke dedicated visual skills (`diagram-design`, `html-diagram`) to produce standalone HTML diagrams and save them exclusively to `docs/views/{system}-view.html`. Core documentation links to this view without storing raw HTML in `docs/architecture/`.

### API Handoff Contract (Integration with `api-design-patterns`)
`system-design` defines the high-level system interface (endpoints, methods, SLAs, caching, and auth). It does **NOT** detail REST envelope schemas or parameter conventions in isolation.

**The Handoff Procedure:**
1. At Step 3 (High-Level Design), produce an **API Surface Summary**:
   ```markdown
   ## API Surface Summary — {system-name}
   - Context & Consumers: {mobile app, web client, 3rd-party integration}
   - Protocols & Auth: {REST / gRPC / WebSocket | JWT Bearer / OAuth2 / API Key}
   - Endpoints Matrix: Method, Path, Latency Target, Caching Strategy
   - Constraints: {e.g. Async 202 needed for heavy jobs, cursor pagination for feeds}
   ```
2. Pass this summary to `api-design-patterns` (see [.agents/skills/api-design-patterns/SKILL.md](../api-design-patterns/SKILL.md)).
3. `api-design-patterns` applies the 7 essential patterns (Versioning, Pagination, Filtering, Field Selection, Expansion, Async 202, Consistent Response) and writes:
   - System-wide API standards $\rightarrow$ `docs/architecture/08-integration-architecture.md`
   - Release endpoint specifications $\rightarrow$ `docs/implementation/{release}/api/vX.md`

---

## 9. Quality Scoring Gate (10/10 Quick Diagnostic)

Before declaring any system design task complete, verify all 8 diagnostic rows:

- [ ] **1. Requirements**: Are 2–4 functional features, numeric non-functional SLAs, and explicit out-of-scope documented?
- [ ] **2. Estimates**: Are QPS, storage growth, and bandwidth computed with units and assumptions?
- [ ] **3. Redundancy**: Is every component free from single points of failure (multi-AZ, replicas)?
- [ ] **4. Database Scaling**: Is the database growth path (read replicas $\rightarrow$ caching $\rightarrow$ sharding key) explicit?
- [ ] **5. Caching**: Is there an explicit caching strategy with TTL, LRU eviction, and stampede mitigation?
- [ ] **6. Async Decoupling**: Are non-critical writes and background jobs isolated behind queues?
- [ ] **7. Observability**: Are the Four Golden Signals, distributed tracing, and alert thresholds defined?
- [ ] **8. Operations**: Are zero-downtime deployment, rollback gates, and RTO/RPO disaster recovery plans stated?

*Detailed Scoring Rubric*: See [references/framework/diagnostic-scoring.md](references/framework/diagnostic-scoring.md).
