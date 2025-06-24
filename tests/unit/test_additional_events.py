"""
Test for additional domain events and cross-domain handlers.
"""

from app.events import (
    ArticleCreated,
    ArticleUpdated,
    ArticleViewIncremented,
    CommentDeleted,
    ContentFlagged,
    DomainEvent,
    RateLimitExceeded,
    SearchPerformed,
    UserLoggedIn,
    UserLoginAttempted,
    UserPasswordChanged,
    UserProfileUpdated,
    UserRegistered,
)
from tests.test_event_bus import MockEventBus


def test_user_registration_event():
    """Test UserRegistered event publishing and handling."""
    test_bus = MockEventBus()

    # Create handler
    handled_events = []

    def test_handler(event):
        handled_events.append(event)

    # Subscribe and publish
    test_bus.subscribe(UserRegistered, test_handler)
    event = UserRegistered(user_id=1, username="testuser", email="test@example.com")
    test_bus.publish(event)

    # Assertions
    assert len(test_bus.published_events) == 1
    assert len(handled_events) == 1
    assert test_bus.published_events[0] == event
    assert test_bus.assert_event_published(UserRegistered, user_id=1, username="testuser")


def test_user_login_event():
    """Test UserLoggedIn event publishing and handling."""
    test_bus = MockEventBus()

    event = UserLoggedIn(user_id=2, username="loginuser", email="login@example.com")
    test_bus.publish(event)

    assert test_bus.assert_event_published(UserLoggedIn, user_id=2)
    assert test_bus.assert_event_published(UserLoggedIn, username="loginuser")


def test_user_profile_updated_event():
    """Test UserProfileUpdated event with updated fields tracking."""
    test_bus = MockEventBus()

    event = UserProfileUpdated(user_id=3, username="updateuser", updated_fields=["bio", "image"])
    test_bus.publish(event)

    assert test_bus.assert_event_published(UserProfileUpdated, user_id=3)
    published_event = test_bus.get_published_events(UserProfileUpdated)[0]
    assert published_event.updated_fields == ["bio", "image"]


def test_article_updated_event():
    """Test ArticleUpdated event with field tracking."""
    test_bus = MockEventBus()

    event = ArticleUpdated(article_id=10, author_id=5, updated_fields=["title", "body"])
    test_bus.publish(event)

    assert test_bus.assert_event_published(ArticleUpdated, article_id=10, author_id=5)
    published_event = test_bus.get_published_events(ArticleUpdated)[0]
    assert published_event.updated_fields == ["title", "body"]


def test_comment_deleted_event():
    """Test CommentDeleted event publishing."""
    test_bus = MockEventBus()

    event = CommentDeleted(comment_id=15, article_id=20, author_id=25)
    test_bus.publish(event)

    assert test_bus.assert_event_published(CommentDeleted, comment_id=15)
    assert test_bus.assert_event_published(CommentDeleted, article_id=20, author_id=25)


def test_cross_domain_event_handling():
    """Test that events can be handled by multiple domains."""
    test_bus = MockEventBus()

    # Multiple handlers for the same event
    domain1_handled = []
    domain2_handled = []

    def domain1_handler(event):
        domain1_handled.append(event)

    def domain2_handler(event):
        domain2_handled.append(event)

    # Subscribe both handlers
    test_bus.subscribe(UserRegistered, domain1_handler)
    test_bus.subscribe(UserRegistered, domain2_handler)

    # Publish event
    event = UserRegistered(user_id=100, username="cross", email="cross@example.com")
    test_bus.publish(event)

    # Both domains should handle the event
    assert len(domain1_handled) == 1
    assert len(domain2_handled) == 1
    assert domain1_handled[0] == event
    assert domain2_handled[0] == event


class TestSecurityEvents:
    """Test security-related events."""

    def test_user_login_attempted_event_creation(self):
        """
        GIVEN login attempt data
        WHEN creating a UserLoginAttempted event
        THEN the event should contain the correct information
        """
        event = UserLoginAttempted(email="test@example.com", success=True, ip_address="192.168.1.1")

        assert event.email == "test@example.com"
        assert event.success is True
        assert event.ip_address == "192.168.1.1"

    def test_password_changed_event_creation(self):
        """
        GIVEN user password change data
        WHEN creating a UserPasswordChanged event
        THEN the event should contain the correct information
        """
        event = UserPasswordChanged(user_id=123, username="testuser")

        assert event.user_id == 123
        assert event.username == "testuser"

    def test_security_event_publishing(self):
        """
        GIVEN a test event bus
        WHEN publishing security events
        THEN the events should be properly handled
        """
        test_bus = MockEventBus()

        # Test login attempt events
        login_event = UserLoginAttempted(email="test@example.com", success=False)
        test_bus.publish(login_event)

        assert test_bus.assert_event_published(
            UserLoginAttempted, email="test@example.com", success=False
        )

        # Test password change events
        pwd_event = UserPasswordChanged(user_id=456, username="secureuser")
        test_bus.publish(pwd_event)

        assert test_bus.assert_event_published(UserPasswordChanged, user_id=456)


