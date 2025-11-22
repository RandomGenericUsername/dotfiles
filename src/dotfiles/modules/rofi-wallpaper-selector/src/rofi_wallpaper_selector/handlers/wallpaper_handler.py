"""Wallpaper handler - processes wallpaper selection."""

import subprocess

from rofi_wallpaper_selector.config.config import AppConfig


def handle_wallpaper_selection(
    selected: str, config: AppConfig, monitor: str
) -> None:
    """Handle wallpaper selection.

    This function is called when the user selects a wallpaper from rofi.
    It finds the wallpaper file and calls dotfiles-manager to change the
    wallpaper with both colorscheme and effects generation enabled.

    The wallpaper change is run in the background so rofi can close immediately.

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
        print(f"Error: Wallpaper not found: {selected}", flush=True)
        return

    # Build command to change wallpaper
    cmd = [
        str(config.paths.dotfiles_manager_cli),
        "change-wallpaper",
        str(wallpaper_path),
        "--monitor",
        monitor,
    ]

    # Add colorscheme flag
    if config.wallpaper.auto_generate_colorscheme:
        cmd.append("--colorscheme")
    else:
        cmd.append("--no-colorscheme")

    # Add effects flag
    if config.wallpaper.auto_generate_effects:
        cmd.append("--effects")
    else:
        cmd.append("--no-effects")

    # Run in background so rofi can close immediately
    # Redirect output to /dev/null to avoid blocking
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
