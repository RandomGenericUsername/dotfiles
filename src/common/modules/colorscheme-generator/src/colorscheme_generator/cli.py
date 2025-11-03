"""Command-line interface for colorscheme generator."""

import argparse
import sys
from pathlib import Path

from colorscheme_generator import ColorSchemeGeneratorFactory
from colorscheme_generator.config.enums import Backend, ColorFormat
from colorscheme_generator.config.settings import Settings
from colorscheme_generator.core.exceptions import (
    BackendNotAvailableError,
    ColorExtractionError,
    InvalidImageError,
    OutputWriteError,
)
from colorscheme_generator.core.managers import OutputManager
from colorscheme_generator.core.types import GeneratorConfig


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate color schemes from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with auto-detected backend
  colorscheme-gen wallpaper.png

  # Use specific backend
  colorscheme-gen wallpaper.png --backend pywal

  # Custom output directory and formats
  colorscheme-gen wallpaper.png -o ~/.config/colors -f json css

  # List available backends
  colorscheme-gen --list-backends
        """,
    )

    parser.add_argument(
        "image",
        type=Path,
        nargs="?",
        help="Path to source image",
    )

    parser.add_argument(
        "-b",
        "--backend",
        type=str,
        choices=["pywal", "wallust", "custom", "auto"],
        default="auto",
        help="Backend to use (default: auto-detect)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        help="Output directory (default: from settings)",
    )

    parser.add_argument(
        "-f",
        "--formats",
        nargs="+",
        choices=["json", "sh", "css", "yaml", "toml"],
        help="Output formats (default: from settings)",
    )

    parser.add_argument(
        "-c",
        "--color-count",
        type=int,
        help="Number of colors to extract (default: 16)",
    )

    parser.add_argument(
        "--list-backends",
        action="store_true",
        help="List available backends and exit",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Load settings
    try:
        settings = Settings.get()
    except Exception as e:
        print(f"Error loading settings: {e}", file=sys.stderr)
        return 1

    # List backends if requested
    if args.list_backends:
        available = ColorSchemeGeneratorFactory.list_available(settings)
        print("Available backends:")
        for backend in available:
            print(f"  - {backend}")
        return 0

    # Require image argument
    if not args.image:
        parser.error("image argument is required")

    # Create runtime config
    config_kwargs = {}

    if args.backend != "auto":
        config_kwargs["backend"] = Backend(args.backend)

    if args.output_dir:
        config_kwargs["output_dir"] = args.output_dir.expanduser()

    if args.formats:
        config_kwargs["formats"] = [ColorFormat(f) for f in args.formats]

    if args.color_count:
        config_kwargs["color_count"] = args.color_count

    config = GeneratorConfig.from_settings(settings, **config_kwargs)

    # Create backend
    try:
        if args.backend == "auto":
            if args.verbose:
                print("Auto-detecting backend...")
            generator = ColorSchemeGeneratorFactory.create_auto(settings)
        else:
            generator = ColorSchemeGeneratorFactory.create(
                Backend(args.backend), settings
            )

        if args.verbose:
            print(f"Using backend: {generator.backend_name}")
    except BackendNotAvailableError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Generate color scheme
    try:
        if args.verbose:
            print(f"Extracting colors from: {args.image}")

        scheme = generator.generate(args.image, config)

        if args.verbose:
            print(f"Background: {scheme.background.hex}")
            print(f"Foreground: {scheme.foreground.hex}")
            print(f"Cursor: {scheme.cursor.hex}")
            print(f"Colors: {len(scheme.colors)}")
    except InvalidImageError as e:
        print(f"Error: Invalid image: {e}", file=sys.stderr)
        return 1
    except ColorExtractionError as e:
        print(f"Error: Color extraction failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    # Write output files
    try:
        if args.verbose:
            print(f"Writing output to: {config.output_dir}")

        output_manager = OutputManager(settings)
        output_files = output_manager.write_outputs(
            scheme,
            config.output_dir,
            config.formats,
        )

        print("Generated files:")
        for format_name, file_path in output_files.items():
            print(f"  {format_name}: {file_path}")
    except OutputWriteError as e:
        print(f"Error: Failed to write output: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
