"""Configuration management for rofi-colorscheme-viewer."""

from pathlib import Path

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    """Paths configuration."""

    colorscheme_file: Path = Field(
        ..., description="Path to colorscheme JSON file"
    )
    temp_dir: Path = Field(
        ..., description="Temporary directory for swatches and state"
    )


class RofiConfig(BaseModel):
    """Rofi display configuration."""

    show_icons: bool = Field(
        True, description="Whether to show color swatches"
    )
    swatch_size: int = Field(100, description="Swatch size in pixels")


class FormatsConfig(BaseModel):
    """Format configuration."""

    available: list[str] = Field(
        default_factory=lambda: ["hex", "rgb", "json"],
        description="Available copy formats",
    )
    default: str = Field("hex", description="Default format")


class ClipboardConfig(BaseModel):
    """Clipboard configuration."""

    method: str = Field(
        "wl-copy",
        description="Clipboard command (e.g., wl-copy, xclip -selection clipboard)",
    )
    auto_copy: bool = Field(
        True, description="Automatically copy on selection"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field("INFO", description="Logging level")


class AppConfig(BaseModel):
    """Application configuration."""

    paths: PathsConfig
    rofi: RofiConfig
    formats: FormatsConfig
    clipboard: ClipboardConfig
    logging: LoggingConfig


def load_config(config_file: Path | None = None) -> AppConfig:
    """Load configuration from settings.toml.

    Args:
        config_file: Optional path to settings.toml. If not provided,
                    uses default location in module's config directory.

    Returns:
        AppConfig object with loaded configuration

    Example:
        >>> config = load_config()
        >>> print(config.paths.colorscheme_file)
        PosixPath('/home/user/.cache/colorscheme/colors.json')
    """
    # Determine config file path
    if config_file is None:
        # Default to module's config directory
        module_dir = Path(__file__).parent.parent.parent.parent
        config_file = module_dir / "config" / "settings.toml"

    # Load with dynaconf
    settings = Dynaconf(
        settings_files=[str(config_file)],
        environments=False,
        load_dotenv=False,
    )

    # Convert to Pydantic models
    return AppConfig(
        paths=PathsConfig(
            colorscheme_file=Path(
                settings.paths.colorscheme_file
            ).expanduser(),
            temp_dir=Path(settings.paths.temp_dir).expanduser(),
        ),
        rofi=RofiConfig(
            show_icons=settings.rofi.show_icons,
            swatch_size=settings.rofi.swatch_size,
        ),
        formats=FormatsConfig(
            available=list(settings.formats.available),
            default=settings.formats.default,
        ),
        clipboard=ClipboardConfig(
            method=settings.clipboard.method,
            auto_copy=settings.clipboard.auto_copy,
        ),
        logging=LoggingConfig(
            level=settings.logging.level,
        ),
    )
