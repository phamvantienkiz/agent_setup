# Monitoring & Observability

> Standards for logging, metrics, tracing, alerting, and Grafana dashboard design.

## 🔭 The Three Pillars of Observability

| Pillar | Tool | Purpose |
|--------|------|---------|
| **Logs** | Winston / Pino + Loki | What happened |
| **Metrics** | Prometheus + Grafana | How the system is behaving |
| **Traces** | OpenTelemetry + Jaeger | Why something is slow |

---

## 📝 Logging Rules

### Log Levels
| Level | When to Use |
|-------|-------------|
| `error` | Unexpected failure requiring attention |
| `warn` | Unexpected but recoverable situation |
| `info` | Normal significant events (startup, request lifecycle) |
| `debug` | Detailed debugging info (dev only) |
| `trace` | Very verbose (never in production) |

### Log Format — Structured JSON (always!)
```js
// ✅ Structured log — searchable and parseable
logger.info({
  event: 'order.placed',
  orderId: order.id,
  userId: user.id,
  amount: order.total,
  durationMs: Date.now() - startTime,
  requestId: req.id,
});

// ❌ Unstructured log — cannot be queried
console.log(`Order ${orderId} placed by user ${userId}`);
```

### Mandatory Fields
```js
{
  level: 'info',
  timestamp: '2026-01-01T00:00:00.000Z',
  service: 'order-service',
  version: '1.2.3',
  environment: 'production',
  requestId: 'uuid',          // trace across services
  userId: 'uuid',             // who triggered it
  event: 'order.placed',      // what happened
  durationMs: 45,             // how long
  // ... domain-specific fields
}
```

### What NOT to Log
```js
// ❌ Never log sensitive data
logger.info({ password: user.password });     // NEVER
logger.info({ token: req.headers.authorization }); // NEVER
logger.info({ creditCard: payment.card });    // NEVER
logger.info({ ssn: user.socialSecurityNumber }); // NEVER
```

### Logger Setup (Pino)
```js
// src/utils/logger.js
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  base: {
    service: process.env.APP_NAME,
    version: process.env.npm_package_version,
    env: process.env.NODE_ENV,
  },
  timestamp: pino.stdTimeFunctions.isoTime,
});
```

---

## 📊 Metrics (Prometheus + Grafana)

### Metric Types
| Type | Use Case | Example |
|------|----------|---------|
| **Counter** | Values that only increase | `http_requests_total` |
| **Gauge** | Values that go up and down | `active_connections`, `memory_usage_bytes` |
| **Histogram** | Distribution of values | `http_request_duration_seconds` |
| **Summary** | Pre-calculated percentiles | `request_latency_percentiles` |

### Naming Convention
```
# Pattern: {namespace}_{subsystem}_{name}_{unit}
# All lowercase, underscores, snake_case

http_request_duration_seconds         # histogram
http_requests_total                   # counter
http_requests_in_flight               # gauge
db_query_duration_seconds             # histogram
cache_hits_total                      # counter
cache_misses_total                    # counter
queue_messages_pending                # gauge
queue_processing_duration_seconds     # histogram
payment_transactions_total            # counter (+ status label)
```

### Labels (Dimensions)
```js
// ✅ Use labels for meaningful dimensions
httpRequestCounter.labels({
  method: req.method,        // GET, POST, etc.
  route: '/api/v1/users',    // normalized route
  status_code: res.statusCode,
  service: 'user-service',
}).inc();

// ❌ Don't use high-cardinality labels (userId, orderId)
// This creates millions of time series → kills Prometheus
```

### Express Middleware for Metrics
```js
// middleware/metrics.js
import client from 'prom-client';

const httpDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
});

export function metricsMiddleware(req, res, next) {
  const end = httpDuration.startTimer();
  res.on('finish', () => {
    end({ method: req.method, route: req.route?.path || req.path, status_code: res.statusCode });
  });
  next();
}

// Expose metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

---

## 📈 Grafana Dashboard Design

### Dashboard Naming
```
# Pattern: {Service} — {Category}
User Service — Overview
User Service — Errors & Latency
Order Service — Business Metrics
Infrastructure — Redis
Infrastructure — PostgreSQL
```

### Panel Naming
```
# Use title case, include units in title
Request Rate (req/s)
P99 Latency (ms)
Error Rate (%)
Active DB Connections
Cache Hit Rate (%)
Queue Depth
Memory Usage (MB)
```

### The RED Method (for Services)
Every service dashboard MUST have these 3 panels:
- **R** — **Rate**: requests per second
- **E** — **Errors**: error rate (%)
- **D** — **Duration**: P50, P95, P99 latency

```promql
# Rate
rate(http_requests_total{service="order-service"}[5m])

# Error rate
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m]) * 100

# P99 latency (ms)
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket{service="order-service"}[5m])
) * 1000
```

### The USE Method (for Infrastructure)
Every infrastructure dashboard MUST have:
- **U** — **Utilization**: % of resource being used
- **S** — **Saturation**: queue depth, wait time
- **E** — **Errors**: error count/rate

### Standard Dashboard Layout
```
Row 1: Summary / Health Overview (traffic lights)
Row 2: RED metrics (Rate, Errors, Duration)
Row 3: Resource usage (CPU, Memory, DB connections)
Row 4: Business metrics (orders/min, signups, payments)
Row 5: Logs panel (Loki integration)
```

---

## 🚨 Alerting Rules

### Severity Levels
| Level | Response Time | Example |
|-------|--------------|---------|
| `critical` | Immediate (PagerDuty) | Service down, payment failures |
| `warning` | Within 30min (Slack) | High error rate, slow queries |
| `info` | Business hours | Unusual traffic patterns |

### Standard Alert Rules (Prometheus AlertManager)
```yaml
groups:
  - name: service-alerts
    rules:
      # Service is down
      - alert: ServiceDown
        expr: up{job="my-service"} == 0
        for: 1m
        severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"

      # High error rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 5m
        severity: warning
        annotations:
          summary: "Error rate > 5% on {{ $labels.service }}"

      # High P99 latency
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        severity: warning
        annotations:
          summary: "P99 latency > 1s on {{ $labels.service }}"

      # Low cache hit rate
      - alert: LowCacheHitRate
        expr: |
          rate(cache_hits_total[5m])
          / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.7
        for: 10m
        severity: warning
```

### Alert Naming Convention
```
{Severity}{Service}{Problem}
CriticalPaymentServiceDown
WarningOrderServiceHighLatency
WarningRedisLowHitRate
CriticalDatabaseConnectionsExhausted
```

---

## 🔍 Distributed Tracing (OpenTelemetry)

```js
// src/tracing.js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';

const sdk = new NodeSDK({
  traceExporter: new JaegerExporter({ endpoint: process.env.JAEGER_ENDPOINT }),
  instrumentations: [getNodeAutoInstrumentations()],
  serviceName: process.env.APP_NAME,
});

sdk.start();
```

### Span Naming
```
# HTTP: {method} {route}
GET /api/v1/users/:id

# DB: {operation} {table}
SELECT users
INSERT orders

# Cache: {operation} {key_pattern}
GET user:{id}
SET session:{id}

# Queue: {operation} {queue_name}
PUBLISH order.placed
CONSUME email.send
```
