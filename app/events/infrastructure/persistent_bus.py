"""
Enhanced event bus with persistence capability for critical events.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.events.core import DomainEvent, EventBus

logger = logging.getLogger(__name__)


class PersistentEventBus(EventBus):
    """
    Event bus that persists events to disk for replay capability.

    This enhanced event bus extends the standard EventBus to provide event
    persistence functionality. All published events are logged to disk in
    JSON format, allowing for event replay, audit trails, and debugging
    of event-driven workflows.

    Args:
        log_file: Path to the file where events will be logged (default: "events.log")

    Usage:
        persistent_bus = PersistentEventBus("app_events.log")
        persistent_bus.publish(ArticleCreated(article_id=123, author_id=456))
        # Event is both handled and logged to disk
    """

    def __init__(self, log_file: str = "events.log") -> None:
        super().__init__()
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _serialize_event(self, event: DomainEvent) -> dict[str, Any]:
        """
        Serialize event to a dictionary.

        Args:
            event: The domain event to serialize

        Returns:
            Dictionary representation of the event with metadata
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.__class__.__name__,
            "event_module": event.__class__.__module__,
            "data": {k: v for k, v in event.__dict__.items()},
        }

    def _log_event(self, event: DomainEvent) -> None:
        """
        Log event to persistent storage.

        Args:
            event: The domain event to log to disk
        """
        try:
            serialized = self._serialize_event(event)
            with open(self.log_file, "a") as f:
                f.write(json.dumps(serialized) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist event {event.__class__.__name__}: {e}")

    def publish(self, event: DomainEvent) -> None:
        """
        Publish event and persist it.

        Args:
            event: The domain event to publish and log
        """
        self._log_event(event)
        super().publish(event)

    async def publish_async(self, event: DomainEvent) -> None:
        """
        Publish async event and persist it.

        Args:
            event: The domain event to publish asynchronously and log
        """
        self._log_event(event)
        await super().publish_async(event)

    def replay_events(self, event_filter: str | None = None) -> list[dict[str, Any]]:
        """
        Replay events from the log file.

        This method reads all persisted events from the log file and returns
        them as a list of dictionaries. Optionally filter by event type.

        Args:
            event_filter: Optional event type name to filter by (e.g., "ArticleCreated")

        Returns:
            List of event dictionaries that match the filter criteria

        Usage:
            # Get all events
            all_events = bus.replay_events()

            # Get only ArticleCreated events
            article_events = bus.replay_events("ArticleCreated")
        """
        events: list[dict[str, Any]] = []
        if not self.log_file.exists():
            return events

        try:
            with open(self.log_file) as f:
                for line in f:
                    if line.strip():
                        event_data = json.loads(line)
                        if event_filter is None or event_data.get("event_type") == event_filter:
                            events.append(event_data)
        except Exception as e:
            logger.error(f"Failed to replay events: {e}")

        return events
