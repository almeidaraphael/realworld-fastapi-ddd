# Service Layer Transaction Management - Advanced Guide

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

> **📖 For quick overview and common usage patterns, see [Transaction Management in README.md](../../README.md#automatic-transaction-management)**  
> **⚡ For @transactional() decorator guidelines, see [TRANSACTION_DECORATOR_GUIDELINES.md](../guides/TRANSACTION_DECORATOR_GUIDELINES.md)**  
> This document provides advanced transaction management patterns, detailed implementation examples, and migration guidance.

## Overview

This detailed guide covers advanced transaction management patterns and implementation details. For basic usage, refer to the main [README.md](../../README.md#automatic-transaction-management) documentation.

The transaction management system provides several key improvements:

1. **Consistent Error Handling**: All service methods now have uniform transaction rollback behavior
2. **Automatic UoW Injection**: Unit of Work is automatically provided to decorated functions
3. **Flexible Configuration**: Control over error handling and logging behavior
4. **Type Safety**: Proper type annotations and validation
5. **Testing Support**: Easy mocking and testing of transactional operations

## Migration Guide

### Before (Original Pattern)

```python
async def create_user(user_req: NewUserRequest) -> UserRead:
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        # ... business logic
        return UserRead.model_validate(user.__dict__)
```

### After (Enhanced Pattern)

```python
@transactional()
async def create_user_enhanced(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    repo = UserRepository(uow.session)
    # ... business logic
    return UserRead.model_validate(user.__dict__)
```

## Available Transaction Management Options

### 1. @transactional() Decorator

**Use Case**: Standard service functions that need transaction management

```python
from app.shared.transaction import transactional

@transactional()
async def create_resource(uow: AsyncUnitOfWork, data: CreateData) -> Resource:
    # UoW is automatically injected as first parameter
    # Transaction is automatically committed on success
    # Transaction is automatically rolled back on exception
    pass

@transactional(reraise=False, log_errors=True)
async def safe_operation(uow: AsyncUnitOfWork) -> Resource | None:
    # Returns None on error instead of raising exception
    pass
```

### 2. TransactionalService Base Class

**Use Case**: Service classes that need multiple transactional methods

```python
from app.shared.transaction import TransactionalService, transactional

class UserService(TransactionalService):
    
    @transactional()
    async def create_user(self, uow: AsyncUnitOfWork, data: UserCreate) -> UserRead:
        # Method with automatic transaction management
        pass
    
    async def safe_get_user(self, user_id: int) -> UserRead | None:
        # Using inherited _execute_in_transaction method
        async def operation(uow: AsyncUnitOfWork) -> UserRead:
            repo = UserRepository(uow.session)
            user = await repo.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            return UserRead.model_validate(user.__dict__)
        
        return await self._execute_in_transaction(
            operation, reraise=False, log_errors=True
        )
    
    async def manual_transaction_example(self) -> UserRead:
        # Manual transaction control
        async with self.transaction() as uow:
            repo = UserRepository(uow.session)
            # ... operations
            return result
```

### 3. Context Manager Approach

**Use Case**: Explicit transaction control in complex scenarios

```python
from app.shared.transaction import transactional_context

async def complex_operation():
    async with transactional_context() as uow:
        # Multiple repository operations
        user_repo = UserRepository(uow.session)
        article_repo = ArticleRepository(uow.session)
        # ... operations
```

### 4. Bulk Operations

**Use Case**: Multiple related operations that must succeed or fail together

```python
from app.shared.transaction import BulkTransactionManager

async def bulk_create_users(users_data: list[UserCreate]) -> list[UserRead]:
    manager = BulkTransactionManager()
    
    for user_data in users_data:
        async def create_user_op(uow: AsyncUnitOfWork) -> UserRead:
            repo = UserRepository(uow.session)
            # ... create user logic
            return user_read
        
        manager.add_operation(create_user_op)
    
    # All operations execute in a single transaction
    return await manager.execute_all()
```

## Implementation Steps

### Step 1: Update Service Functions

Replace manual UoW management with `@transactional()` decorator:

```python
# Before
async def create_user(user_req: NewUserRequest) -> UserRead:
    async with AsyncUnitOfWork() as uow:
        repo = UserRepository(uow.session)
        # ... logic
        return result

# After  
@transactional()
async def create_user(uow: AsyncUnitOfWork, user_req: NewUserRequest) -> UserRead:
    repo = UserRepository(uow.session)
    # ... logic
    return result
```

### Step 2: Update API Layer

Update API endpoints to call the new service signatures:

```python
# Before
@router.post("/users", response_model=UserResponse)
async def create_user_endpoint(user_req: NewUserRequest):
    user = await create_user(user_req)  # No uow parameter
    return UserResponse(user=user)

# After
@router.post("/users", response_model=UserResponse)
async def create_user_endpoint(user_req: NewUserRequest):
    user = await create_user(user_req)  # UoW injected by decorator
    return UserResponse(user=user)
```

### Step 3: Convert Service Classes

For existing service classes, inherit from `TransactionalService`:

```python
# Before
class CommentService:
    def __init__(self, uow: AsyncUnitOfWork):
        self.uow = uow

# After
class CommentService(TransactionalService):
    # No need to store UoW, it's injected per method
    pass
```

### Step 4: Update Tests

Modify tests to work with the new transaction management:

```python
# Integration tests can use the service methods directly
@pytest.mark.asyncio
async def test_create_user():
    user_data = UserCreate(username="test", email="test@example.com", password="secret")
    result = await create_user(user_data)  # UoW managed automatically
    assert result.username == "test"

# Unit tests can mock the UoW
@pytest.mark.asyncio
async def test_create_user_unit(mocker):
    mock_uow = mocker.AsyncMock()
    mock_repo = mocker.Mock()
    
    # Test the service logic directly
    with mocker.patch('app.shared.transaction.AsyncUnitOfWork') as mock_uow_class:
        mock_uow_class.return_value.__aenter__.return_value = mock_uow
        result = await create_user(user_data)
```

## Error Handling Strategies

### 1. Standard Error Propagation (Default)

```python
@transactional()  # reraise=True by default
async def create_user(uow: AsyncUnitOfWork, data: UserCreate) -> UserRead:
    # Exceptions are automatically caught, logged, and reraised
    # Transaction is rolled back on any exception
    pass
```

### 2. Safe Operations (Return None on Error)

```python
@transactional(reraise=False, log_errors=True)
async def safe_get_user(uow: AsyncUnitOfWork, user_id: int) -> UserRead | None:
    # Returns None on any error instead of raising
    # Useful for optional operations
    pass
```

### 3. Custom Error Handling

```python
@transactional(reraise=True, log_errors=False)
async def operation_with_custom_logging(uow: AsyncUnitOfWork, data: Any) -> Result:
    # Handle logging manually for custom behavior
    pass
```

## Best Practices

### 1. Function Signatures

Always put the `AsyncUnitOfWork` parameter first after `self` (for methods):

```python
@transactional()
async def service_method(self, uow: AsyncUnitOfWork, param1: str, param2: int) -> Result:
    pass
```

### 2. Repository Instantiation

Create repositories inside the service method using the injected UoW:

```python
@transactional()
async def create_resource(uow: AsyncUnitOfWork, data: CreateData) -> Resource:
    repo = ResourceRepository(uow.session)  # Use injected UoW
    # ... business logic
```

### 3. Event Publishing

Publish events within the transaction for consistency:

```python
@transactional()
async def create_user(uow: AsyncUnitOfWork, data: UserCreate) -> UserRead:
    # ... create user
    
    # Publish event within transaction
    shared_event_bus.publish(UserCreated(user_id=user.id))
    
    return user_read
```

### 4. Nested Operations

For operations that call other transactional services, consider the context:

```python
@transactional()
async def complex_operation(uow: AsyncUnitOfWork, data: ComplexData) -> Result:
    # This service method runs in its own transaction
    # If it calls other @transactional methods, they should use the same UoW
    # Consider using manual transaction control for such cases
    pass
```

## Migration Checklist

- [ ] Install and import the transaction management utilities
- [ ] Update service functions to use `@transactional()` decorator
- [ ] Update service classes to inherit from `TransactionalService`
- [ ] Modify function signatures to accept `AsyncUnitOfWork` as first parameter
- [ ] Update API endpoints if needed (usually no changes required)
- [ ] Update tests to work with new transaction management
- [ ] Validate that all transactions are properly managed
- [ ] Run integration tests to ensure everything works correctly
- [ ] Monitor logs for transaction-related errors or warnings

## Common Pitfalls

1. **Forgetting to Update Function Signatures**: The UoW parameter must be first after self
2. **Nested Transactions**: Be careful when calling transactional methods from within other transactions
3. **Testing**: Mock the UoW correctly in unit tests
4. **Event Publishing**: Ensure events are published within the transaction scope
5. **Repository Creation**: Always create repositories with the injected UoW session

## Performance Considerations

The new transaction management system adds minimal overhead:

- **Decorator overhead**: Negligible function call wrapping
- **Logging**: Can be disabled per method if needed
- **Error handling**: Consistent exception handling reduces debugging time
- **Connection pooling**: Proper UoW lifecycle management improves connection usage

## Monitoring and Debugging

Enable debug logging to monitor transaction behavior:

```python
import logging
logging.getLogger('app.shared.transaction').setLevel(logging.DEBUG)
```

This will log:
- Transaction start/completion
- Error information
- Operation execution details
