---
name: documentation
description: >
  A 3-layer documentation architecture system (Business / Architecture / Implementation)
  for software projects. Use this skill whenever you need to: initialize a documentation
  structure for a new project, restructure fragmented documentation, classify a document
  into the correct layer, advise on the Single Source of Truth principle, or establish
  architecture guardrails to prevent AI Coding Agents from hallucinating or destroying existing system invariants.
  Trigger keywords: "doc structure", "docs", "architecture doc", "PRD", "SRS", "TDD",
  "ADR", "BRD", "roadmap", "restructure docs", "document layer", "where does this doc go", "backlog structure".
---

# SKILL: PROJECT DOCUMENTATION ARCHITECTURE SYSTEM (AGENT-SAFE EDITION)

> **Skill Type:** Documentation Architecture & System Invariant Protection  
> **Version:** 2.2  
> **Status:** Active  
> **Audience:** Product Owner, Business Analyst, System Architect, Technical Lead, AI Coding Agent, Fullstack Engineer

---

## 1. Purpose & The "Agent Amnesia" Problem

This skill defines the definitive standard for organizing, structuring, and maintaining documentation across the software lifecycle. It solves two critical failure modes in modern software engineering with AI Agents:

1. **Human & Project Scale Failures:**
   - **Documentation fragmented by Release** — each release writes its own architecture notes, causing contradictions and dead documentation.
   - **No Single Source of Truth** — technical decisions are scattered across chat logs, PRs, and outdated wiki pages.
   - **Slow Onboarding** — new engineers and architects cannot find the current state of truth.

2. **AI Agent Amnesia & System Destruction (Critical):**
   - In medium to large projects, AI Coding Agents have limited context windows and quickly suffer from **Context Rot / Amnesia** (forgetting existing architectural patterns, database schemas, security guards, and design principles).
   - When given a task with incomplete context, an unconstrained Coding Agent often implements localized hacks, changes existing table structures, bypasses authentication middleware, or rewrites functional modules — **effectively destroying the system**.
   - **The Solution:** A strict 3-layer architecture where **Architecture is the immutable Single Source of Truth**, and every **Implementation Story provides mandatory guardrails linking back to the Architecture Layer**.

---

## 2. Core Philosophy — The 3 Independent Layers

All project documentation is strictly divided into **3 independent layers** with zero overlapping responsibilities:

```
┌─────────────────────────────────┐
│         BUSINESS LAYER          │  ← Product goals, vision, KPIs (Slow moving)
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│       ARCHITECTURE LAYER        │  ← The Single Source of Truth & System Invariants (Living system)
└────────────────┬────────────────┘     ⛔ NEVER divided by Release!
                 │
┌────────────────▼────────────────┐
│      IMPLEMENTATION LAYER       │  ← Delivery docs: PRD, Backlog, Stories, AC, Tech Design
└─────────────────────────────────┘     ✅ Organized per Release / Sprint
```

**Golden Rule:** When deciding where a document or diagram belongs, ask:  
*"Does this describe a BUSINESS GOAL, a SYSTEM INVARIANT/DESIGN, or a DELIVERY IMPLEMENTATION?"*

---

## 3. Business Layer (`docs/business/`)

### Role
Describes **what the system must achieve and why**, completely independent of technology choices. Documents in this layer change only when business strategy pivots.

### Directory Structure
```
docs/business/
    brd.md            ← Business Requirement Document (Problem, Vision, KPIs, High-level Scope)
    roadmap.md        ← Product Roadmap by Horizon / Release
    glossary.md       ← Unified business & domain terminology
    stakeholders.md   ← Stakeholder register and decision authority
```

### Key Artifacts:
- **`brd.md`**: Persists across the entire project lifecycle. Defines problem statements, personas, ROI, success metrics (KPIs), and module boundaries.
  - *Does NOT describe:* API routes, SQL schemas, code, or low-level technical sequences.
- **`roadmap.md`**: Phased release strategy (Release 1, Release 2...) mapped to business capabilities.
- **`glossary.md`**: Ubiquitous Domain Language (prevents "Order", "Booking", "Transaction" from being conflated).

---

## 4. Architecture Layer (`docs/architecture/`)

### Role
This is the **Single Source of Truth** for the entire technical ecosystem. It establishes the **System Invariants** that no Coding Agent or developer is allowed to violate.

