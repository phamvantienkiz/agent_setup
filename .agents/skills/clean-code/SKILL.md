---
name: clean-code
description: Enforce Robert C. Martin's Clean Code principles, the Boy Scout Rule, and Clean Architecture for AI coding agents. Includes 66 canonical Clean Code rules (C1-C5, F1-F4, G1-G36, N1-N7, T1-T9, P1-P3, TS1-TS3), an operating loop, offline static analysis scripts, and rule packs for 21 languages and 27 frameworks. Use when writing, editing, reviewing, refactoring, or designing code in any language.
metadata:
  version: "5.0.0"
  standard: "Google Antigravity Agent Skill"
---

# Clean Code & Clean Architecture Skill

> **"Always check a module in cleaner than when you checked it out."** — Robert C. Martin (*Clean Code*)  
> **"Teach your AI to write code that doesn't suck."**

This skill provides an authoritative, comprehensive framework enforcing Robert C. Martin's (*Uncle Bob*) Clean Code principles, the Boy Scout Rule, and Clean Architecture layer boundaries.

---

## 0. The Supreme Immutable Rule (Absolute Priority)

> [!CAUTION]
> ### ⚠️ THE SUPREME & IMMUTABLE RULE — OVERRIDES ALL OTHER PRINCIPLES
> **This is the highest-priority, non-negotiable, and immutable principle. Whenever any conflict arises or adhering to other coding conventions would over-complicate or fragment the logic, ALL OTHER CODING RULES (including SOLID, Clean Architecture, Design Patterns, and the 66 Clean Code heuristics below) MUST BE BYPASSED in favor of this rule:**
>
> > *"Good code is code that is simple, readable, runnable, testable, and explainable to understand. It is far better to have a single large function that is easy to comprehend—where reading it allows you to explain its full functionality and logic immediately—than a 'clean code' function of just a few lines that merely calls several other functions, which in turn call several other functions, branching into multiple objects, with those objects further inheriting from various other things, and so forth. The same applies to comments: as long as a comment is easy to understand, that is enough; it does not need to be verbose, nor does it need to be terse—sufficient to understand is all that matters."*

### Key Mandates of the Supreme Rule:
1. **Simplicity & Comprehension Over Premature Abstraction:**
   - Never shatter a function into multiple call layers, nested helper functions, or complex class inheritance hierarchies merely to achieve an arbitrary line-count target (e.g., "keep functions under 15 lines").
   - A single cohesive, sequential function that is straightforward to read, understand, debug, and explain is far superior to fractured indirection and artificial abstraction.
2. **Pragmatic Comments:**
   - Do not dogmatically ban or restrict comments. Any comment that makes the logic, intention, or business edge case immediately clear to the reader is good and welcome. It does not need to be overly verbose, nor does it need to be artificially terse—sufficient clarity is the sole metric.
3. **Absolute Override Authority:**
   - If applying any Clean Code rule (such as strict SLAP, function splitting, SRP micro-separation, or pattern abstraction) increases cognitive load, indirection, or debugging difficulty, **STOP immediately and preserve the simple, direct implementation**.

---

## 1. Core Philosophy: The Boy Scout Rule

You do not have to make every module perfect in one massive rewrite. You simply have to make it **a little bit better** every single time you touch it.

Every time you edit or fix code, look for **at least one small improvement**:
- **Quick Wins (Do Immediately)**:
  - Rename a poorly named variable (`clean-names`).
  - Delete a redundant comment or commented-out code (`clean-comments`).
  - Remove dead code or unused imports.
  - Replace a magic number/string with a named constant.
  - Extract a deeply nested block into a well-named function.
- **Deeper Improvements (When Time Allows)**:
  - Split a function that does multiple things (`clean-functions`).
  - Remove duplication (`DRY`, `clean-general`).
  - Add missing boundary checks.
  - Improve unit test coverage (`clean-tests`).

---

## 2. Hệ Thống Luật & Khung Hoạt Động (Operating Loop)

