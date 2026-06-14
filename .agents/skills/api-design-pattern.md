---
name: api-design-patterns
description: Comprehensive guide to 7 essential REST API design patterns: Versioning, Pagination, Filtering, Field Selection, Expansion, Async Request-Response, and Consistent Response. Use this skill whenever the user asks about API design, how to structure REST endpoints, how to handle large datasets in APIs, how to version APIs without breaking clients, how to return consistent responses, or how to design scalable and maintainable APIs. Also trigger when the user asks to review, critique, or improve existing API designs
---

# API Design Patterns — Reference Skill

A structured reference for 7 battle-tested REST API design patterns.
Apply these when designing new APIs or reviewing existing ones.

---

## Quick Pattern Index

| #   | Pattern                | Problem Solved                      | Key Mechanic               |
| --- | ---------------------- | ----------------------------------- | -------------------------- |
| 1   | Versioning             | Breaking changes when evolving APIs | URL prefix `/v1/`, `/v2/`  |
| 2   | Pagination             | Returning too much data at once     | `?page=&limit=` + meta     |
| 3   | Filtering              | Over-fetching irrelevant records    | Query params as predicates |
| 4   | Field Selection        | Over-fetching unused fields         | `?fields=id,name,avatar`   |
| 5   | Expansion              | Under-fetching related resources    | `?expand=profile,orders`   |
| 6   | Async Request-Response | Long-running tasks timing out       | `jobId` + polling endpoint |
| 7   | Consistent Response    | Inconsistent success/error shapes   | Unified envelope structure |

---

## Pattern 1 — Versioning Pattern

**Philosophy:** _Change without breaking the past._

Every long-lived API must evolve. Versioning lets you introduce breaking changes
while old clients continue working undisturbed.

### When to use

- Changing field names or data structures
- Adding/removing fields in a breaking way
- Changing business logic that affects response shape

### Implementation

```
GET /v1/users/123    →  Users Service Version 1  (legacy clients)
GET /v2/users/123    →  Users Service Version 2  (new clients)
```

