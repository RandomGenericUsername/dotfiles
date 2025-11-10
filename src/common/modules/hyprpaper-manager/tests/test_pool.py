"""Tests for wallpaper pool management."""

from pathlib import Path

import pytest

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.core.exceptions import WallpaperTooLargeError
from hyprpaper_manager.pool import PooledWallpaper, WallpaperPool


@pytest.fixture
def config():
    """Create test config."""
    return HyprpaperConfig(
        max_preload_pool_mb=100,
        max_wallpaper_size_multiplier=2.0,
        auto_unload_unused=True,
    )


@pytest.fixture
def pool(config):
    """Create wallpaper pool."""
    return WallpaperPool(config)


class TestPooledWallpaper:
    def test_pooled_wallpaper_creation(self):
        """Test PooledWallpaper creation."""
        wp = PooledWallpaper(path=Path("/test/wp.jpg"), size_mb=10.5)
        assert wp.path == Path("/test/wp.jpg")
        assert wp.size_mb == 10.5
        assert wp.displayed is False
        assert wp.monitors == []

    def test_pooled_wallpaper_with_monitors(self):
        """Test PooledWallpaper with monitors."""
        wp = PooledWallpaper(
            path=Path("/test/wp.jpg"),
            size_mb=10.5,
            displayed=True,
            monitors=["DP-1", "HDMI-1"],
        )
        assert wp.displayed is True
        assert wp.monitors == ["DP-1", "HDMI-1"]


