"""CLI interface for wallpaper orchestrator."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from wallpaper_effects_orchestrator.config import get_default_config
from wallpaper_effects_orchestrator.orchestrator import WallpaperOrchestrator

app = typer.Typer(
    name="wallpaper-effects-process",
    help="Container-based wallpaper effects processing tool",
    add_completion=False,
)

console = Console()


@app.command()
def process(
    input_path: Path = typer.Option(
        ..., "-i", "--input", help="Input image path"
    ),
    output_path: Path = typer.Option(
        ..., "-o", "--output", help="Output image path"
    ),
    preset: str | None = typer.Option(None, "--preset", help="Preset name"),
    effects: list[str] | None = typer.Option(
        None,
        "-e",
        "--effect",
        help="Effect to apply (can be specified multiple times)",
    ),
    # Effect parameters
    sigma: float | None = typer.Option(None, "--sigma", help="Blur sigma"),
    radius: float | None = typer.Option(None, "--radius", help="Blur radius"),
    adjustment: int | None = typer.Option(
        None, "--adjustment", help="Brightness/saturation adjustment"
    ),
    strength: int | None = typer.Option(
        None, "--strength", help="Vignette strength"
    ),
    color: str | None = typer.Option(
        None, "--color", help="Color overlay hex code"
    ),
    opacity: float | None = typer.Option(
        None, "--opacity", help="Color overlay opacity"
    ),
    # Processing options
    mode: str | None = typer.Option(None, "--mode", help="Processing mode"),
    quality: int | None = typer.Option(
        None, "--quality", help="Output quality"
    ),
    metadata: bool = typer.Option(
        False, "--metadata", help="Write metadata file"
    ),
    # Container options
    runtime: str | None = typer.Option(
        None, "--runtime", help="Container runtime"
    ),
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Don't use cached image"
    ),
) -> None:
    """Process single image with effects."""
    # Load configuration
    config = get_default_config()

    # Override config with CLI options
    if mode:
        config.processing.mode = mode
    if quality:
        config.processing.quality = quality
    if metadata:
        config.processing.write_metadata = metadata
    if runtime:
        config.container.runtime = runtime

    # Build effect parameters
    effect_params = {}
    if effects:
        for effect_name in effects:
            params = {}
            if effect_name == "blur":
                if sigma is not None:
                    params["sigma"] = sigma
                if radius is not None:
                    params["radius"] = radius
            elif effect_name in ("brightness", "saturation"):
                if adjustment is not None:
                    params["adjustment"] = adjustment
            elif effect_name == "vignette":
                if strength is not None:
                    params["strength"] = strength
            elif effect_name == "color_overlay":
                if color is not None:
                    params["color"] = color
                if opacity is not None:
                    params["opacity"] = opacity

            if params:
                effect_params[effect_name] = params

    # Create orchestrator
    orchestrator = WallpaperOrchestrator(config)

    # Ensure image
    if no_cache:
        console.print("[yellow]Building container image...[/yellow]")
        orchestrator.ensure_image(force_rebuild=True)

    # Process image
    try:
        console.print(f"[cyan]Processing {input_path} -> {output_path}[/cyan]")
        success = orchestrator.process_image(
            input_path, output_path, preset, effects, effect_params
        )

        if success:
            console.print("[green]✓ Processing complete[/green]")
        else:
            console.print("[red]✗ Processing failed[/red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def batch(
    batch_dir: Path = typer.Option(..., "--batch-dir", help="Input directory"),
    output_dir: Path = typer.Option(
        ..., "--output-dir", help="Output directory"
    ),
    preset: str | None = typer.Option(None, "--preset", help="Preset name"),
    effects: list[str] | None = typer.Option(
        None, "-e", "--effect", help="Effect to apply"
    ),
    parallel: int = typer.Option(
        1, "--parallel", help="Number of parallel processes"
    ),
    skip_existing: bool = typer.Option(
        False, "--skip-existing", help="Skip existing files"
    ),
    continue_on_error: bool = typer.Option(
        True, "--continue-on-error", help="Continue on errors"
    ),
    # Processing options
    mode: str | None = typer.Option(None, "--mode", help="Processing mode"),
    quality: int | None = typer.Option(
        None, "--quality", help="Output quality"
    ),
    # Container options
    runtime: str | None = typer.Option(
        None, "--runtime", help="Container runtime"
    ),
) -> None:
    """Process batch of images."""
    # Load configuration
    config = get_default_config()

    # Override config
    if mode:
        config.processing.mode = mode
    if quality:
        config.processing.quality = quality
    if runtime:
        config.container.runtime = runtime

    # Create orchestrator
    orchestrator = WallpaperOrchestrator(config)

    # Process batch
    try:
        console.print(
            f"[cyan]Processing batch: {batch_dir} -> {output_dir}[/cyan]"
        )
        successful, failed = orchestrator.process_batch(
            batch_dir,
            output_dir,
            preset,
            effects,
            None,  # effect_params
            parallel,
            skip_existing,
            continue_on_error,
        )

        console.print(f"\n[green]✓ Successful: {successful}[/green]")
        if failed > 0:
            console.print(f"[red]✗ Failed: {failed}[/red]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command("list")
def list_effects() -> None:
    """List available effects."""
    table = Table(title="Available Effects")
    table.add_column("Effect", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Parameters", style="yellow")

    effects_info = [
        ("blur", "Gaussian blur", "sigma (0-100), radius (0-50)"),
        ("brightness", "Adjust brightness", "adjustment (-100 to 100)"),
        ("saturation", "Adjust saturation", "adjustment (-100 to 100)"),
        ("vignette", "Darken edges", "strength (0-100)"),
        ("color_overlay", "Overlay color", "color (hex), opacity (0.0-1.0)"),
        (
            "grayscale",
            "Convert to grayscale",
            "method (average, luminosity, mean)",
        ),
        ("negate", "Invert colors", "none"),
    ]

    for name, desc, params in effects_info:
        table.add_row(name, desc, params)

    console.print(table)


@app.command("variants")
def generate_variants(
    input_path: Path = typer.Option(
        ..., "-i", "--input", help="Input image path"
    ),
    output_dir: Path = typer.Option(
        ..., "-o", "--output-dir", help="Output directory"
    ),
) -> None:
    """Generate all effect variants for an input image.

    Creates a subdirectory named after the input image and generates
    one variant for each available effect with default parameters.

    Example:
        wallpaper-process variants -i canary.png -o /tmp/wallpaper

        Creates:
        /tmp/wallpaper/canary/blur.png
        /tmp/wallpaper/canary/grayscale.png
        /tmp/wallpaper/canary/negate.png
        etc.
    """
    try:
        if not input_path.exists():
            console.print(
                f"[red]Error: Input file not found: {input_path}[/red]"
            )
            sys.exit(1)

        config = get_default_config()
        orchestrator = WallpaperOrchestrator(config)

        console.print(
            f"Generating all variants for {input_path.name} -> {output_dir}/"
        )

        # Generate all variants
        results = orchestrator.generate_all_variants(input_path, output_dir)

        # Display results
        console.print(f"[green]✓ Generated {len(results)} variants:[/green]")
        for effect_name, output_path in sorted(results.items()):
            console.print(f"  • {effect_name}: {output_path}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def presets() -> None:
    """List available presets."""
    config = get_default_config()

    table = Table(title="Available Presets")
    table.add_column("Preset", style="cyan")
    table.add_column("Description", style="white")

    for name, preset in config.presets.items():
        table.add_row(name, preset.description)

    console.print(table)


@app.command()
def build(
    no_cache: bool = typer.Option(
        False, "--no-cache", help="Build without cache"
    ),
    runtime: str | None = typer.Option(
        None, "--runtime", help="Container runtime"
    ),
) -> None:
    """Build container image."""
    config = get_default_config()

    if runtime:
        config.container.runtime = runtime
    if no_cache:
        config.container.build_no_cache = True

    orchestrator = WallpaperOrchestrator(config)

    try:
        console.print("[yellow]Building container image...[/yellow]")
        orchestrator.ensure_image(force_rebuild=True)
        console.print("[green]✓ Build complete[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def clean(
    runtime: str | None = typer.Option(
        None, "--runtime", help="Container runtime"
    ),
) -> None:
    """Clean container resources."""
    config = get_default_config()

    if runtime:
        config.container.runtime = runtime

    orchestrator = WallpaperOrchestrator(config)

    try:
        console.print("[yellow]Cleaning container resources...[/yellow]")
        orchestrator.clean()
        console.print("[green]✓ Cleanup complete[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
