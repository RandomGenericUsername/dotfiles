#!/usr/bin/env python3
"""CLI tool for hyprpaper-manager."""

from __future__ import annotations

import builtins
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.config.settings import get_default_config
from hyprpaper_manager.core.exceptions import HyprpaperError
from hyprpaper_manager.core.types import WallpaperMode

app = typer.Typer(
    help="Hyprpaper wallpaper manager",
    no_args_is_help=True,
)
console = Console()


def _create_manager(
    wallpaper_dirs: list[str] | None = None,
) -> HyprpaperManager:
    """Create HyprpaperManager with optional custom wallpaper directories.

    Args:
        wallpaper_dirs: Optional list of wallpaper directory paths

    Returns:
        Configured HyprpaperManager instance
    """
    if wallpaper_dirs:
        # Load default config and override wallpaper_dirs
        base_config = get_default_config().hyprpaper
        config = HyprpaperConfig(
            config_file=base_config.config_file,
            ipc_enabled=base_config.ipc_enabled,
            splash_enabled=base_config.splash_enabled,
            splash_offset=base_config.splash_offset,
            splash_color=base_config.splash_color,
            wallpaper_dirs=[Path(d).expanduser() for d in wallpaper_dirs],
            auto_unload_unused=base_config.auto_unload_unused,
            auto_create_config=base_config.auto_create_config,
            max_preload_pool_mb=base_config.max_preload_pool_mb,
            max_wallpaper_size_multiplier=base_config.max_wallpaper_size_multiplier,
        )
        return HyprpaperManager(config)
    return HyprpaperManager()


@app.command()
def status() -> None:
    """Show hyprpaper status."""
    try:
        manager = HyprpaperManager()

        if not manager.is_running():
            console.print("[red]hyprpaper is not running[/red]")
            raise typer.Exit(1)

        status_info = manager.get_status()

        # Loaded wallpapers
        console.print("\n[bold]Loaded Wallpapers:[/bold]")
        if status_info.loaded_wallpapers:
            for wp in status_info.loaded_wallpapers:
                console.print(f"  • {wp}")
        else:
            console.print("  [dim]None[/dim]")

        # Active wallpapers
        console.print("\n[bold]Active Wallpapers:[/bold]")
        if status_info.active_wallpapers:
            table = Table()
            table.add_column("Monitor")
            table.add_column("Wallpaper")
            for monitor, wp in status_info.active_wallpapers.items():
                table.add_row(monitor, str(wp))
            console.print(table)
        else:
            console.print("  [dim]None[/dim]")

        # Monitors
        console.print("\n[bold]Monitors:[/bold]")
        if status_info.monitors:
            mon_table = Table()
            mon_table.add_column("Name")
            mon_table.add_column("Focused")
            for mon in status_info.monitors:
                mon_table.add_row(
                    mon.name,
                    "✓" if mon.focused else "",
                )
            console.print(mon_table)
        else:
            console.print("  [dim]None[/dim]")

    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def set(
    wallpaper: Annotated[str, typer.Argument(help="Wallpaper path or name")],
    monitor: Annotated[
        str, typer.Option("--monitor", "-m", help="Monitor name or 'all'")
    ] = "all",
    mode: Annotated[
        WallpaperMode,
        typer.Option("--mode", help="Display mode"),
    ] = WallpaperMode.COVER,
    wallpaper_dir: Annotated[
        builtins.list[str],
        typer.Option(
            "--wallpaper-dir",
            "-d",
            help="Wallpaper directory (can be specified multiple times)",
        ),
    ] = None,
) -> None:
    """Set wallpaper."""
    try:
        manager = _create_manager(wallpaper_dir)
        manager.set_wallpaper(wallpaper, monitor, mode)
        console.print(f"[green]✓[/green] Set wallpaper: {wallpaper}")
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def random(
    monitor: Annotated[
        str, typer.Option("--monitor", "-m", help="Monitor name or 'all'")
    ] = "all",
    mode: Annotated[
        WallpaperMode,
        typer.Option("--mode", help="Display mode"),
    ] = WallpaperMode.COVER,
    wallpaper_dir: Annotated[
        builtins.list[str],
        typer.Option(
            "--wallpaper-dir",
            "-d",
            help="Wallpaper directory (can be specified multiple times)",
        ),
    ] = None,
) -> None:
    """Set random wallpaper."""
    try:
        manager = _create_manager(wallpaper_dir)
        wallpaper = manager.set_random_wallpaper(monitor, mode)
        console.print(
            f"[green]✓[/green] Set random wallpaper: {wallpaper.name}"
        )
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def list(
    wallpaper_dir: Annotated[
        builtins.list[str],
        typer.Option(
            "--wallpaper-dir",
            "-d",
            help="Wallpaper directory (can be specified multiple times)",
        ),
    ] = None,
) -> None:
    """List available wallpapers."""
    try:
        manager = _create_manager(wallpaper_dir)
        wallpapers = manager.list_wallpapers()

        if not wallpapers:
            console.print("[yellow]No wallpapers found[/yellow]")
            return

        console.print(f"\n[bold]Found {len(wallpapers)} wallpapers:[/bold]\n")
        for wp in wallpapers:
            console.print(f"  • {wp.name}")
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def monitors() -> None:
    """List monitors."""
    try:
        manager = HyprpaperManager()
        monitors_list = manager.get_monitors()

        if not monitors_list:
            console.print("[yellow]No monitors found[/yellow]")
            return

        table = Table(title="Monitors")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Focused")
        table.add_column("Current Wallpaper")

        for mon in monitors_list:
            table.add_row(
                mon.name,
                mon.description or "-",
                "✓" if mon.focused else "",
                (
                    str(mon.current_wallpaper.name)
                    if mon.current_wallpaper
                    else "-"
                ),
            )

        console.print(table)
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def preload(
    wallpaper: Annotated[str, typer.Argument(help="Wallpaper path or name")],
    wallpaper_dir: Annotated[
        builtins.list[str],
        typer.Option(
            "--wallpaper-dir",
            "-d",
            help="Wallpaper directory (can be specified multiple times)",
        ),
    ] = None,
) -> None:
    """Preload wallpaper into memory."""
    try:
        manager = _create_manager(wallpaper_dir)
        manager.preload_wallpaper(wallpaper)
        console.print(f"[green]✓[/green] Preloaded: {wallpaper}")
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def unload(
    wallpaper: Annotated[
        str,
        typer.Argument(help="Wallpaper path/name, 'all', or 'unused'"),
    ],
    wallpaper_dir: Annotated[
        builtins.list[str],
        typer.Option(
            "--wallpaper-dir",
            "-d",
            help="Wallpaper directory (can be specified multiple times)",
        ),
    ] = None,
) -> None:
    """Unload wallpaper(s) from memory."""
    try:
        manager = _create_manager(wallpaper_dir)
        manager.unload_wallpaper(wallpaper)
        console.print(f"[green]✓[/green] Unloaded: {wallpaper}")
    except HyprpaperError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def main() -> None:
    """Entry point."""
    app()


if __name__ == "__main__":
    main()