class TestWallpaperPool:
    def test_pool_initialization(self, pool, config):
        """Test pool initialization."""
        assert pool.config == config
        assert pool.get_total_size() == 0
        assert not pool.is_over_limit()

    def test_add_wallpaper(self, pool):
        """Test adding wallpaper to pool."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)

        assert pool.contains(wp)
        assert pool.get_total_size() == 10.0

    def test_add_duplicate_wallpaper(self, pool):
        """Test adding same wallpaper twice moves it to end."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)
        pool.add(Path("/test/wp2.jpg"), 15.0)
        pool.add(wp, 10.0)  # Add again

        # Should still have 2 wallpapers, not 3
        assert pool.get_total_size() == 25.0

    def test_add_wallpaper_too_large(self, pool):
        """Test adding wallpaper that exceeds size limit."""
        # Max allowed = 100 * 2.0 = 200MB
        wp = Path("/test/huge.jpg")

        with pytest.raises(WallpaperTooLargeError) as exc_info:
            pool.add(wp, 250.0)

        assert "250.0MB" in str(exc_info.value)
        assert "200.0MB" in str(exc_info.value)
        assert exc_info.value.wallpaper_size_mb == 250.0
        assert exc_info.value.max_allowed_mb == 200.0

    def test_remove_wallpaper(self, pool):
        """Test removing wallpaper from pool."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)

        removed = pool.remove(wp)

        assert removed is True
        assert not pool.contains(wp)
        assert pool.get_total_size() == 0

    def test_remove_nonexistent_wallpaper(self, pool):
        """Test removing wallpaper not in pool."""
        wp = Path("/test/nonexistent.jpg")
        removed = pool.remove(wp)

        assert removed is False

    def test_contains(self, pool):
        """Test checking if wallpaper is in pool."""
        wp = Path("/test/wp1.jpg")
        assert not pool.contains(wp)

        pool.add(wp, 10.0)
        assert pool.contains(wp)

    def test_mark_displayed(self, pool):
        """Test marking wallpaper as displayed."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)

        pool.mark_displayed(wp, "DP-1")

        status = pool.get_status()
        assert status["preloaded_wallpapers"][0]["displayed"] is True
        assert "DP-1" in status["preloaded_wallpapers"][0]["monitors"]

    def test_mark_displayed_multiple_monitors(self, pool):
        """Test marking wallpaper as displayed on multiple monitors."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)

        pool.mark_displayed(wp, "DP-1")
        pool.mark_displayed(wp, "HDMI-1")

        status = pool.get_status()
        assert status["preloaded_wallpapers"][0]["displayed"] is True
        assert "DP-1" in status["preloaded_wallpapers"][0]["monitors"]
        assert "HDMI-1" in status["preloaded_wallpapers"][0]["monitors"]

    def test_mark_not_displayed(self, pool):
        """Test marking wallpaper as not displayed."""
        wp = Path("/test/wp1.jpg")
        pool.add(wp, 10.0)
        pool.mark_displayed(wp, "DP-1")

        pool.mark_displayed(wp, "DP-1", displayed=False)

        status = pool.get_status()
        assert status["preloaded_wallpapers"][0]["displayed"] is False
        assert "DP-1" not in status["preloaded_wallpapers"][0]["monitors"]

    def test_mark_displayed_nonexistent_wallpaper(self, pool):
        """Test marking nonexistent wallpaper as displayed does nothing."""
        wp = Path("/test/nonexistent.jpg")
        pool.mark_displayed(wp, "DP-1")  # Should not raise

    def test_get_total_size(self, pool):
        """Test getting total pool size."""
        pool.add(Path("/test/wp1.jpg"), 10.0)
        pool.add(Path("/test/wp2.jpg"), 15.5)
        pool.add(Path("/test/wp3.jpg"), 20.25)

        assert pool.get_total_size() == 45.75

    def test_is_over_limit(self, pool):
        """Test checking if pool is over limit."""
        assert not pool.is_over_limit()

        # Add wallpapers up to 110MB (over 100MB limit)
        pool.add(Path("/test/wp1.jpg"), 60.0)
        pool.add(Path("/test/wp2.jpg"), 55.0)

        assert pool.is_over_limit()

    def test_get_unused_wallpapers(self, pool):
        """Test getting unused wallpapers."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")
        wp3 = Path("/test/wp3.jpg")

        pool.add(wp1, 10.0)
        pool.add(wp2, 15.0)
        pool.add(wp3, 20.0)

        pool.mark_displayed(wp1, "DP-1")

        unused = pool.get_unused_wallpapers()

        assert len(unused) == 2
        assert wp2 in unused
        assert wp3 in unused
        assert wp1 not in unused

    def test_get_oldest_wallpapers(self, pool):
        """Test getting oldest wallpapers in LRU order."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")
        wp3 = Path("/test/wp3.jpg")

        pool.add(wp1, 10.0)
        pool.add(wp2, 15.0)
        pool.add(wp3, 20.0)

        oldest = pool.get_oldest_wallpapers(exclude_displayed=False)

        assert oldest == [wp1, wp2, wp3]

    def test_get_oldest_wallpapers_exclude_displayed(self, pool):
        """Test getting oldest wallpapers excluding displayed."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")
        wp3 = Path("/test/wp3.jpg")

        pool.add(wp1, 10.0)
        pool.add(wp2, 15.0)
        pool.add(wp3, 20.0)

        pool.mark_displayed(wp2, "DP-1")

        oldest = pool.get_oldest_wallpapers(exclude_displayed=True)

        assert len(oldest) == 2
        assert wp1 in oldest
        assert wp3 in oldest
        assert wp2 not in oldest

    def test_cleanup_under_limit(self, pool):
        """Test cleanup when pool is under limit."""
        pool.add(Path("/test/wp1.jpg"), 10.0)
        pool.add(Path("/test/wp2.jpg"), 15.0)

        removed = pool.cleanup()

        assert removed == []
        assert pool.get_total_size() == 25.0

    def test_cleanup_removes_unused_first(self, pool):
        """Test cleanup removes unused wallpapers first."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")
        wp3 = Path("/test/wp3.jpg")

        pool.add(wp1, 60.0)
        pool.add(wp2, 30.0)
        pool.add(wp3, 25.0)  # Total: 115MB (over 100MB limit)

        pool.mark_displayed(wp1, "DP-1")

        removed = pool.cleanup()

        # Should remove unused wallpapers (wp2, wp3) until under limit
        assert len(removed) >= 1
        assert wp1 not in removed  # Displayed wallpaper should not be removed
        assert not pool.is_over_limit()

    def test_cleanup_with_auto_unload_disabled(self):
        """Test cleanup with auto_unload_unused disabled."""
        config = HyprpaperConfig(
            max_preload_pool_mb=100,
            max_wallpaper_size_multiplier=2.0,
            auto_unload_unused=False,
        )
        pool = WallpaperPool(config)

        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")

        pool.add(wp1, 60.0)
        pool.add(wp2, 50.0)  # Total: 110MB (over limit)

        removed = pool.cleanup()

        # Should remove oldest (wp1) since auto_unload_unused is False
        assert len(removed) >= 1

    def test_clear(self, pool):
        """Test clearing entire pool."""
        pool.add(Path("/test/wp1.jpg"), 10.0)
        pool.add(Path("/test/wp2.jpg"), 15.0)
        pool.add(Path("/test/wp3.jpg"), 20.0)

        removed = pool.clear()

        assert len(removed) == 3
        assert pool.get_total_size() == 0
        assert not pool.contains(Path("/test/wp1.jpg"))

    def test_get_status(self, pool):
        """Test getting pool status."""
        wp1 = Path("/test/wp1.jpg")
        wp2 = Path("/test/wp2.jpg")

        pool.add(wp1, 30.0)
        pool.add(wp2, 20.0)
        pool.mark_displayed(wp1, "DP-1")

        status = pool.get_status()

        assert status["total_size_mb"] == 50.0
        assert status["max_size_mb"] == 100
        assert status["usage_percent"] == 50.0
        assert status["max_single_wallpaper_mb"] == 200.0
        assert status["is_over_limit"] is False
        assert len(status["preloaded_wallpapers"]) == 2

    def test_get_status_over_limit(self, pool):
        """Test getting pool status when over limit."""
        pool.add(Path("/test/wp1.jpg"), 60.0)
        pool.add(Path("/test/wp2.jpg"), 55.0)

        status = pool.get_status()

        assert status["is_over_limit"] is True
        assert status["usage_percent"] == 115.0

