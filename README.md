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

## Reference
- [RealWorld API Spec](https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- See `.github/copilot-instructions.md` for contributor and code generation guidelines.