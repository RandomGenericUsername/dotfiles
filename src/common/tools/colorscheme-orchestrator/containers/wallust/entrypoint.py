#!/usr/bin/env python3
"""Entrypoint for wallust backend container."""

import json
import os
import sys
from pathlib import Path

from colorscheme_generator import WallustGenerator, OutputManager, GeneratorConfig


def main():
    """Main entrypoint for wallust backend."""
    # Get environment variables
    image_path = os.getenv("IMAGE_PATH")
    output_dir = os.getenv("OUTPUT_DIR", "/output")
    formats = os.getenv("FORMATS", "json,css,yaml,sh").split(",")
    color_count = int(os.getenv("COLOR_COUNT", "16"))
    backend_type = os.getenv("BACKEND_TYPE", "resized")
    output_format = os.getenv("OUTPUT_FORMAT", "json")

    # Validate inputs
    if not image_path:
        print("ERROR: IMAGE_PATH environment variable not set", file=sys.stderr)
        sys.exit(1)

    image_path = Path(image_path)
    if not image_path.exists():
        print(f"ERROR: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Wallust Backend Container")
    print(f"=" * 60)
    print(f"Image:         {image_path}")
    print(f"Output:        {output_dir}")
    print(f"Formats:       {', '.join(formats)}")
    print(f"Colors:        {color_count}")
    print(f"Backend Type:  {backend_type}")
    print(f"Output Format: {output_format}")
    print(f"=" * 60)

    try:
        # Create configuration
        config = GeneratorConfig(
            output_dir=output_dir,
            formats=formats,
        )

        # Create generator
        print("\n→ Initializing wallust generator...")
        generator = WallustGenerator(
            config=config,
            backend_type=backend_type,
            output_format=output_format,
        )

        # Generate colorscheme
        print(f"→ Extracting colors from image...")
        colorscheme = generator.generate(image_path, color_count=color_count)

        print(f"✓ Extracted {len(colorscheme.colors)} colors")
        print(f"  Special colors: {colorscheme.special}")

        # Create output manager
        print(f"\n→ Writing output files...")
        output_manager = OutputManager(config=config)

        # Write output files
        output_files = output_manager.write_all(colorscheme)

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
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"  • metadata: {metadata_path}")

        print(f"\n{'=' * 60}")
        print(f"✓ Wallust backend completed successfully")
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

