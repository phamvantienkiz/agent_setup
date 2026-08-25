---
name: fastapi-backend-scaffold
description: Guidance for scaffolding and organizing a Python backend/microservice project with FastAPI according to a fixed organizational standard (root is always backend/, dependency management via pyproject.toml + uvicorn, isolated virtualenv inside backend/.venv, strict controller/service/repository separation). Use this skill whenever the user asks to "create a backend project", "create a microservice", "scaffold a FastAPI project", "set up a Python backend", add a new endpoint/service/model to an existing backend, or needs to decide where a file belongs in a FastAPI project. Always consult this skill before running any pip/uv install, python -m venv, uvicorn command, or creating files inside a backend directory — even for a small ask like "add one new endpoint".
---

# FastAPI Backend Scaffold

This skill defines the **mandatory, non-negotiable standard** for every backend Python/FastAPI project the agent creates or edits. Goal: every backend the agent produces shares the same skeleton, cleanly separates controller (api) / service / repository, keeps the virtual environment strictly isolated, and never touches the user's system Python.

## 0. Non-negotiable rules (read before doing anything)

1. **The root of the entire backend is always the `backend/` directory** at the root of the repo/workspace. Create it if it doesn't exist. Never put FastAPI code at the repo root or mix it with frontend code.
2. **Never install packages into the system Python.** Every install command must run against `backend/.venv`. Before running an install or list command, the agent must verify `VIRTUAL_ENV` points to `backend/.venv` (see section 3). If the venv isn't active, **stop and activate it first** — never "just install on the system for now and fix it later".
3. Manage dependencies via **`pyproject.toml`** (PEP 621) at `backend/pyproject.toml`. Don't use `requirements.txt` as the source of truth (it may be exported for Docker compatibility if needed, but `pyproject.toml` is authoritative).
4. Run the server with **uvicorn**; the standard entrypoint is the `app.main:app` module.
5. Use **either `pip` or `uv` for environment/dependency management, whichever the user prefers or already has installed** — both operate on the same `backend/.venv` and the same `pyproject.toml`, so neither changes the project structure. Detect which tool is available/preferred and use it consistently for a given project; don't mix lockfiles from both without telling the user. See section 3 for exact commands for each.
6. Each backend is a **self-contained project**: it has its own `.gitignore`, `README.md`, `Dockerfile`, and `docker-compose.yml` inside `backend/`, not shared with the rest of the repo (unless the user explicitly asks otherwise).
7. Keep three layers strictly separated: **api (controller)** — receives the request, validates via schema, calls the service. **services (service)** — business logic. **repositories (repository)** — pure DB access. A layer may only call the layer below it, never upward or skipping a layer (api must never call the repository/DB directly).

If the user asks for something that conflicts with the rules above (e.g. "just install it on my machine to save time", "skip the venv"), the agent should briefly restate the reason (dependency isolation, avoiding version conflicts across projects) and propose the correct approach, unless the user explicitly confirms they want otherwise.

## 1. Workflow for scaffolding a new project

Follow in order, don't skip steps:

