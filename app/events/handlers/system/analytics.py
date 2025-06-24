"""
Event handlers for analytics and performance events.
Handles system metrics, user analytics, and performance monitoring.
"""

import logging

from app.events import (
    ArticleViewIncremented,
    HighTrafficDetected,
    SearchPerformed,
    SlowQueryDetected,
    UserEngagementMilestone,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


def handle_article_view(event: ArticleViewIncremented) -> None:
    """Handle article view events for analytics."""
    logger.debug(f"Article {event.article_id} viewed by user {event.viewer_id or 'anonymous'}")
    # Could update view count in cache, trigger recommendation updates


def handle_search_performed(event: SearchPerformed) -> None:
    """Handle search events for analytics."""
    logger.info(f"Search '{event.query}' returned {event.results_count} results")
    # Could update search analytics, improve search suggestions


def handle_slow_query(event: SlowQueryDetected) -> None:
    """Handle slow query detection for performance monitoring."""
    logger.warning(
        f"Slow {event.query_type} query detected: {event.duration_ms}ms "
        f"(threshold: {event.threshold_ms}ms)"
    )
    # Could trigger alerts, add to performance dashboard


def handle_high_traffic(event: HighTrafficDetected) -> None:
    """Handle high traffic detection."""
    logger.warning(
        f"High traffic detected on {event.endpoint}: "
        f"{event.requests_per_minute} req/min (threshold: {event.threshold})"
    )
    # Could trigger auto-scaling, rate limiting, alerts


def handle_engagement_milestone(event: UserEngagementMilestone) -> None:
    """Handle user engagement milestones."""
    logger.info(
        f"User {event.user_id} reached milestone: {event.milestone_value} {event.milestone_type}"
    )
    # Could trigger congratulations email, badges, notifications


def register_analytics_handlers() -> None:
    """Register all analytics event handlers."""
    shared_event_bus.subscribe(ArticleViewIncremented, handle_article_view)
    shared_event_bus.subscribe(SearchPerformed, handle_search_performed)
    shared_event_bus.subscribe(SlowQueryDetected, handle_slow_query)
    shared_event_bus.subscribe(HighTrafficDetected, handle_high_traffic)
    shared_event_bus.subscribe(UserEngagementMilestone, handle_engagement_milestone)
