---
name: task-scheduling
description: This skill should be used when the user designs a "task scheduler", "job scheduler", "job queue", "cron at scale", "distributed cron", "delayed / scheduled / recurring tasks", a "worker pool", reaches for "Celery / Sidekiq / Airflow", or wrestles with "task leasing", visibility timeouts, job priorities, fairness, or duplicate task execution. Use it whenever work must run later, on a schedule, or be reliably leased to a pool of workers, even if the user doesn't say "scheduler". (For plain queue transport and delivery guarantees, that is `messaging-streaming`.)
---

# Task Scheduling

Decide *when* work runs and *which worker* runs it: fire jobs on a schedule
(cron/delayed/recurring), hand each job to exactly one worker via a lease, and
make sure it completes once despite crashes and retries. This sits *on top of*
`messaging-streaming` queues â€” the queue is the transport; this skill adds the
scheduling, leasing, priorities, and task-level idempotency. Getting it wrong
shows up as jobs that never run, run twice (double charge, double email), or
pile up until a worker fleet falls permanently behind.

## When to reach for this
Work must run **later** (send a reminder in 24h), **on a schedule** (nightly
rollups, hourly cron), or **repeatedly** (poll every 5 min); a slow operation is
already off the request path (â†’ `messaging-streaming`) and now needs reliable
allocation to a pool of workers; jobs need **priorities** (paid before free) or
**fairness** (no single tenant starves others); or a job must complete **exactly
once** even though the worker holding it can crash mid-flight.

## When NOT to
The caller needs the result inline â€” that's a synchronous call, not a scheduled
job. A single fire-and-forget async step with no schedule, priority, or
exactly-once need â€” a plain queue + idempotent consumer (`messaging-streaming`)
is simpler; don't add a scheduler on top. One periodic job on one box â€”
OS `cron` is fine until you have multiple schedulers or need history and
retries. A long-running multi-step saga with rollback â€” reach for a durable
workflow engine instead of hand-rolling state across jobs. Don't stand up
Airflow/Celery "because we'll have batch jobs eventually" (YAGNI): it's a
stateful control plane to operate and monitor.

## Clarify first
- **Trigger type** â€” scheduled (cron/at a time), delayed (run after N seconds),
  recurring (every N), or event-driven (a queue message arrives)? This decides
  whether a scheduler is even in scope.
- **Exactly-once vs at-least-once** â€” is a duplicate run harmful (money, email)
  or harmless (idempotent recompute)? Drives the leasing + dedup design.
- **Latency budget vs throughput** â€” must a delayed job fire within seconds of
  its time, or is "within a few minutes" fine? Tight timing is more expensive.
- **Priority / fairness** â€” do some jobs jump the line, and must one tenant or
  job class be prevented from starving the rest? (â†’ `back-of-the-envelope` for
  arrival vs. service rate.)
- **Job duration & variance** â€” seconds or hours? Sets the visibility-timeout /
  lease length and whether long jobs need heartbeats.
- **Idempotency key** â€” what identifies a task as the same task on retry?
  (The key contract is owned by `api-design`.)

## The options

**Scheduling trigger**
- **OS cron / single scheduler** â€” one process fires jobs on a crontab. *Use
  when* one node, a handful of jobs, no HA requirement.
- **Distributed scheduler (HA cron)** â€” a leader-elected scheduler enqueues due
  jobs into a queue; followers stand by. *Use when* the schedule must survive a
  node loss and must not double-fire.
- **Delay queue / timer** â€” jobs carry a "not before" time; the queue holds them
  until due (delivery delay, sorted-set scoring, or a timer wheel). *Use when*
  per-job delays vary and you don't want a cron tick.
- **Workflow/orchestration DAG** â€” declared task dependencies with backfill and
  history (Airflow-style). *Use when* batch pipelines have dependencies and you
  need a run history and reruns.

