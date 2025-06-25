# Domain-Driven Design Architecture

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

This document explains the Domain-Driven Design (DDD) architecture implementation in the FastAPI RealWorld Demo project.

## Table of Contents

- [DDD Overview](#ddd-overview)
- [Architecture Layers](#architecture-layers)
- [Domain Structure](#domain-structure)
- [Implementation Patterns](#implementation-patterns)
- [Data Flow](#data-flow)
- [Best Practices](#best-practices)

## DDD Overview

Domain-Driven Design is a software development approach that focuses on creating a shared understanding of the business domain and expressing that understanding in code.

### Core Principles

1. **Domain First**: Business logic is the primary concern
2. **Ubiquitous Language**: Shared terminology between developers and domain experts
3. **Bounded Contexts**: Clear boundaries between different domain areas
4. **Rich Domain Models**: Business logic lives in domain entities, not services
5. **Separation of Concerns**: Clear separation between layers

## Architecture Layers

The application follows a clean architecture with four distinct layers:

```
┌─────────────────────────────────────┐
│           API Layer                 │  ← HTTP interface, request/response handling
├─────────────────────────────────────┤
│       Application/Service Layer     │  ← Use cases, orchestration, transactions
├─────────────────────────────────────┤
│          Domain Layer               │  ← Business logic, entities, domain services
├─────────────────────────────────────┤
│       Infrastructure Layer          │  ← External concerns, databases, repositories
└─────────────────────────────────────┘
```

### 1. Domain Layer (`app/domain/`)

**Purpose**: Contains the core business logic and domain rules.

**Components**:
- **Domain Models**: Pure business entities (dataclasses)
- **Domain Exceptions**: Business rule violations
- **Domain Events**: Significant business occurrences
- **Value Objects**: Immutable objects with no identity

**Example Structure**:
```
app/domain/users/
├── models.py      # Domain entities (User, Follower)
├── schemas.py     # Pydantic models for API serialization
├── exceptions.py  # Domain-specific exceptions
└── orm.py         # SQLAlchemy mappings (infrastructure concern)
```

**Domain Model Example**:
```python
# app/domain/users/models.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    """Pure domain model representing a user."""
    username: str
    email: str
    hashed_password: str
    bio: Optional[str] = ""
    image: Optional[str] = ""
    id: Optional[int] = None
    
    def can_edit_article(self, article: 'Article') -> bool:
        """Business rule: Users can only edit their own articles."""
        return self.id == article.author_id
```

### 2. Application/Service Layer (`app/service_layer/`)

**Purpose**: Orchestrates business operations and coordinates between domain and infrastructure.

**Responsibilities**:
- Use case implementation
- Transaction management
- Domain event publishing
- Coordination between repositories

**Service Example**:
```python
# app/service_layer/users/authentication.py
from app.shared.transaction import transactional
from app.adapters.repository.users import UserRepository

@transactional()
async def authenticate_user(
    uow: AsyncUnitOfWork, 
    email: str, 
    password: str
) -> UserRead:
    """
    Authenticate user with email and password.
    
    This service coordinates the authentication process:
    1. Retrieve user by email
    2. Verify password
    3. Return user data or raise exception
    """
    repo = UserRepository(uow.session)
    
    # Get user from repository
    user_orm = await repo.get_by_email(email)
    if not user_orm:
        raise InvalidCredentialsError()
    
    # Verify password (domain logic)
    if not verify_password(password, user_orm.hashed_password):
        raise InvalidCredentialsError()
    
    # Convert to domain model and return
    user = User(**user_orm.__dict__)
    return UserRead.model_validate(user.__dict__)
```

### 3. API Layer (`app/api/`)

**Purpose**: HTTP interface and request/response handling.

**Responsibilities**:
- HTTP request validation
- Response serialization
- Authentication/authorization
- Error handling (converts domain exceptions to HTTP responses)

**API Example**:
```python
# app/api/users.py
from fastapi import APIRouter, HTTPException
from app.service_layer.users.authentication import authenticate_user
from app.domain.users.exceptions import InvalidCredentialsError

router = APIRouter()

@router.post("/users/login", response_model=UserResponse)
async def login_user(user_req: LoginUserRequest) -> UserResponse:
    """User login endpoint."""
    try:
        # Call service layer
        user = await authenticate_user(
            user_req.user.email, 
            user_req.user.password
        )
        
        # Generate JWT token
        token = create_access_token(user.id)
        user_with_token = UserWithToken(**user.dict(), token=token)
        
        return UserResponse(user=user_with_token)
        
    except InvalidCredentialsError:
        # Convert domain exception to HTTP response
        raise HTTPException(
            status_code=422,
            detail={"errors": {"body": ["Invalid email or password"]}}
        )
```

### 4. Infrastructure Layer (`app/adapters/`)

**Purpose**: External concerns like databases, file systems, external APIs.

**Components**:
- **Repository Implementations**: Data access logic
- **ORM Configurations**: Database mappings
- **Unit of Work**: Transaction management
- **External Service Adapters**: Third-party integrations

**Repository Example**:
```python
# app/adapters/repository/users.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.adapters.orm.users import UserORM

class UserRepository:
    """Repository for user data access."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_email(self, email: str) -> UserORM | None:
        """Retrieve user by email address."""
        result = await self.session.execute(
            select(UserORM).where(UserORM.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> UserORM:
        """Create new user in database."""
        user_orm = UserORM(**user_data)
        self.session.add(user_orm)
        await self.session.flush()  # Get ID without committing
        return user_orm
```

## Domain Structure

Each domain follows a consistent structure:

### Users Domain
```
app/domain/users/
├── models.py      # User, Follower domain entities
├── schemas.py     # UserRead, UserCreate, UserUpdate Pydantic models
├── exceptions.py  # UserNotFoundError, EmailAlreadyExistsError
└── orm.py         # SQLAlchemy User and Follower table mappings
```

### Articles Domain
```
app/domain/articles/
├── models.py      # Article domain entity
├── schemas.py     # ArticleRead, ArticleCreate, ArticleUpdate
├── exceptions.py  # ArticleNotFoundError, UnauthorizedArticleAccessError
└── orm.py         # SQLAlchemy Article table mapping
```

### Comments Domain
```
app/domain/comments/
├── models.py      # Comment domain entity
├── schemas.py     # CommentRead, CommentCreate
├── exceptions.py  # CommentNotFoundError, UnauthorizedCommentAccessError
└── orm.py         # SQLAlchemy Comment table mapping
```

## Implementation Patterns

### 1. Domain Model Pattern

Domain models are pure Python dataclasses with business logic:

```python
@dataclass
class Article:
    title: str
    description: str
    body: str
    author_id: int
    slug: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Generate slug from title if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
    
    def can_be_edited_by(self, user_id: int) -> bool:
        """Business rule: Only author can edit article."""
        return self.author_id == user_id
```

### 2. Repository Pattern

Repositories abstract data access:

```python
class ArticleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_slug(self, slug: str) -> ArticleORM | None:
        result = await self.session.execute(
            select(ArticleORM).where(ArticleORM.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def list_by_author_id(self, author_id: int) -> list[ArticleORM]:
        result = await self.session.execute(
            select(ArticleORM).where(ArticleORM.author_id == author_id)
        )
        return list(result.scalars().all())
```

### 3. Unit of Work Pattern

Manages transactions across multiple repositories:

```python
from app.shared.transaction import transactional

@transactional()
async def create_article_with_tags(
    uow: AsyncUnitOfWork,
    article_data: ArticleCreate,
    user: User
) -> ArticleRead:
    """Create article and associate tags in single transaction."""
    
    # Multiple repository operations in one transaction
    article_repo = ArticleRepository(uow.session)
    tag_repo = TagRepository(uow.session)
    
    # Create article
    article = await article_repo.create({
        **article_data.dict(),
        "author_id": user.id
    })
    
    # Create/associate tags
    for tag_name in article_data.tag_list:
        tag = await tag_repo.get_or_create(tag_name)
        await article_repo.add_tag(article.id, tag.id)
    
    # Transaction automatically committed by decorator
    return ArticleRead.model_validate(article.__dict__)
```

### 4. Domain Events Pattern

Capture significant business events:

```python
# Domain event
@dataclass
class UserRegisteredEvent:
    user_id: int
    email: str
    username: str
    timestamp: datetime

# Event publishing (in service layer)
@transactional()
async def register_user(uow: AsyncUnitOfWork, user_data: NewUserRequest) -> UserRead:
    # Create user logic...
    
    # Publish domain event
    event = UserRegisteredEvent(
        user_id=user.id,
        email=user.email,
        username=user.username,
        timestamp=datetime.utcnow()
    )
    await publish_event(event)
    
    return user_read
```

## Data Flow

### Request Flow
```
1. HTTP Request → API Layer
2. API Layer → Service Layer (use case)
3. Service Layer → Domain Models (business logic)
4. Service Layer → Repository (data access)
5. Repository → Database
```

### Response Flow
```
1. Database → Repository (ORM objects)
2. Repository → Service Layer
3. Service Layer → Domain Models → Pydantic Schemas
4. API Layer → HTTP Response (JSON)
```

### Example: Create Article Flow

```python
# 1. API Layer receives HTTP request
@router.post("/articles", response_model=ArticleResponse)
async def create_article(
    article_req: NewArticleRequest,
    current_user: User = Depends(get_current_user)
) -> ArticleResponse:
    # 2. Call service layer
    article = await create_article_service(article_req, current_user)
    return ArticleResponse(article=article)

# 3. Service layer coordinates business operation
@transactional()
async def create_article_service(
    uow: AsyncUnitOfWork,
    article_req: NewArticleRequest, 
    user: User
) -> ArticleRead:
    # 4. Use repository for data access
    repo = ArticleRepository(uow.session)
    
    # 5. Create domain model
    article = Article(
        title=article_req.article.title,
        description=article_req.article.description,
        body=article_req.article.body,
        author_id=user.id
    )
    
    # 6. Persist via repository
    article_orm = await repo.create(article.__dict__)
    
    # 7. Return Pydantic model
    return ArticleRead.model_validate(article_orm.__dict__)
```

## Best Practices

### 1. Domain Purity

- Domain models should have NO infrastructure dependencies
- Business logic belongs in domain entities, not services
- Use dataclasses for domain models, not ORM classes

```python
# ✅ Good: Pure domain model
@dataclass
class User:
    username: str
    email: str
    
    def can_follow(self, other_user: 'User') -> bool:
        return self.id != other_user.id

# ❌ Bad: Domain model with infrastructure dependencies
class User(Base):  # SQLAlchemy dependency
    __tablename__ = 'users'
    # ...
```

### 2. Dependency Direction

Dependencies should flow inward toward the domain:

```python
# ✅ Good: Service depends on repository interface
class UserService:
    def __init__(self, user_repo: UserRepositoryInterface):
        self.user_repo = user_repo

# ❌ Bad: Domain depends on infrastructure
class User:
    def save(self):
        # Direct database access from domain
        session.add(self)
```

### 3. Exception Handling

- Domain and service layers raise domain exceptions
- API layer translates domain exceptions to HTTP responses

```python
# Domain exception
class ArticleNotFoundError(NotFoundError):
    def __init__(self, slug: str):
        super().__init__(f"Article '{slug}' not found")

# Service layer
@transactional()
async def get_article(uow: AsyncUnitOfWork, slug: str) -> ArticleRead:
    repo = ArticleRepository(uow.session)
    article = await repo.get_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(slug)  # Domain exception
    return ArticleRead.model_validate(article.__dict__)

# API layer
@router.get("/articles/{slug}")
async def get_article_endpoint(slug: str) -> ArticleResponse:
    try:
        article = await get_article(slug)
        return ArticleResponse(article=article)
    except ArticleNotFoundError:
        raise HTTPException(status_code=404, detail={"errors": {"body": ["Article not found"]}})
```

### 4. Transaction Management

Use the `@transactional()` decorator for service functions:

```python
@transactional()
async def follow_user(
    uow: AsyncUnitOfWork,
    follower_id: int, 
    followed_id: int
) -> None:
    """Follow a user - single transaction."""
    user_repo = UserRepository(uow.session)
    follower_repo = FollowerRepository(uow.session)
    
    # Multiple operations in single transaction
    follower = await user_repo.get_by_id(follower_id)
    followed = await user_repo.get_by_id(followed_id)
    
    if not follower or not followed:
        raise UserNotFoundError()
    
    await follower_repo.create_follow_relationship(follower_id, followed_id)
    # Transaction automatically committed
```

This architecture ensures clean separation of concerns, testability, and maintainability while following Domain-Driven Design principles.
