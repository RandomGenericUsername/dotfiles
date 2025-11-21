"""Wallpaper selector - lists available wallpapers."""

from pathlib import Path

from rofi_wallpaper_selector.config.config import AppConfig
from rofi_wallpaper_selector.utils.rofi_formatter import format_rofi_item


def list_wallpapers(config: AppConfig) -> None:
    """List all available wallpapers in rofi format.

    This function scans the wallpapers directory for image files and outputs
    them in rofi's expected format. When show_icons is enabled, each wallpaper
    is displayed with its thumbnail.

    Args:
        config: Application configuration

    Output:
        Prints wallpaper list to stdout in rofi format:
        - With icons: "name\\x00icon\\x1f/path/to/image.png"
        - Without icons: "name"
    """
    wallpapers_dir = config.paths.wallpapers_dir

    if not wallpapers_dir.exists():
        print("No wallpapers directory found")
        return

    # Get all image files
    wallpapers = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        wallpapers.extend(wallpapers_dir.glob(ext))

    if not wallpapers:
        print("No wallpapers found")
        return

    # Sort by name
    wallpapers.sort(key=lambda p: p.stem)

    # Output in rofi format
    for wallpaper in wallpapers:
        if config.rofi.show_icons:
            # Format: label\x00icon\x1f/path/to/icon
            print(format_rofi_item(wallpaper.stem, str(wallpaper)))
        else:
            print(wallpaper.stem)
