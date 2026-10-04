# Diagnostic Scoring & Quality Rubric

A quantitative scoring rubric to evaluate system design specifications, adapted from Alex Xu's methodology and the 8 Quick Diagnostic standards.

---

## 1. The 10/10 Scoring Formula

Every architecture should be scored before being declared complete:

$$\text{Score} = \text{round}\left(\frac{\text{Passed Rows}}{8} \times 10\right)$$

### Scoring Tiers:
- **9 – 10 / 10 (Production-Ready / Staff-Approved)**: All or nearly all diagnostic rows pass. Requirements are quantified, capacity is derived mathematically, every layer has redundancy, database scaling and caching are explicitly bounded, async processing isolates spikes, observability monitors the 4 golden signals, and zero-downtime deployment with rollbacks is defined.
- **5 – 6 / 10 (Functional but Fragile)**: The design functions logically on paper but skips capacity estimation, relies on unmitigated SPOFs, or lacks operational failure readiness.
- **$\le$ 3 / 10 (Unacceptable / Memorization Trap)**: Architecture proposed before requirements or scale numbers were established, or technology named without trade-offs.

---

## 2. The 8 Quick Diagnostic Criteria

| # | Diagnostic Question | If Answer is NO | Required Action |
|---|-------------------|-----------------|-----------------|
| **1** | **Are functional & non-functional requirements explicitly listed?** | Design rests on unstated assumptions. | Document 2-4 core features, DAU/MAU, read/write ratio, latency SLA (P50/P99), availability target, and explicit out-of-scope items. |
| **2** | **Is there a Back-of-the-Envelope QPS and storage estimate?** | Capacity is purely guesswork. | Calculate QPS (DAU × actions / 86,400), peak factor (2-5×), storage growth (daily & 1-5 year total), and bandwidth before choosing stores. |
| **3** | **Is every single component redundant?** | Single points of failure (SPOFs) will take down the system. | Introduce multi-server instances, multi-AZ deployment, health-check failover, or leader-follower replicas at every tier. |
| **4** | **Is the database scaling strategy explicitly defined?** | The system will hit a brick wall under load growth. | Define vertical scaling ceiling $\rightarrow$ read replicas $\rightarrow$ caching $\rightarrow$ sharding strategy (Hash/Range/Directory) with a high-cardinality shard key. |
| **5** | **Is there a caching strategy for read-heavy access paths?** | Database takes unnecessary read load and latency suffers. | Apply Cache-Aside / Read-Through using Redis or Memcached with explicit TTL, eviction policy (LRU), and mitigations for stampede and hot keys. |
| **6** | **Are asynchronous paths decoupled using queues/streams?** | Tight coupling causes cascading latency and failure amplification. | Buffer bursty writes and background tasks using Kafka, RabbitMQ, or SQS with dead-letter queues (DLQ) and exponential backoff. |
| **7** | **Is there an observability & alerting plan?** | Teams are blind to production incidents until users complain. | Instrument the Three Pillars: Metrics (Four Golden Signals / RED), Logging (correlation IDs), and Distributed Tracing with alert thresholds. |
| **8** | **Is the deployment & disaster recovery strategy defined?** | Releases carry high downtime risk; disaster recovery is undefined. | Specify rolling update, blue-green, or canary release with automated rollback criteria, plus RTO (Recovery Time) and RPO (Data Loss) targets. |

---

## 3. Four-Step Timeboxing Guide (45–60 min session)

When conducting or presenting a design session, manage time proportionally:

```
Step 1: Understand the Problem & Establish Design Scope  (~5–10 min)
Step 2: Propose High-Level Design & Get Buy-In           (~15–20 min)
Step 3: Design Deep Dive (2–3 Critical Components)       (~15–20 min)
Step 4: Wrap Up & Address Trade-offs / Bottlenecks       (~5 min)
```

### Step 1 Checklist
- [ ] Ask at least 5 clarifying questions.
- [ ] List 2–4 functional requirements.
- [ ] List non-functional constraints (DAU, latency, availability, consistency).
- [ ] List at least 1 explicit out-of-scope feature.
- [ ] Derive order-of-magnitude scale numbers.

### Step 2 Checklist
- [ ] High-level diagram showing Clients, Gateway/LB, Services, Stores, Caches, Queues.
- [ ] Concrete API contract for 2-3 core endpoints (Method, Path, Request, Response).
- [ ] Data model defining primary and partition keys.
- [ ] Ask for agreement on which 2 components to deep dive.

### Step 3 Checklist
- [ ] Dive into the hardest-to-scale component (e.g. database sharding or real-time delivery).
- [ ] Present at least 2 alternative approaches with trade-offs.
- [ ] Pick the approach and state the justification under current constraints.
- [ ] Address edge cases and stress scenarios (hotspots, partitions, stampedes).

### Step 4 Checklist
- [ ] Summarize the architecture in 1 paragraph.
- [ ] Explicitly state acknowledged trade-offs (what this design sacrifices).
- [ ] Identify the next bottleneck when load grows 10×.
- [ ] Review the 8 Quick Diagnostic rows to verify a 10/10 score.
