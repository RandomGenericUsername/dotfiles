"""Tests for configuration."""

import pytest
from pathlib import Path

from hyprpaper_manager.config.config import HyprpaperConfig, AppConfig


def test_hyprpaper_config_defaults():
    """Test HyprpaperConfig has correct defaults."""
    config = HyprpaperConfig()

    assert config.ipc_enabled is True
    assert config.splash_enabled is False
    assert config.auto_unload_unused is True
    assert config.preload_on_set is False
    assert len(config.wallpaper_dirs) > 0


def test_hyprpaper_config_custom():
    """Test HyprpaperConfig with custom values."""
    config = HyprpaperConfig(
        ipc_enabled=False,
        splash_enabled=True,
        wallpaper_dirs=[Path("/custom/path")],
    )

    assert config.ipc_enabled is False
    assert config.splash_enabled is True
    assert config.wallpaper_dirs == [Path("/custom/path")]


def test_app_config_defaults():
    """Test AppConfig has correct defaults."""
    config = AppConfig()

    assert config.hyprpaper is not None
    assert isinstance(config.hyprpaper, HyprpaperConfig)


def test_path_expansion():
    """Test that ~ is expanded in paths."""
    config = HyprpaperConfig(
        config_file="~/.config/hypr/hyprpaper.conf",
        wallpaper_dirs=["~/Pictures/wallpapers"],
    )

    assert "~" not in str(config.config_file)
    assert all("~" not in str(d) for d in config.wallpaper_dirs)
