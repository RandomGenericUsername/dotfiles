"""Factory for creating effect instances and pipelines."""

from __future__ import annotations

from pathlib import Path

# Import backends module to trigger effect registration
from wallpaper_processor import backends  # noqa: F401
from wallpaper_processor.config import AppConfig
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import (
    EffectNotAvailableError,
    PresetNotFoundError,
)
from wallpaper_processor.core.types import EffectParams, ProcessorConfig
from wallpaper_processor.pipeline import EffectPipeline


class EffectFactory:
    """Factory for creating effect instances."""

    @staticmethod
    def create(effect_name: str, settings: AppConfig) -> WallpaperEffect:
        """Create effect instance.

        Args:
            effect_name: Effect identifier (blur, brightness,
                saturation, vignette, color_overlay)
            settings: Application configuration

        Returns:
            WallpaperEffect instance

        Raises:
            ValueError: If effect_name is unknown
            EffectNotAvailableError: If effect dependencies
                unavailable (strict mode)
        """
        # Try ImageMagick first if preferred
        if settings.backend.prefer_imagemagick:
            im_effect = EffectFactory._create_imagemagick(effect_name)
            if im_effect is not None and im_effect.is_available():
                return im_effect

            # If strict mode, raise error
            if settings.backend.strict_mode:
                raise EffectNotAvailableError(
                    effect_name, f"ImageMagick not available for {effect_name}"
                )

        # Fallback to PIL (or use PIL if not preferring ImageMagick)
        if (
            settings.backend.fallback_enabled
            or not settings.backend.prefer_imagemagick
        ):
            pil_effect = EffectFactory._create_pil(effect_name)
            if pil_effect is not None:
                return pil_effect

        raise ValueError(f"Unknown effect: {effect_name}")

    @staticmethod
    def _create_imagemagick(effect_name: str) -> WallpaperEffect | None:
        """Create ImageMagick effect instance using registry.

        Args:
            effect_name: Effect identifier

        Returns:
            ImageMagick effect instance or None if unknown
        """
        from wallpaper_processor.core.registry import EffectRegistry

        effect_class = EffectRegistry.get_effect_class(
            effect_name, "imagemagick"
        )
        if effect_class:
            return effect_class()
        return None

    @staticmethod
    def _create_pil(effect_name: str) -> WallpaperEffect | None:
        """Create PIL effect instance using registry.

        Args:
            effect_name: Effect identifier

        Returns:
            PIL effect instance or None if unknown
        """
        from wallpaper_processor.core.registry import EffectRegistry

        effect_class = EffectRegistry.get_effect_class(effect_name, "pil")
        if effect_class:
            return effect_class()
        return None

    @staticmethod
    def create_from_preset(
        preset_name: str,
        settings: AppConfig,
        config: ProcessorConfig | None = None,
    ) -> EffectPipeline:
        """Create pipeline from preset.

        Args:
            preset_name: Preset identifier
            settings: Application configuration
            config: Processing configuration (uses defaults if None)

        Returns:
            EffectPipeline instance

        Raises:
            PresetNotFoundError: If preset doesn't exist
        """
        if preset_name not in settings.presets:
            raise PresetNotFoundError(preset_name)

        preset = settings.presets[preset_name]
        effects = []

        for effect_config in preset.effects:
            # Create effect instance
            effect = EffectFactory.create(effect_config.name, settings)

            # Create params instance
            params = EffectFactory._create_params(
                effect_config.name, effect_config.params
            )

            effects.append((effect, params))

        return EffectPipeline(effects, config)

    @staticmethod
    def create_params(effect_name: str, params_dict: dict) -> EffectParams:
        """Create params instance from dict (PUBLIC API).

        Args:
            effect_name: Effect identifier
            params_dict: Parameters dictionary

        Returns:
            EffectParams instance

        Raises:
            ValueError: If effect_name is unknown
        """
        from wallpaper_processor.core.registry import EffectRegistry

        params_class = EffectRegistry.get_params_class(effect_name)
        if not params_class:
            raise ValueError(f"Unknown effect: {effect_name}")
        return params_class(**params_dict)

    @staticmethod
    def _create_params(effect_name: str, params_dict: dict) -> EffectParams:
        """Create params instance from dict (DEPRECATED - use create_params).

        Args:
            effect_name: Effect identifier
            params_dict: Parameters dictionary

        Returns:
            EffectParams instance
        """
        # Backwards compatibility wrapper
        return EffectFactory.create_params(effect_name, params_dict)

    @staticmethod
    def get_all_effect_names() -> list[str]:
        """Get list of all registered effect names from registry.

        Returns:
            Sorted list of effect names
        """
        from wallpaper_processor.core.registry import EffectRegistry

        return EffectRegistry.get_all_effect_names()

    @staticmethod
    def list_available_effects(_settings: AppConfig) -> dict[str, list[str]]:
        """List available effects and their backends.

        Args:
            _settings: Application configuration (unused, for future use)

        Returns:
            Dict mapping effect names to list of available backends
        """
        effects = EffectFactory.get_all_effect_names()
        available = {}

        for effect_name in effects:
            backends = []

            # Check ImageMagick
            im_effect = EffectFactory._create_imagemagick(effect_name)
            if im_effect is not None and im_effect.is_available():
                backends.append("imagemagick")

            # Check PIL
            pil_effect = EffectFactory._create_pil(effect_name)
            if pil_effect is not None and pil_effect.is_available():
                backends.append("pil")

            if backends:
                available[effect_name] = backends

        return available

    @staticmethod
    def generate_all_variants(
        input_path: Path,
        output_dir: Path,
        settings: AppConfig | None = None,
        config: ProcessorConfig | None = None,
    ) -> dict[str, Path]:
        """Generate all effect variants for an input image.

        Creates a subdirectory named after the input image
        (without extension) and generates one variant for each
        available effect with default parameters.

        Args:
            input_path: Path to input image
            output_dir: Base output directory
            settings: Application configuration (uses defaults if None)
            config: Processing configuration (uses defaults if None)

        Returns:
            Dict mapping effect names to output paths

        Raises:
            FileNotFoundError: If input file doesn't exist

        Example:
            >>> factory = EffectFactory()
            >>> variants = factory.generate_all_variants(
            ...     Path("canary.png"),
            ...     Path("/tmp/wallpaper")
            ... )
            >>> # Creates:
            >>> # /tmp/wallpaper/canary/blur.png
            >>> # /tmp/wallpaper/canary/grayscale.png
            >>> # /tmp/wallpaper/canary/negate.png
            >>> # etc.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if settings is None:
            settings = AppConfig()

        if config is None:
            config = ProcessorConfig()

        # Get image name without extension
        image_name = input_path.stem

        # Create output subdirectory
        variant_dir = output_dir / image_name
        variant_dir.mkdir(parents=True, exist_ok=True)

        # Get all available effects
        effects = EffectFactory.list_available_effects()

        # Generate variant for each effect
        results = {}
        for effect_name in effects:
            # Create effect with default parameters
            effect = EffectFactory.create(effect_name, settings)
            params = EffectFactory._create_params(effect_name, {})

            # Create pipeline with single effect
            pipeline = EffectPipeline([(effect, params)], config)

            # Determine output extension
            output_ext = config.output_format.value
            if output_ext == "jpg":
                output_ext = "jpeg"

            # Generate output path
            output_path = variant_dir / f"{effect_name}.{output_ext}"

            # Apply effect
            pipeline.apply(input_path, output_path)

            results[effect_name] = output_path

        return results
