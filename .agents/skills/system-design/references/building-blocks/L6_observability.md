---
name: observability
description: This skill should be used when the user asks about "observability" or "monitoring", what "metrics, logs, and traces" to collect, "health checks" (liveness/readiness), "alerting" or "on-call", "SLO/SLI" or "error budgets", the "RED" or "USE" method, "dashboards", or names a tool like "Prometheus", "Grafana", or "Datadog". Use it whenever a design has no answer to "how would we know this is broken?" or "what do we alert on?" â€” i.e. any time failure would be invisible until users complain, even if the user doesn't say "observability".
---

# Observability

Decide *what to measure* so a system can be seen, alerted on, and debugged in
production. Getting this wrong is failure mode #6 â€” ignoring failure: a design
that works on the whiteboard but goes dark under load, where the first signal of
an outage is a user complaint instead of a page.

## When to reach for this
Any production design needs an answer to "how would we know this broke, and how
fast?" Reach for this when defining what the system measures, what pages a human,
what an acceptable level of service is (SLO), or how a request is traced across
services. It is the design move that makes every *other* block's stress section
real â€” you cannot mitigate a thundering herd or a hot shard you can't see.

## When NOT to
Do not build a full metrics-logs-traces stack for a prototype or an internal tool
with no users to disappoint (YAGNI) â€” a health check and error logging are
enough. Do not invent SLOs nobody will defend, or wire alerts before knowing the
symptom that matters; an alert with no owner and no runbook is noise that trains
the team to ignore pages. This skill owns *what* to measure and alert on; the
**high-volume log pipeline** (collect â†’ buffer â†’ ship â†’ index â†’ retain) lives in
`distributed-logging` â€” summarize and link, don't rebuild it here.

## Clarify first
- **What is "healthy" from a user's view?** The symptom that defines a bad
  experience (slow checkout, failed upload) â€” alerts target this, not CPU.
- **SLO target and window?** e.g. 99.9% of requests < 300 ms over 30 days. This
  sets the error budget and the alert thresholds. (â†’ `back-of-the-envelope` for the nines.)
- **Request volume and cardinality?** QPS drives metric/trace sample rates;
  high-cardinality labels (user ID, URL) blow up a metrics store.
- **Is this request-driven or resource-driven?** Picks RED (services) vs USE
  (CPU/disk/queues) as the measurement frame.
- **Multi-service request path?** If a request crosses services, tracing earns
  its keep; a single service may not need it yet.

## The options

**The three pillars** (complementary, not either/or):
- **Metrics** â€” cheap numeric time series (counters, gauges, histograms). Use for
  dashboards, trend analysis, and *alerting* â€” the always-on signal.
- **Logs** â€” discrete events with context. Use for debugging the specific failure
  after an alert fires. (The pipeline that moves them is `distributed-logging`.)
- **Traces** â€” one request's journey across services with timing per hop. Use to
  find *which* service or dependency is the latency/error source.

**What to measure** (pick a frame per component):
- **RED** (request-driven services): **R**ate, **E**rrors, **D**uration. Use for
  APIs, web tiers, anything serving requests.
- **USE** (resources): **U**tilization, **S**aturation, **E**rrors. Use for CPU,
  memory, disk, connection pools, queues.
- **Four golden signals** (latency, traffic, errors, saturation) â€” the superset;
  use as the default service dashboard.

**Health checks** (the signal, consumed by `load-balancing`/orchestrator):
- **Liveness** â€” is the process alive / not deadlocked? Failure â‡’ *restart*. Keep
  it cheap; don't check dependencies. Use to recover stuck processes.
- **Readiness** â€” can this instance serve traffic *now* (deps reachable, warmup
  done)? Failure â‡’ *pull from rotation, don't restart*. Use to gate cold/struggling instances.

**Alerting**:
- **Symptom-based (SLO burn)** â€” page when the user-facing SLO is at risk. Use as
  the default; it is actionable and low-noise.
- **Cause-based (resource thresholds)** â€” ticket/warn on CPU, disk, saturation.
  Use for capacity planning, not paging.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| Metrics | Cheap, always-on alerting + trends | No per-request detail; high-cardinality labels explode storage/cost | You need to debug a *specific* request â†’ add traces/logs |