**Worker allocation**
- **Pull (worker leasing)** â€” workers poll the queue, lease a job for a
  **visibility timeout**, and ack/delete on success. *Use when* you want
  back-pressure for free and elastic, self-balancing workers. The default.
- **Push (dispatcher assigns)** â€” a coordinator routes jobs to specific workers.
  *Use when* affinity/locality matters (a job must run where its data is).

**Priority & fairness**
- **Priority queues** â€” separate high/low queues drained in order. *Use when*
  some classes must run first.
- **Weighted / fair scheduling** â€” round-robin or weighted draw across per-tenant
  queues. *Use when* one tenant's burst must not starve others.

## Trade-offs

| Option | What it solves | What it worsens | Change it when |
|---|---|---|---|
| OS cron / single scheduler | Trivial; zero infra | SPOF â€” node dies, schedule stops; no retry/history | You need HA or missed-run recovery â†’ distributed scheduler |
| Distributed scheduler (HA cron) | Survives node loss; no double-fire (leader-elected) | Needs leader election (â†’ `consistency-coordination`); more moving parts | One box and one job is enough â†’ OS cron |
| Delay queue / timer | Per-job delays without a cron tick; precise-ish timing | Far-future jobs sit in the queue; timer accuracy bounded by poll interval | Delays are uniform/periodic â†’ cron; dependencies exist â†’ DAG |
| Workflow DAG (Airflow-style) | Dependencies, backfill, run history, reruns | Heavy control plane; scheduler latency; overkill for single jobs | Jobs are independent one-shots â†’ plain queue + scheduler |
| Pull (worker leasing) | Self-balancing, elastic, natural back-pressure | At-least-once: lease expiry on a slow job re-runs it (need idempotency) | A job must run on a specific node (data locality) â†’ push |
| Push (dispatcher) | Affinity/locality; central control | Dispatcher is a bottleneck/SPOF; must track worker health | No locality need â†’ pull is simpler |
| Priority queues | Important work runs first | Low-priority starvation under sustained load | Fairness across tenants matters â†’ weighted/fair |
| Weighted / fair scheduling | No tenant starves another | More complex; per-tenant accounting | Only one workload class exists â†’ single queue |

## Behavior under stress
A scheduler can quietly fall behind, or it can *amplify* an outage by
re-dispatching work a struggling fleet can't finish.

- **Backlog growth:** arrival rate exceeds worker throughput; due jobs queue up
  and "scheduled for 09:00" runs at 09:40. End-to-end delay climbs while CPU
  looks fine. *Mitigate:* alarm on **oldest-due-job age** and queue depth, not
  just rate; scale workers; shed or defer low-priority jobs.
- **Lease expiry / re-run storm (the classic):** a job runs longer than its
  visibility timeout, the lease expires, the queue redelivers it to a second
  worker, and now two workers run it â€” wasting capacity and, without idempotency,
  double-applying side effects. *Mitigate:* set the timeout above p99 job
  duration, **heartbeat to extend** the lease on long jobs, and make tasks
  idempotent/deduped.
- **Poison task:** a job that always fails is retried forever, burning workers
  and re-loading a sick downstream. *Mitigate:* cap retries with backoff+jitter,
  then route to a dead-letter queue (retries/backoff/DLQ are owned by
  `resilience-failure`).
- **Thundering herd at the tick:** thousands of cron jobs all scheduled at the
  top of the hour fire at once and stampede a downstream. *Mitigate:* jitter the
  schedule, spread triggers, or rate-limit dispatch.
- **Scheduler split-brain:** two schedulers both think they're leader and
  double-enqueue every recurring job. *Mitigate:* a single leader via leader
  election + fencing (â†’ `consistency-coordination`); idempotent enqueue keyed by
  (job, scheduled_time).
- **Starvation:** a flood of high-priority or one noisy tenant's jobs starves
  everyone else. *Mitigate:* fair/weighted scheduling and per-tenant concurrency
  caps.

