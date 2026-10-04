# FastAPI Project Structure — Domain-Based Architecture (Modular Monolith / DDD)

This guide details the **Domain-based (Feature Slicing)** architecture standard for FastAPI projects. 
- Use this structure when building **Modular Monoliths**, complex enterprise domains, or systems following **Domain-Driven Design (DDD)** principles where features require high autonomy.
- For small-to-medium backends or microservices, the **Layered Architecture** defined in `fastapi-backend-scaffold` is the standard default. Both architectures share identical infrastructure invariants: root is always `backend/`, dependencies managed via PEP 621 `pyproject.toml`, and cross-cutting concerns handled by `app/middlewares/`.

---

## 1. Project Directory Structure

```
repo-root/
└── backend/
    ├── .venv/                     # Isolated virtualenv (never committed)
    ├── .gitignore
    ├── README.md
    ├── pyproject.toml             # PEP 621 dependencies (uv / pip)
    ├── .env.example               # Environment variables template
    ├── Dockerfile                 # Multi-stage production container
    ├── docker-compose.yml         # Local development services (Postgres, Redis)
    ├── migrations/                # Alembic migrations (env.py, versions/)
    ├── logs/                      # Runtime application logs (.gitkeep)
    ├── docs/                      # Architectural decision records (ADRs)
    │
    ├── tests/                     # Test suite mirroring app/
    │   ├── conftest.py            # Async test fixtures, test DB engine
    │   ├── unit/
    │   │   ├── users/
    │   │   │   ├── test_service.py
    │   │   │   └── test_repository.py
    │   │   └── orders/
    │   │       └── test_service.py
    │   └── integration/
    │       ├── test_users_api.py
    │       └── test_orders_api.py
    │
    └── app/
        ├── main.py                # App entry point & lifespan
        ├── core/                  # Global application settings & configuration
        │   ├── config.py          # Pydantic BaseSettings (.env)
        │   ├── security.py        # Token hashing, password verification
        │   └── logging.py         # Structured logging configuration
        │
        ├── db/                    # Core database setup
        │   ├── base.py            # SQLAlchemy DeclarativeBase
        │   └── session.py         # create_async_engine & async_sessionmaker
        │
        ├── middlewares/           # Cross-cutting concerns (applied to all requests)
        │   ├── __init__.py        # register_middlewares(app)
        │   ├── request_id.py      # X-Request-ID propagation
        │   ├── logging.py         # Structured access logging + X-Process-Time
        │   ├── error_handler.py   # Outer catch-all for unhandled exceptions -> safe 500
        │   ├── cors.py            # Centralized CORS policy
        │   └── rate_limit.py      # IP rate limiting
        │
        ├── common/                # Shared utilities & cross-domain primitives
        │   ├── base_repository.py # Generic CRUD repository base
        │   ├── pagination.py      # PaginationParams & PaginatedResponse
        │   └── utils.py           # Pure helper functions
        │
        ├── users/                 # Feature Domain: Users
        │   ├── __init__.py
        │   ├── router.py          # HTTP endpoints for /users
        │   ├── service.py         # User domain business logic
        │   ├── repository.py      # User DB access (AsyncSession)
        │   ├── schemas.py         # Request/response Pydantic models
        │   ├── models.py          # User SQLAlchemy ORM models
        │   ├── dependencies.py    # Domain DI (get_user_service, etc.)
        │   ├── exceptions.py      # Domain-specific exceptions
        │   └── constants.py       # Domain-specific constants
        │
        ├── auth/                  # Feature Domain: Authentication
        │   ├── router.py          # /login, /refresh, /logout
        │   ├── service.py         # Auth business logic (JWT issuance)
        │   ├── schemas.py         # TokenResponse, LoginRequest
        │   └── dependencies.py    # get_current_user, require_admin
        │
        └── orders/                # Feature Domain: Orders
            ├── router.py
            ├── service.py
            ├── repository.py
            ├── schemas.py
            ├── models.py
            └── dependencies.py
```

---

## 2. Concurrency Guidelines: `def` (Sync) vs `async def` (Async)

Do **NOT** blindly make every function `async def`. Concurrency in FastAPI must follow precise technical boundaries:

| Task Type | Declaration | Why & When to Use |
| :--- | :--- | :--- |
| **I/O Operations** | `async def` (with `await`) | **Database queries** (`await db.execute(...)`), external HTTP requests (`httpx.AsyncClient`), Redis calls (`await redis.get(...)`). Releases the Event Loop to handle thousands of concurrent requests while waiting for network/disk. |
| **In-Memory Compute** | `def` (Sync) | **Data validation**, pure business math, string formatting, pagination calculations, Pydantic transformations. Running these synchronously avoids coroutine scheduling overhead. |
| **CPU-Bound / Blocking Legacy Calls** | `def` (in endpoints) or `asyncio.to_thread` | Heavy encryption, image processing, or legacy synchronous libraries. If declared as `def`, FastAPI offloads it to an external threadpool, preventing Main Event Loop freeze. |

