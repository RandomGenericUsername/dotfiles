"""Custom exceptions for socket module."""


class SocketError(Exception):
    """Base exception for all socket-related errors."""

    pass


class ConnectionError(SocketError):
    """Exception raised for connection-related errors."""

    pass


class MessageError(SocketError):
    """Exception raised for message-related errors."""

    pass


class ValidationError(SocketError):
    """Exception raised for validation errors."""

    pass


class TimeoutError(SocketError):
    """Exception raised for timeout errors."""

    pass


class MaxConnectionsError(SocketError):
    """Exception raised when maximum connections limit is reached."""

    pass
