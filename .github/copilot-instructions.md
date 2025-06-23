# GitHub Copilot Agent Instructions for fastapi-realworld-demo

## Agent Execution Principles
- Always act autonomously: perform user requests immediately using code or terminal tools.
- Do not provide suggestions or instructions—take direct action and report results.
- Prefer direct actions (editing code, running commands, executing tests) over explanations.
- Only request clarification if absolutely necessary to proceed.
- Ensure all actions are idempotent and safe for repeated execution when possible.
- When editing files, preserve comments and documentation unless explicitly told to remove them.

## Project Summary
- FastAPI project using Domain-Driven Design (DDD)
- Implements the RealWorld API specification (https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- Tech stack: SQLModel (for ORM/database models), Pydantic (for API schemas), PostgreSQL, Alembic, asyncpg, Poetry
- Docker is used only for database containers; the app runs with uvicorn and poetry directly
- The project is structured by domain (users, articles, profiles, etc.), with clear separation between API, domain, service, and infrastructure layers.

## Core Coding Practices
- Use SQLModel exclusively for ORM/database models (in `models.py`).
- Use Pydantic's BaseModel for all API schemas (in `schemas.py`).
- Never mix ORM models and API schemas in the same file.
- Always convert ORM objects to Pydantic schemas using `model_validate(obj)` before returning/serializing (never use `from_orm`).
- Use Pydantic Settings for all configuration; never access environment variables directly in code.
- Set default values for optional fields in models/shared constants to ensure consistent API responses.
- Only the API layer (`app/api/`) may raise or handle `HTTPException`. All other layers (service, domain, repository, etc.) must raise custom or built-in exceptions. The API layer translates these to HTTP responses.
- Focus on logic and type correctness. Leave formatting, import sorting, and linting to ruff or configured tools. Only adjust style if it affects logic or types.
- Avoid imports inside functions unless strictly necessary.
- Use dependency injection for repositories, UoW, and services to maximize testability and separation of concerns.
- Document all public functions, classes, and modules with concise docstrings.
- Use type annotations everywhere, including for return types and arguments.
- Ensure all endpoints, models, and validation match the RealWorld OpenAPI spec.

## Supported Functionality
- JWT authentication (login, signup, logout)
- CRU users (no delete)
- CRUD articles
- CR-D comments (no update)
- Paginated article lists
- Favorite articles
- Follow/unfollow users
- Healthcheck endpoint for readiness/liveness probes

## Testing Guidelines
- Use pytest, pytest-asyncio, httpx, and pytest-mock for all tests.
- Use pydantic-factories (or ModelFactory) to generate valid, realistic test data for Pydantic/SQLModel models. Do not use MagicMock for domain/data models.
- Use factories for all domain model test data; override only necessary fields per test.
- Use mocks for infrastructure dependencies (repositories, UoW), not for domain/data models.
- All tests must run against a dedicated test database instance.
- Document and maintain the test workflow in the README and codebase.
- Define all test fixtures in `tests/conftest.py`. Do not define fixtures in individual test modules. Import shared fixtures as needed.
- For FastAPI integration tests, use the `async_client` fixture (which uses `ASGITransport(app=...)`) with httpx.AsyncClient. Do not use the deprecated `app=app` shortcut.
- All test functions must include a docstring using the GIVEN/WHEN/THEN pattern to describe scenario, action, and expected outcome.
- Use function-scoped fixtures for DB/session cleanup and engine resets. Avoid autouse unless necessary.
- Ensure the async engine is reset between tests to avoid cross-test contamination and event loop errors.
- Use targeted debug prints (engine URL, session info, user lookup results) to quickly identify where data or context is lost between layers or requests.
- All test data must be realistic and match the expected state for each test, especially when using authentication overrides or patching service methods.

## Type Checking
- Use mypy with strict settings (see `mypy.ini`). Type-annotate all new code. Ignore `alembic/` and `tests/`.
- Use built-in collection types (PEP 585). Remove unused `type: ignore` comments.
- Run type checking as part of the CI pipeline and before merging PRs.

## Maintenance
- Update this file and the README whenever significant changes are made to the codebase, requirements, features, dependencies, or structure.
- If exception handling changes, ensure only the API layer raises/handles `HTTPException`. All other layers must use custom or built-in exceptions, with the API layer translating them to HTTP responses.
- Keep the test and CI workflow documentation up to date.
- Ensure all new features are covered by tests and type annotations.

## Reference & Compliance
- All endpoints, models, and validation must match the RealWorld OpenAPI spec and use the specified tech stack and practices.
- See https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/ for endpoint details.

## FastAPI Startup Events
- Do not use the deprecated `on_event` method in FastAPI. Use lifespan event handlers for startup/shutdown logic in all new and existing code.
- Ensure all startup/shutdown logic is idempotent and safe for repeated execution.

## Common Pitfalls & Debugging
- Ensure the async engine is created after environment variables are set. Reset the engine between tests to avoid cross-test contamination.
- Set DB isolation to READ COMMITTED. Ensure all sessions are committed and closed after each request.
- Only use the override_auth fixture for unit tests needing a fake user. Do not use it for e2e/integration tests that rely on real login.
- Reset the async engine singleton before each test (function scope) to avoid event loop errors with asyncpg/SQLAlchemy.
- Ensure test data matches the expected state for each test, especially when using authentication overrides or patching service methods.
- Use function-scoped fixtures for DB/session cleanup and engine resets. Avoid autouse unless necessary.
- Use targeted debug prints (engine URL, session info, user lookup results) to quickly identify where data or context is lost between layers or requests.
- Always check for deprecation warnings and update code to follow latest best practices.
- Validate that all endpoints, models, and error responses match the RealWorld spec and are covered by tests.

## File Structure for Models and Schemas
- Define all API/Pydantic schemas in `schemas.py` using Pydantic's BaseModel.
- Define all SQLModel ORM/database models in `models.py` using SQLModel.
- This applies to all domains (users, profiles, articles, etc.).
- Never mix API schemas and ORM models in the same file.
- Organize code by domain and layer for maximum clarity and maintainability.
- Keep infrastructure, domain, service, and API layers clearly separated.
