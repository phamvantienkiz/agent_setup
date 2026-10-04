# Dependency Management — Clean Code

You are an expert in dependency management and decoupling for writing clean, maintainable code.

## Core Philosophy

Clean dependency management is about making the invisible visible. Every piece of code depends on something — other classes, libraries, services, configuration — and the quality of a system is largely determined by how these relationships are structured. When dependencies are explicit, minimal, and flow in a single direction, the system is easy to test, easy to change, and easy to understand. When they are hidden, circular, or promiscuous, every change risks an unpredictable cascade of breakage.

The deepest insight in dependency management is the Dependency Inversion Principle applied at scale: high-level policy should never depend on low-level detail. Business logic should not know whether data comes from PostgreSQL or an in-memory store, whether notifications go through email or SMS, or whether logging writes to a file or a cloud service. When the direction of dependency is correct — details depend on abstractions owned by the domain — the core of the system becomes stable, portable, and testable without infrastructure.

Explicit dependencies are a form of honesty. A constructor that declares exactly what it needs tells every reader, tester, and future maintainer exactly what the class depends on. Hidden dependencies — global singletons, service locators, ambient context — are lies of omission. They make code appear simpler than it is, and they exact their cost in debugging sessions where the real dependency graph must be reverse-engineered from runtime behavior rather than read from the source.

## Anti-Patterns

- **Hiding dependencies behind global state or service locators**: When a class fetches its dependencies from a global registry or static accessor, those dependencies become invisible to callers and impossible to substitute in tests without manipulating shared state.

- **Allowing circular dependencies between modules**: Circular imports are a structural symptom of tangled responsibilities. They make it impossible to reason about initialization order, break lazy-loading strategies, and signal that two modules should either be merged or have their shared concern extracted into a third.

- **Injecting too many dependencies into a single constructor**: A class that requires eight or ten injected dependencies is almost certainly violating the Single Responsibility Principle. The excessive injection count is a smell that the class should be split into smaller, more focused collaborators.

- **Leaking internal implementation types through public APIs**: When a module's public interface exposes types from its internal dependencies — returning a Prisma model from a service method, for example — every consumer becomes transitively coupled to that implementation detail and must change when it changes.

- **Depending on volatile infrastructure from stable domain logic**: Core business rules that directly import HTTP frameworks, database drivers, or cloud SDKs become untestable without those systems running and impossible to migrate without rewriting business logic. Always wrap infrastructure behind domain-owned abstractions.

## Overview

Dependencies define the relationships between components in a system. Poorly managed dependencies create tight coupling, making code hard to test, hard to change, and fragile. Clean dependency management means making dependencies explicit, minimizing coupling, and ensuring that changes in one module do not ripple through the entire system.

## Core Principles

- **Depend on abstractions, not concretions**: Program to interfaces, not implementations.
- **Make dependencies explicit**: Constructor injection is preferred over hidden service locators, global state, or implicit singletons.
- **Minimize coupling**: Each module should know as little as possible about other modules.
- **Maximize cohesion**: Things that change together should live together.
- **Stable dependencies principle**: Depend in the direction of stability — volatile modules should depend on stable ones, not the other way around.

## Implementation Patterns

### Hidden Dependency — Before

```python
class ReportGenerator:
    def generate(self, data):
        db = DatabaseConnection.get_instance()  # Hidden dependency
        template = TemplateEngine()              # Hidden dependency
        results = db.query("SELECT ...")
        return template.render("report.html", results)
```

### Explicit Dependency Injection — After

```python
class ReportGenerator:
    def __init__(self, db: DatabaseConnection, template_engine: TemplateEngine):
        self._db = db
        self._template = template_engine

    def generate(self, data):
        results = self._db.query("SELECT ...")
        return self._template.render("report.html", results)
```

### Tight Coupling to Implementation — Before

```typescript
class OrderService {
  private emailer = new SmtpEmailer();
  private logger = new FileLogger("/var/log/orders.log");

  async placeOrder(order: Order) {
    await this.saveOrder(order);
    this.emailer.send(order.customerEmail, "Order placed");
    this.logger.log(`Order ${order.id} placed`);
  }
}
```

### Interface-Based Decoupling — After

```typescript
interface Notifier {
  notify(recipient: string, message: string): Promise<void>;
}

interface Logger {
  log(message: string): void;
}

class OrderService {
  constructor(
    private notifier: Notifier,
    private logger: Logger,
  ) {}

  async placeOrder(order: Order) {
    await this.saveOrder(order);
    await this.notifier.notify(order.customerEmail, "Order placed");
    this.logger.log(`Order ${order.id} placed`);
  }
}
```

### Event-Driven Decoupling

Before — direct calls create a web of dependencies:

```python
class UserService:
    def __init__(self, email_svc, analytics_svc, billing_svc, audit_svc):
        self._email = email_svc
        self._analytics = analytics_svc
        self._billing = billing_svc
        self._audit = audit_svc

    def register(self, user_data):
        user = self._create_user(user_data)
        self._email.send_welcome(user)
        self._analytics.track_signup(user)
        self._billing.create_account(user)
        self._audit.log_registration(user)
```

After — publish events and let subscribers handle themselves:

```python
class UserService:
    def __init__(self, event_bus: EventBus):
        self._events = event_bus

    def register(self, user_data):
        user = self._create_user(user_data)
        self._events.publish(UserRegistered(user_id=user.id, email=user.email))
```

### Facade Pattern to Limit Dependency Surface

```python
# Instead of multiple modules importing from a complex subsystem:
# from billing.internal.tax import TaxCalculator
# from billing.internal.discount import DiscountEngine
# from billing.internal.invoice import InvoiceBuilder

# Expose a single facade:
class BillingFacade:
    def calculate_total(self, items, customer):
        subtotal = self._discount_engine.apply(items, customer)
        tax = self._tax_calculator.compute(subtotal, customer.region)
        return subtotal + tax

    def generate_invoice(self, order):
        return self._invoice_builder.build(order)
```

### Layered Architecture Dependencies

```
Controllers  -->  Services  -->  Repositories  -->  Database
     |                |                |
     v                v                v
  DTOs          Domain Models     Entity Models

Rule: Dependencies point inward. Inner layers never import from outer layers.
```

## Best Practices

- Use a dependency injection container or framework for large applications to automate wiring
- Keep the composition root (where all dependencies are wired) at the application entry point
- Use the Law of Demeter: only talk to your immediate friends, not `a.getB().getC().doThing()`
- Wrap third-party libraries behind your own interfaces so you can swap them
- Use package/module boundaries to enforce dependency direction — e.g., `internal` packages in Go, `__all__` in Python
- Regularly review the dependency graph with visualization tools to spot unwanted couplings

## Common Pitfalls

- **Service locator anti-pattern**: Hiding dependencies behind a global registry makes them invisible and hard to test
- **Circular dependencies**: Module A imports B which imports A — restructure by extracting a shared interface or a third module
- **God object / mega-class**: A class that depends on everything becomes the bottleneck for all changes
- **Over-injection**: Injecting 10 dependencies into a constructor signals the class has too many responsibilities
- **Transitive dependency leakage**: Exposing internal implementation types in public APIs couples consumers to your internals
- **Dependency on volatile modules**: Core business logic should never depend on UI, framework, or infrastructure details directly