| Logs | Rich context for debugging an incident | Volume + cost; needs the `distributed-logging` pipeline to scale | Volume is unmanageable â†’ sample, or shift detail to metrics |
| Traces | Pinpoints the slow/failing hop across services | Instrumentation effort; sampling needed at high QPS | Single-service or low volume â†’ defer; metrics suffice |
| RED | Right frame for request services | Misses resource exhaustion that hasn't yet hurt requests | Component is a resource (queue, disk) â†’ use USE |
| USE | Catches saturation before it hurts users | Resource-centric, not user-centric; can be noisy | Alerting on it â†’ switch to symptom/SLO-based |
| Liveness check | Recovers deadlocked processes | Too aggressive â‡’ restart loops, mask real bugs | Restarts hide a crash-loop â†’ fix readiness/root cause |
| Readiness check | Keeps cold/broken instances out of rotation | Flapping if it checks flaky deps â‡’ capacity yo-yo | All instances fail readiness together â†’ it's a dep outage |
| SLO/error budget | Ties alerting + release pace to user pain | Effort to define + defend; wrong SLO misleads | Budget never burns (too loose) or always burns (too tight) |
| Symptom alerting | Low-noise, actionable pages | Slightly slower to localize root cause | Need faster localization â†’ add cause-based *tickets* (not pages) |

## Behavior under stress
Observability is most needed exactly when it's most likely to break or mislead.

- **The monitoring amplifies the outage.** Synchronous logging on the request path
  turns a slow log backend into request latency. Per-request trace export with no
  sampling melts the collector under a spike. Keep telemetry async and sampled so
  it degrades the *signal*, never the service.
- **Health-check stampede.** Aggressive liveness probes restart instances that are
  merely slow, and readiness flaps yank capacity mid-spike â€” making the spike
  worse. The gating/recovery behavior is owned by `load-balancing` and
  `resilience-failure`; this block owns defining a *stable* signal (sane
  thresholds, consecutive-failure counts, deps in readiness not liveness).
- **Cardinality blow-up.** A label like `user_id` or raw URL multiplies time series
  into the millions and OOMs the metrics store under load â€” drop or bucket
  high-cardinality dimensions.
- **Alert storm.** One root cause (a DB outage) fires fifty correlated alerts; the
  on-call drowns. Alert on the user-facing symptom; group/inhibit downstream alerts.
- **Blind spot on recovery.** After an incident, dashboards must show whether the
  fix worked and whether recovery traffic is overwhelming a cold tier.

**Monitor:** the four golden signals per service (rate, errors, latency p50/p95/p99,
saturation), SLO error-budget burn rate, healthy-host count and probe flap rate,
and the telemetry pipeline's own lag/drop rate (watch the watcher).

## How to apply
1. **Clarify the inputs** â€” pin the user-facing symptom, the SLO target + window,
   request volume/cardinality, and whether the path is multi-service (see *Clarify
   first*). No SLO yet? Define the symptom first; the number follows.
2. **Pick the pillars and frame from the trade-off table** â€” metrics for alerting
   always; RED for services and USE for resources; add traces only when a request
   crosses services or volume justifies it.
3. **Set the key knobs** â€” define liveness vs readiness endpoints (deps in
   readiness, not liveness), consecutive-failure thresholds, trace sample rate, and
   the SLO + error-budget policy. Drop high-cardinality labels up front.
4. **Stress-test the choice** â€” walk *Behavior under stress*: confirm telemetry is
   async/sampled, probes won't stampede, cardinality is bounded, and alerts group
   by root cause so one outage isn't fifty pages.
5. **Size it with numbers** â€” sanity-check metric series count and retention,
   trace/log sample volume against the QPS, and that the SLO's nines match the
   architecture's redundancy (â†’ *Numbers that matter*).
