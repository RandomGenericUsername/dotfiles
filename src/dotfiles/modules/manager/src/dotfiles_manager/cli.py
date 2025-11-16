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
        monitors_to_check = (
            [monitor] if monitor else (attrs.monitors or ["default"])
        )

        wallpaper_table = Table(title="Wallpaper Status")
        wallpaper_table.add_column("Monitor", style="cyan")
        wallpaper_table.add_column("Wallpaper", style="green")
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
