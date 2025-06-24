"""
Centralized event handler registration for the application.
"""

import logging

from app.events import shared_event_bus

logger = logging.getLogger(__name__)


def register_all_event_handlers() -> None:
    """
    Register all domain event handlers with the event bus.

    This function imports all event handler modules to trigger their registration
    with the shared event bus. This ensures that all handlers are properly
    subscribed to their respective events when the application starts.

    The registration includes:
    - Article domain event handlers (sync and async)
    - User domain event handlers (including security handlers)
    - Cross-domain event handlers for inter-domain communication
    - Analytics event handlers for metrics and monitoring

    This function is typically called during application startup to ensure
    all event handlers are ready to process events.

    Usage:
        # During application startup
        register_all_event_handlers()
    """
    # Use the new centralized handler registration
    from app.events.handlers import register_all_handlers

    register_all_handlers()

    logger.info("All event handlers (domain, system, and cross-domain) registered successfully")


def get_registered_handlers() -> dict:
    """
    Get a summary of all registered event handlers for debugging.

    This function provides diagnostic information about which event types
    have handlers registered and how many handlers are subscribed to each
    event type. Useful for debugging event-driven workflows and ensuring
    all expected handlers are properly registered.

    Returns:
        Dictionary mapping event type names to the number of registered handlers

    Usage:
        handlers = get_registered_handlers()
        print(f"ArticleCreated has {handlers.get('ArticleCreated', 0)} handlers")
    """
    handlers_summary = {}
    for event_type, handlers in shared_event_bus._subscribers.items():
        handlers_summary[event_type.__name__] = len(handlers)
    return handlers_summary