### Fundamental Principle
> ⛔ **The Architecture Layer must NEVER be divided by Release.**  
> There is no such thing as `architecture-release-1/` or `architecture-v2/`. There is only **ONE living Architecture set**, updated continuously as the system evolves.

### Directory Structure
```
docs/architecture/
    README.md                          ← Architecture Map & System Invariant Index
    │
    ├── [Backend & System Invariants]
    │   01-system-context.md           ← System boundary, actors, external systems (Use Case Boundary)
    │   02-high-level-architecture.md  ← Overall architecture style & high-level component diagrams
    │   03-service-architecture.md     ← Service breakdown, containers, responsibilities
    │   04-deployment-architecture.md  ← Docker, K8s, Cloud infra, reverse proxy, queues
    │   05-data-architecture.md        ← Database schemas, ERD, caching, object storage, data models
    │   06-ai-architecture.md          ← AI pipelines, LLM harnesses, vector stores, prompt registry
    │   07-security-architecture.md    ← Auth, RBAC, JWT, cookie policies, audit logs, secret management
    │   08-integration-architecture.md ← REST, WebSocket, events, 3rd party webhooks & gateways
    │   09-design-principles.md        ← Code standards, SOLID, Clean Architecture, Repository patterns
    │   10-folder-structure.md         ← Standard repository layout and module boundaries
    │
    ├── [Frontend & UI System]
    │   11-frontend-system-design.md   ← App router, rendering modes (SSR/CSR), route hierarchy
    │   12-design-system.md            ← Reusable component library specs (buttons, modals, tables)
    │   13-frontend-architecture.md    ← State management, React Query / SWR, data fetching
    │   14-design-language.md          ← Color tokens, typography scales, layout grids
    │
    └── adr/                           ← Architecture Decision Records
        ADR-001.md
        ADR-002.md
        ...
```

---

## 5. Implementation Layer (`docs/implementation/`)

### Role
This is the **Delivery Documentation Layer**. All feature specifications, sprint backlogs, detailed user stories, acceptance criteria, and feature-level technical designs belong here.

### Principle
> ✅ **The Implementation Layer IS organized by Release (or Milestone).**

### Standard Release Directory Structure
```
docs/implementation/
    release-1/
        prd.md                         ← Release PRD (Core capabilities, scope, KPIs for this release)
        srs.md                         ← Software Requirements Specification (Functional requirements)
        technical-design.md            ← Feature Sequence Diagrams, Activity Swimlanes, DB diffs
        migration.md                   ← Release-specific DB migration & breaking changes
        │
        ├── backlog/                   ← Delivery Backlog & Sprint Execution
        │   ├── {feature}-story-index.md  ← Backlog ledger: stories, priorities, AC coverage
        │   └── stories/
        │       ├── US-001.md          ← User Story with Given-When-Then AC & Architecture Guardrails
        │       ├── US-002.md
        │       └── ...
        │
        ├── api/                       ← API specs introduced/modified in this release
        │   └── v1.md
        ├── frontend/                  ← Screen specifications & mockup links for this release
        │   └── ui-spec.md
        └── qa/                        ← QA test plans & test cases
            └── test-cases.md
```

---

## 6. Architecture Guardrails & Agent Context Protection

To completely eradicate **Agent Amnesia and System Destruction**, the documentation system enforces the following two-way contract:

```
┌────────────────────────────────────────────────────────┐
│             ARCHITECTURE LAYER                         │
│  (Data Models, RBAC, Security, Patterns, Folders)      │
└───────────────────────────▲────────────────────────────┘
                            │
               Must cite    │ Imposes Invariants
               as invariant │ and Constraints
                            │
┌───────────────────────────┴────────────────────────────┐
│         IMPLEMENTATION STORY (US-xxx.md)               │
│  - User Story & Given-When-Then Acceptance Criteria    │
│  - SECTION 3: ARCHITECTURE GUARDRAILS FOR CODING AGENT │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ Reads story + cited architecture docs
                            ▼
               ┌────────────────────────┐
               │   AI CODING AGENT      │  → Generates clean, compliant code
               │                        │  → Zero architectural violations!
               └────────────────────────┘
```

