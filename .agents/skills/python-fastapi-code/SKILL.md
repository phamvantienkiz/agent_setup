---
name: python-fastapi-code
description: >
  Senior Python & FastAPI engineering skill for building high-performance, clean, and production-grade APIs.
  Enforces Clean Code (PEP 8), SOLID principles, Design Patterns, Pydantic V2, async SQLAlchemy, JWT authentication, WebSockets, error handling, and testing with pytest-asyncio/httpx.
  Trigger when the user asks to:
  - Write or review Python backend code (FastAPI, async SQLAlchemy, Pydantic V2, async/await)
  - Build API endpoints, routers, validation schemas, JWT/OAuth2 auth, background tasks, WebSockets
  - Apply Clean Code & SOLID in Python/FastAPI (SRP, OCP, LSP, ISP, DIP)
  - Apply Design Patterns (Repository, Service Layer, Factory, Strategy, Dependency Injection via Depends)
  - Separate layers: router/service/repository/schema/model
  - Write async unit and integration tests (pytest-asyncio, httpx)
  - Refactor, optimize performance, or migrate code to FastAPI
---

# Python & FastAPI Clean Code & Expert Skill

This skill provides comprehensive senior-engineering guidance for writing high-quality Python backend code with FastAPI, applying Clean Code, SOLID principles, Design Patterns, Pydantic V2, and Async SQLAlchemy.

## Core Principles & Constraints (MUST DO / MUST NOT DO)

### MUST DO
- **Comprehensive Type Hints**: All function signatures, arguments, and return types must have explicit type hints.
- **Pydantic V2 Syntax**: Use `model_config = ConfigDict(...)`, `@field_validator`, `@model_validator`.
- **Dependency Injection**: Use `Annotated[..., Depends(...)]` syntax for all dependencies.
- **Right Concurrency Model**: Use `async def` with `await` for all I/O operations (DB, HTTP calls, Redis). Keep pure in-memory computations, validations, and utility functions as synchronous `def` to avoid coroutine overhead. Offload CPU-heavy tasks via `asyncio.to_thread` or standard `def` endpoints.
- **Modern Python 3.10+ Typing**: Use `X | None` instead of `Optional[X]`, use `list[str]` instead of `List[str]`.
- **Standard REST HTTP Status Codes**: Return appropriate status codes (201 Created, 204 No Content, 404 Not Found, 422 Unprocessable Entity).

### MUST NOT DO
- **Never perform blocking/sync I/O** inside an `async def` function (e.g., `time.sleep()`, synchronous DB sessions, synchronous requests).
- **Never use deprecated Pydantic V1 syntax**: `@validator`, `class Config`.
- **Never store plaintext passwords**: Always hash using bcrypt/passlib/argon2.
- **Never return sensitive data**: Password hashes and internal secrets must never be exposed in response schemas.
- **Never hardcode configurations**: All configurations must be loaded from `pydantic-settings` via environment variables (.env).

## How to Use This Skill

1. Identify the request type -> read the corresponding section below.
2. For complex requirements (project architecture, multiple design patterns) -> consult the relevant reference files.
3. Always prioritize Pythonic, type-safe, and testable code.

## Core Philosophy (Read First)

### Priority Order When Writing Code

1. **Readable** > Clever
2. **Explicit** > Implicit
3. **Simple** > Complex
4. **Testable** > Tightly coupled

---

## 1. CLEAN CODE IN PYTHON

### Naming Conventions (PEP 8)

```python
# Classes: CamelCase
class UserRepository:
    pass

# Functions/Methods/Variables: snake_case
def get_user_by_email(email: str) -> User:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
DEFAULT_PAGE_SIZE = 20

# Private: leading underscore
class UserService:
    def __init__(self):
        self._cache: dict = {}

    def _validate_email(self, email: str) -> bool:
        pass
```

### Naming - Good Naming Practices

```python
# BAD: ambiguous names, obscure abbreviations
def proc_usr(u, f=False):
    d = get_d()
    ...

# GOOD: descriptive name revealing intent
def process_user_registration(user: UserCreate, send_welcome_email: bool = False) -> User:
    database_session = get_database_session()
    ...

# BAD: magic numbers
if user.age > 18:
    ...

# GOOD: named constants
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
    ...
```

### Functions - Clean Function Guidelines