1. **Check the root.** Identify the root of the current repo/workspace. If `backend/` doesn't exist → `mkdir -p backend`. If it exists and already has content → stop and ask the user whether to overwrite/merge before proceeding.
2. **Create the full directory tree** per section 2 below (including empty directories that need a `.gitkeep`, e.g. `logs/`).
3. **Create `backend/pyproject.toml`** with project metadata + core dependencies (`fastapi`, `uvicorn[standard]`, `pydantic-settings`, `sqlalchemy`, `alembic`) + dev dependencies (`pytest`, `pytest-asyncio`, `httpx`, `ruff`). Full sample content is in `.agents\references\fastapi-backend-scaffold\templates.md#pyprojecttoml`.
4. **Create and activate the virtualenv** — exact commands per tool/OS are in section 3. After activating: upgrade pip (if using pip) then install the project in editable mode with dev extras.
5. **Create the scaffold code**: `app/main.py`, `app/core/config.py`, `app/api/v1/router.py`, `app/api/deps.py`, and one sample resource (e.g. `items`) spanning models → schemas → repositories → services → api/v1/endpoints as a template for future resources.
6. **Create project config files**: `.gitignore`, `README.md`, `.env.example`, `Dockerfile`, `docker-compose.yml`. Sample content in `.agents\references\fastapi-backend-scaffold\templates.md`.
7. **Create test skeleton** under `tests/` mirroring the `app/` structure (e.g. `tests/api/v1/test_items.py`), configure pytest in `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["tests"]`).
8. **Initialize Alembic** in `backend/migrations/` (`alembic init migrations`, run inside the venv), pointing `sqlalchemy.url` at `app.core.config.settings`.
9. **Verify (mandatory before reporting done):**
   - `uvicorn app.main:app --reload` (run from `backend/`, venv active) starts without errors.
   - `pytest` runs successfully (even with no real tests yet, at minimum a `GET /health` smoke test must pass).
   - `.venv/` is not committed (already covered by `.gitignore`).

When only asked to **add a small piece** (e.g. "add a new endpoint", "add service X") to an existing backend: check whether `backend/` already follows this structure; if it deviates, tell the user instead of silently creating a parallel structure. Still follow the rule of activating the venv before installing anything new.

## 2. Standard directory tree

```
repo-root/
└── backend/
    ├── .venv/                     # virtualenv, NEVER committed
    ├── .gitignore
    ├── README.md
    ├── pyproject.toml
    ├── .env.example
    ├── Dockerfile
    ├── docker-compose.yml
    ├── logs/                      # runtime logs, .gitkeep, NEVER commit *.log
    ├── docs/                      # backend-specific technical docs (ADRs, API notes...)
    ├── scripts/                   # utility scripts: dev.sh, migrate.sh, lint.sh, seed_db.py
    ├── migrations/                # Alembic
    │   ├── versions/
    │   └── env.py
    ├── tests/                     # pytest, structure mirrors app/
    │   ├── conftest.py
    │   ├── api/v1/
    │   └── services/
    └── app/
        ├── main.py                # creates the FastAPI app, registers router/middleware/lifespan
        ├── api/
        │   ├── deps.py            # shared dependencies for the whole api (get_db, get_current_user...)
        │   └── v1/
        │       ├── router.py      # aggregates all v1 sub-routers
        │       └── endpoints/     # 1 file = 1 resource (controller), e.g. items.py, users.py, auth.py
        ├── core/                  # config, security, logging setup, global constants
        │   ├── config.py          # Settings (pydantic-settings) read from .env
        │   ├── security.py        # hashing, JWT...
        │   └── logging.py         # logging configuration, writes to logs/
        ├── models/                # SQLAlchemy ORM models (represent DB tables)
        ├── schemas/                # Pydantic schemas (request/response), NO business logic
        ├── db/                    # session, base class, engine, init_db
        │   ├── base.py
        │   └── session.py
        ├── repositories/          # repository layer — pure DB access through models (renamed from "crud")
        ├── services/              # business logic — calls repositories, handles business rules, knows nothing about HTTP
        ├── dependencies/          # reusable business-level dependencies (distinct from api/deps.py, which is FastAPI-layer)
        ├── exceptions/            # custom exception classes + exception handlers
        └── utils/                 # pure helper functions (formatting, pagination, retry...)
```

> Every empty directory (e.g. `logs/`, `docs/`) needs a `.gitkeep` file so git keeps it.

## 3. Virtualenv: exact commands, pip or uv

Always run from inside `backend/` (the agent must `cd backend` first, or use absolute paths to the venv). **Both tools operate on the same `backend/.venv` and the same `pyproject.toml` — pick whichever the user prefers or already has installed on their machine; don't force one over the other.**