class TestAnalyticsEvents:
    """Test analytics-related events."""

    def test_article_view_incremented_event_creation(self):
        """
        GIVEN article view data
        WHEN creating an ArticleViewIncremented event
        THEN the event should contain the correct information
        """
        event = ArticleViewIncremented(article_id=456, viewer_id=123, ip_address="192.168.1.1")

        assert event.article_id == 456
        assert event.viewer_id == 123
        assert event.ip_address == "192.168.1.1"

    def test_search_performed_event_creation(self):
        """
        GIVEN search data
        WHEN creating a SearchPerformed event
        THEN the event should contain the correct information
        """
        event = SearchPerformed(query="test query", results_count=42, user_id=123)

        assert event.query == "test query"
        assert event.results_count == 42
        assert event.user_id == 123

    def test_analytics_event_publishing(self):
        """
        GIVEN a test event bus
        WHEN publishing analytics events
        THEN the events should be properly handled
        """
        test_bus = MockEventBus()

        # Test article view events
        view_event = ArticleViewIncremented(article_id=789, viewer_id=None)
        test_bus.publish(view_event)

        assert test_bus.assert_event_published(ArticleViewIncremented, article_id=789)

        # Test search events
        search_event = SearchPerformed(query="python", results_count=15, user_id=100)
        test_bus.publish(search_event)

        assert test_bus.assert_event_published(SearchPerformed, query="python", results_count=15)


class TestModerationEvents:
    """Test content moderation events."""

    def test_content_flagged_event_creation(self):
        """
        GIVEN flagged content data
        WHEN creating a ContentFlagged event
        THEN the event should contain the correct information
        """
        event = ContentFlagged(
            content_type="article", content_id=789, reason="inappropriate content", reporter_id=123
        )

        assert event.content_type == "article"
        assert event.content_id == 789
        assert event.reason == "inappropriate content"
        assert event.reporter_id == 123

    def test_moderation_event_publishing(self):
        """
        GIVEN a test event bus
        WHEN publishing moderation events
        THEN the events should be properly handled
        """
        test_bus = MockEventBus()

        flag_event = ContentFlagged(
            content_type="comment", content_id=555, reason="spam", reporter_id=999
        )
        test_bus.publish(flag_event)

        assert test_bus.assert_event_published(
            ContentFlagged, content_type="comment", reason="spam"
        )


class TestSystemEvents:
    """Test system-level events."""

    def test_rate_limit_exceeded_event_creation(self):
        """
        GIVEN rate limiting data
        WHEN creating a RateLimitExceeded event
        THEN the event should contain the correct information
        """
        event = RateLimitExceeded(
            user_id=123, ip_address="192.168.1.1", operation="create_article", limit_type="hourly"
        )

        assert event.user_id == 123
        assert event.ip_address == "192.168.1.1"
        assert event.operation == "create_article"
        assert event.limit_type == "hourly"

    def test_system_event_publishing(self):
        """
        GIVEN a test event bus
        WHEN publishing system events
        THEN the events should be properly handled
        """
        test_bus = MockEventBus()

        rate_event = RateLimitExceeded(
            user_id=777, ip_address="10.0.0.1", operation="follow_user", limit_type="daily"
        )
        test_bus.publish(rate_event)

        assert test_bus.assert_event_published(RateLimitExceeded, operation="follow_user")


class TestEventIntegration:
    """Test integration of new events with existing system."""

    def test_event_publishing_does_not_break_existing_flow(self):
        """
        GIVEN the enhanced event system
        WHEN publishing both old and new events
        THEN both should work without interference
        """
        test_bus = MockEventBus()

        # Test that we can publish new events without breaking existing ones

        # Publish existing events
        test_bus.publish(ArticleCreated(article_id=1, author_id=1))
        test_bus.publish(UserRegistered(user_id=1, username="test", email="test@example.com"))

        # Publish new events
        test_bus.publish(UserLoginAttempted(email="test@example.com", success=True))
        test_bus.publish(ArticleViewIncremented(article_id=1, viewer_id=1))

        # Should have published all events
        assert len(test_bus.published_events) == 4

    def test_new_events_have_proper_inheritance(self):
        """
        GIVEN new event classes
        WHEN checking their inheritance
        THEN they should inherit from DomainEvent
        """
        assert issubclass(UserLoginAttempted, DomainEvent)
        assert issubclass(ArticleViewIncremented, DomainEvent)
        assert issubclass(ContentFlagged, DomainEvent)
        assert issubclass(RateLimitExceeded, DomainEvent)
