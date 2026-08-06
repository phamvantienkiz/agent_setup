---
name: documentation
description: >
  A 3-layer documentation architecture system (Business / Architecture / Implementation)
  for software projects. Use this skill whenever you need to: initialize a documentation
  structure for a new project, restructure fragmented documentation, classify a document
  into the correct layer, or advise on the Single Source of Truth principle.
  Trigger keywords: "doc structure", "docs", "architecture doc", "PRD", "SRS", "TDD",
  "ADR", "BRD", "roadmap", "restructure docs", "document layer", "where does this doc go".
---

# SKILL: PROJECT DOCUMENTATION ARCHITECTURE SYSTEM

> **Skill Type:** Documentation Architecture  
> **Version:** 2.0  
> **Status:** Active  
> **Audience:** Product Owner, Business Analyst, System Architect, Technical Lead, AI Engineer, Backend Engineer, Frontend Engineer

---

## 1. Purpose

This skill defines the standard for organizing and managing documentation across the entire software development lifecycle. It solves the following common problems:

- **Documentation fragmented by Release** — each Release creates its own Architecture set, leading to conflicts and duplication.
- **No Single Source of Truth** — the same technical decision is documented in multiple places with inconsistent content.
- **Difficult onboarding** — new team members must read dozens of scattered documents to understand the system.
- **AI Agents retrieving wrong information** — no consistent structure causes AI to index outdated documents.

---

## 2. Core Philosophy — 3 Documentation Layers

All documentation is divided into **3 independent layers** with no overlapping responsibilities:

```
┌─────────────────────────────────┐
│         BUSINESS LAYER          │  ← Product goals; rarely changes
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│       ARCHITECTURE LAYER        │  ← Single Source of Truth; evolves continuously with the system
└────────────────┬────────────────┘
                 │
┌────────────────▼────────────────┐
│      IMPLEMENTATION LAYER       │  ← Delivery documentation; organized per Release
└─────────────────────────────────┘
```

**Golden Rule:** When unsure where a document belongs, ask:  
*"Does this content describe a GOAL, a DESIGN, or an IMPLEMENTATION?"*

---

## 3. Business Layer

### Role

Describes **what the system must achieve**, not how to implement it. Documents in this layer have a very long lifespan and only change when the product strategy changes.

### Directory Structure

```
docs/business/
    brd.md            ← Business Requirement Document
    roadmap.md        ← Product Roadmap by Release
    glossary.md       ← Unified terminology glossary
    stakeholders.md   ← Stakeholder register
```

### 3.1 BRD (Business Requirement Document)

The single document that persists across the entire project lifecycle. BRD only answers:

| Question | Example |
|---|---|
| What problem does the system solve? | Digitize & extract metadata from administrative documents |
| Who are the users? | Clerical staff, Managers, Admins |
| What is the business value? | Reduce manual data entry time by 80% |
| What are the success KPIs? | Accuracy >= 95%, throughput >= 100 docs/hour |
| What modules does the Product Roadmap include? | OCR → Auth → Document Management → Archive |

**BRD does NOT describe:** API, Database schema, Folder structure, Sequence diagrams, Source code.

### 3.2 Roadmap

Describes the full development roadmap by Release. **Does not describe technical details.**

```
Release 1 — Metadata Extraction Core
    ↓
Release 2 — User Management & Authentication
    ↓
Release 3 — Document Management
    ↓
Release 4 — Digital Archive & Reporting
```

### 3.3 Glossary

A unified terminology reference for the entire project. Prevents "Task", "Document", "Job" from being used interchangeably across code, documentation, and communication.

### 3.4 Stakeholders

List of stakeholders, their roles, and decision-making authority.

---

## 4. Architecture Layer

### Role

This is the **most important and most stable** layer. Architecture is the **Single Source of Truth** for the entire technical system.

### Core Principle

> ⛔ **Architecture must NOT be divided by Release.**

There is no such thing as `Architecture Release 1` or `Architecture Release 2`. Only **one unified Architecture set** exists, updated continuously as the system evolves.

