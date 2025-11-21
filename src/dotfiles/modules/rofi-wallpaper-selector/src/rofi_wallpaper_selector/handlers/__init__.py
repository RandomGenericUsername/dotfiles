"""Handlers module - processes selections from rofi."""

from rofi_wallpaper_selector.handlers.effect_handler import handle_effect_selection
from rofi_wallpaper_selector.handlers.wallpaper_handler import (
    handle_wallpaper_selection,
)

__all__ = ["handle_effect_selection", "handle_wallpaper_selection"]
