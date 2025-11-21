"""Effect handler - processes effect selection."""

from rofi_wallpaper_selector.config.config import AppConfig
from rofi_wallpaper_selector.utils.manager_client import ManagerClient


def handle_effect_selection(
    selected: str, config: AppConfig, monitor: str
) -> None:
    """Handle effect selection.

    This function is called when the user selects an effect from rofi.
    It finds the effect file (or original wallpaper for "off") and calls
    dotfiles-manager to change the wallpaper with ONLY colorscheme generation
    enabled (effects already exist).

    Args:
        selected: Selected effect name (or "off" for original)
        config: Application configuration
        monitor: Monitor name

    Note:
        When selecting an effect, ONLY colorscheme is regenerated
        (generate_colorscheme=True, generate_effects=False) because
        the effects already exist in the cache.
    """
    manager = ManagerClient(config.paths.dotfiles_manager_path)

    # Get current wallpaper
    current_wallpaper = manager.get_current_wallpaper(monitor)
    if not current_wallpaper:
        print("No wallpaper set")
        return

    wallpaper_name = current_wallpaper.stem

    # Handle "off" - revert to original wallpaper
    if selected == "off":
        wallpaper_path = current_wallpaper
    else:
        # Get effect path
        wallpaper_path = (
            config.paths.effects_cache_dir / wallpaper_name / f"{selected}.png"
        )

        if not wallpaper_path.exists():
            print(f"Effect not found: {selected}")
            return

    # Call dotfiles-manager to change wallpaper
    # IMPORTANT: generate_effects=False because effects already exist!
    # Only regenerate colorscheme from the effect image
    manager.change_wallpaper(
        wallpaper_path=wallpaper_path,
        monitor=monitor,
        generate_colorscheme=config.wallpaper.auto_generate_colorscheme,
        generate_effects=False,  # Don't regenerate effects!
    )