**v1 response (old):**

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```

**v2 response (evolved safely):**

```json
{
  "id": 123,
  "fullName": "John Doe",
  "email": "john@example.com",
  "phone": "0912345678",
  "status": "active",
  "createdAt": "2024-05-18T10:00:00Z"
}
```

### Rules

- **Never** mutate an existing version in a breaking way — add a new version instead.
- Deprecate old versions gracefully with sunset headers: `Sunset: Sat, 01 Jan 2026 00:00:00 GMT`
- Common strategies: URL path (`/v2/`), header (`API-Version: 2`), query param (`?version=2`).
  URL path is the most visible and widely adopted.

### Golden Rule

> Any API that lives long enough **must** have a version strategy. Don't "fix in place" — add a new version. That's how APIs survive long-term.

---

## Pattern 2 — Pagination Pattern

**Philosophy:** _Don't return 100,000 records just because you can._

When data is large, split results into pages. Good for the server, good for the client.

### Request structure

```
GET /users?page=2&limit=10&sort=createdAt&search=john
```

| Parameter | Description                       |
| --------- | --------------------------------- |
| `page`    | Current page number (starts at 1) |
| `limit`   | Number of items per page          |
| `sort`    | Sort field (optional)             |
| `search`  | Search term (optional)            |

### Response structure

```json
{
  "data": [
    { "id": 11, "name": "Alice" },
    { "id": 12, "name": "Bob" }
  ],
  "meta": {
    "page": 2,
    "limit": 10,
    "total": 1000,
    "totalPages": 100,
    "hasNext": true,
    "hasPrevious": true
  }
}
```

### Don't vs Do

| ❌ Don't                      | ✅ Do                                      |
| ----------------------------- | ------------------------------------------ |
| Return all records at once    | Return small pages, just enough            |
| No metadata about total count | Always include `meta` with pagination info |
| Ignore `limit` parameter      | Enforce a maximum limit (e.g. 100)         |

### Benefits

- **Faster** responses
- **Reduces** server and database load
- **Better** user experience
- **Easier** to scale

### Alternative: Cursor-based pagination

For large, real-time datasets use cursors instead of page numbers:

```
GET /users?cursor=eyJpZCI6MTJ9&limit=10
```

Response includes `nextCursor` instead of `page`. More efficient for
deep pagination and live data.

> **Golden Rule:** Pagination saves both the database and the user experience. Don't let a good API become a system bottleneck.

---

## Pattern 3 — Filtering Pattern

**Philosophy:** _Let the client decide what data to fetch._

Allow clients to filter data by multiple criteria so they get exactly what they need — no more, no less.

### Request example

```
GET /users?active=true&role=admin&createdAt>=2024-01-01
```

### Common filter parameters

| Parameter               | Meaning                         |
| ----------------------- | ------------------------------- |
| `active=true`           | Filter active users only        |
| `role=admin`            | Filter by role                  |
| `createdAt>=2024-01-01` | Filter by creation date         |
| `email~=@gmail.com`     | Partial match / search by email |
| `sort=-createdAt`       | Sort descending by field        |
| `limit=20&page=1`       | Combine with pagination         |

### Response example

```json
{
  "data": [
    { "id": 15, "name": "John Doe", "role": "admin", "active": true },
    { "id": 28, "name": "Jane Smith", "role": "admin", "active": true }
  ],
  "meta": {
    "total": 42,
    "page": 1,
    "limit": 20,
    "totalPages": 3
  }
}
```

### Real-world use cases

- **User management:** filter by role, status, creation date
- **Order management:** filter by status, customer, time range
- **Reports/analytics:** multi-criteria data filtering

### Benefits

- Client is flexible and self-sufficient
- Reduces server and database load
- Saves bandwidth and improves performance
- API is flexible and extensible
- Better user experience

> **Golden Rule:** A flexible API lives longer than a rigid one. Give filtering power to the client.

---

## Pattern 4 — Field Selection Pattern

**Philosophy:** _Send only what the client needs._

Clients don't always need all fields. If a screen only shows name and avatar,
don't send 20+ other fields. Bandwidth costs money.

### Request

```
GET /users/123?fields=id,name,avatar
```

The `fields` parameter specifies a comma-separated list of fields to return.

### Without vs With Field Selection

**Without (returns all fields):**

```json
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "0912345678",
  "address": "123 Street, Hanoi",
  "role": "admin",
  "avatar": "https://.../avatar.jpg",
  "createdAt": "2024-05-01T10:00:00Z",
  "updatedAt": "2024-05-10T09:20:00Z",
  "lastLogin": "2024-05-15T08:00:00Z",
  "orders": [...],
  "transactions": [...],
  "preferences": {...}
}
```

**With `?fields=id,name,avatar` (lean response):**

```json
{
  "id": 123,
  "name": "John Doe",
  "avatar": "https://.../avatar.jpg"
}
```

### Implementation notes

- Always have a **default field list** for when client sends no `fields` param
- **Validate** requested fields (avoid leaking sensitive data)
- Can be combined with pagination and filtering
- Support **aliases/presets** for common field groups:

```
?fields=basic    → id, name, avatar
?fields=detail   → id, name, email, phone, address
?fields=profile  → id, name, avatar, bio, website
```

### Benefits

- Smaller response size
- Saves bandwidth
- Faster data transfer
- Mobile apps and web clients load faster
- Reduces server and database load

> **Golden Rule:** Send exactly what the client needs — not more, not less. Bandwidth is money.

---

## Pattern 5 — Expansion Pattern

**Philosophy:** _Fetch related data in a single call._

Instead of making multiple API calls for related resources, the client can
"expand" the resources it needs. Fewer requests, better performance, cleaner API.

### Request

```
GET /users/123?expand=profile,orders
```

| Part             | Meaning                                     |
| ---------------- | ------------------------------------------- |
| `expand`         | The query parameter                         |
| `profile,orders` | Comma-separated related resources to expand |

### Response

```json
{
  "data": {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "profile": {
      "bio": "Full-stack developer",
      "avatar": "https://.../avatar.jpg",
      "phone": "0912345678"
    },
    "orders": [
      { "id": 1, "total": 120000, "status": "paid" },
      { "id": 2, "total": 250000, "status": "pending" }
    ]
  }
}
```

### How it works

1. Client requests the main resource and specifies related resources via `expand`
2. Server returns the main resource **plus** the related resources inline

### Without vs With Expansion

```
❌ Without Expansion (3 requests):
GET /users/123        →  user data
GET /users/123/profile →  profile data
GET /users/123/orders  →  orders data

