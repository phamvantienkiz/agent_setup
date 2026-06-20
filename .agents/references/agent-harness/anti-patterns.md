# Reference: Anti-Patterns & How to Fix Them

Common failures when building enterprise agent harnesses, sorted by severity.

---

## 🔴 CRITICAL — Data loss or system damage

### 1. Persisting after acting (not before)

```
❌ Wrong: crash during action → turn is lost, agent replays destructively
  response = call_model(messages)
  execute_action(response)     ← crash here
  session.persist(response)   ← never reached

✅ Right: crash during action → resume from safe checkpoint
  response = call_model(messages)
  session.persist(response)   ← persist FIRST
  execute_action(response)    ← crash here → session already saved
```

### 2. Sub-agents with unrestricted permissions

```
❌ Wrong: sub-agent can touch anything in the system
  spawn_sub_agent(task=..., permissions=["FULL"])

✅ Right: sub-agent is scoped to exactly what it needs
  spawn_sub_agent(
      task        = "Summarize this user's last 5 support tickets",
      permissions = ["READ_ONLY"],
      data_scope  = { user_id: "12345" }   # can only see this user's data
  )
```

### 3. `max_tokens` not handled

```
❌ Wrong: agent silently stops mid-task; user sees no output, no error
  while True:
      response = call_model(messages)
      if response.stop_reason == "end_turn":
          break
      # max_tokens → falls through, loop either hangs or raises exception

✅ Right: detect and recover gracefully
  if response.stop_reason == "max_tokens":
      messages = compress_context(messages)
      notify_user("Still working, organizing my notes...")
      continue   # model completes its thought in the next turn
```

### 4. Irreversible actions without confirmation

```
❌ Wrong: agent sends a refund, cancels an order, deletes a record —
   without asking the user first. Non-technical users have no recourse.

✅ Right: classify action risk; HIGH-risk always requires confirmation
  if classify_action(action) == HIGH:
      show_confirmation_dialog(
          "I'm about to issue a $240 refund to card ending 4821. Confirm?"
      )
```

---

## 🟡 HIGH — Inconsistent or unreliable agent behavior

### 5. Calling the model in multiple places

```
❌ Wrong: scattered calls make the agent unpredictable and hard to audit
  def handle_user_message(msg):
      result = call_model([msg])   ← call #1

  def check_completion(messages):
      done = call_model(messages)  ← call #2

✅ Right: one centralized model call location
  class Harness:
      def _call_model(self, messages):
          """The ONLY place in this codebase that calls the model."""
          return anthropic.messages.create(...)
```

### 6. Static system prompt

```
❌ Wrong: agent behaves identically regardless of domain, user, or state
  SYSTEM = "You are a helpful enterprise assistant."

✅ Right: rebuild the prompt with current context
  system = build_system_prompt(
      domain          = "customer_service",
      active_skills   = ["ticket_lookup", "refund_initiation"],
      permission      = "scoped-write",
      session_summary = summarize_session(messages),
      user_prefs      = load_user_prefs(user_id)
  )
```

### 7. Dumping full history into sub-agents

```
❌ Wrong: sub-agent gets 200 turns of irrelevant context
  spawn_sub_agent(task="Summarize tickets", context=ALL_MESSAGES)

✅ Right: minimal, targeted context
  spawn_sub_agent(
      task    = "Summarize tickets for account #1042",
      context = { account_id: "1042", tickets: fetch_tickets("1042") }
  )
```

### 8. No turn limit

```
❌ Wrong: agent loops indefinitely on a stuck task; cost spirals
  while True:
      response = call_model(messages)
      ...

✅ Right: cap turns and escalate
  if turn_count > MAX_TURNS:
      escalate_to_human(
          "I wasn't able to complete this task automatically. "
          "Here's where I got stuck: {summary}"
      )
      break
```

---

## 🟢 MEDIUM — Degrades quality or user experience

### 9. Showing raw errors to end users

```
❌ Wrong: user sees "Error: 429 Too Many Requests at api.vendor.com/v2/..."
   Non-technical users don't know what this means and lose trust.

✅ Right: translate errors into plain language
  if action_failed:
      notify_user("I couldn't complete that step right now. I'll connect you "
                  "with a team member who can help.")
      log_error_for_engineers(full_error_detail)
```

### 10. No progress signals during long tasks

```
❌ Wrong: user submits a request; nothing happens for 90 seconds.
   They assume the agent is broken and refresh or abandon.

✅ Right: keep users informed
  notify_user("On it — give me a moment to pull that together.")
  ... (every 5 turns) ...
  notify_user("Still working on this. Almost there.")
```

### 11. Handoff to human without context

```
❌ Wrong: human agent receives "user has been transferred" with no history.
   User has to repeat everything. Trust is destroyed.

✅ Right: always pass a context summary on handoff
  escalate_to_human({
      plain_summary: "Customer asked about missing order #8821. I confirmed it
                      shipped but tracking shows stalled. Customer wants refund
                      or reship.",
      session_log:   link_to_full_session,
      suggested_action: "Check carrier exception report for order #8821"
  })
```

### 12. User preferences not persisted across sessions

```
❌ Wrong: user tells the agent "always send me summaries in bullet points"
   — next session, the agent has forgotten.

✅ Right: extract and store preference facts during the session
  POST_TURN: scan for user preference signals
      "I prefer...", "always do X", "never do Y", "my name is..."
  → extract → store in user_prefs store → inject into next session's prompt
```

---

## Summary table

| # | Anti-pattern | User impact | Priority |
|---|---|---|---|
| 1 | Persist after action | Data loss on crash | 🔴 Fix now |
| 2 | Sub-agent full permissions | Unauthorized data changes | 🔴 Fix now |
| 3 | `max_tokens` unhandled | Agent silently dies mid-task | 🔴 Fix now |
| 4 | No confirmation on HIGH-risk | Irreversible user harm | 🔴 Fix now |
| 5 | Model called in multiple places | Inconsistent, hard to audit | 🟡 Fix soon |
| 6 | Static system prompt | Agent ignores domain/user context | 🟡 Fix soon |
| 7 | History dump to sub-agents | Wasted tokens, confused sub-agent | 🟡 Fix soon |
| 8 | No turn limit | Runaway cost, stuck agent | 🟡 Fix soon |
| 9 | Raw errors to users | User confusion, lost trust | 🟢 Next sprint |
| 10 | No progress signals | Users think agent is broken | 🟢 Next sprint |
| 11 | Handoff without context | Users repeat themselves | 🟢 Next sprint |
| 12 | Preferences not persisted | Frustrating repeat sessions | 🟢 Next sprint |
