# @transactional() Decorator - Usage Guidelines

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

> **📖 For complete transaction management overview, see [Transaction Management in README.md](../../README.md#automatic-transaction-management)**  
> This document provides specific guidelines for using the `@transactional()` decorator in service layer functions.

## Quick Reference

### ✅ REQUIRED - Use @transactional() for:

- **Database operations** (create, update, delete, read)
- **API entry points** - Functions called directly from API layer
- **Multi-repository coordination** - Operations spanning multiple repositories
- **Event publishing** - Domain events that must be atomic with data changes
- **Read consistency** - Functions requiring transaction-level read consistency

### ❌ NOT REQUIRED - Don't use @transactional() for:

- **Helper functions** - Private functions (prefixed with `_`) called within transactions
- **Pure business logic** - Functions with no repository interactions
- **Data transformation** - Functions only manipulating in-memory objects
- **AsyncSession functions** - Functions accepting `AsyncSession` instead of `AsyncUnitOfWork`

## Usage Patterns

### Standard Pattern

```python
@transactional()
async def create_user(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    """Create a new user with transaction management."""
    repo = UserRepository(uow.session)
    # ... business logic
    return result
```

### Safe Error Handling

```python
@transactional(reraise=False, log_errors=True)
async def get_user_by_email(uow: AsyncUnitOfWork, email: str) -> UserRead | None:
    """Returns None on error instead of raising exceptions."""
    repo = UserRepository(uow.session)
    # ... business logic
    return result
```

### Helper Function (No Decorator)

```python
# NO @transactional() - called within transactional context
async def _batch_fetch_authors(session: AsyncSession, articles: list[Article]) -> dict[int, User]:
    """Helper function that works with existing session."""
    # ... helper logic using session directly
```

## Current Implementation Status

All service layer functions are properly decorated according to these guidelines:

### ✅ Decorated Functions

**Users Service** - 6 functions:
- `authenticate_user_from_token()`, `create_user()`, `authenticate_user()`, `update_user()`, etc.

**Articles Service** - 8 functions:
- `list_articles()`, `create_article()`, `update_article()`, `delete_article()`, etc.

**Comments Service** - 3 functions:
- `add_comment_to_article()`, `get_comments_from_article()`, `delete_comment()`

**Tags Service** - 1 function:
- `get_tags()`

**Profiles Service** - 3 functions:
- `get_profile()`, `follow_user()`, `unfollow_user()`

### ✅ Correctly Not Decorated (Helpers)

- `_batch_fetch_authors()`, `_build_favorited_map()` - Use `AsyncSession` directly
- `_build_comment_response()`, `_build_article_response()` - Pure data transformation
- `ArticleResponseBuilder` methods - Utility functions within existing transactions

## Function Signature Requirements

### With @transactional()
```python
@transactional()
async def my_service_function(uow: AsyncUnitOfWork, other_params...) -> ReturnType:
    repo = MyRepository(uow.session)
    # ... business logic
```

### Without @transactional() (Helpers)
```python
async def _my_helper_function(session: AsyncSession, other_params...) -> ReturnType:
    # ... helper logic using session directly
```

## Event Publishing

Events are published within transactional boundaries for consistency:

```python
@transactional()
async def create_user(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    # ... create user logic
    
    # Event publishing within transaction
    shared_event_bus.publish(UserRegistered(user_id=user.id, username=user.username))
    
    return result
```

## Validation

To verify proper `@transactional()` usage:

1. **Run tests**: `python -m pytest tests/ --tb=short -v`
2. **Check function signatures**: All functions with `AsyncUnitOfWork` parameter should be decorated
3. **Review helper functions**: Functions with `AsyncSession` parameter should NOT be decorated