### The Invariant Rules for Coding Agents:
1. **Never code from a naked prompt:** Coding Agents must never execute code changes based solely on a high-level user request. The request must be broken down into a User Story in `docs/implementation/{release}/backlog/stories/` or reference an existing design.
2. **Mandatory Architecture Citation in Stories:** Every `US-xxx.md` file MUST include a `## Architecture Guardrails` section explicitly referencing the relevant documents in `docs/architecture/`:
   - Data changes $\rightarrow$ Cite `05-data-architecture.md` (Do NOT alter existing columns or drop tables arbitrarily).
   - Auth/Access $\rightarrow$ Cite `07-security-architecture.md` (Must enforce existing RBAC policies).
   - Code Structure $\rightarrow$ Cite `09-design-principles.md` and `10-folder-structure.md` (Match existing patterns).
3. **Pre-execution Verification:** Before modifying code, the Coding Agent must verify that its proposed changes adhere to the cited architecture files.

---

## 7. Document Classification Matrix (Where Does It Go?)

| Artifact / Content | Originating Skill / Role | Correct Layer & Location |
|---|---|---|
| Business Problem, Vision, KPIs | `product-requirements` / BA | `docs/business/brd.md` |
| Release Roadmap & Horizons | BA / PO | `docs/business/roadmap.md` |
| Domain Terminology Glossary | BA / PO | `docs/business/glossary.md` |
| **System Boundary & Use Case Diagram** | `product-requirements` / BA | `docs/architecture/01-system-context.md` |
| High-level System Topology & Box-Arrow | `system-design` / `diagram-design` / Architect | `docs/architecture/02-high-level-architecture.md` |
| Service Boundaries & Decomposition | `system-design` / Architect | `docs/architecture/03-service-architecture.md` |
| Cloud Infrastructure & Deployment Topology | `system-design` / DevOps | `docs/architecture/04-deployment-architecture.md` |
| Global Database Schema, Sharding & Cache | `system-design` / `diagram-design` / Architect | `docs/architecture/05-data-architecture.md` |
| Security Policy & RBAC Matrix | Architect / SecLead | `docs/architecture/07-security-architecture.md` |
| Global API Standard, Envelope & Integration | `system-design` / `api-design-patterns` | `docs/architecture/08-integration-architecture.md` |
| Code Standards & Design Patterns | Tech Lead / Architect | `docs/architecture/09-design-principles.md` |
| Architecture Decision Record (ADR) | `system-design` / Architect | `docs/architecture/adr/ADR-XXX.md` |
| **Release PRD & Scope Definition** | `product-requirements` / BA | `docs/implementation/{release}/prd.md` |
| Detailed Functional Requirements (FR) | BA / Spec Writer | `docs/implementation/{release}/srs.md` |
| **Feature Sequence & Technical Design** | `system-design` / `diagram-design` / Tech Lead | `docs/implementation/{release}/technical-design.md` |
| **Backlog Story Index (Sổ cái Backlog)** | `user-story-ac-writer` / BA | `docs/implementation/{release}/backlog/{feature}-story-index.md` |
| **User Stories & Acceptance Criteria** | `user-story-ac-writer` / BA | `docs/implementation/{release}/backlog/stories/{us-id}.md` |
| Release API Endpoint Specs (7 Patterns) | `api-design-patterns` / Tech Lead | `docs/implementation/{release}/api/vX.md` |
| Release UI Specs & Wireframes | BA / Designer | `docs/implementation/{release}/frontend/ui-spec.md` |
| QA Test Plans & Test Cases | QA / QC | `docs/implementation/{release}/qa/test-cases.md` |
| DB Migrations & Breaking Changes | Dev / DBA | `docs/implementation/{release}/migration.md` |

---

## 8. Integration with Upstream & Downstream Skills

### 1. `product-requirements` Integration:
- Inception / Project Kickoff: Generates `docs/business/brd.md` and updates `docs/architecture/01-system-context.md` with the System Boundary & Use Case Diagram.
- Release Specification: Outputs the feature PRD to `docs/implementation/{release}/prd.md` (or `features/{feature}-prd.md`).

### 2. `diagram-skills-package` / `diagram-design` Integration:
- Scope & Context Diagrams $\rightarrow$ updates `docs/architecture/01-system-context.md`.
- Architecture Diagrams (`/d2-architect`) $\rightarrow$ updates `docs/architecture/02-high-level-architecture.md`.
- Global ERD (`/erd`, `/d2-erd`, `/dbdiagram`) $\rightarrow$ updates `docs/architecture/05-data-architecture.md`.
- Feature Workflows & Sequences (`/sequence`, `/activity-swimlane`, `/bpmn`) $\rightarrow$ embedded into `docs/implementation/{release}/technical-design.md`.

