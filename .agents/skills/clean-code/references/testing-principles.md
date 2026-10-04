# Testing Principles — Clean Code

You are an expert in testing principles and test design for writing clean, maintainable code.

## Core Philosophy

Tests are not a tax on development — they are the infrastructure that makes confident change possible. Without tests, every modification is a leap of faith: developers cannot know whether their change broke something until users report it. With a well-designed test suite, refactoring becomes safe, deployments become routine, and the codebase remains malleable over years of evolution. The investment in testing pays compound returns by making every future change cheaper and less risky.

The most important quality of a test is that it tests behavior, not implementation. A test that verifies "when a customer places an order, they receive a confirmation" survives any refactoring of the order placement internals. A test that verifies "the placeOrder method calls saveToDatabase then sendEmail in that order" breaks the moment the implementation changes, even if the behavior is preserved. Implementation-coupled tests are a maintenance burden that punishes refactoring — the exact opposite of what tests should enable.

The testing pyramid exists because different kinds of tests serve different purposes at different costs. Unit tests are cheap to write, fast to run, and precise in their failure messages — they form the foundation. Integration tests verify that components work together correctly at the boundaries. End-to-end tests confirm that the full system delivers value to users. Inverting this pyramid — writing mostly E2E tests and few unit tests — produces a slow, flaky, expensive suite that developers learn to ignore. Respecting the pyramid means allocating test effort where it delivers the most feedback per second of execution time.

## Anti-Patterns

- **Testing implementation details instead of observable behavior**: Asserting on internal state, method call order, or private data structures couples tests to the implementation and causes false failures on every refactoring. Test the public interface and the outcomes visible to the caller.

- **Building an inverted test pyramid with mostly end-to-end tests**: E2E tests are slow, flaky, and expensive to maintain. When they form the majority of the suite, developers stop running tests frequently, feedback loops lengthen, and confidence erodes. Invest in fast, reliable unit tests as the foundation.

- **Excessive mocking that disconnects tests from reality**: When every dependency is mocked, the test verifies that the code interacts with mocks correctly — not that it works correctly with real collaborators. Use real implementations where practical (in-memory databases, fake services) and mock only at true external boundaries.

- **Copy-pasting test setup across dozens of test functions**: Duplicated setup code makes tests expensive to maintain and obscures the unique aspects of each test case. Extract shared setup into factory functions, builders, or fixtures that express intent clearly.

- **Treating code coverage as a target rather than a diagnostic**: Chasing 100% coverage leads to trivial tests (getter/setter tests, tests that assert true equals true) that inflate the metric without improving confidence. Use coverage to find untested paths, not as a quality score.

## Overview

Tests are the safety net that enables refactoring, documents behavior, and catches regressions. Clean tests are as important as clean production code: they must be readable, maintainable, and fast. A well-designed test suite follows the testing pyramid, uses clear structure, and tests behavior rather than implementation.

## Core Principles

- **Testing pyramid**: Build a wide base of fast unit tests, a middle layer of integration tests, and a thin top of end-to-end tests.
- **Test behavior, not implementation**: Tests should verify what the code does, not how it does it internally.
- **One assertion per concept**: Each test should verify one logical concept. Multiple assertions are fine if they all relate to the same behavior.
- **FIRST properties**: Tests should be Fast, Independent, Repeatable, Self-validating, and Timely.
- **Arrange-Act-Assert**: Structure every test into three clear sections: setup, execution, and verification.
- **Tests are documentation**: A well-named test suite serves as executable documentation of the system's behavior.

## Implementation Patterns

### Testing Pyramid

```
        /  E2E  \          Few, slow, expensive
       /----------\
      / Integration \      Moderate count, moderate speed
     /----------------\
    /    Unit Tests     \  Many, fast, cheap
   /---------------------\
```

- **Unit tests** (70-80%): Test individual functions and classes in isolation. Mock external dependencies. Run in milliseconds.
- **Integration tests** (15-20%): Test interactions between components — database queries, API calls, module boundaries.
- **End-to-end tests** (5-10%): Test complete user workflows through the full stack. Slowest and most brittle.

### Poor Test Structure — Before

