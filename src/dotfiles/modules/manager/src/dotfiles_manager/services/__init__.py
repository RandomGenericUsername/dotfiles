"""Services for dotfiles manager."""

from dotfiles_manager.services.wallpaper_service import WallpaperService
from dotfiles_manager.services.wlogout_service import WlogoutService

__all__ = [
    "WallpaperService",
    "WlogoutService",
]
