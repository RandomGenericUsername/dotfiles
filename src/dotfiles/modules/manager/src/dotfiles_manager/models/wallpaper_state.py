"""Wallpaper state model."""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class WallpaperState(BaseModel):
    """Current wallpaper state for a monitor.

    Attributes:
        monitor: Monitor name (e.g., "DP-1")
        wallpaper_path: Path to current wallpaper (could be original or effect variant)
        original_wallpaper_path: Path to original wallpaper (base image)
        current_effect: Name of current effect applied ("off" for original, or effect name like "blur")
        last_changed: Timestamp of last wallpaper change
        from_cache: Whether wallpaper was loaded from cache
    """

    monitor: str = Field(
        description="Monitor name",
    )
    wallpaper_path: Path = Field(
        description="Path to current wallpaper (could be original or effect variant)",
    )
    original_wallpaper_path: Path = Field(
        description="Path to original wallpaper (base image)",
    )
    current_effect: str = Field(
        default="off",
        description="Name of current effect applied ('off' for original)",
    )
    last_changed: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last wallpaper change",
    )
    from_cache: bool = Field(
        default=False,
        description="Whether wallpaper was loaded from cache",
    )