6. **Pick a provider** â€” default to the generic recipe; open a provider file only
   if the user named a cloud (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Alert on user-facing symptoms (SLO burn), and make every page actionable with a runbook.
- Put dependency checks in *readiness* and keep *liveness* cheap and dependency-free.
- Emit telemetry asynchronously and sampled so it never adds latency or melts the collector.
- Define an SLO + error budget you will actually defend, and tie release pace to it.
- Standardize a per-service dashboard on the four golden signals.

**Don't**
- Don't page on causes (CPU > 80%) â€” ticket those; pages are for user pain.
- Don't use high-cardinality labels (user ID, raw URL) as metric dimensions.
- Don't check downstream dependencies in liveness â€” you'll restart-loop the fleet.
- Don't build a full stack for a prototype, or wire alerts no one owns (YAGNI / alert fatigue).
- Don't reimplement the log pipeline here â€” that's `distributed-logging`.

## Numbers that matter
The SLO sets everything else: 99.9% over 30 days allows ~43 minutes of budget; if
the architecture's redundancy can't deliver those nines, the SLO is fiction (â†’
`back-of-the-envelope` for the availability-nines table). Alert on **p95/p99**, not
averages â€” averages hide tail pain. Sample traces (often 1â€“10% at high QPS) so cost
scales sub-linearly with traffic. Watch metric **cardinality** (series â‰ˆ product of
label values): one unbounded label can mean millions of series. Don't restate the
latency/QPS/nines tables â€” they live in `back-of-the-envelope`.

## Interface sketch
Telemetry has contracts worth pinning down. A **metric**: name + label set +
type (`http_requests_total{service,method,status}` counter) â€” labels are
low-cardinality. A **health endpoint**: `GET /livez` â†’ 200/503 (process only),
`GET /readyz` â†’ 200/503 (deps + warmup), with version/build info in the body for
debugging. A **trace context**: a `trace_id` + `span_id` propagated on every
inbound/outbound call (e.g. W3C `traceparent` header) so traces and logs correlate.

## Choosing a provider
Default to the generic recipe above (Prometheus + Grafana + Loki + Jaeger, glued
by OpenTelemetry). If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping, quotas/limits,
and provider-specific trade-offs. If no file exists for that provider, the generic
recipe is the answer.

## Diagram
To visualize the telemetry flow (app â†’ OpenTelemetry SDK â†’ collector â†’ metrics /
logs / traces backends â†’ dashboard + alertmanager) or the alert-to-page path, use
the in-plugin `architecture-diagram` skill. Telemetry export uses dashed arrows to
show it is off the request path.

## Related building blocks
- `distributed-logging` â€” *owned-concept lives in* there: the high-volume log
  pipeline (collect â†’ buffer â†’ ship â†’ index â†’ retain). This skill decides *what* to
  log and alert on; that skill decides *how* to move and store it at scale.
- `resilience-failure` â€” *pairs with* this: alerts and SLO burn trigger graceful
  degradation and circuit breaking, and the health-check signal defined here is the
  input its failover and `load-balancing` health-gating consume.
- `scaling-evolution` â€” *feeds into* it: saturation metrics and the golden signals
  reveal the next bottleneck that justifies the next scaling step.
- `back-of-the-envelope` â€” *feeds into* this skill: it supplies the availability
  nines and QPS that turn an SLO and sample rates into real numbers.
- `system-design` â€” *owned-concept lives in* the orchestrator: the reasoning loop,
  the trade-off method, and the ten failure modes (this block defends #6).

## References
- **`references/deep-dive.md`** â€” pillar mechanics (histograms vs gauges, push vs
  pull, sampling), SLI/SLO/error-budget math and burn-rate alerts, RED/USE in
  detail, health-check tuning, and alert design. Read when designing the
  observability layer in depth.
- **`references/providers/{generic,aws,azure,gcp}.md`** â€” service mappings, limits,
  and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Observability deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
observability layer in detail.

## The three pillars, mechanically

- **Metrics** are aggregated numeric time series, cheap to store and query.
  - **Counter** â€” monotonically increasing (requests, errors); you graph its
    *rate* (`rate(http_requests_total[5m])`).
  - **Gauge** â€” a value that goes up and down (queue depth, memory, in-flight
    requests).
  - **Histogram** â€” bucketed observations (request duration) so you can compute
    **percentiles** (p95/p99) server-side. Averages lie about tails; histograms are
    why you can alert on p99. Cost is the bucket count Ã— label cardinality.
- **Logs** are discrete, high-context events. They are the *most expensive pillar
  per unit of insight* at volume â€” which is exactly why the collect â†’ buffer â†’ ship
  â†’ index â†’ retain pipeline is its own concern (`distributed-logging`). Decide
  *what* and *at what level* to log here; push the moving/storing there.
- **Traces** capture one request as a tree of **spans** (one span per operation,
  with start/end + attributes), tied together by a propagated `trace_id`. They
  answer "where did the 800 ms go?" across service hops.

### Pull vs push collection
- **Pull** (Prometheus scrapes `/metrics`): the collector controls load and
  discovers targets; great for dynamic fleets, awkward for short-lived jobs and
  across NAT.
- **Push** (StatsD, OTLP push, push-gateway): the source sends; good for batch jobs
  and serverless, but the source must not block on a slow collector. Always buffer
  and drop rather than block the request path.

### OpenTelemetry as the seam
Instrument once with the OpenTelemetry SDK (vendor-neutral metrics, logs, traces)
and export via the **Collector** to whatever backend(s) you choose. This keeps the
app code portable across the generic stack and any cloud provider â€” the seam that
avoids lock-in at the instrumentation layer.

## Sampling (so cost scales sub-linearly)
- **Head sampling** â€” decide at request start (e.g. keep 5%). Cheap, but you may
  drop the trace of the one slow request you cared about.
- **Tail sampling** â€” buffer spans and decide after the request finishes; keep all
  errors and slow requests, sample the boring fast ones. Costs collector memory but
  keeps the *interesting* traces. Prefer tail sampling once volume hurts.
- Metrics are pre-aggregated, so they generally are *not* sampled â€” control their
  cost via **cardinality**, not rate.

## SLI / SLO / error budget (the math)
- **SLI** (indicator) â€” a measured ratio of good events to total, e.g.
  `good = requests < 300 ms and 2xx/3xx`, `SLI = good / valid`.
- **SLO** (objective) â€” the target over a window: "99.9% of requests good over 30
  days."
- **Error budget** â€” `1 âˆ’ SLO`. At 99.9% over 30 days you may "spend" ~43 minutes
  of badness. The budget is the contract: while it has room, ship features fast;
  when it's exhausted, freeze risky releases and spend effort on reliability.

### Burn-rate alerts (the right way to page on an SLO)
Don't page the instant the SLI dips. Alert on **burn rate** = how fast the budget
is being consumed relative to the window. A common two-window scheme:
- **Fast burn** â€” e.g. 14.4Ã— burn over 1 hour (would exhaust a 30-day budget in ~2
  days) â‡’ page now.
- **Slow burn** â€” e.g. 3Ã— over 6 hours â‡’ ticket.
Multi-window/multi-burn-rate alerts catch both sudden outages and slow leaks while
keeping noise low.

## RED and USE, applied
- **RED** per request-driven service: **R**ate (req/s), **E**rrors (failed req/s
  or %), **D**uration (latency histogram â†’ p50/p95/p99). The default API/web-tier
  dashboard.
- **USE** per resource: **U**tilization (% busy), **S**aturation (queued work â€”
  often the *earliest* warning, e.g. run-queue length, connection-pool wait),
  **E**rrors (device/driver errors). Saturation leads utilization: a pool at 100%
  utilization with a growing wait queue is already hurting.
- **Four golden signals** = latency + traffic + errors + saturation â€” RED âˆª the
  saturation half of USE. Use as the standard service dashboard.

## Health checks, tuned
- **Liveness** answers "is the process wedged?" â€” keep it to in-process state
  (event loop responsive, no deadlock). *Never* call the DB here: a DB blip would
  restart-loop the whole fleet and turn a dependency hiccup into an outage.
- **Readiness** answers "should I get traffic right now?" â€” check critical deps,
  warmup/migration completion, and shed when overloaded. Failure pulls the instance
  from rotation without killing it.
- **Thresholds:** require N consecutive failures (â‰ˆ3) before acting, and tune
  probe interval + initial-delay so a slow-but-recovering instance isn't killed.
  The *consumption* of these signals (gating, recovery ramp) is owned by
  `load-balancing` and `resilience-failure`; here you define a *stable* signal.

## Alert design (avoid fatigue)
- **Symptom over cause:** page on "checkout error rate > X" / SLO burn, not "CPU >
  80%". Causes become tickets and dashboards.
- **Every page is actionable + has a runbook link.** If a human can't act on it,
  it's a dashboard, not an alert.
- **Group and inhibit:** one root cause (DB down) should fire *one* incident, not
  fifty correlated pages. Use alert grouping and inhibition rules.
- **Review quarterly:** delete alerts that never fire or always get acked-and-ignored.

## Cardinality, the metrics cost killer
Series count â‰ˆ product of all label-value counts. A `user_id` or raw-`path` label
turns one metric into millions of series and OOMs the store. Keep labels
low-cardinality (status code, route *template*, region); put high-cardinality
identifiers in **traces/logs**, not metric labels.

## Common mistakes
- Synchronous logging/trace export on the request path (telemetry adds latency).
- No sampling at high QPS â†’ the collector falls over during the spike you most need
  to see.
- Alerting on averages instead of percentiles (tail latency stays invisible).
- Dependency checks in liveness â†’ restart loops.
- SLOs nobody defends, or so loose the budget never burns (they mislead instead of guide).
- Treating the metrics store as a log store via high-cardinality labels.

