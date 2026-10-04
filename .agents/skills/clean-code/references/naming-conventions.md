# Naming Conventions — Clean Code

You are an expert in naming conventions for writing clean, maintainable code.

## Core Philosophy

Names are the primary interface between a developer's intent and every future reader of the code. A well-chosen name eliminates the need for a comment, makes the code's purpose self-evident, and reduces the cognitive load required to understand a module, a function, or a variable. Naming is not a cosmetic concern — it is a design activity that directly affects how easily the codebase can be understood, searched, discussed, and changed.

The best names come from the problem domain, not from implementation details. When a financial application uses `ledgerEntry` instead of `row`, `accrualPeriod` instead of `dateRange`, and `reconcile` instead of `process`, the code speaks the same language as the business. This alignment means domain experts can read the code and verify its correctness, new developers can map concepts to documentation, and the gap between requirements and implementation stays narrow.

Good naming requires ongoing investment, not a one-time decision. As understanding of the domain deepens and the system evolves, names that were once clear may become misleading. A variable named `users` that now holds only active subscribers, a function named `process` that now performs validation, transformation, and persistence — these names have drifted from their meaning. Renaming is not busywork; it is the maintenance of truthfulness in the code. Teams that fear renaming accumulate a codebase where names are lies, and lies compound into confusion.

## Anti-Patterns

- **Using generic names like `data`, `info`, `temp`, `result`, or `manager`**: These names carry almost no semantic content. They force the reader to inspect the implementation to understand what the variable holds or what the class does. Every name should communicate its specific role in the domain.

- **Inconsistent vocabulary for the same concept**: Using `fetch`, `get`, `retrieve`, and `load` interchangeably across a codebase for the same operation forces readers to wonder whether the different verbs imply different behaviors. Pick one term per concept and use it consistently throughout the project.

- **Encoding type information into names**: Hungarian notation (`strName`, `lstUsers`, `iCount`) adds noise that becomes actively misleading when types change during refactoring. Let the type system communicate types; let names communicate intent.

- **Abbreviating names to save keystrokes**: Short names like `mgr`, `ctx`, `btn`, `evt`, or `cfg` save a few characters but cost minutes of comprehension every time a new reader encounters them. The only acceptable abbreviations are those universally understood in the domain (`url`, `id`, `http`).

- **Keeping misleading names to avoid merge conflicts**: Developers sometimes tolerate a name that no longer reflects its purpose because renaming would create conflicts in other branches. This prioritizes short-term convenience over long-term clarity. Dedicate small, focused PRs specifically to renaming.

## Overview

Naming is one of the hardest and most important aspects of programming. Good names reduce the need for comments, make code self-documenting, and lower the cognitive load required to understand a codebase. A well-chosen name communicates intent, scope, and type at a glance.

## Core Principles

- **Reveal intent**: A name should tell you why something exists, what it does, and how it is used.
- **Avoid disinformation**: Do not use names that mean something different in common usage or that are misleadingly similar.
- **Make meaningful distinctions**: If two things are different, their names must make the difference obvious.
- **Use pronounceable names**: Names you cannot say aloud are harder to discuss and remember.
- **Use searchable names**: Single-letter names and numeric constants are difficult to locate in a codebase.
- **Match the domain language**: Use terms from the problem domain so domain experts and developers share a vocabulary.

## Implementation Patterns

### Variables — Nouns That Describe Content

Before:

```python
d = 7
t = []
flag = True
```

After:

```python
days_until_deadline = 7
overdue_tasks = []
is_authenticated = True
```

### Functions — Verbs That Describe Action

Before:

```javascript
function data(id) { ... }
function process(items) { ... }
function handle(event) { ... }
```

After:

```javascript
function fetchUserById(id) { ... }
function calculateShippingCost(items) { ... }
function dispatchNotificationEvent(event) { ... }
```

### Booleans — Questions That Return Yes/No

Before:

```typescript
let open = true;
let status = false;
let read = true;
```

After:

```typescript
let isModalOpen = true;
let hasPermission = false;
let wasMessageRead = true;
```

### Classes — Nouns That Describe Entities

Before:

```python
class Manager:
    ...
class Processor:
    ...
class Data:
    ...
```

After:

```python
class PaymentGateway:
    ...
class MarkdownParser:
    ...
class CustomerProfile:
    ...
```

### Constants — Screaming Case for Fixed Values

Before:

```javascript
const val = 3.14159;
const t = 30000;
```

After:

```javascript
const PI = 3.14159;
const REQUEST_TIMEOUT_MS = 30000;
```

### Scope-Appropriate Length

```python
# Short scope — short name is fine
for i in range(10):
    print(i)

# Broad scope — descriptive name required
active_subscription_count = db.query(
    "SELECT COUNT(*) FROM subscriptions WHERE status = 'active'"
)
```

## Best Practices

- Name length should be proportional to the scope in which the name lives
- Use consistent conventions within a project: `camelCase` for JS/TS variables, `snake_case` for Python, `PascalCase` for classes
- Avoid prefixes like `str`, `lst`, `obj` — the type system or context should convey type
- Use domain-specific terms: `invoice`, `ledger`, `prescription` rather than generic `item`, `record`, `object`
- When renaming, use IDE refactoring tools to update all references automatically
- Avoid abbreviations unless they are universally understood (`url`, `id`, `http`)

## Common Pitfalls

- **Generic names**: `data`, `info`, `temp`, `result`, `manager`, `handler`, `utils` — these names carry almost no information
- **Encodings and prefixes**: Hungarian notation (`strName`, `iCount`) adds noise and becomes wrong when types change
- **Misleading names**: A list named `accountList` that is actually a set, or a function named `check` that also modifies state
- **Inconsistent vocabulary**: Using `fetch`, `get`, `retrieve`, and `load` interchangeably for the same concept across a codebase
- **Context-free names**: A variable called `state` is meaningful inside a `StateMachine` class but ambiguous at module level
- **Fear of renaming**: Developers often keep bad names to avoid merge conflicts. Dedicate small PRs specifically to renaming