### 3. `user-story-ac-writer` Integration:
- Reads the Release PRD, SRS, and Technical Design.
- Outputs the backlog ledger to `docs/implementation/{release}/backlog/{feature}-story-index.md`.
- Outputs individual user stories with Given-When-Then AC and Architecture Guardrails to `docs/implementation/{release}/backlog/stories/{us-id}.md`.

### 4. `system-design` Integration:
- Inception / System Architecture Planning: Takes requirements from `product-requirements` (BRD/PRD), executes the 6-Step Reasoning Loop (Clarify $\rightarrow$ BOTEC Scale $\rightarrow$ High-Level Design $\rightarrow$ Trade-offs $\rightarrow$ Failure Modes $\rightarrow$ Deep Dive), and updates:
  - `docs/architecture/02-high-level-architecture.md` (System topology & component interactions)
  - `docs/architecture/03-service-architecture.md` (Microservices/monolith boundaries, gateway)
  - `docs/architecture/04-deployment-architecture.md` (Cloud infrastructure mapping: AWS, GCP, Azure)
  - `docs/architecture/05-data-architecture.md` (Data models, sharding keys, caching topologies)
  - `docs/architecture/adr/ADR-XXX.md` (Major trade-off decisions using the *Solves / Worsens / Change it when* framework)
- Release-Scoped Feature Architecture: Outputs the subsystem technical architecture to `docs/implementation/{release}/technical-design.md`.
- Handoff Contract: Produces an **API Surface Summary** (Context, Endpoints, Constraints, Caching, Protocols) and hands off to `api-design-patterns`.

### 5. `api-design-patterns` Integration:
- Consumes the API Surface Summary produced by `system-design`.
- Applies the 7 essential REST patterns (Versioning, Pagination, Filtering, Field Selection, Expansion, Async 202, Consistent Response Envelope).
- Outputs system-wide API standards and envelope formats to `docs/architecture/08-integration-architecture.md`.
- Outputs feature-specific endpoint specifications to `docs/implementation/{release}/api/vX.md`.

---

## 9. Complete Master Directory Structure

```
docs/
│
├── business/                          ← BUSINESS LAYER
│   ├── brd.md                         ← Business goals, problem, ROI, KPIs
│   ├── roadmap.md                     ← Phased delivery roadmap
│   ├── glossary.md                    ← Ubiquitous terminology
│   └── stakeholders.md                ← RACI & stakeholder matrix
│
├── architecture/                      ← ARCHITECTURE LAYER (Single Source of Truth)
│   ├── README.md                      ← Navigation map & invariant summary
│   │
│   ├── 01-system-context.md           ← System boundary & Use Case scope diagrams
│   ├── 02-high-level-architecture.md  ← System architecture topology
│   ├── 03-service-architecture.md     ← Services, containers, processes
│   ├── 04-deployment-architecture.md  ← Infrastructure, Docker, Cloud, Network
│   ├── 05-data-architecture.md        ← Global Database schema, ERD, Cache
│   ├── 06-ai-architecture.md          ← AI pipelines, models, agents
│   ├── 07-security-architecture.md    ← Auth, RBAC, Data privacy, tokens
│   ├── 08-integration-architecture.md ← Third-party APIs, webhooks, events
│   ├── 09-design-principles.md        ← SOLID, Clean Code, Repository pattern
│   ├── 10-folder-structure.md         ← Repository directory invariants
│   │
│   ├── 11-frontend-system-design.md   ← Routing hierarchy, layout engine
│   ├── 12-design-system.md            ← Component library documentation
│   ├── 13-frontend-architecture.md    ← State management & data fetchers
│   ├── 14-design-language.md          ← Design tokens, colors, typography
│   │
│   └── adr/                           ← Architectural Decision Records
│       ├── ADR-001.md
│       └── ADR-NNN.md
│
└── implementation/                    ← IMPLEMENTATION LAYER
    ├── release-1/
    │   ├── prd.md                     ← Release scope & feature specs
    │   ├── srs.md                     ← Detailed functional specifications
    │   ├── technical-design.md        ← Feature Sequence & Activity Swimlanes
    │   ├── migration.md               ← DB schema migration scripts & breaking changes
    │   │
    │   ├── backlog/                   ← Sổ cái & Danh mục User Stories
    │   │   ├── {feature}-story-index.md
    │   │   └── stories/
    │   │       ├── US-001.md          ← User Story + AC + Architecture Guardrails
    │   │       ├── US-002.md
    │   │       └── ...
    │   │
    │   ├── api/
    │   │   └── v1.md
    │   ├── frontend/
    │   │   └── ui-spec.md
    │   └── qa/
    │       └── test-cases.md
    │
    └── release-N/
        └── ...
│
└── views/                             ← VISUAL VIEWS (Standalone HTML artifacts)
    ├── README.md                      ← Directory index & rendering instructions
    └── {feature-or-system}-view.html  ← On-demand HTML diagrams, dashboards, interactive views
```

