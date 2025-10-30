"""Configuration module for wallpaper processor."""

from wallpaper_processor.config.config import (
    AppConfig,
    BackendConfig,
    EffectDefaults,
    Preset,
    PresetEffect,
    ProcessingConfig,
)
from wallpaper_processor.config.enums import (
    BackendType,
    EffectName,
    OutputFormat,
    ProcessingMode,
)
from wallpaper_processor.config.settings import get_default_config, load_settings

__all__ = [
    # Config models
    "AppConfig",
    "BackendConfig",
    "EffectDefaults",
    "Preset",
    "PresetEffect",
    "ProcessingConfig",
    # Enums
    "BackendType",
    "EffectName",
    "OutputFormat",
    "ProcessingMode",
    # Settings loader
    "get_default_config",
    "load_settings",
]

