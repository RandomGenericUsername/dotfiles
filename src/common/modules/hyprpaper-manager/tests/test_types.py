"""Tests for type definitions."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from hyprpaper_manager.core.types import (
    HyprpaperStatus,
    MonitorInfo,
    MonitorSelector,
    WallpaperInfo,
    WallpaperMode,
)


class TestWallpaperMode:
    def test_wallpaper_mode_values(self):
        """Test WallpaperMode enum values."""
        assert WallpaperMode.COVER.value == "cover"
        assert WallpaperMode.CONTAIN.value == "contain"
        assert WallpaperMode.TILE.value == "tile"

    def test_wallpaper_mode_from_string(self):
        """Test creating WallpaperMode from string."""
        assert WallpaperMode("cover") == WallpaperMode.COVER
        assert WallpaperMode("contain") == WallpaperMode.CONTAIN
        assert WallpaperMode("tile") == WallpaperMode.TILE


class TestMonitorSelector:
    def test_monitor_selector_values(self):
        """Test MonitorSelector enum values."""
        assert MonitorSelector.ALL.value == "all"
        assert MonitorSelector.FOCUSED.value == "focused"
        assert MonitorSelector.SPECIFIC.value == "specific"

    def test_monitor_selector_from_string(self):
        """Test creating MonitorSelector from string."""
        assert MonitorSelector("all") == MonitorSelector.ALL
        assert MonitorSelector("focused") == MonitorSelector.FOCUSED
        assert MonitorSelector("specific") == MonitorSelector.SPECIFIC


class TestWallpaperInfo:
    def test_wallpaper_info_defaults(self):
        """Test WallpaperInfo with defaults."""
        info = WallpaperInfo(path=Path("/test/wp.jpg"))

        assert info.path == Path("/test/wp.jpg")
        assert info.mode == WallpaperMode.COVER
        assert info.monitors == []
        assert info.is_loaded is False
        assert info.is_active is False

    def test_wallpaper_info_custom_values(self):
        """Test WallpaperInfo with custom values."""
        info = WallpaperInfo(
            path=Path("/test/wp.jpg"),
            mode=WallpaperMode.CONTAIN,
            monitors=["DP-1", "HDMI-1"],
            is_loaded=True,
            is_active=True,
        )

        assert info.path == Path("/test/wp.jpg")
        assert info.mode == WallpaperMode.CONTAIN
        assert info.monitors == ["DP-1", "HDMI-1"]
        assert info.is_loaded is True
        assert info.is_active is True

    def test_wallpaper_info_path_required(self):
        """Test WallpaperInfo requires path."""
        with pytest.raises(ValidationError):
            WallpaperInfo()

    def test_wallpaper_info_mode_validation(self):
        """Test WallpaperInfo validates mode."""
        # Valid mode
        info = WallpaperInfo(path=Path("/test/wp.jpg"), mode="cover")
        assert info.mode == WallpaperMode.COVER

        # Invalid mode should raise
        with pytest.raises(ValidationError):
            WallpaperInfo(path=Path("/test/wp.jpg"), mode="invalid")


class TestMonitorInfo:
    def test_monitor_info_defaults(self):
        """Test MonitorInfo with defaults."""
        info = MonitorInfo(name="DP-1")

        assert info.name == "DP-1"
        assert info.description is None
        assert info.focused is False
        assert info.current_wallpaper is None

    def test_monitor_info_custom_values(self):
        """Test MonitorInfo with custom values."""
        info = MonitorInfo(
            name="DP-1",
            description="Dell Monitor",
            focused=True,
            current_wallpaper=Path("/test/wp.jpg"),
        )

        assert info.name == "DP-1"
        assert info.description == "Dell Monitor"
        assert info.focused is True
        assert info.current_wallpaper == Path("/test/wp.jpg")

    def test_monitor_info_name_required(self):
        """Test MonitorInfo requires name."""
        with pytest.raises(ValidationError):
            MonitorInfo()


class TestHyprpaperStatus:
    def test_hyprpaper_status_empty(self):
        """Test HyprpaperStatus with empty lists."""
        status = HyprpaperStatus(
            loaded_wallpapers=[],
            active_wallpapers={},
            monitors=[],
        )

        assert status.loaded_wallpapers == []
        assert status.active_wallpapers == {}
        assert status.monitors == []

    def test_hyprpaper_status_with_data(self):
        """Test HyprpaperStatus with data."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")

        monitor1 = MonitorInfo(
            name="DP-1",
            focused=True,
            current_wallpaper=wp1,
        )
        monitor2 = MonitorInfo(
            name="HDMI-1",
            current_wallpaper=wp2,
        )

        status = HyprpaperStatus(
            loaded_wallpapers=[wp1, wp2],
            active_wallpapers={"DP-1": wp1, "HDMI-1": wp2},
            monitors=[monitor1, monitor2],
        )

        assert len(status.loaded_wallpapers) == 2
        assert wp1 in status.loaded_wallpapers
        assert wp2 in status.loaded_wallpapers
        assert status.active_wallpapers["DP-1"] == wp1
        assert status.active_wallpapers["HDMI-1"] == wp2
        assert len(status.monitors) == 2
        assert status.monitors[0].name == "DP-1"
        assert status.monitors[1].name == "HDMI-1"

    def test_hyprpaper_status_required_fields(self):
        """Test HyprpaperStatus requires all fields."""
        with pytest.raises(ValidationError):
            HyprpaperStatus()

        with pytest.raises(ValidationError):
            HyprpaperStatus(loaded_wallpapers=[])

        with pytest.raises(ValidationError):
            HyprpaperStatus(loaded_wallpapers=[], active_wallpapers={})
