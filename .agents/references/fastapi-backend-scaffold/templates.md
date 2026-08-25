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
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "python-dotenv>=1.0.0",
    "psycopg2-binary>=2.9.0",   # drop if not using Postgres
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
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
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/<project-name>

# --- CORS ---
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
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

Runs at `http://localhost:8000` by default, docs at `/docs`.

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
├── core/ # config, security, logging
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
├── repositories/ # repository layer (pure DB access)
├── services/ # business logic
├── db/ # session/engine
├── dependencies/ # business-level dependencies
├── exceptions/ # custom exceptions
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
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.exceptions.handlers import register_exception_handlers


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## app/api/deps.py

```python
from collections.abc import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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

Illustrates the standard `models → schemas → repositories → services → api/v1/endpoints` flow for a new resource. Copy this pattern for every other resource.

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
from sqlalchemy.orm import Session

from app.models.item import Item
from app.schemas.item import ItemCreate


def get(db: Session, item_id: int) -> Item | None:
    return db.get(Item, item_id)


def list_all(db: Session, skip: int = 0, limit: int = 100) -> list[Item]:
    return db.query(Item).offset(skip).limit(limit).all()


def create(db: Session, data: ItemCreate) -> Item:
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
```

`app/services/item_service.py` — business logic, knows nothing about HTTP

```python
from sqlalchemy.orm import Session

from app.repositories import item as item_repository
from app.exceptions.custom import NotFoundError
from app.schemas.item import ItemCreate, ItemRead


def create_item(db: Session, data: ItemCreate) -> ItemRead:
    item = item_repository.create(db, data)
    return ItemRead.model_validate(item)


def get_item(db: Session, item_id: int) -> ItemRead:
    item = item_repository.get(db, item_id)
    if item is None:
        raise NotFoundError(f"Item {item_id} not found")
    return ItemRead.model_validate(item)


def list_items(db: Session, skip: int = 0, limit: int = 100) -> list[ItemRead]:
    items = item_repository.list_all(db, skip, limit)
    return [ItemRead.model_validate(i) for i in items]
```

`app/api/v1/endpoints/items.py` — controller

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.item import ItemCreate, ItemRead
from app.services import item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=201)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    return item_service.create_item(db, data)


@router.get("/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return item_service.get_item(db, item_id)


@router.get("", response_model=list[ItemRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return item_service.list_items(db, skip, limit)
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
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
```

`tests/api/v1/test_health.py`

```python
def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

---

## migrations (Alembic)

Initialize (run inside the venv, from `backend/`):

```bash
./.venv/bin/alembic init migrations
# or, with uv:
uv run alembic init migrations
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
