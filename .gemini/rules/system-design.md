# System Design Rules

> Principles from "System Design Interview" (Alex Xu), "Designing Data-Intensive Applications" (Martin Kleppmann), and industry best practices.

## 🏗️ Core Principles

### CAP Theorem
- A distributed system can only guarantee 2 of 3: **Consistency**, **Availability**, **Partition Tolerance**
- **CP systems** (sacrifice availability): MySQL, ZooKeeper, HBase → use when data correctness is critical
- **AP systems** (sacrifice consistency): Cassandra, DynamoDB, CouchDB → use for high availability

### Design for Failure
- Every external call CAN fail — design for it
- Use **circuit breakers** to prevent cascade failures
- Use **bulkhead pattern** to isolate failures
- Implement **graceful degradation** (serve cached/partial data when dependencies fail)

---

## 📐 Scalability Patterns

### Horizontal vs Vertical Scaling
```
Vertical  → More CPU/RAM on one machine (limited ceiling)
Horizontal → More machines (preferred for production)
```

### Load Balancing
- **Round Robin** — equal distribution
- **Least Connections** — route to least busy server
- **Consistent Hashing** — for cache/session affinity (minimize remapping on scale)

### Caching Strategies
| Strategy | Use Case |
|----------|----------|
| **Cache-Aside** (Lazy Loading) | Read-heavy, content changes frequently |
| **Write-Through** | Write-heavy, data must be consistent |
| **Write-Behind** (Write-Back) | High write throughput, some lag acceptable |
| **Read-Through** | Cache is always up to date |

### Database Scaling
- **Read Replicas** — scale read-heavy workloads
- **Sharding** — partition data horizontally by shard key
- **Vertical Partitioning** — split tables by column groups
- **CQRS** — separate read model and write model

---

## 🔄 Async Patterns

### Message Queues
Use queues (Redis, RabbitMQ, Kafka) when:
- Processing can be deferred
- Tasks are slow/expensive (email, PDF gen, notifications)
- You need to decouple producers from consumers

```
Producer → [Queue] → Consumer(s)
```

### Event-Driven Architecture
```js
// Publish domain events instead of direct service calls
eventBus.publish('order.created', { orderId, userId, total });
// Other services subscribe independently
```

### Saga Pattern (Distributed Transactions)
- **Choreography** — each service reacts to events (no central coordinator)
- **Orchestration** — a saga orchestrator tells each service what to do

---

## 🗄️ Database Design

### Normalization vs Denormalization
- **Normalize** (OLTP) — avoid data duplication, use JOINs
- **Denormalize** (OLAP/Read-heavy) — duplicate data to eliminate JOINs

### Indexing Rules
```sql
-- ✅ Index columns used in WHERE, JOIN, ORDER BY
CREATE INDEX idx_users_email ON users(email);

-- ❌ Don't index every column — indexes slow down writes
```

### N+1 Query Prevention
```js
// ❌ N+1: one query per user
const users = await db.users.findAll();
for (const user of users) {
  user.orders = await db.orders.findAll({ where: { userId: user.id } });
}

// ✅ Single query with JOIN or include
const users = await db.users.findAll({ include: [{ model: db.orders }] });
```

---

## 🌐 API Design Patterns

### Rate Limiting Algorithms
| Algorithm | Best For |
|-----------|----------|
| **Token Bucket** | Burst traffic allowed (API gateways) |
| **Leaky Bucket** | Smooth/constant output rate |
| **Fixed Window** | Simple, but spiky at window boundaries |
| **Sliding Window** | Most accurate, higher memory cost |

### Idempotency
- GET, PUT, DELETE must be idempotent
- POST operations: use **idempotency keys** for payment/critical actions
```
POST /api/payments
Idempotency-Key: <uuid>
```

### Pagination Patterns
```
Offset: ?page=2&limit=20          → Simple but slow on large offsets
Cursor: ?cursor=<encoded>&limit=20 → ✅ Preferred for large datasets
```

---

## 🔒 Reliability

### Circuit Breaker States
```
CLOSED → OPEN (after N failures) → HALF-OPEN (probe) → CLOSED
```

### Retry Strategy
```js
// ✅ Exponential backoff with jitter
const delay = Math.min(baseDelay * 2 ** attempt + Math.random() * 1000, maxDelay);
```

### Health Checks
```
GET /health        → Basic liveness (is the service running?)
GET /health/ready  → Readiness (is the service ready to serve traffic?)
GET /health/live   → Liveness (should Kubernetes restart this pod?)
```

---

## 📊 Back-of-Envelope Estimation

| Resource | Approximate Speed |
|----------|------------------|
| L1 cache reference | 0.5 ns |
| L2 cache reference | 7 ns |
| RAM access | 100 ns |
| SSD random read | 150 μs |
| Network round trip (same DC) | 0.5 ms |
| HDD seek | 10 ms |
| Network round trip (cross continent) | 150 ms |

> Rule of thumb: Prefer Redis (in-memory) over DB for anything needing < 1ms latency
