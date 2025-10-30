"""Settings loader using Dynaconf."""

from pathlib import Path
from typing import Any

from dynaconf import Dynaconf

from wallpaper_processor.config.config import AppConfig


def load_settings(
    settings_file: Path | None = None,
    user_config_dir: Path | None = None,
) -> AppConfig:
    """Load settings from TOML files using Dynaconf.

    Args:
        settings_file: Path to module settings.toml (defaults to package config)
        user_config_dir: Path to user config directory (defaults to ~/.config/wallpaper-processor)

    Returns:
        AppConfig instance with loaded settings
    """
    # Default settings file location
    if settings_file is None:
        # Get package root directory
        package_root = Path(__file__).parent.parent.parent.parent
        settings_file = package_root / "config" / "settings.toml"

    # Default user config directory
    if user_config_dir is None:
        user_config_dir = Path.home() / ".config" / "wallpaper-processor"

    # User presets file
    user_presets_file = user_config_dir / "presets.toml"

    # Build settings files list
    settings_files = [str(settings_file)]
    if user_presets_file.exists():
        settings_files.append(str(user_presets_file))

    # Load with Dynaconf
    settings = Dynaconf(
        settings_files=settings_files,
        merge_enabled=True,  # Merge user settings with defaults
        envvar_prefix="WALLPAPER_PROCESSOR",  # Environment variable prefix
    )

    # Convert to Pydantic model
    config_dict: dict[str, Any] = {
        "processing": settings.get("processing", {}),
        "backend": settings.get("backend", {}),
        "defaults": settings.get("defaults", {}),
        "presets": settings.get("presets", {}),
    }

    return AppConfig(**config_dict)


def get_default_config() -> AppConfig:
    """Get default configuration.

    Returns:
        AppConfig with default values
    """
    return load_settings()

