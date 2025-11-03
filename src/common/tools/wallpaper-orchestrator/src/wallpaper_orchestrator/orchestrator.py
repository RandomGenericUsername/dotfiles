"""Orchestrator for wallpaper processing."""

from pathlib import Path

from dotfiles_container_manager import ContainerEngineFactory, ContainerRuntime

from wallpaper_orchestrator.config import AppConfig
from wallpaper_orchestrator.containers import (
    ContainerBuilder,
    ContainerRegistry,
    ContainerRunner,
)


class WallpaperOrchestrator:
    """Orchestrates wallpaper processing in containers."""

    def __init__(self, config: AppConfig):
        """Initialize orchestrator.

        Args:
            config: Application configuration
        """
        self.config = config

        # Initialize container engine
        runtime = ContainerRuntime(config.container.runtime)
        self.engine = ContainerEngineFactory.create(runtime)

        # Initialize components
        self.registry = ContainerRegistry(config.container)
        self.builder = ContainerBuilder(self.engine.images, config.container)
        self.runner = ContainerRunner(
            self.engine.containers, config.container, config.processing
        )

    def ensure_image(self, force_rebuild: bool = False) -> None:
        """Ensure container image exists.

        Args:
            force_rebuild: Force rebuild even if image exists

        Raises:
            ImageBuildError: If build fails
        """
        if not force_rebuild and self.registry.image_exists():
            return

        # Get container files
        container_dir = Path(__file__).parent.parent.parent / "container"
        dockerfile_path = container_dir / "Dockerfile"
        entrypoint_path = container_dir / "entrypoint.py"

        # Prepare build context
        dockerfile_content, files = self.builder.prepare_build_context(
            dockerfile_path, entrypoint_path
        )

        # Build
        self.builder.build(dockerfile_content, files)

    def process_image(
        self,
        input_path: Path,
        output_path: Path,
        preset: str | None = None,
        effects: list[str] | None = None,
        effect_params: dict | None = None,
    ) -> bool:
        """Process single image.

        Args:
            input_path: Input image path
            output_path: Output image path
            preset: Preset name (if using preset)
            effects: List of effect names (if not using preset)
            effect_params: Effect parameters dict (if not using preset)

        Returns:
            True if successful, False otherwise
        """
        # Ensure image exists
        self.ensure_image()

        # Validate input
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run processing
        if preset:
            exit_code, stdout, stderr = self.runner.run_preset(
                input_path, output_path, preset
            )
        elif effects:
            exit_code, stdout, stderr = self.runner.run_effects(
                input_path, output_path, effects, effect_params or {}
            )
        else:
            raise ValueError("Either preset or effects must be specified")

        # Check result
        if exit_code != 0:
            print(f"Processing failed: {stderr or stdout}")
            return False

        return True

    def process_batch(
        self,
        input_dir: Path,
        output_dir: Path,
        preset: str | None = None,
        effects: list[str] | None = None,
        effect_params: dict | None = None,
        parallel: int = 1,
        skip_existing: bool = False,
        continue_on_error: bool = True,
    ) -> tuple[int, int]:
        """Process batch of images.

        Args:
            input_dir: Input directory
            output_dir: Output directory
            preset: Preset name (if using preset)
            effects: List of effect names (if not using preset)
            effect_params: Effect parameters dict (if not using preset)
            parallel: Number of parallel processes
            skip_existing: Skip existing output files
            continue_on_error: Continue on processing errors

        Returns:
            Tuple of (successful_count, failed_count)
        """
        # Ensure image exists
        self.ensure_image()

        # Find input images
        image_extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        input_files = [
            f
            for f in input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]

        if not input_files:
            print(f"No images found in {input_dir}")
            return 0, 0

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Process images
        successful = 0
        failed = 0

        if parallel > 1:
            # Parallel processing
            from concurrent.futures import ThreadPoolExecutor, as_completed

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {}
                for input_file in input_files:
                    output_file = output_dir / input_file.name

                    # Skip if exists
                    if skip_existing and output_file.exists():
                        continue

                    future = executor.submit(
                        self.process_image,
                        input_file,
                        output_file,
                        preset,
                        effects,
                        effect_params,
                    )
                    futures[future] = input_file

                for future in as_completed(futures):
                    input_file = futures[future]
                    try:
                        if future.result():
                            successful += 1
                            print(f"✓ {input_file.name}")
                        else:
                            failed += 1
                            print(f"✗ {input_file.name}")
                    except Exception as e:
                        failed += 1
                        print(f"✗ {input_file.name}: {e}")
                        if not continue_on_error:
                            break
        else:
            # Sequential processing
            for input_file in input_files:
                output_file = output_dir / input_file.name

                # Skip if exists
                if skip_existing and output_file.exists():
                    continue

                try:
                    if self.process_image(
                        input_file, output_file, preset, effects, effect_params
                    ):
                        successful += 1
                        print(f"✓ {input_file.name}")
                    else:
                        failed += 1
                        print(f"✗ {input_file.name}")
                except Exception as e:
                    failed += 1
                    print(f"✗ {input_file.name}: {e}")
                    if not continue_on_error:
                        break

        return successful, failed

    def generate_all_variants(
        self, input_path: Path, output_dir: Path
    ) -> dict[str, Path]:
        """Generate all effect variants for an input image.

        Creates a subdirectory named after the input image (without
        extension) and generates one variant for each available effect
        with default parameters.

        Args:
            input_path: Path to input image
            output_dir: Base output directory

        Returns:
            Dict mapping effect names to output paths

        Raises:
            FileNotFoundError: If input file doesn't exist

        Example:
            >>> orchestrator = WallpaperOrchestrator(config)
            >>> variants = orchestrator.generate_all_variants(
            ...     Path("canary.png"),
            ...     Path("/tmp/wallpaper")
            ... )
            >>> # Creates:
            >>> # /tmp/wallpaper/canary/blur.png
            >>> # /tmp/wallpaper/canary/grayscale.png
            >>> # /tmp/wallpaper/canary/negate.png
            >>> # etc.
        """
        # Ensure image exists
        self.ensure_image()

        # Validate input
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Get image name without extension
        image_name = input_path.stem

        # Create output subdirectory
        variant_dir = output_dir / image_name
        variant_dir.mkdir(parents=True, exist_ok=True)

        # Get all available effects
        from wallpaper_processor.factory import EffectFactory

        effects = EffectFactory.get_all_effect_names()

        # Generate variant for each effect
        results = {}
        for effect_name in effects:
            # Determine output extension (use PNG for consistency)
            output_path = variant_dir / f"{effect_name}.png"

            # Process with single effect and default parameters
            success = self.process_image(
                input_path=input_path,
                output_path=output_path,
                effects=[effect_name],
                effect_params={},
            )

            if success:
                results[effect_name] = output_path

        return results

    def clean(self) -> None:
        """Clean container resources."""
        self.registry.remove_image(force=True)
        self.registry.prune_images()
