# Latency Numbers & SLA Availability Guide

Crucial physical constants, order-of-magnitude latencies, and availability composition mathematics required for system design capacity planning.

---

## 1. Latency Numbers Every Programmer Should Know

Originally compiled by Jeff Dean, these physical latencies dictate architectural boundaries:

| Operation | Latency (ns / µs / ms) | Human Scale Equivalent (1 ns = 1 sec) | Architectural Implication |
|---|---|---|---|
| **L1 cache reference** | 0.5 ns | ~0.5 second | CPU execution / thread local |
| **Branch mispredict** | 5 ns | ~5 seconds | In-memory loop cost |
| **L2 cache reference** | 7 ns | ~7 seconds | Low-level caching |
| **Mutex lock / unlock** | 25 ns | ~25 seconds | Concurrency synchronization cost |
| **Main memory (RAM) reference** | 100 ns | ~1.7 minutes | In-memory data store (Redis, local cache) |
| **Compress 1 KB with Snappy** | 3 µs (3,000 ns) | ~50 minutes | Compression before network transfer is almost always worth it |
| **Send 1 KB over 1 Gbps network** | 10 µs | ~2.8 hours | Intra-rack network communication |
| **Read 4 KB randomly from SSD** | 150 µs | ~1.7 days | Fast random I/O (Database index lookup on NVMe SSD) |
| **Read 1 MB sequentially from RAM** | 250 µs | ~2.9 days | In-memory table scanning |
| **Round-trip within same datacenter** | 500 µs (0.5 ms) | ~5.8 days | Service-to-service microservice call / Redis network call |
| **Read 1 MB sequentially from SSD** | 1 ms | ~11.6 days | Sequential log appending (Kafka WAL, Postgres WAL) |
| **HDD disk seek** | 10 ms | ~3.8 months | Random I/O on rotating disk (Avoid in hot read/write path!) |
| **Read 1 MB sequentially from HDD** | 20 ms | ~7.6 months | Batch processing / bulk scans on cold storage |
| **Send packet CA $\rightarrow$ Europe $\rightarrow$ CA** | 150 ms | ~4.75 years | Cross-continental WAN (Origin fetch without CDN) |

### Performance Tiers by SLA Constraint
- **$< 1\text{ ms}$**: Must reside entirely in RAM (local memory, in-process cache, Redis cluster).
- **$< 10\text{ ms}$**: Can afford local SSD read or local key-value store query.
- **$< 100\text{ ms}$**: Can execute indexed relational database queries or remote cache calls within the same region.
- **$< 500\text{ ms}$**: Can make 2–3 sequential network calls within the same datacenter.
- **$> 1\text{ s}$**: Must be offloaded to asynchronous background processing (message queue), returning immediate accepted HTTP 202 status to the client.

---

## 2. Availability Nines & Downtime Table

Availability is measured in percentages, typically referred to as "nines":

| Availability | Downtime per Year | Downtime per Month | Downtime per Week | Downtime per Day |
|---|---|---|---|---|
| **99% (Two nines)** | 3.65 days | 7.31 hours | 1.68 hours | 14.4 minutes |
| **99.9% (Three nines)** | 8.77 hours | 43.83 minutes | 10.08 minutes | 1.44 minutes |
| **99.95% (Three and a half nines)**| 4.38 hours | 21.92 minutes | 5.04 minutes | 43.2 seconds |
| **99.99% (Four nines)** | 52.60 minutes | 4.38 minutes | 1.01 minutes | 8.64 seconds |
| **99.999% (Five nines)** | 5.26 minutes | 26.30 seconds | 6.05 seconds | 864 milliseconds |

---

## 3. SLA Composition Mathematics

### Sequential Dependency (Serial System)
When a request depends sequentially on $N$ services, overall availability is the **product** of individual availabilities:

$$\text{Availability}_{\text{total}} = A_1 \times A_2 \times \dots \times A_n$$

**Examples:**
- Service A (99.9%) calls Service B (99.9%):  
  $$99.9\% \times 99.9\% = 99.8001\% \quad (\approx 17.5\text{ hours downtime/year — degraded by a full nine!})$$
- Chain of 5 services each at 99.9%:  
  $$(0.999)^5 \approx 99.5\% \quad (\approx 43.8\text{ hours downtime/year})$$

> **Architectural Rule**: You cannot achieve four nines (99.99%) in an end-to-end user path if your architecture consists of a long chain of synchronous calls across three-nines services.

### Parallel Redundancy (Active / Standby)
When components operate in parallel redundancy where only one needs to succeed:

$$\text{Availability}_{\text{total}} = 1 - (1 - A_1) \times (1 - A_2) \times \dots \times (1 - A_n)$$

**Examples:**
- Two redundant API servers, each offering 99%:  
  $$1 - (0.01 \times 0.01) = 99.99\% \quad (\text{Boosts availability from two nines to four nines!})$$
- Multi-AZ database with automatic failover (Primary 99.9%, Standby 99.9%):  
  $$1 - (0.001 \times 0.001) = 99.9999\% \quad (\text{Six nines of infrastructure availability})$$
