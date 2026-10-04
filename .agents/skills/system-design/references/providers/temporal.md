# TEMPORAL Cloud Architecture & Service Mapping

Comprehensive mapping of system design building blocks to TEMPORAL managed services and architecture patterns.

---

## Building Block: messaging-streaming

# Messaging & streaming â€” Temporal (durable execution)

Temporal is not a broker; it's a **durable workflow engine**. It belongs here as
the alternative to hand-rolling a multi-step async process out of queues + retry
logic + state flags + compensation handlers.

## What it maps to in the generic options
- Replaces the **durable workflow** option, and often the *orchestration glue*
  around queues. You write the workflow as ordinary code; Temporal persists every
  step's result and the workflow's position, so a worker crash resumes exactly
  where it stopped. Retries, timers (sleep days/weeks), and compensation (saga
  rollback) are first-class. (Saga *theory*: `consistency-coordination`.)
- It does **not** replace a high-throughput transport stream (Kafka/Kinesis) or a
  raw fan-out bus â€” pair Temporal with those: a stream/queue delivers the trigger,
  a Temporal workflow orchestrates the multi-step reaction.

## When to choose it (the decision)
Reach for Temporal when the orchestration *is* the hard part:
- Long-running or human-in-the-loop processes (order â†’ pay â†’ ship â†’ refund;
  approvals that wait days).
- Correctness under partial failure matters and "which step are we on after a
  crash?" is non-trivial.
- You need visibility into in-flight workflows, retries, and history.

Skip it when a single async step suffices â€” a plain queue + idempotent consumer is
simpler. The engine is a new runtime, a new programming model (determinism rules),
and a dependency to operate (self-hosted) or a bill (Temporal Cloud).

## Decision-changing limits (verify against current docs)
- **Workflow code must be deterministic** â€” no direct clocks, randomness, or I/O
  in workflow functions; side effects go in **Activities**. Violating determinism
  breaks replay. This is the main learning curve.
- **Activity timeouts and retry policies** are explicit and per-activity; the
  durable equivalent of visibility timeout + retry/backoff.
- **History size / event count per workflow** is bounded; very long or high-volume
  loops use **Continue-As-New** to reset history.
- **Self-hosted** needs a backing store (Cassandra/PostgreSQL/MySQL) and operational
  care; **Temporal Cloud** removes that at a cost and some lock-in.

## Provider-specific trade-offs
- Buys crash-safe orchestration and removes a whole class of hand-rolled
  state-machine bugs; costs a runtime, the determinism model, and engine lock-in
  (workflow code is Temporal-shaped).
- Cloud-native analogs exist (AWS Step Functions, Azure Durable Functions, GCP
  Workflows). Temporal wins on code-first ergonomics, portability across clouds,
  and complex/long workflows; the cloud-native options win on zero-ops within
  their ecosystem.

## Pitfalls
- Putting non-deterministic code (time, UUIDs, HTTP) directly in a workflow â†’
  replay failures.
- Using Temporal as a message queue or stream â€” it orchestrates, it doesn't
  transport high-volume events.
- Unbounded workflow history (long loops without Continue-As-New).
- Reaching for it for a single fire-and-forget job where a queue would do (YAGNI).


---

## Building Block: resilience-failure

# Resilience & failure â€” Temporal (durable execution)

Read this when the resilient unit of work is a **multi-step, long-running
process** (an order, a payment flow, a provisioning pipeline) rather than a
single request/response call. Temporal makes retries, timeouts, and recovery
*durable primitives of the workflow itself* instead of ad-hoc app logic.

## Service mapping (generic option â†’ Temporal primitive)
- **Retry with backoff + jitter** â†’ an **Activity RetryPolicy** (initial interval,
  backoff coefficient, max interval, max attempts, non-retryable error types).
  Temporal owns the retry loop and persists attempt state, so a worker crash mid-
  retry resumes from the durable record, not from zero.
- **Timeout** â†’ built-in **StartToClose / ScheduleToClose / Heartbeat** timeouts
  per activity. Heartbeat timeouts detect a stuck worker on a long activity.
- **Graceful degradation / compensation** â†’ the **Saga pattern**: on a failed
  step, run registered compensating activities to undo prior steps (the
  distributed-transaction alternative; the saga *theory* is owned by
  `consistency-coordination`).
- **Recovery without stampede** â†’ workflow state is durable, so after an outage a
  workflow **resumes deterministically** from its last completed step instead of
  every client re-driving the whole process. No replay-the-backlog herd.
