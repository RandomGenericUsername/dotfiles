"""Core module for wallpaper processor."""

from wallpaper_processor.core.base import WallpaperEffect
from wallpaper_processor.core.exceptions import (
    EffectNotAvailableError,
    InvalidParametersError,
    PresetNotFoundError,
    ProcessingError,
    UnsupportedFormatError,
    WallpaperProcessorError,
)
from wallpaper_processor.core.types import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    EffectMetadata,
    EffectParams,
    ProcessingMetadata,
    ProcessorConfig,
    SaturationParams,
    VignetteParams,
)

__all__ = [
    # Base class
    "WallpaperEffect",
    # Exceptions
    "EffectNotAvailableError",
    "InvalidParametersError",
    "PresetNotFoundError",
    "ProcessingError",
    "UnsupportedFormatError",
    "WallpaperProcessorError",
    # Types
    "BlurParams",
    "BrightnessParams",
    "ColorOverlayParams",
    "EffectMetadata",
    "EffectParams",
    "ProcessingMetadata",
    "ProcessorConfig",
    "SaturationParams",
    "VignetteParams",
]

