---
name: python-fastapi-code
description: >
  Skill hướng dẫn viết code Python và FastAPI chất lượng cao, áp dụng Clean Code, SOLID, và Design Patterns.
  Sử dụng skill này bất cứ khi nào người dùng yêu cầu:
  - Viết hoặc review code Python backend (FastAPI, SQLAlchemy, Pydantic, async/await)
  - Áp dụng các nguyên lý Clean Code trong Python (đặt tên, hàm, class, comment)
  - Áp dụng SOLID trong Python/FastAPI (SRP, OCP, LSP, ISP, DIP)
  - Thiết kế kiến trúc FastAPI (layered architecture, project structure, folder layout)
  - Áp dụng Design Patterns trong Python/FastAPI (Repository, Service Layer, Factory, Strategy, Observer, Dependency Injection...)
  - Tổ chức project FastAPI, tách layer router/service/repository/schema
  - Code review và refactor code Python backend
  - Xử lý async/await, error handling, validation với Pydantic trong FastAPI
  - Viết unit test, integration test cho FastAPI application

  LUÔN dùng skill này khi thấy bất kỳ đoạn code Python backend nào cần cải thiện,
  hoặc khi người dùng hỏi về cách cấu trúc, tổ chức, hay viết code Python/FastAPI tốt hơn.
---

# Python & FastAPI Clean Code Skill

Skill này cung cấp hướng dẫn toàn diện để viết code Python backend chất lượng cao với FastAPI,
áp dụng Clean Code, SOLID principles, và Design Patterns.

## Cách sử dụng skill này

1. Xác định loại yêu cầu → đọc phần tương ứng bên dưới
2. Với yêu cầu phức tạp (kiến trúc project, multiple patterns) → đọc thêm file reference liên quan
3. Luôn ưu tiên code Pythonic, type-safe, testable

## Nguyên tắc cốt lõi (đọc trước tiên)

### Thứ tự ưu tiên khi viết code

1. **Readable** (dễ đọc) > Clever (khéo léo)
2. **Explicit** (tường minh) > Implicit (ngầm hiểu)
3. **Simple** (đơn giản) > Complex (phức tạp)
4. **Testable** (có thể test) > Tightly coupled (kết hợp chặt)

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

### Naming - Nguyên tắc đặt tên tốt

```python
# BAD: tên mơ hồ, viết tắt khó hiểu
def proc_usr(u, f=False):
    d = get_d()
    ...

# GOOD: tên mô tả rõ ý định
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

### Functions - Nguyên tắc viết hàm sạch

```python
# BAD: hàm làm quá nhiều việc, nhiều tham số
def create_user(name, email, password, role, send_email, log_action, notify_admin):
    # validation
    # hash password
    # save to db
    # send email
    # log
    # notify
    ...

# GOOD: mỗi hàm một trách nhiệm, dùng dataclass/Pydantic cho nhiều tham số
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER

async def create_user(user_data: UserCreate) -> User:
    """Tạo user mới và trả về user đã được lưu."""
    hashed_password = hash_password(user_data.password)
    user = await user_repository.save(user_data, hashed_password)
    await email_service.send_welcome(user.email)
    return user
```

### Type Hints - Bắt buộc trong Python/FastAPI

```python
from typing import Optional, List, Dict, Any
from collections.abc import Sequence

# Luôn annotate function signatures
async def get_users(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None
) -> List[User]:
    ...

# Dùng TypeAlias cho type phức tạp
UserId = int
UserDict = Dict[str, Any]

# Python 3.10+: dùng X | Y thay vì Optional[X]
def find_user(user_id: int) -> User | None:
    ...
```

### Comments và Docstrings

```python
# BAD: comment giải thích "what" (code đã nói rõ)
# Tăng i lên 1
i += 1

# GOOD: comment giải thích "why"
# Delay 100ms để tránh rate limiting của external API
await asyncio.sleep(0.1)

# GOOD: docstring cho public API
async def calculate_discount(
    user: User,
    order_total: float
) -> float:
    """
    Tính giảm giá dựa trên hạng thành viên của user.

    Args:
        user: User object với membership_tier
        order_total: Tổng giá trị đơn hàng (VND)

    Returns:
        Số tiền được giảm (VND), không âm

    Raises:
        ValueError: Nếu order_total < 0
    """
    if order_total < 0:
        raise ValueError(f"order_total phải >= 0, nhận được: {order_total}")
    ...
```

### Pythonic Patterns

```python
# List comprehension thay vì vòng lặp thủ công
# BAD
active_users = []
for user in users:
    if user.is_active:
        active_users.append(user)

# GOOD
active_users = [user for user in users if user.is_active]

# Context managers cho resource management
async with get_db() as db:
    result = await db.execute(query)

# Dataclasses / Pydantic thay vì dict
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

Mỗi class/module chỉ có một lý do để thay đổi. Trong FastAPI: Router chỉ xử lý HTTP, Service chỉ xử lý business logic, Repository chỉ xử lý database.

```python
# BAD: endpoint làm quá nhiều việc
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

# GOOD: mỗi layer một trách nhiệm
@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(user)
```

> Xem chi tiết triển khai đầy đủ tại: `.agents/references/python-fastapi-code/solid-principles.md`

### O - Open/Closed Principle (OCP)

Mở để extend, đóng để modify. Dùng abstract base classes.

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