### Directory Structure

```
docs/architecture/
    README.md                          ← Architecture document map
    │
    ├── [Backend / System]
    │   01-system-context.md           ← System boundary, actors, external systems
    │   02-high-level-architecture.md  ← Overall architecture style (Layered / Microservice / ...)
    │   03-service-architecture.md     ← Details of each service / container
    │   04-deployment-architecture.md  ← Docker, Kubernetes, Nginx, GPU, ...
    │   05-data-architecture.md        ← Database, ERD, Cache, Object Storage
    │   06-ai-architecture.md          ← AI Pipeline, Model Registry, Inference
    │   07-security-architecture.md    ← Auth, RBAC, JWT, Audit Log
    │   08-integration-architecture.md ← REST, WebSocket, Queue, Events
    │   09-design-principles.md        ← SOLID, Clean Architecture, Patterns
    │   10-folder-structure.md         ← Repository structure
    │
    ├── [Frontend]
    │   11-frontend-system-design.md   ← Overall Frontend architecture
    │   12-design-system.md            ← UI Component Library
    │   13-frontend-architecture.md    ← State Management, Data Flow
    │   14-design-language.md          ← Color, Typography, Visual Philosophy
    │
    └── adr/
        ADR-001.md
        ADR-002.md
        ...
```

---

## 5. Role of Each Architecture Document

### README.md — Architecture Map

The entry point for the entire Architecture Layer. Includes:
- A table of all documents with short descriptions
- Reading guide by role (Developer, Architect, QA, AI Agent)
- Summary of ADR decisions

Contains no detailed content — navigation only.

---

### 01 — System Context

Describes the system at the Business level. Does not describe code or APIs.

```
User Browser
     ↓
Frontend (Next.js)
     ↓
API Gateway (Nginx)
     ↓
Backend API + Worker
     ↓
AI Services (OCR, LLM)
     ↓
Storage (DB, Object Storage, Cache)
     ↓
External Services
```

---

### 02 — High-Level Architecture

Describes the overall architecture style. This is the **least frequently changed** document.

Examples: Layered Architecture, Modular Monolith, Microservice, Event-Driven, Hexagonal.

---

### 03 — Service Architecture

Specifies all services and containers in the system. When a new service is added, **only update this document** — do not create a new Architecture set.

---

### 04 — Deployment Architecture

Describes how the system is deployed: Docker Compose, Kubernetes, VM, GPU Server, Nginx reverse proxy, Load Balancer, Redis, RabbitMQ, MinIO, ...  
When deployment changes, only update this document.

---

### 05 — Data Architecture

Describes: Database (ERD, schema overview), Storage strategy, Object Storage, Cache, Search Index.  
**Does not describe SQL migrations** (migrations belong to the Implementation Layer).

---

### 06 — AI Architecture

Dedicated document for the AI subsystem. Includes:

- Full AI Pipeline
- Model Registry & Engine Selection
- Inference flow (OCR → Layout → Extraction → Post-processing)
- Confidence Score strategy
- Dynamic model loading

---

### 07 — Security Architecture

Covers: Authentication strategy, Authorization (RBAC), JWT lifecycle, Cookie security, Audit Log, Secret Management, CORS policy.  
When adding new authentication features, only update this document.

---

### 08 — Integration Architecture

Describes all integration mechanisms: REST API, WebSocket, Message Queue, Event streaming, External APIs.

---

### 09 — Design Principles

Defines the "law" of the project: SOLID, Clean Architecture, Repository Pattern, Factory Pattern, Dependency Injection, Domain-Driven Design (if applied), Pull-based Backpressure, etc.

---

### 10 — Folder Structure

Defines the standard repository structure. **Not divided by Release.**

```
frontend/
backend/
ai/
infra/
shared/
scripts/
docs/
```

---

### 11 — Frontend System Design

The overall architecture of the user interface layer:

- Framework & rendering strategy (SSR / CSR / ISR)
- App Router structure & routing hierarchy
- Auth Guard & Session management pattern
- Data flow diagram: Browser → Component → Hook → API Gateway

