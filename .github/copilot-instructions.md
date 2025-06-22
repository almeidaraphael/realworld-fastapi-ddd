# Copilot Instructions for fastapi-realworld-demo

## Agent Behavior
- Always act as an autonomous agent: when a user requests an action, immediately perform it using the terminal or code tools whenever possible.
- Do not output instructions or suggestions to the user—just take the required actions and report results.
- Prefer direct action (e.g., running commands, editing files, running tests) over explanations or manual guidance.
- Only ask for clarification if absolutely necessary to proceed.

## Project Overview
- FastAPI project following Domain-Driven Design (DDD)
- Implements RealWorld API spec
- Uses SQLModel (ORM + API schemas), PostgreSQL, Alembic, asyncpg, and Poetry
- Docker is used only for database instances. The application runs with uvicorn and poetry directly.

## Key Practices
- Use SQLModel for both ORM and API schemas. Always convert ORM objects to schemas with `model_validate(obj)` before returning/serializing (never use deprecated `from_orm`).
- Use Pydantic Settings for all configuration. Never use direct environment variable access in application code. Always rely on Pydantic Settings for environment/config management.
- Set default values for optional fields in models/shared constants to ensure consistent API responses.
- Only the API layer (e.g., `app/api/`) should raise or handle `HTTPException`. All other layers (service, domain, repository, etc.) must raise custom or built-in exceptions. The API layer is responsible for translating these exceptions into HTTP responses.
- When making code changes, focus on code logic and type correctness. Leave import sorting, formatting, and linting to ruff or the project's configured tools. Do not manually reformat imports or code style unless it affects logic or type correctness.

## Functionality
- JWT authentication (login/signup/logout)
- CRU users (no delete)
- CRUD articles
- CR-D comments (no update)
- Paginated article lists
- Favorite articles
- Follow/unfollow users

## Testing Best Practices
- Use pytest, pytest-asyncio, httpx, and pytest-mock for all tests.
- Use pydantic-factories (or ModelFactory) to generate valid and realistic test data for Pydantic/SQLModel models. Avoid using MagicMock for domain/data models.
- Use factories for all domain model test data. Override only the fields needed for each test case.
- Use mocks for infrastructure dependencies (e.g., repositories, UoW), not for domain/data models.
- All tests should run against a dedicated test database instance.
- Document and maintain the test workflow in README and codebase.
- All test fixtures must be defined in `tests/conftest.py`.
Do not define fixtures in individual test modules. This ensures DRY, reusable, and discoverable test setup across the codebase.
Example: Place all patch_uow, patch_repo, user_factory, and other shared fixtures in conftest.py and import them in your tests.
- When using httpx.AsyncClient in tests, do not use the deprecated `app=app` shortcut. Instead, use the `async_client` fixture (which uses `ASGITransport(app=...)` under the hood) for all FastAPI integration tests. This avoids deprecation warnings and follows best practices for httpx and FastAPI.
- All test functions must include a docstring using the GIVEN/WHEN/THEN pattern to clearly describe the scenario, action, and expected outcome.

## Type Checking
- Use mypy with strict settings (see `mypy.ini`). Type-annotate all new code. Ignore `alembic/` and `tests/`.
- Use built-in collection types (PEP 585). Remove unused `type: ignore` comments.

## Maintenance
- Whenever significant changes are made to the codebase, always update this file and the README to reflect new requirements, features, dependencies, or project structure.
- If you add or change exception handling, ensure that only the API layer raises or handles `HTTPException`. All other layers must use custom or built-in exceptions, and the API layer must translate them to HTTP responses.

## Reference
- All endpoints, models, and validation must match the RealWorld OpenAPI spec and use the above tech stack and practices.

## FastAPI Startup Events
- The `on_event` method in the `FastAPI` class is deprecated. Use lifespan event handlers instead for startup/shutdown logic. Update all new and existing code to follow this best practice.

## Common Pitfalls & Debugging

- **Engine Singleton & Environment:** Always ensure the async engine is created after environment variables (e.g., TEST_MODE) are set. Reset the engine between tests to avoid cross-test contamination.
- **Session/Transaction Isolation:** Set DB isolation to READ COMMITTED. Ensure all sessions are committed and closed after each request.
- **Authentication in Tests:** Only use the override_auth fixture for unit tests that require a fake user. Do not use it for e2e/integration tests that rely on real login.
- **Async Engine & Event Loop:** Reset the engine singleton before each test (function scope) to avoid event loop errors with asyncpg/SQLAlchemy.
- **Test Data Consistency:** Ensure test data matches the expected state for each test, especially when using authentication overrides or patching service methods.
- **Fixture Scope:** Use function-scoped fixtures for DB/session cleanup and engine resets. Avoid autouse unless necessary.
- **Debugging:** Use targeted debug prints (engine URL, session info, user lookup results) to quickly identify where data or context is lost between layers or requests.
