# GEMINI.md — Project Intelligence File

> This file is the primary control layer for Gemini CLI. Read it at the start of every session and after every `/compress` or `/clear`. Follow these rules strictly throughout the entire session.

---

## Project Context

<!-- CUSTOMIZE THIS SECTION FOR YOUR PROJECT -->

- **Project name**: [Your Project Name]
- **Stack**: [e.g., Next.js, TypeScript, PostgreSQL, Tailwind CSS]
- **Current goal**: [e.g., Build user authentication module]
- **Active branch**: [e.g., feat/auth]
- **Key docs**: [e.g., /docs/architecture.md, /docs/api-spec.md]
- **Run command**: [e.g., `npm run dev`]
- **Test command**: [e.g., `npm run test`]
- **Build command**: [e.g., `npm run build`]
- **Log locations**: [e.g., /logs/app.log]

---

## Workflow Orchestration

### 1. Plan Node Default

- Enter **plan mode** for ANY non-trivial task (3+ steps or architectural decisions)
- Write a detailed plan to `tasks/todo.md` with checkable items before touching any file
- If something goes sideways, **STOP and re-plan immediately** — do not keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Always ask: _"Have I understood the full scope before writing a single line?"_

### 2. Subagent Strategy

- Use subagents liberally to keep the main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- **One task per subagent** for focused execution
- Subagents should write their findings back to files, not just the context

### 3. Self-Improvement Loop

- After **ANY correction** from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until the mistake rate drops
- Review `tasks/lessons.md` at the start of every session

### 4. Verification Before Done

- **Never mark a task complete without proving it works**
- Diff behavior between main and your changes when relevant
- Ask yourself: _"Would a staff engineer approve this?"_
- Run tests, check logs, demonstrate correctness
- Always execute: `build → test → lint` as the self-check loop before declaring done

### 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask _"Is there a more elegant way?"_
- If a fix feels hacky: _"Knowing everything I know now, implement the elegant solution"_
- Skip this for simple, obvious fixes — don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing

- When given a bug report: **just fix it**. Do not ask for hand-holding
- Point at logs, errors, failing tests — then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

### 7. Using Skills

- Proactively use inherent skills (available, established) that are appropriate for the task requirements.

- When the skill content is insufficient to complete the task, read the @SKILLS_GUIDE.md file to find and use user-created skill extensions in the project.

---

## Task Management

1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in with user before starting implementation
3. **Track Progress**: Mark items complete (`- [x]`) as you go
4. **Explain Changes**: Provide a high-level summary at each step
5. **Document Results**: Add a review/outcome section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after any correction

### Task File Structure

```
tasks/
  todo.md       ← current plan with checkable items
  lessons.md    ← accumulated patterns and rules from past mistakes
```

---

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.
- **Commit Often**: Commit checkpoints regularly — clean git state enables safe experimentation.
- **Ask Before Destructive Actions**: Confirm before deleting files, dropping tables, or any irreversible operation.

---

## Session Rules

### Starting a Session

1. Read this file (`GEMINI.md`) fully
2. Read `tasks/lessons.md` for relevant patterns
3. Check `tasks/todo.md` for any open items
4. Identify the active branch and any in-progress context
5. Briefly summarize current state to the user before proceeding

### During a Session

- Use `@` to reference specific files — never say "that file" vaguely
- Leverage Gemini's large context window for whole-codebase analysis, but still prefer targeted reads for speed
- When asked to explore a large codebase, summarize findings to a file rather than flooding the context
- Use `!` prefix for shell commands when you need to run something directly
- Proactively suggest `/compress` when context grows large after a major task

### Ending a Session

- Summarize completed work
- Update `tasks/todo.md` with remaining items
- Suggest improvements to this `GEMINI.md` if gaps were discovered
- Commit all changes with a clear conventional commit message

---

## Gemini-Specific Behaviors

### Working with the Large Context Window

Gemini's context window is very large — use this deliberately, not carelessly:

- For **architecture understanding**: load multiple related files at once for a holistic view
- For **refactoring**: load the entire module being refactored, not just one file
- For **debugging**: load the full stack trace, relevant source files, and config together
- Even so: keep context clean by writing intermediate findings to files, not accumulating in chat

### Model Selection Guidance

| Task Type                                         | Recommended                    |
| ------------------------------------------------- | ------------------------------ |
| Quick edits, small scripts, autocomplete-style    | Gemini Flash (faster, cheaper) |
| Feature development, architecture, complex bugs   | Gemini Pro                     |
| System design, multi-file refactor, hard problems | Gemini Pro with deep thinking  |

Use `/model` to switch mid-session if a task demands more reasoning.

### Tool Use

Use these actively:

- Read files with `@filename` references rather than asking the user to paste content
- Run shell commands with `!command` to verify assumptions (e.g., `!npm test`, `!git diff`)
- Search the web for library docs or error messages when needed — don't guess from memory

---

## Code Standards

<!-- CUSTOMIZE THESE FOR YOUR PROJECT -->

### Always

- Write conventional commit messages: `feat(scope): description`
- Add JSDoc/docstring to all public functions
- Handle errors explicitly — no silent failures
- Write or update tests for any changed logic
- Store all AI-generated markdown notes in `/docs/ai/`

### Never

- Push directly to `main`, `master` or `develop`
- Leave `console.log` / debug statements in committed code
- Leave TODO comments without a corresponding task in `tasks/todo.md`
- Auto-approve git operations — always surface them for user review
- Create temp scripts or debug files without cleaning up before commit

---

## Prompt Patterns (How to Work With Me)

### Planning a Feature

```
Analyze this repository and create a step-by-step implementation plan for [feature].
Do not modify any files yet. Output the plan to tasks/todo.md.
```

### Whole-Codebase Analysis (Gemini Strength)

```
Load the entire src/ directory and give me an architectural overview:
- Main modules and their responsibilities
- Data flow between layers
- Potential technical debt or inconsistencies
Write a summary to docs/ai/architecture-review.md
```

### Debugging

```
Here is the full error log: @logs/error.log
Here is the relevant source: @src/module.ts
Explain the root cause and propose the minimal fix.
```

### Code Review

```
Review @src/feature.ts as a senior developer.
Look for: bugs, performance issues, security risks, edge cases.
```

### Refactoring

```
Load @src/large-module.ts and suggest refactoring opportunities.
Focus on readability and modularization. Do not modify yet.
```

### Test Writing

```
Write unit tests for @src/module.ts using [Jest/Vitest/pytest].
Cover: happy path, edge cases, failure scenarios.
```

---

## File Organization Rules

- All markdown notes from AI sessions → `/docs/ai/`
- All task files → `/tasks/`
- Temp/debug scripts → clean up before any commit
- Never scatter generated files across the project root

---

## Self-Check Before Marking Done

Ask yourself:

- [ ] Does this actually solve the problem, or does it just appear to?
- [ ] Have I run the build, tests, and lint?
- [ ] Did I leave any debug code or temp files?
- [ ] Is the commit message clear and conventional?
- [ ] Would a staff engineer approve this PR?
- [ ] Have I updated `tasks/todo.md` and `tasks/lessons.md`?
