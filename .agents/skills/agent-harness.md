---
name: agent-harness
description: >
  Use this skill when designing, building, or debugging long-running AI Agent
  systems for enterprise use — especially when agents need to run across
  many turns without breaking, remember context across sessions, stay safe
  by not taking irreversible actions, and know when to stop and ask a human.
  Trigger when the user mentions: "harness", "agent loop", "context management",
  "session persist", "multi-turn agent", "long-running agent", "AI agent
  production", "agent forgets", "agent crashes", "tool registry", "sub-agent",
  "lifecycle hook", "agentic system", "agent for customer service", "agent for
  HR", "agent for finance", "agent for operations", or any request to build a
  durable, domain-agnostic AI agent system for enterprise end users (as opposed
  to simple chatbots or one-shot agents).
---

# Agent Harness Skill

This skill guides the design and construction of an **Agent Harness** — the
framework wrapping an AI Agent so it runs reliably in enterprise environments:
surviving long sessions, remembering past work, protecting systems from
irreversible mistakes, and knowing when to pause for human input.

> **Harness ≠ Chatbot.** A chatbot responds and forgets. An Agent Harness
> remembers, recovers, enforces permissions, and orchestrates — across sessions,
> across days, serving end users who never see the underlying infrastructure.

---

## Who Uses This

**End users** are typically non-technical: staff in HR, finance, operations,
customer service, or customers themselves — interacting through a web UI, mobile
app, or chat interface. They don't know what a "tool call" is. They expect the
agent to just work, like a capable colleague.

**Builders** are the engineers and product teams constructing the harness that
makes this experience possible.

This skill is written for builders, but every design decision should be
evaluated through the lens of the end user.

---

## Architecture Overview

A complete harness has **9 components**. The first two are mandatory; the
remaining seven are enhancement layers. Read each section in order when
designing from scratch, or jump to the relevant section when debugging.

```
┌──────────────────────────────────────────────────┐
│                    HARNESS                       │
│  ┌────────────┐  ┌──────────────────────────────┐│
│  │ While Loop │  │    Context Management        ││  ← REQUIRED
│  │            │  │    (keep / summarize / drop) ││
│  └────────────┘  └──────────────────────────────┘│
│  ┌───────┐ ┌───────────┐ ┌────────┐ ┌──────────┐ │
│  │ Tools │ │Sub-Agents │ │ Skills │ │ Session  │ │  ← ENHANCEMENT
│  └───────┘ └───────────┘ └────────┘ │ Persist  │ │
│  ┌────────────────┐ ┌───────┐ ┌─────┴────────┐ │ │
│  │ Prompt Assembly│ │ Hooks │ │  Permission  │ │ │
│  └────────────────┘ └───────┘ └──────────────┘ │ │
└──────────────────────────────────────────────────┘
```

---

## Component 1 — While Loop (REQUIRED)

**The foundation.** Every harness is a loop that calls the model repeatedly
until a stopping condition is met.

### Standard structure

```
messages = load_session()          # resume from storage if session exists

LOOP:
    response = call_model(messages)
    persist(response)              # save BEFORE acting on the response

    IF stop_reason == "end_turn"   → deliver result to user, exit loop
    IF stop_reason == "tool_use"   → execute tools, append results, continue
    IF stop_reason == "max_tokens" → compress context, continue
    IF stop_reason == other        → handle or escalate to human
```

### Invariants

- **One place calls the model.** Never scatter model calls across the codebase.
- **Each iteration = one decision.** The model receives the full history,
  reasons, then issues one next action (tool call or final answer).
- **Persist before acting on the response.** A crash mid-execution means the
  session resumes from a safe checkpoint, not from scratch.

### Common failure modes

