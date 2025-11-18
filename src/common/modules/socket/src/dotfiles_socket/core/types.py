"""Core types for socket module."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Message type/channel enum."""

    DATA = "data"
    ERROR = "error"
    CONTROL = "control"


@dataclass
class SocketMessage:
    """Standard message format for socket communication.

    Attributes:
        event_name: Event identifier for this message
        timestamp_ms: Unix timestamp in milliseconds
        timestamp_iso: ISO format timestamp in configured timezone
        message_type: Type/channel of message (DATA, ERROR, CONTROL)
        data: Arbitrary message payload
    """

    event_name: str
    timestamp_ms: int
    timestamp_iso: str
    message_type: MessageType
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary for serialization.

        Returns:
            Dictionary representation of the message
        """
        return {
            "event_name": self.event_name,
            "timestamp_ms": self.timestamp_ms,
            "timestamp_iso": self.timestamp_iso,
            "message_type": self.message_type.value,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SocketMessage":
        """Create message from dictionary.

        Args:
            data: Dictionary containing message data

        Returns:
            SocketMessage instance
        """
        return cls(
            event_name=data["event_name"],
            timestamp_ms=data["timestamp_ms"],
            timestamp_iso=data["timestamp_iso"],
            message_type=MessageType(data["message_type"]),
            data=data["data"],
        )


@dataclass
class ClientInfo:
    """Information about a connected client.

    Attributes:
        client_id: Unique identifier for the client
        connected_at: Unix timestamp in milliseconds when connected
        address: Client address (socket path or host:port)
    """

    client_id: str
    connected_at: int
    address: str


# Event name validation
EVENT_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
EVENT_NAME_MAX_LENGTH = 64


def validate_event_name(event_name: str) -> None:
    """Validate event name format.

    Args:
        event_name: Event name to validate

    Raises:
        ValueError: If event name is invalid
    """
    if not event_name:
        raise ValueError("Event name cannot be empty")

    if len(event_name) > EVENT_NAME_MAX_LENGTH:
        raise ValueError(
            f"Event name too long: {len(event_name)} > {EVENT_NAME_MAX_LENGTH}"
        )

    if not EVENT_NAME_PATTERN.match(event_name):
        raise ValueError(
            f"Invalid event name: '{event_name}'. "
            "Only alphanumeric, underscore, and hyphen allowed"
        )


def get_timestamp_ms() -> int:
    """Get current Unix timestamp in milliseconds.

    Returns:
        Current timestamp in milliseconds
    """
    return int(datetime.now(UTC).timestamp() * 1000)


def get_timestamp_iso(tz_name: str = "UTC") -> str:
    """Get current timestamp in ISO format.

    Args:
        tz_name: Timezone name (e.g., "UTC", "America/New_York")
                 Note: Currently only UTC is supported. Full timezone
                 support can be added later with pytz or zoneinfo.

    Returns:
        ISO format timestamp string
    """
    # For now, use UTC regardless of tz_name parameter
    # Full timezone support can be added later with pytz or zoneinfo
    _ = tz_name  # Acknowledge parameter for future use
    dt = datetime.now(UTC)
    return dt.isoformat()


def create_message(
    event_name: str,
    message_type: MessageType,
    data: dict[str, Any],
    tz_name: str = "UTC",
) -> SocketMessage:
    """Create a new socket message with current timestamps.

    Args:
        event_name: Event identifier
        message_type: Type/channel of message
        data: Message payload
        tz_name: Timezone for ISO timestamp

    Returns:
        New SocketMessage instance
    """
    return SocketMessage(
        event_name=event_name,
        timestamp_ms=get_timestamp_ms(),
        timestamp_iso=get_timestamp_iso(tz_name),
        message_type=message_type,
        data=data,
    )
