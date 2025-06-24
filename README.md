# FastAPI RealWorld Demo

A production-grade FastAPI application implementing the [RealWorld API specification](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/) using Domain-Driven Design (DDD) principles.

This project serves as a comprehensive example of modern FastAPI development practices, including clean architecture, event-driven design, comprehensive testing, and standardized error handling.

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Development Setup](#development-setup)
- [Database Management](#database-management)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Event-Driven Architecture](#event-driven-architecture)
- [Exception Handling](#exception-handling)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 📖 Documentation Index

This project includes comprehensive documentation organized as follows:

### Core Documentation Files
- **[README.md](README.md)** (this file) - Complete project overview, setup guide, and central documentation hub
- **[EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md)** - Comprehensive guide to the exception handling system, architecture, and best practices  
- **[COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)** - Detailed Git commit message standards, conventions, and project-specific guidelines

### Quick Navigation by Topic
- [Project Setup & Installation](#development-setup) - Get started with development environment
- [Architecture & Design](#architecture) - Domain-driven design and project structure
- [API Documentation](#api-documentation) - Interactive API docs and endpoint reference
- [Database Management](#database-management) - Multi-environment database handling and migrations
- [Testing Strategy](#testing) - Comprehensive testing approach and examples
- [Event System](#event-driven-architecture) - Event-driven architecture design and usage
- [Error Handling](#exception-handling) - Quick overview (full guide: [EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md))
- [Development Workflow](#development-workflow) - Git workflow and commit standards (detailed: [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md))
- [Deployment](#deployment) - Production deployment guide
- [Contributing](#contributing) - How to contribute to the project

This documentation is designed to be navigable from README.md as the central hub, with specialized guides for complex topics like exception handling and commit standards.

### API & Deployment
- [API Documentation](#api-documentation) - Interactive docs and endpoint examples  
- [Deployment](#deployment) - Production deployment and scaling
- [Contributing](#contributing) - Contribution guidelines and standards

---

## Quick Start

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- Docker and Docker Compose (for PostgreSQL)
- Make (for using Makefile commands)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd fastapi-realworld-demo
poetry install
```

### 2. Environment Configuration

Copy the example environment files and configure them:

```bash
cp .env.example .env
cp .env.test.example .env.test

# Edit .env files with your database settings
```

### 3. Start Database and Run Migrations

```bash
# Start both development and test databases
make setup-dev

# Or just development
make up-db
```

### 4. Run the Application

```bash
# Start the FastAPI server with auto-reload
make run

# Or manually
poetry run uvicorn app.main:app --reload
```

### 5. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Spec**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/healthcheck

## Project Overview

### Tech Stack

- **Framework**: FastAPI 0.115+ with Pydantic v2
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Migrations**: Alembic
- **Authentication**: JWT tokens with passlib/bcrypt
- **Testing**: pytest with asyncio, httpx, pydantic-factories, and optimized database fixtures for sub-50ms cleanup
- **Configuration**: Pydantic Settings with environment-specific configs
- **Development**: Poetry, Docker Compose, Make, Ruff, Mypy

### Key Features

- ✅ **Complete RealWorld API**: All endpoints from the RealWorld specification
- ✅ **Domain-Driven Design**: Clean separation of concerns across layers
- ✅ **Event-Driven Architecture**: Decoupled components with domain events
- ✅ **Comprehensive Testing**: Unit, integration, and end-to-end tests
- ✅ **Type Safety**: Full type annotations with mypy validation
- ✅ **Exception Handling**: Standardized error handling across all domains
- ✅ **Database Management**: Multi-environment database setup with migrations
- ✅ **Production Ready**: Proper logging, configuration, and deployment setup

## Architecture

### Project Structure

```
fastapi-realworld-demo/
├── alembic/                    # Database migrations
│   ├── versions/              # Migration files
│   └── env.py                 # Alembic configuration
├── app/                       # Application source code
│   ├── adapters/              # Infrastructure layer
│   │   ├── orm/               # Database connection and session management
│   │   └── repository/        # Data access layer
│   ├── api/                   # HTTP API layer (FastAPI routers)
│   │   ├── articles.py        # Article endpoints
│   │   ├── profiles.py        # Profile endpoints
│   │   ├── tags.py            # Tag endpoints
│   │   └── users.py           # User endpoints
│   ├── config/                # Application configuration
│   │   └── settings.py        # Pydantic Settings classes
│   ├── domain/                # Domain layer (business logic)
│   │   ├── articles/          # Article domain
│   │   ├── comments/          # Comment domain
│   │   ├── profiles/          # Profile domain
│   │   ├── tags/              # Tag domain
│   │   └── users/             # User domain
│   │       ├── exceptions.py  # Domain-specific exceptions
│   │       ├── models.py      # SQLModel models
│   │       ├── orm.py         # ORM configurations
│   │       └── schemas.py     # Pydantic schemas
│   ├── events/                # Event-driven architecture
│   │   ├── core.py            # Event system core
│   │   ├── domain/            # Domain events
│   │   ├── handlers/          # Event handlers
│   │   └── infrastructure/    # Event bus implementations
│   ├── service_layer/         # Application services
│   │   ├── articles/          # Article services
│   │   ├── comments/          # Comment services
│   │   ├── profiles/          # Profile services
│   │   ├── tags/              # Tag services
│   │   └── users/             # User services
│   ├── shared/                # Shared utilities
│   │   ├── exceptions.py      # Exception handling system
│   │   ├── jwt.py             # JWT token handling
│   │   └── pagination.py     # Pagination utilities
│   └── main.py                # FastAPI application entry point
├── scripts/                   # Utility scripts
│   ├── db_manager.py          # Database management script
│   └── commit_helper.py       # Git commit helper
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end tests
│   ├── conftest.py            # Test configuration
│   └── factories.py           # Test data factories
├── .env                       # Development environment variables
├── .env.test                  # Test environment variables
├── docker-compose.yml         # PostgreSQL containers
├── pyproject.toml             # Poetry dependencies and configuration
├── Makefile                   # Development commands
└── README.md                  # This file
```

### Domain-Driven Design (DDD) Layers

The application follows DDD principles with clear separation of concerns:

#### 1. Domain Layer (`app/domain/`)
- **Purpose**: Contains business logic and domain rules
- **Components**: Models, schemas, exceptions, domain events
- **Rules**: 
  - No dependencies on infrastructure or external concerns
  - Pure business logic only
  - Defines domain-specific exceptions

#### 2. Application/Service Layer (`app/service_layer/`)
- **Purpose**: Orchestrates business operations and use cases
- **Components**: Service classes that coordinate domain operations
- **Rules**:
  - Coordinates between domain and infrastructure
  - Handles transactions and unit of work
  - Publishes domain events

#### 3. API Layer (`app/api/`)
- **Purpose**: HTTP interface and request/response handling
- **Components**: FastAPI routers and endpoint definitions
- **Rules**:
  - Handles HTTP concerns only
  - Translates domain exceptions to HTTP responses
  - Request/response validation

#### 4. Infrastructure Layer (`app/adapters/`)
- **Purpose**: External concerns (database, file system, etc.)
- **Components**: Repositories, ORM, unit of work
- **Rules**:
  - Implements interfaces defined by domain
  - Handles database connections and queries
  - No business logic

### Data Flow

```
HTTP Request → API Layer → Service Layer → Domain Layer
                   ↓           ↓              ↓
              HTTP Response ← Infrastructure ← Repository
```

1. **HTTP Request** arrives at API layer
2. **API layer** validates request and calls service
3. **Service layer** orchestrates business operations
4. **Domain layer** applies business rules
5. **Infrastructure** handles data persistence
6. **Response** flows back through layers

- API docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

## Database Management

The project uses an advanced database management system with automatic environment detection and validation.

### Environment Detection

The system automatically detects the environment and uses the appropriate database:

- **Development**: Uses `.env` → `rw-demo-db` (port 5432)
- **Testing**: Uses `.env.test` → `rw-demo-test-db` (port 5433) 
- **Production**: Uses `.env.prod` → `rw-demo-prod-db` (port 5432)

Environment detection works through:
1. `APP_ENV` environment variable
2. pytest detection (automatic in tests)
3. Fallback to development

### Database Commands

#### Quick Setup
```sh
# Start both dev and test databases
make setup-dev

# Check environment configuration
make check-env

# Check database health
make health-all
```

#### Development Database
```sh
# Start development database
make up-db

# Stop development database  
make down-db

# Check development database info
make db-info

# Check development database connection
make db-check
```

#### Test Database
```sh
# Start test database
make up-db-test

# Stop test database
make down-db-test

# Check test database info
make db-info-test

# Check test database connection
make db-check-test

# Reset test database (development/testing only)
make db-reset-test
```

#### Database Management Script
```sh
# Get database information
poetry run python scripts/db_manager.py info

# Check database connection
poetry run python scripts/db_manager.py check

# Reset database (with confirmation)
APP_ENV=testing poetry run python scripts/db_manager.py reset
```

### Migration Management
```sh
# Create new migration
make migration msg="Add new table"

# Apply migrations (auto-detects environment)
make migrate

# Apply migrations to test database specifically
make migrate-test
```

### Environment Variables

The system uses different `.env` files per environment:

- `.env` - Development configuration
- `.env.test` - Test configuration  
- `.env.prod` - Production configuration

#### Configuration Validation

The system includes built-in validation to prevent:
- Using test database in production
- Using production database in tests
- Mismatched environment configurations

## API Documentation

### Interactive API Docs

Once the application is running, you can access interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Endpoints

The application implements all endpoints from the [RealWorld API specification](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/):

#### Authentication Endpoints
- `POST /api/users/login` - Authenticate existing user
- `POST /api/users` - Register new user
- `GET /api/user` - Get current user
- `PUT /api/user` - Update user

#### Profile Endpoints  
- `GET /api/profiles/{username}` - Get profile
- `POST /api/profiles/{username}/follow` - Follow user
- `DELETE /api/profiles/{username}/follow` - Unfollow user

#### Article Endpoints
- `GET /api/articles` - List articles (with filtering)
- `GET /api/articles/feed` - Get user's article feed
- `POST /api/articles` - Create article  
- `GET /api/articles/{slug}` - Get article
- `PUT /api/articles/{slug}` - Update article
- `DELETE /api/articles/{slug}` - Delete article
- `POST /api/articles/{slug}/favorite` - Favorite article
- `DELETE /api/articles/{slug}/favorite` - Unfavorite article

#### Comment Endpoints
- `GET /api/articles/{slug}/comments` - Get comments for article
- `POST /api/articles/{slug}/comments` - Add comment to article
- `DELETE /api/articles/{slug}/comments/{id}` - Delete comment

#### Tag Endpoints
- `GET /api/tags` - Get all tags

#### Utility Endpoints
- `GET /healthcheck` - Application health check

### Authentication

The API uses JWT (JSON Web Token) based authentication:

```bash
# Login to get token
curl -X POST "http://localhost:8000/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "email": "user@example.com",
      "password": "password"
    }
  }'

# Use token in subsequent requests
curl -X GET "http://localhost:8000/api/user" \
  -H "Authorization: Token <your-jwt-token>"
```

### Request/Response Examples

#### Create User
```bash
# Request
POST /api/users
{
  "user": {
    "username": "johndoe",
    "email": "john@example.com", 
    "password": "password123"
  }
}

# Response
{
  "user": {
    "email": "john@example.com",
    "token": "jwt-token-here",
    "username": "johndoe",
    "bio": "",
    "image": ""
  }
}
```

#### Create Article
```bash
# Request  
POST /api/articles
Authorization: Token <jwt-token>
{
  "article": {
    "title": "How to build APIs",
    "description": "A comprehensive guide",
    "body": "Content of the article...",
    "tagList": ["programming", "api", "fastapi"]
  }
}

# Response
{
  "article": {
    "slug": "how-to-build-apis",
    "title": "How to build APIs",
    "description": "A comprehensive guide", 
    "body": "Content of the article...",
    "tagList": ["programming", "api", "fastapi"],
    "createdAt": "2024-01-01T00:00:00.000Z",
    "updatedAt": "2024-01-01T00:00:00.000Z",
    "favorited": false,
    "favoritesCount": 0,
    "author": {
      "username": "johndoe",
      "bio": "",
      "image": "",
      "following": false
    }
  }
}
```

## Reference
- [RealWorld API Spec](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- See `.github/copilot-instructions.md` for contributor and code generation guidelines.

## Event-Driven Architecture

The application implements a comprehensive event-driven architecture for loose coupling and extensibility. Events enable different parts of the system to react to business changes without tight coupling.

### Event System Overview

- **Type-Safe Events**: All events are strongly typed with Pydantic models
- **Sync/Async Support**: Events can be handled synchronously or asynchronously  
- **Error Isolation**: Handler failures don't affect other handlers or main application flow
- **Event Persistence**: Optional event logging for audit trails and debugging
- **Testing Support**: Specialized event bus for testing scenarios

### Event Categories

#### Domain Events (`app/events/domain/`)
Business events that represent important domain changes:

```python
# User domain events
UserRegistered(user_id=123, username="john", email="john@example.com")
UserLoggedIn(user_id=123, username="john", email="john@example.com")
UserProfileUpdated(user_id=123, field="bio", old_value="", new_value="New bio")

# Article domain events  
ArticleCreated(article_id=456, author_id=123, title="My Article", slug="my-article")
ArticleFavorited(article_id=456, user_id=789, favorites_count=15)
ArticleDeleted(article_id=456, author_id=123, slug="my-article")

# Comment domain events
ArticleCommentAdded(comment_id=789, article_id=456, author_id=123, body="Great article!")
CommentDeleted(comment_id=789, article_id=456, author_id=123)
```

#### System Events (`app/events/system/`)
Cross-cutting concerns and system-level events:

```python
# Analytics events
ArticleViewIncremented(article_id=456, viewer_id=789, timestamp=datetime.now())
SearchPerformed(query="fastapi", user_id=123, results_count=42)
SlowQueryDetected(query="SELECT ...", duration=5.2, threshold=3.0)

# Security events  
UserLoginAttempted(email="user@example.com", success=True, ip_address="192.168.1.1")
SuspiciousLoginActivity(user_id=123, reason="Multiple failed attempts")
UserPasswordChanged(user_id=123, changed_by="user", timestamp=datetime.now())

# Moderation events
ContentFlagged(content_type="article", content_id=456, reason="spam", reporter_id=789)
SpamDetected(content_type="comment", content_id=123, confidence=0.95)
```

### Using Events

#### Publishing Events

```python
from app.events import shared_event_bus
from app.events.domain import UserRegistered, ArticleCreated

# Publish events in service layer
async def create_user(user_data: UserCreateData) -> User:
    user = User(**user_data)
    await repo.save(user)
    
    # Publish domain event
    shared_event_bus.publish(UserRegistered(
        user_id=user.id,
        username=user.username,
        email=user.email
    ))
    
    return user

# Async publishing
await shared_event_bus.publish_async(ArticleCreated(
    article_id=article.id,
    author_id=article.author_id,
    title=article.title,
    slug=article.slug
))
```

#### Creating Event Handlers

```python
from app.events import shared_event_bus
from app.events.domain import UserRegistered, ArticleCreated

# Simple event handler
def send_welcome_email(event: UserRegistered) -> None:
    """Send welcome email to new users."""
    email_service.send_welcome_email(
        email=event.email,
        username=event.username
    )

# Async event handler
async def update_search_index(event: ArticleCreated) -> None:
    """Update search index when articles are created."""
    await search_service.index_article(
        article_id=event.article_id,
        title=event.title,
        slug=event.slug
    )

# Register handlers
shared_event_bus.subscribe(UserRegistered, send_welcome_email)
shared_event_bus.subscribe_async(ArticleCreated, update_search_index)
```

#### Advanced Event Patterns

```python
# Multiple handlers for same event
shared_event_bus.subscribe(UserRegistered, send_welcome_email)
shared_event_bus.subscribe(UserRegistered, create_user_profile)
shared_event_bus.subscribe(UserRegistered, track_user_registration)

# Conditional event handling
def handle_article_created(event: ArticleCreated) -> None:
    if event.article_id % 100 == 0:  # Every 100th article
        notify_admin_milestone(event.article_id)

# Handler with error handling
def robust_handler(event: UserRegistered) -> None:
    try:
        external_service.notify_user_created(event.user_id)
    except Exception as exc:
        logger.error(f"Failed to notify external service: {exc}")
        # Event system continues with other handlers
```

### Event Testing

```python
from tests.test_event_bus import MockEventBus
from app.events.domain import UserRegistered

def test_user_registration_publishes_event():
    """Test that user registration publishes the correct event."""
    mock_bus = MockEventBus()
    
    # Replace the real event bus with mock
    with mock.patch('app.service_layer.users.shared_event_bus', mock_bus):
        user = await create_user(user_data)
    
    # Verify event was published
    assert mock_bus.call_count == 1
    assert mock_bus.assert_event_published(
        UserRegistered,
        user_id=user.id,
        username=user.username,
        email=user.email
    )
```

### Event Configuration

Events are automatically registered at application startup:

```python
# app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    register_all_event_handlers()  # Auto-discovers and registers handlers
    yield
    # Shutdown
    await cleanup_event_system()
```

### Benefits of Event-Driven Architecture

1. **Loose Coupling**: Components don't need direct references to each other
2. **Extensibility**: Easy to add new features without modifying existing code
3. **Scalability**: Events can be processed asynchronously for better performance
4. **Audit Trail**: All domain changes are automatically tracked
5. **Testing**: Easy to test components in isolation
6. **Observability**: Built-in tracking of system behavior and performance

## Architecture Principles

- **Domain-Driven Design**: Clear separation between domains (users, articles, etc.)
- **Event-Driven**: Loose coupling through domain events
- **Layered Architecture**: API → Service → Domain → Infrastructure
- **Type Safety**: Full type annotations and mypy validation
- **Testing**: Comprehensive test coverage with realistic test data
- **Documentation**: Code that documents itself and comprehensive guides
- **Performance**: Efficient database queries and async operations
- **Maintainability**: Code that is easy to understand and modify

## Development Setup

### Prerequisites

1. **Python 3.12+**: Required for modern type hints and async features
2. **Poetry**: For dependency management and virtual environments
3. **Docker & Docker Compose**: For PostgreSQL databases
4. **Make**: For convenient development commands

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd fastapi-realworld-demo

# Install dependencies with Poetry
poetry install

# Install pre-commit hooks (optional but recommended)
poetry run pre-commit install
```

### Environment Configuration

The application uses environment-specific configuration files:

```bash
# Development environment
cp .env.example .env

# Test environment  
cp .env.test.example .env.test

# Production environment (if needed)
cp .env.prod.example .env.prod
```

#### Environment Variables

Key configuration options:

```bash
# .env (Development)
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rw-demo-db
SECRET_KEY=your-secret-key-here
DEBUG=true

# .env.test (Testing)
APP_ENV=testing
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/rw-demo-test-db
SECRET_KEY=test-secret-key
DEBUG=true
```

### Development Commands

The project includes a comprehensive Makefile for common development tasks:

```bash
# Setup and start everything
make setup-dev              # Start both dev and test databases

# Database management
make up-db                   # Start development database
make up-db-test             # Start test database
make down-db                # Stop development database
make migrate                # Run database migrations
make migration msg="..."    # Create new migration

# Application
make run                    # Start FastAPI server with auto-reload
make test                   # Run all tests
make test-cov              # Run tests with coverage
make lint                  # Run code linting
make format                # Format code with ruff

# Database utilities
make db-info               # Show database connection info
make db-check              # Test database connection
make health-all            # Check all systems
```

## Testing

### Overview

The project includes comprehensive testing with three levels:

- **Unit Tests** (`tests/unit/`): Pure business logic, no I/O operations
- **Integration Tests** (`tests/integration/`): Database and API integration
- **End-to-End Tests** (`tests/e2e/`): Complete user workflows

All tests run against a dedicated test database to ensure isolation and consistency.

### Running Tests

#### Prerequisites

Start the test database:

```bash
make up-db-test
```

#### Test Commands

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test types
poetry run pytest tests/unit/              # Unit tests only
poetry run pytest tests/integration/       # Integration tests only
poetry run pytest tests/e2e/              # E2E tests only

# Run specific test file
poetry run pytest tests/unit/test_users.py

# Run with verbose output
poetry run pytest -v

# Run and stop on first failure
poetry run pytest -x
```

### Test Configuration

Tests use realistic test data generated with pydantic-factories and an improved fixture system for efficient database management:

```python
# tests/factories.py
import factory
from factory import Factory
from app.domain.users.models import User

class UserFactory(Factory):
    class Meta:
        model = User
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    bio = factory.Faker('text', max_nb_chars=200)
    image = factory.Faker('image_url')
```

### Test Database Management & Improved Fixtures

The project features an enhanced test fixture system that provides efficient database operations and automatic isolation:

#### Automatic Database Isolation

Every test runs with automatic database cleanup using an efficient TRUNCATE CASCADE approach:

```python
# Automatic isolation - no setup needed
@pytest.mark.asyncio
async def test_user_creation():
    # Database starts clean automatically
    # Test runs with fresh state
    # Database cleaned automatically after test
```

#### Fast Database Operations

Optimized database utilities provide sub-50ms cleanup times:

```python
# tests/db_utils.py - Available utilities
from tests.db_utils import DatabaseTestUtils

# Fast table cleanup (uses TRUNCATE CASCADE)
await DatabaseTestUtils.truncate_all_tables()

# Verify database state
is_empty = await DatabaseTestUtils.verify_empty_database()
counts = await DatabaseTestUtils.get_table_counts()

# Selective cleanup for specific tests
await DatabaseTestUtils.selective_delete(['article', 'comment'])
```

#### Transaction Rollback Sessions

For maximum isolation, use transaction rollback sessions that automatically roll back all changes:

```python
# Automatic rollback - changes never persist
async def test_with_transaction_rollback(db_session):
    # All database operations within this session
    # are automatically rolled back after the test
    user = await create_user_in_db(db_session, user_data)
    # Changes rolled back automatically
```

#### Multiple Database Session Types

Choose the right session type for your test needs:

```python
# Standard session (with automatic cleanup)
async def test_standard(async_session):
    # Normal database operations
    pass

# Transaction rollback session (maximum isolation)  
async def test_isolated(db_session):
    # All changes automatically rolled back
    pass

# Manual database control
async def test_manual(db_cleanup_strategy):
    strategy = db_cleanup_strategy["selective"]
    await strategy(["user", "article"])
```

The test database is completely separate from development:

```bash
# Start test database
make up-db-test

# Check test database connection  
make db-check-test

# Reset test database (clears all data)
make db-reset-test

# Stop test database
make down-db-test
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/test_users_service.py
import pytest
from app.service_layer.users.services import create_user
from app.domain.users.exceptions import UserAlreadyExistsError

@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises_error():
    """
    GIVEN a user already exists with an email
    WHEN attempting to create another user with the same email  
    THEN UserAlreadyExistsError should be raised
    """
    # Test implementation...
```

#### Integration Test Example

```python
# tests/integration/test_users_api.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_returns_token(async_client: AsyncClient):
    """
    GIVEN valid user registration data
    WHEN posting to /api/users
    THEN should return 201 with user data and JWT token
    """
    response = await async_client.post("/api/users", json={
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "token" in data["user"]
```

#### End-to-End Test Example

```python
# tests/e2e/test_article_workflow.py
@pytest.mark.asyncio 
async def test_complete_article_workflow(async_client: AsyncClient):
    """
    GIVEN a registered user
    WHEN they create, update, and delete an article
    THEN all operations should work correctly
    """
    # Register user
    # Login user  
    # Create article
    # Update article
    # Delete article
    # Verify all steps
```

### Test Utilities

Common test helpers are available in `tests/helpers.py`:

```python
from tests.helpers import register_user, login_user

# Helper functions for common operations
async def register_user(client, username, email, password):
    # Implementation...

async def login_user(client, email, password):
    # Implementation...
```

### Continuous Integration

Tests run automatically in CI/CD pipelines with:

- Multiple Python versions
- Database migrations
- Code coverage reporting
- Type checking with mypy
- Linting with ruff

### Test Performance

The improved fixture system provides significant performance benefits:

```bash
# Run tests with timing to see performance improvements
poetry run pytest --durations=10

# Monitor database cleanup performance (typically <50ms)
poetry run pytest tests/test_improved_fixtures.py::test_database_cleanup_performance -v

# Run tests in parallel (if pytest-xdist installed)
poetry run pytest -n auto
```

#### Performance Optimizations

- **TRUNCATE CASCADE**: Up to 10x faster than DELETE operations
- **Connection pooling**: Reused database connections across tests
- **Automatic isolation**: No manual setup/teardown needed
- **Fallback strategies**: Graceful degradation for edge cases
- **Transaction rollback**: Zero I/O for maximum isolation tests

#### Benchmark Results

Typical performance metrics:
- Database cleanup: <50ms (TRUNCATE CASCADE)
- Test isolation setup: <10ms  
- Transaction rollback: ~1ms (in-memory only)
- Engine reset: <5ms

## Exception Handling

The application implements a comprehensive, standardized exception handling system that ensures consistent error responses across all API endpoints while maintaining clean separation of concerns.

### Quick Overview

- **Domain-Specific Exceptions**: Each domain defines its own exception types that inherit from base classes
- **Automatic HTTP Translation**: Domain exceptions automatically map to correct HTTP status codes (404, 401, 409, etc.)
- **Consistent Error Format**: All error responses follow the same structure with optional error codes
- **Type Safety**: Compile-time validation of exception handling patterns
- **Layer Separation**: Domain/service layers only raise domain exceptions, API layer handles HTTP translation

### Basic Pattern

```python
# 1. Domain exceptions inherit from base classes
class UserNotFoundError(NotFoundError):
    """Raised when a user cannot be found."""

# 2. Service layer raises domain exceptions  
async def get_user(user_id: int) -> User:
    user = await repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError(f"User with ID {user_id} not found")
    return user

# 3. API layer translates to HTTP responses
@router.get("/users/{user_id}")
async def get_user_endpoint(user_id: int):
    try:
        user = await get_user(user_id)
        return UserResponse(user=user)
    except UserNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
```

**Result**: Automatic 404 HTTP response with consistent error format.

### Exception Hierarchy

```
DomainError (Base - 500)
├── NotFoundError (404) → UserNotFoundError, ArticleNotFoundError
├── PermissionError (403) → ArticlePermissionError, CommentPermissionError  
├── ConflictError (409) → UserAlreadyExistsError, ArticleSlugConflictError
├── ValidationError (400) → InvalidEmailError, CannotFollowYourselfError
└── AuthenticationError (401) → InvalidCredentialsError, InvalidTokenError
```

### Key Benefits

1. **Consistency**: All endpoints return errors in the same format
2. **Maintainability**: Centralized status code mapping, no duplication
3. **Type Safety**: Compile-time validation prevents missed exception handling
4. **Testability**: Domain logic can be tested independently of HTTP concerns
5. **Developer Experience**: Clear error messages with actionable guidance

### 📚 Complete Guide

For comprehensive documentation including implementation patterns, best practices, testing strategies, and troubleshooting, see **[EXCEPTION_HANDLING.md](EXCEPTION_HANDLING.md)**.

Topics covered in the complete guide:
- **Implementation Guide**: Step-by-step setup for each layer
- **Advanced Patterns**: Custom error codes, conditional handling, infrastructure wrapping
- **Best Practices**: Domain design, service patterns, API layer guidelines
- **Testing Strategies**: Unit testing, integration testing, mock patterns
- **Migration Guide**: Converting existing HTTPException patterns
- **Troubleshooting**: Common issues and debugging techniques

## Development Workflow

### Git Workflow

The project uses [Conventional Commits](https://www.conventionalcommits.org/) for consistent commit messages and automated changelog generation.

#### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Quick Reference Examples

```bash
# Feature commits
feat(articles): add article deletion endpoint
feat(auth): implement JWT token refresh

# Bug fixes
fix(users): resolve password hashing issue
fix(db): correct migration rollback script

# Documentation
docs(api): update endpoint documentation
docs: add development setup guide

# Refactoring
refactor(services): extract common validation logic
perf(queries): optimize article listing query

# Tests
test(users): add integration tests for login flow
test: improve test coverage for article service
```

- **Full guidelines**: See [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)
- **Available scopes**: `users`, `articles`, `profiles`, `comments`, `auth`, `db`, `api`, `domain`, `service`, `infra`, `config`, `deps`
- **Required format**: `<type>(<scope>): <subject>` followed by optional body and footer

#### Git Hooks and Tools

```bash
# Install pre-commit hooks
poetry run pre-commit install

# Interactive commit helper
git better-commit

# Analyze recent commits
git analyze-commits 10

# Manual commit validation
poetry run python scripts/commit_helper.py validate "feat(api): add new endpoint"
```

### Code Quality Standards

#### Type Checking

```bash
# Run mypy type checking
poetry run mypy app/

# Type checking is required for all new code
# Configure in mypy.ini
```

#### Code Formatting and Linting

```bash
# Format code with ruff
make format

# Run linting
make lint

# Auto-fix linting issues
poetry run ruff check . --fix
```

#### Testing Requirements

- All new features must include tests
- Aim for >90% code coverage  
- Tests must pass before merging
- Follow the GIVEN/WHEN/THEN pattern for test docstrings
- Use the optimized fixture system for database tests:
  - Tests automatically get clean database state (no setup needed)
  - Use `db_session` for transaction rollback isolation
  - Use `async_session` for standard database operations
  - Leverage `DatabaseTestUtils` for manual database operations
- Database cleanup typically completes in <50ms using TRUNCATE CASCADE

### Feature Development Process

#### 1. Create Feature Branch

```bash
git checkout -b feat/article-search
```

#### 2. Implement Domain Logic

Start with domain layer (models, exceptions, schemas):

```python
# app/domain/articles/models.py - Add search fields
# app/domain/articles/exceptions.py - Add search exceptions  
# app/domain/articles/schemas.py - Add search request/response schemas
```

#### 3. Add Service Layer

```python
# app/service_layer/articles/services.py
async def search_articles(query: str, filters: SearchFilters) -> List[Article]:
    # Implementation with domain exceptions
```

#### 4. Implement API Layer

```python
# app/api/articles.py
@router.get("/articles/search")
async def search_articles_endpoint(query: str) -> ArticleListResponse:
    try:
        articles = await search_articles(query)
        return ArticleListResponse(articles=articles)
    except SearchError as exc:
        raise translate_domain_error_to_http(exc) from exc
```

#### 5. Add Tests

```python
# tests/unit/test_article_search.py - Domain logic tests
# tests/integration/test_article_search_api.py - API integration tests
# tests/e2e/test_article_search_flow.py - End-to-end workflow tests
```

#### 6. Update Documentation

```python
# Update API documentation
# Add/update docstrings
# Update README if needed
```

### Database Changes

#### Creating Migrations

```bash
# Create new migration
make migration msg="Add article search index"

# Review generated migration
cat alembic/versions/YYYYMMDD_add_article_search_index.py

# Test migration
make migrate
```

#### Migration Best Practices

1. **Always include both upgrade() and downgrade()**
2. **Test migrations on copy of production data**  
3. **Use descriptive migration messages**
4. **Consider index creation for large tables**
5. **Review migration before committing**

### Performance Monitoring

#### Database Performance

```bash
# Monitor slow queries in logs
tail -f logs/app.log | grep "SlowQueryDetected"

# Check database connection pool
make db-info
```

#### Application Performance

```python
# Use built-in event monitoring
@monitor_performance
async def my_endpoint():
    # Implementation...

# Check metrics in logs
```

### Release Process

#### 1. Prepare Release

```bash
# Ensure all tests pass
make test

# Ensure code quality
make lint
make typecheck

# Update version
poetry version patch  # or minor/major
```

#### 2. Create Release

```bash
# Create release branch
git checkout -b release/v1.2.0

# Update CHANGELOG.md
# Commit changes
git commit -m "chore: prepare release v1.2.0"

# Create tag
git tag v1.2.0
```

#### 3. Deploy

```bash
# Deploy to staging
make deploy-staging

# Run smoke tests
make test-staging

# Deploy to production
make deploy-production
```

## Deployment

### Environment Preparation

#### Production Environment Variables

```bash
# .env.prod
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/rw-demo-prod-db
SECRET_KEY=production-secret-key
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_HOSTS=api.example.com,www.example.com
```

#### Database Setup

```bash
# Run migrations in production
APP_ENV=production poetry run alembic upgrade head

# Verify database schema
APP_ENV=production make db-check
```

### Docker Deployment

#### Build Production Image

```bash
# Build Docker image
docker build -t fastapi-realworld-demo:latest .

# Test locally
docker run -p 8000:8000 fastapi-realworld-demo:latest
```

#### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: fastapi-realworld-demo:latest
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
    depends_on:
      - db
      
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: rw-demo-prod-db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Health Checks and Monitoring

#### Application Health Check

```bash
# Built-in health check endpoint
curl http://localhost:8000/healthcheck

# Response
{"status": "ok"}
```

#### Database Health Check

```bash
# Check database connectivity
make db-check

# Monitor database performance
make db-info
```

#### Application Metrics

The application publishes metrics via events:

```python
# Performance monitoring
SlowQueryDetected(query="SELECT ...", duration=5.2)
HighTrafficDetected(endpoint="/api/articles", requests_per_minute=1000)

# Error monitoring  
UserLoginAttempted(email="user@example.com", success=False)
ContentFlagged(content_type="article", content_id=456, reason="spam")
```

### Scaling Considerations

1. **Database Connection Pooling**: Configured via SQLAlchemy settings
2. **Async Request Handling**: Built-in with FastAPI and asyncio
3. **Event Processing**: Can be moved to background workers if needed
4. **Static Asset Serving**: Use CDN for production
5. **Database Read Replicas**: Can be configured for read-heavy workloads

## Contributing

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see Development Setup)
4. **Create a feature branch** from main
5. **Make your changes** following the development workflow
6. **Submit a pull request** with a clear description

### Contribution Guidelines

#### Code Standards

- Follow existing code style and patterns
- Add type annotations for all new code
- Include comprehensive tests for new features
- Update documentation as needed
- Use conventional commit messages

#### Pull Request Process

1. **Ensure tests pass**: `make test`
2. **Check code quality**: `make lint` and `make typecheck`
3. **Update documentation**: If adding new features
4. **Provide clear description**: What changes were made and why
5. **Reference issues**: Link to relevant GitHub issues

#### Review Criteria

Pull requests are reviewed for:

- **Functionality**: Does it work as intended?
- **Code Quality**: Is it readable, maintainable, and well-structured?
- **Testing**: Are there adequate tests with good coverage?
- **Documentation**: Is the code and any new features documented?
- **Architecture**: Does it follow the established patterns?

### Areas for Contribution

#### High Priority

- **Performance Optimizations**: Database queries, caching strategies
- **Additional RealWorld Features**: Missing endpoints or functionality
- **Enhanced Error Handling**: More specific error types and messages
- **Monitoring & Observability**: Metrics, tracing, structured logging

#### Medium Priority

- **Background Job Processing**: Queue system for long-running tasks
- **Caching Layer**: Redis integration for improved performance
- **Rate Limiting**: API rate limiting and throttling
- **File Upload Support**: User avatars and article images

#### Documentation Improvements

- **API Usage Examples**: More comprehensive API documentation
- **Architecture Guides**: Deep-dive into specific architectural decisions
- **Deployment Guides**: Platform-specific deployment instructions
- **Performance Tuning**: Guidelines for production optimization

### Development Philosophy

This project values:

1. **Clean Architecture**: Clear separation of concerns across layers
2. **Type Safety**: Comprehensive type annotations and validation
3. **Testing**: High test coverage with realistic test scenarios
4. **Documentation**: Code that documents itself and comprehensive guides
5. **Performance**: Efficient database queries and async operations
6. **Maintainability**: Code that is easy to understand and modify

### Questions and Support

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussions
- **Code Review**: All contributions receive thorough review and feedback

---

## Resources and References

- **RealWorld Specification**: https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Domain-Driven Design**: https://martinfowler.com/bliki/DomainDrivenDesign.html
- **Conventional Commits**: https://www.conventionalcommits.org/

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.