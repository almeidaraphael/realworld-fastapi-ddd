# Code Integration Examples

This document shows how the architectural diagrams map to actual code structure, helping developers understand the relationship between visual architecture and implementation.

## Component Diagram to Code Structure

### API Layer → Code Mapping

**Diagram Component**: Users API (FastAPI Router)
```
Component(api_users, "Users API", "FastAPI Router", "Handles user registration, authentication, and profile management")
```

**Code Location**: `app/api/users.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.service_layer.users.services import UserService
from app.domain.users.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, service: UserService = Depends()) -> UserResponse:
    return await service.create_user(user_data)
```

### Service Layer → Code Mapping

**Diagram Component**: User Service (Application Service)
```
Component(svc_users, "User Service", "Application Service", "Orchestrates user-related business operations")
```

**Code Location**: `app/service_layer/users/services.py`
```python
from app.shared.transaction import transactional
from app.adapters.orm.unit_of_work import AsyncUnitOfWork

class UserService:
    @transactional()
    async def create_user(self, uow: AsyncUnitOfWork, user_data: UserCreate) -> User:
        # Business logic orchestration
        user_repo = UserRepository(uow.session)
        # ... implementation
```

### Domain Layer → Code Mapping

**Diagram Component**: Users Domain (Domain Models & Logic)
```
Component(domain_users, "Users Domain", "Domain Models & Logic", "User entities, value objects, and business rules")
```

**Code Locations**:
- **Models**: `app/domain/users/models.py`
```python
@dataclass
class User:
    id: int | None = None
    username: str = ""
    email: str = ""
    # Pure domain model - no infrastructure dependencies
```

- **ORM Mapping**: `app/domain/users/orm.py`
```python
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.metadata import Base

class UserORM(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    # SQLAlchemy-specific infrastructure
```

### Repository Layer → Code Mapping

**Diagram Component**: User Repository (Repository Pattern)
```
Component(repo_users, "User Repository", "Repository Pattern", "Data access for user operations")
```

**Code Location**: `app/adapters/repository/users.py`
```python
from app.adapters.repository.base import BaseRepository
from app.domain.users.models import User
from app.domain.users.orm import UserORM

class UserRepository(BaseRepository[User, UserORM]):
    async def get_by_username(self, username: str) -> User | None:
        # Data access implementation
```

## Sequence Diagram to Request Flow

### Request Flow Example: User Registration

**Diagram Flow**:
```
Client->>API: POST /users
API->>Service: create_user(data)
Service->>Domain: Create User entity
Service->>Repository: save_user(user)
Repository->>Database: INSERT user
```

**Code Flow**:

1. **Client Request** → **API Endpoint** (`app/api/users.py:15`)
```python
@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreate, service: UserService = Depends()):
```

2. **API** → **Service Layer** (`app/service_layer/users/services.py:23`)
```python
@transactional()
async def create_user(self, uow: AsyncUnitOfWork, user_data: UserCreate) -> User:
```

3. **Service** → **Domain Layer** (`app/domain/users/models.py:12`)
```python
@dataclass
class User:
    def __post_init__(self):
        # Domain validation logic
```

4. **Service** → **Repository** (`app/adapters/repository/users.py:18`)
```python
async def save(self, user: User) -> User:
    # Data persistence logic
```

5. **Repository** → **Database** (via SQLAlchemy ORM)

## Event-Driven Architecture Mapping

### Event Bus Component → Code

**Diagram Component**: Event Bus (Event System)
```
Component(event_bus, "Event Bus", "Event System", "Handles domain events and cross-cutting concerns")
```

**Code Locations**:

- **Event Bus**: `app/events/core.py`
```python
class EventBus:
    def publish(self, event: DomainEvent) -> None:
        # Event publishing logic
        
shared_event_bus = EventBus()
```

- **Domain Events**: `app/events/domain/users.py`
```python
@dataclass
class UserCreated(DomainEvent):
    user_id: int
    username: str
    email: str
```

- **Event Handlers**: `app/events/handlers/domain/users.py`
```python
@shared_event_bus.handler(UserCreated)
async def handle_user_created(event: UserCreated) -> None:
    # Cross-cutting concern handling
```

## Transaction Management Integration

### UoW Pattern → Code

**Diagram Component**: Transaction Manager (UoW Pattern)
```
Component(transaction_mgr, "Transaction Manager", "UoW Pattern", "Manages database transactions")
```

**Code Implementation**:

- **Transaction Decorator**: `app/shared/transaction.py`
```python
def transactional():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with AsyncUnitOfWork() as uow:
                result = await func(uow, *args, **kwargs)
                await uow.commit()
                return result
        return wrapper
    return decorator
```

- **Unit of Work**: `app/adapters/orm/unit_of_work.py`
```python
class AsyncUnitOfWork:
    async def __aenter__(self):
        self.session = async_session_factory()
        return self
    
    async def commit(self):
        await self.session.commit()
```

## Directory Structure Alignment

The code organization directly reflects the architectural layers:

```
app/
├── api/              # API Layer (FastAPI routers)
│   ├── users.py      # Maps to: Users API component
│   ├── articles.py   # Maps to: Articles API component
│   └── ...
├── service_layer/    # Service Layer (Application services)
│   ├── users/        # Maps to: User Service component
│   ├── articles/     # Maps to: Article Service component
│   └── ...
├── domain/           # Domain Layer (Business logic)
│   ├── users/        # Maps to: Users Domain component
│   │   ├── models.py # Domain entities
│   │   ├── orm.py    # Infrastructure mapping
│   │   └── schemas.py# API contracts
│   └── ...
├── adapters/         # Infrastructure Layer
│   ├── repository/   # Maps to: Repository components
│   └── orm/          # Maps to: ORM Engine component
├── events/           # Event-Driven Architecture
│   ├── core.py       # Maps to: Event Bus component
│   ├── domain/       # Domain events
│   └── handlers/     # Event handlers
└── shared/           # Cross-cutting concerns
    ├── transaction.py# Maps to: Transaction Manager
    └── jwt.py        # Maps to: JWT Utilities
```

This alignment ensures that:
- Diagrams accurately represent the codebase structure
- New developers can navigate from diagrams to code
- Architectural decisions are enforced in the implementation
- Refactoring efforts maintain diagram-code consistency