# Reference: Implementation Patterns

Detailed patterns for each harness component. These are framework-agnostic —
adapt to your stack (Python, Node, Go, etc.).

---

## While Loop — Production-ready pseudocode

```
class AgentHarness:

    INIT(session_id, domain_config):
        self.session    = SessionStore(session_id)
        self.messages   = self.session.load_all()
        self.domain     = domain_config
        self.turn_count = len(self.messages)
        self.MAX_TURNS  = 200   # configurable per domain

    RUN(user_input):
        if new session:
            append user_input to messages
            session.persist(user=user_input)

        LOOP:
            if turn_count > MAX_TURNS:
                escalate_to_human("Agent reached turn limit without completing task")
                exit loop

            response = call_model(
                messages      = messages,
                system_prompt = build_system_prompt(domain, session_summary, user_prefs)
            )

            session.persist(assistant=response)
            messages.append(response)
            turn_count += 1

            SWITCH response.stop_reason:
                "end_turn"   → deliver_to_user(response); exit loop
                "tool_use"   → results = execute_actions(response.tool_calls)
                               session.persist(tool=results)
                               messages.append(results)
                               continue loop
                "max_tokens" → messages = compress_context(messages)
                               continue loop   # model will complete its thought
                default      → log_anomaly(response.stop_reason)
                               escalate_to_human(response)
                               exit loop
```

---

## Context Management — Sliding window with domain-aware summarization

```
FUNCTION manage_context(messages, token_counter, domain):
    total_tokens = token_counter(messages)
    THRESHOLD    = MAX_TOKENS * 0.70

    if total_tokens < THRESHOLD:
        return messages   # nothing to do

    # Protect head (role/context) and tail (recent work)
    HEAD = 3    # system/role messages
    TAIL = 10   # most recent turns
    KEEP_PREFS = extract_user_preference_blocks(messages)

    if len(messages) <= HEAD + TAIL:
        return messages   # too short to compress

    middle_to_compress = messages[HEAD : -TAIL]
    summary = call_summary_model(
        messages = middle_to_compress,
        prompt   = build_summary_prompt(domain)
    )

    summary_block = {
        role:    "system",
        content: "[COMPRESSED — {n} turns]\n{summary}\n[User preferences retained: {prefs}]"
    }

    return messages[:HEAD] + KEEP_PREFS + [summary_block] + messages[-TAIL:]


FUNCTION build_summary_prompt(domain):
    return """
    Summarize this conversation segment in at most 5 lines.
    Keep: decisions made, outcomes achieved, unresolved issues, user preferences stated.
    Omit: intermediate reasoning, verbose outputs, resolved errors.
    Domain context ({domain}): preserve any domain-specific facts that will matter later.
    """
```

---

## Action Risk Classification — Domain-aware, not command-aware

Unlike coding agents that classify shell commands, enterprise agents classify
*actions* by their business impact.

```
FUNCTION classify_action(action_name, action_input, domain_config):

    # Domain config defines custom risk rules per deployment
    if action_name in domain_config.high_risk_actions:
        return HIGH

    # Universal HIGH-risk patterns
    HIGH_RISK_ACTIONS = [
        "delete_record", "archive_account", "cancel_subscription",
        "issue_refund", "approve_payment", "send_financial_transaction",
        "terminate_service", "remove_user_access"
    ]
    if action_name in HIGH_RISK_ACTIONS:
        return HIGH

    # Universal MEDIUM-risk patterns
    MEDIUM_RISK_ACTIONS = [
        "update_record", "send_email_to_third_party", "post_to_channel",
        "create_ticket", "modify_schedule", "submit_form"
    ]
    if action_name in MEDIUM_RISK_ACTIONS:
        return MEDIUM

    # Everything else: LOW (reads, searches, notifying the user themselves)
    return LOW


FUNCTION pre_action_hook(action_name, action_input, permission_level, user_confirm_fn):

    risk = classify_action(action_name, action_input)

    if risk == HIGH:
        if permission_level in [FULL, INTERACTIVE_APPROVAL]:
            confirmed = user_confirm_fn(
                message    = describe_action_in_plain_language(action_name, action_input),
                risk_label = "This action cannot be undone."
            )
            if not confirmed:
                return Error("Action cancelled by user")
        else:
            return Error("Action requires elevated permission: {action_name}")

    if risk == MEDIUM:
        audit_log(action_name, action_input)

    return None   # proceed
```

