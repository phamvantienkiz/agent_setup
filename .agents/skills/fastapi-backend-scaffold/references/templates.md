# Templates — FastAPI Backend Scaffold

The snippets below are the standard templates. Read this file when the agent actually starts creating each specific file (no need to load everything at once). Replace `<project-name>`, `<Project Description>`, etc. with real project values.

## Table of contents

- [pyproject.toml](#pyprojecttoml)
- [.gitignore](#gitignore)
- [.env.example](#envexample)
- [README.md](#readmemd)
- [Dockerfile](#dockerfile)
- [docker-compose.yml](#docker-composeyml)
- [app/main.py](#appmainpy)
- [app/core/config.py](#appcoreconfigpy)
- [app/core/logging.py](#appcoreloggingpy)
- [app/middlewares](#appmiddlewares)
- [app/db (session.py & base.py)](#appdb-sessionpy--basepy)
- [app/api/deps.py](#appapidepspy)
- [app/api/v1/router.py](#appapiv1routerpy)
- [health.py](#healthpy)
- [Full resource example: items](#full-resource-example-items)
- [tests/conftest.py](#testsconftestpy)
- [migrations (Alembic)](#migrations-alembic)

---

## pyproject.toml

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "<Project Description>"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic-settings>=2.4.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",          # async PostgreSQL driver
    "alembic>=1.13.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "aiosqlite>=0.20.0",        # async SQLite for tests
    "ruff>=0.6.0",
    "mypy>=1.11.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
ignore_missing_imports = true
```

This same `pyproject.toml` works identically whether the environment is managed with `pip`/`venv` or with `uv` — neither tool requires a different dependency format.

---

## .gitignore

```gitignore
# Virtualenv — NEVER commit
.venv/
venv/
env/

# Python
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/

# Env & secrets
.env
.env.*
!.env.example

# Logs
logs/*.log
*.log

# Test / lint / type-check caches
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage

# Local DB
*.sqlite3
*.db

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml
```

---

## .env.example

```dotenv
# --- App ---
APP_NAME=<project-name>
ENVIRONMENT=local          # local | staging | production
DEBUG=true
API_V1_PREFIX=/api/v1

# --- Security ---
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- Database ---
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/<project-name>

# --- CORS (used by app/middlewares/cors.py) ---
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# --- Rate limiting (used by app/middlewares/rate_limit.py) ---
RATE_LIMIT_PER_MINUTE=120
```

---

## README.md

```markdown
# <project-name> — Backend

FastAPI backend for <short project description>.

## Requirements

- Python >= 3.11
- (optional) Docker + Docker Compose
- `pip` (built into Python) or [`uv`](https://docs.astral.sh/uv/) — either works, pick whichever you have installed

## Setup (local dev)

All commands run from inside the `backend/` directory. Never install dependencies outside `.venv`.

**Using pip:**
\`\`\`bash
cd backend
python3 -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env # then fill in real values
\`\`\`

**Using uv (faster, equivalent result):**
\`\`\`bash
cd backend
uv venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
cp .env.example .env
\`\`\`

## Running the dev server

\`\`\`bash
uvicorn app.main:app --reload

# or, with uv:

uv run uvicorn app.main:app --reload
\`\`\`

Runs at `http://localhost:8000` by default, docs at `/docs`. Every response includes an `X-Request-ID` and `X-Process-Time` header (see `app/middlewares/`).

## Running tests

\`\`\`bash
pytest

# or: uv run pytest

\`\`\`

## Database migrations (Alembic)

\`\`\`bash
alembic revision --autogenerate -m "message"
alembic upgrade head
\`\`\`

## Running with Docker

\`\`\`bash
docker compose up --build
\`\`\`

## Directory structure

See `docs/` or the `fastapi-backend-scaffold` skill for full details. Summary:

\`\`\`
app/
├── main.py # FastAPI entrypoint
├── api/ # controller layer (routers, deps)
├── middlewares/ # cross-cutting: CORS, request-id, logging, rate limit, error handling
├── core/ # config, security, logging
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
├── repositories/ # repository layer (pure DB access)
├── services/ # business logic
├── db/ # session/engine
├── dependencies/ # business-level dependencies
├── exceptions/ # custom exceptions + typed handlers
└── utils/ # pure helpers
\`\`\`
```

---

## Dockerfile

```dockerfile
# --- Stage 1: build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY app ./app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# --- Stage 2: runtime image ---
FROM python:3.11-slim AS runtime

# Note: no .venv is created inside the container — the image itself is
# already an isolated environment. .venv is only required for host dev.

RUN useradd --create-home appuser
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app ./app

USER appuser
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## docker-compose.yml

```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./app:/app/app # hot-reload code during dev
    command:
      [
        "uvicorn",
        "app.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8000",
        "--reload",
      ]
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: <project-name>
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

---

## app/main.py

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers
from app.middlewares import register_middlewares


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # TODO: open connection pools / cache clients here if needed
    yield
    # TODO: close connections on shutdown


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # All cross-cutting concerns (CORS, request-id, logging, rate limit,
    # global error handling) are wired here in one place — never add
    # app.add_middleware(...) calls anywhere else.
    register_middlewares(app)

    # Typed handlers for exceptions our own code raises on purpose
    # (e.g. NotFoundError -> 404). Complements, doesn't duplicate,
    # the catch-all in app/middlewares/error_handler.py.
    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
```

---

## app/core/config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "backend"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str

    BACKEND_CORS_ORIGINS: list[str] = []
    RATE_LIMIT_PER_MINUTE: int = 120

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

---

## app/core/logging.py

```python
import logging
import logging.config
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
            },
            "handlers": {
                "console": {"class": "logging.StreamHandler", "formatter": "default"},
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(LOG_DIR / "app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 3,
                    "formatter": "default",
                },
            },
            "root": {"level": "INFO", "handlers": ["console", "file"]},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Used across the app — notably by app/middlewares/logging.py and
    app/middlewares/error_handler.py — so every component logs through
    the same configured handlers."""
    return logging.getLogger(name)
```

---

## app/middlewares

Full, complete middleware layer. `__init__.py` is the only file that ever calls `app.add_middleware(...)`; every other file just defines one middleware class or one piece of config.

`app/middlewares/__init__.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middlewares.cors import get_cors_config
from app.middlewares.error_handler import ErrorHandlingMiddleware
from app.middlewares.logging import RequestLoggingMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.request_id import RequestIDMiddleware


def register_middlewares(app: FastAPI) -> None:
    """Single place that wires every cross-cutting middleware into the app.

    Order matters: Starlette wraps middleware in reverse registration
    order, so the FIRST one added here becomes the OUTERMOST wrapper —
    it sees a request first and a response last. ErrorHandlingMiddleware
    must be outermost so it can catch failures raised by any middleware
    registered after it.
    """
    app.add_middleware(ErrorHandlingMiddleware)              # outermost: catches everything below
    app.add_middleware(CORSMiddleware, **get_cors_config())
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestIDMiddleware)                  # innermost: runs closest to the route
```

`app/middlewares/request_id.py`

```python
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a unique id to every request so it can be traced across
    logs, error reports, and downstream service calls."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
```

`app/middlewares/logging.py`

```python
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger("app.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs one line per request: method, path, status code, and
    duration. Tags each line with the request id set by
    RequestIDMiddleware so a single request can be traced end-to-end."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        request_id = getattr(request.state, "request_id", "-")
        logger.info(
            "%s %s -> %s (%.2fms) [request_id=%s]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
        return response
```

`app/middlewares/error_handler.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger

logger = get_logger("app.errors")


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Last-resort safety net. Registered as the outermost middleware
    (see app/middlewares/__init__.py) so it catches anything that
    escapes route handlers, dependencies, or other middleware —
    including bugs never anticipated by exceptions/handlers.py.
    Never leaks a raw traceback to the client."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception:
            request_id = getattr(request.state, "request_id", "-")
            logger.exception("Unhandled exception [request_id=%s]", request_id)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id},
            )
```

`app/middlewares/cors.py`

```python
from app.core.config import settings


def get_cors_config() -> dict:
    """Centralizes CORS policy so it's configured in one place instead
    of hardcoded inline in main.py. Consumed by
    app.add_middleware(CORSMiddleware, **get_cors_config())."""
    return {
        "allow_origins": settings.BACKEND_CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
```

`app/middlewares/rate_limit.py`

```python
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple fixed-window rate limiter keyed by client IP. In-memory —
    fine for a single instance / local dev. For multi-instance
    production, swap `_hits` for a Redis-backed counter (e.g. INCR +
    EXPIRE) without changing how this middleware is registered."""

    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        window = self._hits[client_ip]
        window[:] = [t for t in window if now - t < WINDOW_SECONDS]

        if len(window) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests, please try again later."},
            )

        window.append(now)
        return await call_next(request)
```

---

## app/db (session.py & base.py)

`app/db/base.py`

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

`app/db/session.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
```

---

## app/api/deps.py

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provides an isolated async database session per request."""
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

## app/api/v1/router.py

```python
from fastapi import APIRouter

from app.api.v1.endpoints import health, items

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items.router)
```

---

## health.py

`app/api/v1/endpoints/health.py`

```python
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
```

---

## Full resource example: items

Illustrates the standard `models → schemas → repositories → services → api/v1/endpoints` flow for a new resource. Copy this pattern for every other resource. Note this layer never touches `app/middlewares/` — middleware applies transparently to every route without any per-endpoint wiring.

`app/models/item.py`

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
```

`app/schemas/item.py`

```python
from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

`app/repositories/item.py` — repository layer, pure DB access

```python
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate


async def get(db: AsyncSession, item_id: int) -> Item | None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Item]:
    result = await db.execute(select(Item).offset(skip).limit(limit))
    return result.scalars().all()


async def create(db: AsyncSession, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item
```

`app/services/item_service.py` — business logic, knows nothing about HTTP

```python
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.custom import NotFoundError
from app.repositories import item as item_repository
from app.schemas.item import ItemCreate, ItemRead


def validate_item_name(name: str) -> None:
    """Pure in-memory business logic: sync def is optimal here."""
    if not name.strip():
        raise ValueError("Item name cannot be empty")


async def create_item(db: AsyncSession, data: ItemCreate) -> ItemRead:
    validate_item_name(data.name)
    item = await item_repository.create(db, data)
    return ItemRead.model_validate(item)


async def get_item(db: AsyncSession, item_id: int) -> ItemRead:
    item = await item_repository.get(db, item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} not found")
    return ItemRead.model_validate(item)


async def list_items(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ItemRead]:
    items = await item_repository.list_all(db, skip, limit)
    return [ItemRead.model_validate(i) for i in items]
```

`app/api/v1/endpoints/items.py` — controller

```python
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.item import ItemCreate, ItemRead
from app.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await item_service.create_item(db, data)


@router.get("/{item_id}", response_model=ItemRead)
async def read_item(
    item_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await item_service.get_item(db, item_id)


@router.get("", response_model=list[ItemRead])
async def list_items(
    skip: int = 0,
    limit: int = 100,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    return await item_service.list_items(db, skip, limit)
```

`app/exceptions/custom.py`

```python
class NotFoundError(Exception):
    pass
```

`app/exceptions/handlers.py`

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.custom import NotFoundError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    def handle_not_found(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})
```

---

## tests/conftest.py

```python
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
```

`tests/api/v1/test_health.py`

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

`tests/middlewares/test_request_id.py`

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_response_has_request_id_and_timing_headers(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time" in response.headers
```

---

## migrations (Alembic)

Initialize for async SQLAlchemy (run inside the venv, from `backend/`):

```bash
./.venv/bin/alembic init -t async migrations
# or, with uv:
uv run alembic init -t async migrations
```

Then edit `migrations/env.py` to point at the correct metadata and URL:

```python
from app.core.config import settings
from app.db.base import Base
import app.models  # noqa: F401  — import so models register themselves on Base.metadata

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata
```

Create the first migration:

```bash
./.venv/bin/alembic revision --autogenerate -m "init"
./.venv/bin/alembic upgrade head
# or, with uv:
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```
