"""CLI interface for colorscheme orchestrator using Typer."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from colorscheme_orchestrator import ColorSchemeOrchestrator
from colorscheme_orchestrator.config import load_settings
from colorscheme_orchestrator.exceptions import (
    ImageNotFoundError,
    InvalidBackendError,
    OrchestratorError,
)
from colorscheme_orchestrator.logging import get_logger

# Create Typer app
app = typer.Typer(
    name="colorscheme-gen",
    help="CLI tool for orchestrating containerized colorscheme generation",
    add_completion=False,
)

# Rich console for beautiful output
console = Console()

# Logger
logger = get_logger("cli")


@app.command(name="generate")
def generate_command(
    backend: str = typer.Option(
        None,
        "--backend",
        "-b",
        help="Backend to use (pywal, wallust, custom). Uses default "
        "from settings if not specified.",
    ),
    image: Path = typer.Option(
        ...,
        "--image",
        "-i",
        help="Path to source image file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for generated files. Uses default from "
        "settings if not specified.",
    ),
    formats: str | None = typer.Option(
        None,
        "--formats",
        "-f",
        help="Comma-separated output formats (json,css,yaml,sh). Uses "
        "default from settings if not specified.",
    ),
    colors: int | None = typer.Option(
        None,
        "--colors",
        "-c",
        help="Number of colors to extract. Uses default from settings "
        "if not specified.",
    ),
    algorithm: str | None = typer.Option(
        None,
        "--algorithm",
        "-a",
        help="Algorithm for custom backend (kmeans, median_cut, octree)",
    ),
    runtime: str | None = typer.Option(
        None,
        "--runtime",
        help="Container runtime to use (docker, podman). Overrides settings.",
    ),
    rebuild: bool = typer.Option(
        False,
        "--rebuild",
        help="Force rebuild container image",
    ),
    keep_container: bool = typer.Option(
        False,
        "--keep-container",
        help="Don't remove container after completion (for debugging)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging",
    ),
):
    """Generate colorscheme from an image using containerized backends.

    Examples:

        # Generate using pywal backend
        colorscheme-gen -b pywal -i wallpaper.png

        # Generate using wallust with custom output
        colorscheme-gen -b wallust -i wallpaper.png -o ~/my-colors

        # Generate using custom backend with specific algorithm
        colorscheme-gen -b custom -i wallpaper.png -a median_cut
    """
    try:
        # Load settings
        config = load_settings()

        # Override runtime if specified
        if runtime:
            config.orchestrator.container_runtime = runtime

        # Use default backend if not specified
        if backend is None:
            backend = config.orchestrator.default_backend
            console.print(f"[dim]Using default backend: {backend}[/dim]")

        # Parse formats if provided
        formats_list = None
        if formats:
            formats_list = [f.strip() for f in formats.split(",")]

        # Create orchestrator
        orchestrator = ColorSchemeOrchestrator(config=config)

        # Prepare backend options
        backend_options = {}
        if algorithm:
            backend_options["algorithm"] = algorithm

        # Generate colorscheme
        output_files = orchestrator.generate(
            backend=backend,
            image_path=image,
            output_dir=output,
            formats=formats_list,
            color_count=colors,
            rebuild=rebuild,
            keep_container=keep_container,
            **backend_options,
        )

        # Display results (if any)
        if output_files:
            console.print(
                "\n[green]✓ Colorscheme generated successfully![/green]"
            )
            console.print("\n[bold]Output files:[/bold]")
            for fmt, path in output_files.items():
                console.print(f"  • {fmt}: {path}")

    except InvalidBackendError as e:
        console.print(f"[red]✗ Invalid backend: {e.backend}[/red]")
        console.print(
            f"[yellow]Valid backends: {', '.join(e.valid_backends)}[/yellow]"
        )
        raise typer.Exit(code=1) from e
    except ImageNotFoundError as e:
        console.print(f"[red]✗ Image not found: {e.image_path}[/red]")
        raise typer.Exit(code=1) from e
    except OrchestratorError as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1) from e
    except Exception as e:
        console.print(f"[red]✗ Unexpected error: {e}[/red]")
        if verbose:
            console.print_exception()
        raise typer.Exit(code=1) from e


@app.command(name="list")
def list_command():
    """List available backends and their status."""
    try:
        # Load settings and create orchestrator
        config = load_settings()
        orchestrator = ColorSchemeOrchestrator(config=config)

        # Get backends
        backends = orchestrator.list_backends()

        # Create table
        table = Table(title="Available Backends")
        table.add_column("Backend", style="cyan", no_wrap=True)
        table.add_column("Image", style="magenta")
        table.add_column("Dependencies", style="green")

        for backend in backends:
            info = orchestrator.get_backend_info(backend)
            table.add_row(
                info["name"],
                info["image"],
                ", ".join(info["dependencies"]),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1) from e


@app.command(name="build")
def build_command(
    backend: str | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Build specific backend (pywal, wallust, custom)",
    ),
    all_backends: bool = typer.Option(
        False,
        "--all",
        help="Build all backend images",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Build without using cache",
    ),
):
    """Build container images for backends.

    Examples:

        # Build specific backend
        colorscheme-gen build -b pywal

        # Build all backends
        colorscheme-gen build --all

        # Build without cache
        colorscheme-gen build -b pywal --no-cache
    """
    try:
        # Load settings and create orchestrator
        config = load_settings()
        orchestrator = ColorSchemeOrchestrator(config=config)

        if all_backends:
            console.print("[bold]Building all backend images...[/bold]\n")
            try:
                orchestrator.builder.build_all_images(
                    rebuild=True, no_cache=no_cache
                )
                console.print(
                    "\n[green]✓ All images built successfully![/green]"
                )
            except NotImplementedError:
                console.print(
                    "[yellow]Image building will be implemented in "
                    "Phase 2[/yellow]"
                )
        elif backend:
            console.print(
                f"[bold]Building image for '{backend}' backend...[/bold]\n"
            )
            try:
                orchestrator.builder.build_backend_image(
                    backend, rebuild=True, no_cache=no_cache
                )
                console.print(
                    f"\n[green]✓ Image for '{backend}' built "
                    "successfully![/green]"
                )
            except NotImplementedError:
                console.print(
                    "[yellow]Image building will be implemented in "
                    "Phase 2[/yellow]"
                )
        else:
            console.print("[red]✗ Please specify --backend or --all[/red]")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1) from e


@app.command(name="clean")
def clean_command(
    backend: str | None = typer.Option(
        None,
        "--backend",
        "-b",
        help="Clean specific backend only",
    ),
    containers: bool = typer.Option(
        True,
        "--containers/--no-containers",
        help="Clean containers",
    ),
    images: bool = typer.Option(
        False,
        "--images/--no-images",
        help="Clean images",
    ),
    all_resources: bool = typer.Option(
        False,
        "--all",
        help="Clean both containers and images",
    ),
):
    """Clean up containers and images.

    Examples:

        # Clean containers only
        colorscheme-gen clean

        # Clean images only
        colorscheme-gen clean --no-containers --images

        # Clean everything
        colorscheme-gen clean --all

        # Clean specific backend
        colorscheme-gen clean -b pywal --all
    """
    try:
        # Load settings and create orchestrator
        config = load_settings()
        orchestrator = ColorSchemeOrchestrator(config=config)

        # Determine what to clean
        clean_containers = containers or all_resources
        clean_images = images or all_resources

        if not clean_containers and not clean_images:
            console.print(
                "[yellow]Nothing to clean (use --containers or "
                "--images)[/yellow]"
            )
            return

        # Get backends to clean
        if backend:
            backends = [backend]
            console.print(
                f"[bold]Cleaning resources for '{backend}' backend...[/bold]\n"
            )
        else:
            backends = orchestrator.list_backends()
            console.print(
                "[bold]Cleaning resources for all backends...[/bold]\n"
            )

        # Clean containers
        if clean_containers:
            console.print("→ Cleaning containers...")
            removed_count = 0
            for b in backends:
                metadata = orchestrator.registry.get(b)
                # List all containers with this prefix
                try:
                    containers_list = orchestrator.engine.containers.list(
                        all=True
                    )
                    for container in containers_list:
                        if container.name.startswith(
                            f"{config.orchestrator.container_prefix}-{b}"
                        ):
                            try:
                                orchestrator.engine.containers.remove(
                                    container.id, force=True
                                )
                                console.print(
                                    f"  ✓ Removed container: {container.name}"
                                )
                                removed_count += 1
                            except Exception as e:
                                console.print(
                                    f"  ✗ Failed to remove "
                                    f"{container.name}: {e}"
                                )
                except Exception as e:
                    console.print(f"  ✗ Error listing containers: {e}")

            if removed_count > 0:
                console.print(f"✓ Removed {removed_count} container(s)\n")
            else:
                console.print("  No containers to remove\n")

        # Clean images
        if clean_images:
            console.print("→ Cleaning images...")
            removed_count = 0
            for b in backends:
                metadata = orchestrator.registry.get(b)
                image_name = f"{metadata.image_name}:{metadata.image_tag}"
                try:
                    orchestrator.engine.images.remove(image_name, force=True)
                    console.print(f"  ✓ Removed image: {image_name}")
                    removed_count += 1
                except Exception as e:
                    console.print(f"  ✗ Failed to remove {image_name}: {e}")

            if removed_count > 0:
                console.print(f"✓ Removed {removed_count} image(s)\n")
            else:
                console.print("  No images to remove\n")

        console.print("[green]✓ Cleanup complete![/green]")

    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise typer.Exit(code=1) from e


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
    ),
):
    """
    Colorscheme Orchestrator - Generate colorschemes using containerized
    backends.

    This tool orchestrates colorscheme generation using Docker/Podman
    containers, providing isolation and reproducibility for different
    backends (pywal, wallust, custom).

    Commands:

        generate    Generate colorscheme from image (default)
        list        List available backends
        build       Build container images
        clean       Clean up containers and images

    Examples:

        # Generate colorscheme
        colorscheme-gen generate -i wallpaper.png

        # With specific backend
        colorscheme-gen generate -i wallpaper.png -b pywal

        # List available backends
        colorscheme-gen list

        # Build container images
        colorscheme-gen build --all

        # Clean up resources
        colorscheme-gen clean --all
    """
    if version:
        console.print("colorscheme-orchestrator version 0.1.0")
        raise typer.Exit()


if __name__ == "__main__":
    app()