| Failure                         | Effect on end user                          | Fix                                      |
| ------------------------------- | ------------------------------------------- | ---------------------------------------- |
| Model called in multiple places | Agent behaves inconsistently, hard to audit | Centralize into one function             |
| No persist after each turn      | User loses all progress on crash            | Flush + fsync immediately after append   |
| `max_tokens` unhandled          | Agent silently stops mid-task               | Detect, compress context, continue       |
| No turn limit                   | Infinite loop, runaway cost                 | Cap at N turns; escalate to human if hit |

---

## Component 2 — Context Management (REQUIRED)

**Context is working memory.** Mismanage it and the agent forgets what it was
doing, hallucinates, or hits token limits mid-task.

### Three-tier strategy

```
KEEP                    SUMMARIZE                    DROP
──────────────          ─────────────────────────    ──────────────────
Recent turns            Old completed task blocks    Verbose tool output
Tool results            Key decisions made           Failed attempts (resolved)
Key decisions           Domain-specific state        Duplicate or redundant calls
Unresolved errors       (e.g. "customer approved X")
User preferences
```

### Practical thresholds

- **Keep intact:** the last 5–10 turns + any unresolved error context.
- **Summarize when:** a task block is marked DONE, or context exceeds 70% of
  the token limit.
- **Drop immediately:** raw verbose output from successful tool calls once the
  result has been acknowledged.

### Summary prompt template

When the model needs to compress an older block:

```
Summarize what happened in this conversation segment in AT MOST 3 lines.
Keep: important decisions made, key outcomes, unresolved issues.
Omit: intermediate reasoning, verbose output, resolved failed attempts.
Preserve any user preferences or domain-specific facts that will matter later.
```

---

## Component 3 — Tools & Skills Registry

**Tool = what the agent can do. Skill = how to do it well in a given domain.**

### Three-tier architecture

```
Tool Primitives          Registry              Skill Guides (Markdown)
─────────────────   ←→  ──────────   ←→       ────────────────────────
search_web()             maps tool             customer_onboarding.md
send_email()             ↔ skill               expense_approval.md
read_document()          skill                 scheduling_workflow.md
update_record()          ↔ tool                document_summarization.md
call_api()
notify_user()
```

### Design principles

- **Tool**: short, atomic, no business logic. Does exactly one thing.
- **Skill**: explains _how_ to combine tools for a specific domain workflow,
  including the sequence of steps, what to check, and when to stop and ask.
- **Registry**: maps skill name → required tools + required permissions. The
  agent consults the registry before attempting a skill to verify it has
  everything it needs.

### Example registry entry

```yaml
skill: expense_approval
description: "Guide a non-technical user through submitting and tracking an expense"
requires_tools: [read_document, update_record, notify_user, call_api]
requires_permissions: [record-write]
guide: skills/expense_approval.md
domains: [finance, hr, operations]
```

---

## Component 4 — Sub-Agents

**When a task is too large, or the context window is filling up — delegate.**

### When to use a sub-agent

- The task is self-contained and doesn't need to share live state with the
  main agent.
- Main agent context > 60% full — offload to keep the main context clean.
- Multiple independent tasks can run in parallel.

### Briefing principle

```
Brief a sub-agent like briefing a capable colleague:
  ✓ Specific task with clear success criteria
  ✓ Minimal context — only what is needed for this task
  ✓ Expected output format defined upfront
  ✗ Never dump the full conversation history
  ✗ Never grant broader permissions than the task requires
```

### Standard pattern

```
spawn_sub_agent(
    task        = "Summarize the last 30 days of support tickets for Account #1042",
    context     = { account_id: "1042", date_range: "last_30_days" },
    permissions = ["READ_ONLY"],
    output_format = "bullet list of top 5 recurring issues"
)
# Main agent receives only the result — not the sub-agent's full session
```

---

## Component 5 — Built-in Skills

**Same harness, same model — but different built-in skills produce
completely different outcomes.** This is the real differentiator between
agent platforms.

### Minimum built-in skill set for enterprise agents

The right set depends on the domain, but every enterprise harness should have:

