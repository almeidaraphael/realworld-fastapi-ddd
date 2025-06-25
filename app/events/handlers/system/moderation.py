"""
Event handlers for content moderation events.
Handles content flagging, approval, removal, and spam detection.
"""

import asyncio
import logging

from app.events import (
    ContentApproved,
    ContentFlagged,
    ContentRemoved,
    SpamDetected,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


async def handle_content_flagged(event: ContentFlagged) -> None:
    """Handle content flagging events for moderation review."""
    logger.warning(
        f"Content flagged for moderation: {event.content_type} {event.content_id} "
        f"by user {event.reporter_id or 'anonymous'} - reason: {event.reason}"
    )
    # Could queue for manual review, trigger automatic checks, notify moderators
    # Simulate async work (e.g., queueing for review, sending alerts)
    await asyncio.sleep(0.01)


async def handle_content_approved(event: ContentApproved) -> None:
    """Handle content approval events after moderation review."""
    logger.info(
        f"Content approved: {event.content_type} {event.content_id} "
        f"by moderator {event.moderator_id}"
    )
    # Could notify reporter of decision, remove moderation flags, update stats
    # Simulate async work (e.g., sending notifications, updating flags)
    await asyncio.sleep(0.01)


async def handle_content_removed(event: ContentRemoved) -> None:
    """Handle content removal events after moderation action."""
    logger.warning(
        f"Content removed: {event.content_type} {event.content_id} "
        f"by moderator {event.moderator_id} - reason: {event.reason}"
    )
    # Could notify author and reporter, update moderation logs, trigger cleanup
    # Simulate async work (e.g., sending notifications, updating logs)
    await asyncio.sleep(0.01)


async def handle_spam_detected(event: SpamDetected) -> None:
    """Handle automated spam detection events."""
    logger.warning(
        f"Spam detected: {event.content_type} {event.content_id} "
        f"by user {event.author_id} - confidence: {event.confidence:.2f}"
    )
    # Could auto-hide content, flag for review, update spam filters
    # Simulate async work (e.g., auto-hiding content, updating filters)
    await asyncio.sleep(0.01)


def register_moderation_handlers() -> None:
    """Register all moderation event handlers."""
    shared_event_bus.subscribe_async(ContentFlagged, handle_content_flagged)
    shared_event_bus.subscribe_async(ContentApproved, handle_content_approved)
    shared_event_bus.subscribe_async(ContentRemoved, handle_content_removed)
    shared_event_bus.subscribe_async(SpamDetected, handle_spam_detected)
