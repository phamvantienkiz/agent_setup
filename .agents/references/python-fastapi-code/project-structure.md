# FastAPI Project Structure — Hướng dẫn đầy đủ

## Cấu trúc dự án chuẩn (Domain-based)

```
fastapi-project/
├── alembic/
│   ├── versions/           # Migration files
│   ├── env.py
│   └── alembic.ini
│
├── src/
│   ├── main.py             # FastAPI app, lifespan, middleware
│   ├── config.py           # Pydantic BaseSettings
│   ├── database.py         # Engine, session factory, get_db
│   ├── exceptions.py       # Global exception handlers
│   │
│   ├── common/             # Shared across domains
│   │   ├── base_model.py   # SQLAlchemy declarative base
│   │   ├── base_repo.py    # Generic CRUD repository
│   │   ├── pagination.py   # PaginationParams, PaginatedResponse
│   │   ├── dependencies.py # Shared DI: get_current_user, etc.
│   │   └── utils.py        # Helpers
│   │
│   ├── users/
│   │   ├── __init__.py
│   │   ├── router.py       # @router endpoints
│   │   ├── service.py      # UserService class
│   │   ├── repository.py   # UserRepository class
│   │   ├── schemas.py      # UserCreate, UserUpdate, UserResponse
│   │   ├── models.py       # User SQLAlchemy model
│   │   ├── dependencies.py # get_user_service, get_user_repository
│   │   ├── exceptions.py   # UserNotFoundError, EmailExistsError
│   │   └── constants.py    # Domain constants
│   │
│   ├── auth/
│   │   ├── router.py       # /login, /refresh, /logout
│   │   ├── service.py      # AuthService
│   │   ├── schemas.py      # TokenResponse, LoginRequest
│   │   ├── dependencies.py # get_current_user, require_admin
│   │   └── utils.py        # jwt encode/decode
│   │
│   └── orders/
│       ├── router.py
│       ├── service.py
│       ├── repository.py
│       ├── schemas.py
│       ├── models.py
│       └── dependencies.py
│
├── tests/
│   ├── conftest.py         # Shared fixtures
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
├── pyproject.toml          # Dependencies, tool config
├── .env                    # Local environment variables
├── .env.example            # Template (commit này, không commit .env)
└── docker-compose.yml
```

---

## main.py — Entry point

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import get_settings
from src.database import create_db_tables
from src.exceptions import DomainError
from src.users.router import router as users_router
from src.auth.router import router as auth_router
from src.orders.router import router as orders_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup và shutdown events."""
    # Startup
    await create_db_tables()
    yield
    # Shutdown (cleanup nếu cần)

app = FastAPI(
    title="My API",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,  # Tắt docs ở production
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc), "error_code": exc.error_code}
    )

# Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
```

---

## config.py — Settings management

```python
from functools import lru_cache
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    app_name: str = "My FastAPI App"
    debug: bool = False
    secret_key: str

    # Database
    database_url: PostgresDsn
    db_echo: bool = False  # Log SQL queries

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Auth
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: list[AnyHttpUrl] = []

    # Email
    sendgrid_api_key: str = ""
    from_email: str = "noreply@example.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> list:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

## database.py — Database setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from src.config import get_settings

settings = get_settings()

engine = create_async_engine(
    str(settings.database_url),
    echo=settings.db_echo,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Reconnect nếu connection bị drop
)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Quan trọng: giữ objects valid sau commit
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: provides database session."""
    async with async_session_factory() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
```

---

## exceptions.py — Error hierarchy

```python
from fastapi import status

class DomainError(Exception):
    """Base class cho tất cả business logic errors."""
    status_code: int = status.HTTP_400_BAD_REQUEST
    error_code: str = "DOMAIN_ERROR"

    def __init__(self, message: str, *, status_code: int = None, error_code: str = None):
        super().__init__(message)
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code

# 404 errors
class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"

class UserNotFoundError(NotFoundError):
    error_code = "USER_NOT_FOUND"

    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} không tồn tại")

# 409 errors
class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"

class EmailAlreadyExistsError(ConflictError):
    error_code = "EMAIL_EXISTS"

    def __init__(self, email: str):
        super().__init__(f"Email '{email}' đã được đăng ký")

# 403 errors
class PermissionDeniedError(DomainError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "PERMISSION_DENIED"

    def __init__(self, action: str = "thực hiện hành động này"):
        super().__init__(f"Bạn không có quyền {action}")
```

---

## common/pagination.py — Pagination

```python
from fastapi import Query
from pydantic import BaseModel
from typing import Generic, TypeVar, List

T = TypeVar("T")

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Số trang"),
        page_size: int = Query(20, ge=1, le=100, description="Số items mỗi trang"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams):
        return cls(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size
        )

# Usage trong router
@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def list_users(
    pagination: PaginationParams = Depends(),
    service: UserService = Depends(get_user_service)
):
    users, total = await service.list_users(
        skip=pagination.offset,
        limit=pagination.page_size
    )
    return PaginatedResponse.create(users, total, pagination)
```

---

## conftest.py — Test configuration

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import app
from src.database import Base, get_db
from src.config import get_settings

settings = get_settings()
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Fresh database for each test."""
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """HTTP test client với overridden DB."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

# Usage trong test
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/v1/users", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "SecurePass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data  # Không leak password
```

---

## pyproject.toml — Dependencies

```toml
[tool.poetry]
name = "my-fastapi-app"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
pydantic = {extras = ["email"], version = "^2.9.0"}
pydantic-settings = "^2.6.0"
sqlalchemy = {extras = ["asyncio"], version = "^2.0.36"}
asyncpg = "^0.30.0"        # PostgreSQL async driver
alembic = "^1.14.0"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
httpx = "^0.27.0"          # Async HTTP client

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
aiosqlite = "^0.20.0"      # SQLite cho tests
ruff = "^0.8.0"            # Linting + formatting
mypy = "^1.13.0"           # Type checking

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]  # PEP8, imports, naming, upgrades

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
```
