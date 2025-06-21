# fastapi-realworld-demo

A FastAPI project following Domain-Driven Design (DDD) principles, implementing the RealWorld API spec.

## Project Structure
```
alembic/          # Database migrations
app/
  adapters/       # Infrastructure (ORM, repositories)
  api/            # FastAPI routers (per subdomain)
  config/         # App settings
  domain/         # Domain models, schemas, commands, events (per subdomain)
  service_layer/  # Application services (per subdomain)
  shared/         # Shared utilities (JWT, pagination, etc.)  
  main.py         # FastAPI app entrypoint
pyproject.toml    # Poetry dependency management
Dockerfile        # Docker build for app
docker-compose.yml # Docker Compose for database
tests/            # Unit, integration, and end-to-end tests
  unit/          # Unit tests
  integration/   # Integration tests
  e2e/           # End-to-end tests
```

## Running the Project

- The application runs directly with Poetry and Uvicorn (not in Docker).
- Docker is used **only for the PostgreSQL database**.
- All common commands are available via the `Makefile`.

### 1. Start the Database (Docker Compose)

```sh
make up-db
```

### 2. Run Database Migrations

```sh
make migrate
```

### 3. Start the FastAPI Application

```sh
make run
```

The API will be available at http://localhost:8000

## Running Tests

- Tests require the database to be running (see above).
- All configuration is managed via Pydantic Settings and `.env` files.
- Tests always run against a dedicated test database instance.

### Start the Test Database

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
- **Unit tests:** `tests/unit/`
- **Integration tests:** `tests/integration/`
- **End-to-end tests:** `tests/e2e/`

---

See `.github/copilot-instructions.md` for contributor and code generation guidelines.