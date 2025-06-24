"""
Event handlers package.

Centralized location for all event handlers, organized by domain and system concerns.
Provides convenient registration functions for all event handlers.
"""

from .cross_domain import register_cross_domain_handlers
from .domain import register_article_handlers, register_comment_handlers, register_user_handlers
from .system import register_analytics_handlers, register_security_handlers

__all__ = [
    # Domain handlers
    "register_article_handlers",
    "register_comment_handlers",
    "register_user_handlers",
    # System handlers
    "register_analytics_handlers",
    "register_security_handlers",
    # Cross-domain handlers
    "register_cross_domain_handlers",
]


def register_all_handlers() -> None:
    """
    Register all event handlers in the application.

    This function should be called during application startup to ensure
    all event handlers are properly subscribed to their respective events.

    Usage:
        from app.events.handlers import register_all_handlers

        # During application startup
        register_all_handlers()
    """
    # Register domain handlers
    register_article_handlers()
    register_comment_handlers()
    register_user_handlers()

    # Register system handlers
    register_analytics_handlers()
    register_security_handlers()

    # Register cross-domain handlers
    register_cross_domain_handlers()
