"""TCP socket server implementation."""

import contextlib
import logging
import socket
import threading
from collections import deque

import msgpack

from dotfiles_socket.config import (
    get_generic_socket_config,
    get_tcp_socket_config,
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


class TcpSocketServer(SocketServer):
    """TCP socket server implementation."""

    def __init__(
        self,
        event_name: str,
        host: str | None = None,
        port: int | None = None,
        port_range_start: int | None = None,
        port_range_end: int | None = None,
        blocking_mode: bool | None = None,
        allow_client_send: bool | None = None,
        max_connections: int | None = None,
        message_queue_size: int | None = None,
    ) -> None:
        """Initialize TCP socket server.

        Args:
            event_name: Event identifier for this server
            host: Host to bind to (default from config)
            port: Specific port to use (overrides port range)
            port_range_start: Start of port range (default from config)
            port_range_end: End of port range (default from config)
            blocking_mode: Run in blocking mode (default from config)
            allow_client_send: Allow clients to send (default from config)
            max_connections: Max concurrent clients (default from config)
            message_queue_size: Max queued messages (default from config)

        Raises:
            ValidationError: If event_name is invalid
        """
        validate_event_name(event_name)
        self._event_name = event_name
        self._logger = logging.getLogger(__name__)

        # Load config
        generic_config = get_generic_socket_config()
        tcp_config = get_tcp_socket_config()

        # Set configuration
        self._host = host or tcp_config.host
        self._port = port
        self._port_range_start = (
            port_range_start
            if port_range_start is not None
            else tcp_config.port_range_start
        )
        self._port_range_end = (
            port_range_end
            if port_range_end is not None
            else tcp_config.port_range_end
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
            else tcp_config.max_connections
        )
        self._message_queue_size = (
            message_queue_size
            if message_queue_size is not None
            else generic_config.message_queue_size
        )
        self._buffer_size = generic_config.buffer_size

        # Server state
        self._actual_port: int | None = None
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

    @property
    def port(self) -> int | None:
        """Get the actual port the server is bound to."""
        return self._actual_port

    def start(self) -> None:
        """Start the socket server."""
        if self._running:
            self._logger.warning(
                f"Server for '{self._event_name}' already running"
            )
            return

        try:
            # Create TCP socket
            self._server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM
            )
            self._server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
            )

            # Bind to port
            if self._port is not None:
                # Use specific port
                self._server_socket.bind((self._host, self._port))
                self._actual_port = self._port
            else:
                # Try port range
                bound = False
                for port in range(
                    self._port_range_start, self._port_range_end + 1
                ):
                    try:
                        self._server_socket.bind((self._host, port))
                        self._actual_port = port
                        bound = True
                        break
                    except OSError:
                        continue

                if not bound:
                    raise SocketError(
                        f"No available port in range "
                        f"{self._port_range_start}-{self._port_range_end}"
                    )

            self._server_socket.listen(self._max_connections)
            self._running = True

            self._logger.info(
                f"TCP socket server started: {self._host}:{self._actual_port}"
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
        self._logger.info(
            f"Stopping TCP socket server: {self._host}:{self._actual_port}"
        )

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

        # Wait for threads to finish
        for thread in self._client_threads:
            if thread.is_alive():
                thread.join(timeout=1.0)

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=1.0)

        self._logger.info("TCP socket server stopped")

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
                    address=f"{self._host}:{self._actual_port}",
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
        """Accept incoming client connections."""
        if not self._server_socket:
            return

        while self._running:
            try:
                # Accept new connection
                client_socket, address = self._server_socket.accept()

                # Check max connections
                with self._clients_lock:
                    if len(self._clients) >= self._max_connections:
                        self._logger.warning(
                            f"Max connections reached, rejecting {address}"
                        )
                        client_socket.close()
                        continue

                    # Generate client ID
                    client_id = f"client_{get_timestamp_ms()}"
                    self._clients[client_id] = client_socket

                # Create client info
                client_info = ClientInfo(
                    client_id=client_id,
                    connected_at=get_timestamp_ms(),
                    address=f"{address[0]}:{address[1]}",
                )

                # Call connection hook
                self.on_client_connected(client_info)

                # Send queued messages to new client
                with self._queue_lock:
                    if self._message_queue:
                        for msg in self._message_queue:
                            try:
                                msg_dict = msg.to_dict()
                                packed_data = msgpack.packb(msg_dict)
                                self._send_to_client(
                                    client_socket, packed_data, client_id
                                )
                            except Exception as e:
                                self._logger.error(
                                    f"Failed to send queued message: {e}"
                                )

                # Start client handler thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_id),
                    daemon=True,
                )
                client_thread.start()
                self._client_threads.append(client_thread)

            except Exception as e:
                if self._running:
                    self._logger.error(f"Error accepting client: {e}")

    def _handle_client(
        self, client_socket: socket.socket, client_id: str
    ) -> None:
        """Handle communication with a connected client."""
        try:
            while self._running:
                # Read length prefix (4 bytes)
                length_data = self._recv_exact(client_socket, 4)
                if not length_data:
                    break

                length = int.from_bytes(length_data, "big")

                # Read message data
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
                    self._logger.error(
                        f"Failed to deserialize message from {client_id}: {e}"
                    )

        except Exception as e:
            self._logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Remove client
            with self._clients_lock:
                if client_id in self._clients:
                    del self._clients[client_id]

            # Close socket
            with contextlib.suppress(Exception):
                client_socket.close()

            # Call disconnection hook
            self.on_client_disconnected(client_id)

    def _recv_exact(
        self, client_socket: socket.socket, num_bytes: int
    ) -> bytes:
        """Receive exactly num_bytes from socket."""
        data = b""
        while len(data) < num_bytes:
            chunk = client_socket.recv(num_bytes - len(data))
            if not chunk:
                return b""
            data += chunk
        return data
