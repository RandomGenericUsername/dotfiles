#!/usr/bin/env python3
"""Container entrypoint for wallpaper processing."""

import json
import os
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, "/app")

from wallpaper_processor import (
    EffectFactory,
    EffectPipeline,
    ProcessorConfig,
    get_default_config,
)


def main() -> int:
    """Main entrypoint."""
    try:
        # Get environment variables
        image_path = Path(os.environ.get("IMAGE_PATH", "/input/image"))
        output_path = Path(os.environ.get("OUTPUT_PATH", "/output/output.png"))
        preset = os.environ.get("PRESET", "")
        effects_str = os.environ.get("EFFECTS", "")
        effect_params_str = os.environ.get("EFFECT_PARAMS", "{}")
        processing_mode = os.environ.get("PROCESSING_MODE", "memory")
        output_format = os.environ.get("OUTPUT_FORMAT", "png")
        quality = int(os.environ.get("QUALITY", "95"))
        write_metadata = os.environ.get("WRITE_METADATA", "false").lower() == "true"

        # Validate input
        if not image_path.exists():
            print(f"Error: Input image not found: {image_path}", file=sys.stderr)
            return 1

        # Load configuration
        config = get_default_config()

        # Create processor config
        proc_config = ProcessorConfig(
            processing_mode=processing_mode,
            output_format=output_format,
            quality=quality,
            write_metadata=write_metadata,
        )

        # Create pipeline
        if preset:
            # Use preset
            print(f"Using preset: {preset}")
            pipeline = EffectFactory.create_from_preset(preset, config, proc_config)
        elif effects_str:
            # Use individual effects
            effects = effects_str.split(",")
            effect_params = json.loads(effect_params_str)

            print(f"Applying effects: {', '.join(effects)}")

            # Build pipeline
            pipeline_effects = []
            for effect_name in effects:
                effect = EffectFactory.create(effect_name.strip(), config)
                params = EffectFactory._create_params(
                    effect_name.strip(), effect_params.get(effect_name.strip(), {})
                )
                pipeline_effects.append((effect, params))

            pipeline = EffectPipeline(pipeline_effects, proc_config)
        else:
            print("Error: No preset or effects specified", file=sys.stderr)
            return 1

        # Apply pipeline
        print(f"Processing {image_path} -> {output_path}")
        pipeline.apply(image_path, output_path)

        print("✓ Processing complete")

        if write_metadata:
            metadata_path = output_path.parent / f"{output_path.stem}_metadata.json"
            print(f"✓ Metadata written to {metadata_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

