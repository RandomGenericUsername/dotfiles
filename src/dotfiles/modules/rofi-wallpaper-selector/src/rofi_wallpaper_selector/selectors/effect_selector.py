"""Effect selector - lists available effects for current wallpaper."""

from rofi_wallpaper_selector.config.config import AppConfig
from rofi_wallpaper_selector.utils.effects_cache import get_available_effects
from rofi_wallpaper_selector.utils.manager_client import ManagerClient
from rofi_wallpaper_selector.utils.rofi_formatter import format_rofi_item


def list_effects(config: AppConfig, monitor: str) -> None:
    """List all available effects for current wallpaper.

    This function queries the dotfiles-manager for the current wallpaper,
    then scans the effects cache directory for generated effects. It always
    includes an "off" option to revert to the original wallpaper.

    Args:
        config: Application configuration
        monitor: Monitor name

    Output:
        Prints effect list to stdout in rofi format:
        - "off" option (always first)
        - Generated effects with thumbnails (if show_icons enabled)
    """
    # Get current wallpaper from manager
    manager = ManagerClient(config.paths.dotfiles_manager_path)
    current_wallpaper = manager.get_current_wallpaper(monitor)

    if not current_wallpaper:
        print("No wallpaper set")
        return

    wallpaper_name = current_wallpaper.stem

    # Get available effects from cache directory
    effects = get_available_effects(
        wallpaper_name, config.paths.effects_cache_dir
    )

    if not effects:
        print(
            "No effects available yet. Select a wallpaper first to generate effects."
        )
        return

    # Always include "off" option to revert to original
    print(format_rofi_item("off", None) if config.rofi.show_icons else "off")

    # Output effects in rofi format
    for effect_name in effects:
        effect_path = (
            config.paths.effects_cache_dir
            / wallpaper_name
            / f"{effect_name}.png"
        )
        if config.rofi.show_icons:
            print(format_rofi_item(effect_name, str(effect_path)))
        else:
            print(effect_name)
