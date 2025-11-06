"""Monitor management for Hyprland."""

import json
import subprocess
from typing import Any

from hyprpaper_manager.core.exceptions import MonitorNotFoundError
from hyprpaper_manager.core.types import MonitorInfo


class MonitorManager:
    """Manage Hyprland monitors."""

    def __init__(self, timeout: int = 5):
        """Initialize monitor manager.

        Args:
            timeout: Command timeout in seconds
        """
        self.timeout = timeout

    def get_monitors(self) -> list[MonitorInfo]:
        """Get all monitors.

        Returns:
            List of monitor information
        """
        try:
            result = subprocess.run(
                ["hyprctl", "monitors", "-j"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True,
            )
            monitors_data: list[dict[str, Any]] = json.loads(result.stdout)

            return [
                MonitorInfo(
                    name=m["name"],
                    description=m.get("description"),
                    focused=m.get("focused", False),
                )
                for m in monitors_data
            ]

        except (
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            FileNotFoundError,
        ):
            # Fallback: return empty list
            return []

    def get_focused_monitor(self) -> MonitorInfo:
        """Get currently focused monitor.

        Returns:
            Focused monitor information

        Raises:
            MonitorNotFoundError: If no focused monitor found
        """
        monitors = self.get_monitors()
        for monitor in monitors:
            if monitor.focused:
                return monitor
        raise MonitorNotFoundError("No focused monitor found")

    def get_monitor(self, name: str) -> MonitorInfo:
        """Get specific monitor by name.

        Args:
            name: Monitor name

        Returns:
            Monitor information

        Raises:
            MonitorNotFoundError: If monitor not found
        """
        monitors = self.get_monitors()
        for monitor in monitors:
            if monitor.name == name:
                return monitor
        raise MonitorNotFoundError(f"Monitor '{name}' not found")
