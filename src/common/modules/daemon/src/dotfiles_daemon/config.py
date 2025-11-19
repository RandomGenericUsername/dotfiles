"""Daemon configuration."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class DaemonConfig(BaseModel):
    """Configuration for the dotfiles daemon."""

    socket_dir: Path = Field(
        default=Path.home() / ".cache" / "dotfiles" / "sockets",
        description="Directory for Unix domain sockets",
    )

    command_socket_name: str = Field(
        default="command.sock",
        description="Name of the command socket (receives events from managers)",
    )

    query_socket_name: str = Field(
        default="query.sock",
        description="Name of the query socket (receives queries from monitors)",
    )

    event_socket_suffix: str = Field(
        default="_events.sock",
        description="Suffix for event sockets (e.g., wallpaper_events.sock)",
    )

    max_message_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum message size in bytes",
    )

    connection_timeout: float = Field(
        default=5.0,
        description="Connection timeout in seconds",
    )

    def get_command_socket_path(self) -> Path:
        """Get the full path to the command socket."""
        return self.socket_dir / self.command_socket_name

    def get_query_socket_path(self) -> Path:
        """Get the full path to the query socket."""
        return self.socket_dir / self.query_socket_name

    def get_event_socket_path(self, event_type: str) -> Path:
        """Get the full path to an event socket.

        Args:
            event_type: Type of event (e.g., "wallpaper", "backup")

        Returns:
            Path to the event socket
        """
        return self.socket_dir / f"{event_type}{self.event_socket_suffix}"

    def ensure_socket_dir(self) -> None:
        """Ensure the socket directory exists."""
        self.socket_dir.mkdir(parents=True, exist_ok=True)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override model_dump to convert Path to str."""
        data = super().model_dump(**kwargs)
        data["socket_dir"] = str(data["socket_dir"])
        return data

