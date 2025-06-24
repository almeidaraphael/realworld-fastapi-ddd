"""
Test event bus for testing event-driven functionality.
This module should only be used in tests.
"""

from typing import Any

from app.events.core import DomainEvent, EventBus


class MockEventBus(EventBus):
    """
    Test-specific event bus implementation for testing event-driven functionality.

    This event bus provides additional testing capabilities like:
    - Call count tracking
    - Published event history
    - Event verification methods

    Should only be used in tests to verify event publishing and handling.

    Usage:
        test_bus = MockEventBus()

        # Your code that should publish events
        service_function()

        # Verify events were published
        assert test_bus.call_count == 1
        assert test_bus.assert_event_published(EventType, field="value")
    """

    def __init__(self) -> None:
        super().__init__()
        self.published_events: list[DomainEvent] = []
        self.call_count = 0

    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event and track it for testing.

        Args:
            event: The domain event to publish
        """
        self.published_events.append(event)
        self.call_count += 1
        super().publish(event)

    async def publish_async(self, event: DomainEvent) -> None:
        """
        Publish an event asynchronously and track it for testing.

        Args:
            event: The domain event to publish
        """
        self.published_events.append(event)
        self.call_count += 1
        await super().publish_async(event)

    def assert_event_published(self, event_type: type[DomainEvent], **kwargs: Any) -> bool:
        """
        Assert that an event of the specified type was published with matching attributes.

        Args:
            event_type: The type of event to look for
            **kwargs: Event attributes that must match

        Returns:
            True if a matching event was found, False otherwise
        """
        matching_events = [
            event
            for event in self.published_events
            if isinstance(event, event_type)
            and all(getattr(event, key, None) == value for key, value in kwargs.items())
        ]

        return len(matching_events) > 0

    def get_published_events(
        self, event_type: type[DomainEvent] | None = None
    ) -> list[DomainEvent]:
        """
        Get all published events, optionally filtered by type.

        Args:
            event_type: Optional event type to filter by

        Returns:
            List of published events
        """
        if event_type is None:
            return self.published_events.copy()
        return [event for event in self.published_events if isinstance(event, event_type)]

    def reset(self) -> None:
        """Reset the test bus state."""
        self.published_events.clear()
        self.call_count = 0
        self._subscribers.clear()
        self._async_subscribers.clear()