# Thêm channel mới không cần sửa code cũ
class PushNotification(NotificationChannel):
    async def send(self, recipient: str, message: str) -> bool:
        # push notification logic
        ...
```

### L - Liskov Substitution Principle (LSP)

Subclass phải có thể thay thế superclass mà không làm hỏng behavior.

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

# In-memory implementation cho testing
class InMemoryUserRepository(BaseRepository):
    async def get_by_id(self, id: int) -> Optional[User]:
        ...  # same contract, substitutable
```

### I - Interface Segregation Principle (ISP)

Tách interface lớn thành nhiều interface nhỏ, chuyên biệt.

```python
# BAD: interface quá lớn
class UserRepository(ABC):
    @abstractmethod
    async def get(self, id: int): ...
    @abstractmethod
    async def save(self, user): ...
    @abstractmethod
    async def delete(self, id: int): ...
    @abstractmethod
    async def get_analytics(self): ...  # không phải mọi repo đều cần
    @abstractmethod
    async def export_csv(self): ...     # không phải mọi repo đều cần

# GOOD: interfaces nhỏ, có thể kết hợp
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

Depend on abstractions, not concretions. FastAPI's `Depends()` là DI built-in.

```python
# BAD: service tạo dependency trực tiếp
class UserService:
    def __init__(self):
        self.repo = SQLUserRepository()  # tightly coupled!
        self.emailer = SendgridEmailer()  # tightly coupled!

# GOOD: inject abstractions qua constructor
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

## 3. FASTAPI PROJECT STRUCTURE

### Cấu trúc khuyến nghị (Domain-based)

```
fastapi-project/
├── alembic/                    # Database migrations
├── src/
│   ├── main.py                 # App entry point
│   ├── config.py               # Global settings (Pydantic BaseSettings)
│   ├── database.py             # DB session, engine setup
│   ├── exceptions.py           # Global exception handlers
│   │
│   ├── users/                  # Feature module
│   │   ├── __init__.py
│   │   ├── router.py           # HTTP endpoints ONLY
│   │   ├── service.py          # Business logic ONLY
│   │   ├── repository.py       # DB queries ONLY
│   │   ├── schemas.py          # Pydantic request/response models
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── dependencies.py     # FastAPI Depends factories
│   │   ├── exceptions.py       # Domain-specific exceptions
│   │   └── constants.py        # Domain constants
│   │
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── schemas.py
│   │   └── dependencies.py     # get_current_user, require_admin, etc.
│   │
│   └── common/                 # Shared utilities
│       ├── base_repository.py  # Generic CRUD base
│       ├── pagination.py       # Pagination schemas/logic
│       └── utils.py
├── tests/
│   ├── conftest.py             # Fixtures, test DB setup
│   ├── unit/
│   │   └── users/
│   │       ├── test_service.py
│   │       └── test_repository.py
│   └── integration/
│       └── test_users_api.py
├── pyproject.toml
└── .env
```

### Layer separation rules

| Layer             | Responsibility                | Được phép import                       |
| ----------------- | ----------------------------- | -------------------------------------- |
| `router.py`       | HTTP in/out, status codes     | service, schemas, dependencies         |
| `service.py`      | Business logic, orchestration | repository, schemas, external services |
| `repository.py`   | Database queries only         | models, database session               |
| `schemas.py`      | Request/response validation   | Pydantic only                          |
| `models.py`       | DB table definition           | SQLAlchemy only                        |
| `dependencies.py` | DI factory functions          | service, repository, config            |

---

## 4. DESIGN PATTERNS IN FASTAPI

Xem chi tiết từng pattern tại file references tương ứng.

### Repository Pattern

Tách biệt database access khỏi business logic:

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

### Dependency Injection Pattern (FastAPI native)

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

> Xem chi tiết: `.agents/references/python-fastapi-code/design-patterns.md`

---

## 5. ERROR HANDLING

```python
# exceptions.py (domain)
class DomainError(Exception):
    """Base cho tất cả domain errors."""
    pass

class UserNotFoundError(DomainError):
    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User {user_id} không tồn tại")

class EmailAlreadyExistsError(DomainError):
    def __init__(self, email: str):
        super().__init__(f"Email {email} đã được sử dụng")

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
# GOOD: async cho I/O operations
async def get_user_with_orders(user_id: int) -> UserWithOrders:
    # Chạy song song thay vì tuần tự
    user, orders = await asyncio.gather(
        user_repo.get_by_id(user_id),
        order_repo.get_by_user_id(user_id)
    )
    return UserWithOrders(user=user, orders=orders)

# BAD: blocking call trong async context
async def get_users():
    time.sleep(1)  # BLOCKS event loop!
    users = requests.get(...)  # BLOCKS event loop!

# GOOD: dùng async libraries
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

# Tách biệt request vs response schemas
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password phải có ít nhất 1 chữ hoa")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

# Không bao giờ expose password trong response!
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

## Files tham khảo chi tiết

- `.agents/references/python-fastapi-code/solid-principles.md` — Ví dụ đầy đủ SOLID với FastAPI
- `.agents/references/python-fastapi-code/design-patterns.md` — Repository, Factory, Strategy, Observer, Unit of Work
- `.agents/references/python-fastapi-code/project-structure.md` — Project structure, config, migrations

Đọc file tương ứng khi cần ví dụ chi tiết hoặc khi xử lý yêu cầu phức tạp.
