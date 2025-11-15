"""Data models for dotfiles manager."""

from dotfiles_manager.models.hook import HookContext, HookResult
from dotfiles_manager.models.system_attributes import SystemAttributes
from dotfiles_manager.models.wallpaper_state import WallpaperState

__all__ = [
    "HookContext",
    "HookResult",
    "SystemAttributes",
    "WallpaperState",
]
