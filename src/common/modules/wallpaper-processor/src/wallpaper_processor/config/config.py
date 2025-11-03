"""Pydantic configuration models for wallpaper processor."""

from typing import Any

from pydantic import BaseModel, Field

from wallpaper_processor.config.defaults import (
    DEFAULT_FALLBACK_ENABLED,
    DEFAULT_IMAGEMAGICK_BINARY,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_PREFER_IMAGEMAGICK,
    DEFAULT_PROCESSING_MODE,
    DEFAULT_QUALITY,
    DEFAULT_STRICT_MODE,
    DEFAULT_WRITE_METADATA,
)
from wallpaper_processor.config.enums import OutputFormat, ProcessingMode


class ProcessingConfig(BaseModel):
    """Processing configuration."""

    mode: ProcessingMode = DEFAULT_PROCESSING_MODE
    output_format: OutputFormat = DEFAULT_OUTPUT_FORMAT
    quality: int = Field(
        ge=1,
        le=100,
        default=DEFAULT_QUALITY,
        description="Quality for lossy formats",
    )
    write_metadata: bool = DEFAULT_WRITE_METADATA


class BackendConfig(BaseModel):
    """Backend configuration."""

    prefer_imagemagick: bool = DEFAULT_PREFER_IMAGEMAGICK
    imagemagick_binary: str = DEFAULT_IMAGEMAGICK_BINARY
    strict_mode: bool = DEFAULT_STRICT_MODE
    fallback_enabled: bool = DEFAULT_FALLBACK_ENABLED


class EffectDefaults(BaseModel):
    """Default parameters for all effects."""

    blur: dict[str, Any] = Field(
        default_factory=lambda: {"radius": 0, "sigma": 8}
    )
    brightness: dict[str, Any] = Field(
        default_factory=lambda: {"adjustment": -20}
    )
    saturation: dict[str, Any] = Field(
        default_factory=lambda: {"adjustment": 0}
    )
    vignette: dict[str, Any] = Field(default_factory=lambda: {"strength": 20})
    color_overlay: dict[str, Any] = Field(
        default_factory=lambda: {"color": "#000000", "opacity": 0.3}
    )


class PresetEffect(BaseModel):
    """Single effect in a preset."""

    name: str
    params: dict[str, Any]


class Preset(BaseModel):
    """Effect preset configuration."""

    description: str
    effects: list[PresetEffect]


class AppConfig(BaseModel):
    """Application configuration."""

    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    backend: BackendConfig = Field(default_factory=BackendConfig)
    defaults: EffectDefaults = Field(default_factory=EffectDefaults)
    presets: dict[str, Preset] = Field(default_factory=dict)