- [ ] **Domain knowledge retrieval** — search internal docs, policies, FAQs
- [ ] **Record lookup & update** — read and write to the relevant data systems
- [ ] **Notification & escalation** — email, Slack, ticket creation
- [ ] **Document handling** — read, summarize, extract structured data from
      uploaded files
- [ ] **Graceful handoff** — recognize when to transfer to a human agent,
      with full context passed along
- [ ] **User preference memory** — remember what this user told the agent
      in prior sessions

### Domain-specific examples

| Domain           | Example built-in skills                                                  |
| ---------------- | ------------------------------------------------------------------------ |
| Customer Service | ticket lookup, refund initiation, FAQ search, escalate to agent          |
| HR               | policy lookup, leave balance check, form submission, calendar scheduling |
| Finance          | expense submission, approval routing, invoice lookup, budget query       |
| Operations       | status check, alert triage, runbook lookup, incident logging             |

---

## Component 6 — Session Persist

**Crash = resume exactly where you left off.** The session lives independently
of the harness process.

### Standard format: Append-only JSONL

```jsonl
{"turn": 1, "role": "user",      "content": "...", "ts": 1700000001}
{"turn": 2, "role": "assistant", "content": "...", "ts": 1700000045}
{"turn": 3, "role": "tool",      "content": "...", "ts": 1700000046}
```

### Mandatory rules

1. **Append-only**: never overwrite or delete past entries.
2. **Flush + fsync** immediately after every append — before any tool executes.
3. **Session ID** is independent of the harness process ID or timestamp.
4. **Resume logic**: on startup, read the JSONL, rebuild the messages array,
   and continue the loop exactly where it stopped.

### What to persist per turn

```
Each turn entry should capture:
  - role         (user / assistant / tool)
  - content      (the message or tool result)
  - timestamp    (for debugging and audit)
  - session_id   (to group turns together)
  - turn_number  (for ordering and gap detection)
```

---

## Component 7 — Prompt Assembly

**The system prompt is not a static string — it is a pipeline assembled fresh
per context.**

### Rebuild triggers

The system prompt should be rebuilt whenever the agent's operating context
changes: new user session, different domain mode, permission level change, or
a significant shift in task.

### Assembly order (fixed — do not reorder)

```
[1] Role definition          ← who the agent is; never changes
[2] Domain context           ← which domain/workflow is active
[3] Active skills            ← what the agent is currently allowed to do
[4] Permission level         ← what actions are permitted
[5] Session summary          ← what has been done so far this session
[6] User preferences         ← remembered facts about this specific user
[7] Safety constraints       ← last block, never overrideable
```

### Why order matters

- **Role first** establishes the agent's identity before any domain context.
- **Safety last** ensures it cannot be overridden by earlier blocks or user
  input injection.
- The session summary and user preferences personalize behavior without
  inflating context unnecessarily.

### Static vs dynamic prompt (the key mistake to avoid)

```
❌ Static — agent behaves identically regardless of domain or user
SYSTEM = "You are a helpful enterprise assistant."

✅ Dynamic — agent adapts to context while maintaining identity
build_system_prompt(
    domain         = "customer_service",
    active_skills  = ["ticket_lookup", "refund_initiation"],
    permission     = "record-write",
    session_summary = summarize_session(messages),
    user_prefs     = load_user_prefs(user_id),
)
```

---

## Component 8 — Lifecycle Hooks

**The right hook in the right place = a safe, observable harness.
Missing hooks = silent failures.**

### Hook map

```
[USER INPUT]
     ↓
[pre_input_hook]       ← validate, sanitize, detect prompt injection
     ↓
[MODEL CALL]
     ↓
[post_model_hook]      ← log response, detect anomalies, rate limit check
     ↓
[pre_action_hook]      ← classify action risk, check permission, ask human if needed
     ↓
[ACTION EXECUTION]     (tool call, API call, record update, notification, etc.)
     ↓
[post_action_hook]     ← log result, detect errors, trigger retry logic
     ↓
[pre_persist_hook]     ← validate session integrity before writing
     ↓
[PERSIST]
     ↓
[post_turn_hook]       ← metrics, alerts, compress context if needed
```

