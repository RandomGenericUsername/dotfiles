"""Wallpaper handler - processes wallpaper selection."""

from pathlib import Path

from rofi_wallpaper_selector.config.config import AppConfig
from rofi_wallpaper_selector.utils.manager_client import ManagerClient


def handle_wallpaper_selection(
    selected: str, config: AppConfig, monitor: str
) -> None:
    """Handle wallpaper selection.

    This function is called when the user selects a wallpaper from rofi.
    It finds the wallpaper file and calls dotfiles-manager to change the
    wallpaper with both colorscheme and effects generation enabled.

    Args:
        selected: Selected wallpaper name (without extension)
        config: Application configuration
        monitor: Monitor name

    Note:
        When selecting a wallpaper, both colorscheme AND effects are generated
        (generate_colorscheme=True, generate_effects=True).
    """
    # Find wallpaper file
    wallpaper_path = None
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = config.paths.wallpapers_dir / f"{selected}{ext}"
        if candidate.exists():
            wallpaper_path = candidate
            break

    if not wallpaper_path:
        print(f"Wallpaper not found: {selected}")
        return

    # Call dotfiles-manager to change wallpaper
    # IMPORTANT: generate_effects=True to generate all effect variants
    manager = ManagerClient(config.paths.dotfiles_manager_path)
    manager.change_wallpaper(
        wallpaper_path=wallpaper_path,
        monitor=monitor,
        generate_colorscheme=config.wallpaper.auto_generate_colorscheme,
        generate_effects=config.wallpaper.auto_generate_effects,
    )
