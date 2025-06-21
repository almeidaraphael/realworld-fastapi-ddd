# Copilot Instructions for fastapi-realworld-demo

## Project Overview
- FastAPI project following Domain-Driven Design (DDD)
- Implements RealWorld API spec
- Uses SQLModel (ORM + API schemas), PostgreSQL, Alembic, asyncpg, Docker, and Poetry

## Key Practices
- Use SQLModel for both ORM and API schemas. Always convert ORM objects to schemas with `model_validate(obj)` before returning/serializing (never use deprecated `from_orm`).
- Use Pydantic Settings for all configuration. **Never use `os.environ.get` or direct environment variable access in application code.** Always rely on Pydantic Settings for environment/config management.
- All config is loaded from `.env` (default/Docker) and/or `TEST_`-prefixed variables for test environments. `POSTGRES_HOST` is `db` in Docker, `localhost` locally.
- All code and tests must work both in Docker and locally, relying on Pydantic for env management.
- Set default values for optional fields (e.g., `bio`, `image`) in models/shared constants to ensure consistent API responses.
- **Only the API layer (e.g., `app/api/`) should raise or handle `HTTPException`. All other layers (service, domain, repository, etc.) must raise custom or built-in exceptions. The API layer is responsible for translating these exceptions into HTTP responses.**
- **When making code changes, focus on code logic and type correctness. Leave import sorting, formatting, and linting to ruff or the project's configured tools. Do not manually reformat imports or code style unless it affects logic or type correctness.**

## Functionality
- JWT authentication (login/signup/logout)
- CRU users (no delete)
- CRUD articles
- CR-D comments (no update)
- Paginated article lists
- Favorite articles
- Follow/unfollow users

## Testing
- Use pytest, pytest-asyncio, httpx
- Use pytest-mock's `mocker` fixture and `unittest.mock.AsyncMock` for mocking async dependencies in unit tests. Avoid hand-rolled dummy classes for mocks; prefer patching dependencies directly with `mocker` and `AsyncMock` for clarity and maintainability.
- Tests must run in both Docker (`POSTGRES_HOST=db`) and locally (`POSTGRES_HOST=localhost`)
- Document and maintain this workflow in README and codebase

## Type Checking
- Use mypy with strict settings (see `mypy.ini`). Type-annotate all new code. Ignore `alembic/` and `tests/`.
- Use built-in collection types (PEP 585). Remove unused `type: ignore` comments.

## Maintenance
- **Whenever significant changes are made to the codebase, always update this file and the README to reflect new requirements, features, dependencies, or project structure.**
- **If you add or change exception handling, ensure that only the API layer raises or handles `HTTPException`. All other layers must use custom or built-in exceptions, and the API layer must translate them to HTTP responses.**

## Reference
- All endpoints, models, and validation must match the RealWorld OpenAPI spec and use the above tech stack and practices.

## FastAPI Startup Events
- The `on_event` method in the `FastAPI` class is deprecated. Use lifespan event handlers instead for startup/shutdown logic. Update all new and existing code to follow this best practice.

