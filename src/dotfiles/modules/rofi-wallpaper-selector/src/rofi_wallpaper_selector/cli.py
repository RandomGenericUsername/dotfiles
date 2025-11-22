"""CLI interface for rofi-wallpaper-selector."""

import os
from pathlib import Path

import typer

from rofi_wallpaper_selector.config.config import load_config
from rofi_wallpaper_selector.handlers.effect_handler import (
    handle_effect_selection,
)
from rofi_wallpaper_selector.handlers.wallpaper_handler import (
    handle_wallpaper_selection,
)
from rofi_wallpaper_selector.selectors.effect_selector import list_effects
from rofi_wallpaper_selector.selectors.wallpaper_selector import (
    list_wallpapers,
)

app = typer.Typer(
    help="Rofi wallpaper and effect selector",
    add_completion=False,
)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def wallpapers(
    _ctx: typer.Context,
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
    - ROFI_RETV=1: Handle selection (passed as extra argument)

    Examples:
        # List wallpapers (called by rofi)
        $ ROFI_RETV=0 rofi-wallpaper-selector wallpapers

        # Handle selection (called by rofi)
        $ ROFI_RETV=1 rofi-wallpaper-selector wallpapers mountain

    Note:
        Rofi passes the selected item as an extra argument, not via stdin.
    """
    config = load_config(config_file)
    rofi_retv = os.environ.get("ROFI_RETV", "0")

    if rofi_retv == "0":
        # List wallpapers
        list_wallpapers(config)
    elif rofi_retv == "1":
        # Handle selection - rofi passes selection as extra argument
        # Get the extra arguments from context
        if _ctx.args:
            selected = _ctx.args[0]
            # Extract label from rofi format (label\x00icon\x1f/path)
            # Rofi may send back the full string, we only want the label part
            label = selected.split("\x00")[0]
            handle_wallpaper_selection(
                selected=label,
                config=config,
                monitor=monitor or config.wallpaper.default_monitor,
            )


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def effects(
    _ctx: typer.Context,
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
    - ROFI_RETV=1: Handle selection (passed as extra argument)

    Examples:
        # List effects (called by rofi)
        $ ROFI_RETV=0 rofi-wallpaper-selector effects

        # Handle selection (called by rofi)
        $ ROFI_RETV=1 rofi-wallpaper-selector effects blur

    Note:
        Rofi passes the selected item as an extra argument, not via stdin.
    """
    config = load_config(config_file)
    rofi_retv = os.environ.get("ROFI_RETV", "0")

    if rofi_retv == "0":
        # List effects
        list_effects(config, monitor or config.wallpaper.default_monitor)
    elif rofi_retv == "1":
        # Handle selection - rofi passes selection as extra argument
        # Get the extra arguments from context
        if _ctx.args:
            selected = _ctx.args[0]
            # Extract label from rofi format (label\x00icon\x1f/path)
            # Rofi may send back the full string, we only want the label part
            label = selected.split("\x00")[0]
            handle_effect_selection(
                selected=label,
                config=config,
                monitor=monitor or config.wallpaper.default_monitor,
            )


if __name__ == "__main__":
    app()
