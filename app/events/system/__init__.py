"""
System events - cross-cutting concerns and infrastructure events.
"""

from .analytics import (
    ArticleViewIncremented,
    HighTrafficDetected,
    SearchPerformed,
    SlowQueryDetected,
    UserEngagementMilestone,
)
from .maintenance import (
    BulkOperationCompleted,
    DatabaseConstraintViolation,
    OrphanedDataDetected,
    RateLimitExceeded,
    UserDataCleanupRequested,
)
from .moderation import (
    ContentApproved,
    ContentFlagged,
    ContentRemoved,
    SpamDetected,
)
from .security import (
    SuspiciousLoginActivity,
    UserAccountLocked,
    UserLoginAttempted,
    UserPasswordChanged,
)

__all__ = [
    # Analytics events
    "ArticleViewIncremented",
    "HighTrafficDetected",
    "SearchPerformed",
    "SlowQueryDetected",
    "UserEngagementMilestone",
    # Maintenance events
    "BulkOperationCompleted",
    "DatabaseConstraintViolation",
    "OrphanedDataDetected",
    "RateLimitExceeded",
    "UserDataCleanupRequested",
    # Moderation events
    "ContentApproved",
    "ContentFlagged",
    "ContentRemoved",
    "SpamDetected",
    # Security events
    "SuspiciousLoginActivity",
    "UserAccountLocked",
    "UserLoginAttempted",
    "UserPasswordChanged",
]
