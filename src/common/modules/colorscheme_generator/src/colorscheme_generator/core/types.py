"""Core type definitions for colorscheme generator.

This module defines the core data types used throughout the colorscheme generator:
- Color: Single color in multiple formats
- ColorScheme: Complete color scheme from an image
- GeneratorConfig: Runtime configuration for generation
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from colorscheme_generator.config.config import AppConfig
from colorscheme_generator.config.enums import Backend, ColorFormat


class Color(BaseModel):
    """Single color in multiple formats.
    
    Represents a color with hex, RGB, and optionally HSL values.
    
    Attributes:
        hex: Hex color code (e.g., "#FF5733")
        rgb: RGB tuple (0-255 for each channel)
        hsl: Optional HSL tuple (hue: 0-360, saturation: 0-1, lightness: 0-1)
    
    Example:
        >>> color = Color(hex="#FF5733", rgb=(255, 87, 51))
        >>> print(color.hex)
        '#FF5733'
    """

    hex: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    rgb: tuple[int, int, int]
    hsl: tuple[float, float, float] | None = None


class ColorScheme(BaseModel):
    """Complete color scheme from image.

    This is the output of backends - just color data.
    OutputManager writes this to files.
    
    Attributes:
        background: Background color
        foreground: Foreground/text color
        cursor: Cursor color
        colors: List of 16 terminal colors (ANSI colors 0-15)
        source_image: Path to source image
        backend: Backend used for generation
        generated_at: Timestamp of generation
        output_files: Dict of format -> path (populated by OutputManager)
    
    Example:
        >>> scheme = ColorScheme(
        ...     background=Color(hex="#1a1a1a", rgb=(26, 26, 26)),
        ...     foreground=Color(hex="#ffffff", rgb=(255, 255, 255)),
        ...     cursor=Color(hex="#ff0000", rgb=(255, 0, 0)),
        ...     colors=[...],  # 16 colors
        ...     source_image=Path("~/wallpapers/mountain.png"),
        ...     backend="pywal"
        ... )
    """

    background: Color
    foreground: Color
    cursor: Color
    colors: list[Color] = Field(..., min_length=16, max_length=16)

    # Metadata
    source_image: Path
    backend: str
    generated_at: datetime = Field(default_factory=datetime.now)

    # Output files (populated by OutputManager after writing)
    output_files: dict[str, Path] = Field(default_factory=dict)


class GeneratorConfig(BaseModel):
    """Runtime configuration for color scheme generation.

    Backends extract colors → OutputManager writes files.
    This config controls both steps.
    
    Settings from settings.toml provide defaults, but can be overridden here.
    
    Attributes:
        backend: Backend to use (overrides settings.generation.default_backend)
        color_count: Number of colors to extract (overrides settings.generation.default_color_count)
        saturation_adjustment: Saturation adjustment factor
        output_dir: Output directory (overrides settings.output.directory)
        formats: Output formats (overrides settings.output.formats)
        backend_options: Backend-specific options (merged with settings)
    
    Example:
        >>> config = GeneratorConfig(
        ...     backend=Backend.PYWAL,
        ...     output_dir=Path("/tmp/colors"),
        ...     formats=[ColorFormat.JSON, ColorFormat.CSS]
        ... )
    """

    # Color extraction settings (for backends)
    backend: Backend | None = None
    color_count: int | None = None
    saturation_adjustment: float | None = None

    # File output settings (for OutputManager)
    output_dir: Path | None = None  # Override settings.output.directory
    formats: list[ColorFormat] | None = None  # Override settings.output.formats

    # Backend-specific options (merged with settings)
    backend_options: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_settings(
        cls, settings: AppConfig, **overrides: Any
    ) -> "GeneratorConfig":
        """Create config from settings with optional overrides.

        Args:
            settings: AppConfig from settings.toml
            **overrides: Runtime overrides for any field

        Returns:
            GeneratorConfig with merged settings and overrides

        Example:
            >>> from colorscheme_generator.config.settings import Settings
            >>> config = GeneratorConfig.from_settings(
            ...     Settings.get(),
            ...     backend=Backend.WALLUST,
            ...     output_dir=Path("/tmp/colors")
            ... )
        """
        return cls(
            # Color extraction
            backend=overrides.get("backend")
            or Backend(settings.generation.default_backend),
            color_count=overrides.get("color_count")
            or settings.generation.default_color_count,
            saturation_adjustment=overrides.get("saturation_adjustment")
            or settings.generation.saturation_adjustment,
            # File output (OutputManager)
            output_dir=overrides.get("output_dir") or settings.output.directory,
            formats=overrides.get("formats")
            or [ColorFormat(f) for f in settings.output.formats],
            # Backend options
            backend_options=overrides.get("backend_options", {}),
        )

    def get_backend_settings(self, settings: AppConfig) -> dict[str, Any]:
        """Get backend-specific settings merged with runtime options.

        Args:
            settings: AppConfig from settings.toml

        Returns:
            Merged backend settings

        Example:
            >>> config = GeneratorConfig(backend=Backend.PYWAL)
            >>> backend_settings = config.get_backend_settings(Settings.get())
            >>> print(backend_settings["cache_dir"])
            PosixPath('/home/user/.cache/wal')
        """
        backend = self.backend or Backend(settings.generation.default_backend)

        if backend == Backend.PYWAL:
            base_settings = settings.backends.pywal.model_dump()
        elif backend == Backend.WALLUST:
            base_settings = settings.backends.wallust.model_dump()
        elif backend == Backend.CUSTOM:
            base_settings = settings.backends.custom.model_dump()
        else:
            base_settings = {}

        # Merge with runtime options
        return {**base_settings, **self.backend_options}

