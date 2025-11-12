#!/usr/bin/env python3
"""CLI interface for dotfiles-manager."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from dotfiles_manager import Manager
from dotfiles_manager.config import ManagerConfig

app = typer.Typer(
    help="Dotfiles manager CLI",
    no_args_is_help=True,
)
console = Console()


@app.command()
def status(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable debug output")
    ] = False,
) -> None:
    """Show manager status and configuration."""
    try:
        manager = Manager()
        config = manager.config

        # Display configuration
        table = Table(title="Manager Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Data Directory", str(config.data_dir))
        table.add_row("Debug Mode", str(config.debug))

        console.print(table)

        if verbose:
            console.print("\n[bold]Manager Details:[/bold]")
            console.print(f"Config: {config}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def init(
    data_dir: Annotated[
        Path | None,
        typer.Option(
            "--data-dir",
            "-d",
            help="Data directory path",
        ),
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug mode"),
    ] = False,
) -> None:
    """Initialize manager with custom configuration."""
    try:
        # Use default if not provided
        if data_dir is None:
            data_dir = Path.home() / ".local/share/dotfiles"

        # Create custom config
        config = ManagerConfig(
            data_dir=data_dir,
            debug=debug,
        )

        # Initialize manager
        with Manager(config):
            console.print(
                "[green]✓[/green] Manager initialized with "
                f"data directory: {data_dir}"
            )

            if debug:
                console.print("[yellow]Debug mode enabled[/yellow]")

    except Exception as e:
        console.print(f"[red]Error initializing manager: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def info() -> None:
    """Display information about the manager."""
    console.print("[bold]Dotfiles Manager[/bold]")
    console.print("\nA flexible manager for dotfiles operations.")
    console.print("\n[bold]Usage:[/bold]")
    console.print("  dotfiles-manager status    - Show current configuration")
    console.print(
        "  dotfiles-manager init      - Initialize with custom config"
    )
    console.print("  dotfiles-manager info      - Show this information")


def main() -> None:
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    main()
