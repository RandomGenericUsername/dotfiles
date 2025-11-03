#!/usr/bin/env python3
"""Entrypoint for pywal backend container."""

import json
import os
import sys
from pathlib import Path

from colorscheme_generator import (
    GeneratorConfig,
    OutputManager,
)


def main():
    """Main entrypoint for pywal backend."""
    # Get environment variables
    image_path = os.getenv("IMAGE_PATH")
    output_dir = os.getenv("OUTPUT_DIR", "/output")
    formats = os.getenv("FORMATS", "json,css,yaml,sh").split(",")
    color_count = int(os.getenv("COLOR_COUNT", "16"))
    use_library = os.getenv("USE_LIBRARY", "true").lower() == "true"

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

    print("Pywal Backend Container")
    print("=" * 60)
    print(f"Image:        {image_path}")
    print(f"Output:       {output_dir}")
    print(f"Formats:      {', '.join(formats)}")
    print(f"Colors:       {color_count}")
    print(f"Use Library:  {use_library}")
    print("=" * 60)

    try:
        # Import the factory and backend
        from colorscheme_generator import (
            Backend,
            ColorSchemeGeneratorFactory,
            Settings,
        )

        # Create configuration
        config = GeneratorConfig(
            color_count=color_count,
            output_dir=output_dir,
            formats=formats,
        )

        # Create generator
        print("\n→ Initializing pywal generator...")
        settings = Settings.get()
        generator = ColorSchemeGeneratorFactory.create(Backend.PYWAL, settings)

        # Generate colorscheme
        print("→ Extracting colors from image...")
        colorscheme = generator.generate(image_path, config)

        print(f"✓ Extracted {len(colorscheme.colors)} colors")
        print(f"  Background: {colorscheme.background.hex}")
        print(f"  Foreground: {colorscheme.foreground.hex}")
        print(f"  Cursor: {colorscheme.cursor.hex}")

        # Create output manager
        print("\n→ Writing output files...")
        output_manager = OutputManager(settings)

        # Convert format strings to ColorFormat enums
        from colorscheme_generator import ColorFormat

        format_enums = [ColorFormat(fmt) for fmt in formats]

        # Write output files
        output_files = output_manager.write_outputs(
            colorscheme, output_dir, format_enums
        )

        print(f"✓ Generated {len(output_files)} files:")
        for fmt, path in output_files.items():
            print(f"  • {fmt}: {path}")

        # Write metadata file
        metadata = {
            "backend": "pywal",
            "image": str(image_path),
            "color_count": len(colorscheme.colors),
            "formats": list(output_files.keys()),
            "output_files": {k: str(v) for k, v in output_files.items()},
        }
        metadata_path = output_dir / "metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)
        print(f"  • metadata: {metadata_path}")

        print(f"\n{'=' * 60}")
        print("✓ Pywal backend completed successfully")
        print(f"{'=' * 60}")

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
