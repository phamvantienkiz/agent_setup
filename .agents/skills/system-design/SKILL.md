---
name: system-design
description: Use when designing system architecture, APIs, components, or data models. Triggers on architecture planning, API specification, component design, database schema, or any technical design discussion — even if the user doesn't explicitly say "system design." Always use this skill when the user wants to think through how a system should be structured, what interfaces it should expose, how data flows between components, or how to scale a service. Also triggers on scalability questions, CAP theorem trade-offs, caching strategy, load balancing, message queues, or any "how should I design X" question.
---

# System Design

## Overview

Guide the creation of clear, well-structured system designs across architecture, APIs, components, and data models. Produces explicit requirements, constraint analysis, validation steps, and documentation artifacts.

## When to Use

- Designing system architecture or individual components
- Specifying APIs (REST, GraphQL) or data models
- Planning scalability, reliability, or performance strategies
- Producing design documents or architectural diagrams
- Evaluating trade-offs (SQL vs NoSQL, sync vs async, caching strategies)

**Do not use** for pure implementation tasks — use an implementation workflow instead.

---

## Behavioral Workflow

### 1. Analyze

Examine the target requirements and any existing system context. Ask clarifying questions if constraints are unclear. Key questions to always address:

- **Data flow** — How do components communicate?
- **Storage** — Where does data live, and how does it scale?
- **Retrieval speed** — What caching strategy is needed?
- **Reliability** — How does the system survive failures?
- **Scalability** — How does the system grow under load?

### 2. Plan

Define the design approach and structure. Choose the right design type:

| Design Type  | Key Concern                                   |
| ------------ | --------------------------------------------- |
| Architecture | Component relationships, scalability patterns |
| API          | Interface contracts, REST/GraphQL trade-offs  |
| Component    | Functional boundaries, interface design       |
| Database     | Schema design, relationship modeling          |

### 3. Design

Produce comprehensive specifications applying industry best practices. Cover all relevant layers — compute, storage, network, and integration.

### 4. Validate

Check the design against:

- Stated requirements and constraints
- Maintainability and operability standards
- Known anti-patterns (see Common Mistakes below)

### 5. Document

Generate clear design documentation. Save the architecture document to:

```
docs/product/{feature-name}-architecture.md
```

Deliver diagrams, specs, and validation notes as appropriate.

**If the design includes APIs**, also produce an **API Surface Summary** (see format below) before handing off to the `api-design-patterns` skill at `@.agents/skills/api-design-pattern.md`. Do not detail the API further here — that is the responsibility of the next skill.

### 6. API Handoff (conditional)

_Only applies when the system design exposes one or more APIs._

After saving the architecture document, produce an API Surface Summary and invoke the `api-design-patterns` skill at file `@.agents/skills/api-design-pattern.md` to expand it into `docs/product/{feature-name}-api.md`.

**API Surface Summary format:**

```markdown
## API Surface Summary — {feature-name}

### Context

- System: {brief description}
- Consumers: {who calls this API — mobile app, third-party, internal service, etc.}
- Protocol: {REST | GraphQL}
- Auth: {JWT | API Key | OAuth2 | None}

### Endpoints

| Method | Path               | Description         | Notes                              |
| ------ | ------------------ | ------------------- | ---------------------------------- |
| GET    | /v1/resources      | List resources      | Large collection, needs pagination |
| GET    | /v1/resources/{id} | Get single resource | May expand related entities        |
| POST   | /v1/resources      | Create resource     | Validate input fields              |
| PUT    | /v1/resources/{id} | Update resource     | Partial update acceptable          |
| DELETE | /v1/resources/{id} | Delete resource     | Soft delete preferred              |

### Data Contracts

{List the primary request/response entities — field names, types, required/optional.}

### Known Constraints

- {e.g. Some endpoints trigger long-running jobs → async pattern required}
- {e.g. Mobile clients need minimal payloads → field selection required}
- {e.g. Dataset can reach millions of rows → cursor pagination required}
```

Once the summary is written, explicitly invoke the `api-design-patterns` skill with this summary as input. That skill will apply the 7 patterns (Versioning, Pagination, Filtering, Field Selection, Expansion, Async, Consistent Response) and produce the full API specification file.

---

## Core Concepts Reference

### Performance

- **Latency** — Time to process a single request; minimize for user-facing paths.
- **Throughput** — Requests handled per second; maximize for batch and async workloads.

