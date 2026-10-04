# Notification System Architecture Pattern

Notification System

### Requirements
- Send push notifications, SMS, and email
- Support millions of users with different preferences
- Handle retry for failed deliveries

### Key Components
- **Notification service:** API to receive notification requests
- **User preference store:** Which channels each user has enabled
- **Template service:** Render notification content from templates
- **Delivery workers:** Per-channel workers (push, SMS, email)
- **Message queues:** One queue per channel for decoupling and retry
- **Delivery log:** Track sent, delivered, read status

### Design Decisions
- **Decouple with queues:** Separate queue per channel allows independent scaling and retry
- **Retry with exponential backoff:** Failed deliveries retry with increasing delay (1s, 2s, 4s, 8s...)
- **Rate limiting per user:** Prevent notification fatigue (max N notifications per hour)
- **Priority levels:** Urgent (password reset) vs normal (marketing) vs low (weekly digest)
- **Deduplication:** Idempotency key prevents sending the same notification twice

---


