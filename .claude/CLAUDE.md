# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Essential Commands
```bash
# Start application with auto-reload
make run

# Run all tests
make test

# Format, lint, and type check
make lint

# Type checking only
make mypy

# Test with coverage
make test-coverage
```

### Database Management
```bash
# Setup development environment (starts both dev and test databases)
make setup-dev

# Apply migrations
make migrate

# Create new migration
make migration msg="Description of change"

# Database health checks
make db-check        # Check dev database
make db-check-test   # Check test database
make health-all      # Check all systems
```

### Test Commands
```bash
# Run specific test types
poetry run pytest tests/unit/         # Unit tests only
poetry run pytest tests/integration/  # Integration tests only
poetry run pytest tests/e2e/          # End-to-end tests only

# Test options
make test-failfast   # Stop on first failure
make test-verbose    # Verbose output
```

## Architecture Overview

This is a FastAPI RealWorld implementation using **Domain-Driven Design** with **Event-Driven Architecture**. The codebase follows strict separation of concerns across layers:

### Layer Structure
- **`app/api/`** - HTTP endpoints (FastAPI routers) - ONLY layer that can raise HTTPException
- **`app/service_layer/`** - Use cases and orchestration - raises custom exceptions only
- **`app/domain/`** - Business logic and entities (pure domain models)
- **`app/adapters/`** - Infrastructure (repositories, ORM, database)
- **`app/events/`** - Event-driven architecture components
- **`app/shared/`** - Common utilities and cross-cutting concerns

### Key Patterns

#### Automatic Transaction Management
Use the `@transactional()` decorator for service functions:
```python
from app.shared.transaction import transactional

@transactional()
async def create_article(uow: AsyncUnitOfWork, article_data: ArticleCreate, user: User) -> Article:
    # UoW is automatically injected as first parameter
    # Transaction automatically commits on success or rolls back on exception
```

#### Domain Events
Publish events from service layer using the shared event bus:
```python
from app.events.core import shared_event_bus
from app.events.domain.articles import ArticleCreated

# In service layer
shared_event_bus.publish(ArticleCreated(
    article_id=article.id,
    title=article.title,
    slug=article.slug
))
```

#### Repository Pattern
Repositories are in `app/adapters/repository/` and take a session parameter:
```python
repo = ArticleRepository(uow.session)
article = await repo.get_by_slug(slug)
```

#### Domain Models
Pure domain models in `app/domain/*/models.py` contain no infrastructure dependencies.
ORM mappings are in `app/domain/*/orm.py`.

## Strict Coding Standards

### File Organization (CRITICAL)
- **Domain Models**: Pure domain entities (dataclasses/classes) in `models.py` files ONLY
- **ORM Infrastructure**: SQLAlchemy mappings in `orm.py` files ONLY 
- **API Schemas**: Pydantic BaseModel in `schemas.py` files ONLY
- **NEVER MIX**: Domain models, ORM mappings, and API schemas must be in separate files
- **Conversion**: Always use `model_validate(obj)` to convert ORM → Pydantic (never `from_orm`)

### Layer Separation Rules
- **API Layer**: ONLY layer that can raise/handle `HTTPException`
- **Service Layer**: Raises custom exceptions only, never HTTPException
- **Domain Layer**: Pure business logic, no infrastructure dependencies
- **Repository Layer**: Data access, raises custom exceptions

### Required Standards
- **Type Annotations**: Required on ALL functions, methods, variables
- **MyPy Compliance**: All code must pass strict MyPy checking
- **Pydantic Settings**: Use for configuration - never access `os.environ` directly
- **Dependency Injection**: Required for repositories, services, UoW patterns

## Testing Requirements

### Critical Testing Rules
- **ALWAYS run tests after code changes**: `make test`
- **Fix test failures immediately** - do not leave broken tests
- **Use pytest-asyncio** for async tests
- **httpx.AsyncClient** with `ASGITransport` for API tests
- **Function-scoped DB cleanup** to avoid test contamination

### Test Structure
- **Unit tests**: `tests/unit/` - Mock infrastructure, test business logic
- **Integration tests**: `tests/integration/` - Real database, full request/response
- **E2E tests**: `tests/e2e/` - Complete workflow testing

### Test Data and Mocking
- **Use factories** from `tests/factories.py` for test data
- **Mock repositories/UoW**, not domain entities
- **pytest-mock**: Use `mocker` fixture, NOT `unittest.mock`

## Configuration

### Technology Stack
- **Poetry** for dependency management
- **Ruff** for formatting and linting (configured in pyproject.toml)
- **MyPy** for type checking (mypy.ini)
- **Pytest** with async support (pytest.ini)
- **Alembic** for database migrations
- **PostgreSQL** with async SQLAlchemy 2.0

### Environment Management
- Development: Uses `.env` file
- Testing: Uses `.env.test` file  
- Check environment: `make check-env`

## Common Pitfalls to Avoid

### Database Issues
- **Reset async engine** between tests (function scope)
- **Following relationships**: Use `UserRepository.is_following()` NOT `FollowerRepository`
- **Check for None** when dealing with model IDs from database

### API Compliance
- **RealWorld spec compliance**: All endpoints/models/errors must match [RealWorld API spec](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/) exactly
- **Use lifespan handlers**, NOT deprecated `@app.on_event`

### Migration Best Practices
- **Migration naming**: Follow `YYYYMMDD_add_table_name.py` pattern
- **Include both upgrade() and downgrade()** functions
- **Use CASCADE DELETE** for automatic cleanup