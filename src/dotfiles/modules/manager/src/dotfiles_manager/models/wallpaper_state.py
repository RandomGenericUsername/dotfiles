"""Wallpaper state model."""

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field


class WallpaperState(BaseModel):
    """Current wallpaper state for a monitor.

    Attributes:
        monitor: Monitor name (e.g., "DP-1")
        wallpaper_path: Path to current wallpaper
        last_changed: Timestamp of last wallpaper change
        from_cache: Whether wallpaper was loaded from cache
    """

    monitor: str = Field(
        description="Monitor name",
    )
    wallpaper_path: Path = Field(
        description="Path to current wallpaper",
    )
    last_changed: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp of last wallpaper change",
    )
    from_cache: bool = Field(
        default=False,
        description="Whether wallpaper was loaded from cache",
    )