---

## 3. Core Implementation Files

### `app/main.py` — Application Entry Point

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.middlewares import register_middlewares
from app.users.router import router as users_router
from app.auth.router import router as auth_router
from app.orders.router import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # Startup
    setup_logging()
    yield
    # Shutdown
    await engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # 1. Wire all cross-cutting middlewares (order-sensitive)
    register_middlewares(app)

    # 2. Register feature routers
    app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth")
    app.include_router(users_router, prefix=f"{settings.API_V1_PREFIX}/users")
    app.include_router(orders_router, prefix=f"{settings.API_V1_PREFIX}/orders")

    return app

app = create_app()
```

---

### `app/core/config.py` — Settings Management

```python
from functools import lru_cache
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "My FastAPI App"
    ENVIRONMENT: str = "local"  # local | staging | production
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: PostgresDsn
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Middleware settings
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    RATE_LIMIT_PER_MINUTE: int = 120

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> list:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

---

### `app/db/session.py` — Async Database Setup

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DB_ECHO,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency yielding an async database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

### `app/common/pagination.py` — In-Memory Pagination Helpers

Demonstrates proper use of synchronous `def` for pure in-memory calculations:

```python
from collections.abc import Sequence
from typing import Generic, TypeVar
from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")

class PaginationParams:
    """Synchronous parameter parser for page & size."""
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: Sequence[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        """Pure in-memory computation — sync def is optimal here."""
        total_pages = (total + params.page_size - 1) // params.page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=total_pages,
        )
```

---

### Domain Example: `app/users/`

#### `app/users/repository.py` — Async Database Access

```python
from collections.abc import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.models import User
from app.users.schemas import UserCreate

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list_users(self, skip: int, limit: int) -> tuple[Sequence[User], int]:
        count_query = select(func.count(User.id))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = select(User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def create(self, data: UserCreate, hashed_password: str) -> User:
        user = User(
            email=data.email,
            name=data.name,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
```

#### `app/users/service.py` — Business Logic Orchestration

```python
from collections.abc import Sequence
from app.common.pagination import PaginatedResponse, PaginationParams
from app.core.security import hash_password
from app.users.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserResponse

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def validate_password_strength(self, password: str) -> bool:
        """Pure in-memory synchronous check."""
        return len(password) >= 8 and any(c.isupper() for c in password)

    async def register_user(self, data: UserCreate) -> UserResponse:
        """Async operation because it interacts with the database."""
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise EmailAlreadyExistsError(data.email)

        hashed_pw = hash_password(data.password)
        user = await self.repo.create(data, hashed_pw)
        return UserResponse.model_validate(user)

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return UserResponse.model_validate(user)

    async def list_users(self, params: PaginationParams) -> PaginatedResponse[UserResponse]:
        users, total = await self.repo.list_users(skip=params.offset, limit=params.page_size)
        user_responses = [UserResponse.model_validate(u) for u in users]
        return PaginatedResponse.create(user_responses, total, params)
```

#### `app/users/router.py` — Controller Layer

```python
from typing import Annotated
from fastapi import APIRouter, Depends, status

from app.common.pagination import PaginatedResponse, PaginationParams
from app.users.dependencies import get_user_service
from app.users.schemas import UserCreate, UserResponse
from app.users.service import UserService

router = APIRouter(tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.register_user(data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    return await service.get_user(user_id)

@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    params: Annotated[PaginationParams, Depends()],
    service: Annotated[UserService, Depends(get_user_service)],
) -> PaginatedResponse[UserResponse]:
    return await service.list_users(params)
```

---

## 4. `pyproject.toml` — Dependency Standard (PEP 621)

Fully compatible with `uv` and `pip` in accordance with the project environment isolation rules:

```toml
[project]
name = "my-fastapi-backend"
version = "0.1.0"
description = "FastAPI Domain-Based Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "pydantic-settings>=2.6.0",
    "pydantic[email]>=2.9.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "aiosqlite>=0.20.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```

---

## 5. Summary: When to Use Which Architecture

| Characteristic | Layered Architecture (`fastapi-backend-scaffold`) | Domain-Based Architecture (`project-structure.md`) |
| :--- | :--- | :--- |
| **Primary Scope** | Microservices, smaller projects, APIs with < 10 resources | Modular Monoliths, complex enterprise DDD systems |
| **Top-Level Organization** | By technical layer (`app/models/`, `app/repositories/`) | By business domain (`app/users/`, `app/orders/`) |
| **Workspace Root** | `backend/` | `backend/` |
| **Package Root** | `app/` | `app/` |
| **Dependency Manager**| PEP 621 (`pyproject.toml` via `uv` or `pip`) | PEP 621 (`pyproject.toml` via `uv` or `pip`) |
| **Middlewares** | Centralized in `app/middlewares/` | Centralized in `app/middlewares/` |
| **Database I/O** | Async SQLAlchemy (`AsyncSession` + `asyncpg`) | Async SQLAlchemy (`AsyncSession` + `asyncpg`) |
