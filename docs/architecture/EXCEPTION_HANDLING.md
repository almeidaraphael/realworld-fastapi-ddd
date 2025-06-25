# Exception Handling Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

This guide provides comprehensive documentation for implementing standardized exception handling in the FastAPI RealWorld application. It covers the complete exception handling system, from design principles to practical implementation patterns.

> **💡 Note**: This document provides the complete exception handling guide. For a quick overview and integration with other architectural concepts, see the [Exception Handling](../../README.md#standardized-exception-handling) section in README.md.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture & Design](#architecture--design)
- [Implementation Guide](#implementation-guide)
- [HTTP Status Code Mapping](#http-status-code-mapping)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Testing Exception Handling](#testing-exception-handling)
- [Migration Guide](#migration-guide)
- [Troubleshooting](#troubleshooting)

## System Overview

The exception handling system provides a standardized approach to error handling that ensures consistency across all API endpoints while maintaining clear separation of concerns between layers. The system automatically translates domain-specific exceptions to appropriate HTTP responses.

### Key Benefits

- **Consistency**: All endpoints return error responses in the same format
- **Type Safety**: Compile-time validation of exception handling patterns
- **Maintainability**: Centralized mapping of exceptions to HTTP status codes
- **Testability**: Domain logic can be tested independently of HTTP concerns
- **Clear Architecture**: Clean separation between business logic and HTTP layer

## Architecture & Design

### Core Principles

1. **Domain Layer Purity**: Domain and service layers only raise domain-specific exceptions
2. **HTTP Translation**: API layer translates domain exceptions to HTTP responses
3. **Automatic Mapping**: Status codes are automatically mapped based on exception types
4. **Error Code Support**: Optional error codes for enhanced client-side handling
5. **Exception Chaining**: Proper exception chaining preserves stack traces for debugging

### Layer Responsibilities

```
┌─────────────────┐
│   API Layer     │  ← Handles HTTP concerns, translates exceptions
├─────────────────┤
│ Service Layer   │  ← Raises domain exceptions, no HTTP knowledge
├─────────────────┤
│ Domain Layer    │  ← Defines domain-specific exceptions
├─────────────────┤
│Infrastructure   │  ← May raise infrastructure exceptions (DB, network)
└─────────────────┘
```

### Exception Flow

```
1. Infrastructure/Service raises domain exception
2. Exception bubbles up to API layer
3. API layer catches domain exception
4. translate_domain_error_to_http() converts to HTTPException
5. FastAPI returns appropriate HTTP response
```

### Exception Class Hierarchy

The exception system is built on a hierarchical structure that allows for precise error handling while maintaining flexibility:

```
DomainError (Base class for all domain exceptions)
├── NotFoundError (404 - Resource not found)
│   ├── UserNotFoundError
│   ├── ProfileNotFoundError  
│   ├── ArticleNotFoundError
│   └── CommentNotFoundError
├── PermissionError (403 - Forbidden access)
│   ├── ArticlePermissionError
│   └── CommentPermissionError
├── ConflictError (409 - Resource conflicts)
│   ├── UserAlreadyExistsError
│   └── ArticleSlugConflictError
├── ValidationError (400 - Data validation failures)
│   ├── CannotFollowYourselfError
│   ├── UserOrFollowerIdMissingError
│   └── InvalidArticleDataError
└── AuthenticationError (401 - Authentication failures)
    └── InvalidCredentialsError
```

### Base Exception Classes

All domain exceptions inherit from base exception classes in `app/shared/exceptions.py`:

- **`DomainError`**: Base class for all domain exceptions with error code support
- **`NotFoundError`**: For resources that cannot be found (404)
- **`PermissionError`**: For authorization and permission failures (403)
- **`ConflictError`**: For resource conflicts like duplicates (409)
- **`ValidationError`**: For data validation and business rule violations (400)
- **`AuthenticationError`**: For authentication failures (401)

## Implementation Guide

### Step 1: Define Domain Exceptions

Each domain should have its own `exceptions.py` file with domain-specific exceptions that inherit from the appropriate base classes:

```python
# app/domain/users/exceptions.py
"""User domain exceptions."""

from app.shared.exceptions import ConflictError, NotFoundError, AuthenticationError


class UserAlreadyExistsError(ConflictError):
    """Raised when attempting to create a user that already exists."""


class UserNotFoundError(NotFoundError):
    """Raised when a requested user cannot be found."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when user login credentials are invalid."""
```

#### Guidelines for Domain Exceptions

1. **Naming Convention**: Use descriptive names ending with "Error"
2. **Inheritance**: Choose the most specific base class that fits the error type
3. **Documentation**: Include clear docstrings explaining when the exception is raised
4. **Context**: Include relevant context in the exception message

### Step 2: Raise Exceptions in Service Layer

Service layer methods should raise domain exceptions without any HTTP concerns:

```python
# app/service_layer/users/services.py
from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError

async def create_user(user_req: NewUserRequest) -> UserRead:
    """Create a new user account."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        
        # Check for existing user
        existing = await repo.get_by_username_or_email(
            user_req.user.username, 
            user_req.user.email
        )
        if existing:
            raise UserAlreadyExistsError(
                "A user with this username or email already exists"
            )
        
        # Create new user
        user = User(
            username=user_req.user.username,
            email=user_req.user.email,
            hashed_password=hash_password(user_req.user.password)
        )
        await repo.add(user)
        return UserRead.model_validate(user.__dict__)


async def get_user_by_id(user_id: int) -> UserRead:
    """Get user by ID."""
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        user = await repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with ID {user_id} not found")
        return UserRead.model_validate(user.__dict__)
```

#### Service Layer Best Practices

1. **Specific Exceptions**: Raise the most specific exception type available
2. **Meaningful Messages**: Include context that helps users understand the problem
3. **Early Validation**: Check for error conditions early in the method
4. **No HTTP Knowledge**: Never import or use FastAPI's HTTPException
5. **Exception Chaining**: Use `raise ... from ...` when wrapping other exceptions

### Step 3: Handle Exceptions in API Layer

API endpoints catch domain exceptions and translate them to HTTP responses:

```python
# app/api/users.py
from fastapi import APIRouter, status
from app.shared.exceptions import translate_domain_error_to_http
from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.service_layer.users.services import create_user, get_user_by_id

router = APIRouter()


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def create_user_endpoint(user: NewUserRequest) -> UserResponse:
    """Register a new user account."""
    try:
        user_data = await create_user(user)
        token = create_access_token({"sub": user_data.email})
        return UserResponse(
            user=UserWithToken(
                email=user_data.email,
                token=token,
                username=user_data.username,
                bio=user_data.bio or "",
                image=user_data.image or "",
            )
        )
    except UserAlreadyExistsError as exc:
        raise translate_domain_error_to_http(exc) from exc


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int) -> UserResponse:
    """Get user by ID."""
    try:
        user_data = await get_user_by_id(user_id)
        return UserResponse(user=UserRead.model_validate(user_data))
    except UserNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
```

#### API Layer Best Practices

1. **Specific Catching**: Catch specific domain exceptions rather than broad Exception types
2. **Exception Chaining**: Always use `from exc` to preserve the original exception
3. **Translation**: Use `translate_domain_error_to_http()` for consistent conversion
4. **Generic Fallback**: Have a fallback for unexpected exceptions (see Migration Guide)
5. **No Business Logic**: Keep API layer focused on HTTP concerns only

## HTTP Status Code Mapping

The system automatically maps exception types to HTTP status codes:

| Exception Type | HTTP Status Code | Description |
|----------------|------------------|-------------|
| `NotFoundError` | 404 | Resource not found |
| `PermissionError` | 403 | Forbidden/unauthorized access |
| `ConflictError` | 409 | Resource conflict |
| `ValidationError` | 400 | Bad request/validation error |
| `AuthenticationError` | 401 | Authentication required |
| `DomainError` (other) | 500 | Internal server error |

## Usage Examples

### Basic Exception Handling Pattern

```python
from app.shared.exceptions import translate_domain_error_to_http
from app.domain.articles.exceptions import ArticleNotFoundError, ArticlePermissionError

@router.get("/articles/{slug}")
async def get_article(slug: str, current_user: UserWithToken | None = None) -> ArticleResponse:
    """Get an article by slug."""
    try:
        article = await get_article_by_slug(slug, current_user)
        return ArticleResponse(article=article)
    except ArticleNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
```

### Handling Multiple Exception Types

For endpoints that can raise multiple types of exceptions, catch them together:

```python
@router.post("/{username}/follow")
async def follow_profile(
    username: str, 
    current_user: UserWithToken = Depends(get_current_user)
) -> ProfileResponse:
    """Follow a user profile."""
    try:
        profile = await follow_user(username, current_user.username)
        return ProfileResponse(profile=ProfileRead.model_validate(profile))
    except (
        CannotFollowYourselfError,
        ProfileNotFoundError, 
        UserOrFollowerIdMissingError
    ) as exc:
        raise translate_domain_error_to_http(exc) from exc
```

### Custom Error Codes for Client Integration

Domain exceptions can include custom error codes for better client-side handling:

```python
# Creating exception with custom error code
class InsufficientPermissionsError(PermissionError):
    """Raised when user lacks required permissions."""
    
    def __init__(self, action: str, resource: str):
        super().__init__(
            f"Insufficient permissions to {action} {resource}",
            error_code="INSUFFICIENT_PERMISSIONS"
        )

# Usage in service layer
if not user.can_edit_article(article):
    raise InsufficientPermissionsError("edit", "article")

# Results in HTTP response:
# {
#   "detail": "INSUFFICIENT_PERMISSIONS: Insufficient permissions to edit article"
# }
```

### Error Code Patterns

Use consistent error codes for common scenarios:

```python
# Authentication errors
class InvalidTokenError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Authentication token is invalid or expired",
            error_code="INVALID_TOKEN"
        )

class MissingTokenError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Authentication token is required",
            error_code="MISSING_TOKEN"
        )

# Validation errors
class InvalidEmailFormatError(ValidationError):
    def __init__(self, email: str):
        super().__init__(
            f"Email address '{email}' is not valid",
            error_code="INVALID_EMAIL_FORMAT"
        )

# Resource conflicts
class DuplicateResourceError(ConflictError):
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            f"{resource_type} with identifier '{identifier}' already exists",
            error_code="DUPLICATE_RESOURCE"
        )
```

### Advanced Exception Handling

#### Conditional Error Codes

Sometimes you want error codes only in certain conditions:

```python
@router.get("/api/user")
async def get_current_user(token: str = Depends(get_token_from_header)) -> UserResponse:
    """Get the current authenticated user."""
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email or not isinstance(email, str):
            # No error code for basic auth failures
            raise AuthenticationError("Invalid authentication credentials", error_code="")
        
        user = await get_user_by_email(email)
        return UserResponse(user=UserWithToken(...))
    except UserNotFoundError:
        # Different error code for user not found
        raise AuthenticationError("User not found", error_code="")
    except AuthenticationError as exc:
        raise translate_domain_error_to_http(exc) from exc
```

#### Wrapping Infrastructure Exceptions

When infrastructure exceptions need to be converted to domain exceptions:

```python
async def get_article_by_slug(slug: str) -> Article:
    """Get article by slug from database."""
    try:
        async with AsyncUnitOfWork() as uow:
            repo = ArticleRepository(uow.session)
            article = await repo.get_by_slug(slug)
            if not article:
                raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
            return article
    except asyncpg.ConnectionError as exc:
        # Wrap infrastructure exceptions in domain exceptions
        raise ArticleNotFoundError(
            f"Unable to retrieve article '{slug}' due to database error"
        ) from exc
    except Exception as exc:
        # Generic fallback for unexpected errors
        raise ArticleNotFoundError(
            f"Failed to retrieve article '{slug}'"
        ) from exc
```

## Best Practices

### Domain Exception Design

1. **Single Responsibility**: Each exception should represent one specific error condition
2. **Descriptive Names**: Use clear, descriptive names that indicate the problem
3. **Proper Inheritance**: Choose the base class that best represents the HTTP status needed
4. **Rich Context**: Include relevant details in exception messages
5. **Consistent Messaging**: Use consistent language and tone across similar exceptions

```python
# ✅ Good: Specific, descriptive, includes context
class ArticleSlugAlreadyExistsError(ConflictError):
    """Raised when attempting to create an article with a slug that already exists."""
    
    def __init__(self, slug: str):
        super().__init__(f"Article with slug '{slug}' already exists")

# ❌ Bad: Generic, vague, lacks context
class ArticleError(Exception):
    pass
```

### Service Layer Exception Handling

1. **Validate Early**: Check for error conditions as early as possible
2. **Specific Exceptions**: Raise the most specific exception type available
3. **No HTTP Knowledge**: Never import or reference HTTP status codes
4. **Context Preservation**: Include relevant context in exception messages
5. **Exception Chaining**: Use proper exception chaining when wrapping other exceptions

```python
# ✅ Good: Early validation, specific exception, rich context
async def update_article(slug: str, user_id: int, data: ArticleUpdateData) -> Article:
    """Update an article."""
    # Early validation
    article = await get_article_by_slug(slug)
    if not article:
        raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
    
    if article.author_id != user_id:
        raise ArticlePermissionError(
            f"User {user_id} cannot edit article '{slug}' owned by user {article.author_id}"
        )
    
    # Update logic...

# ❌ Bad: Late validation, generic exception, poor context
async def update_article(slug: str, user_id: int, data: ArticleUpdateData) -> Article:
    try:
        # Business logic first, validation later
        article = await repo.update(slug, data)
        if article.author_id != user_id:
            raise Exception("Cannot edit")  # Too generic
        return article
    except:
        raise Exception("Update failed")  # Loses original error
```

### API Layer Exception Handling

1. **Catch Specific Types**: Catch specific domain exceptions rather than broad Exception types
2. **Use Translation Function**: Always use `translate_domain_error_to_http()` for consistency
3. **Exception Chaining**: Preserve original exceptions with `from exc`
4. **Generic Fallback**: Have a fallback for truly unexpected errors
5. **No Business Logic**: Keep API layer focused only on HTTP translation

```python
# ✅ Good: Specific catching, proper translation, fallback
@router.put("/articles/{slug}")
async def update_article_endpoint(
    slug: str,
    article_data: ArticleUpdateRequest,
    current_user: UserWithToken = Depends(get_current_user)
) -> ArticleResponse:
    """Update an article."""
    try:
        article = await update_article(slug, current_user.id, article_data.article)
        return ArticleResponse(article=ArticleRead.model_validate(article))
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc
    except Exception as exc:
        # Fallback for unexpected errors
        logger.error(f"Unexpected error updating article {slug}: {exc}")
        raise translate_domain_error_to_http(
            DomainError(f"Failed to update article: {str(exc)}")
        ) from exc

# ❌ Bad: Broad catching, manual HTTP status, lost context
@router.put("/articles/{slug}")
async def update_article_endpoint(slug: str, data: ArticleUpdateRequest) -> ArticleResponse:
    try:
        article = await update_article(slug, data)
        return ArticleResponse(article=article)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))  # Wrong status, lost type info
```

### Error Message Guidelines

1. **User-Friendly**: Write messages that end users can understand
2. **Actionable**: Include guidance on how to resolve the issue when possible
3. **Consistent Tone**: Use consistent language and tone across the application
4. **Avoid Technical Jargon**: Don't expose internal implementation details
5. **Security Conscious**: Don't leak sensitive information in error messages

```python
# ✅ Good: Clear, actionable, user-friendly
class InvalidPasswordError(ValidationError):
    def __init__(self):
        super().__init__(
            "Password must be at least 8 characters and contain at least one number",
            error_code="INVALID_PASSWORD"
        )

class EmailAlreadyRegisteredError(ConflictError):
    def __init__(self, email: str):
        super().__init__(
            f"An account with email '{email}' already exists. Please use a different email or try logging in.",
            error_code="EMAIL_ALREADY_REGISTERED"
        )

# ❌ Bad: Technical, not actionable, potentially insecure
class DatabaseError(Exception):
    def __init__(self, table: str, query: str):
        super().__init__(f"Query failed on table {table}: {query}")  # Exposes internals

class AuthError(Exception):
    def __init__(self):
        super().__init__("Authentication failed")  # Not specific enough
```

### Performance Considerations

1. **Avoid Exception-Heavy Paths**: Don't use exceptions for normal control flow
2. **Minimize Exception Creation**: Reuse exception instances when possible for common errors
3. **Lazy Message Formatting**: Use lazy formatting for expensive message construction
4. **Stack Trace Limitation**: Consider limiting stack trace depth for known error conditions

```python
# ✅ Good: Exceptions for truly exceptional cases
async def get_user_by_email(email: str) -> User | None:
    """Get user by email, returning None if not found."""
    user = await repo.get_by_email(email)
    return user  # Let caller decide if None is an error

async def get_user_by_email_or_raise(email: str) -> User:
    """Get user by email, raising exception if not found."""
    user = await get_user_by_email(email)
    if user is None:
        raise UserNotFoundError(f"User with email '{email}' not found")
    return user

# ❌ Bad: Using exceptions for control flow
async def get_user_by_email(email: str) -> User:
    try:
        return await repo.get_by_email(email)
    except NotFound:
        raise UserNotFoundError(f"User with email '{email}' not found")
```

## Testing Exception Handling

### Unit Testing Domain Exceptions

Test that your service layer properly raises domain exceptions:

```python
import pytest
from app.domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.service_layer.users.services import create_user, get_user_by_id

@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises_error():
    """
    GIVEN a user already exists with an email
    WHEN attempting to create another user with the same email
    THEN UserAlreadyExistsError should be raised
    """
    # Setup - create initial user
    user_data = NewUserRequest(user=UserCreate(
        username="user1",
        email="test@example.com", 
        password="password123"
    ))
    await create_user(user_data)
    
    # Test - attempt to create duplicate
    duplicate_data = NewUserRequest(user=UserCreate(
        username="user2",  # Different username
        email="test@example.com",  # Same email
        password="password456"
    ))
    
    with pytest.raises(UserAlreadyExistsError) as exc_info:
        await create_user(duplicate_data)
    
    assert "already exists" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_nonexistent_user_raises_error():
    """
    GIVEN no user exists with a specific ID
    WHEN attempting to get that user
    THEN UserNotFoundError should be raised
    """
    with pytest.raises(UserNotFoundError) as exc_info:
        await get_user_by_id(99999)
    
    assert "not found" in str(exc_info.value)
    assert "99999" in str(exc_info.value)
```

### Integration Testing API Error Responses

Test that API endpoints return correct HTTP status codes and error formats:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_duplicate_user_returns_409(async_client: AsyncClient):
    """
    GIVEN a user already exists
    WHEN attempting to register with the same email
    THEN the API should return 409 Conflict
    """
    # Create initial user
    user_data = {
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    }
    await async_client.post("/api/users", json=user_data)
    
    # Attempt duplicate registration
    duplicate_data = {
        "user": {
            "username": "differentuser",
            "email": "test@example.com",  # Same email
            "password": "password456"
        }
    }
    response = await async_client.post("/api/users", json=duplicate_data)
    
    assert response.status_code == 409
    assert "detail" in response.json()
    assert "already exists" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_nonexistent_article_returns_404(async_client: AsyncClient):
    """
    GIVEN no article exists with a specific slug
    WHEN requesting that article
    THEN the API should return 404 Not Found
    """
    response = await async_client.get("/api/articles/nonexistent")
    
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()
```

### Testing Error Code Consistency

Ensure error codes are consistent and predictable:

```python
@pytest.mark.asyncio
async def test_error_codes_are_consistent(async_client: AsyncClient):
    """
    GIVEN various error scenarios
    WHEN they occur
    THEN consistent error codes should be returned
    """
    # Test authentication error code
    response = await async_client.get("/api/user")  # No auth token
    assert response.status_code == 401
    
    # Test validation error code  
    invalid_user = {"user": {"email": "invalid-email"}}
    response = await async_client.post("/api/users", json=invalid_user)
    assert response.status_code == 400
    
    # Test not found error code
    response = await async_client.get("/api/articles/nonexistent")
    assert response.status_code == 404
```

### Mock Testing with Exception Translation

Test the exception translation without hitting the database:

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.api.users import create_user_endpoint
from app.domain.users.exceptions import UserAlreadyExistsError

@pytest.mark.asyncio
async def test_exception_translation_in_endpoint():
    """
    GIVEN the service layer raises a domain exception
    WHEN the API endpoint is called
    THEN it should translate to the correct HTTP response
    """
    # Mock the service to raise domain exception
    with patch('app.api.users.create_user') as mock_create:
        mock_create.side_effect = UserAlreadyExistsError("User exists")
        
        # Create mock request
        user_request = NewUserRequest(user=UserCreate(
            username="test",
            email="test@example.com", 
            password="password"
        ))
        
        # Should raise HTTPException with correct status
        with pytest.raises(HTTPException) as exc_info:
            await create_user_endpoint(user_request)
        
        assert exc_info.value.status_code == 409
        assert "User exists" in exc_info.value.detail
```

### Custom Error Codes

Test that custom error codes are returned as expected:

```python
@pytest.mark.asyncio
async def test_custom_error_codes(async_client: AsyncClient):
    """
    GIVEN a request that triggers a custom error
    WHEN the error occurs
    THEN the response should include the custom error code
    """
    response = await async_client.post("/api/users", json={"user": {"email": "test@example.com"}})
    assert response.status_code == 409
    assert response.json()["detail"].startswith("EMAIL_ALREADY_REGISTERED:")
```

## Migration Guide

### Migrating Existing Endpoints

To migrate existing endpoints from the old HTTPException pattern to the new domain exception system:

#### Step 1: Identify Current Exception Handling

Look for patterns like this in your API endpoints:

```python
# ❌ Old pattern to migrate
@router.get("/articles/{slug}")
async def get_article(slug: str) -> ArticleResponse:
    try:
        article = await get_article_by_slug(slug)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return ArticleResponse(article=article)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

#### Step 2: Move Exception Logic to Service Layer

Refactor business logic exceptions to the service layer:

```python
# ✅ New service layer implementation
async def get_article_by_slug(slug: str, user: User | None = None) -> Article:
    """Get article by slug."""
    async with AsyncUnitOfWork() as uow:
        repo = ArticleRepository(uow.session)
        article = await repo.get_by_slug(slug)
        
        if not article:
            raise ArticleNotFoundError(f"Article with slug '{slug}' not found")
        
        if article.is_private and (not user or article.author_id != user.id):
            raise ArticlePermissionError(f"Access denied to private article '{slug}'")
        
        return article
```

#### Step 3: Update API Layer

Simplify the API layer to focus only on HTTP translation:

```python
# ✅ New API layer implementation
@router.get("/articles/{slug}")
async def get_article(
    slug: str,
    current_user: User | None = Depends(get_current_user_optional)
) -> ArticleResponse:
    """Get an article by slug."""
    try:
        article = await get_article_by_slug(slug, current_user)
        return ArticleResponse(article=ArticleRead.model_validate(article))
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc
```

#### Step 4: Update Tests

Update tests to expect new status codes and error formats:

```python
# Update test expectations
@pytest.mark.asyncio
async def test_get_nonexistent_article_returns_404(async_client: AsyncClient):
    response = await async_client.get("/api/articles/nonexistent")
    assert response.status_code == 404  # Was potentially 500 before
    assert "ArticleNotFoundError" in response.json()["detail"]  # New error format
```

### Common Migration Scenarios

#### Scenario 1: Authentication Errors

```python
# ❌ Before: Manual HTTP status in API layer
@router.get("/user")
async def get_current_user(token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ After: Domain exceptions in dependency
def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Token "):
        raise AuthenticationError("Missing or invalid Authorization header")
    
    token = auth_header[6:]  # Remove "Token " prefix
    if not token:
        raise AuthenticationError("Authentication token is required")
    
    return token

@router.get("/user")
async def get_current_user(current_user: UserWithToken = Depends(get_current_user_dependency)):
    return UserResponse(user=current_user)
```

#### Scenario 2: Validation Errors

```python
# ❌ Before: Manual validation in API layer
@router.post("/articles")
async def create_article(article_data: ArticleCreateRequest):
    if not article_data.article.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    if len(article_data.article.body) < 10:
        raise HTTPException(status_code=400, detail="Body must be at least 10 characters")

# ✅ After: Validation in service layer
async def create_article(article_data: ArticleCreateData, author_id: int) -> Article:
    # Validate business rules
    if not article_data.title.strip():
        raise InvalidArticleDataError("Article title cannot be empty")
    
    if len(article_data.body) < 10:
        raise InvalidArticleDataError("Article body must be at least 10 characters")
    
    # Create article logic...
```

#### Scenario 3: Resource Not Found

```python
# ❌ Before: Mixed concerns
@router.delete("/articles/{slug}")
async def delete_article(slug: str, current_user: User = Depends(get_current_user)):
    article = await repo.get_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    if article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete others' articles")

# ✅ After: Clean separation
async def delete_article(slug: str, user_id: int) -> None:
    """Delete an article."""
    article = await get_article_by_slug(slug)  # Raises ArticleNotFoundError
    
    if article.author_id != user_id:
        raise ArticlePermissionError(f"User {user_id} cannot delete article '{slug}'")
    
    await repo.delete(article)

@router.delete("/articles/{slug}")
async def delete_article_endpoint(
    slug: str, 
    current_user: UserWithToken = Depends(get_current_user)
):
    try:
        await delete_article(slug, current_user.id)
        return {"message": "Article deleted successfully"}
    except (ArticleNotFoundError, ArticlePermissionError) as exc:
        raise translate_domain_error_to_http(exc) from exc
```

### Migration Checklist

For each endpoint you migrate:

- [ ] ✅ Move business logic exceptions to service layer
- [ ] ✅ Create appropriate domain exceptions if they don't exist
- [ ] ✅ Update API layer to use `translate_domain_error_to_http()`
- [ ] ✅ Remove manual HTTPException creation from API layer
- [ ] ✅ Update tests to expect new error formats
- [ ] ✅ Verify correct HTTP status codes are returned
- [ ] ✅ Test that error messages are user-friendly
- [ ] ✅ Ensure proper exception chaining with `from exc`

## Troubleshooting

### Common Issues and Solutions

#### Issue: Wrong HTTP Status Code

**Problem**: Getting 500 instead of expected 4xx status code

**Cause**: Exception not properly inheriting from correct base class

```python
# ❌ Wrong: Generic exception gives 500
class UserNotFoundError(Exception):
    pass

# ✅ Correct: Inherits from NotFoundError gives 404
class UserNotFoundError(NotFoundError):
    pass
```

**Solution**: Ensure domain exceptions inherit from the appropriate base class.

#### Issue: Error Code Always Appears

**Problem**: Error code appears in response even when you don't want it

**Cause**: Default behavior includes class name as error code

```python
# ❌ Problem: Always includes "UserNotFoundError:" prefix
raise UserNotFoundError("User not found")

# ✅ Solution: Explicitly set empty error code when needed
raise UserNotFoundError("User not found", error_code="")
```

#### Issue: Exception Not Caught in API Layer

**Problem**: Domain exception not being translated to HTTP response

**Cause**: API layer not catching the specific exception type

```python
# ❌ Problem: Only catches generic Exception
@router.get("/users/{id}")
async def get_user(id: int):
    try:
        user = await get_user_by_id(id)
        return user
    except Exception as exc:  # Too broad
        raise HTTPException(status_code=500, detail=str(exc))

# ✅ Solution: Catch specific domain exceptions
@router.get("/users/{id}")
async def get_user(id: int):
    try:
        user = await get_user_by_id(id)
        return user
    except UserNotFoundError as exc:
        raise translate_domain_error_to_http(exc) from exc
    except Exception as exc:
        # Fallback for truly unexpected errors
        logger.error(f"Unexpected error: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Issue: Lost Exception Context

**Problem**: Original exception information is lost

**Cause**: Not using proper exception chaining

```python
# ❌ Problem: Original exception lost
try:
    result = await some_operation()
except SpecificError:
    raise DomainError("Operation failed")  # Lost original context

# ✅ Solution: Use exception chaining
try:
    result = await some_operation()
except SpecificError as exc:
    raise DomainError("Operation failed") from exc  # Preserves original
```

#### Issue: Test Failures After Migration

**Problem**: Tests failing with new status codes or error formats

**Solution**: Update test expectations:

```python
# ❌ Old test expectations
def test_invalid_user():
    response = client.post("/users", json=invalid_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Validation error"

# ✅ Updated test expectations  
def test_invalid_user():
    response = client.post("/users", json=invalid_data)
    assert response.status_code == 400
    assert "ValidationError" in response.json()["detail"]
```

### Debugging Exception Handling

#### Enable Detailed Logging

Add logging to track exception flow:

```python
import logging

logger = logging.getLogger(__name__)

@router.post("/articles")
async def create_article(data: ArticleCreateRequest):
    try:
        article = await create_article_service(data)
        return ArticleResponse(article=article)
    except DomainError as exc:
        logger.info(f"Domain error in create_article: {type(exc).__name__}: {exc}")
        raise translate_domain_error_to_http(exc) from exc
    except Exception as exc:
        logger.error(f"Unexpected error in create_article: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
```

#### Verify Exception Translation

Test the translation function directly:

```python
from app.shared.exceptions import translate_domain_error_to_http
from app.domain.users.exceptions import UserNotFoundError

# Test exception translation
exc = UserNotFoundError("User not found")
http_exc = translate_domain_error_to_http(exc)

print(f"Status code: {http_exc.status_code}")  # Should be 404
print(f"Detail: {http_exc.detail}")           # Should include message
```

#### Check Exception Hierarchy

Verify that exceptions inherit correctly:

```python
from app.domain.users.exceptions import UserNotFoundError
from app.shared.exceptions import NotFoundError, DomainError

# Verify inheritance
assert issubclass(UserNotFoundError, NotFoundError)
assert issubclass(UserNotFoundError, DomainError)

# Test instance checks
exc = UserNotFoundError("Test")
assert isinstance(exc, NotFoundError)
assert isinstance(exc, DomainError)
```

### Performance Monitoring

Monitor exception rates to identify issues:

```python
import time
from functools import wraps

def monitor_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            return await func(*args, **kwargs)
        except DomainError as exc:
            duration = time.time() - start_time
            logger.info(f"Domain exception in {func.__name__}: {type(exc).__name__} ({duration:.3f}s)")
            raise
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(f"Unexpected exception in {func.__name__}: {type(exc).__name__} ({duration:.3f}s)")
            raise
    return wrapper

# Usage
@monitor_exceptions
async def create_user(user_data: UserCreateRequest) -> User:
    # Implementation...
```

## Related Documentation

- **[README.md](README.md)** - Main project documentation and setup guide
- **[COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)** - Git commit standards and conventions
- **[Exception Handling Overview](README.md#exception-handling)** - Quick reference in README.md
- **[Architecture Documentation](README.md#architecture)** - System architecture overview

---

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**