| Task                  | pip / venv (macOS, Linux)                               | pip / venv (Windows PowerShell)                                     | uv (any OS)                                 |
| --------------------- | ------------------------------------------------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| Create venv           | `python3 -m venv .venv`                                 | `python -m venv .venv`                                              | `uv venv .venv`                             |
| Activate              | `source .venv/bin/activate`                             | `.venv\Scripts\Activate.ps1`                                        | same as pip (uv doesn't replace activation) |
| Upgrade pip           | `python -m pip install --upgrade pip`                   | same                                                                | not needed                                  |
| Install deps (dev)    | `pip install -e ".[dev]"`                               | same                                                                | `uv pip install -e ".[dev]"`                |
| Run dev server        | `uvicorn app.main:app --reload`                         | same                                                                | `uv run uvicorn app.main:app --reload`      |
| Verify venv is active | `which python` must point to `backend/.venv/bin/python` | `where.exe python` must point to `backend\.venv\Scripts\python.exe` | same check applies                          |
| Deactivate            | `deactivate`                                            | `deactivate`                                                        | `deactivate`                                |

In a **non-interactive agent bash environment** (where each command is its own process and doesn't inherit an earlier `source activate`), always call the venv's interpreter/pip directly instead of relying on activation persisting across commands:

```bash
cd backend

# --- with pip ---
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e ".[dev]"
./.venv/bin/uvicorn app.main:app --reload
./.venv/bin/pytest

# --- or with uv (equivalent, faster) ---
uv venv .venv
uv pip install -e ".[dev]"
uv run uvicorn app.main:app --reload
uv run pytest
```

Either path guarantees every command runs against `backend/.venv`, regardless of whether individual bash calls share shell state.

## 4. Role of each layer in `app/` (controller → service → repository)

| Directory           | Role                                                                                                                  | Allowed to call                                            | NOT allowed to                                                                          |
| ------------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `api/v1/endpoints/` | **Controller.** Receives the HTTP request, validates input via `schemas/`, calls `services/`, returns the response.   | `schemas`, `services`, `api/deps.py`                       | Import `models` directly to query the DB, call `repositories/` directly                 |
| `services/`         | **Business logic.** Orchestrates business rules, combines multiple repositories, transactions, calls other services.  | `repositories`, `schemas`, `models`, `exceptions`, `utils` | Know about `Request`/`Response`/HTTP status codes — services must not depend on FastAPI |
| `repositories/`     | **Repository.** Pure DB access through `models` only (create/get/update/delete/query).                                | `models`, `db/session`                                     | Contain business rules (e.g. permission checks, pricing) — that belongs in `services/`  |
| `models/`           | ORM entities, mapped to DB tables.                                                                                    | `db/base`                                                  | Must not import `schemas` or `services`                                                 |
| `schemas/`          | Pydantic models for request/response, pure validation.                                                                | —                                                          | No business logic or DB queries                                                         |
| `dependencies/`     | Reusable business-level dependencies (e.g. resource-scoped permission checks) used via `Depends(...)` in controllers. | `services`, `repositories`                                 | —                                                                                       |
| `exceptions/`       | Custom exceptions + exception handlers registered in `main.py`.                                                       | —                                                          | —                                                                                       |
| `utils/`            | Pure functions, no business side effects (pagination, datetime formatting...).                                        | —                                                          | Must not depend on `models`/`db`                                                        |

**Standard flow for a new resource** (e.g. `items`): `models/item.py` → `schemas/item.py` → `repositories/item.py` → `services/item_service.py` → `api/v1/endpoints/items.py` → registered in `api/v1/router.py`.

## 5. `app/api/` in detail

```
app/api/
├── deps.py              # get_db(), get_current_user(), shared pagination... used via Depends() in every endpoint
└── v1/
    ├── router.py         # APIRouter() that aggregates include_router() calls from each endpoints/*.py, mounted under "/v1"
    └── endpoints/
        ├── health.py      # GET /health — mandatory, used for healthchecks & smoke tests
        ├── items.py
        └── ...
```

- Each file in `endpoints/` declares its own `router = APIRouter(prefix="/items", tags=["items"])` and only exports `router`.
- `v1/router.py` is the single place that calls `include_router()` on sub-routers — endpoints never register themselves on the main `app`.
- `app/main.py` only does `include_router(api_router, prefix="/api")` — it knows nothing about individual resources.
- When `v2` is needed, create a parallel `api/v2/` directory; `main.py` includes both — don't modify `v1` in place, to preserve backward compatibility.

## 6. Where `main.py` belongs — the standard decision

**Use `backend/app/main.py`**, NOT `backend/main.py`. Reasoning:

- The entire `app/` tree is one cohesive Python package (`app/__init__.py`), so the `app.main:app` entrypoint is consistent with standard uvicorn/Docker production setups (`CMD ["uvicorn", "app.main:app", ...]`) and with most popular FastAPI templates (e.g. the FastAPI author's own full-stack-fastapi-template follows this convention).
- Placing `backend/main.py` outside the package is both inconsistent (an orphaned file outside `app/`) and error-prone — it blurs the line between "entrypoint you run directly with `python main.py`" and "entrypoint for uvicorn", which can resolve imports differently.
- Dev run: `uvicorn app.main:app --reload` (from `backend/`, venv active).
- No separate `run.py` / `backend/main.py` is needed; if the user wants a shortcut command, add it to `scripts/dev.sh` rather than introducing a second entrypoint.

`app/main.py` is responsible for: creating the `FastAPI()` instance (via a `create_app()` factory for easier testing), attaching CORS middleware, registering exception handlers from `exceptions/`, including `api_router`, and (if needed) a `lifespan` to init/close DB connections. Full sample code is in `.agents\references\fastapi-backend-scaffold\templates.md#appmainpy`.

## 7. Backend-specific config files

All live inside `backend/`, not shared with the repo root. Full copy-pasteable content is in `.agents\references\fastapi-backend-scaffold\templates.md`:

- **`.gitignore`** — ignores `.venv/`, `__pycache__/`, `*.log`, `.env`, `.pytest_cache/`, `.mypy_cache/`, `uv.lock`-adjacent build artifacts if applicable, etc.
- **`README.md`** — instructions for setting up the venv (pip or uv), running dev, running tests, running Docker, directory structure.
- **`.env.example`** — lists required environment variables (never commit the real `.env`).
- **`Dockerfile`** — multi-stage build. **Note:** the container does NOT need a `.venv` inside it (the container itself is already an isolated environment) — the venv is only required for local host development. The Dockerfile installs directly via `pip install .` (or `uv pip install .`) inside the image.
- **`docker-compose.yml`** — a `backend` service + a DB service (e.g. `postgres`) for local dev, with code mounted to support `--reload`.

## 8. Checklist before reporting "done"

- [ ] `backend/` sits at the repo root, not mixed with other code.
- [ ] `backend/.venv/` exists; every install command ran through the venv's `pip`/`uv` (system Python untouched).
- [ ] `pyproject.toml` is the single source of truth for dependencies.
- [ ] `app/` has all 9 layer directories: `api, core, models, schemas, services, repositories, db, dependencies, exceptions, utils`.
- [ ] `api/v1/` has `router.py`, `endpoints/`, and `api/deps.py` sits at the `api/` level.
- [ ] `app/main.py` exists (not `backend/main.py`), and `uvicorn app.main:app` runs successfully.
- [ ] `.gitignore`, `README.md`, `Dockerfile`, `docker-compose.yml`, `.env.example` all exist in `backend/`.
- [ ] `tests/` run successfully via `pytest`, with at least a smoke test for `/health`.
- [ ] `migrations/` (Alembic) is initialized and correctly points at `models/` metadata.

## 9. Detailed templates

All copy-pasteable sample content (`pyproject.toml`, `.gitignore`, `Dockerfile`, `docker-compose.yml`, `README.md`, `.env.example`, `app/main.py`, `core/config.py`, `api/deps.py`, `api/v1/router.py`, a full `items` resource example spanning models→schemas→repositories→services→endpoints) lives in `.agents\references\fastapi-backend-scaffold\templates.md`. Read that file when actually starting to create each file — no need to load it all into context if you're just answering a question about the structure.
