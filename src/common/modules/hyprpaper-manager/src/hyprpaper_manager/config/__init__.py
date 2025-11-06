"""Configuration management for hyprpaper manager."""

from hyprpaper_manager.config.config import AppConfig, HyprpaperConfig
from hyprpaper_manager.config.manager import ConfigManager
from hyprpaper_manager.config.settings import get_default_config

__all__ = [
    "AppConfig",
    "HyprpaperConfig",
    "ConfigManager",
    "get_default_config",
]
