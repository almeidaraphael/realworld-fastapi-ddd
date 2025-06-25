"""
System event handlers.

Re-exports all system-specific event handlers for convenient importing.
"""

from .analytics import register_analytics_handlers
from .maintenance import register_maintenance_handlers
from .moderation import register_moderation_handlers
from .security import register_security_handlers

__all__ = [
    "register_analytics_handlers",
    "register_maintenance_handlers",
    "register_moderation_handlers",
    "register_security_handlers",
]
