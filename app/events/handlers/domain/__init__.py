"""
Domain event handlers.

Re-exports all domain-specific event handlers for convenient importing.
"""

from .articles import register_article_handlers
from .comments import register_comment_handlers
from .users import register_user_handlers

__all__ = [
    "register_article_handlers",
    "register_comment_handlers",
    "register_user_handlers",
]
