#!/usr/bin/env python3
"""Entrypoint for custom backend container."""

import json
import os
import sys
from pathlib import Path

from colorscheme_generator import (
    CustomGenerator,
    GeneratorConfig,
    OutputManager,
)


def main():
    """Main entrypoint for custom backend."""
    # Get environment variables
    image_path = os.getenv("IMAGE_PATH")
    output_dir = os.getenv("OUTPUT_DIR", "/output")
    formats = os.getenv("FORMATS", "json,css,yaml,sh").split(",")
    color_count = int(os.getenv("COLOR_COUNT", "16"))
    algorithm = os.getenv("ALGORITHM", "kmeans")

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

    print("Custom Backend Container")
    print("=" * 60)
    print(f"Image:      {image_path}")
    print(f"Output:     {output_dir}")
    print(f"Formats:    {', '.join(formats)}")
    print(f"Colors:     {color_count}")
    print(f"Algorithm:  {algorithm}")
    print("=" * 60)

    try:
        # Create configuration
        config = GeneratorConfig(
            output_dir=output_dir,
            formats=formats,
        )

        # Create generator
        print("\n→ Initializing custom generator...")
        generator = CustomGenerator(config=config, algorithm=algorithm)

        # Generate colorscheme
        print(f"→ Extracting colors from image using {algorithm}...")
        colorscheme = generator.generate(image_path, color_count=color_count)

        print(f"✓ Extracted {len(colorscheme.colors)} colors")
        print(f"  Special colors: {colorscheme.special}")

        # Create output manager
        print("\n→ Writing output files...")
        output_manager = OutputManager(config=config)

        # Write output files
        output_files = output_manager.write_all(colorscheme)

        print(f"✓ Generated {len(output_files)} files:")
        for fmt, path in output_files.items():
            print(f"  • {fmt}: {path}")

        # Write metadata file
        metadata = {
            "backend": "custom",
            "image": str(image_path),
            "color_count": len(colorscheme.colors),
            "formats": list(output_files.keys()),
            "output_files": {k: str(v) for k, v in output_files.items()},
            "algorithm": algorithm,
        }
        metadata_path = output_dir / "metadata.json"
        with metadata_path.open("w") as f:
            json.dump(metadata, f, indent=2)
        print(f"  • metadata: {metadata_path}")

        print(f"\n{'=' * 60}")
        print("✓ Custom backend completed successfully")
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
