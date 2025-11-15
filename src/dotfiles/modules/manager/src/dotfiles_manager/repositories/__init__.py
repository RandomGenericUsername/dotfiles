"""Repositories for dotfiles manager."""

from dotfiles_manager.repositories.system_attributes import (
    SystemAttributesRepository,
)
from dotfiles_manager.repositories.wallpaper_state import (
    WallpaperStateRepository,
)

__all__ = [
    "SystemAttributesRepository",
    "WallpaperStateRepository",
]