This is the **Single Source of Truth** for the entire Frontend system design. Update it when adding new pages or changing routing.

---

### 12 — Design System

The standardized UI Component Library of the project:

- List of reusable components (Button, Modal, Input, Select, Badge, ...)
- Component construction patterns (props, variants, accessibility)
- Usage rules — do not arbitrarily override styles inline
- A component is promoted to the Design System when reused across 2+ screens

---

### 13 — Frontend Architecture

Frontend source code structure and key technical mechanisms:

- State management strategy (Custom Hook, Context, Zustand, Redux, ...)
- Data fetching pattern (polling, SWR, React Query, ...)
- Performance optimization (caching, lazy loading, code splitting)
- Data flow: Component → Hook → API Client → Backend

---

### 14 — Design Language

The unified visual design language across the entire system:

- Design philosophy (Glassmorphism, Bento Grid, Flat, Material, ...)
- Color palette & semantic color tokens (Primary, Success, Warning, Error)
- Typography (font family, scale, line-height)
- Spacing & layout grid
- Dark/Light mode switching strategy
- Micro-animation principles

---

## 6. Architecture Decision Record (ADR)

### Role

Records the **history of architectural decisions** made in the project. Each ADR captures **exactly one decision**.

```
docs/architecture/adr/
    ADR-001.md    ← Use FastAPI instead of Django
    ADR-002.md    ← Use ONNX Runtime instead of PyTorch
    ADR-003.md    ← Apply RLS for Queue Isolation
    ...
```

### ADR Template

```markdown
# ADR-XXX: [Decision Title]

**Status:** Accepted | Superseded by ADR-YYY | Deprecated

## Context
[Describe the background and the problem that required a decision]

## Decision
[The decision that was made]

## Reason
[Why this solution was chosen]

## Alternatives Considered
[Other options that were evaluated]

## Trade-offs
[The trade-offs accepted by adopting this decision]
```

### ADR Rules

- **Never rewrite history** — if a decision changes, create a new ADR and mark the old one as `Superseded by ADR-XXX`.
- This allows tracking the **evolutionary history** of the system.

---

## 7. Implementation Layer

### Role

This is the **most frequently changing** layer. All documents describing how features are implemented within a specific delivery cycle belong here.

### Principle

> ✅ **The Implementation Layer IS allowed to be divided by Release.**

### Directory Structure

```
docs/implementation/
    release-1/
        prd.md
        srs.md
        technical-design.md
        migration.md
        api/
            v1.md
        frontend/
            ui-spec.md
        qa/
            test-cases.md

    release-2/
        prd.md
        srs.md
        technical-design.md
        migration.md
        api/
            v1.md
            v2.md        ← New API version introduced in this release
        frontend/
            ui-spec.md
        qa/
            test-cases.md
            regression.md

    release-n/
        ...
```

---

## 8. Role of Each Document Within a Release

### PRD (Product Requirements Document)

**Question answered:** *What features does this Release build?*

Describes: User Stories, Feature list, Acceptance Criteria, Out-of-scope.  
**Does not describe:** architecture, API endpoints, database schema.

---

### SRS (Software Requirements Specification)

Describes the detailed **functional requirements** for each feature in the Release.

Examples:
- Login / Logout / Refresh Token flow
- User CRUD operations
- Permission matrix per role

---

### Technical Design Document (TDD)

The detailed technical document for the Release, including:

- Sequence Diagrams for each use case
- Module & Class Design
- Database changes (schema changes, new indexes)
- API interaction flow
- Error handling strategy

> **Important note:** The TDD is where all "feature-specific implementation" content lives. Many teams mistakenly place this content in Architecture documents — that is incorrect. Architecture describes the overall design; it does not describe the processing flow of individual features.

---

### API Specification

APIs are versioned by **API Version**, not by Release.

```
api/
    v1.md    ← Endpoint definitions for API v1
    v2.md    ← Breaking changes, new endpoints, deprecations
```

**Do not name it** `API Release 2` — clients only care about API Version.

---

