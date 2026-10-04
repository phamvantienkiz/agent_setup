# Rate Limiter Architecture Pattern

Rate Limiter

### Requirements
- Limit the number of requests a client can send in a time window
- Return 429 (Too Many Requests) when limit exceeded
- Must be low-latency (add minimal overhead to each request)

### Key Components
- **Rate limiter middleware:** Checks request against limits before routing to backend
- **Counter store:** Redis for atomic increment and TTL-based expiration
- **Configuration service:** Defines rules (100 requests/minute per API key)

### Algorithms

| Algorithm | How It Works | Pros | Cons |
|-----------|-------------|------|------|
| **Token bucket** | Bucket holds tokens; each request consumes one; bucket refills at fixed rate | Smooth, allows bursts up to bucket size | Requires per-client state |
| **Leaky bucket** | Requests enter a queue; processed at fixed rate | Very smooth output | Doesn't handle bursts well |
| **Fixed window** | Count requests in fixed time windows (e.g., each minute) | Simple | Spike at window boundary (2x burst) |
| **Sliding window log** | Store timestamp of each request; count within sliding window | Accurate | Memory-intensive (stores every timestamp) |
| **Sliding window counter** | Weighted combination of current and previous window | Good accuracy, low memory | Approximate (but close enough) |

### Design Decisions

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Where to rate-limit** | Client-side, API gateway, middleware, server-side | API gateway or middleware (centralized, before business logic) |
| **Counter storage** | Local memory, Redis, database | Redis (atomic operations, TTL, shared across servers) |
| **Distributed coordination** | Single Redis, Redis Cluster, local + sync | Redis Cluster for high availability |
| **Rate limit headers** | X-RateLimit-Remaining, X-RateLimit-Limit, Retry-After | Include all three; Retry-After is most important |

### Handling Exceeded Limits
- Return HTTP 429 with `Retry-After` header
- Optionally queue excess requests instead of rejecting
- Log rate-limited requests for monitoring (detect abuse patterns)

---


