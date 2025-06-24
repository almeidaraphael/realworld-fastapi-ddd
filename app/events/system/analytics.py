"""
Analytics and performance-related events.
"""

from app.events.core import DomainEvent


class ArticleViewIncremented(DomainEvent):
    """
    Event published when an article is viewed.

    This event is triggered every time an article is accessed or viewed by a user.
    Handlers can use this event to track article popularity, update view counts,
    generate analytics reports, or improve content recommendations.

    Args:
        article_id: The unique identifier of the viewed article
        viewer_id: The unique identifier of the viewing user (None for anonymous users)
        ip_address: The IP address of the viewer (optional, for tracking unique views)

    Usage:
        # Authenticated user view
        shared_event_bus.publish(ArticleViewIncremented(
            article_id=123,
            viewer_id=456,
            ip_address="192.168.1.1"
        ))

        # Anonymous user view
        shared_event_bus.publish(ArticleViewIncremented(
            article_id=123,
            viewer_id=None,
            ip_address="192.168.1.1"
        ))
    """

    def __init__(
        self, article_id: int, viewer_id: int | None = None, ip_address: str | None = None
    ) -> None:
        self.article_id = article_id
        self.viewer_id = viewer_id
        self.ip_address = ip_address


class SearchPerformed(DomainEvent):
    """
    Event published when a search is performed.

    This event is triggered when users perform searches within the application.
    Handlers can use this event to track search patterns, improve search algorithms,
    log popular queries, or generate search analytics.

    Args:
        query: The search query string that was performed
        results_count: The number of results returned for the search
        user_id: The unique identifier of the searching user (None for anonymous users)

    Usage:
        shared_event_bus.publish(SearchPerformed(
            query="fastapi tutorial",
            results_count=25,
            user_id=123
        ))
    """

    def __init__(self, query: str, results_count: int, user_id: int | None = None) -> None:
        self.query = query
        self.results_count = results_count
        self.user_id = user_id


class SlowQueryDetected(DomainEvent):
    """
    Event published when a database query takes too long.

    This event is triggered when database queries exceed performance thresholds.
    Handlers can use this event to log performance issues, send alerts to
    administrators, or trigger database optimization processes.

    Args:
        query_type: The type or category of the slow query (e.g., "article_search", "user_lookup")
        duration_ms: The actual duration of the query in milliseconds
        threshold_ms: The performance threshold that was exceeded (default: 1000ms)

    Usage:
        shared_event_bus.publish(SlowQueryDetected(
            query_type="article_search",
            duration_ms=1500.5,
            threshold_ms=1000.0
        ))
    """

    def __init__(self, query_type: str, duration_ms: float, threshold_ms: float = 1000.0) -> None:
        self.query_type = query_type
        self.duration_ms = duration_ms
        self.threshold_ms = threshold_ms


class HighTrafficDetected(DomainEvent):
    """
    Event published when high traffic is detected.

    This event is triggered when specific endpoints or the application overall
    experiences unusually high traffic volumes. Handlers can use this event to
    implement rate limiting, scale resources, or send administrative alerts.

    Args:
        endpoint: The API endpoint experiencing high traffic
        requests_per_minute: The current request rate per minute
        threshold: The threshold that was exceeded (default: 100 requests/minute)

    Usage:
        shared_event_bus.publish(HighTrafficDetected(
            endpoint="/api/articles",
            requests_per_minute=250,
            threshold=100
        ))
    """

    def __init__(self, endpoint: str, requests_per_minute: int, threshold: int = 100) -> None:
        self.endpoint = endpoint
        self.requests_per_minute = requests_per_minute
        self.threshold = threshold


class UserEngagementMilestone(DomainEvent):
    """
    Event published when a user reaches engagement milestones.

    This event is triggered when users achieve significant engagement milestones
    such as creating their 10th article, receiving 100 followers, or posting
    their 50th comment. Handlers can use this event to send congratulatory
    messages, unlock features, or update user badges.

    Args:
        user_id: The unique identifier of the user reaching the milestone
        milestone_type: The type of milestone achieved
            (e.g., "articles_created", "comments_posted", "followers_gained")
        milestone_value: The numeric value of the milestone (e.g., 10, 50, 100)

    Usage:
        shared_event_bus.publish(UserEngagementMilestone(
            user_id=123,
            milestone_type="articles_created",
            milestone_value=10
        ))
    """

    def __init__(self, user_id: int, milestone_type: str, milestone_value: int) -> None:
        self.user_id = user_id
        self.milestone_type = (
            milestone_type  # "articles_created", "comments_posted", "followers_gained"
        )
        self.milestone_value = milestone_value  # 10, 50, 100, etc.
