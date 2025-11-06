"""Hyprpaper Manager - Python API for managing hyprpaper wallpapers."""

from hyprpaper_manager.core.exceptions import (
    HyprpaperError,
    HyprpaperIPCError,
    HyprpaperNotRunningError,
    MonitorNotFoundError,
    WallpaperNotFoundError,
    WallpaperNotLoadedError,
    WallpaperTooLargeError,
)
from hyprpaper_manager.core.types import (
    HyprpaperStatus,
    MonitorInfo,
    MonitorSelector,
    WallpaperInfo,
    WallpaperMode,
)
from hyprpaper_manager.manager import HyprpaperManager

__version__ = "0.1.0"

__all__ = [
    # Main manager
    "HyprpaperManager",
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
    "WallpaperTooLargeError",
]
