"""Dotfiles Manager - Central control point for dotfiles system.

Provides a flexible framework for managing wallpapers, system attributes,
and executing hooks.

Usage:
    from dotfiles_manager.container import Container

    # Initialize container
    container = Container.initialize()

    # Get services
    wallpaper_service = container.wallpaper_service()
    wallpaper_service.change_wallpaper(Path("~/wallpaper.png"), "DP-1")
"""

# Container
from dotfiles_manager.container import Container

# Models
from dotfiles_manager.models import (
    HookContext,
    HookResult,
    SystemAttributes,
    WallpaperState,
)

# Services
from dotfiles_manager.services import WallpaperService, WlogoutService

__all__ = [
    # Container
    "Container",
    # Models
    "HookContext",
    "HookResult",
    "SystemAttributes",
    "WallpaperState",
    # Services
    "WallpaperService",
    "WlogoutService",
]

__version__ = "0.1.0"
