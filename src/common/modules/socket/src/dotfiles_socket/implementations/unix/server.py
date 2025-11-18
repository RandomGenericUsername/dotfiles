"""Unix domain socket server implementation."""

import contextlib
import logging
import socket
import threading
from collections import deque
from pathlib import Path

import msgpack

from dotfiles_socket.config import (
    get_generic_socket_config,
    get_unix_socket_config,
)
from dotfiles_socket.core import (
    ClientInfo,
    MessageError,
    SocketError,
    SocketMessage,
    SocketServer,
    get_timestamp_ms,
    validate_event_name,
)
from dotfiles_socket.core import ConnectionError as SocketConnectionError


class UnixSocketServer(SocketServer):
    """Unix domain socket server implementation."""

    def __init__(
        self,
        event_name: str,
        socket_dir: Path | None = None,
        blocking_mode: bool | None = None,
        allow_client_send: bool | None = None,
        max_connections: int | None = None,
        socket_permissions: str | None = None,
        auto_remove_socket: bool | None = None,
        message_queue_size: int | None = None,
    ) -> None:
        """Initialize Unix socket server.

        Args:
            event_name: Event identifier for this server
            socket_dir: Directory for socket file (default from config)
            blocking_mode: Run in blocking mode (default from config)
            allow_client_send: Allow clients to send (default from config)
            max_connections: Max concurrent clients (default from config)
            socket_permissions: Socket file permissions (default from config)
            auto_remove_socket: Remove socket on stop (default from config)
            message_queue_size: Max queued messages (default from config)

        Raises:
            ValidationError: If event_name is invalid
        """
        validate_event_name(event_name)
        self._event_name = event_name
        self._logger = logging.getLogger(__name__)

        # Load config
        generic_config = get_generic_socket_config()
        unix_config = get_unix_socket_config()

        # Set configuration
        self._socket_dir = (
            Path(socket_dir) if socket_dir else generic_config.socket_dir
        )
        self._blocking_mode = (
            blocking_mode
            if blocking_mode is not None
            else generic_config.blocking_mode
        )
        self._allow_client_send = (
            allow_client_send
            if allow_client_send is not None
            else generic_config.allow_client_send
        )
        self._max_connections = (
            max_connections
            if max_connections is not None
            else unix_config.max_connections
        )
        self._socket_permissions = (
            socket_permissions or unix_config.socket_permissions
        )
        self._auto_remove_socket = (
            auto_remove_socket
            if auto_remove_socket is not None
            else unix_config.auto_remove_socket
        )
        self._message_queue_size = (
            message_queue_size
            if message_queue_size is not None
            else generic_config.message_queue_size
        )
        self._buffer_size = generic_config.buffer_size

        # Server state
        self._socket_path = self._socket_dir / f"{self._event_name}.sock"
        self._server_socket: socket.socket | None = None
        self._running = False
        self._server_thread: threading.Thread | None = None

        # Client management
        self._clients: dict[str, socket.socket] = {}
        self._clients_lock = threading.Lock()
        self._client_threads: list[threading.Thread] = []

        # Message queue (for when no clients connected)
        self._message_queue: deque[SocketMessage] = deque(
            maxlen=self._message_queue_size
        )
        self._queue_lock = threading.Lock()

    @property
    def event_name(self) -> str:
        """Get the event name for this server."""
        return self._event_name

    def start(self) -> None:
        """Start the socket server."""
        if self._running:
            self._logger.warning(
                f"Server for '{self._event_name}' already running"
            )
            return

        try:
            # Create socket directory if needed
            self._socket_dir.mkdir(parents=True, exist_ok=True)

            # Remove existing socket file if present
            if self._socket_path.exists():
                self._socket_path.unlink()

            # Create Unix domain socket
            self._server_socket = socket.socket(
                socket.AF_UNIX, socket.SOCK_STREAM
            )
            self._server_socket.bind(str(self._socket_path))

            # Set socket permissions
            self._socket_path.chmod(int(self._socket_permissions, 8))

            self._server_socket.listen(self._max_connections)
            self._running = True

            self._logger.info(
                f"Unix socket server started: {self._socket_path}"
            )

            if self._blocking_mode:
                # Blocking mode - run in current thread
                self._accept_clients()
            else:
                # Non-blocking mode - run in separate thread
                self._server_thread = threading.Thread(
                    target=self._accept_clients, daemon=True
                )
                self._server_thread.start()

        except Exception as e:
            self._running = False
            raise SocketError(f"Failed to start server: {e}") from e

    def stop(self) -> None:
        """Stop the socket server."""
        if not self._running:
            return

        self._running = False
        self._logger.info(f"Stopping Unix socket server: {self._socket_path}")

        # Close all client connections
        with self._clients_lock:
            for client_id, client_socket in list(self._clients.items()):
                try:
                    client_socket.close()
                except Exception as e:
                    self._logger.error(
                        f"Error closing client {client_id}: {e}"
                    )
            self._clients.clear()

        # Close server socket
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception as e:
                self._logger.error(f"Error closing server socket: {e}")

        # Remove socket file if configured
        if self._auto_remove_socket and self._socket_path.exists():
            try:
                self._socket_path.unlink()
                self._logger.debug(f"Removed socket file: {self._socket_path}")
            except Exception as e:
                self._logger.error(f"Error removing socket file: {e}")

        # Wait for threads to finish
        for thread in self._client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=1.0)

        self._logger.info("Unix socket server stopped")

    def send(
        self, message: SocketMessage, client_id: str | None = None
    ) -> None:
        """Send a message to client(s)."""
        if not self._running:
            raise SocketError("Server is not running")

        # Serialize message
        try:
            msg_dict = message.to_dict()
            packed_data = msgpack.packb(msg_dict)
        except Exception as e:
            raise MessageError(f"Failed to serialize message: {e}") from e

        with self._clients_lock:
            if not self._clients:
                # No clients connected - queue message
                with self._queue_lock:
                    self._message_queue.append(message)
                    self._logger.debug(
                        f"Queued message (no clients): "
                        f"{len(self._message_queue)}/{self._message_queue_size}"
                    )
                return

            if client_id is not None:
                # Unicast to specific client
                if client_id not in self._clients:
                    raise SocketConnectionError(
                        f"Client not connected: {client_id}"
                    )
                self._send_to_client(
                    self._clients[client_id], packed_data, client_id
                )
            else:
                # Broadcast to all clients
                for cid, client_socket in list(self._clients.items()):
                    self._send_to_client(client_socket, packed_data, cid)

    def _send_to_client(
        self, client_socket: socket.socket, data: bytes, client_id: str
    ) -> None:
        """Send data to a specific client socket."""
        try:
            # Send length prefix (4 bytes) + data
            length = len(data)
            client_socket.sendall(length.to_bytes(4, "big") + data)
        except Exception as e:
            self._logger.error(f"Failed to send to client {client_id}: {e}")
            # Remove failed client
            with self._clients_lock:
                if client_id in self._clients:
                    del self._clients[client_id]

    def is_running(self) -> bool:
        """Check if server is currently running."""
        return self._running

    def get_connected_clients(self) -> list[ClientInfo]:
        """Get list of currently connected clients."""
        with self._clients_lock:
            return [
                ClientInfo(
                    client_id=client_id,
                    connected_at=0,  # TODO: Track connection time
                    address=str(self._socket_path),
                )
                for client_id in self._clients
            ]

    def on_client_connected(self, client_info: ClientInfo) -> None:
        """Hook called when a client connects."""
        self._logger.info(f"Client connected: {client_info.client_id}")

    def on_client_disconnected(self, client_id: str) -> None:
        """Hook called when a client disconnects."""
        self._logger.info(f"Client disconnected: {client_id}")

    def on_message_received(
        self, client_id: str, message: SocketMessage
    ) -> None:
        """Hook called when a message is received from a client."""
        self._logger.debug(
            f"Message from {client_id}: {message.message_type.value}"
        )

    def get_queue_size(self) -> int:
        """Get current size of the message queue."""
        with self._queue_lock:
            return len(self._message_queue)

    def clear_queue(self) -> None:
        """Clear all queued messages."""
        with self._queue_lock:
            self._message_queue.clear()
            self._logger.debug("Message queue cleared")

    def _accept_clients(self) -> None:
        """Accept incoming client connections (runs in thread)."""
        if not self._server_socket:
            return

        while self._running:
            try:
                # Accept with timeout to allow checking _running flag
                self._server_socket.settimeout(1.0)
                client_socket, _ = self._server_socket.accept()

                # Check if we can accept more clients
                with self._clients_lock:
                    if len(self._clients) >= self._max_connections:
                        self._logger.warning(
                            f"Max connections reached "
                            f"({self._max_connections}), "
                            f"rejecting client"
                        )
                        client_socket.close()
                        continue

                    # Generate client ID
                    client_id = f"client_{get_timestamp_ms()}"
                    self._clients[client_id] = client_socket

                # Call connection hook
                client_info = ClientInfo(
                    client_id=client_id,
                    connected_at=get_timestamp_ms(),
                    address=str(self._socket_path),
                )
                self.on_client_connected(client_info)

                # Send queued messages to new client
                self._send_queued_messages(client_socket, client_id)

                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id),
                    daemon=True,
                )
                self._client_threads.append(client_thread)
                client_thread.start()

            except TimeoutError:
                # Normal timeout - continue loop
                continue
            except Exception as e:
                if self._running:
                    self._logger.error(f"Error accepting client: {e}")

    def _send_queued_messages(
        self, client_socket: socket.socket, client_id: str
    ) -> None:
        """Send queued messages to newly connected client."""
        with self._queue_lock:
            if not self._message_queue:
                return

            self._logger.debug(
                f"Sending {len(self._message_queue)} "
                f"queued messages to {client_id}"
            )

            for message in self._message_queue:
                try:
                    msg_dict = message.to_dict()
                    packed_data = msgpack.packb(msg_dict)
                    length = len(packed_data)
                    client_socket.sendall(
                        length.to_bytes(4, "big") + packed_data
                    )
                except Exception as e:
                    self._logger.error(f"Failed to send queued message: {e}")

    def _handle_client(
        self, client_socket: socket.socket, client_id: str
    ) -> None:
        """Handle communication with a connected client."""
        try:
            while self._running:
                # Receive length prefix (4 bytes)
                length_data = self._recv_exact(client_socket, 4)
                if not length_data:
                    break

                length = int.from_bytes(length_data, "big")

                # Receive message data
                msg_data = self._recv_exact(client_socket, length)
                if not msg_data:
                    break

                # Deserialize message
                try:
                    msg_dict = msgpack.unpackb(msg_data, raw=False)
                    message = SocketMessage.from_dict(msg_dict)

                    # Call message received hook
                    self.on_message_received(client_id, message)

                except Exception as e:
                    self._logger.error(f"Failed to deserialize message: {e}")

        except Exception as e:
            self._logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up client
            with self._clients_lock:
                if client_id in self._clients:
                    del self._clients[client_id]

            with contextlib.suppress(Exception):
                client_socket.close()

            self.on_client_disconnected(client_id)

    def _recv_exact(
        self, client_socket: socket.socket, num_bytes: int
    ) -> bytes:
        """Receive exact number of bytes from socket."""
        data = b""
        while len(data) < num_bytes:
            chunk = client_socket.recv(num_bytes - len(data))
            if not chunk:
                return b""
            data += chunk
        return data
