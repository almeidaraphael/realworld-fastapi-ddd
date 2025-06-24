# fastapi-realworld-demo

A production-grade FastAPI project implementing the RealWorld API spec using Domain-Driven Design (DDD) principles.

## Overview

- **Tech stack:** FastAPI, SQLModel, Pydantic, PostgreSQL, Alembic, asyncpg, Poetry
- **Architecture:** DDD, layered by domain (users, articles, profiles, etc.)
- **API Spec:** [RealWorld API Spec](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- **Testing:** pytest, pytest-asyncio, httpx, pydantic-factories
- **Config:** Pydantic Settings, `.env` files
- **Docker:** Used only for PostgreSQL (app runs locally)

## Project Structure
```
alembic/          # Database migrations
app/
  adapters/       # Infrastructure (ORM, repositories, UoW)
  api/            # FastAPI routers (per domain)
  config/         # App settings (Pydantic Settings)
  domain/         # Domain models, schemas, exceptions (per domain)
  events/         # Event-driven architecture (domain & system events)
    domain/       # Business domain events (articles, users, comments, tags)
    system/       # Cross-cutting events (analytics, security, moderation)
    infrastructure/ # Event bus implementations and testing utilities
  service_layer/  # Application services (per domain)
  shared/         # Shared utilities (JWT, pagination, etc.)
  main.py         # FastAPI app entrypoint
pyproject.toml    # Poetry dependency management
Dockerfile        # Docker build for app (not used in dev)
docker-compose.yml # Docker Compose for database only
tests/            # Unit, integration, and end-to-end tests
  unit/          # Unit tests (pure logic, no I/O)
  integration/   # Integration tests (DB, API, etc.)
  e2e/           # End-to-end tests (full stack)
```

## Quickstart

### 1. Start the Database and Run Migrations (Docker Compose)

```sh
make up-db
```

### 2. Start the FastAPI Application

```sh
make run
```

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

## Running Tests

- Tests require the test database to be running (see below).
- All tests run against a dedicated test database instance.
- Test data is generated using pydantic-factories for realism and coverage.

### Start the Test Database and Run Migrations

```sh
make up-db-test
```

### Run All Tests

```sh
make test
```

### Run Tests with Coverage

```sh
make test-cov
```

### Stop the Test Database

```sh
make down-db-test
```

### Test Types
- **Unit tests:** `tests/unit/` (pure logic, no DB)
- **Integration tests:** `tests/integration/` (DB, API, etc.)
- **End-to-end tests:** `tests/e2e/` (full stack, RealWorld flows)

## Commit Guidelines

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for consistent commit messages and automated changelog generation. All commit messages are validated by a Git hook.

### Quick Tools

- **Interactive commit helper**: `git better-commit` (guides you through creating proper commits)
- **Analyze recent commits**: `git analyze-commits [count]` (default: 10)
- **Full guidelines**: See [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Examples

```bash
# Feature with scope
feat(articles): add article deletion endpoint

# Bug fix
fix(auth): resolve JWT token expiration handling

# Documentation
docs: update API documentation with examples

# With body and footer
feat(users): implement user registration

Add user registration endpoint following RealWorld spec.
Includes email validation and password hashing.

Closes #42
```

### Types & Scopes

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`

**Scopes**: `users`, `articles`, `profiles`, `comments`, `auth`, `db`, `api`, `domain`, `service`, `infra`, `config`, `deps`

## Reference
- [RealWorld API Spec](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- See `.github/copilot-instructions.md` for contributor and code generation guidelines.

## Event-Driven Architecture

The project implements a comprehensive event-driven architecture for loose coupling and extensibility.

### Event System Overview

- **Event Bus**: Type-safe publish-subscribe system with sync/async support
- **Error Isolation**: Handler failures don't affect other handlers or main flow
- **Event Persistence**: Optional event logging for audit trails and debugging
- **Testing Support**: Specialized event bus for testing scenarios

### Event Organization

```
app/events/
├── core.py                    # Base classes (DomainEvent, EventBus)
├── domain/                    # Business domain events
│   ├── articles.py           # Article lifecycle events
│   ├── comments.py           # Comment-related events
│   ├── users.py              # User registration, login, profile events
│   └── tags.py               # Tag creation and usage events
├── system/                    # Cross-cutting system events
│   ├── analytics.py          # Performance and usage analytics
│   ├── security.py           # Authentication and security events
│   ├── moderation.py         # Content moderation events
│   └── maintenance.py        # System maintenance and cleanup
└── infrastructure/           # Event bus implementations
    ├── persistent_bus.py     # Event persistence for audit trails
    └── test_bus.py          # Testing utilities
```

### Usage Examples

#### Publishing Events
```python
from app.events import shared_event_bus, ArticleCreated, UserRegistered

# Publish domain events
shared_event_bus.publish(ArticleCreated(article_id=123, author_id=456))
shared_event_bus.publish(UserRegistered(
    user_id=789, 
    username="johndoe", 
    email="john@example.com"
))

# Async publishing
await shared_event_bus.publish_async(ArticleViewIncremented(
    article_id=123, 
    viewer_id=456
))
```

#### Creating Event Handlers
```python
from app.events import shared_event_bus, ArticleCreated

def handle_article_created(event: ArticleCreated) -> None:
    """Send notifications when articles are created."""
    # Notify followers, update search index, etc.
    logger.info(f"Article {event.article_id} created by {event.author_id}")

# Register handler
shared_event_bus.subscribe(ArticleCreated, handle_article_created)
```

#### Available Events

**Domain Events:**
- Articles: `ArticleCreated`, `ArticleUpdated`, `ArticleDeleted`, `ArticleFavorited`, `ArticleUnfavorited`
- Comments: `ArticleCommentAdded`, `CommentDeleted`
- Users: `UserRegistered`, `UserLoggedIn`, `UserProfileUpdated`, `UserFollowed`, `UserUnfollowed`
- Tags: `TagCreated`, `TagUsed`, `TagRemoved`, `PopularTagDetected`

**System Events:**
- Analytics: `ArticleViewIncremented`, `SearchPerformed`, `SlowQueryDetected`, `HighTrafficDetected`
- Security: `UserLoginAttempted`, `UserPasswordChanged`, `UserAccountLocked`, `SuspiciousLoginActivity`
- Moderation: `ContentFlagged`, `ContentApproved`, `ContentRemoved`, `SpamDetected`
- Maintenance: `UserDataCleanupRequested`, `OrphanedDataDetected`, `BulkOperationCompleted`

### Event Testing

```python
from tests.test_event_bus import MockEventBus
from app.events.domain import UserRegistered

def test_user_registration():
    test_bus = MockEventBus()
    
    # Your code that should publish events
    register_user(user_data)
    
    # Verify events were published
    assert test_bus.call_count == 1
    assert test_bus.assert_event_published(
        UserRegistered, 
        user_id=123, 
        email="test@example.com"
    )
```

## Architecture Principles

- **Domain-Driven Design**: Clear separation between domains (users, articles, etc.)
- **Event-Driven**: Loose coupling through domain events
- **Layered Architecture**: API → Service → Domain → Infrastructure
- **Type Safety**: Full type annotations and mypy validation
- **Testing**: Comprehensive test coverage with realistic test data