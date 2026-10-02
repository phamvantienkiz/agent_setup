# AGENTS.md — Project Intelligence File

> This file is the primary control layer for Antigravity CLI (`agy`) and Antigravity 2.0. Read it completely at the start of every session, after any `/clear`, or upon context compression. Follow these rules strictly throughout the entire session.

---

## 1. Project Context

- **Project Name**: Agent setup and configuration
- **Current Goal**: Agent setup and configuration
- **Infrastructure Context**: MCP servers available via `.agents/mcp_config.json`.

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

## 3. Environment Isolation & Script Execution Rules

- **Strict Environment Isolation:** NEVER install packages, dependencies, or toolchains into the global system environment, regardless of language or stack (Python, Node.js, or any other). All installations and executions MUST stay scoped to the current workspace.
- **Verification Before Execution:** Before running any install, build, or script command, verify that the project-local environment exists and is being used. If it is missing, create it first.
- **No Global Scope Spillage:** Any command that risks altering the host machine's global configurations, system PATH, or environment variables is strictly forbidden.

### Python

- **Mandatory Use of `uv` or `.venv`:** All package installations and script executions MUST happen within an isolated virtual environment (`.venv`) located inside the current workspace.
- Use the `uv run` / `uv pip` toolchain (which handles isolation automatically), or activate `.venv` first. If `.venv` is missing, create it (`uv venv` or `python -m venv .venv`) before proceeding.
- Never run bare `pip install` or `python script.py` against the global interpreter.

### Node.js / JavaScript / TypeScript

- Install dependencies locally to the project (`node_modules`) using the package manager already in use (detect via lockfile: `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`). Do not switch package managers.
- NEVER use global installs (`npm install -g`, `yarn global add`, `pnpm add -g`). Run one-off CLI tools via `npx` / `pnpm dlx` / `bunx` instead.

### Other Stacks

- Apply the same principle to any other ecosystem (Go, Rust, Java, etc.): use project-scoped dependency management (e.g., `go.mod`, `Cargo.toml`, wrapper scripts) and never modify system-wide installations.
- If a task seems to require a global install or system-level change, **STOP** and ask the user first.

---

## 4. Pre-Completion Checklist

Before declaring any task done, verify every item:

- [ ] **Surgical Check**: Does every modified line trace directly back to the core request without unnecessary changes?
- [ ] **Simplicity Check**: Is the solution as minimal and straightforward as possible, avoiding over-engineering?
- [ ] **Verification Loop**: Have I run the local build, unit tests, and linters, ensuring zero errors or warnings remain?
- [ ] **Cleanliness Check**: Have all temporary debug files, logs, or dangling scripts been cleaned up?
- [ ] **Documentation**: Are all JSDoc/docstrings updated, and have `tasks/todo.md` and `tasks/lessons.md` been synchronized?
- [ ] **Peer Standard**: Would a rigorous Staff Engineer approve this precise diff?

---

## 5. Working Rules

- **Commit Checkpoints Often**: Maintain a clean git state to enable safe experimentation and easy rollbacks.
- **No Laziness**: Identify and resolve root causes; temporary patches or quick hacks are strictly forbidden.
- **Explicit Error Handling**: Handle errors explicitly; zero silent failures or unhandled rejections allowed.
- **Ask Before Destruction**: Always request explicit user confirmation before executing any destructive action, dropping tables, or deleting files.
- **No Hidden Logs**: Never leave `console.log`, debug statements, or temporary test scripts in committed code.
