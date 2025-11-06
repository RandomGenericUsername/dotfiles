"""Tests for HyprpaperManager."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from hyprpaper_manager import HyprpaperManager
from hyprpaper_manager.core.exceptions import (
    WallpaperNotFoundError,
)


@pytest.fixture
def mock_config():
    """Mock configuration."""
    from hyprpaper_manager.config.config import HyprpaperConfig

    return HyprpaperConfig(
        wallpaper_dirs=[Path("/tmp/wallpapers")],
        auto_unload_unused=True,
        preload_on_set=False,
    )


@pytest.fixture
def manager(mock_config):
    """Create manager with mock config."""
    return HyprpaperManager(config=mock_config)


def test_manager_initialization(manager):
    """Test manager initializes correctly."""
    assert manager.config is not None
    assert manager.ipc is not None
    assert manager.monitors is not None
    assert manager.wallpapers is not None


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_is_running_true(mock_run, manager):
    """Test is_running returns True when hyprpaper is running."""
    mock_run.return_value = Mock(returncode=0)
    assert manager.is_running() is True


@patch("hyprpaper_manager.ipc.client.subprocess.run")
def test_is_running_false(mock_run, manager):
    """Test is_running returns False when hyprpaper is not running."""
    mock_run.return_value = Mock(returncode=1)
    assert manager.is_running() is False


def test_list_wallpapers_empty(manager, tmp_path):
    """Test list_wallpapers with no wallpapers."""
    manager.config.wallpaper_dirs = [tmp_path]
    wallpapers = manager.list_wallpapers()
    assert wallpapers == []


def test_list_wallpapers(manager, tmp_path):
    """Test list_wallpapers finds wallpapers."""
    # Create test wallpapers
    (tmp_path / "test1.png").touch()
    (tmp_path / "test2.jpg").touch()
    (tmp_path / "test.txt").touch()  # Should be ignored

    manager.config.wallpaper_dirs = [tmp_path]
    wallpapers = manager.list_wallpapers()

    assert len(wallpapers) == 2
    assert all(wp.suffix in [".png", ".jpg"] for wp in wallpapers)


def test_find_wallpaper_by_path(manager, tmp_path):
    """Test find_wallpaper with full path."""
    wallpaper = tmp_path / "test.png"
    wallpaper.touch()

    found = manager.find_wallpaper(str(wallpaper))
    assert found == wallpaper.resolve()


def test_find_wallpaper_by_name(manager, tmp_path):
    """Test find_wallpaper by name."""
    wallpaper = tmp_path / "test.png"
    wallpaper.touch()

    manager.config.wallpaper_dirs = [tmp_path]
    found = manager.find_wallpaper("test.png")
    assert found == wallpaper.resolve()


def test_find_wallpaper_not_found(manager):
    """Test find_wallpaper raises when not found."""
    with pytest.raises(WallpaperNotFoundError):
        manager.find_wallpaper("nonexistent.png")
