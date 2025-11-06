"""Settings loader using dynaconf."""

from pathlib import Path

from dynaconf import Dynaconf

from hyprpaper_manager.config.config import AppConfig
from hyprpaper_manager.config.defaults import HYPRPAPER_DEFAULTS


def _get_settings_files() -> list[str]:
    """Get list of settings files to load.

    Priority (highest to lowest):
    1. User config: ~/.config/hyprpaper-manager/settings.toml
    2. Local config: ./config/settings.toml
    """
    files = []

    # Local config
    local_config = Path("config/settings.toml")
    if local_config.exists():
        files.append(str(local_config))

    # User config
    user_config = Path.home() / ".config/hyprpaper-manager/settings.toml"
    if user_config.exists():
        files.append(str(user_config))

    return files


def get_default_config() -> AppConfig:
    """Get default configuration.

    Returns:
        AppConfig with default values
    """
    settings_files = _get_settings_files()

    if settings_files:
        # Load from files
        dynaconf_settings = Dynaconf(
            settings_files=settings_files,
            merge_enabled=True,
        )
        config_dict = dynaconf_settings.to_dict()
    else:
        # Use defaults
        config_dict = {"hyprpaper": HYPRPAPER_DEFAULTS}

    return AppConfig(**config_dict)