**Monitor:** oldest-due-job age (the best lateness signal), queue depth per
priority, lease-expiry / redelivery rate, retry and DLQ rate, worker utilization,
and per-tenant share.

## How to apply
1. **Clarify the inputs.** Settle trigger type, exactly-once vs at-least-once,
   latency budget, priority/fairness, and job duration (see *Clarify first*). If
   the work is a single async step with no schedule or priority, stop â€” a plain
   queue + idempotent consumer (`messaging-streaming`) is enough.
2. **Pick from the trade-off table.** Choose a trigger (cron â†’ distributed
   scheduler â†’ delay queue â†’ DAG, cheapest that fits), an allocation model (pull
   leasing is the default; push only for locality), and a priority/fairness model
   only if more than one class exists.
3. **Set the key knobs.** Visibility timeout above p99 job duration, retry cap +
   backoff before the DLQ, the dedup/idempotency key per task, the lease
   heartbeat interval for long jobs, and per-tenant concurrency limits.
4. **Stress-test the choice.** Walk backlog growth, lease-expiry re-runs, poison
   tasks, tick stampede, scheduler split-brain, and starvation. Confirm a
   mitigation exists for each one the workload can trigger.
5. **Size it with numbers.** Workers needed = arrival rate Ã— avg job seconds /
   target concurrency (Little's law); confirm sustained throughput drains peak
   arrival, and that far-future delayed jobs fit storage (â†’ *Numbers that matter*).
6. **Pick a provider.** Default to the generic recipe; only open a provider file
   if the user named a cloud (see *Choosing a provider*).

## Dos and don'ts
**Do**
- Default to pull-based worker leasing with a visibility timeout; it self-balances.
- Set the visibility timeout above p99 job duration and heartbeat-extend long jobs.
- Make every task idempotent (dedup on a task key) so a re-run is harmless.
- Elect a single leader for the scheduler and key recurring enqueues by (job, time).
- Cap retries with backoff+jitter, then dead-letter; alarm on oldest-due-job age.

**Don't**
- Don't assume a leased job ran once â€” at-least-once means design for duplicates.
- Don't schedule every cron job at :00 â€” jitter so the tick doesn't stampede.
- Don't run two schedulers without leader election (split-brain double-fires).
- Don't retry a poison task forever; cap it and dead-letter it.
- Don't reach for Airflow/Celery before a schedule, priority, or HA need is real (YAGNI).

## Numbers that matter
Size the worker pool with Little's law: in-flight jobs = arrival rate Ã— average
job duration, so workers â‰ˆ peak arrival Ã— avg seconds-per-job / per-worker
concurrency. Sustained drain must exceed peak arrival or the backlog never
clears. Set the visibility timeout above the p99 job duration (a too-short
timeout is the #1 cause of duplicate runs); set far-future delay storage =
delayed-job rate Ã— max delay Ã— job size. Don't restate the latency/QPS tables â€”
pull the rates and durations from `back-of-the-envelope`.

## Interface sketch
A scheduled task is a contract. Define it, not "a job":
- **Task envelope:** stable `task_id` / idempotency key (dedup on retry â€” key
  contract owned by `api-design`), `task_type`/version, `payload`, `priority`,
  `scheduled_for` (run-not-before), `attempt`, and a `trace_id`.
- **Schedule spec:** for recurring jobs, the cron/interval expression *plus* a
  `dedup_key = (job_name, scheduled_time)` so a double-enqueue is a no-op.
- **Lease contract:** on dequeue a worker gets the task invisible for
  `visibility_timeout`; it must ack/delete on success or heartbeat to extend.
  Lease expiry â†’ automatic redelivery. Failure after the retry cap â†’ DLQ with
  attempt count and last error.

## Choosing a provider
Default to the generic recipe above. If the user names a cloud, read
`references/providers/<provider>.md` for the managed-service mapping,
quotas/limits, and provider-specific trade-offs. If no file exists for that
provider, the generic recipe is the answer.

## Diagram
To visualize the scheduler â†’ queue â†’ leased workers path, or the lease-expiry
redelivery loop, use the in-plugin `architecture-diagram` skill. Quick inline
sketch: `[scheduler] â†’ [delay/priority queue] â†’ workers (lease) â”€expireâ†’ requeue â”€failÃ—Nâ†’ [DLQ]`;
main path solid, the expiry/DLQ branches dashed.

## Related building blocks
- `messaging-streaming` â€” *depends on* it: queues are the transport this skill
  schedules onto and leases from; it owns delivery guarantees, ordering, and DLQs
  and this skill does not reimplement them.
- `resilience-failure` â€” *pairs with* it for the retry policy: backoff, jitter,
  and DLQ-as-containment are tuned there; this skill names them.
- `api-design` â€” *depends on* its idempotency-key contract, the mechanism that
  makes a re-run after lease expiry safe.
- `consistency-coordination` â€” *depends on* it for leader election (and fencing)
  so only one scheduler is active and recurring jobs don't double-fire.
- `back-of-the-envelope` â€” *feeds into* sizing: arrival rate and job duration set
  the worker count and backlog drain.
- `system-design` â€” *feeds into* the orchestrator's reasoning loop; it routes here
  when work must run later, on a schedule, or be reliably allocated to workers.

## References
- **`references/deep-dive.md`** â€” leasing/visibility-timeout mechanics and
  heartbeats, distributed-cron + leader election, delay-queue implementations
  (sorted set, timer wheel), priority/fairness algorithms, exactly-once-effect via
  dedup, and Celery/Sidekiq/Airflow internals. Read when designing the scheduler in detail.
- **`references/providers/{generic,aws,azure,gcp,temporal}.md`** â€” service
  mappings, decision-changing limits, and pitfalls per environment.


---

# Deep Dive & Technical Mechanics

# Task scheduling deep-dive

Mechanics that don't belong in the lean SKILL.md. Read when designing the
scheduler/worker layer in detail. Queue delivery itself lives in
`messaging-streaming`; this covers what scheduling and leasing add on top.

## Worker leasing & visibility timeout (the core mechanism)

Pull-based allocation works by *leasing*, not deleting on dequeue:

1. A worker dequeues a task; the broker makes it **invisible** to other workers
   for `visibility_timeout` seconds (the lease).
2. The worker processes it. On success it **acks/deletes** the task.
3. If the worker crashes or runs past the timeout without acking, the lease
   expires and the broker **redelivers** the task to another worker.

This gives at-least-once delivery for free: no task is lost on a crash. The cost
is duplicates â€” a slow job whose lease expires runs twice. Three knobs control
the failure surface:

- **Timeout length:** set above p99 job duration. Too short â†’ constant
  re-delivery of healthy long jobs (the #1 cause of accidental double-runs). Too
  long â†’ a crashed worker's job sits stuck until the timeout elapses (slow
  recovery). When duration varies wildly, prefer heartbeats over a single big
  timeout.
- **Heartbeat / lease extension:** long jobs periodically renew the lease (extend
  visibility). If the worker dies, heartbeats stop and the lease expires
  promptly â€” fast recovery *and* no spurious re-delivery of live jobs.
- **Fencing token:** when a re-delivery races the original (the first worker was
  only slow, not dead), a monotonic fence token + a "last writer wins by token"
  check at the side-effect boundary stops the stale worker from committing.
  Fencing/leases theory: `consistency-coordination`.

## Distributed cron & leader election

A single scheduler is a SPOF; running N schedulers naively double-fires every
job. The standard fix: **elect one leader** that owns enqueuing due jobs;
followers stand by and take over on leader loss (lease/lock in
ZooKeeper/etcd/Consul, or a DB row lock). Leader election + fencing are owned by
`consistency-coordination`.

Even with one leader, make enqueue **idempotent**: key each recurring fire by
`(job_name, scheduled_time)` so a leader handover that re-runs the tick produces
a no-op, not a duplicate. The scheduler's job is only to *enqueue* due work; the
worker fleet drains it â€” keep the two concerns separate so the scheduler stays
light and the workers scale independently.

## Delay-queue implementations

Holding a job until its "not before" time, three common ways:

- **Native delivery delay:** the broker hides the message until the delay
  elapses (simple; often capped, e.g. max ~15 min â€” chain or re-enqueue for
  longer).
- **Sorted set by timestamp** (Redis `ZADD score=run_at`): a poller pops members
  whose score â‰¤ now. Timer accuracy is bounded by the poll interval; cheap and
  flexible for arbitrary far-future delays.
- **Timer wheel / hashed wheel:** O(1) insert/expire buckets for huge numbers of
  short timers (used inside many schedulers). Best for millions of near-term
  timers; more complex.

Far-future jobs (a reminder in 30 days) shouldn't squat in a hot queue â€”
persist them in a store and have the scheduler promote them to the run queue as
their time approaches.

## Priority & fairness algorithms

- **Strict priority queues:** drain high before low. Simple, but sustained
  high-priority load **starves** low forever.
- **Weighted round-robin / weighted fair queuing:** draw across classes by weight
  (e.g. 4 high : 1 low) so low still makes progress. Prevents starvation.
- **Per-tenant fair share:** one queue per tenant (or a token/credit per tenant),
  drained round-robin, plus a **per-tenant concurrency cap** so one tenant's
  burst can't seize the whole fleet. The fix for the "noisy neighbor" problem.
- **Aging:** bump a job's effective priority the longer it waits, so low-priority
  work eventually runs even under high-priority pressure.

## Exactly-once *effect* (not exactly-once delivery)

True exactly-once delivery across systems is impractical; aim for **exactly-once
effect** under at-least-once delivery:

- **Dedup table / idempotency key:** record `task_id` (or a business key) on
  first successful completion; a re-delivery that finds the key already done
  short-circuits. Key contract owned by `api-design`.
- **Idempotent operations:** design side effects so applying them twice equals
  once (upsert by id, conditional write, "charge with idempotency key").
- **Transactional outcome:** commit the result and the dedup marker in one
  transaction where the store allows it, so a crash can't leave them out of sync.

## Engine landscape (when it matters)

- **Celery (Python) / Sidekiq (Ruby) / BullMQ (Node):** task queues over a broker
  (Redis/RabbitMQ). Provide worker pools, retries, scheduled/delayed tasks
  (Celery `beat`, Sidekiq-cron), and priority queues. Beat/cron schedulers are
  typically single-instance â€” make them HA yourself (leader lock) or they SPOF.
- **Quartz (JVM):** a scheduler library with clustered mode (DB-backed) for HA
  cron and misfire handling.
- **Airflow / Dagster / Prefect:** DAG orchestrators for batch pipelines â€”
  dependencies, backfill, run history, retries per task. Heavier; scheduler
  latency makes them wrong for low-latency or high-rate tiny jobs.
- **Temporal / durable workflows:** when the *orchestration* (multi-step, retries,
  timers, compensation) is the hard part â€” see `providers/temporal.md` and
  `messaging-streaming`.

## Common mistakes

- Visibility timeout shorter than the job â†’ healthy jobs re-run constantly.
- No heartbeat on long jobs â†’ either re-runs (short timeout) or slow recovery
  (long timeout); heartbeats give both.
- Treating a leased task as "ran once" â€” at-least-once requires idempotent tasks.
- Running the scheduler/beat in HA without a leader lock â†’ split-brain double-fire.
- Strict priority with no aging/fairness â†’ low-priority or one tenant starves.
- Far-future delayed jobs parked in a hot queue instead of a store.

