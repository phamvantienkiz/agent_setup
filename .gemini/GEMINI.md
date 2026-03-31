# Gemini AI Configuration

## Project Overview

This project uses Gemini AI as an intelligent agent to assist with development tasks.

## Core Instructions

- Always follow the rules defined in `.gemini/rules/`
- Use available commands from `.gemini/commands/` for common tasks
- Leverage skills from `~/skills/` for specialized operations
- Coordinate with sub-agents in `.gemini/agents/` for complex workflows

## Mandatory Rules

All rules in `.gemini/rules/` are **mandatory** and must be followed at all times:

### Code Quality

- `clean-code.md` — Clean Code principles (variables, functions, SOLID, concurrency)
- `code-style.md` — Formatting and naming style guide
- `error-handling.md` — Error classes and global handler patterns

### Architecture & Design

- `tech-stack.md` — Approved technologies (Next.js, PG, Redis, Prisma, BullMQ, docs)
- `system-design.md` — System design patterns (CAP, caching, scaling, queues)
- `project-structure.md` — Folder organization and layered architecture
- `api-conventions.md` — REST API design standards

### Data & Naming

- `naming-conventions.md` — Cache keys, DB identifiers, queues, events, env vars
- `database.md` — Query patterns, transactions, migrations

### Operations

- `security.md` — Security requirements (CRITICAL — never violate)
- `monitoring.md` — Logging, metrics (Prometheus), Grafana dashboards, alerting
- `testing.md` — Test coverage standards and patterns
- `git-workflow.md` — Git branching strategy and commit format

## Available Commands

- `deploy` — Deploy the application
- `fix-issue` — Analyze and fix a reported issue
- `review` — Perform a code review

## Available Agents

Specialized sub-agents in `.gemini/agents/`. Invoke the right agent for each task:

| Agent              | File                          | When to Invoke                                           |
| ------------------ | ----------------------------- | -------------------------------------------------------- |
| Frontend Developer | `agents/frontend.md`          | Components, pages, routing, state, performance           |
| Backend Developer  | `agents/backend-fastapi.md`   | APIs, services, DB queries, background jobs              |
| Project Manager    | `agents/project-manager.md`   | User stories, sprint planning, status reports            |
| Systems Architect  | `agents/systems-architect.md` | Architecture decisions, ADRs, system design, scalability |
| UI/UX Designer     | `agents/ui-ux-designer.md`    | Design system, wireframes, UX patterns, accessibility    |
| QA Engineer        | `agents/qa.md`                | Test plans, writing tests, bug reports, coverage         |
| Copywriter/SEO     | `agents/copywriter-seo.md`    | Page copy, microcopy, meta tags, SEO optimization        |

## Agent Behavior

- Be proactive in identifying potential issues
- Always explain changes before making them
- Prefer incremental changes over large rewrites
- Test assumptions before acting