✅ With Expansion (1 request):
GET /users/123?expand=profile,orders  →  everything at once
```

### Benefits

- Fewer requests (3 → 1)
- Better performance, lower latency
- Keeps API clean — no need to create many sub-endpoints
- Client controls what data it needs

### Pro tip

Combine expansion with field selection for maximum optimization:

```
GET /users/123?expand=profile,orders&fields=id,name,profile.bio,orders.id,orders.total
```

> **Golden Rule:** Get all related data in one call. Your client (and your network) will thank you.

---

## Pattern 6 — Async Request-Response Pattern

**Philosophy:** _Not everything finishes in 3 seconds._

For long-running tasks (seconds, minutes, or more), don't force the client to
wait until timeout. Process asynchronously and return a `jobId`.

### Process flow

```
1. POST /reports          →  202 Accepted  (server creates job, returns jobId)
2. GET /jobs/{jobId}      →  200 OK        (client polls for status)
3. GET /reports/{id}.csv  →  200 OK        (client downloads result when done)
```

### Step 1 — Create task (Request)

```
POST /reports
{
  "type": "sales-report",
  "params": {
    "from": "2024-05-01",
    "to": "2024-05-31"
  }
}
```

**Response: `202 Accepted`**

```json
{
  "jobId": "a1b2c3d4",
  "status": "pending",
  "statusUrl": "/jobs/a1b2c3d4"
}
```

### Step 2 — Poll for status

```
GET /jobs/a1b2c3d4
```

**While processing:**

```json
{
  "jobId": "a1b2c3d4",
  "status": "processing",
  "progress": 45
}
```

**When complete:**

```json
{
  "jobId": "a1b2c3d4",
  "status": "completed",
  "resultUrl": "/reports/a1b2c3d4.csv"
}
```

### Step 3 — Download result

```
GET /reports/a1b2c3d4.csv
```

### When to use

- Generating large reports or statistics
- Sending bulk emails/SMS
- Processing video, images, large files
- AI/ML training or inference
- Any task that takes significant time

### Benefits

| Benefit                 | Description                                        |
| ----------------------- | -------------------------------------------------- |
| Better UX               | Client doesn't wait for timeout                    |
| Reduces server load     | Processing in background, no long-held connections |
| Stability & reliability | Easy to retry, easy to scale, low risk             |
| Monitoring & control    | Know progress and status of every task             |

### Pro tip

Combine with **Webhook / SSE / WebSocket** to push notifications when the job
completes — instead of having the client poll continuously.

> **Golden Rule:** Don't force clients to wait. Return a `jobId`, process in the background, let them check back.

---

## Pattern 7 — Consistent Response Pattern

**Philosophy:** _Consistent responses — easy to use, easy to extend, easy to maintain._

A great API isn't just about good requests. It's about responding consistently
in every situation — success, client error, server error.

### Recommended response envelope

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Successfully retrieved user list",
  "data": [{ "id": 1, "name": "John Doe", "email": "john@example.com" }],
  "meta": {
    "timestamp": "2024-05-20T10:30:00Z",
    "path": "/users",
    "requestId": "c0a801f2-8b7e-4d3f-a1c2-4b9b0d9e7b1a"
  }
}
```

