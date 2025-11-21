"""Configuration management for rofi-wallpaper-selector."""

from pathlib import Path

from dynaconf import Dynaconf
from pydantic import BaseModel


class PathsConfig(BaseModel):
    """Paths configuration."""

    wallpapers_dir: Path
    effects_cache_dir: Path
    dotfiles_manager_path: Path

    def model_post_init(self, __context) -> None:
        """Expand user paths after initialization."""
        self.wallpapers_dir = self.wallpapers_dir.expanduser()
        self.effects_cache_dir = self.effects_cache_dir.expanduser()
        self.dotfiles_manager_path = self.dotfiles_manager_path.expanduser()


class RofiConfig(BaseModel):
    """Rofi configuration."""

    wallpaper_mode_name: str
    effect_mode_name: str
    show_icons: bool
    icon_size: int


class WallpaperConfig(BaseModel):
    """Wallpaper configuration."""

    default_monitor: str
    auto_generate_colorscheme: bool
    auto_generate_effects: bool


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str
    format: str = "%(levelname)s - %(message)s"


class AppConfig(BaseModel):
    """Application configuration."""

    paths: PathsConfig
    rofi: RofiConfig
    wallpaper: WallpaperConfig
    logging: LoggingConfig


def load_config(config_path: Path | None = None) -> AppConfig:
    """
    Load configuration from TOML file.

    Args:
        config_path: Optional path to config file. If not provided, uses default.

    Returns:
        AppConfig: Loaded configuration
    """
    if config_path is None:
        # Default to config/settings.toml relative to this file
        config_path = (
            Path(__file__).parent.parent.parent.parent
            / "config"
            / "settings.toml"
        )

    settings = Dynaconf(
        settings_files=[str(config_path)],
        load_dotenv=False,
    )

    return AppConfig(
        paths=PathsConfig(
            wallpapers_dir=Path(settings.paths.wallpapers_dir),
            effects_cache_dir=Path(settings.paths.effects_cache_dir),
            dotfiles_manager_path=Path(settings.paths.dotfiles_manager_path),
        ),
        rofi=RofiConfig(
            wallpaper_mode_name=settings.rofi.wallpaper_mode_name,
            effect_mode_name=settings.rofi.effect_mode_name,
            show_icons=settings.rofi.show_icons,
            icon_size=settings.rofi.icon_size,
        ),
        wallpaper=WallpaperConfig(
            default_monitor=settings.wallpaper.default_monitor,
            auto_generate_colorscheme=settings.wallpaper.auto_generate_colorscheme,
            auto_generate_effects=settings.wallpaper.auto_generate_effects,
        ),
        logging=LoggingConfig(
            level=settings.logging.level,
            format=settings.logging.get(
                "format", "%(levelname)s - %(message)s"
            ),
        ),
    )
