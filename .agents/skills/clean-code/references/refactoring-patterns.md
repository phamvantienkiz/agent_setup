# Refactoring Patterns — Clean Code

You are an expert in refactoring patterns for writing clean, maintainable code.

## Core Philosophy

Refactoring is the practice of improving code structure without changing its behavior — and the key word is "without." Every refactoring must be behavior-preserving, which means it must be verifiable by tests. This is not a suggestion; it is a prerequisite. Refactoring without tests is not refactoring — it is rewriting, with all the risk that implies. The discipline of small, test-verified structural changes is what makes refactoring safe and sustainable.

The best time to refactor is when you are already changing the code for another reason. The Boy Scout Rule — leave the code cleaner than you found it — turns refactoring from a separate, schedulable activity into a continuous practice embedded in daily work. When you are adding a feature and notice a long method, extract it. When you are fixing a bug and see duplicated logic, consolidate it. This incremental approach avoids the need for risky "refactoring sprints" and keeps technical debt from accumulating.

Refactoring should be guided by concrete smells and design feedback, not by speculative improvement. Refactoring toward a design pattern because the pattern is elegant, refactoring a module that is stable and never changes, or rewriting code that is merely unfamiliar but functional — these are traps that consume time without delivering value. The strongest signal that refactoring is needed is friction: difficulty adding a feature, difficulty understanding a section of code, or difficulty writing a test. Let the pain point, not the aesthetic preference, determine where to invest.

## Anti-Patterns

- **Big-bang refactoring without incremental steps**: Attempting to restructure an entire module or subsystem in a single effort leads to long-lived branches, merge conflicts, and broken behavior that is difficult to isolate. Always decompose large refactorings into a series of small, individually testable changes.

- **Mixing refactoring with feature changes in the same commit**: When a commit contains both structural changes and behavioral changes, it becomes impossible to determine whether a test failure is caused by the refactoring or the new feature. Separate them into distinct commits or PRs.

- **Refactoring without tests or writing tests after the refactoring**: If tests do not exist before the refactoring begins, there is no way to verify that behavior was preserved. Write characterization tests that capture the current behavior first, then refactor with confidence.

- **Gold-plating stable code that rarely changes**: Refactoring a module that has been untouched for a year and is unlikely to change adds cost without value. Focus refactoring effort on code that is actively being modified, where the investment pays off immediately in reduced friction.

- **Refactoring toward a pattern before the need is clear**: Introducing a Strategy pattern, a Builder, or a Factory prematurely adds indirection and complexity. Apply patterns when you have three or more concrete cases that share a structure, not when you anticipate future cases that may never materialize.

## Overview

Refactoring is the process of restructuring existing code without changing its external behavior. The goal is to improve nonfunctional attributes: readability, reduced complexity, improved maintainability, and better extensibility. Each refactoring should be a small, safe, testable step.

## Core Principles

- **Preserve behavior**: Every refactoring must keep tests green. If no tests exist, write characterization tests first.
- **Small steps**: Make one change at a time. Commit frequently so each step is easily reversible.
- **Follow the smells**: Let code smells guide which refactoring to apply rather than refactoring speculatively.
- **Refactor on a separate axis from feature work**: Do not mix behavior changes with structural improvements.

## Implementation Patterns

### Extract Method

Pull a coherent block of code into its own named function.

Before:

```python
def print_report(invoice):
    print("=== Invoice Report ===")
    # calculate total
    total = 0
    for item in invoice.items:
        total += item.price * item.quantity
        if item.taxable:
            total += item.price * item.quantity * 0.1
    print(f"Total: {total}")
```

After:

```python
def calculate_total(items):
    total = 0
    for item in items:
        subtotal = item.price * item.quantity
        tax = subtotal * 0.1 if item.taxable else 0
        total += subtotal + tax
    return total

def print_report(invoice):
    print("=== Invoice Report ===")
    total = calculate_total(invoice.items)
    print(f"Total: {total}")
```

### Replace Conditional with Polymorphism

Before:

```typescript
function getSpeed(vehicle: Vehicle): number {
  switch (vehicle.type) {
    case "car":
      return vehicle.horsepower * 0.5;
    case "bicycle":
      return vehicle.gearRatio * 3;
    case "airplane":
      return vehicle.thrust / vehicle.weight;
    default:
      throw new Error("Unknown vehicle");
  }
}
```

After:

```typescript
interface Vehicle {
  getSpeed(): number;
}

class Car implements Vehicle {
  constructor(private horsepower: number) {}
  getSpeed(): number {
    return this.horsepower * 0.5;
  }
}

class Bicycle implements Vehicle {
  constructor(private gearRatio: number) {}
  getSpeed(): number {
    return this.gearRatio * 3;
  }
}

class Airplane implements Vehicle {
  constructor(
    private thrust: number,
    private weight: number,
  ) {}
  getSpeed(): number {
    return this.thrust / this.weight;
  }
}
```

### Introduce Parameter Object

Before:

```python
def create_event(title, start_date, end_date, location, organizer, max_attendees):
    ...
```

After:

```python
@dataclass
class EventConfig:
    title: str
    start_date: datetime
    end_date: datetime
    location: str
    organizer: str
    max_attendees: int

def create_event(config: EventConfig):
    ...
```

### Replace Magic Numbers with Named Constants

Before:

```javascript
if (password.length < 8) { ... }
if (retries > 3) { ... }
setTimeout(callback, 86400000);
```

After:

```javascript
const MIN_PASSWORD_LENGTH = 8;
const MAX_RETRIES = 3;
const ONE_DAY_MS = 24 * 60 * 60 * 1000;

if (password.length < MIN_PASSWORD_LENGTH) { ... }
if (retries > MAX_RETRIES) { ... }
setTimeout(callback, ONE_DAY_MS);
```

### Decompose Conditional

Before:

```python
if date.month >= 6 and date.month <= 8 and not is_holiday(date):
    rate = base_rate * 1.2
else:
    rate = base_rate
```

After:

```python
def is_summer(date):
    return 6 <= date.month <= 8

def is_working_day(date):
    return not is_holiday(date)

if is_summer(date) and is_working_day(date):
    rate = base_rate * 1.2
else:
    rate = base_rate
```

## Best Practices

- Always have passing tests before you start refactoring
- Use version control commits to checkpoint each refactoring step
- Rename variables and functions as you go to reflect their true purpose
- Use IDE refactoring tools when available — they automate rename, extract, and inline operations safely
- Refactor toward design patterns only when the pattern clearly fits the problem

## Common Pitfalls

- **Big-bang refactoring**: Attempting to rewrite large sections at once without incremental steps leads to breakage
- **Refactoring without tests**: Changing structure without behavioral verification risks introducing regressions
- **Mixing refactoring with feature changes**: Makes it impossible to isolate the cause when something breaks
- **Gold plating**: Refactoring code that works, is readable, and will not change again adds cost without value
- **Ignoring performance implications**: Some refactorings (e.g., extracting hot-loop bodies) can affect performance — measure if the code is performance-sensitive
