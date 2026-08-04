# Design Patterns — Ví dụ đầy đủ với FastAPI/Python

## 1. Repository Pattern

Tách biệt database access logic. Cho phép thay đổi ORM/DB mà không ảnh hưởng business logic.

```python
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository."""

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**obj_in)
        )
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        return result.rowcount > 0

# Domain-specific repository extends BaseRepository
class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self, skip: int = 0, limit: int = 20) -> List[User]:
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
```

---

## 2. Unit of Work Pattern

Đảm bảo nhiều operations được thực hiện trong cùng một transaction.

```python
from contextlib import asynccontextmanager

class UnitOfWork:
    """Quản lý transaction boundary cho multiple repositories."""

    def __init__(self, session_factory):
        self._session_factory = session_factory

    async def __aenter__(self) -> "UnitOfWork":
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.orders = OrderRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

# Usage trong service
class OrderService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def place_order(self, user_id: int, items: List[OrderItem]) -> Order:
        async with self.uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError(user_id)

            # Cả hai operations trong cùng transaction
            order = await uow.orders.create({"user_id": user_id, "items": items})
            await uow.users.update(user_id, {"last_order_at": datetime.now()})

            await uow.commit()
            return order
```

---

## 3. Factory Pattern

Tạo objects mà không cần biết class cụ thể. Hữu ích cho multiple implementations.

```python
from enum import Enum

class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"

class StorageServiceInterface(ABC):
    @abstractmethod
    async def upload(self, file: bytes, filename: str) -> str:
        """Returns public URL của file đã upload."""
        ...

    @abstractmethod
    async def delete(self, file_url: str) -> None: ...

class LocalStorageService(StorageServiceInterface):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    async def upload(self, file: bytes, filename: str) -> str:
        file_path = self.base_path / filename
        file_path.write_bytes(file)
        return f"/files/{filename}"

class S3StorageService(StorageServiceInterface):
    def __init__(self, bucket: str, region: str):
        self._s3 = boto3.client("s3", region_name=region)
        self._bucket = bucket

    async def upload(self, file: bytes, filename: str) -> str:
        await asyncio.to_thread(
            self._s3.put_object,
            Bucket=self._bucket,
            Key=filename,
            Body=file
        )
        return f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{filename}"

# Factory function
def create_storage_service(config: Settings) -> StorageServiceInterface:
    if config.storage_type == StorageType.LOCAL:
        return LocalStorageService(config.local_storage_path)
    elif config.storage_type == StorageType.S3:
        return S3StorageService(config.s3_bucket, config.aws_region)
    elif config.storage_type == StorageType.GCS:
        return GCSStorageService(config.gcs_bucket)
    raise ValueError(f"Unsupported storage type: {config.storage_type}")

# FastAPI DI
@lru_cache  # singleton - chỉ tạo một lần
def get_storage_service() -> StorageServiceInterface:
    return create_storage_service(get_settings())
```

---

## 4. Strategy Pattern

Định nghĩa family of algorithms, đóng gói từng cái, cho phép swap lúc runtime.

```python
# Scenario: Multiple discount strategies

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order_total: Decimal, user: User) -> Decimal:
        """Returns discount amount (không phải percentage)."""
        ...

class NoDiscount(DiscountStrategy):
    def calculate(self, order_total: Decimal, user: User) -> Decimal:
        return Decimal("0")

class MembershipDiscount(DiscountStrategy):
    RATES = {
        "bronze": Decimal("0.05"),
        "silver": Decimal("0.10"),
        "gold": Decimal("0.15"),
    }

    def calculate(self, order_total: Decimal, user: User) -> Decimal:
        rate = self.RATES.get(user.membership_tier, Decimal("0"))
        return order_total * rate

class VoucherDiscount(DiscountStrategy):
    def __init__(self, voucher: Voucher):
        self._voucher = voucher

    def calculate(self, order_total: Decimal, user: User) -> Decimal:
        if order_total < self._voucher.min_order_amount:
            return Decimal("0")
        return min(self._voucher.discount_amount, order_total)

# Context sử dụng strategy
class OrderCalculator:
    def __init__(self, discount_strategy: DiscountStrategy):
        self._strategy = discount_strategy

    def calculate_final_price(self, order_total: Decimal, user: User) -> Decimal:
        discount = self._strategy.calculate(order_total, user)
        return max(Decimal("0"), order_total - discount)

# FastAPI endpoint
@router.post("/checkout")
async def checkout(
    cart: CartRequest,
    voucher_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    voucher_repo: VoucherRepository = Depends(get_voucher_repo),
):
    # Chọn strategy dựa trên context
    if voucher_code:
        voucher = await voucher_repo.get_valid_voucher(voucher_code, current_user.id)
        if voucher:
            strategy = VoucherDiscount(voucher)
        else:
            raise HTTPException(400, "Invalid or expired voucher")
    elif current_user.membership_tier:
        strategy = MembershipDiscount()
    else:
        strategy = NoDiscount()

    calculator = OrderCalculator(strategy)
    final_price = calculator.calculate_final_price(cart.total, current_user)
    return {"final_price": final_price}
```

---

## 5. Observer Pattern

Một object thay đổi → nhiều objects được notify. Hữu ích cho event-driven systems.

