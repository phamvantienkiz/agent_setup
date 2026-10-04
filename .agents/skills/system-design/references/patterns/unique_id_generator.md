# Distributed Unique ID Generator Architecture Pattern

Unique ID Generator

### Requirements
- Generate globally unique IDs at high throughput
- IDs should be roughly sortable by time
- 64-bit (fits in a long integer)

### Approaches

| Approach | Format | Pros | Cons |
|----------|--------|------|------|
| **UUID** | 128-bit random | Simple, no coordination | 128-bit (too large), not sortable |
| **Auto-increment (single DB)** | Sequential integer | Simple, sortable | Single point of failure, doesn't scale |
| **Auto-increment (multi DB)** | Even/odd or ranges per DB | Scales writes | Gaps in sequence, coordination for ranges |
| **Snowflake** | 64-bit: timestamp + datacenter + machine + sequence | Time-sortable, distributed, 64-bit | Clock sync dependency |
| **ULID** | 128-bit: timestamp + random | Sortable, simple | 128-bit |

### Snowflake ID Structure (Recommended for Most Systems)

```
| 1 bit unused | 41 bits timestamp | 5 bits datacenter | 5 bits machine | 12 bits sequence |
```

- **41-bit timestamp:** Milliseconds since custom epoch; ~69 years of IDs
- **5-bit datacenter ID:** Up to 32 datacenters
- **5-bit machine ID:** Up to 32 machines per datacenter
- **12-bit sequence:** Up to 4,096 IDs per millisecond per machine
- **Total capacity:** 4,096 x 32 x 32 = ~4 million IDs/second system-wide

### Design Decisions
- **Clock sync:** Use NTP; if clock goes backward, wait or reject (never generate duplicate)
- **Custom epoch:** Start from your launch date, not Unix epoch (maximizes timestamp range)
- **Machine ID assignment:** Use ZooKeeper, etcd, or config to assign unique machine IDs
- **Sequence overflow:** If 4,096 exhausted in one millisecond, wait for next millisecond

---


