"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def mock_wallpapers_dir(tmp_path):
    """Create a mock wallpapers directory with test wallpapers."""
    wallpapers_dir = tmp_path / "wallpapers"
    wallpapers_dir.mkdir()

    # Create test wallpapers
    (wallpapers_dir / "mountain.jpg").touch()
    (wallpapers_dir / "ocean.png").touch()
    (wallpapers_dir / "forest.jpeg").touch()

    return wallpapers_dir


@pytest.fixture
def mock_effects_cache_dir(tmp_path):
    """Create a mock effects cache directory with test effects."""
    cache_dir = tmp_path / "effects_cache"
    cache_dir.mkdir()

    # Create effects for mountain wallpaper
    mountain_cache = cache_dir / "mountain"
    mountain_cache.mkdir()
    (mountain_cache / "blur.png").touch()
    (mountain_cache / "grayscale.png").touch()

    return cache_dir


@pytest.fixture
def mock_manager_path(tmp_path):
    """Create a mock manager path with CLI."""
    manager_path = tmp_path / "manager"
    manager_path.mkdir()

    venv_bin = manager_path / ".venv" / "bin"
    venv_bin.mkdir(parents=True)
    (venv_bin / "dotfiles-manager").touch()

    return manager_path
