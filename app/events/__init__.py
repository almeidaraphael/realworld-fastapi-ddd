"""
Event-driven architecture for the FastAPI RealWorld demo application.

This package provides a comprehensive event system with:
- Domain events for business logic
- System events for cross-cutting concerns
- Infrastructure for event buses and testing

Quick Start:
    from app.events import shared_event_bus, UserRegistered

    # Publish an event
    shared_event_bus.publish(UserRegistered(
        user_id=123,
        username="johndoe",
        email="john@example.com"
    ))

Organization:
    - core: Base classes and main event bus
    - domain: Business domain events (articles, users, comments, tags)
    - system: Cross-cutting events (analytics, security, moderation, maintenance)
    - infrastructure: Event bus implementations and testing utilities
"""

# Core event system
from .core import DomainEvent, EventBus, shared_event_bus

# Domain events (business logic)
from .domain import *  # noqa: F403, F401

# Infrastructure
from .infrastructure import PersistentEventBus

# System events (cross-cutting concerns)
from .system import *  # noqa: F403, F401

__all__ = [
    # Core
    "DomainEvent",
    "EventBus",
    "shared_event_bus",
    # Infrastructure
    "PersistentEventBus",
    # All domain and system events are exported via star imports
]
