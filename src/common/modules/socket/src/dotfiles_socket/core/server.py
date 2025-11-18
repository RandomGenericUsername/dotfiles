"""Abstract base class for socket servers."""

from abc import ABC, abstractmethod

from .types import ClientInfo, SocketMessage


class SocketServer(ABC):
    """Abstract base class for all socket server implementations.

    Implementations must provide concrete implementations for all
    abstract methods and properties.
    """

    @property
    @abstractmethod
    def event_name(self) -> str:
        """Get the event name for this server.

        Returns:
            Event name identifier
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Start the socket server.

        Starts accepting client connections. Behavior depends on
        blocking_mode configuration:
        - Non-blocking (default): Returns immediately, runs in thread
        - Blocking: Blocks until server is stopped

        Raises:
            SocketError: If server fails to start
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the socket server.

        Closes all client connections and performs cleanup.
        Should be idempotent (safe to call multiple times).

        Raises:
            SocketError: If server fails to stop cleanly
        """
        pass

    @abstractmethod
    def send(
        self, message: SocketMessage, client_id: str | None = None
    ) -> None:
        """Send a message to client(s).

        Args:
            message: Message to send
            client_id: Optional client ID for unicast. If None, broadcast
                      to all connected clients.

        Raises:
            MessageError: If message cannot be sent
            ConnectionError: If client_id specified but not connected
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Check if server is currently running.

        Returns:
            True if server is running, False otherwise
        """
        pass

    @abstractmethod
    def get_connected_clients(self) -> list[ClientInfo]:
        """Get list of currently connected clients.

        Returns:
            List of ClientInfo objects for connected clients
        """
        pass

    @abstractmethod
    def on_client_connected(self, client_info: ClientInfo) -> None:
        """Hook called when a client connects.

        Implementations can override to add custom behavior.

        Args:
            client_info: Information about the connected client
        """
        pass

    @abstractmethod
    def on_client_disconnected(self, client_id: str) -> None:
        """Hook called when a client disconnects.

        Implementations can override to add custom behavior.

        Args:
            client_id: ID of the disconnected client
        """
        pass

    @abstractmethod
    def on_message_received(
        self, client_id: str, message: SocketMessage
    ) -> None:
        """Hook called when a message is received from a client.

        Only called if allow_client_send is enabled.

        Args:
            client_id: ID of the client that sent the message
            message: The received message
        """
        pass

    @abstractmethod
    def get_queue_size(self) -> int:
        """Get current size of the message queue.

        Returns:
            Number of messages currently queued
        """
        pass

    @abstractmethod
    def clear_queue(self) -> None:
        """Clear all queued messages.

        Removes all messages from the queue without sending them.
        """
        pass
