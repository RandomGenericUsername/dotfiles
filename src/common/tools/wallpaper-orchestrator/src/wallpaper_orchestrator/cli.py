"""CLI interface for wallpaper orchestrator using Typer."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wallpaper_orchestrator import WallpaperOrchestrator
from wallpaper_orchestrator.config import load_settings

# Create Typer app
app = typer.Typer(
    name="wallpaper-orchestrator",
    help="Complete wallpaper setup: effects, color scheme, and setting",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()


@app.command()
def process(
    wallpaper: Path = typer.Option(
        ...,
        "-i",
        "--input",
        "--wallpaper",
        help="Path to wallpaper image",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    effects_output: Path | None = typer.Option(
        None,
        "--effects-output",
        help="Output directory for effect variants (uses config default)",
    ),
    colorscheme_output: Path | None = typer.Option(
        None,
        "--colorscheme-output",
        help="Output directory for colorscheme files (uses config default)",
    ),
    backend: str | None = typer.Option(
        None,
        "-b",
        "--backend",
        help="Color scheme backend (pywal, wallust, custom)",
    ),
    monitor: str | None = typer.Option(
        None,
        "-m",
        "--monitor",
        help="Monitor to set wallpaper on (all, focused, or monitor name)",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable verbose output",
    ),
    force_rebuild: bool = typer.Option(
        False,
        "--force-rebuild",
        "-f",
        help="Force regeneration even if cached",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching for this run",
    ),
) -> None:
    """Process wallpaper: generate effects, color scheme, and set wallpaper.

    This command orchestrates the complete wallpaper setup process:

    1. Generates ALL effect variants using wallpaper-effects-orchestrator
    2. Generates color scheme from original wallpaper using
       colorscheme-orchestrator
    3. Sets the original wallpaper using hyprpaper-manager

    Examples:

        # Basic usage (uses all defaults from config)
        wallpaper-orchestrator process -i wallpaper.png

        # With custom output directories
        wallpaper-orchestrator process -i wallpaper.png \\
            --effects-output ~/wallpapers/effects \\
            --colorscheme-output ~/.config/colors

        # With specific backend and monitor
        wallpaper-orchestrator process -i wallpaper.png \\
            --backend pywal --monitor DP-1

        # Verbose output
        wallpaper-orchestrator process -i wallpaper.png -v
    """
    try:
        # Load configuration
        config = load_settings()

        # Override settings if provided
        if backend:
            config.colorscheme.backend = backend
        if verbose:
            config.orchestrator.verbose = True
            config.orchestrator.log_level = "DEBUG"
        if no_cache:
            config.cache.enabled = False

        # Create orchestrator
        orchestrator = WallpaperOrchestrator(config=config)

        # Process wallpaper
        console.print(
            f"\n[cyan]Processing wallpaper: {wallpaper.name}[/cyan]\n"
        )

        result = orchestrator.process(
            wallpaper_path=wallpaper,
            effects_output_dir=effects_output,
            colorscheme_output_dir=colorscheme_output,
            monitor=monitor,
            force_rebuild=force_rebuild,
        )

        # Display results
        if result.success:
            console.print(
                "\n[green]✓ Wallpaper orchestration complete![/green]\n"
            )

            # Effects table
            if result.effect_variants:
                effects_table = Table(title="Effect Variants")
                effects_table.add_column("Effect", style="cyan")
                effects_table.add_column("Path", style="white")

                for effect_name, path in sorted(
                    result.effect_variants.items()
                ):
                    effects_table.add_row(effect_name, str(path))

                console.print(effects_table)
                console.print()

            # Color scheme table
            if result.colorscheme_files:
                colorscheme_table = Table(title="Color Scheme Files")
                colorscheme_table.add_column("Format", style="cyan")
                colorscheme_table.add_column("Path", style="white")

                for fmt, path in sorted(result.colorscheme_files.items()):
                    colorscheme_table.add_row(fmt, str(path))

                console.print(colorscheme_table)
                console.print()

            # Wallpaper status
            console.print(
                f"[bold]Wallpaper Set:[/bold] {result.wallpaper_set}"
            )
            console.print(
                f"[bold]Monitor:[/bold] {result.monitor_set or 'all'}"
            )

        else:
            console.print("\n[red]✗ Wallpaper orchestration failed[/red]\n")
            if result.errors:
                console.print("[bold]Errors:[/bold]")
                for error in result.errors:
                    console.print(f"  • {error}")
            sys.exit(1)

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        if verbose:
            import traceback

            console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


@app.command()
def batch(
    wallpapers: list[Path] = typer.Argument(
        ...,
        help="Paths to wallpaper images",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    effects_output: Path | None = typer.Option(
        None,
        "--effects-output",
        help="Output directory for effect variants",
    ),
    colorscheme_output: Path | None = typer.Option(
        None,
        "--colorscheme-output",
        help="Output directory for color scheme files",
    ),
    backend: str | None = typer.Option(
        None,
        "-b",
        "--backend",
        help="Color scheme backend",
    ),
    monitor: str | None = typer.Option(
        None,
        "-m",
        "--monitor",
        help="Monitor to set wallpaper on",
    ),
    continue_on_error: bool = typer.Option(
        True,
        "--continue-on-error/--stop-on-error",
        help="Continue processing if one wallpaper fails",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Enable verbose output",
    ),
    force_rebuild: bool = typer.Option(
        False,
        "--force-rebuild",
        "-f",
        help="Force regeneration even if cached",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Disable caching for this run",
    ),
) -> None:
    """Process multiple wallpapers in batch.

    Examples:

        # Process multiple wallpapers
        wallpaper-orchestrator batch wallpaper1.png wallpaper2.png \\
            wallpaper3.png

        # With custom settings
        wallpaper-orchestrator batch *.png --backend pywal --monitor DP-1
    """
    try:
        # Load configuration
        config = load_settings()

        # Override settings if provided
        if backend:
            config.colorscheme.backend = backend
        if verbose:
            config.orchestrator.verbose = True
            config.orchestrator.log_level = "DEBUG"
        if no_cache:
            config.cache.enabled = False

        # Create orchestrator
        orchestrator = WallpaperOrchestrator(config=config)

        # Process batch
        console.print(
            f"\n[cyan]Processing {len(wallpapers)} wallpapers...[/cyan]\n"
        )

        results = orchestrator.process_batch(
            wallpaper_paths=wallpapers,
            effects_output_dir=effects_output,
            colorscheme_output_dir=colorscheme_output,
            monitor=monitor,
            force_rebuild=force_rebuild,
            continue_on_error=continue_on_error,
        )

        # Display summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        console.print(f"\n[green]✓ Successful: {successful}[/green]")
        if failed > 0:
            console.print(f"[red]✗ Failed: {failed}[/red]")

        if failed > 0:
            sys.exit(1)

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]\n")
        if verbose:
            import traceback

            console.print("[dim]" + traceback.format_exc() + "[/dim]")
        sys.exit(1)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit",
    ),
) -> None:
    """
    Wallpaper Orchestrator - Complete wallpaper setup tool.

    Orchestrates the complete wallpaper setup process:
    - Generates all effect variants
    - Generates color scheme from original wallpaper
    - Sets wallpaper using hyprpaper

    Commands:

        process    Process single wallpaper (default)
        batch      Process multiple wallpapers

    Examples:

        # Process single wallpaper
        wallpaper-orchestrator process -i wallpaper.png

        # With custom backend
        wallpaper-orchestrator process -i wallpaper.png --backend pywal

        # Process multiple wallpapers
        wallpaper-orchestrator batch *.png
    """
    if version:
        console.print("wallpaper-orchestrator version 0.1.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()
