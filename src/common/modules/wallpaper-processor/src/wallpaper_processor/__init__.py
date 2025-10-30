"""Wallpaper processor module for applying effects to wallpapers."""

# Configuration
from wallpaper_processor.config import (
    AppConfig,
    BackendConfig,
    EffectDefaults,
    Preset,
    PresetEffect,
    ProcessingConfig,
    get_default_config,
    load_settings,
)

# Core
from wallpaper_processor.core import (
    BlurParams,
    BrightnessParams,
    ColorOverlayParams,
    EffectMetadata,
    EffectNotAvailableError,
    EffectParams,
    InvalidParametersError,
    PresetNotFoundError,
    ProcessingError,
    ProcessingMetadata,
    ProcessorConfig,
    SaturationParams,
    UnsupportedFormatError,
    VignetteParams,
    WallpaperEffect,
    WallpaperProcessorError,
)

# Managers
from wallpaper_processor.core.managers import OutputManager, PresetManager

# Factory and Pipeline
from wallpaper_processor.factory import EffectFactory
from wallpaper_processor.pipeline import EffectPipeline

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "AppConfig",
    "BackendConfig",
    "EffectDefaults",
    "Preset",
    "PresetEffect",
    "ProcessingConfig",
    "get_default_config",
    "load_settings",
    # Core
    "BlurParams",
    "BrightnessParams",
    "ColorOverlayParams",
    "EffectMetadata",
    "EffectNotAvailableError",
    "EffectParams",
    "InvalidParametersError",
    "PresetNotFoundError",
    "ProcessingError",
    "ProcessingMetadata",
    "ProcessorConfig",
    "SaturationParams",
    "UnsupportedFormatError",
    "VignetteParams",
    "WallpaperEffect",
    "WallpaperProcessorError",
    # Managers
    "OutputManager",
    "PresetManager",
    # Factory and Pipeline
    "EffectFactory",
    "EffectPipeline",
]