- **Rate limiting** â†’ worker **task-queue concurrency limits** and activity
  **rate limits** cap how fast work is pulled â€” backpressure rather than a 429 at
  the edge (edge limiting still belongs upstream).

## Limits / things that bite (verify against current docs)
- Workflow code must be **deterministic** â€” no wall-clock, random, or direct I/O
  in workflow functions (use activities / Temporal's SDK APIs). Non-determinism
  breaks replay-based recovery.
- Event-history size and per-workflow limits are bounded; very long or high-event
  workflows need **Continue-As-New** to reset history.
- The Temporal **service/cluster (and its persistence store) is itself a
  dependency** to make highly available â€” it's not magic uptime.

## Provider-specific trade-offs
- Temporal replaces *hand-rolled* retry/timeout/saga state machines and the brittle
  "where was I?" recovery logic with durable guarantees â€” a big win for
  long-running orchestration.
- It adds an operational dependency (the cluster) and a programming-model
  constraint (determinism). **YAGNI for a plain stateless request path** â€” a
  resilience library is lighter there. Reach for it when the *process*, not the
  call, must survive crashes.

## Pitfalls
- Sneaking non-determinism into workflow code (clock, UUID, network) â€” passes in
  test, fails on replay.
- Treating Temporal's durable retries as a license to retry **non-idempotent**
  activities without dedup â€” the activity still needs an idempotency key
  (â†’ `api-design`).
- Letting event history grow unbounded instead of using Continue-As-New.
- Forgetting the Temporal cluster needs the same redundancy/SPOF analysis as any
  other critical component.


---

## Building Block: task-scheduling

# Task scheduling â€” Temporal (durable execution)

Temporal is not a queue or a cron daemon; it's a **durable workflow engine**. It
belongs here as the alternative to hand-rolling reliable scheduling, leasing,
retries, and timeouts out of a queue + cron + state flags â€” the engine makes all
of those first-class and crash-safe.

## What it maps to in the generic options
- Replaces the **distributed scheduler** + **worker leasing** + **retry/timeout**
  machinery with one model. Temporal **Schedules** fire recurring/cron and delayed
  workflows (no leader lock to operate). Inside a workflow, `sleep` for seconds or
  weeks is a durable timer; **Activity timeouts + retry policies** are the durable
  equivalent of visibility timeout + lease heartbeat + retry/backoff.
- It does **not** replace a high-throughput transport (Pub/Sub, Kafka, SQS) for
  fan-out delivery â€” pair them: a queue delivers the trigger, a Temporal workflow
  orchestrates the multi-step, retry-heavy reaction. (Saga *theory*:
  `consistency-coordination`.)

## When to choose it (the decision)
Reach for Temporal when the *reliability of the orchestration* is the hard part:
multi-step jobs with retries and compensation, long-running or human-in-the-loop
delays (wait days for approval), and "which step are we on after a crash?" being
non-trivial. The engine persists every step, so a worker crash resumes exactly
where it stopped. Skip it when a single scheduled or delayed job suffices â€” a
plain scheduler + queue + idempotent worker is simpler.

## Decision-changing limits (verify against current docs)
- **Workflow code must be deterministic** â€” no direct clocks, randomness, or I/O
  in workflow functions; side effects go in **Activities**. This is the main
  learning curve and the source of most bugs.
- **Activity timeouts (start-to-close, heartbeat) and retry policies** are
  explicit and per-activity â€” set heartbeat timeouts for long activities so a
  dead worker is detected promptly (the lease-heartbeat equivalent).
- **History size / event count per workflow** is bounded; long recurring loops use
  **Continue-As-New** to reset history.
- **Self-hosted** needs a backing store (Cassandra/PostgreSQL/MySQL) and ops care;
  **Temporal Cloud** removes that at a cost and some lock-in.

## Provider-specific trade-offs
- Buys crash-safe scheduling/retries/timeouts and removes a class of hand-rolled
  state-machine and double-fire bugs; costs a runtime, the determinism model, and
  engine lock-in (workflow code is Temporal-shaped).
- Cloud-native analogs (AWS Step Functions, Azure Durable Functions, GCP
  Workflows) win on zero-ops within their ecosystem; Temporal wins on code-first
  ergonomics, cross-cloud portability, and complex/long workflows.

## Pitfalls
- Putting non-deterministic code (time, UUIDs, HTTP) directly in a workflow â†’
  replay failures.
- Using Temporal as a high-volume message queue/stream â€” it orchestrates, it
  doesn't transport bulk events.
- Unbounded workflow history (long recurring loops without Continue-As-New).
- Reaching for it for a single cron job where a scheduler + queue would do (YAGNI).


---


