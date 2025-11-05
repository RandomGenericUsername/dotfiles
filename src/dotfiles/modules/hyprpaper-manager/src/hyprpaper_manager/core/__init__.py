"""Core types and exceptions for hyprpaper manager."""

from hyprpaper_manager.core.exceptions import (
    HyprpaperError,
    HyprpaperIPCError,
    HyprpaperNotRunningError,
    MonitorNotFoundError,
    WallpaperNotFoundError,
    WallpaperNotLoadedError,
)
from hyprpaper_manager.core.types import (
    HyprpaperStatus,
    MonitorInfo,
    MonitorSelector,
    WallpaperInfo,
    WallpaperMode,
)

__all__ = [
    # Types
    "HyprpaperStatus",
    "MonitorInfo",
    "MonitorSelector",
    "WallpaperInfo",
    "WallpaperMode",
    # Exceptions
    "HyprpaperError",
    "HyprpaperIPCError",
    "HyprpaperNotRunningError",
    "MonitorNotFoundError",
    "WallpaperNotFoundError",
    "WallpaperNotLoadedError",
]
