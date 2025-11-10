"""Configuration models for state manager."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class SQLiteConfig(BaseModel):
    """SQLite backend configuration."""

    db_path: Path = Field(
        default=Path.home() / ".local/share/dotfiles/state.db",
        description="Path to SQLite database file",
    )
    wal_mode: bool = Field(
        default=True,
        description="Enable WAL mode for better concurrency",
    )
    auto_cleanup_enabled: bool = Field(
        default=True,
        description="Enable automatic cleanup of expired keys",
    )
    cleanup_interval_days: int = Field(
        default=7,
        description="Days between automatic cleanup runs",
    )


class RedisConfig(BaseModel):
    """Redis backend configuration."""

    host: str = Field(
        default="localhost",
        description="Redis server host",
    )
    port: int = Field(
        default=6379,
        description="Redis server port",
    )
    db: int = Field(
        default=0,
        description="Redis database number",
    )
    password: str = Field(
        default="",
        description="Redis password (if required)",
    )
    max_connections: int = Field(
        default=10,
        description="Maximum connections in pool",
    )
    socket_timeout: int = Field(
        default=5,
        description="Socket timeout in seconds",
    )
    socket_connect_timeout: int = Field(
        default=5,
        description="Socket connect timeout in seconds",
    )
    key_prefix: str = Field(
        default="dotfiles:",
        description="Prefix for all state manager keys",
    )
    default_ttl: int = Field(
        default=0,
        description="Default TTL for keys (0 = no expiration)",
    )


class StateManagerConfig(BaseModel):
    """State manager configuration."""

    backend: Literal["sqlite", "redis"] = Field(
        default="sqlite",
        description="Backend to use for state persistence",
    )
    state_dir: Path = Field(
        default=Path.home() / ".local/share/dotfiles",
        description="State directory (for file-based backends)",
    )
    sqlite: SQLiteConfig = Field(
        default_factory=SQLiteConfig,
        description="SQLite backend configuration",
    )
    redis: RedisConfig = Field(
        default_factory=RedisConfig,
        description="Redis backend configuration",
    )


class AppConfig(BaseModel):
    """Application configuration matching dynaconf structure."""

    state_manager: StateManagerConfig = Field(
        default_factory=StateManagerConfig,
        description="State manager configuration",
    )