When working on any coding or refactoring task, follow this 6-step operating loop:

1. **Frame**: Define the exact behavioral change, assumptions, minimal scope, and success check. Ask only if ambiguity fundamentally changes the implementation.
2. **Read**: Inspect nearby code, naming conventions, tests, error-handling style, and framework idioms. Search for existing implementations before writing new code.
3. **Place**: Determine the owning unit and layer boundary *before* writing code. Files belong to folders by architectural role, never in the repository root or current directory.
4. **Edit Surgically**: Every changed line must trace directly to the request. Targeted edits, never whole-file regeneration; remove whatever your change orphaned.
5. **Verify**: Narrowest meaningful check first, followed by suite tests. Never claim success without executing verification commands and inspecting output.
6. **Review Diff**: Check the diff against the 66 Clean Code rules.

### Core Architectural Invariants:
- **Placement by Role**: Role decides folder per pack roles and project layout; mirror similar files. New files only with a cohesive home, fully wired (imports, exports, routes, DI). Never create sibling variants (`_v2`, `_new`, `_final`, `_copy`) or grow junk drawers (`utils`, `helpers`, `common`).
- **One Job Per Unit (SRP)**: If a unit needs "and" to describe its purpose, split it. Parsing, domain rules, persistence, external calls, presentation, and wiring stay in separate homes.
- **Minimal Code (YAGNI)**: Stop at the first yes: Unneeded? Write nothing. Already in codebase? Reuse it. Standard library/installed package does it? Use that. One line? Write it. Else write the minimum.
- **Layer Rules & The Dependency Rule**: Source dependencies point only inward, toward higher-level policy. Business rules never depend on database, web, UI, framework, or delivery mechanism details.

---

## 3. The 66 Canonical Clean Code Rules (Heuristics Index)

When reviewing, writing, or refactoring code, cite violations explicitly by their canonical Rule ID:

### Comments (C1–C5)
- **C1**: No metadata in comments (use Git log/blame).
- **C2**: Delete obsolete comments immediately.
- **C3**: No redundant comments (don't restate what the code clearly says).
- **C4**: Write comments well if you must (explain *why*, not *what*).
- **C5**: **Never commit commented-out code** (delete it; Git remembers).

### Environment (E1–E2)
- **E1**: One command to build the project.
- **E2**: One command to run all unit tests.

### Functions (F1–F4)
- **F1**: Maximum 3 arguments (use objects, structs, or dataclasses for more).
- **F2**: No output arguments (return values from functions).
- **F3**: **No flag arguments** (boolean flags mean the function does two things; split it into two functions).
- **F4**: Delete dead or uncalled functions.

### General Design (G1–G36)
- **G1**: One language per source file.
- **G2**: Implement expected behavior.
- **G3**: Handle boundary conditions and edge cases.
- **G4**: Don't override safeties or bypass type checks.
- **G5**: **DRY (Don't Repeat Yourself)** — no duplication.
- **G6**: Consistent abstraction levels within each abstraction layer.
- **G7**: Base classes don't know their derived children.
- **G8**: Minimize public interface (narrowest visibility possible).
- **G9**: Delete dead code, unreachable branches, and unused variables.
- **G10**: Variables declared near usage.
- **G11**: Be consistent across naming, patterns, and conventions.
- **G12**: Remove clutter and unused imports.
- **G13**: No artificial coupling between independent concepts.
- **G14**: No **Feature Envy** (methods using data from another class more than their own).
- **G15**: No selector arguments that drive divergent behaviors.
- **G16**: No obscured intent (code must speak for itself).
- **G17**: Code where expected (place code where the reader naturally expects to find it).
- **G18**: Prefer instance methods over static methods when behavior depends on state.
- **G19**: Use explanatory variables to clarify complex expressions.
- **G20**: Function names say what they do (including side effects).
- **G21**: Understand the algorithm before implementing it.
- **G22**: Make dependencies physical (don't rely on ambient state or implicit ordering).
- **G23**: **Polymorphism over if/else**: Use polymorphic types/strategies instead of sprawling conditional branches.
- **G24**: Follow established language conventions and style guides (PEP 8, ESLint).
- **G25**: **Named constants, not magic numbers or magic strings**.
- **G26**: Be precise (choose types, ranges, and precision deliberately).
- **G27**: Structure over convention.
- **G28**: Encapsulate conditionals into boolean helper methods with descriptive names.
- **G29**: Avoid negative conditionals (prefer `if is_active` over `if not is_inactive`).
- **G30**: **Functions do ONE thing** (Single Responsibility Principle at function scale).
- **G31**: Make temporal coupling explicit (if B must follow A, pass A's output as B's argument).
- **G32**: Don't be arbitrary; adhere to existing structure and naming patterns.
- **G33**: Encapsulate boundary conditions in variables or dedicated checks.
- **G34**: **One abstraction level per function (SLAP)**.
- **G35**: Config at high levels.
- **G36**: **Law of Demeter (one dot)**: Talk only to immediate collaborators; avoid train wrecks like `a.getB().getC().getValue()`.

### Naming (N1–N7)
- **N1**: Choose descriptive names revealing intent.
- **N2**: Names at appropriate abstraction level.
- **N3**: Use standard nomenclature and ubiquitous domain terms.
- **N4**: Unambiguous names leaving no doubt about purpose.
- **N5**: Name length matches scope (longer names for broader scope, concise for small loop scopes).
- **N6**: No encodings, prefixes, or Hungarian notation (`strName`, `arrList`).
- **N7**: Names describe side effects and mutations.

### Language-Specific Rules (P1–P3, TS1–TS3)
- **P1 (Python)**: No wildcard imports (`from module import *`).
- **P2 (Python)**: Use `Enum` or `Literal` types, not magic constants.
- **P3 (Python)**: Type hints on public interfaces.
- **TS1 (TypeScript)**: Keep imports explicit and stable.
- **TS2 (TypeScript)**: Use enums or literal unions, not magic constants.
- **TS3 (TypeScript)**: Type public interfaces and avoid `any` at boundaries.

### Tests (T1–T9)
- **T1**: Test everything that could break.
- **T2**: Use coverage tools as a diagnostic.
- **T3**: Don't skip trivial tests.
- **T4**: Ignored test = ambiguity question.
- **T5**: **Test boundary conditions** (empty, zero, null, limits).
- **T6**: Exhaustively test near bugs.
- **T7**: Look for patterns in failures.
- **T8**: Check coverage when debugging.
- **T9**: **Tests must be fast (< 100ms each)**.

---

## 4. Anti-Patterns Quick Guide (Don't → Do)

| ❌ Don't | ✅ Do | Violated Rule |
|:---|:---|:---:|
| Comment every single line | Delete obvious comments; let clean code explain itself | **C3** |
| `from utils import *` | Explicit named imports: `from utils import format_date` | **P1 / TS1** |
| Hardcoded numbers: `if timeout > 86400:` | Named constant: `SECONDS_PER_DAY = 86400` | **G25** |
| Boolean flag argument: `def save(user, notify=True):` | Separate functions: `save(user)` and `save_and_notify(user)` | **F3, G30** |
| Train wreck: `user.get_company().get_billing().charge()` | Delegate method: `user.charge_billing()` | **G36** |
| God function spanning 100+ lines | Split by responsibility into 5-15 line functions at single SLAP | **F1, G30, G34** |
| Deeply nested `if-else` blocks (4+ levels) | Guard clauses with early returns | **G28, G34** |
| Vague names: `data`, `info`, `temp`, `res`, `mgr` | Specific domain names: `pending_invoices`, `user_profile` | **N1, N4** |

---

## 5. Bộ Công Cụ Scripts Phân Tích Tĩnh (Zero External Dependencies)

The skill includes offline, dependency-free Python scripts inside `scripts/` (using Python's standard library `ast`, `re`, `json`, `pathlib`):

```bash
# 1. Detect project stack, frameworks, and verification commands
python .agents/skills/clean-code/scripts/detect_stack.py

# 2. Map structure, detect misplaced files, God files, and naming clashes
python .agents/skills/clean-code/scripts/map_structure.py --path <directory>

# 3. Check for architectural layer violations and illegal inward imports
python .agents/skills/clean-code/scripts/check_boundaries.py

# 4. Scan entire repository health and report findings
python .agents/skills/clean-code/scripts/scan_repo.py
```

*Note: All scripts run locally, write only to `.clean/` (when `--write` is specified), and never make network requests.*

---

## 6. Khả Năng Mở Rộng: 21 Ngôn Ngữ & 27 Frameworks

When working in a specific stack, consult the specialized reference pack in `references/`:

### Languages (21 Packs in `references/languages/`)
- `python.md`, `typescript.md`, `javascript.md`, `go.md`, `rust.md`, `java.md`, `csharp.md`, `cpp.md`, `c.md`, `php.md`, `ruby.md`, `swift.md`, `kotlin.md`, `dart.md`, `scala.md`, `r.md`, `shell.md`, `powershell.md`, `objective-c.md`, `css.md`, `sass.md`.

### Frameworks (27 Packs in `references/frameworks/`)
- **Backend / Microservices**: `fastapi.md`, `django.md`, `flask.md`, `express.md`, `nestjs.md`, `spring.md`, `aspnet-core.md`, `laravel.md`, `symfony.md`, `rails.md`, `gin-beego.md`, `ktor.md`.
- **Frontend / Fullstack**: `react.md`, `nextjs.md`, `vue-nuxt.md`, `angular.md`, `svelte.md`, `tailwind.md`, `strapi.md`, `drupal.md`, `wordpress.md`.
- **Mobile & Desktop**: `flutter.md`, `swiftui-uikit.md`, `jetpack-compose.md`, `unity.md`.
- **Machine Learning**: `pytorch.md`, `tensorflow.md`.
- **Index**: See `references/framework-map.md` for framework selection and scope adaptation.

---

## 7. Deep-Dive Design Guides in `references/`

For comprehensive theory, anti-patterns, and realistic before/after code transformations, read the dedicated deep-dive guides:

| Design Topic | Reference Guide | Key Highlights |
|:---|:---|:---|
| **SOLID Principles** | `references/solid-principles.md` | SRP, OCP, LSP, ISP, DIP evaluated as systemic design lenses |
| **Function Design** | `references/function-design.md` | Functions as units of thought, SLAP, CQS, 5-15 line target |
| **Error Handling** | `references/error-handling.md` | Separation of happy path, contextual exceptions, eliminating `null` |
| **Dependency Management** | `references/dependency-management.md` | Explicit constructor injection, Stable Dependencies, DIP at scale |
| **Code Smells** | `references/code-smells.md` | Smells as immune system, Feature Envy, Primitive Obsession, Data Clumps |
| **Naming Conventions** | `references/naming-conventions.md` | Domain-driven naming, searchable names, maintaining truthfulness |
| **Refactoring Patterns** | `references/refactoring-patterns.md` | Behavior-preserving transformation, Characterization Tests, Rule of 3 |
| **Testing Principles** | `references/testing-principles.md` | Testing Pyramid (Unit/Integration/E2E), testing behavior vs mocks |

---

## 8. AI Behavior & Reporting Standards

- **Always respect the Supreme Immutable Rule first**: Prioritize simplicity, comprehensibility, runnability, testability, and explainability above all else. Never artificially splinter code into nested calls or deep inheritance trees in the name of "clean code".
- When reviewing code, identify violations by rule number (e.g., "G5 violation: duplicated logic", "F3 violation: boolean flag argument").
- When fixing or editing code, report what was fixed with citations (e.g., "Fixed: extracted magic number to `SECONDS_PER_DAY` (G25)").
- When writing new code, adhere strictly to the 6-step Operating Loop, placing code by architectural role and verifying with tests before declaring completion.
