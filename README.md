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