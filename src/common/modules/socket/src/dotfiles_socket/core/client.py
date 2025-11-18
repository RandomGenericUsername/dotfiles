"""Abstract base class for socket clients."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from .types import SocketMessage


class SocketClient(ABC):
    """Abstract base class for all socket client implementations.

    Implementations must provide concrete implementations for all
    abstract methods and properties.
    """

    @property
    @abstractmethod
    def event_name(self) -> str:
        """Get the event name for this client.

        Returns:
            Event name identifier
        """
        pass

    @abstractmethod
    def connect(self) -> None:
        """Connect to the socket server.

        Establishes connection to the server. If auto_reconnect is
        enabled, will automatically reconnect on connection loss.

        Raises:
            ConnectionError: If connection fails
            TimeoutError: If connection times out
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the socket server.

        Closes the connection to the server. Should be idempotent
        (safe to call multiple times).

        Raises:
            SocketError: If disconnection fails
        """
        pass

    @abstractmethod
    def send(self, message: SocketMessage) -> None:
        """Send a message to the server.

        Only works if server has allow_client_send enabled.

        Args:
            message: Message to send

        Raises:
            MessageError: If message cannot be sent
            ConnectionError: If not connected to server
            SocketError: If server doesn't allow client send
        """
        pass

    @abstractmethod
    def receive(self, timeout: float | None = None) -> SocketMessage:
        """Receive a single message from the server (blocking).

        Blocks until a message is received or timeout expires.

        Args:
            timeout: Optional timeout in seconds. None = wait forever

        Returns:
            Received message

        Raises:
            TimeoutError: If timeout expires before message received
            ConnectionError: If connection is lost
            MessageError: If message cannot be decoded
        """
        pass

    @abstractmethod
    def receive_iter(self) -> Iterator[SocketMessage]:
        """Iterate over received messages.

        Returns an iterator that yields messages as they arrive.
        Blocks waiting for each message.

        Yields:
            SocketMessage objects as they are received

        Raises:
            ConnectionError: If connection is lost
            MessageError: If message cannot be decoded
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if client is currently connected.

        Returns:
            True if connected, False otherwise
        """
        pass

    @abstractmethod
    def get_buffer_size(self) -> int:
        """Get number of messages in the receive buffer.

        Returns:
            Number of buffered messages
        """
        pass

    @abstractmethod
    def clear_buffer(self) -> None:
        """Clear all buffered messages.

        Removes all messages from the receive buffer without
        processing them.
        """
        pass