### The most important hook: `pre_action_hook`

This runs before **every** action the agent takes. It is the layer that keeps
the end user safe without them having to think about it.

```
pre_action_hook(action_name, action_input):

    risk = classify_action(action_name, action_input)
    # → LOW:  safe reads, notifications to the user themselves
    # → MEDIUM: writes, updates, sends to third parties
    # → HIGH:  deletions, financial transactions, irreversible changes

    if risk == HIGH and permission_level != FULL:
        show_user_confirmation_dialog(action_name, action_input)
        if not confirmed:
            return error("Action cancelled by user")

    if risk == MEDIUM:
        log_for_audit(action_name, action_input)

    # LOW → proceed immediately, no friction
```

---

## Component 9 — Permission Layer

**Every action the agent takes is classified before execution. This is the
layer that makes enterprise deployment possible.**

### 4 permission levels

| Level                | Symbol | What it permits                                               |
| -------------------- | ------ | ------------------------------------------------------------- |
| Read-only            | `RO`   | Read data, search, summarize — no state changes               |
| Scoped-write         | `SW`   | Write within a defined scope (e.g., this user's records only) |
| Full                 | `FU`   | Unrestricted action within the agent's configured domain      |
| Interactive approval | `IA`   | Every HIGH-risk action requires explicit user confirmation    |

### Action risk classification

Not just shell commands — any action an enterprise agent takes should be
classified:

| Action type                | Example                              | Default risk |
| -------------------------- | ------------------------------------ | ------------ |
| Read / search              | Look up a policy, fetch a ticket     | LOW          |
| Notify user themselves     | Send them a summary email            | LOW          |
| Update a record            | Modify an expense status             | MEDIUM       |
| Send to a third party      | Email a vendor, post to Slack        | MEDIUM       |
| Financial transaction      | Approve payment, issue refund        | HIGH         |
| Delete or archive          | Remove a record, close an account    | HIGH         |
| Irreversible system action | Cancel a contract, terminate service | HIGH         |

### Least-privilege principle

- Start every agent session at `RO`.
- Elevate to `SW` or `FU` only for specific task blocks that require it.
- Sub-agents always start at `RO` or `SW` — never `FU`.
- `IA` mode is appropriate for agents handling HIGH-risk domains (finance,
  legal, healthcare) where end users need explicit control.

---

## Quick Design Checklist

Use this before shipping any harness to production:

### Foundation

- [ ] Single while loop with one model call location?
- [ ] Persist with flush + fsync after every turn?
- [ ] Resume logic tested: crash mid-session → restart → continues correctly?
- [ ] Context management: clear keep / summarize / drop strategy?

### Safety

- [ ] `pre_action_hook` (or equivalent) on every agent action?
- [ ] Sub-agents start READ_ONLY?
- [ ] Human-in-the-loop for HIGH-risk actions?
- [ ] Permission level set explicitly — not defaulting to full?

### Durability

- [ ] System prompt rebuilt dynamically (not static)?
- [ ] Context compression triggers before 70% token limit?
- [ ] Session ID is process-independent?
- [ ] All `stop_reason` values handled (especially `max_tokens`)?

### End-user experience

- [ ] Agent communicates progress to the user during long tasks?
- [ ] Errors surfaced in plain language — no stack traces to the user?
- [ ] Handoff to human includes full context summary?
- [ ] User can always see what the agent did and undo if needed?

---

## Further Reference

- `.agents/references/agent-harnes/patterns.md` — Detailed implementation patterns per component
- `.agents/references/agent-harnes/anti-patterns.md` — Common failures and how to fix them
- `.agents/references/agent-harnes/production-checklist.md` — Full checklist for production deployment
