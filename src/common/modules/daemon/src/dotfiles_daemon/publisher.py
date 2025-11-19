"""Publisher client for sending events to daemon."""

import asyncio

from dotfiles_event_protocol import Message

from .config import DaemonConfig
from .logger import Logger


class DaemonPublisher:
    """Client for publishing events to the daemon.

    Features:
    - Non-blocking connection with timeout
    - Fire-and-forget message sending
    - Graceful degradation if daemon unavailable
    """

    def __init__(
        self,
        config: DaemonConfig | None = None,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the publisher.

        Args:
            config: Daemon configuration (uses defaults if None)
            logger: Logger instance (creates default if None)
        """
        self.config = config or DaemonConfig()
        self.logger = logger or Logger(name="daemon-publisher")
        self._writer: asyncio.StreamWriter | None = None
        self._reader: asyncio.StreamReader | None = None
        self._connected = False

    async def connect(self, timeout: float | None = None) -> bool:
        """Connect to the daemon.

        Args:
            timeout: Connection timeout in seconds (uses config default if None)

        Returns:
            True if connected, False if connection failed
        """
        if self._connected:
            return True

        timeout = timeout or self.config.connection_timeout
        socket_path = self.config.get_command_socket_path()

        try:
            self.logger.debug(f"Connecting to daemon at {socket_path}")

            # Try to connect with timeout
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_unix_connection(str(socket_path)),
                timeout=timeout,
            )

            self._connected = True
            self.logger.info("Connected to daemon")
            return True

        except asyncio.TimeoutError:
            self.logger.warning(
                f"Connection to daemon timed out after {timeout}s"
            )
            return False
        except FileNotFoundError:
            self.logger.warning(f"Daemon socket not found: {socket_path}")
            return False
        except Exception as e:
            self.logger.warning(f"Failed to connect to daemon: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the daemon."""
        if not self._connected:
            return

        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()

        self._writer = None
        self._reader = None
        self._connected = False
        self.logger.info("Disconnected from daemon")

    async def publish(self, message: Message) -> bool:
        """Publish a message to the daemon.

        Automatically connects if not connected. If connection fails,
        logs warning and returns False (graceful degradation).

        Args:
            message: Message to publish

        Returns:
            True if message sent successfully, False otherwise
        """
        # Ensure connected
        if not self._connected:
            if not await self.connect():
                return False

        try:
            # Serialize message
            data = message.model_dump_json().encode("utf-8")

            # Send message
            if self._writer:
                self._writer.write(
                    len(data).to_bytes(4, "big")
                )  # Length prefix
                self._writer.write(data)
                await self._writer.drain()

            self.logger.debug(
                f"Published {message.event_type} event to daemon"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")
            self._connected = False
            return False

    async def __aenter__(self) -> "DaemonPublisher":
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.disconnect()
