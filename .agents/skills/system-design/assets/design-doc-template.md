# Design: <system name>

A write-up structured around the reasoning loop, so trade-offs and failure
behavior are first-class — not footnotes. Keep each section tight.

> ### 📁 Documentation Placement Guide (3-Layer Architecture)
> - **Global System Design (Living Invariants)**:
>   - §4 High-level design $\rightarrow$ `docs/architecture/02-high-level-architecture.md` & `03-service-architecture.md`
>   - §5 Data model & Caching $\rightarrow$ `docs/architecture/05-data-architecture.md`
>   - §6 Key decisions $\rightarrow$ File an ADR at `docs/architecture/adr/ADR-XXX-{title}.md`
>   - §3 API entry points $\rightarrow$ Hand off to `api-design-patterns` $\rightarrow$ `docs/architecture/08-integration-architecture.md`
>   - Standalone HTML Views (On-demand only) $\rightarrow$ `docs/views/{system}-view.html` (delegated to `diagram-design` / `html-diagram`)
> - **Release-Scoped Feature Design (Delivery Layer)**:
>   - Entire technical design $\rightarrow$ `docs/implementation/{release}/technical-design.md`
>   - Non-functional scope & BOTEC sizing $\rightarrow$ `docs/implementation/{release}/srs.md`
>   - Detailed API endpoints $\rightarrow$ Hand off to `api-design-patterns` $\rightarrow$ `docs/implementation/{release}/api/vX.md`

## 1. Problem & scope
Core functional requirements, key non-functional constraints, and explicit
out-of-scope. (See the requirements template.)

## 2. Scale estimates
Peak read/write QPS, storage/day and /year, bandwidth, working set. State the
assumptions behind each number. What the numbers force (sharding? caching?
queues?).

## 3. API (entry points)
The core endpoints with concrete request/response shapes, pagination, and
idempotency where it matters. Vague boxes become real here.

## 4. High-level design
A diagram of components and data flow — render it using standard Mermaid syntax (`flowchart TD` / `flowchart LR`).
For each component, one line: *what requirement or number it satisfies.* Add nothing that isn't earning its place.

> [!NOTE]
> Standalone interactive HTML visual views are generated on-demand only in `docs/views/{system}-view.html` via specialist visual skills (`diagram-design`, `html-diagram`).

## 5. Data model
Stores chosen (and why — SQL/NoSQL), primary/sort keys, indexes, and the
partition/shard key with its access patterns.

## 6. Key decisions & trade-offs
For each major choice, a row: **solves / worsens / when I'd change it.** Name the
breaking point of the design.

| Decision | Solves | Worsens | Change it when |
|---|---|---|---|
| | | | |

## 7. Failure modes & degradation
SPOFs, the degradation story per dependency (fall back to cache / partial / hide),
and recovery without stampede. What the user experiences during each failure.

## 8. Scale evolution
The current bottleneck, and what changes at the next order of magnitude (10×/100×).
What metric signals it's time to evolve.

## 9. Open questions
Assumptions to confirm; things deferred for time.

---
### Validation (fill-in gate — check before sharing)
- [ ] Every row in §6 Key decisions has a **non-empty "Worsens"** and a breaking point.
- [ ] §2 estimates carry **units** and state their assumptions.
- [ ] §7 names a **degradation path** for each critical dependency (not just "retry").
- [ ] Each component in §4 ties to a **requirement or number** in §1–§2 (nothing unjustified).
- [ ] The coverage sweep ran: media / IDs / search / logs / SLOs each addressed **or explicitly deferred**.
