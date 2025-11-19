"""Event broker for managing dynamic event sockets."""

import asyncio
from typing import Any

from dotfiles_event_protocol import Message

from .config import DaemonConfig
from .logger import Logger


class EventBroker:
    """Manages dynamic event sockets and broadcasts events.

    The broker:
    1. Creates event sockets on-demand based on event_type
    2. Maintains a registry of active event sockets
    3. Broadcasts events to the appropriate socket
    """

    def __init__(
        self,
        config: DaemonConfig,
        logger: Logger,
    ) -> None:
        """Initialize the event broker.

        Args:
            config: Daemon configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self._event_servers: dict[str, Any] = {}
        self._running = False

    async def start(self) -> None:
        """Start the event broker."""
        if self._running:
            return

        self.logger.info("Starting event broker")
        self._running = True

    async def stop(self) -> None:
        """Stop the event broker and all event servers."""
        if not self._running:
            return

        self.logger.info("Stopping event broker")

        # Stop all event servers
        for event_type, server in self._event_servers.items():
            self.logger.info(f"Stopping event server for: {event_type}")
            await self._stop_event_server(server)

        self._event_servers.clear()
        self._running = False

    async def broadcast(self, message: Message) -> None:
        """Broadcast a message to the appropriate event socket.

        Creates the event socket if it doesn't exist yet.

        Args:
            message: Message to broadcast
        """
        event_type = message.event_type

        # Ensure event server exists for this event type
        if event_type not in self._event_servers:
            await self._create_event_server(event_type)

        # Broadcast to event server
        server = self._event_servers[event_type]
        await self._send_to_server(server, message)

    async def _create_event_server(self, event_type: str) -> None:
        """Create a new event server for the given event type.

        Args:
            event_type: Type of event (e.g., "wallpaper", "backup")
        """
        socket_path = self.config.get_event_socket_path(event_type)
        self.logger.info(
            f"Creating event server for '{event_type}' at {socket_path}"
        )

        # Remove existing socket file if it exists
        if socket_path.exists():
            socket_path.unlink()

        # Create Unix domain socket server
        server = await asyncio.start_unix_server(
            lambda r, w: self._handle_event_client(event_type, r, w),
            path=str(socket_path),
        )

        self._event_servers[event_type] = {
            "server": server,
            "socket_path": socket_path,
            "clients": [],
        }

        self.logger.info(f"Event server created for: {event_type}")

    async def _handle_event_client(
        self,
        event_type: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle a new event client connection.

        Args:
            event_type: Type of event
            reader: Stream reader
            writer: Stream writer
        """
        addr = writer.get_extra_info("peername")
        self.logger.info(f"New event client connected to {event_type}: {addr}")

        # Add client to list
        if event_type in self._event_servers:
            self._event_servers[event_type]["clients"].append(writer)

        try:
            # Keep connection alive (clients only receive, don't send)
            while True:
                await asyncio.sleep(1)
        except (ConnectionResetError, BrokenPipeError):
            self.logger.info(f"Event client disconnected from {event_type}")
        finally:
            # Remove client from list
            if event_type in self._event_servers:
                try:
                    self._event_servers[event_type]["clients"].remove(writer)
                except ValueError:
                    pass
            writer.close()
            await writer.wait_closed()

    async def _send_to_server(
        self, server_info: dict[str, Any], message: Message
    ) -> None:
        """Send message to all clients of an event server.

        Args:
            server_info: Server information dictionary
            message: Message to send
        """
        # Serialize message
        data = message.model_dump_json().encode("utf-8")

        # Send to all connected clients
        clients = server_info["clients"]
        for writer in clients:
            try:
                writer.write(
                    len(data).to_bytes(4, "big")
                )  # Message length prefix
                writer.write(data)
                await writer.drain()
            except Exception as e:
                self.logger.error(f"Failed to send to client: {e}")

    async def _stop_event_server(self, server_info: dict[str, Any]) -> None:
        """Stop an event server.

        Args:
            server_info: Server information dictionary
        """
        server = server_info["server"]
        socket_path = server_info["socket_path"]

        # Close server
        server.close()
        await server.wait_closed()

        # Remove socket file
        if socket_path.exists():
            socket_path.unlink()