### Scalability

- **Vertical scaling** — Upgrade the existing server's hardware.
- **Horizontal scaling** — Add more servers; preferred for distributed systems.

### CAP Theorem

Every distributed system must trade off between:

- **Consistency** — All nodes see the same data at the same time.
- **Availability** — Every request gets a response (possibly stale).
- **Partition Tolerance** — System continues operating despite network splits.

No system achieves all three simultaneously. Choose the pair that fits the use case.

### Availability Patterns

- **Active-Active** — All nodes serve traffic; higher throughput and fault tolerance.
- **Active-Passive** — Standby node takes over on failure; simpler but slower failover.

### Database Patterns

- **Master-Slave** — One write master, multiple read replicas; good for read-heavy workloads.
- **Master-Master** — Multiple write nodes; higher availability, more complex conflict resolution.

### System Optimization

| Technique                     | Purpose                                                            |
| ----------------------------- | ------------------------------------------------------------------ |
| CDN (Push/Pull)               | Serve static assets from nodes close to users; reduces latency     |
| Load Balancer (L4/L7)         | Distribute requests across servers (Round Robin, Least Connection) |
| Reverse Proxy                 | Hide internal topology; adds security and SSL termination          |
| Background Jobs               | Offload slow work via event-driven or scheduled processing         |
| Message Queue (e.g. RabbitMQ) | Decouple producers and consumers; improves reliability under load  |

### Caching Strategies

- **Cache Aside** — Application manages cache explicitly; flexible, requires cache-miss handling.
- **Write Through** — Writes go to cache and DB simultaneously; consistent but higher write latency.
- **Write Behind** — Writes go to cache first, DB asynchronously; faster writes, risk of data loss.

### API Design

- **REST** — Resource-based, stateless, widely supported; can suffer from over-fetching.
- **GraphQL** — Client-specified queries; solves over-fetching and N+1 queries, more complex to implement.

### SQL vs NoSQL

| Factor      | SQL                           | NoSQL                                            |
| ----------- | ----------------------------- | ------------------------------------------------ |
| Consistency | ACID guarantees               | Eventual consistency (usually)                   |
| Schema      | Fixed, structured             | Flexible, dynamic                                |
| Scaling     | Vertical (primarily)          | Horizontal                                       |
| Best for    | Relational data, transactions | High volume, unstructured, or fast-changing data |

---

## Common Mistakes to Avoid

- **Designing without constraints** — Always establish scale targets, SLAs, and budget before proposing solutions.
- **Mixing spec scope with implementation details** — Keep design documents at the interface and contract level.
- **N+1 Query problems** — Use eager loading or DataLoader patterns; address in both API and DB design.
- **Overusing synchronous calls** — Identify async opportunities early; don't bolt on queues after the fact.
- **Ignoring connection pool limits** — Plan DB and service connection budgets as part of capacity design.
- **No observability plan** — Every design should include monitoring, logging, and alerting strategy (CPU, RAM, error rates, DDoS detection).

---

## Thinking Modes (Personas)

- **Architect** — Focus on system structure, scalability patterns, and component relationships.
- **System Designer** — Focus on design principles, interface contracts, and specification clarity.

Apply both perspectives when validating a design.

---

## Output Artifacts

- **Architecture document** → `docs/product/{feature-name}-architecture.md`
- **Design diagrams** — Component diagrams, data flow diagrams, sequence diagrams as needed
- **Validation notes** — Trade-off analysis and open follow-up questions
- **API Surface Summary** _(conditional — only if APIs are present)_ → intermediate handoff artifact passed to `api-design-patterns` skill
- **API specification** _(conditional)_ → `docs/product/{feature-name}-api.md` — produced by `api-design-patterns` skill, not this skill

---

## Boundaries

**Will:**

- Produce comprehensive design specifications following industry best practices
- Generate multiple output formats (diagrams, specs, API contracts) based on requirements
- Validate designs against scalability, maintainability, and reliability standards
- Surface trade-offs clearly so decisions are explicit
- Produce an API Surface Summary and invoke `api-design-patterns` when APIs are present

**Will Not:**

- Write actual implementation code (use an implementation workflow for that)
- Modify an existing architecture without explicit design approval
- Produce designs that violate stated architectural constraints
- Write detailed API pattern documentation — that is delegated entirely to the `api-design-patterns` skill
