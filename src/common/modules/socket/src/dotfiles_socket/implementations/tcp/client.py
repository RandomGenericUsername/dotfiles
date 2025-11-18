"""TCP socket client implementation."""

import builtins
import logging
import socket
import threading
import time
from collections import deque
from collections.abc import Iterator

import msgpack

from dotfiles_socket.config import get_generic_socket_config
from dotfiles_socket.core import ConnectionError as SocketConnectionError
from dotfiles_socket.core import (
    MessageError,
    SocketClient,
    SocketMessage,
    TimeoutError,
    validate_event_name,
)


class TcpSocketClient(SocketClient):
    """TCP socket client implementation."""

    def __init__(
        self,
        event_name: str,
        host: str | None = None,
        port: int | None = None,
        auto_reconnect: bool = True,
        buffer_size: int | None = None,
    ) -> None:
        """Initialize TCP socket client.

        Args:
            event_name: Event identifier to connect to
            host: Server host (default from config)
            port: Server port (required for TCP)
            auto_reconnect: Automatically reconnect on disconnect
            buffer_size: Message buffer size (default from config)

        Raises:
            ValidationError: If event_name is invalid
            ValueError: If port is not provided
        """
        validate_event_name(event_name)
        self._event_name = event_name
        self._logger = logging.getLogger(__name__)

        # Load config
        generic_config = get_generic_socket_config()

        # Set configuration
        from dotfiles_socket.config import get_tcp_socket_config

        tcp_config = get_tcp_socket_config()
        self._host = host or tcp_config.host

        if port is None:
            raise ValueError("Port must be provided for TCP socket client")
        self._port = port

        self._auto_reconnect = auto_reconnect
        self._buffer_size = (
            buffer_size
            if buffer_size is not None
            else generic_config.buffer_size
        )
        self._timeout = generic_config.default_timeout

        # Client state
        self._socket: socket.socket | None = None
        self._connected = False
        self._receive_thread: threading.Thread | None = None

        # Message buffer
        self._message_buffer: deque[SocketMessage] = deque(
            maxlen=self._buffer_size
        )
        self._buffer_lock = threading.Lock()
        self._buffer_condition = threading.Condition(self._buffer_lock)

    @property
    def event_name(self) -> str:
        """Get the event name for this client."""
        return self._event_name

    def connect(self) -> None:
        """Connect to the socket server."""
        if self._connected:
            self._logger.warning(
                f"Client already connected to '{self._event_name}'"
            )
            return

        try:
            # Create TCP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(self._timeout)

            # Connect to server
            self._socket.connect((self._host, self._port))
            self._connected = True

            self._logger.info(
                f"Connected to TCP socket: {self._host}:{self._port}"
            )

            # Start receive thread
            self._receive_thread = threading.Thread(
                target=self._receive_loop, daemon=True
            )
            self._receive_thread.start()

        except Exception as e:
            self._connected = False
            raise SocketConnectionError(f"Failed to connect: {e}") from e

    def disconnect(self) -> None:
        """Disconnect from the socket server."""
        if not self._connected:
            return

        self._connected = False
        self._logger.info(
            f"Disconnecting from TCP socket: {self._host}:{self._port}"
        )

        # Close socket
        if self._socket:
            try:
                self._socket.close()
            except Exception as e:
                self._logger.error(f"Error closing socket: {e}")

        # Wait for receive thread
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=1.0)

        self._logger.info("Disconnected from TCP socket")

    def send(self, message: SocketMessage) -> None:
        """Send a message to the server."""
        if not self._connected or not self._socket:
            raise SocketConnectionError("Not connected to server")

        try:
            # Serialize message
            msg_dict = message.to_dict()
            packed_data = msgpack.packb(msg_dict)

            # Send length prefix (4 bytes) + data
            length = len(packed_data)
            self._socket.sendall(length.to_bytes(4, "big") + packed_data)

        except Exception as e:
            raise MessageError(f"Failed to send message: {e}") from e

    def receive(self, timeout: float | None = None) -> SocketMessage:
        """Receive a message from the server (blocking).

        Args:
            timeout: Timeout in seconds (None = wait forever)

        Returns:
            Received message

        Raises:
            TimeoutError: If timeout expires
            ConnectionError: If not connected
        """
        if not self._connected:
            raise SocketConnectionError("Not connected to server")

        with self._buffer_condition:
            # Wait for message in buffer
            if timeout is not None:
                if not self._buffer_condition.wait_for(
                    lambda: len(self._message_buffer) > 0, timeout=timeout
                ):
                    raise TimeoutError(
                        f"No message received within {timeout}s"
                    )
            else:
                self._buffer_condition.wait_for(
                    lambda: len(self._message_buffer) > 0
                )

            # Get message from buffer
            return self._message_buffer.popleft()

    def receive_iter(self) -> Iterator[SocketMessage]:
        """Iterate over received messages.

        Yields:
            Messages as they are received
        """
        while self._connected:
            try:
                yield self.receive(timeout=1.0)
            except TimeoutError:
                continue

    def is_connected(self) -> bool:
        """Check if client is currently connected."""
        return self._connected

    def get_buffer_size(self) -> int:
        """Get current size of the message buffer."""
        with self._buffer_lock:
            return len(self._message_buffer)

    def clear_buffer(self) -> None:
        """Clear all buffered messages."""
        with self._buffer_lock:
            self._message_buffer.clear()
            self._logger.debug("Message buffer cleared")

    def _receive_loop(self) -> None:
        """Receive messages from server in background thread."""
        while self._connected and self._socket:
            try:
                # Read length prefix (4 bytes)
                length_data = self._recv_exact(4)
                if not length_data:
                    break

                length = int.from_bytes(length_data, "big")

                # Read message data
                msg_data = self._recv_exact(length)
                if not msg_data:
                    break

                # Deserialize message
                try:
                    msg_dict = msgpack.unpackb(msg_data, raw=False)
                    message = SocketMessage.from_dict(msg_dict)

                    # Add to buffer
                    with self._buffer_condition:
                        self._message_buffer.append(message)
                        self._buffer_condition.notify_all()

                except Exception as e:
                    self._logger.error(f"Failed to deserialize message: {e}")

            except Exception as e:
                if self._connected:
                    self._logger.error(f"Error receiving message: {e}")
                    if self._auto_reconnect:
                        self._reconnect()
                break

    def _recv_exact(self, num_bytes: int) -> bytes:
        """Receive exactly num_bytes from socket."""
        if not self._socket:
            return b""

        data = b""
        while len(data) < num_bytes:
            try:
                chunk = self._socket.recv(num_bytes - len(data))
                if not chunk:
                    return b""
                data += chunk
            except builtins.TimeoutError:
                continue
            except Exception:
                return b""
        return data

    def _reconnect(self) -> None:
        """Attempt to reconnect to the server."""
        self._logger.info("Attempting to reconnect...")
        self.disconnect()
        time.sleep(1.0)

        try:
            self.connect()
            self._logger.info("Reconnected successfully")
        except Exception as e:
            self._logger.error(f"Reconnection failed: {e}")
