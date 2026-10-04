# News Feed (Social Feed) Architecture Pattern

News Feed (Social Feed)

### Requirements
- Users follow other users
- When a user posts, followers see the post in their feed
- Feed is ordered by recency (or ranked by algorithm)

### Key Components
- **Post service:** Stores posts
- **Follow graph:** Stores who follows whom
- **Feed generation service:** Assembles personalized feeds
- **Feed cache:** Pre-computed feeds per user (Redis sorted sets)
- **Notification service:** Alerts followers of new posts

### The Core Tradeoff: Fanout Strategy

| Strategy | How It Works | Pros | Cons |
|----------|-------------|------|------|
| **Fanout-on-write (push)** | When user posts, write to every follower's feed cache | Fast reads (feed is pre-built) | Slow writes for celebrities, wastes storage for inactive users |
| **Fanout-on-read (pull)** | When user reads feed, fetch posts from all followed accounts | Fast writes, no wasted storage | Slow reads (must merge N sources), high read-time computation |
| **Hybrid** | Push for normal users, pull for celebrities | Balanced | More complex code |

### Hybrid Design (Recommended)
- Users with < 10K followers: fanout-on-write (pre-push to follower feeds)
- Users with > 10K followers: fanout-on-read (merge at read time)
- Feed cache: Redis sorted set per user, scored by timestamp, capped at ~1,000 entries
- Celebrity posts: fetch at read time and merge into the cached feed

---


