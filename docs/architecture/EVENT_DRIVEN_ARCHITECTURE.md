# Event-Driven Architecture

> 📖 **[← Back to README](../../README.md)** | **[📋 Documentation Index](../README.md)**

The FastAPI RealWorld Demo implements a comprehensive event-driven architecture that enables loose coupling between domains and provides extensibility for cross-cutting concerns.

## 🎯 Overview

The event system provides:
- **Loose Coupling**: Domains don't need direct references to each other
- **Extensibility**: Add new features without modifying existing code  
- **Scalability**: Async event processing for better performance
- **Audit Trail**: All business changes are automatically tracked
- **Testing**: Components can be tested in isolation
- **Observability**: Built-in tracking of system behavior

## 📁 Event Categories

The system organizes events into clear categories:

- **Domain Events** (`app/events/domain/`): Core business events (user registration, article creation, etc.)
- **System Events** (`app/events/system/`): Cross-cutting concerns (analytics, security, maintenance, moderation)
- **Infrastructure Events**: Event bus implementations and persistence

## 🔄 Core Patterns

### Publishing Events

Events are published from the service layer to maintain clean separation of concerns:

```python
from app.events import shared_event_bus
from app.events.domain import UserRegistered, ArticleCreated

# Synchronous event publishing
@transactional()
async def create_user(uow: AsyncUnitOfWork, user_data: UserCreate) -> User:
    # Business logic
    user = await user_service.create(user_data)
    
    # Publish domain event
    shared_event_bus.publish(UserRegistered(
        user_id=user.id,
        username=user.username,
        email=user.email
    ))
    
    return user

# Asynchronous event publishing for long-running operations
await shared_event_bus.publish_async(ArticleCreated(
    article_id=article.id,
    author_id=article.author_id,
    title=article.title,
    slug=article.slug
))
```

### Event Handler Patterns

```python
from app.events import shared_event_bus
from app.events.domain import UserRegistered, ArticleCreated

# Simple synchronous handler
def send_welcome_email(event: UserRegistered) -> None:
    """Send welcome email to new users."""
    email_service.send_welcome_email(event.email, event.username)

# Asynchronous handler for I/O operations
async def update_search_index(event: ArticleCreated) -> None:
    """Update search index when articles are created."""
    await search_service.index_article(
        article_id=event.article_id,
        title=event.title,
        slug=event.slug
    )

# Register handlers during application startup
shared_event_bus.subscribe(UserRegistered, send_welcome_email)
shared_event_bus.subscribe_async(ArticleCreated, update_search_index)
```

### Cross-Domain Event Handling

Events enable loose coupling between domains:

```python
# Multiple handlers for the same event from different domains
shared_event_bus.subscribe(UserRegistered, send_welcome_email)      # Email domain
shared_event_bus.subscribe(UserRegistered, create_user_profile)     # Profile domain  
shared_event_bus.subscribe(UserRegistered, initialize_analytics)    # Analytics domain

# Conditional event handling
def handle_milestone_articles(event: ArticleCreated) -> None:
    if event.article_id % 100 == 0:  # Every 100th article
        notify_admin_milestone(event.article_id)

# Error-resistant handlers
def robust_notification_handler(event: UserRegistered) -> None:
    try:
        external_service.notify_user_created(event.user_id)
    except Exception as exc:
        logger.error(f"Failed to notify external service: {exc}")
        # Event system continues with other handlers
```

## 🧪 Testing Events

```python
from tests.test_event_bus import MockEventBus
from app.events.domain import UserRegistered

@pytest.mark.asyncio
async def test_user_registration_publishes_event():
    """Test that user registration publishes the correct event."""
    mock_bus = MockEventBus()
    
    # Replace real event bus with mock
    with mock.patch('app.service_layer.users.shared_event_bus', mock_bus):
        user = await create_user(user_data)
    
    # Verify event was published
    assert mock_bus.call_count == 1
    assert mock_bus.assert_event_published(
        UserRegistered,
        user_id=user.id,
        username=user.username,
        email=user.email
    )
```

## ⚙️ Event Configuration

Events are automatically registered at application startup:

```python
# app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    register_all_event_handlers()  # Registers domain, system, and cross-domain handlers
    yield
    # Shutdown (graceful cleanup)
```