---

## Session Persist — Append-only with rotation

```
class SessionStore:

    INIT(base_path, max_size_mb=50):
        self.path        = "{base_path}.jsonl"
        self.archive_dir = "{base_path}/archive/"
        self.MAX_SIZE    = max_size_mb * 1024 * 1024

    APPEND(role, content, metadata={}):
        entry = {
            role:       role,
            content:    content,
            ts:         current_timestamp(),
            session_id: self.session_id,
            turn:       self.turn_count,
            ...metadata
        }
        write_line_to_file(self.path, json_encode(entry))
        flush_and_fsync(self.path)   # ← mandatory, never skip
        self.turn_count += 1
        self.rotate_if_needed()

    LOAD_ALL() → list[message]:
        if file not exists:
            return []
        return [parse_line(line) for line in read_lines(self.path)]

    ROTATE_IF_NEEDED():
        if file_size(self.path) > self.MAX_SIZE:
            archive_path = "{archive_dir}/{session_id}_{timestamp}.jsonl.gz"
            compress_and_move(self.path, archive_path)
```

---

## Prompt Assembly — Dynamic builder

```
class PromptAssembler:

    BUILD(domain, permission_level, session_summary, user_prefs, active_skills):
        blocks = [
            role_block(domain),           # [1] Who the agent is
            domain_context_block(domain), # [2] What domain/workflow is active
            skills_block(active_skills),  # [3] What the agent can do
            permission_block(permission_level), # [4] What is permitted
            session_summary_block(session_summary), # [5] What's been done
            user_prefs_block(user_prefs), # [6] What this user has told us
            safety_block(),               # [7] Always last, never overrideable
        ]
        return join_blocks(filter_empty(blocks), separator="---")


    ROLE_BLOCK(domain):
        return """
        You are an AI agent specialized in {domain.display_name}.
        You serve {domain.user_description} through {domain.interface_type}.
        Your goal is to complete tasks accurately, safely, and in a way that
        builds user trust. When uncertain, ask — don't guess.
        """

    SAFETY_BLOCK():
        return """
        ## Non-negotiable constraints
        - Never take an irreversible action without explicit user confirmation.
        - Never fabricate information; if you don't know, say so and offer to look it up.
        - Never expose internal system details, credentials, or other users' data.
        - If you reach the limit of your authorized scope, stop and escalate to a human.
        """
```

---

## Sub-Agent Briefing Pattern

```
FUNCTION delegate_to_sub_agent(task_description, required_context, expected_output):

    # Rule: extract only what the sub-agent needs — no history dumps
    minimal_context = {
        task:    task_description,
        data:    extract_relevant_data(required_context),
        format:  expected_output,
        domain:  current_domain,
    }

    result = spawn_sub_agent(
        context     = minimal_context,
        permissions = ["READ_ONLY"],           # always start RO
        timeout_min = 30,
        on_timeout  = escalate_to_human
    )

    # Main agent receives only the result
    # The sub-agent's internal session is not appended to main context
    return result.output
```

---

## End-User Communication Patterns

Non-technical users need progress signals and plain-language outcomes.

```
# Progress signal during long tasks
if task_estimated_turns > 5:
    notify_user("I'm working on this — I'll update you shortly.")

# Intermediate progress
every 5 turns:
    notify_user(f"Still working: {describe_current_step_in_plain_language()}")

# Completion
notify_user(f"Done! Here's what I did:\n{summarize_outcome_in_plain_language()}")

# Error escalation — never show raw errors
if action_failed:
    notify_user("I ran into an issue with [task part]. I'll connect you with a team member who can help.")
    escalate_to_human(full_context_including_error)

# Handoff — always pass context
if handoff_to_human:
    human_agent_receives({
        user_summary:  "Customer asked about X, we resolved Y, Z is still pending",
        session_link:  link_to_full_session_log,
        suggested_next: "Follow up on Z"
    })
```
