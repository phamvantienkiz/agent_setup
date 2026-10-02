# Reference: Production Deployment Checklist

Use this when preparing to deploy any enterprise agent harness.
Each item should be confirmed by at least one team member before shipping.

---

## Phase 1: Foundation (MANDATORY — do not deploy if any are missing)

### While Loop
- [ ] Single model call location in the entire codebase
- [ ] All `stop_reason` values handled: `end_turn`, `tool_use`, `max_tokens`, and edge cases
- [ ] Timeout configured per model call (recommended: 5 minutes)
- [ ] Maximum turn limit set (recommended: 200 turns) with human escalation on hit

### Session Persist
- [ ] Append-only JSONL format
- [ ] `flush()` + `fsync()` after every append
- [ ] Session ID is independent of process ID or startup timestamp
- [ ] Resume tested: kill the process mid-session → restart → continues correctly
- [ ] Archive/rotation logic when file exceeds size limit

### Context Management
- [ ] Summarization triggers before 70% of max token limit
- [ ] Summary retains: key decisions, unresolved issues, user preferences
- [ ] Summary drops: verbose tool output, resolved errors, redundant reasoning
- [ ] Post-summarization test: agent still knows what it was doing

---

## Phase 2: Safety (MANDATORY for any enterprise deployment)

### Permission Layer
- [ ] Every agent action passes through `pre_action_hook` or equivalent
- [ ] Actions classified by business risk (LOW / MEDIUM / HIGH) — not just by type
- [ ] Sub-agents default to READ_ONLY
- [ ] HIGH-risk actions require explicit user confirmation at IA permission level
- [ ] No way to bypass the permission layer through user input

### Lifecycle Hooks
- [ ] `pre_input_hook` validates and sanitizes all user input
- [ ] `pre_action_hook` classifies risk and enforces permission before every action
- [ ] `post_action_hook` logs result, detects failure, triggers retry if appropriate
- [ ] Audit log captures: timestamp, action name, risk level, input summary, outcome

### Human-in-the-Loop
- [ ] Explicit list of actions requiring human confirmation for this domain
- [ ] Confirmation dialog shows plain-language description of what will happen
- [ ] Timeout on approval request: if user doesn't respond → default to cancel (not proceed)
- [ ] Escalation to human agent includes full session context summary

---

## Phase 3: Reliability (Should be complete before scaling)

### Prompt Assembly
- [ ] System prompt rebuilt dynamically — not hardcoded
- [ ] Safety block is always the last block and cannot be overridden
- [ ] Prompt injection tested: user cannot override safety constraints via input
- [ ] Domain context and user preferences injected correctly per session

### Tools & Skills Registry
- [ ] Every skill has an explicit list of tool dependencies and required permissions
- [ ] Agent checks registry before attempting any skill
- [ ] Graceful fallback when a tool is unavailable (notify user, don't crash)

### Sub-Agents
- [ ] Sub-agents receive minimal context only — no full history dumps
- [ ] Main agent receives only the result, not the sub-agent's session
- [ ] Sub-agent timeout configured (recommended: 30 minutes)
- [ ] Sub-agent failures handled gracefully in the main agent loop

---

## Phase 4: End-User Experience (Required for non-technical users)

### Communication
- [ ] Agent sends progress signals for tasks expected to take more than 10 seconds
- [ ] All errors translated to plain language before reaching the user
- [ ] No raw stack traces, API errors, or internal identifiers shown to users
- [ ] Completion messages summarize what was done in plain language

### Memory & Personalization
- [ ] User preferences extracted and stored during sessions
- [ ] User preferences injected into system prompt on subsequent sessions
- [ ] Users can explicitly update or clear their stored preferences

### Handoff
- [ ] Human escalation always includes: plain-language summary, session log link, suggested next action
- [ ] Users are told they're being transferred before it happens
- [ ] Handoff tested end-to-end: human agent receives and understands the context

---

## Phase 5: Observability (Required for operations team)

### Logging
- [ ] Every turn logged: session_id, turn_number, timestamp, token_count
- [ ] Every action logged: action_name, risk_level, duration, success/failure
- [ ] Error log includes full context (not just the error message)

### Metrics to track
- [ ] Token usage per session and per task type
- [ ] Turn count per completed task (rising average = something degrading)
- [ ] Action success rate by action type
- [ ] Human escalation rate (too high = agent scope is too narrow; too low = may be overreaching)
- [ ] Session resume rate (rising = more crashes than expected)
- [ ] User satisfaction signals (thumbs up/down, task completion rate)

### Alerts
- [ ] Alert: session exceeds X turns without completing
- [ ] Alert: token usage spike beyond normal range
- [ ] Alert: HIGH-risk action blocked repeatedly (may indicate misconfigured permissions)
- [ ] Alert: escalation rate exceeds threshold

---

## Deployment Sign-off

Before going to production:

| Reviewer | Role | Signed off | Date |
|---|---|---|---|
| | Tech Lead | ☐ | |
| | Security / Compliance | ☐ | |
| | Product / Domain Owner | ☐ | |
| | End-User Representative | ☐ | |

**Deployment record:**
```
Version:
Deploy date:
Deployed by:
Domains active:
Rollback plan:
First review checkpoint:
```