```python
# BAD: function does too many things, too many parameters
def create_user(name, email, password, role, send_email, log_action, notify_admin):
    # validation
    # hash password
    # save to db
    # send email
    # log
    # notify
    ...

# GOOD: single responsibility per function, use dataclass/Pydantic for multiple parameters
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

async def create_user(user_data: UserCreate) -> User:
    """Create a new user and return the persisted user record."""
    hashed_password = hash_password(user_data.password)
    user = await user_repository.save(user_data, hashed_password)
    await email_service.send_welcome(user.email)
    return user
```

### Type Hints - Required in Python/FastAPI

```python
from typing import Optional, List, Dict, Any
from collections.abc import Sequence

# Always annotate function signatures
async def get_users(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None
) -> List[User]:
    ...

# Use TypeAlias for complex types
UserId = int
UserDict = Dict[str, Any]

# Python 3.10+: use X | Y instead of Optional[X]
def find_user(user_id: int) -> User | None:
    ...
```

### Comments and Docstrings

```python
# BAD: comment explains "what" (code is already self-explanatory)
# Increment i by 1
i += 1

# GOOD: comment explains "why"
# Delay 100ms to avoid rate limiting from external API
await asyncio.sleep(0.1)

# GOOD: docstring for public API
async def calculate_discount(
    user: User,
    order_total: float
) -> float:
    """
    Calculate discount based on the user's membership tier.

    Args:
        user: User object with membership_tier
        order_total: Total order amount (USD)

    Returns:
        Discount amount (USD), non-negative

    Raises:
        ValueError: If order_total < 0
    """
    if order_total < 0:
        raise ValueError(f"order_total must be >= 0, got: {order_total}")
    ...
```

### Pythonic Patterns

```python
# List comprehension instead of manual loop
# BAD
active_users = []
for user in users:
    if user.is_active:
        active_users.append(user)

# GOOD
active_users = [user for user in users if user.is_active]

# Context managers for resource management
async with get_db() as db:
    result = await db.execute(query)

# Dataclasses / Pydantic models instead of raw dictionaries
# BAD
user = {"name": "Alice", "email": "alice@example.com"}

# GOOD
class UserResponse(BaseModel):
    name: str
    email: EmailStr

# Walrus operator (Python 3.8+)
if user := await find_user(user_id):
    return user
raise HTTPException(status_code=404, detail="User not found")
```

---

## 2. SOLID PRINCIPLES IN FASTAPI

### S - Single Responsibility Principle (SRP)

Each class/module should have only one reason to change. In FastAPI: Routers handle only HTTP, Services handle only business logic, Repositories handle only database operations.

```python
# BAD: endpoint does too many things
@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Validate
    if not user.email or not user.password:
        raise HTTPException(400, "Email and password required")
    # Check duplicate
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(409, "Email already exists")
    # Hash password & save
    hashed = bcrypt.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user); db.commit()
    return db_user

# GOOD: each layer has a single responsibility
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user)
```

> See complete implementation details in: `references/solid-principles.md`

### O - Open/Closed Principle (OCP)

Open for extension, closed for modification. Use abstract base classes.

```python
from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: str) -> bool:
        ...

class EmailNotification(NotificationChannel):
    async def send(self, recipient: str, message: str) -> bool:
        # send email logic
        ...

class SMSNotification(NotificationChannel):
    async def send(self, recipient: str, message: str) -> bool:
        # send SMS logic
        ...

# Adding a new channel requires no modification to existing code
class PushNotification(NotificationChannel):
    async def send(self, recipient: str, message: str) -> bool:
        # push notification logic
        ...
```

### L - Liskov Substitution Principle (LSP)

Subclasses must be substitutable for their superclasses without breaking behavior.

```python
class BaseRepository(ABC):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[BaseModel]:
        ...

    @abstractmethod
    async def save(self, entity: BaseModel) -> BaseModel:
        ...

# SQLAlchemy implementation
class SQLUserRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Optional[User]:
        ...  # implements fully, no narrower exceptions

# In-memory implementation for testing
class InMemoryUserRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Optional[User]:
        ...  # same contract, substitutable
```

### I - Interface Segregation Principle (ISP)

Split bloated interfaces into smaller, client-specific interfaces.