| Field        | Purpose                                         |
| ------------ | ----------------------------------------------- |
| `success`    | Overall boolean status                          |
| `statusCode` | HTTP status code (mirrored in body)             |
| `message`    | Human-readable description                      |
| `data`       | Returned payload (if any)                       |
| `meta`       | Supplementary info (timestamp, path, requestId) |

### 1. Success Response — `200 OK`

```json
{
  "success": true,
  "statusCode": 200,
  "message": "Success",
  "data": {
    "id": 123,
    "name": "Alice"
  },
  "meta": {
    "timestamp": "2024-05-20T10:30:00Z"
  }
}
```

### 2. Client Error Response — `400 Bad Request`

```json
{
  "success": false,
  "statusCode": 400,
  "message": "Invalid data",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": [{ "field": "email", "message": "Invalid email format" }]
  },
  "meta": {
    "timestamp": "2024-05-20T10:31:00Z"
  }
}
```

### 3. Server Error Response — `500 Internal Server Error`

```json
{
  "success": false,
  "statusCode": 500,
  "message": "System error, please try again later",
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "details": "Cannot connect to database"
  },
  "meta": {
    "timestamp": "2024-05-20T10:32:00Z",
    "requestId": "c0a801f2-8b7e-4d3f-a1c2-4b9b0d9e7b1a"
  }
}
```

### Best Practices

| Practice                                       | Why                             |
| ---------------------------------------------- | ------------------------------- |
| Always keep response structure consistent      | Client can parse reliably       |
| Use clear, readable `message` text             | Reduces debugging time          |
| Never leak sensitive system info               | Security                        |
| Use `code` in errors for programmatic handling | Client can branch on error type |
| Log with `requestId` for easy tracing          | Operations and debugging        |

### Benefits

- Client can parse and handle responses easily
- Fewer bugs from inconsistent formats
- Extend API without impacting clients
- Clearer, more professional API documentation

> **Golden Rule:** Document your response structure clearly in API docs so every client handles responses the same way.

---

## Combining Patterns

These patterns compose well together. Real-world API calls often use several at once:

```
GET /v2/users?
  active=true&role=admin        ← Filtering
  &page=1&limit=20              ← Pagination
  &fields=id,name,avatar        ← Field Selection
  &expand=profile               ← Expansion
  &sort=-createdAt              ← Sorting (part of Filtering)
```

**Layered optimization:**

```
/v2/users/123
  ?expand=profile,orders
  &fields=id,name,profile.bio,orders.id,orders.total
  &orders.status=paid
```

---

## Design Checklist

Before shipping any API endpoint, verify:

- [ ] Does it have a version? (`/v1/`, `/v2/`)
- [ ] Does it paginate large collections?
- [ ] Does it support filtering by relevant fields?
- [ ] Does it support `?fields=` for field selection?
- [ ] Does it support `?expand=` for related resources?
- [ ] Are long tasks handled asynchronously (jobId)?
- [ ] Is the response envelope consistent across success, 4xx, and 5xx?
- [ ] Is `requestId` included for traceability?
- [ ] Are error messages clear without leaking internals?
- [ ] Is everything documented?

---

## HTTP Status Codes Quick Reference

| Code | Meaning               | Use When                                |
| ---- | --------------------- | --------------------------------------- |
| 200  | OK                    | Successful GET, PUT, PATCH              |
| 201  | Created               | Successful POST that creates a resource |
| 202  | Accepted              | Async job accepted, processing started  |
| 204  | No Content            | Successful DELETE                       |
| 400  | Bad Request           | Client sent invalid data                |
| 401  | Unauthorized          | Missing or invalid authentication       |
| 403  | Forbidden             | Authenticated but not authorized        |
| 404  | Not Found             | Resource doesn't exist                  |
| 409  | Conflict              | Duplicate / state conflict              |
| 422  | Unprocessable Entity  | Validation error                        |
| 429  | Too Many Requests     | Rate limit exceeded                     |
| 500  | Internal Server Error | Server-side bug                         |
| 503  | Service Unavailable   | Server is down or overloaded            |