```python
def test_order():
    o = Order()
    o.add(Item("Widget", 10, 2))
    o.add(Item("Gadget", 20, 1))
    assert o.total() == 40
    o.apply_discount(0.1)
    assert o.total() == 36
    o.add(Item("Doohickey", 5, 3))
    assert o.total() == 49.5
    assert len(o.items) == 3
```

### Clean Test Structure — After

```python
class TestOrderTotal:
    def test_calculates_total_from_price_and_quantity(self):
        order = Order()
        order.add(Item("Widget", price=10, quantity=2))
        order.add(Item("Gadget", price=20, quantity=1))

        assert order.total() == 40

    def test_applies_percentage_discount_to_total(self):
        order = create_order_with_total(100)

        order.apply_discount(percent=0.1)

        assert order.total() == 90

    def test_discount_applies_to_items_added_after_discount(self):
        order = create_order_with_total(40)
        order.apply_discount(percent=0.1)

        order.add(Item("Doohickey", price=5, quantity=3))

        assert order.total() == 49.5
```

### Test Doubles — Types and Usage

```python
# Stub — returns canned answers
class StubPaymentGateway:
    def charge(self, amount, token):
        return PaymentResult(success=True, transaction_id="stub-123")

# Mock — verifies interactions
def test_sends_confirmation_email(self):
    mock_mailer = Mock(spec=Mailer)
    service = OrderService(mailer=mock_mailer)

    service.place_order(order)

    mock_mailer.send.assert_called_once_with(
        to="customer@example.com",
        subject="Order Confirmed"
    )

# Fake — working lightweight implementation
class FakeUserRepository:
    def __init__(self):
        self._users = {}

    def save(self, user):
        self._users[user.id] = user

    def find_by_id(self, user_id):
        return self._users.get(user_id)
```

### Testing Error Paths

```python
def test_raises_insufficient_funds_for_overdraft(self):
    account = Account(balance=50)

    with pytest.raises(InsufficientFundsError) as exc_info:
        account.withdraw(100)

    assert exc_info.value.requested == 100
    assert exc_info.value.available == 50
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input_str, expected", [
    ("hello", "Hello"),
    ("WORLD", "World"),
    ("hello world", "Hello world"),
    ("", ""),
])
def test_capitalizes_first_letter_only(input_str, expected):
    assert capitalize_first(input_str) == expected
```

### Test Builder Pattern

```typescript
class OrderBuilder {
  private items: Item[] = [];
  private customer = new Customer("default@test.com");
  private discount = 0;

  withItem(name: string, price: number, qty: number = 1): this {
    this.items.push(new Item(name, price, qty));
    return this;
  }

  withCustomer(email: string): this {
    this.customer = new Customer(email);
    return this;
  }

  withDiscount(percent: number): this {
    this.discount = percent;
    return this;
  }

  build(): Order {
    const order = new Order(this.customer, this.items);
    if (this.discount) order.applyDiscount(this.discount);
    return order;
  }
}

// Usage in tests:
const order = new OrderBuilder()
  .withItem("Widget", 10, 2)
  .withDiscount(0.1)
  .build();
```

## Best Practices

- Name tests to describe the expected behavior: `test_returns_empty_list_when_no_results_found`
- Use factory functions or builders to create test data and avoid duplication in setup
- Keep tests independent — no test should depend on the outcome of another
- Avoid testing private methods directly; test through the public interface
- Run the full test suite before committing; run fast unit tests continuously during development
- Use code coverage as a guide, not a goal — 100% coverage does not guarantee good tests
- Delete tests that no longer provide value (e.g., trivial getter/setter tests)

## Common Pitfalls

- **Testing implementation details**: Asserting on internal state or method call order couples tests to implementation, causing false failures on refactoring
- **Flaky tests**: Tests that pass sometimes and fail others due to timing, shared state, or external dependencies erode trust in the suite
- **Slow test suites**: When tests take too long, developers stop running them. Keep unit tests under 10 seconds total
- **Excessive mocking**: Mocking every dependency can result in tests that pass even when the real integration is broken
- **Copy-paste test code**: Duplicated setup across tests makes changes expensive; extract shared setup into helpers
- **Inverted pyramid**: Too many slow E2E tests and too few unit tests inverts the ideal distribution and slows development
- **Missing edge cases**: Happy-path-only tests miss null inputs, empty collections, boundary values, and concurrent access
