"""Tests for configuration manager."""

import pytest

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.config.manager import ConfigManager


@pytest.fixture
def config(tmp_path):
    """Create test config."""
    config_file = tmp_path / "hyprpaper.conf"
    return HyprpaperConfig(
        config_file=config_file,
        auto_create_config=True,
    )


@pytest.fixture
def manager(config):
    """Create config manager."""
    return ConfigManager(config)


def test_ensure_config_creates_file(manager, tmp_path):
    """Test that ensure_config_exists creates config file."""
    config_file = manager.config.config_file

    assert not config_file.exists()

    created = manager.ensure_config_exists()

    assert created is True
    assert config_file.exists()
    assert config_file.is_file()


def test_ensure_config_does_not_recreate(manager):
    """Test that ensure_config_exists doesn't recreate existing file."""
    # Create config first time
    created1 = manager.ensure_config_exists()
    assert created1 is True

    # Try to create again
    created2 = manager.ensure_config_exists()
    assert created2 is False


def test_ensure_config_respects_auto_create_setting(tmp_path):
    """Test that auto_create_config=False prevents creation."""
    config = HyprpaperConfig(
        config_file=tmp_path / "hyprpaper.conf",
        auto_create_config=False,
    )
    manager = ConfigManager(config)

    created = manager.ensure_config_exists()

    assert created is False
    assert not config.config_file.exists()


def test_generated_config_has_ipc_enabled(manager):
    """Test that generated config includes IPC setting."""
    manager.ensure_config_exists()

    content = manager.config.config_file.read_text()

    assert "ipc = on" in content


def test_generated_config_has_splash_when_enabled(tmp_path):
    """Test that generated config includes splash settings."""
    config = HyprpaperConfig(
        config_file=tmp_path / "hyprpaper.conf",
        splash_enabled=True,
        splash_offset=3.0,
        splash_color="aabbccdd",
    )
    manager = ConfigManager(config)

    manager.ensure_config_exists()
    content = config.config_file.read_text()

    assert "splash = true" in content
    assert "splash_offset = 3.0" in content
    assert "splash_color = aabbccdd" in content


def test_validate_config_success(manager):
    """Test config validation succeeds for valid config."""
    manager.ensure_config_exists()

    is_valid, error = manager.validate_config()

    assert is_valid is True
    assert error == ""


def test_validate_config_missing_file(manager):
    """Test config validation fails for missing file."""
    is_valid, error = manager.validate_config()

    assert is_valid is False
    assert "not found" in error.lower()


def test_validate_config_not_a_file(tmp_path):
    """Test config validation fails when path is a directory."""
    config_path = tmp_path / "hyprpaper.conf"
    config_path.mkdir()  # Create as directory

    config = HyprpaperConfig(config_file=config_path)
    manager = ConfigManager(config)

    is_valid, error = manager.validate_config()

    assert is_valid is False
    assert "not a file" in error.lower()
