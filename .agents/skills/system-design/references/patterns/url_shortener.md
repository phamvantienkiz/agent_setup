# URL Shortener Architecture Pattern

URL Shortener

### Requirements
- Given a long URL, generate a short unique URL
- Given a short URL, redirect to the original URL
- Optional: custom short URLs, expiration, analytics

### Key Components
- **API service:** Accepts long URL, returns short URL; accepts short URL, returns redirect
- **ID generator:** Creates unique short codes (base62-encoded auto-increment or hash)
- **Key-value store:** Maps short code to long URL (Redis, DynamoDB, or Cassandra)
- **Analytics service:** Logs redirects for click tracking (async via message queue)

### Design Decisions

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **ID generation** | Auto-increment + base62, hash (MD5/SHA), pre-generated IDs | Auto-increment + base62 for simplicity; pre-generated ranges for distributed |
| **Redirect type** | 301 (permanent) vs 302 (temporary) | 302 if you need analytics (browser doesn't cache); 301 for maximum performance |
| **Storage** | SQL vs NoSQL | NoSQL key-value (simple lookup, massive scale) |
| **Read optimization** | Cache layer | Cache-aside with Redis; short URLs follow power-law (few URLs get most traffic) |

### Scale Calculations (100M DAU)
- Write QPS: ~116 (10M new URLs/day)
- Read QPS: ~5,800 (500M redirects/day), peak ~29K
- Storage: ~1.1 TB/year (300 bytes per record, 10M/day, 10-year retention)

---


