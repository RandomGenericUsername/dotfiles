"""Type definitions and Pydantic models for wallpaper processor."""

from pathlib import Path

from pydantic import BaseModel, Field

from wallpaper_processor.config.defaults import (
    DEFAULT_BLUR_RADIUS,
    DEFAULT_BLUR_SIGMA,
    DEFAULT_BRIGHTNESS_ADJUSTMENT,
    DEFAULT_COLOR_OVERLAY_COLOR,
    DEFAULT_COLOR_OVERLAY_OPACITY,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PROCESSING_MODE,
    DEFAULT_QUALITY,
    DEFAULT_SATURATION_ADJUSTMENT,
    DEFAULT_VIGNETTE_STRENGTH,
    DEFAULT_WRITE_METADATA,
)
from wallpaper_processor.config.enums import OutputFormat, ProcessingMode


class EffectParams(BaseModel):
    """Base class for effect parameters."""

    pass


class BlurParams(EffectParams):
    """Parameters for blur effect."""

    sigma: float = Field(
        ge=0,
        le=100,
        default=DEFAULT_BLUR_SIGMA,
        description="Blur strength (sigma)",
    )
    radius: float = Field(
        ge=0, le=50, default=DEFAULT_BLUR_RADIUS, description="Blur radius"
    )


class BrightnessParams(EffectParams):
    """Parameters for brightness effect."""

    adjustment: int = Field(
        ge=-100,
        le=100,
        default=DEFAULT_BRIGHTNESS_ADJUSTMENT,
        description="Brightness adjustment percentage",
    )


class SaturationParams(EffectParams):
    """Parameters for saturation effect."""

    adjustment: int = Field(
        ge=-100,
        le=100,
        default=DEFAULT_SATURATION_ADJUSTMENT,
        description="Saturation adjustment percentage",
    )


class VignetteParams(EffectParams):
    """Parameters for vignette effect."""

    strength: int = Field(
        ge=0,
        le=100,
        default=DEFAULT_VIGNETTE_STRENGTH,
        description="Vignette strength percentage",
    )


class ColorOverlayParams(EffectParams):
    """Parameters for color overlay effect."""

    color: str = Field(
        default=DEFAULT_COLOR_OVERLAY_COLOR,
        description="Hex color code (e.g., #ff00ff)",
    )
    opacity: float = Field(
        ge=0.0,
        le=1.0,
        default=DEFAULT_COLOR_OVERLAY_OPACITY,
        description="Overlay opacity (0.0 to 1.0)",
    )


class GrayscaleParams(EffectParams):
    """Parameters for grayscale effect."""

    method: str = Field(
        default="average",
        description="Grayscale conversion method (average, luminosity, mean)",
    )


class NegateParams(EffectParams):
    """Parameters for negate (color inversion) effect."""

    pass


class ProcessorConfig(BaseModel):
    """Runtime configuration for wallpaper processor."""

    processing_mode: ProcessingMode = DEFAULT_PROCESSING_MODE
    output_format: OutputFormat = DEFAULT_OUTPUT_FORMAT
    quality: int = Field(
        ge=1,
        le=100,
        default=DEFAULT_QUALITY,
        description="Quality for lossy formats",
    )
    write_metadata: bool = DEFAULT_WRITE_METADATA


class EffectMetadata(BaseModel):
    """Metadata about an applied effect."""

    name: str
    backend: str
    params: dict[str, float | int | str]


class ProcessingMetadata(BaseModel):
    """Metadata about the processing operation."""

    input_path: Path
    output_path: Path
    effects_applied: list[EffectMetadata]
    processing_mode: ProcessingMode
    output_format: OutputFormat
    quality: int
