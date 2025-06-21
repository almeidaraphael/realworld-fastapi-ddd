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