```python
# BAD: interface is too bloated
class UserRepository(ABC):
    @abstractmethod
    async def get(self, id: int): ...
    @abstractmethod
    async def save(self, user): ...
    @abstractmethod
    async def delete(self, id: int): ...
    @abstractmethod
    async def get_analytics(self): ...  # not every repo needs this
    @abstractmethod
    async def export_csv(self): ...     # not every repo needs this

# GOOD: small, composable interfaces
class Readable(ABC):
    @abstractmethod
    async def get_by_id(self, id: int): ...

class Writable(ABC):
    @abstractmethod
    async def save(self, entity): ...

class Deletable(ABC):
    @abstractmethod
    async def delete(self, id: int): ...

class UserRepository(Readable, Writable, Deletable):
    ...
```

### D - Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions. FastAPI's `Depends()` is built-in Dependency Injection.

```python
# BAD: service creates dependencies directly
class UserService:
    def __init__(self):
        self.repo = SQLUserRepository()  # tightly coupled!
        self.emailer = SendgridEmailer()  # tightly coupled!

# GOOD: inject abstractions via constructor
class UserService:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,
        email_service: EmailServiceInterface
    ):
        self.user_repo = user_repo
        self.email_service = email_service

# FastAPI DI setup
def get_user_service(
    db: AsyncSession = Depends(get_db)
) -> UserService:
    return UserService(
        user_repo=SQLUserRepository(db),
        email_service=SendgridEmailService()
    )

@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

---

## 3. FASTAPI PROJECT STRUCTURE & ARCHITECTURAL PATTERNS

FastAPI supports two architectural styles depending on project scale, both sharing the **same infrastructure invariants** (root is always `backend/`, dependencies via PEP 621 `pyproject.toml` with `uv`/`pip`, and cross-cutting concerns in `app/middlewares/`):

1. **Layered / Technical Slicing Architecture (`fastapi-backend-scaffold`)**:
   - Best for **microservices**, focused APIs, and small-to-medium backends (< 10 resources).
   - Organized by technical concern: `app/models/`, `app/schemas/`, `app/repositories/`, `app/services/`, `app/api/v1/endpoints/`.
2. **Domain-Based / Feature Slicing Architecture (`references/project-structure.md`)**:
   - Best for **Modular Monoliths**, complex business domains, and Domain-Driven Design (DDD).
   - Organized by autonomous business features: `app/users/`, `app/auth/`, `app/orders/`.

### Standard Domain-Based Structure (Modular Monolith / DDD)

```
repo-root/
└── backend/
    ├── .venv/                     # Isolated virtual environment
    ├── pyproject.toml             # PEP 621 dependencies (uv / pip)
    ├── .env.example
    ├── Dockerfile
    ├── docker-compose.yml
    ├── migrations/                # Alembic migrations
    ├── tests/
    │   ├── conftest.py
    │   ├── unit/
    │   └── integration/
    └── app/
        ├── main.py                # App entrypoint & lifespan
        ├── core/                  # Settings (pydantic-settings), security, logging
        ├── db/                    # Async engine & sessionmaker
        ├── middlewares/           # CORS, request-id, access logging, error handling
        ├── common/                # Shared base repo, pagination, utils
        │
        ├── users/                 # Feature Domain: Users
        │   ├── router.py          # HTTP endpoints ONLY
        │   ├── service.py         # Business logic ONLY
        │   ├── repository.py      # Async DB queries ONLY
        │   ├── schemas.py         # Pydantic request/response models
        │   ├── models.py          # SQLAlchemy ORM models
        │   └── dependencies.py    # Domain DI
        │
        ├── auth/                  # Feature Domain: Auth
        │   ├── router.py
        │   ├── service.py
        │   ├── schemas.py
        │   └── dependencies.py
        │
        └── orders/                # Feature Domain: Orders
            ├── router.py
            ├── service.py
            ├── repository.py
            ├── schemas.py
            └── models.py
