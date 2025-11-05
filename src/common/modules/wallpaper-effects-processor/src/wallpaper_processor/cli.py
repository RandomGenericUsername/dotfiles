"""CLI interface for wallpaper processor (standalone mode)."""

import sys
from pathlib import Path

from wallpaper_processor import (
    EffectFactory,
    EffectPipeline,
    ProcessorConfig,
    get_default_config,
)
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    SaturationParams,
    VignetteParams,
)


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Apply effects to wallpapers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single effect
  wallpaper-process -i input.jpg -o output.jpg -e blur --sigma 8

  # Multiple effects
  wallpaper-process -i input.jpg -o output.jpg \\
    -e blur --sigma 6 \\
    -e brightness --adjustment -15

  # Use preset
  wallpaper-process -i input.jpg -o output.jpg --preset dark_blur

  # List available effects
  wallpaper-process --list-effects

  # List presets
  wallpaper-process --list-presets
        """,
    )

    parser.add_argument("-i", "--input", type=Path, help="Input image path")
    parser.add_argument("-o", "--output", type=Path, help="Output image path")
    parser.add_argument(
        "-e",
        "--effect",
        action="append",
        dest="effects",
        help="Effect to apply (can be specified multiple times)",
    )
    parser.add_argument("--preset", type=str, help="Use preset")
    parser.add_argument(
        "--list-effects", action="store_true", help="List available effects"
    )
    parser.add_argument(
        "--list-presets", action="store_true", help="List available presets"
    )

    # Effect parameters
    parser.add_argument("--sigma", type=float, help="Blur sigma")
    parser.add_argument("--radius", type=float, help="Blur radius")
    parser.add_argument(
        "--adjustment", type=int, help="Brightness/saturation adjustment"
    )
    parser.add_argument("--strength", type=int, help="Vignette strength")
    parser.add_argument("--color", type=str, help="Color overlay hex code")
    parser.add_argument("--opacity", type=float, help="Color overlay opacity")

    # Processing options
    parser.add_argument(
        "--mode",
        choices=["memory", "file"],
        help="Processing mode (memory or file)",
    )
    parser.add_argument("--quality", type=int, help="Output quality (1-100)")
    parser.add_argument(
        "--metadata", action="store_true", help="Write metadata file"
    )

    args = parser.parse_args()

    # Load configuration
    config = get_default_config()

    # List effects
    if args.list_effects:
        available = EffectFactory.list_available_effects(config)
        print("Available Effects:")
        for effect_name, backends in available.items():
            print(f"  {effect_name}: {', '.join(backends)}")
        return

    # List presets
    if args.list_presets:
        from wallpaper_processor.core.managers import PresetManager

        manager = PresetManager(config)
        presets = manager.list_presets()
        print("Available Presets:")
        for name, description in presets.items():
            print(f"  {name}: {description}")
        return

    # Validate required arguments
    if not args.input or not args.output:
        parser.error("--input and --output are required")

    # Build processor config
    proc_config = ProcessorConfig()
    if args.mode:
        proc_config.processing_mode = args.mode
    if args.quality:
        proc_config.quality = args.quality
    if args.metadata:
        proc_config.write_metadata = True

    # Build pipeline
    if args.preset:
        # Use preset
        pipeline = EffectFactory.create_from_preset(
            args.preset, config, proc_config
        )
    elif args.effects:
        # Build from individual effects
        effects = []
        for effect_name in args.effects:
            effect = EffectFactory.create(effect_name, config)

            # Create params based on effect type
            if effect_name == "blur":
                params = BlurParams(
                    sigma=args.sigma if args.sigma is not None else 8,
                    radius=args.radius if args.radius is not None else 0,
                )
            elif effect_name == "brightness":
                params = BrightnessParams(
                    adjustment=(
                        args.adjustment if args.adjustment is not None else -20
                    )
                )
            elif effect_name == "saturation":
                params = SaturationParams(
                    adjustment=(
                        args.adjustment if args.adjustment is not None else 0
                    )
                )
            elif effect_name == "vignette":
                params = VignetteParams(
                    strength=args.strength if args.strength is not None else 20
                )
            elif effect_name == "color_overlay":
                params = ColorOverlayParams(
                    color=args.color if args.color is not None else "#000000",
                    opacity=args.opacity if args.opacity is not None else 0.3,
                )
            else:
                print(f"Unknown effect: {effect_name}", file=sys.stderr)
                sys.exit(1)

            effects.append((effect, params))

        pipeline = EffectPipeline(effects, proc_config)
    else:
        parser.error("Either --preset or --effect must be specified")

    # Apply pipeline
    try:
        print(f"Processing {args.input} -> {args.output}")
        pipeline.apply(args.input, args.output)
        print("✓ Processing complete")

        if proc_config.write_metadata:
            metadata_path = (
                args.output.parent / f"{args.output.stem}_metadata.json"
            )
            print(f"✓ Metadata written to {metadata_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
