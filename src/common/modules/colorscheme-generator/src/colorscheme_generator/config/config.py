"""Pydantic configuration models for colorscheme generator.

This module defines the configuration structure that matches the
settings.toml file. It uses Pydantic for validation and type safety,
following the same pattern as the dotfiles installer.
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from colorscheme_generator.config.defaults import (
    custom_algorithm,
    custom_n_clusters,
    default_backend,
    default_color_count,
    default_formats,
    output_directory,
    pywal_cache_dir,
    pywal_use_library,
    saturation_adjustment,
    template_directory,
    template_strict_mode,
    wallust_backend_type,
    wallust_output_format,
)
from colorscheme_generator.config.enums import Backend, ColorAlgorithm


class OutputSettings(BaseModel):
    """Output configuration (controlled by OutputManager).

    These settings control where and how the OutputManager writes
    generated color scheme files. Backends don't use these settings.
    """

    directory: Path = Field(
        default=output_directory,
        description="Directory where OutputManager writes generated files",
    )
    formats: list[str] = Field(
        default_factory=lambda: default_formats.copy(),
        description="Output formats to generate",
    )


class GenerationSettings(BaseModel):
    """Color scheme generation defaults.

    These settings provide default values for color extraction
    that can be overridden at runtime via GeneratorConfig.
    """

    default_backend: str = Field(
        default=default_backend,
        description="Default backend for color extraction",
    )
    default_color_count: int = Field(
        default=default_color_count,
        ge=8,
        le=256,
        description="Default number of colors to extract",
    )
    saturation_adjustment: float = Field(
        default=saturation_adjustment,
        ge=0.0,
        le=2.0,
        description="Default saturation adjustment factor",
    )

    @field_validator("default_backend", mode="before")
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate backend string."""
        try:
            Backend(v)
            return v
        except ValueError:
            valid = ", ".join([b.value for b in Backend])
            raise ValueError(
                f"Invalid backend '{v}'. Valid options: {valid}"
            ) from None


class PywalBackendSettings(BaseModel):
    """Pywal backend configuration (for color extraction only).

    Note: Pywal always writes to ~/.cache/wal/ internally.
    We read from there to extract colors, but OutputManager
    writes our own files to the configured output directory.
    """

    cache_dir: Path = Field(
        default=pywal_cache_dir,
        description="Where pywal writes its files (read-only for us)",
    )
    use_library: bool = Field(
        default=pywal_use_library,
        description="Use pywal as Python library instead of CLI",
    )


class WallustBackendSettings(BaseModel):
    """Wallust backend configuration (for color extraction only).

    Note: We run wallust with JSON output to stdout and parse it.
    We don't use wallust's template system - OutputManager handles file
    generation.
    """

    output_format: str = Field(
        default=wallust_output_format,
        description="Output format for wallust (json, plain, etc.)",
    )
    backend_type: str = Field(
        default=wallust_backend_type,
        description="Wallust backend type (resized, full, etc.)",
    )


class CustomBackendSettings(BaseModel):
    """Custom Python backend configuration."""

    algorithm: str = Field(
        default=custom_algorithm, description="Color extraction algorithm"
    )
    n_clusters: int = Field(
        default=custom_n_clusters,
        ge=8,
        le=256,
        description="Number of color clusters for extraction",
    )

    @field_validator("algorithm", mode="before")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate algorithm string."""
        try:
            ColorAlgorithm(v)
            return v
        except ValueError:
            valid = ", ".join([a.value for a in ColorAlgorithm])
            raise ValueError(
                f"Invalid algorithm '{v}'. Valid options: {valid}"
            ) from None


class BackendSettings(BaseModel):
    """Backend-specific configurations (for color extraction only)."""

    pywal: PywalBackendSettings = Field(
        default_factory=PywalBackendSettings,
        description="Pywal backend settings",
    )
    wallust: WallustBackendSettings = Field(
        default_factory=WallustBackendSettings,
        description="Wallust backend settings",
    )
    custom: CustomBackendSettings = Field(
        default_factory=CustomBackendSettings,
        description="Custom backend settings",
    )


class TemplateSettings(BaseModel):
    """Template rendering configuration (for OutputManager)."""

    directory: Path = Field(
        default=template_directory,
        description="Directory containing Jinja2 templates",
    )
    strict_mode: bool = Field(
        default=template_strict_mode,
        description="Fail on missing template variables",
    )


class AppConfig(BaseModel):
    """Application configuration matching dynaconf structure.

    This is the root configuration model that aggregates all settings
    from settings.toml. It follows the same pattern as the dotfiles
    installer's AppConfig.
    """

    output: OutputSettings = Field(
        default_factory=OutputSettings,
        description="Output configuration (OutputManager)",
    )
    generation: GenerationSettings = Field(
        default_factory=GenerationSettings, description="Generation defaults"
    )
    backends: BackendSettings = Field(
        default_factory=BackendSettings,
        description="Backend-specific settings (color extraction only)",
    )
    templates: TemplateSettings = Field(
        default_factory=TemplateSettings,
        description="Template configuration (OutputManager)",
    )