## 📋 Available Events Reference

### Domain Events (`app/events/domain/`)

#### User Events
- `UserRegistered` - User account creation
- `UserLoggedIn` - User authentication 
- `UserProfileUpdated` - Profile changes
- `UserFollowed` / `UserUnfollowed` - Social relationships

#### Article Events
- `ArticleCreated` / `ArticleUpdated` / `ArticleDeleted` - Article lifecycle
- `ArticleFavorited` / `ArticleUnfavorited` - User interactions

#### Comment Events
- `ArticleCommentAdded` / `CommentDeleted` - Comment lifecycle

#### Tag Events
- `TagCreated` / `TagUsed` / `TagRemoved` - Tag management
- `PopularTagDetected` - Analytics trigger

### System Events (`app/events/system/`)

#### Analytics Events
- `ArticleViewIncremented` - Page view tracking
- `SearchPerformed` - Search analytics
- `SlowQueryDetected` - Performance monitoring
- `HighTrafficDetected` - Traffic spikes
- `UserEngagementMilestone` - User activity milestones

#### Security Events
- `UserLoginAttempted` - Login monitoring
- `UserPasswordChanged` - Security changes
- `UserAccountLocked` - Account security
- `SuspiciousLoginActivity` - Threat detection

#### Moderation Events
- `ContentFlagged` / `ContentApproved` / `ContentRemoved` - Content moderation
- `SpamDetected` - Automated spam detection

#### Maintenance Events
- `UserDataCleanupRequested` - Data lifecycle
- `OrphanedDataDetected` - Data integrity
- `DatabaseConstraintViolation` - System alerts
- `BulkOperationCompleted` - Batch operations
- `RateLimitExceeded` - Rate limiting

## 🎛️ Event Types & Usage Patterns

### Domain Events
**Purpose**: Record significant business events within a single domain
**When to use**: User registration, article creation, comment addition
**Handling**: Usually synchronous, immediate business rule validation

### System Events  
**Purpose**: Handle cross-cutting concerns and system-wide operations
**When to use**: Analytics, monitoring, cleanup, security alerts
**Handling**: Often asynchronous, may involve external services

### Cross-Domain Events
**Purpose**: Coordinate between different business domains
**When to use**: User follows affecting recommendations, article creation affecting search
**Handling**: Mixed synchronous/asynchronous based on requirements

## 🔍 Event Architecture Benefits

1. **Loose Coupling**: Domains operate independently without tight dependencies
2. **Extensibility**: New features can subscribe to existing events without code changes
3. **Scalability**: Async processing prevents blocking operations
4. **Audit Trail**: Comprehensive logging of all business activities
5. **Testing**: Isolated testing of individual components and workflows
6. **Observability**: Built-in monitoring and debugging capabilities
7. **Performance**: Non-blocking event processing for better responsiveness

## 🚀 Best Practices

### Event Design
- **Immutable Events**: Events should never change after creation
- **Rich Information**: Include all necessary data to avoid additional queries
- **Domain-Specific**: Events should be meaningful within their business domain
- **Backwards Compatible**: Consider event schema evolution

### Handler Design
- **Idempotent Operations**: Handlers should be safe to run multiple times
- **Error Handling**: Graceful degradation when handlers fail
- **Performance**: Keep handlers lightweight, delegate heavy work to background tasks
- **Testing**: All handlers should have comprehensive test coverage

### Event Bus Usage
- **Service Layer Publishing**: Only service layer should publish domain events
- **Startup Registration**: Register all handlers during application initialization
- **Graceful Shutdown**: Ensure all events are processed during shutdown
- **Monitoring**: Track event publishing and handler execution metrics

## 🔗 Related Documentation

- **[Domain-Driven Design](DOMAIN_DRIVEN_DESIGN.md)** - Overall architecture patterns
- **[Transaction Management](TRANSACTION_MANAGEMENT.md)** - Event publishing within transactions
- **[Testing Guide](../guides/TESTING.md)** - Testing event-driven components
- **[Development Workflow](../development/DEVELOPMENT_WORKFLOW.md)** - Working with events in development

---

> **Complete event definitions and handlers are documented in the code via docstrings**
