"""Tests for configuration."""

from pathlib import Path

from hyprpaper_manager.config.config import AppConfig, HyprpaperConfig


def test_hyprpaper_config_defaults():
    """Test HyprpaperConfig has correct defaults."""
    config = HyprpaperConfig()

    assert config.ipc_enabled is True
    assert config.splash_enabled is False
    assert config.auto_unload_unused is True
    assert config.auto_create_config is True
    assert config.autostart is True
    assert len(config.wallpaper_dirs) > 0
    assert config.ipc_timeout == 5
    assert config.ipc_retry_attempts == 3
    assert config.max_preload_pool_mb == 100


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