### Frontend Specification (`frontend/`)

UI/UX and interface design documentation for the Release:

- Wireframes or Figma links
- List of screens to implement in this Release
- New components to be added to the Design System
- UX edge cases

---

### QA

Test documentation per Release:

- Test Cases
- Regression Test plan
- Performance Test targets
- Security Test checklist

---

### Migration

Describes the changes required when upgrading to this Release:

- Database Migration (schema, data)
- API Breaking Changes & Deprecation notices
- Config / Environment variable changes

---

## 9. Documentation Update Rules

### When adding a new feature to a Release

Example: Adding **User Management** to Release 2.

```
✅ UPDATE (Architecture Layer):
   - 03-service-architecture.md     ← Add Auth Service if a new service is introduced
   - 07-security-architecture.md    ← Update RBAC model

✅ CREATE (Implementation Layer):
   - implementation/release-2/prd.md
   - implementation/release-2/srs.md
   - implementation/release-2/technical-design.md

⛔ DO NOT CREATE:
   - architecture/release-2/...    ← Completely wrong
```

---

### When changing architecture

Example: Migrating from **SQLite → PostgreSQL**.

```
✅ UPDATE:
   - 05-data-architecture.md
   - 04-deployment-architecture.md

✅ CREATE:
   - adr/ADR-007-migrate-to-postgresql.md

✅ ADD to Release:
   - implementation/release-3/migration.md

⛔ DO NOT CREATE:
   - architecture-v2/...    ← Completely wrong
```

---

### When changing the Frontend (new UI, new components)

Example: Adding a **Split-Screen Editor** in Release 3.

```
✅ UPDATE (Architecture Layer):
   - 11-frontend-system-design.md   ← Update routing diagram if a new page is added
   - 12-design-system.md            ← Add SplitScreenEditor to the Component Library
   - 13-frontend-architecture.md    ← Update if a new State management pattern is introduced

✅ CREATE (Implementation Layer):
   - implementation/release-3/frontend/ui-spec.md
```

---

### When business requirements change

Example: The client adds a **Knowledge Base** module.

```
✅ UPDATE:
   - business/brd.md
   - business/roadmap.md

⛔ DO NOT MODIFY:
   - SRS documents from completed Releases
```

---

## 10. Document Classification Reference

| Content | Layer | Specific Document |
|---|---|---|
| Business Goal, Product Vision | Business | `brd.md` |
| Product Roadmap | Business | `roadmap.md` |
| Project terminology | Business | `glossary.md` |
| Overall system architecture | Architecture | `02-high-level-architecture.md` |
| Deployment topology | Architecture | `04-deployment-architecture.md` |
| AI Pipeline | Architecture | `06-ai-architecture.md` |
| RBAC, Security model | Architecture | `07-security-architecture.md` |
| Frontend system design | Architecture | `11-frontend-system-design.md` |
| UI Component Library | Architecture | `12-design-system.md` |
| Frontend State & Data Flow | Architecture | `13-frontend-architecture.md` |
| Color tokens, Typography | Architecture | `14-design-language.md` |
| Strategic technical decisions | Architecture | `adr/ADR-XXX.md` |
| User Story, Feature list | Implementation | `release-N/prd.md` |
| Functional requirements | Implementation | `release-N/srs.md` |
| Sequence diagram (feature-level) | Implementation | `release-N/technical-design.md` |
| Endpoint definitions | Implementation | `release-N/api/vX.md` |
| UI screen spec, Wireframes | Implementation | `release-N/frontend/ui-spec.md` |
| Test Cases, Regression | Implementation | `release-N/qa/` |
| DB Migration, Breaking Changes | Implementation | `release-N/migration.md` |

---

## 11. Complete Directory Structure

