#!/usr/bin/env python3
"""Entrypoint for wallust backend container."""

import json
import os
import sys
from pathlib import Path

from colorscheme_generator import (
    ColorFormat,
    GeneratorConfig,
    OutputManager,
    WallustGenerator,
)


def main():
    """Main entrypoint for wallust backend."""
    # Get environment variables
    image_path = os.getenv("IMAGE_PATH")
    output_dir = os.getenv("OUTPUT_DIR", "/output")
    formats_str = os.getenv("FORMATS", "json,css,yaml,sh").split(",")
    # Convert format strings to ColorFormat enums
    formats = [ColorFormat(fmt.strip()) for fmt in formats_str]
    color_count = int(os.getenv("COLOR_COUNT", "16"))
    backend_type = os.getenv("BACKEND_TYPE", "resized")
    output_format = os.getenv("OUTPUT_FORMAT", "json")

    # Validate inputs
    if not image_path:
        print(
            "ERROR: IMAGE_PATH environment variable not set", file=sys.stderr
        )
        sys.exit(1)

    image_path = Path(image_path)
    if not image_path.exists():
        print(f"ERROR: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Wallust Backend Container")
    print("=" * 60)
    print(f"Image:         {image_path}")
    print(f"Output:        {output_dir}")
    print(f"Formats:       {', '.join(formats)}")
    print(f"Colors:        {color_count}")
    print(f"Backend Type:  {backend_type}")
    print(f"Output Format: {output_format}")
    print("=" * 60)

    try:
        # Create configuration
        gen_config = GeneratorConfig(
            output_dir=output_dir,
            formats=formats,
        )

        # Create app config with wallust settings
        from colorscheme_generator.config.config import AppConfig

        app_config = AppConfig()
        # Override wallust settings
        app_config.backends.wallust.backend_type = backend_type
        app_config.backends.wallust.output_format = output_format

        # Create generator
        print("\n→ Initializing wallust generator...")
        generator = WallustGenerator(app_config)

        # Generate colorscheme
        print("→ Extracting colors from image...")
        colorscheme = generator.generate(image_path, gen_config)

        print(f"✓ Extracted {len(colorscheme.colors)} colors")
        print(f"  Background: {colorscheme.background.hex}")
        print(f"  Foreground: {colorscheme.foreground.hex}")
        print(f"  Cursor: {colorscheme.cursor.hex}")

        # Create output manager
        print("\n→ Writing output files...")
        output_manager = OutputManager(app_config)

        # Write output files
        output_files = output_manager.write_outputs(
            colorscheme, output_dir, formats
        )

        print(f"✓ Generated {len(output_files)} files:")
        for fmt, path in output_files.items():
            print(f"  • {fmt}: {path}")

        # Write metadata file
        metadata = {
            "backend": "wallust",
            "image": str(image_path),
            "color_count": len(colorscheme.colors),
            "formats": list(output_files.keys()),
            "output_files": {k: str(v) for k, v in output_files.items()},
            "backend_type": backend_type,
            "output_format": output_format,
        }
        metadata_path = output_dir / "metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)
        print(f"  • metadata: {metadata_path}")

        print(f"\n{'=' * 60}")
        print("✓ Wallust backend completed successfully")
        print(f"{'=' * 60}")

        # Display the color scheme with colored blocks
        from colorscheme_generator.cli import _show_colorscheme

        _show_colorscheme(colorscheme)

        sys.exit(0)

    except Exception as e:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"✗ Error: {e}", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
