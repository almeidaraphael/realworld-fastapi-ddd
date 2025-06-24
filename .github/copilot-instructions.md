# GitHub Copilot Agent Instructions for fastapi-realworld-demo

## 🚨 CRITICAL EXECUTION PRINCIPLES (ALWAYS FOLLOW)

### Action-First Approach
- **ACT IMMEDIATELY**: Execute user requests using tools - never just provide suggestions
- **NO EXPLANATIONS WITHOUT ACTION**: If you can do something, do it first, then explain
- **USE TOOLS AGGRESSIVELY**: Prefer `run_in_terminal`, `read_file`, `replace_string_in_file` over text responses
- **REQUEST CLARIFICATION ONLY AS LAST RESORT**: Try multiple approaches before asking questions

### Testing Workflow (MANDATORY)
- **ALWAYS RUN TESTS AFTER CHANGES**: Execute `python -m pytest tests/ --tb=short -v > test_results.txt 2>&1`
- **ALWAYS READ TEST RESULTS**: Use `read_file` on test result files to verify fixes worked
- **SAVE ALL TEST OUTPUTS**: Use descriptive filenames like `test_fix_results.txt`, `test_final_results.txt`
- **FIX FAILURES IMMEDIATELY**: If tests fail, debug and fix them in the same interaction

### File Editing Rules
- **PRESERVE EXISTING CODE**: Keep comments, documentation, and structure unless explicitly told to remove
- **USE PROPER TOOLS**: Use `replace_string_in_file` or `insert_edit_into_file` - never show code blocks
- **INCLUDE CONTEXT**: When replacing strings, include 3-5 lines before/after for uniqueness
- **VERIFY CHANGES**: Check files after editing to ensure changes applied correctly

## 📋 PROJECT CONTEXT & TECH STACK

### Architecture Overview
- **Pattern**: Domain-Driven Design (DDD) with clean architecture layers
- **API Specification**: RealWorld API (https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/)
- **Framework**: FastAPI with async/await throughout
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Validation**: Pydantic for API schemas and data validation
- **Deployment**: Docker for database only; app runs with uvicorn + poetry

### Domain Structure
```
app/
├── api/           # HTTP endpoints and request/response handling (Interface/Presentation)
├── domain/        # Business entities, domain services, and domain logic
├── service_layer/ # Application services - orchestration and use cases
├── adapters/      # Infrastructure (ORM, repositories, external services)
└── shared/        # Common utilities and cross-cutting concerns
```

### Supported Features
- ✅ JWT authentication (login, signup, logout)
- ✅ User management (CRU operations - no delete)
- ✅ Article CRUD with slug-based URLs
- ✅ Comment system (CR-D operations - no update)
- ✅ Article favoriting and feed generation
- ✅ User following/follower relationships
- ✅ Tag system and filtering
- ✅ Pagination for article lists
- ✅ Health check endpoints

## 🔧 MANDATORY CODING STANDARDS

### Layer Separation (CRITICAL)
- **API Layer** (`app/api/`): ONLY layer that can raise/handle `HTTPException`
- **Application Services** (`app/service_layer/`): Use case orchestration, raises custom exceptions
- **Domain Layer** (`app/domain/`): 
  - **Entities & Value Objects**: Core business objects with identity/behavior
  - **Domain Services**: Business logic that doesn't belong to entities
  - **Domain Events**: Record significant business events
  - **Aggregates**: Consistency boundaries and transaction scope
- **Infrastructure Layer** (`app/adapters/`): External concerns (DB, external APIs, repositories)
  - **Repository Implementation** (`app/adapters/repository/`): Data access, raises custom exceptions
  - **ORM Engine** (`app/adapters/orm/`): Database connection and session management

### File Organization (ENFORCED)
- **Domain Models**: Pure domain entities (dataclasses/classes) in `models.py` files ONLY
- **ORM Infrastructure**: SQLAlchemy mappings in `orm.py` files ONLY (within domain folders)
- **API Schemas**: Pydantic BaseModel in `schemas.py` files ONLY  
- **NEVER MIX**: Domain models, ORM mappings, and API schemas must be in separate files
- **Conversion**: Always use `model_validate(obj)` to convert ORM → Pydantic (never `from_orm`)

### Code Quality Requirements
- **Type Annotations**: Required on ALL functions, methods, variables
- **Documentation**: Docstrings required on all public classes/functions
- **Configuration**: Use Pydantic Settings - never access `os.environ` directly
- **Imports**: At file top only - avoid function-level imports
- **Dependency Injection**: Required for repositories, services, UoW patterns
- **Single Responsibility**: Each service/repository handles ONE domain concern only
- **Interface Segregation**: Define specific repository interfaces per domain aggregate

## 🧪 TESTING REQUIREMENTS (NON-NEGOTIABLE)

