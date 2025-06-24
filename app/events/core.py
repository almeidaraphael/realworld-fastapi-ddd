"""
Domain event base classes and event bus for cross-domain communication.

This module provides the foundation for an event-driven architecture that enables
loose coupling between different domains and services. The event system supports
both synchronous and asynchronous event handling with built-in error isolation.

Key Components:
- DomainEvent: Base class for all domain events
- EventBus: Central event dispatcher with sync/async support
- shared_event_bus: Global singleton instance for application-wide use

Usage:
    # Define a custom event
    class UserCreated(DomainEvent):
        def __init__(self, user_id: int, email: str):
            self.user_id = user_id
            self.email = email

    # Register a handler
    def handle_user_created(event: UserCreated):
        send_welcome_email(event.email)

    shared_event_bus.subscribe(UserCreated, handle_user_created)

    # Publish an event
    shared_event_bus.publish(UserCreated(user_id=123, email="user@example.com"))

The event system provides error isolation, ensuring that handler failures
don't affect other handlers or the main application flow.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="DomainEvent")


class DomainEvent:
    """
    Base class for all domain events.

    Domain events represent significant business occurrences that other parts
    of the application might need to react to. They provide a way to decouple
    the code that triggers business logic from the code that responds to it.

    All domain events should inherit from this class and include relevant
    data as instance attributes. Events should be immutable and contain
    all necessary information for handlers to process them.

    Example:
        class OrderPlaced(DomainEvent):
            def __init__(self, order_id: int, customer_id: int, total: float):
                self.order_id = order_id
                self.customer_id = customer_id
                self.total = total
    """

    # Base class for type safety and clarity - not strictly abstract
    pass


EventHandler = Callable[[DomainEvent], None]
AsyncEventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """
    Simple synchronous event bus for domain events with error handling.

    The EventBus provides a publish-subscribe mechanism for domain events,
    supporting both synchronous and asynchronous event handlers. It includes
    built-in error isolation to ensure that failures in individual handlers
    don't affect other handlers or the main application flow.

    Features:
    - Type-safe event subscription and publishing
    - Support for both sync and async handlers
    - Error isolation with logging
    - Multiple handlers per event type
    - Automatic handler discovery based on event type

    Usage:
        bus = EventBus()

        # Subscribe handlers
        bus.subscribe(UserCreated, send_welcome_email)
        bus.subscribe_async(UserCreated, update_analytics)

        # Publish events
        bus.publish(UserCreated(user_id=123, email="user@example.com"))
        await bus.publish_async(UserCreated(user_id=123, email="user@example.com"))
    """

    def __init__(self) -> None:
        self._subscribers: dict[type[DomainEvent], list[EventHandler]] = {}
        self._async_subscribers: dict[type[DomainEvent], list[AsyncEventHandler]] = {}

    def subscribe(self, event_type: type[T], handler: Callable[[T], None]) -> None:
        """
        Subscribe a synchronous handler to an event type.

        Args:
            event_type: The class of events this handler should receive
            handler: The function to call when events of this type are published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)  # type: ignore

    def subscribe_async(self, event_type: type[T], handler: Callable[[T], Awaitable[None]]) -> None:
        """
        Subscribe an asynchronous handler to an event type.

        Args:
            event_type: The class of events this handler should receive
            handler: The async function to call when events of this type are published
        """
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        self._async_subscribers[event_type].append(handler)  # type: ignore

    def publish(self, event: DomainEvent) -> None:
        """
        Publish event to all synchronous handlers with error isolation.

        Each handler is called in sequence. If a handler raises an exception,
        it is logged but does not prevent other handlers from executing.

        Args:
            event: The domain event to publish to all registered handlers
        """
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Event handler failed for {event_type.__name__}: {e}")

    async def publish_async(self, event: DomainEvent) -> None:
        """
        Publish event to all asynchronous handlers with error isolation.

        Each async handler is awaited in sequence. If a handler raises an exception,
        it is logged but does not prevent other handlers from executing.

        Args:
            event: The domain event to publish to all registered async handlers
        """
        for event_type, handlers in self._async_subscribers.items():
            if isinstance(event, event_type):
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Async event handler failed for {event_type.__name__}: {e}")


# Singleton event bus instance for the app
shared_event_bus = EventBus()
