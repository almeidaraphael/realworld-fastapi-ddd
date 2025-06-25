"""
Event handlers for user domain events.
Handles user lifecycle events including registration, login, and profile updates.
"""

import logging

from app.events import (
    UserFollowed,
    UserLoggedIn,
    UserProfileUpdated,
    UserRegistered,
    UserUnfollowed,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


async def handle_user_registered(event: UserRegistered) -> None:
    """Handle user registration event - could send welcome email, setup defaults, etc."""
    logger.info(
        f"UserRegistered: user_id={event.user_id}, username={event.username}, email={event.email}"
    )
    # Simulate async operations like sending welcome email
    import asyncio
    await asyncio.sleep(0.01)  # Placeholder for actual async operations


async def handle_user_logged_in(event: UserLoggedIn) -> None:
    """Handle user login event - could track login analytics, security monitoring, etc."""
    logger.info(f"UserLoggedIn: user_id={event.user_id}, username={event.username}")
    # Simulate async operations like updating analytics
    import asyncio
    await asyncio.sleep(0.01)


async def handle_user_profile_updated(event: UserProfileUpdated) -> None:
    """Handle user profile update event - could sync with external systems, etc."""
    logger.info(
        f"UserProfileUpdated: user_id={event.user_id}, username={event.username}, "
        f"fields={event.updated_fields}"
    )
    # Simulate async operations like syncing with external systems
    import asyncio
    await asyncio.sleep(0.01)


async def handle_user_followed(event: UserFollowed) -> None:
    """Handle user followed event - could send notifications, update recommendations, etc."""
    logger.info(f"UserFollowed: follower_id={event.follower_id}, followee_id={event.followee_id}")
    # Simulate async operations like sending notifications
    import asyncio
    await asyncio.sleep(0.01)


async def handle_user_unfollowed(event: UserUnfollowed) -> None:
    """Handle user unfollowed event - could update recommendations, etc."""
    logger.info(f"UserUnfollowed: follower_id={event.follower_id}, followee_id={event.followee_id}")
    # Simulate async operations like updating recommendations
    import asyncio
    await asyncio.sleep(0.01)


def register_user_handlers() -> None:
    """Register all user event handlers."""
    shared_event_bus.subscribe_async(UserRegistered, handle_user_registered)
    shared_event_bus.subscribe_async(UserLoggedIn, handle_user_logged_in)
    shared_event_bus.subscribe_async(UserProfileUpdated, handle_user_profile_updated)
    shared_event_bus.subscribe_async(UserFollowed, handle_user_followed)
    shared_event_bus.subscribe_async(UserUnfollowed, handle_user_unfollowed)
