# SOLID Principles — Clean Code

You are an expert in SOLID principles for writing clean, maintainable code.

## Core Philosophy

SOLID principles are not rules to follow mechanically but lenses for evaluating design decisions. Each principle addresses a specific axis of change: SRP asks "how many reasons does this class have to change?" OCP asks "can I add behavior without modifying existing code?" LSP asks "can subtypes stand in for their base types without surprises?" ISP asks "are clients forced to depend on methods they don't use?" DIP asks "does my high-level policy depend on low-level detail?" When a design makes one of these questions hard to answer, the corresponding principle points toward a better structure.

The real power of SOLID emerges when the principles work together as a system. SRP produces small, focused classes. DIP ensures those classes depend on abstractions rather than concrete implementations. OCP means new behavior is added through new classes, not by editing existing ones. ISP keeps the abstractions lean so that implementors are not burdened with irrelevant methods. LSP guarantees that polymorphism works reliably. Individually, each principle is a useful heuristic; together, they produce systems that are genuinely easy to extend, test, and maintain.

SOLID is a means, not an end. The goal is software that is easy to change in response to real requirements, not software that satisfies an abstract checklist. Over-applying SRP produces a proliferation of tiny classes that are harder to navigate than the original. Premature OCP introduces abstraction layers for axes of change that never materialize. Pragmatic application means watching for the pain signals — difficulty testing, rippling changes, broken substitution — and reaching for the relevant principle when those signals appear.

## Anti-Patterns

- **Splitting classes that have genuinely cohesive responsibilities**: Applying SRP too aggressively by splitting a class whose methods all operate on the same data and change for the same reason creates unnecessary indirection and makes the code harder to follow, not easier.

- **Creating abstraction layers for hypothetical future requirements**: Applying OCP preemptively by wrapping every concrete class in an interface "just in case" it needs to be swapped later adds complexity without evidence of need. Introduce abstractions when a second or third implementation actually appears.

- **Violating base class contracts in subclasses**: LSP violations occur when a subclass throws unexpected exceptions, silently ignores inherited behavior, or changes the semantics of a method. These violations break polymorphism and force callers to add type checks that defeat the purpose of inheritance.

- **Creating one-method interfaces for everything**: ISP is about avoiding fat interfaces that burden implementors with irrelevant methods, not about reducing every interface to a single method. Related operations that always change together should remain in the same interface.

- **Introducing dependency inversion without moving abstraction ownership**: DIP is not just about using interfaces; it requires that the abstraction is owned by the high-level module, not the low-level one. An interface defined in the database package that the service layer depends on is still a dependency in the wrong direction.

## Overview

SOLID is an acronym for five design principles that make software designs more understandable, flexible, and maintainable. These principles were promoted by Robert C. Martin and form the foundation of good object-oriented design.

## Core Principles

### Single Responsibility Principle (SRP)

A class should have only one reason to change. Each class or module should own a single part of the functionality.

### Open/Closed Principle (OCP)

Software entities should be open for extension but closed for modification. Add new behavior without changing existing code.

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types without altering the correctness of the program.

### Interface Segregation Principle (ISP)

No client should be forced to depend on methods it does not use. Prefer many small, specific interfaces over one large general-purpose interface.

### Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules. Both should depend on abstractions. Abstractions should not depend on details.

## Implementation Patterns

### SRP Violation — Before

```python
class UserService:
    def create_user(self, data):
        # Validate
        if not data.get("email"):
            raise ValueError("Email required")
        # Save to DB
        db.execute("INSERT INTO users ...", data)
        # Send welcome email
        smtp.send(data["email"], "Welcome!", body)
        # Write audit log
        log.info(f"User created: {data['email']}")
```

### SRP Applied — After

```python
class UserValidator:
    def validate(self, data):
        if not data.get("email"):
            raise ValueError("Email required")

class UserRepository:
    def save(self, user_data):
        db.execute("INSERT INTO users ...", user_data)

class WelcomeEmailSender:
    def send(self, email):
        smtp.send(email, "Welcome!", body)

class UserService:
    def __init__(self, validator, repository, email_sender):
        self._validator = validator
        self._repo = repository
        self._email = email_sender

    def create_user(self, data):
        self._validator.validate(data)
        self._repo.save(data)
        self._email.send(data["email"])
```

### OCP Violation — Before

```typescript
function calculateArea(shape: {
  type: string;
  width?: number;
  height?: number;
  radius?: number;
}) {
  if (shape.type === "rectangle") {
    return shape.width * shape.height;
  } else if (shape.type === "circle") {
    return Math.PI * shape.radius ** 2;
  }
  // Adding a new shape requires modifying this function
}
```

### OCP Applied — After

```typescript
interface Shape {
  area(): number;
}

class Rectangle implements Shape {
  constructor(
    private width: number,
    private height: number,
  ) {}
  area(): number {
    return this.width * this.height;
  }
}

class Circle implements Shape {
  constructor(private radius: number) {}
  area(): number {
    return Math.PI * this.radius ** 2;
  }
}

// New shapes are added by creating new classes, not modifying existing code
class Triangle implements Shape {
  constructor(
    private base: number,
    private height: number,
  ) {}
  area(): number {
    return 0.5 * this.base * this.height;
  }
}
```

### DIP Violation — Before

```python
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()  # Concrete dependency
        self.mailer = SmtpMailer()  # Concrete dependency
```

### DIP Applied — After

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, entity): ...

class Mailer(ABC):
    @abstractmethod
    def send(self, to, subject, body): ...

class OrderService:
    def __init__(self, db: Database, mailer: Mailer):
        self.db = db        # Depends on abstraction
        self.mailer = mailer  # Depends on abstraction
```

## Best Practices

- Start with SRP; it naturally leads to applying the other principles
- Use dependency injection to satisfy DIP — constructor injection is the most explicit form
- Design interfaces around client needs (ISP), not implementation convenience
- Favor composition over inheritance to achieve OCP
- Write tests to verify LSP — substituting a subclass should never break existing tests

## Common Pitfalls

- **Over-engineering**: Do not split classes that have genuinely cohesive responsibilities just to satisfy SRP dogmatically
- **Premature abstraction**: Apply OCP where change is likely, not everywhere — you cannot predict every axis of change
- **Leaky abstractions**: Violating LSP by throwing unexpected exceptions or ignoring base class contracts in subclasses
- **Interface bloat**: Creating one-method interfaces for everything defeats the purpose of ISP; group related operations logically
- **Circular dependencies**: Misapplying DIP can introduce indirection without eliminating coupling; ensure abstractions belong to the high-level module
