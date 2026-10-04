# Code Smells — Clean Code

You are an expert in identifying and fixing code smells for writing clean, maintainable code.

## Core Philosophy

Code smells are the immune system's early warning signals. They do not indicate that the code is broken today — tests pass, features work — but they reveal structural weaknesses that will make the code increasingly expensive to change tomorrow. The discipline of recognizing smells is about developing an instinct for design friction: the feeling that something is harder to understand, modify, or extend than it should be.

The value of cataloging smells is not to create a checklist for mechanical compliance but to build a shared vocabulary within a team. When a reviewer says "this looks like Feature Envy," everyone immediately understands the nature of the concern, the likely root cause, and the family of refactorings that would address it. This shared language accelerates code review, reduces subjective disagreement, and focuses discussions on design intent rather than surface-level style.

Not every smell demands immediate action. The decision to refactor should be driven by change frequency, not smell severity. A god class in a module that has not been touched in two years is a lower priority than mild duplication in a file that is modified every sprint. Smell awareness paired with pragmatic prioritization — refactoring the code you are already changing — is what turns code quality from an abstract ideal into a sustainable daily practice.

## Anti-Patterns

- **Ignoring smells because "the code works"**: Functional correctness is a necessary but insufficient measure of code quality. Smells accumulate as silent technical debt that compounds with every change, making future work slower and riskier.

- **Refactoring smells without test coverage**: Changing the structure of code without a safety net of tests is a recipe for introducing regressions. Always establish adequate test coverage before refactoring, even if that means writing characterization tests first.

- **Treating the symptom instead of the disease**: Extracting a few methods from a 500-line god class does not fix the underlying single-responsibility violation. Follow the smell to its root cause and address the design problem, not just the surface indicator.

- **Applying smell detection dogmatically by metrics alone**: A function with 25 lines is not automatically a Long Method, and a class with two responsibilities is not necessarily violating SRP. Smells are heuristics that require human judgment about context, cohesion, and change frequency.

- **Becoming blind to your own codebase's smells**: Teams that work in the same codebase daily develop tolerance for its quirks. Rotate reviewers, invite fresh-eyes reviews from outside the team, and use static analysis tools to surface smells that familiarity has rendered invisible.

## Overview

A code smell is a surface indication that usually corresponds to a deeper problem in the system. Code smells are not bugs — the code works — but they signal design weaknesses that increase the cost of change, invite bugs, and make the codebase harder to understand. Learning to recognize smells is the first step toward systematic refactoring.

## Core Principles

- **Smells are heuristics, not rules**: A smell indicates a potential problem. Context determines whether action is needed.
- **Follow the smell to the root cause**: The smell is a symptom. The refactoring should address the underlying design issue.
- **Fix smells incrementally**: Tackle one smell at a time, verify tests pass, then move on.
- **Prevention over cure**: Code review and design discussion prevent smells from entering the codebase in the first place.

## Implementation Patterns

### Long Method

A function that has grown beyond 20 lines and mixes multiple levels of abstraction.

Before:

```python
def generate_invoice(order):
    lines = []
    subtotal = 0
    for item in order.items:
        line_total = item.price * item.quantity
        discount = 0
        if item.quantity > 10:
            discount = line_total * 0.1
        elif item.quantity > 5:
            discount = line_total * 0.05
        line_total -= discount
        subtotal += line_total
        lines.append(f"{item.name}: ${line_total:.2f}")
    tax = subtotal * 0.08
    total = subtotal + tax
    header = f"Invoice for {order.customer.name}\nDate: {datetime.now()}\n"
    body = "\n".join(lines)
    footer = f"\nSubtotal: ${subtotal:.2f}\nTax: ${tax:.2f}\nTotal: ${total:.2f}"
    return header + body + footer
```

After — extract methods by responsibility:

```python
def generate_invoice(order):
    lines, subtotal = calculate_line_items(order.items)
    tax = calculate_tax(subtotal)
    total = subtotal + tax
    return format_invoice(order.customer.name, lines, subtotal, tax, total)

def calculate_line_items(items):
    lines = []
    subtotal = 0
    for item in items:
        line_total = compute_discounted_price(item)
        subtotal += line_total
        lines.append(f"{item.name}: ${line_total:.2f}")
    return lines, subtotal

def compute_discounted_price(item):
    base = item.price * item.quantity
    discount_rate = 0.1 if item.quantity > 10 else 0.05 if item.quantity > 5 else 0
    return base * (1 - discount_rate)
```

### Feature Envy

A method that uses data from another class more than its own.

Before:

```typescript
class OrderPrinter {
  printTotal(order: Order) {
    const subtotal = order.items.reduce(
      (sum, i) => sum + i.price * i.quantity,
      0,
    );
    const tax = subtotal * order.taxRate;
    console.log(`Total: ${subtotal + tax}`);
  }
}
```

After — move the logic to where the data lives:

```typescript
class Order {
  getTotal(): number {
    const subtotal = this.items.reduce(
      (sum, i) => sum + i.price * i.quantity,
      0,
    );
    return subtotal + subtotal * this.taxRate;
  }
}

class OrderPrinter {
  printTotal(order: Order) {
    console.log(`Total: ${order.getTotal()}`);
  }
}
```

### Primitive Obsession

Using primitives instead of small domain objects.

Before:

```python
def send_money(from_account: str, to_account: str, amount: float, currency: str):
    ...
```

After:

```python
@dataclass(frozen=True)
class AccountId:
    value: str

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)

def send_money(from_account: AccountId, to_account: AccountId, amount: Money):
    ...
```

### Data Clumps

Groups of data that always appear together.

Before:

```javascript
function distanceBetween(x1, y1, z1, x2, y2, z2) { ... }
function translate(x, y, z, dx, dy, dz) { ... }
```

After:

```javascript
class Point3D {
  constructor(x, y, z) { this.x = x; this.y = y; this.z = z; }
}

function distanceBetween(a: Point3D, b: Point3D) { ... }
function translate(point: Point3D, delta: Point3D) { ... }
```

## Best Practices

- Catalog of smells to watch for: Long Method, Large Class, Feature Envy, Data Clumps, Primitive Obsession, Switch Statements, Parallel Inheritance, Lazy Class, Speculative Generality, Temporary Field, Message Chains, Middle Man, Divergent Change, Shotgun Surgery
- Use static analysis tools (linters, complexity analyzers) to detect smells automatically
- Track smell density over time as a codebase health metric
- Pair code review with smell identification to build team awareness

## Common Pitfalls

- **Ignoring smells because the code works**: Working code with smells accumulates technical debt silently
- **Refactoring without tests**: Fixing a smell without test coverage risks introducing regressions
- **Treating the symptom, not the cause**: Extracting a method from a god class does not fix the god class
- **Smell blindness**: Teams acclimate to their own code smells. Rotate reviewers and use fresh-eyes reviews
- **Dogmatic smell counting**: Not every smell needs immediate attention. Prioritize by how often the code changes
