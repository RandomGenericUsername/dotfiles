"""Main daemon implementation."""

import asyncio
import json
import signal
from typing import Any

from dotfiles_event_protocol import MessageValidator

from .config import DaemonConfig
from .event_broker import EventBroker
from .logger import Logger


class DotfilesDaemon:
    """Persistent daemon for event distribution.

    The daemon:
    1. Receives events from managers via command socket
    2. Dynamically creates event sockets based on event_type
    3. Broadcasts events to monitors via event sockets
    4. Handles queries from monitors via query socket
    """

    def __init__(
        self,
        config: DaemonConfig | None = None,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the daemon.

        Args:
            config: Daemon configuration (uses defaults if None)
            logger: Logger instance (creates default if None)
        """
        self.config = config or DaemonConfig()
        self.logger = logger or Logger(name="dotfiles-daemon")
        self.event_broker = EventBroker(config=self.config, logger=self.logger)
        self._running = False
        self._command_server: Any = None
        self._query_server: Any = None

    async def start(self) -> None:
        """Start the daemon.

        Creates socket directory, starts command and query servers,
        and begins event loop.
        """
        if self._running:
            self.logger.warning("Daemon already running")
            return

        self.logger.info("Starting dotfiles daemon")

        # Ensure socket directory exists
        self.config.ensure_socket_dir()

        # Start event broker
        await self.event_broker.start()

        # Start command socket server (receives events from managers)
        await self._start_command_server()

        # Start query socket server (receives queries from monitors)
        await self._start_query_server()

        self._running = True
        self.logger.info("Daemon started successfully")

    async def stop(self) -> None:
        """Stop the daemon.

        Stops all servers and performs cleanup.
        """
        if not self._running:
            return

        self.logger.info("Stopping dotfiles daemon")

        # Stop servers
        if self._command_server:
            await self._stop_server(self._command_server)
        if self._query_server:
            await self._stop_server(self._query_server)

        # Stop event broker
        await self.event_broker.stop()

        self._running = False
        self.logger.info("Daemon stopped")

    async def run(self) -> None:
        """Run the daemon until stopped.

        Starts the daemon and runs until SIGINT or SIGTERM received.
        """
        # Setup signal handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(self.stop())
            )

        await self.start()

        # Keep running until stopped
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()

    async def _start_command_server(self) -> None:
        """Start the command socket server."""
        socket_path = self.config.get_command_socket_path()
        self.logger.info(f"Starting command server at {socket_path}")

        # Remove existing socket file if it exists
        if socket_path.exists():
            socket_path.unlink()

        # Create Unix domain socket server
        self._command_server = await asyncio.start_unix_server(
            self._handle_command_client,
            path=str(socket_path),
        )

        self.logger.info("Command server started")

    async def _start_query_server(self) -> None:
        """Start the query socket server."""
        socket_path = self.config.get_query_socket_path()
        self.logger.info(f"Starting query server at {socket_path}")

        # Remove existing socket file if it exists
        if socket_path.exists():
            socket_path.unlink()

        # Create Unix domain socket server
        self._query_server = await asyncio.start_unix_server(
            self._handle_query_client,
            path=str(socket_path),
        )

        self.logger.info("Query server started")

    async def _stop_server(self, server: Any) -> None:
        """Stop a server."""
        server.close()
        await server.wait_closed()

    async def _handle_command_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle a command client connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        addr = writer.get_extra_info("peername")
        self.logger.debug(f"Command client connected: {addr}")

        try:
            while True:
                # Read message length (4 bytes)
                length_bytes = await reader.readexactly(4)
                message_length = int.from_bytes(length_bytes, "big")

                # Read message data
                data = await reader.readexactly(message_length)

                # Handle the command
                await self._handle_command(data)

        except asyncio.IncompleteReadError:
            self.logger.debug("Command client disconnected")
        except Exception as e:
            self.logger.error(f"Error handling command client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _handle_query_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """Handle a query client connection.

        Args:
            reader: Stream reader
            writer: Stream writer
        """
        addr = writer.get_extra_info("peername")
        self.logger.debug(f"Query client connected: {addr}")

        try:
            while True:
                # Read query length (4 bytes)
                length_bytes = await reader.readexactly(4)
                query_length = int.from_bytes(length_bytes, "big")

                # Read query data
                data = await reader.readexactly(query_length)

                # Handle the query
                response = await self._handle_query(data)

                # Send response
                writer.write(len(response).to_bytes(4, "big"))
                writer.write(response)
                await writer.drain()

        except asyncio.IncompleteReadError:
            self.logger.debug("Query client disconnected")
        except Exception as e:
            self.logger.error(f"Error handling query client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _handle_command(self, data: bytes) -> None:
        """Handle incoming command (event from manager).

        Args:
            data: Raw message data
        """
        try:
            # Parse message
            message_dict = json.loads(data.decode("utf-8"))
            message = MessageValidator.validate_message(message_dict)

            self.logger.debug(
                f"Received {message.event_type} event: {message.message_id}"
            )

            # Broadcast to event socket
            await self.event_broker.broadcast(message)

        except Exception as e:
            self.logger.error(f"Failed to handle command: {e}")

    async def _handle_query(self, data: bytes) -> bytes:
        """Handle incoming query from monitor.

        Args:
            data: Raw query data

        Returns:
            Response data
        """
        # Placeholder - will implement query handling
        return b'{"status": "ok"}'
