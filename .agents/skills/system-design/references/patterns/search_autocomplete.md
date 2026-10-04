# Search Autocomplete Architecture Pattern

Search Autocomplete

### Requirements
- As user types, suggest top completions
- Latency under 100ms
- Suggestions ranked by frequency/relevance

### Key Components
- **Trie (prefix tree):** Data structure optimized for prefix matching
- **Aggregation service:** Collects search queries and computes frequencies
- **Cache layer:** Top-k results for popular prefixes (Redis)
- **Data collection service:** Logs queries for frequency analysis

### Design Decisions
- **Trie structure:** Each node stores a character; leaf or internal nodes store top-k completions
- **Pre-computation:** Compute top-k for each prefix offline (daily/hourly job), store in trie
- **Caching:** Cache results for popular prefixes (top 20% of prefixes serve 80% of queries)
- **Sharding:** Shard trie by first character or first two characters
- **Update frequency:** Rebuild trie hourly or daily from query logs (real-time updates are rarely needed)

---


