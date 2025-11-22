"""Effect handler - processes effect selection."""

import subprocess

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

    The wallpaper change is run in the background so rofi can close immediately.

    Args:
        selected: Selected effect name (or "off" for original)
        config: Application configuration
        monitor: Monitor name

    Note:
        When selecting an effect, ONLY colorscheme is regenerated
        (generate_colorscheme=True, generate_effects=False) because
        the effects already exist in the cache.
    """
    try:
        manager = ManagerClient(config.paths.dotfiles_manager_cli)

        # Get current wallpaper state
        current_state = manager.get_current_wallpaper_state(monitor)
        if not current_state:
            print("Error: No wallpaper set", flush=True)
            return

        # Get original wallpaper path from state
        original_wallpaper = current_state["original_wallpaper_path"]
        wallpaper_name = original_wallpaper.stem

        # Handle "off" - revert to original wallpaper
        if selected == "off":
            wallpaper_path = original_wallpaper
        else:
            # Get effect path
            wallpaper_path = (
                config.paths.effects_cache_dir
                / wallpaper_name
                / f"{selected}.png"
            )

            if not wallpaper_path.exists():
                print(f"Error: Effect not found: {selected}", flush=True)
                return

        # Build command to change wallpaper
        cmd = [
            str(config.paths.dotfiles_manager_cli),
            "change-wallpaper",
            str(wallpaper_path),
            "--monitor",
            monitor,
            "--effect",
            selected,
            "--original-wallpaper",
            str(original_wallpaper),
        ]

        # Add colorscheme flag
        if config.wallpaper.auto_generate_colorscheme:
            cmd.append("--colorscheme")
        else:
            cmd.append("--no-colorscheme")

        # IMPORTANT: Don't regenerate effects - they already exist!
        cmd.append("--no-effects")

        # Run in background so rofi can close immediately
        # Redirect output to /dev/null to avoid blocking
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:  # noqa: BLE001
        print(f"Error: Exception while changing wallpaper: {e}", flush=True)
