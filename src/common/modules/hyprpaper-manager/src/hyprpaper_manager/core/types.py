"""Type definitions for hyprpaper manager."""

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class WallpaperMode(str, Enum):
    """Wallpaper display modes."""

    COVER = "cover"
    CONTAIN = "contain"
    TILE = "tile"


class MonitorSelector(str, Enum):
    """Monitor selection strategies."""

    ALL = "all"
    FOCUSED = "focused"
    SPECIFIC = "specific"


class WallpaperInfo(BaseModel):
    """Information about a wallpaper."""

    path: Path
    mode: WallpaperMode = WallpaperMode.COVER
    monitors: list[str] = Field(default_factory=list)
    is_loaded: bool = False
    is_active: bool = False


class MonitorInfo(BaseModel):
    """Information about a monitor."""

    name: str
    description: str | None = None
    focused: bool = False
    current_wallpaper: Path | None = None


class HyprpaperStatus(BaseModel):
    """Current hyprpaper status."""

    loaded_wallpapers: list[Path]
    active_wallpapers: dict[str, Path]  # monitor -> wallpaper
    monitors: list[MonitorInfo]
