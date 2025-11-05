"""Main hyprpaper manager."""

from pathlib import Path
from typing import Literal

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


class HyprpaperManager:
    """High-level hyprpaper manager."""

    def __init__(self, config: HyprpaperConfig | None = None):
        """Initialize manager.

        Args:
            config: Configuration (uses defaults if None)
        """
        self.config = config or get_default_config().hyprpaper
        self.ipc = HyprpaperIPC()
        self.monitors = MonitorManager()
        self.wallpapers = WallpaperFinder(self.config)

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

    def set_wallpaper(
        self,
        wallpaper: Path | str,
        monitor: str | MonitorSelector = MonitorSelector.ALL,
        mode: WallpaperMode = WallpaperMode.COVER,
    ) -> None:
        """Set wallpaper for monitor(s).

        Args:
            wallpaper: Wallpaper path or name
            monitor: Monitor name, "all", or "focused"
            mode: Display mode (cover, contain, tile)

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

        if not wallpaper_path.exists():
            raise WallpaperNotFoundError(
                f"Wallpaper not found: {wallpaper_path}"
            )

        # Resolve monitor(s)
        if monitor == MonitorSelector.ALL:
            monitor_name = ""
        elif monitor == MonitorSelector.FOCUSED:
            monitor_name = self.monitors.get_focused_monitor().name
        else:
            monitor_name = monitor

        # Set wallpaper
        mode_str = mode.value if mode != WallpaperMode.COVER else None

        if self.config.preload_on_set:
            # Traditional: preload then set
            self.ipc.preload(wallpaper_path)
            self.ipc.wallpaper(monitor_name, wallpaper_path, mode_str)
        else:
            # Fast: use reload
            self.ipc.reload(monitor_name, wallpaper_path, mode_str)

        # Auto cleanup
        if self.config.auto_unload_unused:
            self.ipc.unload("unused")

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

    def preload_wallpaper(self, wallpaper: Path | str) -> None:
        """Preload wallpaper into memory.

        Args:
            wallpaper: Wallpaper path or name

        Raises:
            WallpaperNotFoundError: If wallpaper not found
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        if isinstance(wallpaper, str):
            wallpaper = self.wallpapers.find_wallpaper(wallpaper)
        self.ipc.preload(wallpaper)

    def unload_wallpaper(
        self, wallpaper: Path | str | Literal["all", "unused"]
    ) -> None:
        """Unload wallpaper(s) from memory.

        Args:
            wallpaper: Wallpaper path/name, "all", or "unused"

        Raises:
            WallpaperNotFoundError: If wallpaper not found
            HyprpaperNotRunningError: If hyprpaper not running
            HyprpaperIPCError: If IPC command fails
        """
        if isinstance(wallpaper, str) and wallpaper not in (
            "all",
            "unused",
        ):
            wallpaper = self.wallpapers.find_wallpaper(wallpaper)
        self.ipc.unload(wallpaper)

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
