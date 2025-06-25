# Development Workflow Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

This guide covers the complete development workflow for contributing to the FastAPI RealWorld Demo project.

## Table of Contents

- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Code Standards](#code-standards)
- [Testing Workflow](#testing-workflow)
- [Database Management](#database-management)
- [Debugging](#debugging)
- [Performance](#performance)

## Development Setup

### Environment Setup

```bash
# Clone and setup
git clone <repository-url>
cd fastapi-realworld-demo
poetry install --with dev
poetry shell

# Setup databases
make setup-dev

# Verify setup
make test
```

### Development Tools

The project includes several development tools:

- **Ruff**: Code formatting and linting
- **MyPy**: Static type checking
- **Pytest**: Testing framework with async support
- **Poetry**: Dependency management
- **Make**: Task automation

### IDE Configuration

#### VS Code Settings

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.formatting.provider": "ruff",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "python.testing.pytestEnabled": true
}
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **feature/**: New features (`feature/add-user-profiles`)
- **fix/**: Bug fixes (`fix/authentication-token-validation`)
- **docs/**: Documentation updates (`docs/update-api-guide`)

### Development Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes Following Standards**
   - Write tests first (TDD approach)
   - Follow the commit guidelines
   - Ensure type safety

3. **Test Your Changes**
   ```bash
   make test           # Run all tests
   make test-unit      # Unit tests only
   make test-e2e       # End-to-end tests
   ```

4. **Code Quality Checks**
   ```bash
   make lint           # Run ruff
   make type-check     # Run mypy
   make format         # Format code
   ```

5. **Commit with Proper Messages**
   ```bash
   # Follow the commit guidelines in docs/development/COMMIT_GUIDELINES.md
   git add .
   git commit -m "feat(users): add user profile update functionality"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Architecture Layers

Follow the DDD (Domain-Driven Design) architecture:

```python
# Domain Layer - Pure business logic
@dataclass
class User:
    username: str
    email: str
    # No infrastructure dependencies

# Service Layer - Use cases and orchestration
@transactional()
async def create_user(uow: AsyncUnitOfWork, user_data: NewUserRequest) -> UserRead:
    repo = UserRepository(uow.session)
    # Business logic with transaction management

# API Layer - HTTP interface
@router.post("/users", response_model=UserResponse)
async def create_user_endpoint(user_req: NewUserRequest) -> UserResponse:
    user = await create_user(user_req)  # Service layer call
    return UserResponse(user=user)
```

### Type Safety

All code must be fully typed:

```python
from typing import Optional

# Function signatures
async def get_user_by_id(user_id: int) -> Optional[User]:
    # Implementation

# Class definitions
@dataclass
class UserCreate:
    username: str
    email: str
    password: str
```

### Error Handling

Use domain-specific exceptions:

```python
# Domain exceptions
class UserNotFoundError(NotFoundError):
    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found")

# Service layer
@transactional()
async def get_user(uow: AsyncUnitOfWork, user_id: int) -> UserRead:
    repo = UserRepository(uow.session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError(user_id)
    return UserRead.model_validate(user.__dict__)
```

## Testing Workflow

### Test Categories

1. **Unit Tests** (`tests/unit/`): Test business logic in isolation
2. **Integration Tests** (`tests/integration/`): Test with real database
3. **End-to-End Tests** (`tests/e2e/`): Full API workflows

### Test Development Process

1. **Write Failing Test First**
   ```python
   async def test_create_user_success(client: AsyncClient):
       # Given
       user_data = {
           "user": {
               "username": "testuser",
               "email": "test@example.com",
               "password": "testpass123"
           }
       }
       
       # When
       response = await client.post("/api/users", json=user_data)
       
       # Then
       assert response.status_code == 201
       assert response.json()["user"]["username"] == "testuser"
   ```

2. **Implement Feature**
3. **Ensure Test Passes**
4. **Refactor if Needed**

### Running Tests

```bash
# All tests
make test

# Specific categories
make test-unit
make test-integration
make test-e2e

# With coverage
make test-cov

# Specific test file
pytest tests/integration/test_users.py -v

# Specific test function
pytest tests/integration/test_users.py::test_create_user_success -v
```

## Database Management

### Development Database

```bash
# Start development database
make up-db

# Apply migrations
make migrate

# Reset database (destructive!)
make reset-db

# Create new migration
poetry run alembic revision --autogenerate -m "add user table"
```

### Test Database

```bash
# Setup test database
make setup-test

# Run tests with fresh database
make test
```

### Database Debugging

```bash
# Connect to development database
docker exec -it fastapi-realworld-demo-postgres-1 psql -U rw-demo -d rw-demo-db

# View database logs
docker logs fastapi-realworld-demo-postgres-1
```

## Debugging

### Application Debugging

1. **Add Debug Logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   async def my_function():
       logger.info("Processing user request")
       # Your code here
   ```

2. **Use Interactive Debugger**
   ```python
   import pdb; pdb.set_trace()  # Add breakpoint
   ```

3. **Environment Variables**
   ```bash
   # Enable debug mode
   DEBUG=True poetry run uvicorn app.main:app --reload
   ```

### Database Debugging

```python
# Log SQL queries
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Test Debugging

```bash
# Run single test with output
pytest tests/test_file.py::test_name -v -s

# Drop into debugger on failure
pytest --pdb
```

## Performance

### Database Performance

- Use async queries everywhere
- Implement proper indexing
- Use database transactions appropriately

```python
# Good: Async all the way
@transactional()
async def get_user_articles(uow: AsyncUnitOfWork, user_id: int) -> list[Article]:
    repo = ArticleRepository(uow.session)
    return await repo.list_by_author_id(user_id)
```

### API Performance

- Use appropriate HTTP status codes
- Implement pagination for list endpoints
- Use response models to control serialization

```python
# Pagination example
async def list_articles(
    limit: int = 20,
    offset: int = 0
) -> dict[str, Any]:
    # Implementation with proper limits
```

### Testing Performance

The test suite is optimized for speed:

- Database cleanup in <50ms
- Parallel test execution
- Efficient test fixtures

## Continuous Integration

The project includes CI/CD checks:

1. **Code Quality**: Ruff linting and formatting
2. **Type Safety**: MyPy type checking
3. **Tests**: Full test suite execution
4. **Security**: Dependency vulnerability scanning

### Local CI Simulation

```bash
# Run all CI checks locally
make ci-check

# Individual checks
make lint
make type-check
make test
make security-check
```

## Common Tasks

### Adding a New Feature

1. Create feature branch
2. Write tests for the new functionality
3. Implement domain models and business logic
4. Add service layer functions with `@transactional()`
5. Create API endpoints
6. Update documentation
7. Commit following guidelines

### Fixing a Bug

1. Create a test that reproduces the bug
2. Fix the issue
3. Ensure the test passes
4. Check for regression in related areas
5. Commit with proper message

### Updating Dependencies

```bash
# Update all dependencies
poetry update

# Update specific dependency
poetry add fastapi@latest

# Check for security vulnerabilities
poetry audit
```

For detailed commit message guidelines, see [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md).
