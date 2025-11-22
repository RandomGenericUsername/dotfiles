"""Main hyprpaper manager."""

import logging
from pathlib import Path
from typing import Any

from hyprpaper_manager.config.config import HyprpaperConfig
from hyprpaper_manager.config.settings import get_default_config
from hyprpaper_manager.core.exceptions import WallpaperNotFoundError
from hyprpaper_manager.core.types import (
    HyprpaperStatus,
    MonitorInfo,
    MonitorSelector,
    WallpaperMode,
)
from hyprpaper_manager.ipc.client import HyprpaperIPC
from hyprpaper_manager.monitor import MonitorManager
from hyprpaper_manager.wallpaper import WallpaperFinder

logger = logging.getLogger(__name__)


class HyprpaperManager:
    """High-level hyprpaper manager."""

    def __init__(self, config: HyprpaperConfig | None = None):
        """Initialize manager.

        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or get_default_config().hyprpaper

        logger.debug(
            f"Initializing HyprpaperManager with config: {self.config}"
        )

        # Ensure config file exists if auto_create_config is enabled
        from hyprpaper_manager.config.manager import ConfigManager

        config_mgr = ConfigManager(self.config)
        config_mgr.ensure_config_exists()

        # Initialize components
        from hyprpaper_manager.pool import WallpaperPool

        self.ipc = HyprpaperIPC(
            timeout=self.config.ipc_timeout,
            retry_attempts=self.config.ipc_retry_attempts,
            retry_delay=self.config.ipc_retry_delay,
            startup_wait=self.config.ipc_startup_wait,
            autostart=self.config.autostart,
        )
        self.monitors = MonitorManager()
        self.wallpapers = WallpaperFinder(self.config)
        self.pool = WallpaperPool(self.config)

        logger.info("HyprpaperManager initialized successfully")

    # Helper methods

    def _get_wallpaper_size_mb(self, wallpaper: Path) -> float:
        """Get wallpaper file size in MB.

        Args:
            wallpaper: Path to wallpaper

        Returns:
            Size in MB
        """
        size_bytes = wallpaper.stat().st_size
        return size_bytes / (1024 * 1024)

    # Status methods

    def is_running(self) -> bool:
        """Check if hyprpaper is running.

        Returns:
            True if hyprpaper is running
        """
        return self.ipc.is_running()

    def get_status(self) -> HyprpaperStatus:
        """Get current hyprpaper status.

        Returns:
            Current status including loaded/active wallpapers and monitors
        """
        loaded = self.ipc.listloaded()
        active = self.ipc.listactive()
        monitors = self.monitors.get_monitors()

        # Update monitor wallpapers
        for monitor in monitors:
            monitor.current_wallpaper = active.get(monitor.name)

        return HyprpaperStatus(
            loaded_wallpapers=loaded,
            active_wallpapers=active,
            monitors=monitors,
        )

    # Wallpaper operations

    def set(
        self,
        wallpaper: Path | str,
        monitor: str | MonitorSelector = MonitorSelector.ALL,
        mode: WallpaperMode = WallpaperMode.COVER,
    ) -> None:
        """Set wallpaper for monitor(s).

        Smart method that auto-preloads wallpaper if needed, then sets it.
        Manages pool size automatically.

        Args:
            wallpaper: Wallpaper path or name
            monitor: Monitor name, "all", or "focused"
            mode: Display mode (cover, contain, tile)

        Raises:
            WallpaperNotFoundError: If wallpaper not found
            WallpaperTooLargeError: If wallpaper exceeds size limits
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        logger.info(
            f"Setting wallpaper: {wallpaper} on monitor={monitor}, mode={mode}"
        )

        # Resolve wallpaper path
        if isinstance(wallpaper, str):
            wallpaper_path = self.wallpapers.find_wallpaper(wallpaper)
            logger.debug(f"Resolved wallpaper path: {wallpaper_path}")
        else:
            wallpaper_path = wallpaper

        if not wallpaper_path.exists():
            logger.error(f"Wallpaper not found: {wallpaper_path}")
            raise WallpaperNotFoundError(
                f"Wallpaper not found: {wallpaper_path}"
            )

        # Get wallpaper size and validate
        size_mb = self._get_wallpaper_size_mb(wallpaper_path)
        logger.debug(f"Wallpaper size: {size_mb:.2f}MB")

        # Validate size limits before preloading
        self.pool.add(wallpaper_path, size_mb)

        # Preload if not already loaded in hyprpaper
        loaded_wallpapers = self.ipc.listloaded()
        if wallpaper_path not in loaded_wallpapers:
            logger.debug(f"Preloading wallpaper: {wallpaper_path}")
            self.ipc.preload(wallpaper_path)
        else:
            logger.debug(f"Wallpaper already loaded: {wallpaper_path}")

        # Resolve monitor(s)
        if monitor == MonitorSelector.ALL:
            # Get all actual monitors and set wallpaper on each
            all_monitors = self.monitors.get_monitors()
            if not all_monitors:
                # Fallback: use empty string for "all monitors"
                monitor_names = [""]
                logger.warning(
                    "No monitors detected, using empty monitor name"
                )
            else:
                monitor_names = [m.name for m in all_monitors]
                logger.debug(
                    f"Setting wallpaper on all monitors: {monitor_names}"
                )
        elif monitor == MonitorSelector.FOCUSED:
            monitor_name = self.monitors.get_focused_monitor().name
            logger.debug(f"Resolved focused monitor: {monitor_name}")
            monitor_names = [monitor_name]
        else:
            monitor_names = [monitor]

        # Set wallpaper on all resolved monitors
        mode_str = mode.value if mode != WallpaperMode.COVER else None
        for monitor_name in monitor_names:
            logger.debug(
                f"Setting wallpaper on monitor '{monitor_name}' "
                f"with mode={mode_str}"
            )
            self.ipc.wallpaper(monitor_name, wallpaper_path, mode_str)

            # Mark as displayed in pool
            self.pool.mark_displayed(wallpaper_path, monitor_name or "all")

        # Cleanup pool if over limit
        removed = self.pool.cleanup()
        if removed:
            logger.info(f"Cleaned up {len(removed)} wallpapers from pool")
            for wp in removed:
                logger.debug(f"Unloading: {wp}")
                self.ipc.unload(wp)

        logger.info(f"Successfully set wallpaper: {wallpaper_path.name}")

    # Alias for backwards compatibility
    def set_wallpaper(
        self,
        wallpaper: Path | str,
        monitor: str | MonitorSelector = MonitorSelector.ALL,
        mode: WallpaperMode = WallpaperMode.COVER,
    ) -> None:
        """Set wallpaper for monitor(s). Alias for set().

        Args:
            wallpaper: Wallpaper path or name
            monitor: Monitor name, "all", or "focused"
            mode: Display mode (cover, contain, tile)
        """
        self.set(wallpaper, monitor, mode)

    def set_random_wallpaper(
        self,
        monitor: str | MonitorSelector = MonitorSelector.ALL,
        mode: WallpaperMode = WallpaperMode.COVER,
    ) -> Path:
        """Set random wallpaper.

        Args:
            monitor: Monitor name, "all", or "focused"
            mode: Display mode (cover, contain, tile)

        Returns:
            Path to selected wallpaper

        Raises:
            WallpaperNotFoundError: If no wallpapers found
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        # Get current wallpaper to exclude
        current = None
        try:
            status = self.get_status()
            if status.loaded_wallpapers:
                current = status.loaded_wallpapers[0]
        except Exception:
            pass

        wallpaper = self.wallpapers.get_random_wallpaper(exclude=current)
        self.set_wallpaper(wallpaper, monitor, mode)
        return wallpaper

    def preload(self, wallpaper: Path | str) -> None:
        """Preload wallpaper into memory (explicit preload for pool).

        Args:
            wallpaper: Wallpaper path or name

        Raises:
            WallpaperNotFoundError: If wallpaper not found
            WallpaperTooLargeError: If wallpaper exceeds size limits
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        # Resolve wallpaper path
        if isinstance(wallpaper, str):
            wallpaper_path = self.wallpapers.find_wallpaper(wallpaper)
        else:
            wallpaper_path = wallpaper

        if not wallpaper_path.exists():
            raise WallpaperNotFoundError(
                f"Wallpaper not found: {wallpaper_path}"
            )

        # Get size and add to pool
        size_mb = self._get_wallpaper_size_mb(wallpaper_path)
        self.pool.add(wallpaper_path, size_mb)

        # Preload via IPC
        self.ipc.preload(wallpaper_path)

        # Cleanup pool if needed
        removed = self.pool.cleanup()
        for wp in removed:
            self.ipc.unload(wp)

    # Alias for backwards compatibility
    def preload_wallpaper(self, wallpaper: Path | str) -> None:
        """Preload wallpaper into memory. Alias for preload().

        Args:
            wallpaper: Wallpaper path or name
        """
        self.preload(wallpaper)

    def unload(self, wallpaper: Path | str) -> None:
        """Unload wallpaper from memory.

        Args:
            wallpaper: Wallpaper path or name

        Raises:
            WallpaperNotFoundError: If wallpaper not found
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        # Resolve wallpaper path
        if isinstance(wallpaper, str):
            wallpaper_path = self.wallpapers.find_wallpaper(wallpaper)
        else:
            wallpaper_path = wallpaper

        # Remove from pool
        self.pool.remove(wallpaper_path)

        # Unload via IPC
        self.ipc.unload(wallpaper_path)

    # Alias for backwards compatibility
    def unload_wallpaper(self, wallpaper: Path | str) -> None:
        """Unload wallpaper from memory. Alias for unload().

        Args:
            wallpaper: Wallpaper path or name
        """
        self.unload(wallpaper)

    def unload_unused(self) -> list[Path]:
        """Unload wallpapers not currently displayed.

        Returns:
            List of wallpaper paths that were unloaded

        Raises:
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        unused = self.pool.get_unused_wallpapers()
        for wp in unused:
            self.ipc.unload(wp)
            self.pool.remove(wp)
        return unused

    def unload_all(self) -> list[Path]:
        """Unload all wallpapers from memory.

        Returns:
            List of wallpaper paths that were unloaded

        Raises:
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        all_wallpapers = self.pool.clear()
        for wp in all_wallpapers:
            self.ipc.unload(wp)
        return all_wallpapers

    # Batch operations

    def preload_batch(self, wallpapers: list[Path | str]) -> None:
        """Preload multiple wallpapers.

        Args:
            wallpapers: List of wallpaper paths or names

        Raises:
            WallpaperNotFoundError: If any wallpaper not found
            WallpaperTooLargeError: If any wallpaper exceeds size limits
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        for wallpaper in wallpapers:
            self.preload(wallpaper)

    def unload_batch(self, wallpapers: list[Path | str]) -> None:
        """Unload multiple wallpapers.

        Args:
            wallpapers: List of wallpaper paths or names

        Raises:
            WallpaperNotFoundError: If any wallpaper not found
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        for wallpaper in wallpapers:
            self.unload(wallpaper)

    # Pool management

    def get_pool_status(self) -> dict[str, Any]:
        """Get wallpaper pool status.

        Returns:
            Dictionary with pool information including:
            - preloaded_wallpapers: List of preloaded wallpapers with details
            - total_size_mb: Total size of pool in MB
            - max_size_mb: Maximum pool size in MB
            - usage_percent: Pool usage percentage
            - max_single_wallpaper_mb: Maximum allowed single wallpaper size
            - is_over_limit: Whether pool exceeds size limit
        """
        return self.pool.get_status()

    # Monitor operations

    def get_monitors(self) -> list[MonitorInfo]:
        """Get all monitors.

        Returns:
            List of monitor information
        """
        return self.monitors.get_monitors()

    def get_focused_monitor(self) -> MonitorInfo:
        """Get focused monitor.

        Returns:
            Focused monitor information

        Raises:
            MonitorNotFoundError: If no focused monitor found
        """
        return self.monitors.get_focused_monitor()

    # Wallpaper discovery

    def list_wallpapers(self) -> list[Path]:
        """List available wallpapers.

        Returns:
            List of wallpaper paths
        """
        return self.wallpapers.find_wallpapers()

    def find_wallpaper(self, name: str) -> Path:
        """Find wallpaper by name.

        Args:
            name: Wallpaper name or path

        Returns:
            Resolved wallpaper path

        Raises:
            WallpaperNotFoundError: If wallpaper not found
        """
        return self.wallpapers.find_wallpaper(name)
