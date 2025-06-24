"""
Infrastructure events - event bus implementations.
"""

from .persistent_bus import PersistentEventBus

__all__ = [
    "PersistentEventBus",
]
