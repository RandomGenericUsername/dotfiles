"""Tests for effects cache utility."""

import pytest
from pathlib import Path
from rofi_wallpaper_selector.utils.effects_cache import get_available_effects


class TestGetAvailableEffects:
    """Test effects cache querying."""

    def test_get_effects_when_cache_exists(self, tmp_path):
        """Test getting effects when cache directory exists with effects."""
        # Create cache structure
        wallpaper_cache = tmp_path / "mountain"
        wallpaper_cache.mkdir()
        (wallpaper_cache / "blur.png").touch()
        (wallpaper_cache / "grayscale.png").touch()
        (wallpaper_cache / "pixelate.png").touch()

        effects = get_available_effects("mountain", tmp_path)

        assert len(effects) == 3
        assert "blur" in effects
        assert "grayscale" in effects
        assert "pixelate" in effects
        assert effects == sorted(effects)  # Should be sorted

    def test_get_effects_when_cache_empty(self, tmp_path):
        """Test getting effects when cache directory is empty."""
        wallpaper_cache = tmp_path / "mountain"
        wallpaper_cache.mkdir()

        effects = get_available_effects("mountain", tmp_path)

        assert effects == []

    def test_get_effects_when_cache_not_exists(self, tmp_path):
        """Test getting effects when cache directory doesn't exist."""
        effects = get_available_effects("nonexistent", tmp_path)

        assert effects == []

    def test_get_effects_ignores_non_png_files(self, tmp_path):
        """Test that non-PNG files are ignored."""
        wallpaper_cache = tmp_path / "mountain"
        wallpaper_cache.mkdir()
        (wallpaper_cache / "blur.png").touch()
        (wallpaper_cache / "readme.txt").touch()
        (wallpaper_cache / "config.json").touch()

        effects = get_available_effects("mountain", tmp_path)

        assert len(effects) == 1
        assert effects == ["blur"]
