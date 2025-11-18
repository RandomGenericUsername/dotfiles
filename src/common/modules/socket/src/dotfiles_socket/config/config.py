"""Configuration models for socket module."""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class SocketConfig(BaseModel):
    """Generic socket configuration."""

    socket_dir: Path = Field(
        default=Path("/tmp/sockets"),
        description="Directory for Unix domain socket files",
    )
    default_timeout: int = Field(
        default=5,
        description="Default timeout for socket operations (seconds)",
    )
    buffer_size: int = Field(
        default=4096,
        description="Buffer size for socket I/O (bytes)",
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for timestamp_iso formatting",
    )
    message_queue_size: int = Field(
        default=100,
        description="Max messages to queue when no clients connected",
    )
    blocking_mode: bool = Field(
        default=False,
        description="Server threading mode (False=non-blocking)",
    )
    allow_client_send: bool = Field(
        default=True,
        description="Allow clients to send messages back to server",
    )

    @field_validator("default_timeout", "buffer_size", "message_queue_size")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Validate that value is positive."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


class UnixSocketConfig(BaseModel):
    """Unix domain socket specific configuration."""

    max_connections: int = Field(
        default=10,
        description="Maximum number of concurrent client connections",
    )
    socket_permissions: str = Field(
        default="0600",
        description="File permissions for socket file (octal string)",
    )
    auto_remove_socket: bool = Field(
        default=True,
        description="Automatically remove socket file when server stops",
    )

    @field_validator("max_connections")
    @classmethod
    def validate_max_connections(cls, v: int) -> int:
        """Validate max_connections is positive."""
        if v <= 0:
            raise ValueError("max_connections must be positive")
        return v

    @field_validator("socket_permissions")
    @classmethod
    def validate_permissions(cls, v: str) -> str:
        """Validate socket permissions format."""
        if not v.startswith("0"):
            raise ValueError("Permissions must be octal string (e.g., '0600')")
        try:
            int(v, 8)
        except ValueError as e:
            raise ValueError(f"Invalid octal permissions: {v}") from e
        return v


class TcpSocketConfig(BaseModel):
    """TCP socket specific configuration."""

    host: str = Field(
        default="127.0.0.1",
        description="Host to bind TCP server to",
    )
    port_range_start: int = Field(
        default=9000,
        description="Start of port range for auto-assignment",
    )
    port_range_end: int = Field(
        default=9100,
        description="End of port range for auto-assignment",
    )
    max_connections: int = Field(
        default=10,
        description="Maximum number of concurrent client connections",
    )

    @field_validator("port_range_start", "port_range_end")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port is in valid range."""
        if not 1024 <= v <= 65535:
            raise ValueError("Port must be between 1024 and 65535")
        return v

    @field_validator("max_connections")
    @classmethod
    def validate_max_connections(cls, v: int) -> int:
        """Validate max_connections is positive."""
        if v <= 0:
            raise ValueError("max_connections must be positive")
        return v


class SocketModuleConfig(BaseModel):
    """Socket module configuration."""

    socket: SocketConfig = Field(
        default_factory=SocketConfig,
        description="Generic socket configuration",
    )
    unix: UnixSocketConfig = Field(
        default_factory=UnixSocketConfig,
        description="Unix socket specific configuration",
    )
    tcp: TcpSocketConfig = Field(
        default_factory=TcpSocketConfig,
        description="TCP socket specific configuration",
    )


class AppConfig(BaseModel):
    """Application configuration matching dynaconf structure."""

    socket: SocketModuleConfig = Field(
        default_factory=SocketModuleConfig,
        description="Socket module configuration",
    )