---

## 10. Pure Markdown Standard & Centralized Visual Views (`docs/views/`)

To keep documentation clean, reviewable in pull requests, and maintainable across long-term projects, all documentation and visual views adhere to a strict separation of concerns:

### 10.1. Pure Markdown Invariant for Core Documentation
- All files residing within `docs/business/`, `docs/architecture/`, and `docs/implementation/` **MUST be written in pure Markdown (`.md`)**.
- **Embedded Diagrams:** Represent all internal diagrams, sequences, flowcharts, data flows, and state machines using standard **Mermaid syntax** (`flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`, `erDiagram`) or clean Markdown tables.
- **Strictly Prohibited in Core Docs:**
  - NO inline HTML tags (`<script>`, `<canvas>`, `<style>`, raw `<div>`, inline `<svg>` blocks).
  - NO inline base64 image strings.
  - NO raw SVG or PNG file dumps cluttering documentation folders.

### 10.2. Centralized HTML Views Folder (`docs/views/`)
- When rich, interactive, styled, or canvas-rendered views are desired (e.g. standalone interactive HTML architecture diagrams, system dashboards, interactive flowcharts, UI mockups), they **MUST be placed exclusively in `docs/views/`**.
- Core Markdown documentation can cleanly reference these views via standard Markdown links:
  ```markdown
  > [!NOTE]
  > For an interactive visual representation of this topology, see [System Topology View](../../views/02-system-topology-view.html).
  ```

### 10.3. On-Demand Generation Only
- **Zero Automatic HTML Overhead:** Analytical and documentation skills (`product-requirements`, `system-design`, `api-design-patterns`, `documentation`, `user-story-ac-writer`) **NEVER** generate HTML views automatically during routine analysis or documentation tasks.
- HTML views in `docs/views/` are generated **ONLY upon explicit user request** (e.g., "vẽ HTML view cho kiến trúc này", "tạo bản đồ tương tác", "export giao diện trực quan").

### 10.4. Delegation to Specialist Visual Skills
Analysis and design skills do not contain internal HTML rendering engines. When the user requests an HTML visual view:
1. The Agent reads the source Markdown document from `docs/` as the single source of truth.
2. The Agent invokes the dedicated visual specialist skill suited for the artifact:
   - **`diagram-design`**: Branded architecture, cloud topology, sequence, flowchart, ERD, and C4 diagrams.
   - **`html-diagram`**: Self-contained interactive HTML diagrams with notation, zoom/pan controls, and layer toggles.
   - **`design-artifact` / `html`**: Interactive dashboards, landing pages, technical reports, and presentations.
   - **`html-prototype` / `html-wireframe`**: Interactive mockups and low-fidelity wireframes.
   - **`html-plan`**: Visual project roadmaps, phased plans, and dependency timelines.
3. The generated standalone file is saved to `docs/views/{name}.html`.

---

## 11. Summary Checklist for Engineering Teams & Agents

- [ ] **Layer Integrity:** No implementation details (APIs, SQL migrations) in `business/` or `architecture/`.
- [ ] **No Architecture per Release:** All technical invariants live in `docs/architecture/` and are updated in-place.
- [ ] **Pure Markdown:** All core documentation files in `business/`, `architecture/`, and `implementation/` use pure Markdown and standard Mermaid; no inline HTML or binary clutter.
- [ ] **Centralized Views:** Standalone HTML visual views reside strictly in `docs/views/` and are generated on-demand only.
- [ ] **Agent Guardrails Active:** Every story in `docs/implementation/{release}/backlog/stories/` cites specific architecture files to constrain Coding Agents.
- [ ] **Single Source of Truth:** If an architecture pattern changes, an ADR is filed and the relevant `01-14` document is updated immediately.
