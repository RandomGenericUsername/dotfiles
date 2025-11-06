"""Wallpaper pool management for memory control."""

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.core.exceptions import WallpaperTooLargeError


@dataclass
class PooledWallpaper:
    """Information about a preloaded wallpaper in the pool."""

    path: Path
    size_mb: float
    displayed: bool = False
    monitors: list[str] = None

    def __post_init__(self):
        """Initialize monitors list."""
        if self.monitors is None:
            self.monitors = []


class WallpaperPool:
    """Manage preloaded wallpapers pool with size limits."""

    def __init__(self, config: HyprpaperConfig):
        """Initialize wallpaper pool.

        Args:
            config: Hyprpaper configuration
        """
        self.config = config
        # Use OrderedDict for LRU tracking
        self._pool: OrderedDict[str, PooledWallpaper] = OrderedDict()

    def add(self, wallpaper: Path, size_mb: float) -> None:
        """Add wallpaper to pool.

        Args:
            wallpaper: Path to wallpaper
            size_mb: Size of wallpaper in MB

        Raises:
            WallpaperTooLargeError: If wallpaper exceeds size limits
        """
        # Check if wallpaper exceeds maximum allowed size
        max_allowed = (
            self.config.max_preload_pool_mb
            * self.config.max_wallpaper_size_multiplier
        )

        if size_mb > max_allowed:
            raise WallpaperTooLargeError(
                f"Wallpaper size ({size_mb:.1f}MB) exceeds maximum allowed "
                f"({max_allowed:.1f}MB = {self.config.max_preload_pool_mb}MB "
                f"* {self.config.max_wallpaper_size_multiplier})",
                wallpaper_size_mb=size_mb,
                max_allowed_mb=max_allowed,
            )

        wallpaper_str = str(wallpaper)

        # If already in pool, move to end (most recently used)
        if wallpaper_str in self._pool:
            self._pool.move_to_end(wallpaper_str)
            return

        # Add to pool
        self._pool[wallpaper_str] = PooledWallpaper(
            path=wallpaper, size_mb=size_mb
        )

    def remove(self, wallpaper: Path) -> bool:
        """Remove wallpaper from pool.

        Args:
            wallpaper: Path to wallpaper

        Returns:
            True if wallpaper was removed, False if not in pool
        """
        wallpaper_str = str(wallpaper)
        if wallpaper_str in self._pool:
            del self._pool[wallpaper_str]
            return True
        return False

    def contains(self, wallpaper: Path) -> bool:
        """Check if wallpaper is in pool.

        Args:
            wallpaper: Path to wallpaper

        Returns:
            True if wallpaper is in pool
        """
        return str(wallpaper) in self._pool

    def mark_displayed(
        self, wallpaper: Path, monitor: str, displayed: bool = True
    ) -> None:
        """Mark wallpaper as displayed on a monitor.

        Args:
            wallpaper: Path to wallpaper
            monitor: Monitor name
            displayed: Whether wallpaper is displayed
        """
        wallpaper_str = str(wallpaper)
        if wallpaper_str not in self._pool:
            return

        pooled = self._pool[wallpaper_str]

        if displayed:
            if monitor not in pooled.monitors:
                pooled.monitors.append(monitor)
            pooled.displayed = True
        else:
            if monitor in pooled.monitors:
                pooled.monitors.remove(monitor)
            pooled.displayed = len(pooled.monitors) > 0

        # Move to end (most recently used)
        self._pool.move_to_end(wallpaper_str)

    def get_total_size(self) -> float:
        """Get total size of all wallpapers in pool.

        Returns:
            Total size in MB
        """
        return sum(wp.size_mb for wp in self._pool.values())

    def is_over_limit(self) -> bool:
        """Check if pool exceeds size limit.

        Returns:
            True if pool size exceeds max_preload_pool_mb
        """
        return self.get_total_size() > self.config.max_preload_pool_mb

    def get_unused_wallpapers(self) -> list[Path]:
        """Get list of wallpapers not currently displayed.

        Returns:
            List of wallpaper paths not displayed on any monitor
        """
        return [wp.path for wp in self._pool.values() if not wp.displayed]

    def get_oldest_wallpapers(
        self, exclude_displayed: bool = True
    ) -> list[Path]:
        """Get wallpapers in LRU order (oldest first).

        Args:
            exclude_displayed: If True, exclude currently displayed wallpapers

        Returns:
            List of wallpaper paths in LRU order
        """
        wallpapers = []
        for wp in self._pool.values():
            if exclude_displayed and wp.displayed:
                continue
            wallpapers.append(wp.path)
        return wallpapers

    def cleanup(self) -> list[Path]:
        """Remove wallpapers to bring pool under size limit.

        Strategy:
        1. Remove unused wallpapers first (not displayed)
        2. If still over limit, remove oldest wallpapers (LRU)
        3. Never remove currently displayed wallpapers

        Returns:
            List of wallpaper paths that were removed
        """
        if not self.is_over_limit():
            return []

        removed = []

        # Phase 1: Remove unused wallpapers
        if self.config.auto_unload_unused:
            unused = self.get_unused_wallpapers()
            for wallpaper in unused:
                if not self.is_over_limit():
                    break
                self.remove(wallpaper)
                removed.append(wallpaper)

        # Phase 2: Remove oldest wallpapers (excluding displayed)
        if self.is_over_limit():
            oldest = self.get_oldest_wallpapers(exclude_displayed=True)
            for wallpaper in oldest:
                if not self.is_over_limit():
                    break
                self.remove(wallpaper)
                removed.append(wallpaper)

        return removed

    def clear(self) -> list[Path]:
        """Remove all wallpapers from pool.

        Returns:
            List of wallpaper paths that were removed
        """
        removed = list(self._pool.keys())
        self._pool.clear()
        return [Path(p) for p in removed]

    def get_status(self) -> dict[str, Any]:
        """Get pool status information.

        Returns:
            Dictionary with pool status
        """
        total_size = self.get_total_size()
        max_size = self.config.max_preload_pool_mb
        max_single = max_size * self.config.max_wallpaper_size_multiplier

        wallpapers = [
            {
                "path": str(wp.path),
                "size_mb": round(wp.size_mb, 2),
                "displayed": wp.displayed,
                "monitors": wp.monitors.copy(),
            }
            for wp in self._pool.values()
        ]

        return {
            "preloaded_wallpapers": wallpapers,
            "total_size_mb": round(total_size, 2),
            "max_size_mb": max_size,
            "usage_percent": (
                round((total_size / max_size * 100), 1) if max_size > 0 else 0
            ),
            "max_single_wallpaper_mb": round(max_single, 2),
            "is_over_limit": self.is_over_limit(),
        }
