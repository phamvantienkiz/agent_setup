# AGENTS.md — Project Intelligence File

> This file is the primary control layer for Antigravity CLI (`agy`) and Antigravity 2.0. Read it completely at the start of every session, after any `/clear`, or upon context compression. Follow these rules strictly throughout the entire session.

---

## 1. Project Context

<!-- CUSTOMIZE THIS SECTION FOR YOUR PROJECT -->

- **Project Name**: [Your Project Name]
- **Stack**: [e.g., Node.js, FastAPI, TypeScript, PostgreSQL]
- **Current Goal**: [e.g., Build user authentication module]
- **Active Branch**: [e.g., feat/auth]
- **Key Docs**: [e.g., /docs/architecture.md, /docs/api-spec.md]
- **Execution Commands**:
  - Run: `npm run dev`
  - Test: `npm run test`
  - Build: `npm run build`
- **Infrastructure Context**: Local MCP servers available via `.agents/mcp_config.json`.

---

## 2. Core Philosophy (Caution Over Speed)

### Think Before Coding

- **Don't assume, don't hide confusion, and always surface tradeoffs.**
- State your assumptions explicitly before implementing any solution; if uncertain, ask the user immediately.
- If multiple interpretations or approaches exist, present them clearly instead of picking one silently.
- If a simpler or more elegant approach exists, push back and suggest it before writing code.
- If something within the requirements is unclear, **STOP** and name what is confusing.

### Simplicity First

- **Write the minimum code that solves the problem. Absolutely nothing speculative.**
- Do not implement any features, abstractions, or "future-proofing" configurability beyond what was explicitly requested.
- Avoid adding complex error handling for impossible or out-of-scope scenarios.
- If a solution can be written in 50 lines instead of 200, rewrite and simplify it ruthlessly.

### Surgical Changes

- **Touch only what you must. Clean up only your own mess.**
- Do not "improve", reformat, or refactor adjacent code or comments that are not broken or requested.
- Strictly match the existing codebase style, naming conventions, and architecture patterns.
- If your changes create orphans (unused imports, variables, or functions), remove them immediately. Do not touch pre-existing dead code unless explicitly instructed.
- Every changed line must trace directly and cleanly back to the user's request.

---

## 3. Workflow Orchestration

### 1. Goal-Driven Plan Mode

- Enter `/plan` mode for ANY non-trivial task involving 3+ steps or architectural decisions.
- Transform tasks into verifiable goals with strict success criteria before touching any file.
- Write your step-by-step execution plan to `tasks/todo.md` using the following exact structure:

```
1. [Step Description] → verify: [Specific check, command, or test behavior]

2. [Step Description] → verify: [Specific check, command, or test behavior]
```

- Check in and verify the plan with the user before starting implementation.
- If something goes sideways during execution, **STOP and re-plan immediately** — do not force a broken approach.

### 2. Autonomous Bug Fixing

- When given a bug report or error log, actively analyze and fix it without hand-holding.
- Point out the root cause based on errors or failing tests, then implement the minimal surgical fix.
- Go fix failing CI/CD or local test scripts autonomously.

### 3. Progressive Skill Discovery

- Proactively discover and leverage inherent workspace skills defined inside `.agents/skills/`.
- Trust the progressive disclosure mechanism; trigger skills explicitly using slash commands (e.g., `/spec-gen`) or by attaching them via `@.agents/skills/` when required.

### 4. Subagent & Infrastructure Automation

- Use subagents liberally to offload research, exploration, or parallel data analysis to keep the main context clean.
- Subagents must write their intermediate findings back to specific files rather than flooding the active chat window.
- Monitor automated workspace hooks (`/hooks`) to ensure linting, formatting, or validation occurs naturally during file mutations.
- Leverage Model Context Protocol via `/mcp` to interact with external databases or local system tools securely.

### 5. Self-Improvement Loop

- After receiving **ANY correction** from the user, immediately update `tasks/lessons.md` with the failure pattern.
- Formulate strict rules for yourself to prevent repeating the same technical or logical mistake.
- Review `tasks/lessons.md` at the start of every single session to reinforce behavioral updates.

---

## 4. Session Rules & Context Management

### Starting a Session

1. Read this `AGENTS.md` file fully to align behavioral constraints.
2. Read `tasks/lessons.md` to review past mistakes and accumulated patterns.
3. Check `tasks/todo.md` for open goals, success criteria, or remaining tasks.
4. Briefly summarize the active branch and current system state to the user before working.

### During a Session

- Explicitly use the `@` prefix to reference target files, directories, or skills — never refer to context vaguely.
- When analyzing large directories, output structural overviews or intermediate notes to files instead of overloading the live chat context.
- For large-scale refactoring or complex multi-file visual management, proactively prepare the session context for a seamless export to the Antigravity 2.0 desktop environment.

### Ending a Session

- Provide a high-level summary of completed tasks and modified architectural components.
- Update `tasks/todo.md` with remaining goals, outstanding checkable items, and review outcomes.
- Commit all finalized changes using clean conventional commit messages.

---

## 5. Code Standards & File Organization

### Development Rules

- **Commit Checkpoints Often**: Maintain a clean git state to enable safe experimentation and easy rollbacks.
- **No Laziness**: Identify and resolve root causes; temporary patches or quick hacks are strictly forbidden.
- **Explicit Error Handling**: Handle errors explicitly; zero silent failures or unhandled rejections allowed.
- **Ask Before Destruction**: Always request explicit user confirmation before executing any destructive action, dropping tables, or deleting files.
- **No Hidden Logs**: Never leave `console.log`, debug statements, or temporary test scripts in committed code.

### File Layout Customization

- All AI-generated markdown notes, architectural reviews, and session summaries → `/docs/ai/`.
- All active plans, verification criteria, and learned behaviors → `/tasks/`.
- Maintain strict separation of components: do not scatter generated files across the root directory.

---

## 6. Pre-Commit Verification Loop

Before declaring any task or goal complete, you must execute the following self-check loop and prove correctness:

- [ ] **Surgical Check**: Does every modified line trace directly back to the core request without unnecessary changes?
- [ ] **Simplicity Check**: Is the solution as minimal and straightforward as possible, avoiding over-engineering?
- [ ] **Verification Loop**: Have I run the local build, unit tests, and linters, ensuring zero errors or warnings remain?
- [ ] **Cleanliness Check**: Have all temporary debug files, logs, or dangling scripts been cleaned up?
- [ ] **Documentation**: Are all JSDoc/docstrings updated, and have `tasks/todo.md` and `tasks/lessons.md` been synchronized?
- [ ] **Peer Standard**: Would a rigorous Staff Engineer approve this precise diff?
