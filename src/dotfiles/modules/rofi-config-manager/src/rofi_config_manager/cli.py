#!/usr/bin/env python3
"""CLI interface for rofi-config-manager."""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from rofi_config_manager.config.config import load_config
from rofi_config_manager.config.types import RofiConfigType
from rofi_config_manager.services.config_service import RofiConfigService

app = typer.Typer(
    help="Rofi configuration manager CLI",
    no_args_is_help=True,
)
console = Console()


@app.command()
def generate(
    config_type: Annotated[
        Optional[str],
        typer.Option(
            "--type",
            "-t",
            help="Config type to generate (wallpaper-selector, colorscheme-viewer, colorscheme-viewer-minimal)",
        ),
    ] = None,
    all_configs: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Generate all enabled configs",
        ),
    ] = False,
    config_file: Annotated[
        Optional[Path],
        typer.Option(
            "--config",
            "-c",
            help="Path to config file",
        ),
    ] = None,
) -> None:
    """Generate rofi configuration files."""
    try:
        # Load configuration
        config = load_config(config_file)
        service = RofiConfigService(config)

        if all_configs:
            # Generate all configs
            console.print("[cyan]Generating all rofi configs...[/cyan]")
            results = service.generate_all_configs()

            # Display results
            table = Table(title="Generated Configs")
            table.add_column("Config Type", style="cyan")
            table.add_column("Output Path", style="green")

            for config_name, output_path in results.items():
                table.add_row(config_name, str(output_path))

            console.print(table)
            console.print(
                f"[green]✓[/green] Generated {len(results)} config(s)"
            )

        elif config_type:
            # Generate specific config
            try:
                rofi_config_type = RofiConfigType(config_type)
            except ValueError:
                console.print(
                    f"[red]Error: Invalid config type '{config_type}'[/red]"
                )
                console.print(
                    f"Valid types: {', '.join([t.value for t in RofiConfigType])}"
                )
                raise typer.Exit(1)

            console.print(
                f"[cyan]Generating {config_type} config...[/cyan]"
            )
            output_path = service.generate_config(rofi_config_type)
            console.print(
                f"[green]✓[/green] Generated: {output_path}"
            )

        else:
            console.print(
                "[red]Error: Specify --all or --type <config_type>[/red]"
            )
            raise typer.Exit(1)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            "[yellow]Hint: Run 'dotfiles-manager change-wallpaper' first[/yellow]"
        )
        raise typer.Exit(1) from e
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def list_types() -> None:
    """List available config types."""
    table = Table(title="Available Config Types")
    table.add_column("Type", style="cyan")
    table.add_column("Template", style="green")
    table.add_column("Output", style="yellow")

    for config_type in RofiConfigType:
        table.add_row(
            config_type.value,
            config_type.template_name,
            config_type.output_filename,
        )

    console.print(table)


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
