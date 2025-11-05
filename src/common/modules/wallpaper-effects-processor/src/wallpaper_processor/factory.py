"""Factory for creating effect instances and pipelines."""

from __future__ import annotations

from pathlib import Path

from wallpaper_processor.backends import (
    ImageMagickBlur,
    ImageMagickBrightness,
    ImageMagickColorOverlay,
    ImageMagickGrayscale,
    ImageMagickNegate,
    ImageMagickSaturation,
    ImageMagickVignette,
    PILBlur,
    PILBrightness,
    PILColorOverlay,
    PILGrayscale,
    PILNegate,
    PILSaturation,
    PILVignette,
)
from wallpaper_processor.config import AppConfig
from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import (
    EffectNotAvailableError,
    PresetNotFoundError,
)
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    GrayscaleParams,
    NegateParams,
    ProcessorConfig,
    SaturationParams,
    VignetteParams,
)
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
        """Create ImageMagick effect instance.

        Args:
            effect_name: Effect identifier

        Returns:
            ImageMagick effect instance or None if unknown
        """
        if effect_name == "blur":
            return ImageMagickBlur()
        elif effect_name == "brightness":
            return ImageMagickBrightness()
        elif effect_name == "saturation":
            return ImageMagickSaturation()
        elif effect_name == "vignette":
            return ImageMagickVignette()
        elif effect_name == "color_overlay":
            return ImageMagickColorOverlay()
        elif effect_name == "grayscale":
            return ImageMagickGrayscale()
        elif effect_name == "negate":
            return ImageMagickNegate()
        return None

    @staticmethod
    def _create_pil(effect_name: str) -> WallpaperEffect | None:
        """Create PIL effect instance.

        Args:
            effect_name: Effect identifier

        Returns:
            PIL effect instance or None if unknown
        """
        if effect_name == "blur":
            return PILBlur()
        elif effect_name == "brightness":
            return PILBrightness()
        elif effect_name == "saturation":
            return PILSaturation()
        elif effect_name == "vignette":
            return PILVignette()
        elif effect_name == "color_overlay":
            return PILColorOverlay()
        elif effect_name == "grayscale":
            return PILGrayscale()
        elif effect_name == "negate":
            return PILNegate()
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
    def _create_params(effect_name: str, params_dict: dict) -> object:
        """Create params instance from dict.

        Args:
            effect_name: Effect identifier
            params_dict: Parameters dictionary

        Returns:
            EffectParams instance
        """
        if effect_name == "blur":
            return BlurParams(**params_dict)
        elif effect_name == "brightness":
            return BrightnessParams(**params_dict)
        elif effect_name == "saturation":
            return SaturationParams(**params_dict)
        elif effect_name == "vignette":
            return VignetteParams(**params_dict)
        elif effect_name == "color_overlay":
            return ColorOverlayParams(**params_dict)
        elif effect_name == "grayscale":
            return GrayscaleParams(**params_dict)
        elif effect_name == "negate":
            return NegateParams(**params_dict)
        else:
            raise ValueError(f"Unknown effect: {effect_name}")

    @staticmethod
    def get_all_effect_names() -> list[str]:
        """Get list of all registered effect names.

        Returns:
            List of effect names
        """
        return [
            "blur",
            "brightness",
            "saturation",
            "vignette",
            "color_overlay",
            "grayscale",
            "negate",
        ]

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