```python
# Scenario: User events trigger multiple side effects

from typing import Callable, Awaitable
from dataclasses import dataclass

@dataclass
class UserCreatedEvent:
    user_id: int
    email: str
    name: str

EventHandler = Callable[[any], Awaitable[None]]

class EventBus:
    """Simple in-process event bus."""

    def __init__(self):
        self._handlers: dict[type, list[EventHandler]] = {}

    def subscribe(self, event_type: type, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: any) -> None:
        handlers = self._handlers.get(type(event), [])
        await asyncio.gather(*[handler(event) for handler in handlers])

# Event handlers
async def send_welcome_email(event: UserCreatedEvent) -> None:
    await email_service.send_welcome(event.email, event.name)

async def create_user_profile(event: UserCreatedEvent) -> None:
    await profile_service.create_default_profile(event.user_id)

async def notify_admin(event: UserCreatedEvent) -> None:
    await notification_service.notify_new_user(event.user_id)

# Wire up handlers (ví dụ trong main.py hoặc startup event)
event_bus = EventBus()
event_bus.subscribe(UserCreatedEvent, send_welcome_email)
event_bus.subscribe(UserCreatedEvent, create_user_profile)
event_bus.subscribe(UserCreatedEvent, notify_admin)

# Service publish event
class UserService:
    def __init__(self, user_repo: UserRepository, event_bus: EventBus):
        self.user_repo = user_repo
        self.event_bus = event_bus

    async def register_user(self, data: UserCreate) -> User:
        user = await self.user_repo.create(data)

        # Publish event — service không cần biết ai xử lý
        await self.event_bus.publish(UserCreatedEvent(
            user_id=user.id,
            email=user.email,
            name=user.name
        ))
        return user
```

---

## 6. Decorator Pattern (Python native)

Thêm behavior vào function/method mà không thay đổi code gốc.

```python
import functools
import logging
import time

# Logging decorator
def log_execution(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper

# Retry decorator
def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    await asyncio.sleep(delay * (attempt + 1))
        return wrapper
    return decorator

# Cache decorator
def cache_result(ttl_seconds: int = 300):
    def decorator(func):
        _cache: dict = {}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            if cache_key in _cache:
                value, expires_at = _cache[cache_key]
                if time.time() < expires_at:
                    return value

            result = await func(*args, **kwargs)
            _cache[cache_key] = (result, time.time() + ttl_seconds)
            return result
        return wrapper
    return decorator

# Usage
class ExternalApiService:
    @retry(max_attempts=3, delay=0.5, exceptions=(httpx.HTTPError,))
    @log_execution
    @cache_result(ttl_seconds=60)
    async def fetch_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rates",
                params={"from": from_currency, "to": to_currency}
            )
            response.raise_for_status()
            return response.json()["rate"]
```

---

## 7. Singleton Pattern (qua FastAPI lifespan + lru_cache)

```python
# Đừng dùng class Singleton truyền thống. Dùng lru_cache hoặc FastAPI lifespan.

# Cách 1: lru_cache cho stateless singletons
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()

# Cách 2: FastAPI lifespan cho stateful singletons (DB pool, Redis, etc.)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db_pool = await create_async_engine(settings.database_url)
    app.state.redis = await aioredis.from_url(settings.redis_url)

    yield  # App runs here

    # Shutdown
    await app.state.db_pool.dispose()
    await app.state.redis.close()

app = FastAPI(lifespan=lifespan)
```

---

## 8. Facade Pattern

Cung cấp interface đơn giản cho hệ thống phức tạp.

```python
# Scenario: Checkout process gọi nhiều services

class CheckoutFacade:
    """
    Simplify checkout process bằng cách đóng gói coordination giữa các services.
    Clients chỉ gọi một method thay vì phải biết flow phức tạp bên trong.
    """

    def __init__(
        self,
        cart_service: CartService,
        payment_service: PaymentService,
        inventory_service: InventoryService,
        order_service: OrderService,
        notification_service: NotificationService,
    ):
        self._cart = cart_service
        self._payment = payment_service
        self._inventory = inventory_service
        self._orders = order_service
        self._notifications = notification_service

    async def process_checkout(
        self,
        user_id: int,
        payment_token: str,
        shipping_address: Address
    ) -> CheckoutResult:
        """
        Facade method — client chỉ cần gọi cái này.
        Bên trong tự xử lý validate cart → reserve stock → charge → create order → notify.
        """
        # 1. Validate cart
        cart = await self._cart.get_and_validate(user_id)

        # 2. Reserve inventory
        reservation = await self._inventory.reserve(cart.items)

        try:
            # 3. Process payment
            payment = await self._payment.charge(cart.total, payment_token)

            # 4. Create order
            order = await self._orders.create(
                user_id=user_id,
                items=cart.items,
                payment_id=payment.id,
                shipping_address=shipping_address
            )

            # 5. Notify
            await self._notifications.send_order_confirmation(order)

            return CheckoutResult(order_id=order.id, status="success")

        except PaymentError:
            await self._inventory.release(reservation)
            raise

# FastAPI endpoint — sử dụng facade, rất gọn
@router.post("/checkout")
async def checkout(
    request: CheckoutRequest,
    user: User = Depends(get_current_user),
    facade: CheckoutFacade = Depends(get_checkout_facade),
):
    return await facade.process_checkout(
        user_id=user.id,
        payment_token=request.payment_token,
        shipping_address=request.shipping_address
    )
```
