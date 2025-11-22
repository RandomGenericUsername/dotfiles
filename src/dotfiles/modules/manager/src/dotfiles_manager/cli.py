#!/usr/bin/env python3
"""CLI interface for dotfiles-manager."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dotfiles_manager.container import Container

app = typer.Typer(
    help="Dotfiles manager CLI",
    no_args_is_help=True,
)
console = Console()


@app.command()
def change_wallpaper(
    wallpaper_path: Annotated[
        Path,
        typer.Argument(help="Path to wallpaper image"),
    ],
    monitor: Annotated[
        str | None,
        typer.Option(
            "--monitor", "-m", help="Monitor name (default: auto-detect)"
        ),
    ] = None,
    force_rebuild: Annotated[
        bool,
        typer.Option("--force-rebuild", help="Force rebuild containers"),
    ] = False,
    colorscheme: Annotated[
        bool,
        typer.Option(
            "--colorscheme/--no-colorscheme",
            help="Generate colorscheme (default: enabled)",
        ),
    ] = True,
    effects: Annotated[
        bool,
        typer.Option(
            "--effects/--no-effects",
            help="Generate effect variants (default: enabled)",
        ),
    ] = True,
    effect: Annotated[
        str,
        typer.Option(
            "--effect",
            help="Effect name applied ('off' for original wallpaper)",
        ),
    ] = "off",
    original_wallpaper: Annotated[
        Path | None,
        typer.Option(
            "--original-wallpaper",
            help="Path to original wallpaper (for effect variants)",
        ),
    ] = None,
) -> None:
    """Change wallpaper and execute hooks."""
    try:
        container = Container.initialize()
        wallpaper_service = container.wallpaper_service()

        # Auto-detect monitor if not specified
        if monitor is None:
            from hyprpaper_manager import HyprpaperManager

            try:
                hyprpaper = HyprpaperManager()
                status = hyprpaper.get_status()
                if status.monitors:
                    # Use the focused monitor, or first monitor if none focused
                    focused = next(
                        (m for m in status.monitors if m.focused), None
                    )
                    monitor = (
                        focused.name if focused else status.monitors[0].name
                    )
                else:
                    monitor = "default"
            except Exception:
                # Fallback to system attributes if hyprpaper detection fails
                system_attrs_repo = container.system_attributes_repo()
                attrs = system_attrs_repo.get_attributes()
                if attrs.monitors:
                    monitor = attrs.monitors[0]
                else:
                    monitor = "default"

        console.print(f"[cyan]Changing wallpaper on {monitor}...[/cyan]")

        result = wallpaper_service.change_wallpaper(
            wallpaper_path=wallpaper_path,
            monitor=monitor,
            force_rebuild=force_rebuild,
            generate_colorscheme=colorscheme,
            generate_effects=effects,
            effect=effect,
            original_wallpaper_path=original_wallpaper,
        )

        console.print(f"[green]✓[/green] Wallpaper changed: {wallpaper_path}")
        console.print(f"  Monitor: {monitor}")
        console.print(f"  From cache: {result['from_cache']}")

        # Display hook results
        hook_results = result.get("hook_results", {})
        if hook_results:
            console.print("\n[bold]Hook Results:[/bold]")
            for hook_name, hook_result in hook_results.items():
                status = "✓" if hook_result.success else "✗"
                color = "green" if hook_result.success else "red"
                console.print(
                    f"  [{color}]{status}[/{color}] {hook_name}: {hook_result.message}"
                )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def set_font(
    family: Annotated[
        str | None,
        typer.Option("--family", "-f", help="Font family"),
    ] = None,
    size: Annotated[
        int | None,
        typer.Option("--size", "-s", help="Font size in pixels"),
    ] = None,
) -> None:
    """Set system font settings."""
    try:
        container = Container.initialize()
        system_attrs_repo = container.system_attributes_repo()

        if family:
            system_attrs_repo.set_font_family(family)
            console.print(f"[green]✓[/green] Font family set to: {family}")

        if size:
            system_attrs_repo.set_font_size(size)
            console.print(f"[green]✓[/green] Font size set to: {size}px")

        if not family and not size:
            console.print(
                "[yellow]No changes made. Specify --family or --size[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def get_wallpaper_state(
    monitor: Annotated[
        str,
        typer.Argument(help="Monitor name"),
    ] = "default",
) -> None:
    """Get current wallpaper state for a monitor (JSON format).

    Outputs JSON with wallpaper state including original wallpaper and effect.
    Exits with code 1 if no wallpaper is set.

    Special monitor names:
    - "focused": Resolves to the currently focused monitor
    - "all": Returns wallpaper from any monitor that has one set
    - "default": Returns wallpaper from the "default" monitor
    """
    import json

    try:
        container = Container.initialize()
        wallpaper_service = container.wallpaper_service()

        # Resolve special monitor names
        resolved_monitor = monitor
        if monitor == "focused":
            # Get focused monitor from hyprpaper
            try:
                from hyprpaper_manager import HyprpaperManager

                hyprpaper = HyprpaperManager()
                status = hyprpaper.get_status()
                for mon in status.monitors:
                    if mon.focused:
                        resolved_monitor = mon.name
                        break
                else:
                    # No focused monitor found, fallback to default
                    resolved_monitor = "default"
            except Exception:
                # Fallback to default
                resolved_monitor = "default"
        elif monitor == "all":
            # Try to get wallpaper from any monitor
            try:
                from hyprpaper_manager import HyprpaperManager

                hyprpaper = HyprpaperManager()
                status = hyprpaper.get_status()
                if status.monitors:
                    # Try each monitor until we find one with a wallpaper
                    for mon in status.monitors:
                        state = wallpaper_service.get_current_wallpaper(
                            mon.name
                        )
                        if state:
                            print(
                                json.dumps(
                                    {
                                        "monitor": state.monitor,
                                        "wallpaper_path": str(
                                            state.wallpaper_path
                                        ),
                                        "original_wallpaper_path": str(
                                            state.original_wallpaper_path
                                        ),
                                        "current_effect": state.current_effect,
                                        "last_changed": state.last_changed.isoformat(),
                                        "from_cache": state.from_cache,
                                    }
                                )
                            )
                            return
                # No wallpaper found on any monitor, fallback to default
                resolved_monitor = "default"
            except Exception:
                # Fallback to default
                resolved_monitor = "default"

        state = wallpaper_service.get_current_wallpaper(resolved_monitor)
        if state:
            # Output JSON
            print(
                json.dumps(
                    {
                        "monitor": state.monitor,
                        "wallpaper_path": str(state.wallpaper_path),
                        "original_wallpaper_path": str(
                            state.original_wallpaper_path
                        ),
                        "current_effect": state.current_effect,
                        "last_changed": state.last_changed.isoformat(),
                        "from_cache": state.from_cache,
                    }
                )
            )
        else:
            err_console = Console(stderr=True)
            err_console.print(
                f"[red]No wallpaper set for monitor: {monitor}[/red]"
            )
            raise typer.Exit(1)

    except Exception as e:
        err_console = Console(stderr=True)
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def get_wallpaper(
    monitor: Annotated[
        str,
        typer.Argument(help="Monitor name"),
    ] = "default",
) -> None:
    """Get current wallpaper path for a monitor.

    Outputs only the wallpaper path (machine-readable format).
    Exits with code 1 if no wallpaper is set.

    Special monitor names:
    - "focused": Resolves to the currently focused monitor
    - "all": Returns wallpaper from any monitor that has one set
    - "default": Returns wallpaper from the "default" monitor
    """
    try:
        container = Container.initialize()
        wallpaper_service = container.wallpaper_service()

        # Resolve special monitor names
        resolved_monitor = monitor
        if monitor == "focused":
            # Get focused monitor from hyprpaper
            try:
                from hyprpaper_manager import HyprpaperManager

                hyprpaper = HyprpaperManager()
                status = hyprpaper.get_status()
                for mon in status.monitors:
                    if mon.focused:
                        resolved_monitor = mon.name
                        break
                else:
                    # No focused monitor found, fallback to default
                    resolved_monitor = "default"
            except Exception:
                # Fallback to default
                resolved_monitor = "default"
        elif monitor == "all":
            # Try to get wallpaper from any monitor
            try:
                from hyprpaper_manager import HyprpaperManager

                hyprpaper = HyprpaperManager()
                status = hyprpaper.get_status()
                if status.monitors:
                    # Try each monitor until we find one with a wallpaper
                    for mon in status.monitors:
                        state = wallpaper_service.get_current_wallpaper(
                            mon.name
                        )
                        if state:
                            print(str(state.wallpaper_path))
                            return
                # No wallpaper found on any monitor, fallback to default
                resolved_monitor = "default"
            except Exception:
                # Fallback to default
                resolved_monitor = "default"

        state = wallpaper_service.get_current_wallpaper(resolved_monitor)
        if state:
            # Output only the path (machine-readable)
            print(str(state.wallpaper_path))
        else:
            # Use stderr console for error messages
            err_console = Console(stderr=True)
            err_console.print(
                f"[red]No wallpaper set for monitor: {monitor}[/red]"
            )
            raise typer.Exit(1)

    except Exception as e:
        err_console = Console(stderr=True)
        err_console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def status(
    monitor: Annotated[
        str | None,
        typer.Option("--monitor", "-m", help="Monitor name"),
    ] = None,
) -> None:
    """Show current system status."""
    try:
        container = Container.initialize()
        system_attrs_repo = container.system_attributes_repo()
        wallpaper_service = container.wallpaper_service()

        # Get system attributes
        attrs = system_attrs_repo.get_attributes()

        # Display system attributes
        table = Table(title="System Attributes")
        table.add_column("Attribute", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Font Family", attrs.font_family)
        table.add_row("Font Size", f"{attrs.font_size}px")
        table.add_row(
            "Monitors",
            ", ".join(attrs.monitors) if attrs.monitors else "auto-detect",
        )

        console.print(table)

        # Display wallpaper status
        # Determine which monitors to check
        if monitor:
            # User specified a monitor
            monitors_to_check = [monitor]
        elif attrs.monitors:
            # System attributes have configured monitors
            monitors_to_check = attrs.monitors
        else:
            # Auto-detect monitors from hyprpaper
            try:
                from hyprpaper_manager import HyprpaperManager

                hyprpaper = HyprpaperManager()
                status_info = hyprpaper.get_status()
                if status_info.monitors:
                    monitors_to_check = [m.name for m in status_info.monitors]
                else:
                    monitors_to_check = ["default"]
            except Exception:
                # Fallback to default
                monitors_to_check = ["default"]

        wallpaper_table = Table(title="Wallpaper Status")
        wallpaper_table.add_column("Monitor", style="cyan")
        wallpaper_table.add_column("Wallpaper", style="green", no_wrap=False)
        wallpaper_table.add_column("Last Changed", style="yellow")

        for mon in monitors_to_check:
            state = wallpaper_service.get_current_wallpaper(mon)
            if state:
                wallpaper_table.add_row(
                    mon,
                    str(state.wallpaper_path),
                    state.last_changed.strftime("%Y-%m-%d %H:%M:%S"),
                )
            else:
                wallpaper_table.add_row(mon, "Not set", "-")

        console.print(wallpaper_table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
