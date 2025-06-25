"""
Event handlers for security-related events.
Handles authentication, authorization, and security monitoring events.
"""

import asyncio
import logging

from app.events import (
    SuspiciousLoginActivity,
    UserAccountLocked,
    UserLoginAttempted,
    UserPasswordChanged,
    shared_event_bus,
)

logger = logging.getLogger(__name__)


async def handle_user_login_attempted(event: UserLoginAttempted) -> None:
    """Handle user login attempt events for security monitoring."""
    if event.success:
        logger.info(f"Successful login: {event.email} from {event.ip_address or 'unknown IP'}")
    else:
        logger.warning(
            f"Failed login attempt: {event.email} from {event.ip_address or 'unknown IP'}"
        )
        # Could trigger additional security measures here
        # e.g., increment failed attempt counter, check for rate limiting
    # Simulate async work (e.g., updating security logs, checking patterns)
    await asyncio.sleep(0.01)


async def handle_password_change(event: UserPasswordChanged) -> None:
    """Handle password change events."""
    logger.info(f"Password changed for user {event.username} (ID: {event.user_id})")
    # Could send email notification, audit log, etc.
    # Simulate async work (e.g., sending security notifications)
    await asyncio.sleep(0.01)


async def handle_account_locked(event: UserAccountLocked) -> None:
    """Handle account lockout events."""
    logger.warning(f"Account locked for user {event.username} ({event.email})")
    # Could send security alert email, notify administrators
    # Simulate async work (e.g., sending security alerts)
    await asyncio.sleep(0.01)


async def handle_suspicious_activity(event: SuspiciousLoginActivity) -> None:
    """Handle suspicious login activity."""
    logger.error(
        f"Suspicious login activity detected for {event.email} "
        f"from {event.ip_address or 'unknown IP'}: {event.reason}"
    )
    # Could trigger additional security measures, alerts, or temporary blocks
    # Simulate async work (e.g., triggering security measures)
    await asyncio.sleep(0.01)


def register_security_handlers() -> None:
    """Register all security event handlers."""
    shared_event_bus.subscribe_async(UserLoginAttempted, handle_user_login_attempted)
    shared_event_bus.subscribe_async(UserPasswordChanged, handle_password_change)
    shared_event_bus.subscribe_async(UserAccountLocked, handle_account_locked)
    shared_event_bus.subscribe_async(SuspiciousLoginActivity, handle_suspicious_activity)
