# SOLID Principles — Ví dụ đầy đủ với FastAPI

## S — Single Responsibility Principle (SRP)

Cấu trúc 3 layer chuẩn cho một feature:

```python
# ===== schemas.py =====
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ===== models.py =====
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ===== repository.py =====
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class UserRepository:
    """Chỉ chịu trách nhiệm: truy vấn database liên quan đến User."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, name: str, email: str, hashed_password: str) -> User:
        user = User(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def exists_by_email(self, email: str) -> bool:
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None


# ===== service.py =====
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

class UserService:
    """Chỉ chịu trách nhiệm: business logic liên quan đến User."""

    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.email_service = email_service

    async def register_user(self, data: UserCreate) -> User:
        """Đăng ký user mới: validate → hash password → save → send email."""
        if await self.user_repo.exists_by_email(data.email):
            raise EmailAlreadyExistsError(data.email)

        hashed_pw = pwd_context.hash(data.password)
        user = await self.user_repo.create(data.name, data.email, hashed_pw)
        await self.email_service.send_welcome(user.email, user.name)
        return user

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user


# ===== router.py =====
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    """Chỉ chịu trách nhiệm: nhận HTTP request, trả HTTP response."""
    return await service.register_user(data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

---

## O — Open/Closed Principle (OCP)

Pattern: Abstract base class + concrete implementations.

```python
# Scenario: Hệ thống payment hỗ trợ nhiều provider

from abc import ABC, abstractmethod
from decimal import Decimal

# Abstract interface — đóng để modify
class PaymentGateway(ABC):
    @abstractmethod
    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        ...

    @abstractmethod
    async def refund(self, transaction_id: str, amount: Decimal) -> RefundResult:
        ...

# Concrete implementations — mở để extend
class StripeGateway(PaymentGateway):
    def __init__(self, api_key: str):
        self._client = stripe.AsyncClient(api_key)

    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        result = await self._client.charge.create(
            amount=int(amount * 100),
            currency=currency,
            source=token
        )
        return PaymentResult(transaction_id=result.id, status="success")

    async def refund(self, transaction_id: str, amount: Decimal) -> RefundResult:
        ...

class VNPayGateway(PaymentGateway):
    async def charge(self, amount: Decimal, currency: str, token: str) -> PaymentResult:
        # VNPay-specific implementation
        ...

# Service không cần thay đổi khi thêm provider mới
class OrderService:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment = payment_gateway

    async def checkout(self, order: Order, token: str) -> PaymentResult:
        return await self.payment.charge(order.total, "VND", token)

# FastAPI DI: chọn gateway qua config
def get_payment_gateway() -> PaymentGateway:
    if settings.payment_provider == "stripe":
        return StripeGateway(settings.stripe_api_key)
    elif settings.payment_provider == "vnpay":
        return VNPayGateway(settings.vnpay_config)
    raise ValueError(f"Unsupported: {settings.payment_provider}")
```

---

## L — Liskov Substitution Principle (LSP)

Subclasses phải fulfill cùng contract với superclass.

```python
from abc import ABC, abstractmethod

class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Returns User hoặc None — không raise exception nếu không tìm thấy."""
        ...

    @abstractmethod
    async def save(self, user: User) -> User:
        """Saves và returns user đã được persist. Raises PersistenceError nếu fail."""
        ...

# Production implementation
class SQLUserRepository(UserRepositoryInterface):
    async def get_by_id(self, user_id: int) -> Optional[User]:
        # Returns User | None — đúng contract
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

# Test implementation — LSP: hoàn toàn substitutable
class InMemoryUserRepository(UserRepositoryInterface):
    def __init__(self):
        self._store: dict[int, User] = {}
        self._id_counter = 1

    async def get_by_id(self, user_id: int) -> Optional[User]:
        return self._store.get(user_id)  # đúng contract: User | None

    async def save(self, user: User) -> User:
        if not user.id:
            user.id = self._id_counter
            self._id_counter += 1
        self._store[user.id] = user
        return user

# Service hoạt động với cả 2 implementations
service = UserService(repo=SQLUserRepository(db))       # production
service = UserService(repo=InMemoryUserRepository())    # testing
```

---

## I — Interface Segregation Principle (ISP)

```python
# Scenario: Một số clients chỉ cần đọc, một số cần ghi, một số cần cả hai

class UserReader(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]: ...

    @abstractmethod
    async def list_active(self, skip: int = 0, limit: int = 20) -> list[User]: ...

class UserWriter(ABC):
    @abstractmethod
    async def create(self, data: UserCreate) -> User: ...

    @abstractmethod
    async def update(self, user_id: int, data: UserUpdate) -> User: ...

class UserDeleter(ABC):
    @abstractmethod
    async def delete(self, user_id: int) -> None: ...

# Full implementation implements tất cả
class UserRepository(UserReader, UserWriter, UserDeleter):
    async def get_by_id(self, user_id: int) -> Optional[User]: ...
    async def list_active(self, skip: int, limit: int) -> list[User]: ...
    async def create(self, data: UserCreate) -> User: ...
    async def update(self, user_id: int, data: UserUpdate) -> User: ...
    async def delete(self, user_id: int) -> None: ...

# Analytics service chỉ cần đọc
class UserAnalyticsService:
    def __init__(self, user_reader: UserReader):  # ISP: chỉ inject interface cần dùng
        self.reader = user_reader

# Admin service cần tất cả
class UserAdminService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
```

---

## D — Dependency Inversion Principle (DIP)

```python
# Scenario: Email service với multiple providers

class EmailServiceInterface(ABC):
    @abstractmethod
    async def send_welcome(self, to_email: str, username: str) -> None: ...

    @abstractmethod
    async def send_password_reset(self, to_email: str, reset_token: str) -> None: ...

class SendgridEmailService(EmailServiceInterface):
    def __init__(self, api_key: str, from_email: str):
        self._client = SendGridAPIClient(api_key)
        self._from = from_email

    async def send_welcome(self, to_email: str, username: str) -> None:
        message = Mail(
            from_email=self._from,
            to_emails=to_email,
            subject="Welcome!",
            html_content=render_welcome_template(username)
        )
        await self._client.send(message)

class MockEmailService(EmailServiceInterface):
    """For testing — không thực sự gửi email."""
    def __init__(self):
        self.sent_emails: list[dict] = []

    async def send_welcome(self, to_email: str, username: str) -> None:
        self.sent_emails.append({"type": "welcome", "to": to_email})

# Service depend on abstraction, không phải concrete class
class UserService:
    def __init__(
        self,
        user_repo: UserRepositoryInterface,   # abstraction
        email_service: EmailServiceInterface,  # abstraction
    ):
        self.user_repo = user_repo
        self.email_service = email_service

# dependencies.py — wire up concretes
def get_email_service() -> EmailServiceInterface:
    return SendgridEmailService(
        api_key=settings.sendgrid_api_key,
        from_email=settings.from_email
    )

def get_user_service(
    db: AsyncSession = Depends(get_db),
    email_svc: EmailServiceInterface = Depends(get_email_service),
) -> UserService:
    return UserService(
        user_repo=SQLUserRepository(db),
        email_service=email_svc
    )
```