### Test Execution Workflow
1. **AFTER EVERY CODE CHANGE**: Run `python -m pytest tests/ --tb=short -v > test_results.txt 2>&1`
2. **READ RESULTS IMMEDIATELY**: Use `read_file` to analyze test output from saved files
3. **NAME FILES DESCRIPTIVELY**: `test_initial.txt`, `test_after_fix.txt`, `test_final.txt`
4. **FIX FAILURES IN SAME SESSION**: Don't leave broken tests - debug and fix immediately

### Testing Technology Stack
- **Framework**: pytest with pytest-asyncio for async tests
- **HTTP Client**: httpx with AsyncClient for API testing  
- **Mocking**: pytest-mock (NOT unittest.mock) - use `mocker` fixture
- **Test Data**: pydantic-factories for realistic model generation
- **Database**: Dedicated test database with function-scoped cleanup

### Test Categories & Patterns
- **Unit Tests**: Mock infrastructure dependencies, test business logic
- **Integration Tests**: Real database, test full request/response cycles
- **E2E Tests**: Complete user workflows from signup to feature usage
- **Test Documentation**: Every test MUST have GIVEN/WHEN/THEN docstring pattern

### Critical Test Rules
- **Fixtures in conftest.py ONLY**: Never define fixtures in individual test files
- **AsyncClient with ASGITransport**: `ASGITransport(app=...)` - never use deprecated `app=app`
- **Function-scoped DB cleanup**: Reset async engine between tests to avoid contamination
- **Realistic test data**: Use factories, override specific fields per test
- **Mock infrastructure, not domain**: Mock repositories/UoW, not business entities

## 🔍 TYPE CHECKING & CODE QUALITY

### MyPy Configuration
- **Strict mode enabled**: See `mypy.ini` for complete settings
- **Required annotations**: All functions, methods, and variables must be typed
- **Built-in collections**: Use `list[str]` not `List[str]` (PEP 585)
- **Ignored paths**: `alembic/` and `tests/` excluded from type checking
- **CI Integration**: Type checking runs in pipeline before merge

### Code Standards
- **Focus on logic**: Let ruff handle formatting, focus on correctness
- **Remove unused ignores**: Clean up unnecessary `# type: ignore` comments
- **Document public APIs**: Docstrings required on all public classes/functions

## ⚠️ COMMON PITFALLS & DEBUGGING (CRITICAL AWARENESS)

### Database & Testing Issues
- **Async Engine Reset**: ALWAYS reset engine singleton between tests (function scope)
- **Event Loop Contamination**: Use function-scoped fixtures to avoid asyncpg/SQLAlchemy errors
- **Test Authentication**: Use `override_auth` fixture ONLY for unit tests, not e2e/integration
- **Database Isolation**: Set READ COMMITTED, ensure sessions are committed/closed
- **Test Data Consistency**: Ensure test data matches expected state, especially with auth overrides

### Repository & Service Layer
- **Following Relationships**: Use `UserRepository.is_following()` NOT `FollowerRepository`
- **Nullable ID Handling**: Always check for None when dealing with model IDs from database
- **Service Layer Validation**: Services validate business rules, don't handle HTTP concerns
- **Repository Patterns**: Each domain has specific query methods (e.g., `list_by_article_id`)

### Database Migrations & Schema
- **Migration Naming**: Follow `YYYYMMDD_add_table_name.py` pattern
- **Migration Completeness**: Always include both `upgrade()` and `downgrade()` functions
- **CASCADE DELETE**: Use for automatic cleanup (comments when articles/users deleted)

### FastAPI & Modern Practices
- **Lifespan Events**: Use lifespan handlers, NOT deprecated `@app.on_event`
- **Startup Safety**: Ensure all startup/shutdown logic is idempotent
- **Deprecation Warnings**: Check and update to latest best practices immediately

### Development Workflow
- **Environment Setup**: Async engine created AFTER environment variables set
- **Debug Targeted**: Use specific debug prints (engine URL, session info, user lookups)
- **RealWorld Compliance**: All endpoints/models/errors must match spec exactly

## 📚 REFERENCE SPECIFICATIONS

### API Compliance
- **Primary Reference**: https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints/
- **Validation Requirement**: All endpoints, models, error responses must match spec exactly
- **Coverage Requirement**: All features must have corresponding tests

### Technology Standards
- **Domain Models**: Pure Python classes/dataclasses in `models.py` files only
- **ORM Infrastructure**: SQLAlchemy mappings in `orm.py` files only (within domain folders)  
- **API Schemas**: Pydantic BaseModel in `schemas.py` files only
- **Conversion Pattern**: Always `model_validate(obj)` for ORM → Pydantic (never `from_orm`)
- **Configuration**: Pydantic Settings only - never direct `os.environ` access

### Maintenance Requirements
- **Documentation Updates**: Update this file AND README when structure/features change
- **Exception Handling**: Only API layer handles `HTTPException`, others use custom exceptions
- **Test Coverage**: All new features require comprehensive test coverage
- **Type Coverage**: All new code requires complete type annotations
