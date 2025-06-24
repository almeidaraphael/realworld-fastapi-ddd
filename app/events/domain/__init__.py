"""
Domain events - business events from specific domains.
"""

# Article domain events
from .articles import (
    ArticleCreated,
    ArticleDeleted,
    ArticleFavorited,
    ArticleUnfavorited,
    ArticleUpdated,
)

# Comment domain events
from .comments import ArticleCommentAdded, CommentDeleted

# Tag domain events
from .tags import PopularTagDetected, TagCreated, TagRemoved, TagUsed

# User domain events
from .users import (
    UserFollowed,
    UserLoggedIn,
    UserProfileUpdated,
    UserRegistered,
    UserUnfollowed,
)

__all__ = [
    # Article events
    "ArticleCreated",
    "ArticleDeleted",
    "ArticleFavorited",
    "ArticleUnfavorited",
    "ArticleUpdated",
    # Comment events
    "ArticleCommentAdded",
    "CommentDeleted",
    # User events
    "UserFollowed",
    "UserLoggedIn",
    "UserProfileUpdated",
    "UserRegistered",
    "UserUnfollowed",
    # Tag events
    "PopularTagDetected",
    "TagCreated",
    "TagRemoved",
    "TagUsed",
]
