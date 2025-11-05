"""Tests for wallpaper operations."""

import pytest

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.core.exceptions import WallpaperNotFoundError
from hyprpaper_manager.wallpaper import WallpaperFinder


@pytest.fixture
def config(tmp_path):
    """Create test config."""
    return HyprpaperConfig(wallpaper_dirs=[tmp_path])


@pytest.fixture
def finder(config):
    """Create wallpaper finder."""
    return WallpaperFinder(config)


def test_find_wallpapers_empty(finder, tmp_path):
    """Test finding wallpapers in empty directory."""
    wallpapers = finder.find_wallpapers()
    assert wallpapers == []


def test_find_wallpapers(finder, tmp_path):
    """Test finding wallpapers."""
    # Create test files
    (tmp_path / "test1.png").touch()
    (tmp_path / "test2.jpg").touch()
    (tmp_path / "test3.jpeg").touch()
    (tmp_path / "test4.webp").touch()
    (tmp_path / "test.txt").touch()  # Should be ignored

    wallpapers = finder.find_wallpapers()

    assert len(wallpapers) == 4
    assert all(
        wp.suffix in [".png", ".jpg", ".jpeg", ".webp"] for wp in wallpapers
    )


def test_find_wallpaper_by_absolute_path(finder, tmp_path):
    """Test finding wallpaper by absolute path."""
    wallpaper = tmp_path / "test.png"
    wallpaper.touch()

    found = finder.find_wallpaper(str(wallpaper))
    assert found == wallpaper.resolve()


def test_find_wallpaper_by_relative_path(finder, tmp_path):
    """Test finding wallpaper by relative path from CWD."""
    import os

    # Create wallpaper in a subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    wallpaper = subdir / "test.png"
    wallpaper.touch()

    # Change to tmp_path and use relative path
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        found = finder.find_wallpaper("./subdir/test.png")
        assert found == wallpaper.resolve()
    finally:
        os.chdir(old_cwd)


def test_find_wallpaper_by_name(finder, tmp_path):
    """Test finding wallpaper by name in configured dirs."""
    wallpaper = tmp_path / "test.png"
    wallpaper.touch()

    found = finder.find_wallpaper("test.png")
    assert found == wallpaper.resolve()


def test_find_wallpaper_without_extension(finder, tmp_path):
    """Test finding wallpaper by name without extension."""
    wallpaper = tmp_path / "test.png"
    wallpaper.touch()

    found = finder.find_wallpaper("test")
    assert found == wallpaper.resolve()


def test_find_wallpaper_not_found(finder):
    """Test finding non-existent wallpaper."""
    with pytest.raises(WallpaperNotFoundError):
        finder.find_wallpaper("nonexistent.png")


def test_get_random_wallpaper(finder, tmp_path):
    """Test getting random wallpaper."""
    # Create test wallpapers
    (tmp_path / "test1.png").touch()
    (tmp_path / "test2.png").touch()
    (tmp_path / "test3.png").touch()

    wallpaper = finder.get_random_wallpaper()
    assert wallpaper.exists()
    assert wallpaper.suffix == ".png"


def test_get_random_wallpaper_with_exclude(finder, tmp_path):
    """Test getting random wallpaper with exclusion."""
    # Create test wallpapers
    wp1 = tmp_path / "test1.png"
    wp2 = tmp_path / "test2.png"
    wp1.touch()
    wp2.touch()

    # Get random excluding wp1
    wallpaper = finder.get_random_wallpaper(exclude=wp1)
    assert wallpaper == wp2.resolve()


def test_get_random_wallpaper_no_wallpapers(finder):
    """Test getting random wallpaper with no wallpapers."""
    with pytest.raises(WallpaperNotFoundError):
        finder.get_random_wallpaper()
