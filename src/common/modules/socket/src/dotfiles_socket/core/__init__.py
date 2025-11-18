"""Core abstractions for socket module."""

from .client import SocketClient
from .exceptions import (
    ConnectionError,
    MaxConnectionsError,
    MessageError,
    SocketError,
    TimeoutError,
    ValidationError,
)
from .server import SocketServer
from .types import (
    ClientInfo,
    MessageType,
    SocketMessage,
    create_message,
    get_timestamp_iso,
    get_timestamp_ms,
    validate_event_name,
)

__all__ = [
    # Abstract base classes
    "SocketServer",
    "SocketClient",
    # Types
    "SocketMessage",
    "MessageType",
    "ClientInfo",
    # Exceptions
    "SocketError",
    "ConnectionError",
    "MessageError",
    "ValidationError",
    "TimeoutError",
    "MaxConnectionsError",
    # Utility functions
    "validate_event_name",
    "get_timestamp_ms",
    "get_timestamp_iso",
    "create_message",
]
