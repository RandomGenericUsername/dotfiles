"""Tests for configuration module."""

from pathlib import Path

from dotfiles_manager.config import (
    AppConfig,
    ManagerConfig,
    get_default_config,
    get_manager_config,
)


def test_manager_config_defaults() -> None:
    """Test ManagerConfig default values."""
    config = ManagerConfig()
    assert (
        config.data_dir
        == Path.home() / ".local" / "share" / "dotfiles" / "manager"
    )
    assert config.debug is False


def test_manager_config_custom() -> None:
    """Test ManagerConfig with custom values."""
    custom_dir = Path("/tmp/test")
    config = ManagerConfig(data_dir=custom_dir, debug=True)
    assert config.data_dir == custom_dir
    assert config.debug is True


def test_app_config_defaults() -> None:
    """Test AppConfig default values."""
    config = AppConfig()
    assert config.manager is not None
    assert isinstance(config.manager, ManagerConfig)


def test_get_default_config() -> None:
    """Test get_default_config function."""
    config = get_default_config()
    assert isinstance(config, AppConfig)
    assert config.manager is not None


def test_get_manager_config() -> None:
    """Test get_manager_config function."""
    config = get_manager_config()
    assert isinstance(config, ManagerConfig)
