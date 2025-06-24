"""
Test for the event-driven architecture.
"""

from app.events import (
    ArticleCommentAdded,
    ArticleCreated,
    ArticleFavorited,
    UserFollowed,
)
from tests.test_event_bus import MockEventBus


def test_event_bus_subscription_and_publishing():
    """Test basic event bus functionality."""
    test_bus = MockEventBus()

    # Create a simple handler
    handled_events = []

    def test_handler(event):
        handled_events.append(event)

    # Subscribe and publish
    test_bus.subscribe(ArticleCreated, test_handler)
    event = ArticleCreated(article_id=1, author_id=2)
    test_bus.publish(event)

    # Assertions
    assert len(test_bus.published_events) == 1
    assert len(handled_events) == 1
    assert test_bus.published_events[0] == event
    assert handled_events[0] == event


def test_event_bus_filtering():
    """Test filtering events by type."""
    test_bus = MockEventBus()

    # Publish different event types
    article_event = ArticleCreated(article_id=1, author_id=2)
    comment_event = ArticleCommentAdded(article_id=1, comment_id=3, author_id=2)
    user_event = UserFollowed(follower_id=1, followee_id=2)

    test_bus.publish(article_event)
    test_bus.publish(comment_event)
    test_bus.publish(user_event)

    # Test filtering
    article_events = test_bus.get_published_events(ArticleCreated)
    comment_events = test_bus.get_published_events(ArticleCommentAdded)
    user_events = test_bus.get_published_events(UserFollowed)

    assert len(article_events) == 1
    assert len(comment_events) == 1
    assert len(user_events) == 1
    assert article_events[0] == article_event


def test_event_assertion_utility():
    """Test the event assertion utility."""
    test_bus = MockEventBus()

    # Publish an event
    event = ArticleFavorited(article_id=123, user_id=456)
    test_bus.publish(event)

    # Test assertions
    assert test_bus.assert_event_published(ArticleFavorited, article_id=123, user_id=456)
    assert test_bus.assert_event_published(ArticleFavorited, article_id=123)
    assert not test_bus.assert_event_published(ArticleFavorited, article_id=999)
    assert not test_bus.assert_event_published(ArticleCreated)
