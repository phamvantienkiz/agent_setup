# Real-Time Chat System Architecture Pattern

Chat System

### Requirements
- 1:1 and group messaging
- Real-time delivery (< 1 second latency)
- Message persistence and history
- Online/offline status (presence)

### Key Components
- **Connection service:** Manages WebSocket connections (stateful)
- **Message service:** Stores and retrieves messages
- **Presence service:** Tracks online/offline status
- **Notification service:** Push notifications for offline users
- **Group service:** Manages group membership and routing

### Design Decisions

| Decision | Options | Recommendation |
|----------|---------|----------------|
| **Protocol** | HTTP polling, long polling, WebSocket, SSE | WebSocket for bidirectional real-time |
| **Message storage** | SQL, NoSQL, wide-column | Wide-column (Cassandra/HBase) for write-heavy, time-series access |
| **Message ordering** | Timestamp, sequence number, hybrid | Monotonic ID per conversation (timestamp + sequence) |
| **Presence** | Heartbeat, connection-based | Heartbeat every 30s; mark offline after 3 missed beats |
| **Group message routing** | Fan-out to members, pull on read | Fan-out via message queue for groups up to ~500 members |

### Message Flow (1:1)
1. Sender sends message via WebSocket to connection service
2. Connection service publishes to message queue
3. Message service persists to database
4. If recipient is online: deliver via their WebSocket connection
5. If recipient is offline: send push notification, store for later delivery

---


