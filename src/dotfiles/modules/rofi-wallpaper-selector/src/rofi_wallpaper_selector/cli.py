"""CLI interface for rofi-wallpaper-selector."""

import os
import sys
from pathlib import Path

import typer

from rofi_wallpaper_selector.config.config import load_config
from rofi_wallpaper_selector.handlers.effect_handler import handle_effect_selection
from rofi_wallpaper_selector.handlers.wallpaper_handler import (
    handle_wallpaper_selection,
)
from rofi_wallpaper_selector.selectors.effect_selector import list_effects
from rofi_wallpaper_selector.selectors.wallpaper_selector import list_wallpapers

app = typer.Typer(
    help="Rofi wallpaper and effect selector",
    add_completion=False,
)


@app.command()
def wallpapers(
    monitor: str = typer.Option(
        None, "--monitor", "-m", help="Monitor to set wallpaper on"
    ),
    config_file: Path = typer.Option(
        None, "--config", "-c", help="Path to settings.toml"
    ),
):
    """List wallpapers or handle wallpaper selection.

    Called by rofi in script mode:
    - ROFI_RETV=0: List wallpapers
    - ROFI_RETV=1: Handle selection (stdin contains selected item)

    Examples:
        # List wallpapers (called by rofi)
        $ ROFI_RETV=0 rofi-wallpaper-selector wallpapers

        # Handle selection (called by rofi)
        $ echo "mountain" | ROFI_RETV=1 rofi-wallpaper-selector wallpapers
    """
    config = load_config(config_file)
    rofi_retv = os.environ.get("ROFI_RETV", "0")

    if rofi_retv == "0":
        # List wallpapers
        list_wallpapers(config)
    elif rofi_retv == "1":
        # Handle selection
        selected = sys.stdin.read().strip()
        if selected:
            handle_wallpaper_selection(
                selected=selected,
                config=config,
                monitor=monitor or config.wallpaper.default_monitor,
            )


@app.command()
def effects(
    monitor: str = typer.Option(
        None, "--monitor", "-m", help="Monitor to set wallpaper on"
    ),
    config_file: Path = typer.Option(
        None, "--config", "-c", help="Path to settings.toml"
    ),
):
    """List effects or handle effect selection.

    Called by rofi in script mode:
    - ROFI_RETV=0: List effects for current wallpaper
    - ROFI_RETV=1: Handle selection (stdin contains selected item)

    Examples:
        # List effects (called by rofi)
        $ ROFI_RETV=0 rofi-wallpaper-selector effects

        # Handle selection (called by rofi)
        $ echo "blur" | ROFI_RETV=1 rofi-wallpaper-selector effects
    """
    config = load_config(config_file)
    rofi_retv = os.environ.get("ROFI_RETV", "0")

    if rofi_retv == "0":
        # List effects
        list_effects(config, monitor or config.wallpaper.default_monitor)
    elif rofi_retv == "1":
        # Handle selection
        selected = sys.stdin.read().strip()
        if selected:
            handle_effect_selection(
                selected=selected,
                config=config,
                monitor=monitor or config.wallpaper.default_monitor,
            )


if __name__ == "__main__":
    app()
