"""Configuration models for hyprpaper manager."""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class HyprpaperConfig(BaseModel):
    """Hyprpaper configuration."""

    # Config file location
    config_file: Path = Field(
        default=Path.home() / ".config/hypr/hyprpaper.conf",
        description="Path to hyprpaper config file",
    )

    # IPC settings
    ipc_enabled: bool = Field(default=True, description="Enable IPC control")
    ipc_timeout: int = Field(
        default=5,
        description="Default IPC command timeout in seconds",
        gt=0,
    )
    ipc_retry_attempts: int = Field(
        default=3,
        description="Number of retry attempts for transient IPC failures",
        ge=1,
    )
    ipc_retry_delay: float = Field(
        default=0.5,
        description=(
            "Initial delay between retries in seconds (exponential backoff)"
        ),
        gt=0,
    )
    ipc_startup_wait: float = Field(
        default=2.0,
        description="Maximum time to wait for hyprpaper socket on startup",
        gt=0,
    )

    # Splash settings
    splash_enabled: bool = Field(
        default=False, description="Enable Hyprland splash"
    )
    splash_offset: float = Field(
        default=2.0, description="Splash offset (% of height)"
    )
    splash_color: str = Field(
        default="55ffffff", description="Splash color (ARGB)"
    )

    # Wallpaper directories
    wallpaper_dirs: list[Path] = Field(
        default_factory=lambda: [
            Path.home() / "Pictures/wallpapers",
            Path.home() / "wallpapers",
        ],
        description="Directories to search for wallpapers",
    )

    # Behavior
    auto_unload_unused: bool = Field(
        default=True, description="Automatically unload unused wallpapers"
    )

    auto_create_config: bool = Field(
        default=True,
        description="Automatically create config file if it doesn't exist",
    )

    # Memory management
    max_preload_pool_mb: int = Field(
        default=100,
        description="Maximum memory (MB) for preloaded wallpapers pool",
        gt=0,
    )

    max_wallpaper_size_multiplier: float = Field(
        default=2.0,
        description="Max single wallpaper size = pool_size * multiplier",
        gt=0,
    )

    @field_validator("wallpaper_dirs", mode="before")
    @classmethod
    def expand_paths(cls, v: list[Path | str]) -> list[Path]:
        """Expand ~ in paths."""
        return [Path(p).expanduser() for p in v]

    @field_validator("config_file", mode="before")
    @classmethod
    def expand_config_path(cls, v: Path | str) -> Path:
        """Expand ~ in config file path."""
        return Path(v).expanduser()


class AppConfig(BaseModel):
    """Application configuration."""

    hyprpaper: HyprpaperConfig = Field(default_factory=HyprpaperConfig)
