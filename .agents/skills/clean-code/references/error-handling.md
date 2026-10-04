# Error Handling — Clean Code

You are an expert in error handling for writing clean, maintainable code.

## Core Philosophy

Clean error handling is about separating the happy path from the failure path so that both are readable and neither obscures the other. When error handling code is tangled with business logic — nested try-catch blocks, error codes checked at every call site, null checks on every return value — the intent of the code disappears behind a wall of defensive boilerplate. The goal is to structure code so that the normal flow reads as a clear, sequential narrative, and error recovery is handled in dedicated, well-defined locations.

Exceptions should carry enough context to diagnose a problem without requiring the developer to reproduce it. A good exception message answers three questions: what operation was being performed, what input or state caused the failure, and why it failed. "Cannot read property 'id' of undefined" forces a debugging session; "Failed to load user profile: user ID 'abc-123' not found in database" tells the on-call engineer exactly what happened and where to look.

The boundary between your code and third-party libraries is the most important place to get error handling right. Wrapping external exceptions behind your own application-specific exception types insulates callers from the implementation details of libraries you may swap out later. It also gives you a single place to normalize error messages, add context, and decide which failures are recoverable and which are fatal — decisions that belong to your application, not to the library author.

## Anti-Patterns

- **Swallowing exceptions with empty catch blocks**: A bare `except: pass` or `catch (e) {}` hides failures completely, turning bugs into silent data corruption or mysterious downstream errors that are nearly impossible to diagnose.

- **Catching the broadest possible exception type at every level**: Wrapping entire functions in `catch (Exception)` prevents callers from handling specific failures appropriately and masks programming errors like null references and type errors that should crash loudly.

- **Using error codes or magic return values instead of exceptions**: Returning `-1`, `null`, or `false` to signal failure forces every caller to remember to check the return value and know what each magic value means. Exceptions make failures impossible to accidentally ignore.

- **Logging the same error at every level of the call stack**: When every catch block logs the error and re-throws, a single failure generates five identical log entries with no additional context. Log at the boundary where the error is handled, and add context when re-throwing at intermediate levels.

- **Using exceptions for expected control flow**: Throwing an exception to exit a loop, signal a validation failure on user input, or indicate a cache miss abuses the exception mechanism. Exceptions are for exceptional situations; expected outcomes should use return values, option types, or result types.

## Overview

Error handling is essential to robust software, but when done poorly it obscures business logic and makes code difficult to follow. Clean error handling separates the happy path from failure recovery, uses exceptions rather than error codes, and provides enough context to diagnose problems without leaking implementation details.

## Core Principles

- **Use exceptions, not return codes**: Exceptions separate error handling from the main logic, keeping the happy path clean.
- **Write try-catch-finally first**: When writing code that could fail, start with the error handling structure to define the scope of expected failures.
- **Provide context with exceptions**: Include enough information to determine the source and cause of the error — operation, input, and what went wrong.
- **Define exception classes by caller needs**: The caller determines what granularity of exception handling is useful.
- **Do not return null**: Returning null forces every caller to add a null check. Return empty collections, default objects, or throw instead.
- **Do not pass null**: Passing null as an argument creates fragile code that must defensively check every parameter.

## Implementation Patterns

### Error Codes — Before

```python
def withdraw(account, amount):
    if amount <= 0:
        return -1  # invalid amount
    if account.balance < amount:
        return -2  # insufficient funds
    account.balance -= amount
    return 0  # success

result = withdraw(account, 100)
if result == -1:
    print("Invalid amount")
elif result == -2:
    print("Insufficient funds")
```

### Exceptions — After

```python
class InvalidAmountError(ValueError):
    pass

class InsufficientFundsError(Exception):
    def __init__(self, account_id, requested, available):
        self.account_id = account_id
        self.requested = requested
        self.available = available
        super().__init__(
            f"Account {account_id}: requested {requested}, available {available}"
        )

def withdraw(account, amount):
    if amount <= 0:
        raise InvalidAmountError(f"Amount must be positive, got {amount}")
    if account.balance < amount:
        raise InsufficientFundsError(account.id, amount, account.balance)
    account.balance -= amount
```

### Catching Too Broadly — Before

```python
try:
    result = do_everything()
except Exception:
    log.error("Something went wrong")
```

### Granular Handling — After

```python
try:
    config = load_config(path)
except FileNotFoundError:
    log.warning(f"Config not found at {path}, using defaults")
    config = default_config()
except json.JSONDecodeError as e:
    raise ConfigError(f"Malformed config at {path}: {e}") from e
```

### Returning Null — Before

```typescript
function findUser(id: string): User | null {
  const row = db.query("SELECT * FROM users WHERE id = ?", id);
  if (!row) return null;
  return mapToUser(row);
}

// Every caller must check:
const user = findUser(id);
if (user === null) {
  // handle missing...
}
```

### Null Object / Optional — After

```typescript
function findUser(id: string): User {
  const row = db.query("SELECT * FROM users WHERE id = ?", id);
  if (!row) throw new UserNotFoundError(id);
  return mapToUser(row);
}

// Or use Optional for queries where absence is normal:
function findUsers(filter: Filter): User[] {
  const rows = db.query("SELECT * FROM users WHERE ...", filter);
  return rows.map(mapToUser); // Returns empty array, never null
}
```

### Wrapping Third-Party Exceptions

```python
class PaymentGatewayError(Exception):
    """Wraps all payment provider exceptions into a single type."""
    pass

class PaymentGateway:
    def charge(self, amount, card_token):
        try:
            return stripe.Charge.create(amount=amount, source=card_token)
        except stripe.error.CardError as e:
            raise PaymentGatewayError(f"Card declined: {e}") from e
        except stripe.error.APIConnectionError as e:
            raise PaymentGatewayError(f"Cannot reach payment provider: {e}") from e
```

### Result Type Pattern

```typescript
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function parseConfig(raw: string): Result<Config, string> {
  try {
    const data = JSON.parse(raw);
    return { ok: true, value: validateConfig(data) };
  } catch (e) {
    return { ok: false, error: `Invalid config: ${e.message}` };
  }
}

const result = parseConfig(input);
if (result.ok) {
  startApp(result.value);
} else {
  log.error(result.error);
}
```

## Best Practices

- Define a small hierarchy of application-specific exception types
- Wrap third-party library exceptions so callers are not coupled to external APIs
- Log at the boundary where the error is handled, not where it is raised
- Use `finally` or context managers for cleanup (file handles, connections, locks)
- In async code, ensure rejected promises are always caught — unhandled rejections crash processes
- Use structured logging with error context: include request IDs, user IDs, and operation names

## Common Pitfalls

- **Swallowing exceptions silently**: `except: pass` hides bugs and makes debugging impossible
- **Catching too broadly**: `except Exception` at every level prevents specific handling upstream
- **Logging and re-raising without new context**: Creates duplicate log entries without additional value
- **Using exceptions for control flow**: Exceptions are for exceptional situations, not for normal branching logic
- **Inconsistent error responses in APIs**: Return a uniform error shape (`{ error: { code, message } }`) across all endpoints
- **Missing cleanup on error paths**: Forgetting to release resources when exceptions interrupt the normal flow
