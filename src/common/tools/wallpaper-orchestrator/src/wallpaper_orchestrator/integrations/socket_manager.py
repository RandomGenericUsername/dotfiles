"""Socket manager for real-time progress updates."""

import logging
from pathlib import Path
from typing import Any

from dotfiles_socket import (
    MessageType,
    SocketType,
    UnixSocketServer,
    create_message,
    create_server,
)

logger = logging.getLogger(__name__)


class WallpaperProgressSocketManager:
    """Manages socket server for wallpaper orchestrator progress updates."""

    def __init__(
        self,
        event_name: str = "wallpaper_progress",
        socket_dir: str | Path | None = None,
    ):
        """Initialize socket manager.

        Args:
            event_name: Event name for the socket (default: wallpaper_progress)
            socket_dir: Directory for socket file (default: from config)
        """
        self._event_name = event_name
        self._socket_dir = socket_dir
        self._server: UnixSocketServer | None = None
        self._is_running = False

    def start(self) -> None:
        """Start the socket server."""
        if self._is_running:
            logger.warning("Socket server already running")
            return

        try:
            # Create server
            kwargs: dict[str, Any] = {"event_name": self._event_name}
            if self._socket_dir:
                kwargs["socket_dir"] = self._socket_dir

            self._server = create_server(SocketType.UNIX, **kwargs)
            self._server.start()
            self._is_running = True

            logger.info(
                f"Socket server started for event '{self._event_name}'"
            )

        except Exception as e:
            logger.error(f"Failed to start socket server: {e}")
            raise

    def stop(self) -> None:
        """Stop the socket server."""
        if not self._is_running or not self._server:
            return

        try:
            self._server.stop()
            self._is_running = False
            self._server = None
            logger.info("Socket server stopped")

        except Exception as e:
            logger.error(f"Failed to stop socket server: {e}")

    def send_progress(
        self,
        step_name: str,
        progress_percent: float,
        status: str = "processing",
        extra_data: dict[str, Any] | None = None,
    ) -> None:
        """Send progress update to connected clients.

        Args:
            step_name: Name of current step
            progress_percent: Progress percentage (0-100)
            status: Status message (processing, complete, error)
            extra_data: Additional data to include in message
        """
        if not self._is_running or not self._server:
            logger.warning(
                "Socket server not running, skipping progress update"
            )
            return

        try:
            # Build message data
            data = {
                "step": step_name,
                "progress": round(progress_percent, 2),
                "status": status,
            }

            if extra_data:
                data.update(extra_data)

            # Create and send message
            message = create_message(
                self._event_name,
                MessageType.DATA,
                data,
            )
            self._server.send(message)

            logger.debug(
                f"Progress update sent: {step_name} - {progress_percent:.1f}%"
            )

        except Exception as e:
            logger.error(f"Failed to send progress update: {e}")

    def send_error(
        self, error_message: str, step_name: str | None = None
    ) -> None:
        """Send error message to connected clients.

        Args:
            error_message: Error description
            step_name: Name of step where error occurred (optional)
        """
        if not self._is_running or not self._server:
            return

        try:
            data = {
                "error": error_message,
                "status": "error",
            }
            if step_name:
                data["step"] = step_name

            message = create_message(
                self._event_name,
                MessageType.ERROR,
                data,
            )
            self._server.send(message)

        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    def send_ready(self) -> None:
        """Send ready signal to notify clients that server is ready.

        This should be called after starting the server to allow clients
        to connect before processing begins.
        """
        if not self._is_running or not self._server:
            return

        try:
            data = {
                "status": "ready",
                "step": "Initializing",
                "progress": 0.0,
            }

            message = create_message(
                self._event_name,
                MessageType.CONTROL,
                data,
            )
            self._server.send(message)
            logger.debug("Ready signal sent to clients")

        except Exception as e:
            logger.error(f"Failed to send ready signal: {e}")

    def __enter__(self) -> "WallpaperProgressSocketManager":
        """Context manager entry."""
        self.start()
        # Send ready signal and give clients time to connect
        self.send_ready()
        # Small delay to allow clients to connect (500ms)
        import time

        time.sleep(0.5)
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Context manager exit."""
        self.stop()