```

### Layer Separation Rules

| Layer             | Responsibility                | Allowed Imports                        |
| ----------------- | ----------------------------- | -------------------------------------- |
| `router.py`       | HTTP in/out, status codes     | service, schemas, dependencies         |
| `service.py`      | Business logic, orchestration | repository, schemas, external services |
| `repository.py`   | Database queries only         | models, database session               |
| `schemas.py`      | Request/response validation   | Pydantic only                          |
| `models.py`       | DB table definitions          | SQLAlchemy only                        |
| `dependencies.py` | DI factory functions          | service, repository, config            |

---

## 4. DESIGN PATTERNS IN FASTAPI

Refer to the corresponding reference files for detailed walkthroughs of each pattern.

### Repository Pattern

Decouples database access from business logic:

```python
class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def save(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity
```

### Service Layer Pattern

```python
class UserService:
    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    async def register_user(self, data: UserCreate) -> User:
        await self._validate_unique_email(data.email)
        hashed_pw = hash_password(data.password)
        user = await self.user_repo.create(data, hashed_pw)
        await self.email_service.send_welcome(user.email)
        return user

    async def _validate_unique_email(self, email: str) -> None:
        if await self.user_repo.exists_by_email(email):
            raise EmailAlreadyExistsError(email)
```

### Dependency Injection Pattern (FastAPI Native)

```python
# dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        async with session.begin():
            yield session

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
    email_svc: EmailService = Depends(get_email_service),
) -> UserService:
    return UserService(repo, email_svc)

# router.py
@router.post("/users")
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    ...
```

> See details: `references/design-patterns.md`

---

## 5. ERROR HANDLING

```python
# exceptions.py (domain)
class DomainError(Exception):
    """Base class for all domain errors."""
    pass

class UserNotFoundError(DomainError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} does not exist")

class EmailAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Email {email} is already registered")

# main.py - global exception handlers
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "error_code": "USER_NOT_FOUND"}
    )

@app.exception_handler(EmailAlreadyExistsError)
async def email_exists_handler(request: Request, exc: EmailAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc), "error_code": "EMAIL_EXISTS"}
    )
```

---

## 6. ASYNC BEST PRACTICES

```python
# GOOD: async for I/O operations
async def get_user_with_orders(user_id: int) -> UserWithOrders:
    # Run concurrently rather than sequentially
    user, orders = await asyncio.gather(
        user_repo.get_by_id(user_id),
        order_repo.get_by_user_id(user_id)
    )
    return UserWithOrders(user=user, orders=orders)

# BAD: blocking call in async context
async def get_users():
    time.sleep(1)  # BLOCKS event loop!
    users = requests.get(...)  # BLOCKS event loop!

# GOOD: use async libraries
async def get_users():
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(...)
```

---

## 7. PYDANTIC & SCHEMAS BEST PRACTICES

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional

# Separate request vs response schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

# Never expose passwords in response models!
```

---

## 8. TESTING PATTERNS

```python
# conftest.py
@pytest.fixture
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_test_session() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# Unit test service
async def test_create_user_sends_welcome_email():
    mock_repo = AsyncMock(spec=UserRepository)
    mock_email = AsyncMock(spec=EmailService)
    mock_repo.exists_by_email.return_value = False
    mock_repo.create.return_value = fake_user

    service = UserService(mock_repo, mock_email)
    await service.register_user(user_create_data)

    mock_email.send_welcome.assert_called_once_with(fake_user.email)
```

---

## Detailed Reference Guides (Internal References)

All detailed reference documentation is self-contained within the `references/` directory of this skill:

| Topic | Reference File | Detailed Contents |
|:---|:---|:---|
| **Pydantic V2** | `references/pydantic-v2.md` | Validation schemas, model_config, field_validator, serialization |
| **Async SQLAlchemy** | `references/async-sqlalchemy.md` | Async engine, session management, async CRUD patterns |
| **Authentication & Security** | `references/authentication.md` | JWT token flow, OAuth2 password bearer, get_current_user |
| **Endpoints & Routing** | `references/endpoints-routing.md` | APIRouter, dependency injection, path/query params |
| **Async Testing** | `references/testing-async.md` | pytest-asyncio, httpx AsyncClient, fixtures, mocking |
| **Django Migration** | `references/migration-from-django.md` | Migrating from Django / Django REST Framework to FastAPI |
| **Design Patterns** | `references/design-patterns.md` | Repository, Factory, Strategy, Observer, Unit of Work |
| **SOLID Principles** | `references/solid-principles.md` | Concrete examples for each SOLID principle in FastAPI |
| **Project Structure** | `references/project-structure.md` | Layered architectural details: Router -> Service -> Repository |

Read the corresponding reference file when you need comprehensive examples or when handling complex technical requirements.
