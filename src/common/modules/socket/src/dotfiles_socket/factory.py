"""Factory functions for creating socket servers and clients."""

from enum import Enum
from typing import Any

from dotfiles_socket.core import SocketClient, SocketServer


class SocketType(Enum):
    """Socket type enumeration."""

    UNIX = "unix"
    TCP = "tcp"


def create_server(
    socket_type: SocketType | str,
    event_name: str,
    **kwargs: Any,
) -> SocketServer:
    """Create a socket server instance.

    Args:
        socket_type: Type of socket (SocketType.UNIX or SocketType.TCP)
        event_name: Event identifier for this server
        **kwargs: Additional arguments passed to the server constructor

    Returns:
        SocketServer instance (UnixSocketServer or TcpSocketServer)

    Raises:
        ValueError: If socket_type is invalid

    Examples:
        # Create Unix socket server
        server = create_server(
            SocketType.UNIX,
            "my_event",
            socket_dir=Path("/tmp/sockets"),
            blocking_mode=False,
        )

        # Create TCP socket server
        server = create_server(
            SocketType.TCP,
            "my_event",
            host="127.0.0.1",
            port=9000,
        )
    """
    # Convert string to enum if needed
    if isinstance(socket_type, str):
        try:
            socket_type = SocketType(socket_type.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid socket_type: {socket_type}. Must be 'unix' or 'tcp'"
            ) from e

    if socket_type == SocketType.UNIX:
        from dotfiles_socket.implementations.unix import UnixSocketServer

        return UnixSocketServer(event_name=event_name, **kwargs)
    elif socket_type == SocketType.TCP:
        from dotfiles_socket.implementations.tcp import TcpSocketServer

        return TcpSocketServer(event_name=event_name, **kwargs)
    else:
        raise ValueError(f"Unsupported socket type: {socket_type}")


def create_client(
    socket_type: SocketType | str,
    event_name: str,
    **kwargs: Any,
) -> SocketClient:
    """Create a socket client instance.

    Args:
        socket_type: Type of socket (SocketType.UNIX or SocketType.TCP)
        event_name: Event identifier to connect to
        **kwargs: Additional arguments passed to the client constructor

    Returns:
        SocketClient instance (UnixSocketClient or TcpSocketClient)

    Raises:
        ValueError: If socket_type is invalid

    Examples:
        # Create Unix socket client
        client = create_client(
            SocketType.UNIX,
            "my_event",
            socket_dir=Path("/tmp/sockets"),
            auto_reconnect=True,
        )

        # Create TCP socket client
        client = create_client(
            SocketType.TCP,
            "my_event",
            host="127.0.0.1",
            port=9000,
        )
    """
    # Convert string to enum if needed
    if isinstance(socket_type, str):
        try:
            socket_type = SocketType(socket_type.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid socket_type: {socket_type}. Must be 'unix' or 'tcp'"
            ) from e

    if socket_type == SocketType.UNIX:
        from dotfiles_socket.implementations.unix import UnixSocketClient

        return UnixSocketClient(event_name=event_name, **kwargs)
    elif socket_type == SocketType.TCP:
        from dotfiles_socket.implementations.tcp import TcpSocketClient

        return TcpSocketClient(event_name=event_name, **kwargs)
    else:
        raise ValueError(f"Unsupported socket type: {socket_type}")
