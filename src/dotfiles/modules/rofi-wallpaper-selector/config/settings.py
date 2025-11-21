"""Configuration models for rofi-wallpaper-selector."""

from pathlib import Path
from typing import Literal

from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class PathsConfig(BaseModel):
    """Paths configuration."""

    wallpapers_dir: Path = Field(description="Directory containing wallpapers")
    effects_cache_dir: Path = Field(
        description="Directory containing wallpaper effects cache"
    )
    dotfiles_manager_path: Path = Field(
        description="Path to dotfiles-manager module"
    )

    def model_post_init(self, __context):
        """Expand user paths after initialization."""
        self.wallpapers_dir = self.wallpapers_dir.expanduser()
        self.effects_cache_dir = self.effects_cache_dir.expanduser()
        self.dotfiles_manager_path = self.dotfiles_manager_path.expanduser()


class RofiConfig(BaseModel):
    """Rofi display configuration."""

    show_icons: bool = Field(default=True, description="Show icons in rofi")
    icon_size: int = Field(default=100, description="Icon size in pixels")
    wallpaper_mode_name: str = Field(
        default="wallpapers", description="Wallpaper mode name"
    )
    effect_mode_name: str = Field(
        default="effects", description="Effect mode name"
    )


class WallpaperConfig(BaseModel):
    """Wallpaper configuration."""

    default_monitor: str = Field(default="focused", description="Default monitor")
    auto_generate_effects: bool = Field(
        default=True, description="Auto-generate effects on wallpaper selection"
    )
    auto_generate_colorscheme: bool = Field(
        default=True, description="Auto-generate colorscheme on wallpaper change"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="Logging level"
    )


class AppConfig(BaseModel):
    """Application configuration."""

    paths: PathsConfig
    rofi: RofiConfig = Field(default_factory=RofiConfig)
    wallpaper: WallpaperConfig = Field(default_factory=WallpaperConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


def load_config(config_file: Path | None = None) -> AppConfig:
    """Load configuration from TOML file.

    Args:
        config_file: Path to settings.toml file. If None, uses default location.

    Returns:
        Validated AppConfig instance
    """
    if config_file is None:
        config_file = Path(__file__).parent / "settings.toml"

    settings = Dynaconf(
        settings_files=[str(config_file)],
        load_dotenv=False,
    )

    return AppConfig(
        paths=PathsConfig(**settings.paths),
        rofi=RofiConfig(**settings.rofi),
        wallpaper=WallpaperConfig(**settings.wallpaper),
        logging=LoggingConfig(**settings.logging),
    )
