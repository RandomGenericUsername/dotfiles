"""Socket module for inter-process communication.

This module provides a generic socket abstraction for both Unix domain
sockets and TCP sockets, with support for:
- Server and client implementations
- Message queuing and broadcasting
- Thread-safe operations
- Auto-reconnect for clients
- MessagePack serialization

Examples:
    # Using factory functions (recommended)
    from dotfiles_socket import create_server, create_client, SocketType

    server = create_server(SocketType.UNIX, "my_event")
    server.start()

    client = create_client(SocketType.UNIX, "my_event")
    client.connect()

    # Using specific implementations
    from dotfiles_socket.implementations.unix import (
        UnixSocketServer,
        UnixSocketClient,
    )

    server = UnixSocketServer("my_event")
    client = UnixSocketClient("my_event")
"""

# Core types and utilities
# Configuration
from dotfiles_socket.config import (
    AppConfig,
    SocketConfig,
    SocketModuleConfig,
    TcpSocketConfig,
    UnixSocketConfig,
    get_default_config,
    get_generic_socket_config,
    get_socket_config,
    get_tcp_socket_config,
    get_unix_socket_config,
)

# Exceptions
from dotfiles_socket.core import (
    ClientInfo,
    ConnectionError,
    MaxConnectionsError,
    MessageError,
    MessageType,
    SocketClient,
    SocketError,
    SocketMessage,
    SocketServer,
    TimeoutError,
    ValidationError,
    create_message,
    get_timestamp_iso,
    get_timestamp_ms,
    validate_event_name,
)

# Factory functions
from dotfiles_socket.factory import SocketType, create_client, create_server

# Implementations (for direct use if needed)
from dotfiles_socket.implementations.tcp import (
    TcpSocketClient,
    TcpSocketServer,
)
from dotfiles_socket.implementations.unix import (
    UnixSocketClient,
    UnixSocketServer,
)

__all__ = [
    # Core types
    "SocketServer",
    "SocketClient",
    "SocketMessage",
    "MessageType",
    "ClientInfo",
    # Core utilities
    "create_message",
    "validate_event_name",
    "get_timestamp_ms",
    "get_timestamp_iso",
    # Exceptions
    "SocketError",
    "ConnectionError",
    "MessageError",
    "ValidationError",
    "TimeoutError",
    "MaxConnectionsError",
    # Configuration
    "AppConfig",
    "SocketModuleConfig",
    "SocketConfig",
    "UnixSocketConfig",
    "TcpSocketConfig",
    "get_default_config",
    "get_socket_config",
    "get_generic_socket_config",
    "get_unix_socket_config",
    "get_tcp_socket_config",
    # Factory
    "SocketType",
    "create_server",
    "create_client",
    # Unix implementations
    "UnixSocketServer",
    "UnixSocketClient",
    # TCP implementations
    "TcpSocketServer",
    "TcpSocketClient",
]
