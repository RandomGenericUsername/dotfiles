"""Unix domain socket client implementation."""

import logging
import socket
import threading
import time
from collections import deque
from collections.abc import Iterator
from pathlib import Path

import msgpack

from dotfiles_socket.config import get_generic_socket_config
from dotfiles_socket.core import ConnectionError as SocketConnectionError
from dotfiles_socket.core import (
    MessageError,
    SocketClient,
    SocketMessage,
    validate_event_name,
)
from dotfiles_socket.core import TimeoutError as SocketTimeoutError


class UnixSocketClient(SocketClient):
    """Unix domain socket client implementation."""

    def __init__(
        self,
        event_name: str,
        socket_dir: Path | None = None,
        auto_reconnect: bool = True,
        reconnect_delay: float = 1.0,
        buffer_size: int | None = None,
    ) -> None:
        """Initialize Unix socket client.

        Args:
            event_name: Event identifier to connect to
            socket_dir: Directory for socket file (default from config)
            auto_reconnect: Automatically reconnect on disconnect
            reconnect_delay: Delay between reconnect attempts (seconds)
            buffer_size: Message buffer size (default from config)

        Raises:
            ValidationError: If event_name is invalid
        """
        validate_event_name(event_name)
        self._event_name = event_name
        self._logger = logging.getLogger(__name__)

        # Load config
        generic_config = get_generic_socket_config()

        # Set configuration
        self._socket_dir = (
            Path(socket_dir) if socket_dir else generic_config.socket_dir
        )
        self._auto_reconnect = auto_reconnect
        self._reconnect_delay = reconnect_delay
        self._buffer_size_bytes = (
            buffer_size
            if buffer_size is not None
            else generic_config.buffer_size
        )

        # Client state
        self._socket_path = self._socket_dir / f"{self._event_name}.sock"
        self._client_socket: socket.socket | None = None
        self._connected = False
        self._receive_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

        # Message buffer
        self._message_buffer: deque[SocketMessage] = deque()
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
            # Create Unix domain socket
            self._client_socket = socket.socket(
                socket.AF_UNIX, socket.SOCK_STREAM
            )
            self._client_socket.connect(str(self._socket_path))
            self._connected = True

            self._logger.info(f"Connected to Unix socket: {self._socket_path}")

            # Start receive thread
            self._stop_event.clear()
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
        self._stop_event.set()

        self._logger.info(
            f"Disconnecting from Unix socket: {self._socket_path}"
        )

        # Close socket
        if self._client_socket:
            try:
                self._client_socket.close()
            except Exception as e:
                self._logger.error(f"Error closing socket: {e}")

        # Wait for receive thread
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=1.0)

        self._logger.info("Disconnected from Unix socket")

    def send(self, message: SocketMessage) -> None:
        """Send a message to the server."""
        if not self._connected or not self._client_socket:
            raise SocketConnectionError("Not connected to server")

        try:
            # Serialize message
            msg_dict = message.to_dict()
            packed_data = msgpack.packb(msg_dict)

            # Send length prefix (4 bytes) + data
            length = len(packed_data)
            self._client_socket.sendall(
                length.to_bytes(4, "big") + packed_data
            )

        except Exception as e:
            raise MessageError(f"Failed to send message: {e}") from e

    def receive(self, timeout: float | None = None) -> SocketMessage:
        """Receive a message from the server (blocking).

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            Received SocketMessage

        Raises:
            TimeoutError: If timeout expires before message received
            ConnectionError: If not connected
        """
        if not self._connected:
            raise SocketConnectionError("Not connected to server")

        with self._buffer_condition:
            # Wait for message in buffer
            if not self._message_buffer and not self._buffer_condition.wait(
                timeout=timeout
            ):
                raise SocketTimeoutError("Timeout waiting for message")

            if not self._message_buffer:
                raise SocketTimeoutError("Timeout waiting for message")

            return self._message_buffer.popleft()

    def receive_iter(self) -> Iterator[SocketMessage]:
        """Iterate over received messages.

        Yields:
            SocketMessage objects as they arrive

        Raises:
            ConnectionError: If not connected
        """
        if not self._connected:
            raise SocketConnectionError("Not connected to server")

        while self._connected:
            try:
                message = self.receive(timeout=0.1)
                yield message
            except SocketTimeoutError:
                # No message available - continue waiting
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
        """Receive messages from server (runs in thread)."""
        while not self._stop_event.is_set() and self._connected:
            try:
                if not self._client_socket:
                    break

                # Set timeout to allow checking stop event
                self._client_socket.settimeout(0.5)

                # Receive length prefix (4 bytes)
                length_data = self._recv_exact(4)
                if not length_data:
                    break

                length = int.from_bytes(length_data, "big")

                # Receive message data
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

            except TimeoutError:
                # Normal timeout - continue loop
                continue
            except Exception as e:
                if self._connected:
                    self._logger.error(f"Error receiving message: {e}")
                    if self._auto_reconnect:
                        self._attempt_reconnect()
                    else:
                        break

    def _recv_exact(self, num_bytes: int) -> bytes:
        """Receive exact number of bytes from socket."""
        if not self._client_socket:
            return b""

        data = b""
        while len(data) < num_bytes:
            chunk = self._client_socket.recv(num_bytes - len(data))
            if not chunk:
                return b""
            data += chunk
        return data

    def _attempt_reconnect(self) -> None:
        """Attempt to reconnect to the server."""
        self._logger.info(
            f"Attempting to reconnect in {self._reconnect_delay}s..."
        )
        time.sleep(self._reconnect_delay)

        try:
            self.disconnect()
            self.connect()
            self._logger.info("Reconnected successfully")
        except Exception as e:
            self._logger.error(f"Reconnect failed: {e}")