```
docs/
│
├── business/
│   ├── brd.md
│   ├── roadmap.md
│   ├── glossary.md
│   └── stakeholders.md
│
├── architecture/
│   ├── README.md
│   │
│   ├── 01-system-context.md
│   ├── 02-high-level-architecture.md
│   ├── 03-service-architecture.md
│   ├── 04-deployment-architecture.md
│   ├── 05-data-architecture.md
│   ├── 06-ai-architecture.md
│   ├── 07-security-architecture.md
│   ├── 08-integration-architecture.md
│   ├── 09-design-principles.md
│   ├── 10-folder-structure.md
│   │
│   ├── 11-frontend-system-design.md
│   ├── 12-design-system.md
│   ├── 13-frontend-architecture.md
│   ├── 14-design-language.md
│   │
│   └── adr/
│       ├── ADR-001.md
│       ├── ADR-002.md
│       └── ADR-NNN.md
│
├── implementation/
│   ├── release-1/
│   │   ├── prd.md
│   │   ├── srs.md
│   │   ├── technical-design.md
│   │   ├── migration.md
│   │   ├── api/
│   │   │   └── v1.md
│   │   ├── frontend/
│   │   │   └── ui-spec.md
│   │   └── qa/
│   │       └── test-cases.md
│   │
│   ├── release-2/
│   │   ├── prd.md
│   │   ├── srs.md
│   │   ├── technical-design.md
│   │   ├── migration.md
│   │   ├── api/
│   │   │   ├── v1.md
│   │   │   └── v2.md
│   │   ├── frontend/
│   │   │   └── ui-spec.md
│   │   └── qa/
│   │       ├── test-cases.md
│   │       └── regression.md
│   │
│   └── release-N/
│       └── ...
│
└── ai/                            ← (optional) Documents generated by AI Agents
    ├── architecture-review.md
    └── session-summary.md
```

---

## 12. File Naming Conventions

| Rule | Correct Example | Incorrect Example |
|---|---|---|
| Architecture: 2-digit prefix + kebab-case | `11-frontend-system-design.md` | `frontend_system_design.md` |
| ADR: `ADR-` prefix + 3-digit number + kebab-case | `ADR-007-migrate-to-postgresql.md` | `adr7.md` |
| Implementation: standard name only, no Release number | `prd.md`, `srs.md` (inside `release-2/`) | `prd-release-2.md` |
| API: version number only, not Release number | `v1.md`, `v2.md` | `api-release-2.md` |

---

## 13. Skill Usage Guide

### When initializing documentation for a new project

1. Create the `docs/business/`, `docs/architecture/`, and `docs/implementation/` structure from the template in **Section 11**.
2. Start with `business/brd.md` — define goals and scope before writing any technical documents.
3. Write `architecture/README.md` as the navigation map.
4. Fill in architecture files `01` through `10` (backend/system). Add `11`–`14` if the project has a Frontend.
5. Create `implementation/release-1/` when the first sprint begins.

### When restructuring existing documentation

1. Inventory all existing documents.
2. Use the **Classification Reference (Section 10)** to map each document to the correct layer.
3. Move "feature-specific implementation" content (feature sequence diagrams, feature class designs) from Architecture documents into the corresponding `technical-design.md`.
4. Merge multiple Architecture sets that were split by phase/release into one unified Architecture set.
5. Create ADRs for significant architectural decisions that were already made.

### When an Agent needs to look up information

- **"What does the system do?"** → `business/brd.md`
- **"How is the system designed?"** → `architecture/`
- **"What does Release X build? What APIs does it expose?"** → `implementation/release-X/`
- **"Why was technology Y chosen?"** → `architecture/adr/`
- **"How is component Z used?"** → `architecture/12-design-system.md`

---

## 14. Summary

Three documentation layers with clearly separated responsibilities:

| Layer | Description | When It Changes |
|---|---|---|
| **Business** | Product goals & scope | When product strategy changes |
| **Architecture** | Overall technical design (Single Source of Truth) | When the system technically evolves |
| **Implementation** | How features are built per Release | With every new Release |

This separation ensures:

- Documentation is **always consistent** — no duplication or contradictions across Releases.
- **AI Agents** retrieve accurate information and are not confused by outdated documents.
- **New team members** can understand the entire system through a single, unified Architecture set.
- **The architecture evolves naturally** without requiring a full documentation restructure every Release.
