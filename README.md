# Gemini CLI Agent Setup

A comprehensive collection of configurations, specialized skills, and workflows designed to transform **Gemini CLI** into a high-performance, autonomous coding agent.

This repository provides a battle-tested structure that you can drop into any project root to establish clear engineering standards, automate repetitive tasks, and enforce disciplined development cycles (like TDD and systematic debugging).

---

## 🚀 What's Inside

### 1. `.gemini/` - The Brain

Contains the foundational rules and persona definitions for your agent.
**Agents**: Specialized personas for Backend (FastAPI/Node.js), Frontend, UI/UX, QA, and Project Management.
**Rules**: Strict engineering standards covering API design, security, database management, naming conventions, and testing.
**Commands**: Pre-defined workflows for common tasks like `deploy`, `fix-issue`, and `review`.

### 2. `skills/` - The Superpowers

A library of modular skills that extend Gemini's capabilities.

- **Development**: Test-Driven Development (TDD), Systematic Debugging, and Writing Implementation Plans.
- **Infrastructure**: Dockerfile generation and validation, Postgres optimization.
- **Specialized**: RAG architecture design, security reviews, and document specialization.
- **Process**: Brainstorming, subagent-driven development, and git worktree isolation.

### 3. `tasks/` - Task Management

Templates for tracking progress and capturing lessons learned.

- `todo.md`: A structured way for Gemini to plan and track multi-step implementations.
- `lessons.md`: A "memory" file where Gemini records corrections to avoid repeating mistakes.

### 4. Foundational Guides

- **`GEMINI.md`**: The primary project intelligence file. Gemini reads this at the start of every session to understand your stack, goals, and rules.
- **`gemini_guide.md`**: A comprehensive manual for humans on how to interact with Gemini CLI effectively.
- **`SKILL_GUIDE.md`**: An internal index that helps the agent find and invoke the correct skill for any task.

---

## 🛠 How to Use

To use this setup in your own project:

1. **Copy the following to your project root:**

- Folder `.gemini/`
- Folder `skills/`
- Folder `tasks/`
- Files `GEMINI.md`, `SKILL_GUIDE.md`, and `gemini_guide.md`

2. **Customize `GEMINI.md`:**
   Open the file and fill in your project-specific details (Name, Tech Stack, Current Goals).

3. **Start Gemini:**
   Run `gemini` in your terminal. Gemini will automatically detect `GEMINI.md` and adopt the configured standards.

---

## Acknowledgments

This setup is heavily inspired by and adapted from the excellent work done for the Claude Code community. Special thanks to the original author: [[Class-AI-Agent](https://github.com/fdhhhdjd/Class-AI-Agent)]

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE)
